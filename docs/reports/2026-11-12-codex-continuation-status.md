# Codex-Fortsetzung: Umsetzung, Betrieb und offener Rollout

Stand: 13.11.2026 11:39:12 MEZ.

## Aktueller Auftrag

**Der Nutzer hat den Rollout von Build018 auf alle sechs Server ausdrücklich freigegeben. Die Durchführung ist aktuell durch fehlenden Deploymentzugriff blockiert. Es wurde noch keine Instanz aktualisiert oder neu gestartet.**

Der Umfang ist Dev zuerst, danach Red Station, Yodeller, Skulls, Little Trouble und Hole: insgesamt zwölf Botclients mit acht Bots je Instanz. DLL und die tatsächlich getestete aktive Kampfeinstellung gehören zusammen. Der bestehende Namen-/GUID-/Spawn0-Stand ist zu erhalten.

**Frisch geprüft:**ssam.ai-System-Control-Hostcheck vom13.11.2026 um11:30:14MEZ erfolgreich, Kontrolldienst aktiv. Der Lesetest einer bestehenden privaten Backupquittung wird mit Permission denied abgewiesen; allgemeine Dienstdiagnose nicht erlaubt. Im aktuellen Toolbestand fehlt eine geeignete Deploy-/SSH-/Binärkopierfunktion. RDC wurde wegen der bestehenden Monatskontingentsperre nicht erneut aufgerufen. Das ist ein Zugriffsblocker trotz vorhandener Nutzerfreigabe.

**Fortsetzung:**[Ausführungsplan für den freigegebenen Rollout](../superpowers/plans/2026-11-13-build018-fleet-rollout.md) und [konkreter Zugriffsbefund](milestone-a-20261112/build018-rollout-authorized-20261113.json). Nach legitimer Wiederverfügbarkeit aktuelle Rollen, Profile, Rückstände und Payload prüfen, dann die Instanzen nacheinander umstellen und kurz tatsächlich kontrollieren. Kein Deploymentprozess läuft.

**Fachliche Einordnung:**Die sechs kurzen Vergleiche mit109:33 direkten Abschüssen bleiben belegt. A2 ist fertig. Die offenen A1-/A3-/A4-/Dauerabnahmen werden durch die neue Rolloutfreigabe nicht als bestanden bezeichnet; sie ersetzen aber auch nicht den aktuellen ausdrücklichen Auftrag durch eine neue Freigaberunde. B ist weiter unimplementiert.

**Letzter vollständiger Flottenbeleg:**12.11.2026 22:43:05MEZ, sechs mal acht eigene Bots mit bisherigen DLLs, UNKNOWN0 und Spawn0. Heute wurde kein neuer vollständiger Flottensnapshot erhoben. Delta022/023 sind auf dem Server separat restauriert; ihre großen externen Kopien fehlen im letzten belegten Stand. Private Übergabe und Delta022-Manifest sind dagegen extern zurückgeprüft.


---

## Historische Detailbefunde vor diesem Fortschrittsstand

Die folgenden Einzelbelege bleiben nachvollziehbar erhalten. Für den aktuellen Gesamtstatus gelten die Aussagen oben und der aktuelle Handoff.


Stand: 12.11.2026 15:59:33 MEZ

**Die Namensaufgabe A2 ist abgeschlossen und auf allen sechs Instanzen wirksam. Meilenstein A ist insgesamt weiterhin nicht abgenommen; B wurde entsprechend der vorgegebenen Reihenfolge nicht begonnen.** Neue Kampf-/Navigationskorrekturen sind gebaut und teilweise nativ nachgewiesen. Offene Funktions- und Stabilitätsgates verhindern weiterhin die Releasefreigabe. Der zuvor blockierte Sicherungsnachtrag Delta020 wurde inzwischen vollständig auf Drive hochgeladen und zurückgeprüft.

## 1. Was tatsächlich umgesetzt und aktiv ist

