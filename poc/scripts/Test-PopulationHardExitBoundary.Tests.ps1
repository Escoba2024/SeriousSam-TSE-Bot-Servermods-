param([string]$SupervisorPath=(Join-Path $PSScriptRoot 'PopulationSupervisor.ps1'))
$ErrorActionPreference='Stop'
. $SupervisorPath
$checks=0
function Assert($Value,[string]$Message){if(!$Value){throw $Message};$script:checks++}
function AwaitFile([string]$Path,$Process){
    $end=[datetime]::UtcNow.AddSeconds(15)
    while(!(Test-Path -LiteralPath $Path)){
        if($Process.HasExited -or [datetime]::UtcNow -gt $end){throw "Helper handshake missing: $Path"}
        Start-Sleep -Milliseconds 50
    }
}
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('tse-hard-exit-boundary-'+[guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp|Out-Null
$exe=(Get-Process -Id $PID).Path
$controller=$null;$orphan=$null;$locks=@();$contender=$null
# Only this new fixture directory and these retained helper handles are used.
@'
param($Source,$Root)
$ErrorActionPreference='Stop'
. $Source
$held=Enter-PopulationClientLocks @($Root)
$p=$null
try {
 $exe=(Get-Process -Id $PID).Path
 $p=Start-Process $exe -ArgumentList '-NoProfile -NonInteractive -Command "Start-Sleep -Seconds 90"' -WindowStyle Hidden -PassThru
 [void]$p.Handle
 @{pid=$p.Id;exe=$p.Path;startedUtc=$p.StartTime.ToUniversalTime().ToString('o');parent=$PID}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $Root 'identity.json')
 Set-Content -LiteralPath (Join-Path $Root 'ready') -Value 'ready'
 while($true){Start-Sleep -Milliseconds 100}
} finally {
 if($p -and !$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}
 foreach($h in $held){$h.Dispose()}
 Set-Content -LiteralPath (Join-Path $Root 'finally-ran') -Value 'yes'
}
'@|Set-Content -LiteralPath (Join-Path $tmp 'controller.ps1')
@'
param($Source,$Root)
$ErrorActionPreference='Stop'
. $Source
$held=@()
try {$held=Enter-PopulationClientLocks @($Root);Set-Content -LiteralPath (Join-Path $Root 'contender-result') -Value 'acquired'}
catch {Set-Content -LiteralPath (Join-Path $Root 'contender-result') -Value 'blocked'}
finally {foreach($h in $held){$h.Dispose()}}
'@|Set-Content -LiteralPath (Join-Path $tmp 'contender.ps1')
try {
    $args=@('-NoProfile','-NonInteractive','-File',('"'+(Join-Path $tmp 'controller.ps1')+'"'),('"'+$SupervisorPath+'"'),('"'+$tmp+'"'))
    $controller=Start-Process $exe -ArgumentList $args -WindowStyle Hidden -PassThru
    [void]$controller.Handle
    AwaitFile (Join-Path $tmp 'ready') $controller
    $entry=Get-Content -LiteralPath (Join-Path $tmp 'identity.json') -Raw|ConvertFrom-Json
    Assert ($entry.parent -eq $controller.Id) 'Fixture child was not published by our controller'
    $candidate=[Diagnostics.Process]::GetProcessById($entry.pid)
    try {
        [void]$candidate.Handle
        Assert ($candidate.Path -eq $exe -and $candidate.StartTime.ToUniversalTime().Ticks -eq ([datetimeoffset]$entry.startedUtc).UtcTicks) 'Helper identity changed before pinning'
        # Only a validated, pinned identity may enter the cleanup-owned set.
        $orphan=$candidate;$candidate=$null
    } finally {if($candidate){$candidate.Dispose()}}
    $args=@('-NoProfile','-NonInteractive','-File',('"'+(Join-Path $tmp 'contender.ps1')+'"'),('"'+$SupervisorPath+'"'),('"'+$tmp+'"'))
    $contender=Start-Process $exe -ArgumentList $args -WindowStyle Hidden -PassThru
    [void]$contender.Handle
    Assert ($contender.WaitForExit(15000)) 'Contender did not finish'
    Assert ((Get-Content -LiteralPath (Join-Path $tmp 'contender-result')) -eq 'blocked') 'Parallel controller acquired held installation lock'
    $controller.Kill();Assert ($controller.WaitForExit(5000)) 'Owned controller did not exit'
    Assert (!(Test-Path -LiteralPath (Join-Path $tmp 'finally-ran'))) 'Hard exit unexpectedly ran controller finally'
    Assert (!$orphan.HasExited) 'Hard exit did not reproduce surviving helper'
    $locks=Enter-PopulationClientLocks @($tmp)
    Assert ($locks.Count -eq 1) 'Dead controller lock was not released by OS'
    # Check the actual restart guard, substituting config/profile and executable
    # enumeration only. The surviving process above is real, not a retail exe.
    function Get-FleetConfig {param($Path) return @{server='127.0.0.1:25600';processes=@(@{clientDir=$tmp;localPlayers=1;startupScript='Scripts/Test.ini'})}}
    function Get-FleetIdentities {param($Config) return @(@{clientDir=$tmp;name='A'})}
    function Get-Process {
        param($Name,$Id)
        if($Name -eq 'SeriousSam'){
            if(!$orphan.HasExited){return [pscustomobject]@{Path=(Join-Path $tmp 'Bin/SeriousSam.exe')}}
            return
        }
        Microsoft.PowerShell.Management\Get-Process @PSBoundParameters
    }
    foreach($h in $locks){$h.Dispose()};$locks=@()
    $failure=$null
    try{Invoke-PopulationSupervisor -Config 'fixture' -StateDirectory (Join-Path $tmp 'restart') -Iterations 1}catch{$failure=$_.Exception.Message}
    Assert ($failure -eq 'Client already running; never adopt it.') "Restart did not fail closed: $failure"
    Assert (!$orphan.HasExited) 'Restart guard touched surviving child'
    Remove-Item Function:Get-Process,Function:Get-FleetConfig,Function:Get-FleetIdentities
    # CIM is denied in some sandboxes. This unit supplies the known original
    # parent to exercise the real stop predicate, never an orphan kill.
    function Get-CimInstance {param($ClassName,$Filter) return @{ParentProcessId=$entry.parent}}
    $failure=$null
    try{Stop-PopulationOwnedRecord @{Entry=$entry;StatePath=(Join-Path $tmp 'missing.json')} -GracefulWaitSeconds 0|Out-Null}catch{$failure=$_.Exception.Message}
    Assert ($failure -eq 'Refusing to stop a process not created by this supervisor.') "Orphan stop was not refused: $failure"
    Assert (!$orphan.HasExited) 'Orphan was adopted by replacement controller'
    Remove-Item Function:Get-CimInstance
    # Cleanup exclusively through the object pinned before killing controller.
    $orphan.Kill();Assert ($orphan.WaitForExit(5000)) 'Pinned fixture cleanup failed'
    $locks=Enter-PopulationClientLocks @($tmp)
    Assert ($locks.Count -eq 1) 'Lock did not permit clean subsequent run'
    foreach($h in $locks){$h.Dispose()};$locks=@()
    $a=(New-Item -ItemType Directory -Path (Join-Path $tmp 'a-free')).FullName
    $b=(New-Item -ItemType Directory -Path (Join-Path $tmp 'b-held')).FullName
    $busy=Enter-PopulationClientLocks @($b)
    try {
        $rejected=$false
        try{$locks=Enter-PopulationClientLocks @($a,$b)}catch{$rejected=$true}
        Assert $rejected 'Multi-installation acquisition ignored busy second lock'
        $locks=Enter-PopulationClientLocks @($a,$a)
        Assert ($locks.Count -eq 1) 'Failed acquisition leaked first lock or duplicate directories were not deduplicated'
        foreach($h in $locks){$h.Dispose()};$locks=@()
    } finally {foreach($h in $busy){$h.Dispose()}}
    # Unknown and torn ownership markers must not become adoption evidence.
    foreach($content in '{', '{"format":"foreign"}'){
        $path=Join-Path $tmp '.tse-population-controller.lock'
        Set-Content -LiteralPath $path -Value $content
        $rejected=$false
        try{$locks=Enter-PopulationClientLocks @($tmp)}catch{$rejected=$true}
        Assert $rejected 'Unknown/torn installation lock accepted'
        Assert ((Get-Content -LiteralPath $path -Raw).Trim() -eq $content) 'Rejected marker was overwritten'
    }
    "HARD EXIT BOUNDARY PASS: $checks checks; real controller/child/lock; restart enumeration and orphan parent predicate supplied as fixtures; no automatic reaper"
} finally {
    foreach($h in $locks){$h.Dispose()}
    foreach($p in $contender,$controller,$orphan){if($p){if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)};$p.Dispose()}}
}
