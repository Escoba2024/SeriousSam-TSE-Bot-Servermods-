param(
    [Parameter(Mandatory=$true)][string]$Output,
    [string]$Evidence='.codex/evidence/shadow-20261010/local-release'
)
# Explicit source allowlist: never package retail binaries, SDK imports or backups.
$ErrorActionPreference='Stop'
$repo=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$outputPath=[IO.Path]::GetFullPath($Output)
if(Test-Path -LiteralPath $outputPath){throw 'Use a new source archive path.'}
if(!(Test-Path -LiteralPath (Split-Path $outputPath -Parent) -PathType Container)){throw 'Archive output directory must already exist.'}
$evidencePath=(Resolve-Path -LiteralPath $Evidence).Path
$files=@(Get-Item -LiteralPath (Join-Path $repo 'README.md'),(Join-Path $repo 'CODEX_WINDOWS_POC_REPORT.md'),(Join-Path $repo 'tools/run-shadow-fleet.ps1'),(Join-Path $repo 'tools/ShadowRuntimeLog.ps1'))
$files+=@(Get-ChildItem -LiteralPath (Join-Path $repo 'poc') -File -Filter '*.md')
foreach($folder in 'poc/botcore','poc/patch','poc/scripts','poc/release','tools','docs/reports'){
    $files+=@(Get-ChildItem -LiteralPath (Join-Path $repo $folder) -Recurse -File | Where-Object { $_.Extension -in '.cpp','.h','.patch','.ps1','.py','.ini','.json','.bat','.sh','.md','.vcxproj' -or $_.Name -in 'Makefile','LICENSE' })
}
$files+=@(Get-Item -LiteralPath (Join-Path $repo 'THIRD-PARTY-NOTICES.md'),(Join-Path $repo '.gitattributes'),(Join-Path $repo '.gitignore'),(Join-Path $repo 'docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md'),(Join-Path $repo 'docs/superpowers/plans/2026-10-10-local-bot-release.md'))
# This is a private local qualification archive. Raw summaries can contain
# machine paths; publish the sanitized docs/reports summaries through Git.
# Summaries are portable; large raw logs and restoration backups remain local.
foreach($name in 'report.md','final-code-review.md','final-verification.json','final-preservation.json','eight-render-hour/acceptance-audit.json','production-smoke-query-ready/production-audit.json'){
    $path=Join-Path $evidencePath $name
    if(!(Test-Path -LiteralPath $path -PathType Leaf)){throw "Missing final release evidence: $name"}
    $files+=@(Get-Item -LiteralPath $path)
}
$files=@($files|Sort-Object -Property FullName -Unique)
$hour=Get-Content -LiteralPath (Join-Path $evidencePath 'eight-render-hour/acceptance-audit.json') -Raw|ConvertFrom-Json
$production=Get-Content -LiteralPath (Join-Path $evidencePath 'production-smoke-query-ready/production-audit.json') -Raw|ConvertFrom-Json
$verification=Get-Content -LiteralPath (Join-Path $evidencePath 'final-verification.json') -Raw|ConvertFrom-Json
$preservation=Get-Content -LiteralPath (Join-Path $evidencePath 'final-preservation.json') -Raw|ConvertFrom-Json
$candidateHash='61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9'
if(@($hour,$production,$verification,$preservation|Where-Object {$_.passed -ne $true}).Count){throw 'Release acceptance summary failed.'}
if($hour.dllSha256 -ne $candidateHash -or $production.dllSha256 -ne $candidateHash -or $verification.candidateDllSha256 -ne $candidateHash){throw 'Release acceptance summary uses a stale candidate.'}
if($hour.nativeJoinOnly -or !$hour.lifecycle -or $hour.completeMinuteWindows -ne 480 -or $hour.completeMinutesPerBot -ne 60 -or $hour.nativeQuerySeconds -lt 3600 -or $hour.startupSha256 -ne (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'Phase1ObstacleAvoidance.ini')).Hash){throw 'Release acceptance summary lacks the exact full AI hour.'}
if(!$production.nativeJoinOnly -or !$production.lifecycle -or $production.startupSha256 -ne (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'LocalBotRelease.ini')).Hash){throw 'Release acceptance summary lacks the exact production startup smoke.'}
if($preservation.ownedProcesses -or $preservation.udpPorts -or @($preservation.binaries).Count -ne 30 -or $preservation.globalManifestFiles -ne 815){throw 'Release acceptance summary lacks original preservation.'}
$expectedSourceNames=@(Get-ChildItem -LiteralPath (Join-Path $repo 'poc/release/gamemp') -File|ForEach-Object Name)
$actualSourceNames=@($verification.sources|ForEach-Object name)
if(@($verification.sources).Count -ne 13 -or @($actualSourceNames|Select-Object -Unique).Count -ne 13 -or @(Compare-Object $expectedSourceNames $actualSourceNames).Count){throw 'Release acceptance summary lacks the complete unique captured sources.'}
foreach($source in $verification.sources){
    $provenance=Get-Content -LiteralPath (Join-Path $repo 'docs/reports/2026-10-12-source-verification.json') -Raw|ConvertFrom-Json
    $published=@($provenance.sources|Where-Object name -eq $source.name)
    if(!$source.matched -or $published.Count -ne 1 -or $published[0].originalSha256 -ne $source.sha256 -or (Get-FileHash -LiteralPath (Join-Path $repo "poc/release/gamemp/$($source.name)")).Hash -ne $published[0].publishedSha256){throw 'Release acceptance summary sources changed.'}
    $bytes=[IO.File]::ReadAllBytes((Join-Path $repo "poc/release/gamemp/$($source.name)"))
    $notice=[Text.Encoding]::UTF8.GetBytes($published[0].noticeText)
    $offset=[int]$published[0].noticeOffset
    if($offset -lt 0 -or $notice.Length -ne $published[0].noticeBytes -or $offset+$notice.Length -gt $bytes.Length){throw 'Release acceptance summary invalid publication notice.'}
    $actual=[byte[]]$bytes[$offset..($offset+$notice.Length-1)]
    if([Convert]::ToBase64String($actual) -ne [Convert]::ToBase64String($notice)){throw 'Release acceptance summary publication notice changed.'}
    $original=[byte[]]::new($bytes.Length-$notice.Length)
    [Array]::Copy($bytes,0,$original,0,$offset)
    [Array]::Copy($bytes,$offset+$notice.Length,$original,$offset,$bytes.Length-$offset-$notice.Length)
    $sha=[Security.Cryptography.SHA256]::Create()
    try{$originalHash=([BitConverter]::ToString($sha.ComputeHash($original))).Replace('-','')}finally{$sha.Dispose()}
    if($originalHash -ne $source.sha256){throw 'Release acceptance summary original capture changed.'}
}
$candidateGame=Join-Path $repo '.codex/shadow-20261010-release-render-lock/Sources/Game'
$compiledFiles=@(Get-ChildItem -LiteralPath $candidateGame -File -Recurse|Where-Object Extension -in '.cpp','.h','.rc','.vcxproj')
$expectedCompiledNames=@($compiledFiles|ForEach-Object {$_.FullName.Substring($candidateGame.Length+1)})
$actualCompiledNames=@($verification.compiledSources|ForEach-Object name)
if($compiledFiles.Count -ne 32 -or @($verification.compiledSources).Count -ne 32 -or @($actualCompiledNames|Select-Object -Unique).Count -ne 32 -or @(Compare-Object $expectedCompiledNames $actualCompiledNames).Count){throw 'Release acceptance summary lacks the complete unique compiled source comparison.'}
foreach($source in $verification.compiledSources){
    if(!$source.matched -or (Get-FileHash -LiteralPath (Join-Path $candidateGame $source.name)).Hash -ne $source.sha256){throw 'Release acceptance summary compiled sources changed.'}
}
$prefix=$repo.TrimEnd('\')+'\'
$entries=@(foreach($file in $files){
    if(!$file.FullName.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Package source escaped repository.'}
    [pscustomobject]@{path=$file.FullName.Substring($prefix.Length).Replace('\','/');bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash}
})
$manifest=[ordered]@{format='SeriousSamTSE-LocalBotRelease-source-v1';candidateDllSha256='61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9';sdkCommit='aa7869c2c2c4db0562281814d0ac3784e6b9d6f0';includesCommit='94ff8cd0e63941f8601294350b616472f772ed51';files=$entries;scope='Source and acceptance summaries only; no retail binaries/assets or byte-identical-DLL claim.'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::Open($outputPath,[IO.Compression.ZipArchiveMode]::Create)
try{
    foreach($entry in $entries){[IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $repo $entry.path),$entry.path,[IO.Compression.CompressionLevel]::Optimal)|Out-Null}
    $jsonEntry=$zip.CreateEntry('SOURCE-MANIFEST.json')
    $stream=$jsonEntry.Open()
    try{$bytes=[Text.Encoding]::UTF8.GetBytes(($manifest|ConvertTo-Json -Depth 6));$stream.Write($bytes,0,$bytes.Length)}finally{$stream.Dispose()}
}finally{$zip.Dispose()}
$zip=[IO.Compression.ZipFile]::OpenRead($outputPath)
try{
    if($zip.Entries.Count -ne $entries.Count+1){throw 'Unexpected source archive contents.'}
    foreach($entry in $entries){
        $stream=$zip.GetEntry($entry.path).Open()
        $sha=[Security.Cryptography.SHA256]::Create()
        try{$digest=([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','')}
        finally{$stream.Dispose();$sha.Dispose()}
        if($digest -ne $entry.sha256){throw "Archive/source mismatch: $($entry.path)"}
    }
}finally{$zip.Dispose()}
$manifest|ConvertTo-Json -Depth 6|Set-Content -LiteralPath ($outputPath+'.manifest.json')
[pscustomobject]@{passed=$true;sourceFiles=$entries.Count;archive=$outputPath;archiveSha256=(Get-FileHash -LiteralPath $outputPath).Hash;archiveBytes=(Get-Item -LiteralPath $outputPath).Length}|ConvertTo-Json
