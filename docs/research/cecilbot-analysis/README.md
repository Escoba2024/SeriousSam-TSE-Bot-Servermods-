# CecilBotMod – vollständige Übernahmeanalyse für ssam.ai

Stand: 07.11.2026. Status: **SOURCE_ANALYSIS / DATA_EXPORT**, keine produktive Implementierung, kein neuer nativer Spieltest.

## Ergebnis

Eine vollständige unveränderte Übernahme der Cecil-Mod ist mit unserer Vorgabe eines unveränderten Retail-Dedicated-Servers nicht vereinbar. Die Mod verwendet eigene Entities, Player-Anpassungen, direkte Enginezustandsänderungen und eigene Netzwerkpakete. **Die Navigationsdaten und erhebliche Teile der Entscheidungslogik lassen sich dagegen wiederverwenden.** Umfang und Verhalten müssen je Subsystem getrennt behandelt werden.

Nachgewiesen sind die Quellcodebefunde sowie ein verlustfreier Export aller neun zugänglichen Original-Navigationsdateien. Red Station enthält **193 Punkte und 879 gerichtete Verbindungen**, davon 203 einseitige Verbindungen. Die vollständigen Daten wurden weder symmetrisiert noch auf den vereinfachten ssam-Graphen reduziert. Eine native Übernahme, bessere Spielstärke und Retail-/Sync-Kompatibilität sind **noch nicht getestet**.

## Zehn Antworten

1. **Vollständig 1:1?** Nein, nicht als komplette Mod/DLL bei unverändertem Dedicated und originalen menschlichen Clients. Daten können unverändert erhalten bleiben; ein Clientport braucht Adapter.
2. **Was verhindert das?** CPlayerBot/EntitiesMP, Player-/Game-Hooks, eigene Netzwerknachricht 49, Detours, Entityevents und direkte Bewegungs-/Waffenzustandsänderungen. Rohes Struct-ABI ist ungeeignet.
3. **Wie viel direkt?** Alle neun NAV-Dateien sind verlustfrei auslesbar; die Waffen- und Einstellungstabellen sind extrahiert. Ein seriöser Prozentwert für die gesamte KI ist aus Codezeilen nicht ableitbar. Die Übernahmematrix bewertet 41 Funktionsbereiche einzeln.
4. **Größter Nutzen?** Vollständiger gerichteter Red-Station-Graph, sinnvolle Itemziele und konsistente Verbindung von Pickup und Waffenwahl. Diese lösen konkrete aktuelle Lücken.
5. **Welche Daten sofort?** Punktkoordinaten, IDs, Slots, Radien, gerichtete Links, Flags, Lock-/Important-Referenzen, vier Presets und zwei Waffentabellen. Entity-IDs benötigen eine Karten-/Entity-Zuordnung. Sofort auswertbar bedeutet nicht sofort sicher installierbar.
6. **Red-Station-Navigation übertragbar?** Technisch begründet ja. Der Export ist bestätigt; Stockwerke, Sprung, Teleport, Locks und echte Traversierbarkeit müssen nativ nachgewiesen werden.
7. **Combat originalgetreu?** Cecil-Entscheidungen samt Reihenfolge, Zeitbasis und Zufall über explizite Snapshots portieren und gegen ein gepinntes Referenzmodell vergleichen. Bekannte Fehler nicht stillschweigend übernehmen; Abweichungen versionieren.
8. **Architekturanpassungen?** Typisierte Welt-/Item-/Weapon-Snapshots, gerichteter Navgraph mit Metadaten, per-Bot-Zustand, normalisierte Steuerungsausgabe. Vorhandenen BotSupplyNative-/BotDriver-Ausgang erweitern; keine neue Serverarchitektur.
9. **Schnellster sicherer Weg?** Bestehende Vorarbeiten konsolidieren, Pickup/Waffenwahl-Diskrepanz isoliert beheben, vollständige Red-Station-Daten anbinden, dann auf dem Entwicklungsserver qualifizieren. Kein pauschaler Austausch der vorhandenen Human-KI: diese ist in einigen Punkten bereits differenzierter.
10. **Erster Integrationsschritt?** Neues enginefreies CecilNavData-Modul, Importformat mit Slots/IDs/Flags und Tests; Erweiterungen an BotSupplyNative.h, bot_supply_navigation.h beziehungsweise vorhandener NavV2-Bridge sowie BotDriver.cpp erst nach Entscheidung. Exakte Dateien, Schnittstellen und Abnahmen: [ROADMAP.md](ROADMAP.md).

## Dokumente und Daten

- [NAVIGATION.md](NAVIGATION.md): Format, alle Karten, Red Station, Pathfinding, Bewegung, Einschränkungen.
- [COMBAT.md](COMBAT.md): Wahrnehmung, Zielwahl, Aim, Waffen, Items, Taktik, Schwierigkeitsgrade.
- [ARCHITECTURE.md](ARCHITECTURE.md): Abhängigkeiten, ABI, vorhandene ssam-Arbeiten, Lizenzbefund.
- [Übernahmematrix](TRANSFER_MATRIX.md), [CSV](exports/transfer-matrix.csv), [JSON](exports/transfer-matrix.json).
- [ROADMAP.md](ROADMAP.md), [VERIFICATION.md](VERIFICATION.md), [SOURCES.md](SOURCES.md), [PLAN.md](PLAN.md).
- exports/: Kartenstatistik, Referenzmanifest, 30 Waffenzeilen, Einstellungen und Quellfunktionsindex.
- scripts/: strikter NAV-Parser, Exporter, Rekonstruktion der gepinnten Referenzen und Tests.

Vollständige Original-NAV und koordinatengetreue JSON/CSV liegen im privaten Analysepaket. Die öffentliche Dokumentationsfassung enthält Hashes, Quelllinks und aggregierte Daten. Es wurde keine gesonderte ausdrückliche Rechteerklärung für die NAV-Datensätze gefunden. Das ist eine offene Provenienzfrage, **kein nachgewiesenes Weiterverbreitungsverbot**. Reproduzierbare Referenzbeschaffung ist dokumentiert.

Die Untersuchung verändert keine der fünf Produktivinstanzen und auch nicht den öffentlichen Entwicklungsserver. Ein Source-Snapshot ist kein Beweis für die dort geladene DLL. Nach diesem Bericht erfolgt keine Implementierung ohne Auswahl der nächsten Komponenten.
