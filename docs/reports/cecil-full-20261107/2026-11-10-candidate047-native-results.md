# Normal047: Supply besteht begrenzt, funktionale Routen bleiben offen

Normal047 ist nicht insgesamt qualifiziert. Quelle `d47bcf76d20aede8a24fdb462308f187e3604e57`, Tree `21176801c5ab0583131ecf86adc3a268919a9599`, DLL `1f80eca362ab0fd414f2cf6c24abff3cf4606f94f9786a1611e2824f49aa089e`. Der korrekte Win32-Build kompiliert15 MSVC-Einheiten und linkt PE32/x86; alle28 Overlay-Dateien und47 gesamten Build-Eingaben sind gebunden. Gegenüber046 ändern sich nur Supply-Header und Driver. [Bereinigtes Buildmanifest](build047.json), SHA256 `8d23732433dd9c69756fb8447e1076f299998f14dad89d325b9d5a24d71a1d36`; privates Originalmanifest `3c83964b211bd60bc37242323fa4cc0c387ba8f4acb770a5b321aa216856e398`. Kein Build- oder Native-Kredit anderer Kandidaten.

## Änderung und geprüfter Umfang

Passive gültige Hop-/Fehlkantenhistorie übersteht aktuelleFALL- und begrenzteSTUCK-Phasen. Daraus entsteht keine Luftbewegungs- oder Bodenfreigabe: Ein Checkpoint verlangt weiterhin normalen aktuellen Transit, STAND/CROUCH, statische WorldBase und im selben Tick erfolgreiche gewöhnliche Nearest-LOS. Die vorbereitete Alternatephase bleibt sechs Sekunden lang und verlangt aktuelle Wand-/Bodenprüfung im gemeinsamen16-Strahlenbudget. Graph, Radien, Locks, Ankunft, Spezialregeln und Itemfristen bleiben unverändert. [Passive Hop-Beobachtung](../../decisions/2026-11-10-cecil-passive-hop-observation.md).

Der neue Player-Observer liest nur bei bestehender1Hz-Telemetrie, angeforderter Translation und nahezu null nativer Geschwindigkeit einen festen begrenzten Zustandsstack, Action-/Bewegungsfelder und aktuelle Kamera-/Markerpräsenz unter dem vorhandenen Weltlock. Er verändert weder Actions noch Player-/Enginezustand. Nur das Kamera-Feldlayout wurde mit tatsächlichem MSVC/SDK107 und der originale107-AliveActions-Export statisch geprüft; dies ist keine vollständige ABI-Abnahme. Ein anfänglicher const-GetWorld-Compilefehler wurde vor Link/Installation korrigiert und durch direkte konstante Feldlese ersetzt. Die historische046-Kameraursache bleibt unbewiesen. [Player-Action-Beobachtung](../../decisions/2026-11-10-cecil-player-action-observation.md).

Finale integrierte SDK107-Bridge1242/0 unter ASan/UBSan, neun C++-Prüfsuiten und vier Adapterverträge, Player-Observer14/0, unveränderter Waffenobserver306/0 und tatsächlicher Driver-Actionvertrag bestehen. Alle30 privaten Vorlagen sind gebunden und158 reine Harness-/Readerprüfungen bestehen. Das sind portable/Build-Nachweise, keine zusätzliche native Laufzeit oder Ressourcenfreigabe.

## Vollständige native Fenster

