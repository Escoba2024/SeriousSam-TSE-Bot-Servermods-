# A1: Original-Waffenroute nach belegter RD-Kalibrierung

Datum: 2026-11-12
Status: **READY_FOR_INDEPENDENT_ROOT_REVIEW — privates Paket deaktiviert, kein nativer Lauf dieses Nachfolgers.**

## Ergebnis

Der vorbereitete Nachfolger führt zuerst exakt die unveränderte RD.run_calibration aus. Erst nach ihrem neuen erfolgreichen Abschluss startet er die unveränderte shooter_policy.Route für botA und anschließend eine normale Fire-Eingabe von 2 Sekunden. Das alte S.run_program wird nicht aufgerufen und seine frühere Kalibrierung deshalb nicht wiederholt.

Der gesamte begrenzte Ablauf bleibt eine Vorbereitung. qualified, input_once_proven, actual_shot_proven, foreign_hit_proven und first_processed_state_proven sind weiterhin false. Eine normale 2-s-Fire-Eingabe ist ein begrenzter Feuerstoß als Bedieneingabe; sie belegt weder genau ein Geschoss noch einen tatsächlichen Treffer. Erst nach vollständiger normaler Beendigung, akzeptierten geschlossenen Logs und erfolgreicher Wiederherstellung darf der Controller PASS_LIMITED_NORMAL_PREPARATION_REVIEW_REQUIRED melden.

## Isolierung und exakte Artefakte

- Basis: 1a9ab5e35331fe9bfa74de414ffef7c0aca3091c.
- Branch: codex/20261112-a1-route-after-rotation.
- Worktree: /srv/tse-milestone-a-a1-route-completion-20261112.
- Claim: /srv/tse-milestone-a-continuation-evidence-20261112/a1-route-claim.json.
- Neuer privater Nachfolger: /srv/tse-a1-route-after-rotation-completion-20261112.
- Spezifikation: docs/superpowers/specs/2026-11-12-a1-route-after-rotation.md.
- Ausführungsplan: docs/superpowers/plans/2026-11-12-a1-route-after-rotation.md.

| Artefakt im privaten Paket | SHA-256 |
| --- | --- |
| source-manifest.json | a902c0133fb31f6f4703e3626b5ebe2521567169c00fb89e1f3c68ea8bdd5bb8 |
| run_dual.py | 47a59a6ffdb64274d56198e1587b1e3760b4b2beb7ada9fbfaacc3d18d95e79b |
| preparation_policy.py | 57aa07c533cf3c61be81dde36064d2de97cf3689eded71f27393ca7730541c83 |
| evidence/route-normalized-delta.json | a273e6057d280ea45dd2a5bc703033fd3e3b062dea96268119fe94c600224f9e |
| evidence/route-native-v3-baseline.json | f3685a6dc6494bc2a91002efe0521d1781f8a8c55b93e48ee289c565b73b16f6 |

Das Manifest enthält 48 Runtime-, 41 eigene Quell- und 56 Evidence-Pins. Beide Laufzeitgates bleiben false. Der Repository-Commit enthält ausschließlich Dokumentation; die privaten Runtime-Quellen sind durch die oben angegebenen Artefakte eingefroren.

## Tatsächlich beobachteter Ausgangspunkt

Der Elternstand ist /srv/tse-a1-input-diagnostics-completion-v3-20261112 mit Manifest 0f15a0cb6e82ebfe8694ddf8cc007c74a5318f42bae2fc984138ffb460029e26.

Im vollständig geschlossenen und wiederhergestellten nativen Fenster a1-input-diagnostics-completion-v3-20261112-090901 war die tatsächliche Join-Zuordnung vanilla = Slot 0 und botA = Slot 1. Alle 35 gültigen Server-Snapshots zeigten botA als Entity 563 unverändert an [70.875,0.3763999938964844,63], Yaw 90.00000762939453, SpawnTick 7.900012016296387. Der erste Zustand hatte 100 HP, owned 3 / current 2. Diese tatsächliche Lage passt zum bestehenden Korridor; sie wurde nicht aus dem Namen abgeleitet. Der Nachfolger prüft den aktuellen Original-Spawn vor der ersten Eingabe und nach der RD-Kalibrierung erneut.

Das V3-Fenster lieferte zwei kumulative Gains von −.25 und einen Body-Returnfehler von 0.0001068115234375 Grad bei 38 Paarversuchen / 3 transienten Verwerfungen. Alle 3 Rollen und 2 Displays wurden normal geschlossen, 673 Dateien wiederhergestellt. Die neue private Baseline-Quittung referenziert die SHA-256-Werte von result.json, inventory.jsonl, join-registry.json und dem tatsächlichen nativen Manifest. Die Rohbelege wurden nicht verändert.

## Implementierung und Grenzen

