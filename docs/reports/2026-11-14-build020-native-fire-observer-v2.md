# Build020: archivierte Feueraktionen und Observer-V2-Design

Der ursprüngliche Build020-Lauf bleibt **FAIL**: Phase0 `botA:3:fire_action_rows`.
Der neue, reine Archivaudit findet in allen **24/24 Slotphasen** tatsächlich
serverseitig gelesene Schusswaffen-Feueraktionen mit Besitz/Ammo/FIREbit und
Sourcecounterzuwachs im eindeutig gleichen Leben. Ebenso existieren überall
echte Useful-Besitzübergänge im gleichen Entity-/Welt-/Lebenszustand.
Das ist keine nachträgliche native Abnahme und keine Controllerfreigabe.

Privater unveränderter Lauf: `a4-reset020-extended-20261114-092735` unter dem
bestehenden Milestone-A-Evidence-Verzeichnis. DLL
`094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`.
Der Controller sammelte 423,897843 Sekunden; der Hauptagent prüfte anschließend
Restore, geschlossene Rollen/Logs und Preflight. Dieser Archivaudit ersetzt
diese gesonderte Betriebs-/Restoreprüfung nicht.

Der konkrete Aliasfall betrifft Phase0 A3: fünf beobachtete Leben, vier Tode,
105 Bewegungszeilen, zwei Useful-Pickup-Leben und elf native Schusswaffensamples.
Bei current12 liegen Originalserver-Feuersamples zwischen native12,50003 und
13,20003, bei current9 weitere zwischen111,10218 und112,85229. Die sekündlichen
`CecilState`-Zeilen verfehlen diese Pulse; der Counter steigt dennoch0→16 bzw.
26→37. `last_buttons & 1`, Ammo und `fire_requested` kommen aus dem geerbten
Originalserver-Reader, der Weapon-Owner/Welt prüft und veränderte Doppelreads
verwirft. Ein AI-Wunsch allein zählt im neuen Audit nicht.

| Phase | A0 Feuer/Pickup | A1 | A2 | A3 | B0 | B1 | B2 | B3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 11/6 | 143/1 | 31/3 | 11/2 | 184/4 | 26/2 | 22/2 | 173/3 |
| 1 | 135/3 | 21/3 | 71/3 | 27/3 | 32/5 | 26/3 | 110/1 | 7/2 |
| 2 | 19/5 | 67/3 | 4/1 | 136/3 | 32/3 | 10/2 | 97/5 | 95/6 |

Feuerzahlen sind beobachtete Samples, keine Schusszahlen. Pickupzahlen sind
beobachtete Besitzübergänge, keine zusätzlich interpolierten Beschaffungen.
Zeitzeugen an Spawn-/Beobachtungsgrenzen werden verworfen: der ganze mögliche
sechsstellige printf-Rundungsbereich muss innerhalb der unveränderten exakten
Serverlebensgrenzen liegen. Weder die Grenzen noch Gameplaytoleranzen werden
erweitert. Counterresets oder widersprüchliche Generation-/Lebensbindungen
wären unzulässig; im archivierten Material wurden keine solchen Konflikte
gefunden. Ein Sourcecounter allein beweist keinen Treffer oder Schaden.

Reproduktion ausschließlich offline:

```bash
cd tools
python3 -m unittest test_audit_a4_native_fire_observer_v2 -v
python3 audit_a4_native_fire_observer_v2.py /PRIVATE/EVIDENCE_ROOT
```

Dreizehn fokussierte Tests bestehen. Der konservative untere printf-Grenztest
reproduzierte zuerst einen echten Fehler (2 statt0 Samples), bevor das gesamte
Rundungsintervall geprüft wurde. Ein erster Testaufruf aus dem Repo statt dem
angegebenen `tools`-CWD scheiterte am Modulimport; das war kein funktionaler Test.
Keine breite Discovery, Builds oder nativen Prozesse wurden gestartet.

Der [bereinigte JSON-Beleg](milestone-a-20261114/build020-native-fire-observer-v2-audit.json)
enthält alle Eingabehashes und konkrete Inventar-/Sourcelogzeilen je Slotphase.
Der [Plan](../superpowers/plans/2026-11-14-a4-native-fire-observer-v2.md) beschreibt
den künftigen V2-Vertrag. Aktuell importiert kein Controller den Archivaudit.
Ein separater deaktivierter Controller muss dieselben Identitäts-/Epochengates
und den Originalreader beibehalten, ausschließlich das fehlleitende Samplegate
ersetzen und alle übrigen A4-Kriterien erhalten. Review und eigener nativer Lauf
bleiben offen. Die native positive Ausführung des Build020-Terminalwatchdogs
wurde in diesem Lauf weiterhin nicht beobachtet.
