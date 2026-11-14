# Build022: deaktivierter einzelner Nav20-Red600-Arm

Status: OFFLINE vorbereitet und gepinnt; keine Native-/Funktionsfreigabe.
Root allein reviewt, friert ein und startet gegebenenfalls genau ein isoliertes
600s-Fenster. Kein Rollout und kein neues verpflichtendes Dreierset.

## Herkunft und feste Bedingungen

Parent `/srv/tse-nav20-020-red600-disabled-20261114`, Manifest
`7c1bd1aef595adf3eb4abc1203414dbfe129ff0f722e998b5a181b6b5cf7e4d8`, bleibt unangetastet. Build022 ist erfolgreich gebaut,
aber noch nicht nativ abgenommen: Source `621e92faf1d84e0fe03892b07ab7db230d630390`,
Manifest `8557a3a3de831ed21ba99a74194c8060a1c346629f72bc9a1bd7d7f1184a07c1`, DLL
`28028e448e514cae8589b078d06533c8934a4a12ca7ab52aaead77e1590ab8fc` /434176Bytes.
Builder prüft frisch alle47Source- und28Overlaydateien, Manifest und DLL.

Hard2, DEMON3/duelist und bestehende Seeds/Profile, acht Bots plus unveränderter
Original, RedStation/Nav, diag0, Originalobserver20FPS und600s bleiben gleich.
Leser, V3-Provenienz/Fire-/Usefulgates, Readraten, Gap-/Hostbudget,
Start-/Pause-/Module-/Identitäts-/Restore-/Normalclosepfade bleiben bytegleich.
75%CPU,1.5GiB verfügbarerRAM und8GiBfreierDatenträger bleiben die Grenzen.
Es werden keine zusätzlichen Inputs/Queries/Inventarreads/Hooks eingeführt.

Genau drei vorhandene Paketdateien ändern sich: `run-a4.py` erhält022-DLLpfad
und ehrliche Namespace-/Session-/Hilfelabels, `adapter_policy.py` den022-Hash
und Armverweis, die paketlokale `navigation_comparison_policy.py` ergänzt nur
den geschlossenen022-Kandidateneintrag. Die unveränderte versionierte
Kandidatentabelle wird nicht erweitert. Die Rücktransformation rekonstruiert
alle drei Parentdateien exakt; weitere58Parentsourcedateien sind bytegleich.
Separate kleine Quelldiffs werden im Paket gepinnt mitgeliefert.

Metadaten bezeichnen ausdrücklich nur Arm022, `order=['022']`, kein Retry und
keine automatische Sequenz; bisherige Vergleichsmetadaten bleiben historisch
separat erhalten. Runtime-/Reviewgates bleiben False. Das neue
`health_connector_proposal` bedeutet nur Planungsvorschlag, keinen akzeptierten
Input, tatsächlichen Healthgewinn oder Pickup. Die konkrete native Ursache der
alten Waffenunverfügbarkeit und Healthgain-Zuordnung bleibt UNKNOWN. Alte
FAIL-/PASS_LIMITED-Ergebnisse werden nicht neu bewertet.

## Offlineverifikation

Sieben echte REDs vor Existenz des Builders; finale sieben neue Tests,
sechs Observer20- und neun Vergleichsregressionen: **22/22 PASS**, Exit0.
Die erste Reversefassung scheiterte an überlappenden Namespaceankern (2Fehler)
und anschließend an einem gemischten schon retargeteten Text (1Fehler);
volle eindeutige Anker und explizite Partialretargetablehnung beheben dies.
Ein separater Verifikationswrapper hatte vor jeder Operation einen Syntaxfehler;
der korrigierte vollständige finale Lauf und Generator sind erfolgreich.
Keine Compiler-/Runtime-/Display-/Frida-/Spielausführung.

```sh
python3 -B -m unittest discover -s tools -p test_navigation_build022.py -v
python3 -B tools/test_navigation_observer20.py -v
python3 -B tools/test_navigation_comparison.py -v
python3 -B tools/prepare_navigation_build022.py --destination /NEUER/PRIVATER/PFAD
```

Frischer deaktivierter Fork:
`/srv/tse-nav20-022-red600-disabled-20261114`.
Manifest `aa5783efbed7dc53a33ccee9f0755890eba6c2bdc8f5e9b43e76ff0059d648df`,
Controller `d9e899a11dbe105de49225d8dcd1f71d8b551e646f15602bd4127f60829d1dc5`.
139Runtime-/66Source-/41Pythonpins frisch vollständig rückgelesen und korrekt.
Private Befehls-/Outputquittungen liegen im eigenen Worktree unter
`.codex/evidence/nav20-build022/`; Finalquittung SHA
`0267c33f60cadc7f35bbeb1320258d5da5f6312f626be1a283f5806f68bd94fc`.
Keine alten komprimierten Nav20-Rohdateien wurden benötigt oder entpackt.
