param(
    [Parameter(Mandatory=$true)][string]$State,
    [int]$GracefulWaitSeconds = 15
)
# Phase 3: beendet eine mit Start-BotFleet.ps1 gestartete Flotte.
# Erst CloseMainWindow() (nativer Quit-/Renderer-Cleanup-Pfad, Retail-Exitcode 1),
# nach Ablauf der Wartezeit Stop-Process als harter Fallback (der dann KEINEN
# regulaeren Shutdown beweist - im Protokoll vermerken).
$ErrorActionPreference = 'Stop'
$fleet = Get-Content -Raw -LiteralPath $State | ConvertFrom-Json
$results = @()
foreach ($entry in $fleet.processes) {
    $outcome = [ordered]@{ pid = $entry.pid; exe = $entry.exe }
    $process = Get-Process -Id $entry.pid -ErrorAction SilentlyContinue
    if ($null -eq $process -or $process.Path -ne $entry.exe) {
        $outcome.state = 'not-running'
    } else {
        $closed = $process.CloseMainWindow()
        if ($closed -and $process.WaitForExit($GracefulWaitSeconds * 1000)) {
            $outcome.state = 'graceful'
            $outcome.exitCode = $process.ExitCode
        } else {
            Stop-Process -Id $process.Id -Force
            $process.WaitForExit(5000) | Out-Null
            $outcome.state = 'forced'
        }
    }
    $results += $outcome
}
$stopped = [ordered]@{
    stoppedUtc = [DateTime]::UtcNow.ToString('o')
    results = $results
}
$stopped | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath ($State + '.stopped.json')
$stopped | ConvertTo-Json -Depth 4
if (@($results | Where-Object state -eq 'forced').Count) {
    Write-Warning 'At least one bot client needed a forced stop; no regular-shutdown evidence for it.'
}
