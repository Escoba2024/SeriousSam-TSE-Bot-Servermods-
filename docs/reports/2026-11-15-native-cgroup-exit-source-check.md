# Cgroup-Exit: reproduzierte Fehlerklasse, deaktivierte Quellkorrektur

Der ON071200-Fall bleibt FAIL. Mangels Traceback ist dessen konkrete
FileNotFoundError-Stelle unbekannt. Der tatsächliche gepinnte Backendbody
(SHA256b4d57b35ce54f74185e3d891c17676a374ab3e892e148400a0a6ac712a9a1158)
führt in empty() zuerst exists(), dann read_text() aus. Ein deterministischer
Lifecycle-Test und ein echter temporärer Dateiunlink zwischen diesen Aufrufen
reproduzieren FileNotFoundError am unveränderten Originalbody.

Die neue reine Source-Transformation ändert ausschließlich empty(): ein Read;
bei FileNotFoundError muss dessen filename exakt die erwartete Cgroupdatei sein.
Ist diese danach verschwunden, gilt die Cgroup bei dieser Prüfung als leer;
eine wiedererschienene Datei bleibt nichtleer. Fremde/unklare Fehlpfade,
PermissionError und I/O-Fehler propagieren. Zusätzliche Identitäts-, Unit- und
Präfix-Quieszenzprüfungen der Caller bleiben unverändert erforderlich.

Echter RED am fehlenden neuen Modul bei bereits reproduzierter Altquellrace;
anschließend6Tests0,034s GREEN; um zwei reale/unklare Fehlerfälle erweitert:
**8Tests0,041s PASS**. Die Tests führen die tatsächliche transformierte Methode
aus, prüfen Busy/Empty/Missing/Disappearing/Reappearing, fremde Fehler sowie
die vollständige bytegenaue Parentinverse. Veränderungen fremder Methoden
werden durch den vollständigen Parenthash zurückgewiesen.

Kein gefrorenes Paket geändert, keine Runtime ausgeführt, keine Nativefreigabe.
Dies schließt eine nachgewiesene Fehlerklasse, beweist aber nicht die konkrete
ON-Ursache oder einen früher nicht attestierten Close. Integration in einen
neuen deaktivierten Controller, unabhängiger Review und gezielter echter
Lifecycle-Nachweis stehen separat aus. Kein automatischer 600s-Retry.

Die neue deaktivierte Backendkopie liegt unter
`/srv/tse-native-cgroup-exit-disabled-20261115` und besitzt ausdrücklich keinen
Runner/Activationentrypoint. Manifest
`6ce198408fcadf2bdaf99c84a1eada8ac2a4078fa099d6a18448c7c36a6b2dff`.
Unabhängiger Quellreview ist angefordert; keine Nativeprüfung vorwegnehmen.
