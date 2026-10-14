$ErrorActionPreference='Stop'
if(Test-Path "$PSScriptRoot/PopulationSupervisor.ps1"){. "$PSScriptRoot/PopulationSupervisor.ps1"}
if(!(Get-Command Invoke-PopulationLoop -ErrorAction SilentlyContinue)){throw 'Population loop is missing'}
$checks=0
function Assert($c,$m){if(!$c){throw $m};$script:checks++}
function RunCase($Counts,$Iterations,$Ready=$true,$FailStart=$false,$FailLog=$false,$Target=4,$Ghost=$false,$StopDelay=0){
 $ctx=@{tick=0;time=0;starts=0;stops=0;events=@();children=@();ready=$Ready;startTimes=@();stopTimes=@()}
 $g=@([pscustomobject]@{Id='A';Size=4;Active=$false;EligibleAt=0;Names=@('A1','A2','A3','A4')})
 $pwsh=(Get-Process -Id $PID).Path
 $start={param($group)
    if($FailStart){throw 'launch fault'}
    $p=Start-Process $pwsh -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 90"' -WindowStyle Hidden -PassThru
    $ctx.children+=@($p);$ctx.starts++;$ctx.startTimes+=@($ctx.time)
    return $p
 }.GetNewClosure()
 $stop={param($group) $ctx.stops++;if($group.Record -and !$group.Record.HasExited){$group.Record.Kill();[void]$group.Record.WaitForExit(5000)};$ctx.time+=$StopDelay;$ctx.stopTimes+=@($ctx.time)}.GetNewClosure()
 $read={ $count=$Counts[$ctx.tick % $Counts.Count];if($count -eq -2){return [pscustomobject]@{Valid=$false}};if($count -lt 0){throw 'query fault'};$names=if($Ghost){@('A1')}elseif($count -ge 4){@('A1','A2','A3','A4')}elseif($count -eq 1){@('Human')}else{@()};[pscustomobject]@{Valid=$true;Total=$count;MaxPlayers=16;Map='Fortress';Names=$names}}.GetNewClosure()
 $wait={param($ms) $ctx.tick++;$ctx.time+=1}.GetNewClosure()
 $clock={return $ctx.time}.GetNewClosure()
 $log={param($e) $ctx.events+=@($e);if($FailLog -and $e.Event -eq 'Start'){throw 'log fault'}}.GetNewClosure()
 $running={param($group) return $group.Record -and !$group.Record.HasExited}
 $isready={param($group,$sample) return $ctx.ready}.GetNewClosure()
 $failed=$null
 try{Invoke-PopulationLoop -Groups $g -TargetPopulation $Target -ReservedHumanSlots 2 -Iterations $Iterations -PollMilliseconds 1 -ReadSample $read -StartGroup $start -StopGroup $stop -IsRunning $running -IsReady $isready -Wait $wait -Now $clock -Log $log -StopRequested {$false} | Out-Null}catch{$failed=$_.Exception.Message}
 finally{foreach($p in $ctx.children){Assert ($p.HasExited) 'Owned child leaked';if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}}}
 return [pscustomobject]@{Context=$ctx;Failure=$failed}
}
$r=RunCase @(0,0,4,4,5,1,1,0,0,0,0,0,0,0,0,0,0) 17
Assert (!$r.Failure -and $r.Context.starts -eq 2) 'Start/resume after cooldown failed'
Assert ($r.Context.stops -eq 2) 'Human-priority stop and final cleanup missing'
$r=RunCase @(0,-1,0,-1,0,-1) 6
Assert (!$r.Failure -and $r.Context.starts -eq 0) 'Query faults did not reset start stability'
$r=RunCase @(0,-2,0) 3
Assert (!$r.Failure -and $r.Context.starts -eq 0) 'Invalid returned sample did not reset stability'
$r=RunCase @(0) 49 $false
Assert (!$r.Failure -and $r.Context.starts -eq 1 -and $r.Context.stops -eq 1) 'Join timeout/cooldown failed'
Assert (@($r.Context.events|Where-Object Event -eq 'JoinTimeout').Count -eq 1) 'Join timeout not evidenced'
$r=RunCase @(0) 3 $true $true
Assert ($r.Failure -eq 'launch fault' -and $r.Context.starts -eq 0) 'Launch error lost'
$r=RunCase @(0) 3 $true $false $true
Assert ($r.Failure -eq 'log fault' -and $r.Context.stops -eq 1) 'Logging failure leaked child'
$r=RunCase @(1) 4 $true $false $false 8 $true
Assert (!$r.Failure -and $r.Context.starts -eq 0) 'Prior native identity still present: must not start'
$r=RunCase @(0,0,4,4,5,1,0,0,0,0,0,0,0,0,0,0,0) 17 $true $false $false 4 $false 5
Assert ($r.Context.startTimes.Count -eq 2 -and $r.Context.startTimes[1]-$r.Context.stopTimes[0] -ge 10) 'Cooldown starts at stop completion'
# Two independent state roots still contend on the installation lock.
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('pop-lock-'+[guid]::NewGuid());New-Item -ItemType Directory $tmp|Out-Null
$first=Enter-PopulationClientLocks @($tmp)
try{$blocked=$false;try{$second=Enter-PopulationClientLocks @($tmp)}catch{$blocked=$true};Assert $blocked 'Second controller acquired client lock'}
finally{foreach($h in $first){$h.Dispose()}}
$again=Enter-PopulationClientLocks @($tmp);foreach($h in $again){$h.Dispose()}
Assert $true 'Released lock reacquired'
"POPULATION CONTROL PASS: $checks checks"
