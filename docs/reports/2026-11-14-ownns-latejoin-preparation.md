# OwnNS-Spätjoin: Offlinevorbereitung

Plan `3c7be9ad7525c173e4065adb3e756c1c7d22d3fd`, Rootintegration31004b9.
Claim candidate_audit: neue Latejoin-Dateien, schmale Capture-/Execkopplung,
eigene Tests und dieser Bericht. Root allein integriert und startet Runtime.
XRecord bleibt pausiert. Keine native Ausführung/Displays/Netz/Capture.

## Vertragsentscheidungen

- FD-Fix382503a wurde unverändert als Vorarbeit übernommen; kein zweiter Fix.
- Checker→Capture: exakt drei gebundene Rollen vor Join, unveränderliche
  Altbindungen, einmalige echte Originalaufnahme. Kein Phantomprozess.
- Capture→Controller: unveränderte640s erlauben30s Admission,600s Nachjoin
  und vorhandene10s normale Stopfrist; keine Verlängerung oder Retry.
- Root bestätigte getrenntes Sync-/Joinresultat: acht tatsächlich verbundene,
  aktive kämpfende Bots und volle Sync-/Capture-/Log-/Restore-/Ressourcengates;
  keine Originalspawn-/A4-Frischspawnabnahme. A4-Diagnosen bleiben separat
  offen beziehungsweise NOT_APPLICABLE_TO_SYNC_PROTOCOL, niemals PASS.

## Aufgabe1: privater Acht-Bot-Checker

Reine Policy `ownns_latejoin_preflight.py`: echte16er-Nativtabellen aus drei
Rollen, fortschreitende Sessionticks, genaue lokale0–3→globale0–7-Bindung,
Hard-/Query-/Namens-/Originalhash-/Pause-/Ressourcenbedingungen. Guarded IO
und tatsächlicher flock erfolgen später im Controller; diese Modelltests
beanspruchen keine Prozess-/Runtimefreigabe. Die API besitzt kein canStart.

RED: expliziter fehlender-Checker-Fall schlug vor Implementierung fehl.
GREEN: `cd tools && python3 -m unittest test_ownns_latejoin_preflight`,
12 Fälle PASS. Eine zunächst unrealistisch kleine positive Entityadresse
der Testfixture wurde auf eine Adresse oberhalb der unveränderten nativen
0x10000-Grenze korrigiert; kein Produktionsgrenzwert wurde gelockert.
Keine breite Discovery, Runtimeimports oder externen Preflightänderungen.

## Aufgabe2: gestufte Capturebindung

RED: fehlende gestufte Captureklasse explizit beobachtet. Neue Ableitung
bewahrt drei Originalbindungen, startet denselben unveränderten BPF vor
Originallaunch und lässt genau eine wirkliche vierte PID-/FD-/NetNSbindung
zu. Keine Phantomports, Portauswahl nach CRC oder Altbindungsrebaseline.
Der eigene Execadapter prüft die drei tatsächlichen Rollen vor exec erneut.
Schmale Basisklassenhooks erhalten den bisherigen exakten Vierrollenpfad;
zwei vorhandene FDscans und der FD-Churn-Fix bleiben erhalten.

Prospektive vollständige Recordgrenzen werden vor Decoderaufrufen festgelegt;
Rohdaten/Joinunterschiede bleiben erhalten. Ein sauberer Nachjoinbereich kann
eine frühere tatsächliche Differenz nicht verbergen. Teilrecords werden
ausgewiesen; keine EPS-/Paar-/Decoderänderung. Fehlende Originalaufnahme
verhindert vollständigen Vergleich, aber nicht normales Capturecleanup,
Rohhash und verfügbaren A↔B-Audit. Alle Ausführungsgates bleiben False.

Gezielt55 Fälle PASS (15 neue Capturefälle plus bestehende Capture-/FD-/
Decoderregressionen),0,177s. Zusätzlich ursprüngliche48 Fälle PASS0,599s.
Bei diesem historischen48er-Lauf zeigt ausschließlich der FD-Builder seine
`__file__`-Sourcefixture auf den unveränderlichen FD-Autorenstand; dessen
absichtlich auf zwei readlink-Catches begrenzter Builder darf neue Hooks
nicht akzeptieren. Alle tatsächlichen Vierrollen-/FD-/Sockettests verwenden
die aktuelle neue Library. Kein alter Buildervertrag wurde geändert.

## Aufgabe3: deaktivierter Controller und Guarded-IO

