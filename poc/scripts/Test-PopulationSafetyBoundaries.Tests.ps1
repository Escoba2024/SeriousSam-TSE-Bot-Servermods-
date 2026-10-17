param([string]$SupervisorPath=(Join-Path $PSScriptRoot 'PopulationSupervisor.ps1'))
$ErrorActionPreference='Stop'
. $SupervisorPath
$checks=0
function Assert($Value,[string]$Message){if(!$Value){throw $Message};$script:checks++}

# Pure process doubles: none of these IDs is ever passed to the OS.
function New-ProcessDouble([int]$Number,[string]$Path,[datetime]$Time){
    $p=[pscustomobject]@{Id=$Number;Path=$Path;StartTime=$Time;HasExited=$false;Handle=1;Killed=$false;ExitCode=0}
    $p|Add-Member ScriptMethod Kill {$this.Killed=$true;$this.HasExited=$true}
    $p|Add-Member ScriptMethod WaitForExit {param($Milliseconds) return $this.HasExited}
    $p|Add-Member ScriptMethod CloseMainWindow {return $false}
    $p|Add-Member ScriptMethod Dispose {}
    return $p
}
$stamp=[datetime]::UtcNow
$fixture=@{process=$null;parent=$PID;deny=$false;processes=@()}
function Get-Process {param($Id) if($PSBoundParameters.ContainsKey('Id')){return $fixture.process};return $fixture.processes}
function Get-CimInstance {param($ClassName,$Filter) if($fixture.deny){throw 'fixture: identity unavailable'};return @{ParentProcessId=$fixture.parent}}
foreach($case in 'path','timestamp','parent','self','unreadable'){
    $p=New-ProcessDouble 100001 'fixture.exe' $stamp
    $entry=@{pid=$p.Id;exe=$p.Path;startedUtc=$stamp.ToString('o')}
    $fixture.process=$p;$fixture.parent=$PID;$fixture.deny=$false
    switch($case){
        'path' {$entry.exe='other.exe'}
        'timestamp' {$entry.startedUtc=$stamp.AddTicks(1).ToString('o')}
        'parent' {$fixture.parent=0}
        'self' {$p.Id=$PID;$entry.pid=$PID}
        'unreadable' {$fixture.deny=$true}
    }
    $failed=$false
    try{Stop-PopulationOwnedRecord @{Entry=$entry;StatePath='unused'} -GracefulWaitSeconds 0|Out-Null}catch{$failed=$true}
    Assert (!$p.Killed) "Unsafe stop accepted $case identity"
    if($case -in 'parent','self','unreadable'){Assert $failed "Missing refusal for $case"}
}
# Review finding: rollback identifies a time/path/parent set, not one launch.
# Reproduce exclusively on doubles, never on parallel live processes.
$fixture.deny=$false;$fixture.parent=$PID
$fixture.processes=@((New-ProcessDouble 100001 'fixture.exe' $stamp),(New-ProcessDouble 100002 'fixture.exe' $stamp))
Stop-PopulationOwnedLaunch -ExpectedExe 'fixture.exe' -NotBeforeUtc $stamp
Assert ($fixture.processes[0].Killed -and $fixture.processes[1].Killed) 'Rollback candidate-set boundary changed; review test and narrow ownership contract'
Remove-Item Function:Get-Process,Function:Get-CimInstance

