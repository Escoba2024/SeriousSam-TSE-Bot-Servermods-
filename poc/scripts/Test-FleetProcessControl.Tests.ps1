$ErrorActionPreference='Stop'
if(Test-Path "$PSScriptRoot/FleetProcessControl.ps1"){. "$PSScriptRoot/FleetProcessControl.ps1"}
$out=Join-Path ([IO.Path]::GetTempPath()) ('fleet-pause-'+[guid]::NewGuid())
New-Item -ItemType Directory $out|Out-Null
$childScript=Join-Path $out 'counter.ps1'
Set-Content $childScript 'param($Output); while($true){[IO.File]::AppendAllText($Output,"tick`n"); Start-Sleep -Milliseconds 50}'
$exe=(Get-Process -Id $PID).Path
$p=Start-Process $exe -ArgumentList @('-NoProfile','-File',('"'+$childScript+'"'),('"'+"$out/counter.txt"+'"')) -WindowStyle Hidden -PassThru
$paused=$false
try {
    $null=$p.Handle
    $deadline=[datetime]::UtcNow.AddSeconds(10)
    while(!(Test-Path "$out/counter.txt")){if([datetime]::UtcNow -gt $deadline){throw 'Counter child failed to start'};Start-Sleep -Milliseconds 100}
    $owned=Get-OwnedPinnedProcess $p.Id $exe $p.StartTime.ToUniversalTime().Ticks $PID
    foreach($bad in @(@($p.Id,$exe,($p.StartTime.ToUniversalTime().Ticks+1),$PID),@($p.Id,$exe,$p.StartTime.ToUniversalTime().Ticks,0),@($p.Id,($exe+'.wrong'),$p.StartTime.ToUniversalTime().Ticks,$PID))){
        $rejected=$false;try{Get-OwnedPinnedProcess @bad|Out-Null}catch{$rejected=$true};if(!$rejected){throw 'Stale or unowned process accepted'}
    }
    Set-OwnedProcessPaused $owned $true;$paused=$true
    Start-Sleep -Milliseconds 100
    $before=(Get-Item "$out/counter.txt").Length
    Start-Sleep -Milliseconds 500
    if((Get-Item "$out/counter.txt").Length -ne $before){throw 'Owned child did not pause'}
    Set-OwnedProcessPaused $owned $false;$paused=$false
    Start-Sleep -Milliseconds 500
    if((Get-Item "$out/counter.txt").Length -le $before){throw 'Owned child did not resume'}
    'FLEET OWNED PROCESS PAUSE/RESUME REGRESSIONS PASS'
} finally {
    if($paused){Set-OwnedProcessPaused $owned $false}
    if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}
    # Only literal files in our newly created temporary directory.
    foreach($file in Get-ChildItem -LiteralPath $out -File){Remove-Item -LiteralPath $file.FullName}
    Remove-Item -LiteralPath $out
}