Offline fertig vorbereitet; unabhängiger Review, Rootfreeze und jede native
Prüfung bleiben offen. Neues unveränderliches Paket:
`/srv/tse-owned-sync018-latejoin-disabled-20261114`, Manifest-SHA256
`0d6b16609f7d4356a6f127e219f23e9f61b2363dac1a169c1b09986337180920`.
74 Runtime-,75 Source- und53 Pythonpins; alle vier Ausführungsgates False.
`qualified`, `functional_pass`, `a4_accepted` und `runtime_performed` sind False.
Parent ist ausschließlich das unveränderte FD-Churn-Autorenpaket
`3c30151507cf336cd3e23522828de5f3392552f594334e7bb61841846b13851d`.
Der Builder prüft dessen komplette Pinmenge sowie Build018-Quell-/Overlaypins
erneut; ein adversarial geänderter BotDriver-Quellhash bleibt FAIL.

Der Controller startet server→vierA→vierB ohne Bootstrap/Pause oder
Originaleingaben. Vor Capture läuft höchstens der ausdrücklich von Root
festgelegte20s-Readinessabschnitt: alle acht Slots müssen innerhalb desselben
beobachteten Lebens tatsächlich mehr als1m zurücklegen; mindestens ein Slot
benötigt unveränderten V3-Native-FIREflag-/Sourcegrowthbeleg und die eigene
Kohorte mindestens einen serverseitigen Abschuss **oder** positiven eigenen
Queryfragzuwachs seit Beginn dieses Abschnitts. Nicht jeder Bot muss in20s
feuern. Kein Pickup-/Frischspawn-/A4-Sieggate. Zwei feste Vierer-Readgruppen,
echte unveränderte Source-/Decimal-/Lifeprüfungen, Readattemptjournal,
Host-/PID-/Datei-/Namespace-/Pause-/Logguards und bestehende Abtastkadenz.
Timeout bleibt FAIL mit normalem Readerclose, ohne Capture/Originallaunch/Retry.
Neue Readiness-Rohstreams und Fehlerquittungen sind O_EXCL/0600.

Danach privater Acht-Bot-Check→Capture→erneuter frischer Check→einziger
Originallaunch. Die neue private Prüfquittung verfällt spätestens1s nach ihrem
Ende, entsprechend der vorhandenen Hostguardkadenz; auch direkt an der
Popen-Grenze wird diese Frist geprüft. Dies ist kein neuer Gameplaygapwert.
Die30s-Aufnahmefrist beginnt unverändert am Capturestart und umfasst auch
Capturebereitschaft/zweiten Check/Launch und Admission. Eigene systemd-run-
CLI-Kinder werden sofort registriert, mit höchstens100ms Polling während
bestehender20s-Launchfrist betreut; Host-/Rollen-/Captureguards laufen weiter.
Timeoutcleanup betrifft ausschließlich diesen eigenen CLI-Child. Spielrollen
schließen regulär, nie per Force. Unbeendete eigene Hilfskinder verhindern
Restorefreigabe; Partialstart übernimmt den engen Empty-Unit-/frischen
OwnIdentity-Normalclosepfad. Keine zusätzliche Startwiederholung/Wartefrist.

Jede der zwei nativen Tabellen pro Rolle trägt tatsächliche PID/Startbindung
vor/nach Read, verifizierte Engine/Entities/Gamehashes, Readintervall und zwei
Slot-/Entitybindungen. Stale/PID-/Hash-/Entityabweichung bleibt FAIL. Original-
local0→Source→global8 wird zusätzlich passiv anhand der originalen gepinnten
Instruktionsbytes beobachtet und gegen Query9, native Server-/Originaltabellen,
EntityID und die neue tatsächliche UDP-/FD-/NetNSbindung geprüft. Die neue
Retail-ABI-Beobachtung ist **nicht nativ qualifiziert**; konkrete Bytes/RVAs,
Quellgegenprüfung, Toolverfügbarkeit und begrenzte objdump-Alternative stehen
in [der Entscheidung](../decisions/2026-11-14-ownns-latejoin-local-source-probe.md).
Fehler vor der Schemaaufnahme behalten bereits die tatsächliche vierte
Endpointbindung privat; eine fehlgeschlagene Admission ist kein global8-Beleg.

