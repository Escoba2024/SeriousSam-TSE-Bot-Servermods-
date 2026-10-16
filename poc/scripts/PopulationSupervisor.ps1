$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisorCore.ps1"
. "$PSScriptRoot/PopulationCore.ps1"
. "$PSScriptRoot/FleetQuery.ps1"

function Enter-PopulationClientLocks([string[]]$Directories) {
    $held=@()
    try{
        foreach($dir in @($Directories|Sort-Object -Unique)){
            $path=Join-Path $dir '.tse-population-controller.lock'
            $h=[IO.File]::Open($path,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
            $held+=@($h)
            if($h.Length){
                $reader=[IO.StreamReader]::new($h,[Text.Encoding]::UTF8,$false,1024,$true)
                try{$old=$reader.ReadToEnd()|ConvertFrom-Json}finally{$reader.Dispose()}
                if($old.format -ne 'SeriousSamPopulationClientLock/v1'){throw 'Unknown installation lock; left unchanged.'}
            }
            $bytes=[Text.Encoding]::UTF8.GetBytes((@{format='SeriousSamPopulationClientLock/v1';pid=$PID;utc=[datetime]::UtcNow.ToString('o')}|ConvertTo-Json -Compress))
            $h.SetLength(0);$h.Position=0;$h.Write($bytes,0,$bytes.Length);$h.Flush()
        }
        return ,$held
    }catch{foreach($h in $held){$h.Dispose()};throw}
}
function Invoke-PopulationLoop {
    param([object[]]$Groups,[int]$TargetPopulation,[int]$ReservedHumanSlots,
          [int]$PollMilliseconds=1000,[int]$Iterations=0,
          [scriptblock]$ReadSample,[scriptblock]$StartGroup,[scriptblock]$StopGroup,
          [scriptblock]$IsRunning,[scriptblock]$IsReady,[scriptblock]$Wait,
          [scriptblock]$Now,[scriptblock]$Log,[scriptblock]$StopRequested,
          [switch]$ObserveOnly)
    foreach($g in $Groups){foreach($kv in @{Pending=$false;Deadline=0;Record=$null}.GetEnumerator()){if(!$g.PSObject.Properties[$kv.Key]){$g|Add-Member $kv.Key $kv.Value}}}
    $stable=0;$key=$null;$poll=0;$fence=$null;$operationError=$null
    try{
        while(($Iterations -eq 0 -or $poll -lt $Iterations) -and !(& $StopRequested)){
            $poll++;$time=[double](& $Now)
            foreach($g in $Groups){
                if($g.Active -and !(& $IsRunning $g)){
                    $g.Active=$false;$g.Pending=$false;$g.EligibleAt=$time+10
                    & $Log ([ordered]@{Event='ProcessExited';Group=$g.Id;Time=$time})
                }
            }
            $sample=$null
            try{$sample=& $ReadSample}catch{$stable=0;$key=$null;& $Log ([ordered]@{Event='QueryUncertain';Time=$time;Error=$_.Exception.Message})}
            $time=[double](& $Now)
            $timedOut=@($Groups|Where-Object{$_.Active -and $_.Pending -and $time -ge $_.Deadline}|Select-Object -First 1)
            if($timedOut.Count){
                $g=$timedOut[0]
                if(!$ObserveOnly){& $StopGroup $g;$g.Active=$false;$g.Pending=$false;$g.EligibleAt=[double](& $Now)+10}
                & $Log ([ordered]@{Event='JoinTimeout';Group=$g.Id;Time=$time})
                $stable=0;$key=$null
            }elseif($sample -and $sample.Valid){
                $next="$($sample.Total)|$($sample.MaxPlayers)|$($sample.Map)"
                if($next -eq $key){$stable++}else{$key=$next;$stable=1}
                $allReady=$true
                foreach($g in @($Groups|Where-Object Active)){
                    $ready=(& $IsReady $g $sample)
                    if($ready){$g.Pending=$false}else{
                        $allReady=$false
                        # A joined process can survive a network/sync disconnect.
                        # Re-arm the bounded readiness deadline instead of waiting forever.
                        if(!$ObserveOnly -and !$g.Pending){
                            $g.Pending=$true;$g.Deadline=$time+45
                            & $Log ([ordered]@{Event='ReadinessLost';Group=$g.Id;Time=$time})
                        }
                    }
                }
                $decision=Get-PopulationGroupDecision $sample $Groups $TargetPopulation $ReservedHumanSlots $time
                if($fence){
                    $removedStillPresent=@($fence.Names|Where-Object{$_ -in $sample.Names}).Count -gt 0
                    if($sample.Total -le $fence.ExpectedTotal -or !$removedStillPresent -or $time -ge $fence.Deadline){$fence=$null}
                }
                if($decision.Action -eq 'Start' -and ($stable -lt 2 -or !$allReady)){$decision.Action='Hold';$decision.Reason='WaitingForStableReadySample'}
                if($decision.Action -eq 'Start'){
                    $candidate=@($Groups|Where-Object Id -eq $decision.GroupId)[0]
                    if(@($candidate.Names|Where-Object{$_ -in $sample.Names}).Count){$decision.Action='Hold';$decision.Reason='PreviousGroupSlotsStillPresent'}
                }
                if($fence){$decision.Action='Hold';$decision.Reason='WaitingForSlotRelease'}
                & $Log ([ordered]@{Event='Observation';Time=$time;Total=$sample.Total;Cap=$decision.Cap;Action=$decision.Action;Group=$decision.GroupId;Reason=$decision.Reason;ObserveOnly=[bool]$ObserveOnly})
                if(!$ObserveOnly -and $decision.Action -in 'Start','Stop'){
                    $g=@($Groups|Where-Object Id -eq $decision.GroupId)[0]
                    if($decision.Action -eq 'Start'){
                        # Start adapter must roll back its own partial-launch errors.
                        $g.Record=& $StartGroup $g
                        $g.Active=$true;$g.Pending=$true;$g.Deadline=[double](& $Now)+45
                    }else{
                        & $StopGroup $g
                        $g.Active=$false;$g.Pending=$false;$g.EligibleAt=[double](& $Now)+10
                        $fence=@{Names=@($g.Names);ExpectedTotal=[math]::Max(0,$sample.Total-$g.Size);Deadline=[double](& $Now)+45}
                    }
                    $stable=0;$key=$null
                    & $Log ([ordered]@{Event=$decision.Action;Group=$g.Id;Time=$time})
                }
            }else{$stable=0;$key=$null}
            if($Iterations -eq 0 -or $poll -lt $Iterations){& $Wait $PollMilliseconds}
        }
    }catch{$operationError=$_;throw}
    finally{
        $cleanup=@()
        if(!$ObserveOnly){
            foreach($g in @($Groups|Where-Object Active)){
                try{& $StopGroup $g;$g.Active=$false}catch{$cleanup+=@($_.Exception.Message)}
            }
        }
        if($cleanup.Count){if($operationError){Write-Warning ($cleanup -join '; ')}else{throw ('Owned cleanup failed: '+($cleanup -join '; '))}}
    }
}
function Stop-PopulationOwnedLaunch([string]$ExpectedExe,[datetime]$NotBeforeUtc) {
    foreach($p in @(Get-Process -ErrorAction SilentlyContinue)){
        try{
            [void]$p.Handle
            if($p.Id -eq $PID -or $p.HasExited -or $p.Path -ne $ExpectedExe -or $p.StartTime.ToUniversalTime() -lt $NotBeforeUtc.ToUniversalTime()){continue}
            $identity=Get-CimInstance Win32_Process -Filter ("ProcessId="+$p.Id) -ErrorAction Stop
            if(!$identity -or $identity.ParentProcessId -ne $PID){continue}
            # The retained handle pins the identity checked above, even if the PID is reused.
            $p.Kill()
            if(!$p.WaitForExit(5000)){throw 'Owned post-launch rollback timed out.'}
        }catch [System.ComponentModel.Win32Exception] {
            # Unreadable processes cannot establish ownership and are never stopped.
            continue
        }catch [System.InvalidOperationException] {continue}
        finally{$p.Dispose()}
    }
}
function Stop-PopulationOwnedRecord($Record,[int]$GracefulWaitSeconds=5) {
    # The in-memory start identity is authoritative; disk receipts are evidence only.
    $p=Get-Process -Id $Record.Entry.pid -ErrorAction SilentlyContinue
    if(!$p){return}
    try{
        [void]$p.Handle
        $start=([datetimeoffset]$Record.Entry.startedUtc).UtcDateTime
        if($p.HasExited -or $p.Path -ne $Record.Entry.exe -or $p.StartTime.ToUniversalTime().Ticks -ne $start.Ticks){return}
        $identity=Get-CimInstance Win32_Process -Filter ("ProcessId="+$p.Id) -ErrorAction Stop
        if($p.Id -eq $PID -or !$identity -or $identity.ParentProcessId -ne $PID){throw 'Refusing to stop a process not created by this supervisor.'}
        $outcome='window-exit-unverified'
        if(!$p.CloseMainWindow() -or !$p.WaitForExit($GracefulWaitSeconds*1000)){
            $p.Kill();if(!$p.WaitForExit(5000)){throw 'Owned child did not stop.'};$outcome='forced'
        }
        $receipt=@{pid=$p.Id;state=$outcome;exitCode=$p.ExitCode;stoppedUtc=[datetime]::UtcNow.ToString('o')}
        try{$receipt|ConvertTo-Json|Set-Content -LiteralPath ($Record.StatePath+'.supervisor-stopped.json')}catch{Write-Warning ('Child stopped; stop receipt unavailable: '+$_.Exception.Message)}
        return $receipt
    }finally{$p.Dispose()}
}
function Test-PopulationOwnedRunning($Record) {
    if(!$Record -or !$Record.Entry){return $false}
    $p=Get-Process -Id $Record.Entry.pid -ErrorAction SilentlyContinue
    if(!$p){return $false}
    try{
        [void]$p.Handle
        $time=([datetimeoffset]$Record.Entry.startedUtc).UtcDateTime
        return $p.Path -eq $Record.Entry.exe -and $p.StartTime.ToUniversalTime().Ticks -eq $time.Ticks -and !$p.HasExited
    }finally{$p.Dispose()}
}
function Test-PopulationNativeReady($Group,$Sample) {
    if(!(Test-PopulationOwnedRunning $Group.Record)){return $false}
    foreach($name in $Group.Names){if(@($Sample.Names|Where-Object{$_ -ceq $name}).Count -ne 1){return $false}}
    $path=Join-Path $Group.Config.processes[0].clientDir 'SeriousSam.log'
    if(!(Test-Path -LiteralPath $path)){return $false}
    $started=([datetimeoffset]$Group.Record.Entry.startedUtc).UtcDateTime
    if((Get-Item -LiteralPath $path).LastWriteTimeUtc -lt $started){return $false}
    $text=Get-Content -LiteralPath $path -Raw
    # Retail clients emit an indented "joined"; CRC check OK is server evidence.
    $joins=@([regex]::Matches($text,'(?m)^\s*joined\s*$'))
    if(!$joins.Count){return $false}
    $joined=$joins[-1].Index
    $fail=@([regex]::Matches($text,'(?im)^.*(?:Disconnected|Connection timed out|Cannot join|Timeout while waiting|Session has been stopped|sync lost|out of sync|bad sync|wrong crc|stopping game).*$'))
    if($fail.Count -and $fail[-1].Index -gt $joined){return $false}
    foreach($slot in 0..($Group.Size-1)){
        $drivers=@([regex]::Matches($text,('(?m)^\[BotDriver\] local player '+$slot+' \(player index \d+\) is now bot-driven: '+[regex]::Escape($Group.Names[$slot])+'\r?$')))
        if(!$drivers.Count -or $drivers[-1].Index -lt $joined){return $false}
    }
    return $true
}
function Invoke-PopulationSupervisor {
    param([string]$Config,[string]$StateDirectory,[ValidateRange(0,16)][int]$TargetPopulation=8,
          [ValidateRange(0,15)][int]$ReservedHumanSlots=2,[ValidateRange(100,5000)][int]$PollMilliseconds=1000,
          [ValidateRange(0,100000)][int]$Iterations=0,[switch]$ObserveOnly,[string]$FleetState)
    $fleet=Get-FleetConfig $Config
    $identities=Get-FleetIdentities $fleet
    if(Test-Path -LiteralPath $StateDirectory){throw 'Use a new supervisor state directory.'}
    $state=(New-Item -ItemType Directory -Path $StateDirectory).FullName
    $groups=@();$locks=@();$clock=[Diagnostics.Stopwatch]::StartNew()
    try{
        if(!$ObserveOnly){$locks=Enter-PopulationClientLocks @($fleet.processes.clientDir)}
        $existing=$null
        if($FleetState){if(!$ObserveOnly){throw 'Existing fleet state is read-only observation only.'};$existing=Get-Content -LiteralPath $FleetState -Raw|ConvertFrom-Json}
        foreach($i in 0..($fleet.processes.Count-1)){
            $entry=$fleet.processes[$i]
            $sub=[pscustomobject]@{server=$fleet.server;startStaggerSeconds=0;processes=@($entry)}
            $g=[pscustomobject]@{Id="$i";Size=[int]$entry.localPlayers;Names=@($identities|Where-Object clientDir -eq $entry.clientDir|ForEach-Object name);Config=$sub;Active=$false;EligibleAt=0;Record=$null;Generation=0}
            if($existing){
                $record=@($existing.processes|Where-Object clientDir -eq $entry.clientDir)
                if($record.Count -gt 1){throw 'Ambiguous fleet state.'}
                if($record.Count){$g.Record=@{Entry=$record[0];StatePath=$FleetState};$g.Active=Test-PopulationOwnedRunning $g.Record}
            }elseif(!$ObserveOnly -and (Get-Process SeriousSam -ErrorAction SilentlyContinue|Where-Object Path -eq (Join-Path $entry.clientDir 'Bin/SeriousSam.exe'))){throw 'Client already running; never adopt it.'}
            $groups+=@($g)
        }
        $server=$fleet.server.Substring(0,$fleet.server.LastIndexOf(':'))
        $port=if($fleet.queryPort){[int]$fleet.queryPort}else{[int]$fleet.server.Split(':')[-1]+1}
        if($port -lt 1 -or $port -gt 65535){throw 'Invalid query port.'}
        $read={
            $before=Invoke-FleetQuery -Request '\status\' -Server $server -Port $port
            $players=Invoke-FleetQuery -Request '\players\' -Server $server -Port $port
            $after=Invoke-FleetQuery -Request '\status\' -Server $server -Port $port
            ConvertTo-PopulationSample $before $players $after
        }
        $start={
            param($g)
            $g.Generation++
            $prefix=Join-Path $state ("group-"+$g.Id+"-"+$g.Generation)
            $cfg=$prefix+'.config.json';$sf=$prefix+'.state.json'
            $g.Config|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $cfg
            $log=Join-Path $g.Config.processes[0].clientDir 'SeriousSam.log'
            if(Test-Path -LiteralPath $log){Copy-Item -LiteralPath $log -Destination ($prefix+'.before.log');Remove-Item -LiteralPath $log}
            $launchAt=[datetime]::UtcNow
            try{
                & "$PSScriptRoot/Start-BotFleet.ps1" -Config $cfg -State $sf | Out-Null
                $record=Get-Content -LiteralPath $sf -Raw|ConvertFrom-Json
                if(@($record.processes).Count -ne 1){throw 'Expected exactly one started group.'}
                $held=@{Entry=$record.processes[0];StatePath=$sf}
                if($held.Entry.exe -ne (Join-Path $g.Config.processes[0].clientDir 'Bin/SeriousSam.exe') -or !(Test-PopulationOwnedRunning $held)){throw 'Started group state does not identify the live expected client.'}
                $origin=Get-CimInstance Win32_Process -Filter ("ProcessId="+$held.Entry.pid) -ErrorAction Stop
                if(!$origin -or $origin.ParentProcessId -ne $PID -or ([datetimeoffset]$held.Entry.startedUtc).UtcDateTime -lt $launchAt){throw 'Started group ownership is unproven.'}
                return $held
            }catch{
                $primary=$_
                try{Stop-PopulationOwnedLaunch -ExpectedExe (Join-Path $g.Config.processes[0].clientDir 'Bin/SeriousSam.exe') -NotBeforeUtc $launchAt}catch{Write-Warning ('Post-launch cleanup failed: '+$_.Exception.Message)}
                throw $primary
            }
        }
        $stop={
            param($g)
            if(Test-PopulationOwnedRunning $g.Record){Stop-PopulationOwnedRecord $g.Record -GracefulWaitSeconds 5 | Out-Null}
            if(Test-PopulationOwnedRunning $g.Record){throw 'Owned group still running.'}
        }
        $log={param($e) $e.utc=[datetime]::UtcNow.ToString('o');$e|ConvertTo-Json -Compress|Add-Content -LiteralPath (Join-Path $state 'events.jsonl')}
        $stopRequested={Test-Path -LiteralPath (Join-Path $state 'stop.request')}
        $now={$clock.Elapsed.TotalSeconds}
        Invoke-PopulationLoop -Groups $groups -TargetPopulation $TargetPopulation -ReservedHumanSlots $ReservedHumanSlots -PollMilliseconds $PollMilliseconds -Iterations $Iterations -ObserveOnly:$ObserveOnly -ReadSample $read -StartGroup $start -StopGroup $stop -IsRunning {param($g) Test-PopulationOwnedRunning $g.Record} -IsReady {param($g,$s) Test-PopulationNativeReady $g $s} -Now $now -Wait {param($ms) Start-Sleep -Milliseconds $ms} -Log $log -StopRequested $stopRequested
        [ordered]@{completed=$true;nativeAcceptance=$false;scope='Whole-process conservative occupancy controller; no Human prefix classification or exact single-slot/race/24h guarantee';observeOnly=[bool]$ObserveOnly;groups=$groups.Count}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $state 'completed.json')
    }finally{foreach($h in $locks){$h.Dispose()};$clock.Stop()}
}
