param(
    [Parameter(Mandatory=$true)][string]$BotLog,
    [Parameter(Mandatory=$true)][string]$Output,
    [switch]$QueryServer
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
if ($QueryServer) {
    $udp = [Net.Sockets.UdpClient]::new()
    $udp.Client.ReceiveTimeout = 2000
    try {
        $udp.Connect('127.0.0.1', 25601)
        $request = [Text.Encoding]::ASCII.GetBytes('\status\')
        [void]$udp.Send($request, $request.Length)
        $peer = [Net.IPEndPoint]::new([Net.IPAddress]::Any, 0)
        $result.serverStatus = [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
    } finally { $udp.Dispose() }
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Output
$result | ConvertTo-Json -Depth 6
