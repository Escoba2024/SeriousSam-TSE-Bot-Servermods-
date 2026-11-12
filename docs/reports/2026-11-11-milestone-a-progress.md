# Meilenstein A: implementierter Zwischenstand, keine Gesamtfreigabe

## Fortsetzung 12.11.2026, 00:54 UTC

Zwei echte Public012-MITTEL-Vergleiche mit vertauschter Kohortenzuordnung sind abgeschlossen: 240,058 s und 240,037 s. Beide liefen ohne beobachtete Syncfehler; alle vier Rollen wurden regulär geschlossen und ihre erst danach archivierten Logs bestanden die Prüfung. Alle neun ersten neutralen Startbeobachtungen passen exakt zur unveränderten Referenz. Keine atomare Erstzustandsmessung. Beleg: `milestone-a-20261111/public012-mittel-pair.json`. Die vollständige Lebens-, Waffen- und Scoreauswertung läuft separat. Erste Swap0-Auswertung: Kandidat 19 von 23 Leben mit nützlichem Waffenerwerb, Legacy 7 von 38; letzter beobachteter Fragzuwachs Kandidat20, Legacy26. Verbesserter Erwerb ist damit noch kein Nachweis stärkerer Kampflogik. STARK/Swap0 läuft jetzt mit demselben unveränderten Controller; sein Ergebnis ist offen.

Originalchronologie für A1 ist nun statisch gegengeprüft: InitializePlayer löscht NOTCONNECTED und APPLIEDACTION; erst PostMoving kann ohne Aktion SetUnconnected aufrufen. Ein späterer SetConnected-Aufruf wäre daher kein vollständiger Beobachter des ersten angreifbaren Fensters. Das echte Spawn-Tick-HP-Kriterium bleibt bestehen. RespawnInPlace ist im normalen DM-Todespfad kein geeigneter Wiederholungshebel. Ein neuer begrenzter DM-Versuch mit normalen FIRE-Loslassaktionen und unveränderten Spawnmarkern wird vorbereitet; noch keine neue A1-Abnahme.

Breiterer privater JumpFromBouncer-v3-Entwurf wurde unabhängig ohne wichtige/kritische Befunde geprüft. Root hat eine neue Controllerkopie mit vorab gehashten Abhängigkeiten, strengem Identitätswartehelfer, Brush-Registry, Ereignisfolge-/Threadprüfung und tatsächlich ausgewertetem Stop-/Detach-/Byte-Restore-Abschluss vorbereitet. Elf gezielte Batchtests bestanden. Der Controller selbst ist noch im Gegenreview und wurde nicht ausgeführt. Weder zusätzlicher Hookpunkt noch Gameplayänderung. Die Laser-Endkontakt-/Reakquisitionsursache bleibt offen.

A ist unvollständig; B bleibt unbegonnen. Keine neue A-DLL und keine neuen Namen sind produktiv. Letzte frische Flottenprüfung bleibt 00:33:58, keine neue Betriebsbehauptung aus späteren Labortests. Neuere Änderungen seit Remote fd847e6 und Drive-Delta011 werden im nächsten Nachtrag gesichert. Die formalen 3600/3600/7200-s-Gates bleiben offen.

## Fortsetzung 12.11.2026, 00:38 UTC

Der Gesamtauftrag A→B bleibt aktiv. A ist nicht abgenommen; B wurde nicht begonnen. Keine neue A-DLL und keine neuen Namen sind produktiv. Die frische Prüfung00:33:58 bestätigt sechs Instanzen mit je acht eigenen Bots und keinen zusätzlichen UNKNOWN. Public5: aktuelle Logs0BAD/0SyncDisconnect. Dev: unverändert21BAD/2SyncDisconnect. Verfügbarer RAM2,53GiB, Disk21,83GiB. Beide Windows-Testgeräte sind weiterhin offline; lokale Wine-Belege ersetzen keine externe Windows-/WAN-Abnahme.

