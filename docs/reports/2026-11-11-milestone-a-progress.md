# Meilenstein A: implementierter Zwischenstand, keine Gesamtfreigabe

Stand 11.11.2026 UTC. Auftrag wird auf dem vorhandenen Hetzner ausgeführt. **A ist nicht abgenommen; B wurde nicht begonnen.** Drei bestätigte externe Sync-Abbrüche im Dev-Test verhindern die Freigabe. Neue Kampf-DLL und Namen wurden nicht produktiv aktiviert. Alle Instanzen behalten ihre bisherigen DLLs/Maps. Vier öffentliche Instanzen haben die neue Spawn-Konfiguration geladen; Dev wurde um19:11 UTC und Hole um20:20 UTC vorsorglich auf den gesicherten Ausgangsstand zurückgesetzt. Hole hatte neun SYNCBAD ohne Disconnect, Dev zuvor drei bestätigte Disconnects; die Ursache ist offen. Aktueller Hole-Beleg: `milestone-a-20261111/hole-precautionary-rollback.json`.

## 1. Tatsächliche Änderungen und Betrieb

- A1: Ladereihenfolge geprüft. Dedicated überspringt das `PersistentSymbols.ini`-Laden in `Game.cpp`; dort vorhandene Nullwerte waren daher kein Wirksamkeitsbeweis. Dev-Shellwert vor Änderung tatsächlich 3,0, nach Änderung 0,0, gelesen aus dem hashgebundenen GameMP-Modul (RVA 0x5b120), ohne Speicheränderung.
- Sechs versionierte Mapstart-Vorlagen setzen `gam_tmSpawnInvulnerability=(FLOAT)0`; eine typkorrekte bedingte Logmeldung prüft den Shellwert bei jedem Sessionstart. Respawnverzögerung, HP und andere Regeln bleiben erhalten. Ein anfänglicher Retail-Typfehler in der Prüfbedingung wurde erkannt, zurückgerollt und auf einem isolierten Serverprobeprozess korrigiert.
- A2: 208 bestehende Namen bytegetreu erhalten, exakt 250 neue, insgesamt **458**. Neue Namen noch nicht in Live-Spielerprofile geschrieben.
- A3: MITTEL/STARK/DEMON, explizite Migration, Schutz gegen überschreibende Cecil-Voreinstellungen, Waffenbesitz-/Distanzprüfung und Colts-Grenze von 18 Welteinheiten. Gemeinsame Fähigkeiten und Zustand je lokalem Bot bleiben erhalten. Waffenbeschaffung, Supply/Kampf-Arbitrierung und alle geforderten Bewegungseigenschaften sind **nicht vollständig neu umgesetzt oder abgenommen**.
- A4: Originalkatalog und alle neun Navdateien geprüft. Keine neue Produktionsfreigabe einer Cecil-Map; öffentliche Legacy-Navigation bleibt aktiv. Keine Original-Cecil-DLL kopiert.
- Dev hatte bereits vor diesem Auftrag die serverseitige selektive Entfernung von Serious Damage/Invisibility aktiv. Dieser neuere Stand wurde erhalten. Unlimited Ammo und vorhandene Blood/Gibs-/Schwierigkeitsregeln wurden nicht verändert.

## 2. Quellen, Builds und Identität

Ausgangsbasis `4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`. Lokale Implementierungscommits: `c261a540f258a271f559d0db790b9cee1352e8fd` (Kampf), `41b2369` (Namen), `904bf8a` (Retail-FLOAT-Vorlagen). Build `tse-milestone-a-build-001-20261111`, MSVC Win32 unter Wine, `build_ok=true`, **qualified=false**, DLL-SHA256 `def7c044ba64a65b742c63d76c775c955b892655e626bf96a1380d778d35719a`. Manifest enthält SDK-/Include-Commits, Quell-/Overlay-Hashes und Compilerflags. Der Build ist **nicht deployed**.

| Rolle | Vorher und weiterhin aktive GameMP-SHA256 |
|---|---|
| Öffentliche Botclients | `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835` |
| Öffentliche Dedicated | `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208` |
| Dev Botclients, Cecil048 | `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530` |
| Dev Dedicated, selektive Powerups | `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0` |

