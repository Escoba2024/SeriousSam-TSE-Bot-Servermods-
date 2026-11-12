# A1: belegbare Spielerflags und die Grenze des First-State-Witness

Read-only Originalanalyse, keine Runtime und keine Änderung der Damage-v2. Ergebnis: `m_ulFlags` lässt sich im bestehenden Damage-Snapshot mit belegtem Retail-1.07-Offset lesen. Daraus entsteht ein genauerer Verbindungs-/Actionphasenbefund, **kein eindeutiger Nachweis des ersten vollständig verarbeiteten Respawnzustands**. `same_spawn_tick_health_decrease` und `first_processed_state_proven` bleiben verschiedene Aussagen; Letzteres bleibt false.

## Verifizierte Originalgrundlage

Original `EntitiesMP.dll` SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`, bevorzugte Basis `60310000`. SDK107 `Sources/EntitiesMP/Player.es` SHA256 `85c92933fa5b0cc726be7b42a3bc82d4c95b255507ec8b1fffe2666fcf3888af`. Beide Hashes wurden erneut geprüft; PE-Disassembly wurde ausschließlich aus der Originaldatei gelesen. Kein 1.10-ABI oder Scheduler wurde übernommen. Die Adressen unten sind bevorzugte virtuelle Adressen, keine behaupteten aktuellen Prozessadressen.

SDK-Zeilen230,237,238 definieren INITIALIZED=0x1, APPLIEDACTION=0x80 und NOTCONNECTED=0x100; Zeile998 deklariert `m_ulFlags`. Der Offset wird **nicht** aus dieser Deklarationsreihenfolge geschätzt: fünf originale Zugriffsstellen benutzen übereinstimmend DWORD `this+0x380`.

| Originalpfad | Zugriff und Reihenfolge | Aussage |
| --- | --- | --- |
| InitializePlayer, SDK4964–5000 | `60402cc7` lädt `+380`; `60402cd5` maskiert mit0xA01; `60402cdc` speichert. Danach `60402d8d` setzt ENF_ALIVE, `60402da9` ruft TeleportPlayer. | APPLIEDACTION und NOTCONNECTED werden beide gelöscht; INITIALIZED bleibt erhalten. Das ist noch kein erster fertig verarbeiteter Action-/Bewegungstakt. |
| ApplyAction, SDK3567–3578 | `603fe91e` lädt `+380`; `603fe924` prüft INITIALIZED, `603fe92c` NOTCONNECTED; gegebenenfalls SetConnected; `603fe941/94b` setzt/speichert APPLIEDACTION. | Das Bit wird am **Anfang** der Actionverarbeitung gesetzt, bevor Rotation, Buttons und AliveActions/DeathActions verarbeitet werden. Es beweist keinen Rücksprung aus ApplyAction. |
| SetConnected, SDK2788–2798 | `603fc543` lädt `+380`, `603fc54e/551` löscht/speichert0x100; anschließend Physik/Kollision aktivieren. | Kein ausschließliches erstes Lebensereignis: InitializePlayer hat0x100 bereits gelöscht. |
| PostMoving, SDK2717ff/2757–2764 | `603fc45f` prüft0x80; ohne Bit SetUnconnected; `603fc475/477` löscht/speichert0x80. | Das Bit ist ein wiederverwendetes Actionindikatorbit, kein monotoner Lebens-/Taktzähler. Mit vorheriger Action kann PostMoving verbunden enden, obwohl0x80 danach null ist. |
| SetUnconnected, SDK2768–2785 | `603fc499` lädt `+380`; `603fc4a8/4ac` setzt/speichert0x100; danach ForceFullStop und reduzierte Physik/Kollision. | Belegt den Ausschlusszustand; eine bloße Physikzahl ersetzt die Originalflagprüfung nicht. |
| ReceiveDamage, SDK3013–3042 | `603fd3e5`: `8b 86 80 03 00 00`; `603fd3eb`: `f6 c4 01`; `603fd3ee`: früher Return bei gesetztem0x100. | Der bereits unveränderte volle1395-Byte-Damagefingerprint enthält genau diesen Offset und den tatsächlichen Ausschlusszweig. Kein neuer Hook-/Guardbereich nötig, um den Feldbeleg zu begründen. |

Der Spawnclock-Store liegt weiterhin in TeleportPlayer bei `604039c8` nach Original-CurrentTick. Spawnclock ist keine Actionanzahl. SDK3680ff wählt nach Aliveflag AliveActions/AutoActions oder DeathActions; DeathActions4391ff löst nach regulärer FIRE-Loslasskante EEnd aus, der Todeszustand liefert ERebirth, Rebirth5873ff ruft InitializePlayer. Die vollständige Original-Engine-Ereignisreihenfolge relativ zu allen Waffen-/Bewegungsereignissen ist dadurch nicht bewiesen.

## Was „erster verarbeiteter Zustand“ mindestens benötigt

Für einen ordinalen First-State-Nachweis muss derselbe reale Serverlebenslauf ab seiner Respawninitialisierung vollständig verankert sein. Es muss zusätzlich die **erste** maßgebliche abgeschlossene serverseitige Verarbeitung dieses neuen Lebens beobachtet werden. Ein Zustand muss dabei derselben Entity/World/Session und positiven Spawnclock angehören und lebend/initialisiert/verbunden sein. Ein vorgelagertes Action-Eintrittsbit genügt nicht als Abschlussmarker. Weder eine später ausgewählte erste Pollprobe noch der erste Damageaufruf definieren nachträglich diesen Anfang.

Die einzelnen Originalgrenzen bleiben verschieden: InitializePlayer-Abschluss, ApplyAction-Eintritt/-Abschluss und PostMoving-Abschluss. Die vorliegenden Daten enthalten keine lückenlose Folge dieser Grenzen pro neuem Leben. Deshalb wird hier keine davon stillschweigend als neuer Ersatz für die geforderte erste serververarbeitete Phase eingesetzt. CurrentTick==Spawnclock kann einen tatsächlichen Treffer im Spawn-Takt belegen, aber keine Reihenfolge mehrerer Unterphasen desselben Takts.

## Gegenbeispiel zur Eindeutigkeit der Bits

Betrachtet man nur INITIALIZED/APPLIEDACTION/NOTCONNECTED, sind zwei verschiedene gültige Geschichten ununterscheidbar:

- Unmittelbar nach der Originalinitialisierung:1/0/0.
- Nach einer späteren Action mit anschließendem PostMoving, das die bestehende Verbindung erhält und APPLIEDACTION löscht: ebenfalls1/0/0.

Auch1/1/0 kann sowohl im ersten als auch in einem beliebigen späteren Actiondurchgang vorkommen und wird bereits vor dessen Abschluss gesetzt. Eine vollständige Damagehook-Coverage schließt unbeobachtete **Damageaufrufe** aus, nicht vorherige Action-/PostMoving-Zustände ohne Damage. Selbst ein seit dem vorigen Tod durchgehend aktiver Damagehook liefert daher keine vollständige Lebensphasenhistorie. Initialisierung kann das zuvor im auslösenden Actionpfad gesetzte Bit wieder löschen; die konkrete Ereignisverschachtelung wird nicht erraten.

## Minimaler sinnvoller Zusatz im vorhandenen Callback — nur Messvorschlag

Eine spätere ausdrücklich versionierte Änderung könnte in `snapshot.take()` lediglich `player_flags: p.add(0x380).readU32()` ergänzen. Damit greifen die bestehenden zwei Reads und Gleichheitsprüfung pro entry/leave auch für dieses Feld: vier zusätzliche skalare Loads pro passendem Damageaufruf, keine zusätzlichen Adressauflösungen, Hooks, Rays, RNG, NativeFunction oder Writes. Unknown-Victims bleiben vor jedem Dereferenzieren ausgeschlossen. Das neue Feld müsste offen im Record-/Snapshot-Schema, Manifest und Negativtests ergänzt werden; die eingefrorene Damage2-Version wird nicht still geändert.

Der zulässige neue Befund wäre: „Dieser tatsächlich beobachtete normale Fremd-Damageaufruf traf ein initialisiertes verbundenes Spielerobjekt; seit dem letzten Flagreset war beim Eintritt eine Action begonnen worden“ — sofern INITIALIZED1/NOTCONNECTED0/APPLIEDACTION1 tatsächlich gelesen werden. APPLIEDACTION0 bedeutet ausdrücklich weder „noch nie verarbeitet“ noch „nicht angreifbar“. Bei NOTCONNECTED1 lässt sich die konkrete Original-Ausschlussbedingung sehen. Vorher/nachher rohe Flags bleiben getrennt; ein tödlicher Treffer darf nicht durch einen nachträglichen Alivefilter verschwinden.

Für eine echte Schadensaussage bleiben zusätzlich die bisherigen Original-TLS-/SameLife-/SameTick-/Overlap-/HP-/bekannter-fremder-Inflictor-/DMT_BULLET4- und vollständigen Cleanup-/Denominatorgates erforderlich. Ein zusätzliches bereits bekanntes Entityflag ENF_ALIVE liegt separat bei `+0x10`; es darf nicht mit den Spielerflags `+0x380` verwechselt werden. HP>0 und PlayerFlags allein werden hier nicht als vollständig bewiesenes Alive-Engineflag ausgegeben.

**Grenze:** Ohne eine verifizierte vollständige Lifecycle-Grenzbeobachtung oder einen beweisbar monotonen vorhandenen Original-Lebensphasenmarker kann der ausschließlich bestehende Damagecallback keinen zuverlässigen First-State-Witness liefern. Die statische Prüfung findet hier keinen solchen Marker. Ein zusätzlicher SetConnected-Hook allein würde diese Lücke ebenfalls nicht schließen. In diesem Auftrag wurden weder neue Hookstellen vorgeschlagen implementiert noch Runtime gestartet; es gibt nur den begrenzten, belegten Flags-Messvorschlag und die präzise offene Beobachtungsgrenze.

## Reproduktion

Private statische Artefakte liegen im eigenen Verzeichnis `tse-combat-a1-firststate-static-20261112`: read_static.py, vier begrenzte Disassemblies und static-proof.json. Der Reader prüft die exakten Original-/SDK-Hashes und den Offsetzugriff zusätzlich gegen den bereits eingefrorenen vollständigen Damageguard. Ausführung ausschließlich lesend in eigener CPUQuota25%-Unit, kein Compiler/TSE/Prozessattach. Rohdisassembly/Originalbytes bleiben privat; dieses Dokument enthält nur erforderliche Adressen und eine kurze Identifikationssequenz.
