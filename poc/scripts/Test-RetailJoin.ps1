param(
    [Parameter(Mandatory=$true)][string]$Dll,
    [Parameter(Mandatory=$true)][string]$Evidence,
    [int]$Seconds = 30,
    [string]$Startup = '',
    [switch]$Observer,
    [switch]$VisibleClients,
    [switch]$CaptureObserver
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$retail = Join-Path $repo '.codex\retail'
$serverDir = Join-Path $retail 'TSE-Server'
$clientDir = Join-Path $retail 'TSE-BotClient'
$observerDir = Join-Path $retail 'TSE-Observer'
$clientWindowStyle = if ($VisibleClients) { 'Normal' } else { 'Hidden' }
$dllPath = (Resolve-Path -LiteralPath $Dll).Path
if ($CaptureObserver -and !$Observer) { throw 'CaptureObserver requires Observer.' }
if (Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "$retail\*"
}) {
    throw 'Existing isolated game/server process: stop it before this test.'
}
if (Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue) {
    throw 'Test UDP ports are already in use.'
}
if (Test-Path -LiteralPath $Evidence) { throw 'Use a new evidence directory.' }
$out = (New-Item -ItemType Directory -Path $Evidence).FullName
Copy-Item "$clientDir\Bin\GameMP.dll" "$out\GameMP-before.dll"
foreach ($file in @("$serverDir\Dedicated_BotTest.log", "$clientDir\SeriousSam.log", "$clientDir\Bin\SeriousSam.RPT")) {
    if (Test-Path $file) { Move-Item -LiteralPath $file -Destination (Join-Path $out ('before-' + (Split-Path $file -Leaf))) }
}
Copy-Item -LiteralPath $dllPath -Destination "$clientDir\Bin\GameMP.dll"
$server = $null
$client = $null
$observerProcess = $null
$loaded = $false
$configBackups = @{}
try {
    if ($CaptureObserver) {
        $frames = @(Get-ChildItem "$observerDir\ScreenShots\Anim_*.tga" -ErrorAction SilentlyContinue |
            ForEach-Object { if ($_.BaseName -match '^Anim_(\d+)$') { [int]$Matches[1] } })
        $frameStart = 10000 + [int](($frames | Measure-Object -Maximum).Maximum)
        foreach ($directory in @($clientDir, $observerDir)) {
            $config = "$directory\Scripts\PersistentSymbols.ini"
            $backup = "$out\$(Split-Path $directory -Leaf)-PersistentSymbols-before.ini"
            Copy-Item -LiteralPath $config -Destination $backup
            $configBackups[$config] = $backup
            $settings = Get-Content -Raw -LiteralPath $config
            foreach ($setting in @{sam_bFullScreen=0; sam_iScreenSizeI=960; sam_iScreenSizeJ=540;
                sam_iMaxFPSActive=10; sam_iMaxFPSInactive=5; sam_bPauseOnMinimize=0}.GetEnumerator()) {
                $settings = $settings -replace ($setting.Key+'\s*=\s*[^;]*;'), ($setting.Key+'=(INDEX)'+$setting.Value+';')
            }
            if ($directory -eq $observerDir) { $settings += "`ndem_iAnimFrame = $frameStart;" }
            Set-Content -LiteralPath $config -Value $settings
        }
    }
    $server = Start-Process "$serverDir\Bin\DedicatedServer.exe" -ArgumentList 'BotTest' -WorkingDirectory "$serverDir\Bin" -WindowStyle Hidden -PassThru
    $deadline = [DateTime]::UtcNow.AddSeconds(20)
    do {
        Start-Sleep -Milliseconds 250
        $ready = (Test-Path "$serverDir\Dedicated_BotTest.log") -and ((Get-Content -Raw "$serverDir\Dedicated_BotTest.log") -match 'ALL OK: Dedicated server')
    } until ($ready -or $server.HasExited -or [DateTime]::UtcNow -gt $deadline)
    if (!$ready) { throw 'Dedicated server did not start.' }
    if ($Observer) {
        if (Test-Path "$observerDir\SeriousSam.log") { Move-Item "$observerDir\SeriousSam.log" "$out\before-observer.log" }
        $observerProcess = Start-Process "$observerDir\Bin\SeriousSam.exe" -ArgumentList '+connect 127.0.0.1:25600 +quickjoin' -WorkingDirectory "$observerDir\Bin" -WindowStyle $clientWindowStyle -PassThru
        $deadline = [DateTime]::UtcNow.AddSeconds(20)
        do {
            Start-Sleep -Milliseconds 250
            $ready = (Test-Path "$observerDir\SeriousSam.log") -and ((Get-Content -Raw "$observerDir\SeriousSam.log") -match '(?m)^\s*joined\s*$')
        } until ($ready -or $observerProcess.HasExited -or [DateTime]::UtcNow -gt $deadline)
        if (!$ready) { throw 'Vanilla observer did not join.' }
    }
    $args = '+connect 127.0.0.1:25600 +quickjoin'
    if ($Startup) { $args += ' +script ' + $Startup }
    $client = Start-Process "$clientDir\Bin\SeriousSam.exe" -ArgumentList $args -WorkingDirectory "$clientDir\Bin" -WindowStyle $clientWindowStyle -PassThru
    $started = [DateTime]::UtcNow
    $deadline = $started.AddSeconds($Seconds)
    do {
        Start-Sleep -Milliseconds 250
        if (!$client.HasExited -and !$loaded) {
            $loaded = @((Get-Process -Id $client.Id).Modules | Where-Object {$_.ModuleName -eq 'GameMP.dll'}).Count -gt 0
        }
    } until ($client.HasExited -or [DateTime]::UtcNow -gt $deadline)
    $alive = !$client.HasExited
    $exitCode = if ($alive) { $null } else { $client.ExitCode }
    $serverText = Get-Content -Raw "$serverDir\Dedicated_BotTest.log"
    $clientText = Get-Content -Raw "$clientDir\SeriousSam.log"
    $result = [ordered]@{
        dll = $dllPath; sha256 = (Get-FileHash $dllPath).Hash
        startedUtc = $started.ToString('o'); elapsedSeconds = ([DateTime]::UtcNow-$started).TotalSeconds
        loaded = $loaded; alive = $alive; exitCode = $exitCode
        crcChallenge = $serverText -match 'Sent CRC challenge'
        crcAccepted = $serverText -match 'CRC check OK'
        serverJoined = $serverText -match '(?m)^.+ joined\s*$'
        clientJoined = $clientText -match '(?m)^.+ joined\s*$'
    }
    if ($Observer) {
        $result.observerAlive = !$observerProcess.HasExited
        $result.observerSawBotJoin = (Get-Content -Raw "$observerDir\SeriousSam.log") -match 'TSE_Bot_PoC.* joined'
        $result.crcAcceptedCount = ([regex]::Matches($serverText, 'CRC check OK')).Count
    }
    $result | ConvertTo-Json | Set-Content "$out\result.json"
    $result | ConvertTo-Json | Write-Output
    if (!$alive -or !$result.crcAccepted -or !$result.serverJoined -or !$result.clientJoined) {
        throw 'Retail join/stability gate failed; evidence saved.'
    }
    if ($Observer -and (!$result.observerAlive -or !$result.observerSawBotJoin -or $result.crcAcceptedCount -ne 2)) { throw 'Observer/bot coexistence gate failed.' }
} finally {
    $cleanupErrors = @()
    try {
        foreach ($process in @($client,$observerProcess,$server)) {
            try {
                if ($process -and !$process.HasExited) {
                    Stop-Process -Id $process.Id -Force
                    $process.WaitForExit(5000) | Out-Null
                }
            } catch {
                if (!$process.HasExited) { $cleanupErrors += $_ }
            }
        }
    } finally {
        foreach ($config in $configBackups.Keys) {
            try { Copy-Item -LiteralPath $configBackups[$config] -Destination $config -Force }
            catch { $cleanupErrors += $_ }
        }
    }
    if ($CaptureObserver -and $null -ne $frameStart) {
        $screenshots = New-Item -ItemType Directory "$out\observer-screenshots"
        $captured = @(Get-ChildItem "$observerDir\ScreenShots\Anim_*.tga" -ErrorAction SilentlyContinue |
            Where-Object { $_.BaseName -match '^Anim_(\d+)$' -and [int]$Matches[1] -ge $frameStart })
        $captured | Move-Item -Destination $screenshots.FullName
        @{frameStart=$frameStart; count=$captured.Count; format='Native GameMP TGA; console overlays excluded'} |
            ConvertTo-Json | Set-Content "$out\capture.json"
        if ($captured.Count -eq 0) { Write-Warning 'No native capture frames; visual evidence is missing.' }
    }
    foreach ($file in @("$serverDir\Dedicated_BotTest.log", "$clientDir\SeriousSam.log", "$clientDir\Bin\SeriousSam.RPT")) {
        if (Test-Path $file) { Copy-Item -LiteralPath $file -Destination $out }
    }
    if ($Observer -and (Test-Path "$observerDir\SeriousSam.log")) { Copy-Item "$observerDir\SeriousSam.log" "$out\observer-SeriousSam.log" }
    if ($cleanupErrors.Count) { throw ($cleanupErrors | Out-String) }
}
