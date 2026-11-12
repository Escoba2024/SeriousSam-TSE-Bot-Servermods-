# A4 Build017: längerer Red-Lauf – Waffenversorgung und Freigabegrenzen

Stand: 2026-11-12. Ausschließlich geschlossene Belege; Autor /root/identify_latest_codex. Root besitzt Integration, Build und Runtime. Keine Source-, Controller- oder Runtimeänderung.

## Entscheidung

Der eigenständige 480-s-Versuch belegt den **begrenzten Reset-/Aktivitätsnachweis auf Red Station**: 24 von 24 Slotphasen erfüllen die unveränderten fünf Aktivitätsfelder. Der Originalstatus bleibt PASS_LIMITED_BOT_RESET_FRESH_OBSERVER_REVIEW_REQUIRED. **Eine produktive Red-Whitelist und eine Verbesserung der Waffenversorgung sind damit nicht nachgewiesen.**

Alle **178 beobachteten Leben** bleiben im Nenner. In 57 wurde nützlicher Besitz gesehen, in 55 eine tatsächliche Vorher/Nachher-Aufnahme; in 121 Leben kein nützlicher Besitz. Davon endeten 104 mit beobachtetem HP-Tod und 17 am Fensterende. Zwei der 104 Todesfälle wurden ausschließlich als Leiche erfasst. Der längste offene Qualitätsfall ist **P2 A0: mindestens 63,453865 s Lebensalter ohne beobachteten nützlichen Besitz**, mit 338 lebenden Inventarsamples und owned=3 in allen 63 zugehörigen lebenden CecilState-Zeilen.

Alte 300-s-FAILs bleiben unverändert. Identische DLL und längere Beobachtungszeit sind kein kausaler Gameplay-Vergleich.

## Quellen und strikte Grenzen

Rohfenster: /srv/tse-milestone-a-evidence-20261111/a4-reset017-extended-20261112-165124

Kandidat: /srv/tse-milestone-a-build-017-20261112/Sources/Game/GameMP.dll

| Quelle | SHA256 |
|---|---|
| result.json | 5f87a9046d581d86db830c3db235a8d940278531ff963a1c45d68185b499c971 |
| host-resources.json | 8274ea63b1257f209bf95dedab5d4a3be713d1f5679d71abf20042a209b6d18f |
| Rootpostflight | 98e15985fca3927ca6640be5c875946544c8ffc2fa095b9d2fa7f1c8404a2e35 |
| Buildmanifest | b4905cf1c279c6461ea892f159c16d3e92196901c6aa8d255bf62311a8e0e32f |
| GameMP.dll | a5a379aadfd0cc376ad15a8368dd6814518e3f2da1fde22fdde9bd86f02abc5d |
| Originalauftrag request.md | 50f05983b03f727d57c6057fe1686d83b8f5115c8815c8cf305be48d7efa95e1 |

Rootpostflight: /srv/tse-milestone-a-continuation-evidence-20261112/a4-build017-extended-root-postflight.json. Originalauftrag: /srv/tse-milestone-a-evidence-20261111/request.md. Build-Commit b35397f024b8a8722a01178a08c06d3d40802f65, Baum ce74a529a1c55dd3317476d44137f1bd2327d9c0, qualified=false. Vollständige weitere Dateipins stehen in source-pins.json und wurden nach der Auswertung erneut geprüft.

Die drei gespeicherten Phasenlogs wurden bytegenau als Ausschnitte der geschlossenen Logs geprüft. phase-byte-boundaries.json hält Anfang und Ende fest. Ereignisse zwischen Phasen und im Cleanup liefern **keinen** nachträglichen Pickup-/Fire-Pass. Server-PID/Startzeit, phasenweise Registry, Entity-ID, Entity-Pointer und World-Pointer binden die Inventarproben. Alle Originalfelder der 178 Leben bleiben erhalten. 17.101 eindeutige native Botzustände; keine widersprüchlichen überlappenden Inventarsamples.

