# Sync: frühe Originalbeobachtung ist kein Latejoin-Beleg

**Nur Quellen-/Archivdiagnose, keine bewiesene CRC-Ursache.** Basis `7fd2180`.
XRecord-Methodenworktree unverändert pausiert. Keine Implementierung,
Kompilierung, Tests, Hooks, Prozesse oder native Reproduktion gestartet.
Private Namen, GUIDs und Peeradressen wurden ausschließlich intern verglichen.

## Tatsächliche Joinreihenfolge und globale Slots

OwnSync-Archiv:
`/srv/tse-milestone-a-evidence-20261111/own-sync018-json-root-20261114-150433`;
Result-SHA `75eb5fa3333f7962463f58df98030336f3e5538e038094689b20f14cd783880e`.

Der archivierte Controller startet Dedicated→inerten einzelnen Bootstrapbot,
pausiert über normalen Input, verbindet den Originalclient, schließt Bootstrap
und startet danach die beiden Vierergruppen. Tatsächlich ermittelte Zuordnung:

| Rolle | Globale Slots |
|---|---|
| botA, lokale0–3 | 0,2,3,4 |
| botB, lokale0–3 | 5,6,7,8 |
| eigener Originalclient | 1 |

Die später freigegebene Pausebarriere ist archiviert. Die456 passenden
abgetasteten Syncvergleichspunkte gelten für diese frühe Originalverbindung
und genau diese Bedingungen. Gesamtlauf bleibt FAIL wegen des späteren
FD-readlink-ENOENT; kein600s-PASS, WAN-, aktiver Originalinput- oder
Latejoinnachweis. Ein Bot auf global8 ist dadurch tatsächlich beobachtet.

Die Live-Vorfallarchive liegen unter
`/srv/tse-cecil-full-20261107/.codex/evidence/`:

| Instanz / Snapshot vor eigenem Rollback | Eigene Zuordnung aus Attachlogs | Serverfehler im archivierten Präfix |
|---|---|---|
| Red, restart-fleet-20261111-red-sync-rollback-20261114-105950/redstation | botA0–3, botB4–7 | 27BAD,2TooManyBadSyncs |
| Yodeller, restart-fleet-20261111-yodeller-sync-rollback-20261114-135331/yodeller | botA0–3, botB4–7 | 27BAD,2TooManyBadSyncs |
| Dev, restart-fleet-20261111-development-sync-rollback-20261114-152137/development | botA0–3, botB4–7 | 7BAD,0TooManyBadSyncs |

Jedes archivierte eigene Botlog enthält genau vier eindeutige
`local player … (player index …) is now bot-driven`-Zuordnungen und
0SYNCBAD/0TooManyBadSyncs. Die zusätzlichen Live-Peers sind kein belegter
unveränderter Originalclient. Ihre globalen Entityslots sind aus diesen
Archiven nicht direkt bewiesen: keine BotSnapshot-Zeilen, und ein GameSpy-
Ausgabeindex darf nicht still als globaler Entityslot behandelt werden.
Die OwnSync-Slot1-Kontrolle deckt die zusätzliche spätere Verbindung daher
nicht ab. Beim Yodeller-Rollbacksnapshot war der Zusatzteilnehmer bereits
weg; dessen früherer Vorfall bleibt separat durch die private Klassifikation
belegt, nicht durch eine erfundene aktuelle Neunerteilnehmerzahl.

Nach dieser Archivprüfung bestätigte der Nutzer, der aktuelle zusätzliche
Devteilnehmer sei sein unveränderter TSE1.07-Client. Das ist eine relevante
Nutzerangabe; vier Dateihashes/geladene Module und die private Zuordnung zum
konkreten Server-Syncpeer sind noch nicht unabhängig gebunden. Root belegte
nach Bot-only-Rollback auf048 denselben beibehaltenen Teilnehmer über90,340s/
43Queries mit acht eigenen Bots und0neuenBADs/Disconnects. Das ergänzt die
Betriebsbelege, ersetzt aber die offenen Bindungen nicht.

Stabile Serverpräfixe:

- Red: `d357eef33d0bfc5a71450ed8e8b044337547ede60664db5ea2bfa1295a79c0ea`;
  ersteBAD-Zeile20452, Tick7230,38.
- Yodeller: `c2d193ddfa4a5caa7cf4778de72f5013ee31bc5ea42019ae7d372f50b020f3a5`;
  ersteBAD-Zeile58200, Tick16004,42. Sanitized peer receipt weist zwei
  externe Adresstoken und keine neuen eigenen Clientlogfehler aus.
- Dev: `6e260e404d02a18560f4a73270675960446af06048cf6e91cfe60d2d47ea877e`;
  ersteBAD-Zeile78411, Tick24029,71.

