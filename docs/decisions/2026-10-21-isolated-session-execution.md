# Isolierte Ausführung individueller Retail-Sitzungen

Datum: 21.10.2026. Geltungsbereich: PR #47 auf `ubuntu-4gb-nbg1-2`.
Keine Produktionsaktivierung oder neue DLL-Abnahme.

Der tatsächliche Fortsetzungspunkt ist `2914e1c`, Worktree
`/srv/tse-identities-20261021`, Branch `agent/identities/20261021-sessions`.
Der vorhandene SQLite-Planer, PLC4-Adapter und die unveränderte qualifizierte
Build04-Human-KI werden weiterverwendet. Der neue `SessionExecutor` verbindet
diese Komponenten; er erzeugt keine zweite KI oder einen zweiten festen
Populations-Supervisor. PR #46 und dessen offene lokale Änderungen bleiben
unangetastet. Seine frühere Stundenmessung ersetzt keine Abnahme von acht
einzelnen Wine-Prozessen.

Jede private Identität erhält eine eigene Spielkopie und einen Wine-Prefix als
Overlay über den vorhandenen unveränderten Installationen. Prozessbindung:
PID, Startticks, CWD, UID und cgroup. Startabsicht und reguläres Leave erhalten
vor ihrer Außenwirkung einen persistenten einmaligen Claim pro Identität/Epoche.
Bei unklarem Start gibt es keinen automatischen zweiten Spawn. Ein bestätigter
Prozess allein gilt nicht als Join. Abgang benötigt Prozessende und drei
vollständige aufeinanderfolgende GameSpy-Abwesenheiten; Ghosts bleiben gesperrt.
Der Planer behält seine zufälligen Sessions, Pausen, Human-Reserve, Rate-Limits
und den persistenten Admin-Halt. `min_bots` verschiebt ausschließlich geplante
Abgänge; Admin-Halt und menschliche Kapazität haben Vorrang.

Der Native-Runner ist standardmäßig nur lesend. Ausschließlich `--execute`
mit aktivierter privater Konfiguration kann Spiele starten. Eine hostweite
Kernel-Sperre serialisiert seine Qualifikationen. Der innere Controller läuft
in einem neuen Linux-Netzwerk-Namespace ausschließlich mit Loopback. Somit
kann auch der Retail-GameSpy-Port bei internem Wildcard-Binding nicht ins
öffentliche Netz gelangen. Keine Firewall-/DNS-/Produktionsänderung erforderlich.
Die Namespace-Prüfung verwendet Kernel-Interface-Abfragen; das nicht neu
gemountete `/sys/class/net` zeigt weiterhin Host-Interfaces und ist hierfür
kein geeigneter Beleg. Der Namespace-Smoke wurde auf diesem Host ausgeführt.

Ein äußerer Controller prüft fortlaufend die unveränderten öffentlichen
PID-/Start-/CWD-Bindungen, vollständige öffentliche Rosterabfragen, eigene
Syncfehler und frische Telemetrie. Neue Testlast wird bei weniger als 768 MiB
verfügbarem RAM, weniger als 8 GiB Platte oder drei aufeinanderfolgenden
Fünfsekundenfenstern mit mindestens 85 % Host-Auslastung beendet. Diese
Abbruchschwelle ist keine pauschale Kapazitätsfreigabe. Vor jedem zusätzlichen Client werden darüber hinaus 300 MiB Startbudget verlangt (insgesamt 1068 MiB verfügbar). Der innere Prozess
erhält ein Parent-Death-Signal für den Verlust seines äußeren Guards.

Die unveränderte Originalclient-DLL bleibt als stationäre Retail-Gegenstelle
verbunden. Nur ihre privaten Anzeigeeinstellungen werden angepasst:
Fenstermodus, begrenzte Software-Render-Bildrate. Dies ist ein Join-/CRC-/
Koexistenznachweis unter Wine; kein Nachweis aktiver menschlicher Bedienung,
eines unabhängigen Windows-PCs oder öffentlicher Browser-Erreichbarkeit.
Farbmarkup wird ausschließlich mit `--color-probe` in private Profile geschrieben.
`colors_enabled` ist seit dem begrenzten nativen Sicht-/Grenznachweis opt-in verfügbar; Standard false. Vier RGB-Farben sind im Original-Scoreboard sichtbar, 22 sichtbare ASCII-Zeichen plus Codes (32 Bytes) vollständig per Query und HUD geprüft. Dies ist ein eigener konservativer Policy-Cap, keine Behauptung über das tatsächliche Retail-Maximum.

