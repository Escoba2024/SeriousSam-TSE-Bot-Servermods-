param(
    [Parameter(Mandatory=$true)][string]$BaseBuild,
    [Parameter(Mandatory=$true)][string]$BuildDir
)
# Add the native world lock to an unchanged, accepted obstacle SDK build.
$ErrorActionPreference='Stop'
$repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=(Resolve-Path -LiteralPath $BaseBuild).Path
$baseDll=Join-Path $base 'Sources\Bin\vs2022.Release_TSE107\GameMP.dll'
$accepted='1A38F0A41583A11A0790CE91EEA2A86162B2B3B8E575204AB1360854BA6AF1E7'
if((Get-FileHash -LiteralPath $baseDll).Hash -ne $accepted){throw 'Expected the accepted 1A38F0A4 obstacle build.'}
if(Test-Path -LiteralPath $BuildDir){throw 'Use a new build directory.'}
$build=(New-Item -ItemType Directory -Path $BuildDir).FullName
New-Item -ItemType Directory -Path "$build\Sources\Bin\vs2022.Release_TSE107","$build\Bin" | Out-Null
Copy-Item -LiteralPath "$base\Sources\Game","$base\Sources\Properties" -Destination "$build\Sources" -Recurse
foreach($name in 'Includes','EntitiesTSE'){
    New-Item -ItemType Junction -Path "$build\Sources\$name" -Target "$base\Sources\$name" | Out-Null
}
$patch=Join-Path $repo 'poc\patch\0006-gamemp-ai-world-lock.patch'
& git apply --check --unsafe-paths "--directory=$build" $patch
if($LASTEXITCODE){throw 'World-lock patch does not match the accepted obstacle source.'}
& git apply --unsafe-paths "--directory=$build" $patch
if($LASTEXITCODE){throw 'World-lock patch application failed.'}
$msbuild='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
$arguments=@("$build\Sources\Game\Game.vcxproj",'/t:Rebuild','/p:Configuration=Release_TSE107','/p:Platform=Win32','/p:PlatformToolset=v143','/p:UseOfMfc=false',"/p:SolutionDir=$build\Sources\",'/p:WindowsTargetPlatformVersion=10.0.19041.0','/m:2','/v:minimal')
@($msbuild)+$arguments | Set-Content -LiteralPath "$build\build-command.txt"
& $msbuild @arguments > "$build\build.log" 2>&1
if($LASTEXITCODE){Get-Content -LiteralPath "$build\build.log" -Tail 30; throw 'Release GameMP build failed.'}
Get-FileHash -LiteralPath "$build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll"