Der Pool enthält jetzt **458 Einträge: alle 208 bisherigen Namen in unveränderter Reihenfolge plus exakt 250 neue sichtbare Namen**. Gleichzeitig verbundene 48 Bots tragen flottenweit eindeutige Namen. Der Rollout erfolgte zuerst auf Dev und danach einzeln auf Red Station, Yodeller, Skulls, Little Trouble und Hole. Zwölf eigene Botclients wurden regulär neu gestartet; alle 51 vorgesehenen Payloaddateien wurden gegen den tatsächlichen Nachzustand geprüft. Stabile GUIDs blieben erhalten. Sechs aktuelle Runtime-Identitätsdateien wurden mit den tatsächlichen Prozessgenerationen und Profil-/Modulhashes erneuert; die historischen Zuordnungen bleiben als Historie erhalten.

Die öffentliche Bot-DLL ist weiterhin der bisherige 7fc-Stand. Dev verwendet weiterhin Botbuild 048/ec820d und seinen bereits freigegebenen fe4-Server. **Build016 und der neue Diagnosebuild017 wurden nicht produktiv verteilt.** Bestehende Maps, Navdaten, Unlimited Ammo, Blut-/No-Gibs-Regeln, Powerupregeln und Serverhinweise wurden durch die Namenstransaktion nicht ersetzt.

## 2. Quell-, Build- und Datenstände

| Gegenstand | Nachgewiesener Stand |
|---|---|
| Ursprünglich fortgesetzter Worktree | `9c6d5c20500a8b28e6c6fcc273252e2b19ed0aec`, unverändert erhalten |
| Build015-Kampfkorrektur | Quelle `b6b776ddbc761ee96049e6626edd5af4895cb3af`, DLL `10015f213c05b2faefc312e11a310dae63d64eda1c7173601c6ffd4386a70313` |
| Build016-Rotationskorrektur | Quelle `58e8559903d999772218a6b5fd1d042b1759b547`, DLL `e5a80634b5247c900ae25b5b18869c433c30dcfb49b890338fb231da63b04825` |
| Build016-Manifest | SHA256 `4cd6b5a8d853afe2dbe492fb12fff0aed22a06c77b5de7fc4e732795d2676603`, Build erfolgreich, `qualified=false` |
| Build017-Diagnose | Quelle b35397f024b8a8722a01178a08c06d3d40802f65, DLL a5a379aadfd0cc376ad15a8368dd6814518e3f2da1fde22fdde9bd86f02abc5d; erfolgreich gebaut, qualified=false |
| Aktive öffentliche Bot-DLL | `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835` |
| Aktive Dev-Bot-DLL | `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530` |
| Aktive öffentliche Dedicated-DLL | `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208` |
| Aktive Dev-Dedicated-DLL | `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0` |
| Vollständiger Namenspool | SHA256 `005cd7bbee01d2b24367f46401d2cf8bf4dae45db311f3cdfa35c789ca8d0dc2` |

Config-/Navstand: Die wirksamen Spawnparameter und Neustartvorlagen sind auf allen sechs Instanzen 0. Die neue Namensdatenversion ist separat ausgerollt; eine neue Cecil-/Kampf-Releasekonfiguration wurde nicht verteilt. Die versionierten A1-Vorher-/Nachher-Daten stehen in `poc/runtime/milestone-a-20261111/manifest.json`, die ursprüngliche vollständige Navmatrix mit Welt-/Nav-CRC im [Milestone-A-Bericht](2026-11-11-milestone-a-progress.md). Aktuelle Prozess-/DLL-/Spawnwerte sind im [Flottensnapshot](milestone-a-20261112/fleet-completion-final.json) festgehalten.

## 3. Tatsächliche Flotte und aktuelle Aktivität

