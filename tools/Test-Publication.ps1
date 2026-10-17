param(
    [Parameter(Mandatory=$true)][string]$Evidence,
    [string]$Python='python',
    [switch]$IncludeLocalPackageFixtures
)
# Existing short regressions only: no SeriousSam or DedicatedServer launches.
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
if(Test-Path -LiteralPath $Evidence){throw 'Use a new verification directory.'}
$out=(New-Item -ItemType Directory -Path $Evidence).FullName
$pwsh=(Get-Process -Id $PID).Path
$isWindowsHost=[Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
$results=@()
$windowsOnly=@{
    'Test-FleetProcessControl.Tests.ps1'='Requires Windows CIM and ntdll pause/resume.'
    'Test-LocalReleasePreparation.Tests.ps1'='Requires Windows release-staging path semantics.'
    'Test-PopulationSupervisorAdapter.Tests.ps1'='Requires Windows CIM ownership/cleanup; portable CLI/UDP suite runs separately.'
    'Test-PopulationHardExitBoundary.Tests.ps1'='Requires Windows-oriented process fixture and exact cross-process start-time identity.'
    'Test-PopulationWatchdogProcess.Tests.ps1'='Requires Windows guardian/mailbox process fixture; Linux transport is not qualified.'
}
function Invoke-PublicationCheck([string]$Name,[string]$Kind,[string]$Executable,[object[]]$Arguments) {
    $log=Join-Path $out ($Name+'.log')
    $code=$null;$failure=$null;$stdoutLog=$null;$stderrLog=$null
    try{
        $command=Get-Command -Name $Executable -CommandType Application -ErrorAction Stop|Select-Object -First 1
        if($Kind -in 'Python','Provenance'){
            # Preserve PR #15's separated native streams on Windows PowerShell 5.1.
            # Do not treat non-fatal stderr (e.g. unittest) as a failed test.
            if($Arguments.Count -ne 2 -or $Arguments[0] -ne '-B'){
                throw 'Unexpected Python arguments for publication regression.'
            }
            $stdoutLog=Join-Path $out ($Name+'.stdout.log')
            $stderrLog=Join-Path $out ($Name+'.stderr.log')
            $argumentLine='-B "'+[string]$Arguments[1]+'"'
            $process=Start-Process -FilePath $command.Source -ArgumentList $argumentLine -WorkingDirectory $repo -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -ErrorAction Stop
            $code=$process.ExitCode
            # Keep the original combined log schema, used by the test counter.
            $stdout=Get-Content -LiteralPath $stdoutLog -Raw
            $stderr=Get-Content -LiteralPath $stderrLog -Raw
            ($stdout+$stderr)|Set-Content -LiteralPath $log
        }else{
            $savedPreference=$ErrorActionPreference
            try{
                $ErrorActionPreference='Continue'
                & $command.Source @Arguments > $log 2>&1
                $code=$LASTEXITCODE
            }finally{$ErrorActionPreference=$savedPreference}
        }
    }catch{
        $failure=$_.Exception.Message
        $failure|Set-Content -LiteralPath $log
    }
    $status=if($null -eq $failure -and $null -ne $code -and $code -eq 0){'PASS'}else{'FAIL'}
    Write-Host "$status $Name"
    return [pscustomobject]@{name=$Name;kind=$Kind;status=$status;exitCode=$code;error=$failure;log=$log;stdoutLog=$stdoutLog;stderrLog=$stderrLog}
}
foreach($test in Get-ChildItem -LiteralPath "$repo/poc/scripts" -Filter '*.Tests.ps1'|Sort-Object Name){
    $reason=$null
    if($test.Name -eq 'Test-RetailCleanup.Tests.ps1'){$reason='Requires a native game run.'}
    elseif($test.Name -eq 'Test-LocalReleasePackage.Tests.ps1' -and !$IncludeLocalPackageFixtures){$reason='Requires qualified private SDK artifacts.'}
    elseif(!$isWindowsHost -and $windowsOnly.ContainsKey($test.Name)){$reason=$windowsOnly[$test.Name]}
    if($reason){
        $results+=@([pscustomobject]@{name=$test.Name;kind='PowerShell';status='SKIP';reason=$reason})
        Write-Host "SKIP $($test.Name): $reason"
        continue
    }
    $arguments=@('-NoProfile','-File',$test.FullName)
    if($test.Name -in 'Test-LocalReleasePackage.Tests.ps1','Test-LocalReleasePreparation.Tests.ps1'){$arguments+=@('-Evidence',(Join-Path $out $test.BaseName))}
    $results+=@(Invoke-PublicationCheck $test.Name 'PowerShell' $pwsh $arguments)
}
$results+=@(Invoke-PublicationCheck 'Test-ShadowRuntimeLog.ps1' 'PowerShell' $pwsh @('-NoProfile','-File',"$PSScriptRoot/Test-ShadowRuntimeLog.ps1"))
foreach($test in 'test_fleet_ai_evidence.py','test_obstacle_evidence.py','test_local_release_smoke.py'){
    $results+=@(Invoke-PublicationCheck $test 'Python' $Python @('-B',"$repo/poc/scripts/$test"))
}
$results+=@(Invoke-PublicationCheck 'Verify-SourceProvenance.py' 'Provenance' $Python @('-B',"$PSScriptRoot/Verify-SourceProvenance.py"))
$hashes=0;$hashError=$null
try{
    $provenance=Get-Content -LiteralPath "$repo/docs/reports/2026-10-12-source-verification.json" -Raw|ConvertFrom-Json
    foreach($entry in $provenance.sources){
        if((Get-FileHash -LiteralPath "$repo/poc/release/gamemp/$($entry.name)").Hash -ne $entry.publishedSha256){throw "Published source hash changed: $($entry.name)"}
        $hashes++
    }
}catch{$hashError=$_.Exception.Message}
$results+=@([pscustomobject]@{name='PublishedSourceHashes';kind='Provenance';status=$(if($hashError){'FAIL'}else{'PASS'});error=$hashError})
$pythonCount=0
foreach($row in @($results|Where-Object{$_.kind -eq 'Python' -and $_.status -eq 'PASS'})){
    $count=[regex]::Match((Get-Content -LiteralPath $row.log -Raw),'Ran (\d+) tests?')
    if($count.Success){$pythonCount+=[int]$count.Groups[1].Value}
}
$failed=@($results|Where-Object status -eq 'FAIL')
$summary=[ordered]@{
    passed=($failed.Count -eq 0)
    validationScope='Selected portable publication checks; native game acceptance is excluded.'
    windowsHost=$isWindowsHost
    windowsPortableCoverageComplete=($isWindowsHost -and $failed.Count -eq 0)
    powerShellSuites=@($results|Where-Object{$_.kind -eq 'PowerShell' -and $_.status -eq 'PASS'}|ForEach-Object name)
    powerShellFailed=@($results|Where-Object{$_.kind -eq 'PowerShell' -and $_.status -eq 'FAIL'}).Count
    powerShellSkipped=@($results|Where-Object{$_.kind -eq 'PowerShell' -and $_.status -eq 'SKIP'}).Count
    pythonFixtureTests=$pythonCount
    publishedSourceHashes=$hashes
    localPackageFixtures=[bool]$IncludeLocalPackageFixtures
    nativeRuntimeStarted=$false
    results=$results
}
$summary|ConvertTo-Json -Depth 6|Set-Content -LiteralPath "$out/result.json"
$summary|ConvertTo-Json -Depth 6
if($failed.Count){throw "Publication checks failed: $($failed.Count); see result.json for all results."}
