# Return only offsets belonging to failed native joins followed by a proven
# successful retry to the same target. All other runtime markers remain errors.
function Get-RecoveredJoinTimeouts([string]$Text) {
    $attempts=[regex]::Matches($Text,'(?m)^\[BotReconnect\] attempt address=([^\r\n]+)\r?$')
    $pending=@();$allowed=@();$target=$null
    for($i=0;$i -lt $attempts.Count;$i++) {
        $attempt=$attempts[$i]
        $end=if($i+1 -lt $attempts.Count){$attempts[$i+1].Index}else{$Text.Length}
        $block=$Text.Substring($attempt.Index,$end-$attempt.Index)
        $results=[regex]::Matches($block,'(?m)^\[BotReconnect\] result=(failed|joined)\r?$')
        if($results.Count -ne 1){throw 'Reconnect attempt has no unique result.'}
        if($pending.Count -and $target -ne $attempt.Groups[1].Value){throw 'Reconnect target changed before recovery.'}
        $result=$results[0]
        $native=$block.Substring(0,$result.Index)
        if($result.Groups[1].Value -eq 'failed') {
            if($block.Substring($result.Index+$result.Length) -match '(?m)^\s*joined\s*$|^Disconnected:'){throw 'Failed retry episode ended before recovery.'}
            if($native -notmatch '(?m)^Cannot join game:' -or $native -match '(?m)^\s*joined\s*$') {throw 'Failed retry lacks native failure evidence.'}
            $catch=[regex]::Matches($native,'(?m)^Cannot join game:\r?\n(?<error>Timeout while waiting for reply|Client: Timeout receiving UDP port)\r?$')
            if($catch.Count -ne 1){throw 'Failed retry lacks one direct native join timeout.'}
            $pending+=@($attempt.Index+$catch[0].Groups['error'].Index)
            $target=$attempt.Groups[1].Value
        } else {
            if($native -notmatch '(?m)^\s*joined\s*$' -or $native -match '(?m)^Disconnected:|^Cannot join game:') {throw 'Retry success lacks an uninterrupted native joined marker.'}
            $allowed+=@($pending);$pending=@();$target=$null
        }
    }
    if($pending.Count){throw 'Native failed join was never recovered.'}
    return $allowed
}
