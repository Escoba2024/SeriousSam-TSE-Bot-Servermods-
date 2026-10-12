# A failed second launch must not leave the first owned process running.
# Only the external launch is substituted; config/profile parsing and the
# launcher are real, and cleanup is asserted on real child process lifetime.
$ErrorActionPreference='Stop'
$testDir=Join-Path ([IO.Path]::GetTempPath()) ('tse-fleet-launch-'+[guid]::NewGuid())
New-Item -ItemType Directory $testDir | Out-Null
$config=@{server='127.0.0.1:25600';startStaggerSeconds=0;processes=@()}
foreach($prefix in 'A','B'){
    $dir=Join-Path $testDir $prefix
    New-Item -ItemType Directory "$dir\Bin","$dir\Data","$dir\Players" | Out-Null
    [IO.File]::WriteAllBytes("$dir\Bin\SeriousSam.exe",[byte[]]@())
    $stream=[IO.MemoryStream]::new(); $writer=[IO.BinaryWriter]::new($stream)
    $writer.Write([Text.Encoding]::ASCII.GetBytes('GAMEV012')); $writer.Write([int]0)
    foreach($value in 0,0,0,1,2,3,0){$writer.Write([int]$value)}
    [IO.File]::WriteAllBytes("$dir\Data\SeriousSam.gms",$stream.ToArray()); $writer.Dispose()
    $stream=[IO.MemoryStream]::new(); $writer=[IO.BinaryWriter]::new($stream)
    $writer.Write([Text.Encoding]::ASCII.GetBytes('PLC4')); $name=[Text.Encoding]::ASCII.GetBytes($prefix)
    $writer.Write([int]$name.Length); $writer.Write($name); $writer.Write([int]0)
    $writer.Write([guid]::NewGuid().ToByteArray()); $writer.Write([byte[]]::new(32))
    [IO.File]::WriteAllBytes("$dir\Players\Player0.plr",$stream.ToArray()); $writer.Dispose()
    $config.processes+=@(@{clientDir=$dir;localPlayers=1;startupScript='Scripts\BotStartup.ini'})
}
$config | ConvertTo-Json -Depth 4 | Set-Content "$testDir\fleet.json"
$pwsh=(Get-Process -Id $PID).Path
$unrelated=Microsoft.PowerShell.Management\Start-Process $pwsh -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' -WindowStyle Hidden -PassThru
$launch=@{calls=0;child=$null;children=@();failSecond=$true;lockState=$null;lockAfter=2;stateLock=$null}
function Start-Process {
    param([string]$FilePath,[string]$ArgumentList,[string]$WorkingDirectory,[string]$WindowStyle,[switch]$PassThru)
    $launch.calls++
    if($launch.failSecond -and $launch.calls -eq 2){throw 'Injected second launch failure.'}
    $launch.child=Microsoft.PowerShell.Management\Start-Process $pwsh -ArgumentList '-NoProfile -Command "Start-Sleep -Seconds 60"' -WindowStyle Hidden -PassThru
    $launch.children+=@($launch.child)
    if($launch.lockState -and $launch.calls -eq $launch.lockAfter){
        # Real sharing violation at state persistence, after both children started.
        $launch.stateLock=[IO.File]::Open($launch.lockState,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None)
    }
    return $launch.child
}
try{
    $failure=$null
    try{& "$PSScriptRoot\Start-BotFleet.ps1" -Config "$testDir\fleet.json" -State "$testDir\state.json" | Out-Null}
    catch{$failure=$_.Exception.Message}
    if($failure -ne 'Injected second launch failure.'){throw "Original launch error was lost: $failure"}
    if($launch.calls -ne 2 -or !$launch.child){throw 'Partial launch scenario was not exercised.'}
    if(!$launch.child.WaitForExit(5000)){throw 'Failed fleet launch leaked its first owned process.'}
    if($unrelated.HasExited){throw 'Launch rollback stopped an unrelated process.'}
    $state=Get-Content "$testDir\state.json" -Raw | ConvertFrom-Json
    if(@($state.processes).Count -ne 1 -or $state.processes[0].pid -ne $launch.child.Id){throw 'Partial launch bookkeeping was lost.'}
    $rollback=Get-Content "$testDir\state.json.rollback.json" -Raw | ConvertFrom-Json
    if(@($rollback.results).Count -ne 1 -or $rollback.results[0].state -ne 'stopped'){throw 'Missing verified rollback evidence.'}
    $launch.calls=0; $launch.failSecond=$false; $launch.lockState="$testDir\write-failed.json"
    $failure=$null
    try{& "$PSScriptRoot\Start-BotFleet.ps1" -Config "$testDir\fleet.json" -State $launch.lockState | Out-Null}
    catch{$failure=$_.Exception.Message}
    if(!$failure -or $launch.calls -ne 2){throw 'State persistence failure was not exercised.'}
    foreach($p in $launch.children){if(!$p.WaitForExit(5000)){throw 'Failed state persistence leaked an owned child.'}}
    if($unrelated.HasExited){throw 'Persistence rollback stopped an unrelated process.'}
    $rollback=Get-Content ($launch.lockState+'.rollback.json') -Raw | ConvertFrom-Json
    if(@($rollback.results).Count -ne 2 -or @($rollback.results | Where-Object state -ne 'stopped').Count){throw 'Persistence rollback evidence did not verify both children.'}
    $launch.stateLock.Dispose(); $launch.stateLock=$null
    $launch.calls=0; $launch.failSecond=$true; $launch.lockAfter=1; $launch.lockState="$testDir\combined-failed.json"
    $failure=$null
    try{& "$PSScriptRoot\Start-BotFleet.ps1" -Config "$testDir\fleet.json" -State $launch.lockState | Out-Null}
    catch{$failure=$_.Exception.Message}
    if($failure -ne 'Injected second launch failure.'){throw "Combined failure lost original launch error: $failure"}
    if(!$launch.child.WaitForExit(5000)){throw 'Combined failure leaked an owned child.'}
    if($unrelated.HasExited){throw 'Combined rollback stopped an unrelated process.'}
    $rollback=Get-Content ($launch.lockState+'.rollback.json') -Raw | ConvertFrom-Json
    if($rollback.launchError -ne $failure -or !$rollback.stateError){throw 'Combined failure evidence lost a primary or secondary error.'}
    if(@($rollback.results).Count -ne 1 -or $rollback.results[0].state -ne 'stopped'){throw 'Combined failure rollback was not verified.'}
    'ALL FLEET LAUNCH FAILURE CHECKS PASSED'
}finally{
    if($launch.stateLock){$launch.stateLock.Dispose()}
    foreach($p in @($launch.children)+@($unrelated)){if($p -and !$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}}
}