REA/Ghidra/Frida werden für diesen belegten Join-/Quit-Pfad nicht zusätzlich
gestartet. Es gibt keine neue ABI-Annahme, keinen Engine-Patch, keine
Speicherinstrumentierung und keine Abschaltung von Sync-Kicks. Private
SQLite-Daten, Profile, Screenshots und Rohlogs bleiben auf Hetzner.

Aktuelle Messungen, Fehler und verbleibende Gates stehen im
[Fortsetzungsbericht](../reports/2026-10-21-session-execution.md).

## Neue Retail-Befunde aus der isolierten Fortsetzung

Nach einem echten eigenen Prozessabbruch liefert Retail 1.07 eine vollständige
Query mit vier Spielern und den Nummern 0, 2, 3, 4. Die Indizes sind nicht
zusammenhängend; `numplayers` zählt Einträge. Der Parser prüft deshalb Anzahl,
eindeutige sichtbare Namen und gültige Slotnummern 0..15, statt die lückenlose
Menge 0..N-1 zu verlangen. Rohe Antworten bleiben privat. Unklare Queries
sperren neue Aktionen und setzen den Abwesenheitszähler zurück; >15 s bleiben
ein Abbruchgrund.

Ein nativer Ghost kann den ursprünglichen Session-Endtermin überleben. Deshalb
bleibt ein positiv gebundener eigener Prozess-Exit vor einem Leave-Claim
persistent erhalten; der spätere Slot-Abgang wird als Crash verbucht. Rejoin
erst nach vollständiger Abwesenheit und Cooldown, niemals durch ein
ungeprüftes Wiederholen des Start-Claims.

## Kapazitätsprüfung und begrenzter Grafikversuch

Der erste Achtbot-Startversuch mit normalen Zeitbändern und aktivierter
Farbkonfiguration wurde nach fünf verbundenen Einzelprozessen bei 970,465 MiB
verfügbarem RAM vor dem nächsten Spawn verweigert (1068 MiB erforderlich).
Die private cgroup erreichte 1322,781 MiB; anschließend 20/20 Unmounts und
unveränderte öffentliche Prozesse. Kein Stunden-PASS.

`low_memory_rendering` ist eine neue standardmäßig deaktivierte, ausschließlich
auf private Bot-Grafikeinstellungen begrenzte Option: normale Texturgröße 6,
Animation/Effekt/Static-/Dynamic-Shadow-Größe 5 statt der höheren vorhandenen
Werte. Die Retail-Symbole sind in der Originalkonfiguration vorhanden;
Dedicated-Originalskripte verwenden bereits kleinere Grafikgrenzen. Weder
Spielphysik, GUIDs, KI noch DLLs werden dadurch verändert. Neuer Native-Nachweis
ist trotzdem erforderlich. Ein Einzelbotlauf über 90 s bestand mit Peak
546,148 MiB privater cgroup; daraus folgt noch keine Achtbot-Kapazität.
Vierbot-/Achtbot-Gegenprüfung bleiben nachweispflichtig. Guards werden nicht
abgesenkt, die Produktionsflotte bleibt unverändert.

## Abschließender Status 22.10.2026

Vierbot-Grafikgegenprüfung 150 s begrenzt bestanden (1047,352 MiB Peak,
12/12 Unmounts). Erneuter Achtbot-Versuch nach sechs verbundenen Bots vor
Client sieben bei 921,137 MiB verfügbarem RAM verweigert; 1068 MiB erforderlich.
20/20 Unmounts, Public unverändert. Der Host bietet unter diesen Schutzvorgaben
keine belegte Kapazität für den geforderten Achtbot-Stundenlauf. Keine Reserve
abgesenkt, kein produktiver Bot entfernt. Ergebnis BLOCKED_CAPACITY.
Alle eigenen Tests beendet; leere eigene cgroups manuell bereinigt. Für die
fehlende Abnahme werden ausreichend isolierte zusätzliche Testressourcen
benötigt; die Begrenzung wird nicht durch geringere Qualitätsanforderungen
oder einen unbelegten Stunden-PASS umgangen.