Nach Admission sind feste600s erforderlich. Alle neun nativen Slots bleiben
exakt gebunden; für alle acht eigenen Bots sind tatsächliche SameLife-Bewegung
und gebundene native FIREflag-/Sourcegrowthbelege erforderlich, außerdem
serverseitiger eigener Abschuss und Queryscoreänderung. Native-Flag zählt als
beobachteter Flag, niemals als bewiesener Waffenfunktionsaufruf. Alter V3-Kern,
Retaildecoder, externe Ein-Bot-Preflights, ursprüngliche Regessions-/Sync-/
Ressourcen-/Capture-/Restoregates bleiben unverändert. Neue Protokollkennung,
eigenes Unit-/Evidencepräfix und privater Sessionname trennen diesen Versuch.
Das Paket führt die alten A4-Diagnosen weiter, ihr Fehlen ist OFFEN bzw.
NOT_APPLICABLE_TO_SYNC_PROTOCOL und kann keine A4-/Gesamtqualifikation ergeben.

## Vollständige Änderungen an owned_sync_capture.py

Seit dem FD-Churn-Parent wurden ausschließlich die folgenden Kopplungen
ergänzt; der bereits übernommene zweifache readlink-ENOENT-Fix bleibt unverändert:

- Die bisherigen Port-/FDbeobachtungsfunktionen sind in interne Helfer mit
  geschlossenem Drei- **oder** Vierrollenschema extrahiert. Die öffentlichen
  Wrapper verlangen weiterhin exakt vier Rollen. Ein beliebiges Zweirollen-
  oder erweitertes Schema scheitert vor IO. Dieselben zwei FDscans,
  PID-/Start-/FDinode-/NetNS-/JSON-Listenprüfungen bleiben bestehen.
- Schmale überschreibbare Methoden `observe_binding`, `binding_ports`,
  `setup_helper`, `setup_config`, `run_audits`, `comparison_complete` ermöglichen
  die gesonderte Latejoinableitung. Die Standardmethoden enthalten die
  bisherigen Vierrollenoperationen und denselben Execadapter/Decoder.
- `start`, `guard` und `close` rufen diese Methoden an den bisherigen Stellen
  auf. Der Capturehelperpfad wird vor Popen bestimmt und bei Execbereitschaft
  identisch geprüft. Childownership, Guardfristen, BPF, Caps, normaler Stop,
  Fallbackfehler, Hashes und voneinander unabhängige Cleanupschritte bleiben.

`owned_capture_exec.py` ist byteidentisch zum Parent. Keine neue akzeptierte
FD-/PID-/Namespaceausnahme oder zusätzliche Scan-/Sleep-/Retryschleife.

## Abschließende Offlineprüfungen

Gezielter finaler Lauf aus `tools/`:

```text
python3 -m unittest test_ownns_latejoin_preflight test_owned_latejoin_capture test_ownns_latejoin_local_mapping test_ownns_latejoin_runtime test_ownns_latejoin_readiness test_prepare_owned_latejoin
Ran 56 tests in 0.200s — OK
python3 -m unittest test_a4_ordered_memory_v3
Ran 24 tests in 0.066s — OK
```

Historische48 Capture-/Decoder-/FD-/Builderfälle erneut PASS0,602s, ohne Skips;
derselbe oben erklärte unveränderte FD-Builder-Quellfixturepfad. Kein breiter
Discoverylauf. Die neuen Module begannen mit beobachtetem Missing-Contract-RED;
zusätzliche konkrete RED→GREEN-Fälle deckten PID/Hash/Entity/Stale, geänderte
018-Quellpins, int-Zähler statt bool-Gleichheit sowie0600 statt0644 ab.
Der echte20s-Timeoutfall bestätigt normalen Readerclose, FAILquittung und
keinen Sample/Retry/Originallaunch. Alle Tests modellieren IO; der PE-Guardtest
liest nur die eigene unveränderte Datei. Kein Xlib/Frida/Display/Game/Netz/Capture.

Reproduktion des Pakets in einem **neuen** Ziel:

```text
python3 tools/prepare_owned_latejoin.py --destination /srv/NEW-private-disabled-package
```

Root kann nach unabhängigem Review ausschließlich eine neue eingefrorene
Kopie erstellen, dort die vier exakt benannten Gates sowie Namespace-/
Pinpfade konsistent retargeten und alle74 Runtime-/75 Source-/53 Pythonpins
frisch prüfen. Native Abnahmen umfassen vor600s insbesondere den neuen
Original-local0/global8-Reader und die echte8→9-Belegung. Ohne deren Beleg
FAIL/normaler Cleanup; kein automatischer Retry. Bestehende ursprüngliche
externe Ein-Bot-Preflights bleiben ein separater Vertrag und werden durch
diesen privaten Checker weder freigegeben noch umgangen.