Kandidat012 ist gebaut: Quelle2275ae2ad37c98d8153015e82fc9c90d9269fab9, DLL e049557795e85a5b6676612500ee93c23f4d61233eead757f43b4e8d6bff43c0, qualified=false. Root wiederholte2526 SDK107-ASan/UBSan-Prüfungen und den Driver-Actiontest erfolgreich. Enger Fix nur für denselben Update-Aufruf beim qualifizierten8/11→12→34-Übergang; spätere Flugaktionen unverändert. Erstes natives012-Fenster120,11s sauber geschlossen/Postclose sauber, ein echter234-Aufruf und eine Minigunaufnahme. Der neue positive Arrival-UP-Fall wurde darin nicht ausgeübt,11→12 ebenfalls nicht. Längste Waffenaufnahme77,60s und Laser-Endkontakt-/Reakquisitionsproblem bleiben offene Gameplay-Befunde, keine Gesamtfreigabe.

Public011s alter Positions-FAIL bleibt erhalten. Gleicher Spawn-Tick enthält nachweislich zwei originale Verbindungs-/Gravityphasen; v3 des Vergleichsqualifikators hält rohe erste Probe, alle ungültigen Zwischenbeobachtungen und die erste neutrale Probe getrennt fest. Position/Yaw bleiben exakt, keine Koordinatentoleranz. Unabhängiger Gegenreview und Root29Tests bestanden. Der erste Public012-v3-Lauf scheiterte anschließend schon an transientem CWD während BotB-Start; dessen unidentifizierter Restprozess wurde erst nach frischer vollständiger PID-/Start-/Cgroup-/CWD-/Modulprüfung regulär geschlossen. Kein Force, keine fremde Session, ursprünglicher FAIL unverändert. Neuer strenger Wartehelfer aus7600ccf: Root12Tests plus9Finalizer-Tests bestanden, keine Identity-Lockerung. Public012-v4 mit diesem Helfer läuft jetzt als erster vierminütiger MITTEL/Swap0-Vergleich; alle neun neutralen Startproben passen exakt. Noch kein abschließendes Ergebnis.

A1: erster echter privater Damage-v2-Lauf30,087s,52 vollständige Aufrufe,0Fault/Drop/Detachfehler, volle Originalbytes nach Detach restauriert. Keine HP-Abnahme exakt im Spawn-Tick und keine erste-Zustand-Abnahme. Originale NOTCONNECTED-/SetConnected-Reihenfolge wird gesondert geprüft, um den ersten tatsächlich angreifbaren Zustand korrekt zu definieren. Keine Umgehung gültiger Entitäts-/Verbindungsprüfungen. A4 hat einen reinen vorbereiteten Katalog-/Prüfplan für fünf Karten, noch keinen neuen Laufzeitpass. Erweiterte reine JumpFromBouncer-Beobachtung für bekannte eigene Welt-Brushes ist erst ein privater Diagnoseentwurf; unbekannte Pointer bleiben ausgeschlossen.

Letzte verifizierte GitHub-Veröffentlichung: fd847e6f5b319c4a7389544395475e909a46d78e, exakter Baum f9f51d0e586a43b20ab7659dd0a46b527ae11102 des lokalen f51436a0f458ca53799f84c5cff748fc15ec995c. Spätere012-/Wartehelferänderungen sind noch nicht darin. Neues privates Drive-Delta011:25.155.401 Bytes, SHA256 d7828bdaa1b8807cd88f76785b5d69235cf8cab331404f811d9378fbb282b174, Datei1nS6XNO2bfXi1R85WXA22qa8kMUNOiNNV. Rückdownload identisch,588 reguläre Dateien/232.152.559 Bytes separat restauriert,4 Links nur indexiert; keine native Restoreausführung. Delta enthält die abgeschlossene uninstrumentierte A1-Kontrolle, noch nicht den späteren instrumentierten Lauf oder012. Weitere Veröffentlichung/Sicherung folgt. Formale1/4/8-Bot-Gates3600/3600/7200s, vollständige A-Funktionen und gestaffelter Flottenrollout bleiben offen.

## Fortsetzung 12.11.2026, 00:01 UTC

### Neuer Teststand12.11.2026 00:09 UTC

