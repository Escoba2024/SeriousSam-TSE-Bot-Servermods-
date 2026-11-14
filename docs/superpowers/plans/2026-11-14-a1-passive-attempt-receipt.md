# A1: begrenzte Quittung jedes tatsächlichen Emissionsversuchs

Rootauftrag vom14.11.2026; Implementierer `/root/candidate_audit` im eigenen
Worktree ab`e9202ce`. Claims: `tools/a1_passive_xrecord.py`, zugehörige Tests,
neuer enger Paketbuilder, dieser Plan und eigener Bericht. Keine Runtime.

Der geschlossene erste passive Lauf bleibt FAIL. Die abgewiesene lokale Row
wurde vor dem Anhängen geprüft und ging verloren; genaue Counter/Grenzverletzung
ist unbekannt. Cold-XTEST-Initialisierung ist nur eine statisch gestützte
Hypothese, kein Grund für Warmup oder eine höhere erlaubte Sequenzspanne.

1. RED: echte Proxy-/Recorderpfade mit reinem Fake-C-Transport belegen verlorene
   abgewiesene Row und fehlende Cleanupquittung. Keine Displays/Xlib/CDLL.
2. GREEN: max96 Speicherplätze vor bestehendem Nativepfad reservieren, dieselbe
   Row ausschließlich mit schon vorhandenen Counter-/Return-/Zeitwerten füllen.
   Reserviert/native_invoked/Counterprüfung angenommen oder abgewiesen trennen.
   Fehler beim ersten Counter behalten einen ausdrücklich nicht aufgerufenen
   Nativezustand. Keine erfundenen fehlenden Werte. Keine Datei-I/O im Inputpfad.
3. Unveränderte Validemissionsliste und ursprünglichen Guard einschließlich
   `b-a>4` erhalten. Nativeexceptions behalten Vorrang vor Journalfehlern.
   Bei Cleanup neues exklusives0600-Journal schreiben; beide Journalversuche
   unabhängig durchführen und eigene Childbereinigung trotz I/O-Fehlern sichern.
4. Enger deaktivierter Fork vom tatsächlich gelaufenen Rootfreeze`c41b8f20…`:
   ausschließlich Journalquelle, zusätzliche Tests/Builder, eigene Pfade und
   deaktivierte fünf Gates. Methodgetter/Lookup/Metadatenprobe/Core4 unverändert;
   actual167-Methodenqualifikation behalten. Frische Pins und enger Paketdiff.
5. Gezielte Tests/Regressionsfälle, privates Paket, bereinigter Bericht und
   Commit. Root allein integriert/reviewt und entscheidet über einen neuen
   einmaligen Lauf zur Erfassung fehlender Counterwerte.

Ruling Root: Platz96 ist ein hartes Maximum; Versuch97 wird unmittelbar vor dem
Nativepfad abgewiesen, damit kein ausgeführter Versuch unquittierbar wird.
Das präzisiert das vorhandene96Inputbudget; Calls1–96/Inputs/Return/Exceptions,
CP/ACK/EPS/Clock-/350ms-/IPC-/15s-Grenzen und Frida bleiben unverändert.

Reviewkorrektur: Der Peer fand IMPORTANT, dass `self.failed` im neuen
Reservierungsguard auch den erforderlichen Keyup im geerbten Finally vor dem
Nativeaufruf blockierte. Rootentscheidung: ausschließlich dieses Prädikat aus
`reserve_attempt` entfernen; closed/max96, before_input-Stickyblock und
record_emission bleiben unverändert. Der feste InputScope erlaubt maximal48
Aktionen mit höchstens2Forwardaktionen, somit höchstens50Nativecalls; die
97er-Releasekante ist in diesem Protokoll nicht erreichbar. Keine neue
Paarreservierung oder generalisierte Eingabelogik.

Status:14gezielte neue Fälle plus29bestehende Fälle sind grün (43/43,2,443s).
Erste8Journalfälle nach korrigierter Counterfixture tatsächlich8RED; zwei
Builderfälle danach2RED→GREEN. Zwei alte Proxytestdoubles wurden auf den echten
Recorder aktualisiert, statt einen fehlenden internen Vertrag zu kaschieren.
Der neue Releasefall führt echte unveränderte action_step-/Endpoint-/event-
Methoden mit Fake-C aus: Down ausgeführt→Counterreject→finallyUp. Vor Fix war
nur Down ausgeführt (RED), danach Down+Up jeweils genau einmal (GREEN), während
Gesamtergebnis FAIL und neue Eingabephase stickygesperrt bleiben. Ein zunächst
fehlender privater Modulimport war ein Testaufbaufehler; vor RED durch reine
AST-Extraktion der tatsächlichen geerbten Methoden ersetzt.
Frisches deaktiviertes Release-safe-Paket und77/71/14Pins fertig, Bericht
`docs/reports/2026-11-14-a1-passive-attempt-receipt.md`. Rootreview/Integration und
eine mögliche neue Nativequittung bleiben offen. Kein Nativeauftrag läuft,
historische FAILs werden nicht umgewertet.
