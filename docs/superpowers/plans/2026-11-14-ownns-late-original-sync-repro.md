# Privater OwnNS-Spätjoin: Implementierungsplan

> Status: PLAN ONLY. Keine Implementierung, Tests oder Runtimeausführung mit diesem Plan.
> Basis: `18734c9`. Root integriert, prüft und startet allein.

**Ziel:** In einer ausschließlich eigenen Netzwerknamespace acht aktive
Build018-Bots auf global0–7 verbinden und erst danach einen unveränderten
Originalclient auf global8 aufnehmen. Seine Joinphase und anschließend600s
werden aufgezeichnet. Dies prüft eine konkrete bisher nicht abgedeckte
Versuchsbedingung; es behauptet keine bekannte CRC-Ursache.

**Architektur:** Enger neuer Controller auf dem vorhandenen OwnSync-Capture-
Controller, mit eigenem privaten Acht-Bot-Prestartchecker und einer expliziten
Capture-Zustandsfolge THREE_ROLES→FOUR_ROLES. Bestehende externe Ein-Bot-
Preflights, Vier-Rollen-Captureaufrufe, Reader und Retail-Paketdecoder bleiben
in ihrer bisherigen Bedeutung erhalten. Kein Bootstrapbot, Pauseinput,
Frida, Originalinput oder zusätzlicher Gameserver.

**Technik:** Python/unittest, vorhandene systemd-/Wine-/Namespace-Launcher,
FileTransaction, passive Originalreader, vorhandener tcpdump-Exec-Helfer und
`analyze_retail_sync_pcap.analyze(stream, source_ports, destination_port)`.

**Spezifikation und Quellen:**

- [Join-/Slotaudit](../../reports/2026-11-14-sync-joinorder-slot-source-audit.md).
- `tools/owned_sync_capture.py`: `observe_roles`, `validate_role_ports`,
  `OwnedSyncCapture.start/guard/gameplay_complete/close`, `capture_argv`.
- `tools/owned_capture_exec.py`: Sourcepins, eigener PID/Start, Binding vor exec.
- `tools/analyze_retail_sync_pcap.py`: unveränderter sampled-CRC-Decoder.
- Privater eingefrorener Parent
  `/srv/tse-owned-sync018-json-root-frozen-20261114/run-a4.py`:
  `launch`, `count`, `close`, `whole_quiescent`, Transaktion und Sampling.
  Parentmanifest `3662dd2f064b7404d9c12585c93ebecc14a39b5cb49415b1275215702163274b`.
- `/srv/tse-milestone-a-evidence-20261111/session-readonly.py`: `read`
  prüft Original-Enginecode und liest die tatsächliche16er-Sessiontabelle.

## Verbindlicher Rahmen und offene Abgrenzung

Nur eigene Labrollen server/botA/botB/vanilla unter
`/srv/tse-arena-isolated-20261111`, eigener systemd-Namespace und bestehende
exklusive `runtime.lock`. Bestehende Build-/Deploy-/Runtimeclaims zusätzlich
prüfen; fremde Ressourcen oder Liveinstanzen nicht verändern. Root pausiert
andere Tests, Builds, Archive und Veröffentlichungen vor der Messung.
Keine neuen kostenpflichtigen Dienste oder Paketinstallationen.

Vor Ableitung zuerst den bereits vorhandenen FD-Churn-Fix übernehmen, nicht
erneut entwickeln: Autorencommit
`320f286b759e2561f1842e7d9b577169b6be05f6`, Rootintegration `382503a`.
Autorenpaket `/srv/tse-owned-sync018-fd-churn-disabled-20261114`, Manifest
`3c30151507cf336cd3e23522828de5f3392552f594334e7bb61841846b13851d`.
Root meldete48 gezielte Checks PASS. Vor neuer Ableitung tatsächlichen
integrierten Stand und vollständige Parentpins frisch feststellen; daraus
folgt noch keine native Qualifikation. Die zwei vorhandenen readlink-
ENOENT-Behandlungen und JSON-Portlistenlösung unverändert wiederverwenden.

