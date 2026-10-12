$ErrorActionPreference='Stop'
. "$PSScriptRoot\ShadowRuntimeLog.ps1"
$after="  joined`nDisconnected: Server stopped.`nstopping game.`nCannot join game:`nTimeout while waiting for reply`n-> /Quit()`nRenderer buffers cleared.`nCDS: mode reset"
if(@(Get-UnexpectedRuntimeMarkers $after $true).Count){throw 'Expected post-server-stop timeout rejected.'}
if(@(Get-UnexpectedRuntimeMarkers $after $false).Count -ne 1){throw 'Stability mode accepted a timeout.'}
if(@(Get-UnexpectedRuntimeMarkers ("Timeout while waiting`n"+$after) $true).Count -ne 1){throw 'Earlier timeout masked by later stop.'}
if(@(Get-UnexpectedRuntimeMarkers ($after+"`nwrong crc`nout of sync`naccess violation") $true).Count -ne 3){throw 'Shutdown masked runtime faults.'}
if(@(Get-UnexpectedRuntimeMarkers "joined`nClient: Timeout receiving UDP port" $true).Count -ne 1){throw 'Unexplained client timeout accepted.'}
if(@(Get-UnexpectedRuntimeMarkers "Disconnected: Server stopped.`n  joined`nTimeout while waiting" $true).Count -ne 1){throw 'Later joined session timeout masked by old stop.'}
if(@(Get-UnexpectedRuntimeMarkers "Disconnected: Server stopped.`nClient: Timeout receiving UDP port" $true).Count){throw 'Expected UDP-port timeout rejected.'}
if(@(Get-UnexpectedRuntimeMarkers "joined`nPlayer chat: Disconnected: Server stopped.`nTimeout while waiting" $true).Count -ne 1){throw 'Embedded stop text masked timeout.'}
if(@(Get-UnexpectedRuntimeMarkers "joined`nDisconnected: Server stopped.`nTimeout while waiting`nDisconnected: Server stopped." $true).Count){throw 'Repeated native stop rejected earlier expected timeout.'}
'SHADOW RUNTIME LOG CHECKS PASS'