Die letzte zusätzliche Aktivitätsprüfung endete am **12.11.2026 um 11:12:56 UTC**, dauerte **30.509s** und enthält sieben beantwortete Abfragen je Instanz, insgesamt 42. Die eigenen Namen sind an reale Prozess-/Profilidentitäten gebunden; alle Prozessgenerationen waren vor/nach der Beobachtung gleich. Ein geänderter Fragstand belegt Aktivität im Beobachtungsfenster, keinen Treffer-/Schadensvergleich und keine Aktivität jedes einzelnen Slots.

| Port | Map | Eigene verbundene Bots | Zusätzliche UNKNOWN | Slots mit geändertem Fragstand | Netto-Fragänderung eigener Bots |
|---:|---|---:|---:|---:|---:|
| 25600 | Red Station | 8 | 0 | 5 | 10 |
| 25610 | Yodeller | 8 | 0 | 8 | 19 |
| 25620 | We Got Skulls'n'Bones Too | 8 | 0 | 3 | 5 |
| 25630 | Little Trouble | 8 | 0 | 7 | 13 |
| 25640 | Hole | 8 | 0 | 6 | 5 |
| 25650 | Red Station | 8 | 0 | 4 | 4 |

Hostweite CPU-Intervallwerte: **30.94–35.35%**. Mindestens **2.790GiB verfügbarer RAM** und **15.990GiB freier Datenträger**. Diese 30-Sekunden-Messung ersetzt kein Stabilitätsgate und keine Messung von Einzelkern-/Tickspitzen.

Der aktuelle Logcheck um 11:03 UTC zeigt auf den fünf öffentlichen Instanzen 0 BAD-/0 Disconnectereignisse. Dev enthält weiterhin die bereits vorher dokumentierten kumulativen **37 BAD-/3 Disconnectereignisse**. Ein Syncfix wurde nicht behauptet. Quellen: [Aktivitätsbeleg](milestone-a-20261112/fleet-current-activity.json), [Snapshot](milestone-a-20261112/fleet-completion-final.json), [Namensrollout](2026-11-12-names-sequential-live-completion.md).

Eine zusätzliche Bestandsprüfung am 12.11.2026 um **14:43:31 MEZ** bestätigt weiterhin sechs Instanzen mit je acht eigenen Bots und null zusätzlichen UNKNOWN. Die Logzähler bleiben öffentlich 0/0 und auf Dev 37 BAD/3 Disconnects. Verfügbar waren 2,67 GiB RAM und 14,30 GiB Datenträger. Dieser [neue Bestandsbeleg](milestone-a-20261112/fleet-resume1-before-native.json) enthält keinen neuen Schadens- oder Langzeittest.

## 4. Spawn, Namen und Kampf

### A1: Effektiver Wert null, Erstzustandsnachweis noch offen

Alle sechs aktuellen Sessionwerte und relevanten Vorlagen stehen auf 0. Der verlangte wiederholte normale Treffer ab dem ersten gültigen serverseitig verarbeiteten Respawnzustand für Bot und Vanilla, einschließlich Reload/Neustart, ist weiterhin nicht belegt.

Die Normalinput-Vorbereitung wurde weiter repariert und geprüft: V2 schloss eine tatsächlich reproduzierte Lücke zwischen letzter Policyprüfung und XTest-Request. V3 beseitigt eine vorzeitige Float32-Grenzablehnung unter Beibehaltung des ACK-Bereichs und der vorhandenen 0,001°-Konsistenzgrenze. Rohwerte bleiben erhalten. 155 Tests bestanden; ein unabhängiger Review bestätigte die tatsächlichen 104429-Rohdaten und alle Gegenfälle.