CPU≤75%, verfügbarer RAM≥1,5GiB und freier Datenträger≥8GiB gelten vor
Start und im Messfenster. Bestehende Hostsamplingrate und Fehlerregeln
beibehalten; keine künstliche neue Samplegap-Toleranz einführen. Während
des neuen Joinwartens denselben Host-/Identitäts-/Captureguard fortführen,
statt bis zu einer langen blockierenden Startwartezeit unbeobachtet zu sein.
Keine ACK-, Sync-Kick-, Spielregel-, Aim- oder Navänderung.

Die bestehende externe Ein-Bot-Freigabe ist **kein** Acht-Bot-Checker:
`Test-TSEExternalVanillaPreflight.ps1` und `external_vanilla_preflight.py`
bleiben unverändert. Bei acht Spielern bleibt deren Ein-Bot-Bedingung falsch.
Ein `canStart=false` wird niemals überschrieben oder als Freigabe benutzt.
Dieser neue Checker erhält eine andere Schema-/Protokollkennung und darf
ausschließlich die eigene bewiesene PrivateNetwork-Namespace freigeben.
Ein externer Vanilla-Testweg erfordert weiterhin den externen Ein-Bot-Test.

Historischer früher Original-Slot1-Lauf bleibt insgesamt FAIL; die456
passenden Syncvergleichspunkte sind kein Latejoin-/600s-Abschluss. Zusätzliche
Live-Teilnehmer sind nicht durch GameSpy-Zeilenposition als global8 bewiesen.
Der Nutzer identifizierte seinen Devclient als unverändert; unabhängige
Datei-/Modul- und Peerbindungen sind davon getrennte Belege.

Neuere Rootmeldung: Nach dem Dev-Rollback auf048 traten später vier weitere
BADs auf, obwohl das erste90s-Fenster0 neue Fehler hatte. Deshalb weder
018 als alleinige Ursache noch048 als allgemeine Lösung behaupten.
`fe4a…`-Dedicated gegenüber Original-Dedicated und048 gegenüber018 sind
**getrennte spätere Diskriminatoren**, keine Varianten dieses ersten Laufs.
Ein negatives Ergebnis mit Original-Dedicated/018 schließt den Livefall
mit abweichendem Dedicated, WAN oder anderen Bedingungen nicht aus.

## Aufgabe1: Acht-Bot-Prestartchecker mit echten Bindungen

Neue Dateien `tools/ownns_latejoin_preflight.py` und
`tools/test_ownns_latejoin_preflight.py`; erst gezielte Modellfälle RED,
dann reine Validierung und ein kleiner bestehende Reader nutzender Adapter.
Keine Xlib-/Frida-/Gameaufrufe in Offlinefällen.

Der private Check muss unter gehaltenem Runtime-Lock folgendes gemeinsam
belegen und privat journalisieren:

1. Nur drei gestartete eigene Rollen; vanilla noch nicht gestartet. Eigene
   server-PID/Start/Unit/CWD und botA/B-PIDs, Originalmodule, exakte DLLpins,
   gleicher nicht-host NetNS-Inode und keine externe Route unverändert.
2. Frische gültige GameSpy-Abfrage: Retail1.07, Yodeller, Hard2,
   genau acht erwartete eigene Teilnehmer, keine zusätzlichen/unbekannten.
   Rohnamen/GUIDs nur privat; Queryposition ist kein Entityslotbeleg.
3. Native Sessiontable aller drei Rollen enthält genau globale0–7;
   botA-Attachlog bindet local0–3 eindeutig auf0–3, botB auf4–7.
   Der Reader durchläuft0–15; keine lediglich achtfach gekürzte Sicht.
   Nichtatomare Reads mit Hostzeit/PIDstart vor/nach ablegen und nur bei
   konsistent wiederholtem Set freigeben; nichts über übersprungene Reads
   interpolieren. Ein laufender Respawn ändert Leben, nicht Botidentität.
