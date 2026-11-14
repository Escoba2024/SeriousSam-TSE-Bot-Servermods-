# Aktueller Handoff — 14.11.2026, 15:54 UTC

Gesamtauftrag OFFEN. Initialer Cecil-Rollout 6/6 tatsächlich erfolgt; nach externen Syncbefunden drei betroffene Bot-Runtimes kontrolliert zurückgerollt. A nicht abgeschlossen, B nicht begonnen. Kein Root-Native-/Build-/Captureprozess aktiv. Alle historischen FAILs bleiben FAILs.

Der vollständige vorherige Handoff ist bytegleich unter [Historie](archive/2026-11-14-cecil-rollout-a-b-handoff-history.md) erhalten. Aktueller Gesamtplan: [Rollout/A/B](../superpowers/plans/2026-11-14-cecil-rollout-a-b.md). Nur Root integriert und verändert Runtime. Kein RDC-Ausführungszugriff: Monatskontingent weiterhin 0; regulärer lokaler Root-Terminalzugang auf ubuntu-4gb-nbg1-2 ist vorhanden.

## Live

Adresse 91.99.75.33. Acht eigene Bots je Server; individuelle Sessions und Botchat noch nicht implementiert.

| Instanz | Port | Map | Bot-DLL | Zusatzteilnehmer zuletzt |
|---|---:|---|---|---:|
| development | 25650 | Red Station | Cecil048 ec820d04 | 1, Nutzer bestätigt unveränderten Original-1.07-Client |
| redstation | 25600 | Red Station | Gen2 7fc94a39 | 0 |
| yodeller | 25610 | Yodeller | Gen2 7fc94a39 | 0 |
| skulls | 25620 | We Got Skulls'n'Bones Too | Build018 6db89204 | 0 |
| trouble | 25630 | Little Trouble | Build018 6db89204 | 0 |
| hole | 25640 | Hole | Build018 6db89204 | 0 |

Build018 SHA256 6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a; Gen2 7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835; Cecil048 ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530. Dedicated public original1c41…, Dev selektiver Powerupmod fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0; beide Rollen getrennt. Kein Build020 live.

Hard2 nur Dev/Red; andere vier vorbestehend Serious3, Korrektur bis geprüfter Versorgung zurückgestellt. Spawn0/UnlimitedAmmo/Blumenblut/keineGibs/keineLimits/englische Hinweise300s erhalten. Namenpool458 und Identitätsdateien unverändert;48 sichtbare eigene Namen kollisionsfrei,40 eindeutige GUIDs wegen acht bereits vorher über zwei Instanzen wiederverwendeter GUIDs. Keine Behauptung48eindeutiger GUIDs.

## Jüngster Syncvorfall und Rückroll

Dev bis15:17:35 gegenüber verifiziertem14:54-Präfix sieben neue serverseitige BAD/kein Disconnect, beide eigenen Botlogs null BAD/Disconnect. Historische Peerzuordnung nicht mit der aktuellen Nutzerattestation gleichsetzen. Root rollte nur eigene Dev-Botclients regulär auf gesicherten Cecil048 zurück, Dedicated/PID und Identitäten unverändert. Neue Module im Prozess geprüft.90,340s/43Queries danach:8eigene+1zusätzlich durchgehend, alle8 tatsächliche Bewegung,0neueBAD/Disconnect. Begrenzter Betriebsbeleg, keine Ursachenbehebung/Langzeitfreigabe. Nachtrag15:53: vier weitereBAD/0Disconnect nach Rückrolloffset3829466 mit048-Modulen; aktuell8eigene/0zusätzlich. AnderefünfServerdelta0. Rückroll behebt Ursache nicht nachweisbar.

Privat: /srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-development-sync-rollback-20261114-152137/development. Zwei geschlossene before-Logkopien dort verlustfrei gzip-komprimiert, SHA-Roundtrip und Metadaten in current018/compressed-before-logs.json; aktive Logs unangetastet. Vorherige Red-/Yodeller-Rückrolle ebenfalls begrenzt fehlerfrei. Bericht: [Dev-Rückroll](../reports/2026-11-14-development-sync-rollback.md).

