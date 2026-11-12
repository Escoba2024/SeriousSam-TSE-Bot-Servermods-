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

## Privates Testpaket V1 (Reviewbasis)

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

## Review-Nachtrag: V2 mit zwei begrenzten Korrekturen

Root hat den Reader-Commit unverändert bei `ddd65b7` integriert. Die unabhängige Prüfung fand zwei zusätzliche Fehler ausschließlich im privaten Controller. Für jede spätere Freigabe ist jetzt `/srv/tse-a1-input-diagnostics-completion-v2-20261112` maßgeblich; das alte V1-Paket und die Frozen-Basen bleiben unverändert.

**Transitive Close-Abhängigkeit:** Der ursprüngliche Helfer `/srv/tse-development-live-20261107/graceful-stop-bot.py` ist nun Teil der Runtime-Closure mit SHA-256 `9e572c15dd6191c1ca6022f3c713037c8c143180182954c59b8b587afb26840f`. Der ebenfalls gepinnte Wrapper `/srv/tse-cecil-rules-20261107/.codex/evidence/cecil_close_window.py` behält SHA-256 `68edd45db16eae91c32be99662d530c51222f68e0eaaa071ccb40ff355483011`. Vor nativen Imports, Backend-Erzeugung oder Starts werden beide Datei-Hashes und der AST-Vertrag des Wrappers geprüft: genau der erwartete literale `ORIGINAL=Path(...)`-Pfad und `ORIGINAL_SHA`. Die Prüfung importiert oder führt keinen der Helfer aus. Fehlende Pins, Dateidrift, abweichende/dynamische Literale und doppelte Vertragszuweisungen werden zurückgewiesen.

**Lokale Zwei-Sekunden-Grenze:** `settled()` und `acknowledged()` konnten zuvor einen erfolgreichen Datenzustand zurückgeben, bevor sie die eigene Deadline überprüften. Zwei neue Regressionstests reproduzierten vier solche Fälle: ansonsten gültige, frisch gelesene Daten bei genau 2.00 und nach 2.01 Sekunden. V2 prüft die lokale Deadline jetzt unmittelbar vor dem erfolgreichen Rückweg. Die zu späte Beobachtung bleibt im Receipt; die Policy bricht ab, ohne einen weiteren Impuls zu senden oder eine erfolgreiche Quittung zu markieren. Die bereits vorhandene strikte Grenze `< deadline` bleibt bestehen.

Beide Korrekturen wurden RED→GREEN geprüft. Die vollständige kleine private Suite besteht nun mit **103 Tests** (95 bisherige plus zwei Deadline- und sechs Close-Closure-Tests). Die Repo-Reader-Dateien wurden nicht geändert; die bereits geprüften 262 Python-/32 Reader-Tests wurden unter dem exklusiven A4-Fenster nicht unnötig wiederholt. Kein nativer Start oder Compile erfolgte durch diesen Worker.

`evidence/v2-normalized-delta.json` belegt: Nach Entfernen genau der zwei neuen Deadline-Prüfungen sowie der Close-Vertragsprüfung und der eigenen V2-Labels entspricht der Controller-/Policy-Quelltext exakt V1. Alle 60 Dateien des alten Pakets und alle privaten Toolkopien blieben unverändert; sämtliche bisherigen externen Abhängigkeitspins wurden übernommen. V2 pinnt **47 Runtime-Abhängigkeiten und 38 eigene Quell-/Test-/Konfigurationsdateien**. Die 85/90-Sekunden-Limits, Hostbudgets, Transport, Restore, Gain-Grenzen und begrenzte Vier-Schritt-Folge sind unverändert.

Beide Review-Gates bleiben `False`, ebenso `runtime_performed`. Der V2-Runplan bleibt: unabhängig prüfen, separate Root-Frozen-Kopie erstellen, erst danach ein exklusives begrenztes Diagnosefenster zulassen. A1 und die Ursache des alten Faktors zwei bleiben offen.

## Review-Nachtrag: V3 mit begrenzter passiver Neuerfassung

### Tatsächlicher V2-Abbruch

Der Root-Lauf `a1-input-diagnostics-completion-v2-20261112-084124` blieb **FAIL**. Genau `look_right` und `forward` wurden ausgeführt; ihre normalen Input-Quittungen waren PASS mit 0.148766 bzw. 0.179711 Sekunden bis zur Freigabe. Die letzten zwei von 16 Paar-Leseversuchen meldeten `EvidenceError('state changed during read')`. Anschließend fehlte das neu angeforderte Paar; der bestehende Frische-Guard brach vor einer linken Eingabe ab.

Die gültigen Paar-Lesungen benötigten im Median etwa 9.57 ms; der bisherige Zähler für erfolgreiche Reader-Zeit lag bei 0.147721 Sekunden. Die drei Spielprozesse wurden normal geschlossen, die geschlossenen Logs akzeptiert und die Dateien wiederhergestellt. Diese Angaben stammen aus dem unveränderten privaten Resultat und den Raw-Receipts; die V3-Arbeit hat keinen nativen Versuch ausgeführt. Insbesondere ist daraus weder die Ursache der früheren doppelten Gegenrotation noch ein erfolgreicher A1-Test abzuleiten.