Der einzige neue native V3-Lauf 111716 absolvierte die vollständige Kalibrierung mit bestätigten Gains −0,25 / −0,25 und 0,000106812° Rückkehrfehler. Der zuvor problematische Grenzfall −0,5 wurde in diesem neuen Lauf nicht erneut erzeugt; dafür liegt der unveränderte tatsächliche 104429-Replay vor. Anschließend blieb die Route im bestehenden Approach-/Flugübergang hängen. Die 17. versuchte Aktion wurde vor dem Request abgewiesen; 16 Inputquittungen liegen vor. Pickup und normales Feuer wurden nicht erreicht. **Gesamtergebnis FAIL.** Alle drei Rollen wurden normal geschlossen, beide Displays entfernt und 673 Restorepfade unabhängig geprüft. Kein Once-, Schuss-, Treffer- oder FirstState-PASS. Quelle: [A1-V3-Ursachenanalyse](2026-11-12-a1-route-v3-native-result.md), [kompakter Nativebeleg](milestone-a-20261112/a1-route-v3-native.json), [V3-Korrektur](2026-11-12-a1-route-ack-body-v3.md).

V4 blieb vor einem neuen Spielstart durch den unabhängigen Review blockiert: Eine neuere After-Input-Probe konnte zugunsten eines älteren Ankers übergangen werden. Der separate V5-Entwurf schließt zusätzlich den belegten periodischen Lesepfad und besteht187Tests sowie den strikten Originalreplay; die unabhängige Prüfung läuft. Beide Ausführungsgates bleibenfalse. Siehe [V4-Blocker](2026-11-12-a1-flight-v4-independent-review.md) und [V5](2026-11-12-a1-flight-transition-v5.md).

### A2: Abgeschlossen

250 neue normalisiert eindeutige Namen, keine Kollision gegenüber dem Altbestand. Aufteilung: 147 schlicht, 45 Farbe, 26 Bold, 25 Italic, 7 kombiniert; keine neuen Flashnamen. Maximal 15 sichtbare Zeichen und 30 ASCII-Bytes; festgeschriebener Seed 20261111. Alle Ergänzungen wurden am echten Retailparser geprüft. Repräsentative Fälle aller fünf verwendeten Stilklassen wurden im Original 1.07-Client unter Wine und per GameSpy-Abfrage geprüft; ein physischer Windows-/WAN-Test wird daraus nicht abgeleitet. Die Live-Zuweisung und die GUID-Erhaltung sind separat nachgewiesen. 123 Tests der Namens-/Rollouttransaktion bestanden.

### A3: Verbesserungen belegt, Gesamtvergleich unvollständig

Build015 reduziert ausschließlich die MITTEL-Aimabweichung von 0,9 auf 0,6; STARK 0,45 und DEMON 0,15 bleiben differenziert. Der relevante tatsächliche Policytest ging von 524/1100 auf 887–1025/1100 in den sechs langsamen Fällen. Ein ungünstiger schneller 60°/s-Fall bleibt dokumentiert: 72→24 Feuerfreigaben/2097. Das ist keine allgemeine Leistungsfreigabe.

Das native MITTEL-Kreuzpaar zeigt gemischte Ergebnisse: 35:21 Queryfrags, aber 2910,817:3407,339 begrenzten Fremd-HP-Schaden, jeweils Kandidat:Public. Der vollständige STARK-Build015-Lauf 093722 ist begrenzt positiv: 35:15 Frags, 3196,795:2156,333 begrenzter Fremd-HP-Schaden und nützlicher Waffenbesitz in 13/17 gegenüber 3/40 beobachteten Leben. Fehlgeschlagene Starts, Tote und zensierte Leben wurden erhalten. Vertauschte STARK-Starts, vollständige DEMON-/aktuelle Build016-Vergleiche und die Gesamtabnahme bleiben offen. Ein allgemeiner menschlicher Schwierigkeitsgrad folgt nicht aus diesen Botduellen. Quellen: [MITTEL-Vergleich](2026-11-12-build015-mittel-progress.md), [STARK-Fenster](2026-11-12-build015-stark-first-window.md).

## 5. Cecil-Navigation und vollständige Mapmatrix