Native Spieluhr, Controller-Walltime und lokale Bot-Ticks werden getrennt. Ein konstanter Sekundenversatz aus späteren Respawns wurde **verworfen**: Alle sechs Prozessphasen überschreiten die frühere 1-ms-Residuenprüfung; P2 botB hat zusätzlich diskrete Versätze5797 und5798Ticks. Keine Toleranz wurde erhöht. clock-calibration.json erhält diesen negativen Befund. native-observer-clock-bounds.json hält die wenigen unabhängigen Native-Time-Werte fest, ohne lückenlose Synchronisation zu behaupten.

Lebenszeiten stammen ausschließlich aus nativen Inventarwerten. Alle 178 Cecil-Lebenszuordnungen sind über vollständig übereinstimmende Spawnreihenfolge, Entity und Generation gebunden (life-log-bindings.json). Exakte Konkurrenzbelege werden nur innerhalb desselben Prozesses und Ticks behauptet. Hinweise auf mögliche Float-Akkumulation werden nicht als Beweis einer generell konstanten Uhr benutzt.

## Vollständige Lebens- und Phasennenner

| Phase | Leben | HP-Tode | rechtszensiert | Besitz-Leben | Aufnahme-Leben | native Fernfeuer-Samples | Server-Fremdtötungen |
|---|---:|---:|---:|---:|---:|---:|---:|
| P0 | 54 | 46 | 8 | 19 | 19 | 580 | 43 |
| P1 | 61 | 53 | 8 | 17 | 16 | 468 | 52 |
| P2 | 63 | 56 | 7 | 21 | 20 | 515 | 57 |

Gesamt: 178 Leben, 155 HP-Tode, 23 rechtszensierte Leben, 57 Besitz-Leben, 55 Aufnahme-Leben und 1.563 native Fernfeuer-Samples. Nach den anfänglichen acht Leben je Phase wurden 154 weitere Leben erfasst. HP-Tode, Log-Tötungen und abgeschlossene Respawns sind verschiedene Größen; ihre abweichenden Abtast- und Endgrenzen werden nicht durch Nenneränderungen ausgeglichen.

### Zeit bis erstmals beobachtetem nützlichem Besitz

Unverändert gilt die Maske 0x3df8. Knife, Colt, Double Colt und Chainsaw zählen nicht. Eine bewaffnete Erstprobe belegt Besitz, keine erfundene Aufnahme. Zwei linkszensierte Besitzfälle erklären 57 gegenüber 55.

| obere Altersgrenze der ersten Besitzprobe | Leben, exklusives Intervall |
|---|---:|
| bis5s |18|
| über5bis10s |12|
| über10bis20s |23|
| über20bis40s |4|
| kein nützlicher Besitz beobachtet |121|

Nur unter den 57 Besitz-Leben: Minimum 0,300 s, P25 3,550 s, Median 9,950 s, P75 13,550 s, P90 16,711 s, Maximum 29,352 s. **Das ist kein Gesamtmedian aller 178 Leben.** Todesfälle werden nicht als statistisch unabhängige Zensierung behandelt.

Die tatsächliche Aufnahme liegt zwischen letzter lebender unbewaffneter und erster lebender bewaffneter Probe. Bei bewaffneter Erstprobe bleibt die Untergrenze 0. Median der Intervallbreiten 0,150 s, Maximum 7,550 s. all178-lives.json bewahrt Unter- und Obergrenzen, Rohzeilen, letzte lebende und erste Todesprobe. Die beiden ausschließlich als Leiche erfassten Fälle bleiben enthalten.

### Lange erfolglose Abschnitte

Alle Leben ohne beobachteten nützlichen Besitz mit letztem lebendem Lebensalter von mindestens 20 s:

