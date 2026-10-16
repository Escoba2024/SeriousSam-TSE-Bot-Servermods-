# Actual matching child must stop; a stale timestamp must preserve another child.
$ErrorActionPreference='Stop'
$window=@{}
if([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT){$window.WindowStyle='Hidden'}
$root=Join-Path ([IO.Path]::GetTempPath()) ('tse-stop-current-'+[guid]::NewGuid())
New-Item -ItemType Directory $root|Out-Null
$exe=(Get-Process -Id $PID).Path
foreach($stale in $true,$false){
    $child=Start-Process $exe -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' @window -PassThru
    try{
        $started=$child.StartTime.ToUniversalTime()
        if($stale){$started=$started.AddSeconds(-1)}
        $state=Join-Path $root ("state-$stale.json")
        @{processes=@(@{pid=$child.Id;exe=$child.Path;clientDir=$root;startedUtc=$started.ToString('o')})}|ConvertTo-Json -Depth 4|Set-Content $state
        & "$PSScriptRoot/Stop-BotFleet.ps1" -State $state -GracefulWaitSeconds 0|Out-Null
        $result=Get-Content "$state.stopped.json" -Raw|ConvertFrom-Json
        if($stale){
            if($child.HasExited -or $result.results.state -ne 'not-running'){throw 'Stale timestamp touched an unrelated child.'}
        }else{
            if(!$child.HasExited -or $result.results.state -eq 'not-running'){throw 'Matching live owned child was falsely classified not-running.'}
        }
    }finally{if(!$child.HasExited){$child.Kill();[void]$child.WaitForExit(5000)}}
}
Write-Output "FLEET CURRENT-CHILD STOP REGRESSIONS PASS ($root)"