Versionierte A1-Configpfade und Vorher/Nachher-SHA stehen in `poc/runtime/milestone-a-20261111/manifest.json`. Navbindung Dev unverändert: maps.txt SHA256 `a98c865c4b4aee3adc8a10b79dfd3bcc011d20df1a339921271d243921ee9c78`. Die Sanitized-Manifeste unter `milestone-a-20261111/` unterscheiden Beobachtungszeitpunkte. Runtime-Identitäten werden nach jedem abschließenden Neustart frisch zugeordnet.

## 3. Flotte und Aktivität

Snapshot 19:04 UTC, vor Dev-Rollback. Botnachweis durch eigene PLC4-Profile, Prozess-/Slot-Zuordnung und passende Query-Namen, nicht allein durch Spielerzahl. Weitere Slots bleiben UNKNOWN. GameSpy-Query jeweils Gameport+1.

| Port | Map | Eigene Bots | Weitere UNKNOWN | Slots mit verändertem Score in 7 Queries/30 s |
|---|---|---:|---:|---:|
| 25600 | Red Station | 8 | 0 | 6 |
| 25610 | Yodeller | 8 | 0 | 8 |
| 25620 | We Got Skulls'n'Bones Too | 8 | 0 | 2 |
| 25630 | Little Trouble | 8 | 0 | 6 |
| 25640 | Hole | 8 | 0 | 4 |
| 25650 | Red Station Dev | 8 | 2 | 4 |

Alle 42 Query-Samples beantwortet. Aktuelle Dev-Logs enthielten 121 CecilSpawn-Ereignisse. Score-/Respawnaktivität ersetzt weder Damage-Messung noch Sync-Freigabe. Sechs CPU-Stichproben über 30 s: 34,81–38,16 % Gesamtlast; mindestens 3,109 GiB verfügbarer RAM, rund 33 GiB frei. Keine kontrollierte Vorher/Nachher-Leistungsstudie. Vorläufiges Budget 25 % CPU-Reserve, 1,5 GiB RAM verfügbar, 8 GiB Disk; Tick-/Einzelkernspitzen und Langzeitverbrauch bleiben zu prüfen.

## 4. Tests und Sync-Rückschlag

183 Python-Tests bestanden; zusätzlich portable Arena-/Legacy-C++-Tests einschließlich ASan/UBSan im Implementierungs-Worktree. Ein unabhängiger Code-Review fand keine wichtigen neuen Defekte. Das sind keine Gameplay-Abnahmen.

Namensprüfung: 250 zusätzliche normalisierte sichtbare Namen ohne Kollision, 147 schlicht/45 Farbe/26 Bold/25 Italic/7 kombiniert, 0 Flash. Maximal 15 sichtbare Zeichen und 30 ASCII-Bytes. Seed 20261111; Pool-SHA256 `005cd7bbee01d2b24367f46401d2cf8bf4dae45db311f3cdfa35c789ca8d0dc2`. Original-Retail-Parserbelege stützen die verwendete Dekoration; `^f3` verschluckt im belegten Beispiel ein Zeichen und wird nicht neu verwendet. Acht Validator-/Allocator-Tests bestanden. Aktuelles natives Rendering und externe Formatabfrage der neuen Namen bleiben offen. Vier alte Live-Namen mit historisch problematischer Flash-Syntax wurden nicht stillschweigend ersetzt.

Spawn: sechs konditionale Sessionstart-Marker und Dev-Live-Shellmessung belegen die Konfiguration. **Kein Test beweist bisher Schaden ab dem ersten Respawnzustand**, für Bot oder Vanilla, nach Mapwechsel und Neustart. Eine Null im Shellwert reicht dafür nicht.

Kampf: Kandidat kompiliert; synthetisches Tracking lieferte 403/499/499 Schussticks. Dies beweist **keinen Vorteil DEMON gegenüber STARK** und keinen menschlichen Schwierigkeitsgrad. Drei native Vergleichsläufe mit vertauschten Starts, Damage-/Treffer-/Waffen-/Stuck-Messungen fehlen.

