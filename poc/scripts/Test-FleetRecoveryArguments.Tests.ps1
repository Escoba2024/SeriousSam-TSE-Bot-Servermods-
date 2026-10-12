$ErrorActionPreference='Stop'
foreach($args in @(@{SyncMinutes=0;Seconds=120},@{SyncMinutes=1;Seconds=60})){
    $rejected=$false
    try{& "$PSScriptRoot/Test-RetailFleet.ps1" -Dll 'nonexistent-dll-for-argument-check' -Evidence 'unused-argument-check' -Lifecycle -UnexpectedExitRecovery @args | Out-Null}
    catch{$rejected=$_.Exception.Message -like 'UnexpectedExitRecovery requires*SyncMinutes*'}
    if(!$rejected){throw 'Hard-exit mode must reject insufficient minute coverage before accessing files/processes.'}
}
'FLEET RECOVERY ARGUMENT REGRESSIONS PASS'