011-Wiederholung120,04s: vier echte234-Launches, alleKandidaten; beide8→12/11→12-Unterdrückungen nachgewiesen, nur eine Minigunaufnahme. Drei weitereLaunches nicht alsPickup zählen. Vollständiger Lebensnenner13Kandidatenleben enthält3Tode und2Zensierungen ohne Fernwaffe; erfolgreiche Aufnahme reicht bis62,90s. KeinRapidWeapon-PASS. Beim gerichtetenAnkunftswechsel kann im selbenUpdate einUP1→11 durchkommen; enger Folgefix mit Originalpfad-/Replay-Prüfung inArbeit. SieheNative011-Repeatbericht.

Erster echterPublic011/MITTEL/Swap0-Versuch ist explizitFAIL: ersteMessungen derSlots6/7/8 liegen0,075m überhistorischerReferenz, X/Zgleich, winzigeYaw-/Physicsflagsabweichung; Messphasenursache nochzuprüfen. RegulärerCleanup undnachträglicharchivierteLogs sauber, keinangerechneterVergleich. KeineToleranz stillschweigendgelockert.

A1-Controller Root904976d… erlaubt nun dieselbeprivateKonfiguration ohneInstrumentierung als Kontrollzweig. Uninstrumentiertes30,07-s-Spawn0-Fenster ohneSyncfehler, vierRollen normalgeschlossen, archivierteLogs sauber. NochkeineTSE-Damage-Hookausführung undkeineA1-Abnahme. GenerischerSame-Spawn-Tick-HPverlust allein istkeinNachweis einesgültigen normalenFremdtreffers. Root15Offline-Tests desDamagecontrollers bestanden; v2Hook unverändert767a013… .

Frische Flottenprüfung12.11.2026 00:01:54 UTC: sechs Instanzen mit jeweils8 nachgewiesenen eigenen Bots, aktuell keine zusätzlichen UNKNOWN. Public5 aktuelle Logs0BAD/0SyncDisconnect; Dev kumulativ21BAD/2SyncDisconnect. Die zugehörigen drei Dev-Logs und echten PID-/Modulidentitäten sind privat schreibgeschützt gesichert, keine fremden Prozesse verändert. Verfügbarer RAM1,89GiB während isolierter Probe, Disk22,33GiB; kein abgeschlossenes Ressourcen-Dauergate.

A bleibt unvollständig, B wurde nicht begonnen. Keine neue A-DLL ist produktiv. Der isolierte Repro mit tatsächlichem bisherigem Dev-Server `fe4a77…`, beiden Cecil048-Botclients `ec820d…`, aktivem ursprünglichem Powerupfilter, Spawn0 und unverändertem Vanilla-Client lief 180,08 s ohne beobachtete Syncfehler, Disconnects oder Crashes. Alle vier Rollen regulär geschlossen und danach archivierte Logs sauber. Native Vanilla-Samples belegen Bewegung und Feueranforderungen. Private Loopback-Bedingungen reproduzieren den externen Dev-Syncfehler nicht; Ursache bleibt offen. Bereinigter Beleg: `milestone-a-20261111/dev-existing-local-sync-repro.json`.

Kandidat011: Quelle `eed5db617c61a4d2e304e1d73dacfc06ad18eadd`, DLL `4184df65d927054470ac37967711236deeec442c4dbf92a9428769458e3ed5db`, Build erfolgreich, qualified=false. Exakte Bouncer-Annäherung erweitert auf gerichtete Originalkante11→12; 1918 SDK107-ASan/UBSan-Prüfungen und Driver-Action-Test bestanden. Das erste 120,03-s-Fenster endete mit vier regulär geschlossenen Rollen und sauberen nachträglich archivierten Logs. Der Kandidat benutzte die betroffene Route darin nicht; 0 passende Pad234-Aufrufe bei33 anderen Pad-Aufrufen. Kein Funktions-PASS für die Korrektur. Zweite gezielte120-s-Probe läuft seit00:00 UTC unter exklusivem privatem Runtime-Lock; Produktionsflotte bleibt unangetastet.

