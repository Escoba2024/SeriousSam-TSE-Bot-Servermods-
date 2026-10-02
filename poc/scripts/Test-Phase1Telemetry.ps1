param(
    [Parameter(Mandatory=$true)][string]$BotLog,
    [Parameter(Mandatory=$true)][string]$Output,
    [switch]$QueryServer,
    [int]$SyncMinutes = 0,
    [ValidateRange(1,4)][int]$ExpectedPlayers = 1
)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $Output) { throw 'Use a new output file.' }
$rejected = 0
$samples = @(foreach ($line in Get-Content -LiteralPath $BotLog) {
    if ($line -match '^\[BotSnapshot\] tick=(\d+) player=(\d+) pos=\(([-\d.]+),([-\d.]+),([-\d.]+)\) yaw=([-\d.]+) health=([-\d.]+) buttons=(\d+) (.+)$') {
        $sample = [pscustomobject]@{
            tick=[int]$Matches[1]; player=[int]$Matches[2]
            x=[double]$Matches[3]; y=[double]$Matches[4]; z=[double]$Matches[5]
            yaw=[double]$Matches[6]; health=[double]$Matches[7]
            buttons=[uint32]$Matches[8]; info=$Matches[9]
        }
        if (!($sample.info -match ('\\frags_'+$sample.player+'\\(-?\d+)'))) {
            $rejected++
            continue
        }
        $sample | Add-Member frags ([int]$Matches[1])
        $sample
    } elseif ($line.Contains('[BotSnapshot]')) {
        $rejected++
    }
})
if ($samples.Count -eq 0) { throw 'No player snapshots found.' }
$players = @(foreach ($group in $samples | Group-Object player) {
    $rows = @($group.Group)
    [ordered]@{
        player=[int]$group.Name; samples=$rows.Count
        firstTick=$rows[0].tick; lastTick=$rows[-1].tick
        distinctPositions=@($rows | ForEach-Object { "$($_.x),$($_.y),$($_.z)" } | Sort-Object -Unique).Count
        distinctYaw=@($rows.yaw | Sort-Object -Unique).Count
        fireOnSamples=@($rows | Where-Object { $_.buttons -band 1 }).Count
        fireOffSamples=@($rows | Where-Object { !($_.buttons -band 1) }).Count
        minimumHealth=($rows.health | Measure-Object -Minimum).Minimum
        maximumHealth=($rows.health | Measure-Object -Maximum).Maximum
        minimumFrags=($rows.frags | Measure-Object -Minimum).Minimum
        maximumFrags=($rows.frags | Measure-Object -Maximum).Maximum
        healthChanges=@(for ($i=1; $i -lt $rows.Count; $i++) {
            if ($rows[$i].health -ne $rows[$i-1].health) { $rows[$i] }
        })
    }
})
$result = [ordered]@{
    capturedUtc=[DateTime]::UtcNow.ToString('o')
    botLog=(Resolve-Path -LiteralPath $BotLog).Path
    players=$players
    rejectedSnapshotLines=$rejected
    scope='Local replicated player snapshots; no visual or full Phase-1 pass assertion.'
}
if ($SyncMinutes -gt 0) {
    if ($rejected) { throw 'Malformed snapshots during sync run.' }
    if ($players.Count -ne $ExpectedPlayers) { throw 'Expected native player count does not match.' }
    $windows = @(foreach ($playerIndex in 0..($ExpectedPlayers-1)) {
      $rows = @($samples | Where-Object player -eq $playerIndex)
      if ($rows.Count -lt $SyncMinutes*1200) { throw 'Insufficient active native ticks for requested sync duration.' }
      for ($i=1; $i -lt $rows.Count; $i++) {
        if ($rows[$i].tick -le $rows[$i-1].tick) { throw 'Native tick counter restarted or duplicated during sync run.' }
      }
      $firstTick = $rows[0].tick
      for ($minute=0; $minute -lt $SyncMinutes; $minute++) {
        $part = @($rows | Where-Object { $_.tick -ge $firstTick+$minute*1200 -and $_.tick -lt $firstTick+($minute+1)*1200 })
        $entry = [ordered]@{
            player=$playerIndex; minute=$minute+1; samples=$part.Count
            positions=@($part | ForEach-Object { "$($_.x),$($_.y),$($_.z)" } | Sort-Object -Unique).Count
            yaw=@($part.yaw | Sort-Object -Unique).Count
            fireOn=@($part | Where-Object { $_.buttons -band 1 }).Count
            fireOff=@($part | Where-Object { !($_.buttons -band 1) }).Count
        }
        if ($entry.samples -lt 1190 -or $entry.positions -lt 10 -or $entry.yaw -lt 10 -or
            !$entry.fireOn -or !$entry.fireOff) {
            if ($ExpectedPlayers -eq 1) { throw "Native actions stalled in minute $($minute+1)." }
            throw "Native actions stalled for player $playerIndex in minute $($minute+1)."
        }
        $entry
      }
    })
    $result.activeSyncMinutes = $windows
}
if ($QueryServer) {
    $udp = [Net.Sockets.UdpClient]::new()
    $udp.Client.ReceiveTimeout = 2000
    try {
        $udp.Connect('127.0.0.1', 25601)
        $request = [Text.Encoding]::ASCII.GetBytes('\status\')
        [void]$udp.Send($request, $request.Length)
        $peer = [Net.IPEndPoint]::new([Net.IPAddress]::Any, 0)
        $result.serverStatus = [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
        $request = [Text.Encoding]::ASCII.GetBytes('\players\')
        [void]$udp.Send($request, $request.Length)
        $result.serverPlayers = [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
    } finally { $udp.Dispose() }
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Output
$result | ConvertTo-Json -Depth 6
