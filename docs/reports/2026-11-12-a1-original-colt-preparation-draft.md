# A1: deaktivierter Original-Start-Colt-Entwurf

## Ergebnis und Status

**READY FOR INDEPENDENT OFFLINE REVIEW.** Neuer privater Entwurf unter `/srv/tse-a1-colt-preparation-20261112`. Beide Runtimegates false. Keine nativen Starts, keine Spieleingabe, kein Build und keine Produktionsänderung durch diesen Worker. Root übernimmt nach unabhängigem Review eine eigene Freeze-Kopie und einen frischen vollständigen Preflight.

Isolierter Autorbranch `codex/20261112-a1-colt-preparation`, Basis `47a819ab9b48244847fd43f401c7902c1b059d27`. Ausschließlich Plan und dieser Bericht liegen im Git-Worktree; private Runtimequellen, Originalbyteguards und Rohbelege bleiben außerhalb des Repositorys.

## Warum die Vorbereitung geändert wird

Der bisherige A1-Waffenweg endete im abgeschlossenen V5-Fenster153533 an der unveränderten Flight-Deadline. Die tatsächliche Flugbahn erreichte die geplante Minigun nicht. Der Originalauftrag verlangt wiederholten echten Schaden ab dem ersten verarbeiteten Respawnzustand, aber keinen Bouncer- oder Minigunpickup als zwingende Vorbereitung. Die Original-Startwaffe erlaubt einen deutlich engeren normalen Kontrollschuss.

Die abgeschlossene Ursachenanalyse unter `/srv/tse-a1-v5-flight-deadline-analysis-20261112` bleibt unverändert. Der neue Entwurf ist kein weiterer Route-/Timeoutversuch und erweitert keine bisherige Deadline.

## Konkreter neuer Ablauf

Die bestehende normale Start-/Identitäts-/World-/Close-/Restorehülle bleibt erhalten. Der Vanilla-Originalclient ist Schütze, weil exakt dieser Client die unveränderte RD-Kalibrierung durchläuft. Der zweite Originalclient botA ist ausschließlich Ziel und erhält keine neue Eingabe. Die Rollenbezeichnung ersetzt keine spätere Bot-AI-Abnahme.

Nach RD wird Pitch durch eigene normale +12/−12-Pixel-Gegenimpulse bestätigt. Server-received, Client-local und Client-received müssen übereinstimmen; die tatsächliche Original-Viewpoint-Antwort muss dazu passen. Danach richten begrenzte Einzelachsenimpulse mit maximal 12 Pixeln auf den tatsächlichen Original-Zielmittelpunkt aus. Ein einziges Fire-Halten von 0,1 s wird erst nach der letzten frischen Ziel-/Pending-/Budgetprüfung unmittelbar vor XTest zugelassen. Es gibt keine Eingabewiederholung.

Die Feuergeometrie verwendet tatsächlichen Viewpoint, Animator-EyesYOffset, aktuelle Colt-Handle-/Fire-/FOV-Parameter und Original-Standing-Zielzentrum. Keine angenommene Fuß-/Augenhöhe und kein unbestätigt übernommener Pitchgain. Der neue Reader ist explizit optional; alle zusätzlichen Felder liegen im bestehenden Doppelpass. Geladene Originalfunktionen werden mit 14 tatsächlichen bytegebundenen Guards und ausschließlich ihren dokumentierten Relokationen geprüft. Standardreader und bisherige Yawdiagnose bleiben identisch.

## Reichweite, Sicht und Auswertung

Die früheren tatsächlich beobachteten Startpositionen lagen ungefähr 129 Einheiten auseinander. Das ist **keine neue Beobachtung und kein LOS-Beleg**. Im neuen Lauf werden Posen und Mündung neu gelesen. Die statische Original-Coltreichweite≤500 besagt nur, dass der Zielpunkt nicht außerhalb dieser Reichweite liegt. Der Entwurf besitzt keinen Raycast und keine Hindernisumgehung.

Nach dem einen Firehold folgen nur frische passive Doppelreads bis zur festen Deadline zwei Sekunden nach dem tatsächlichen Requestende. Beidseitig übereinstimmende Clipabnahme **und** tatsächlicher Ziel-HP-Verlust sind zwingend für `PREPARATION_COMPLETED_REVIEW_REQUIRED`. Fehlt ein Beleg, lautet das Ergebnis FAIL; LOS bleibt ungeklärt. Keine zusätzliche Bewegung, kein zweiter Firehold, kein automatischer Retry. Ein tatsächlicher FAIL muss danach ursächlich analysiert werden.

Auch beim begrenzten positiven Ergebnis bleiben `qualified`, `input_once_proven`, `actual_shot_proven`, `foreign_hit_proven`, `first_processed_state_proven` und `line_of_sight_proven` false. Passive Clip-/HP-Werte sind keine vollständige Original-Bullet-/Inflictor-/Lifecycle-Provenienz.

## Erhaltene Grenzen

