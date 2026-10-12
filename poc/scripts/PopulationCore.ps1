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
    if ($config.server -notmatch '^[\w.\-]+:(\d+)$') { throw 'Fleet server must be host:port.' }
    if ([double]$Matches[1] -lt 1 -or [double]$Matches[1] -gt 65535) { throw 'Invalid server port.' }
    if (@($config.processes).Count -lt 1) { throw 'Fleet config needs at least one process.' }
    $dirs = @()
    foreach ($process in $config.processes) {
        foreach ($field in @('clientDir','localPlayers','startupScript')) {
            if ($null -eq $process.$field) { throw "Fleet process misses '$field'." }
        }
        if ($process.localPlayers -notin 1,2,3,4) {
            throw 'localPlayers must be 1..4 (NET_MAXLOCALPLAYERS).'
        }
        if (![IO.Path]::IsPathRooted($process.clientDir)) { throw 'clientDir must be absolute.' }
        $process.clientDir = [IO.Path]::GetFullPath($process.clientDir).TrimEnd('\','/')
        if ($process.clientDir -match '["\r\n]' -or $process.startupScript -notmatch '^Scripts[\\/][\w.\\/-]+\.ini$') { throw 'Invalid client path or startupScript.' }
        if ($dirs -contains $process.clientDir) {
            throw 'Each fleet process needs its own bot-client installation (profiles/GUIDs/logs).'
        }
        $dirs += $process.clientDir
    }
    if ($null -eq $config.startStaggerSeconds) {
        $config | Add-Member startStaggerSeconds 10
    }
    if ($config.startStaggerSeconds -lt 0 -or $config.startStaggerSeconds -gt 60) { throw 'Invalid start stagger (0..60 seconds).' }
    return $config
}

# Read the native settings, not a BotDriver join override. PLC4 stores
# name/team as length-prefixed strings followed by a 16-byte character GUID.
function Read-RetailString($Reader) {
    $length = $Reader.ReadInt32()
    if ($length -lt 0 -or $length -gt 4096) { throw 'Invalid native string length.' }
    $bytes = $Reader.ReadBytes($length)
    if ($bytes.Length -ne $length) { throw 'Truncated native string.' }
    return [Text.Encoding]::ASCII.GetString($bytes)
}

function Get-FleetIdentities($Config) {
    $identities = @()
    foreach ($entry in $Config.processes) {
        $reader = [IO.BinaryReader]::new([IO.File]::OpenRead((Join-Path $entry.clientDir 'Data\SeriousSam.gms')))
        try {
            if ([Text.Encoding]::ASCII.GetString($reader.ReadBytes(8)) -ne 'GAMEV012') { throw 'Unsupported native game settings.' }
            Read-RetailString $reader | Out-Null
            $reader.ReadInt32() | Out-Null
            $reader.ReadInt32() | Out-Null
            $profiles = @(1..4 | ForEach-Object { $reader.ReadInt32() })
            if ($reader.ReadInt32() -ne $entry.localPlayers-1) { throw 'Native split-screen count differs from fleet localPlayers.' }
        } finally { $reader.Dispose() }
        foreach ($slot in 0..($entry.localPlayers-1)) {
            $profile = $profiles[$slot]
            if ($profile -lt 0 -or $profile -gt 7) { throw 'Invalid native profile index.' }
            $reader = [IO.BinaryReader]::new([IO.File]::OpenRead((Join-Path $entry.clientDir "Players\Player$profile.plr")))
            try {
                if ([Text.Encoding]::ASCII.GetString($reader.ReadBytes(4)) -ne 'PLC4') { throw 'Unsupported native player profile.' }
                $name = Read-RetailString $reader
                Read-RetailString $reader | Out-Null
                $guid = $reader.ReadBytes(16)
                if ($guid.Length -ne 16 -or ($guid | Measure-Object -Sum).Sum -eq 0 -or !$name -or $name -match '[\\\r\n]') { throw 'Invalid native player identity.' }
                # Steam retail may load the persistent GUID from a companion
                # file. Reject stale cloned companions instead of accepting
                # disjoint PLC4 GUIDs that will not reach the server.
                $sidecarPath=Join-Path $entry.clientDir "Players\Player$profile.plr.guid"
                $guidSource='profile'
                if(Test-Path -LiteralPath $sidecarPath){
                    $sidecar=[IO.File]::ReadAllBytes($sidecarPath)
                    if($sidecar.Length -ne 16 -or ($sidecar|Measure-Object -Sum).Sum -eq 0){throw 'Invalid native GUID sidecar.'}
                    if([BitConverter]::ToString($sidecar) -ne [BitConverter]::ToString($guid)){throw 'Native GUID sidecar differs from profile.'}
                    $guidSource='profile+sidecar'
                }
                $identities += [pscustomobject]@{clientDir=$entry.clientDir;slot=$slot;profile=$profile;name=$name;guid=[BitConverter]::ToString($guid);guidSource=$guidSource}
            } finally { $reader.Dispose() }
        }
    }
    if (@($identities.guid | Sort-Object -Unique).Count -ne $identities.Count -or
        @($identities.name | Sort-Object -Unique).Count -ne $identities.Count) { throw 'Duplicate fleet GUID or name.' }
    return ,$identities
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
