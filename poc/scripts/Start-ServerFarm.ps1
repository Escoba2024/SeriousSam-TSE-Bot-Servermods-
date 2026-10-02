param(
    [Parameter(Mandatory=$true)][string]$Config,
    [Parameter(Mandatory=$true)][string]$State,
    [switch]$DryRun
)
# Phase 7: startet mehrere UNVERAENDERTE Dedicated-Server-Instanzen aus einer
# gemeinsamen Installation mit getrennten Konfigurationen/Ports. Die Bot-
# Flotten je Instanz werden anschliessend separat mit Start-BotFleet.ps1 bzw.
# Manage-BotPopulation.ps1 (eigene fleetConfig je Instanz) betrieben.
# Auf dem Server wird weiterhin NIEMALS eine Binary getauscht.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\PopulationCore.ps1"

if (Test-Path -LiteralPath $State) { throw 'Use a new farm state file.' }
$farm = Get-Content -Raw -LiteralPath $Config | ConvertFrom-Json
if ($null -eq $farm.serverDir -or $null -eq $farm.instances) { throw "Farm config needs 'serverDir' and 'instances'." }
if (@($farm.instances).Count -lt 1) { throw 'Farm config needs at least one instance.' }
$ports = @(); $names = @()
foreach ($instance in $farm.instances) {
    foreach ($field in @('name','port','maxPlayers','targetPopulation','botNamePrefix','fleetConfig')) {
        if ($null -eq $instance.$field) { throw "Farm instance misses '$field'." }
    }
    if ($ports -contains $instance.port) { throw 'Farm instances must use distinct ports.' }
    if ($names -contains $instance.name) { throw 'Farm instances must use distinct config names.' }
    $ports += $instance.port; $names += $instance.name
}

$plan = @(foreach ($instance in $farm.instances) {
    [pscustomobject]@{
        name = $instance.name
        exe = Join-Path $farm.serverDir 'Bin\DedicatedServer.exe'
        arguments = $instance.name
        workingDir = Join-Path $farm.serverDir 'Bin'
        configDir = Join-Path $farm.serverDir ("Scripts\Dedicated\" + $instance.name)
        port = [int]$instance.port
        queryPort = [int]$instance.port + 1
        log = Join-Path $farm.serverDir ('Dedicated_' + $instance.name + '.log')
        fleetConfig = $instance.fleetConfig
    }
})

if ($DryRun) {
    [pscustomobject]@{ dryRun=$true; plan=$plan } | ConvertTo-Json -Depth 4
    return
}

foreach ($entry in $plan) {
    if (!(Test-Path -LiteralPath $entry.exe)) { throw "Missing DedicatedServer.exe: $($entry.exe)" }
    if (!(Test-Path -LiteralPath $entry.configDir)) {
        throw "Missing dedicated config '$($entry.configDir)'. Copy dedicated-config/, set net_iPort = $($entry.port); in init.ini."
    }
    $init = Get-Content -Raw (Join-Path $entry.configDir 'init.ini')
    if ($init -notmatch ('net_iPort\s*=\s*' + $entry.port + '\s*;')) {
        throw "init.ini of '$($entry.name)' must set net_iPort = $($entry.port); (distinct per instance)."
    }
}
$started = @()
try {
    foreach ($entry in $plan) {
        $process = Start-Process $entry.exe -ArgumentList $entry.arguments `
            -WorkingDirectory $entry.workingDir -WindowStyle Hidden -PassThru
        $deadline = [DateTime]::UtcNow.AddSeconds(20)
        do {
            Start-Sleep -Milliseconds 250
            $ready = (Test-Path $entry.log) -and ((Get-Content -Raw $entry.log) -match 'ALL OK: Dedicated server')
        } until ($ready -or $process.HasExited -or [DateTime]::UtcNow -gt $deadline)
        if (!$ready) { throw "Instance '$($entry.name)' did not start." }
        $started += [ordered]@{
            name = $entry.name; pid = $process.Id; port = $entry.port
            queryPort = $entry.queryPort; fleetConfig = $entry.fleetConfig
            startedUtc = [DateTime]::UtcNow.ToString('o')
        }
        Write-Output "Instance '$($entry.name)' running on port $($entry.port) (PID $($process.Id))"
    }
} finally {
    [ordered]@{
        configPath = (Resolve-Path -LiteralPath $Config).Path
        serverDir = $farm.serverDir
        instances = $started
        scope = 'Server process bookkeeping only; per-instance gates follow TESTPROTOKOLL-PHASE-4-7.md.'
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $State
}
Write-Output "Farm state written to $State"
