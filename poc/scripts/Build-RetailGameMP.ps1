param(
    [Parameter(Mandatory=$true)][string]$Sdk,
    [Parameter(Mandatory=$true)][string]$BuildDir,
    [switch]$Bot
)
$ErrorActionPreference = 'Stop'
$sdkPath = (Resolve-Path -LiteralPath $Sdk).Path
if (Test-Path -LiteralPath $BuildDir) { throw 'Use a new build directory to preserve evidence.' }
$build = (New-Item -ItemType Directory -Path $BuildDir).FullName
$git = 'C:\Program Files\Git\cmd\git.exe'
& $git -C $sdkPath archive --format=tar -o "$build\sdk-game.tar" HEAD Sources/Game Sources/Properties
if ($LASTEXITCODE) { throw 'SDK archive failed.' }
tar -xf "$build\sdk-game.tar" -C $build
if ($LASTEXITCODE) { throw 'SDK extraction failed.' }
foreach ($directory in @('Includes','EntitiesTSE')) {
    New-Item -ItemType Junction -Path "$build\Sources\$directory" -Target "$sdkPath\Sources\$directory" | Out-Null
}
New-Item -ItemType Directory "$build\Bin" | Out-Null
$game = "$build\Sources\Game"
$patch = Join-Path (Split-Path $PSScriptRoot -Parent) 'patch\gamemp'
Copy-Item "$patch\RetailAllocator.cpp" $game
$header = Get-Content -Raw "$game\StdAfx.h"
Set-Content "$game\StdAfx.h" $header.Replace('<EntitiesTSE/Players/Player.h>', '<EntitiesV/Player.h>')
$project = Get-Content -Raw "$game\Game.vcxproj"
$project = $project.Replace('$(SamEngineIncludes);$(SamEngineModels);$(SdkIncl)', '$(SamEngineIncludes);$(SamEngineLibraries)EntitiesV\;$(SamEngineModels);$(SdkIncl)')
$project = $project.Replace('$(SamEngineLibraries);$(SdkLibs)', '$(ProjectDir);$(SamEngineLibraries);$(SdkLibs)')
$project = $project.Replace('<GenerateDebugInformation>true</GenerateDebugInformation>', '<GenerateDebugInformation>true</GenerateDebugInformation><GenerateMapFile>true</GenerateMapFile>')
$project = $project.Replace('<ClCompile Include="Game.cpp" />', '<ClCompile Include="Game.cpp" /><ClCompile Include="RetailAllocator.cpp"><PrecompiledHeader>NotUsing</PrecompiledHeader></ClCompile>')
if ($Bot) {
    Copy-Item "$patch\BotDriver.cpp","$patch\BotDriver.h" $game
    $botcore = Join-Path (Split-Path $PSScriptRoot -Parent) 'botcore'
    Copy-Item "$botcore\botcore.h","$botcore\botcore_ai.h" $game
    $source = Get-Content -Raw "$game\Game.cpp"
    # Phase-2 anchor: the multi-local-player join override must run at the head
    # of CGame::JoinGame(). All anchors fail closed: a mismatch aborts the build.
    $anchors = @('#include "LCDDrawing.h"', "void CGame::GameHandleTimer(void)`n{", '  CAM_Init();', "BOOL CGame::JoinGame(CNetworkSession &session)`n{")
    $source = $source.Replace("`r`n", "`n")
    foreach ($anchor in $anchors) { if (!$source.Contains($anchor)) { throw 'Bot integration anchor missing.' } }
    $source = $source.Replace($anchors[0], $anchors[0]+"`n"+'#include "BotDriver.h"')
    $source = $source.Replace($anchors[1], $anchors[1]+"`n  if (BotDriver_HandleTimer(this)) return;")
    $source = $source.Replace($anchors[2], $anchors[2]+"`n  BotDriver_Init();")
    $source = $source.Replace($anchors[3], $anchors[3]+"`n  BotDriver_ConfigureJoin(this);")
    Set-Content "$game\Game.cpp" $source
    $project = $project.Replace('<ClCompile Include="Game.cpp" />', '<ClCompile Include="Game.cpp" /><ClCompile Include="BotDriver.cpp" />')
}
Set-Content "$game\Game.vcxproj" $project
# The SDK ships a retail ENTITIESMP.dll import library under the name EntitiesV.lib.
if (!(Test-Path "$sdkPath\Sources\Includes\Engine107\EntitiesMP.lib")) {
    Copy-Item "$sdkPath\Sources\Includes\Engine107\EntitiesV.lib" "$build\Sources\Game\EntitiesMP.lib"
}
$msbuild = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
$arguments = @("$game\Game.vcxproj", '/t:Rebuild', '/p:Configuration=Release_TSE107', '/p:Platform=Win32', '/p:PlatformToolset=v143', '/p:UseOfMfc=false', "/p:SolutionDir=$build\Sources\", '/p:WindowsTargetPlatformVersion=10.0.19041.0', '/m:2', '/v:minimal')
@($msbuild) + $arguments | Set-Content "$build\build-command.txt"
& $git -C $sdkPath rev-parse HEAD | Set-Content "$build\sdk-commit.txt"
& $msbuild @arguments > "$build\build.log"
if ($LASTEXITCODE) { Get-Content "$build\build.log"; throw 'GameMP build failed.' }
Get-FileHash "$build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll"
