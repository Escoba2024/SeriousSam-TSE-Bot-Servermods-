# Red Station: Cecil048/018/020 Vergleichsplan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Root allein implementiert/integrated und führt native Schritte aus; keine Delegation. Die aktuelle Aufgabe endet bei diesem Plan und Source-/Evidenzaudit.

**Goal:** Die subjektive Navigations-/Stillstandsmeldung anhand gleicher
Red-Station-Bedingungen gegen die tatsächliche048-Botbaseline prüfen.

**Architecture:** Drei getrennte, prospektiv feste600s-Fenster mit je acht
Bots derselben DLL, identischen Nav-/Config-/Server-/Startbedingungen.
Vorhandenen Originalserver-/V3-Hardcontroller ableiten; passive vorhandene
Reader und strikte Source-/Lifeauswertung erhalten. Kein Frida, keine
neue Bot-DLL oder Policyänderung für diesen Vergleich.

**Tech Stack:** Retail1.07/Wine, bestehender privater OwnNS-Controller,
FileTransaction/strict_backend/HostBudget, InventoryReader, V3-OrderedMemory,
vorhandene Ceciltelemetrie und Sync-/Closedlogprüfer.

**Spec:** [Frischer Source-/Evidenzaudit](../../reports/2026-11-14-navigation-baseline-source-evidence-audit.md),
Nutzerauftrag A3/A4 und Rootaufgabe: erneuter Rollout erst bei belegter
Verbesserung von Navigation/Versorgung/Kampf/Sync. Nutzerbeobachtung bleibt
subjektiv, alte FAILs bleiben FAIL. Keine Ausführung durch diesen Plan.

## Grenzen und Vergleichsvertrag

- Keine Änderung an Live, fremden Spielern, IDs, GUIDs, bestehenden Archiven
  oder alten Controllern. Neuer eigener Evidence-/Unitnamespace und vollständiger
  Restore; Eltern- und DLLpins aus dem Audit frisch verifizieren.
- Feste Reihenfolge048→018→020, je600s, je neuer vollständig restaurierter
  Startzustand. Keine erfolgsabhängigen Wiederholungen/Phasencuts. Ein
  ungültiges/ressourcenfehlgeschlagenes Fenster bleibt FAIL; die Dreierreihe
  ist dann unvollständig. Startreihenfolge ist vorab fest, keine Randomisierungs-
  oder statistische Überlegenheitsbehauptung aus drei Fenstern.
- Alle Arme gleicher **Original**-Dedicated-GameMP1c41…, OriginalEngine/
  Entities und eigener unveränderter Originalclient.048 ist die echte
  ec820d-Bot-DLL mit Devprofilwerten; der gemeinsame Server ist eine bewusste
  kontrollierte Bedingung und keine exakte Dev-fe4-Powerup-Reproduktion.
  fe4 gegen OriginalDedicated später gegebenenfalls separat diskriminieren,
  niemals zugleich mit dem Bot-DLLvergleich ändern.
- RedStation World-CRCff3776e0/Nav-CRCe4571656, identische SHA-Payloads aus
  dem Audit,193Knoten,settings preset2. Hard2/UnlimitedAmmo/Blumenblut3/
  Gibs0/Respawnschutz0/kein Zeit-/Fraglimit; gleiche bestehenden Powerup-,
  Itemstay-,Netzwerk-/FPSregeln in allen Armen tatsächlich nativ prüfen.
- Gemeinsame geparste Devkonfiguration mit Profile0–3=7,Seed2026110750,
  HumanAI/AutoCombat/SupplyNavigation/ObstacleAvoidance1,Diagnostics0,
  LogEvery200 und20FPS. Pro Gruppe ausschließlich fester RosterOffset0/4.
  Nicht mit ArenaTieroverride einen vermeintlich identischen048-Stufenwert
  erfinden: unterschiedliche Profilsemantik ist Teil der geprüften Bot-DLL.
