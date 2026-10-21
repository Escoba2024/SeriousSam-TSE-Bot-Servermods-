# Hetzner: nachgewiesene Toolchain und Human-/CPU-Integration

Stand während der laufenden Abnahme am 21.10.2026. Ergänzt die Toolrichtlinie vom 17.10.; historische Shadow-Nachweise werden nicht als neue Hetzner- oder Windows-Abnahme übernommen.

## Tatsächlich verwendet

- Ausschließlich bestehender Hetzner-Host ubuntu-4gb-nbg1-2, zwei vCPU, 3819 MiB RAM, Ubuntu/Wine 9, Xvfb und Mesa llvmpipe ohne GPU.
- Vorhandene MSVC-Distribution 14.44.35207 unter Wine, tatsächliche cl-Version 19.44.35229.0 und Linker 14.44.35229.0, Win32/PE32. Keine neue Installation, Lizenzannahme oder Bestellung.
- Gepinntes ModSDK aa7869c2c2c4db0562281814d0ac3784e6b9d6f0 und Engine107-Includes 94ff8cd0e63941f8601294350b616472f772ed51. Alle 15 Quellen der Release_TSE107-Konfiguration direkt mit cl/link gebaut.
- RDC, GitHub-Connector, Python, g++/Make und bestehende lokale Bibliotheken. Keine zusätzlichen KI-Agenten und kein Shadow-Zugriff.
- GUI-Nachweise mit X11-Bildaufnahme sowie normalen XTest-Tastatur-/Mauseingaben an PID-/Arbeitsverzeichnis-/Fenster-eigentumsgeprüfte eigene Retail-Testclients. Tatsächliche Bewegung, Schaden, Kill/Score und Respawn visuell geprüft. Kein UI-TARS-/Frida-/Ghidra-Smoke wird als Ersatz dafür gewertet.

## Testniveaus getrennt

Portable Suiten: sieben C++-Suiten mit 555 Human-AI-Checks, realer extrahierter Integrationsblock einschließlich Munitionsadapter, 59 Benchmark-/Anschlusstests sowie 41 Parser-/Query-/Preflight-/Betriebsguardtests bestanden.

MSVC-Build04: GameMP.dll SHA256 7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835. Quellbaum 9d7512dc2db395688f7ec0ec116b998d2f4cd764, veröffentlichter Quellcommit 65219c355c08c6859150a9aa9d596f476da5247c. Ein Rebuild ist weiterhin ein eigener Kandidat; die Build-Zeitstempel sind Bestandteil des konkreten Artefakts.

Reales Retail-Multiplayer unter Wine: ein Bot mit Originalclient über 300s und vier Human-/vier Legacy-Bots je 600s bestanden. Originale EXE-/Engine-/Entities-/Vanilla-GameMP-Hashes gepinnt, nur private Bot-GameMP ersetzt. Die Acht-Bot-Stunde mit Originalgegenstelle ist für genau Build04 bestanden: 3600s, alle acht Bots in jedem der zwölf Fünfminutenintervalle bewegt und mit echten Combat-Fire-Aktionen, Scoreänderungen, drei erfolgreiche CRC-Checks, null SYNCBAD und null Disconnects. Median 20Hz, null cgroup-Throttling. Öffentlicher Betrieb wird separat geprüft.

Nicht neu nachgewiesen: nativer Windows-/GPU-Client auf einem unabhängigen Spieler-PC, 24/7, mehrere Maps, 16+ Bots. Externe Query, Masterliste und In-Game-Browser bleiben eigenständige Gates.

## Architekturentscheidung

Der bestätigte Renderer-A/B-Vergleich der älteren P0-DLL verwendet drei Paare mit 180s Warm-up und 600s Messung, vier bewegten Bots mit 20Hz, null Sync-Fehlern und null cgroup-Throttling. Mittlere Ersparnis: 78,74% Client-CPU und 66,85% gesamte Test-cgroup. Ein späterer Vergleich der fertigen Version wird separat dokumentiert.

NullRender überspringt Renderarbeit, während native Engine, Netzwerk, Physik und 20-Hz-Aktionspipeline weiterlaufen. Xvfb/GL-Kontext werden beim Start weiterhin benötigt. Ein eigener BotHost oder vollständiger Architekturumbau ist für die aktuelle Acht-Bot-Abnahme nicht Voraussetzung; er würde neue ABI-/CRC-/Runtime-Gates benötigen.

Optionale Legacy-Scanthrottles bleiben konservativ; sie umschließen die Human-Policy nicht. Seitwärtsbewegung bleibt bis eigener nativer Prüfung auf StrafeScale=0. Globale Item-/Navmesh-Navigation ist kein behauptetes Ergebnis dieser Integration.

## Betrieb und Belegschutz

Builds, CPU-Fenster und Laufzeittests werden seriell ausgeführt. Overlayfs trennt Installationen und Wine-Präfixe; eigenes WM_CLOSE-/PID-/Arbeitsverzeichnis-gebundenes Cleanup und prefix-spezifischer wineserver-Abschluss schützen andere Sessions. Alle eigenen Mounts werden ausgewertet.

61DC-Rückfall-DLL und geschützte Release-Quellen bleiben erhalten. Kein Deaktivieren der Sync-Prüfung; der ursprüngliche Kickgrenzwert 10 wird nicht zur Scheinabnahme heraufgesetzt oder abgeschaltet. Private Rohlogs, Screenshots, Spielbinaries und Profil-GUIDs bleiben auf Hetzner.

Source-of-Truth: Integrationsplan und Berichte unter docs/reports. Drive-Dokumente werden als getrennt verifizierter Spiegel aktualisiert. Finale öffentliche Aktivierung und GitHub-Merge erst nach den tatsächlichen Abnahmekriterien.

Aktuelle Referenzmessung: unveränderte 61DC-DLL mit vier bewegten Bots, 20Hz und Scoreänderungen über 600s: Client 103,593% / Server 9,768% eines Kerns. Integriert Legacy 22,658%, Human 21,305%. Je ein Fenster, keine isolierte Human-CPU-Kausalität. Alle eigenen Mounts entfernt.

Öffentlicher Betrieb verwendet nach bestandenem Same-DLL-Stundengate einen separaten Overlay-Lauf; ursprüngliche Installation und DLL bleiben als Rückfall erhalten. Öffentliche Population darf zusätzliche Menschen enthalten, verlangt aber alle acht Botnamen. PID-, Startzeit- und CWD-geprüftes Stopwerkzeug schützt fremde Prozesse. Vorbereitungsprobe bestanden; Backup mit 415 bytegenau restaurierten Dateien geprüft.

Masterserver-Konfiguration enthält net_strMasterServer UND net_strMasterServerOverride explizit. Ein geerbter localhost-Override führte zum kontrollierten Abbruch des ersten öffentlichen Versuchs, ohne fremde Spieler und mit vollständigem Unmount. Keine Listungsabnahme aus einer lokalen Query.
