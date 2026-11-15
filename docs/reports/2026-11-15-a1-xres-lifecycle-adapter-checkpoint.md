# A1-XRes-Lifecycle: überprüfbarer Offline-Quellcheckpoint

Noch kein Paket/Methodencontroller und keine Nativequalifikation. Dieser
Checkpoint sichert nur neue Adapter-, Worker-, Evidence- und Testquellen nach
23 gezielten PASS/0Skips/0,072s. Root entscheidet Integration und Native später.

Claim: neue `a1_xres_attribution{,_worker,_evidence}.py` und ihre drei Tests;
keine bestehenden Core-/A1-/Runtimequellen verändert. Eigenes WT ab Root1af4ab2.
Die vier eingefrorenen Parent-Coredateien wurden frisch gegen die vorhandenen
Runtimepins geprüft; ihre Quellhashes sind in der privaten Quittung erhalten.
Eine neue A1-Kopie wurde noch nicht erzeugt, ihre spätere Bytegleichheit ist
folglich noch keine bestandene Paketprüfung.

Die Rangefactory erhält alle bisherigen Protokollranges und setzt nur in der
ersten frischen Range die beiden Lifecycleflags. Keine gemeinsamen Coreglobals
werden verändert. Der explizit kopierte Armkörper verwendet diese Factory,
beweist StartOfData und liest erst danach Snapshot1. Snapshot2 erfolgt vor dem
unverändert weiterverwendeten Core-Disable/Enddrain/Close. Nur method167 kann die
zweite Aufnahme vor normalem Peerleave vorziehen; A1154 verweigert diesen Befehl.
Eine dritte Aufnahme ist verboten. Metadatafehler bleiben sticky, überspringen
aber den normalen Corecleanup nicht.

Metadaten dürfen keine großen Stop-/IPCantworten erzwingen. Die beiden Snapshots
und begrenzten Versuche werden ausschließlich in `xres-attribution.json` mit
inherited private_json (0600/O_EXCL,262144Bytegrenze) gespeichert. Die bestehende
kleine Nativeclosequittung trägt nur Hash/Länge/Pfad und kompakte Zähler;
16384ByteIPC und die bestehende16384ByteNativeclosegrenze bleiben erhalten.
Der Parent liest die Sidecar erst nach inherited Close/Reap, prüft ihren Hash
und die unveränderte vollständige RECORDdatei. Kein Metadatencall pro Input/ACK.

Die pure Auswertung replayt jede Rawrow durch den unveränderten Coredecoder,
prüft die Native-Callback-/Free-/Drop-/Start-/Endzähler und dieselben Worker-
Monotonicgrenzen. Jeder Clientstart/-tod sperrt die betroffene Base für positive
Intervallzuordnung, auch bei gleicher PID in beiden Snapshots. Neue oder
abweichende PID/TID bleibt ungebunden; falsche explizite Originalfenster-/GC-
Resourcezuordnung scheitert strikt. Keine Clockfusion, kein Zeit-/Gain-/FPSfix.
Alte U und historische Gain-FAILs bleiben unverändert.

Private RED/GREEN-Logs und Quittung:
`/srv/tse-a1-xres-lifecycle-evidence-20261114/adapter-23-source-checkpoint.json`,
SHA256 `4ae3a2e044930bb83125cc2c39d47eb8aa4f532f29a624d9f3af9dc23e02e6ba`.
Finaler Checkpointlog `green-parent-and-worker-first.log`, SHA256
`1c22044faa030dbb692afaf251264faeb1819365ae330f5462ed42083d96f533`.
Ein früher erster Pure-GREEN-Versuch scheiterte an zwei unvollständigen
Testfixtures; dieser Log bleibt erhalten. Danach wurden beide Fixtures korrigiert
und die reine Suite grün. Weitere tatsächliche REDs für fehlende Worker/Adapter,
getrennten Methodenscope, Native-Bool-/Monotonicgrenzen sind ebenfalls gespeichert.

```sh
cd /srv/tse-a1-xres-lifecycle-adapter-20261114/tools
python3 -B -m unittest test_a1_xres_attribution_evidence test_a1_xres_attribution_worker test_a1_xres_attribution -v
```

Nächster Arbeitsschritt: getrennten deaktivierten inputfreien167-Methodenfall und
A1-Builder nach eigenen REDs vervollständigen; kein ausführbares Folgefenster.
