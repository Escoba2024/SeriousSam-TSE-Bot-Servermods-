# Native profile preparation. No engine/entity binaries, server files or processes.
$ErrorActionPreference='Stop'
. "$PSScriptRoot\PopulationCore.ps1"

function New-LocalBotReleasePlan($Fleet,[string]$Dll,[string]$Startup) {
    $plan=@()
    foreach($entry in $Fleet.processes){
        $dir=$entry.clientDir
        if((Split-Path $dir -Leaf) -notmatch '^TSE-BotClient[\w-]*$'){throw 'Use an isolated TSE-BotClient directory.'}
        $startupPath=[IO.Path]::GetFullPath((Join-Path $dir $entry.startupScript))
        if(!$startupPath.StartsWith(($dir+'\'),[StringComparison]::OrdinalIgnoreCase)){throw 'Startup path escapes its isolated bot client.'}
        if(!(Test-Path -LiteralPath (Split-Path $startupPath -Parent) -PathType Container)){throw 'Startup parent directory must exist.'}
        if((Get-Content -LiteralPath "$dir\Data\Var\Sam_Version.var" -Raw).Trim() -ne 'v1.07'){throw 'Expected a native TSE 1.07 client.'}
        foreach($name in 'SeriousSam.exe','Engine.dll','EntitiesMP.dll','GameMP.dll'){
            if(!(Test-Path -LiteralPath "$dir\Bin\$name" -PathType Leaf)){throw "Missing native client file $name"}
        }
        $gmsPath="$dir\Data\SeriousSam.gms"
        $gms=[IO.File]::ReadAllBytes($gmsPath)
        if($gms.Length -lt 12 -or [Text.Encoding]::ASCII.GetString($gms,0,8) -ne 'GAMEV012'){throw 'Unsupported native settings.'}
        $offset=12+[BitConverter]::ToInt32($gms,8)
        if($offset -lt 12 -or $offset+28 -gt $gms.Length){throw 'Invalid native settings length.'}
        foreach($slot in 0..3){[Array]::Copy([BitConverter]::GetBytes([int]$slot),0,$gms,$offset+8+4*$slot,4)}
        [Array]::Copy([BitConverter]::GetBytes([int]($entry.localPlayers-1)),0,$gms,$offset+24,4)
        $plan+=@([pscustomobject]@{path=$gmsPath;bytes=$gms})
        $symbolsPath=Join-Path $dir 'Scripts\PersistentSymbols.ini'
        # Latin-1 gives a reversible byte mapping; unrelated strings retain
        # their exact bytes while these ASCII window/FPS settings are replaced.
        $encoding=[Text.Encoding]::GetEncoding(28591)
        $symbols=$encoding.GetString([IO.File]::ReadAllBytes($symbolsPath))
        foreach($setting in @{sam_bFullScreen=0;sam_bPauseOnMinimize=0;sam_iMaxFPSActive=60;sam_iMaxFPSInactive=30;sam_iScreenSizeI=960;sam_iScreenSizeJ=540}.GetEnumerator()){
            $pattern='\b'+$setting.Key+'\s*=\s*[^;]*;'
            if([regex]::Matches($symbols,$pattern).Count -ne 1){throw "Missing/duplicate native window setting $($setting.Key)"}
            $symbols=[regex]::Replace($symbols,$pattern,($setting.Key+'=(INDEX)'+$setting.Value+';'))
        }
        $plan+=@([pscustomobject]@{path=$symbolsPath;bytes=$encoding.GetBytes($symbols)})
        foreach($slot in 0..($entry.localPlayers-1)){
            $path="$dir\Players\Player$slot.plr"
            $bytes=[IO.File]::ReadAllBytes($path)
            if($bytes.Length -lt 8 -or [Text.Encoding]::ASCII.GetString($bytes,0,4) -ne 'PLC4'){throw 'Unsupported native player profile.'}
            $offset=8+[BitConverter]::ToInt32($bytes,4)
            if($offset -lt 8 -or $offset+4 -gt $bytes.Length){throw 'Invalid player name length.'}
            $guidOffset=$offset+4+[BitConverter]::ToInt32($bytes,$offset)
            if($guidOffset -lt $offset+4 -or $guidOffset+48 -ne $bytes.Length){throw 'Invalid native profile length.'}
            $name=[Text.Encoding]::ASCII.GetBytes("$($Fleet.botNamePrefix)_$((Split-Path $dir -Leaf).Replace('TSE-BotClient','Client'))_$($slot+1)")
            $tail=$bytes[$offset..($bytes.Length-1)]
            $guid=[guid]::NewGuid().ToByteArray()
            [Array]::Copy($guid,0,$tail,$guidOffset-$offset,16)
            $new=[byte[]]($bytes[0..3]+[BitConverter]::GetBytes([int]$name.Length)+$name+$tail)
            $plan+=@([pscustomobject]@{path=$path;bytes=$new},[pscustomobject]@{path=$path+'.guid';bytes=$guid})
        }
        $plan+=@([pscustomobject]@{path="$dir\Bin\GameMP.dll";bytes=[IO.File]::ReadAllBytes($Dll)},
            [pscustomobject]@{path=$startupPath;bytes=[IO.File]::ReadAllBytes($Startup)})
    }
    return ,$plan
}

function Assert-LocalBotClientsStopped($Fleet) {
    foreach($entry in $Fleet.processes){
        $exe=Join-Path $entry.clientDir 'Bin\SeriousSam.exe'
        if(Get-Process SeriousSam -ErrorAction SilentlyContinue | Where-Object Path -eq $exe){throw "Stop the bot client before preparing/restoring: $exe"}
    }
}
