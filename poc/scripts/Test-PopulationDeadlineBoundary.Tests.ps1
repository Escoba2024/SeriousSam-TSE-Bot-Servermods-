$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
# Deterministic adapters exercise the real loop, without OS process APIs or games.
function Invoke-DeadlineCase([object[]]$Timeline,[bool]$InitiallyPending=$false,[bool]$Observe=$false) {
    $ctx=@{index=0;time=$(if($Timeline[0].ContainsKey('Begin')){$Timeline[0].Begin}else{$Timeline[0].Time});events=@();starts=0;stops=@()}
    $groups=@([pscustomobject]@{Id='A';Size=4;Names=@('A1','A2','A3','A4');Active=$true;Pending=$InitiallyPending;Deadline=45;EligibleAt=0})
    $read={
        $row=$Timeline[$ctx.index];$ctx.time=$row.Time
        if($row.Error){throw 'query unavailable'}
        [pscustomobject]@{Valid=(!$row.Invalid);Total=4;MaxPlayers=16;Map='Fortress';Names=@('A1','A2','A3','A4')}
    }.GetNewClosure()
    Invoke-PopulationLoop -Groups $groups -TargetPopulation 4 -ReservedHumanSlots 2 -Iterations $Timeline.Count `
        -ReadSample $read -StartGroup {param($g)$ctx.starts++}.GetNewClosure() `
        -StopGroup {param($g)$ctx.stops+=@($ctx.time)}.GetNewClosure() -IsRunning {$true} `
        -IsReady {param($g,$s)[bool]$Timeline[$ctx.index].Ready}.GetNewClosure() `
        -Now {$ctx.time}.GetNewClosure() -Wait {param($ms)$ctx.index++;$ctx.time=if($Timeline[$ctx.index].ContainsKey('Begin')){$Timeline[$ctx.index].Begin}else{$Timeline[$ctx.index].Time}}.GetNewClosure() `
        -Log {param($e)$ctx.events+=@($e)}.GetNewClosure() -StopRequested {$false} -ObserveOnly:$Observe
    return $ctx
}
foreach($initial in $true,$false){
    # A query begun before the deadline may finish after it with proof of recovery.
    $timeline=if($initial){@(@{Begin=44;Time=46;Ready=$true})}else{@(@{Time=0;Ready=$false},@{Begin=44;Time=46;Ready=$true})}
    $r=Invoke-DeadlineCase $timeline $initial
    if(@($r.events|Where-Object Event -eq 'JoinTimeout').Count){throw "Fresh ready sample lost to expired deadline (initial=$initial)"}
    if($r.starts -or $r.stops.Count -ne 1){throw 'Recovered group changed before final cleanup'}
}
$r=Invoke-DeadlineCase @(@{Time=0;Ready=$true},@{Time=1;Ready=$false},@{Time=44;Ready=$true},@{Time=45;Ready=$false},@{Time=89;Ready=$false},@{Time=90;Ready=$false})
$lost=@($r.events|Where-Object Event -eq 'ReadinessLost')
$timeouts=@($r.events|Where-Object Event -eq 'JoinTimeout')
if($lost.Count -ne 2 -or $lost[0].Time -ne 1 -or $lost[1].Time -ne 45 -or $timeouts.Count -ne 1 -or $timeouts[0].Time -ne 90){throw 'Repeated readiness loss did not get one independent 45-second deadline per outage'}
foreach($bad in @(@{Time=46;Error=$true},@{Time=46;Invalid=$true},@{Time=46;Ready=$false})){
    $r=Invoke-DeadlineCase @($bad) $true
    if(@($r.events|Where-Object Event -eq 'JoinTimeout').Count -ne 1 -or $r.stops.Count -ne 1 -or $r.starts){throw 'Uncertain/not-ready sample bypassed bounded timeout'}
}
$r=Invoke-DeadlineCase @(@{Time=0;Ready=$true},@{Time=46;Error=$true})
if(@($r.events|Where-Object Event -eq 'JoinTimeout').Count -or $r.starts){throw 'Query outage alone restarted a previously ready group'}
foreach($pending in $true,$false){
    $r=Invoke-DeadlineCase @(@{Time=0;Ready=$false},@{Time=46;Ready=$false},@{Time=100;Ready=$true}) $pending $true
    if($r.starts -or $r.stops.Count -or @($r.events|Where-Object Event -eq 'ReadinessLost').Count){throw 'ObserveOnly controlled processes or armed readiness deadline'}
}
'POPULATION DEADLINE BOUNDARIES PASS: 9 scenarios'
