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
$resultTable=$ast.Find({param($node) $node -is [Management.Automation.Language.HashtableAst] -and @($node.KeyValuePairs | Where-Object {$_.Item1.Value -eq 'clientJoined'}).Count -eq 1},$true)
$joinExpression=($resultTable.KeyValuePairs | Where-Object {$_.Item1.Value -eq 'clientJoined'}).Item2.Extent.Text
foreach($case in @(@{text=@('startup',"TSE_Bot_PoC joined`n");expected=$true},@{text=@('startup','not joined yet');expected=$false})) {
    $clientText=$case.text
    $value=Invoke-Expression $joinExpression
    if($value -isnot [bool] -or $value -ne $case.expected){throw 'Chunked log must produce a scalar join Boolean.'}
}
'ALL NATIVE JOIN STATE CHECKS PASSED'