Neue Pflicht für alle folgenden nativen Controller: `tools/native_closed_log_evidence.py` archiviert und prüft erst nach normalem Ende aller Rollen die tatsächlichen Logs; 25 kombinierte Helper-/Finalizer-Tests bestanden. A1-Schadensbeobachter v2 bleibt privat: drei zusätzliche RED/GREEN-Korrekturen (positive Spawnclock, sämtliche überlappenden Aufrufe, unabhängig wiederholbares Detach) und Gegenreview bestanden. Separater ELF32-x87-Selbsttest8000/8000/8000 ohne Fehler; dies ist keine TSE-Hook-Abnahme. Controllerprüfung läuft. Public011-Controller vorbereitet,15 Offlineprüfungen bestanden; noch keine echten finalen Public011-Vergleichsläufe.

Letzte verifizierte Veröffentlichung bleibt Remote `8fa3de3a39739dccaa0908aff706ee4b9bb03bea`, exakter Baum `ea06add8bd87fa7fcbba803911582eaa8ce49a1c` des lokalen `d74c30d…`. Neuere011-/Closed-Log-Änderungen folgen separat. Letztes Drive-Delta009 ist zurückgeladen und separat restauriert; es enthält noch nicht010/011, den lokalen Dev-Repro oder A1-v2. Neue Sicherung nach quieszentem Testende erforderlich. Die formalen1/4/8-Bot-Stabilitätsgates3600/3600/7200s bleiben offen, ebenso übrige A-Abnahmen und gestaffelter Rollout.

Historischer Betriebsstand: **11.11.2026, 23:11:40 UTC**. Der Auftrag bleibt aktiv. **A ist nicht abgenommen; B wurde nicht begonnen.** Keine neue A-Kampf-DLL und keine neuen Namen sind produktiv aktiviert. Alle sechs Instanzen haben acht verifizierte eigene Bots. Dev hat zusätzlich einen nicht zugeordneten Spieler und im aktuellen Serverlog zehn SYNCBAD-Ereignisse mit einem Sync-Disconnect; die fünf öffentlichen Instanzen haben aktuell keine solchen Ereignisse. Die Dev-Rohlogs und tatsächlichen Prozess-/Modulidentitäten wurden separat privat gesichert. Keine Ursache aus Spawn0 oder der unbeteiligten isolierten009-Diagnose abgeleitet. Effektiver nativer Sessionwert für Spawn-Unverwundbarkeit ist überall0.0; erste-Tick-Abnahme bleibt offen.

Korrektur der bisherigen Betriebsbeschreibung: Der frische, tatsächliche DLL-/Inode-Nachweis liefert auf beiden öffentlichen Botprozessen Legacy7fc und auf beiden Dev-Botprozessen Cecil048. Auch die versionierten maschinenlesbaren Snapshots von22:38 und22:59 enthalten diese Werte. Die vorherige Prosa, die Notice-DLLs zu diesen Zeitpunkten als aktiv bezeichnete, widersprach diesen Snapshots und ist damit zurückgenommen. Das private separate Notice-Rolloutprotokoll21:02–21:12 und die übernommene, standardmäßig deaktivierte Notice-Quelldatei bleiben erhalten; deren spätere Laufzeitpräsenz wird nicht behauptet. Der genaue Wechselzeitpunkt und Verursacher sind nicht belegt. Vor jedem späteren Rollout werden Konfiguration, aktive Module und Eigentum neu geprüft.

Siehe aktuellen Snapshot `milestone-a-20261111/fleet-after-hole-rollback.json`. Die nachfolgenden älteren Abschnitte dokumentieren frühere Prüfzeitpunkte und sind kein aktuelles Laufzeitinventar.

## 1. Tatsächliche Änderungen und Betrieb

