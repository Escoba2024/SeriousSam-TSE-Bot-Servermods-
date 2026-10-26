# ssam.ai – Log-Prüfung: Performancebefund und abgesicherte Diagnosevorbereitung

**Stand: 26.10.2026, 08:25 Uhr CET.** Der Acht-Bot-Dauerlauf vom Morgen ist fehlgeschlagen und beendet. Die hier beschriebene Optimierung ist portabel und auf erhaltenen echten Logs überprüft; die neue native 25-Minuten-Probe wurde **noch nicht gestartet**. Dieser Bericht ersetzt keine M1-Dauerabnahme und erteilt keine Release-Freigabe.

## Belastbarer Befund

Der vorherige Acht-Bot-Lauf brach nach gemeldeten 1.089,464 Sekunden wegen dreier aufeinanderfolgender Host-CPU-Proben über der unveränderten 85-%-Schwelle ab. RAM- und Disk-Reserve lagen über ihren Mindestgrenzen; zehn vollständige erhaltene Engine-/Spiel-Logs enthielten keine beobachteten `SYNCBAD`, `Too many bad syncs` oder `CRC check failed`. Cleanup und unabhängige Prozess-/Cgroup-/Mount-Inventur waren sauber. Ein-/Vier-Bot-Belege des bisherigen Harness bleiben historische bestandene Belege, der Acht-Bot-Dauernachweis fehlt.

Die private native Prüfhülle las in jedem Prüftick alle Logs vollständig und wendete dieselbe vergleichsweise teure Regex erneut an. Ein rein lesender Benchmark mit niedriger Priorität auf **denselben zehn erhaltenen Logs** zeigt:

| Operation | Median CPU-Zeit je vollständiger Prüfoperation |
|---|---:|
| Original: vollständiges Lesen/Dekodieren und Regex | 0,515609 Sekunden |
| Neuer Vorfilter, weiterhin vollständiges Lesen/Dekodieren | 0,070742 Sekunden |

Das entspricht **7,289-facher Beschleunigung beziehungsweise 86,280 % weniger CPU-Zeit für diese Prüfoperation**. Der Korpus blieb anhand von Inode, Länge, Zeitmetadaten und Inhaltshashes unverändert; Referenz und Optimierung lieferten auf allen enthaltenen Logs dieselben Treffer. Das ist **keine** Messung von 86 % weniger CPU für den gesamten Gameserver und noch kein Beweis, dass die Gesamtlast einer neuen Acht-Bot-Session dauerhaft unter dem Guard bleibt.

Die CPU-Zeitreihe der zuvor getrennt erfassten Spielprozesse erklärte nicht die gesamte Hostlast; zusätzliche Python-/Wine-/Xvfb-Anteile konnten im alten Lauf nicht vollständig zugerechnet werden. Die neue Probe soll daher zusätzliche zeitlich gemeinsame, private Host-/Cgroup-/Prozess-CPU-Daten erfassen.

## Was genau geändert wird

Der neue Helper prüft auf mögliche Fehlermarker und führt bei jedem möglichen Treffer weiterhin die unveränderte Referenzregex aus. Unbekannte Pattern oder Flags fallen auf die Referenz zurück. Jede Logdatei wird weiterhin auf jedem Tick vollständig gelesen; es gibt keine unsichere Append-only-, Offset-, Dateigrößen- oder Textcache-Annahme.

Das Elternreview fand vor nativer Nutzung eine zu breite Ausnahme für `sam_strTechTestLevel`: Nach der ursprünglichen Regex ist nur der exakt mit schließender Quote abgeschlossene Identifier ausgenommen. Erweiterte Namen, Zeilenumbrüche oder andere Fortsetzungen dürfen nicht übersprungen werden. Dieser Sonderfall wurde zuerst per RED-Tests belegt und anschließend korrigiert.

**19/19 portable Helper-/Entry-Point-Tests** bestehen normal und mit `python -O`. Die AST der übrigen nativen Harness-Kopie – einschließlich Guards, Session-Lifecycle, CLI, Render-/Action-Konfiguration und Cleanup – ist unverändert. Im eigenen Worktree liegen die neue Kopie und ihr Helper getrennt vom geschützten Original.

- Geschützter Original-Runner: SHA256 `a6cc7b2205d3243ec932123d71293454880ab15526e1a63192cb0bba96859034`.
- Neue eigene Runner-Kopie: SHA256 `8cde5bd5c8e0c7f35cabaece4c83594297b516bf25adaf82a7cd4e263c66b69b`.
- Korrigierter Helper: SHA256 `ae1579b923207345f176becacfde924fcf624aaed1a13db8c9bcc5c08f24d200`.
- GameMP-Kandidat unverändert: SHA256 `7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf`.

Engine, Entities, Dedicated Server, Original-Observer und der GameMP-Build werden dafür nicht ersetzt. Es gab kein Deployment, keinen Push und keine Veröffentlichung privater Logs oder Profile.

## Safety-Review vor der neuen Probe