## Tatsächliche Buildquellen statt Branchannahmen

Die vorhandenen Buildmanifeste und tatsächlichen `Sources/Game`-Dateien
wurden gegeneinander gehasht. Cecil048 besitzt ein Overlay; dessen
Quellcommit allein beschreibt nicht sämtliche Buildbytes. Der Gen2-Commit
war im geprüften Gitobjektbestand nicht auflösbar; die vorhandenen
manifestgepinnten Buildquellen waren lesbar und passen zu ihren Pins.

| Kandidat / Buildverzeichnis unter /srv | DLL-SHA256 | BotDriver.cpp-SHA256 |
|---|---|---|
| tse-milestone-a-build-018-20261112 | `6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a` | `75cf99356b70ec1150e3af1316c8bae2d989c37b1608f2d0e64ec056e5e71551` |
| tse-cecil-full-build-048-20261109 | `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530` | `e90c259be7dc14b88cb8cd9454c8f91b9bcbf73ab435845f3b5a27b6646874a4` |
| tse-integrated-build-20261021-04 | `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835` | `e4ebf21d35b7cc1fdee7a47c663e7cc1fb607836dcee16e0d67ad3acb3ef81b0` |

Alle drei tatsächlichen BotDriver führen Human- und Legacy-Targetscans
über0..15 und Arrays mit16Einträgen aus. `bot_perception.h` verwendet
`kMaxPlayers=16` und weist nur Indizes außerhalb0..15 ab. Lokale
Clientzustände und `BotCombatIsLocal` behandeln vier lokale Sources und
vergleichen deren echte `pls_Index`-Werte; global8+ wird nicht zu local8.

Die gefundenen achtteiligen Grenzen sind andere Domänen:

- Game.cpp lädt/speichert acht lokale Player-/Controlsprofile; `lp_iPlayer<8`
  ist der Profilindex, nicht `pls_Index` des globalen Netzwerkspielers.
- `IsOwnBotCharacter` vergleicht acht bekannte GUIDs. Im gepinnten Build018-
  Game-Verzeichnis wurde nur diese Definition, kein Aufruf gefunden.
- SenseInput trägt index/local/enemy, jedoch kein menschlich/Bot-Merkmal.
  Die geprüfte Targetverdrahtung erkennt eigene lokale Geschwister; sie
  beweist keine eigenständige Priorisierung eines menschlichen global8-
  Teilnehmers gegenüber Bots des anderen Clientprozesses.

Damit ist in den geprüften Pfaden kein fester globaler Acht-Spieler-
Targetoverflow belegt. Die Aussage gilt nicht automatisch für sämtliche
importierten Retailbibliotheken oder jeden Engine-/Entitypfad.

## CRC-relevante Grenze

Der konkrete gemeinsame Transportweg ist in allen drei Sources vorhanden:
eigene lokale Source→CPlayerAction→`ctl_ComposeActionPacket`→`ppls->SetAction`.
Der Driver sichert/restauriert den gemeinsamen Controlsbuffer und erzeugt
Translation/Rotation/Buttons im Actionpacket. Targetwahl beeinflusst diese
Actions und damit spätere normale Simulation; unterschiedliche Botactions
sind jedoch für sich keine CRC-Divergenz zwischen simulierten Peers.

Der abschließend direkt gelesene018↔048-BotDriverdiff trennt gemeinsame
Pfade von tatsächlichen Änderungen: Finite-/NeutralAction-Prüfungen,
Welt-/Netzwerkmutex und WeaponObserver samt GetAnimLength existieren bereits
in048. Sie sind keine neuen018-Deltas. Tatsächliche018-Änderungen sind:

- Rotationbaseline bei eigener Entity-/Mapgrenze neu an native LastRotation
  binden; nur private gewünschte Heading/Pitch-Baseline übernehmen, keine
  native Last-/CumulativeRotation direkt überschreiben.
- FOV/MaxFOV-Damping als zusätzlichen Eingang des eigenen Aimgates lesen;
  dieser Helfer schreibt keinen FOV-Wert.
- ArenaTier-Profile und geänderte Kampf-/Supply-Priorität erzeugen andere
  gültige Actionentscheidungen; fehlgeschlagene Rotationbindung wird neutral
  an die eigene PlayerSource übergeben.
- Zusätzliche begrenzte Aim-/Transporttelemetrie bei bestehenden Diagnostics-
  und Logintervallen liest Zustände um Compose/SetAction.

Diese Änderungen betreffen Actions bzw. eigenen Policyzustand und können
reproduktionsrelevant sein. Welche davon überhaupt am ersten abweichenden
Syncpunkt beteiligt ist, wurde nicht gemessen. Es ist kein CRC-Fixvorschlag.

