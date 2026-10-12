$ErrorActionPreference='Stop'
if(Test-Path "$PSScriptRoot/FleetRoundReadiness.ps1"){. "$PSScriptRoot/FleetRoundReadiness.ps1"}
function Check([string]$Text){if(Get-Command Test-FleetRoundStarting -ErrorAction SilentlyContinue){return Test-FleetRoundStarting $Text};return $false}
$ready="Executing: 'Scripts\Dedicated\BotTest\1_begin.ini'`nlevel: 'Fortress.wld'`nALL OK: Dedicated server is now running!`n"
$starting=$ready+"Executing: 'Scripts\Dedicated\BotTest\2_begin.ini'`nlevel: 'DM_LittleTrouble.wld'`n"
if(!(Check $starting)){throw 'Previous readiness cannot satisfy a fresh native round.'}
if(Check $ready){throw 'Ready server accepted as a transition.'}
if(Check ($starting+"ALL OK: Dedicated server is now running!`n")){throw 'New round still pending after fresh readiness.'}
if(Check "ALL OK: Dedicated server is now running!`nnetwork error"){throw 'Unrelated network error treated as round transition.'}
if(Check 'Executing: different script'){throw 'Unrelated script treated as native round transition.'}
'FLEET NATIVE ROUND READINESS REGRESSIONS PASS'
