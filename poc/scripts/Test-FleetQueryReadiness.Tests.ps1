$ErrorActionPreference='Stop'
. "$PSScriptRoot/FleetQuery.ps1"
function Check($Status,$Players,[int]$Count){
    if(Get-Command Test-FleetQueryCountReady -ErrorAction SilentlyContinue){return Test-FleetQueryCountReady $Status $Players $Count}
    # Previous Wait-Count returned on the reported slot count alone.
    return $Status -match "\\numplayers\\$Count\\"
}
$eight=''
foreach($i in 0..7){$eight+='\player_'+$i+'\TSE_Fleet_'+$(if($i -lt 4){'A'}else{'B'})+'_'+(($i%4)+1)}
$nine=$eight+'\player_8\Vanilla_Human_1'
if(Check '\numplayers\9\' $eight 9){throw 'Slot reservation without the ninth native name is not a completed human rejoin.'}
if(!(Check '\numplayers\9\' $nine 9)){throw 'Complete human rejoin was not ready.'}
if(!(Check '\numplayers\8\' $eight 8)){throw 'Complete eight-bot join was not ready.'}
if(Check '\numplayers\8\' $nine 8){throw 'Mismatched status/player responses were accepted.'}
if(Check '\numplayers\9\' ($eight+'\player_8\TSE_Fleet_A_1') 9){throw 'Duplicate native player names were accepted.'}
if(Check '\numplayers\9\' ($eight+'\player_7\Vanilla_Human_1') 9){throw 'Duplicate native player indices were accepted.'}
if(Check '\gamename\serioussamse\' $eight 8){throw 'Missing native count was accepted.'}
'FLEET NATIVE QUERY READINESS REGRESSIONS PASS'
