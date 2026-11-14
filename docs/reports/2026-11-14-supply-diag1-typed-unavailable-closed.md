# Build023: alle87typisierten Unavailablebelege geschlossen geprüft

**Diagnosebelege gebunden, kein SDKfix oder A4-Abschluss.** 84Zeilen melden
`render_type`,2 `missing_entity`,1 `typed_need`. Die langen Versorgungszeiten
bleiben real; ein pauschaler WeaponNeed-/Avoid-/Timeoutfix ist nicht belegt.
Ein separater GroundedReplan-Handshake-Reproducer ist eng begründbar.

## Unverändertes Fenster und vollständige Bindung

Privatfenster `supply023-diag1-root-redstation-20261114-224736`,180.091179s,
ResultSHA256 `caaf0e72dc26f63044d1f27d1670335ff45d314a712a0dda77427f11158217e8`.
Originalstatus bleibt `PASS_LIMITED_SUPPLY_DIAGNOSTIC_OBSERVATION_ONLY`.
Root belegt0neueFehler in vierRollen, reguläreCloses und640Datei-/vierClosedlog-
Restorechecks. AndereTestbedingung als600s/diag0; keine Vergleichs-, Ressourcen-,
Sync-/Dauer-, A4- oder Promotioneinstufung.

Alle87Zeilen wurden vollständig nach dem tatsächlich kompilierten Schema
getypt, keine doppelten EventIDs. Jede bindet Rolle/Local→Ownslot/Registry,
SourceSpawn/Generation/Botentity→WPO→genau ein natives Leben mit identischem
World-/Epoch-/PID-/Startkontext. Itementity bleibt vom Botentity getrennt.
87/87 passen zum letzten tatsächlichen SourceGoal und unmittelbar folgenden
sameTick-GoalEnd `unavailable`;53gemappteDeadlines entsprechen dem ursprünglich
geloggtenGoal. JedeSource-Ownedmaske wurde auch im selben Nativeleben gesehen;
dies ist keine Behauptung atomarer Gleichzeitigkeit.

Sämtliche V3-Rohhüllen/Versuche/Lebenssummen wurden mit dem bestehenden reinen
Validator unabhängig geprüft: identisch zur vollständigen Rootauswertung.
Kein Legacy-A4-CLI wurde durch Retagging passiert. Exakte Nativefloats und
vollständige6Dezimal-Druckintervalle innerhalb desselben lebenden Intervalls
bleiben unverändert; keine policytick/20-Uhr oder neueEPS. Unqualifizierte
WPO-Entwurfsgrenzen mit Tod/Nativezeit0 wurden vor Abschluss entfernt; finale
Zeitgrenzen verwenden ausschließlich genau gebundene lebendeWPO-Zeilen.

93Source-GoalEnds melden `unavailable`;6haben keine typisierteZeile. Drosselung
und separate Readcallsite sind daraus nicht unterscheidbar: **UNKNOWN**.
Auch neueRecoveryvorschläge: **0**, der023-Recoverypfad bleibt nativ unbewiesen.

## Tatsächlich beobachtete Gründe

| Grund | Anzahl | Belegte Metadaten und Grenze |
|---|---:|---|
| render_type |84 |AlleRender5/Flags65600;64Weapon,11Armor,9Health |
| missing_entity |2 |GewöhnlicheWeaponziele verschwunden; vorherGoal vorhanden, Destroyursache unbekannt |
| typed_need |1 |Health255, kein Weaponziel; konkrete Unterbedingung nicht einzeln geloggt |

Render5 ist im SDK107 `RT_EDITORMODEL`. `Item.es:ItemReceived` schaltet darauf
um und wartet beiRespawn auf Wiedererscheinen, sonst folgt das Lebensende.
Das stützt reguläre Nichtverfügbarkeit nach Aufnahme, beweist aber weder
Itemcallback, Verursacher noch Aufnahmezeitpunkt. Von64Weaponzeilen sind55
Respawn1/Drop0 und9Drop1/Respawn0. Alle64haben PickupOnce0/Pickedmask0/
PickedForPlayer0; alle87WeaponsStay0. Bei20Nichtweaponzeilen sind diese
Weapon-spezifischen Felder ungültig, keine erfundenen Nullbeweise.
Kein typisierter `hidden`- oder `picked_for_player`-Ablehnungsgrund beobachtet.

