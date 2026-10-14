# Whole-process-group planning. No Human/Bot name classification.
$ErrorActionPreference='Stop'
function Get-PopulationFields([string]$Text) {
    $fields=@{}
    foreach($m in [regex]::Matches($Text,'\\([^\\]+)\\([^\\]*)')){
        $key=$m.Groups[1].Value
        if($fields.ContainsKey($key)){throw 'Duplicate query field.'}
        $fields[$key]=$m.Groups[2].Value
    }
    if(!$fields.ContainsKey('final') -or $fields['final'] -cne ''){throw 'Incomplete UDP response.'}
    return $fields
}
function ConvertTo-PopulationSample([string]$StatusBefore,[string]$Players,[string]$StatusAfter) {
    $before=Get-PopulationFields $StatusBefore
    $after=Get-PopulationFields $StatusAfter
    foreach($key in 'gamename','gamever','activemod','numplayers','maxplayers','mapname'){
        if(!$before.ContainsKey($key) -or !$after.ContainsKey($key) -or $before[$key] -cne $after[$key]){throw 'Status changed during player query.'}
    }
    if($after.gamename -cne 'serioussamse' -or $after.gamever -cne '1.07' -or $after.activemod -cne ''){throw 'Wrong game/version/mod.'}
    if($after.numplayers -notmatch '^\d+$' -or $after.maxplayers -notmatch '^\d+$'){throw 'Invalid player limits.'}
    $count=[int]$after.numplayers; $max=[int]$after.maxplayers
    if($max -lt 1 -or $max -gt 16 -or $count -lt 0 -or $count -gt $max){throw 'Invalid player limits.'}
    $pf=Get-PopulationFields $Players
    $entries=@()
    foreach($key in $pf.Keys){
        if($key -match '^player_(\d+)$'){
            $index=[int]$Matches[1]
            if($index -lt 0 -or $index -ge 16 -or !$pf[$key]){throw 'Invalid player row.'}
            $entries+=@([pscustomobject]@{Index=$index;Name=$pf[$key]})
        }
    }
    if($entries.Count -ne $count -or @($entries.Index|Sort-Object -Unique).Count -ne $count){throw 'Incomplete player list.'}
    [pscustomobject]@{Valid=$true;Total=$count;MaxPlayers=$max;Map=$after.mapname;Names=@($entries.Name)}
}
function Get-PopulationGroupDecision {
    param($Sample,[object[]]$Groups,[ValidateRange(0,16)][int]$TargetPopulation,
          [ValidateRange(0,15)][int]$ReservedHumanSlots,[double]$Now)
    if(!$Sample.Valid){return [pscustomobject]@{Action='Hold';GroupId=$null;Reason='QueryUncertain';Cap=$null}}
    $ids=@()
    foreach($g in $Groups){
        if(!$g.Id -or $g.Size -notin 1,2,3,4 -or $ids -contains $g.Id){throw 'Invalid process group.'}
        $ids+=@($g.Id)
    }
    $cap=[math]::Min($TargetPopulation,[math]::Max(0,$Sample.MaxPlayers-$ReservedHumanSlots))
    $reason='AtTargetOrGroupDoesNotFit';$action='Hold';$id=$null
    if($Sample.Total -gt $cap){
        $pick=@($Groups|Where-Object Active|Sort-Object Size,@{Expression='Id';Descending=$true}|Select-Object -First 1)
        if($pick.Count){$action='Stop';$id=$pick[0].Id;$reason='FreeCapacity'}
        else{$reason='OverCapacityWithoutOwnedGroup'}
    }elseif($Sample.Total -lt $cap){
        $room=$cap-$Sample.Total
        $pick=@($Groups|Where-Object{!$_.Active -and $_.EligibleAt -le $Now -and $_.Size -le $room}|Sort-Object @{Expression='Size';Descending=$true},Id|Select-Object -First 1)
        if($pick.Count){$action='Start';$id=$pick[0].Id;$reason='FillAvailableCapacity'}
    }
    [pscustomobject]@{Action=$action;GroupId=$id;Reason=$reason;Cap=$cap;Total=$Sample.Total}
}
