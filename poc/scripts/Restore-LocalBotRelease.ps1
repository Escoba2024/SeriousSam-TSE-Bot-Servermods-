param([Parameter(Mandatory=$true)][string]$Backup)
$ErrorActionPreference='Stop'
. "$PSScriptRoot\LocalBotReleaseCore.ps1"
$backupPath=(Resolve-Path -LiteralPath $Backup).Path.TrimEnd('\','/')
$manifestPath=Join-Path $backupPath 'manifest.json'
$manifest=Get-Content -LiteralPath $manifestPath -Raw|ConvertFrom-Json
Assert-LocalBotClientsStopped $manifest.fleet
# Validate the complete restore set before writing any destination.
foreach($entry in $manifest.files){
    $destination=[IO.Path]::GetFullPath($entry.path)
    $inside=@($manifest.fleet.processes|Where-Object{$destination.StartsWith(([IO.Path]::GetFullPath($_.clientDir).TrimEnd('\','/')+'\'),[StringComparison]::OrdinalIgnoreCase)})
    if($inside.Count -ne 1){throw 'Restore target escapes its isolated bot client.'}
    if($entry.existed){
        $source=[IO.Path]::GetFullPath($entry.backup)
        if(!$source.StartsWith(($backupPath+'\'),[StringComparison]::OrdinalIgnoreCase) -or (Get-FileHash -LiteralPath $source).Hash -ne $entry.sha256){throw 'Restore backup hash/path mismatch.'}
    }
}
foreach($entry in $manifest.files){
    if($entry.existed){
        Copy-Item -LiteralPath $entry.backup -Destination $entry.path -Force
        if((Get-FileHash -LiteralPath $entry.path).Hash -ne $entry.sha256){throw 'Restore hash mismatch.'}
    }elseif(Test-Path -LiteralPath $entry.path){Remove-Item -LiteralPath $entry.path}
}
foreach($entry in $manifest.native){if((Get-FileHash -LiteralPath $entry.path).Hash -ne $entry.sha256){throw 'Native engine/entity/executable changed outside the release preparation.'}}
@{restored=$true;utc=[datetime]::UtcNow.ToString('o');files=@($manifest.files).Count}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $backupPath 'restored.json')
"RESTORED: $(@($manifest.files).Count) original file states"