Der neue Diagnosecontroller nutzt die bestehende geprüfte Heartbeat-/Budget-/pidfd-/Census-Logik, aber ausschließlich für eine eigenständige Diagnose. Ein unabhängiges Review identifizierte zusätzliche Blocker. Ein falscher Sandbox-Pfad wurde auf den realen Hetzner-Worktree korrigiert. Der originale hash-geprüfte, begrenzt wiederholende Receipt-Reader ersetzt unsichere Live-Lesezugriffe auf nichtatomar geschriebene JSON-Dateien; hierfür bestehen drei zusätzliche Integrationsregressionen.

Gemeinsamer `matrix.lock`, gegen Schreibfehler robuster Ausnahme-/Cleanup-Pfad, eine unmittelbar frische Entscheidung gegen doppelte Abbruchsignale und revalidierte Cgroup-/Inner-PID-Generationen sind aus einer getrennten Offline-Arbeitskopie zusammengeführt und überprüft. Die vollständige gemeinsame Testmenge besteht mit **66/66 Tests** in der Sandbox normal und mit `python -O`; auf Hetzner bestehen ebenfalls **66/66 synthetische Tests**. Die dortige native CLI ohne `--execute` bestätigt `DRY_RUN_NO_RUNTIME` mit acht Identitäten. Das ist noch kein nativer Spieltest.

Die unabhängige Endprüfung ist separat umgesetzt und besteht **15/15 portable Tests** normal und mit `python -O`. Sie verlangt das tatsächliche native Schema und den gepinnten Kandidaten, Original-Client, 1.500 Sekunden Messung, keine Cgroup-Drosselung, passenden Cgroup-Bezug, vollständige Guard-Zeitabdeckung mit unveränderten Reserven, mindestens 1.200 Sekunden neun Spieler mit acht gesunden und generationstreuen Botrollen, vollständig gültige 20-Hz-Telemetrie, exakte Cleanup-/Unmount-Pfade und einen vollständigen, eigenständigen Sync-Scan aller zehn Logs. Im Receipt bleiben nur Metadaten, Hashes und Fehlerzähler, keine Rohlogs.

Der tatsächliche rein lesende Hetzner-Bootstrap hat um 08:23 Uhr die fünf Producer-Pins, elf Zusatzinputs, den unabhängigen Endvalidator, den unveränderten Kandidaten, die echten Modulverträge, frische Diagnosepfade und den verfügbaren gemeinsamen Lock bestätigt. Controller-SHA256: `25bf7ab97ffbbe6c32ebbf2eb212ccac1836de970741020b196dc1f8f40f6cc3`; V2-Policy-SHA256: `0868d4262f633cb0fb82e2c41fbf7f0411db8da852c098b8ce0e4a74a04ac909`. Die V1-Policy und die historische M1-Matrix bleiben unverändert.

Der geschützte Native-Outer besitzt im Ausnahmefall ein 180-Sekunden-Wartefenster. Daraus wird **keine** garantierte Global-Lock-Retention für beliebig langes Inner-Cleanup abgeleitet. Der neue Controller muss seinen gemeinsamen Matrix-Lock bis nach eigenem begrenztem Warten und Census halten; unklare Residuen bedeuten HOLD und keine automatische Wiederholung.

## Vorgesehene nächste native Prüfung

Nach vollständigem Safety-Green und erneutem realen Bootstrap: ein einzelner privater, isolierter Acht-Bot-Lauf mit unverändertem GameMP-Kandidaten und derselben Acht-Bot-Konfiguration, `--preset redstation`, eigenem Port 27160 und Display `:157`. Das Messfenster beträgt **25 Minuten**, zuzüglich Startup, geordnetem Drain, Cleanup und Schlussprüfung.

Ein positiver Abschluss darf ausschließlich `DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE` mit `m1_complete=false` heißen. Die Probe prüft die Performancehypothese, Vollpopulation, Action-/Sync-/Cleanup-Befunde und zusätzliche CPU-Attribution. Sie ist weder M1-PASS noch Stunden-/Zwei-Stunden-/24/7-Nachweis.

Für einen Abschluss von M1 bleiben danach neue vollständige 1-/4-/8-Bot-Dauerbelege unter derselben neuen Harness-Provenienz, Recovery und die erforderliche Sync-Ursachen-/Abschlussprüfung offen. Alte Belege werden erhalten, aber nicht als neue Harness-Abnahme umetikettiert. M2–M4 bleiben von der nativen Promotion bis zum M1-Gate getrennt. Öffentliche Releases, Löschungen und Ausgaben benötigen die erforderliche gesonderte Freigabe.

## Reproduzierbare Belege in dieser Arbeitsumgebung

`failure-analysis/log-prefilter-comparison-benchmark.json` enthält die rein numerischen echten Vergleichsdaten. Die Quellmodule und Tests liegen unter `performance/`; die frühere V1-Policy ist unverändert erhalten. Eine neue V2-Policy pinnt zusätzlich die unabhängige Endprüfung, ohne die historische M1-Policy oder die kanonische BLOCKED-Matrix zu ändern.
