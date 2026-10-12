$ErrorActionPreference='Stop'
. "$PSScriptRoot/FleetQuery.ps1"
# Real UDP peers: first packet lost then reply, and permanent packet loss.
Add-Type -TypeDefinition @'
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
public sealed class ShadowFleetQueryPeer : IDisposable {
  readonly UdpClient udp = new UdpClient(new IPEndPoint(IPAddress.Loopback, 0));
  public int Port { get { return ((IPEndPoint)udp.Client.LocalEndPoint).Port; } }
  public ShadowFleetQueryPeer(bool recover) {
    Task.Run(async () => {
      try {
        for (int i=0; i<2; i++) {
          UdpReceiveResult packet = await udp.ReceiveAsync();
          if (recover && i==1) {
            byte[] response=Encoding.ASCII.GetBytes("\\status\\OK");
            await udp.SendAsync(response,response.Length,packet.RemoteEndPoint);
          }
        }
      } catch (ObjectDisposedException) {} catch (SocketException) {}
    });
  }
  public void Dispose() { udp.Dispose(); }
}
'@
$root=Join-Path ([IO.Path]::GetTempPath()) ('tse-query-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $root|Out-Null
$peer=[ShadowFleetQueryPeer]::new($true)
try{
    $answer=Invoke-FleetQuery -Request '\status\' -Port $peer.Port -Attempts 2 -ReceiveTimeoutMs 100 -RetryDelayMs 10 -AttemptLog "$root/recovered.jsonl"
    if($answer -ne '\status\OK'){throw 'Recovered UDP reply missing'}
    $rows=@(Get-Content "$root/recovered.jsonl"|ForEach-Object{$_|ConvertFrom-Json})
    if($rows.Count -ne 1 -or $rows[0].socketError -ne 'TimedOut' -or !$rows[0].retry){throw 'Missing bounded retry evidence'}
}finally{$peer.Dispose()}
$peer=[ShadowFleetQueryPeer]::new($false)
try{
    $failed=$false
    try{Invoke-FleetQuery -Request '\status\' -Port $peer.Port -Attempts 2 -ReceiveTimeoutMs 100 -RetryDelayMs 10 -AttemptLog "$root/failed.jsonl"|Out-Null}catch{$failed=$true}
    if(!$failed){throw 'Permanent query outage accepted'}
    $rows=@(Get-Content "$root/failed.jsonl"|ForEach-Object{$_|ConvertFrom-Json})
    if($rows.Count -ne 2 -or $rows[-1].retry){throw 'Retry limit not respected'}
}finally{$peer.Dispose()}
"FLEET UDP QUERY REGRESSIONS PASS ($root)"
