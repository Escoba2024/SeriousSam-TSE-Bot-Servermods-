# Windows CIM cleanup integration; portable CLI/UDP coverage lives in Test-PopulationQueryAdapter.Tests.ps1.
$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){throw 'This owned-cleanup integration suite requires Windows CIM.'}
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('pop-owned-cleanup-'+[guid]::NewGuid())
New-Item -ItemType Directory $tmp|Out-Null
$own=Get-Process -Id $PID
 if(!(Get-Command Stop-PopulationOwnedLaunch -ErrorAction SilentlyContinue)){throw 'Owned post-launch rollback is missing'}
 $pwsh=$own.Path
 $older=Start-Process $pwsh -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' -WindowStyle Hidden -PassThru
 $anchor=[datetime]::UtcNow
 $newer=Start-Process $pwsh -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' -WindowStyle Hidden -PassThru
 try{
   Stop-PopulationOwnedLaunch -ExpectedExe $pwsh -NotBeforeUtc $anchor
   if(!$newer.WaitForExit(5000) -or $older.HasExited){throw 'Post-launch rollback missed own child or stopped older process'}
   if(!(Get-Command Stop-PopulationOwnedRecord -ErrorAction SilentlyContinue)){throw 'Disk-independent owned stop is missing'}
   $child=Start-Process $pwsh -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' -WindowStyle Hidden -PassThru
   try{
     $held=@{Entry=@{pid=$child.Id;exe=$pwsh;startedUtc=$child.StartTime.ToUniversalTime().ToString('o')};StatePath="$tmp/missing-state.json"}
     Stop-PopulationOwnedRecord $held -GracefulWaitSeconds 0|Out-Null
     if(!$child.WaitForExit(5000)){throw 'Lost state file orphaned own child'}
   }finally{if(!$child.HasExited){$child.Kill();[void]$child.WaitForExit(5000)}}
 }finally{foreach($p in $older,$newer){if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}}}
 'WINDOWS POPULATION OWNED CLEANUP PASS'
Remove-Item -LiteralPath $tmp -Recurse -Force
