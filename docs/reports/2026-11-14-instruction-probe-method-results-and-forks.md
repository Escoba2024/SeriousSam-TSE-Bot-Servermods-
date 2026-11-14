# Eigene IA32-Methodenbefunde und deaktivierte Retail-Forks

Root führte drei getrennte Aufrufe der eigenen Kernel32-EXE durch. Kein TSE und
keine Retailqualifikation. Die eigenen Resultate wurden unabhängig gelesen:

| Aufruf | Result-SHA256 | Enges Ergebnis |
|---|---|---|
| baseline125220 | c76101bc3ec95fa3bf7eea7483d51783181652cfadec3551d75ffb101f384b4e | PASS_METHOD_ONLY |
| function-probe125238 | 42b2f249ac55b968bf7ae36c87c3723454d1755ab7600d4ee869fb6f40d299b0 | PASS_METHOD_ONLY |
| historical-object125305 | 050b8472223ef93ddaa83f61ba268f573bee7dbeb0a9b0379f1246c15aa54148 | FAIL_METHOD_EVIDENCE |

Quittungen privat unter
`/srv/tse-win32-instruction-method-stdin-fixed-root-frozen-20261114/evidence-*/result.json`.
Baseline und Funktionsprobe lieferten tatsächlich EDI12345678 und Argumentwert
10203040. Funktionsprobe: zwei richtige Sitekontexte, gleicher positiver Thread,
originale Stackoberkanten, kein Drop/Fault, vollständige Originalbytes verifiziert,
Idle/Detach/Unload bestätigt, normales eigenes Prozessende0 vor Workerreap.

Die Objektkontrolle beschädigte beide tatsächlichen nativen Endwerte zu
EDI7f51460f/Argument7e534b0b. Close-RPC überschritt jedoch seine unveränderte
2s-Frist; Originalbytes, Hookdetach, Unload und Sessiondetach bleiben unbekannt.
Normales Q führte zum eigenen Ende0, anschließend eigener Workerreap; der Fehler
blieb sticky. Deshalb kein vollständiger negativer Kontroll-PASS und kein
kombinierter Methoden-PASS. Kein Retry mit der nachweislich schädlichen Form
ist nötig, um ausschließlich die separat bestandene Funktionsform prospektiv
weiterzuprüfen. Die Ursache früherer Retailbefunde ist damit noch nicht bewiesen.

## Neue deaktivierte Pakete

`tools/prepare_instruction_forks.py` prüft vor jeder Kopie die exakten vollständigen
Elternmanifeste und alle vererbten aktiven Runtime-/Sourcepins. Neuer Zielpfad ist
Pflicht. Alte Pakete und native FAILs bleiben unverändert. Kein Launcherstart,
Compiler-, Wine-, Frida- oder TSE-Aufruf durch den Builder.

| Paket | Parentmanifest | Neues Manifest | Runtimepins |
|---|---|---|---|
| /srv/tse-a1-instruction-probe-disabled-20261114 | 27972cdd295fc7a81f3177e4745bffc4c91bea32b4c71f918ce716c59b0db80b | 686b9c1085337d839da7b4de9409054033971dd805c17283a972299df2c2db5f | 68 |
| /srv/tse-a3-instruction-probe-disabled-20261114 | 3e9a93ac6f06503f84f8f914b5a6b45aec03a35dfce7ed6552b9905676c39a5e | 4143c97affe1870f864d41757d9d22bff0b7a8e91b78d8b37dc89511b054a3d2 | 79 |

A1 übernimmt exakt die vier bereits geprüften Midpoint-Funktionsformen aus
1bbd3a658cd2b00cedb9edbfb97b94a9573eed78. Echte GetInput/CreateAction-
Funktionspaare bleiben unverändert. A3 ändert ausschließlich die Getter+15-
Callbackform; der resultierende private Hook ist bytegleich zum bereits
veröffentlichten Lifecyclepatch auf dessen exakter Originalquelle.

Zusätzlich nur neue Prefixe/Evidencepfade, A1-PRIVATE-Pfad, deaktivierte Gates und
aktive Sourcepins einschließlich A3-FROZEN_HASHES. A1 Worker- und vollständige
Originalreceipt-Logik bleiben bis auf Gatefalse bytegleich; CP, InputScope,
Dualinput und InventoryReader bleiben bytegleich. A3 Worker/Collector,
Originaldamage- und Restorecode bleiben bytegleich. Keine Sites, Inputs,
Sampleraten, TTLs, IPCfristen, ACK-/Gain-/EPS- oder Abnahmekriterien ändern sich.
Neue Manifeste behaupten keine native Ausführung oder Qualifikation.

## Fokussierte Offlineprüfung und nächste Schritte

Zwei neue Builderfälle zunächst RED wegen fehlendem Modul, anschließend GREEN:
exakte deaktivierte Kopien/alle aktiven Pins/geschützte bytegleiche Komponenten
und Ablehnung unbekannter Hookquellen. Eine zusätzliche A3-Pinassertion fand vor
Korrektur das noch alte FROZEN_HASHES (RED); der Generator retargetet nun genau
diesen einen Hash (GREEN). Zwei frühe Datei-Schreibversuche verwendeten den
falschen CWD und erstellten keine Dateien; sie sind keine fachlichen RED-Belege.
31 A1-JS-VM- und sieben A3-Lifecycle-/Getter-VM-Fälle bestanden ohne Skip.
Insgesamt40 gezielte Offlinefälle; keine breite Discovery oder native Aktion.
Frischer Abschlussread:68/68 und79/79 Runtimepins korrekt.

```sh
cd tools
python3 -m unittest test_prepare_instruction_forks -v
node test_a1_input_trace_callbacks.js
TSE_ORIGINAL_DAMAGE_JS=/srv/tse-a3-direct020-hard-controller-20261114/frozen-v2/damage_readonly.js python3 -m unittest test_a3_damage_quiescence -v
```

Root integriert nach unabhängigem Review und erstellt eigene neue Freezes mit
konsistenten Gates/Namespaces/Quellpins. Jeder native Retailaufruf erfordert einen
frischen exklusiven Preflight und nachfolgende Cleanup-/Restoreprüfung. A1 bleibt
auf die vorhandene NoFire-Diagnose begrenzt; A3 bleibt direkter Hard2-Tiervergleich.
Keine automatische Serie/Retry und keine Freigabe aus dem eigenen Methodenbefund.