Build016 behebt die Übernahme alter eigener kumulativer Sollwinkel in eine neue Kartenepoche. Der echte Driver-Test reproduzierte vorher 8 Fehler in 18 Prüfungen; die erweiterte korrigierte Fassung bestand 47 Prüfungen unter ASan/UBSan sowie die bestehenden Aktionsguards. Native Folge: **Red Station→Red Station→Red Station**, keine andere Welt. Alle 16 Slot-/Reloadübergänge zeigen frische native Basis und erste lebend beobachtete View/Input/Last-Winkel 0. Normale Respawns wurden separat betrachtet; 49/49 behalten ihre Entity, 48/49 ihren exakt gleichen kumulativen Pitch in der ersten Folgeprobe, ein Sample enthält bereits neue Zielkorrektur.

Die neue frühe Inventarerfassung liefert 259 zusätzliche akzeptierte Gruppenproben vor der späteren Registry. Trotzdem erfüllen nur 16/24 Slot-/Phasenfälle alle bisherigen Aktivitätsfelder. Vier fehlende Feuerzeilen sind als Abtastlücken unabhängig belegt, ein früher Cannon-Pickup bleibt ohne nativen Vorher-/Nachhernachweis. Bei einem Bot fehlen über vier beobachtete Leben sowohl nützliche Waffenaufnahme als auch Feuer. **A4 bleibt FAIL; die vorhandenen Bedingungen wurden nicht gelockert.** Alle vier Rollen des Versuchs sind geschlossen und 648 Restorepfade unabhängig geprüft. Siehe [Nativeauswertung](2026-11-12-build016-native-reset-analysis.md).

Build017 ergänzt ausschließlich eine unabhängig geprüfte, standardmäßig ausgeschaltete Diagnose für zwei konkrete Versorgungsannäherungen.68Beobachterchecks,2687Bridgechecks und Driver-Guards bestanden; der native Diagnoseablauf wird separat vorbereitet. Die Ursache ist noch nicht repariert und keine Kartenfreigabe hinzugekommen. Siehe [Build017-Fortschritt](2026-11-12-build017-observer-progress.md).

Die Original-Navdateien wurden gegen Cecil-Commit `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c` auditiert. Der Suffix ist der Weltpfad-Hash; Welt-/Nav-CRC sind separate Integritätswerte. Die folgende Tabelle beschreibt den belegten Stand der Portierung und ihre offenen Grenzen, keine neue Produktionsfreigabe.

| Karte | Originale Navdatei | Belegter Stand / offene Grenze |
|---|---|---|
| Desert Temple | DesertTemple_E6B24B0F.nav | Welt nicht installiert, keine gültige Bindung; gesperrt. |
| Little Trouble | DM_LittleTrouble_6C64BF87.nav | Build013: 300 s mit echten Aktivitätsbelegen; zwei Waffenbeschaffungen über 54 / 65 s langsam bzw. offen. Keine aktuelle vollständige Freigabe. |
| The Lost Tomb | DM_TheLostTomb_AACB1C67.nav | Welt und Bindung auditiert; vollständige Funktionsabnahme fehlt. |
| Fortress | Fortress_5652374B.nav | Bindung vorhanden; Lava-/Flüssigkeits-/Absturzwege und aktuelle Funktion nicht abgenommen. |
| Hole | Hole_1AD627D0.nav | Älterer 048-Lauf über 600 s vorhanden; aktuelle funktionale Gefahren-/Navigationsabnahme fehlt. |
| Compound | KuntaKinte_AFD9424F.nav | Welt und Bindung auditiert; vollständige Funktionsabnahme fehlt. |
| Red Station | RedStation_5AF1A276.nav | Konkrete Bouncer-/Itembelege und neue Reload-Rotationsbasis vorhanden; beschriebene Aktivitäts-/Versorgungslücken verhindern Gesamtfreigabe. |
| Skulls'n'Bones | WeGotSkullsNBonesToo_9B573405.nav | Build013: 600 s ausgewertet; zwei Leben rund 223 / 263 s ohne nützliche Waffe. Für die neue Whitelist gesperrt. |
| Yodeller | Yodeller_FC72665B.nav | Welt/Bindung und ältere Tests vorhanden; früherer automatischer Vanilla-Rejoin fehlgeschlagen, keine aktuelle Gesamtfreigabe. |

