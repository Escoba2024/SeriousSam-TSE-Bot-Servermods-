$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
$status='\gamename\serioussamse\gamever\1.07\activemod\\numplayers\1\maxplayers\16\mapname\Fortress\final\\queryid\1.1'
$players='\player_0\A\frags_0\0\ping_0\30\final\\queryid\2.1'
$bad=@(('garbage'+$players),($players+'\player_1'),($players+'\'),($players+'\queryid'),($players+'\final'))
$checks=0
foreach($text in $bad){
    $rejected=$false
    try{ConvertTo-PopulationSample $status $text $status|Out-Null}catch{$rejected=$true}
    if(!$rejected){throw "Malformed UDP framing accepted: $text"};$checks++
}
foreach($text in @(('garbage'+$status),($status+'\numplayers'),($status+'\'))){
    foreach($before in $true,$false){
        $rejected=$false
        try{if($before){ConvertTo-PopulationSample $text $players $status|Out-Null}else{ConvertTo-PopulationSample $status $players $text|Out-Null}}catch{$rejected=$true}
        if(!$rejected){throw 'Malformed status framing accepted'};$checks++
    }
}
foreach($reply in @($players,$players.Replace('A\frags','final\frags'),$players.Replace('\final\\queryid\2.1','\final\'))){
    if((ConvertTo-PopulationSample $status $reply $status).Total -ne 1){throw 'Complete GameSpy reply rejected'};$checks++
}
# Rejected samples must reset the two-sample start gate in the actual loop.
$ctx=@{tick=0;starts=0;uncertain=0}
$g=@([pscustomobject]@{Id='A';Size=1;Names=@('Other');Active=$false;EligibleAt=0})
$read={ConvertTo-PopulationSample $status $(if($ctx.tick -eq 1){$players+'\player_1'}else{$players}) $status}.GetNewClosure()
Invoke-PopulationLoop -Groups $g -TargetPopulation 2 -ReservedHumanSlots 2 -Iterations 3 -ReadSample $read `
    -StartGroup {param($g)$ctx.starts++}.GetNewClosure() -StopGroup {} -IsRunning {$true} -IsReady {$true} `
    -Wait {param($ms)$ctx.tick++}.GetNewClosure() -Now {$ctx.tick}.GetNewClosure() `
    -Log {param($e)if($e.Event -eq 'QueryUncertain'){$ctx.uncertain++}}.GetNewClosure() -StopRequested {$false}
if($ctx.starts -or $ctx.uncertain -ne 1){throw 'Malformed reply authorized a group start'}
"POPULATION UDP FRAMING PASS: $checks parser checks and start-gate scenario"
