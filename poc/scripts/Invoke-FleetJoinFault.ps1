param(
    [Parameter(Mandatory)][int]$ServerPid,
    [Parameter(Mandatory)][long]$StartedUtcTicks,
    [Parameter(Mandatory)][int]$OwnerPid,
    [Parameter(Mandatory)][string]$Evidence
)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/FleetProcessControl.ps1"
$repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$retail=Join-Path $repo '.codex/retail'
$serverExe=[IO.Path]::GetFullPath("$retail/TSE-Server/Bin/DedicatedServer.exe")
$serverLog="$retail/TSE-Server/Dedicated_BotTest.log"
$logs=@("$retail/TSE-BotClient/SeriousSam.log","$retail/TSE-BotClient2/SeriousSam.log")
$p=$null;$paused=$false;$passed=$false;$errorText=$null;$resumed=$false
$record=[ordered]@{serverPid=$ServerPid;startedUtcTicks=$StartedUtcTicks;ownerPid=$OwnerPid;target=$serverExe;trigger='DM_LittleTrouble.wld';passed=$false}
try {
    $p=Get-OwnedPinnedProcess $ServerPid $serverExe $StartedUtcTicks $OwnerPid
    # Preload the native boundary before the short map/retry race.
    if(!('FleetNativePause' -as [type])){
        Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class FleetNativePause { [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr p); [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr p); }'
    }
    $deadline=[datetime]::UtcNow.AddSeconds(180)
    do {
        if($p.HasExited){throw 'Owned server exited before fault trigger.'}
        $text=Get-Content -LiteralPath $serverLog -Raw
        if($text -match "(?m)^\s*level: '.*\\DM_LittleTrouble\.wld'"){break}
        if([datetime]::UtcNow -gt $deadline){throw 'Native second-map trigger not observed.'}
        Start-Sleep -Milliseconds 25
    }while($true)
    $offsets=@($logs|ForEach-Object{(Get-Content -LiteralPath $_ -Raw).Length})
    Set-OwnedProcessPaused $p $true;$paused=$true
    $record.pausedUtc=[datetime]::UtcNow.ToString('o')
    $record.logOffsets=$offsets
    $record|ConvertTo-Json -Depth 5|Set-Content "$Evidence/fault-started.json"
    $deadline=[datetime]::UtcNow.AddSeconds(60)
    do {
        $failed=@(foreach($i in 0..1){
            $text=Get-Content -LiteralPath $logs[$i] -Raw
            $fresh=$text.Substring([Math]::Min($offsets[$i],$text.Length))
            [bool]($fresh -match '(?m)^\[BotReconnect\] result=failed\r?$' -and $fresh -match '(?m)^Cannot join game:\r?\n(Timeout while waiting for reply|Client: Timeout receiving UDP port)\r?$')
        })
        if($failed[0] -and $failed[1]){$passed=$true;break}
        if($p.HasExited){throw 'Owned server exited during join fault.'}
        Start-Sleep -Milliseconds 100
    }until([datetime]::UtcNow -gt $deadline)
    $record.failedByClient=$failed
    if(!$passed){throw 'Both native failed joins were not observed within the bounded pause.'}
}catch{$errorText=$_.Exception.Message}
finally {
    if($paused){
        try{Set-OwnedProcessPaused $p $false;$resumed=$true}catch{$errorText="Resume failed: $($_.Exception.Message)";$passed=$false}
    }
    $record.resumedUtc=[datetime]::UtcNow.ToString('o')
    $record.resumed=$resumed;$record.passed=($passed -and $resumed);$record.error=$errorText
    $record|ConvertTo-Json -Depth 5|Set-Content "$Evidence/fault-finished.json"
    if($p){$p.Dispose()}
}
if(!$record.passed){throw "Native join fault injection failed: $errorText"}