- A1: Ladereihenfolge geprüft. Dedicated überspringt das `PersistentSymbols.ini`-Laden in `Game.cpp`; dort vorhandene Nullwerte waren daher kein Wirksamkeitsbeweis. Dev-Shellwert vor Änderung tatsächlich 3,0, nach Änderung 0,0, gelesen aus dem hashgebundenen GameMP-Modul (RVA 0x5b120), ohne Speicheränderung.
- Sechs versionierte Mapstart-Vorlagen setzen `gam_tmSpawnInvulnerability=(FLOAT)0`; eine typkorrekte bedingte Logmeldung prüft den Shellwert bei jedem Sessionstart. Respawnverzögerung, HP und andere Regeln bleiben erhalten. Ein anfänglicher Retail-Typfehler in der Prüfbedingung wurde erkannt, zurückgerollt und auf einem isolierten Serverprobeprozess korrigiert.
- A2: 208 bestehende Namen bytegetreu erhalten, exakt 250 neue, insgesamt **458**. Neue Namen noch nicht in Live-Spielerprofile geschrieben.
- A3: MITTEL/STARK/DEMON, explizite Migration, Schutz gegen überschreibende Cecil-Voreinstellungen, Waffenbesitz-/Distanzprüfung und Colts-Grenze von 18 Welteinheiten. Gemeinsame Fähigkeiten und Zustand je lokalem Bot bleiben erhalten. Waffenbeschaffung, Supply/Kampf-Arbitrierung und alle geforderten Bewegungseigenschaften sind **nicht vollständig neu umgesetzt oder abgenommen**.
- A4: Originalkatalog und alle neun Navdateien geprüft. Keine neue Produktionsfreigabe einer Cecil-Map; öffentliche Legacy-Navigation bleibt aktiv. Keine Original-Cecil-DLL kopiert.
- Dev hatte bereits vor diesem Auftrag die serverseitige selektive Entfernung von Serious Damage/Invisibility aktiv. Dieser neuere Stand wurde erhalten. Unlimited Ammo und vorhandene Blood/Gibs-/Schwierigkeitsregeln wurden nicht verändert.

## 2. Quellen, Builds und Identität

Ausgangsbasis `4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`. Lokale Implementierungscommits: `c261a540f258a271f559d0db790b9cee1352e8fd` (Kampf), `41b2369` (Namen), `904bf8a` (Retail-FLOAT-Vorlagen). Build `tse-milestone-a-build-001-20261111`, MSVC Win32 unter Wine, `build_ok=true`, **qualified=false**, DLL-SHA256 `def7c044ba64a65b742c63d76c775c955b892655e626bf96a1380d778d35719a`. Manifest enthält SDK-/Include-Commits, Quell-/Overlay-Hashes und Compilerflags. Der Build ist **nicht deployed**.

| Rolle | Aktive GameMP-SHA256, geprüft23:11 UTC |
|---|---|
| Öffentliche BotA und BotB | `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835` |
| Öffentliche Dedicated | `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208` |
| Dev BotA und BotB | `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530` |
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
| A1 | Alle sechs aktuellen Sessionwerte0; frühere Rückwege gesichert, erstes serverseitiges Damage-/Reset-Gate offen |
| A2 | 250 neue Namen, Originalparser alle250 und fünf native Render-/Query-Formatfälle bestanden; flotteweite Live-Zuweisung offen |
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

## Aktuelle Fortsetzung: geprüfte Startbedingungen und Kandidaten005/006

Zwei240-Sekunden-Fenster005 gegen bisherige Dev048 sind vollständig geschlossen, jeweils0BAD/0Disconnect. Tatsächliche DLL-Rollen wurden vertauscht. Alle acht physischen Erstpositionen und Anfangsinventare stimmen zwischen den Fenstern überein; gleiche PRNG vor Freigabe, je Fenster kein Spawnzeitversatz. Absolute Sessionuhren unterscheiden sich; kein identischer kompletter Replay. Neuer MITTEL-Kandidat erzielt32:9 und22:6 Frags. Das ist ein begrenzter Botvergleich auf RedStation gegen Dev048, kein Vergleich gegen den öffentlichen7fc-Pfad und kein menschliches Schwierigkeitsurteil.

Die Waffenbeschaffung besteht noch nicht:005 hat im ersten Fenster22 Leben(17Aufnahmen,3Tode ohne Aufnahme,2zensiert ohne Aufnahme), im zweiten17(12/2/3). Erfolgreiche Aufnahmen benötigen maximal63.0 beziehungsweise50.6 Sekunden. Fehlende Aufnahmen werden nicht aus dem Nenner entfernt. Der begrenzte Flugabschluss verhindert einen konkret reproduzierten Itemverlustfehler, aber die zweite Gegenprobe zeigt eine andere Unterbrechung mit erneutem Sprungpad-Anflug. Kein Gesamt-PASS aus höheren Frags.