Die Auswahl prüft bereits den echten `BotCecilReadItem`-Guard. Somit ist nicht
belegt, dass Bots Ziele schon beiRender5 blind neu wählen. Bei späterem
Verfügbarkeitsverlust endet der Versuch regulär und wird neu geplant.
`typed_need` betrifft lesbareHealth; SourceHP65→75 passt zu einem entfallenden
Gesundheitsbedarf, exakter Itemwert/Unterzweig bleibt ungemessen.

## Drei vollständig erhaltene langeNoUseful-Leben

NativeAliveintervalle, linkeBeobachtungszensierung und Tod bleiben unverändert;
keine günstige Verkürzung. Mask3/7 enthalten nur Messer/Colt/DoubleColt.
SourceTickfolgen sind keine nativeWegezeitrechnung.

| EigenerAlias /Gen | Nativ beobachteterAliveabschnitt | Vollständige Zielkette mit Abbruch |
|---|---:|---|
| B:3 /9 |122.302864→179.106323:56.803459s |243ticks2461–2652 render_type→5442731–2967 render_type→3112967–3402 unreachable_hold→4013403–3599 death |
| A:1 /6 |28.899845→68.249565:39.349720s |267918–1194 render_type→Health3581194–1253 connector→2431314–1547 death |
| A:0 /8 |60.499363→91.951012:31.451649s |2431390–1772 render_type→4011792–2023 death |

B:3 hat0Healthgoals/0Importantinteraktionen; A:0 ebenfalls0/0. A:1 hat einen
kurzen Healthversuch mit explizitemConnectorende, keine belegte dauerhafte
Healthblockade. NativeMasken B:3 nur3/7, die beiden anderen nur3. Auch der
Coltgewinn3→7 wird nicht als brauchbareZusatzwaffe gezählt.

AndereOwnslots zeigen passende NativeWeaponbitgewinne innerhalb umgebender
WPO-Zeitfenster: für243 Readserial3157/Game131.853439, Abstand zur geloggten
Goalposition1.608m; für544 Read3524/Game147.654404/1.086m; für267 Read1277/
Game50.649513/3.324m. Alle passenden Zeugen stehen privat, keine günstige
Auswahl oder neueDistanzschwelle. Die Beobachtungen sind mit konkurrierenden
Aufnahmen vereinbar, aber keine Item-ID-/Callbackattribution. Einige
WPO-Fenster sind breit; genaue einzelne Wegezeiten bleibenUNKNOWN.

Kandidaten-/Selection-/Connectorlogs sind vollständig privat erhalten.
B:3 wählte beispielsweise243 mitScore270.6595 trotz geloggtem248/181.871568;
später311/341.232615 trotz267/241.247883. Die lokalen Claim-/Contestedwerte
sind nicht geloggt, ungewählte Connector-/Routenerfolge nicht belegt. Die
vorhandene lokale Konkurrenzpräferenz kann Scores überstimmen. Kein
behaupteter nächster/erreichbarer Alternativgewinn und kein Crossslot-
Tickgleichheitsbeweis werden daraus konstruiert.

## Eng begründeter weiterer Reproducer, noch keine Umsetzung

Beim B:3-Terminal311 zeigt SourceState3400 tatsächlichesNavSource/Anchor69,
Hop71 und Positiony0.376, bevor3402 `unreachable_hold` folgt. OriginalNav69
liegt beiY38.3673,71bei36.5; beideFlags0/Lock−1. Der vorhandene Stayzweig und
zweiteilige GroundedReplan-/UnreachableHoldpfad sind daher konkret prüfbar.
Welcher Support-/Velocity-/Budget-/Nearestguard nativ scheiterte, ist unbekannt.

