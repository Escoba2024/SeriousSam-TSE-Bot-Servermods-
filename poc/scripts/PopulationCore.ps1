# PopulationCore.ps1 - reine Entscheidungslogik fuer Phase 3/5/7-Skripte.
# Wird von Start-BotFleet.ps1 / Manage-BotPopulation.ps1 / Start-ServerFarm.ps1
# dot-sourced und von den .Tests.ps1-Dateien direkt getestet. Keine Prozess-
# oder Netzwerkzugriffe in dieser Datei.
#
# Die Populationsregeln sind der exakte Spiegel von botcore_ai.h
# (botcore::DesiredBots / PopulationStep); beide Seiten werden durch die
# jeweiligen Unit-Tests auf dieselbe Szenariotabelle geprueft.
$ErrorActionPreference = 'Stop'

function Get-DesiredBots {
    param([Parameter(Mandatory=$true)][int]$MaxPlayers,
          [Parameter(Mandatory=$true)][int]$Humans,
          [Parameter(Mandatory=$true)][int]$TargetPopulation,
          [int]$ReservedHumanSlots = 0)
    $desired = $TargetPopulation - $Humans
    $capacity = $MaxPlayers - $Humans - $ReservedHumanSlots
    if ($desired -gt $capacity) { $desired = $capacity }
    if ($desired -lt 0) { $desired = 0 }
    return $desired
}

function Get-PopulationAction {
    param([Parameter(Mandatory=$true)][int]$MaxPlayers,
          [Parameter(Mandatory=$true)][int]$Humans,
          [Parameter(Mandatory=$true)][int]$Bots,
          [Parameter(Mandatory=$true)][int]$TargetPopulation,
          [int]$ReservedHumanSlots = 0)
    $desired = Get-DesiredBots -MaxPlayers $MaxPlayers -Humans $Humans `
        -TargetPopulation $TargetPopulation -ReservedHumanSlots $ReservedHumanSlots
    if ($Bots -gt $desired) { return 'StopBot' }
    if ($Bots -lt $desired -and ($Humans + $Bots) -lt ($MaxPlayers - $ReservedHumanSlots)) {
        return 'StartBot'
    }
    return 'None'
}

# Deterministischer LCG (identische Konstanten wie botcore::Lcg), damit
# Join-/Leave-Verzoegerungen reproduzierbar und pro Instanz verschieden sind.
function New-BotLcg {
    param([uint32]$Seed)
    if ($Seed -eq 0) { $Seed = 1 }
    return [pscustomobject]@{ State = [uint32]$Seed }
}

function Get-BotLcgNext {
    param([Parameter(Mandatory=$true)]$Lcg)
    $Lcg.State = [uint32](([uint64]$Lcg.State * 1664525 + 1013904223) % 4294967296)
    return $Lcg.State
}

function Get-BotLcgRange {
    param([Parameter(Mandatory=$true)]$Lcg,
          [Parameter(Mandatory=$true)][int]$Minimum,
          [Parameter(Mandatory=$true)][int]$Maximum)
    $span = [uint32]($Maximum - $Minimum + 1)
    return $Minimum + [int]((([uint32](Get-BotLcgNext $Lcg)) -shr 8) % $span)
}

# Fleet-Konfiguration (Phase 3) validieren; liefert das geparste Objekt.
function Get-FleetConfig {
    param([Parameter(Mandatory=$true)][string]$Path)
    $config = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    foreach ($field in @('server','processes')) {
        if ($null -eq $config.$field) { throw "Fleet config misses '$field'." }
    }
    if ($config.server -notmatch '^[\w.\-]+:\d+$') { throw 'Fleet server must be host:port.' }
    if (@($config.processes).Count -lt 1) { throw 'Fleet config needs at least one process.' }
    $dirs = @()
    foreach ($process in $config.processes) {
        foreach ($field in @('clientDir','localPlayers','startupScript')) {
            if ($null -eq $process.$field) { throw "Fleet process misses '$field'." }
        }
        if ($process.localPlayers -lt 1 -or $process.localPlayers -gt 4) {
            throw 'localPlayers must be 1..4 (NET_MAXLOCALPLAYERS).'
        }
        if ($dirs -contains $process.clientDir) {
            throw 'Each fleet process needs its own bot-client installation (profiles/GUIDs/logs).'
        }
        $dirs += $process.clientDir
    }
    if ($null -eq $config.startStaggerSeconds) {
        $config | Add-Member startStaggerSeconds 10
    }
    return $config
}

# Geplante Startkommandos einer Fleet-Konfiguration (fuer -DryRun und Tests).
function Get-FleetPlan {
    param([Parameter(Mandatory=$true)]$Config)
    $plan = @()
    foreach ($process in $Config.processes) {
        $plan += [pscustomobject]@{
            exe = Join-Path $process.clientDir 'Bin\SeriousSam.exe'
            workingDir = Join-Path $process.clientDir 'Bin'
            arguments = '+connect ' + $Config.server + ' +quickjoin +script ' + $process.startupScript
            localPlayers = [int]$process.localPlayers
            clientDir = $process.clientDir
        }
    }
    return ,$plan
}

# Spieler aus einer GameAgent-\players\-Antwort zaehlen und nach Bot-Praefix
# klassifizieren. Rueckgabe: @{Humans=..; Bots=..; Names=..}.
function Get-PlayerClassification {
    param([Parameter(Mandatory=$true)][string]$PlayersReply,
          [Parameter(Mandatory=$true)][string]$BotNamePrefix)
    $names = @([regex]::Matches($PlayersReply, '\\player_\d+\\([^\\]+)') |
        ForEach-Object { $_.Groups[1].Value })
    $bots = @($names | Where-Object { $_.StartsWith($BotNamePrefix) })
    return [pscustomobject]@{
        Names = $names
        Humans = $names.Count - $bots.Count
        Bots = $bots.Count
    }
}