Prozessgenerationen zuletzt: Dev Dedicated1336140/127116227, botA1436385/129610621, botB1436491/129613433. Red1337395/127127818,1389123/128042002,1389245/128044846. Yodeller1340003/127151007,1419417/129082063,1419489/129082877. Skulls1321795/126381762,1331708/127056698,1331782/127057511. Trouble1321798/126381763,1332860/127068543,1332930/127069846. Hole1321792/126381761,1334023/127080412,1334134/127083222. Format PID/start_ticks, vor Mutation frisch prüfen. Tatsächliche Units/Roots privat in RootEV/fleet-runtime-identities-after-partial-sync.json, Dev-Botgenerationen danach ersetzt. Keine Unitnamen erfinden.

## Aktuelle Arbeitsstände

RootWT /srv/tse-cecil-rollout-a-b-20261114, Branch codex/20261114-cecil-rollout-a-b. Vor diesem Nachtrag HEAD18734c9e5b64efc80b39c1e860df9e4654481b95. Verifiziert gefetchter Remote34c05ed6c84e6445a94410a836b507b73e765177, Tree03ff0161a3c37eb3e79786592a996894d58b793c identisch lokal18734c9; neuester Nachtrag noch zu veröffentlichen. Direkter Push ohne Credentials, autorisierte GitHub-API plus tatsächlicher Fetch/Treevergleich verwenden. Keine PR-/main-Integration erfolgt.

A1 letzter Original-Eingabelauf144306 FAIL: drei reale Emissionen137/160/144ms innerhalb Grenzen, rechts zwei GetInput-Lesungen desselben12px-Deltas, links eine; Gewinne−0,5/−0,25. Ursache des Recenterverlaufs offen. Originalbytes/Workerende/Root664+8+3RestorePASS. Kein Schadens-/Respawnnachweis. XRecordmethodWT /srv/tse-own-xrecord-core-method-20261114:28RED/Parser begonnen, pausiert, keine Display-/Nativeausführung.

Eigener018/Hard2-Syncversuch150433 FAIL wegen verschwundenem fd46 beim capture.guard. Trotzdem realer normal geschlossener Capture:58088Pakete/0Kerneldrops, PCAP SHA3612c085169c6f6204602ca29a63dfc10255fc3bc8c9efd43f6ce6a807adfa6a. Drei Paare jeweils456gleich/0abweichend; vollständige600s nicht erfüllt, Original früh auf Slot1, kein WAN-/Spätjoinnachweis. Vier normale Closes/Root640+4RestorePASS. Result75eb5fa3333f7962463f58df98030336f3e5538e038094689b20f14cd783880e. [Bericht](../reports/2026-11-14-owned-sync-partial-packet-checkpoint.md).

Agent a4_diagnosis arbeitet seit15:43 ausschließlich offline am engen FD-Churn-Fix in /srv/tse-owned-capture-fd-churn-20261114; nur FileNotFoundError einzelner readlinks tolerieren, Socket-/PID-/NSbindung unverändert. Fertig author320f286b→Root382503a, Root48gezielteFällePASS0,590s; Disabledmanifest3c30151507cf336cd3e23522828de5f3392552f594334e7bb61841846b13851d,69/62/41Pins. Kein Runtimezugriff/Rootfreeze/Retry. Candidate_audit beendet Slot-/Quellenaudit, Commit923e64a+d8b6535 bereits Root896c6df+379446c; [Audit](../reports/2026-11-14-sync-joinorder-slot-source-audit.md). Nächster sinnvoller Syncdiskriminator acht eigene Bots zuerst, Original spät, eigener privater Prestartchecker nötig; externes Ein-Bot-Preflight niemals umgehen. Noch kein Implementierungsplan dafür.

