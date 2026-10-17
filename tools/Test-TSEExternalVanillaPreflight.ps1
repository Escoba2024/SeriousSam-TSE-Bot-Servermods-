#Requires -Version 5.1
<#
.SYNOPSIS
  Fail-closed preflight for an isolated TSE Retail 1.07 vanilla-observer join.
.DESCRIPTION
  Read-only: checks original file hashes, in-use profile, and LIVE UDP GameSpy
  status. Offline fixtures may validate parsing, but NEVER authorize launching.
  Does not start, stop, configure or modify any game process or server.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ObserverDir,
  [Parameter(Mandatory=$true)][string]$ManifestPath,
  [Parameter(Mandatory=$true)][string]$ServerAddress,
  [Parameter(Mandatory=$true)][ValidateRange(1,65535)][int]$QueryPort,
  [Parameter(Mandatory=$true)][ValidateRange(1,65535)][int]$GamePort,
  [Parameter(Mandatory=$true)][string]$ExpectedPlayerName,
  [string]$ExpectedVersion='1.07',
  [ValidateRange(100,10000)][int]$TimeoutMs=3000,
  [string]$StatusFixturePath=''
)
$ErrorActionPreference='Stop'
$report=[ordered]@{
 status='BLOCKED'; canStart=$false; simulated=!!$StatusFixturePath
 checkedUtc=[DateTime]::UtcNow.ToString('o')
 filesVerified=0; checks=@(); live=$false; oneBotOnly=$false
 reasons=@(); scope='Read-only preflight, not an accepted runtime or join'
}
try {
 if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){throw 'File manifest missing'}
 if(-not (Test-Path -LiteralPath $ObserverDir -PathType Container)){throw 'Observer directory missing'}
 # DO NOT wrap ConvertFrom-Json output in @(...): Windows PowerShell would
 # create an array of ONE nested array and silently join four file names.
 $required=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
 $expected=@('SeriousSam.exe','GameMP.dll','Engine.dll','EntitiesMP.dll')
 if(@($required).Count -ne $expected.Count){throw 'Manifest requires exactly four original retail components'}
 $seen=@{}
 foreach($entry in $required){
  $name=[IO.Path]::GetFileName([string]$entry.Path)
  if($expected -cnotcontains $name -or $seen.ContainsKey($name)){
   throw 'Manifest contains duplicate or unexpected binary'
  }
  $seen[$name]=$true
  if(([string]$entry.Hash) -notmatch '^[0-9A-Fa-f]{64}$'){throw ('Invalid expected SHA256 for '+$name)}
  $actualPath=Join-Path (Join-Path $ObserverDir 'Bin') $name
  if(-not (Test-Path -LiteralPath $actualPath -PathType Leaf)){
   $report.reasons+=('Missing original observer binary: '+$name)
   continue
  }
  $observed=(Get-FileHash -LiteralPath $actualPath -Algorithm SHA256).Hash
  $ok=$observed -eq [string]$entry.Hash
  $report.checks+=@{name=$name;ok=$ok}
  if($ok){$report.filesVerified++}
  else {$report.reasons+=('Original SHA256 mismatch: '+$name)}
 }
 $exe=[IO.Path]::GetFullPath((Join-Path (Join-Path $ObserverDir 'Bin') 'SeriousSam.exe'))
 try{
  $occupied=@(Get-CimInstance Win32_Process -Filter "Name='SeriousSam.exe'" | Where-Object {
   $_.ExecutablePath -and $_.ExecutablePath.Equals($exe,[StringComparison]::OrdinalIgnoreCase)
  })
  if($occupied.Count){$report.reasons+='Observer installation already running'}
 }catch{$report.reasons+='Could not independently check local observer processes'}
 if($StatusFixturePath){
  $response=Get-Content -LiteralPath $StatusFixturePath -Raw
 }else{
  $udp=[Net.Sockets.UdpClient]::new()
  try{
   $udp.Client.ReceiveTimeout=$TimeoutMs
   $udp.Connect($ServerAddress,$QueryPort)
   $query=[Text.Encoding]::ASCII.GetBytes('\status\')
   [void]$udp.Send($query,$query.Length)
   $peer=[Net.IPEndPoint]::new([Net.IPAddress]::Any,0)
   $response=[Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
   $report.live=$true
  }finally{$udp.Dispose()}
 }
 $tokens=$response.Split([char]'\')
 $map=@{}
 for($i=1;$i -lt ($tokens.Count-1);$i+=2){
  if($tokens[$i] -and -not $map.ContainsKey($tokens[$i])){
   $map[$tokens[$i]]=$tokens[$i+1]
  }
 }
 $report.oneBotOnly=(
  $map['gamever'] -eq $ExpectedVersion -and
  $map['hostport'] -eq [string]$GamePort -and
  $map['numplayers'] -eq '1' -and
  $map['player_0'] -ceq $ExpectedPlayerName -and
  -not $map.ContainsKey('player_1') -and
  $map['dedicatedserver'] -eq 'yes'
 )
 if(-not $report.oneBotOnly){$report.reasons+='Current query does not contain exactly the expected single bot'}
 if($StatusFixturePath){
  $report.reasons+='Fixture mode never authorizes actual game launches'
 }
 if($report.reasons.Count -eq 0 -and $report.filesVerified -eq 4 -and $report.live){
  $report.status='READY_AT_CHECK_TIME'
  $report.canStart=$true
 }elseif($StatusFixturePath -and $report.oneBotOnly -and $report.filesVerified -eq 4 -and $report.reasons.Count -eq 1){
  $report.status='FIXTURE_MATCH_ONLY'
 }
}catch{
 $report.reasons+=('Preflight failed: '+$_.Exception.Message)
}
$report | ConvertTo-Json -Depth 6