| Phase/Slot | native Spawnclock | letztes lebendes Alter s | Ende | inventory.jsonl Rohzeilen |
|---|---:|---:|---|---:|
| P2 A0 | 71.999794 | 63.454 | Fensterende | 5058–5951 |
| P1 A3 | 8.250013 | 36.600 | HP-Tod | 2256–2844 |
| P2 A1 | 17.600018 | 33.299 | HP-Tod | 4234–4784 |
| P1 B3 | 12.650030 | 30.300 | HP-Tod | 2308–2808 |
| P2 A2 | 31.999798 | 26.100 | HP-Tod | 4463–4881 |
| P0 B0 | 94.501167 | 25.552 | Fensterende | 1787–2244 |
| P1 B2 | 0.350000 | 23.800 | HP-Tod | 2253–2491 |
| P1 B1 | 83.450493 | 21.601 | HP-Tod | 3459–3846 |
| P0 A2 | 99.701485 | 20.351 | Fensterende | 1881–2243 |
| P1 B3 | 94.251152 | 20.151 | HP-Tod | 3640–4003 |

Die Altersangabe ist keine Behauptung kontinuierlicher atomarer Überwachung. Viele Intervalle knapp über 0,5 s liegen in der nativen Zeitdarstellung bei 0,500031 s; sie bleiben bei der strikten Intervallauswertung unverändert ausgeschlossen.

**P2 A0 im Detail:** Spawn 71,999794; letzte lebende Probe 135,453659. inventory.jsonl Zeilen 5058–5951; Entity 560, Server-Slot 1, Cecil-Generation 10; botA-closed.log Zeile 8049/Tick 7381. 338 lebende Proben, maximale Lücke 0,550034 s. Kein nützlicher Besitz. 63 lebende CecilState-Zeilen, davon 60 mit Bewegung, owned stets 3. Der kumulative Fire-Inputzähler steigt 539→558: 19 ausgegebene Kampffeuer-Inputs, **keine** 19 bewiesenen Projektile oder Treffer. Native nützliche Fernfeuer-Samples dieses Lebens: 0.

Fünf nützliche Ziele werden unavailable: Tick 7556/7784/7808/8049/8074, botA-closed.log Zeilen 8195/8397/8464/8684/8707. Zwei verlorene Ziele sind exakt als konkurrierende Aufnahme belegt:

- A2 erwirbt am Tick 7784 Grenade, owned 3→259, Abstand 2,556 zum Ziel 544; Zeile 8403. A0 verliert dasselbe Ziel am selben Tick.
- A1 erwirbt am Tick 7808 Flamethrower, owned 11→1035, Abstand 3,146 zum Ziel 248; Zeile 8470. A0 verliert dasselbe Ziel am selben Tick.

Derselbe Prozess und Tick, richtiges neues Waffenbit und tatsächliche Zielposition tragen diese Aussagen. Für die drei übrigen Verluste wird keine präzise prozessübergreifende Ursache behauptet. A0 bleibt auf weiteren Knoten beweglich, hat LockApproach an Knoten 2 (Zeile 8846) und verfolgt erneut Ziel 544 (Zeile 8950). **Kein eindeutiger Timeout- oder Stillstandsfehler ist daraus bewiesen.**

P1 A3 bleibt mindestens 36,600 s bis zum HP-Tod ohne nützliche Waffe; P1 B3 mindestens 30,300 s. Wechselnde Ziele und Bewegung sind erfasst. long-unarmed-cases.json enthält vollständige Zustände und Marker aller zehn langen Fälle sowie elf exakte Konkurrenzbelege. Diese erklären einzelne Zielverluste, nicht pauschal jede Verzögerung.

## Waffen, Kampf und Stillstand

Native Fernfeuer-Samples erfordern alive, current weapon in der nützlichen Maske, has_ammo und fire_requested. Mehrere Proben können denselben Feuerzustand erfassen. Sie sind **weder Schusszahl noch Schaden**. 51 Leben enthalten mindestens eine solche Probe; sechs der 57 Besitz-Leben keine.

| Waffen-ID/Name | P0 | P1 | P2 | Summe |
|---|---:|---:|---:|---:|
| 4 / Shotgun | 0 | 18 | 13 | 31 |
| 5 / Double Shotgun | 98 | 22 | 51 | 171 |
| 6 / Tommygun | 0 | 0 | 0 | 0 |
| 7 / Minigun | 128 | 191 | 145 | 464 |
| 8 / Rocket | 8 | 0 | 10 | 18 |
| 9 / Grenade | 48 | 33 | 27 | 108 |
| 11 / Flamethrower | 17 | 1 | 0 | 18 |
| 12 / Laser | 167 | 101 | 76 | 344 |
| 13 / Sniper | 14 | 27 | 58 | 99 |
| 14 / Cannon | 100 | 75 | 135 | 310 |

