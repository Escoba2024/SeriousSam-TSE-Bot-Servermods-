param(
    [Parameter(Mandatory=$true)][string]$Evidence,
    [int]$Seconds=120,
    [int]$SyncMinutes=1,
    [switch]$Lifecycle,
    [switch]$MapCycle,
    [switch]$ControlledObserverRejoin,
    [switch]$FailedJoinRecovery,
    [switch]$UnexpectedExitRecovery,
    [string]$Dll,
    [string]$StartupSource,
    [switch]$NativeJoinOnly
)
# Local preservation wrapper around the existing Phase-3 retail runner.
$ErrorActionPreference='Stop'
if($NativeJoinOnly -and (!$StartupSource -or $SyncMinutes -ne 0 -or $MapCycle -or $ControlledObserverRejoin -or $FailedJoinRecovery -or $UnexpectedExitRecovery)){throw 'NativeJoinOnly requires explicit StartupSource, SyncMinutes 0 and no map/recovery modes.'}
if($StartupSource -and (!(Test-Path -LiteralPath $StartupSource -PathType Leaf) -or $StartupSource -notmatch '\.ini$')){throw "StartupSource must reference an existing .ini file: $StartupSource"}
$startupPath=if($StartupSource){(Resolve-Path -LiteralPath $StartupSource).Path}else{$null}
$repo=Split-Path $PSScriptRoot -Parent
Set-Location $repo
. "$PSScriptRoot/ShadowRuntimeLog.ps1"
. "$repo/poc/scripts/FleetReconnectAcceptance.ps1"
$retail=Join-Path $repo '.codex\retail'
if(Test-Path $Evidence){throw 'Use new evidence directory.'}
if(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue|Where-Object Path -like "$retail\*"){throw 'Isolated runtime already active.'}
if(Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue){throw 'Test ports occupied.'}
$out=(New-Item -ItemType Directory $Evidence).FullName
$backups=@{}; $preservedRoots=@()
foreach($dir in 'TSE-Server','TSE-BotClient','TSE-BotClient2','TSE-Observer','TSE-Human'){
    $root=Join-Path $retail $dir
    $preservedRoots+=@($root)
    $files=@(foreach($sub in 'Players','Controls','Scripts','Data'){Get-ChildItem "$root\$sub" -Recurse -File|ForEach-Object FullName})
    $files+=@('Bin\GameMP.dll','SeriousSam.log','Dedicated_BotTest.log','Bin\SeriousSam.RPT'|ForEach-Object{Join-Path $root $_})
    foreach($path in $files){
        if($backups.ContainsKey($path)){continue}
        $backup=Join-Path $out ("before-$($backups.Count)-"+(Split-Path $path -Leaf))
        if(Test-Path $path){Copy-Item -LiteralPath $path -Destination $backup; $backups[$path]=$backup}
        else{$backups[$path]=$null}
    }
}
$backups.GetEnumerator()|ForEach-Object{[pscustomobject]@{path=$_.Key;backup=$_.Value;hash=if($_.Value){(Get-FileHash $_.Value).Hash}else{$null}}}|ConvertTo-Json|Set-Content "$out\backup-manifest.json"
$passed=$false; $restore=@(); $errors=@(); $created=@()
$wrapperStarted=[datetime]::UtcNow
try{
    if(!$Dll){$Dll="$repo\.codex\shadow-20261008-bot-build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll"}
    $args=@{Dll=$Dll;Evidence="$out\retail";Seconds=$Seconds;SyncMinutes=$SyncMinutes}
    if($startupPath){$args.StartupSource=$startupPath}
    if($NativeJoinOnly){$args.NativeJoinOnly=$true}
    if($Lifecycle){$args.Lifecycle=$true}
    if($MapCycle){$args.MapCycle=$true}
    if($ControlledObserverRejoin){$args.ControlledObserverRejoin=$true}
    if($FailedJoinRecovery){$args.FailedJoinRecovery=$true}
    if($UnexpectedExitRecovery){$args.UnexpectedExitRecovery=$true}
    & "$repo\poc\scripts\Test-RetailFleet.ps1" @args
    $native=Get-Content "$out\retail\diagnostics.json" -Raw|ConvertFrom-Json
    if(!$native.passed -or $native.cleanupErrors.Count -or $native.ownedProcesses -or $native.udpPorts -or $native.crashReports -or $native.matchingCrashEvents -or !$native.applicationEventsRead){throw 'Native fleet acceptance/cleanup failed.'}
    $runtimeLogs=@(Get-ChildItem "$out/retail" -File|Where-Object Name -match '^TSE-.*-(SeriousSam|Dedicated_BotTest)\.log$')
    if($Lifecycle){
        foreach($label in 'human-leave','human-leave-again','four-bots-leave'){
            $runtimeLogs+=@(Get-Item -LiteralPath "$out/retail/$label.log")
        }
    }
    if($ControlledObserverRejoin){
        foreach($label in 'observer-fortress-leave','observer-littletrouble-leave'){
            $runtimeLogs+=@(Get-Item -LiteralPath "$out/retail/$label.log")
        }
    }
    foreach($log in $runtimeLogs){
        $text=Get-Content -LiteralPath $log.FullName -Raw
        $allowed=@()
        if($FailedJoinRecovery -and $log.Name -in @('TSE-BotClient-SeriousSam.log','TSE-BotClient2-SeriousSam.log')){$allowed=@(Get-RecoveredJoinTimeouts $text)}
        if(@(Get-UnexpectedRuntimeMarkers $text $false|Where-Object Index -notin $allowed).Count){throw "Unexpected fleet runtime marker: $($log.Name)"}
    }
    if($Lifecycle){
        foreach($label in 'human-leave','human-leave-again','four-bots-leave'){
            if($UnexpectedExitRecovery -and $label -eq 'four-bots-leave'){continue}
            $stop=Get-Content "$out\retail\$label-state.json.stopped.json" -Raw|ConvertFrom-Json
            if(@($stop.results).Count -ne 1 -or @($stop.results|Where-Object state -ne 'graceful').Count){throw "Controlled exit was not graceful: $label"}
        }
    }
    $passed=$true
}finally{
    # The native runner normally handles all children; recover any remnants
    # before restoring files if its own cleanup failed.
    foreach($p in @(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue|Where-Object Path -like "$retail\*")){
        try{
            $origin=Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)"
            if($origin.ParentProcessId -ne $PID -or $p.StartTime.ToUniversalTime() -lt $wrapperStarted){
                $errors+=@("Unknown isolated process left untouched: $($p.Id)");continue
            }
            if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}
        }catch{$errors+=@($_.Exception.Message)}
    }
    $blockedRoots=@(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue|Where-Object Path -like "$retail\*"|ForEach-Object{Split-Path (Split-Path $_.Path -Parent) -Parent})
    # Preserve newly generated files as evidence before restoring the original
    # directory inventory. No recursive delete: each observed file is archived
    # and removed by its exact literal path.
    foreach($root in $preservedRoots){
        if($root -in $blockedRoots){$errors+=@("Restore blocked by active process: $root");continue}
        foreach($sub in 'Players','Controls','Scripts','Data'){
            foreach($file in @(Get-ChildItem "$root\$sub" -Recurse -File)){
                if($backups.ContainsKey($file.FullName)){continue}
                try{
                    $archive=Join-Path $out ("created-$($created.Count)-"+$file.Name)
                    Copy-Item -LiteralPath $file.FullName -Destination $archive
                    $hash=(Get-FileHash -LiteralPath $file.FullName).Hash
                    if((Get-FileHash -LiteralPath $archive).Hash -ne $hash){throw 'Created-file archive mismatch.'}
                    Remove-Item -LiteralPath $file.FullName
                    $created+=@(@{path=$file.FullName;archive=$archive;sha256=$hash;removed=!(Test-Path -LiteralPath $file.FullName)})
                }catch{$errors+=@($_.Exception.Message)}
            }
        }
    }
    foreach($path in $backups.Keys){
        if(@($blockedRoots|Where-Object{$path.StartsWith($_+'\',[StringComparison]::OrdinalIgnoreCase)}).Count){continue}
        try{
            if($backups[$path]){Copy-Item -LiteralPath $backups[$path] -Destination $path -Force;$ok=(Get-FileHash $path).Hash -eq (Get-FileHash $backups[$path]).Hash}
            else{if(Test-Path $path){Remove-Item -LiteralPath $path};$ok=!(Test-Path $path)}
            $restore+=@(@{path=$path;restored=$ok});if(!$ok){throw "Restore mismatch: $path"}
        }catch{$errors+=@($_.Exception.Message)}
    }
    $owned=@(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue|Where-Object Path -like "$retail\*")
    $ports=@(Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue)
    @{passed=($passed -and !$errors.Count -and !$owned.Count -and !$ports.Count);nativeAccepted=$passed;seconds=$Seconds;syncMinutes=$SyncMinutes;lifecycle=[bool]$Lifecycle;mapCycle=[bool]$MapCycle;controlledObserverRejoin=[bool]$ControlledObserverRejoin;failedJoinRecovery=[bool]$FailedJoinRecovery;unexpectedExitRecovery=[bool]$UnexpectedExitRecovery;restored=$restore;createdFiles=$created;ownedProcesses=$owned.Count;udpPorts=$ports.Count;cleanupErrors=$errors}|ConvertTo-Json -Depth 5|Set-Content "$out\preservation.json"
    if($errors.Count -or $owned.Count -or $ports.Count){throw 'Fleet preservation cleanup failed.'}
}
"SHADOW FLEET PASS: $out"
