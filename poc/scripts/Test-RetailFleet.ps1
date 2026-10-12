param(
    [Parameter(Mandatory=$true)][string]$Dll,
    [Parameter(Mandatory=$true)][string]$Evidence,
    [ValidateRange(60,7200)][int]$Seconds=120,
    [ValidateRange(0,120)][int]$SyncMinutes=0,
    [switch]$Lifecycle,
    [switch]$MapCycle,
    [switch]$ControlledObserverRejoin,
    [switch]$FailedJoinRecovery,
    [switch]$UnexpectedExitRecovery,
    [string]$StartupSource,
    [switch]$NativeJoinOnly
)
# Retail-only acceptance. Uses native GAMEV012/PLC4 settings; no join hook.
$ErrorActionPreference='Stop'
if($NativeJoinOnly -and (!$StartupSource -or $SyncMinutes -ne 0 -or $MapCycle -or $ControlledObserverRejoin -or $FailedJoinRecovery -or $UnexpectedExitRecovery)){throw 'NativeJoinOnly requires explicit StartupSource, SyncMinutes 0 and no map/recovery modes.'}
if($StartupSource -and (!(Test-Path -LiteralPath $StartupSource -PathType Leaf) -or $StartupSource -notmatch '\.ini$')){throw "StartupSource must reference an existing .ini file: $StartupSource"}
$startupPath=if($StartupSource){(Resolve-Path -LiteralPath $StartupSource).Path}else{Join-Path $PSScriptRoot 'Phase1Respawn.ini'}
$startupHash=(Get-FileHash -LiteralPath $startupPath).Hash
if($ControlledObserverRejoin -and !$MapCycle){throw 'ControlledObserverRejoin requires MapCycle.'}
if($FailedJoinRecovery -and (!$MapCycle -or !$ControlledObserverRejoin -or $Lifecycle -or $Seconds -lt 300)){throw 'FailedJoinRecovery requires MapCycle, ControlledObserverRejoin, at least 300 seconds, and no Lifecycle.'}
if($UnexpectedExitRecovery -and (!$Lifecycle -or $MapCycle -or $FailedJoinRecovery -or $SyncMinutes -lt 1 -or $Seconds -lt 120)){throw 'UnexpectedExitRecovery requires Lifecycle, SyncMinutes >= 1, Seconds >= 120, and no map/fault cycle.'}
. "$PSScriptRoot\PopulationCore.ps1"
. "$PSScriptRoot\FleetMapAcceptance.ps1"
. "$PSScriptRoot\FleetQuery.ps1"
. "$PSScriptRoot\FleetReconnectAcceptance.ps1"
. "$PSScriptRoot\FleetProcessControl.ps1"
. "$PSScriptRoot\FleetRoundReadiness.ps1"
$repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$retail=Join-Path $repo '.codex\retail'
$dllPath=(Resolve-Path -LiteralPath $Dll).Path
if (Test-Path -LiteralPath $Evidence) { throw 'Use a new evidence directory.' }
if (Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$retail\*" }) { throw 'Isolated runtime already in use.' }
if (Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue) { throw 'Test ports already in use.' }
$dirs=@('TSE-BotClient','TSE-BotClient2','TSE-Observer','TSE-Human','TSE-Server')
foreach($dir in $dirs) { if (!(Test-Path "$retail\$dir\Bin\Engine.dll")) { throw "Missing isolated retail copy $dir." } }
$out=(New-Item -ItemType Directory -Path $Evidence).FullName
$started=[DateTime]::UtcNow
$backups=@{}; $processes=@(); $fleetStates=@(); $success=$false;$faultProcess=$null
$serverDir="$retail\TSE-Server"; $observerDir="$retail\TSE-Observer"; $humanDir="$retail\TSE-Human"
function Save-File([string]$Path) {
    if ($backups.ContainsKey($Path)) { return }
    $backup=Join-Path $out ("before-$($backups.Count)-"+(Split-Path $Path -Leaf))
    if (Test-Path -LiteralPath $Path) { Copy-Item -LiteralPath $Path -Destination $backup; $backups[$Path]=$backup }
    else { $backups[$Path]=$null }
}
function Set-NativePlayers([string]$Dir,[int]$Count,[string]$Prefix) {
    $path="$Dir\Data\SeriousSam.gms"; Save-File $path
    $bytes=[IO.File]::ReadAllBytes($path)
    if ([Text.Encoding]::ASCII.GetString($bytes,0,8) -ne 'GAMEV012') { throw 'Unsupported settings header.' }
    $offset=12+[BitConverter]::ToInt32($bytes,8)
    if ($offset -lt 12 -or $offset+28 -gt $bytes.Length) { throw 'Invalid settings length.' }
    foreach($slot in 0..3) { [Array]::Copy([BitConverter]::GetBytes([int]$slot),0,$bytes,$offset+8+4*$slot,4) }
    [Array]::Copy([BitConverter]::GetBytes([int]($Count-1)),0,$bytes,$offset+24,4)
    [IO.File]::WriteAllBytes($path,$bytes)
    if ($Count -eq 0) { return }
    foreach($slot in 0..($Count-1)) {
        $path="$Dir\Players\Player$slot.plr"; Save-File $path
        $bytes=[IO.File]::ReadAllBytes($path)
        if ([Text.Encoding]::ASCII.GetString($bytes,0,4) -ne 'PLC4') { throw 'Unsupported profile header.' }
        $offset=8+[BitConverter]::ToInt32($bytes,4)
        if ($offset -lt 8 -or $offset+4 -gt $bytes.Length) { throw 'Invalid player name length.' }
        $guidOffset=$offset+4+[BitConverter]::ToInt32($bytes,$offset)
        if ($guidOffset -lt $offset+4 -or $guidOffset+48 -ne $bytes.Length) { throw 'Invalid native profile length.' }
        $name=[Text.Encoding]::ASCII.GetBytes("${Prefix}_$($slot+1)")
        $tail=$bytes[$offset..($bytes.Length-1)]
        $guid=[guid]::NewGuid().ToByteArray()
        [Array]::Copy($guid,0,$tail,$guidOffset-$offset,16)
        [IO.File]::WriteAllBytes($path,[byte[]]($bytes[0..3]+[BitConverter]::GetBytes([int]$name.Length)+$name+$tail))
        Save-File ($path+'.guid')
        [IO.File]::WriteAllBytes(($path+'.guid'),$guid)
    }
}
function Query([string]$Request) {
    try{Invoke-FleetQuery -Request $Request -Attempts $(if($MapCycle){3}else{1}) -AttemptLog "$out/query-retries.jsonl"}
    catch{
        $socketError=$_.Exception
        while($socketError.InnerException){$socketError=$socketError.InnerException}
        $faultActive=$FailedJoinRecovery -and (Test-Path "$out/fault-started.json") -and !(Test-Path "$out/fault-finished.json")
        if(!$MapCycle -or $faultActive -or $socketError -isnot [Net.Sockets.SocketException] -or $socketError.SocketErrorCode -notin @('ConnectionReset','ConnectionRefused','TimedOut')){throw}
        $serverText=Get-Content "$serverDir/Dedicated_BotTest.log" -Raw
        if(!(Test-FleetRoundStarting $serverText)){throw}
        $waitStarted=[datetime]::UtcNow
        $deadline=$waitStarted.AddSeconds(15)
        do{
            if($server.HasExited){throw 'Owned server exited during native round startup.'}
            Start-Sleep -Milliseconds 100
            $serverText=Get-Content "$serverDir/Dedicated_BotTest.log" -Raw
        }while((Test-FleetRoundStarting $serverText) -and [datetime]::UtcNow -lt $deadline)
        if(Test-FleetRoundStarting $serverText){throw 'Native round did not become ready within fifteen seconds.'}
        @{utc=[datetime]::UtcNow.ToString('o');request=$Request;socketError=$socketError.SocketErrorCode.ToString();waitSeconds=([datetime]::UtcNow-$waitStarted).TotalSeconds}|ConvertTo-Json -Compress|Add-Content "$out/round-readiness-waits.jsonl"
        Invoke-FleetQuery -Request $Request -Attempts 3 -AttemptLog "$out/query-retries.jsonl"
    }
}
function Wait-Count([int]$Count,[string]$Label,[int]$TimeoutSeconds=45) {
    $deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $lastWaitSample=[datetime]::MinValue
    do {
        Start-Sleep -Milliseconds 500
        $status=Query '\status\'
        if($UnexpectedExitRecovery -and $Label -eq 'exactly-four-freed' -and ([datetime]::UtcNow-$lastWaitSample).TotalSeconds -ge 5){
            $lastWaitSample=[datetime]::UtcNow
            @{utc=$lastWaitSample.ToString('o');label=$Label;expected=$Count;status=$status}|ConvertTo-Json -Compress|Add-Content "$out/wait-count-attempts.jsonl"
        }
        if ($status -match "\\numplayers\\$Count\\") {
            $players=Query '\players\'
            if(Test-FleetQueryCountReady $status $players $Count){
                [ordered]@{utc=[DateTime]::UtcNow.ToString('o');label=$Label;status=$status;players=$players} |
                    ConvertTo-Json -Compress | Add-Content "$out\queries.jsonl"
                return
            }
        }
    } until ([DateTime]::UtcNow -gt $deadline)
    throw "Player count $Count not reached ($Label): $status"
}
function Start-Client([string]$Dir,[string]$Arguments='+connect 127.0.0.1:25600 +quickjoin') {
    $p=Start-Process "$Dir\Bin\SeriousSam.exe" -ArgumentList $Arguments -WorkingDirectory "$Dir\Bin" -WindowStyle Hidden -PassThru
    $script:processes+=@($p)
    return $p
}
function Stop-Client($Process,[string]$Dir,[string]$Label) {
    $state="$out\$Label-state.json"
    @{processes=@(@{pid=$Process.Id;exe=$Process.Path;clientDir=$Dir;startedUtc=$Process.StartTime.ToUniversalTime().ToString('o')})} | ConvertTo-Json -Depth 4 | Set-Content $state
    & "$PSScriptRoot\Stop-BotFleet.ps1" -State $state -GracefulWaitSeconds 5 | Out-Null
    Copy-Item "$Dir\SeriousSam.log" "$out\$Label.log"
}
try {
    & 'C:\Program Files\Git\cmd\git.exe' -C $repo rev-parse HEAD | Set-Content "$out\commit.txt"
    & 'C:\Program Files\Git\cmd\git.exe' -C $repo diff | Set-Content "$out\source.diff"
    $hashes=@(foreach($dir in $dirs) { foreach($file in 'GameMP.dll','EntitiesMP.dll','Engine.dll') { Get-FileHash "$retail\$dir\Bin\$file" } })
    $hashes | Select-Object Path,Hash | ConvertTo-Json | Set-Content "$out\hashes-before.json"
    foreach($dir in $dirs) {
        foreach($file in 'SeriousSam.log','Dedicated_BotTest.log','Bin\SeriousSam.RPT') {
            $path="$retail\$dir\$file"; Save-File $path
            if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }
        }
        if ($dir -eq 'TSE-Server') { continue }
        $path="$retail\$dir\Scripts\PersistentSymbols.ini"; Save-File $path
        $text=Get-Content -Raw $path
        foreach($setting in @{sam_bFullScreen=0;sam_bPauseOnMinimize=0;sam_iMaxFPSActive=60;sam_iMaxFPSInactive=30;sam_iScreenSizeI=960;sam_iScreenSizeJ=540}.GetEnumerator()) {
            $text=$text -replace ($setting.Key+'\s*=\s*[^;]*;'),($setting.Key+'=(INDEX)'+$setting.Value+';')
        }
        Set-Content $path $text
    }
    Set-NativePlayers "$retail\TSE-BotClient" 4 'TSE_Fleet_A'
    Set-NativePlayers "$retail\TSE-BotClient2" 4 'TSE_Fleet_B'
    Set-NativePlayers $observerDir 0 'Observer'
    Set-NativePlayers $humanDir 1 'Vanilla_Human'
    $config=@{server='127.0.0.1:25600';queryPort=25601;startStaggerSeconds=3;processes=@()}
    foreach($dir in 'TSE-BotClient','TSE-BotClient2') {
        $path="$retail\$dir\Bin\GameMP.dll"; Save-File $path; Copy-Item $dllPath $path -Force
        $path="$retail\$dir\Scripts\Phase1Respawn.ini"; Save-File $path; Copy-Item -LiteralPath $startupPath -Destination $path -Force
        $config.processes+=@(@{clientDir="$retail\$dir";localPlayers=4;startupScript='Scripts\Phase1Respawn.ini'})
    }
    $config | ConvertTo-Json -Depth 4 | Set-Content "$out\fleet.json"
    $fleet=Get-FleetConfig "$out\fleet.json"
    $identities=Get-FleetIdentities $fleet
    $identities | ConvertTo-Json | Set-Content "$out\identities.json"
    $round="$serverDir\Scripts\Dedicated\BotTest"
    foreach($file in 'init.ini','1_begin.ini','1_end.ini','2_begin.ini','2_end.ini','3_begin.ini','3_end.ini') { Save-File "$round\$file" }
    $first=(Get-Content -Raw "$round\1_begin.ini").Replace('DM_LittleTrouble.wld','Fortress.wld')+"`ngam_iFragLimit=0;gam_iTimeLimit=0;"
    if($MapCycle) {
        if ($backups["$round\2_begin.ini"] -or $backups["$round\3_begin.ini"]) { throw 'Extra server rounds already exist.' }
        Set-Content "$round\init.ini" ((Get-Content -Raw "$round\init.ini").Replace('ded_tmTimeout = -1;','ded_tmTimeout = 1;'))
        $first=$first.Replace('gam_iTimeLimit=0;','gam_iTimeLimit=1;')
        Set-Content "$round\2_begin.ini" ($first.Replace('Fortress.wld','DM_LittleTrouble.wld'))
        if($FailedJoinRecovery){Set-Content "$round\2_begin.ini" ((Get-Content "$round\2_begin.ini" -Raw).Replace('gam_iTimeLimit=1;','gam_iTimeLimit=2;'))}
        Set-Content "$round\3_begin.ini" ($first.Replace('Fortress.wld','WeGotSkullsNBonesToo.wld').Replace('gam_iTimeLimit=1;','gam_iTimeLimit=0;'))
        Set-Content "$round\2_end.ini" '// native round'; Set-Content "$round\3_end.ini" '// native round'
    }
    Set-Content "$round\1_begin.ini" $first
    $server=Start-Process "$serverDir\Bin\DedicatedServer.exe" -ArgumentList BotTest -WorkingDirectory "$serverDir\Bin" -WindowStyle Hidden -PassThru
    $processes+=@($server)
    $deadline=[DateTime]::UtcNow.AddSeconds(20)
    do { Start-Sleep -Milliseconds 250; $ready=(Test-Path "$serverDir\Dedicated_BotTest.log") -and ((Get-Content -Raw "$serverDir\Dedicated_BotTest.log") -match 'ALL OK: Dedicated server') } until($ready -or $server.HasExited -or [DateTime]::UtcNow -gt $deadline)
    if(!$ready) { throw 'Server did not start.' }
    $observer=Start-Client $observerDir
    Start-Sleep -Seconds 5
    & "$PSScriptRoot\Start-BotFleet.ps1" -Config "$out\fleet.json" -State "$out\fleet-state.json" | Out-Null
    $fleetStates+=@("$out\fleet-state.json")
    Wait-Count 8 'eight-bots'
    if($FailedJoinRecovery){
        $initialFleet=Get-Content "$out/fleet-state.json" -Raw|ConvertFrom-Json
        $null=$server.Handle
        $faultProcess=Start-Process (Get-Process -Id $PID).Path -ArgumentList @('-NoProfile','-File',('"'+"$PSScriptRoot/Invoke-FleetJoinFault.ps1"+'"'),'-ServerPid',$server.Id,'-StartedUtcTicks',$server.StartTime.ToUniversalTime().Ticks,'-OwnerPid',$PID,'-Evidence',('"'+$out+'"')) -WindowStyle Hidden -PassThru -RedirectStandardOutput "$out/fault-stdout.txt" -RedirectStandardError "$out/fault-stderr.txt"
        $null=$faultProcess.Handle
    }
    $observerSessions=@();$observerMaps=@('Fortress')
    if($ControlledObserverRejoin){
        Stop-Client $observer $observerDir 'observer-fortress-leave'
        $observerSessions+=@(@{map='Fortress';log='observer-fortress-leave.log';state='observer-fortress-leave-state.json.stopped.json';pid=$observer.Id})
    }
    if($Lifecycle) {
        $human=Start-Client $humanDir; Wait-Count 9 'human-join'
        Stop-Client $human $humanDir 'human-leave'; Wait-Count 8 'human-left'
        $human=Start-Client $humanDir; Wait-Count 9 'human-rejoin'
        Stop-Client $human $humanDir 'human-leave-again'; Wait-Count 8 'human-left-again'
        $state=Get-Content "$out\fleet-state.json" -Raw | ConvertFrom-Json
        $lifecycleInitialState=$state
        $entry=$state.processes[1]
        if($UnexpectedExitRecovery){
            $killed=Get-OwnedPinnedProcess $entry.pid $entry.exe ([datetime]$entry.startedUtc).ToUniversalTime().Ticks $PID
            $killUtc=[datetime]::UtcNow
            $killed.Kill()
            if(!$killed.WaitForExit(5000)){throw 'Owned fault-injected bot process did not exit.'}
            $hardExit=[ordered]@{passed=$false;scope='Bounded test-controller detection and relaunch through Start-BotFleet; no permanent supervisor.';oldProcess=$entry;killUtc=$killUtc.ToString('o');detectedUtc=[datetime]::UtcNow.ToString('o');exitCode=$killed.ExitCode;detectedExit=$killed.HasExited;normalShutdown=$false}
            $hardExit|ConvertTo-Json -Depth 5|Set-Content "$out/hard-exit.json"
            $killed.Dispose()
            Copy-Item -LiteralPath "$($entry.clientDir)/SeriousSam.log" -Destination "$out/four-bots-leave.log"
        }else{Stop-Client (Get-Process -Id $entry.pid) $entry.clientDir 'four-bots-leave'}
        # A terminated client cannot send its normal disconnect acknowledgment.
        # Let the unchanged server use its own longer native timeout, bounded
        # here at 330s. The ordinary controlled-leave limit remains 45s.
        Wait-Count 4 'exactly-four-freed' $(if($UnexpectedExitRecovery){330}else{45})
        if($UnexpectedExitRecovery){
            $hardExit.fourSlotsFreedUtc=[datetime]::UtcNow.ToString('o')
            # The killed process cannot finish renderer cleanup. Archive its
            # log, then require a completely fresh log for its replacement.
            Remove-Item -LiteralPath "$($entry.clientDir)/SeriousSam.log"
        }
        $single=@{server=$config.server;startStaggerSeconds=0;processes=@($config.processes[1])}
        $single | ConvertTo-Json -Depth 4 | Set-Content "$out\restart.json"
        & "$PSScriptRoot\Start-BotFleet.ps1" -Config "$out\restart.json" -State "$out\restart-state.json" | Out-Null
        $fleetStates+=@("$out\restart-state.json")
        Wait-Count 8 'four-bots-restored'
        if($UnexpectedExitRecovery){
            $replacement=(Get-Content "$out/restart-state.json" -Raw|ConvertFrom-Json).processes[0]
            if($replacement.pid -eq $entry.pid -and $replacement.startedUtc -eq $entry.startedUtc){throw 'Recovery did not create a new process identity.'}
            $hardExit.replacement=$replacement;$hardExit.eightSlotsRestoredUtc=[datetime]::UtcNow.ToString('o')
            $hardExit|ConvertTo-Json -Depth 5|Set-Content "$out/hard-exit.json"
        }
    }
    $steadyStart=[DateTime]::UtcNow
    do {
        Start-Sleep -Seconds 5
        foreach($statePath in $fleetStates) {
            $state=Get-Content $statePath -Raw | ConvertFrom-Json
            foreach($entry in $state.processes) {
                $p=Get-Process -Id $entry.pid -ErrorAction SilentlyContinue
                if($p -and $p.Path -eq $entry.exe) {
                    [ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=$p.Id;role=(Split-Path $entry.clientDir -Leaf);cpuSeconds=$p.CPU;privateBytes=$p.PrivateMemorySize64;workingSet=$p.WorkingSet64;handles=$p.HandleCount;threads=$p.Threads.Count} | ConvertTo-Json -Compress | Add-Content "$out\resources.jsonl"
                }
            }
        }
        $p=Get-Process -Id $server.Id
        [ordered]@{utc=[DateTime]::UtcNow.ToString('o');pid=$p.Id;role='server';cpuSeconds=$p.CPU;privateBytes=$p.PrivateMemorySize64;workingSet=$p.WorkingSet64;handles=$p.HandleCount;threads=$p.Threads.Count} | ConvertTo-Json -Compress | Add-Content "$out\resources.jsonl"
        $faultActive=$FailedJoinRecovery -and (Test-Path "$out/fault-started.json") -and !(Test-Path "$out/fault-finished.json")
        if($faultActive){continue}
        try{$sample=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');status=(Query '\status\');players=(Query '\players\')}}
        catch{
            $queryError=$_.Exception
            while($queryError.InnerException){$queryError=$queryError.InnerException}
            if($FailedJoinRecovery -and (Test-Path "$out/fault-started.json") -and !(Test-Path "$out/fault-finished.json") -and $queryError -is [Net.Sockets.SocketException] -and $queryError.SocketErrorCode -in @('ConnectionReset','ConnectionRefused','TimedOut')){
                @{utc=[datetime]::UtcNow.ToString('o');error=$_.Exception.Message}|ConvertTo-Json -Compress|Add-Content "$out/fault-query-races.jsonl"
                continue
            }
            throw
        }
        $sample|ConvertTo-Json -Compress|Add-Content "$out\queries.jsonl"
        if(!$MapCycle){Assert-FleetSteadySample $sample $identities}
        if($ControlledObserverRejoin -and $sample.status -match '\\numplayers\\8\\'){
            $map=[regex]::Match($sample.status,'\\mapname\\([^\\]+)\\').Groups[1].Value
            if($map -notin $observerMaps){
                # Previous sessions were archived by Stop-Client. Never allow
                # their joined marker to satisfy the next process's readiness.
                $observerLogPath="$observerDir\SeriousSam.log"
                if(Test-Path -LiteralPath $observerLogPath){
                    Copy-Item -LiteralPath $observerLogPath -Destination "$out/observer-before-rejoin-$($observerMaps.Count).log"
                    Remove-Item -LiteralPath $observerLogPath
                }
                $observer=Start-Client $observerDir
                $deadline=[DateTime]::UtcNow.AddSeconds(30)
                do{
                    Start-Sleep -Milliseconds 250
                    $observerLog=if(Test-Path -LiteralPath $observerLogPath){Get-Content -LiteralPath $observerLogPath -Raw}else{''}
                }until($observerLog -match '(?m)^\s*joined\s*$' -or $observer.HasExited -or [DateTime]::UtcNow -gt $deadline)
                if($observer.HasExited -or $observerLog -notmatch '(?m)^\s*joined\s*$'){throw "Controlled vanilla observer join failed on $map"}
                $observerMaps+=@($map)
                if($map -eq 'Little Trouble'){
                    Stop-Client $observer $observerDir 'observer-littletrouble-leave'
                    $observerSessions+=@(@{map=$map;log='observer-littletrouble-leave.log';state='observer-littletrouble-leave-state.json.stopped.json';pid=$observer.Id})
                }else{
                    $observerSessions+=@(@{map=$map;log='TSE-Observer-SeriousSam.log';pid=$observer.Id})
                }
            }
        }
    } until(([DateTime]::UtcNow-$steadyStart).TotalSeconds -ge $Seconds)
    Wait-Count 8 'final-eight'
    if($FailedJoinRecovery){
        if(!$faultProcess.HasExited){throw 'Fault helper still active after steady period.'}
        $fault=Get-Content "$out/fault-finished.json" -Raw|ConvertFrom-Json
        if($faultProcess.ExitCode -ne 0 -or !$fault.passed -or !$fault.resumed){throw 'Bounded fault helper failed.'}
        foreach($entry in $initialFleet.processes){
            $live=Get-OwnedPinnedProcess $entry.pid $entry.exe ([datetime]$entry.startedUtc).ToUniversalTime().Ticks $PID
            $live.Dispose()
        }
        $initialFleet|ConvertTo-Json -Depth 5|Set-Content "$out/recovery-retained-processes.json"
    }
    $runtimeIdentities=Get-FleetIdentities $fleet
    $runtimeIdentities|ConvertTo-Json|Set-Content "$out\runtime-identities.json"
    foreach($identity in $identities){
        if(@($runtimeIdentities|Where-Object{$_.clientDir -eq $identity.clientDir -and $_.slot -eq $identity.slot -and $_.name -eq $identity.name -and $_.guid -eq $identity.guid}).Count -ne 1){throw 'Runtime profile/GUID changed after native load.'}
    }
    $players=Query '\players\'; $status=Query '\status\'
    foreach($identity in $identities) { if([regex]::Matches($players,[regex]::Escape('\'+$identity.name+'\')).Count -ne 1) { throw 'Fleet name missing or duplicated in player query.' } }
    if($status -notmatch '\\gamever\\1\.07\\' -or $status -notmatch '\\activemod\\\\') { throw 'Vanilla status version/mod mismatch.' }
    foreach($dir in 'TSE-BotClient','TSE-BotClient2') {
        $text=Get-Content "$retail\$dir\SeriousSam.log" -Raw
        $joinedMarker=$text -match '(?m)^\s*joined\s*$'
        $allowed=@()
        if($FailedJoinRecovery){
            $allowed=@(Get-RecoveredJoinTimeouts $text)
            if(!$allowed.Count){throw "No proven failed join recovery for $dir"}
            @{allowedTimeoutOffsets=$allowed;failedJoins=$allowed.Count;successfulRetries=[regex]::Matches($text,'(?m)^\[BotReconnect\] result=joined\r?$').Count}|ConvertTo-Json|Set-Content "$out/recovery-$dir.json"
        }
        $unexpected=@([regex]::Matches($text,'(?im)sync lost|out of sync|bad sync|wrong crc|access.violation|Timeout while waiting|Client: Timeout receiving UDP port')|Where-Object Index -notin $allowed)
        $failureMarker=$unexpected.Count -gt 0
        [IO.File]::WriteAllText("$out/gate-$dir.log",[string]$text)
        @{utc=[datetime]::UtcNow.ToString('o');path="$retail\$dir\SeriousSam.log";characters=([string]$text).Length;diskBytes=(Get-Item "$retail\$dir\SeriousSam.log").Length;joinedMarker=[bool]$joinedMarker;failureMarker=[bool]$failureMarker;failure=if($failureMarker){$unexpected[0].Value}else{$null}}|ConvertTo-Json|Set-Content "$out/gate-$dir.json"
        if(!$joinedMarker -or $failureMarker) { throw "Client gate failed: $dir" }
        if(!$MapCycle -and !$NativeJoinOnly) { & "$PSScriptRoot\Test-Phase1Telemetry.ps1" -BotLog "$retail\$dir\SeriousSam.log" -Output "$out\$dir-telemetry.json" -ExpectedPlayers 4 -LocalOnly -SyncMinutes $SyncMinutes | Out-Null }
    }
    $observerText=Get-Content "$observerDir\SeriousSam.log" -Raw
    if($observer.HasExited -or $observerText -notmatch '(?m)^\s*joined\s*$' -or $observerText -match 'sync lost|out of sync|bad sync|wrong crc|Timeout while waiting') { throw 'Vanilla observer gate failed.' }
    if($ControlledObserverRejoin){
        if($observerMaps.Count -ne 3){throw 'Missing controlled observer session on a native map.'}
        foreach($session in $observerSessions|Where-Object state){
            $text=Get-Content "$out/$($session.log)" -Raw
            if($text -notmatch '(?m)^\s*joined\s*$' -or $text -match 'sync lost|out of sync|bad sync|wrong crc|Timeout while waiting'){throw 'Earlier controlled observer session failed.'}
            $stop=Get-Content "$out/$($session.state)" -Raw|ConvertFrom-Json
            if(@($stop.results).Count -ne 1 -or @($stop.results|Where-Object state -ne 'graceful').Count){throw 'Observer controlled stop was not graceful.'}
        }
        $observerSessions|ConvertTo-Json|Set-Content "$out/observer-map-sessions.json"
    }
    $serverText=Get-Content "$serverDir\Dedicated_BotTest.log" -Raw
    if(([regex]::Matches($serverText,'CRC check OK')).Count -lt 3) { throw 'Missing independent CRC accepts.' }
    if($MapCycle) {
        $mapQueries=@(Get-Content "$out\queries.jsonl"|ForEach-Object{$_|ConvertFrom-Json})
        $mapAcceptance=@{maps=@(Assert-FleetMapQueries $mapQueries $identities);server=@(Assert-FleetMapServer $serverText $identities)}
        foreach($dir in 'TSE-BotClient','TSE-BotClient2'){
            $mapAcceptance[$dir]=@(Assert-FleetMapActions (Get-Content "$retail\$dir\SeriousSam.log" -Raw))
        }
        $mapAcceptance|ConvertTo-Json -Depth 5|Set-Content "$out\map-acceptance.json"
    }
    if($UnexpectedExitRecovery){
        foreach($entry in @($lifecycleInitialState.processes[0],$replacement)){
            $live=Get-OwnedPinnedProcess $entry.pid $entry.exe ([datetime]$entry.startedUtc).ToUniversalTime().Ticks $PID
            $live.Dispose()
        }
        $hardExit.passed=$true;$hardExit.remainingClient=$lifecycleInitialState.processes[0]
        $hardExit|ConvertTo-Json -Depth 5|Set-Content "$out/hard-exit.json"
    }
    $success=$true
    @{passed=$true;startedUtc=$started.ToString('o');elapsedSeconds=([DateTime]::UtcNow-$started).TotalSeconds;steadySeconds=([DateTime]::UtcNow-$steadyStart).TotalSeconds;dllSha256=(Get-FileHash $dllPath).Hash;startupSource=$startupPath;startupSha256=$startupHash;status=$status;players=$players;crcAcceptedCount=([regex]::Matches($serverText,'CRC check OK')).Count;lifecycle=[bool]$Lifecycle;mapCycle=[bool]$MapCycle;controlledObserverRejoin=[bool]$ControlledObserverRejoin;failedJoinRecovery=[bool]$FailedJoinRecovery;unexpectedExitRecovery=[bool]$UnexpectedExitRecovery;nativeJoinOnly=[bool]$NativeJoinOnly;syncMinutes=$SyncMinutes} | ConvertTo-Json | Set-Content "$out\result.json"
} finally {
    $cleanupErrors=@(); $exits=@()
    if($faultProcess -and !$faultProcess.HasExited){
        # Stop our server first: the bounded helper detects exit and leaves its
        # resume finally. Never kill a helper while it owns a suspended server.
        try{
            if(!$server.HasExited){$server.Kill();if(!$server.WaitForExit(5000)){throw 'Owned server did not exit; fault helper left alive to resume it.'}}
            if(!$faultProcess.WaitForExit(5000)){$faultProcess.Kill();if(!$faultProcess.WaitForExit(5000)){throw 'Owned fault helper did not exit after server exit.'}}
        }catch{$cleanupErrors+=@($_.Exception.Message)}
    }
    foreach($statePath in $fleetStates) {
        try { & "$PSScriptRoot\Stop-BotFleet.ps1" -State $statePath -GracefulWaitSeconds 5 | Out-Null } catch { $cleanupErrors+=@($_.Exception.Message) }
    }
    foreach($p in $processes) {
        try { if(!$p.HasExited) { $p.Kill(); [void]$p.WaitForExit(5000) }; $exits+=@(@{pid=$p.Id;exitCode=$p.ExitCode}) } catch { $cleanupErrors+=@($_.Exception.Message) }
    }
    foreach($dir in $dirs) { foreach($file in 'SeriousSam.log','Dedicated_BotTest.log','Bin\SeriousSam.RPT') { $path="$retail\$dir\$file"; if(Test-Path $path) { Copy-Item -LiteralPath $path -Destination "$out\$dir-$(Split-Path $file -Leaf)" } } }
    $restored=@()
    foreach($path in $backups.Keys) {
        try {
            if($backups[$path]) { Copy-Item -LiteralPath $backups[$path] -Destination $path -Force; $ok=(Get-FileHash $path).Hash -eq (Get-FileHash $backups[$path]).Hash }
            else { if(Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }; $ok=!(Test-Path -LiteralPath $path) }
            if(!$ok) { throw "Restore mismatch $path" }; $restored+=@(@{path=$path;restored=$ok})
        } catch { $cleanupErrors+=@($_.Exception.Message) }
    }
    $owned=@(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$retail\*" })
    $ports=@(Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue)
    $events=@(); $eventsRead=$true
    try { $events=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001;StartTime=$started.ToLocalTime()} -ErrorAction Stop | Where-Object { $_.Message -match 'SeriousSam|DedicatedServer' }) }
    catch { if($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') { $eventsRead=$false } }
    $crashReports=@(Get-ChildItem "$out\*-SeriousSam.RPT")
    $faultRemains=$faultProcess -and !$faultProcess.HasExited
    @{passed=$success;restored=$restored;exits=$exits;ownedProcesses=$owned.Count;faultHelperRemaining=[bool]$faultRemains;udpPorts=$ports.Count;crashReports=$crashReports.Count;applicationEventsRead=$eventsRead;matchingCrashEvents=$events.Count;cleanupErrors=$cleanupErrors} | ConvertTo-Json -Depth 5 | Set-Content "$out\diagnostics.json"
    if($cleanupErrors.Count -or $owned.Count -or $faultRemains -or $ports.Count -or $crashReports.Count -or !$eventsRead -or $events.Count) { throw "Retail fleet cleanup/crash diagnostics failed; inspect $out." }
}
Write-Output "Retail 2x4 fleet PASS: $out"