Dev-Sync: gesicherter Ausgangslog vor dem ersten A1-Versuch: 1 SYNCBAD, kein Sync-Disconnect. Nach korrigierter A1-Aktivierung: **36 SYNCBAD, 3 ausdrücklich bestätigte Disconnects**, verteilt auf zwei externe Verbindungen; beide erreichen zuletzt ab demselben Tick 260,66 den Grenzwert 10. Ein generischer Textscanner meldete zunächst 39 Treffer, weil er auch die drei Disconnectzeilen zählte. Botclientlogs zeigen keine entsprechenden Disconnects. Beide Dev-Stände hatten dieselbe serverseitige Powerup-Entfernung 2→0. Ursache und Zusammenhang mit Spawn=0 sind **nicht bewiesen**. Deshalb weiterer Rollout gestoppt und Dev-Config vorsorglich zurückgesetzt; Kickgrenzwert bleibt unverändert. Rohlogs/IP-Adressen bleiben privat. Öffentliche Logs hatten zum kontrollierten Prüfzeitpunkt keine entsprechenden Treffer; daraus folgt keine externe Langzeitfreigabe.

## 5. Vollständige Cecil-Mapmatrix

Cecil-Quelle: Commit `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c`; neun lokale Navdateien entsprechen den Git-Blobs des Originals. Acht installierte Welten in `SE1_00_Levels.gro` stimmen mit dem privaten Assetmanifest überein. Alle folgenden Weltpfade liegen unter `Levels\\LevelsMP\\Deathmatch\\`. Originalsuffix = Weltpfad-Hash; Welt-/Nav-CRC sind getrennt geprüft.

| Karte | Weltdatei / CRC32 | Navdatei / CRC32 | Bindung und tatsächliche Testgrenze |
|---|---|---|---|
| Desert Temple | nicht installiert | DesertTemple_E6B24B0F.nav / 0e3f2564 | Keine Bindung; gesperrt |
| Little Trouble | DM_LittleTrouble.wld / 4060d0dd | DM_LittleTrouble_6C64BF87.nav / 980013d4 | Gebunden; nur ältere Kandidatentests, keine aktuelle 048-Abnahme |
| The Lost Tomb | DM_TheLostTomb.wld / 618198ad | DM_TheLostTomb_AACB1C67.nav / 4f94f077 | Bindung, keine Funktionsabnahme |
| Fortress | Fortress.wld / 6a8768d6 | Fortress_5652374B.nav / 941478b1 | Bindung; Lava/Flüssigkeiten/Absturzrisiken ungeprüft |
| Hole | Hole.wld / 582bd040 | Hole_1AD627D0.nav / d7cac057 | 048: 600,008 s/595 Queries/8 Bots; numerisches Gate, funktionales Verdict fehlt |
| Compound | KuntaKinte.wld / 14288f5b | KuntaKinte_AFD9424F.nav / 9e90da19 | Bindung, keine Funktionsabnahme |
| Red Station | RedStation.wld / ff3776e0 | RedStation_5AF1A276.nav / e4571656 | 193 Knoten geladen; 048: 120 s/119 Queries, begrenzte Supply-Belege; keine Gesamtfreigabe |
| Skulls'n'Bones | WeGotSkullsNBonesToo.wld / 42d03dd2 | WeGotSkullsNBonesToo_9B573405.nav / 70b554dd | 048: 600,006 s/595 Queries/8 Bots; funktionales Verdict fehlt |
| Yodeller | Yodeller.wld / b3c8ceeb | Yodeller_FC72665B.nav / a4a7950c | Gebunden; ältere Tests, keine aktuelle 048-Abnahme |

**Keine dieser neun Karten ist für den neuen Kandidaten vollständig abgenommen.** Insbesondere Höhen, Teleporter, Sprünge, Gefahren, Itemzuordnung und Mapreset sind nicht allein durch Query-Zahlen belegt. Es gibt noch keine bestandene Cecil-Ersatzkarte, auf die die gesamte Flotte wahrheitsgemäß als freigegeben umgestellt werden könnte. Die fünf öffentlichen Maps bleiben auf ihrem bisherigen Stand.