Controller 90 s / Policy strikt vor 85 s / CPU 75% / bestehende RAM- und Diskgrenzen bleiben erhalten. Alle 48 erlaubten Aktionen zählen gemeinsam mit RD und Pitch. Die zusätzliche Aimgrenze 20 s verlängert nichts. ACK und Effekte müssen jeweils strikt vor 2 s erfolgreich sein. Jede entscheidende Probe muss neu angefordert und höchstens 0,2 s alt sein. Der vorhandene Readretry betrifft ausschließlich explizite transiente Konsistenzfehler, niemals Eingaben.

Langsame Endpoint-/Focus-/Transportprüfungen stehen vor dem abschließenden aktuellen Zustands-/Budgetcheck. Tatsächliche Requestzeit, Teilfehler und Releases bleiben erhalten. Safe Release wird auch nach Deadlinefehlern versucht. Fire-Screenshots erfolgen erst nach Release. Normales Schließen aller Rollen, geschlossene Logs und vollständige Restaurierung sind unverändert.

## Tatsächliche Prüfung

- **223/223 private Tests**, 2,674 s. Enthält erhaltene V5-Regressionen und 36 neue tatsächliche Reader-/Geometrie-/Controller-/Endpoint-/Transportfälle.
- **32/32 bestehende Readertests** gegen den neuen privaten Reader, 0,059 s; ausschließlich synthetische Prozessdateien.
- **50 Schutz-/Lifecyclefunktionen AST-identisch**, neun wesentliche Dateien bytegleich, darunter RD und die bestehende Close-/Restore-/Hosthülle.
- **14 Originalbyteguards** einschließlich Relokationen gegen die tatsächlichen hashgepinnten Originaldateien geprüft.
- **172 Dateien des V5-Autorenpakets, 172 des Root-Freeze und 684 des ursprünglichen CPU-FAILs** erneut exakt gleich geprüft; das Resultat153533 bleibt ebenfalls unverändert.
- Finale Closure: **48 Runtimepins, 57 eigene Quellen/Dokumente, 171 Evidenzdateien und 12 bestehende Fixture-Preflightpins** geprüft.

RED→GREEN deckt neue tatsächliche APIs, reale Original-FX/FY-Pushreihenfolge, Waffen-/Animatorgenerationen und lineare Viewpointverschiebung ab. Verzögerte echte Transportguards, positive Proben nach Deadline, fehlender ACK/Clip/HP-Beleg und negative Ziel-HP werden ohne weiteren Input behandelt. Nur die vorhandenen Tests des aktuellen Controlleraufrufs wurden auf den neuen CP-Einstieg retargetet; historische Route-/Flight-Fälle prüfen weiter unveränderte alte Funktionen. Kein Test ist ein nativer Spielnachweis.

## Reproduzierbare Pins

| Artefakt im privaten Paket | SHA256 |
|---|---|
| `source-manifest.json` | `b3595baafb60e51364fa6db69fcb8356cfc860c2655a5f9f51cd62481e6ed8fe` |
| `run_dual.py` | `f5495b8118a7f9b199e2e735c0ad26bac07f33892a61aaaf4004cd78f5f7b68c` |
| `colt_preparation.py` | `46bccee495c276166fcc9f48c7041d5aec8e9a39e9694eabc76e08b74fc9dc56` |
| `tools/retail_inventory_readonly.py` | `a5a16d49ed2ce2af0cb51b0b0cc3bc1d5597ee689766557145f6c4f1707c19fd` |
| `evidence/normalized-delta.json` | `929017ce85f71ead628e0ddaadc9d18a5ed0b297308e2e6827ce2cff196d8b5b` |
| `evidence/final-colt-regression.log` | `e50937aeed83e64949576620ae5f7898358d99105adf89cf57846bfe847c3c54` |
| `evidence/final-reader-regression.log` | `4c0444a931e891ee881ac63591551dc680a5b6f30a6412440d61c21b4c1bd085` |

Der vollständige Einstieg liegt in `HANDOFF.md`, `HANDOFF.json`, `SPEC.md`, `ORIGINAL-BINDING.md` und `FINAL-VERIFY.json`. Der private normalisierte Diff ist exakt gepinnt. Kein Runtimegate ist durch diese Dokumentation freigegeben.

## Für die eigentliche A1-Abnahme noch offen

Nach einer später erfolgreichen Preparation braucht es wiederholte tatsächliche Fremdschadentreffer ab dem ersten verarbeiteten Respawnzustand, Bot/Vanilla sowie Mapwechsel/Neustart. Die vorhandenen Damage-Dual-/Lifecycle-Entwürfe sind lediglich Kandidaten für passive Original-Fire/Bullet/Damage- und InitPlayer/PostMoving-Belege, noch keine native Freigabe. Der Lifecycle-Nachweis muss die tatsächliche Prozess-/Entity-/Lebens-/Worldgeneration, lückenlose Ereignisfolge und einen erwarteten Trefferdenominator binden. Bereits geprüfte normale Inputs, frische Doppelreads, Request/Release-Quittungen und vollständige normale Close-/Restorehülle können wiederverwendet werden. Normales Feuer/Respawn und tatsächlich beobachtete Spawnpositionen bleiben erforderlich; direkte Engine-Damage-Aufrufe und Zustandswrites sind ausgeschlossen.
