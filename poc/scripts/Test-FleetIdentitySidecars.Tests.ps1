# Regression for cloned Steam retail GUID sidecars, with real native fixtures.
$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationCore.ps1"
$root=Join-Path ([IO.Path]::GetTempPath()) ('tse-sidecar-'+[guid]::NewGuid())
$config=@{processes=@()}
$guids=@{}
foreach($prefix in 'A','B'){
    $dir=Join-Path $root $prefix
    New-Item -ItemType Directory "$dir/Data","$dir/Players"|Out-Null
    $stream=[IO.MemoryStream]::new();$writer=[IO.BinaryWriter]::new($stream)
    $writer.Write([Text.Encoding]::ASCII.GetBytes('GAMEV012'));$writer.Write([int]0)
    foreach($value in 0,0,0,1,2,3,0){$writer.Write([int]$value)}
    [IO.File]::WriteAllBytes("$dir/Data/SeriousSam.gms",$stream.ToArray());$writer.Dispose()
    $guid=[guid]::NewGuid().ToByteArray();$guids[$prefix]=$guid
    $stream=[IO.MemoryStream]::new();$writer=[IO.BinaryWriter]::new($stream)
    $writer.Write([Text.Encoding]::ASCII.GetBytes('PLC4'));$writer.Write([int]1)
    $writer.Write([Text.Encoding]::ASCII.GetBytes($prefix));$writer.Write([int]0)
    $writer.Write($guid);$writer.Write([byte[]]::new(32))
    [IO.File]::WriteAllBytes("$dir/Players/Player0.plr",$stream.ToArray());$writer.Dispose()
    [IO.File]::WriteAllBytes("$dir/Players/Player0.plr.guid",$guid)
    $config.processes+=@(@{clientDir=$dir;localPlayers=1})
}
if((Get-FleetIdentities $config).Count -ne 2){throw 'Matching sidecars must pass.'}
# Distinct PLC4 GUIDs cannot make cloned .guid files safe.
[IO.File]::WriteAllBytes("$root/B/Players/Player0.plr.guid",$guids['A'])
$failure=$null
try{Get-FleetIdentities $config|Out-Null}catch{$failure=$_.Exception.Message}
if($failure -notmatch 'sidecar.*(differs|mismatch)'){throw 'Cloned sidecar with unique embedded GUID was accepted.'}
[IO.File]::WriteAllBytes("$root/B/Players/Player0.plr.guid",[byte[]]@(1,2,3))
$failure=$null
try{Get-FleetIdentities $config|Out-Null}catch{$failure=$_.Exception.Message}
if($failure -notmatch 'sidecar'){throw 'Malformed sidecar was accepted.'}
[IO.File]::WriteAllBytes("$root/B/Players/Player0.plr.guid",$guids['B'])
if((Get-FleetIdentities $config).Count -ne 2){throw 'Repaired sidecars must pass.'}
Write-Output "FLEET SIDECAR REGRESSIONS PASS ($root)"
