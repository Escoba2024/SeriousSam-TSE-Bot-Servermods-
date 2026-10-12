function Test-FleetQueryCountReady([string]$Status,[string]$Players,[int]$ExpectedCount) {
    $count=[regex]::Match($Status,'\\numplayers\\(\d+)(?:\\|$)')
    $entries=@([regex]::Matches($Players,'\\player_(\d+)\\([^\\]+)'))
    $names=@($entries|ForEach-Object {$_.Groups[2].Value})
    $indices=@($entries|ForEach-Object {$_.Groups[1].Value})
    return $count.Success -and [int]$count.Groups[1].Value -eq $ExpectedCount -and $entries.Count -eq $ExpectedCount -and @($names|Sort-Object -Unique).Count -eq $ExpectedCount -and @($indices|Sort-Object -Unique).Count -eq $ExpectedCount
}

function Assert-FleetSteadySample($Sample,$Identities) {
    $count=[regex]::Match($Sample.status,'\\numplayers\\(\d+)(?:\\|$)')
    $names=@([regex]::Matches($Sample.players,'\\player_\d+\\([^\\]+)')|ForEach-Object{$_.Groups[1].Value})
    if(!$count.Success -or [int]$count.Groups[1].Value -ne @($Identities).Count -or $names.Count -ne @($Identities).Count -or @($names|Sort-Object -Unique).Count -ne $names.Count){throw 'Steady fleet lost players or has an incomplete/duplicate player list.'}
    foreach($identity in $Identities){if($names -notcontains $identity.name){throw 'Steady fleet native identity changed.'}}
}

function Invoke-FleetQuery {
    param(
        [Parameter(Mandatory)][string]$Request,
        [string]$Server='127.0.0.1',
        [ValidateRange(1,65535)][int]$Port=25601,
        [ValidateRange(1,3)][int]$Attempts=1,
        [ValidateRange(50,2000)][int]$ReceiveTimeoutMs=2000,
        [ValidateRange(1,500)][int]$RetryDelayMs=250,
        [string]$AttemptLog
    )
    for($attempt=1;$attempt -le $Attempts;$attempt++){
        $udp=[Net.Sockets.UdpClient]::new()
        try{
            $udp.Client.ReceiveTimeout=$ReceiveTimeoutMs
            $udp.Connect($Server,$Port)
            $bytes=[Text.Encoding]::ASCII.GetBytes($Request)
            [void]$udp.Send($bytes,$bytes.Length)
            $peer=[Net.IPEndPoint]::new([Net.IPAddress]::Any,0)
            return [Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
        }catch{
            $errorObject=$_.Exception
            if($errorObject.InnerException){$errorObject=$errorObject.InnerException}
            if($errorObject -isnot [Net.Sockets.SocketException]){throw}
            $canRetry=$attempt -lt $Attempts -and $errorObject.SocketErrorCode -in @('ConnectionReset','ConnectionRefused','TimedOut')
            if($AttemptLog){
                [ordered]@{utc=[datetime]::UtcNow.ToString('o');request=$Request;attempt=$attempt;socketError=$errorObject.SocketErrorCode.ToString();retry=$canRetry}|
                    ConvertTo-Json -Compress|Add-Content -LiteralPath $AttemptLog
            }
            if(!$canRetry){throw}
        }finally{$udp.Dispose()}
        Start-Sleep -Milliseconds $RetryDelayMs
    }
}
