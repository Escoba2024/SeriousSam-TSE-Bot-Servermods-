# External guardian. Ownership exists only in this process, never in a receipt.
$ErrorActionPreference='Stop'

function New-PopulationWatchdogContext {
    return @{OwnerId=[guid]::NewGuid().ToString('N');Children=@{};Failures=@()}
}
function New-PopulationWatchdogIdentity($Process,[string]$OwnerId,[string]$ExpectedExe) {
    [void]$Process.Handle # Pin before inspecting metadata or acknowledging launch.
    # Windows can expose an empty MainModule path while a child initializes.
    # Refresh this same pinned object for at most 500ms; never reopen a PID.
    $path=$null
    for($attempt=0;$attempt -le 20;$attempt++){
        if($Process.HasExited){throw 'Launched process exited before ownership capture.'}
        $path=$Process.Path
        if($path){break}
        if($attempt -lt 20){Start-Sleep -Milliseconds 25;$Process.Refresh()}
    }
    if(!$ExpectedExe -or $path -cne $ExpectedExe){throw 'Launched process executable identity is unavailable or differs from plan.'}
    return @{Process=$Process;OwnerId=$OwnerId;Pid=$Process.Id;Exe=$path;StartedUtc=$Process.StartTime.ToUniversalTime()}
}
function Register-PopulationWatchdogChild($Context,[string]$Group,$Process,[string]$ExpectedExe) {
    $record=@{Process=$Process;OwnerId=$Context.OwnerId;Pid=$Process.Id;Exe=$ExpectedExe;StartedUtc=$null;CapturePending=$false}
    $Context.Children[$Group]=$record
    $launchHandle=$Process.Handle
    if($null -eq $launchHandle -or $launchHandle -eq [IntPtr]::Zero){throw 'Launch process handle is unavailable; identity capture is unproven.'}
    # Only a successfully pinned launch may retry incomplete metadata capture.
    $record.CapturePending=$true
    $identity=New-PopulationWatchdogIdentity $Process $Context.OwnerId $ExpectedExe
    $Context.Children[$Group]=$identity
    return $identity
}
function Stop-PopulationWatchdogChild($Context,$Record) {
    # No PID lookup, tree kill, state-file input, window messages or name-based stop.
    $p=$Record.Process
    if($Record.OwnerId -cne $Context.OwnerId -or $Record.Pid -eq $PID){throw 'Watchdog owner identity mismatch.'}
    if($p.HasExited){return}
    [void]$p.Handle
    if($p.Id -ne $Record.Pid){throw 'Watchdog child identity mismatch; refusing stop.'}
    if($Record.CapturePending -eq $true){
        $identity=New-PopulationWatchdogIdentity $p $Context.OwnerId $Record.Exe
        $Record.StartedUtc=$identity.StartedUtc
        $Record.CapturePending=$false
    }
    if($p.Id -ne $Record.Pid -or $p.Path -cne $Record.Exe -or
       $p.StartTime.ToUniversalTime().Ticks -ne $Record.StartedUtc.Ticks){throw 'Watchdog child identity mismatch; refusing stop.'}
    $p.Kill()
    if(!$p.WaitForExit(5000)){throw 'Watchdog owned child did not exit.'}
}
function Invoke-PopulationOrphanCleanup($Context,[bool]$ControllerExited) {
    if(!$ControllerExited){return $false}
    $ok=$true
    foreach($record in @($Context.Children.Values)){
        try{Stop-PopulationWatchdogChild $Context $record}catch{$ok=$false;$Context.Failures+=@($_.Exception.Message)}
    }
    return $ok
}
function Write-PopulationWatchdogJson([string]$Path,$Value) {
    $temp=$Path+'.'+[guid]::NewGuid().ToString('N')+'.tmp'
    $backup=$temp+'.bak'
    try{
        [IO.File]::WriteAllText($temp,($Value|ConvertTo-Json -Depth 8 -Compress))
        # A real backup path also works on Windows PowerShell 5.1, which coerces
        # a null string argument to an invalid empty path. Retry sharing races.
        for($attempt=0;;$attempt++){
            try{
                if([IO.File]::Exists($Path)){[IO.File]::Replace($temp,$Path,$backup)}else{[IO.File]::Move($temp,$Path)}
                break
            }catch [IO.IOException]{if($attempt -ge 20){throw};Start-Sleep -Milliseconds 25}
        }
    }finally{foreach($file in $temp,$backup){if([IO.File]::Exists($file)){[IO.File]::Delete($file)}}}
}
function Get-PopulationWatchdogCaller {
    $p=Get-Process -Id $PID
    try{return @{pid=$PID;exe=$p.Path;startedUtc=$p.StartTime.ToUniversalTime().ToString('o')}}finally{$p.Dispose()}
}
function Test-PopulationWatchdogPeer($Identity) {
    $p=Get-Process -Id $Identity.pid -ErrorAction SilentlyContinue
    if(!$p){return $false}
    try{
        [void]$p.Handle
        return !$p.HasExited -and $p.Path -ceq $Identity.exe -and $p.StartTime.ToUniversalTime().Ticks -eq ([datetimeoffset]$Identity.startedUtc).UtcTicks
    }catch{return $false}finally{$p.Dispose()}
}
function Invoke-PopulationWatchdogRequest($Session,[string]$Action,[string]$Group='',[int]$TimeoutSeconds=15) {
    $Session.Sequence++
    $seq=$Session.Sequence
    $requestId=[guid]::NewGuid().ToString('N')
    $request=@{ownerId=$Session.OwnerId;requestId=$requestId;sequence=$seq;action=$Action;group=$Group;caller=(Get-PopulationWatchdogCaller)}
    Write-PopulationWatchdogJson (Join-Path $Session.Directory 'request.json') $request
    $timer=[Diagnostics.Stopwatch]::StartNew()
    while($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds){
        if(!(Test-PopulationWatchdogPeer $Session.Watchdog)){throw 'External watchdog is unavailable; no local fallback launch or stop.'}
        $reply=$null
        try{$reply=Get-Content -LiteralPath (Join-Path $Session.Directory 'response.json') -Raw -ErrorAction Stop|ConvertFrom-Json}catch{}
        if($reply -and $reply.ownerId -ceq $Session.OwnerId -and $reply.requestId -ceq $requestId -and $reply.sequence -eq $seq){
            if(!$reply.ok){throw ('Watchdog refused operation: '+$reply.error)}
            return $reply.result
        }
        Start-Sleep -Milliseconds 50
    }
    throw 'Watchdog request timed out; controller must exit, guardian retains cleanup ownership.'
}
function Open-PopulationWatchdogSession([string]$Path) {
    $session=Get-Content -LiteralPath $Path -Raw|ConvertFrom-Json
    if($session.format -cne 'SeriousSamPopulationWatchdog/v1' -or $session.ownerId -cnotmatch '^[a-f0-9]{32}$' -or
       [IO.Path]::GetFullPath($Path) -cne (Join-Path $session.directory 'session.json')){throw 'Invalid watchdog session.'}
    $session|Add-Member Sequence 0
    Invoke-PopulationWatchdogRequest $session Hello|Out-Null
    return $session
}
function Assert-PopulationWatchdogInstallationsFree($Plans) {
    foreach($p in @(Get-Process)){
        try{
            $path=$p.Path
            if(!$path -and $p.ProcessName -eq 'SeriousSam'){throw 'Unreadable game process; cannot prove installation is free.'}
            if($path -and @($Plans|Where-Object exe -eq $path).Count -and !$p.HasExited){throw 'Client already running; watchdog never adopts it.'}
        }finally{$p.Dispose()}
    }
}
function Test-PopulationWatchdogRequestIdentity($Request,$Context,$ControllerIdentity,[long]$NextSequence) {
    try{
        return $Request.ownerId -ceq $Context.OwnerId -and $Request.requestId -cmatch '^[a-f0-9]{32}$' -and
            ($Request.sequence -is [long] -or $Request.sequence -is [int]) -and $Request.sequence -eq $NextSequence -and
            $Request.caller.pid -eq $ControllerIdentity.Pid -and $Request.caller.exe -ceq $ControllerIdentity.Exe -and
            ([datetimeoffset]$Request.caller.startedUtc).UtcDateTime.Ticks -eq $ControllerIdentity.StartedUtc.Ticks
    }catch{return $false}
}
function Invoke-PopulationWatchdog {
    param([object[]]$Plans,[string[]]$Directories,[string]$StateDirectory,
          [scriptblock]$StartController,[scriptblock]$CheckFree={param($plans) Assert-PopulationWatchdogInstallationsFree $plans})
    # StartController and CheckFree are internal test seams, never mailbox inputs.
    if(Test-Path -LiteralPath $StateDirectory){throw 'Use a new watchdog state directory; stale state is never adopted.'}
    $directory=(New-Item -ItemType Directory -Path $StateDirectory).FullName
    $ctx=New-PopulationWatchdogContext
    $locks=@();$controller=$null;$clean=$false;$lastSequence=0
    try{
        $locks=Enter-PopulationClientLocks $Directories
        & $CheckFree $Plans
        $session=@{format='SeriousSamPopulationWatchdog/v1';ownerId=$ctx.OwnerId;directory=$directory;watchdog=(Get-PopulationWatchdogCaller)}
        $sessionPath=Join-Path $directory 'session.json'
        Write-PopulationWatchdogJson $sessionPath $session
        $controller=& $StartController $sessionPath
        [void]$controller.Handle
        $controllerIdentity=New-PopulationWatchdogIdentity $controller $ctx.OwnerId $session.watchdog.exe
        Write-PopulationWatchdogJson (Join-Path $directory 'controller.json') @{pid=$controllerIdentity.Pid;exe=$controllerIdentity.Exe;startedUtc=$controllerIdentity.StartedUtc.ToString('o');ownerId=$ctx.OwnerId}
        while(!$controller.HasExited){
            $requestPath=Join-Path $directory 'request.json'
            if(Test-Path -LiteralPath $requestPath){
                $request=$null;$result=$null;$errorText=$null
                try{
                    $request=Get-Content -LiteralPath $requestPath -Raw|ConvertFrom-Json
                    Remove-Item -LiteralPath $requestPath
                    if(!(Test-PopulationWatchdogRequestIdentity $request $ctx $controllerIdentity ($lastSequence+1))){throw 'Request owner, sequence or controller identity mismatch.'}
                    $lastSequence=$request.sequence
                    if($controller.HasExited){break}
                    $key=[string]$request.group
                    switch -CaseSensitive ($request.action){
                        Hello {$result=@{ownerId=$ctx.OwnerId}}
                        Start {
                            $index=0
                            if(![int]::TryParse($key,[ref]$index) -or $index -lt 0 -or $index -ge $Plans.Count -or $key -cne [string]$index){throw 'Unknown configured group.'}
                            if($ctx.Children.ContainsKey($key)){
                                if(!$ctx.Children[$key].Process.HasExited){throw 'Group still running.'}
                                $ctx.Children[$key].Process.Dispose()
                                $ctx.Children.Remove($key)
                            }
                            & $CheckFree @($Plans[$index])
                            if($controller.HasExited){break}
                            $plan=$Plans[$index]
                            $p=Start-Process -FilePath $plan.exe -ArgumentList $plan.arguments -WorkingDirectory $plan.workingDir -WindowStyle Hidden -PassThru
                            # Retain the pinned launch even if metadata capture fails.
                            $identity=Register-PopulationWatchdogChild $ctx $key $p $plan.exe
                            $result=@{pid=$identity.Pid;exe=$identity.Exe;startedUtc=$identity.StartedUtc.ToString('o');ownerId=$ctx.OwnerId}
                            Write-PopulationWatchdogJson (Join-Path $directory ('group-'+$key+'.json')) $result
                        }
                        Stop {
                            if(!$ctx.Children.ContainsKey($key)){throw 'Unknown owned group.'}
                            Stop-PopulationWatchdogChild $ctx $ctx.Children[$key]
                            $result=@{stopped=$true;ownerId=$ctx.OwnerId}
                        }
                        default {throw 'Unknown watchdog operation.'}
                    }
                }catch{$errorText=$_.Exception.Message}
                # An acknowledgement failure must not lose the held ownership record.
                if($request){
                    try{Write-PopulationWatchdogJson (Join-Path $directory 'response.json') @{ownerId=$ctx.OwnerId;requestId=$request.requestId;sequence=$request.sequence;ok=($null -eq $errorText);error=$errorText;result=$result}}catch{Write-Warning 'Watchdog response unavailable; waiting for controller exit.'}
                }
            }
            Start-Sleep -Milliseconds 50
        }
        $clean=Invoke-PopulationOrphanCleanup $ctx $controller.HasExited
        Write-PopulationWatchdogJson (Join-Path $directory 'completed.json') @{ownerId=$ctx.OwnerId;controllerExited=$controller.HasExited;controllerExitCode=$controller.ExitCode;cleanupPassed=$clean;failures=@($ctx.Failures);nativeAcceptance=$false}
        if(!$clean){throw 'External watchdog cleanup failed closed; inspect private completion evidence.'}
        if($controller.ExitCode -ne 0){throw ('Controller exited with code '+$controller.ExitCode+'; watchdog cleanup passed.')}
    }finally{
        # A guardian interruption is not proof the controller is dead. Never stop a live controller's clients here.
        if($controller -and $controller.HasExited -and !$clean){[void](Invoke-PopulationOrphanCleanup $ctx $true)}
        foreach($record in @($ctx.Children.Values)){$record.Process.Dispose()}
        if($controller){$controller.Dispose()}
        foreach($h in $locks){$h.Dispose()}
    }
}
