$ErrorActionPreference = 'Stop'
$testDir = Join-Path ([IO.Path]::GetTempPath()) ('tse-telemetry-' + [guid]::NewGuid())
New-Item -ItemType Directory $testDir | Out-Null
@'
[BotSnapshot] tick=1 player=1 pos=(0.00,0.00,0.00) yaw=0.00 health=100.0 buttons=32768 \player_1\TSE_Bot_PoC\frags_1\0\ping_1\40
[BotSnapshot] tick=2 player=1 pos=(0.00,0.00,-1.00) yaw=2.25 health=0.0 buttons=32769 \player_1\TSE_Bot_PoC\frags_1\-1\ping_1\40
[BotSnapshot] tick=3 player=1 pos=(0.00,0.00,-2.00) yaw=4.50 health=100.0 buttons=0 incomplete
'@ | Set-Content "$testDir\sample.log"
& "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\sample.log" -Output "$testDir\result.json" | Out-Null
$result = Get-Content -Raw "$testDir\result.json" | ConvertFrom-Json
$player = $result.players[0]
if ($result.rejectedSnapshotLines -ne 1 -or $player.samples -ne 2 -or
    $player.fireOnSamples -ne 1 -or $player.fireOffSamples -ne 1 -or
    $player.minimumHealth -ne 0 -or $player.minimumFrags -ne -1 -or
    $player.healthChanges.Count -ne 1 -or $player.distinctPositions -ne 2) {
    throw 'Telemetry regression failed.'
}
$rejectedOverwrite = $false
try {
    & "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\sample.log" -Output "$testDir\result.json" | Out-Null
} catch { $rejectedOverwrite = $_.Exception.Message -eq 'Use a new output file.' }
if (!$rejectedOverwrite) { throw 'Existing evidence was not protected.' }
Write-Output "ALL TELEMETRY CHECKS PASSED ($testDir)"