preparation_policy.py ist ein reiner Controller ohne Prozesszugriff. Er nutzt RD und Route unverändert. native_roles fordert jetzt für jeden Aufruf ein neues Paar über die bereits bewährte V3-Akquisition an, auch innerhalb der normalen Sample-Drossel. Das Paar wird über Prozessidentität, Tick und Vanilla-Lebensschlüssel an den zugehörigen Server-Snapshot gebunden.

Vor der Kalibrierung werden beide Reader-Prozessidentitäten und die beiden serverseitigen Spieler-/Lebens-/Weltschlüssel verankert. Sie dürfen während des gesamten Ablaufs nicht neu verankert werden. Ein Rollenframe muss nach der aktuellen Leseanforderung begonnen haben, geordnete Zeitstempel besitzen, höchstens 0.2 s alt sein und genau beide Rollen enthalten. Lebendig/initialisiert/verbunden, unveränderte Identitäten und nicht rückläufige Native-Ticks sind zusätzliche Bedingungen.

Jede Eingabe erhält frische Zustände vor dem Aufruf, unmittelbar innerhalb des letzten Pre-Emission-Callbacks und nach der Freigabe. Für die Kalibrierung bleibt RD's eigene frische Doppelread-Baseline die letzte Zustandsbeobachtung vor Emission. Bei einer geplanten Route-Eingabe wird dieselbe Entscheidung gegen den neuen Zustand auf einer Kopie des vorherigen Route-Zustands nachgeprüft. Ein geänderter Korridor, Flugbeginn, Besitz oder Steuerbefehl bricht ab; der Controller wählt keinen günstigen Ersatz und wiederholt keine Eingabe.

Alle zurückgegebenen Frames und Eingabequittungen werden vor der ablehnenden Prüfung kopiert. Bereits gelesene Teilzustände sowie fehlgeschlagene Rohversuche bleiben in der unveränderten Finally-/Flush-Strecke erhalten. Bei einer späten Rückgabe bleibt auch der tatsächlich verspätete Zeitpunkt sichtbar.

| Grenze | Verhalten |
| --- | --- |
| Gemeinsames Policyfenster | Strikt unter 85 s ab bestehendem Inputfenster-Start; einschließlich RD, Route, Screenshots, Waffenwahl, Feuer und abschließender Host-/Query-Prüfung |
| Bestehendes Controllerfenster | 90-s-Eingabewache unverändert |
| Eingaben | Insgesamt höchstens 48 Versuche, einschließlich der 4 RD-Eingaben |
| Original-Route | 45 s; eine geplante Eingabe muss samt bestehender Überlaufreserve noch passen |
| Bouncer-Flug | 8 s, kein weiterer Bewegungsinput im erkannten Flug |
| Waffenwahl | 3 s; owned 64 und current/wanted 7 müssen rechtzeitig beobachtet sein |
| RD-ACK/Settling | Unverändert strikt 2 s und 42 Iterationen |
| Pair-Akquisition | Unverändert höchstens 8 Versuche, zusätzlicher 0.2-s-Rahmen nach Periodic, maximal 10 ms Pause |
| Gesamtleselimit | Unverändert 1024 Rohpaarversuche; kann einen langsamen Ablauf früher abbrechen |
| Normales Feuer | Genau eine 2-s-Fire-Bedieneingabe nach frischer Besitz-/Auswahlprüfung |

Die ursprünglichen Gain-, Rückkehr- und View-Rest-Schwellen bleiben unverändert. Als wiederholbare Konsistenzfehler gelten weiterhin ausschließlich die exakten Texte state changed during read und tick changed during read. Sonstige Reader-/Modul-/Lebens-/Hashfehler propagieren sofort. Erfolg an oder nach Route-, Flug-, Auswahl- oder Gesamtdeadline wird abgewiesen, auch wenn der gerade gelesene Zustand ansonsten passend ist.

## Verifikation

Die finalen 138 Privattests bestanden in 0.685 s. Darin sind die bisherigen 116 Tests und 22 neue gezielte Tests enthalten; ein bisheriger Wiringtest wurde ausdrücklich vom früheren Diagnostic-only-Aufruf auf den nun beauftragten Preparation-Aufruf angepasst. Die ursprünglichen eigenständigen RD-Tests bleiben erhalten.

Die 22 neuen Tests waren vor Implementierung rot. Sie führen echte RD-/Route-Funktionen sowie den tatsächlichen Controller-Aufruf, native_roles und die abschließende Zeitwache aus. Negative Fälle prüfen falschen Spawn, fehlgeschlagene Kalibrierung ohne Route, Lebens-/Prozesswechsel, gecachte/alte Frames, Drift direkt vor Emission, späte erfolgreiche Route-/Flug-/Waffenbeobachtungen, abgelaufene Gesamtfristen vor und nach Eingabe, 48 Actions, falsche Freigabe-/Emissionsbelege, doppelte Callbacks sowie sofortiges Ende nach Eingabefehlern. Ein weiterer Rot-/Grün-Beleg innerhalb desselben Tests prüft, dass eine erst bei 85 s zurückkehrende Feuerquittung erhalten und abgewiesen wird und die echte späte Zeit im Fehlerbericht steht.

