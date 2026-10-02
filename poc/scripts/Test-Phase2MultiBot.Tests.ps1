# Unit-Regressionen fuer Test-Phase2MultiBot.ps1 mit synthetischen Bot-Logs.
# Laufzeitunabhaengig: ersetzt keinen echten Retail-Lauf und keine Abnahme.
$ErrorActionPreference = 'Stop'
$testDir = Join-Path ([IO.Path]::GetTempPath()) ('tse-phase2-' + [guid]::NewGuid())
New-Item -ItemType Directory $testDir | Out-Null

function New-BotLog {
    param([int]$Bots = 2, [int]$Samples = 40, [switch]$Lockstep, [switch]$FrozenBot1,
          [switch]$DuplicateIndex, [switch]$DuplicateName, [switch]$ExtraSlot)
    $lines = @()
    for ($slot=0; $slot -lt $Bots; $slot++) {
        $index = if ($DuplicateIndex) { 2 } else { 2 + $slot }
        $name = if ($DuplicateName) { 'TSE_Bot_A' } else { 'TSE_Bot_' + [char](65+$slot) }
        $lines += "[BotDriver] local player $slot (player index $index) is now bot-driven: $name"
    }
    for ($tick=20; $tick -le 20*$Samples; $tick += 20) {
        for ($slot=0; $slot -lt $Bots; $slot++) {
            $frozen = $FrozenBot1 -and $slot -eq 1
            $x = if ($Lockstep) { $tick/10 } elseif ($frozen) { 5 } else { $tick/10 + 100*$slot }
            $z = if ($frozen) { 1 } else { $tick/20 }
            $h = if ($frozen) { 90 } else { ($tick/20)*2.25 + 90*$slot }
            $fire = if (($tick/20 + $slot) % 4 -eq 0) { 1 } else { 0 }
            $lines += "[BotDriver] bot$slot tick=$tick pos=($x.00,0.00,-$z.00) heading=$h fire=$fire"
        }
    }
    if ($ExtraSlot) { $lines += '[BotDriver] bot2 tick=400 pos=(1.00,0.00,-1.00) heading=0 fire=0' }
    return $lines
}

function Expect-Throw {
    param([string]$LogName, [string[]]$Lines, [string]$Pattern, [hashtable]$Params = @{})
    $log = "$testDir\$LogName.log"
    $Lines | Set-Content $log
    $thrown = $null
    try {
        & "$PSScriptRoot\Test-Phase2MultiBot.ps1" -BotLog $log -Output "$testDir\$LogName.json" @Params | Out-Null
    } catch { $thrown = $_.Exception.Message }
    if ($null -eq $thrown -or $thrown -notmatch $Pattern) {
        throw "Expected failure '$Pattern' for $LogName, got: $thrown"
    }
}

# PASS: two independent bots
$log = "$testDir\pass.log"
New-BotLog | Set-Content $log
& "$PSScriptRoot\Test-Phase2MultiBot.ps1" -BotLog $log -Output "$testDir\pass.json" | Out-Null
$result = Get-Content -Raw "$testDir\pass.json" | ConvertFrom-Json
if ($result.bots.Count -ne 2 -or $result.bots[0].name -ne 'TSE_Bot_A' -or
    $result.bots[1].playerIndex -ne 3 -or $result.bots[0].fireOnSamples -lt 1 -or
    $result.bots[0].distinctPositions -lt 10) {
    throw 'Phase-2 pass case produced wrong summary.'
}

# PASS: four bots
$log4 = "$testDir\pass4.log"
New-BotLog -Bots 4 | Set-Content $log4
& "$PSScriptRoot\Test-Phase2MultiBot.ps1" -BotLog $log4 -Output "$testDir\pass4.json" -ExpectedBots 4 | Out-Null

# evidence protection
$rejected = $false
try { & "$PSScriptRoot\Test-Phase2MultiBot.ps1" -BotLog $log -Output "$testDir\pass.json" | Out-Null }
catch { $rejected = $_.Exception.Message -eq 'Use a new output file.' }
if (!$rejected) { throw 'Existing evidence was not protected.' }

# FAIL regressions
Expect-Throw 'one-bot' (New-BotLog -Bots 1) 'Expected 2 bot-driven local players'
Expect-Throw 'dup-index' (New-BotLog -DuplicateIndex) 'Player indices of the local bots are not unique'
Expect-Throw 'dup-name' (New-BotLog -DuplicateName) 'Profile names of the local bots are not unique'
Expect-Throw 'lockstep' (New-BotLog -Lockstep) 'move in lockstep'
Expect-Throw 'frozen' (New-BotLog -FrozenBot1) 'positions look frozen'
Expect-Throw 'extra-slot' (New-BotLog -ExtraSlot) 'Activity from unexpected local slot 2'
Expect-Throw 'too-few' (New-BotLog -Samples 5) 'too few status samples'

Write-Output "ALL PHASE-2 MULTIBOT CHECKS PASSED ($testDir)"
