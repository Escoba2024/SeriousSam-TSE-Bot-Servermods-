$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('tse-stop-exit-'+[guid]::NewGuid())
New-Item -ItemType Directory $root|Out-Null
$child=Start-Process (Get-Process -Id $PID).Path -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' -WindowStyle Hidden -PassThru
try{
    $state=Join-Path $root 'state.json'
    @{processes=@(@{pid=$child.Id;exe=$child.Path;clientDir=$root;startedUtc=$child.StartTime.ToUniversalTime().ToString('o')})}|ConvertTo-Json -Depth 4|Set-Content $state
    & "$PSScriptRoot/Stop-BotFleet.ps1" -State $state -GracefulWaitSeconds 0|Out-Null
    [void]$child.WaitForExit(5000)
    $result=Get-Content "$state.stopped.json" -Raw|ConvertFrom-Json
    if($null -eq $result.results.exitCode -or $result.results.exitCode -ne $child.ExitCode){throw 'Stop evidence lost the actual owned-child exit code.'}
    if($result.results.state -ne 'forced'){throw 'Console sleeper must not become graceful evidence.'}
}finally{if(!$child.HasExited){$child.Kill();[void]$child.WaitForExit(5000)}}
Write-Output "FLEET EXIT-CODE REGRESSION PASS ($root)"