- Vorhandene frühe Ein-Bot-/Original-Pausebarriere/achtfache normale Botstarts
  aus dem Original-Hardcontroller in allen Armen gleich. Tatsächliche
  Source-/globalSlot-/Entity-/Life-/Worldzuordnung und gleiche neutral
  beobachtete Anfangsreferenz prüfen. Kein neuer Latejoin, Spawnteleport,
  erzwungener Itemzustand oder privateOriginalinput außer der übernommenen
  normalen Pausebarriere. Externer Ein-Bot-Preflight unverändert; canStart=false
  ist keine Startfreigabe.
- CPU≤75%,MemAvailable≥1,5GiB,Disk≥8GiB, unveränderte Sampling-/Guard-/
  Readbounds und normale Closefristen. Keine parallelen Tests/Publikationen/
  Archive/Compiler. Keine mehrstündige Zusatzschleife für diese Diagnose.

## Reviewfokus

1. Tatsächliche Bewegung kann eine bounded-position-Schleife sein; gleiches
   Ziel/Hop, SameLife-Fortschritt und anschließend echtes Pickup/Feuer prüfen.
2. Links-/rechtszensierte Leben, verschwundene Items, Bedrohungsunterbrechungen,
   Leserfehler und Beobachtungslücken müssen in den Nennern sichtbar bleiben.
3.048-Profil-/Logschema nicht durch020-DEMON-Validator ablehnen oder mit einer
   Default/Fallbackannahme als gültig erklären; exakte versionsgebundene Werte.
4. Serverfe4, Serious3, Gen2 oder anderer Navpayload sind fremde Bedingungen,
   keine ergänzbaren Samples dieses Vergleichs.
5. Sync-/Crash-/Restorefehler sind Betriebsfehler, keine bloßen Messausreißer;
   keine Herkunfts-/Identitäts-/Beobachtergrenze lockern, um sie zu verbergen.

## Aufgabe1: kontrollierte Ableitung vorbereiten, noch nicht starten

**Vorhandene Eltern:**
`/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114`,
Manifesta4568cbe60716887e195f7996ffeed774c1035cadcb11660b644c1fe64b4b2d9.
`run-a4.py` liefert Hard-/600s-/Originalbarriere, Source-/Framebindung,
Transaktion, normale Closes und Schlusslogs;`a4_ordered_memory_v3.py` und
`audit_a4_ordered_memory_v3.py` bleiben byteidentisch.048s
`/srv/tse-cecil-gate8-20261109/native048_safe.py` liefert den vorhandenen
10s-Stillstandsvertrag und verweigert ungeprüfte formale Voraussetzungen;
diese Sperren niemals zum Start formaler Stunden umgehen.

- [ ] Root erstellt einen neuen deaktivierten Vergleichsadapter mit drei
  geschlossenen Kandidatenpins und neuen Namespaces. Keine alten freezes ändern.
- [ ] Engen Offline-RED→GREEN-Vertrag festhalten: falsche048/018/020-DLL,
  Profil/Fallback, Nav, Sourcehash, Serverrolle, andere Schwierigkeit,
  fehlende Rolle/Readattempt, PID-/Entity-/Lifewechsel und Zensierung dürfen
  keinen scheinbar vollständigen Vergleich ergeben.048-Profilprüfung erwartet
  ausdrücklich Expert-Rifle/tier5/marksman,018/020 DEMON/tier3/duelist.
- [ ] Lediglich Kandidatenpins, Versions-Profilprüfung und Ergebnisnamespace
  ableiten; keine Bewegung/Aim/Timeouts oder Datenfilter ändern. Vorhandene
  Reader an048-Logschema offline prüfen; fehlt ein notwendiger Beleg, Status
  NOT_OBSERVABLE und Entwurf zur Rootreview, keine erfundenen Defaults.
- [ ] Vollständiger unabhängiger Source-/Closure-/Gate-/Restorevergleich,
  fokussierte vorhandene Tests, Commit und deaktiviertes Manifest. Kein
  Native-PASS aus Modell-/Quellprüfung.

## Aufgabe2: Root führt genau die festgelegten drei Fenster aus

- [ ] Vor jedem Arm frischer Ressourcen-/Prozess-/Display-/Port-/Lock-/
  Originalhashpreflight; unbekannte Belegung blockiert. Sicherung und
  Wiederherstellungsdateien vor jeder Änderung vollständig vorhanden.