43/52/57 serverseitige Fremdtötungen sind zusätzlich dokumentiert. Kein kontrollierter Public-Vergleich oder Tiervergleich liegt in diesem A4-Lauf vor. Der shots-Zähler zählt ausgegebene Kampffeuer-Inputs (Build017 overlay/BotDriver.cpp Zeilen 1631–1632 und 1662–1668); daraus wird keine Trefferzahl abgeleitet.

| Slotphase | Leben | HP-Tode | Aufnahme-Leben | Fire-Action-Zeilen | native Fernfeuer-Samples | max. erfasster Stillstand s |
|---|---:|---:|---:|---:|---:|---:|
| P0 A0 | 8 | 7 | 2 | 1 | 6 | 0.700 |
| P0 A1 | 7 | 6 | 4 | 13 | 100 | 0.650 |
| P0 A2 | 4 | 3 | 2 | 21 | 141 | 1.000 |
| P0 A3 | 6 | 5 | 1 | 3 | 20 | 1.250 |
| P0 B0 | 8 | 7 | 2 | 20 | 104 | 0.600 |
| P0 B1 | 9 | 8 | 2 | 4 | 20 | 2.050 |
| P0 B2 | 3 | 2 | 3 | 26 | 149 | 1.150 |
| P0 B3 | 9 | 8 | 3 | 8 | 40 | 0.700 |
| P1 A0 | 9 | 8 | 2 | 5 | 21 | 1.250 |
| P1 A1 | 3 | 2 | 2 | 34 | 184 | 0.700 |
| P1 A2 | 9 | 8 | 2 | 16 | 95 | 0.500 |
| P1 A3 | 8 | 7 | 2 | 11 | 51 | 2.000 |
| P1 B0 | 5 | 4 | 3 | 8 | 63 | 0.900 |
| P1 B1 | 12 | 11 | 1 | 6 | 34 | 0.550 |
| P1 B2 | 10 | 9 | 2 | 4 | 8 | 0.950 |
| P1 B3 | 5 | 4 | 2 | 3 | 12 | 1.200 |
| P2 A0 | 6 | 5 | 2 | 21 | 121 | 0.700 |
| P2 A1 | 7 | 6 | 3 | 15 | 71 | 0.550 |
| P2 A2 | 11 | 10 | 2 | 2 | 6 | 0.450 |
| P2 A3 | 7 | 6 | 2 | 22 | 104 | 0.600 |
| P2 B0 | 9 | 8 | 2 | 5 | 28 | 0.800 |
| P2 B1 | 7 | 6 | 4 | 9 | 40 | 0.750 |
| P2 B2 | 6 | 5 | 3 | 22 | 91 | 0.600 |
| P2 B3 | 10 | 10 | 2 | 14 | 54 | 1.100 |

Ready und Motion sind ebenfalls alle 24 positiv; vollständige Werte in all24-slotphases.csv. Stillstandsmaxima P0/P1/P2: 2,050/2,000/1,100 s. Unbekannte Stillstandsintervalle wegen strikter >0,5-s-Lücken: 0/4/195. Maximale native Lücke zwischen lebenden Proben desselben Lebens: 0,400024/0,500031/0,600037 s. Kein längerer erfasster Stillstand; keine behauptete Lückenfreiheit.

Beidseitig lebend beprobte Intervalle bis 0,5 s summieren 2.510,960 Botsekunden: 1.421,783 ohne nützlichen Besitz, 1.080,227 mit Besitz, 8,950 mit Wechsel. Dies ist keine kontinuierliche Verfügbarkeitsquote.

## Red-Navigation: belegte Funktionen und konkrete Grenzen

Originalwelt-SHA 66e1309ee6eeeda8c564574df65df87a8406f4079b78ad508e77c82d19971111, CRC ff3776e0. OriginalNAV-SHA 70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6, CRC e4571656, Format 6, 193 Knoten. Originaldatei bis EOF ausgewertet. Tatsächliche Runtimebindung und Mapserial 1/2/3 vorhanden; keine NAV ersetzt.