Originalquellen geprüft: [Cecil BotMod](https://dreamycecil.itch.io/botmod), [Repository](https://github.com/DreamyCecil/CecilBotMod), [Wiki](https://github.com/DreamyCecil/CecilBotMod/wiki), [Navmeshes](https://github.com/DreamyCecil/CecilBotMod/tree/master/Cecil/Navmeshes). Original unterstützt Koop; unsere automatischen Kampfpfade sind weiterhin auf Scorematch/Fragmatch begrenzt. Monster, Follow und Kampagneninteraktion sind nicht freigegeben; keine neue Koop-Portierung.

## 6. Sicherung und Wiederherstellung

Vor Änderungen: alle relevanten Worktrees inventarisiert, uncommittete/ungetrackte Arbeiten separat archiviert, Git-Bundle, SDK-/Include-Bundles, aktive Laufzeiten/Buildquellen/Units/Configs/Nav/Spielerprofile gesichert. Lizenzierte Daten ausschließlich im privaten Projektbereich. Keine fremden Änderungen verworfen.

Ausgangsarchiv lokal 14.451.147.335 Bytes, SHA256 `e000af085e1248773f45420358633cec542f0f1214cd0244efba4738b331496a`. Separater Restore: **36.009 reguläre Dateien vollständig gelesen, geschrieben und erneut gehasht**, 4.290 eindeutige Inhalts-/Modusgruppen. 692 Symlinks/Sonderdateien sind im Restoreindex dokumentiert, wegen absoluter Wine-Pfade nicht materialisiert. Keine native Spielausführung aus dem Restore; Dateirestore ist keine komplette Betriebsabnahme.

Dedup-Restorearchiv 726.796.930 Bytes, SHA256 `862af28e291c9425f71a9eb2ec7290488a7d20513e3e4a088990a9b3e8afe689`, acht geordnete 96-MiB-Teile (letzter kleiner), Upload und Rückdownload aller acht größen-/SHA-identisch. Wegen Uploadlimits wurden zuvor größere Uploadversuche abgewiesen; diese gelten nicht als Backup. Companion enthält Wiederherstellungsanweisung, Datei-/Linkindex und Teilchecksummen.

Git-Ausgangsbundle SHA256 `754cafccfc8fb2222e796904ba1d8604b4b150118dfc19e86af496db0f9b53af`, ebenfalls zurückgeladen und geprüft. [Ausgangsbundle](https://drive.google.com/file/d/1oTTgKPOaUPcbqWGFUXEWh6EuiPTNP91F/view). [Privater Drive-Projektordner](https://drive.google.com/drive/folders/14HBTUlfJvyE821KnoHJhNGZ__4Ge2-y2). Abschließender Quell-/Kandidaten-/Config-Nachtrag und Remote-Commit-Nachweis im Handoff/Backupindex.

## 7. Abnahmestatus

| Bereich | Status |
|---|---|
| A1 | Öffentliche Config aktiv; Dev wegen Sync-Abbrüchen zurückgesetzt; Gameplay-Gate offen |
| A2 | Implementiert und portabel validiert; native Formatprüfung/Live-Ausrollung offen |
| A3 | Teilweise implementiert, gebaut und portabel getestet; nativer Vergleich/Verbesserungsnachweis offen |
| A4 | Neun Karten auditiert; keine vollständige Kandidaten-Whitelist |
| A5 / Gesamt-A | **NICHT ABGENOMMEN**, keine neue Release-DLL produktiv |
| B-Dev | **NICHT BEGONNEN**, harte Abhängigkeit A |
| B-Flotte | **NICHT BEGONNEN** |

## 8. Blocker und Fortsetzung

Beide bekannten Windows-/Shadow-RDC-Geräte waren offline (letzte Sichtbarkeit etwa 67 bzw. 38 Stunden zuvor); daher kein verfügbarer externer Vanilla-Windows-Client für die verlangten Render-/Damage-/Sync-Tests. Lokales Wine ist erreichbar und wurde für Build, Probe und Betrieb verwendet; fehlendes Windows blockiert nicht jede weitere lokale Untersuchung.

Zuerst Dev-Rollbackbeleg und erneute Synckontrolle prüfen. Dann auf isolierten eigenen Prozessen mit separatem Port eine kontrollierte Paarung Originalserver/selektiver Powerupserver × Spawn 3/0 × unveränderter Vanilla-/Botclient aufbauen. Gleiche Map/Actions, vollständige Server-/Clientlogs; erster divergierender Tick vor jeder weiteren DLL-Promotion. Fremde externe Spieler sind keine instrumentierten Testclients. Anschließend A1-Damage, Namenrendering, drei Kampfvergleiche, fehlende funktionale Mapverdicts und vorgeschriebene 3600/3600/7200-s-Gates. Erst nach vollständigem A und Backups B beginnen.

Nachtrag 19:15 UTC: Abschlussinventar bestätigt wieder 18 native Prozesse und je acht eigene Bots; Hole ein zusätzlicher UNKNOWN, Dev keine zusätzlichen Spieler. Dev nach Rollback bisher 0 SYNCBAD/0 Sync-Disconnects; kurze Kontrolle ohne externen Vergleichsclient, keine Ursachenbestätigung.


Abschließende Veröffentlichung: [Remote-Commit b6ae14e](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/commit/b6ae14e5497f6013bf198fad5cd105bfe658f05c), durch `git ls-remote` geprüft; Dateibaum `c6f5a8bb67add95267729edcd51d55c03cae8c71` exakt wie lokaler Commit `64aa881ff329809dd337dc47e98f82a009ac6a62`. HTTPS-Push hatte keine CLI-Credentials; Veröffentlichung erfolgte über den vorhandenen GitHub-Connector ohne Force. Deshalb unterschiedliche Commit-IDs bei identischem Baum. Beide Historien im Nachher-Bundle.

[Privates Nachher-Archiv](https://drive.google.com/file/d/1AY_m0ApX_XrUuvZTFE_vVDFPIDM2vhUG/view): 11.731.684 Bytes, SHA256 `4230396b834f64c74f8820f26f4438916af63085353407530a5857837dce9c27`; Rückdownload identisch, 283 reguläre Dateien separat geschrieben und erneut gehasht. Enthält Quellenbundle, nicht freigegebenen Build mit Overlay, Berichte, finale Live-Configs/Identitäten und private Restart-/Rollbackbelege. Kein nativer Start aus Restore. [Companion mit Restoreindex](https://drive.google.com/file/d/11EpEq1YqP7FDWiPLlb63eCGdHeYlMpeb/view), SHA256 `cc71d0cff6e8787d72001fc5174d06938fc885aab0fd5a6484c9171eadd9fd49`, ebenfalls rückgeprüft.

Letzte Kontrolle im beigefügten `final-sync-check.json`: alle 18 aktuellen Logs ohne SYNCBAD/Sync-Disconnect, Dev-Live-Shellwert wieder **3,0**, technische Locks frei und Probeunit inaktiv. Das löscht den gesicherten fehlgeschlagenen Test nicht und beweist ohne denselben externen Client keine Ursachenbehebung. A bleibt unvollständig.

## Fortsetzung: neue Implementierung und isolierte Native-Belege

Der volle Meilensteinauftrag bleibt aktiv. Der aktuelle Stand ersetzt die früheren Zwischenstände nur hinsichtlich der hier konkret nachgewiesenen Punkte:

- Alle250 neuen Namen wurden in einem neu kompilierten Probeprogramm tatsächlich durch Original-Retail-`Undecorated` und `LengthNaked` geprüft: alle sichtbaren Namen/Längen exakt. Vollständige Ergebnisse in `milestone-a-20261111/native-decoder-250.json`. Sichtbares GUI-Rendering und externe Namenabfrage bleiben noch offen.
- A3: realer Regressionstest fand Schussunterdrückung trotz ausgerichtetem Fadenkreuz bei bewegten Zielen. Finaler begrenzter Aimfehler und geordnete Antwortverstärkung10/14/20 korrigiert; gewöhnliche Itemziele unterdrücken geeigneten sichtbaren Kampf nicht mehr. Urgente Waffenbeschaffung bleibt erhalten. Siehe aktualisierten Kampfbericht.
- A4: tatsächliche alte Hole44s-/Skulls25s-Schleifen belegt. Neuer passiver Abbruch für festhängende erweiterte Itemtransits belässt Bewegungs-/Entity-/Map-/Gravity-Grenzen und ursprüngliche Fristen. Nach10s ohne0,75m neuen Bestdistanzgewinn wird nur das betreffende Item mit bestehendem30s-Backoff verworfen. Keine neue Bewegungsautorität. Siehe Itemtransitbericht.
- Integrierter Build002: Quelle3dc99dc75d3dcae22f9af18537d5df282c27f0e5, DLL `50b132c0d83d209b399c7178bcb41dc16c0ee1ffe7c28652cecbd69a07baafd5`, gebaut, **qualified=false**, ausschließlich isoliert. Main bestätigt183Python-Tests und1372Bridgechecks; unabhängige gegenseitige Reviews fanden keine wesentlichen neuen Defekte.
- Eigene routenlose Namespace-Kontrollen mit bestehendem Dev-Servermod, alter048 und unverändertem Retail-Client: jeweils320s mit Spawn3 und Spawn0, alle156Sessionbytes stets gleich in drei Prozessen, beide Läufe ohne SYNCBAD/Disconnect und vollständig normal beendet. Details `spawn-session-controls.json`. Keine erste-Tick-Schadens-/WAN-Ursachenfreigabe.
- Erster240s-Arenavergleich: Originalserver/Spawn0, vier alte048 gegen vier neueMITTEL-Bots, plus unveränderter Retail-Client,100 gültige Queries,0 Syncmeldungen/Abbrüche. Scoreänderung alte Gruppe+7, neue+25. Ein einzelnes Duellfenster liefert keinen allgemeinen Schwierigkeitsnachweis. Log-Schussaktionen sind keine separat zugerechneten Trefferdaten. Weitere Stufen mit vertauschter Joinreihenfolge folgen. CPU44,3–47,0% in der Stichprobe, mindestens2,37GiB verfügbarer RAM.

Die öffentliche Flotte hat weiterhin ihre alten DLLs; Dev weiterhin Spawn3 nach dem gesicherten Rückbau. B bleibt unverändert gesperrt bis zur Gesamt-A-Abnahme.


## Fortsetzung 20:22 UTC: Hole-Rückweg und Build004

Hole wurde nach neun SYNCBAD eines externen Clients, maximaler Zähler8, ohne beobachteten Disconnect vorsorglich normal neu gestartet und auf seine bytegenaue ursprüngliche Mapstartdatei zurückgesetzt. Baseline vorA1:0BAD/0Disconnect; gesicherter Spawn0-Lauf:9BAD/0Disconnect. Keine kausale Aussage. Frische Query und Prozess-/Inode-/Hashzuordnung bestätigen wieder acht eigene Bots und keine weiteren Spieler; tatsächlich gelesener Originalengine-Sessionwert3,0. Die bisherigen DLLs blieben erhalten, keine neue Kandidaten-DLL produktiv. Sechs Runtime-Identitätsdateien aktualisiert. Vier öffentliche Instanzen verbleiben auf Config0, Hole undDev auf3; A bleibt offen.

Diagnosecommit7e96f03 enthält ausschließlich standardmäßig abgeschaltete Itementscheidungsausgaben, unabhängig geprüft. Fehlende Waffenmetadaten werden ausdrücklich unbekannt statt als false markiert. Main bestätigte1406Bridgechecks mit SDK107 und ASan/UBSan. Build004 Quelle7e96f03, DLL SHA256 `43908fa08d7cb40c058fd03d455797feae8b40c9be4cf94667aa9ee179b14310`, build_oktrue/qualifiedfalse. Nur eigener isolierter Retail/Wine-Versuch, gleiche DLL mit Diagnostik aus/an; noch kein neuer Verhaltensfix, keine Freigabe aus Logs.
