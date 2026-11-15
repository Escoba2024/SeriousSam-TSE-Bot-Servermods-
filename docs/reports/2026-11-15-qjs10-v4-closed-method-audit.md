# QJS10 V4: geschlossener Observer-Nachweis

Die passende Kontrolle und der Trace sind begrenzt bestanden. Der archivische Vollreplay bestätigt den Observertransport und vier tatsächlich beobachtete Hookarten. Er ist keine A1-, Schadens- oder vollständige ABI-Abnahme. In beiden Armen gab es keine Eingabe und keinen initialen PENDING-Discard; der neue Nullanimator-Zweig ist damit nativ weiterhin nicht qualifiziert.

Der Trace enthält 53 vollständige IPC-Wireframes, 199 strikte Drain-Pakete und 2.870 vollständig geordnete Ereignisse aus 1.435 vollständig zurückgekehrten Aufrufen. Alle Serialnummern 1 bis F=199 stimmen mit den exakten archivierten Journal-Bytebereichen und SHA256 überein. S=198, der positive Cutoff umfasst 2.870 Ereignisse; das eine Tailpaket enthält keine zusätzlichen Ereignisse. Alle Pakete einschließlich Tail bestehen den unveränderten Packet-/TraceValidator. Alle 53 IPC-Aufrufe enden innerhalb ihrer jeweiligen Frist und der absoluten Observerfrist; 58 Legacy-Metadatenquittungen sind ohne Fehler vorhanden.

| Hookart | Eintritt / Rückkehr | Abgrenzung |
|---|---:|---|
| ProcessGameTick | 205 / 205 | Main-Thread-Kontext, vollständig gepaart |
| ApplyAction | 410 / 410 | registrierte Originalakteure |
| PostMoving | 410 / 410 | registrierte Originalakteure |
| CastRay | 410 / 410 | ausdrücklich unregistered; kein Bullet-/Treffernachweis |
| übrige 14 Arten | je 0 / 0 | einschließlich Initialize, Tod/Respawn, Waffen-/Bullet- und Schadenspfade unbeobachtet |

Keine Drops, Faults, verlorenen Fehler, abgebrochenen Rückkehren oder ausgeschlossenen Entryversuche; final kein offener Call. Genau ein tatsächlicher Getter-Callback bindet TLS auf dem aufgezeichneten Server-Hauptthread nach 38 ms. Der kalte archivierte Runtime-RPC meldet tatsächlich QJS, denselben Server-PID, ia32 und Pointergröße 4; nicht nur einen angeforderten Runtime-Namen. Dieser Befund qualifiziert weder zusätzliche GetTLS-Aufrufe noch unbeobachtete Funktionen. JS-Wallclock, Host-Monotonic und native Spielzeit werden nicht zusammengeführt.

Der erste Stop schließt die Admission, quittiert aber noch keine vollständige Entfernung der Hooks: stopped=false, danach echte Idle-Quittung mit allen Callback-/Callzählern null, anschließend finishstop=true. Alle 38 erwarteten, rebasierten Originalregionen stimmen vor und nach Unload/Detach vollständig überein; äußere Identität bleibt gleich. Der eigene Worker endet mit -15 ohne sticky Fehler nach normalen Rollencloses gemäß dem geerbten gezielten SIGTERM-Reap. Das ist kein behauptetes exit0 und kein beobachteter Frida-Crash. Roots getrennte Restorequittungen belegen je 664 Dateien, 9 Absenzen, beide Namespace-Zeitstempel und drei normale geschlossene Rollenlogs; dieser Audit wiederholt keine Runtime-Restaurierung.

| Messung | Kontrolle | Trace |
|---|---:|---:|
| eigene CPU-Samples | 50 | 52 |
| Bindefehler | 0 | 0 |
| Host-Samples | 13 | 13 |
| maximal gemessene Host-CPU | 45,5142 % | 66,8113 % |
| größter Host-Sampleabstand | 26,3410 s | 26,0828 s |
| vollständiger Hostbudget-PASS | false | false |

Alle archivierten Prozess-/Cgroup-Deltas wurden aus den tatsächlichen Leseintervallen erneut berechnet und stimmen exakt überein. PID/Start werden gegen beide Rohlesungen und Rollen-/Workerpins geprüft; Cgroup-Pfad/Dev/Inode und Rohcounter bleiben strikt. Startup-/Endlücken und die durchgehend fehlende unbenutzte botB-Domain bleiben UNKNOWN. Prozess- und Cgroup-Domänen überlappen und werden nicht addiert; es gibt keine behauptete CPU-Ursache oder Verbesserung durch QJS/FPS10.

Der nächste getrennte NaturalAI-Zweiakteur-Fall benötigt einen tatsächlich gebundenen eigenen Bot-AI-Schützen mit eigener Bot-DLL und eine unveränderte Original-Opferrolle. Diese Rollenbedingung ist neu: die jetzigen beiden Akteure sind Originalclients. Erforderlich bleiben der tatsächliche Ein-Local-Bot-/Registry-/Hash-/Life-Nachweis und beobachtete Waffen-/Bulletowner-/Cast-/ReceiveDamage-Ketten. Vor Arm erfolgte Joins sind links zensiert; es wurde kein Initialize oder erster gültiger Respawnzustand beobachtet. Normaler und ausreichender tödlicher Schaden ab diesem Zustand sowie die Bot-Opferklasse bleiben gesonderte Nachweise. Kein weiterer stationärer Trace wird aus diesem Audit vorgeschlagen.

Reproduktion: `python3 -B tools/audit_first_state_qjs10_v4_closed.py --output <neue-private-Datei>`; ergänzende Metadatenprüfung `/srv/tse-qjs10-v4-closed-audit-evidence-20261115/finish-audit.py`. Der Vollreplay lief einmal vollständig; ein vorangegangener Leser-Konstruktionsfehler nahm fälschlich eine ID im inneren reply statt im äußeren Frame an und stoppte schon am ersten Frame. Er ist separat erhalten und keine Native-Regression. Nur dieses geschlossene Fallpaar wurde gelesen; keine Original-/Nav-/Runtimezugriffe, Tests, Paketerzeugung oder neue Nativeaktion.

Private Vollquittung: `/srv/tse-qjs10-v4-closed-audit-evidence-20261115/full-receipt.json`, SHA256 `02c77041d47ffe217a8a8e6128423ebc2676b459fc08ff2065c67444265766ed`. Ergänzung und finale Übergabe enthalten sämtliche Source-/Raw-/CPU-/Restorepins. Outputs zusammen unter 1 MiB, Readbudget 64 MiB; der vollständige Leser benötigte rund 8,14 MB.
