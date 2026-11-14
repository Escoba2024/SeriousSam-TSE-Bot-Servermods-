# A1: abgewiesene Emissionsmetadaten erhalten

Der erste geschlossene passive Original-Lauf bleibt FAIL. Beim ersten+12-Impuls
scheiterte der vorhandene Counter-/Clockguard. Seine lokale Row wurde vor dem
Anhängen verworfen; die exakten Counterwerte und die verletzte Teilbedingung
sind deshalb unbekannt. Der Servertrace enthält keine XTEST-Beobachtung, aber
die Ausnahme verhinderte auch den nachfolgenden Transport-XSync. Daraus folgt
kein Beweis, dass kein Request gepuffert war. Weder Cold-Initialisierung noch
ein Clockfehler ist als Ursache nachgewiesen.

Der enge Fix reserviert unmittelbar vor dem bisherigen Counter-/Nativepfad
einen von maximal96 Speicherplätzen. Dieselbe lokale Row wird mit den ohnehin
gelesenen Werten ergänzt. `native_invoked` kennzeichnet den begonnenen Aufruf;
`validation_status` trennt RESERVED, ACCEPTED und REJECTED. ACCEPTED bedeutet
ausschließlich, dass der unveränderte Metadatenguard angenommen hat; es ist
kein Input-, Serververarbeitungs-, ACK- oder Gainbeweis. Eine Nativeexception
bleibt auch bei anschließendem Metadatenfehler die originale Ausnahme.

Ein Fehler schon beim ersten Counter lässt den reservierten Versuch ausdrücklich
ohne Nativeaufruf und ohne erfundene Nachherwerte zurück. Weitere Stufen werden
als after_counter, finished_clock oder validation erfasst. Versuch97 wird vor
Counter und Nativepfad verhindert; Root hat dies als Präzisierung des bestehenden
96er-Budgets festgelegt. Die gültige Emissionsliste und deren kompletter
`record_emission`-AST einschließlich`b-a>4` sind unverändert.

Keine zusätzliche Native-/Clockabfrage, kein Warmup und keine Datei-I/O im
Inputpfad. Bei Cleanup wird zusätzlich
`controller-emission-attempts.json` exklusiv mit0600 geschrieben. Beide
Journalversuche laufen unabhängig; I/O-Fehler verhindern die eigene
Childbereinigung nicht. CP/ACK/Gain/EPS,350ms-Input-/Releasegrenze, Frida und
15s-/3s-/5s-Lifecyclegrenzen bleiben unverändert. Produktions-Gameplay und
öffentliche Runtime wurden nicht berührt.

## Offlinebelege und Paket

14neue Fälle plus29bestehende Fälle:43/43PASS,0Skips,2,443s. Nur reine
Fake-C-/Dateisystem-/Quellen-/Pakettests; keine Xlib-CDLL, Displays, Eingaben,
Spielprozesse, Compiler oder Frida-Attachs. Die Tests prüfen unter anderem die
unverändert rote6er-Span, exakte4er/5er-Grenze, Clockumkehr, fehlgeschlagene erste
und zweite Counterreads, unveränderte gültige Rows, Nativeexception-Vorrang,
Budget97 und Cleanup trotz beider Journal-I/O-Fehler.

Vor Implementierung reproduzierten die ersten8Fälle das Defizit. Eine zunächst
zu kurze Fakecounterfolge verursachte einen Fixture-StopIteration statt des
Budgetbefunds; vor Implementierung korrigiert, danach8echte REDs, darunter
97tatsächliche Fakecalls statt96. Die zwei Builderfälle waren anschließend
RED→GREEN. Zwei bestehende Proxytestdoubles fehlten die neue Reservierung;
sie nutzen jetzt den echten Recorder, ohne Assertions zu lockern.

Die unabhängige Prüfung von`1d6e991` fand anschließend IMPORTANT: Der neue
Reservierungsguard blockierte bei stickyObserverfehler auch den sichernden
Keyup vor dem Nativecall. Der authentische Regressionstest extrahiert die
unveränderten tatsächlichen action_step-/Endpoint-/Transport-event-Methoden
aus dem qualifizierten Parent und ersetzt nur externe Prozess-/Displaychecks
und C-Funktionen. Nach tatsächlichem Fake-C-Forwarddown und Counterreject fehlte
der Finally-Keyup (RED). Ausschließlich `self.failed` wurde aus
`reserve_attempt` entfernt. Danach laufen Down und Up jeweils genau einmal,
beide abgewiesenen Metadatenversuche bleiben erhalten; das Ergebnis bleibt FAIL
und `before_input` blockiert jede neue Eingabephase sticky. Ein anfänglicher
Testaufbaufehler durch Import eines ausschließlich privaten Moduls wurde vor
diesem RED durch die reine AST-Extraktion korrigiert.