### Nordkante 68→6

563 dichte passive Actionproben: 523 Nordkante, 40 Source87. Elf Nordfenster; **sieben** erreichen den unveränderten Originalradius 1 und zeigen echten Sourcefortschritt zu 6. Zwei führen danach zu 27 statt 7; beide Nachfolger existieren im Originalgraph. Eine Prüfung ausschließlich auf 6→7 würde diese zwei Erfolge übersehen.

| Phase/Slot | lokale Ticks | kleinste Originalmetrik | Befund | jeweiliges closed.log Zeilen |
|---|---:|---:|---|---:|
| P0 A3 | 2349–2368 | 19.026018 | offen/abgebrochen | 2475–2529 |
| P1 A1 | 3341–3401 | 0.656255 | Reached + Source 6 | 3491–3631 |
| P2 A3 | 6517–6577 | 0.656258 | Reached + Source 6 | 6723–6824 |
| P2 A2 | 6589–6649 | 0.656258 | Reached + Source 6 | 6840–6960 |
| P2 A1 | 6677–6725 | 0.881430 | Reached + Source 6 | 6977–7099 |
| P2 A0 | 7097–7160 | 0.624514 | Reached + Source 6 | 7654–7784 |
| P0 B2 | 549–590 | 16.680302 | offen/abgebrochen | 713–796 |
| P1 B1 | 4150–4205 | 16.154733 | offen/abgebrochen | 4550–4686 |
| P1 B2 | 4960–5003 | 0.367746 | Reached + Source 6 | 5352–5497 |
| P1 B3 | 4997–5011 | 18.994254 | offen/abgebrochen | 5435–5519 |
| P2 B2 | 6574–6623 | 0.850871 | Reached + Source 6 | 7038–7140 |

Die erfolgreichen Fenster enthalten echte vertikale Flüge bis etwa 33–41 Welteinheiten mit anschließendem Knotenfortschritt. Das belegt diese Bouncer- und Höhenroute für die beobachteten Startlagen.

P0 A3 und P0 B2 verlieren das betrachtete Ziel unmittelbar nach dem dichten Fenster. P1 B1 stirbt am nächsten Tick 4206. P1 B3 verliert ab Tick 5012 die dichte Beobachtung beim sichtbaren Colt-Kampf (botB-closed.log Zeilen 5521–5522); Tick 5020 zeigt den geänderten Bewegungswunsch und weiterhin Source68/Hop6 (Zeile 5542). Weitere Samples fallen bis Y≈0,379; Source68/Hop6 bleibt bis Zielverlust 5068 offen (Zeilen 5572/5607/5629). Die 108 nativen lebenden Proben dieses Lebens liegen mindestens 5,361 vom Originalziel entfernt. Ein dichter Ankunftsnachweis fehlt. **Kampfübernahme während des Flugs ist ein konkreter Prüfkandidat; eine isolierte Transport- oder Navigationsursache ist noch nicht belegt.**

### Source87

P2 B2/Generation 8: 40 Proben/Ticks 6952–6991, botB-closed.log Zeilen 7460–7531. Originalknoten 87: Radius 1, Jump-Flag 2. Im aufgezeichneten erneuten Anflug bleibt die kleinste Metrik 2,296623>1, Y fällt bis −5,997, Safety 2 erscheint. Anschließend Bodenroute 46→47→48 (Zeilen 7562/7593/7602/7618). Keine Ankunft im dichten Fenster.

**Früher im selben Leben** liegt allerdings eine native Probe bereits im Knoten 87: Metrik 0,633389, Game 57,299412, inventory.jsonl Zeile 4846. Daher lautet der Befund fehlender Nachweis dieses späteren Wiederanflugs; „Knoten 87 unerreichbar“ wäre falsch. Eine ursächliche Korrektur braucht die tatsächliche Verarbeitungskette und darf daraus nicht geraten werden.

### Abnahmematrix

