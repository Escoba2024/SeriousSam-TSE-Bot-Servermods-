# Integrationsplan – noch nicht ausgeführt

Alle Aufwände sind grobe technische Schätzungen in konzentrierten Entwicklertagen, ohne Wartezeiten und ohne Zusage einer Modelllaufzeit. Erst nach Auswahl durch Simon umsetzen. Vor jeder Umsetzung Live-/Quellstand erneut lesen; parallele bestehende Arbeiten erhalten.

## Arbeitspakete

| Paket | Umfang und konkrete Dateien | Aufwand | Abnahme |
|---|---|---:|---|
| P0 Konsolidierung | Dev ed08e2 veröffentlichen/abgleichen; PR54/55/57/69/91 prüfen, eine Bridge wählen; Source/DLL/Config manifestieren | 0,5–1 | Eindeutige Basis, kein doppelter Planner, Rollback-Hashes |
| P1a Datentreue | Neuer enginefreier CecilNavData-Typ; Original PathPoint/Navmesh-Datenstruktur; vorhandenen Parser nutzen | 1–2 | 9 Rundläufe bytegleich; IDs/Slots/gerichtete Links/Flags/Locks erhalten; falsche Map abgewiesen |
| P1b Navigation | FindNextPoint-Logik adaptieren; vorhandene NavV2-/Supply-Bridge konsolidieren; per-Bot Suchkontext | 2–4 | Alle Paare: Cecil-Parität und Dijkstra-Optimalität getrennt; Sonderkanten ohne falsche Symmetrie |
| P1c Native Bewegung | BotSupplyNative.h + BotDriver.cpp: Graphanker, Locks, up/strafe, Teleport-/Sprungsemantik | 2–5 | Native Stockwerk-/Jump-/Teleport-/Door-Szenarien; normale CPlayerAction; kein Entitywrite |
| P2a Waffenversorgung | bot_redstation_behavior.h, bot_supply_navigation.h, botcore_ai.h beziehungsweise gemeinsame WeaponCapability | 0,5–1,5 | Aufgenommene geeignete Waffe wird nutzbar gewählt; keine Selbstschadensblindheit |
| P2b Items | BotItems.cpp-Regeln über ItemSnapshot; vorhandene item-utility/bridge wiederverwenden | 1,5–3 | Health/Armor/Ammo/Powerup korrekt erreichbar; Invalidierung/Respawn; Randfälle getestet |
| P3 Combat | Originaltabellen BotWeapons.cpp; reine Bewertungs-/Aim-/Targetregeln; Human-Pfad erhalten | 2–4 | Snapshotparität, gültige Waffenindices, Switch-/Feuergates; Vergleichsmessung |
| P4 Bewegung/Recovery | BotMovement-Regeln; FloorProbes aus NavV2 statt mutierendem CheckPit | 1,5–3 | Stuck/Abgrund/Hindernisse, Timersemantik, keine actionlosen Dauerschleifen |
| P5 Presets/Last | BotSettings-Felder in versionierter Config, vier Cecilpresets; bounded snapshots/cache | 1–2 | Presetfixtures, Tick-/RNG-Parität, CPU/RAM-Budget und Regression |
| Q Qualifikation | Isolierter Build, Retailclient, 1/4/8 Bots, Recovery, A/B | 1–3 plus Laufzeiten | VERIFICATION.md-Gates, Original-DLL-/Serverhashes unverändert |

Pakete überlappen teilweise; Summierung ist keine belastbare Projektfrist. P2a kann nach P0 unabhängig von der vollständigen Navigation vorbereitet werden und behebt die kleinste konkrete Verhaltenslücke. P1a/P1b gehen vor nativen Sonderbewegungen. Kein Produktivrollout Teil dieser Analyse.

## Übernehmen statt neu schreiben

| Original | Ziel | Behandlungsweise |
|---|---|---|
| PathPoint.h/.cpp, Navmesh.cpp | vorgeschlagen poc/botcore/cecil_nav_data.h und cecil_path_policy.h | Datenfelder möglichst identisch; Container/Pointer durch stabile Indizes ersetzen |
| FindNextPoint | vorhandene NavigationPlanner-Bridge | Suchsemantik erhalten; Teleport-Heuristikkorrektur separat kennzeichnen |
| BotWeapons.cpp Tabellen | vorgeschlagen cecil_weapon_policy.h | Originalwerte/Attribution; explizite Enumabbildung |
| BotStructure.cpp BotWeapons | reine SelectWeapon(snapshot,state) | Besitz, Ammo, Range/Score; UB-/Indexfallen korrigiert separat testen |
| BotItems.cpp | vorhandene ItemUtility/Planner | Originalreihenfolge als Referenz; Entityabfragen über Snapshots |
| BotMovement.cpp BotAim/BotMovement | vorhandene Human/DriverPolicy | Nur ausgewählte Regeln, keine doppelte Actionausgabe |
| BotSettings.h/.cpp | explizites versioniertes Settingsschema | Roh-Struct-Serialisierung nicht übernehmen |
| PlayerBot.es, Patcher, NetworkPatch | kein Zielmodul | Nicht als Modarchitektur übernehmen |

Neue Dateinamen sind Vorschläge, noch keine existierenden Implementierungen. Betroffene native Dateien stammen aus dem ed08e2-Kandidaten. Nach P0 müssen endgültige Integrationspfade festgeschrieben werden.

## Schnittstellenverträge

1. ReadSnapshot liest nur den vorhandenen Clientweltzustand, kopiert Werte und IDs/generation; keine dauerhaft gehaltenen Entityzeiger.
2. Plan(snapshot, nav, state, clock, rng) ist enginefrei, deterministisch bei gleichen Eingaben, erzeugt BotCommand.
3. ComposeCommand validiert aktuelle Waffe, Alivezustand, Winkel-/Geschwindigkeitsgrenzen und ruft genau einen bestehenden SetAction-Ausgang auf.
4. LoadNav prüft Quellhash, Mapfingerprint, Größe, Indizes, finite Werte und unterstützte Flags; unbekannte Semantik fail-closed pro Kante, ohne stilles Entfernen aus dem Export.
5. Map-/Entitywechsel verwirft alte Ziele und Suchcaches. Kein Dateizugriff im Spieltimer.

Nicht alles kann entfallen: normaler Actioncomposer, Respawn-/Slotmanagement, Supervisor und bestehende Syncguards bleiben. Erst nach Paritätsnachweis können doppelte Legacy-Routing-/Waffenlisten entfernt werden. Der derzeitige Supplyfallback bleibt bis zum bestandenen Rückfalltest verfügbar.

## Entscheidungsvarianten

**Empfohlen:** Cecil-Daten und ausgewählte Policies mit dokumentierten Bugfixes; vorhandene Humanfähigkeiten ergänzend erhalten.

**Strenger Referenzmodus:** Originalregeln mit gleicher Reihenfolge/Zeitskala/RNG, aber gefährliche undefinierte Zugriffe abgefangen; jeden unvermeidlichen Unterschied dokumentieren.

**Nicht empfohlen:** komplette Mod/DLL/Patcher übernehmen oder den 193-Punkte-Graphen blind in den symmetrischen Supplygraph konvertieren.