function Run-LoopBoundary([string]$Mode){
    $ctx=@{time=0;stops=@();events=@();starts=0}
    $g=[pscustomobject]@{Id='A';Size=1;Names=@('A');Active=$true;EligibleAt=0;Record=@{fixture=$true}}
    $read={
        if($Mode -eq 'outage' -and $ctx.time -ge 2){throw 'fixture query outage'}
        [pscustomobject]@{Valid=$true;Total=1;MaxPlayers=16;Map='fixture';Names=@('A')}
    }.GetNewClosure()
    $ready={param($Group,$Sample)
        if($Mode -eq 'rearm'){return $ctx.time -eq 0 -or $ctx.time -eq 45}
        return $ctx.time -eq 0
    }.GetNewClosure()
    $stop={param($Group) $ctx.stops+=@($ctx.time)}.GetNewClosure()
    $iterations=if($Mode -eq 'rearm'){94}else{51}
    Invoke-PopulationLoop -Groups @($g) -TargetPopulation 1 -ReservedHumanSlots 2 -Iterations $iterations -PollMilliseconds 1 -ObserveOnly:($Mode -eq 'observe') -ReadSample $read -IsReady $ready -IsRunning {$true} -StartGroup {$ctx.starts++;throw 'Unexpected start'} -StopGroup $stop -Wait {param($ms)$ctx.time++}.GetNewClosure() -Now {$ctx.time}.GetNewClosure() -Log {param($e)$ctx.events+=@($e)}.GetNewClosure() -StopRequested {$false}
    return $ctx
}
$r=Run-LoopBoundary 'outage'
Assert ($r.stops.Count -eq 1 -and $r.stops[0] -eq 46) 'Query outage postponed owned readiness timeout'
Assert (@($r.events|Where-Object Event -eq 'ReadinessLost').Count -eq 1) 'Outage deadline was not armed once'
Assert (@($r.events|Where-Object Event -eq 'JoinTimeout').Count -eq 1) 'Timeout not recorded under query outage'
$r=Run-LoopBoundary 'rearm'
Assert ($r.stops.Count -eq 1 -and $r.stops[0] -eq 91) 'Recovered deadline did not clear/rearm from second readiness loss'
Assert (@($r.events|Where-Object Event -eq 'ReadinessLost').Count -eq 2) 'Separated outages did not receive independent deadlines'
$r=Run-LoopBoundary 'observe'
Assert (!$r.stops.Count -and !$r.starts) 'ObserveOnly performed cleanup/start'
Assert (!@($r.events|Where-Object Event -in 'ReadinessLost','JoinTimeout').Count) 'ObserveOnly created recovery deadlines'

# A cleanup failure in one group must not skip another owned group.
$attempts=[Collections.Generic.List[string]]::new()
$groups=@('A','B'|ForEach-Object{[pscustomobject]@{Id=$_;Size=1;Names=@($_);Active=$true;EligibleAt=0}})
$failed=$null
try {
    Invoke-PopulationLoop -Groups $groups -TargetPopulation 0 -ReservedHumanSlots 2 -Iterations 1 -ReadSample {@{Valid=$false}} -IsRunning {$true} -IsReady {$false} -StartGroup {throw 'Unexpected start'} -StopGroup {param($g)$attempts.Add($g.Id);if($g.Id -eq 'A'){throw 'fixture cleanup failure'}} -Wait {} -Now {0} -Log {} -StopRequested {$false}
} catch {$failed=$_.Exception.Message}
Assert ($failed -eq 'Owned cleanup failed: fixture cleanup failure') 'Cleanup failure was hidden by normal completion'
Assert (($attempts -join ',') -eq 'A,B' -and !$groups[1].Active) 'Cleanup failure skipped the next owned group'

# Reserve cases include zero capacity, reserve above maximum, whole-group
# underfill and capacity loss. Names resembling bots are ordinary occupancy.
foreach($max in 1,4,8,16){foreach($reserve in 0,2,15){foreach($target in 0,4,8,16){foreach($total in 0..$max){foreach($size in 1..4){
    $sample=@{Valid=$true;Total=$total;MaxPlayers=$max;Names=@('TSE_Bot_Human')}
    $cap=[math]::Min($target,[math]::Max(0,$max-$reserve))
    $group=[pscustomobject]@{Id='A';Size=$size;Active=$false;EligibleAt=0}
    $d=Get-PopulationGroupDecision $sample @($group) $target $reserve 0
    Assert ($d.Cap -eq $cap) 'Human reserve cap mismatch'
    Assert (($d.Action -eq 'Start') -eq ($total+$size -le $cap)) 'Whole group crossed reserve or failed to fit'
    $group.Active=$true
    $d=Get-PopulationGroupDecision $sample @($group) $target $reserve 0
    Assert (($d.Action -eq 'Stop') -eq ($total -gt $cap)) 'Owned group did not yield reserved capacity'
}}}}}
"SAFETY BOUNDARIES PASS: $checks checks; identity uses process doubles; rollback multi-candidate limitation confirmed without live kills"
