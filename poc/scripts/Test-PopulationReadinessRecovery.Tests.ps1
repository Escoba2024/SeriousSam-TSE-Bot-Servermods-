$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
# A real child remains alive after its actual retail-format log says disconnected.
function Invoke-RecoveryCase([bool]$Transient,[bool]$RetainReportedName=$false) {
 $tmp=Join-Path ([IO.Path]::GetTempPath()) ('tse-readiness-'+[guid]::NewGuid())
 New-Item -ItemType Directory $tmp|Out-Null
 $ctx=@{tick=0;time=0;starts=0;stops=@();children=@();events=@()}
 $native="Sending CRC request"+[char]10+"  joined"+[char]10+"Adding player: 'A1'"+[char]10+"[BotDriver] local player 0 (player index 0) is now bot-driven: A1"+[char]10
 $path=Join-Path $tmp 'SeriousSam.log'
 $groups=@([pscustomobject]@{Id='A';Size=1;Names=@('A1');Config=@{processes=@(@{clientDir=$tmp})};Active=$false;EligibleAt=0})
 $exe=(Get-Process -Id $PID).Path
 $start={param($g)
  $p=Start-Process $exe -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 90"' -WindowStyle Hidden -PassThru
  $ctx.children+=@($p);$ctx.starts++
  $native|Set-Content -LiteralPath $path
  return @{Entry=@{pid=$p.Id;exe=$exe;startedUtc=$p.StartTime.ToUniversalTime().ToString('o')}}
 }.GetNewClosure()
 $stop={param($g)
  $p=Get-Process -Id $g.Record.Entry.pid -ErrorAction SilentlyContinue
  if($p){$p.Kill();[void]$p.WaitForExit(5000)}
  $ctx.stops+=@($ctx.time)
 }.GetNewClosure()
 $read={
  $lost=$ctx.starts -eq 1 -and $ctx.tick -ge 3 -and (!$Transient -or $ctx.tick -lt 8)
  if($lost){($native+'Disconnected: Too many bad syncs')|Set-Content -LiteralPath $path}
  elseif($ctx.starts){$native|Set-Content -LiteralPath $path}
  # The stale server slot disappears after its owning process is stopped.
  $reported=$ctx.starts -and (!$lost -or ($RetainReportedName -and !$ctx.stops.Count))
  [pscustomobject]@{Valid=$true;Total=$(if($reported){1}else{0});MaxPlayers=16;Map='Little Trouble';Names=$(if($reported){@('A1')}else{@()})}
 }.GetNewClosure()
 $ready={param($g,$s) Test-PopulationNativeReady $g $s}
 try {
  Invoke-PopulationLoop -Groups $groups -TargetPopulation 1 -ReservedHumanSlots 2 -PollMilliseconds 1 -Iterations 72 -ReadSample $read -StartGroup $start -StopGroup $stop -IsRunning {param($g)Test-PopulationOwnedRunning $g.Record} -IsReady $ready -Wait {param($ms)$ctx.tick++;$ctx.time++}.GetNewClosure() -Now {$ctx.time}.GetNewClosure() -Log {param($e)$ctx.events+=@($e)}.GetNewClosure() -StopRequested {$false}
  if($Transient){
   if($ctx.starts -ne 1 -or @($ctx.events|Where-Object Event -eq 'JoinTimeout').Count){throw 'Transient readiness loss restarted a recovered client'}
  } else {
   if($ctx.starts -lt 2 -or !$ctx.stops.Count -or $ctx.stops[0] -gt 50){throw 'Disconnected live client was not recovered within bounded readiness timeout'}
  }
  return $ctx
 } finally {
  foreach($p in $ctx.children){if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)};$p.Dispose()}
  Remove-Item -LiteralPath $tmp -Recurse -Force
 }
}
$permanent=Invoke-RecoveryCase $false
$ghost=Invoke-RecoveryCase $false $true
$transient=Invoke-RecoveryCase $true $true
"POST-JOIN READINESS RECOVERY PASS: missing-slot starts=$($permanent.starts); log-only starts=$($ghost.starts); transient starts=$($transient.starts)"