4. Pause ist nativ0; tatsächlicher GameTickfortschritt und vorhandene
   Positions-/Inventar-/Combatbelege zeigen unpausierten Betrieb. Keine
   neue Killmarge erfinden; fehlende Bewegung/Kampfbelege bleiben offen.
5. Vier Vanilla-Dateien vor Start frisch passend, kein Prozess aus dessen
   Root, freie eigene Display-/Unitbelegung und bestehende Kapazitätsgrenzen.
   Freier Zielslot8 folgt aus der tatsächlichen16er-Tabelle, nicht UDPindex.

Originaldateipins:

| Datei | SHA256 |
|---|---|
| SeriousSam.exe | `9f8f9a0b8fd718616036ed2c3584904e2dfd58e49515bf4c8ecc45175d02cc53` |
| GameMP.dll | `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208` |
| Engine.dll | `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f` |
| EntitiesMP.dll | `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350` |

Server-Dedicated.exe und Original-Servermodule aus dem verifizierten
Parentmanifest übernehmen; keinen Dedicated durch die Bot-DLL ersetzen.
Build018-Bot-DLL:
`6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a`;
Quellcommit `1802fb3f0720b53feb032abfe2c2a83407bfea6e`.
Aktive Kampfkonfiguration, Yodeller-Navdaten und Player-/Controlsidentitäten
des Parents unverändert pinnen; keine Buildnummer als Herkunftsnachweis.

Negative Fälle: fremde/zusätzliche Teilnehmer, fehlende oder verschobene
Slots, falsche lokale Zuordnung, Pause, falsche Map/Hard/Version/Hashes,
PID-/Unit-/NetNS-/Inodewechsel, veralteter Check und jeder Ressourcenfehler.
Die Freigabe ist zeitpunktbezogen; vor Originallaunch nochmals prüfen.

## Aufgabe2: Capture vor Originallaunch, einmalige Rollenaufnahme

Neue `tools/owned_latejoin_capture.py` und gezielte Tests. Vorhandene
Capture-/Execklasse nur um schmale überschreibbare Binding-/Audithooks
ergänzen; deren Standardpfad bleibt exakt vier Rollen. Die neue Ableitung
und ein eigener Exec-Adapter erlauben ausschließlich diese feste Folge:

- THREE_ROLES: server/A/B vollständig gebunden. Rohcapture starten und
  Bereitschaft prüfen, **bevor** vanilla gestartet wird.
- ADMITTING: diese drei Bindungen unveränderlich erhalten. Nur das bereits
  vor Start registrierte eigene vanilla-Launchrecord darf dazukommen.
- FOUR_ROLES: Original-PID/Start/Unit/CWD, vier Originalmodule, derselbe
  Namespace sowie eigener FD/Inode/Port geprüft; einmaliges Admissionreceipt.
  Danach wieder strikte unveränderliche Vier-Rollen-Bindung.

Der vorhandene BPF `udp and port27850` auf Namespace-lo erfasst bereits
den vorher unbekannten Originalquellport. Keine Filterrotation, kein
Capture-Neustart und keine erfundene Original-PID vor deren tatsächlichem
Start. Alte drei Prozess-/Socketbindungen niemals neu basieren. Portreuse,
zweite Admission, zweiter Zusatzprozess und wechselnde alte Bindungen FAIL.
Originalport ausschließlich aus eigenem PID/FD/UDP-Beleg wählen, niemals
anhand passender CRCs. Private Configs/Owner/Admissionreceipts0600/O_EXCL.

Max640s/250000Pakete/64MiB und vorhandene Loglimits unverändert.
600s nach erfolgreicher Admission plus vorhandene10s normale Capture-
Stopfrist erfordern Admission spätestens30s nach Capturestart. Das ist eine
neue strengere Setupgrenze dieses Protokolls, keine verlängerte Messung.
Bestehende Start-/Joinwartezeiten auf dieses gemeinsame frühere Deadline
kappen; bei Ablauf FAIL mit Cleanup, keine Wiederholung, kein kürzeres600s-
Fenster. Keine neue Originalbewegung oder Spawnanforderung erzwingen.

