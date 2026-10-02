# Unit-Regressionen fuer PopulationCore.ps1 / Start-BotFleet.ps1 (Phase 3/5/6/7).
# Reine Logiktests ohne Spielprozesse; ersetzen keine Runtime-Abnahme.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\PopulationCore.ps1"
$testDir = Join-Path ([IO.Path]::GetTempPath()) ('tse-fleet-' + [guid]::NewGuid())
New-Item -ItemType Directory $testDir | Out-Null

function Expect-Throw([scriptblock]$Block, [string]$Pattern, [string]$Case) {
    $thrown = $null
    try { & $Block | Out-Null } catch { $thrown = $_.Exception.Message }
    if ($null -eq $thrown -or $thrown -notmatch $Pattern) {
        throw "Case '$Case': expected failure '$Pattern', got: $thrown"
    }
}

# --- Populationsregeln: identische Szenariotabelle wie test_botcore_ai.cpp ---
if ((Get-DesiredBots -MaxPlayers 16 -Humans 0 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 12) { throw 'empty server fills to target' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 0 -Bots 0 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 'StartBot') { throw 'start first bot' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 0 -Bots 12 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 'None') { throw 'target reached' }
if ((Get-DesiredBots -MaxPlayers 16 -Humans 3 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 9) { throw 'humans count against target' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 3 -Bots 12 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 'StopBot') { throw 'bots yield to humans' }
if ((Get-DesiredBots -MaxPlayers 16 -Humans 13 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 0) { throw 'humans above target leave no room' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 13 -Bots 3 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 'StopBot') { throw 'shrink to zero' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 13 -Bots 0 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 'None') { throw 'zero bots stable' }
if ((Get-DesiredBots -MaxPlayers 16 -Humans 16 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 0) { throw 'full server wants zero bots' }
if ((Get-DesiredBots -MaxPlayers 16 -Humans 0 -TargetPopulation 99 -ReservedHumanSlots 2) -ne 14) { throw 'target clamped to capacity' }
if ((Get-DesiredBots -MaxPlayers 16 -Humans 14 -TargetPopulation 16 -ReservedHumanSlots 2) -ne 0) { throw 'reserve blocks start' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 14 -Bots 0 -TargetPopulation 16 -ReservedHumanSlots 2) -ne 'None') { throw 'no bot in reserved slots' }
if ((Get-DesiredBots -MaxPlayers 16 -Humans 8 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 4) { throw 'target below capacity' }
if ((Get-PopulationAction -MaxPlayers 16 -Humans 8 -Bots 2 -TargetPopulation 12 -ReservedHumanSlots 2) -ne 'StartBot') { throw 'fill toward target' }

# --- LCG: exakter Spiegel von botcore::Lcg (Referenzwerte aus test_botcore_ai) ---
$lcg = New-BotLcg -Seed 1234
$expected = @(3067928073, 889114580, 3219257635, 1486326822, 3450746189)
foreach ($value in $expected) {
    if ((Get-BotLcgNext $lcg) -ne $value) { throw 'LCG mismatch with botcore::Lcg.' }
}
$lcg = New-BotLcg -Seed 1234
$expectedRange = @(85, 84, 52, 23, 14)
foreach ($value in $expectedRange) {
    $range = Get-BotLcgRange $lcg -Minimum 5 -Maximum 90
    if ($range -ne $value) { throw "LCG range mismatch: $range vs $value." }
    if ($range -lt 5 -or $range -gt 90) { throw 'LCG range out of bounds.' }
}

# --- GameAgent-\players\-Klassifikation ---
$reply = '\player_0\Human_Hank\frags_0\3\ping_0\40\player_1\TSE_Bot_A\frags_1\1\ping_1\10\player_2\TSE_Bot_B\frags_2\0\ping_2\12\final\'
$classified = Get-PlayerClassification -PlayersReply $reply -BotNamePrefix 'TSE_Bot'
if ($classified.Humans -ne 1 -or $classified.Bots -ne 2 -or $classified.Names.Count -ne 3) {
    throw 'Player classification failed.'
}
$empty = Get-PlayerClassification -PlayersReply '\final\' -BotNamePrefix 'TSE_Bot'
if ($empty.Humans -ne 0 -or $empty.Bots -ne 0) { throw 'Empty player list misclassified.' }

# --- Fleet-Konfiguration: Validierung und Plan ---
$good = @{
    server = '127.0.0.1:25600'; queryPort = 25601; botNamePrefix = 'TSE_Bot'
    startStaggerSeconds = 1
    processes = @(
        @{ clientDir = 'C:\tse\bot1'; localPlayers = 4; startupScript = 'Scripts\Phase2FourBots.ini' },
        @{ clientDir = 'C:\tse\bot2'; localPlayers = 2; startupScript = 'Scripts\Phase2TwoBots.ini' }
    )
}
$goodPath = "$testDir\fleet.json"
$good | ConvertTo-Json -Depth 4 | Set-Content $goodPath
$config = Get-FleetConfig -Path $goodPath
$plan = Get-FleetPlan -Config $config
if ($plan.Count -ne 2 -or $plan[0].exe -ne 'C:\tse\bot1\Bin\SeriousSam.exe' -or
    $plan[0].arguments -ne '+connect 127.0.0.1:25600 +quickjoin +script Scripts\Phase2FourBots.ini' -or
    $plan[1].localPlayers -ne 2) {
    throw 'Fleet plan composition failed.'
}

function Write-BadConfig([hashtable]$Mutation, [string]$Name) {
    $bad = $good.Clone()
    foreach ($key in $Mutation.Keys) { $bad[$key] = $Mutation[$key] }
    $path = "$testDir\$Name.json"
    $bad | ConvertTo-Json -Depth 4 | Set-Content $path
    return $path
}
Expect-Throw { Get-FleetConfig -Path (Write-BadConfig @{server=$null} 'noserver') } "misses 'server'" 'missing server'
Expect-Throw { Get-FleetConfig -Path (Write-BadConfig @{server='nonsense'} 'badserver') } 'host:port' 'bad server'
Expect-Throw { Get-FleetConfig -Path (Write-BadConfig @{processes=@()} 'empty') } 'at least one process' 'no processes'
Expect-Throw { Get-FleetConfig -Path (Write-BadConfig @{processes=@(@{clientDir='C:\x'; localPlayers=5; startupScript='s.ini'})} 'toomany') } '1\.\.4' 'localPlayers over limit'
Expect-Throw { Get-FleetConfig -Path (Write-BadConfig @{processes=@(
    @{clientDir='C:\same'; localPlayers=2; startupScript='a.ini'},
    @{clientDir='C:\same'; localPlayers=2; startupScript='b.ini'})} 'dupdir') } 'own bot-client installation' 'duplicate client dir'

# --- Start-BotFleet -DryRun: Plan ohne Prozessstart, Statusschutz ---
$dry = & "$PSScriptRoot\Start-BotFleet.ps1" -Config $goodPath -State "$testDir\state.json" -DryRun | ConvertFrom-Json
if (!$dry.dryRun -or @($dry.plan).Count -ne 2) { throw 'Fleet dry run failed.' }
if (Test-Path "$testDir\state.json") { throw 'Dry run must not write a state file.' }
'{}' | Set-Content "$testDir\state.json"
Expect-Throw { & "$PSScriptRoot\Start-BotFleet.ps1" -Config $goodPath -State "$testDir\state.json" -DryRun } 'new fleet state file' 'state protection'

# --- Start-ServerFarm -DryRun: Planvalidierung ---
$farm = @{
    serverDir = 'C:\tse\server'
    instances = @(
        @{ name='BotTest'; port=25600; maxPlayers=16; targetPopulation=12; reservedHumanSlots=2; botNamePrefix='TSE_Bot'; fleetConfig='f1.json' },
        @{ name='BotTest2'; port=25610; maxPlayers=16; targetPopulation=8; reservedHumanSlots=2; botNamePrefix='TSE2_Bot'; fleetConfig='f2.json' }
    )
}
$farmPath = "$testDir\farm.json"
$farm | ConvertTo-Json -Depth 4 | Set-Content $farmPath
$farmDry = & "$PSScriptRoot\Start-ServerFarm.ps1" -Config $farmPath -State "$testDir\farm-state.json" -DryRun | ConvertFrom-Json
if (@($farmDry.plan).Count -ne 2 -or $farmDry.plan[1].queryPort -ne 25611 -or
    $farmDry.plan[0].arguments -ne 'BotTest') {
    throw 'Farm dry-run plan failed.'
}
$dupPorts = @{ serverDir='C:\tse\server'; instances=@(
    @{ name='A'; port=25600; maxPlayers=16; targetPopulation=4; reservedHumanSlots=0; botNamePrefix='B'; fleetConfig='f.json' },
    @{ name='B'; port=25600; maxPlayers=16; targetPopulation=4; reservedHumanSlots=0; botNamePrefix='B'; fleetConfig='f.json' }) }
$dupPath = "$testDir\farm-dup.json"
$dupPorts | ConvertTo-Json -Depth 4 | Set-Content $dupPath
Expect-Throw { & "$PSScriptRoot\Start-ServerFarm.ps1" -Config $dupPath -State "$testDir\farm-dup-state.json" -DryRun } 'distinct ports' 'duplicate farm ports'

Write-Output "ALL FLEET/POPULATION CHECKS PASSED ($testDir)"
