# CecilBotMod – Untersuchungsplan, 07.11.2026

Ziel: belegte Funktionsinventur, reale Navigationsdaten exportieren, Übernahmematrix und Integrations-/Abnahmeplan. Analyseauftrag; keine produktive Implementierung.

## Grenzen
Unveränderter Retail-1.07-Dedicated und Originalclients. Keine Serveroperationen, DLL-Wechsel oder Runtime-Tests. Eigener Dokumentationsbranch. Bestehende fremde Worktrees bleiben unberührt. Originaldaten nur mit belegter Provenienz/Lizenz.

## Aufgaben und Abnahme
- [x] Prompt und kanonische Drive-Dokumente lesen, GitHub main/PRs und laufende Agenten/Worktrees inventarisieren.
- [x] Quellen und Versionen pinnen; aktuelle lokale Dev-Quelle gegen GitHub abgrenzen; vorhandene Analysen wiederverwenden.
- [x] Sämtliche Bots/Logic-, PathFinding-, Struktur-, Entity- und Netzwerk-Anschlüsse untersuchen. Jede Schlussfolgerung mit Datei/Funktion/Zeile.
- [x] Alle neun vorhandenen NAV-Dateien verlustfrei dekodieren; IDs/Kanten/Flags/Referenzen prüfen; Red Station gesondert auswerten; Export JSON/CSV und reproduzierbarer Parser.
- [x] Funktionen und Konfigurationen exportieren; Waffen- und Zielentscheidungen, ABI, SDK, Lizenz und Synchronisation abgleichen.
- [x] Übernahmematrix A/B/C/D/E/U, konkrete Dateien/Adapter, Aufwand, Risiken und Abnahmeplan erstellen.
- [x] Exporte/Quellenverweise prüfen, unabhängige Abschlussprüfung, Dokumentationsbranch veröffentlichen, Drive-Protokoll/Handoff/Reviewboard aktualisieren.

## Status und Entscheidungen
2026-11-07: GitHub main ab0c7400353a108f8461bb82280c539fdfe81499; Cecil master 953b477e53fdc5a5d84c8ae8d759c84fdf6c973c. Drive-Protokoll zuletzt 27.10.; zusätzliche Live-Test-Übergabe 07.11. gelesen. GitHub main ist nicht gleich Entwicklungsserver-Quelle.
Ruling: Dieser Plan steuert Analyse und Export, keine Softwareintegration. Deshalb keine Produktions-Builds/Gameplaytests; Exportprüfung und Quellbelege sind die Abnahme. Native Verhaltensgleichheit bleibt NOT_TESTED.
Ruling: Isolierter neuer Clone ist die eigene Arbeitskopie; keine bestehenden Worktrees mutieren. Vollständige Klone auf Hetzner verfügbar, lokaler Windows-Netzwerkzugriff ist eingeschränkt.

2026-11-07: Zwei unabhängige Quellen-/Dokumentreviews abgeschlossen. Typ CBotPathPoint/CPathPoint korrigiert; serieller Thinkingablauf, Coop-Catch-up-Teleport und initiale Targetbox präzisiert. Veröffentlichung hält ungeklärte NAV-Datensatzprovenienz getrennt. Vollständiges privates Exportpaket geplant; öffentlicher Branch ohne NAV-Koordinaten.

Abschluss: Quellen-/Dokumentreviews und Offline-Abnahmen erfüllt. GitHub-Dokumentationsbranch veröffentlicht (erster Publikationscommit e0b3891bc84fd3a068b204a86d32ad1c324a3858); öffentliche Dateiauswahl geprüft. Drive-Protokoll inklusive Wochenbericht, Handoff und Reviewboard aktualisiert und vollständig zurückgelesen. Vollständige Exporte werden als privates Analysepaket bereitgestellt. Native Umsetzung bleibt ausdrücklich ausstehend.
