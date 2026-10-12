param([Parameter(Mandatory=$true)][string]$Evidence)
$ErrorActionPreference='Stop'
$root=(New-Item -ItemType Directory -Path $Evidence).FullName
foreach($case in 'failed','stale','duplicate-sources','missing-compiled','duplicate-compiled','changed-compiled'){
    $ev=Join-Path $root $case
    New-Item -ItemType Directory -Path "$ev/eight-render-hour","$ev/production-smoke-query-ready"|Out-Null
    foreach($name in 'report.md','final-code-review.md'){Set-Content -LiteralPath (Join-Path $ev $name) -Value 'Synthetic negative fixture; no native acceptance.'}
    $value=@{passed=($case -eq 'stale');dllSha256='old';candidateDllSha256='old'}|ConvertTo-Json
    foreach($name in 'final-verification.json','final-preservation.json','eight-render-hour/acceptance-audit.json','production-smoke-query-ready/production-audit.json'){Set-Content -LiteralPath (Join-Path $ev $name) -Value $value}
    if($case -notin 'failed','stale'){
        $hash='61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9'
        @{passed=$true;dllSha256=$hash;nativeJoinOnly=$false;lifecycle=$true;completeMinuteWindows=480;completeMinutesPerBot=60;nativeQuerySeconds=3601;startupSha256=(Get-FileHash -LiteralPath "$PSScriptRoot/Phase1ObstacleAvoidance.ini").Hash}|ConvertTo-Json|Set-Content -LiteralPath "$ev/eight-render-hour/acceptance-audit.json"
        @{passed=$true;dllSha256=$hash;nativeJoinOnly=$true;lifecycle=$true;startupSha256=(Get-FileHash -LiteralPath "$PSScriptRoot/LocalBotRelease.ini").Hash}|ConvertTo-Json|Set-Content -LiteralPath "$ev/production-smoke-query-ready/production-audit.json"
        @{passed=$true;ownedProcesses=0;udpPorts=0;globalManifestFiles=815;binaries=@(1)*30}|ConvertTo-Json|Set-Content -LiteralPath "$ev/final-preservation.json"
        $repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
        $provenance=Get-Content -LiteralPath "$repo/docs/reports/2026-10-12-source-verification.json" -Raw|ConvertFrom-Json
        $sources=@(foreach($file in $provenance.sources){@{name=$file.name;matched=$true;sha256=$file.originalSha256}})
        $game=Join-Path $repo '.codex/shadow-20261010-release-render-lock/Sources/Game'
        $compiled=@(foreach($file in Get-ChildItem -LiteralPath $game -File -Recurse|Where-Object Extension -in '.cpp','.h','.rc','.vcxproj'){@{name=$file.FullName.Substring($game.Length+1);matched=$true;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash}})
        if($case -eq 'duplicate-sources'){$sources=@($sources[0])*13}
        if($case -eq 'missing-compiled'){$compiled=@($compiled|Select-Object -Skip 1)}
        if($case -eq 'duplicate-compiled'){$compiled=@($compiled[0])*32}
        if($case -eq 'changed-compiled'){$compiled[0].sha256='stale-source-hash'}
        @{passed=$true;candidateDllSha256=$hash;sources=$sources;compiledSources=$compiled}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath "$ev/final-verification.json"
    }
    $archive=Join-Path $root "$case-rejected-source.zip"
    $rejected=$false
    try{& "$PSScriptRoot/Package-LocalBotRelease.ps1" -Evidence $ev -Output $archive|Out-Null}
    catch{$rejected=$_.Exception.Message -like 'Release acceptance summary*'}
    if(!$rejected -or (Test-Path -LiteralPath $archive)){throw "Failed or stale release evidence must be rejected before archive creation: $case"}
}
'LOCAL RELEASE PACKAGE NEGATIVE FIXTURES PASS'
