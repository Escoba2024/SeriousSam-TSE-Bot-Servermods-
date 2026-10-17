param(
 [Parameter(Mandatory)][string]$Config,
 [Parameter(Mandatory)][string]$StateDirectory,
 [ValidateRange(0,16)][int]$TargetPopulation=8,
 [ValidateRange(0,15)][int]$ReservedHumanSlots=2,
 [ValidateRange(100,5000)][int]$PollMilliseconds=1000,
 [ValidateRange(0,100000)][int]$Iterations=0,
 [switch]$ObserveOnly,
 [string]$FleetState,
 [string]$WatchdogSession
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
Invoke-PopulationSupervisor @PSBoundParameters