### Enger V3-Delta

Neue deaktivierte Kopie: `/srv/tse-a1-input-diagnostics-completion-v3-20261112`. Geprüfte Basis ist das V2-Manifest `1df916e64fb2c2575929195e83d52bd258aa3fe931cf95ddd42d5694437d1faa`.

Nur zwei private Controllerfunktionen ändern Verhalten:

- `sample()` verwirft ausschließlich die exakten EvidenceError-Texte `state changed during read` und `tick changed during read`. Andere Fehler werden sofort weitergereicht. Der bestehende finally-Pfad schreibt zuvor jeden fehlgeschlagenen oder partiellen Raw-Versuch.
- `native_rotation_pair()` erlaubt höchstens acht Paar-Leseversuche pro Anforderung einschließlich eines etwaigen Reads im unveränderten `periodic()`. Nach dessen Rückkehr gilt zusätzlich eine strikte Erfassungsdeadline von 0.2 Sekunden, mit höchstens 10 ms Pause zwischen transienten Fehlschlägen. Ein synchroner Read ist nicht präemptiv abbrechbar; an oder nach der Deadline gelieferte Daten werden gespeichert und vor der Rückgabe abgelehnt.

Ein Paar muss neu zur jeweiligen Anforderung hinzugekommen sein, seinen Leseanfang ab dem Anforderungszeitpunkt haben und weiterhin höchstens 0.2 Sekunden alt sein. Das gilt auch bei gleichbleibendem Testuhrwert. Ein erfolgreich gelesener, aber ungültiger Datensatz führt sofort zum Abbruch; es wird nicht nach günstigeren Werten gesucht. Eingaben werden niemals wiederholt. Die begrenzte Vier-Schritt-Folge, alle Gain-/View-/Return-Prüfungen, die lokalen strikten Zwei-Sekunden-Grenzen sowie die 85/90-Sekunden-Limits bleiben unverändert.

### Reproduzierbare Offline-Prüfung

Die 13 neuen Regressionstests führen die tatsächlichen verschachtelten Funktionen `sample()`, `periodic()` und `native_rotation_pair()` aus. Nur native Reader, Uhr und Hostgrenzen werden durch kontrollierte In-Memory-Fixtures ersetzt. Gegen unveränderten V2-Code waren alle 13 Fälle RED, einschließlich 19 negativer Subfälle; nach dem Fix sind sie GREEN.

Geprüft sind beide transienten Fehlertypen bis zum ersten neuen Paar, Erfolg beim achten Versuch, Ausschluss eines neunten Versuchs, ausgelastete und stehenbleibende Uhr, die strikte Deadline einschließlich ansonsten gültiger Erfolge genau an und nach ihr, alter Cache und vor der Anforderung gestartete Daten, sofortige fatale Fehler mit Teil-Snapshot-Erhalt sowie echte Policy-Integration nach rechts + forward. Erschöpfung und ein anschließend beobachteter Life-Wechsel stoppen dabei vor einer linken Eingabe.

| Prüfung | Beleg |
|---|---|
| Unveränderte private Basis nach Umstellung eigener Manifestpfade | 103 Tests / 0.167 s, PASS |
| Neue Regressionen gegen V2 | 13 Tests, 19 negative Subfälle, RED |
| Neue Fälle und bestehende Controllerprüfungen nach Fix | 21 Tests / 0.319 s, PASS |
| Gesamte private Offline-Suite | **116 Tests / 0.456 s, PASS** |
| Erhalt der V2-Kopie | **Alle 69 Dateien bytegleich; Dateimenge unverändert** |
| Geschützte Lifecycle-/Guard-Funktionen | **22 AST-identisch**, darunter Input, periodic, Close und Restore |
| Externe Runtime-Pins | **27 unverändert übernommen** |
| Repo-Reader, Rotation-Policy und geschützte Transport-/Restore-Dateien | unverändert |

Der erste Baseline-Aufruf der neuen Kopie schlug ausschließlich wegen noch auf V2 gerichteter eigener Manifestpfade in `test_wiring` fehl. Nach deren begrenzter Umstellung bestanden die 103 bisherigen Tests vor jeder Änderung am Laufzeitcode. Beide Baseline-Logs bleiben erhalten. Repository-Tests und Reader-Tests wurden nicht erneut breit ausgeführt; der Reader ist bytegleich. Es gab keinen Compile und keine Runtime-Änderung.

`evidence/v3-normalized-delta.json` hat SHA-256 `868a89e3f1ae1fa287fc86a258c5b1e08699a3ae752ceca10f8e704729da1641`. Nach Rücknahme genau der zwei Funktionsänderungen und Normalisierung der zwei V3-Labels entspricht der gesamte Controllertext exakt V2. Der private Diff, RED/GREEN-Logs, Quellen- und Manifestpins sowie der finale Paketbeleg bleiben im V3-Verzeichnis.

Beide Gates und `runtime_performed` bleiben False. Root übernimmt unabhängiges Review, einen separaten Freeze und gegebenenfalls ein einziges exklusives natives Diagnosefenster. Der alte FAIL bleibt unverändert; diese Änderung ist keine A1-Abnahme.
