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

if ((Test-Path -LiteralPath $State) -or (Test-Path -LiteralPath ($State + '.rollback.json'))) { throw 'Use a new fleet state file.' }
$fleet = Get-FleetConfig -Path $Config
$plan = Get-FleetPlan -Config $fleet

if ($DryRun) {
    [pscustomobject]@{ dryRun=$true; server=$fleet.server; plan=$plan } |
        ConvertTo-Json -Depth 4
    return
}

foreach ($entry in $plan) {
    if (!(Test-Path -LiteralPath $entry.exe)) { throw "Missing bot client: $($entry.exe)" }
    if (Get-Process SeriousSam -ErrorAction SilentlyContinue | Where-Object Path -eq $entry.exe) { throw 'Bot client installation already running.' }
}
$identities = Get-FleetIdentities $fleet
$statePath = [IO.Path]::GetFullPath($State)
if (!(Test-Path -LiteralPath (Split-Path $statePath -Parent))) { throw 'Fleet state parent directory must exist before launch.' }
# Prove state is writable before starting any child.
[IO.File]::WriteAllText($statePath, '{}')
$started = @()
$ownedProcesses = @()
$operationError = $null
$stateError = $null
try {
  try {
    foreach ($entry in $plan) {
        $process = Start-Process $entry.exe -ArgumentList $entry.arguments `
            -WorkingDirectory $entry.workingDir -WindowStyle Hidden -PassThru
        # Retain the actual child object before accessing metadata or writing state.
        $ownedProcesses += $process
        $started += [ordered]@{
            pid = $process.Id
            exe = $entry.exe
            clientDir = $entry.clientDir
            localPlayers = $entry.localPlayers
            startedUtc = $process.StartTime.ToUniversalTime().ToString('o')
        }
        Write-Output "Started $($entry.exe) (PID $($process.Id), $($entry.localPlayers) local bots)"
        if ($entry -ne $plan[-1]) { Start-Sleep -Seconds $fleet.startStaggerSeconds }
    }
  } catch {
    $operationError = $_
    throw
  } finally {
    try {
    [ordered]@{
        configPath = (Resolve-Path -LiteralPath $Config).Path
        server = $fleet.server
        processes = $started
        identities = $identities
        scope = 'Process bookkeeping only; joins, CRC and sync must be verified per TESTPROTOKOLL-PHASE-3.md.'
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $State
    } catch {
        $stateError = $_
        throw
    }
  }
} catch {
    $launchError = if ($operationError) { $operationError } else { $_ }
    $rollback = @()
    foreach ($process in $ownedProcesses) {
        $outcome = [ordered]@{ pid=$process.Id; state='failed' }
        try {
            # A failed launch is rolled back, not counted as regular shutdown.
            # Use retained process handles, never a fresh lookup of a reusable PID.
            if (!$process.HasExited) { $process.Kill() }
            if (!$process.WaitForExit(5000)) { throw 'Owned child did not stop.' }
            $outcome.state = 'stopped'
            $outcome.exitCode = $process.ExitCode
        } catch {
            $outcome.error = $_.Exception.Message
            Write-Warning "Fleet launch rollback failed for PID $($process.Id): $($_.Exception.Message)"
        }
        $rollback += $outcome
    }
    try {
        [ordered]@{failedUtc=[DateTime]::UtcNow.ToString('o');launchError=$launchError.Exception.Message;stateError=$(if($stateError){$stateError.Exception.Message});results=$rollback} |
            ConvertTo-Json -Depth 4 | Set-Content -LiteralPath ($State + '.rollback.json')
    } catch { Write-Warning "Could not write fleet rollback evidence: $($_.Exception.Message)" }
    throw $launchError
}
Write-Output "Fleet state written to $State"
