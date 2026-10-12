function Get-UnexpectedRuntimeMarkers([string]$Text,[bool]$ExpectedShutdown=$false) {
    $states=[regex]::Matches($Text,'(?im)^[ \t]*(joined|Disconnected: Server stopped\.)[ \t]*\r?$')
    foreach($marker in [regex]::Matches($Text,'(?im)sync lost|out of sync|bad sync|wrong crc|access.violation|Timeout while waiting|Client: Timeout receiving UDP port')){
        $previous=$states | Where-Object Index -lt $marker.Index | Select-Object -Last 1
        if($ExpectedShutdown -and $marker.Value -match 'Timeout' -and $previous -and
            $previous.Groups[1].Value -eq 'Disconnected: Server stopped.'){continue}
        $marker
    }
}