| Originalkriterium | Belegt | Konkrete verbleibende Grenze |
|---|---|---|
| Welt/OriginalNAV/CRC/Runtimebindung | Drei Red-Phasen, 193 Originalknoten | Keine andere Karte daraus freigeben |
| Reset plus acht aktive Bots | Tatsächliche 1/2/3_begin, native 2/2/0 min, zwei Reloads, 24/24 Aktivität, korrekt geänderte Registry | Nur Red→Red→Red; keine Rückkehr aus anderer Welt |
| Item- und Waffenzuordnung | 55 echte Aufnahme-Leben, mehrere Klassen, nativer Besitz und Feuer | Lange erfolglose Leben; schnelle Beschaffung nicht in jedem Respawn belegt |
| Nord-Bouncer und Höhe | Sieben Original-Reached-Erfolge mit Flug und Nachfolger | Kampfübernahme P1 B3; keine vollständige Startlagen- und Kampfmatrix |
| Weitere Verbindungen und Sprünge | Knoten-/Zielwechsel, vier GroundReplan und zwei HopCheckpoint | Recovery-Marker sind no_hop_progress/landed_below, keine Routenabschlüsse |
| Source87 | Sprunginput und Weiterbewegung; frühere Knotennähe | Späterer Wiederanflug nicht erfolgreich belegt |
| Teleporter | OriginalNAV hat genau einen Flag32-Knoten: 12 mit Flags42 und Link34 | Quellcode nennt ihn Bouncerroute. Flagname oder Positionssprung ist kein Teleporterbeleg. Weltobjekt/Ein-/Ausgang bestimmen oder Nichtvorhandensein belegen |
| Locks und Interaktion | LockApproach an Knoten2; zwei Interaction an175/Entity544 | Beide Interaction sind not_usable (A-Log2081/3589); kein Tür- oder Interaktionspass |
| Sichere Wege und Gefahren | Begrenzter Stillstandsbefund und Recovery | Keine gezielte Fall-/Gefahrenabnahme sämtlicher Höhenrouten |
| Kampfqualität und Tiers | Fernfeuer und Tötungen auf DEMON | A3-Public- und Tiervergleich separat |

Eine native Positionsänderung über 40 Einheiten in 0,45 s liegt auf hoher Flugbahn und hat keine Teleporterbindung. Sie wird nicht als Teleport gezählt. Die Flag32-Metadaten stehen in metrics.json. Fehlender Teleporterbeleg bedeutet auch nicht nachgewiesene Existenz eines Teleporterfehlers; zunächst Anwendbarkeit der Mechanik für die gehashte Welt klären.

Frühe Inventarerfassung vor Vanilla-Ready: P1 Game 7,950→19,650 mit 135 akzeptierten Gruppensamples; P2 Game 4,000→15,000 mit 125. Anfangsleben vorher bleiben linkszensiert. Fünf/eine während Änderungen verworfene Probe bleibt verworfen. early-phase-*-inventory.json sind Zwischenreceipts; die Registrybestätigung erfolgt danach im Controller. Keine Erstprobe wurde als Pickup umgedeutet.

## Vergleich zum kurzen Build017-Fenster

Vorherige Analyse: /srv/tse-a4-build017-dense-analysis-20261112; analysis-result-SHA 3ccb261678d6d97b1d49e61d4c1f4b265e4872e8b00b7203fae83bc2767b701c. Identische DLL und bytegleiche adapter_policy.py geprüft.

| Größe | kurzer Lauf, weiterhin FAIL | längerer Lauf |
|---|---:|---:|
| Leben | 75 | 178 |
| nützlicher Besitz | 34 (45,3 %) | 57 (32,0 %) |
| beobachtete Aufnahme-Leben | 31 | 55 |
| native Fernfeuer-Samples | 755 | 1.563 |
| Slotphasen mit fehlendem Aktivitätsfeld | 3 | 0 |
| bedingter Median der ersten Besitzprobe | 9,550 s | 9,950 s |

Mehr Zeit verändert Ereigniszahlen, Nenner und Begegnungen. Weder 24/24 noch bedingte Verteilungen belegen bessere KI. Kein Grund, die alten Fehlphasen umzuwerten.

