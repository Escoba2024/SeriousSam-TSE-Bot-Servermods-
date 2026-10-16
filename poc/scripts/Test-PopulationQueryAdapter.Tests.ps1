# Portable CLI/UDP and process-identity checks; Windows CIM cleanup is a separate suite.
$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('pop-adapter-'+[guid]::NewGuid())
$dir=Join-Path $tmp 'client';New-Item -ItemType Directory "$dir/Data","$dir/Players","$dir/Bin"|Out-Null
$s=[IO.MemoryStream]::new();$b=[IO.BinaryWriter]::new($s)
$b.Write([Text.Encoding]::ASCII.GetBytes('GAMEV012'));foreach($x in 0,0,0,0,1,2,3,0){$b.Write([int]$x)}
[IO.File]::WriteAllBytes("$dir/Data/SeriousSam.gms",$s.ToArray());$b.Dispose()
$s=[IO.MemoryStream]::new();$b=[IO.BinaryWriter]::new($s)
$b.Write([Text.Encoding]::ASCII.GetBytes('PLC4'));$b.Write([int]1);$b.Write([Text.Encoding]::ASCII.GetBytes('A'));$b.Write([int]0);$guid=[guid]::NewGuid().ToByteArray();$b.Write($guid);$b.Write([byte[]]::new(32))
[IO.File]::WriteAllBytes("$dir/Players/Player0.plr",$s.ToArray());$b.Dispose();[IO.File]::WriteAllBytes("$dir/Players/Player0.plr.guid",$guid)
$udp=[Net.Sockets.UdpClient]::new([Net.IPEndPoint]::new([Net.IPAddress]::Loopback,0));$udp.Client.ReceiveTimeout=2000
$port=$udp.Client.LocalEndPoint.Port
@{server='127.0.0.1:25600';queryPort=$port;startStaggerSeconds=0;processes=@(@{clientDir=$dir;localPlayers=1;startupScript='Scripts/BotStartup.ini'})}|ConvertTo-Json -Depth 5|Set-Content "$tmp/fleet.json"
$worker=[powershell]::Create()
[void]$worker.AddScript({
 param($socket)
 for($i=0;$i -lt 9;$i++){
   $peer=[Net.IPEndPoint]::new([Net.IPAddress]::Any,0)
   $request=[Text.Encoding]::ASCII.GetString($socket.Receive([ref]$peer))
   $reply=if($request -eq '\players\'){'\final\\queryid\2.1'}else{'\gamename\serioussamse\gamever\1.07\activemod\\numplayers\0\maxplayers\16\mapname\Fortress\final\\queryid\1.1'}
   $bytes=[Text.Encoding]::ASCII.GetBytes($reply);[void]$socket.Send($bytes,$bytes.Length,$peer)
 }
}).AddArgument($udp)
$run=$worker.BeginInvoke()
try{
 & "$PSScriptRoot/Manage-BotPopulation.ps1" -Config "$tmp/fleet.json" -StateDirectory "$tmp/state" -TargetPopulation 0 -Iterations 3 -ObserveOnly -PollMilliseconds 100
 $events=@(Get-Content "$tmp/state/events.jsonl"|ForEach-Object{$_|ConvertFrom-Json})
 if(@($events|Where-Object Event -eq 'Observation').Count -ne 3 -or @($events|Where-Object Event -eq 'QueryUncertain').Count){throw 'Real CLI/UDP adapter did not observe all three valid samples.'}
 if(Test-Path "$dir/.tse-population-controller.lock"){throw 'ObserveOnly changed installation.'}
 $own=(Get-Process -Id $PID)
 $record=@{Entry=@{pid=$PID;exe=$own.Path;startedUtc=$own.StartTime.ToUniversalTime().ToString('o')}}
 if(!(Test-PopulationOwnedRunning $record)){throw 'Live exact identity rejected'}
 $record.Entry.startedUtc=$own.StartTime.ToUniversalTime().AddTicks(1).ToString('o')
 if(Test-PopulationOwnedRunning $record){throw 'Start-time mismatch accepted'}
 $record.Entry.startedUtc=$own.StartTime.ToUniversalTime().ToString('o')
 $group=[pscustomobject]@{Size=1;Names=@('A');Record=$record;Config=@{processes=@(@{clientDir=$dir})}}
 $native="Sending CRC request`n  joined`nAdding player: 'A'`n  done.`n[BotDriver] local player 0 (player index 0) is now bot-driven: A`n"
 $native|Set-Content "$dir/SeriousSam.log"
 if(!(Test-PopulationNativeReady $group @{Names=@('A')})){throw 'Actual retail client join format rejected'}
 ($native+"Cannot join game:`nTimeout while waiting for reply`n")|Set-Content "$dir/SeriousSam.log"
 if(Test-PopulationNativeReady $group @{Names=@('A')}){throw 'Historical join hid later failure'}
 $native|Set-Content "$dir/SeriousSam.log"
 if(Test-PopulationNativeReady $group @{Names=@('A','A')}){throw 'Ambiguous own name accepted as ready'}
 'POPULATION CLI/UDP/READINESS ADAPTER PASS'
}finally{$udp.Dispose();try{$worker.EndInvoke($run)|Out-Null}catch{};$worker.Dispose();Remove-Item -LiteralPath $tmp -Recurse -Force}
