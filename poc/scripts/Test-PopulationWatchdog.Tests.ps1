$ErrorActionPreference='Stop'
$core=Join-Path $PSScriptRoot 'PopulationWatchdog.ps1'
if(!(Test-Path -LiteralPath $core)){throw 'External watchdog core is missing'}
. $core
$checks=0
function Assert($value,$message){if(!$value){throw $message};$script:checks++}
$json=Join-Path ([IO.Path]::GetTempPath()) ('watchdog-json-'+[guid]::NewGuid()+'.json')
try{
 Write-PopulationWatchdogJson $json @{sequence=1}
 Write-PopulationWatchdogJson $json @{sequence=2}
 Assert ((Get-Content -LiteralPath $json -Raw|ConvertFrom-Json).sequence -eq 2) 'Atomic mailbox replacement failed'
}finally{if(Test-Path -LiteralPath $json){Remove-Item -LiteralPath $json}}
function FakeProcess([int]$Number=23456){
 $p=[pscustomobject]@{Id=$Number;Path='C:/mock/Bin/SeriousSam.exe';StartTime=[datetime]::UtcNow;HasExited=$false;Handle=123;Kills=0}
 $p|Add-Member ScriptMethod Kill {$this.Kills++;$this.HasExited=$true}
 $p|Add-Member ScriptMethod WaitForExit {param($ms) return $this.HasExited}
 return $p
}
function Case {
 $ctx=New-PopulationWatchdogContext
 $p=FakeProcess
 $record=New-PopulationWatchdogIdentity $p $ctx.OwnerId $p.Path
 $ctx.Children['0']=$record
 return @{Context=$ctx;Process=$p;Record=$record}
}
$delayed=FakeProcess
$delayed|Add-Member Reads 0
$delayed|Add-Member ScriptProperty Path {$this.Reads++;if($this.Reads -gt 2){return 'C:/mock/Bin/SeriousSam.exe'}} -Force
$delayed|Add-Member ScriptMethod Refresh {}
$delayedIdentity=New-PopulationWatchdogIdentity $delayed 'test-owner' 'C:/mock/Bin/SeriousSam.exe'
Assert ($delayedIdentity.Exe -eq 'C:/mock/Bin/SeriousSam.exe') 'Delayed process metadata was not captured from held handle'
foreach($mutation in 'None','Owner','Replay','Future','SequenceType','CallerPid','CallerStart','CallerExe','CorruptTime','MissingCaller'){
 $c=Case
 $controller=New-PopulationWatchdogIdentity (FakeProcess 22222) $c.Context.OwnerId 'C:/mock/Bin/SeriousSam.exe'
 $request=@{ownerId=$c.Context.OwnerId;requestId=[guid]::NewGuid().ToString('N');sequence=2;caller=@{pid=$controller.Pid;exe=$controller.Exe;startedUtc=$controller.StartedUtc.ToString('o')}}
 switch($mutation){
  Owner {$request.ownerId='foreign'}
  Replay {$request.sequence=1}
  Future {$request.sequence=3}
  SequenceType {$request.sequence='2'}
  CallerPid {$request.caller.pid++}
  CallerStart {$request.caller.startedUtc=$controller.StartedUtc.AddTicks(1).ToString('o')}
  CallerExe {$request.caller.exe='C:/foreign.exe'}
  CorruptTime {$request.caller.startedUtc='invalid'}
  MissingCaller {$request.Remove('caller')}
 }
 Assert ((Test-PopulationWatchdogRequestIdentity $request $c.Context $controller 2) -eq ($mutation -eq 'None')) "Mailbox identity validation failed: $mutation"
}
$c=Case
Assert (!(Invoke-PopulationOrphanCleanup $c.Context $false)) 'Live controller must hold cleanup'
Assert ($c.Process.Kills -eq 0) 'Live controller child stopped'
Assert (Invoke-PopulationOrphanCleanup $c.Context $true) 'Confirmed orphan cleanup failed'
Assert ($c.Process.Kills -eq 1) 'Exact owned child not stopped once'
Assert (Invoke-PopulationOrphanCleanup $c.Context $true) 'Idempotent cleanup failed'
Assert ($c.Process.Kills -eq 1) 'Exited child stopped twice'
foreach($field in 'OwnerId','Pid','StartedUtc','Exe'){
 $c=Case
 switch($field){
  OwnerId {$c.Record.OwnerId=[guid]::NewGuid().ToString('N')}
  Pid {$c.Record.Pid++}
  StartedUtc {$c.Record.StartedUtc=$c.Record.StartedUtc.AddTicks(1)}
  Exe {$c.Record.Exe='C:/other/Bin/SeriousSam.exe'}
 }
 Assert (!(Invoke-PopulationOrphanCleanup $c.Context $true)) "Mismatch accepted: $field"
 Assert ($c.Process.Kills -eq 0) "Mismatch killed a process: $field"
}
$c=Case
$c.Process|Add-Member ScriptProperty Path {throw 'Access denied'} -Force
Assert (!(Invoke-PopulationOrphanCleanup $c.Context $true)) 'Unreadable identity accepted'
Assert ($c.Process.Kills -eq 0) 'Unreadable process killed'
$c=Case
$c.Process|Add-Member ScriptMethod Kill {throw 'Denied'} -Force
Assert (!(Invoke-PopulationOrphanCleanup $c.Context $true)) 'Stop failure reported success'
$c=Case
$c.Record.Process=FakeProcess ($c.Record.Pid+1)
Assert (!(Invoke-PopulationOrphanCleanup $c.Context $true)) 'Reused PID/handle replacement accepted'
Assert ($c.Process.Kills -eq 0) 'Original process affected by handle replacement'
$c=Case
$unrelated=FakeProcess 34567
$c.Context.Children['1']=New-PopulationWatchdogIdentity $unrelated 'foreign-owner' $unrelated.Path
Assert (!(Invoke-PopulationOrphanCleanup $c.Context $true)) 'Partial ownership failure hidden'
Assert ($c.Process.Kills -eq 1 -and $unrelated.Kills -eq 0) 'Safe partial cleanup failed'
$c=Case
$c.Record.Process.Id=$PID;$c.Record.Pid=$PID
Assert (!(Invoke-PopulationOrphanCleanup $c.Context $true)) 'Watchdog self-stop accepted'
Assert ($c.Process.Kills -eq 0) 'Watchdog self-stop attempted'
"POPULATION WATCHDOG OWNERSHIP PASS: $checks checks"
