# Nachweise und spätere Qualifikation

## In dieser Untersuchung tatsächlich ausgeführt

- Alle neun gepinnten BNMV-v6-Dateien geparst; JSON-Rückwandlung erzeugt jeweils byteidentische Originaldaten.
- Testfall mit synthetischem Lockorigin und PPO2-Polygon erhält alle sechs Platzierungswerte und Polygonvertices.
- Abgeschnittene Daten, angehängte Bytes, ungültiger Linkindex und NaN werden abgewiesen.
- 30 Originalwaffeneinträge (15 DM, 15 Coop) mit Originalsymbolen und aufgelösten Konstanten extrahiert.
- Funktionsindex ist ein lexikalischer Index, kein Vollständigkeitsbeweis eines C++-AST.
- Keine GameMP gebaut oder installiert, kein Server neu gestartet, kein Originalclienttest und kein neuer Live-Bot-Test.

Das Testprotokoll wird nach abschließender Ausführung unter exports/verification.json abgelegt. Frühere Supply-/Human-Tests aus dem Handoff sind **historische Nachweise**, keine Tests dieser Arbeit.

## Reproduzierbarer Offline-Test

```bash
cd docs/research/cecilbot-analysis
python3 scripts/fetch_reference.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/export_analysis.py reference /tmp/cecil-export-new
python3 scripts/export_rules.py reference /tmp/cecil-rules-new
```

Neue Ausgabeordner verwenden. Hashmanifest verifiziert gepinnte Referenzbytes. Kein Test verändert Produktivdateien.

## Zukünftige Tests: noch nicht ausgeführt

| Ebene | Szenarien | Vorgeschlagene Abnahme |
|---|---|---|
| Format | ungültige IDs/Slots, finite Werte, Flags, Radius, Locks, PPO1/2, Mapwechsel | Kein Crash/Truncation; unbekannte Version abgewiesen |
| Graph | alle 193×193 Punktpaare, einseitige Links, Teleport, Lock offen/zu | Erreichbarkeit gegen unabhängigen gerichteten Dijkstra; Kosten nur bei passender Heuristik vergleichen |
| Weapon | alle Waffen, Ammo0, InfiniteAmmo, NONE, Spawn, Pickup8/9/14, Switch-CD | Gültige Indizes/Masken; keine Feuerfreigabe auf unpassendes Profil |
| Perception | Occlusion, Modellblocker, Target-CD mit anderem Gegner, Team, Sightloss | Ziel+Distanz konsistent; Sichtsemantik explizit; keine fremden Entitywrites |
| Items | zweites geeignetes Healthitem, ferner AmmoPack, gelöschtes Item, falsches Stockwerk | Erklärbarer Zielentscheid, zeitnahe Invalidierung, keine unerreichbaren Dauertargets |
| Actions | mehrere Tickintervalle, Winkel, up/strafe, Springen, Respawn | Gleiches Steuerziel; normale PlayerAction; keine Doppelkomposition |
| Resources | 1/4/8 Bots, Snapshot/Ray/Search-Budget, mapchange | P95-Kosten und RSS gemessen; keine unbeschränkten Allokationen/Scans |

Die 193×193 Prüfung enthält Selbstpaare; für Routingstatistik diese separat ausweisen. Erreichbarkeit ist keine physische Traversierbarkeit.

## Native A/B/C-Qualifikation auf isolierter Entwicklungsinstanz

A = aktuell tatsächlich geladener ssam-Build, B = originaler gepinnter Cecil-Referenzbuild in **eigener Modumgebung**, C = zukünftiger Clientport am unveränderten Dedicated. Cecil-Mod kann nicht als B auf dem unveränderten Produktionsserver vorausgesetzt werden.

Vor Test: Hashmanifest von Dedicated/Engine/Entities, GameMP, NAV, Config und Map; Compiler/SDK, Modus, acht Botprofile, RNG-Seeds, Tickrate, Waffen-/Ammo-/Schwierigkeitseinstellungen festhalten. Dieselben Startbedingungen/Beobachtungsfenster, mindestens drei Wiederholungen. Wenn Originalmod-Seed/Spawn nicht kontrollierbar: Einschränkung dokumentieren, keine strikte Kausalbehauptung.

Vorgeschlagene Verhaltensgates (vor Umsetzung mit gemessener Baseline konkretisieren):

- Nach Spawn/Respawn beginnt jeder lebende Bot innerhalb 5 Sekunden eine nachvollziehbare Bewegung oder Kampfaktion.
- Mindestens 90 % der erreichbaren Test-Itemziele werden in den vorab festgelegten Szenarien erreicht; nicht global 90 % ohne definierte Start-/Zielmenge.
- Für festgelegte Red-Station-Spawns erste sinnvolle Waffe median <=15 s und P95 <=30 s; Verfügbarkeit/Bedrohungsabbrüche gesondert erfassen.
- Keine ununterbrochene unbegründete Stillstandsphase >10 s; Anteil der Zeit ohne Positionsfortschritt getrennt von absichtlichem Kampfstillstand.
- Nach Pickup einer auswählbaren Waffe geeignete Auswahl innerhalb eines Wechsel-CD-Zyklus; Rocket/Grenade/Cannon separat inklusive Nahbereich.
- Gegnererkennungslatenz, Schüsse/Treffer, aktive Kampfzeit, Waffenanteile, Pickups und Scores je Bot erfassen. Score allein beweist keine bessere KI.
- 100 beobachtete Todesfälle über die Testgruppe: kein dauerhafter Dead-/Slotzustand; Respawnzeiten gemäß Preset.
- Null beobachtete SYNCBAD/CRC/Joinfehler/Kicks; keine Syncschutzabschaltung. Original-Retailclient tritt bei und spielt.
- CPU-Median/P95 und RSS gegen gleiche Baseline messen; vorgeschlagen <=20 % CPU-Mehrlast und kein anhaltendes RSS-Wachstum. Grenze ist ein Vorschlag, kein gemessenes Ergebnis.

Stabilitätsgates des Projekts: 1 Bot >=60 min, 4 Bots >=60 min, 8 Bots >=120 min, danach Recovery/Wiederanlauf. Bei veränderter DLL dieselben Gates mit eindeutigem Hash neu qualifizieren. Erst danach separate Produktiventscheidung. Während dieser Analyse bleiben alle Gates für den zukünftigen Port offen.
