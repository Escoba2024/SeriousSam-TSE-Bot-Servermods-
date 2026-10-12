param(
    [Parameter(Mandatory=$true)][string]$BaseBuild,
    [Parameter(Mandatory=$true)][string]$BuildDir
)
# Continue an accepted auto-combat SDK build without overwriting its source/binary.
$ErrorActionPreference='Stop'
$repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=(Resolve-Path -LiteralPath $BaseBuild).Path
$baseDll=Join-Path $base 'Sources\Bin\vs2022.Release_TSE107\GameMP.dll'
$accepted='28A32C6401928717FE8AA5619E490DE8A8CEB8713116368914D5CBBCEC646615'
if((Get-FileHash -LiteralPath $baseDll).Hash -ne $accepted){throw 'Expected the accepted 28A32C64 auto-combat build.'}
if(Test-Path -LiteralPath $BuildDir){throw 'Use a new build directory.'}
$build=(New-Item -ItemType Directory -Path $BuildDir).FullName
New-Item -ItemType Directory -Path "$build\Sources\Bin\vs2022.Release_TSE107","$build\Bin" | Out-Null
Copy-Item -LiteralPath "$base\Sources\Game","$base\Sources\Properties" -Destination "$build\Sources" -Recurse
foreach($name in 'Includes','EntitiesTSE'){
    New-Item -ItemType Junction -Path "$build\Sources\$name" -Target "$base\Sources\$name" | Out-Null
}
Copy-Item -LiteralPath "$repo\poc\botcore\bot_navigation.h" -Destination "$build\Sources\Game"
$patch=Join-Path $repo 'poc\patch\0005-gamemp-obstacle-recovery.patch'
# Explicit destination is confined to the newly created build; no working-tree edit.
& git apply --check --unsafe-paths "--directory=$build" $patch
if($LASTEXITCODE){throw 'Obstacle patch does not match the accepted combat source.'}
& git apply --unsafe-paths "--directory=$build" $patch
if($LASTEXITCODE){throw 'Obstacle patch application failed.'}
$msbuild='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
$arguments=@("$build\Sources\Game\Game.vcxproj",'/t:Rebuild','/p:Configuration=Release_TSE107','/p:Platform=Win32','/p:PlatformToolset=v143','/p:UseOfMfc=false',"/p:SolutionDir=$build\Sources\",'/p:WindowsTargetPlatformVersion=10.0.19041.0','/m:2','/v:minimal')
@($msbuild)+$arguments | Set-Content -LiteralPath "$build\build-command.txt"
& $msbuild @arguments > "$build\build.log" 2>&1
if($LASTEXITCODE){Get-Content -LiteralPath "$build\build.log" -Tail 30; throw 'Obstacle GameMP build failed.'}
Get-FileHash -LiteralPath "$build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll"