Damit gibt es noch keine vollständig abgenommene neue Kandidaten-Whitelist. Die öffentlichen Maps blieben beim bisherigen Stand; ein nicht abgenommener Red-Station-Fallback wurde nicht als freigegeben ausgerollt. Original-Cecil besitzt Koop, unsere automatischen Kampfpfade bleiben auf Scorematch/Fragmatch begrenzt. Monsterziele, Follow und Kampagneninteraktionen sind nicht durch Umschalten freigegeben; keine zusätzliche Koop-Portierung.

## 6. Veröffentlichung, Backup und Wiederherstellung

[Fortsetzungsbranch auf GitHub](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/tree/codex/20261112-milestone-a-completion). Die tatsächliche Build016-Quellveröffentlichung [553afa7](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/commit/553afa7c73af0c080f9ac165c7b2045f20d65724) wurde auf Ubuntu erneut gefetcht; der Tree `3337a68d4208e1a4e15d76b57374943e0f538f42` entspricht exakt dem lokalen Buildsource-Commit. Die abschließende Berichtsveröffentlichung wird ebenfalls über den tatsächlichen Git-Tree geprüft; lokale/API-Commit-IDs können wegen unterschiedlicher Eltern bei gleichem Inhalt abweichen. Kein Force-Push und kein Merge eines unqualifizierten Builds.

Der neue private Nachtrag **Delta020 wurde auf Ubuntu erzeugt und separat restauriert**. Archiv: `/srv/tse-milestone-a-backup-completion-20261112/runtime-evidence-delta020-build016-114326.tar.gz`. Größe: **114.833.032 Byte**; SHA-256: `82a661bb52ae8d6b08232aba3f70577ebdaa594e52ddf8dfe9edee147cb7c132`. Er enthält den sauberen Quellstand `cd7a4a639191a2033390f39f0681e8b64b3d6b6c`, alle Git-Refs, Build016, die abgeschlossene Namenstransaktion mit tatsächlichem Nachzustand, aktuelle Identitätsbelege, neue Controller/Reviews und die im Index benannten abgeschlossenen Nativefenster.

Der unabhängige Dateirestore schrieb und prüfte **14.707 reguläre Dateien / 999.970.861 Byte**, einschließlich SHA256, Eigentümer, Modus und Nanosekunden-Zeitstempel. 2 Symlinks sind indexiert, nicht materialisiert. Restoreverzeichnis: `/srv/tse-milestone-a-backup-completion-20261112/restore-delta020-build016-114326`. Kein Spielstart aus dem Restore und keine Betriebsfreigabe daraus. Als inkrementeller Nachtrag benötigt Delta020 den verifizierten Ausgangsstand und die bisherigen Deltas bis 019.

**Delta020 ist vollständig auf Drive hochgeladen und durch echten Rückdownload verifiziert.** Beide Teile wurden am 12.11.2026 um 14:38:58 MEZ erneut heruntergeladen. Größen, Einzel-SHA256 und der Hash der geordneten Zusammensetzung entsprechen exakt dem bereits separat restaurierten Ubuntu-Archiv. Auch der Inhalt des Wiederherstellungsmanifests wurde nach dem Upload zurückgelesen und exakt verglichen. Der frühere Ausfall der lokalen Ausführungsumgebung ist behoben.

