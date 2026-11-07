# Quellen, Stände und Beweisgrenzen

## Gepinnte Primärquellen

| Quelle | Stand | Verwendung |
|---|---|---|
| [CecilBotMod](https://github.com/DreamyCecil/CecilBotMod/tree/953b477e53fdc5a5d84c8ae8d759c84fdf6c973c) | 953b477e53fdc5a5d84c8ae8d759c84fdf6c973c | Vollständige zugängliche Botquellen, NAV, Konfiguration |
| [SDK Includes](https://github.com/DreamyCecil/SE1-ModSDK/tree/94ff8cd0e63941f8601294350b616472f772ed51) | 94ff8cd0e63941f8601294350b616472f772ed51 | TSE107-/TSE110-Properties |
| [Serverbranch](https://github.com/DreamyCecil/CecilBotMod/tree/9b0b4a6f5babb405dd875ae918f28dc2e8627d8f) | 9b0b4a6f5babb405dd875ae918f28dc2e8627d8f | Alternative Netzwerk-/Serverintegration, 27.04.2022 |
| [Wiki](https://github.com/DreamyCecil/CecilBotMod/wiki) | bb02db3fa87102888757bdce58f23bd15c0ad8a8 | Navigationediting, Integration, Befehle |
| [Release 0.2.3](https://github.com/DreamyCecil/CecilBotMod/releases/tag/0.2.3) | 01.02.2023 | Releasehistorie; nicht mit master 2026 gleichsetzen |
| [Autorenseite](https://dreamycecil.itch.io/botmod) | gelesen 07.11.2026 | Dokumentierte Grenzen, Maps, Presets |
| [ssam main](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/tree/ab0c7400353a108f8461bb82280c539fdfe81499) | ab0c7400353a108f8461bb82280c539fdfe81499 | Veröffentlichte Ausgangsbasis |
| ssam lokaler Dev-Snapshot | ed08e2c8efc9366e880da274e70acab53f8bf2a5 | Aktueller Supply-/Parser-/Kandidatcode, isoliert archiviert |
| [Desktop-Handoff](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/tree/4bfb6bff547118a5611a3349143e6bd25dcda3ab) | 4bfb6bff547118a5611a3349143e6bd25dcda3ab | Enthält Dokument, nicht vollständigen neueren Dev-Code |

Quellbelege in den Berichten beziehen sich, sofern nicht anders bezeichnet, auf Cecil master 953b477. Botquellenpfade beginnen mit Sources/Bots/. EntitiesMP-Projekt/Player.es liegen unter Sources/EntitiesMP/, Game.cpp unter Sources/GameMP/; SDK-Properties haben ihre eigenen angegebenen Pfade. Bei ssam gilt der oben genannte Dev-Snapshot oder explizit der jeweilige PR-Pin. Zeilennummern gelten nur für diesen Stand.

Release-ZIP/ausführbare Originalmod wurde nicht installiert und nicht als Laufzeitreferenz ausgeführt. Releaseinformationen liefern daher keine aktuelle Verhaltensmessung. Alle neun zugänglichen NAV-Dateien des master sind erfasst.

## Vor Untersuchung gelesene Projektdokumente

- [Projektprotokoll & Wissensstand](https://docs.google.com/document/d/1odDCeRJhTrWP1xs9ksHKGwqMZPW3zdVSJ5Odr6Urkb0/edit): jüngster vorgefundener Eintrag 27.10.2026.
- [Technische Umsetzung & KI-Handoff](https://docs.google.com/document/d/1C26GfC2E1GHyJnBmbYOXNJ7G7wgMeE3FmqaMbu2UzW8/edit): Stand 21.10.2026.
- [KI-Reviewboard](https://docs.google.com/document/d/1iFauUGivTuxhI1uwE8C2F8gY2HyvoN2xTFPBXSm0pNo/edit): Stand 21.10.2026.
- AGENTS.md, MCP-/AI-Policy 17.10., offene PRs, Branches, lokale Worktrees und laufende Entwicklungsprozesse.
- ssam-ai-live-test-2026-11-07.md: historische Messung 16:24:55–16:26:25 Berlin, 90,62 Sekunden, acht aktive Bots, +31 Scores, sieben Waffenpickups, 47/50 Combat-Stichproben Colt. Keine erneute Messung in dieser Analyse.
- Historischer Live-Build 38e42ae84a8b147411f236e3e015187a27bc1e2a; historische DLL SHA256 ce559971ce4a1677c1b299a7d0c27f148fa4ecace2a55d45e006bdb1598ac6a4. Keine Aussage über eine jetzt geladene DLL.

Ältere Drive-M1-Aussagen werden nicht als aktuelle Live-Telemetrie behandelt. Neuere lokale Entwicklung ist nicht automatisch main oder Produktion.

## Beweissprache

**Bestätigt:** konkreter Quelltext, Exportstatistik oder hier ausgeführter Test.  
**Technische Schlussfolgerung:** aus den Quellen abgeleitete Portierbarkeit/Risiken.  
**Offen / NOT_TESTED:** nativer Build, Verhalten, CPU/RAM, Spielstärke, Sync und Retail-Kompatibilität des zukünftigen Ports.

Keine Quality-Prozentzahl, kein Geschwindigkeitsversprechen und kein bestandenes M1-Gate werden aus Offline-Exporttests abgeleitet.
