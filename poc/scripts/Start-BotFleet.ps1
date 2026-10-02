param(
    [Parameter(Mandatory=$true)][string]$Config,
    [Parameter(Mandatory=$true)][string]$State,
    [switch]$DryRun
)
# Phase 3: startet mehrere Bot-Client-Prozesse (je 1..4 lokale Bots) gegen
# EINEN unveraenderten Dedicated Server, gestaffelt (kein Join-Burst).
# Schreibt eine Statusdatei fuer Stop-BotFleet.ps1 / Manage-BotPopulation.ps1.
# -DryRun validiert die Konfiguration und gibt nur den Plan aus (testbar).
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\PopulationCore.ps1"

if (Test-Path -LiteralPath $State) { throw 'Use a new fleet state file.' }
$fleet = Get-FleetConfig -Path $Config
$plan = Get-FleetPlan -Config $fleet

if ($DryRun) {
    [pscustomobject]@{ dryRun=$true; server=$fleet.server; plan=$plan } |
        ConvertTo-Json -Depth 4
    return
}

foreach ($entry in $plan) {
    if (!(Test-Path -LiteralPath $entry.exe)) { throw "Missing bot client: $($entry.exe)" }
}
$started = @()
try {
    foreach ($entry in $plan) {
        $process = Start-Process $entry.exe -ArgumentList $entry.arguments `
            -WorkingDirectory $entry.workingDir -WindowStyle Hidden -PassThru
        $started += [ordered]@{
            pid = $process.Id
            exe = $entry.exe
            clientDir = $entry.clientDir
            localPlayers = $entry.localPlayers
            startedUtc = [DateTime]::UtcNow.ToString('o')
        }
        Write-Output "Started $($entry.exe) (PID $($process.Id), $($entry.localPlayers) local bots)"
        if ($entry -ne $plan[-1]) { Start-Sleep -Seconds $fleet.startStaggerSeconds }
    }
} finally {
    [ordered]@{
        configPath = (Resolve-Path -LiteralPath $Config).Path
        server = $fleet.server
        processes = $started
        scope = 'Process bookkeeping only; joins, CRC and sync must be verified per TESTPROTOKOLL-PHASE-3.md.'
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $State
}
Write-Output "Fleet state written to $State"
