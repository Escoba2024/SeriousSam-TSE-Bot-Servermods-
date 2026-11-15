# Eigener Original-Coltfall auf Little Trouble – prospektiver Entwurf

Nur Design, keine Implementierung oder Runtimefreigabe. Claim: diese neue Spec,
zugehöriger kurzer Plan und private Quellenquittung. Die alte Festziel030-
Bedingung und F3 bleiben FAIL:84 Ownershipcaptures,83 vollständige Frames über
23,721479s, Original immer HP100/MayRespawn0,kein DEAD_READY. Kein Budgetretry.

## Ein empfohlener Aufbau und seine echte offene Grenze

Neue Bedingung `ORIGINAL_RESPAWN030_COLT_LITTLE_TROUBLE_V1`: unveränderter Original-
Dedicated, unveränderter Originalclient als Opfer global0, genau ein normaler
Build030-Bot global1. Ein normal geladenes Retail `DM_LittleTrouble.wld`, normale
Join-/Deathmatchspawns, keine Markerwahl, kein Spawncheat oder HP/Pose/Winkelwrite.
Bot-TestTarget0 bleibt die vorhandene explizite Colt-Select-Bedingung. Als klarer
neuer Configdelta MoveFactor1→0 vorschlagen, damit nach vorhandenem geometrischem
AimReady kein direkter Lauf gegen die Karte beginnt. Das ist kein Positionsfreeze:
Build030 `TestJump(tick)` bleibt tick%80<4 und muss mitbeobachtet werden.

Little Trouble ist der kleinste bereits im vorhandenen Fünfmap-Katalog gebundene
Navgraph (110Knoten). Seine Navausdehnung103,25×8,005×89,5m beweist weder offene
Fläche noch freie Spawn-Sicht. **Kein vorhandenes Manifest belegt eine bestimmte
frei verbundene Spawnpaarung.** Vor einem Methodenfall ist deshalb ein eigener
Root-Admissionbeleg nötig: tatsächlich geladene Karte, beide echten normalen
Spawnpositionen/Actor-Life-Bindungen und visuell eindeutig freie Schussachse in
der eigenen Instanz. Unklare/verdeckt liegende Spawns: vor Arm FAIL, kein neuer
Join-/Spawnwurf, kein geometrisches PASS aus Navknotenabständen. Ein Screenshot
ersetzt keine Kollision-/Hitkette; positiven Treffer beweist später ausschließlich
die vollständige beobachtete Colt→Bullet→Cast→Direct→Receive-Kette. Ohne diesen
Admissionbeleg ist auch dieser konkret benannte Kandidat NICHT native-ready.

Zusätzliche normale Originalbewegung wäre unter dem Nutzerauftrag zulässig,
aber eine weitere explizite Vorbereitungsbedingung mit Down/Up/Neutral/Fokus/ACK
und48/96/85/90-Budgets. Sie wird hier zunächst vermieden. Falls die normale
Spawnpaarung keine prüfbare Sicht zulässt, nicht blind starten: Root muss eine
konkret geometrisch begründete normale Aufstellungsvorbereitung separat festlegen.
Kein Live-/Userclient, keine Wiederholung stationärer AI-only-Fenster ohne Beleg.

## Tatsächlich vorhandene Assets und Startpfade

| Gegenstand | Vorhandener Pfad / Pin |
|---|---|
| Mapkatalog | `/srv/tse-nav20-030-skulls600-diag1-timestamps-disabled-20261115/map-catalog.json`, SHA11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3 |
| World | `Levels/LevelsMP/Deathmatch/DM_LittleTrouble.wld` in `/srv/tse-development-live-20261107/server/SE1_00_Levels.gro`;1104924B, SHAe74e48e99bcc6e945500e1f28921c443515898791bfbca4d7ebf1ae61a26593c, CRC4060d0dd |
| Nav | `/srv/tse-cecil-full-private-assets-20261107/DM_LittleTrouble_6C64BF87.nav`;6618B, SHA252d7e4c003804fe9ae2afef359843feb39b5dda29c1d6eadb0835fbe64a30ac, CRC980013d4,110Knoten |
| Maps/Settings | dasselbe Verzeichnis `maps.txt` SHAa98c865c4b4aee3adc8a10b79dfd3bcc011d20df1a339921271d243921ee9c78 und `settings.txt` SHA997ba93194bb1ae76632819184effdbb5e894636ccf57940beca4b09ba6b287a |
| Eigentumsbeleg | `asset-manifest.json` SHA49d19a2c010f1fbbb1c4e7f6e71687f4e062a26fa088970ce6815c871296c100; vorhandener Mapbuilder `tools/prepare_navigation_build024_maps.py` als Inversenvorbild, NICHT ausführen |
| Tatsächlich aktiver Start | `/srv/tse-arena-isolated-20261111/server/Scripts/Dedicated/BotTest/1_begin.ini`, SHA866030fd89efaadf2e7168a528d7d332f53d783a5d076aef9f0c298332e51d8f |

Worldentry und Nav wurden frisch NOATIME/NOFOLLOW gegen diese Pins geprüft.
Archiv enthält für Little Trouble nur WLD und Thumbnail, keine separate
Spawnkonfigurationsdatei. Ob/wo die WLD-Spawnmarker freie Sicht haben, bleibt offen.
`Player.es:4895–4958,5163–5169` beschreibt Auswahl unter entfernten Deathmatch-
Markern, keinen normalen festen Slot→Marker-Schalter; Source allein ist kein
neuer Retail-ABI-Nachweis. Keine zufällige Wiederholung als versteckte Suche.

