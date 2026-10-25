# Integrierter Human-KI-/CPU-Kandidat

Fortsetzung 25.10.: öffentliche Flotte auf Benutzerauftrag deaktiviert; neue
Route-Memory hinter `bot_bExploratorySearch=1` bleibt separat nativ zu prüfen.
Sie speichert ausschließlich eigene Wege und konservative Warnstellen nach
starkem Schaden ohne zuvor sichtbaren Gegner, keine unbekannten Kartendaten.
Ein neuer Build besitzt keine automatische Retail- oder Produktionsfreigabe.

## Fortsetzung Bot AI2 am 25.10.2026

Die aktuellen Quellen enthalten zusätzliche Abfang-/Explosivschutz- und verletzungsabhängige Rückzugslogik. `bot_bExploratorySearch` bleibt nach einer nativen Qualitätsregression standardmäßig 0. `bot_fStrafeScale` bleibt standardmäßig 0; ein begrenzter Privatlauf mit 0,5 ersetzt keine Acht-Bot-Abnahme. Die bekannten qualifizierten DLLs werden nicht verändert.

[AI2-Bericht und Grenzen](../../../docs/reports/2026-10-25-bot-ai2.md): echte Kämpfe und Vierclient-Rejoins gemessen, aber Acht-Einzelclient-Abnahme am RAM-Gate blockiert und keine allgemein stärkere KI freigegeben. `debug_logging` des privaten Session-Harness aktiviert auch begrenzte Snapshot-/Projektil-Diagnostik. Passive Frida-Hooks sind auf eigene isolierte Server mit Originalpins und getrenntem Werkzeugnachweis beschränkt.

Gaming-Pool: `python3 tools/gaming_names.py --count 150 --seed 20261025 --output NEW-CONFIG.json` vom Repository-Root. Ausgabe ist deaktiviert, überschreibt keine Datei und enthält keine BOT-Präfixe. `--advanced-styles` ergänzt Bold/Italic-Vorschläge; Flash bleibt wegen des tatsächlich nachgewiesenen Retail-Decoderfehlers ausgeschlossen.

**Nicht qualifiziert.** Nur dieser Overlay kombiniert die Änderungen; die ursprünglichen Patchdateien #42 und #44 sind alternative Vorschläge und dürfen nicht zusätzlich darüber angewendet werden. Die doppelte Nummer 0008 bleibt als historische Herkunft erhalten, nicht als Ausführungsreihenfolge.

Basis: main 67f1977 mit #43. Imports: #42 f3c9384, #44 7d9e695. Telemetrie-CSV: 21 exakt typisierte Formatfelder statt 22. Die qualifizierten Release-Quellen und 61DC-DLL bleiben geschützt.

## Materialisierung und Build

```bash
python3 poc/candidates/integrated-human-cpu-20261021/apply.py /NEW/gamemp
python3 tools/build_integrated_gamemp.py --sdk /PINNED/SDK --toolchain /INSTALLED/MSVC --prefix /PRIVATE/BUILD/PREFIX --output /NEW/BUILD
```

Der Materialisierer kopiert die gepinnten Release-Dateien sowie alle fünf neuen KI-Header und verweigert bestehende Ziele. Das Buildskript führt die 15 Quellen des Release_TSE107/Win32-Projekts direkt mit cl/link aus, protokolliert Quellhashes und erzeugt einen neuen PE32-x86-Kandidaten. Es installiert keine Software und verändert keine Runtime-DLL.

## Feature-Schalter

| Symbol | Standard | Geltung |
|---|---:|---|
| bot_bHumanAI | 0 | Neue Wahrnehmung/Zielwahl/Aim/Waffenwahl; nur bei AutoCombat aktiv |
| bot_bNullRender | 0 | Überspringt GameRedrawView vor dem Render-Lock; Simulation läuft weiter |
| bot_iNullRenderFps | 0 | Optionales Pacing des NullRender-Pfads |
| bot_iTelemetry | 1 | CSV-Watchdog, ca. eine Zeile/s |
| bot_bDiag | 0 | Zusätzlicher Timer-/Konfigurationsheartbeat |
| bot_iScanInterval | 1 | Nur Legacy-Zielsuche; Human-KI nutzt eigene LOS-Budgets |
| bot_fTargetRange | 0 | Legacy-Reichweitengrenze, 0 unbegrenzt |
| bot_iMaxLosRays | 0 | Legacy-LOS-Budget, 0 unbegrenzt |
| bot_iObstacleInterval | 1 | Intervall der seitlichen Hindernisstrahlen |
| bot_fStrafeScale | 0 | Human-Seitwärtsbewegung bleibt bis eigener Runtime-Prüfung aus |
| bot_iRosterOffset | 0 | Client A: 0, Client B: 4 |
| bot_iProfile0..3 | -1 | Explizite Rosterwahl oder Offset + lokaler Slot |

Human-KI wird einmal pro normalem 20-Hz-Bot-Tick aufgerufen; Legacy-Scanthrottling umschließt sie nicht. Fähigkeitsstufen 1–5 und sechs Personas aggressor, survivor, duelist, controller, marksman, flaky stammen unverändert aus #44. Acht Rosterplätze decken alle Stufen und Personas ab. Ohne wahrgenommenes Ziel liefert die Policy nur den Suchwinkel. Der integrierte Driver erhält dann den konfigurierten Vorwärtsinput und die bestehende Hinderniserholung; tote oder unbewaffnete Spieler bleiben stehen. Globale Wege-/Itemnavigation ist nicht hinzugefügt.

## Abnahme

Portable Tests, vollständiger MSVC-Build, isolierter 1/4/8-Bot-Lauf, originale Retail-Gegenstelle, aktive Kampf-/Bewegungsbelege und 60-Minuten-Sync sind getrennte Gates. Aktuelle Nachweise und offene Punkte stehen im persistenten Integrationsplan. Keine Kapazitäts- oder Produktionsfreigabe aus einem Offline-Smoke ableiten.
