param(
    [Parameter(Mandatory=$true)][string]$State
)
# Phase 7: beendet die mit Start-ServerFarm.ps1 gestarteten Instanzen.
# Bot-Flotten VORHER mit Stop-BotFleet.ps1 beenden, damit der Serverlog die
# regulaeren Disconnects enthaelt.
$ErrorActionPreference = 'Stop'
$farm = Get-Content -Raw -LiteralPath $State | ConvertFrom-Json
$results = @()
foreach ($instance in $farm.instances) {
    $outcome = [ordered]@{ name = $instance.name; pid = $instance.pid }
    $process = Get-Process -Id $instance.pid -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        $outcome.state = 'not-running'
    } else {
        Stop-Process -Id $process.Id    # DedicatedServer: console process, exit 0 expected
        if (!$process.WaitForExit(10000)) {
            Stop-Process -Id $process.Id -Force
            $outcome.state = 'forced'
        } else {
            $outcome.state = 'stopped'
            $outcome.exitCode = $process.ExitCode
        }
    }
    $results += $outcome
}
$stopped = [ordered]@{ stoppedUtc = [DateTime]::UtcNow.ToString('o'); results = $results }
$stopped | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath ($State + '.stopped.json')
$stopped | ConvertTo-Json -Depth 4
