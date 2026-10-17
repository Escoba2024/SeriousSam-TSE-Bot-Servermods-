param(
    [Parameter(Mandatory)][string]$Evidence
)
# PowerShell-only companion to Test-Publication.ps1. No native game fixtures.
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
$full=[IO.Path]::GetFullPath($Evidence)
$root=[IO.Path]::GetFullPath($repo).TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
if(!$full.StartsWith($root,[StringComparison]::OrdinalIgnoreCase)){throw 'Evidence must be inside this worktree.'}
if(Test-Path -LiteralPath $full){throw 'Use a new verification directory.'}
$out=(New-Item -ItemType Directory -Path $full).FullName
$temp=(New-Item -ItemType Directory -Path (Join-Path $out 'temp')).FullName
$exe=(Get-Process -Id $PID).Path
$oldTemp=$env:TEMP;$oldTmp=$env:TMP
$results=@()
try {
    $env:TEMP=$temp;$env:TMP=$temp
    $tests=@(Get-ChildItem -LiteralPath "$repo/poc/scripts" -Filter '*.Tests.ps1'|Sort-Object Name)
    $tests+=Get-Item -LiteralPath "$PSScriptRoot/Test-ShadowRuntimeLog.ps1"
    foreach($test in $tests){
        $reason=switch($test.Name){
            'Test-RetailCleanup.Tests.ps1' {'Requires native retail run'}
            'Test-LocalReleasePackage.Tests.ps1' {'Requires qualified private SDK artifacts'}
        }
        if($reason){$results+=@([ordered]@{suite=$test.Name;status='SKIP';reason=$reason});Write-Output "SKIP $($test.Name): $reason";continue}
        $args=@('-NoProfile','-NonInteractive','-File',('"'+$test.FullName+'"'))
        if($test.Name -eq 'Test-LocalReleasePreparation.Tests.ps1'){$args+=@('-Evidence',('"'+(Join-Path $out $test.BaseName)+'"'))}
        $log=Join-Path $out ($test.Name+'.log');$err=Join-Path $out ($test.Name+'.stderr.log')
        $watch=[Diagnostics.Stopwatch]::StartNew();$p=$null
        try {
            $p=Start-Process -FilePath $exe -ArgumentList $args -WorkingDirectory $repo -WindowStyle Hidden -PassThru -RedirectStandardOutput $log -RedirectStandardError $err
            # Let each suite finish its own finally/retained-handle cleanup.
            # Killing a timed-out suite could strand its nested helper processes.
            [void]$p.Handle
            $p.WaitForExit();$status=if($p.ExitCode -eq 0){'PASS'}else{'FAIL'}
            $results+=@([ordered]@{suite=$test.Name;status=$status;exitCode=$p.ExitCode;seconds=[math]::Round($watch.Elapsed.TotalSeconds,3);stdout=$log;stderr=$err})
            Write-Output "$status $($test.Name)"
        } catch {
            $results+=@([ordered]@{suite=$test.Name;status='FAIL';error=$_.Exception.Message;stdout=$log;stderr=$err})
            Write-Output "FAIL $($test.Name): $($_.Exception.Message)"
        } finally {if($p){$p.Dispose()};$watch.Stop()}
    }
} finally {
    $env:TEMP=$oldTemp;$env:TMP=$oldTmp
    $summary=[ordered]@{
        branch=(& git -C $repo branch --show-current);commit=(& git -C $repo rev-parse HEAD)
        utc=[datetime]::UtcNow.ToString('o');powerShell=$PSVersionTable.PSVersion.ToString();executable=$exe
        passed=@($results|Where-Object status -eq 'PASS').Count
        failed=@($results|Where-Object status -eq 'FAIL').Count
        skipped=@($results|Where-Object status -eq 'SKIP').Count
        suites=$results;nativeRuntimeStarted=$false;pythonAndProvenanceRun=$false
    }
    $summary|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $out 'result.json')
}
if($summary.failed){throw "$($summary.failed) portable suites failed; see $out/result.json"}
"PORTABLE PASS: $($summary.passed); SKIP: $($summary.skipped)"
