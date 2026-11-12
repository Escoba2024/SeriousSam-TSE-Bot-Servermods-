# A1: passive Diagnose der normalen Rotationseingabe

## Ergebnis und Abgrenzung

Der optionale Diagnosemodus des Retail-Readers und ein separat gepinntes, deaktiviertes privates Testpaket sind implementiert und offline geprüft. Der Standardmodus liest dieselben Adressen in derselben Reihenfolge und erzeugt dieselben Ausgabebytes wie zuvor. Es wurden keine Spiele gestartet, Builds ausgeführt, Hooks eingebaut, Prozessspeicher geschrieben oder öffentliche Server geändert.

A1 ist damit **nicht abgenommen**. Die Ursache der früheren doppelten Gegenrotation ist noch nicht nachgewiesen. Der neue Controller soll genau die bisher fehlenden Eingabe- und View-Quittungen erfassen. Er endet nach dem begrenzten Kalibrierungspaar oder beim ersten Fehler. Er setzt weder Pickup-Route noch Fire fort und behauptet keinen Schuss, Fremdtreffer, ersten verarbeiteten Zustand oder eindeutig einmaligen Eingabeverbrauch.

Basis ist `b6b776ddbc761ee96049e6626edd5af4895cb3af`, Arbeitsbranch `codex/20261112-a1-input-diagnostics`. Die ursprünglichen Worktrees, Frozen-Controller und fehlgeschlagenen Messungen blieben erhalten.

## Belegter Ausgangsfehler

Die unveränderte private Messung `a1-shooter-calibration-20261112-045050` endete mit `opposite normal look does not reproduce body response`. Die drei stabilen Server-Endpunkte lagen bei:

| Punkt | Zeit ab Fensterstart | Game-Tick | Body-Yaw |
|---|---:|---:|---:|
| vor rechter Eingabe | 0.108738 s | 8.500014 | -135.0000457763672° |
| nach rechter Eingabe und normalem Vorwärtsschritt | 1.591990 s | 9.950020 | -138.0001220703125° |
| nach linker Eingabe und normalem Vorwärtsschritt | 2.926492 s | 11.300025 | -132.0001983642578° |

Das entspricht ungefähr -0.25000636°/Pixel und -0.49999364°/Pixel, einer Gain-Differenz von 0.24998728°/Pixel und einem Rückkehrfehler von 2.99984741°. Die unveränderten Grenzen sind 0.05°/Pixel bzw. 0.75°. Stabile gleiche Life-/Entity-Endpunkte und ruhende Körper belegen den Fehler. Sie unterscheiden lokalen Eingabeverbrauch, Netzwerkquittung und Übertragung des relativen Blickwinkels auf den Körper nicht. Der exakte Faktor zwei ist aus diesen alten Daten daher nicht rekonstruierbar.

Zusätzlich schrieb der alte Shooter-Code sein Kalibrierungs-Receipt erst **nach** der ablehnenden Prüfung. Ein Regressionstest mit genau diesen Endpunktwinkeln reproduzierte das leere Receipt. Die private Kopie speichert es jetzt vor derselben unveränderten Prüfung.

Private Originalbelege:

- `inventory.jsonl`: SHA-256 `991ce7e9a922a167a4833e796b00d9924ba8a6d9a5dd2dbe85ce372908a8f119`.
- `result.json`: SHA-256 `90141dde77ddbd872eaa126e99527664debbe9a4ac3174357fbebf79f6ce9528`.
- Ursprünglicher Frozen-Controller: SHA-256 `da817596ba4d2d1f223cdcf725e7674940041b2562a9a0f310e366769d8d6479`.

## Reader-Erweiterung

`tools/retail_inventory_readonly.py` erhält ausschließlich eine explizite API-Option `rotation_diagnostics=False`. Bei `True` kommen pro vorhandenem Spieler vier Skalarwerte unter `rotation_diagnostic` hinzu:

