$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationWatchdog.ps1"
# Real helper processes with same-process metadata fault proxies. No mailbox/Windows-CIM
# substitute: this suite covers launch registration and orphan cleanup only.
function Invoke-CaptureCase([string]$Mode) {
    $shell=(Get-Process -Id $PID).Path
    $launch=@{FilePath=$shell;ArgumentList='-NoProfile -Command "Start-Sleep -Seconds 60"';PassThru=$true}
    if([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT){$launch.WindowStyle='Hidden'}
    $children=@()
    try{
        $controller=Start-Process @launch;$children+=@($controller)
        $client=Start-Process @launch;$children+=@($client)
        $unrelated=Start-Process @launch;$children+=@($unrelated)
        foreach($p in $children){[void]$p.Handle}
        # Process.Path is a non-overridable PowerShell type-data property. A
        # metadata proxy injects faults while every lifetime/kill call reaches
        # the actual pinned child object kept in $children for final teardown.
        $client=[pscustomobject]@{Native=$client;Mode=$Mode;CaptureReads=0}
        $client|Add-Member ScriptProperty Id {return $this.Native.Id}
        $client|Add-Member ScriptProperty HasExited {return $this.Native.HasExited}
        $client|Add-Member ScriptProperty Handle {
            if($this.Mode -eq 'PinFailure'){$this.CaptureReads++;if($this.CaptureReads -eq 1){throw 'Injected launch pin failure'}}
            return $this.Native.Handle
        }
        $client|Add-Member ScriptProperty StartTime {
            if($this.Mode -in 'TransientStartTime','WrongOwner','WrongPid','WrongExe'){$this.CaptureReads++;if($this.CaptureReads -eq 1){throw 'Injected transient start-time read failure'}}
            return $this.Native.StartTime
        }
        $client|Add-Member ScriptProperty Path {
            if($this.Mode -in 'DelayedPath','PermanentPath'){
                $this.CaptureReads++
                if($this.Mode -eq 'PermanentPath' -or $this.CaptureReads -le 21){return $null}
            }
            return $this.Native.Path
        }
        $client|Add-Member ScriptMethod Refresh {$this.Native.Refresh()}
        $client|Add-Member ScriptMethod Kill {$this.Native.Kill()}
        $client|Add-Member ScriptMethod WaitForExit {param($ms)return $this.Native.WaitForExit($ms)}
        $ctx=New-PopulationWatchdogContext
        $failure=$null
        try{Register-PopulationWatchdogChild $ctx '0' $client $shell|Out-Null}catch{$failure=$_.Exception.Message}
        if(!$ctx.Children.ContainsKey('0')){throw ('Launch registration did not retain its real child: '+$failure)}
        $expectedFailure=$Mode -in 'TransientStartTime','DelayedPath','PermanentPath','WrongOwner','WrongPid','WrongExe','PinFailure'
        if([bool]$failure -ne $expectedFailure){throw "Capture fault was not exercised: $Mode"}
        if($Mode -eq 'WrongOwner'){$ctx.Children['0'].OwnerId='foreign'}
        if($Mode -eq 'WrongPid'){$ctx.Children['0'].Pid++}
        if($Mode -eq 'WrongExe'){$ctx.Children['0'].Exe=$shell+'.foreign'}
        if($Mode -eq 'UnmarkedMissingStart'){$ctx.Children['0'].StartedUtc=$null}
        $beforeReads=$client.CaptureReads
        if((Invoke-PopulationOrphanCleanup $ctx $controller.HasExited) -or $client.HasExited){throw 'Live controller lost its owned child.'}
        if($beforeReads -ne $client.CaptureReads){throw 'Live-controller cleanup retried identity capture.'}
        $controller.Kill()
        if(!$controller.WaitForExit(5000)){throw 'Fixture controller did not exit.'}
        $clean=Invoke-PopulationOrphanCleanup $ctx $controller.HasExited
        $mustRefuse=$Mode -in 'PermanentPath','WrongOwner','WrongPid','WrongExe','PinFailure','UnmarkedMissingStart'
        if($mustRefuse){
            if($clean -or $client.HasExited -or !$ctx.Failures.Count){throw "Unproven identity stopped or reported clean: $Mode"}
        }else{
            if(!$clean -or !$client.WaitForExit(1000)){throw "Recoverable capture failure orphaned real child: $Mode"}
            if(!(Invoke-PopulationOrphanCleanup $ctx $true)){throw 'Repeated cleanup was not idempotent.'}
        }
        if($unrelated.HasExited){throw 'Capture cleanup affected unrelated helper.'}
    }finally{
        # Teardown exclusively through these actual launch objects.
        foreach($p in $children){try{if(!$p.HasExited){$p.Kill();[void]$p.WaitForExit(5000)}}finally{$p.Dispose()}}
    }
}
foreach($mode in 'None','TransientStartTime','DelayedPath','PermanentPath','WrongOwner','WrongPid','WrongExe','PinFailure','UnmarkedMissingStart'){Invoke-CaptureCase $mode}
'WATCHDOG CAPTURE PASS: 9 real helper-process scenarios; unreadable/unproven identities remain fail-closed'
