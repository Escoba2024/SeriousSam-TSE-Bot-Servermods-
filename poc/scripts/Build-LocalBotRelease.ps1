param(
    [Parameter(Mandatory=$true)][string]$Sdk,
    [Parameter(Mandatory=$true)][string]$BuildDir
)
# Build the captured release sources against a pinned, separately acquired SDK.
$ErrorActionPreference='Stop'
$sdkPath=(Resolve-Path -LiteralPath $Sdk).Path
$sdkCommit=(& git -C $sdkPath rev-parse HEAD)
if($LASTEXITCODE -or $sdkCommit -ne 'aa7869c2c2c4db0562281814d0ac3784e6b9d6f0'){throw 'Expected the documented SE1-ModSDK commit aa7869c2.'}
$includesCommit=(& git -C "$sdkPath\Sources\Includes" rev-parse HEAD)
if($LASTEXITCODE -or $includesCommit -ne '94ff8cd0e63941f8601294350b616472f772ed51'){throw 'Expected the pinned SDK Includes submodule 94ff8cd0.'}
$dirtyIncludes=(& git -C "$sdkPath\Sources\Includes" status --porcelain --untracked-files=all)
if($LASTEXITCODE -or $dirtyIncludes){throw 'SDK Includes headers/libraries must be clean.'}
$dirtyEntities=(& git -C $sdkPath status --porcelain --untracked-files=all -- Sources/EntitiesTSE)
if($LASTEXITCODE -or $dirtyEntities){throw 'SDK Entities headers must be clean.'}
if(Test-Path -LiteralPath $BuildDir){throw 'Use a new build directory.'}
$sources=Join-Path (Split-Path $PSScriptRoot -Parent) 'release\gamemp'
$build=(New-Item -ItemType Directory -Path $BuildDir).FullName
& git -C $sdkPath archive --format=tar -o "$build\sdk-game.tar" HEAD Sources/Game Sources/Properties
if($LASTEXITCODE){throw 'SDK source archive failed.'}
& tar -xf "$build\sdk-game.tar" -C $build
if($LASTEXITCODE){throw 'SDK source extraction failed.'}
foreach($name in 'Includes','EntitiesTSE'){
    New-Item -ItemType Junction -Path "$build\Sources\$name" -Target "$sdkPath\Sources\$name"|Out-Null
}
New-Item -ItemType Directory -Path "$build\Bin","$build\Sources\Bin\vs2022.Release_TSE107"|Out-Null
foreach($file in Get-ChildItem -LiteralPath $sources -File){Copy-Item -LiteralPath $file.FullName -Destination "$build\Sources\Game"}
if(!(Test-Path -LiteralPath "$sdkPath\Sources\Includes\Engine107\EntitiesMP.lib")){
    Copy-Item -LiteralPath "$sdkPath\Sources\Includes\Engine107\EntitiesV.lib" -Destination "$build\Sources\Game\EntitiesMP.lib"
}
$msbuild='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
$arguments=@("$build\Sources\Game\Game.vcxproj",'/t:Rebuild','/p:Configuration=Release_TSE107','/p:Platform=Win32','/p:PlatformToolset=v143','/p:UseOfMfc=false',"/p:SolutionDir=$build\Sources\",'/p:WindowsTargetPlatformVersion=10.0.19041.0','/m:2','/v:minimal')
@($msbuild)+$arguments|Set-Content -LiteralPath "$build\build-command.txt"
$sdkCommit|Set-Content -LiteralPath "$build\sdk-commit.txt"
& $msbuild @arguments > "$build\build.log" 2>&1
if($LASTEXITCODE){Get-Content -LiteralPath "$build\build.log" -Tail 30; throw 'Local release source build failed.'}
Get-FileHash -LiteralPath "$build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll"