- [ ] Jeweilige DLL plus gleiche zugehörige aktive Konfiguration/Nav in
  ruhenden eigenen Labrollen installieren. Dedicated separat original halten.
  Geladene Module/PIDstart und tatsächliche Seeds/Profil/CRC/Regeln nachweisen.
- [ ] Bestehende Startbarriere exakt ablaufen lassen. Gleichartige feste
  Gruppe-/Slotbindung vor den Outcomes deklarieren; alle Rawreads/Readattempts
  und Sourcecuts erhalten. Bestehende Hotloop-/Query-/Host-/Pinguards gleich.
- [ ]600s vollständige Beobachtung, anschließend normale vier Rollencloses,
  unabhängiger Datei-/Metadaten-/Absenzen-/Closedlog-/PID-/Displayrestore.
  Jeglicher neuer schwerer Fehler stoppt die Vergleichsserie; kein blindes Retry.

## Aufgabe3: geschlossene Belege anhand gemeinsamer Maße vergleichen

- [ ] Pro Slot/Leben SameLife-Bewegung>1m, echte HP-Tode/Respawns, native
  Inventargewinne mit Maske0x3df8, gebundene FIREflags+Sourcegrowth und
  serverseitige eigene Nicht-Suizid-Kills getrennt berichten. Beobachtete
  SameLife-HP-Abnahmen am Server sind reale sparse Schadensbelege, kein
  vollständiger Damage-/Armor-/Angreiferzähler. Queryfrags sind kein
  zugeschriebener Schaden; keine zusätzliche Hookmessung aufnehmen.
- [ ] Den bestehenden maximal10s unerklärten Stillstand unverändert prüfen.
  Den vorhandenen10s/0,75m-Zielfortschrittsmaßstab für geeignete gewöhnliche
  Itemkanten bei allen drei Builds gleich auswerten. Das ist eine gemeinsame
  Diagnose, kein nachträglicher Codewatchdog in048. Echte Annäherung,
  Knoten-/Zielwechsel und bounded-position-Schleifen separat ausweisen.
- [ ] Alle verfügbaren Itemversuche vom Beginn bis Pickup/Timeout/unavailable/
  Tod/Windowende tabellieren. Für Recovery nur nachfolgende gebundene
  Zielannäherung/Inventargewinn/Feuer als Erfolg zählen, niemals allein
  Replan/Reject/Checkpoint/TransitEnd. Nicht beobachtete Spezialübergänge
  NOT_EXERCISED; keine vollständige Cecil-Parität behaupten. Hop-/Goalfolgen
  aus der vorhandenen Telemetrie sind abgetastete Anker, keine kontinuierliche
  Kollisionsspur; Lücken nicht interpolieren oder als Stillstandsfreigabe deuten.
- [ ] Erfolgszahlen mit vollständigen Nennern und Zensierungsgründen ausgeben;
  Latenzmedian/P95 nur mit beobachteter Grundgesamtheit beschriften. Die
  bestehenden Einzelbot-Supply9/10-/15s-/30s-Kriterien nicht auf andersartige
  Acht-Bot-FFA-Leben übertragen oder als hier nachgeprüft ausgeben.
- [ ]048/018/020 nebeneinander, keine historische Stichprobenaddition.
  Einzelne bessere Kills oder kleinerer Standmaximumwert beweisen weder
  allgemeine Überlegenheit noch deren Ursache. Widersprüchliche/zu wenige
  vollständige Episoden ergeben INCONCLUSIVE; keine erfundene Killmarge.

**Weiterentscheidung:** Dieser begrenzte Vergleich kann eine konkrete
Navigations-/Versorgungsverbesserung oder Regression sichtbar machen. Ein
Rollout bleibt gesperrt, solange Navigation/Versorgung/Kampf gegenüber048
nicht belegt verbessert und Syncursache/maßgebliche Nativegates offen sind.
Insbesondere fehlt diesem privaten frühen Originalvergleich der WAN-/aktive
Mensch-/Latejoinnachweis. Keine A-/B-/Langzeitabnahme aus drei600s-Fenstern.