Der gemeinsame Weaponobserver liest u.a. native Waffenstates und ruft
GetAnimLength; dessen vollständige Wirkung auf private Enginecaches wird
hier nicht als bewiesen nebenwirkungsfrei qualifiziert. Er ist in **beiden**
beobachteten Situationen tatsächlich vorhanden:
OwnSync150433 protokolliert2143/2319WeaponObserve-Zeilen; Devvorfallarchive
96152/96648. Diagnostics0 ist kein Beleg für dessen vollständige Abschaltung.

Game.cpp unterscheidet sich zwischen048 und018 ausschließlich durch den
opt-in normalen Community-SendChat-Pfad; die örtlichen achtteiligen
Profilroutinen sind gleich. Gen2 und048 haben dieselbe Game.cpp-SHA
`43e14e8d0cb5270211436d203bc5aba4abce64fb8cb4b39c80d2bb0bcbea53d7`.

Alle drei Manifeste pinnen denselben SDK-/Include-Basisstand; das beweist
keine Retail1.07/SDK1.10-Simulationsgleichheit. Es wurde weder eine neue
Retail-CRCfunktion verändert noch der erste abweichende Action-/Entity-
CRCbestandteil gemessen. Die bisherige Retail-Ghidra-Kette bestätigt
Vergleich/Reset/Zähler/Kick; sie identifiziert die aktuelle Divergenzursache
weiterhin nicht. Rollbackerholung ist ein wichtiger Betriebsbeleg, aber
wegen neuer Botverbindungen, Sessionzeit und Spielzustand keine reine
kontrollierte Binärursachenprobe.

## Kleinster neuer OwnNS-Late-Original-Entwurf

Noch kein ausführbarer Plan/Controller und keine Startfreigabe:

1. Neue eigene Namespace-/Lock-/Port-/Dateitransaktion mit vollständigem
   Restore. Unveränderter vorhandener Dedicated und Originalclient mit vier
   Originalhashes, Build018-Botkandidat, Yodeller/Hard2/Diagnostics0 sowie
   bisherige Limits/Kickschwelle und gebundener passiver Sync-Capture.
2. Dedizierte private Kapazität9. Ohne frühen Originalclient und ohne die
   alte Bootstrap-/Original-Pausebarriere zunächst botA4+botB4 verbinden.
   Alle acht eigenen stabilen IDs, Sources und echten Globalslots0..7,
   Aktivität, richtige Map/Regeln und keinen unklaren Teilnehmer beweisen.
3. **Neuer separater OwnNS8Bot-Vorstartcheck**, unmittelbar vor dem einen
   Latejoin erneut: Hashes/geladene Module/PIDstart/NetNS/UDP-FDs, exklusive
   Locks, genau8eigene Connections/keine weiteren, freie neunte Kapazität,
   ursprünglicher Originalclient noch nicht gestartet, Ressourcen und alle
   Capturebindungen/Fehlerstände. Unklarheit oder Abweichung→kein Start.
4. Capture vor dem Join aktiv, dann genau einen eigenen unveränderten
   Originalclient regulär verbinden. Tatsächlichen global8-Slot durch
   Original-/Serverregistry plus Botquellen belegen; nicht aus GameSpy
   behaupten. Stationär ohne zusätzliche Gameplayinputs. Ersten
   divergierenden Vergleichspunkt samt Join-/Slot-/Action-/Simulation-
   Belegen erhalten, keine Wiederholung ohne konkrete Auswertung.
5. Vorab festes einzelnes Beobachtungsfenster und alle bestehenden
   Ressourcen-/Cleanup-/Restoregates beibehalten. Historische frühOriginal-
   und pausegeschützte456Samples bleiben getrennt; ein ungepauster Latejoin
   ist ausdrücklich eine neue Bedingung. Falls später ein kausales Paar
   nötig ist, muss dessen frühe Kontrolle dieselben ungepausten Bedingungen
   besitzen, statt den alten Verlauf umzudeklarieren.

Der **externe OneBot-Vanilla-Preflight aus AGENTS bleibt unverändert**.
Bei acht Bots muss dessen bestehendes `canStart=false` bestehen bleiben.
Der separate ausschließlich eigene Namespacefall ist kein Überschreiben,
Fixture-PASS oder Umgehen dieses externen Vorstartvertrags. Ein zusätzlicher
fremder/unklarer Peer wird weder entfernt noch in eine instrumentierte Probe
einbezogen; dann ist die neue private Probe blockiert.

Diese Reproduktion würde Joinorder/Slotlage für einen tatsächlich originalen
eigenen Teilnehmer prüfen. Sie könnte weder den unbekannten öffentlichen
Clienttyp noch WAN-/Input-/CRCursache ohne weitere Belege gleichsetzen.
