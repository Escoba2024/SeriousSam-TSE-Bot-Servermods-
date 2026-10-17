$ErrorActionPreference='Stop'
$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile("$PSScriptRoot/Test-RetailJoin.ps1",[ref]$null,[ref]$errors)
if($errors){throw $errors}
$predicate=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Test-NativeJoined'},$true)
if(!$predicate){throw 'Native join predicate missing.'}
Invoke-Expression $predicate.Extent.Text
if(Test-NativeJoined ''){throw 'Empty log accepted.'}
if(Test-NativeJoined 'startup only'){throw 'Unjoined client accepted.'}
if(!(Test-NativeJoined "  joined`n")){throw 'Current native join rejected.'}
if(Test-NativeJoined "  joined`nCannot join game:`nTimeout while waiting for reply"){throw 'Historical join masked later timeout.'}
if(!(Test-NativeJoined "Cannot join game:`nTimeout while waiting for reply`n  joined`n")){throw 'Successful normal rejoin rejected.'}
if(Test-NativeJoined "  joined`nDisconnected: Too many bad syncs`n"){throw 'Historical join masked a real sync disconnect.'}
if(Test-NativeJoined "  joined`nConnection timed out`n"){throw 'Historical join masked a timeout.'}
if(!(Test-NativeJoined "  joined`nDisconnected: Too many bad syncs`n  joined`n")){throw 'Successful rejoin after sync disconnect rejected.'}
# Regression: the observer must identify the complete, color-normalized player name.
# Extract the real result expression to keep this a direct harness gate test.
$observerAssignment=$ast.Find({param($node) $node -is [Management.Automation.Language.AssignmentStatementAst] -and $node.Left.Extent.Text -eq '$result.observerSawBotJoin'},$true)
if(!$observerAssignment){throw 'Observer bot-join gate missing.'}
$observerExpression=$observerAssignment.Right.Extent.Text
$observerHelper=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Test-ObserverSawExactBotJoin'},$true)
if($observerHelper){Invoke-Expression $observerHelper.Extent.Text}
$ExpectedBotName='TSE_Bot_Client_1'
foreach($case in @(
    @{log="^oTSE_Bot_Client_1^r joined";expected=$true;label='actual Retail colored join'},
    @{log="TSE_Bot_Client_1 joined";expected=$true;label='plain exact join'},
    @{log="^o^i^cff6600TSE_Bot_Client_1^r joined";expected=$true;label='decorated exact join'},
    @{log="Player ImpostorTSE_Bot_Client_1_Else joined";expected=$false;label='impostor substring'},
    @{log="^oTSE_Bot_Client_1_Else^r joined";expected=$false;label='suffix impersonation'},
    @{log="Other_Player joined";expected=$false;label='unrelated join'}
)) {
    $observerText=$case.log
    $actual=[bool](Invoke-Expression $observerExpression)
    if($actual -ne $case.expected){throw ('Observer exact-identity gate wrong for '+$case.label)}
}
$ExpectedBotName=''
$observerText='Other_Player joined'
$rejectedEmpty=$false
try { [void](Invoke-Expression $observerExpression) } catch { $rejectedEmpty=$true }
if(!$rejectedEmpty){throw 'An empty ExpectedBotName was not rejected.'}
$ExpectedBotName='TSE_Bot_Client_1'
$resultTable=$ast.Find({param($node) $node -is [Management.Automation.Language.HashtableAst] -and @($node.KeyValuePairs | Where-Object {$_.Item1.Value -eq 'clientJoined'}).Count -eq 1},$true)
$joinExpression=($resultTable.KeyValuePairs | Where-Object {$_.Item1.Value -eq 'clientJoined'}).Item2.Extent.Text
foreach($case in @(@{text=@('startup',"TSE_Bot_PoC joined`n");expected=$true},@{text=@('startup','not joined yet');expected=$false})) {
    $clientText=$case.text
    $value=Invoke-Expression $joinExpression
    if($value -isnot [bool] -or $value -ne $case.expected){throw 'Chunked log must produce a scalar join Boolean.'}
}
# Pure fixture test: no retail installation or game process may be touched.
$restore=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Restore-RetailTestDll'},$true)
if(!$restore){throw 'Retail DLL restore helper missing.'}
Invoke-Expression $restore.Extent.Text
$source=Get-Content -LiteralPath "$PSScriptRoot/Test-RetailJoin.ps1" -Raw
if($source -notmatch 'Restore-RetailTestDll -Backup \$savedDll -Destination \$clientDllPath -ExpectedHash \$originalDllHash'){
    throw 'Main native join cleanup does not call the checked DLL restorer.'
}
$tempRoot=Join-Path ([IO.Path]::GetTempPath()) ('tse-joinrestore-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot|Out-Null
try {
    $backup=Join-Path $tempRoot 'GameMP-before.dll'
    $active=Join-Path $tempRoot 'GameMP.dll'
    [IO.File]::WriteAllText($backup,'ORIGINAL_DLL_FIXTURE')
    [IO.File]::WriteAllText($active,'CANDIDATE_DLL_FIXTURE')
    $originalHash=(Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash
    Restore-RetailTestDll -Backup $backup -Destination $active -ExpectedHash $originalHash
    if((Get-FileHash -LiteralPath $active -Algorithm SHA256).Hash -ne $originalHash){throw 'Fixture DLL was not restored.'}
    [IO.File]::WriteAllText($active,'CANDIDATE_DLL_FIXTURE')
    [IO.File]::WriteAllText($backup,'CORRUPTED_BACKUP')
    $blocked=$false
    try {Restore-RetailTestDll -Backup $backup -Destination $active -ExpectedHash $originalHash} catch {$blocked=$true}
    if(!$blocked -or [IO.File]::ReadAllText($active) -ne 'CANDIDATE_DLL_FIXTURE'){
        throw 'Corrupt backup was not rejected before touching destination.'
    }
} finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force
}
# Validate cross-bitness module checks using only an owned 32-bit PowerShell test process.
$moduleHelper=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Test-NativeModuleLoaded'},$true)
if(!$moduleHelper){throw 'Native cross-bitness module helper missing.'}
Invoke-Expression $moduleHelper.Extent.Text
if([Environment]::Is64BitOperatingSystem -and [Environment]::Is64BitProcess){
    $x86=Join-Path $env:WINDIR 'SysWOW64\WindowsPowerShell\v1.0\powershell.exe'
    if(Test-Path -LiteralPath $x86){
        $fixture=Start-Process -FilePath $x86 -ArgumentList '-NoProfile -NonInteractive -Command "Start-Sleep -Seconds 20"' -WindowStyle Hidden -PassThru
        try {
            Start-Sleep -Milliseconds 1500
            if($fixture.HasExited){throw '32-bit module fixture ended too soon.'}
            if(!(Test-NativeModuleLoaded -GameProcessId $fixture.Id -ExpectedModule 'mscorlib.ni.dll')) {
                throw '32-bit module check failed to detect an actual loaded module.'
            }
            if(Test-NativeModuleLoaded -GameProcessId $fixture.Id -ExpectedModule 'TSE_NotInstalled_Fake.dll'){
                throw '32-bit module check falsely accepted a nonexistent DLL.'
            }
        } finally {
            if(!$fixture.HasExited){$fixture.Kill();$fixture.WaitForExit(5000)|Out-Null}
            $fixture.Dispose()
        }
    }
}
'ALL NATIVE JOIN STATE, X86 MODULE AND DLL RESTORE CHECKS PASSED'
