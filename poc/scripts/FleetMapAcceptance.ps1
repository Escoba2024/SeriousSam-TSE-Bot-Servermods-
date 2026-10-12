function Assert-FleetMapQueries($Queries, $Identities) {
    $accepted = @()
    foreach($map in @('Fortress', 'Little Trouble', "We Got Skulls'n'Bones Too")) {
        $full = @($Queries | Where-Object {
            $status = $_.status
            $names = @([regex]::Matches($_.players, '\\player_\d+\\([^\\]+)\\') | ForEach-Object { $_.Groups[1].Value })
            $valid = $status -match ('\\mapname\\'+[regex]::Escape($map)+'\\') -and
                $status -match '\\numplayers\\8\\' -and
                $status -match '\\gamever\\1\.07\\' -and $status -match '\\activemod\\\\' -and
                $names.Count -eq 8 -and @($names | Sort-Object -Unique).Count -eq 8
            foreach($identity in $Identities) { if($identity.name -notin $names) { $valid=$false } }
            $valid
        })
        if($full.Count -lt 3) { throw "Map lacks three complete eight-bot samples: $map" }
        $span=([datetimeoffset]$full[-1].utc-[datetimeoffset]$full[0].utc).TotalSeconds
        if($span -lt 10) { throw "Map eight-bot sample span below ten seconds: $map" }
        $accepted+=@([pscustomobject]@{map=$map;completeSamples=$full.Count;sampleSpanSeconds=$span})
    }
    $accepted
}

function Assert-FleetMapServer([string]$Text, $Identities) {
    $maps=@('Fortress','DM_LittleTrouble','WeGotSkullsNBonesToo')
    $levels=[regex]::Matches($Text, "(?m)^\s*level: '([^']+)'")
    if($levels.Count -ne 3) { throw 'Expected exactly three native server levels.' }
    $accepted=@()
    foreach($i in 0..2) {
        if($levels[$i].Groups[1].Value -notlike "*\$($maps[$i]).wld") { throw 'Native map order mismatch.' }
        $end=if($i -lt 2){$levels[$i+1].Index}else{$Text.Length}
        $part=$Text.Substring($levels[$i].Index,$end-$levels[$i].Index)
        $crc=[regex]::Matches($part,'CRC check OK').Count
        if($crc -lt 3) { throw "Missing three CRC accepts on $($maps[$i])." }
        foreach($identity in $Identities) {
            if($part -notmatch ([regex]::Escape($identity.name)+'\^r joined')) { throw "Missing native player join on $($maps[$i]): $($identity.name)" }
        }
        $accepted+=@([pscustomobject]@{level=$maps[$i];crcAccepted=$crc})
    }
    $accepted
}

function Assert-FleetMapActions([string]$Text) {
    $joins=[regex]::Matches($Text,'(?m)^[ \t]*joined[ \t]*\r?$')
    if($joins.Count -ne 3){throw 'Expected exactly three successful client sessions.'}
    $accepted=@()
    foreach($i in 0..2){
        $end=if($i -lt 2){$joins[$i+1].Index}else{$Text.Length}
        $part=$Text.Substring($joins[$i].Index,$end-$joins[$i].Index)
        $disconnect=[regex]::Match($part,'(?m)^Disconnected:')
        if($disconnect.Success){$part=$part.Substring(0,$disconnect.Index)}
        foreach($slot in 0..3){
            $records=[regex]::Matches($part,('\[BotDriver\] bot'+$slot+' tick=(\d+) pos=\(([^)]+)\) heading=([-\d.]+) fire=([01])'))
            $ticks=@($records|ForEach-Object{[int]$_.Groups[1].Value})
            $positions=@($records|ForEach-Object{$_.Groups[2].Value}|Sort-Object -Unique)
            $headings=@($records|ForEach-Object{$_.Groups[3].Value}|Sort-Object -Unique)
            $fire=@($records|ForEach-Object{$_.Groups[4].Value}|Sort-Object -Unique)
            if($records.Count -lt 10 -or $ticks[-1] -le $ticks[0] -or $positions.Count -lt 2 -or $headings.Count -lt 2 -or $fire.Count -ne 2){
                throw "Inactive local bot on native map session $($i+1), slot $slot"
            }
            for($j=1;$j -lt $ticks.Count;$j++){if($ticks[$j] -le $ticks[$j-1]){throw 'Non-increasing action ticks within map session.'}}
            $accepted+=@([pscustomobject]@{session=$i+1;localSlot=$slot;samples=$records.Count;firstTick=$ticks[0];lastTick=$ticks[-1];positions=$positions.Count;headings=$headings.Count;fireStates=$fire.Count})
        }
    }
    $accepted
}
