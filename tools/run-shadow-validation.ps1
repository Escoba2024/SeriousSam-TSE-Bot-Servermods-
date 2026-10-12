param(
    [ValidateSet('Smoke','Cleanup','Soak','Combat','Shutdown')][string]$Mode='Smoke',
    [int[]]$Counts=@(1,2,4),
    [int]$Seconds=90,
    [int]$SyncMinutes=0,
    [switch]$VisibleClients,
    [string]$Dll,
    [string]$StartupSource,
    [Parameter(Mandatory=$true)][string]$Evidence
)
# Local evidence harness. Reuses the existing retail runners and native settings writer.
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
Set-Location $repo
$retail=Join-Path $repo '.codex\retail'
$dll=if($Dll){(Resolve-Path -LiteralPath $Dll).Path}else{Join-Path $repo '.codex\shadow-20261008-bot-build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll'}
$startupPath=if($StartupSource){(Resolve-Path -LiteralPath $StartupSource).Path}else{$null}
if($startupPath -and $Mode -ne 'Combat'){throw 'StartupSource is only supported for Combat.'}
if(Test-Path -LiteralPath $Evidence){throw 'Use new evidence directory.'}
if(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object Path -like "$retail\*"){throw 'Isolated runtime already active.'}
$out=(New-Item -ItemType Directory -Path $Evidence).FullName
$backups=@{}
$started=[DateTime]::UtcNow
function Save-File([string]$Path){
    if($backups.ContainsKey($Path)){return}
    $backup=Join-Path $out ("before-$($backups.Count)-"+(Split-Path $Path -Leaf))
    if(Test-Path -LiteralPath $Path){Copy-Item -LiteralPath $Path -Destination $backup; $backups[$Path]=$backup}
    else{$backups[$Path]=$null}
}
$errors=$null
. "$PSScriptRoot\ShadowRuntimeLog.ps1"
$ast=[Management.Automation.Language.Parser]::ParseFile("$repo\poc\scripts\Test-RetailFleet.ps1",[ref]$null,[ref]$errors)
if($errors){throw $errors}
$writer=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Set-NativePlayers'},$true)
if(!$writer){throw 'Existing native settings writer missing.'}
Invoke-Expression $writer.Extent.Text
. "$repo\poc\scripts\PopulationCore.ps1"
$job=$null; $passed=$false
try{
    foreach($dir in 'TSE-Server','TSE-BotClient','TSE-Observer'){
        $root="$retail\$dir"
        foreach($sub in 'Players','Controls','Scripts','Data'){
            Get-ChildItem "$root\$sub" -Recurse -File | ForEach-Object {Save-File $_.FullName}
        }
        foreach($file in 'Bin\GameMP.dll','SeriousSam.log','Dedicated_BotTest.log','Bin\SeriousSam.RPT'){Save-File "$root\$file"}
    }
    if($startupPath){Save-File "$retail\TSE-BotClient\Scripts\Phase1AutoCombat.ini"}
    $backups.GetEnumerator() | ForEach-Object {[pscustomobject]@{path=$_.Key;backup=$_.Value;hash=if($_.Value){(Get-FileHash $_.Value).Hash}else{$null}}} |
        ConvertTo-Json | Set-Content "$out\backup-manifest.json"
    if($startupPath){Copy-Item -LiteralPath $startupPath -Destination "$retail\TSE-BotClient\Scripts\Phase1AutoCombat.ini"}
    foreach($dir in 'TSE-BotClient','TSE-Observer'){
        $path="$retail\$dir\Scripts\PersistentSymbols.ini"
        $settings=Get-Content -LiteralPath $path -Raw
        foreach($s in @{sam_bFullScreen=0;sam_bPauseOnMinimize=0;sam_iMaxFPSActive=60;sam_iMaxFPSInactive=30;sam_iScreenSizeI=960;sam_iScreenSizeJ=540}.GetEnumerator()){
            $settings=$settings -replace ($s.Key+'\s*=\s*[^;]*;'),($s.Key+'=(INDEX)'+$s.Value+';')
        }
        Set-Content -LiteralPath $path -Value $settings
    }
    $round="$retail\TSE-Server\Scripts\Dedicated\BotTest"
    if($Mode -in 'Smoke','Soak'){
        Set-Content "$round\1_begin.ini" (((Get-Content "$round\1_begin.ini" -Raw).Replace('DM_LittleTrouble.wld','Fortress.wld'))+"`ngam_iFragLimit=0;gam_iTimeLimit=0;")
    }
    if($Mode -eq 'Shutdown'){
        Set-Content "$round\init.ini" ((Get-Content "$round\init.ini" -Raw).Replace('ded_tmTimeout = -1;','ded_tmTimeout = 1;'))
        Add-Content "$round\1_begin.ini" 'gam_iTimeLimit=1;'
        Set-Content "$round\1_end.ini" 'Quit();'
    }
    Set-NativePlayers "$retail\TSE-Observer" $(if($Mode -in 'Combat','Cleanup','Shutdown'){1}else{0}) 'Vanilla_Observer'
    $job=Start-Job -ArgumentList $retail,$out -ScriptBlock {
        param($retail,$out)
        while($true){
            $utc=[DateTime]::UtcNow.ToString('o')
            foreach($p in @(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object Path -like "$retail\*")){
                [ordered]@{utc=$utc;pid=$p.Id;exe=$p.Path;cpuSeconds=$p.CPU;privateBytes=$p.PrivateMemorySize64;workingSet=$p.WorkingSet64;handles=$p.HandleCount;threads=$p.Threads.Count} |
                    ConvertTo-Json -Compress | Add-Content "$out\resources.jsonl"
            }
            if(Get-NetUDPEndpoint -LocalPort 25601 -ErrorAction SilentlyContinue){
                $udp=[Net.Sockets.UdpClient]::new()
                try{
                    $udp.Client.ReceiveTimeout=2000; $udp.Connect('127.0.0.1',25601)
                    $replies=@{utc=$utc}
                    foreach($request in '\status\','\players\'){
                        $b=[Text.Encoding]::ASCII.GetBytes($request); [void]$udp.Send($b,$b.Length)
                        $peer=[Net.IPEndPoint]::new([Net.IPAddress]::Any,0)
                        $replies[$request]=[Text.Encoding]::ASCII.GetString($udp.Receive([ref]$peer))
                    }
                    $replies | ConvertTo-Json -Compress | Add-Content "$out\queries.jsonl"
                }catch{[ordered]@{utc=$utc;error=$_.Exception.Message} | ConvertTo-Json -Compress | Add-Content "$out\query-errors.jsonl"}
                finally{$udp.Dispose()}
            }
            Start-Sleep -Seconds 10
        }
    }
    foreach($count in $Counts){
        Set-NativePlayers "$retail\TSE-BotClient" $count 'TSE_Bot_PoC'
        Get-FleetIdentities @{processes=@(@{clientDir="$retail\TSE-BotClient";localPlayers=$count})} |
            ConvertTo-Json | Set-Content "$out\identities-$count.json"
        $run="$out\native-$count-$Mode"
        "RUN mode=$Mode players=$count seconds=$Seconds utc=$([DateTime]::UtcNow.ToString('o'))"
        if($Mode -eq 'Cleanup'){
            & "$repo\poc\scripts\Test-RetailCleanup.Tests.ps1" -Dll $dll -Evidence $run
        }else{
            $args=@{Dll=$dll;Evidence=$run;Seconds=$Seconds;Observer=$true;Startup='Scripts\Phase1Respawn.ini'}
            if($VisibleClients){$args.VisibleClients=$true}
            if($Mode -in 'Combat','Shutdown'){$args.Startup='Scripts\Phase1Combat.ini'}
            if($startupPath){$args.Startup='Scripts\Phase1AutoCombat.ini'}
            if($Mode -eq 'Shutdown'){$args.ExpectedShutdown=$true}
            & "$repo\poc\scripts\Test-RetailJoin.ps1" @args | Tee-Object "$out\join-$count.json"
            & "$repo\poc\scripts\Test-Phase1Telemetry.ps1" -BotLog "$run\SeriousSam.log" -Output "$run\telemetry.json" -ExpectedPlayers $count -LocalOnly -SyncMinutes $SyncMinutes | Out-Null
            $telemetry=Get-Content "$run\telemetry.json" -Raw | ConvertFrom-Json
            if($telemetry.rejectedSnapshotLines -or $telemetry.players.Count -ne $count){throw 'Missing/corrupt local snapshots.'}
            foreach($p in $telemetry.players){
                if($p.samples -lt 600 -or $p.distinctPositions -lt 10 -or $p.distinctYaw -lt 10 -or !$p.fireOffSamples -or (!$startupPath -and !$p.fireOnSamples)){throw "Inactive bot $($p.player)"}
            }
            foreach($log in "$run\SeriousSam.log","$run\observer-SeriousSam.log","$run\Dedicated_BotTest.log"){
                if(@(Get-UnexpectedRuntimeMarkers (Get-Content $log -Raw) ($Mode -eq 'Shutdown')).Count){throw "Runtime error/sync marker: $log"}
            }
        }
        "PASS mode=$Mode players=$count utc=$([DateTime]::UtcNow.ToString('o'))"
    }
    $passed=$true
}finally{
    if($job){Stop-Job $job; Receive-Job $job -ErrorAction Continue | Out-File "$out\monitor-output.txt"; Remove-Job $job}
    $restore=@(); $cleanupErrors=@()
    foreach($path in $backups.Keys){
        try{
            if($backups[$path]){Copy-Item -LiteralPath $backups[$path] -Destination $path -Force; $ok=(Get-FileHash $path).Hash -eq (Get-FileHash $backups[$path]).Hash}
            else{if(Test-Path -LiteralPath $path){Remove-Item -LiteralPath $path}; $ok=!(Test-Path -LiteralPath $path)}
            $restore+=@(@{path=$path;restored=$ok}); if(!$ok){throw "Restore mismatch $path"}
        }catch{$cleanupErrors+=@($_.Exception.Message)}
    }
    $owned=@(Get-Process SeriousSam,DedicatedServer -ErrorAction SilentlyContinue | Where-Object Path -like "$retail\*")
    $ports=@(Get-NetUDPEndpoint -LocalPort 25600,25601 -ErrorAction SilentlyContinue)
    $events=@(); $eventsRead=$true
    try{$events=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001;StartTime=$started.ToLocalTime()} -ErrorAction Stop | Where-Object Message -match 'SeriousSam|DedicatedServer')}
    catch{if($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*'){$eventsRead=$false}}
    $rpts=@(Get-ChildItem $out -Filter '*.RPT' -Recurse)
    @{passed=$passed;mode=$Mode;counts=$Counts;seconds=$Seconds;syncMinutes=$SyncMinutes;startedUtc=$started.ToString('o');elapsedSeconds=([DateTime]::UtcNow-$started).TotalSeconds;restored=$restore;ownedProcesses=$owned.Count;udpPorts=$ports.Count;matchingCrashEvents=$events.Count;applicationEventsRead=$eventsRead;crashReports=$rpts.Count;cleanupErrors=$cleanupErrors} |
        ConvertTo-Json -Depth 5 | Set-Content "$out\diagnostics.json"
    if($cleanupErrors.Count -or $owned.Count -or $ports.Count -or $events.Count -or !$eventsRead -or $rpts.Count){throw "Cleanup/crash diagnostics failed: $out"}
}
"SHADOW VALIDATION PASS: $out"
