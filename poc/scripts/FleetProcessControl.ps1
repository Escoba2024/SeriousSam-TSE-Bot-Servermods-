function Get-OwnedPinnedProcess([int]$ProcessId,[string]$ExpectedExe,[long]$StartedUtcTicks,[int]$OwnerProcessId) {
    $p=[Diagnostics.Process]::GetProcessById($ProcessId)
    # Pin the process object before reading identity; never operate through a
    # newly acquired PID after validation.
    $null=$p.Handle
    $origin=Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId"
    if($p.HasExited -or $p.Path -ne $ExpectedExe -or $p.StartTime.ToUniversalTime().Ticks -ne $StartedUtcTicks -or !$origin -or $origin.ParentProcessId -ne $OwnerProcessId){
        $p.Dispose();throw 'Pause target is not the expected live owned process.'
    }
    return $p
}
function Set-OwnedProcessPaused([Diagnostics.Process]$Process,[bool]$Paused) {
    if(!('FleetNativePause' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class FleetNativePause {
    [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr process);
    [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr process);
}
'@
    }
    if($Process.HasExited){throw 'Owned process already exited.'}
    $status=if($Paused){[FleetNativePause]::NtSuspendProcess($Process.Handle)}else{[FleetNativePause]::NtResumeProcess($Process.Handle)}
    if($status -ne 0){throw "Owned process pause/resume failed: NTSTATUS $status"}
}