Eine erste Cache-Test-Fixture zog ihren Zeitstempel nur vom bereits fortgeschrittenen Leseende ab und war dadurch noch nach der Anforderung. Die Fixture wurde auf einen tatsächlich vor der Anforderung liegenden Zeitpunkt korrigiert; die Frischegrenze wurde nicht gelockert. Ein zunächst falsch qualifizierter Unittest-Klassenname wurde vor dem gültigen Wiring-RED-Aufruf berichtigt und zählt nicht als fachlicher RED-Nachweis.

Alle 82 Dateien des alten V3-Pakets sind unverändert. Im Controller sind 32 Funktionen AST-identisch; nur main und native_roles unterscheiden sich. Der dokumentierte Normalisierer führt den gesamten neuen Controller nach Rücknahme der benannten Verkettungs-, Label-, Metadaten- und native_roles-Änderungen exakt auf die ursprünglichen V3-Bytes zurück. 17 Runtime-Dateien, insbesondere RD, Route, Plan, Transport, Backend und Lifecycle-/Restore-Helfer, sind bytegleich. Die 27 externen Runtime-Pins wurden unverändert übernommen und einmal gegen die tatsächlichen Dateien geprüft; ebenso die vorhandenen Fixture-Preflightpins. Der ursprüngliche transitive Close-Wrapper-/graceful-helper-Vertrag bleibt vor Native-Imports wirksam.

Die gezielten und vollständigen Logs, Diffs, Baseline und Preservation-Quittungen liegen unter evidence/route-*. Die endgültige Source-/Evidence-Closure wurde nach der letzten reinen README-Präzisierung nochmals vollständig geprüft. Kein C++-Build, kein nativer Start und keine Änderung an alten Paketen, Originalquellen oder Runtime-Fixture erfolgte. Repository-/Reader-Suiten außerhalb der 138 Privattests wurden nicht erneut ausgeführt.

## Nächster konkreter A1-Schritt

Nach einer erfolgreich nativ beobachteten Waffenroute folgt als separates Experiment normales Bewegen/Ausrichten auf den eigenen zweiten Spieler anhand frischer tatsächlicher Positionen, danach passive Original-Schuss-, Damage- und Lifecycle-Belege. Das aktuelle Paket richtet noch nicht auf einen Spieler aus und behauptet keinen Schuss-/Treffernachweis.

Die vorhandene Zwei-Spieler-Lifecycle-/Hookvorbereitung ist dafür nur ein Kandidat und besitzt keine native Freigabe. Ein instrumentiertes Fenster benötigt einen gesonderten Review und eine vergleichbare uninstrumentierte Kontrolle. Bestehende Damage-Drafts sehen vollständige Original-Byte-/TLS-/CurrentTick-/Lebensbindungen, einen bekannten fremden Inflictor, DMT_BULLET 4, den Original-Waffenpfad und tatsächliche Vorher-/Nachher-HP vor. Ein unbekannter Inflictor oder ein fire_requested-Feld reicht nicht.

Für einen gültigen ersten verarbeiteten Zustand muss zusätzlich dieselbe Server-Lebensgeneration von InitializePlayer-Abschluss bis zu einer definierten ersten vollständig verarbeiteten Grenze lückenlos beobachtet werden. INITIALIZED/APPLIEDACTION sind keine monotonen Erstzustandsmarker; SpawnClock-Gleichheit ordnet keine Unterphasen. Die vorhandene Analyse hat noch keinen hinreichenden Marker bewiesen. Spätere wiederholte Spawn-Treffer können über normales Feuer, normalen Deathmatch-Fire-Respawn und tatsächlich beobachtete unveränderte Spawnpositionen mit realer Sichtlinie untersucht werden. RespawnInPlace ist im betrachteten Pfad kooperativ; direkte Engine-Damage-Aufrufe, Teleports oder Zustandswrites sind kein Bestandteil dieses Wegs.

## Übergabe an Root

Root prüft dieses deaktivierte Paket unabhängig und erstellt erst danach eine eigene eingefrorene Kopie. Beim Umsetzen der Gates/Pfade müssen auch der eigene Controller-Runtimepin und der neue preparation_policy.py-Pin angepasst und erneut geprüft werden. Keine Aktivierung dieses Autorenpakets in-place. Root besitzt Scheduling, exklusives natives Fenster, vollständige Close-/Log-/Restore-Abnahme und Integration des Dokumentationscommits. Bis zum tatsächlichen nativen Nachweis bleibt die neue Vorbereitung NOT_RUN und A1 insgesamt nicht abgenommen.
