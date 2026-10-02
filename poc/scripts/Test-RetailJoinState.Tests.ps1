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
'ALL NATIVE JOIN STATE CHECKS PASSED'
