# Public7fc gegen013 STARK: vollständiges instrumentiertes Kreuzpaar

In beiden abgeschlossenen120-s-Fenstern erzeugt Kandidat013 mehr zuordenbaren HP-Verlust und mehr tödliche Fremdtreffer als die tatsächliche Public7fc-Baseline. Das ist ein nativer STARK-Einzelpaarbeleg, **keine Gesamt-A3-, A1-First-State- oder Release-Abnahme**. Rohdaten bleiben privat; [JSON mit allen101 beobachteten Leben](2026-11-12-native-public013-stark-damage-pair.json) enthält auch erfolglose und zensierte Leben.

Originalserver/Vanilla bleiben unverändert. Kandidat SHA`3a8d84c9…`, Public`7fc94a39…`; Public nutzt seine kanonische HumanAI0-/AutoCombat1-Konfiguration. Physische Startgruppen wurden gekreuzt: Swap0 PublicA Slots0/2/3/4, KandidatB5–8; Swap1 KandidatA0/2/3/4, PublicB5–8; Vanilla jeweilsSlot1. Kohorten stammen aus tatsächlich geloggten Local-/Global-Slots und allen neun nativen Entity-/Pointerbindungen, nicht aus Inventar-Samplinggruppen.

| Vollständiger Lebensnenner | Swap0 Public | Swap0 Kandidat | Swap1 Public | Swap1 Kandidat |
|---|---:|---:|---:|---:|
| Beobachtete Leben |36|15|31|17|
| Tod / Fensterzensierung |32 /4|11 /4|27 /4|13 /4|
| Lebend nützliche Waffe besessen (`0x3df8`) |1|11|7|13|
| Beendet ohne nützlichen Besitz |31|2|21|3|
| Zensiert ohne nützlichen Besitz |4|2|3|1|
| Nützliche aktuelle/besessene Waffe |1|11|5|13|
| Nützliche aktuelle Waffe mit Fire-Request |0|9|0|12|
| Erstbesitz-Median, nur erfolgreiche Leben (s) |1,150|5,950|8,850|8,400|
| Spätester Erstbesitz (s) |1,150|13,500|30,951|31,600|
| Letzter Query-Fragdelta |+14|+26|+11|+28|

Zusammen: Kandidat24 Erwerbe in32 Leben, fünf abgeschlossene und drei zensierte Leben ohne Erwerb; Public8 in67,52 abgeschlossen und sieben zensiert ohne Erwerb. Es gibt keine ausschließlich als Leiche beobachteten Leben. Die beiden zusätzlichen Vanilla-Leben enden jeweils ohne Erwerb; sie sind in den101 Leben enthalten, getrennt von den99 Botleben. Ein erfolgreicher Legacy-Median ist wegen der vielen erfolglosen Leben kein All-Life-Geschwindigkeitsvorteil. Kandidatenspezifische CecilSpawn/Death/Pickup-Ereignisse stimmen pro Leben vollständig mit dem nativen Inventar überein. Besitz und Fire-Request sind verschiedene Nachweise; Fire-Requests sind weder abgefeuerte Projektile noch Treffer.

Die ersten Kandidatenleben erwerben in Swap0 nach3,850/4,050/11,300/10,350 s, in Swap1 nach2,400/10,900/10,500/13,200 s. Alle acht ersten Public-Leben enden ohne nützlichen Besitz. Längster Kandidatenerwerb: Swap1 local1/Slot2/Leben2, Spawnclock20,949966, Erstbesitz31,599518 s später; erste nützliche aktuelle Waffe nach36,149448 s, Fire-Request nach36,349445 s. Diese Verzögerung ist erhalten; dieses Berichtspaar erklärt oder behebt sie nicht. Zeiten stammen aus ursprünglichen Server-Spieluhren, nicht aus pauschal `clientTick*0.05` als Wanduhr.

| Validierte lebende bekannte Fremd-Damagecalls | Swap0 Public | Swap0 Kandidat | Swap1 Public | Swap1 Kandidat |
|---|---:|---:|---:|---:|
| Aufrufe |59|93|53|82|
| Tatsächlicher HP-Verlust, auf Vorhit-HP begrenzt |2049,170|2418,830|1798,892|2432,064|
| Tödliche Aufrufe |15|27|12|28|
| Unbegrenzter HP-Verlust einschließlich Overkill |2335,000|6826,280|2048,253|3755,135|

