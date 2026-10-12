$ErrorActionPreference='Stop'
. "$PSScriptRoot\FleetQuery.ps1"
$ids=@(1..8|ForEach-Object{[pscustomobject]@{name="Bot_$_"}})
$players=(@(0..7|ForEach-Object{"\player_$_\Bot_$($_+1)"}) -join '')
$valid=@{status='\numplayers\8\';players=$players}
Assert-FleetSteadySample $valid $ids
foreach($bad in @(@{status='\numplayers\4\';players=$players},@{status='\numplayers\8\';players=$players.Replace('\player_7\Bot_8','')},@{status='\numplayers\8\';players=$players.Replace('Bot_8','Bot_7')})){
    $rejected=$false
    try{Assert-FleetSteadySample $bad $ids}catch{if($_.Exception.Message -notmatch 'Steady fleet'){throw};$rejected=$true}
    if(!$rejected){throw 'Incomplete steady fleet accepted.'}
}
'PASS: complete steady fleet, lost process/slots, incomplete list and duplicate identity fail immediately'
