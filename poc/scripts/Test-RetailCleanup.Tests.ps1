param(
    [Parameter(Mandatory=$true)][string]$Dll,
    [Parameter(Mandatory=$true)][string]$Evidence
)
$ErrorActionPreference = 'Stop'
$retail = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) '.codex\retail'
$race = @{ injected = $false }
function Stop-Process {
    param([int]$Id, [switch]$Force)
    Microsoft.PowerShell.Management\Stop-Process -Id $Id -Force:$Force
    if (!$race.injected) {
        $race.injected = $true
        throw 'Simulated process-exit race after successful termination.'
    }
}
& "$PSScriptRoot\Test-RetailJoin.ps1" -Dll $Dll -Evidence $Evidence -Seconds 30 -Observer -CaptureObserver | Out-Null
if (!$race.injected) { throw 'Race was not injected.' }
foreach ($copy in 'BotClient','Observer') {
    $name = "TSE-$copy"
    $before = (Get-FileHash "$Evidence\$name-PersistentSymbols-before.ini").Hash
    $after = (Get-FileHash "$retail\$name\Scripts\PersistentSymbols.ini").Hash
    if ($before -ne $after) { throw "Config restore failed: $name" }
}
if (Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object Path -like "$retail\*") {
    throw 'An isolated test process survived cleanup.'
}
if (Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue) { throw 'Test port survived cleanup.' }
$capture = Get-Content -Raw "$Evidence\capture.json" | ConvertFrom-Json
if ($capture.count -lt 1) { throw 'Native capture produced no evidence.' }
foreach ($log in 'Dedicated_BotTest.log','SeriousSam.log','observer-SeriousSam.log') {
    if (!(Test-Path "$Evidence\$log")) { throw "Missing evidence: $log" }
}
'ALL CLEANUP RACE CHECKS PASSED'
