param([Parameter(Mandatory=$true)][string]$Evidence)
$ErrorActionPreference='Stop'
$ev=(New-Item -ItemType Directory -Path $Evidence).FullName
$config=[ordered]@{server='127.0.0.1:25600';queryPort=25601;botNamePrefix='TSE_Bot';startStaggerSeconds=0;processes=@()}
$before=@{}
foreach($name in 'TSE-BotClient','TSE-BotClient2'){
    $dir=Join-Path $ev $name
    New-Item -ItemType Directory -Path "$dir\Bin","$dir\Data\Var","$dir\Players","$dir\Scripts"|Out-Null
    foreach($file in 'SeriousSam.exe','Engine.dll','EntitiesMP.dll','GameMP.dll'){[IO.File]::WriteAllBytes("$dir\Bin\$file",[byte[]](1,2,3,4,5))}
    [IO.File]::WriteAllText("$dir\Data\Var\Sam_Version.var",'v1.07')
    [IO.File]::WriteAllText("$dir\Scripts\PersistentSymbols.ini",'sam_bFullScreen=1;sam_bPauseOnMinimize=1;sam_iMaxFPSActive=200;sam_iMaxFPSInactive=200;sam_iScreenSizeI=640;sam_iScreenSizeJ=480;')
    # Native binary shapes with an empty initial string and four selected profiles.
    [IO.File]::WriteAllBytes("$dir\Data\SeriousSam.gms",[byte[]]([Text.Encoding]::ASCII.GetBytes('GAMEV012')+[byte[]]::new(32)))
    foreach($slot in 0..3){
        [IO.File]::WriteAllBytes("$dir\Players\Player$slot.plr",[byte[]]([Text.Encoding]::ASCII.GetBytes('PLC4')+[byte[]]::new(56)))
        if($slot -eq 0){[IO.File]::WriteAllBytes("$dir\Players\Player$slot.plr.guid",[byte[]]::new(16))}
    }
    foreach($file in Get-ChildItem -LiteralPath $dir -File -Recurse){$before[$file.FullName]=(Get-FileHash -LiteralPath $file.FullName).Hash}
    $config.processes+=@([pscustomobject]@{clientDir=$dir;localPlayers=4;startupScript='Scripts\LocalBotRelease.ini'})
}
$configPath=Join-Path $ev 'fleet.json'
$config|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $configPath
$dll=Join-Path $ev 'fixture.dll'
[IO.File]::WriteAllBytes($dll,[byte[]](7,8,9))
$hash=(Get-FileHash -LiteralPath $dll).Hash
& "$PSScriptRoot\Initialize-LocalBotRelease.ps1" -Config $configPath -Dll $dll -ExpectedDllHash $hash -Backup "$ev\backup"|Out-Null
. "$PSScriptRoot\PopulationCore.ps1"
$ids=Get-FleetIdentities (Get-FleetConfig $configPath)
if($ids.Count -ne 8 -or @($ids.guid|Sort-Object -Unique).Count -ne 8 -or @($ids.name|Sort-Object -Unique).Count -ne 8){throw 'Preparation did not create eight distinct native identities.'}
foreach($entry in $config.processes){
    if((Get-FileHash -LiteralPath "$($entry.clientDir)\Bin\GameMP.dll").Hash -ne $hash){throw 'Candidate staging failed.'}
    foreach($file in 'SeriousSam.exe','Engine.dll','EntitiesMP.dll'){
        $path="$($entry.clientDir)\Bin\$file"
        if((Get-FileHash -LiteralPath $path).Hash -ne $before[$path]){throw 'Protected native file changed.'}
    }
}
& "$PSScriptRoot\Restore-LocalBotRelease.ps1" -Backup "$ev\backup"|Out-Null
foreach($entry in $before.GetEnumerator()){
    if((Get-FileHash -LiteralPath $entry.Key).Hash -ne $entry.Value){throw 'Original native fixture hash not restored.'}
}
foreach($entry in $config.processes){
    if(Test-Path -LiteralPath "$($entry.clientDir)\Scripts\LocalBotRelease.ini"){throw 'Previously absent startup file remains.'}
    foreach($slot in 1..3){if(Test-Path -LiteralPath "$($entry.clientDir)\Players\Player$slot.plr.guid"){throw 'Previously absent sidecar remains.'}}
}
# Bad native format must be rejected before creating backup or changing siblings.
[IO.File]::WriteAllBytes("$($config.processes[1].clientDir)\Players\Player3.plr",[byte[]](1,2,3))
$rejected=$false
try{& "$PSScriptRoot\Initialize-LocalBotRelease.ps1" -Config $configPath -Dll $dll -ExpectedDllHash $hash -Backup "$ev\bad-format-backup"|Out-Null}catch{if($_.Exception.Message -notmatch 'Unsupported native player'){throw};$rejected=$true}
if(!$rejected -or (Test-Path -LiteralPath "$ev\bad-format-backup")){throw 'Invalid native input was not rejected before writes.'}
foreach($entry in $before.GetEnumerator()|Where-Object Key -ne "$($config.processes[1].clientDir)\Players\Player3.plr"){
    if((Get-FileHash -LiteralPath $entry.Key).Hash -ne $entry.Value){throw 'Bad input changed another native file.'}
}
& "$PSScriptRoot\Restore-LocalBotRelease.ps1" -Backup "$ev\backup"|Out-Null
$config.processes[0].startupScript='Scripts\..\..\outside.ini'
$config|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $configPath
$rejected=$false
try{& "$PSScriptRoot\Initialize-LocalBotRelease.ps1" -Config $configPath -Dll $dll -ExpectedDllHash $hash -Backup "$ev\bad-path-backup"|Out-Null}catch{if($_.Exception.Message -notmatch 'Startup path escapes'){throw};$rejected=$true}
if(!$rejected -or (Test-Path -LiteralPath "$ev\bad-path-backup") -or (Test-Path -LiteralPath "$ev\outside.ini")){throw 'Startup path traversal was not rejected before writes.'}
$config.processes[0].startupScript='Scripts\LocalBotRelease.ini'
$config.botNamePrefix='TSE_B'+[char]0x00f6+'t'
$config|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $configPath
$rejected=$false
try{& "$PSScriptRoot\Initialize-LocalBotRelease.ps1" -Config $configPath -Dll $dll -ExpectedDllHash $hash -Backup "$ev\bad-prefix-backup"|Out-Null}catch{if($_.Exception.Message -notmatch 'short ASCII'){throw};$rejected=$true}
if(!$rejected -or (Test-Path -LiteralPath "$ev\bad-prefix-backup")){throw 'Non-ASCII prefix must be rejected before lossy profile encoding or writes.'}
'PASS: native preparation, eight distinct profile/sidecar identities, full rollback, invalid-format/path-traversal/non-ASCII validation before writes'
