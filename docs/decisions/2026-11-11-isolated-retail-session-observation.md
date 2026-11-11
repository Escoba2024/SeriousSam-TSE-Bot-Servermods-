# Isolierte Retail-Sessionmessung auf Hetzner

11.11.2026, Fortsetzung des ausdrücklich autorisierten Meilensteinauftrags. Native Windows-RDC-Geräte erneut offline; lokale Original-Retail-1.07-Dateien und Wine verfügbar. Daher isolierte eigene Runtime `/srv/tse-a1-isolated-20261111`, eigene Präfixe, Display153, Port27750, systemd-`PrivateNetwork=yes` und gemeinsame eigene Namespace ausschließlich für Testprozesse. Keine Route ins WAN; öffentliche Flotte ist keine Messpopulation.

Keine Ghidra-/REA-/Frida-MCP-Tools in der tatsächlich verfügbaren Toolliste. Keine Wiederholung des fehlerhaften GUI-Ports8080. Für die kleine exportierte Lesestrecke wird vorläufig **objdump-Disassemblierung**, keine Ghidra-Dekompilation, dokumentiert. Das ist kein Ersatz für die noch offene vollständige CRC-Ursachenanalyse.

Unveränderte Engine.dll SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, Imagebase600c0000:

- Export `_pNetwork` RVA20d6a4.
- Export `CNetworkLibrary::GetSessionProperties` RVAdca00; Rückgabe bei6019ca1f `lea eax,[esi+0x96c]`. Headervergleich ergibt Spawn-Floatoffset84hex im Sessionblock; tatsächliche Bytes werden gegen geplante3/0-Werte geprüft.
- Export `CEntity::GetPlayerEntity` RVAf9d70 liest Network+20hex, dessen Tabelle bei+4, Eintragsgröße136, aktiver Eintrag+0 und Entitypointer+4. Keine Funktionsaufruf-Injektion.
- Export `CLiveEntity::GetHealth` RVA17020: `flds [ecx+0xcc]; ret`. Export `CEntity::GetPlacement` RVA16d50: `lea eax,[ecx+0x20]; ret`.
- `CTimer::CurrentTick` benutzt TLS, daher keine frei erfundene feste Timerobjekt-Adresse als Ticknachweis.

Beobachtung über `/proc/PID/mem` ausschließlich read-only nach CWD-, DLL-SHA-, gemapptem Inode- und Bytepatterncheck; keine Hooks, Breakpoints, Action-/Entitäts-/Speicheränderungen. Live-Sessionwert wird in allen drei eigenen Prozessen verglichen. Messkosten und nicht instrumentierte Kontrolle bleiben getrennte Prüfpunkte. Rohspeicheradressen und private Logdaten bleiben außerhalb Git.

Die erste Probe öffnete mit ausgeschaltetem GameSpy-Heartbeat keinen Querysocket; normale Beendigung, keine Funktionsabnahme. Enumeration allein öffnete ihn ebenfalls nicht. Im **routenlosen privaten Namespace** wird Heartbeat eingeschaltet und Masterziel localhost; erst damit ist die unabhängige Statusabfrage verfügbar. Das ist keine öffentliche Masterlistenabnahme.

Der vorhandene native CTString-Probequelltext wird unverändert aus dem Namecap-Worktree übernommen, mit vorhandener MSVC-Toolchain gegen Original-Retail-Engine gelinkt und privat ausgeführt. Alle250 neuen Roh-Namen müssen mit dem tatsächlichen `Undecorated` und `LengthNaked` den Validatorwerten entsprechen. Das belegt den Parser, nicht allein die sichtbare Clientdarstellung.


Weitere Gegenprüfung Original-EntitiesMP.dll SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`: exportiertes `CPlayer::ReceiveDamage` RVAed380, Imagebase60310000. Bei603fd443 folgt der Sessiongetter-Aufruf,603fd445 lädt `[eax+0x84]`; der Vergleich mit0 springt bei603fd45c an der zeitlichen Spawnprüfung vorbei. Bei positivem Wert wird bis603fd47a aktuelle Zeit minus `[esi+0xc14]` verglichen. Ein neuer SDK-Layoutprobe meldet `m_tmSpawned=3092=0xc14`, konsistent mit diesen Originalbefehlen. Das belegt den echten binären Gate-Pfad, noch keinen gemessenen regulären Treffer am ersten Respawntick.

Original-Engine `GetGameTime` RVAdc8d0 besteht aus `mov eax,[ecx+0x20]; flds [eax+0x4c]; ret`; dieser Sessiontick wird für rein lesende Alters-/Health-Samples verwendet. Werte zwischen Prozessen können wegen Vorhersage um einen Tick differieren. Die Original-Sessionproperties stimmen hingegen vollständig in der verglichenen156-Byte-Region überein. Die erste3,0-Kontrolle lief320,08s mit zwei Spielern ohne protokolliertes SYNCBAD oder Disconnect und wurde vollständig normal beendet. Vergleich0 und dichtere Kampfpopulation sind separate Nachweise.
