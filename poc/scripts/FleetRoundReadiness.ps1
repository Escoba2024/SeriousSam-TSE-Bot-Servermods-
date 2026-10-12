function Test-FleetRoundStarting([string]$Text) {
    $begins=[regex]::Matches($Text,"(?m)^Executing: 'Scripts\\Dedicated\\BotTest\\[123]_begin\.ini'\r?$")
    if(!$begins.Count){return $false}
    return $Text.Substring($begins[$begins.Count-1].Index) -notmatch '(?m)^ALL OK: Dedicated server is now running!\r?$'
}