Die existierende echte SDK107-Brücke besitzt bereits
`groundedReplanFixture/groundedReplanGuards` mit denselben hohenMetadaten,
setzt nach Landung aber explizit `s.anchor=0`. Dieser positive Test ersetzt
keine tatsächliche AcquireRoute-/BotCecilChooseGoal-/BotSupplyNearest-Kette
gegen einen noch gehaltenen hohenAnker69.

Nächster enger Vorschlag: diese realen Körper mit echtem committed69→71,
FALL→STAND und frisch gemessener Bodenposition/ursprünglichen Navdaten
sequenziell prüfen; Bodenanker nicht vorab setzen. Budget/LOS, WorldBase-
Support und genaueGeschwindigkeit bleiben getrennte unbekannte/adversariale
Eingaben, keine erfundenen Nativefakten. Erst tatsächlichesRED und Rootreview
rechtfertigen eineFixentscheidung. Keine pauschale Need-/Timeout-/Radius-/
Lock-/Floorfreigabe. Die alten103s-/76s-Diagnostics0-Leben bleibenUNKNOWN.

## Reproduktion und Handoff

Private vollständige Rohbelegquittung und zwei reproduzierbare Offline-
Einstiegsskripte im eigenenWorktree
`/srv/tse-build023-supply-diag1-analysis-20261114/.codex/evidence/typed-unavailable/`.
Reihenfolge `python3 -B analyze.py`, danach `python3 -B enrich.py`, aus dem
Worktreeroot mit jeweiligen privaten Skriptpfaden. Keine Runtimezugriffe.
Diese beiden Schritte ergeben die vollständige Fall-/Rohbeleganalyse mit SHA256
`94cccb7499c07164ca3105d1f3fb9391e97059a2b979f801e62731c0fc7dd021`.
Die zuerst veröffentlichte Endquittung enthielt danach separat ergänzte
Metadaten: zwei erklärende Felder und drei zusätzliche Quellhashes. Dieser
abschließende Schritt war im ursprünglichen Aufruf unvollständig dokumentiert.
Er ist jetzt als privates `metadata_finalizer.py` reproduzierbar (SHA256
`5496b31017f9261166a0104360d0904722a5ccf1b5b62e404029b04df20efd43`):
Der explizite dritte Rezeptschritt lautet (jeweils mit privaten absoluten Pfaden):
`python3 -B metadata_finalizer.py INPUT_RECEIPT HISTORICAL_SOURCE_ROOT NEW_OUTPUT`.
Der Zweiskriptreplay ist inhaltlich vollständig gleich, aber vor diesem Schritt
**nicht bytegleich** zur Endquittung. Nachgetragen werden ausschließlich
`reproducer_proposal_only`, `audit_print_command_failure` und die drei
`source_sha256`-Blätter für `cecil_rules.h`, `cecil_motion.h` und
`test_cecil_native_bridge.py`. Inputpin `94cccb7499c07164ca3105d1f3fb9391e97059a2b979f801e62731c0fc7dd021`,
drei historische Quellpins und Outputpin `17905303c8a0bb8dd180f215412c9ac61c7d1ede3e259bf971e0897837dc1bea`
werden strikt geprüft. Das neue Output verwendet 0600/O_EXCL/NOFOLLOW.
Keine Fallbindung, Rohdaten oder numerischen Resultate werden verändert.
Der auf Roots Zweiskriptreplay bereits getrennt geprüfte dritte Schritt ergab
bytegleiche Endquittungen; Root führt diesen Finalizer zusätzlich selbst aus.
`final-receipt.json` SHA256
`17905303c8a0bb8dd180f215412c9ac61c7d1ede3e259bf971e0897837dc1bea`.
Alle87vollständigen Zeilen, SourceSpawn/Goal/End/State/WPO, Nativeidentitäten,
Readserials, Langzeit-Nativerows, Kandidatenpools und Hashpins bleiben privat.
Dateien0600/Verzeichnis0700; keine Rohspieleridentitäten oder Retailbytes imGit.
Kein SDKtest/Fixture/Fix/Build oder Nativefenster gestartet. AlleJobs beendet.