Root begrenzte diese Änderung ausdrücklich auf den festen InputScope: maximal48
Aktionen, davon höchstens2Forwardaktionen, somit höchstens50Nativecalls. Die
97er-Releasekante ist darin nicht erreichbar; closed/max96 bleiben unverändert.
Keine Paarreservierung, zusätzlichen Eingaben oder generalisierte Refaktoren.

Reproduktion ab Repository-`tools/`:

```sh
python3 -B -m unittest test_a1_passive_attempt_journal test_a1_passive_xrecord test_a1_passive_xrecord_worker test_a1_passive_xrecord_evidence test_prepare_a1_passive_xrecord -v
python3 -B prepare_a1_passive_attempt_journal.py --destination /NEUER/PRIVATER/PFAD
```

Privater deaktivierter Fork:
`/srv/tse-a1-passive-attempt-release-safe-disabled-20261114`.
ManifestSHA256`f1cbd265f9b5ade97b8ec27748370b523f877524a6302118bf74fad3e8b18b18`.
Frisch geprüft:77Runtime-,71Diagnostik- und14Collectorpins.
Quelle`a1_passive_xrecord.py`SHA256
`8f3aaad57a5e5f0b6c95a4d60d5656a4e906f71c0d8708bfd180f1ca1198859e`.
Private OfflinequittungSHA256
`ef7fd0be7f4a06710cfe378e456130ce98da3e73483d9bb78beb1c00b28d17df`.
Das alte deaktivierte Paket`/srv/tse-a1-passive-attempt-disabled-20261114`
mit Manifest`68ef7e11…` bleibt unverändert archiviert; wegen des beschriebenen
Releasefehlers darf dieser ältere Entwurf nicht nativ gestartet werden.

Parent ist der tatsächlich gelaufene Rootfreeze`c41b8f20…`; alle fünf Gates des
neuen Forks sind False. Eigene Service-/Evidence-/Collectornamespaces und neue
Pins sind vollständig retargetet. `controller_gc`, `lookup_resource`,
`metadata_probe` und die vier Coredateien sind unverändert; die tatsächliche
Own167-Metadatenqualifikation`81c402ed…` wird mit identischen Fingerprints
weiterverwendet. Der Builder verweigert diese Wiederverwendung bei abweichenden
Methodenfingerprints. Runner nach Rücknahme ausschließlich von Gates und
Namespaces bytegleich; CP/RD/Inputscope/Transport/Host/Transaktion/Auditor
ebenfalls unverändert.

Rootreview/Integration und gegebenenfalls ein separat eingefrorener einzelner
Native-Lauf zur Erfassung der fehlenden tatsächlichen Counterwerte bleiben
offen. Kein automatischer Retry, keine Grenzerhöhung und keine Umwertung des
alten FAIL. Ein neuer Build oder Rollout ist nicht Bestandteil dieses Fixes.

## Rootintegration und Reviewkorrektur

1d6e991→Root99eedfa und Releasefix11756e3→Rootb156307 integriert. Root prüfte den vollständigen29Zeilen-Diff und den anschließenden Ein-Predicate-Fix;43gezielte Fälle bestanden auch unabhängig im Rootlauf (2,394s), vollständiger Log privat RootEV/a1-attempt-journal-root-tests.log. Der ursprüngliche unabhängige IMPORTANT-Befund bleibt in seiner Quittung erhalten und ist durch den echten geerbten Down→Guardreject→finally-Up-Gegenfall geschlossen. Der feste unveränderte InputScope erlaubt maximal50Nativecalls; die97er-Releasekante ist darin unerreichbar. Separate Author-RED/GREEN-Rohlogdateien existieren nicht, deren Ergebnisse wurden im Tooltranskript beobachtet. Offlinequittung und Root-GREEN-Log sind tatsächlich als Dateien gesichert. Neuer Rootfreeze e26d3c6e64a32fc2e554baa3281f3e8551a6382b63281bd8392be884e5d07c66 vorbereitet; nur Gates/Namespace/CollectorPRIVATE/Repins gegenüber sicherem deaktiviertemf1cbd265 verändert. Kein neuer Native-Lauf bisher.

## Stand 20:56 UTC – A1-Zählerbefund und Build022-Testvorbereitung

Der einzelne A1-NoFire-Lauf205026 ist geschlossen **FAIL**. Das neue Journal
belegt erstmals den tatsächlichen ersten Aufruf: XTestFakeRelativeMotionEvent
(+12), Return1, Requestzähler26→31, Dauer0,217ms. Der unveränderte Guard
verweigert diese Fünferspanne. Welche Requests die Spanne verursachen, wird
statisch untersucht; keine Toleranz-, Input-, ACK- oder Gainänderung. ResultSHA
269295bf1890621b641a7c976b27e521ea4775d5b1b37e40897331c9baf9e2ae.
RootRestore664Dateien+8Absenzen+3Schlusslogs PASS; alle drei Spielrollen normal
beendet. Recorder40Callbacks/40freed, keine unbekannten/fehlerhaften/verlorenen
Records, Exit0/reaped/noForce. Kein A1-Schadens- oder Gainnachweis.