Kandidat006 erhält die separat vorhandene Community-Notice und ergänzt ausschließlich die Beobachtung der bereits ausgeführten Waffen-Connector-Kollisionsprüfung. Quelle `d0b2f05bbc7cf098e2551ec61efe8ec7a95af01f`, DLL `9690b088719ccd21e7a54e06063331a1391d4bfc904dc93fb20fadfe7dfeec7d`, gebaut und ausdrücklich **qualified=false**, nur eigene isolierte Kopie.1520 SDK107 ASan/UBSan-Bridgechecks und192 Tooltests bestanden. Der neue Connector-Logtest fiel vor Implementierung erwartungsgemäß durch. Keine Kollisionsfilter, Wegkosten oder Entscheidungen geändert. Aktuelle Kontrollen und nächste Ursachenprüfung werden im Handoff geführt.

A1-Wiederholungen für erstes Schadensereignis/Vanilla/Mapwechsel/Neustart, endgültige drei Kampfvergleiche mit besseren Stufen, funktionale Map- und vorgeschriebene Stabilitätsgates, Dev-Abnahme und gestaffelter A-Flottenrollout bleiben offen. B bleibt davon abhängig.

### Build007 und enger Inventarnachweis

Die beiden begrenzten Ursachenfixes sind in Quelle297c1bc integriert. Build007 DLL `ce15842a36fee25d56fb1ffcb0f0a45878c254d9b0c5b95b129ce7708abf4b7f` ist unqualified und ausschließlich isoliert.1563 gemeinsame SDK107Sanitizer-Bridgechecks, tatsächliche Driver-Action- und Itemadaptertests bestanden. Eine15,5968s-Original-Retail/Wine-Probe endet regulär mit0Syncfehlern,426 konsistenten passiven Inventargruppen und9 verworfenen wechselnden Lesungen. Details `milestone-a-20261111/native007-inventory-smoke.json`; dies bestätigt weder schnelle Beschaffung noch erstes Schadensereignis.

Ein nachfolgender Versuch scheitert schon im Bootstrap an der Instruktionsprüfung des Pause-Lesers. Beide gestarteten Prozesse normal beendet; kein Kampffenster. Die konkreten abweichenden Bytes wurden nicht gespeichert. Eine unabhängige statische Prüfung findet eine ungültige Annahme im Leser: ein absoluter Original-Engine-Operand wird bisher ohne echte PE-Relokation verglichen. Der Leser wird auf exakt berechnete Umzugsbytes korrigiert, bevor der Test erneut startet; keine pauschale Lockerung der Signaturprüfung.


### 22:38 UTC — gerichteter Bouncerfehler eingegrenzt, Backups erweitert

Build007 hat im vollständig geschlossenen240s-Vergleich53Leben mit passiver Originalinventarprüfung,0Syncfehlern und37:12Frags, aber weiterhin langsame/ausbleibende erste Waffenaufnahme. Das zusätzliche120s-Fenster mit vertauschtenDLLs und begrenztem Original-Bouncer-Hook zeigt zwei echte007-Starts (einer mit Minigunaufnahme, einer mit Konkurrentenverlust und fortgesetztem Flug) sowie vier andere Anflüge ohne234-Call. Die Fehlanflüge überfliegen das Pad von einer anderen Zugangsroute; exakter Arrival-/Jumptick bleibt zu messen. Siehe `2026-11-11-bouncer-hook2-directed-approaches.md`. Kein allgemeiner Navigations-PASS.

Ein separater Legacy7fc-Konsolentest ist vor jeder Eingabe an der strikten Ladeadressprüfung gescheitert; alle vier Rollen normalgeschlossen, kein Kampffenster. Exakte tatsächlicheMismatchadresse wurde nicht gespeichert. Der nächste Leser muss echtePE-Relokationen exakt unterstützen; keine pauschale Signaturmaskierung.

