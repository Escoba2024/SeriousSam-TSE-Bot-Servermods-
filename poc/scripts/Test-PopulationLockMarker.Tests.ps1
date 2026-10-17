$ErrorActionPreference='Stop'
. "$PSScriptRoot/PopulationSupervisor.ps1"
$root=Join-Path ([IO.Path]::GetTempPath()) ('tse-lock-marker-'+[guid]::NewGuid().ToString('N'))
$first=Join-Path $root 'a-first';$second=Join-Path $root 'b-marker'
New-Item -ItemType Directory $first,$second|Out-Null
$path=Join-Path $second '.tse-population-controller.lock'
$marker='SeriousSamPopulationClientLock/v1'
$cases=@(
    @{Name='single-array-root';Text=('[{"format":"'+$marker+'"}]')},
    @{Name='multiple-array-root';Text=('[{"format":"'+$marker+'"},{"format":"'+$marker+'"}]')},
    @{Name='single-array-format';Text=('{"format":["'+$marker+'"]}')},
    @{Name='multiple-array-format';Text=('{"format":["'+$marker+'","'+$marker+'"]}')},
    @{Name='future-version';Text='{"format":"SeriousSamPopulationClientLock/v2"}'},
    @{Name='foreign-marker';Text='{"format":"OtherController/v1"}'},
    @{Name='wrong-case';Text='{"format":"serioussampopulationclientlock/v1"}'},
    @{Name='missing-format';Text='{}'},
    @{Name='null-format';Text='{"format":null}'},
    @{Name='object-format';Text='{"format":{"value":"SeriousSamPopulationClientLock/v1"}}'},
    @{Name='null-root';Text='null'},
    @{Name='empty-array-root';Text='[]'},
    @{Name='string-root';Text='"SeriousSamPopulationClientLock/v1"'},
    @{Name='torn-json';Text='{"format":'},
    @{Name='whitespace';Text=" `r`n "}
)
$failures=@();$checks=0;$held=@()
try {
    foreach($case in $cases){
        [IO.File]::WriteAllText($path,$case.Text)
        $before=[Convert]::ToBase64String([IO.File]::ReadAllBytes($path))
        $refused=$false
        try{$held=Enter-PopulationClientLocks @($second,$first)}catch{$refused=$true}
        finally{foreach($h in $held){$h.Dispose()};$held=@()}
        if(!$refused){$failures+=@('Malformed marker accepted: '+$case.Name)};$checks++
        if([Convert]::ToBase64String([IO.File]::ReadAllBytes($path)) -cne $before){$failures+=@('Rejected marker bytes changed: '+$case.Name)};$checks++
        # Failure on sorted second directory must release the earlier lock.
        $held=Enter-PopulationClientLocks @($first)
        foreach($h in $held){$h.Dispose()};$held=@();$checks++
    }
    # Missing/empty markers and one known object remain recoverable. Marker PID
    # fields are informational; ownership still comes from the OS file handle.
    foreach($text in '',('{"format":"'+$marker+'","pid":0}'),(" `r`n {`"format`":`""+$marker+"`"} `r`n")){
        [IO.File]::WriteAllText($path,$text)
        $held=Enter-PopulationClientLocks @($second)
        if($held.Count -ne 1){throw 'Known/empty marker did not acquire exactly one lock.'};$checks++
        $blocked=$false;$other=@()
        try{$other=Enter-PopulationClientLocks @($second)}catch{$blocked=$true}
        finally{foreach($h in $other){$h.Dispose()}}
        if(!$blocked){throw 'Held marker allowed duplicate controller lock.'};$checks++
        foreach($h in $held){$h.Dispose()};$held=@()
    }
    if($failures.Count){throw ($failures -join '; ')}
    "LOCK MARKER PASS: $checks checks; malformed bytes preserved, partial locks released, valid markers still exclusive"
} finally {
    foreach($h in $held){$h.Dispose()}
    Remove-Item -LiteralPath $root -Recurse -Force
}
