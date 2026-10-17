param(
 [Parameter(Mandatory)][string]$Config,
 [Parameter(Mandatory)][string]$StateDirectory,
 [ValidateRange(0,16)][int]$TargetPopulation=8,
 [ValidateRange(0,15)][int]$ReservedHumanSlots=2,
 [ValidateRange(100,5000)][int]$PollMilliseconds=1000,
 [ValidateRange(0,100000)][int]$Iterations=0
)
# Opt-in external guardian; launch this instead of Manage-BotPopulation.
$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
$fleet=Get-FleetConfig $Config
Get-FleetIdentities $fleet|Out-Null
$configPath=(Resolve-Path -LiteralPath $Config).Path
$statePath=[IO.Path]::GetFullPath($StateDirectory).TrimEnd('\','/')
if(Test-Path -LiteralPath $statePath){throw 'Use a new supervisor state directory.'}
$shell=(Get-Process -Id $PID).Path
$controllerScript=Join-Path $PSScriptRoot 'Manage-BotPopulation.ps1'
# Reject shell argument delimiters. Use a script file, never interpolated -Command.
foreach($path in $configPath,$statePath,$controllerScript){if($path -match '["\r\n]'){throw 'Unsupported path characters.'}}
$start={param($sessionPath)
 $arguments='-NoProfile -ExecutionPolicy Bypass -File "'+$controllerScript+'" -Config "'+$configPath+'" -StateDirectory "'+$statePath+'" -WatchdogSession "'+$sessionPath+'" -TargetPopulation '+$TargetPopulation+' -ReservedHumanSlots '+$ReservedHumanSlots+' -PollMilliseconds '+$PollMilliseconds+' -Iterations '+$Iterations
 Start-Process -FilePath $shell -ArgumentList $arguments -WindowStyle Hidden -PassThru
}.GetNewClosure()
Invoke-PopulationWatchdog -Plans (Get-FleetPlan $fleet) -Directories @($fleet.processes.clientDir) -StateDirectory ($statePath+'.watchdog') -StartController $start