Quellstand09381fa ist aufGitHub alsbe41c86 mit identischem, zurückgeholtem Baum8731ca005b984653d5792a03783892aa76228def gesichert. Build007/Frida-Backup61015280Bytes, SHA2d7fb024d64d2b1f86cc17815eb53383edc9a5ac47cb40a21e88847be56fbd32: Drive-Rückdownload identisch,270reguläre Dateien separatgeschrieben/erneutgehasht,2Links nurindexiert. Neuere Hook2-/Legacyfehlversuchsbelege brauchen den nächsten Nachtrag; keine Freigabe aus Sicherung.


### 23:08 UTC — erster Gameplayfix 009 wird nativ geprüft

Die tatsächlichen 008-Actiondaten belegen zwei zu frühe normale Sprünge auf dem gerichteten Original-Red-Station-Anflug 8→12. Der eng gebundene Fix aus 6b749d8 unterdrückt nur die positive Up-Ausgabe auf dieser Kante bei gültigem statischem Brushsupport und exakt geprüfter aktueller Welt-/Navbindung; Originalflags, Radien, Jumpclock und andere Kanten bleiben erhalten. Root bestätigt 1676 integrierte SDK107-Checks mit ASan/UBSan, null Fehler, sowie den tatsächlichen Driver-Actiontest. Unabhängiger Review ohne wichtigen/kritischen Befund.

Build009 aus 8664767e3e22179d49304700052c04d9bc17e07c hat DLL-SHA256 0146cfeef95b532d7050672963d58d4542ac21ad2a8a957c5810db46970d74eb; Build bestanden, qualified=false. Aktiver eigener 120s-Diagnoselauf: Session37776, `run-arena009-bouncer-action-diagnostic.py 1 120 1 1 1`, Controller-SHA40c77a3a0bfd8acf0db8c59291c287d930eea2eeba2b7d5e7ac66875e2fc8f7e. Konsole arena009-action-diagnostic-controller.log, eigene Namespace/Port27850/Display154 und runtime.lock. Erst nach finalem Cleanup bewerten. Noch keine native Wirksamkeit oder Releasefreigabe.

Der vorige Public008-Vergleich ist vollständig geschlossen: 120.1141s, alle vier Rollen normal beendet, null Sync-/Disconnectereignisse. Alle neun initialen Spawnclocks0.7500001192 und Startinventare gleich, per-Slot-Positionen in vier Prozessansichten bestätigt. Tatsächliche Public7fc mit HumanAI0/AutoCombat1: 21 Leben=3 Erwerbe/15 Tode ohne Erwerb/3 zensiert. Kandidat008: 13=10/2/1. Vollständige Nenner in 2026-11-11-public-baseline008-native-lives.md/json; keine finale Drei-Tier-Abnahme.

Letzte Flottenmessung22:59: sechs Instanzen mit jeweils acht eigenen Bots, UNKNOWN0, 18 aktuelle Logs ohne BAD/Disconnect, effektiver Spawnwert überall0. Keine A-DLL produktiv ausgerollt. Remote ba530393f80d0ad7d39cbb395d778bb5675f9a99 entspricht exakt dem lokalen a35bd22-Baum; neue009-Änderungen noch nachzusichern. 008-Drivebackup rückgeladen und 257 Dateien separat wiederhergestellt, neue009-Daten noch nicht enthalten. A bleibt unvollständig; B unbegonnen.


### 23:12 UTC —009 Diagnose abgeschlossen, Gameplayproblem bleibt offen

Session37776 terminal0, Fenster arena009hook2-checked-swap1-trial-1-230743: 120.0395s, alle vier Rollen normal geschlossen, errors[], null BAD/Disconnect. 360 Actionzeilen, 46 originale Bouncer-Aufrufe an anderen Pads, kein Aufruf an234, null unbekannte Spieler/Drop/Fault, volle Listenerabdeckung, Detach und Originalkörperrestaurierung geprüft. Sanitisiert native009-action-diagnostic.json.

Local2/gen5 tick1368 belegt die beabsichtigte Unterdrückung: rawup1/finalup0 bei Support54. Später tick1373 rawup1/finalup11 ohne Support, tick1374 Kontakt193, tick1375 wieder ohne Support mit vertikaler Geschwindigkeit14.3; tick1381 Weiterleitung12→34 noch in der Luft. Exaktes Action-/Physiktiming wird gegen Originalsteuerung geprüft. Das reine Ground-Gate ist für diesen Verlauf unzureichend; keine Bouncer-/Waffenbeschaffungsfreigabe aus diesem Lauf. Kein weiterer nativer Versuch läuft, eigenes Display entfernt.

