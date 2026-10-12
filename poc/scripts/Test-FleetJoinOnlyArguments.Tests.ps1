$ErrorActionPreference='Stop'
$repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
foreach($runner in @((Join-Path $PSScriptRoot 'Test-RetailFleet.ps1'),(Join-Path $repo 'tools/run-shadow-fleet.ps1'))){
    foreach($extra in @(@{SyncMinutes=1;StartupSource=(Join-Path $PSScriptRoot 'LocalBotRelease.ini')},@{SyncMinutes=0},@{SyncMinutes=0;StartupSource=(Join-Path $PSScriptRoot 'LocalBotRelease.ini');MapCycle=$true})){
        $rejected=$false
        try { & $runner -NativeJoinOnly -Dll 'missing-join-only-argument-dll' -Evidence 'unused-join-only-evidence' @extra | Out-Null }
        catch { $rejected=$_.Exception.Message -like 'NativeJoinOnly requires*' }
        if(!$rejected){throw "Join-only argument conflict must fail before runtime, DLL or evidence access: $runner"}
    }
}
'FLEET JOIN-ONLY ARGUMENT REGRESSIONS PASS'
