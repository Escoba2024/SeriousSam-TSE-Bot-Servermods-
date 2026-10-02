param(
    [Parameter(Mandatory=$true)][string]$Config,
    [Parameter(Mandatory=$true)][string]$StateDir,
    [int]$TargetPopulation = 12,
    [int]$ReservedHumanSlots = 2,
    [int]$MaxPlayers = 16,
    [int]$PollSeconds = 10,
    [uint32]$PresenceSeed = 1,
    [switch]$Once,
    [switch]$DryRun
)
# Phase 5: Population Manager. Haelt die Gesamtspielerzahl eines EINZELNEN
# unveraenderten Dedicated Servers auf TargetPopulation, priorisiert Menschen
# (ReservedHumanSlots bleiben immer frei) und startet/stoppt dafuer ganze
# Bot-Client-Prozesse aus der Fleet-Konfiguration (Phase 3).
#
# Phase 6 (Presence): Join-/Leave-Aktionen werden deterministisch gejittert
# (LCG-Seed), damit keine mechanischen Muster entstehen. Chat kommt aus dem
# BotDriver selbst (bot_fChatPeriod, Phase6Presence.ini).
#
# Es gibt KEINE kuenstliche GetPlayersCount()-Semantik: gezaehlt wird nur die
# normale GameAgent-\players\-Antwort des unveraenderten Servers; Bots werden
# ausschliesslich ueber ihren Namenspraefix erkannt.
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\PopulationCore.ps1"

$fleet = Get-FleetConfig -Path $Config
if ($null -eq $fleet.botNamePrefix) { throw 'Population management needs botNamePrefix in the fleet config.' }
if ($null -eq $fleet.queryPort) { throw 'Population management needs queryPort in the fleet config.' }
$serverHost = ($fleet.server -split ':')[0]
$plan = Get-FleetPlan -Config $fleet
if (!(Test-Path -LiteralPath $StateDir)) { New-Item -ItemType Directory $StateDir | Out-Null }
$stateFile = Join-Path $StateDir 'population-state.json'
$lcg = New-BotLcg -Seed $PresenceSeed

function Read-RunningProcesses {
    if (!(Test-Path -LiteralPath $stateFile)) { return @() }
    $entries = @((Get-Content -Raw -LiteralPath $stateFile | ConvertFrom-Json))
    return @($entries | Where-Object {
        $process = Get-Process -Id $_.pid -ErrorAction SilentlyContinue
        $null -ne $process -and $process.Path -eq $_.exe
    })
}

function Write-RunningProcesses([object[]]$Entries) {
    ConvertTo-Json @($Entries) -Depth 4 | Set-Content -LiteralPath $stateFile
}

function Invoke-ServerQuery([string]$Request) {
    $udp = [Net.Sockets.UdpClient]::new()
    $udp.Client.ReceiveTimeout = 2000
    try {
        $udp.Connect($serverHost, [int]$fleet.queryPort)
        $bytes = [Text.Encoding]::ASCII.GetBytes($Request)
        [void]$udp.Send($bytes, $bytes.Length)
        $peer = [Net.IPEndPoint]::new([Net.IPAddress]::Any, 0)
        return [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
    } finally { $udp.Dispose() }
}

do {
    $players = Invoke-ServerQuery '\players\'
    $classified = Get-PlayerClassification -PlayersReply $players -BotNamePrefix $fleet.botNamePrefix
    $running = Read-RunningProcesses
    $action = Get-PopulationAction -MaxPlayers $MaxPlayers -Humans $classified.Humans `
        -Bots $classified.Bots -TargetPopulation $TargetPopulation `
        -ReservedHumanSlots $ReservedHumanSlots
    $step = [ordered]@{
        utc = [DateTime]::UtcNow.ToString('o')
        humans = $classified.Humans; bots = $classified.Bots
        runningProcesses = $running.Count; action = $action
    }

    if ($action -eq 'StartBot') {
        $used = @($running | ForEach-Object clientDir)
        $candidate = @($plan | Where-Object { $used -notcontains $_.clientDir })
        if ($candidate.Count -eq 0) {
            $step.note = 'No idle bot-client installation left; extend the fleet config.'
        } else {
            $delay = Get-BotLcgRange $lcg 5 90   # Phase 6: join delay, never instant
            $step.joinDelaySeconds = $delay
            if ($DryRun) {
                $step.note = "DRYRUN would start $($candidate[0].exe) after ${delay}s"
            } else {
                Start-Sleep -Seconds $delay
                $process = Start-Process $candidate[0].exe -ArgumentList $candidate[0].arguments `
                    -WorkingDirectory $candidate[0].workingDir -WindowStyle Hidden -PassThru
                $running = @($running) + @([pscustomobject]@{
                    pid = $process.Id; exe = $candidate[0].exe
                    clientDir = $candidate[0].clientDir
                    localPlayers = $candidate[0].localPlayers
                    startedUtc = [DateTime]::UtcNow.ToString('o')
                })
                Write-RunningProcesses $running
                $step.startedPid = $process.Id
            }
        }
    } elseif ($action -eq 'StopBot') {
        if ($running.Count -eq 0) {
            $step.note = 'Server still reports bots but no managed process is running; manual check required.'
        } else {
            $victim = $running[$running.Count - 1]   # LIFO: newest bots leave first
            $delay = Get-BotLcgRange $lcg 2 30       # Phase 6: leave delay
            $step.leaveDelaySeconds = $delay
            if ($DryRun) {
                $step.note = "DRYRUN would stop PID $($victim.pid) after ${delay}s"
            } else {
                Start-Sleep -Seconds $delay
                $process = Get-Process -Id $victim.pid -ErrorAction SilentlyContinue
                if ($process -and $process.Path -eq $victim.exe) {
                    if (!$process.CloseMainWindow() -or !$process.WaitForExit(15000)) {
                        Stop-Process -Id $process.Id -Force
                        $step.forcedStop = $true
                    }
                }
                Write-RunningProcesses @($running | Where-Object pid -ne $victim.pid)
                $step.stoppedPid = $victim.pid
            }
        }
    }

    $step | ConvertTo-Json -Depth 4
    Add-Content -LiteralPath (Join-Path $StateDir 'population-log.jsonl') `
        -Value (($step | ConvertTo-Json -Depth 4 -Compress))
    if (!$Once) { Start-Sleep -Seconds $PollSeconds }
} while (!$Once)
