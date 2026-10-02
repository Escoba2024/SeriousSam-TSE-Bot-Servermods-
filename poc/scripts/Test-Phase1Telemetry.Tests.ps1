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
$active = @(for ($tick=1; $tick -le 1200; $tick++) {
    "[BotSnapshot] tick=$tick player=0 pos=($tick,0.00,0.00) yaw=$($tick%360) health=100.0 buttons=$($tick%2) \frags_0\0"
})
$active | Set-Content "$testDir\active.log"
& "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\active.log" -Output "$testDir\active.json" -SyncMinutes 1 | Out-Null
$stalled = @($active) + @(for ($tick=1201; $tick -le 2400; $tick++) {
    "[BotSnapshot] tick=$tick player=0 pos=(0.00,0.00,0.00) yaw=0.00 health=100.0 buttons=1 \frags_0\0"
})
$stalled | Set-Content "$testDir\stalled.log"
$rejectedStall = $false
try {
    & "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\stalled.log" -Output "$testDir\stalled.json" -SyncMinutes 2 | Out-Null
} catch { $rejectedStall = $_.Exception.Message -eq 'Native actions stalled in minute 2.' }
if (!$rejectedStall) { throw 'Ticking input with frozen native actions was accepted.' }
@($active)+@($active) | Set-Content "$testDir\duplicate.log"
$rejectedDuplicate = $false
try {
    & "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\duplicate.log" -Output "$testDir\duplicate.json" -SyncMinutes 2 | Out-Null
} catch { $rejectedDuplicate = $_.Exception.Message -eq 'Native tick counter restarted or duplicated during sync run.' }
if (!$rejectedDuplicate) { throw 'Duplicate input ticks inflated sync duration.' }
$multi = @($active) + @(for ($tick=21; $tick -le 1220; $tick++) {
    "[BotSnapshot] tick=$tick player=1 pos=(0.00,0.00,0.00) yaw=0.00 health=100.0 buttons=1 \frags_1\0"
})
$multi | Set-Content "$testDir\multi-stalled.log"
$rejectedSecondPlayer = $false
try {
    & "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\multi-stalled.log" -Output "$testDir\multi-stalled.json" -SyncMinutes 1 -ExpectedPlayers 2 | Out-Null
} catch { $rejectedSecondPlayer = $_.Exception.Message -eq 'Native actions stalled for player 1 in minute 1.' }
if (!$rejectedSecondPlayer) { throw 'A frozen second native player was not detected.' }
$multiActive = @($active) + @(for ($tick=21; $tick -le 1220; $tick++) {
    "[BotSnapshot] tick=$tick player=1 pos=($tick,0.00,0.00) yaw=$($tick%360) health=100.0 buttons=$($tick%2) \frags_1\0"
})
$multiActive | Set-Content "$testDir\multi-active.log"
& "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\multi-active.log" -Output "$testDir\multi-active.json" -SyncMinutes 1 -ExpectedPlayers 2 | Out-Null
$multiResult = Get-Content "$testDir\multi-active.json" -Raw | ConvertFrom-Json
if($multiResult.activeSyncMinutes.Count -ne 2 -or $multiResult.activeSyncMinutes[1].samples -ne 1200){throw 'Later native player join did not receive a complete independent minute.'}
$rejectedMissing = $false
try {
    & "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$testDir\multi-active.log" -Output "$testDir\multi-missing.json" -SyncMinutes 1 -ExpectedPlayers 3 | Out-Null
} catch { $rejectedMissing = $_.Exception.Message -eq 'Expected native player count does not match.' }
if (!$rejectedMissing) { throw 'Missing local player was accepted.' }
Write-Output "ALL TELEMETRY CHECKS PASSED ($testDir)"