Getestete Fehlerpfade: Capture-Popen vor Ownerbindung behalten; Capturearm
scheitert; Original startet teilweise oder nie; Admissiontimeout; FDchurn;
PID/Portreuse; Captureende/Limit; fehlende Originalrolle. Capturecleanup muss
auch mit nur drei Rollen versuchen, eigenen Capture normal zu stoppen und
seine Kinder zu reapen. Fehlende Audits dürfen Cleanup nicht verhindern.
Die bisherige Helper-/NetNS-/Supervisorprüfung bleibt aktiv.

## Aufgabe3: Neuer deaktivierter Controller

Neuer Offlinebuilder `tools/prepare_owned_latejoin.py` und Buildertests;
neues privates Paket `/srv/tse-owned-sync018-latejoin-disabled-20261114`.
Bestehende geschlossene Pakete nicht verändern. Alle Runtimegates false.

1. Source-/Build-/Runtimepins prüfen, Ressourcenbaseline und exklusiver Lock,
   alle eigenen Rollen und Displays quieszent; Transaktion vollständig
   sichern/sealen, bevor eine Spiel-/Profil-/Konfigdatei geschrieben wird.
2. Original-Dedicated starten; count0; botA mit vier aktiven018Bots starten,
   count4; botB mit vier aktiven018Bots starten, count8. Beide erhalten die
   identische bewiesene Kampfkonfiguration. Kein Bootstrap/Schließen von A,
   kein Pause-/Unpause-Input und kein früher Originalclient.
3. Privaten Acht-Bot-Check bestehen, Capture THREE_ROLES arm/bereit,
   unmittelbar frisch erneut Acht-Bot-Check; eigener Originallaunch.
4. Regulärer Originaljoin; genaue neue native9er-Slotmenge und erhaltene
   A/B-Zuordnung prüfen. Global8 wird zusätzlich durch die neue eigene
   Verbindung, Original-Sessionansicht, privaten Joinlog und exklusiven
   Admission-/Socketbeleg gebunden; nicht nur als Rest einer Queryliste.
   Keine direkte LocalPlayer-ABIbehauptung ohne entsprechenden Reader.
5. FOUR_ROLES committen und600s beobachten. Vorhandene Readergruppen und
   Samplingraten erhalten; echte Session-/Life-/Worldwechsel journalisieren.
   Original darf stationär bleiben; sein Spawn/aktive Eingaben sind kein
   Bestandteil. Acht eigene Bots müssen verbunden bleiben; Slotwechsel,
   unbekannte Teilnehmer, Syncfehler/Disconnect/Crash führen FAIL.
6. Capture zuerst normal stoppen, anschließend alle tatsächlich gestarteten
   Spielrollen über vorhandenen normalen Closeweg unabhängig schließen.
   Partialstart: frische eigene B.ready/B.identity-Bindung oder nachgewiesen
   leere eigene Unit; niemals fremden PID übernehmen/Force-Spielrollen töten.
   Erst nach whole_quiescent transaktional restaurieren.

Neuer Controller ist ein Sync-/Joinversuch, kein unveränderter A4-Resettest.
Die historische Pause-/Frischspawnbarriere wird nicht durch eine weichere
A4-Freigabe ersetzt. Keine `functional_pass`-/Gesamtqualifikation daraus.

## Aufgabe4: Paketbelege und prospektive Phasengrenzen

Unveränderten vollen Roh-PCAP samt Hash erhalten. Vollauswertung aller drei
Paare A↔B/A↔Original/B↔Original mit unverändertem Decoder ablegen;
Prejoin-Fehlen des Originals und nicht implementierte Jointransporte bleiben
sichtbar und verhindern einen vollständigen Vergleich dieser Gesamtsicht.
Jeder tatsächlich vergleichbare abweichende CRC-Punkt bleibt FAIL, auch
in der Joinphase. Keine Grenzwerte, fragmentierten oder widersprüchlichen
Pakete ignorieren. Erster Paarunterschied ist kein erster20Hz-Simulationstick.