Drive: [Teil 1](https://drive.google.com/file/d/1J2tomfoi2axX2S3NJndr9-L_IvYv9iFc/view), [Teil 2](https://drive.google.com/file/d/1zEHBb5Jc78i4cfFIGO5O2sCfahT5td4B/view), [Wiederherstellungsmanifest](https://drive.google.com/file/d/1PK7hqH4RWAO1KIH_4pX_6E3TMEWvTB74/view). Der [vollständige Rückdownloadbeleg](milestone-a-20261112/backup020-drive-roundtrip.json) nennt IDs, Reihenfolge, Größen, Prüfsummen und Restoreumfang. Der exakte Archivquellstand bleibt unverändert; spätere Berichts- und Fortsetzungsarbeiten benötigen ihren eigenen folgenden Sicherungsnachtrag.

Die Übertragung ist in **zwei geordnete Teile** zu 100.663.296 und 14.169.736 Byte vorbereitet. Beide Teilhashes und der SHA256 des wieder zusammengesetzten Archivs wurden unabhängig eingelesen und geprüft. Diese lokalen Prüfnachweise wurden inzwischen durch die oben belegte Drive-Rückprüfung ergänzt. Die [Archiv-/Restorequittung](milestone-a-20261112/backup020.json) und das [Übertragungsmanifest](milestone-a-20261112/backup020-transfer-parts.json) enthalten die exakten Pfade, Größen und Prüfsummen. Nach dem Aufteilen blieben 15.818.780.672 Byte frei; die geforderte Reserve von 8 GiB blieb eingehalten.

Der vorherige [Drive-Nachtrag Delta019](https://drive.google.com/file/d/1MAHfGkschhrtPJivuJxvlza3l83CsTvP/view) bleibt im bestehenden Projektordner erhalten: 45.078.384 Byte, SHA256 `0342390c65ae7759d0e6838d6696b4f28eadb3a27364d44d71a4f14b4309ba3b`, separater Restore mit 11.858 regulären Dateien / 297.185.813 Byte. Zur Wiederherstellung von Delta020 werden weiterhin das verifizierte Basisbackup und die Deltas bis 019 benötigt. Lizenzierte Dateien und private Rohlogs bleiben außerhalb des öffentlichen Git-Projekts.

## 7. Abnahmestatus

| Bereich | Status |
|---|---|
| A1 Spawn | Effektiv 0 auf allen sechs Instanzen; verlangter wiederholter Erstzustands-Treffer offen. |
| A2 Namen | **Abgeschlossen und live.** |
| A3 Kampf | Teilweise umgesetzt und nativ verglichen; aktuelle vollständige Vergleichs-/Leistungsabnahme offen. |
| A4 Navigation | Reproduzierbarer Rotationsfehler korrigiert und begrenzt nativ bestätigt; funktionale Karten-/Aktivitätsabnahme offen. |
| Stabilität | Weiterhin gültige 1/4/8-Bot-Gates über 3600/3600/7200 s nicht bestanden bzw. nicht abgeschlossen. |
| A5 / Gesamt-A | **Nicht abgenommen.** Neue Release-DLL nicht flottenweit aktiv; Spiel-, Stabilitäts- und Releaseabnahme bleiben offen. |
| B-Dev | **Nicht begonnen**, da A nicht vollständig abgenommen. |
| B-Flotte | **Nicht begonnen.** |

## 8. Konkrete Fortsetzung

1. **Erledigt:** Unverändertes Delta020 auf Drive hochgeladen, beide Teile zurückgeladen sowie Einzel- und Gesamthash verifiziert. Die Fortsetzung arbeitet jetzt an A1 und A4; spätere Änderungen bleiben separat zu sichern.
2. Den nativ belegten Approach-/Flugübergang des Original-Testclients anhand seiner vorhandenen Rohzustände korrigieren und anschließend A1-Schadens-/Erstzustandsnachweise erbringen. Keine blind wiederholte Probe und keine Korridorerweiterung als Ersatz für eine Ursache.
3. Die verbleibende Waffenversorgung und Map-/Reloadaktivität für den aktuellen Kandidaten beheben, volle Vergleichspaare und die gültigen Stabilitätsgates abschließen.
4. Erst danach den qualifizierten und vollständig gesicherten A-Stand auf Dev und kontrolliert jede öffentliche Instanz ausrollen. B bleibt bis zur vollständigen A-Abnahme gesperrt.

Der [aktuelle Handoff](../coordination/HANDOFF.md) und der [persistente Ausführungsplan](../superpowers/plans/2026-11-12-milestone-a-continuation.md) enthalten Zuständigkeiten, genaue private Belegpfade und nächste Schritte. Vorhandene Arbeiten, gescheiterte Versuche und ursprüngliche Backups wurden erhalten.


## Continuation checkpoint 2026-11-12T18:31:47.457732+00:00

- Root integrated the independently reviewed live-item flight V3 source. Both actual review blockers are closed for its exact hashes; final actual-body ASan/UBSan run2763checks/0FAIL. The original2742/0scope and both independent behavioral REDs remain preserved. Build018 is prepared but not yet executed; native qualification remains false. See a4-live-item-flight report.
- The A3 initial-acquisition correction is independently READY0C/0I with74actual runtime pins,141source pins,11verification pins and65unchanged parent files. The native017initial FAIL remains FAIL. A separate retarget must use actual018build pins before a new control and one instrumented tier1/swap0 trial.
- The compensated A1input comparison retains original effective gain through normal settings1/1to0/0.25. Independent review found one actual sticky-reader defect: an already-read wrong global pair can be hidden by a concurrent retryable tick change. A separate disabled V2 correction is in progress; no native repeat is authorized from the blocked V1package.
- Latest verified public source before this integration is GitHubc1fb8346cb1064ca7dffda17527cb4c0a65ff8c0, exact local55efaa2tree90c2b972. New source publication remains pending. Delta021archive and complete restore manifest are actually restored and Drive-roundtrip verified; this later work requires Delta022.
- Last actual fleet receipt17:48:53UTC reports6x8ownbots,UNKNOWN0andunchanged historical Dev counters. Public candidate DLL rollout has not occurred.
- Root alone owns integration/build/native/live. identify_latest_codex closes the blocked V1input review; review_names_transaction owns only its separate sticky-reader V2correction; finish_names_transaction is idle after the completed A4V3review. At most two workers. No native game is active.
- Next: guarded018build; independently checked018controller retarget; new A3control plus one instrumented trial, then remaining tier/start windows if valid; native A4verification; finish the bounded A1first-state proof and original duration/rollout gates. A remains incomplete;B unstarted.


## Guarded Build018 completed — 2026-11-12T18:38:51.851870+00:00

Actual build finished18:33:54.876145UTC. Root wrapper1226016 returned0 after26.70seconds. Build source1802fb3f0720b53feb032abfe2c2a83407bfea6e/tree df9f4336153662e3398a28793e72c53e0c2161a3. The actual428544-byte DLL is6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a; manifest f4212443317b58b04808bd42d084e6a3286e458af2c0dbcfb276aa3bca931c2e. All47stagedsource and28overlay pins were independently verified by the A3retarget author. native_qualified remainsfalse; no newDLLwasinstalledinLab,fleetorDev.

The fresh18:33:29UTCpreflight verified allfourLabrootsquiescent, bothdisplaysabsent and bothlocksavailable; CPU40.104167%, availableRAM2616410112bytes, freedisk14200320000bytes. This snapshot is not a duration/resource gate.

Current worker ownership: identify_latest_codex authors only the separately disabled018A3retarget from the independently READYinitial-capture correction; review_names_transaction fixes only the separately reproduced sticky optional-input-reader defect in disabledV2. finish_names_transaction is idle for independent retarget review. Root retains all build/native/live execution. No native controller is active. Next steps and all original A1/A3/A4/duration/rollout gates remain unchanged. Exact-tree public source publication for this checkpoint is in progress; Delta022 remains required for private evidence.