## Cleanup, Restore und Ressourcen

Rootpostflight: alle vier Rollen normal geschlossen, vier akzeptierte Closed-Logs, 643 exakt wiederhergestellte reguläre Dateien plus fünf bestätigte Abwesenheiten. Vier Labwurzeln quieszent, beide Displays abwesend, keine Cleanup-Fehler. Beobachtung 423,836349 s im separaten 480-s-Protokoll; keine automatische Wiederholung.

400 Hostproben: CPU maximal 57,3201 %, MemAvailable mindestens 1.894.895.616 B, freier Speicherplatz mindestens 14.925.201.408 B. Die Grenzen 75 %/1,5 GiB/8 GiB wurden in den beobachteten Werten nicht verletzt. Globale Probenlücke 47,496 s bei Start/Transition; Gameplay maximal 2,370 s. Original budget_pass_claim=false bleibt bestehen; kein lückenloser Ressourcen-PASS.

## Nächste konkrete offene Prüfung

Keine weitere Verlängerung auf Verdacht. Vor einer produktiven Red-Whitelist ein vorab begründetes, begrenztes Funktionsprotokoll:

1. Nordkante 68→6 mit sichtbarem Gegner während des Flugs prüfen: Originalknoten und Radius, vollständige zeitgebundene Entscheidung bis sichere Landung bzw. Tod/Zielverlust. Ausgangsbeleg P1 B3/Ticks5011–5068. Kampfeingriff von verlorenem Flugziel trennen; keine Native-Writes oder Radiusvergrößerung.
2. Tatsächliche Teleporter-, Lock- und Gefahreninventarisierung der gehashten Red-Welt abschließen. Nicht vorhandene Mechanik als nicht anwendbar begründen; vorhandene Ein-/Ausgänge mit Entity/Leben/Mapepoch und Weiterweg gezielt abnehmen.
3. Einen echten Weltwechsel zurück nach Red abnehmen, sofern die produktive Rotation freigegeben werden soll: erneute Originalbindung, Rotationsepoche und acht aktive Bots.
4. Waffenversorgung mit allen Leben bewerten. Der 63,454-s-Fall bleibt konkreter Qualitätsfall; jetzige Daten rechtfertigen keine geratene Parameter- oder Gameplayänderung. A3 bleibt separat.

Review-Handoff, **keine Native-Startfreigabe**. Root entscheidet die weitere Ausführung.

## Reproduktion und Artefakte

Alle Analyseskripte nutzen Stdlib, geschlossene Quellen, eigenen Offline-Lock und nice10; sie importieren keinen Runtimecontroller. Ausgaben ausschließlich in diesem Verzeichnis. analyze.py PID1220452 Exit0/1,68s; correlate.py PID1221436 Exit0/1,03s; metrics.py PID1221824 abgeschlossen. Kein Spielstart, kein Build, keine Controller- oder Spielsuiten.

~~~bash
python3 -B /srv/tse-a4-build017-extended-analysis-20261112/analyze.py
python3 -B /srv/tse-a4-build017-extended-analysis-20261112/correlate.py
python3 -B /srv/tse-a4-build017-extended-analysis-20261112/metrics.py
python3 -B /srv/tse-a4-build017-extended-analysis-20261112/finalize.py
~~~

all178-lives.json/CSV enthält alle Lebensdaten, all24-slotphases.csv die Aktivität. life-observations.jsonl und life-log-bindings.json erhalten die Rohzuordnung; long-unarmed-cases.json enthält die zehn langen Fälle. navigation-cases.json hält die exakten Kanten- und Source87-Belege fest. parsed-closed-events.jsonl enthält Marker und Rohzeilen. clock-calibration.json erhält die abgelehnte Uhrannahme; original-nav-nodes.json den Originalgraph. data-checks.json und analysis-checks.json dokumentieren die Integritätsprüfung; source-pins.json und artifact-pins.json die Hashes.

Kein Quell-, Controller- oder Runtime-Delta. Nach dem Handoff ist der Worker idle.
