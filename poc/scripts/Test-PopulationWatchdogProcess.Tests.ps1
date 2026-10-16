param([string]$Role='Test',[string]$Root,[string]$Mode='Hold',[string]$Installation)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
$shell=(Get-Process -Id $PID).Path
$self=$PSCommandPath
if($Role -eq 'Controller'){
 if($Mode -in 'Supervisor','SupervisorReceiptFail'){
  # Production supervisor flow with local query/config doubles; no UDP or game.
  function Get-FleetConfig {param($Path) return [pscustomobject]@{server='fixture:25600';processes=@(@{clientDir=$Root;localPlayers=1;startupScript='Scripts/Bot.ini'})}}
  function Get-FleetIdentities {param($Config) return ,@(@{clientDir=$Root;name='FixtureBot'})}
  function Get-FleetPlan {param($Config) return ,@(@{exe=$shell})}
  function Invoke-FleetQuery {
   param($Request,$Server,$Port)
   if($Mode -eq 'SupervisorReceiptFail'){
    $blockedState=Join-Path $Root 'supervisor/group-0-1.state.json'
    if(!(Test-Path -LiteralPath $blockedState)){New-Item -ItemType Directory -Path $blockedState|Out-Null}
   }
   if($Request -eq '\players\'){return '\final\\queryid\2.1'}
   return '\gamename\serioussamse\gamever\1.07\activemod\\numplayers\0\maxplayers\16\mapname\Fixture\final\\queryid\1.1'
  }
  Invoke-PopulationSupervisor -Config fixture -StateDirectory (Join-Path $Root 'supervisor') -TargetPopulation 1 -Iterations 3 -PollMilliseconds 100 -WatchdogSession (Join-Path $Root 'guardian/session.json')
  exit 0
 }
 $session=Open-PopulationWatchdogSession (Join-Path $Root 'guardian/session.json')
 $owned=Invoke-PopulationWatchdogRequest $session Start 0
 if($Mode -eq 'Protocol'){
  foreach($bad in 'Owner','Replay','Future','CallerPid','CallerTime','CallerPath'){
   $request=@{ownerId=$session.OwnerId;requestId=[guid]::NewGuid().ToString('N');sequence=($session.Sequence+1);action='Stop';group='0';caller=(Get-PopulationWatchdogCaller)}
   switch($bad){
    Owner {$request.ownerId='foreign'}
    Replay {$request.sequence=$session.Sequence}
    Future {$request.sequence+=10}
    CallerPid {$request.caller.pid++}
    CallerTime {$request.caller.startedUtc=[datetime]::UtcNow.ToString('o')}
    CallerPath {$request.caller.exe='C:/foreign.exe'}
   }
   $response=Join-Path $session.Directory 'response.json'
   if(Test-Path -LiteralPath $response){Remove-Item -LiteralPath $response}
   Write-PopulationWatchdogJson (Join-Path $session.Directory 'request.json') $request
   $deadline=[datetime]::UtcNow.AddSeconds(10)
   while(!(Test-Path -LiteralPath $response)){if([datetime]::UtcNow -gt $deadline){throw 'Bad request received no rejection'};Start-Sleep -Milliseconds 25}
   $reply=Get-Content -LiteralPath $response -Raw|ConvertFrom-Json
   if($reply.ok -or !(Test-PopulationWatchdogPeer $owned)){throw ('Bad request affected live owned child: '+$bad)}
  }
  $original=$owned
  Invoke-PopulationWatchdogRequest $session Stop 0|Out-Null
  if(Test-PopulationWatchdogPeer $original){throw 'First generation did not stop'}
  $owned=Invoke-PopulationWatchdogRequest $session Start 0
  Write-PopulationWatchdogJson (Join-Path $Root 'generations.json') @{old=$original;current=$owned;rejectedRequests=6}
 }
 Write-PopulationWatchdogJson (Join-Path $Root 'ready.json') $owned
 while(!(Test-Path -LiteralPath (Join-Path $Root 'release'))){Start-Sleep -Milliseconds 50}
 exit 0
}
if($Role -eq 'Guardian'){
 $plan=@{exe=$shell;arguments='-NoProfile -Command "Start-Sleep -Seconds 90"';workingDir=$Root}
 $start={param($sessionPath)
  Start-Process $shell -ArgumentList ('-NoProfile -ExecutionPolicy Bypass -File "'+$self+'" -Role Controller -Root "'+$Root+'" -Mode '+$Mode) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Root 'stdout-controller.txt') -RedirectStandardError (Join-Path $Root 'stderr-controller.txt')
 }.GetNewClosure()
 if($Mode -in 'ExitBeforeAck','ReceiptFail','ResponseFail'){
  # Deterministic crash injection after handle capture, before start acknowledgement.
  $script:originalWriter=${function:Write-PopulationWatchdogJson}
  function Write-PopulationWatchdogJson([string]$Path,$Value){
   if([IO.Path]::GetFileName($Path) -eq 'group-0.json' -and $Mode -eq 'ReceiptFail'){
    & $script:originalWriter (Join-Path $Root 'fault-child.json') $Value
    throw 'Injected child receipt failure'
   }
   if([IO.Path]::GetFileName($Path) -eq 'response.json' -and $Mode -eq 'ResponseFail' -and $Value.result.pid){
    & $script:originalWriter (Join-Path $Root 'fault-child.json') $Value.result
    $controller.Kill();[void]$controller.WaitForExit(5000)
    throw 'Injected response failure after controller hard exit'
   }
   & $script:originalWriter $Path $Value
   if([IO.Path]::GetFileName($Path) -eq 'group-0.json' -and $Mode -eq 'ExitBeforeAck'){$controller.Kill();[void]$controller.WaitForExit(5000)}
  }
 }
 if(!$Installation){$Installation=Join-Path $Root 'installation'}
 Invoke-PopulationWatchdog -Plans @($plan) -Directories @($Installation) -StateDirectory (Join-Path $Root 'guardian') -StartController $start -CheckFree {param($plans)}
 exit 0
}
$checks=0;$held=@();$roots=@();$controllers=@();$guardians=@()
function Assert($value,$message){if(!$value){throw $message};$script:checks++}
function WaitFile([string]$Path,$Process){
 $watch=[Diagnostics.Stopwatch]::StartNew()
 while(!(Test-Path -LiteralPath $Path)){
  if($Process -and $Process.HasExited){throw "Fixture exited before $Path"}
  if($watch.Elapsed.TotalSeconds -gt 15){throw "Fixture deadline: $Path"}
  Start-Sleep -Milliseconds 50
 }
 return Get-Content -LiteralPath $Path -Raw|ConvertFrom-Json
}
function Capture($Identity){
 $p=Get-Process -Id $Identity.pid -ErrorAction Stop
 [void]$p.Handle
 if($p.StartTime.ToUniversalTime().Ticks -ne ([datetimeoffset]$Identity.startedUtc).UtcDateTime.Ticks -or $p.Path -cne $Identity.exe){throw 'Fixture identity changed'}
 $script:held+=@($p)
 return $p
}
function StartGuardian([string]$Directory,[string]$Variant='Hold',[string]$ClientInstallation=''){
 $arguments='-NoProfile -ExecutionPolicy Bypass -File "'+$self+'" -Role Guardian -Root "'+$Directory+'" -Mode '+$Variant
 if($ClientInstallation){$arguments+=' -Installation "'+$ClientInstallation+'"'}
 $p=Start-Process $shell -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Directory ('stdout-'+[guid]::NewGuid()+'.txt')) -RedirectStandardError (Join-Path $Directory ('stderr-'+[guid]::NewGuid()+'.txt'))
 [void]$p.Handle;$script:held+=@($p);$script:guardians+=@($p);return $p
}
function NewRoot {
 $dir=Join-Path ([IO.Path]::GetTempPath()) ('tse-watchdog-'+[guid]::NewGuid().ToString('N'))
 New-Item -ItemType Directory -Path (Join-Path $dir 'installation')|Out-Null
 $script:roots+=@($dir);return $dir
}
try{
 $unrelated=Start-Process $shell -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 90"' -WindowStyle Hidden -PassThru
 [void]$unrelated.Handle;$held+=@($unrelated)
 # Confirm controller stays live longer than several polling cycles: no heartbeat timeout cleanup.
 $dir=NewRoot;$guardian=StartGuardian $dir Protocol
 $controller=Capture (WaitFile (Join-Path $dir 'guardian/controller.json') $guardian)
 $controllers+=@($controller)
 $client=Capture (WaitFile (Join-Path $dir 'ready.json') $guardian)
 $generations=WaitFile (Join-Path $dir 'generations.json') $guardian
 Assert ($generations.rejectedRequests -eq 6 -and !(Test-PopulationWatchdogPeer $generations.old)) 'Invalid mailbox requests or repeated generations failed'
 Start-Sleep -Milliseconds 300
 Assert (!$controller.HasExited -and !$client.HasExited -and !$unrelated.HasExited) 'Live controller/client or unrelated child affected'
 # Another fresh state directory still cannot get the installation lock.
 $blocked=$false
 try{$locks=Enter-PopulationClientLocks @((Join-Path $dir 'installation'));foreach($h in $locks){$h.Dispose()}}catch{$blocked=$true}
 Assert $blocked 'Concurrent restart acquired live guardian lock'
 # Mutable disk state points to unrelated process; retained launch handle must win.
 $fake=@{pid=$unrelated.Id;exe=$unrelated.Path;startedUtc=$unrelated.StartTime.ToUniversalTime().ToString('o');ownerId='forged'}
 Write-PopulationWatchdogJson (Join-Path $dir 'guardian/group-0.json') $fake
 $controller.Kill();Assert ($controller.WaitForExit(5000)) 'Controller hard exit failed'
 Assert ($guardian.WaitForExit(10000)) 'Watchdog failed to finish after controller crash'
 $done=WaitFile (Join-Path $dir 'guardian/completed.json') $null
 Assert ($done.cleanupPassed -and $done.controllerExited -and !$done.nativeAcceptance) 'Hard-exit cleanup not evidenced'
 Assert ($client.WaitForExit(1000) -and !$unrelated.HasExited) 'Orphan leaked or unrelated process stopped'
 Assert ($guardian.ExitCode -ne 0) 'Controller crash hidden by successful watchdog cleanup'
 # Restart with stale state is refused, even if receipt identifies a live process.
 $stale=StartGuardian $dir
 Assert ($stale.WaitForExit(10000) -and $stale.ExitCode -ne 0) 'Stale state was adopted'
 Assert (!$unrelated.HasExited) 'Stale state stopped unrelated process'
 # Fresh restart against the SAME installation after cleanup is allowed.
 $fresh=Join-Path $dir 'restart';New-Item -ItemType Directory -Path $fresh|Out-Null
 # Reacquire and then run a new guardian against the SAME physical installation.
 $locks=Enter-PopulationClientLocks @((Join-Path $dir 'installation'));foreach($h in $locks){$h.Dispose()}
 Assert $true 'Lock not released after orphan cleanup'
 $dir2=$fresh;$guardian2=StartGuardian $dir2 Hold (Join-Path $dir 'installation')
 $controller2=Capture (WaitFile (Join-Path $dir2 'guardian/controller.json') $guardian2)
 $controllers+=@($controller2)
 $client2=Capture (WaitFile (Join-Path $dir2 'ready.json') $guardian2)
 New-Item -ItemType File -Path (Join-Path $dir2 'release')|Out-Null
 Assert ($guardian2.WaitForExit(10000) -and $guardian2.ExitCode -eq 0) 'Normal controller completion failed'
 Assert ($client2.WaitForExit(1000) -and !$unrelated.HasExited) 'Normal final cleanup leaked or affected unrelated process'
 # Race: controller hard exits after child creation, before receiving the response.
 $dir3=NewRoot;$guardian3=StartGuardian $dir3 ExitBeforeAck
 Assert ($guardian3.WaitForExit(15000)) 'Launch/ack race watchdog hung'
 $race=WaitFile (Join-Path $dir3 'guardian/completed.json') $null
 $receipt=WaitFile (Join-Path $dir3 'guardian/group-0.json') $null
 Assert ($race.cleanupPassed -and $race.controllerExited) 'Launch/ack race leaked ownership'
 Assert (!(Test-PopulationWatchdogPeer $receipt)) 'Child survived launch/ack race'
 Assert (!$unrelated.HasExited) 'Race cleanup affected unrelated process'
 foreach($fault in 'ReceiptFail','ResponseFail'){
  $faultRoot=NewRoot;$faultGuardian=StartGuardian $faultRoot $fault
  Assert ($faultGuardian.WaitForExit(15000)) "Persistence failure hung guardian: $fault"
  $faultDone=WaitFile (Join-Path $faultRoot 'guardian/completed.json') $null
  $faultChild=WaitFile (Join-Path $faultRoot 'fault-child.json') $null
  Assert ($faultDone.cleanupPassed -and !(Test-PopulationWatchdogPeer $faultChild) -and !$unrelated.HasExited) "Persistence failure leaked or affected unrelated child: $fault"
 }
 $supervisorRoot=NewRoot;$supervisorGuardian=StartGuardian $supervisorRoot Supervisor
 Assert ($supervisorGuardian.WaitForExit(15000) -and $supervisorGuardian.ExitCode -eq 0) 'Production supervisor watchdog transport failed'
 $supervisorDone=WaitFile (Join-Path $supervisorRoot 'supervisor/completed.json') $null
 $supervisorChild=WaitFile (Join-Path $supervisorRoot 'guardian/group-0.json') $null
 Assert ($supervisorDone.completed -and !(Test-PopulationWatchdogPeer $supervisorChild) -and !$unrelated.HasExited) 'Production supervisor transport leaked or affected unrelated child'
 $receiptRoot=NewRoot;$receiptGuardian=StartGuardian $receiptRoot SupervisorReceiptFail
 Assert ($receiptGuardian.WaitForExit(15000) -and $receiptGuardian.ExitCode -ne 0) 'Supervisor receipt failure did not propagate'
 $receiptDone=WaitFile (Join-Path $receiptRoot 'guardian/completed.json') $null
 $receiptChild=WaitFile (Join-Path $receiptRoot 'guardian/group-0.json') $null
 Assert ($receiptDone.cleanupPassed -and !(Test-PopulationWatchdogPeer $receiptChild) -and !$unrelated.HasExited) 'Supervisor receipt failure leaked or affected unrelated child'
 # Existing processes are rejected by the real preflight (same executable).
 $rejected=$false
 try{Assert-PopulationWatchdogInstallationsFree @(@{exe=$shell})}catch{$rejected=$true}
 Assert $rejected 'Existing installation process was adopted'
 "POPULATION WATCHDOG CHILD PROCESS PASS: $checks checks; hard-exit, restart, live-owner hold, stale receipt, launch/ack race, normal cleanup"
}catch{
 foreach($dir in $roots){Get-ChildItem -LiteralPath $dir -Filter 'stderr-*.txt' -ErrorAction SilentlyContinue|ForEach-Object{Get-Content -LiteralPath $_.FullName -Tail 15}}
 throw
}finally{
 # Only retained fixture handles; no process enumeration or PID-based teardown.
 foreach($p in $controllers){if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}}
 foreach($p in $guardians){if(!$p.HasExited){[void]$p.WaitForExit(10000)}}
 foreach($p in $held){try{if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}}finally{$p.Dispose()}}
 # Temp evidence deliberately remains private; no runtime data is staged.
}
