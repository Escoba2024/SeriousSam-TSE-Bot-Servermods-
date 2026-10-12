$ErrorActionPreference='Stop'
$missing=Join-Path $PSScriptRoot 'missing-startup-argument-check.ini'
foreach($runner in @((Join-Path $PSScriptRoot 'Test-RetailFleet.ps1'),(Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'tools/run-shadow-fleet.ps1'))){
    $rejected=$false
    try { & $runner -Dll 'nonexistent-dll-for-argument-check' -Evidence 'unused-startup-check' -StartupSource $missing | Out-Null }
    catch { $rejected=$_.Exception.Message -like 'StartupSource must reference an existing .ini file:*' }
    if(!$rejected){throw "Missing startup must be rejected before DLL, runtime or evidence access: $runner"}
    $rejected=$false
    try { & $runner -Dll 'nonexistent-dll-for-argument-check' -Evidence 'unused-startup-check' -StartupSource $PSScriptRoot | Out-Null }
    catch { $rejected=$_.Exception.Message -like 'StartupSource must reference an existing .ini file:*' }
    if(!$rejected){throw "Startup directory must not be treated as a file: $runner"}
}
'FLEET STARTUP ARGUMENT REGRESSIONS PASS'