Für das separate600s-Nachjoinfenster **vor** CRCauswertung Start-/Endoffset
an vollständigen PCAP-Recordgrenzen festhalten, mit Hostzeiten und
unveränderlichem Admissionreceipt. Ein reiner Offlinewrapper liefert Header
und bytegleiche vollständige Records dieses festgelegten Bereichs an den
vorhandenen Decoder. Es ist eine Speicher-/Capturebeobachtungsgrenze, kein
atomarer Enginezeitpunkt. tcpdump-Pufferung und Randpaare können daher
weiterhin INCOMPLETE bewirken; keine EPS, Ergebnisauswahl oder nachträgliche
Verschiebung zur Reparatur. Vollcapture und Joinphase nie dadurch verwerfen.

Nachjoinvergleich nur begrenzt vollständig, wenn alle drei Paare mindestens
einen gültigen Vergleichspunkt,0Unterschiede/fehlende Peers/Fragmentierung/
unsupportedTransporte/Konflikte und0KernelDrops haben, zugleich600s erreicht,
Capture-/Ressourcen-/Rollen-/Slot-/Loggates bestanden sind. Server-/Bot-/
Original-SYNCBAD/Disconnectdifferenzen und tatsächlich aktive Kampfbelege
getrennt ausweisen. `qualified=False` bleibt immer erhalten. Jeder andere
Fall FAIL/INCOMPLETE; kein generelles Stability-/WAN-/Humaninput-PASS.

## Aufgabe5: RED→GREEN, Review, genau ein Rootlauf

Zukünftige gezielte Offlinebefehle, **hier nicht ausgeführt**:

```sh
python3 -m unittest tools.test_ownns_latejoin_preflight
python3 -m unittest tools.test_owned_latejoin_capture
python3 -m unittest tools.test_prepare_owned_latejoin
```

Erst fehlende Funktionen/konkrete Gegenbeispiele RED beobachten; anschließend
gezielt implementieren und GREEN belegen. Zusätzlich die vorhandenen48
FD-/Capture-/JSONfälle mit denselben ursprünglichen Fixtures ausführen,
deren exakte Befehle aus dem FD-Churn-Bericht übernehmen. Kein breites
Discovery, keine nativen Imports/Displays/Netzoperationen in Modelltests.
Testen: JSONroundtrip und Execstage, falsche alte Bindungen, doppelte
Admission, Startup- und Cleanupfehler, feste Limits, Slot8-Beweis, volle
PCAP-Erhaltung, vor Outcomes fixierte Recordcuts, fehlende/abweichende
CRCpaare und Rand-INCOMPLETE. Originaldecoder bytegleich pinnen.

Commits trennen: Checker+Tests; gestufte Capturebindung+Regressionen;
Controllerbuilder+Audits+Handoff. Ein unabhängiger Reviewer prüft danach
Quellen, vollständig frische externe Pins, unveränderte Standardpfade und
alle Fehler-/Partialcleanupwege. Root erstellt eigene Gate-/Namespacecopy;
deren Diff darf nur benannte Gates/Pfade/Namespaces und abhängige Hashpins
enthalten. Vorher kein Runtimekommando aus einem Entwurf ausführen.

Root startet danach höchstens einen600s-Versuch bei frischem Preflight und
beendeten Paralleljobs. Ergebnis, gestartete/geschlossene Rollen, Capture-
Owner/-Kinder, Displays, Locks, tatsächliche Dateianzahl/Absenzen/Metadaten,
geschlossene Loghashes und unabhängige Restaurierung quittieren; keine
historische feste Restoredateizahl erfinden. Bereinigter Bericht ins Git,
private Restore-/PCAP-/Identitätsdaten nur in bestehende private Sicherung
mit Rücklesen/Hashvergleich. Erst nach Befund neue diskriminierende Planung;
kein automatischer Retry oder gleichzeitiger Dedicated-/Botbuildwechsel.
