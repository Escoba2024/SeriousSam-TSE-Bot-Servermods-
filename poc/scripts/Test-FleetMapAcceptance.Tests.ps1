$ErrorActionPreference='Stop'
. "$PSScriptRoot/FleetMapAcceptance.ps1"
$ids=@(1..8|ForEach-Object{[pscustomobject]@{name="Bot$_"}})
$names=(1..8|ForEach-Object{"\player_$($_-1)\Bot$_\frags_$($_-1)\0"}) -join ''
$queries=@(foreach($map in @('Fortress','Little Trouble',"We Got Skulls'n'Bones Too")) {
    foreach($sec in 0,5,10) { [pscustomobject]@{utc="2026-10-09T16:00:$($sec.ToString('00'))Z";status="\mapname\$map\numplayers\8\gamever\1.07\activemod\\";players=$names} }
})
if(@(Assert-FleetMapQueries $queries $ids).Count -ne 3){throw 'Complete fixture rejected'}
function Reject($Data,[string]$Case) {
    $rejected=$false
    try{Assert-FleetMapQueries $Data $ids|Out-Null}catch{$rejected=$true}
    if(!$rejected){throw "Invalid fixture accepted: $Case"}
}
Reject @($queries|Where-Object status -notmatch 'Little Trouble') 'missing intermediate map with valid final eight'
$bad=@($queries|ForEach-Object{[pscustomobject]@{utc=$_.utc;status=$_.status;players=if($_.status -match 'Little Trouble'){$_.players.Replace('Bot8','Bot7')}else{$_.players}}})
Reject $bad 'allocated eight with duplicate and missing name'
$short=@($queries|ForEach-Object{[pscustomobject]@{utc='2026-10-09T16:00:00Z';status=$_.status;players=$_.players}})
Reject $short 'three simultaneous samples are not stable coverage'
$server=@(foreach($map in 'Fortress','DM_LittleTrouble','WeGotSkullsNBonesToo') {
    "  level: 'Levels\LevelsMP\Deathmatch\$map.wld'"
    'CRC check OK';'CRC check OK';'CRC check OK'
    foreach($id in $ids){"^o$($id.name)^r joined"}
}) -join "`n"
if(@(Assert-FleetMapServer $server $ids).Count -ne 3){throw 'Server fixture rejected'}
$rejected=$false
try{Assert-FleetMapServer ($server.Replace('Bot8^r joined','Other^r joined')) $ids|Out-Null}catch{$rejected=$true}
if(!$rejected){throw 'Missing real server player accepted'}
$actions=@(foreach($session in 1..3){
    '  joined'
    foreach($tick in 1..12){foreach($slot in 0..3){
        "[BotDriver] bot$slot tick=$tick pos=($($tick%2),0,0) heading=$($tick*10) fire=$($tick%2)"
    }}
    'Disconnected: Server stopped.'
}) -join "`n"
if(@(Assert-FleetMapActions $actions).Count -ne 12){throw 'Action fixture rejected'}
$rejected=$false
try{Assert-FleetMapActions ($actions -replace 'heading=\d+','heading=10')|Out-Null}catch{$rejected=$true}
if(!$rejected){throw 'Frozen actions accepted despite full eight-name membership'}
'FLEET MAP ACCEPTANCE REGRESSIONS PASS'
