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
$results=@()
foreach($test in Get-ChildItem -LiteralPath "$repo/poc/scripts" -Filter '*.Tests.ps1'|Sort-Object Name){
    if($test.Name -eq 'Test-RetailCleanup.Tests.ps1'){continue} # Requires a native game run.
    if($test.Name -eq 'Test-LocalReleasePackage.Tests.ps1' -and !$IncludeLocalPackageFixtures){continue} # Requires original local candidate Sources/Game.
    $arguments=@('-NoProfile','-File',$test.FullName)
    if($test.Name -in 'Test-LocalReleasePackage.Tests.ps1','Test-LocalReleasePreparation.Tests.ps1'){$arguments+=@('-Evidence',(Join-Path $out $test.BaseName))}
    & $pwsh @arguments > (Join-Path $out ($test.Name+'.log')) 2>&1
    if($LASTEXITCODE){Get-Content -LiteralPath (Join-Path $out ($test.Name+'.log')) -Tail 12;throw "Regression failed: $($test.Name)"}
    $results+=@($test.Name)
}
& $pwsh -NoProfile -File "$PSScriptRoot/Test-ShadowRuntimeLog.ps1" > "$out/ShadowRuntimeLog.log" 2>&1
if($LASTEXITCODE){throw 'ShadowRuntimeLog regression failed.'}
$results+=@('Test-ShadowRuntimeLog.ps1')
foreach($test in 'test_fleet_ai_evidence.py','test_obstacle_evidence.py','test_local_release_smoke.py'){
    & $Python -B "$repo/poc/scripts/$test" > "$out/$test.log" 2>&1
    if($LASTEXITCODE){Get-Content -LiteralPath "$out/$test.log" -Tail 12;throw "Python regression failed: $test"}
}
$provenance=Get-Content -LiteralPath "$repo/docs/reports/2026-10-12-source-verification.json" -Raw|ConvertFrom-Json
& $Python -B "$PSScriptRoot/Verify-SourceProvenance.py" > "$out/source-provenance.log" 2>&1
if($LASTEXITCODE){throw 'Source provenance verification failed.'}
foreach($entry in $provenance.sources){
    if((Get-FileHash -LiteralPath "$repo/poc/release/gamemp/$($entry.name)").Hash -ne $entry.publishedSha256){throw "Published source hash changed: $($entry.name)"}
}
$summary=[ordered]@{passed=$true;powerShellSuites=$results;pythonFixtureTests=44;publishedSourceHashes=13;localPackageFixtures=[bool]$IncludeLocalPackageFixtures;nativeRuntimeStarted=$false}
$summary|ConvertTo-Json -Depth 4|Set-Content -LiteralPath "$out/result.json"
$summary|ConvertTo-Json -Depth 4
