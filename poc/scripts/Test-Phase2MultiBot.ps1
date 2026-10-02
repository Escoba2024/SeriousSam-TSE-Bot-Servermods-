param(
    [Parameter(Mandatory=$true)][string]$BotLog,
    [Parameter(Mandatory=$true)][string]$Output,
    [ValidateRange(2,4)][int]$ExpectedBots = 2,
    [int]$MinSamplesPerBot = 30,
    [int]$MinDistinctPositions = 10,
    [int]$MinDistinctHeadings = 10,
    [switch]$QueryServer,
    [string]$ServerHost = '127.0.0.1',
    [int]$ServerQueryPort = 25601
)
# Phase-2-Auswertung: mehrere lokale Bots in EINEM Bot-Client-Prozess.
# Liest ausschliesslich den Bot-Clientlog ([BotDriver]-Zeilen) und optional den
# unveraenderten GameAgent-Querypfad des Servers. Prueft Slot-/Index-/Namens-
# Eindeutigkeit und unabhaengige Aktivitaet pro Bot. Ersetzt KEINE visuelle
# Abnahme und keine Sync-Langlaeufe (TESTPROTOKOLL-PHASE-2.md).
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $Output) { throw 'Use a new output file.' }
$text = Get-Content -LiteralPath $BotLog

# 1) registration lines: slot -> player index -> profile name
$registrations = @(foreach ($line in $text) {
    if ($line -match '^\[BotDriver\] local player (\d+) \(player index (\d+)\) is now bot-driven: (.+)$') {
        [pscustomobject]@{ slot=[int]$Matches[1]; playerIndex=[int]$Matches[2]; name=$Matches[3].Trim() }
    }
})
if ($registrations.Count -eq 0) { throw 'No bot-driven local players found.' }
$slots = @($registrations | Group-Object slot)
$activeSlots = @($slots | ForEach-Object { [int]$_.Name } | Sort-Object)
if ($activeSlots.Count -ne $ExpectedBots) {
    throw "Expected $ExpectedBots bot-driven local players, found $($activeSlots.Count)."
}
if (($activeSlots -join ',') -ne ((0..($ExpectedBots-1)) -join ',')) {
    throw "Bot-driven slots are not 0..$($ExpectedBots-1): $($activeSlots -join ',')."
}
# the LAST registration per slot describes the current session (rejoin-safe)
$current = @(foreach ($group in $slots) { @($group.Group)[$group.Group.Count - 1] })
if (@($current.playerIndex | Sort-Object -Unique).Count -ne $ExpectedBots) {
    throw 'Player indices of the local bots are not unique.'
}
if (@($current.name | Sort-Object -Unique).Count -ne $ExpectedBots) {
    throw 'Profile names of the local bots are not unique; create distinct profiles.'
}

# 2) per-bot activity from the periodic [BotDriver] botN status lines
$activity = @(foreach ($line in $text) {
    if ($line -match '^\[BotDriver\] bot(\d+) tick=(\d+) pos=\(([-\d.]+),([-\d.]+),([-\d.]+)\) heading=([-\d.]+) fire=(\d)$') {
        [pscustomobject]@{ slot=[int]$Matches[1]; tick=[int]$Matches[2]
            pos="$($Matches[3]),$($Matches[4]),$($Matches[5])"
            heading=[double]$Matches[6]; fire=[int]$Matches[7] }
    }
})
$unexpected = @($activity | Where-Object { $_.slot -ge $ExpectedBots })
if ($unexpected.Count) { throw "Activity from unexpected local slot $($unexpected[0].slot)." }
$bots = @(foreach ($slot in 0..($ExpectedBots-1)) {
    $rows = @($activity | Where-Object slot -eq $slot)
    if ($rows.Count -lt $MinSamplesPerBot) { throw "Bot $slot has too few status samples ($($rows.Count))." }
    $entry = [ordered]@{
        slot=$slot
        playerIndex=@($current | Where-Object slot -eq $slot)[0].playerIndex
        name=@($current | Where-Object slot -eq $slot)[0].name
        samples=$rows.Count
        firstTick=$rows[0].tick; lastTick=$rows[$rows.Count-1].tick
        distinctPositions=@($rows.pos | Sort-Object -Unique).Count
        distinctHeadings=@($rows.heading | Sort-Object -Unique).Count
        fireOnSamples=@($rows | Where-Object fire -eq 1).Count
        fireOffSamples=@($rows | Where-Object fire -eq 0).Count
    }
    if ($entry.distinctPositions -lt $MinDistinctPositions) { throw "Bot $slot positions look frozen." }
    if ($entry.distinctHeadings -lt $MinDistinctHeadings) { throw "Bot $slot heading looks frozen." }
    if (!$entry.fireOnSamples -or !$entry.fireOffSamples) { throw "Bot $slot fire cadence missing." }
    $entry
})

# 3) independence: identical position sequences would mean lockstep clones
for ($a=0; $a -lt $ExpectedBots; $a++) {
    for ($b=$a+1; $b -lt $ExpectedBots; $b++) {
        $posA = @($activity | Where-Object slot -eq $a | ForEach-Object pos)
        $posB = @($activity | Where-Object slot -eq $b | ForEach-Object pos)
        $n = [Math]::Min($posA.Count, $posB.Count)
        $same = 0
        for ($i=0; $i -lt $n; $i++) { if ($posA[$i] -eq $posB[$i]) { $same++ } }
        if ($n -gt 0 -and $same / $n -gt 0.5) {
            throw "Bots $a and $b move in lockstep ($same of $n identical positions)."
        }
    }
}

$result = [ordered]@{
    capturedUtc=[DateTime]::UtcNow.ToString('o')
    botLog=(Resolve-Path -LiteralPath $BotLog).Path
    expectedBots=$ExpectedBots
    bots=$bots
    scope='Local bot-client log evaluation; no visual acceptance, no sync gate, no GUID byte proof (profile GUIDs are asserted via distinct profiles in the protocol).'
}

# 4) optional: the unmodified server-side view through the GameAgent query
if ($QueryServer) {
    $udp = [Net.Sockets.UdpClient]::new()
    $udp.Client.ReceiveTimeout = 2000
    try {
        $udp.Connect($ServerHost, $ServerQueryPort)
        $request = [Text.Encoding]::ASCII.GetBytes('\status\')
        [void]$udp.Send($request, $request.Length)
        $peer = [Net.IPEndPoint]::new([Net.IPAddress]::Any, 0)
        $result.serverStatus = [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
        $request = [Text.Encoding]::ASCII.GetBytes('\players\')
        [void]$udp.Send($request, $request.Length)
        $result.serverPlayers = [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
    } finally { $udp.Dispose() }
    if ($result.serverStatus -match '\\numplayers\\(\d+)') {
        $result.serverNumPlayers = [int]$Matches[1]
        if ($result.serverNumPlayers -lt $ExpectedBots) {
            throw "Server reports $($result.serverNumPlayers) players; expected at least $ExpectedBots."
        }
    } else { throw 'Server status reply did not contain numplayers.' }
    foreach ($bot in $bots) {
        $occurrences = [regex]::Matches($result.serverPlayers,
            [regex]::Escape('\'+$bot.name+'\')).Count
        if ($occurrences -ne 1) {
            throw "Bot name '$($bot.name)' appears $occurrences times in the server player list."
        }
    }
}

$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $Output
$result | ConvertTo-Json -Depth 5