| Prüfung | Tatsächlicher Umfang | Begrenztes Ergebnis |
| --- | --- | --- |
| Supplyv20 | Zehn feste Erstziele und zehn feste Initialleben;590 gültige Ein-Bot-Abfragen, elf normale Abschlüsse | Erste Ziele9/10, Median8,375s/P9512,45s: genuineSupply-onlyPASS. Ein Kohorten-Timeout und zwei spätere Zensoren bleiben erhalten. |
| Skulls |600,005819s/595 Abfragen, volle Abdeckung, alle acht positive Scoreänderungen, maxquiet5,040954s, keine erkannten Monitorfehler, drei normale Abschlüsse | Numerische Grenzen erfüllt;169s Important-Transit und separater30s TELEPORT-Kontext bleiben funktionalOPEN. |
| Hole |600,007189s/595 Abfragen, volle Abdeckung, alle acht positive Scoreänderungen, maxquiet3,025809s, keine erkannten Monitorfehler, drei normale Abschlüsse | Numerische Grenzen erfüllt; zwei autonome begrenzte Alternativketten, ein Todeszensor und ein echter Fehlschlag. Item-/Important-/Liquid-Routen bleibenOPEN. |
| Übrige drei Karten, Original-Retail047, formale Stunden, Ressourcen, Rotation, Recovery, All6+900s | Nicht durchgeführt | Kein rückwirkender oder geerbter Nachweis; kein öffentlicher047-Rollout. |

Session Exit0 ist weder ein vollständiges Funktionszertifikat noch ein Stundenfenster. Noch erfüllt keine047-Messung die3600/3600/7200-s-Gates oder eine vollständige Fünf-Karten-/Waffen-/Sonderaktionsabnahme.

## Supply: fester Nenner und echte Nicht-Erfolge

Die zehn festen Initialleben ergeben8,40/8,40/6,40/9,65/8,35/2,60/2,45/4,85/9,90/12,45s. Median8,375s und nächstrangigerP9512,45s erfüllen unverändert15s/30s. Genau9/10 der chronologisch ersten ausgewählten typisierten Waffenversuche sind anhand tatsächlicher Zielentity, neuem korrektem Besitzbit, angrenzendemGoalEnd, räumlicher und gleicher Lebenskontext-Korrelation belegt. `goal_picked=0` zählt nicht allein; weder eine universelle2,5m-Reichweite noch ein instrumentierterReceiveItem-Aufruf wird erfunden.

Rang6/Fall3/Grenade544 endet tatsächlich alsTimeout756→996=12s. Alle26 Waffenstarts bleiben erhalten:23 korroborierte Erwerbe, dieser eine Timeout und zwei rechtszensierte Nichtkohortenversuche (Ränge20 und26). Alle31Goalstarts und Wiederholversuche bleiben im vollständigen Replay; keine spätere Wiederholung ersetzt ein Initialleben. Bei mehreren Initialleben ist der erste nützliche Pickup eine beiläufige Shotgun, während das gewählte Flamer-Ziel erst später folgt. Erstzielquote und Erstpickup-Latenz sind verschiedene Messgrößen.

Zehn PID-/Kernelstart-Epochen, elf normale Unit-Abschlüsse, zehn tatsächlichePop0-Drains und17 geschützte Original-/Konfigurationspins sind gebunden. WM_CLOSE-Unitstatus1 der Bots bleibt erhalten und wird weder alsSyncfatal noch alsExit0 umbenannt. Server-Normalabschluss und Slotdrains sind separat persistiert. Main und unabhängiger vollständiger Rohreview bestätigen nur diesen Supply-Scope.

Supply-Main-Verdict `70eed048b525ff23eb375069d0c47180616bc3a1bddab84f0077d24bdea5464d`, unabhängigerReview `8108e048211b2b7ee9a47fc01cf049585e836192e3fa1a9d06a0ae046fd940da`; Protokoll `76e5b428a15a103cc350dac36b173509e41746f42383bbb9d34864c83ff5f12e`, numerischerAudit `e3b4f4c2dbf0f3e3c3011bd5fe8248e786993e0020b98811dbb749a510d29e14`.

## Skulls: Important-Transit und TELEPORT bleiben getrennt offen