| Feld | Offset im CPlayer | Bedeutung |
|---|---:|---|
| `last_action_yaw_deg` | +0xCA0 | zuletzt verarbeiteter kumulativer Action-Yaw |
| `local_action_yaw_deg` | +0xCC4 | lokal kumulierter Eingabe-Yaw |
| `relative_view_yaw_deg` | +0x344 | relativer View-Yaw, getrennt vom Body-Yaw |
| `player_flags` | +0x380 | unveränderte rohe PlayerFlags |

Die Floatwerte müssen endlich sein. Alle vier Werte gehen in die bestehende zweite identische Leseprüfung ein. PID/Startzeit, eigenes Fixture, Moduldateien, Mapping und ursprüngliche Byteguards bleiben verbindlich. Der Speicherdescriptor bleibt `O_RDONLY`. Implizite wahrheitsartige Moduswerte werden vor jedem Zugriff zurückgewiesen. Die CLI und normale Aufrufer bleiben unverändert.

Zusätzliche opt-in Byteguards wurden gegen die tatsächliche Originaldatei geprüft. EntitiesMP.dll hat SHA-256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`. Die Tabelle nennt RVAs, keine Dateioffsets:

| RVA | Erwartete Bytes | Bezug |
|---:|---|---|
| 0xEE956 | `d8a3a00c0000` | Differenz zum letzten Action-Yaw +0xCA0 |
| 0xEEA2F | `898ba00c0000` | Speichern des letzten Action-Yaw +0xCA0 |
| 0xF03D7 | `d98644030000` | relativen View-Yaw +0x344 laden |
| 0xF049A | `89be44030000` | relativen View-Yaw +0x344 zurücksetzen |
| 0xE3CED | `d987c40c0000` | lokalen kumulativen Yaw +0xCC4 laden |
| 0xE3CF6 | `8d87c40c0000` | Adresse des lokalen Yaw +0xCC4 |
| 0xEE91E | `8b8380030000` | PlayerFlags +0x380 lesen |

Der vorhandene APPLIEDACTION-Flag ist weiterhin kein eindeutiger Zustandscounter; siehe `2026-11-12-a1-first-processed-state-boundary.md`. Diese Erweiterung behauptet aus dem Flag keinen First-State-Nachweis.

## Privates Testpaket

Das neue Paket liegt unter `/srv/tse-a1-input-diagnostics-completion-20261112`. `run_dual.RUNTIME_REVIEWED` und `source-manifest.json.runtime_reviewed` sind beide `False`; `runtime_performed` ist ebenfalls `False`.

Der Controller verwendet zwei getrennt gepinnte Reader für Server und eigenen Vanilla-Prozess. Vor jedem Impuls, während der Verarbeitung, vor dem Vorwärtsschritt und nach dem Abklingen werden Zeitstempel, Life-/Process-Identität, Body-Yaw, beide View-Yaws und die kumulativen Eingabewerte aufgezeichnet. Eine zusätzliche frische Prüfung liegt innerhalb der vorhandenen Eingabefunktion unmittelbar vor der Emission. Die tatsächlichen Request-/Hold-/Release-Zeiten bleiben auch bei Fehlern im Receipt. Eine bestätigte X-Anfrage wird nicht mit verarbeitetem Spieleingang gleichgesetzt.

Server-Last-Action, Vanilla-Local-Action und Vanilla-Last-Action müssen übereinstimmen und über mindestens 0.1 fortgeschrittene native Sekunden stabil sein. Erst anschließend ist der normale Vorwärtsschritt zulässig. Vor dem nächsten Look müssen beide relativen View-Yaws ruhen. Fehlende Quittung, umgekehrte oder zusätzliche kumulative Bewegung, abweichende Gegengains, Rest-View, veraltete Samples oder Identitätswechsel stoppen weitere Eingaben. Es gibt keinen Wiederholungsversuch und keine Auswahl günstiger Samples.

Jede Policy-Beobachtung wird vor ihrer Prüfung gespeichert. `rotation-read-attempts.jsonl` wird im `finally`-Block geschrieben und behält bereits gelesene Teil-Snapshots, wenn der zweite Reader oder die Spielerzuordnung scheitert. `rotation-pairs.jsonl` enthält zusätzlich die während der Eingabe gelesenen Paare. Die Grenzen sind 256 Policy-Beobachtungen, 42 Beobachtungen und zwei Sekunden je Quittungs-/Ruhephase sowie 1024 rohe Leseversuche. Die Policy bleibt innerhalb von 85 Sekunden, der Controller innerhalb seines bisherigen 90-Sekunden-Limits. Ein vollständiges 90-Sekunden-Fenster wird nicht behauptet.

Gain-Bereich [-0.5,-0.02], Gegengain-Differenz 0.05 und Rückkehrtoleranz 0.75 bleiben unverändert. Die zusätzliche Konsistenzprüfung von 0.001° verschärft die Ablehnung inkonsistenter Action-/View-Beobachtungen. Normale XTest-Eingabe, Hostbudgets, exklusives Lock, Netzwerkisolation, Identitätswächter, normales Schließen, Archivierung geschlossener Logs und exakte Wiederherstellung bleiben bestehen. 17 kritische Lifecycle-Funktionen sind AST-identisch; sechs Transport-/Guard-/Restore-Dateien sind bytegleich zur geprüften Frozen-Basis. Im Backend wurde ausschließlich der Pfad des unverändert kopierten Query-Helfers auf das eigene Paket umgestellt.

## Offline-Prüfung

| Prüfung | Ergebnis |
|---|---|
| Native Gegenrotationswerte gegen alten Receipt-Code | RED: Receipt fehlte; danach GREEN mit weiterhin abgelehntem Gain |
| Neue optionale Reader- und Negativfälle | zuerst RED; anschließend 32 Reader-Tests einschließlich bestehender Fälle bestanden |
| Standardmodus-Golden | gleiche Ausgabebytes und exakt dieselbe Folge von 121 Lesezugriffen |
| Gezielte private Diagnosefälle | fehlende/verspätete Quittung, Teilinkremente, doppelte Antwort, Vanilla-View-Rest, frische Baseline, Eingabefehler, eingefrorene Zeit, Teil-Snapshot-Erhalt geprüft |
| Gesamte private Offline-Suite | **95 Tests bestanden** |
| Repository-Python-Suite ohne Compiler-Modul | **262 Tests bestanden** |
| Original-Byteguards | sieben von sieben direkt gegen die gepinnte Original-DLL bestätigt |
| Externe ursprüngliche Runtime-Abhängigkeiten und Fixture-Pins | vor Umkopieren geprüft; keine unerklärte Abweichung |

Der erste breite Python-Aufruf hatte ein falsches Arbeitsverzeichnis und dadurch einen Importfehler in `test_parse_cecil_navmesh`. Nach Korrektur von Arbeitsverzeichnis und Importpfad bestanden alle 262 Tests; beide Logs bleiben erhalten. `test_arena_combat.py` wurde ausdrücklich ausgelassen, weil es g++ startet und Compiles außerhalb dieses Auftrags liegen. Das ist kein erfolgreicher neuer Build- oder Combat-Test.

Die finalen Logs und Hashes liegen ausschließlich im privaten Paket. Das Manifest pinnt 46 Runtime-Abhängigkeiten und 37 eigene Quell-/Test-/Konfigurationsdateien. `evidence/lifecycle-diff-review.json` dokumentiert die unveränderten Lifecycle-Funktionen; `README.md` enthält den konkreten Root-Runplan.

## Nächster Schritt

Root prüft die tatsächliche Änderung und die Pins unabhängig, erstellt gegebenenfalls eine separate Frozen-Kopie mit dokumentierter Gate-Umstellung und führt erst danach ein einziges begrenztes Diagnosefenster aus. Die zusätzliche Reader-Last und die native Quittungsfolge sind noch nicht gemessen. Eine neue Messung muss gemeinsam mit normalem Shutdown, geschlossenen Logs und exakter Wiederherstellung ausgewertet werden. Erst daraus folgt gegebenenfalls eine Eingabekorrektur. Diese Offline-Arbeit rechtfertigt weder eine Toleranzänderung noch eine XTest-Änderung oder A1-Erfolgsaussage.
