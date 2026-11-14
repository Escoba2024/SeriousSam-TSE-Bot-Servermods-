#Requires -Version 5.1
<#
.SYNOPSIS
  Read loaded original-client component hashes and sanitized sync-log counts.
.DESCRIPTION
  Run locally as the user already running SeriousSam.exe. Does not start,
  stop, configure, hook or send input to any process. Writes nothing to disk.
  Paths, player names, addresses and raw log lines are omitted from output.
  This is evidence collection, not runtime qualification or a launch preflight.
#>
[CmdletBinding()]
param([ValidateRange(0,2147483647)][int]$ClientProcessId=0)
$ErrorActionPreference='Stop'
$report=[ordered]@{
  scope='READ_ONLY_CURRENT_CLIENT_MODULE_FILES_AND_SYNC_COUNTS'
  checkedUtc=[DateTime]::UtcNow.ToString('o')
  status='INCOMPLETE'; qualified=$false; reasons=@(); components=@()
}
try {
  $clients=@(Get-Process -Name SeriousSam -ErrorAction Stop)
  if($ClientProcessId){$clients=@($clients | Where-Object Id -eq $ClientProcessId)}
  if($clients.Count -ne 1){throw 'Expected exactly one SeriousSam process; supply -ClientProcessId for your own client'}
  $client=$clients[0]; $clientStarted=$client.StartTime.ToUniversalTime()
  $exe=$client.MainModule.FileName
  if([IO.Path]::GetFileName($exe) -ine 'SeriousSam.exe'){throw 'Unexpected executable'}
  $bin=[IO.Path]::GetDirectoryName($exe)
  $expected=[ordered]@{
    'SeriousSam.exe'='9f8f9a0b8fd718616036ed2c3584904e2dfd58e49515bf4c8ecc45175d02cc53'
    'GameMP.dll'='1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
    'Engine.dll'='b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
    'EntitiesMP.dll'='7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'
  }
  foreach($name in $expected.Keys){
    $selected=@(foreach($loaded in $client.Modules){if($loaded.ModuleName -ieq $name){$loaded}})
    if($selected.Count -ne 1){throw ('Missing or ambiguous loaded component: '+$name)}
    $module=$selected[0]; $path=$module.FileName
    $before=Get-Item -LiteralPath $path
    $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $after=Get-Item -LiteralPath $path
    if($before.Length -ne $after.Length -or $before.LastWriteTimeUtc -ne $after.LastWriteTimeUtc){throw ('Component changed while hashing: '+$name)}
    $sameBin=[IO.Path]::GetDirectoryName($path).Equals($bin,[StringComparison]::OrdinalIgnoreCase)
    $report.components+=@{
      name=$name; sha256=$hash; bytes=$after.Length
      loaded=$true; moduleBase=('0x{0:x}' -f $module.BaseAddress.ToInt64())
      moduleBytes=$module.ModuleMemorySize; sameExecutableDirectory=$sameBin
      matchesProjectReference=($hash -eq $expected[$name])
    }
  }
  $log=Join-Path ([IO.Path]::GetDirectoryName($bin)) 'SeriousSam.log'
  $report.log=[ordered]@{present=(Test-Path -LiteralPath $log -PathType Leaf);scope='FULL_CURRENT_LOG_SNAPSHOT_NOT_A_TIMESTAMPED_DELTA'}
  if($report.log.present){
    $stream=[IO.File]::Open($log,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite)
    try {
      $length=$stream.Length
      if($length -gt 33554432){throw 'Log exceeds read-only evidence bound'}
      $buffer=New-Object byte[] ([int]$length)
      $offset=0
      while($offset -lt $buffer.Length){
        $read=$stream.Read($buffer,$offset,$buffer.Length-$offset)
        if($read -eq 0){throw 'Log truncated during snapshot'}
        $offset+=$read
      }
      $text=[Text.Encoding]::ASCII.GetString($buffer)
      $report.log.bytesAtOpen=$length
    }finally{$stream.Dispose()}
    foreach($pattern in @('SYNCBAD','Too many bad syncs','CRC check failed','Cannot join game:','Access violation','Fatal Error')){
      $report.log[$pattern]=[regex]::Matches($text,[regex]::Escape($pattern),[Text.RegularExpressions.RegexOptions]::IgnoreCase).Count
    }
    $report.log.lastWriteUtc=(Get-Item -LiteralPath $log).LastWriteTimeUtc.ToString('o')
  }
  $again=Get-Process -Id $client.Id -ErrorAction Stop
  if($again.StartTime.ToUniversalTime() -ne $clientStarted){throw 'Client process generation changed'}
  $report.clientProcessId=$client.Id; $report.clientStartedUtc=$clientStarted.ToString('o')
  $report.status='COLLECTED_ONLY'
}catch{
  $report.reasons+=('Collection failed: '+$_.Exception.GetType().Name)
}
$report | ConvertTo-Json -Depth 6