A3 Rootfreeze /srv/tse-a3-instruction-probe-root-frozen-20261114, Manifest272d04e3f82f270ecf52241da8fc66a2f516e7f9657215af08703044e6aad6a7, Launcherf9cb4c4991d101e096787c5ccd5ee26a552b0a34dc8f43e600e7f75f07a7433a,79/109Pins+59gezielteOfflinefällePASS_SCOPE. Erstes120s-Fenster154843 geschlossen PASS_LIMITED,244Damagecalls/direktSTARK13:3MITTEL, keine Fehler; Root640+4RestorePASS. Result2567e1803cd1dcf9065301b4576dcd1c7e3fe61e1333458ec904910519350e26. Swaps undDEMON noch offen. [Bericht](../reports/2026-11-14-a3-first-direct-damage-checkpoint.md). Aufruf bisher: python3 -B run-a3-direct020.py --instrumentation 1 1 120 0 0. Danach Ergebnis/Restore unabhängig prüfen, keine automatische Serie.

A4 Build020 Quellee5f7a65502fbea683014ef8fcc95ecdd2a927b6a, DLL094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0/431104B.2920SDK107-ASan-FällePASS. Hard2-Red/Yodeller je600s echte Bewegung/UsefulPickup/Feuer begrenzt bestanden; je nur eine Phase, kein aktiver Watchdogfall. Skulls/Trouble/Hole ungetestet. ResetWT /srv/tse-a4-epoch-reset-v3-20261114 pausiert mit5GREEN/nächstenRED, keine24Phasenabnahme. Drei Zusatzwelten funktional ungetestet; DesertTemple fehlt. Formale1/4/8-Bot3600/3600/7200s-Gates nicht begonnen. A/B bleiben offen.

## Sicherungen und nächste Schritte

Private Delta022–038 im vorhandenen Driveprojekt vollständig rückgelesen/SHA- und Dateimetadatenrekonstruktion geprüft, kein kompletter nativer Archiv-Restorestart behauptet.037:83e7a8aca0ece37f8c223e94e7b91e96184f000812894b1e636fe1cdb9e4763a/1670314B, Drive12k6aN7j0SsadoPDJmD8VhULHanfd1fRK.038 jetzt ebenfalls externfullPASS:38956273Bytes/SHAde0f0d79dc7cf0bd5b26b717f91339dd992bc694477cdb9cec170fc422c1d603, Drive1jMieRxD9hl0An_LaLuuyVWiHuW4gDVVz,1300Dateihashes/Metadaten einschließlichmtime_ns rekonstruiert und erneut geprüft. Temporäre Rekonstruktion entfernt. NeuesteA3-Belege für039 offen. Backuproot /srv/tse-cecil-rollout-backup-20261114.029–036 identische lokale Rückdownloadduplikate nach erneutemHashcheck entfernt, Originalarchive/Drive/Quittungen erhalten; Receipt drive-return-duplicate-cleanup-20261114.json. Letztmals9,05GBfrei, vor Arbeit8GiB+Budget sichern. Bestehende komprimierte A4-Streams durch RootEV/restore-compressed-closed-a4-streams.py exakt wiederherstellbar.

Nächste Schritte: Optionalen Clienttextbeleg abwarten (Frage mit publiziertem Helfer gestellt); FD-Fix unabhängig prüfen und privaten Spätjoinplan konkretisieren. A3 zweites120s-Fenster mit vertauschten Gruppen nach AgentenSTATICONLY und frischem Preflight; danach einzeln STARK/DEMON. Neue Berichte/Plan/Remote prüfen;039 für neue Belege sichern. Anschließend A1/A4/Formalgates bis nachgewiesenem A-Abschluss, erst dann B.

RootEV /srv/tse-cecil-rollout-evidence-20261114. Frischer Labpreflight fresh-lab-preflight.py prüft vier Rollen, Displays154/155 und Runtime-/Buildlocks; Controller hält danach selbst exklusiv. Vor Native alle Agententests/Builds/Reader, Archiv/Downloads/Gitjobs beenden. Keine parallele Last verfälscht Messungen. Unbekannten Xvfb151 erhalten. Keine unbeaufsichtigten Prozesse behauptet.
