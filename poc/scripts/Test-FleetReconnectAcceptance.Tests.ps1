$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../tools/ShadowRuntimeLog.ps1"
if(Test-Path "$PSScriptRoot/FleetReconnectAcceptance.ps1"){. "$PSScriptRoot/FleetReconnectAcceptance.ps1"}
function Allowed([string]$Text){
    if(Get-Command Get-RecoveredJoinTimeouts -ErrorAction SilentlyContinue){return @(Get-RecoveredJoinTimeouts $Text)}
    return @()
}
$failed="[BotReconnect] attempt address=127.0.0.1:25600`nCannot join game:`nTimeout while waiting for reply`n[BotReconnect] result=failed`n"
$joined="[BotReconnect] attempt address=127.0.0.1:25600`n  joined`n[BotReconnect] result=joined`n"
$valid="  joined`nDisconnected: Server stopped.`n"+$failed+$failed+$joined
$allowed=@(Allowed $valid)
if($allowed.Count -ne 2){throw 'Recovered native failed joins must allow exactly their two timeout offsets.'}
if(@(Get-UnexpectedRuntimeMarkers $valid | Where-Object Index -notin $allowed).Count){throw 'Recovered join timeouts remain rejected.'}
foreach($bad in @($failed,($failed+$joined.Replace('  joined','connecting')),($failed+$joined.Replace('127.0.0.1:25600','other')),($failed+$joined+$failed),($failed+"Disconnected: Server stopped.`n"+$joined),($failed.Replace("Cannot join game:`nTimeout while waiting for reply","Timeout while waiting for reply`nCannot join game:`nOther failure")+$joined),($failed.Replace("Cannot join game:`nTimeout","Cannot join game:`nOther failure`nTimeout")+$joined))){
    $rejected=$false
    try{Allowed $bad|Out-Null}catch{$rejected=$true}
    if(!$rejected){throw 'Unresolved or inconsistent retry accepted.'}
}
foreach($marker in @('Timeout while waiting for reply','sync lost','wrong crc','access violation','Client: Timeout receiving UDP port')){
    foreach($text in @(($marker+"`n"+$valid),($valid+$marker),($valid.Replace('Cannot join game:',"Cannot join game:`n$marker")))){
        try{$allowed=@(Allowed $text)}catch{continue}
        if(!(Get-UnexpectedRuntimeMarkers $text | Where-Object Index -notin $allowed)){throw "Unexpected marker exempted: $marker"}
    }
}
$udp=$valid.Replace('Timeout while waiting for reply','Client: Timeout receiving UDP port')
if(@(Allowed $udp).Count -ne 2){throw 'Direct native UDP-port timeout not recognized.'}
'FLEET RECONNECT ACCEPTANCE REGRESSIONS PASS'
