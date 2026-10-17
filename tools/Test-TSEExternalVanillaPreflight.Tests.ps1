#Requires -Version 5.1
# Offline, disposable fixtures: no TSE installation, port or external host touched.
$ErrorActionPreference='Stop'
$tool=Join-Path $PSScriptRoot 'Test-TSEExternalVanillaPreflight.ps1'
$root=Join-Path ([IO.Path]::GetTempPath()) ('TSE-preflight-test-'+[guid]::NewGuid().ToString('N'))
$dir=Join-Path $root 'Observer'
$bin=Join-Path $dir 'Bin'
$manifest=Join-Path $root 'manifest.json'
$fixture=Join-Path $root 'query.txt'
$names=@('SeriousSam.exe','GameMP.dll','Engine.dll','EntitiesMP.dll')
$passes=0
function Check([bool]$condition,[string]$message){
 if(-not $condition){throw ('FAIL: '+$message)}
 $script:passes++
}
function Invoke-Fixture([string]$query){
 Set-Content -LiteralPath $fixture -Value $query -NoNewline -Encoding Ascii
 $cmd=@('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass',
 '-File',$tool,'-ObserverDir',$dir,'-ManifestPath',$manifest,
 '-ServerAddress','127.0.0.1','-QueryPort','25631','-GamePort','25630',
 '-ExpectedPlayerName','Expected_Bot','-StatusFixturePath',$fixture)
 $raw=& powershell.exe @cmd | Out-String
 if($LASTEXITCODE -ne 0){throw 'Fixture runner failed'}
 return ($raw | ConvertFrom-Json)
}
try {
 New-Item -ItemType Directory -Path $bin -Force | Out-Null
 $items=@()
 foreach($name in $names){
  $path=Join-Path $bin $name
  Set-Content -LiteralPath $path -Value ('mock-'+$name) -Encoding Ascii
  $items+=@{Path=$path;Hash=(Get-FileHash $path -Algorithm SHA256).Hash}
 }
 ConvertTo-Json -InputObject $items -Depth 4 | Set-Content -LiteralPath $manifest -Encoding UTF8
 $valid='\gamename\serioussamse\gamever\1.07\hostport\25630\numplayers\1\dedicatedserver\yes\player_0\Expected_Bot\final\\queryid\1.1'
 $busy='\gamename\serioussamse\gamever\1.07\hostport\25630\numplayers\2\dedicatedserver\yes\player_0\Expected_Bot\player_1\Human\final\\queryid\1.1'
 $ok=Invoke-Fixture $valid
 Check ($ok.filesVerified -eq 4) 'all four hashes verified'
 Check ($ok.oneBotOnly -and $ok.status -eq 'FIXTURE_MATCH_ONLY') 'one-bot fixture matches'
 Check (-not $ok.canStart -and -not $ok.live) 'offline fixture never authorizes launch'
 $no=Invoke-Fixture $busy
 Check ($no.status -eq 'BLOCKED' -and -not $no.oneBotOnly) 'second player blocked'
 $wrong=Invoke-Fixture ($valid.Replace('\gamever\1.07\','\gamever\1.10\'))
 Check ($wrong.status -eq 'BLOCKED') 'wrong game version blocked'
 $wrongPort=Invoke-Fixture ($valid.Replace('\hostport\25630\','\hostport\25600\'))
 Check ($wrongPort.status -eq 'BLOCKED') 'wrong game port blocked'
 Set-Content -LiteralPath (Join-Path $bin 'GameMP.dll') -Value 'tampered' -Encoding Ascii
 $tampered=Invoke-Fixture $valid
 Check ($tampered.status -eq 'BLOCKED' -and $tampered.filesVerified -eq 3) 'binary hash mismatch blocked'
 Remove-Item -LiteralPath (Join-Path $bin 'EntitiesMP.dll') -Force
 $missing=Invoke-Fixture $valid
 Check ($missing.status -eq 'BLOCKED' -and $missing.filesVerified -eq 2) 'missing binary blocked'
 # Restore all four benign fixture files before parser-negative cases.
 foreach($name in $names){Set-Content -LiteralPath (Join-Path $bin $name) -Value ('mock-'+$name) -Encoding Ascii}
 $noFinal=Invoke-Fixture ($valid.Replace('\final\\queryid\1.1',''))
 Check ($noFinal.status -eq 'BLOCKED' -and -not $noFinal.oneBotOnly) 'missing final blocked'
 $duplicate=Invoke-Fixture ($valid.Replace('\numplayers\1\','\numplayers\1\numplayers\9\'))
 Check ($duplicate.status -eq 'BLOCKED') 'duplicate numplayers blocked'
 $unexpected=Invoke-Fixture ($valid.Replace('\final\\queryid\1.1','\player_2\Intruder\final\\queryid\1.1'))
 Check ($unexpected.status -eq 'BLOCKED') 'unexpected extra player index blocked'
 $prefixed=Invoke-Fixture ('garbage'+$valid)
 Check ($prefixed.status -eq 'BLOCKED') 'garbage prefix blocked'
 $dangling=Invoke-Fixture ($valid+'\extra')
 Check ($dangling.status -eq 'BLOCKED') 'dangling unpaired field blocked'
 $badFinal=Invoke-Fixture ($valid.Replace('\final\\queryid\1.1','\final\garbage\queryid\1.1'))
 Check ($badFinal.status -eq 'BLOCKED') 'nonempty final marker blocked'
 $badGame=Invoke-Fixture ($valid.Replace('\gamename\serioussamse\','\gamename\othergame\'))
 Check ($badGame.status -eq 'BLOCKED') 'wrong gamename blocked'
 $noQueryid=Invoke-Fixture ($valid.Replace('\final\\queryid\1.1','\final\'))
 Check ($noQueryid.oneBotOnly -and $noQueryid.status -eq 'FIXTURE_MATCH_ONLY') 'final without optional queryid allowed'
 $afterFinal=Invoke-Fixture ($valid.Replace('\final\\queryid\1.1','\final\\unexpected\junk'))
 Check ($afterFinal.status -eq 'BLOCKED') 'unknown field after final blocked'
 $twice=Invoke-Fixture ($valid.Replace('\final\\queryid\1.1','\final\\final\'))
 Check ($twice.status -eq 'BLOCKED') 'duplicate final blocked'
 Write-Output ([ordered]@{result='PASS';checks=$passes;scope='offline simulated only; never authorizes runtime'}|ConvertTo-Json -Compress)
}finally {
 if(Test-Path -LiteralPath $root){Remove-Item -LiteralPath $root -Recurse -Force}
}