Im selben Leben und Ziel150 wechseln170 Sekundensamples über169s zwischen gewöhnlichen Hops226/236, ohne sichtbaren Gegner oder Schusszähleranstieg. Rund793,682m summierter Weltweg beweisen keine Zielannäherung; erst späterer Combat beendet den Kontext. Das originale Ziel bindet ArmorItem1770. Die globalenImportant-Prädikate schützen im047-Adapter auch die gewöhnliche Anreise. Eine echte private Original-NAV- und synthetische portable Reproduktion belegt diesen Prädikatsunterschied; sie beweist keine genaue ungesampelte native Resetfolge oder spätere körperliche Heilung.

Ein separater30s-Verlauf zu Ziel224 bleibt offen: Flag32 istTELEPORT, nichtIMPORTANT64. Die Important-Hypothese erklärt ihn nicht. Ein geloggterAnchor−1 beweist auch keinen Aufruf des Pure-Navigators mit ungültigemAnchor, da der native Tick vorher überReacquire zurückkehrt. Fünf Checkpoints zeigen begrenzte physische/gerichtete Folgen, teils combatkonfundiert; keinePatrol-Tags in diesem Fenster. Drei tatsächlich begrenzte gemappte Waffen13-Versuche endenTimeout und bleiben als solche erhalten.

63 strenge Health-Death→Folgegeneration-Respawnpaare liegen im tatsächlichen Fenster (26A+37B), maximale beobachtete Aktivität nachSpawn0,95s. Die gefiltertenPlayer-Beobachtungen zeigen keine aktuelle Kamera-/Markerpräsenz; keine exhaustive Negativ- oder Ursachenbehauptung daraus.

Skulls-Main-Verdict `33e4c095858492cfd6c31ccf032f656cea11899eb56da4c2d0a65d2520ebd1d7`, eingefrorener unabhängigerReview `a6b4a46d07b3dede92fd8381f98a19c56a1d76ed6a2879a5d61c5992439251fd`.

## Hole: zwei echte Alternativketten, ein Todeszensor, ein Fehlschlag

34 Checkpoints und10Patrol-Tags enthalten vier tatsächliche Alternativversuche. A2/g7 erwirbt nach Hint69 bei98,05s tatsächlich gewöhnlichOriginal69 und setzt im selben Leben vor Combat die Navigation fort. Die1Hz-Probe1960 liegt innerhalb des unverändertenRadius2. A2/g13 erwirbt69 bei426,60s und zeigt bei fehlender Gegnersicht/konstantem Schusszähler anschließend69→70→77→80→81 samt echter Höhenfolge. Hier verpasst1Hz die direkteInside-Radiusposition; Original-Navigator-Kontrollfluss und nachfolgende physische Bewegung sind getrennte Belege, keine erfundene gesampelte Radiusankunft oder Trigger-ID.

A3/g5 bewegt sich zumHint52, stirbt aber vor Ende der festen6s-Frist: Todeszensor, kein Erfolg. B0/g12 meldet ausdrücklich `exhausted_candidates`; neuesImportant-Ziel12 führt wieder zuHop50. Kein versteckter fünfter Erfolg und keine ungesampelte freie Alternative wird angenommen.

Die unabhängige Prüfung erhält15 ganze Zielzyklen und acht langeSame-Hop-Kontexte. Ihre20s-Auswahl ist Triage, keine neue Abnahmeschwelle. A1/g11 gemapptesItem418 endet nach33,30sTimeout mit vier51→50-Checkpoints; A1/g18 gemapptesItem417 nach exakt45s mit sechs0→1-Checkpoints. Itemziele sind vomPatrol-Alternativmodus ausgeschlossen. Keine nachträgliche Fristverlängerung oder gewöhnliche12s-Erneuerung ist damit belegt. A1/g14 gemapptes688 endet `unavailable`, nichtTod/Timeout. Weitere entfernteImportant-Ziele undDIVE-Kontexte (ordinary105/hop85 sowie64/hop86) bleiben hinsichtlich wirksamer Route offen. Jump-/Override-Hops sind nicht als gewöhnliche Fehlkante umklassifiziert.

