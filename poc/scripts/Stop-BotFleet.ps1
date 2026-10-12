param(
    [Parameter(Mandatory=$true)][string]$State,
    [ValidateRange(0,60)][int]$GracefulWaitSeconds = 15
)
# Phase 3: beendet eine mit Start-BotFleet.ps1 gestartete Flotte.
# Erst CloseMainWindow() (nativer Quit-/Renderer-Cleanup-Pfad, Retail-Exitcode 1),
# nach Ablauf der Wartezeit Process.Kill als harter Fallback (der dann KEINEN
# regulaeren Shutdown beweist - im Protokoll vermerken).
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath ($State + '.stopped.json')) { throw 'Existing stop evidence must not be overwritten.' }
$fleet = Get-Content -Raw -LiteralPath $State | ConvertFrom-Json
$results = @()
foreach ($entry in $fleet.processes) {
    $outcome = [ordered]@{ pid = $entry.pid; exe = $entry.exe }
    $process = Get-Process -Id $entry.pid -ErrorAction SilentlyContinue
    # Pin before reading identity metadata: opening a handle only after the
    # timestamp check could attach to a PID recycled between the two steps.
    if($null -ne $process){[void]$process.Handle}
    # ConvertFrom-Json may return DateTime rather than an ISO string. Compare
    # UTC instants with full tick precision, preserving the PID-reuse guard.
    $expectedStart=$null
    try{if($entry.startedUtc){$expectedStart=([datetimeoffset]$entry.startedUtc).UtcDateTime}}catch{}
    if ($null -eq $process -or $process.Path -ne $entry.exe -or
        $null -eq $expectedStart -or $process.StartTime.ToUniversalTime().Ticks -ne $expectedStart.Ticks) {
        $outcome.state = 'not-running'
    } else {
        # Pin the verified process handle before it exits. Get-Process objects
        # otherwise may lose ExitCode; the fallback also uses this handle,
        # rather than looking up a potentially reused PID again.
        $closed = $process.CloseMainWindow()
        if ($closed -and $process.WaitForExit($GracefulWaitSeconds * 1000)) {
            $text = Get-Content -LiteralPath (Join-Path $entry.clientDir 'SeriousSam.log') -Raw -ErrorAction SilentlyContinue
            $outcome.state = if ($process.ExitCode -eq 1 -and $text -match '(?s)Renderer buffers cleared\..*CDS: mode reset') { 'graceful' } else { 'window-exit-unverified' }
            $outcome.exitCode = $process.ExitCode
        } else {
            $process.Kill()
            $process.WaitForExit(5000) | Out-Null
            $outcome.state = 'forced'
            if (!$process.HasExited) { throw "Bot PID $($process.Id) did not stop." }
            $outcome.exitCode = $process.ExitCode
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
