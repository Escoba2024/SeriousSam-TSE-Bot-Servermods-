$ErrorActionPreference='Stop'
if(Test-Path "$PSScriptRoot/PopulationSupervisorCore.ps1"){. "$PSScriptRoot/PopulationSupervisorCore.ps1"}
if(!(Get-Command ConvertTo-PopulationSample -ErrorAction SilentlyContinue) -or !(Get-Command Get-PopulationGroupDecision -ErrorAction SilentlyContinue)){throw 'Supervisor functions are missing'}
$checks=0
function Assert($Condition,$Label){if(!$Condition){throw $Label};$script:checks++}
function Status($Count,$Max=16,$Map='Fortress'){return "\gamename\serioussamse\gamever\1.07\activemod\\numplayers\$Count\maxplayers\$Max\mapname\$Map\final\\queryid\1.1"}
function Players($Names){$t='';for($i=0;$i -lt $Names.Count;$i++){$t+="\player_$i\$($Names[$i])\frags_$i\0\ping_$i\30"};return $t+'\final\\queryid\2.1'}
function Sample($Names){ConvertTo-PopulationSample (Status $Names.Count) (Players $Names) (Status $Names.Count)}
function Reject($Before,$Reply,$After){$bad=$false;try{ConvertTo-PopulationSample $Before $Reply $After|Out-Null}catch{$bad=$true};Assert $bad 'Malformed/fenced snapshot accepted'}
$s=Sample @('A1','A2','A3','A4','B1','B2','B3','B4')
Assert ($s.Total -eq 8 -and $s.MaxPlayers -eq 16) 'Valid count'
$dup=Sample @('SameHuman','SameHuman')
Assert ($dup.Total -eq 2) 'Legitimate duplicate display names rejected'
Reject (Status 2) (Players @('One')) (Status 2)
Reject (Status 1) (Players @('One')) (Status 2)
Reject (Status 1) (Players @('One')) (Status 1 16 'OtherMap')
Reject (Status 0) '\final\\queryid\2.1' ((Status 0).Replace('1.07','1.10'))
Reject (Status 0) '\final\\queryid\2.1' ((Status 0).Replace('\activemod\\','\activemod\Mod\'))
Reject (Status 1) '\player_0\A\player_0\B\final\\queryid\2.1' (Status 1)
Reject (Status 1) '\player_16\A\final\\queryid\2.1' (Status 1)
Reject ((Status 0)+'\numplayers\0') (Players @()) (Status 0)
Reject (Status 1) ((Players @('One')).Replace('\final\','')) (Status 1)
Reject (Status 1) '\player_0\final\' (Status 1)
Assert ((Sample @('final')).Total -eq 1) 'Valid player named final rejected'
Reject (Status 17 16) (Players @(1..17)) (Status 17 16)
$groups=@(
 [pscustomobject]@{Id='A';Size=4;Active=$true;EligibleAt=0},
 [pscustomobject]@{Id='B';Size=4;Active=$true;EligibleAt=0})
$d=Get-PopulationGroupDecision $s $groups 8 2 0
Assert ($d.Action -eq 'Hold') 'Stable eight should hold'
$d=Get-PopulationGroupDecision (Sample @('A1','A2','A3','A4','B1','B2','B3','B4','TSE_Fleet_SpoofHuman')) $groups 8 2 0
Assert ($d.Action -eq 'Stop' -and $d.GroupId -eq 'B') 'Unknown/prefix-looking player must consume capacity'
$groups[1].Active=$false
$d=Get-PopulationGroupDecision (Sample @('A1','A2','A3','A4','Human')) $groups 8 2 0
Assert ($d.Action -eq 'Hold') 'Do not overfill remaining three slots with group4'
$d=Get-PopulationGroupDecision (Sample @('A1','A2','A3','A4')) $groups 8 2 0
Assert ($d.Action -eq 'Start' -and $d.GroupId -eq 'B') 'Fill four available slots'
$groups[1].EligibleAt=10
Assert ((Get-PopulationGroupDecision (Sample @('A1','A2','A3','A4')) $groups 8 2 9).Action -eq 'Hold') 'Cooldown not respected'
Assert ((Get-PopulationGroupDecision ([pscustomobject]@{Valid=$false}) $groups 8 2 11).Action -eq 'Hold') 'Uncertain sample acted'
$groups[1].Active=$true
$d=Get-PopulationGroupDecision (Sample @(1..8)) $groups 16 10 0
Assert ($d.Action -eq 'Stop' -and $d.Cap -eq 6) 'Hard reserve not respected'
$groups[0].Size=0
$bad=$false;try{Get-PopulationGroupDecision $s $groups 8 2 0|Out-Null}catch{$bad=$true}
Assert $bad 'Invalid group accepted'
"POPULATION MODEL PASS: $checks checks"