102 strenge Health-Paare (59A+43B), Death→Spawn höchstens1,9s und Aktivität nachSpawn höchstens1,15sA/.95sB sind vollständig korreliert.42 in-windowPlayer-Snapshots zeigen Kamera0/Marker0 und keinen benachbarten nativenStopped-Zustand; die Filterung schließt ungesampelte ignorierte Actions nicht aus. Die046-Spawnblockade wird weder als047-Ursache übernommen noch durch Abwesenheit einzelner Samples pauschal für geheilt erklärt.

Hole-Main-Verdict `dafe40b0437e556db8de3b043906b84b8ab5b9246a21d975025693309cc52dcd`, unabhängigerReview `f626fbb926147be076f92bcb3a5cf0b60d96799679ec8b1453cf705c72da715a`, Main-Rohindex `e287982b4effb04032923b11dbebbf63505266699019351009bee9adf101fe52` und gesamterZielindex `c22baa27f4b15542d94184df52350b6d3f48c630082f3f9196cbd08b002be0be`.

## Aktueller Restauftrag und historische Grenzen

165 unterschiedliche aktuelle gesundheitskorrelierte Paare erfüllen Zähl-/Timinggrenzen begrenzt in beiden tatsächlichen Fenstern. Aktivität≤5s **nachSpawn** ist getrennt vonDeath→Spawn≤Presetdelay+5s(default6s). Daraus folgt keine vollständige Lifecycle-, Fünf-Karten-, Recovery- oder Dauerfreigabe. Schussaktionen sind keine direkten Treffer; Wechsel-/Opportunity-/Animationszeitdomänen bleiben separat zu messen.

Die41Bereiche sind an127 aktuelle Quellanker-Vorkommen und14Dateihashes gebunden. Originalkategorien/Schnittstellen und039-/045-/046-Historien bleiben erhalten;151 oder178 frühere Health-Paare werden nicht auf047 addiert. Die Originalmod-Runtime ist weiterhin ein konkreter ECC-/Entities-/Toolchain-/ABI-Zusatzauftrag, keine pauschale technische Unmöglichkeit. GPL-/CPOL-/Patcher-/Vanilla-Grenzen und Veröffentlichungsschutz originaler Spieldaten bleiben verbindlich.

Alle eigenen047-Prozesse sind normal geschlossen. Der289-Dateien-Postrun-Snapshot `d2d0db06e4d1d5cb07ff8ab9a409bfc381a9b333c18b79fff62d7bdd179b54da` belegt Quieszenz/Integrität am Prüfzeitpunkt, kein Gameplay oder Rollout. Die getrennte048-Important-Transitkorrektur ist portabelRED/GREEN geprüft und reviewed, gehört aber nicht zu047 und besitzt hier keinen nativen Kredit; eine weitereLiquid-RCA ist kein behaupteter Fix. Keine047-Stunden, Retail-, übrige Karten-, CPU/RSS-, Rotations-, Recovery- oder öffentliche Flottenprüfung wurde durchgeführt.

Main hat den öffentlichen Bestand ausschließlich lesend um02:12:52UTC geprüft: alle sechs Instanzen mit je acht eigenen Bots, fünf Produktionsinstanzen ohne zusätzliche Spieler und Dev/Hole mit zwei zusätzlichen Spielern. Die fünf Produktionsinstanzen behalten7fc94a39…, Dev/Hole den Normal013-Kandidaten0b3b44de… unverändert;047 ist nicht installiert. Snapshot-SHA256 `8e1dcd92fae5e0682fb8adf8c7bf9ace41dedf55d1769a97c5edf16e429da879`. Diese Momentaufnahme ist keine spätere Start-/Deployfreigabe; vor Änderungen sind Anwesenheit und Besucherschutz frisch zu prüfen.

Gesamtstatus: **Supply-onlyPASS, beide funktionalen KartenrouteOPEN, qualified=false**. Unveränderte Kriterien und fehlende Gates bleiben maßgeblich.
