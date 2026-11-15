# A1 Autodrain: erster Getterfehler und separater Cleanup-Folgefehler

Der inputfreie Trace 085939 bleibt **FAIL**. Armierung und Headerguards
bestanden, aber keine vollständige Methoden- oder A1-Abnahme. Die geschlossenen
Rohdaten belegen einen vorübergehend nicht originalen Getterbereich nach der
TLS-Bindung; sie speichern keinen abweichenden Bytewert am Fehlerzeitpunkt.

| Reihenfolge | Tatsächlicher Beleg |
|---|---|
| Arm | native wall_ms 1794733207260 |
| ProcessGameTick ENTER, Call 1 | wall_ms 1794733207273 |
| ApplyAction ENTER, Call 2 | wall_ms 1794733207274, noch kein TLS-Wert im Playerrecord |
| Einziger Getteraufruf bindet TLS | wall_ms 1794733207275 |
| Erster Fehler | gleicher ms, ApplyAction Call 2 **LEAVE**, `bound getter changed` |
| Erster Drain | 2 ENTER-Events, 2 Faults, 0 Drops; Getter `restored=false` |
| Drains 2–45 | Getter `restored=true`; ursprüngliche Faults bleiben sticky |

Der vollständige Getterguard betrifft Original-Engine SHA256
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`,
RVA `0x2c1a0`, in diesem Prozess VA `0x600ec1a0`, Länge 22 Byte. Die temporäre
**Instruktionsprobe** sitzt bei `+15` vor FLD, registriert als einzelner
`function`-Callback, ohne Entry-/onLeave-Paar. Keiner der 18 permanenten Hookguards
überlappt diesen Bereich. Der erste Fehler enthält `raw.detail=null`; die
Bytevergleichsfunktion archiviert nur ein boolesches Ergebnis. Daher bleiben
erster Byteoffset und tatsächliche Patchbytes **UNKNOWN**.

Die Reihenfolge passt zu einem noch nicht abgeschlossenen Detach-Commit.
Sie beweist den konkreten Gum-Mechanismus nicht. Der bisherige portable
Deferred-Detach-VM committet am Callbackende und modelliert diese zusätzliche
Verzögerung nicht. Ein neuer Getterfix wurde hier nicht implementiert.
Der frühere Legacy-Colt-Inputguard ist nicht der erste Fehler dieses inputfreien
Traces; uninstrumentierter Control ist kein ABI-Beleg.

Der anschließend separat von Root durchgeführte eigene ELF32-Integergetter-
Methodenfall reproduzierte das native Problem **nicht**: unmittelbar im
Selfdetach waren Bytes noch verändert, aber bereits beide äußeren Leaves
und erster/späterer RPC lasen Originalbytes. Drei eigene Kinder endeten mit 0,
vollständige 22 Byte nach Unload gleich. Private Methodenquittung SHA256
`02bc2b127547d977c8e53f5ab0dbfdebc95d949d3412c0fbc9bec90e8c16b575`.
Seine Entry-/onLeave-Probe war jedoch **nicht methodenäquivalent** zum tatsächlichen
Instruktionscallback `+15` vor FLD. Auch Roots nachfolgender x87-Entry-Versuch
war deshalb kein passender Reproducer. Alle beiden Nativecalls und der Getter
liefen auf dem tatsächlichen Main-TID; Non-Main-Zähler waren null. Insbesondere
Hooktyp und Instruktionsposition, zusätzlich x87-/TLS-Leseform, bleiben noch
unqualifizierte Unterschiede. Keine Ursache aus der allgemeinen Flushannahme
ableiten.

Der externe Abschlussrecord enthält alle 38 Regionen bytegleich zum Original-
Vorherrecord und unabhängig zu den aus `G` rebasierten HIGHLOW-Bytes, bei
identischer Prozess-/Session-/Spielerbindung. Unload und Detach sind bestätigt.
Die nachgelagerte Gesamtvalidierung bleibt wegen der bestehenden Faults FAIL.

Ein **getrennter, kausal reproduzierter Cleanup-Fehler** verlangte nach sicherem
Idle/Detach ausschließlich `host requested`, bevor finaler Drain und `F`
geschrieben wurden. Ein authentischer Fault-Stop gelangte deshalb nie zu `F`.
Im Originalfall: `S=6`, `F=null`, 0 validierte Pakete, 40 wiederholte
`finishstop`-Aufrufe und insgesamt 1477 Schedulerfehler. Darunter befinden sich
spätere Fehler nach Rollenabbau; sie ersetzen nicht den ersten Getterfehler.

Die enge Korrektur bindet den exakten `finishstop`-Record an den Stopgrund des
geprüften Idle-Status. Nicht-Host-Gründe werden weiterhin sticky FAIL, erlauben
aber den unveränderten finalen Raw-Capture und `index.finish()`. Abweichende
ACK-Form, geänderter Grund oder aktive Callbacks sperren den Abschluss weiter.
Ein fehlgeschlagener finaler Raw-Schreibversuch bleibt als fehlende Evidenz im
Versuchsnenner sichtbar. Keine Queue-, Deadline-, Schema- oder TTL-Erhöhung.

Die neuen Tests verwenden tatsächliche `JournalCollector`, `CaptureJournal`
und `DrainPump` mit synthetischen RPC-Exports. Erst ein Fixture-Aufbaufehler
(`loaded` fehlte) wurde separat behalten; anschließend echtes RED mit fünf
Verhaltensfehlern, danach vier fokussierte Tests PASS (0,060 s). Gesamte bisherige
Autodrainreihe plus neue Fälle: **61 Tests PASS, 4,275 s**. Kein neuer nativer Lauf.

```sh
nice -n 15 python3 -m unittest tools.test_first_state_autodrain_protocol tools.test_first_state_autodrain_worker tools.test_first_state_autodrain_proxy tools.test_first_state_autodrain_native_adapter tools.test_first_state_autodrain_session tools.test_first_state_autodrain_window_patch tools.test_prepare_first_state_autodrain tools.test_first_state_autodrain_fault_stop
```

Private deterministische Analyse, Ausgangs-/Quellhashes, vollständige Quittung
und unveränderte Testlogs liegen im eigenen Worktree unter
`.codex/evidence/a1-autodrain-first-fault/`. Reader nimmt optional einen neuen
exklusiven Ausgabepfad entgegen. Originale FAIL-Rohdaten und Pakete bleiben
unverändert; kein Paket oder Runtime-/Getterfix wurde erzeugt.

Die finale private Raw-Diagnosequittung hat SHA256
`d9c576f8d2eec93f4af1cdc10ad642c6f657b1ece6ccb95e8097da92338493a6`;
sie ist mit dem ebenfalls privaten Reader `analyze.py` und einem neuen
exklusiven Ausgabepfad reproduzierbar.

Für den nächsten getrennten Own-Methodenbeleg stehen die bereits vorhandenen
ELF-Probequellen unter `/srv/tse-frida-method-smoke-20261114/` bereit. Deren alter
`stop()` führt ein explizites `Interceptor.flush()` aus und qualifiziert deshalb
keinen natürlichen Selfdetach-Commit. Ein enger neuer Own-Reproducer muss
`outer→inner`, permanenten äußeren CallListener und eine eigene IA32-22-Byte-
TLS-ähnliche Leseform mit Instruktionsprobe als `function` bei `+15` vor FLD
abdecken. Selfdetach und vollständige Bytes vor/während/nach Callback sowie in
erstem/späterem Drain vergleichen, ohne expliziten Flush. Root führt ihn separat
aus; ein ELF64-Ergebnis wäre kein Retail-IA32-/A1-Beleg.