Root hat den neuen Quellstand f819c8c über die GitHub-API veröffentlicht und tatsächlich erneut gefetcht: Remote539a54943dbf8b034b8e522b888d7a463b447387 mit exakt identischem Baum9281b25272c6ce8db7d75f5531f845f01b68146a. Publication010.json enthält den privaten Nachweis. Kein gleicher Commit-Hash behauptet. Nächster privater Fortschrittsbackup muss009 und Public008 samt vollständigen Rohbelegen aufnehmen. Der eigene A1-Damage-Hook ist nur als statischer Entwurf gesichert; erster Respawnzustand weiterhin offen. A unvollständig, B unbegonnen.


### 23:29 UTC — Build010 prüft die verbleibenden Anflüge

Root integrierte den engen Verhaltensfix02acaea als4d186a2 und die separat geprüfte Diagnose6e375a7 alsb2f46e1. Beide unabhängig ohne wichtige/kritische Befunde geprüft. Root hat danach tatsächlich1806 SDK107-Bridgechecks mit ASan/UBSan und den Driver-Actiontest bestanden. Die positive UP-Ausgabe auf der exakt gebundenen8→12-Kante wird nun auch ohne Referenz in STAND/CROUCH unterdrückt; vorhandene Referenzen bleiben streng geprüft. Die zusätzliche11→12-Aufzeichnung ist rein passiv; dort bleibt die Steuerung unverändert.

Build010 aus b2f46e1725be49151ac062a565723afff2248c6a, DLL6e1e244495b43182eff60f1acb8ca61aba178f0638680298255673f5dcf60ef1, build_oktrue/qualifiedfalse. Aktiver eigener120s-Diagnoselauf Session93072, run-arena010-bouncer-action-diagnostic.py, SHA b0a8bfebc5b35556f6534b08b1267a439cc90894738774eb01e7716d5040baf5. Konsole arena010-action-diagnostic-controller.log; bekannte isolierteR/Port27850/Display154/runtime.lock. Erst nach Vierrollen-Cleanup und echter Auswertung als abgeschlossen behandeln. Kein Produktionsrollout.

Root-gefrorener Public010-Vergleichscontroller ist vorbereitet, aber noch nicht ausgeführt: privates public010-controller-frozen/run-public010.py SHA7564841eb06ef8d90815bca998d44e4ac7354e5f7701d7775b1c412c4b3e54ed, Policy592279dc080b4cf562342a9a58eecc250929a6c93ca4f7a485f88a51b3789055. Root15 Offline-Tests bestanden. Archivierte Public7fc-/Kandidatenkonfigurationen und tatsächliche physische Roster0/4 werden getrennt abgeleitet; keine Einstellungen aus dem zuletzt getesteten R-Verzeichnis übernommen. Frühe doppelt gelesene Erstspawns werden streng auf gleiche Uhr/Inventare/Referenzpositionen geprüft, ohne ersten Simulationszustand zu behaupten.

Private009-Sicherung abgeschlossen:15,215,101Bytes/SHA b0460eeb2cd0dade911a351f882b0dd324461f68db6752923291c752aaacd735, Drive1wdJTpKufnbx9euMRJhr1vJW4Atgr7xn3. Tatsächlicher Rückdownload identisch,233 Dateien separat geschrieben und erneut gehasht (127,551,099Bytes),2Links nur indexiert, kein Native-Restorestart. Enthält Quelle3afde4f/Build009, Public008/009-Rohbelege und Dev-Sync-Snapshot; neuere010-Arbeit braucht nächsten Nachtrag.

Die zusätzliche30s-Dev-Bestandsmessung23:19 ergab8 eigene Bots+1UNKNOWN, elf kumulative BAD und einen Disconnect ohne weitere Zunahme im Messfenster. HostCPU37.23–56.81%, mindestens2.553GiB verfügbarerRAM; keine Stabilitätsfreigabe. Beleg dev-sync-resource-followup.json. A bleibt offen; B unbegonnen.
