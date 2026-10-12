param(
    [Parameter(Mandatory=$true)][string]$Config,
    [Parameter(Mandatory=$true)][string]$Dll,
    [Parameter(Mandatory=$true)][string]$Backup,
    [string]$ExpectedDllHash='61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9'
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot\LocalBotReleaseCore.ps1"
$fleet=Get-FleetConfig -Path $Config
if(!$fleet.botNamePrefix -or $fleet.botNamePrefix -notmatch '^[A-Za-z0-9_]{1,24}$'){throw 'Expected a short ASCII botNamePrefix.'}
if((Get-FileHash -LiteralPath $Dll).Hash -ne $ExpectedDllHash){throw 'Release DLL hash does not match.'}
if(Test-Path -LiteralPath $Backup){throw 'Use a new backup directory.'}
Assert-LocalBotClientsStopped $fleet
$startup=Join-Path $PSScriptRoot 'LocalBotRelease.ini'
$plan=New-LocalBotReleasePlan $fleet $Dll $startup
# All native formats are validated before the first filesystem mutation.
$backupPath=(New-Item -ItemType Directory -Path $Backup).FullName
$saved=@()
foreach($entry in $plan){
    $exists=Test-Path -LiteralPath $entry.path -PathType Leaf
    $copy=Join-Path $backupPath "$($saved.Count).original"
    $hash=$null
    if($exists){Copy-Item -LiteralPath $entry.path -Destination $copy; $hash=(Get-FileHash -LiteralPath $copy).Hash}
    $saved+=@([pscustomobject]@{path=$entry.path;existed=$exists;backup=$copy;sha256=$hash})
}
$native=@(foreach($entry in $fleet.processes){foreach($name in 'SeriousSam.exe','Engine.dll','EntitiesMP.dll'){
    $path=Join-Path $entry.clientDir "Bin\$name"
    [pscustomobject]@{path=$path;sha256=(Get-FileHash -LiteralPath $path).Hash}
}})
$manifest=[ordered]@{prepared=$false;config=(Resolve-Path -LiteralPath $Config).Path;fleet=$fleet;dllSha256=$ExpectedDllHash;files=$saved;native=$native}
$manifestPath=Join-Path $backupPath 'manifest.json'
$manifest|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $manifestPath
try{
    foreach($entry in $plan){[IO.File]::WriteAllBytes($entry.path,$entry.bytes)}
    $identities=Get-FleetIdentities $fleet
    foreach($entry in $native){if((Get-FileHash -LiteralPath $entry.path).Hash -ne $entry.sha256){throw 'Native engine/entity/executable changed.'}}
    $manifest.prepared=$true
    $manifest['identities']=$identities
    $manifest|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $manifestPath
}catch{
    $operationError=$_
    try{& "$PSScriptRoot\Restore-LocalBotRelease.ps1" -Backup $backupPath|Out-Null}catch{Write-Warning "Preparation rollback failed: $($_.Exception.Message)"}
    throw $operationError
}
"PREPARED: $($identities.Count) distinct native bots; backup $manifestPath"
"START: & '$PSScriptRoot\Start-BotFleet.ps1' -Config '$Config' -State '<new fleet-state.json>'"