Aktuelles tatsächliches Startscript nennt StartMode2,StartDifficulty3,
InfiniteAmmo1,SpawnInvulnerability0 und RedStation. A1 hat hier keine Hard2-
Qualifikation. Neuer transaktionaler Delta nur ded_strLevel→LittleTrouble,
neue Config Move0 und korrespondierende Map-/Nav-/Scopepins; diese effektiven
Startflags sonst ehrlich beibehalten. Mapstarts vor NewGame prüfen. NAI hat
expliziten RedStation/193/CRC-Guard: nur exakte neue Kartenbedingung mit ganzen
Sourceinversen, kein Allowlist-Fallback. Beide Reader/Core/ABI-Sites unverändert.

## Warum nicht einfach AutoCombat statt Festziel?

Gepinnter Driver030 SHA7af47d87aaaf4c51ebaca6f65d628cfec3c2544419be07e39b65e52b370eb386:
:1182 macht TestTarget0 zu automatic=false. :1427–1441 geometrischer Aim ohne LOS;
:1451/1491/1550 deshalb keine Nav-/SafeMotionroute. :1529–1543 periodisches Feuer,
:1621 Colt. Sourcevis0/target-1/shots0 sind in diesem Zweig kein LOS-/Fireverbot.

Alternative TestTarget-1 benötigt HumanAI0 **und** SupplyNavigation0, um den
älteren generischen Entscheider zu wählen (:1182–1183,1326). Der hat echte
BotCombatVisible-Filter und `SelectWeapon`-Prioritätslisten
(`bot_combat.h:38–72`, `botcore_ai.h:132–142`). Bei ausschließlich Knife+Colt
kann Colt gewählt werden; spätere Aufnahmen können andere Waffen gewinnen.
Kein vorhandener geprüfter Colt-only-Configschalter wurde belegt. HumanAI0
allein reicht wegen `humanMode=HumanAI||SupplyNavigation` nicht. Deshalb nicht
als erzwungene Coltbedingung empfohlen; kein stiller anderer Waffenvertrag.

## Ablauf und unveränderte Abnahmegrenzen

Nach spezifischem Admissionbeleg: tatsächlichen normalen Bot-Tod vor Arm
beobachten oder bounded FAIL. Original neutral; echtes DEAD_READY/MayRespawn2 mit
unveränderten Doppelreads. Nach Arm/TLS genau ein reales FireDownUp mit tatsächlichen
Hold-/Release-/ACKzeiten; keine Aim-/Gainkalibrierung voraussetzen. Init nach Arm,
erster valider Tick sowie normale und tödliche bekannte Colt-Ownerketten müssen
im echten Fenster vorhanden sein, sonst INCOMPLETE. Erste gültige Schadenstate-
Abnahme bleibt gesondert; Beispiele können ausdrücklich nur später sein.
Native10s/TTL15/Queue64/16384/38Restore/ACK2s/Hold.35/.2s8/85inner90outer unverändert.

## Neue operative Metadatenreserve, keine Schadenstoleranz

Beobachtete minimale Framedauer0,134001s ergibt für85s rund635Reads nur als
Kapazitätsmodell, **nicht** als garantierte Mindestdauer. Harte Obergrenze bleibt
1024 einschließlich Initialframe. Tatsächliches F3-Maximum27013B×1024≈26,4MiB;
neue Map/Logwachstum können davon abweichen. Alter allgemeiner Einzelcap1,5MiB
mal1024 wäre1,5GiB und ist kein sinnvoll unbemerkt verfügbarer Platz.

Vorschlag nach separater Sourceprüfung: maximal512MiB Ownershippayload,
O_EXCL0600/frische0700Serialverzeichnisse unverändert; weiterhin vollen alten
1,5MiB vor jedem Callback reservieren. Ein konservativer neuer serialisierter
Beleggrößennachweis muss vor Code übernommen werden: Log≤65536Rohbytes mit
maximal6-fachem JSONescaping (=384KiB), GMS≤4096Bytes→8KiBHex, übrige fest gepinnte
Felder/JSON inklusive konkreter PID/start-Längen≤24KiB: zusammen≤416KiB.
1024×416KiB=416MiB; plus1,5MiB letzter Vorbehalt und begrenzter Index <512MiB.
Ein Überschreiten wäre weiterhin FAIL mit erhaltenem Rohbeleg, kein Truncation-
PASS. Dieser Nachweis benötigt gezielte maximale Escape-/Feldtests, nicht das
Umbenennen des alten Grenzwerts. Alternative vollständiger alter Maximalvertrag
würde1,5GiB Reserve verlangen; keine schnellere Readlatenz als Ersatzbeweis.

Disk vor Start mindestens8GiB+64MiB Sicherheitsreserve+512MiB neue Metadata+
bestehende512MiB Rawjournal =9730785280Bytes, **zuzüglich** konkret gebundener
Snapshots/Screenshots/sonstiger Sidecars und Forkgröße. Kein Preflight, solange
diese Zusatzgrößen ungeklärt oder der Platz nicht wirklich frei ist. Kein
Speicherretire durch Autor. Resource75%/1,5GiB/8GiB bleiben bindend. Ein größeres
Metadatenbudget allein rechtfertigt keinen F4 und keinen Damage-PASS.