Gesamt: Kandidat175 zugeordnete Aufrufe,4850,894 begrenzter HP-Verlust und55 tödliche Aufrufe; Public112/3848,062/27. Gezählt werden Nicht-Selbsttreffer auf alle anderen Spieler, einschließlich Gegner derselben KI-Kohorte und Vanilla; es sind keine Teams. Die stärkere Overkill-Summe ist kein zusätzlicher lebender Schaden.

Der vollständige Hooknenner lautet Swap0 **242 =152 bekannte Fremdaufrufe+88 Leichenaufrufe+1 Selbstaufruf+1 unzuordenbarer Inflictor**; Swap1 **179 =135+36+5+3**. Es gibt keine außerhalb/über die Fenstergrenze reichenden Records. Jeder Record wurde erneut auf fortlaufende sequence/total_sequence, Hauptthread/TLS, kein Overlap, gepinnten Victimpointer, positive unveränderte Lebensuhr, gleiche CurrentTicks und endliche HP/Armor geprüft. Unbekannte/Selbst-/Leichenereignisse werden nicht auf eine Schützenkohorte umgelegt.

Public verwendet bei diesen Fremdtreffern ausschließlich DamageType4/BULLET. Kandidat Swap0:74 BULLET,12 PROJECTILE,2 EXPLOSION,5 CANNONBALL; Swap1:56/17/9/0. Retail107-Header`Engine/Classes/BaseEvents.h:108–120` definiert1/2/4/12; `Player.es:924–940` erklärt die entsprechenden nativen Todesmeldungen. Die42 bzw40 Fremdkillmeldungen des am Fensterende archivierten `server.log` stimmen **für jedes Schütze-/Opfer-Slotpaar exakt** mit sämtlichen tödlichen Fremd-Damagecalls überein. Query-Fragdeltas haben einen früheren letzten Abtastzeitpunkt und sind nicht die Killmeldungssumme. Der spätere Swap0-Closed-Log enthält zwei weitere Cleanup-Kills; sie gehören nicht zum Hookfenster und werden nicht hinzugerechnet.

Beide Original-Initialreferenzreplays wurden über alle Inventarproben erneut ausgeführt: unveränderte raw-first/first-neutral-Archive, keine pending errors und alle neun neutralen Positionen/Richtungen exakt gleich der Referenz. Die kanonischen Kohortenkonfigurationen wurden erneut bytegenau erzeugt. Alle Inventarproben tragen dieselbe gepinnte Server-PID/start-Identität und die drei Original-Hashes. Die vier Closed-Log-Hashes/Längen pro Fenster stimmen, keine Syncbad-/Disconnect-/Crash-/InvalidAction-Muster; normale vierfache Schließung und vollständige Dateirestaurierung sind archiviert. Hookzähler242/242 bzw179/179, volle Fensterüberdeckung, keine Faults/Drops/unknown-victim/non-main/in-flight/detach-errors; ursprüngliche22 Getter- und1395 Damagebytes wurden laut den endgültigen Root-Receipts restauriert. Die Dateianalyse startet selbst keine Runtime.

Die Fenster dauern120,117857 und120,029329 s. Gemessene Host-CPU-Intervallmaxima69,195%/60,444%, minimale verfügbare RAM1.989.459.968/1.948.762.112 Bytes; keine gemessene Grenzverletzung. Das ist kein kontinuierlicher Peaknachweis: Startvorbereitung hat47,329/46,445 s Samplinglücke, während Gameplay beträgt die größte Lücke1,757/1,770 s. Controllerverbrauch25,773/25,545 CPU-Sekunden und MaxRSS167772/166988 KiB; Originalserver4,88/4,78 CPU-Sekunden. Diese beiden instrumentierten Fenster isolieren keinen kausalen Hookoverhead gegenüber einem uninstrumentierten Kontrolllauf.

In beiden Fenstern bleiben SameSpawnTick-HP-Witnesses **0**, FirstProcessedState **false**. Weitere Tier-/Startplatzpaare, vollständige A4-/Langzeitbelege und die offenen A1-Kriterien bleiben eigenständige Grenzen. Private Auswertung: `/srv/tse-combat-a3-stark-pair-audit-20261112`; sämtliche Parser/JSON-Prüfungen unter eigener CPUQuota25%/Nice10-Unit. Skript-/Eingabehashs im JSON, keine Rohkonfigurationen, Namen, GUIDs oder Speicheradressen veröffentlicht.
