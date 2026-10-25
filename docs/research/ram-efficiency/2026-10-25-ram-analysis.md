# Wine-Client-Ressourcenanalyse: RAM/CPU pro unabhängigem Bot (Retail 1.07)

**Datum:** 2026-10-25 · **Umgebung:** isolierte LMArena-Sandbox, **keine**
Wine-/Retail-Laufzeit vorhanden · **Status:** Analyse + Offline-Werkzeuge.

> **Messprovenienz-Grundsatz dieses Dokuments:** In dieser Sandbox wurde kein
> einziger Wine-/Retail-Benchmark ausgeführt. Jede Zahl stammt aus bereits
> veröffentlichten Hetzner-Berichten dieses Repositories bzw. der PR-Branches
> #47/#51 und ist entsprechend zitiert. Neue Zahlen aus dieser Sitzung sind
> ausschließlich Offline-Testergebnisse der neuen Werkzeuge (Fixtures/Dummy-
> Prozesse) oder Modellrechnungen.

Evidenzklassen (werden an jeder Aussage geführt):

| Klasse | Bedeutung |
|---|---|
| **[T]** Technisch nachgewiesen | reale Hetzner-/Retail-Messung, Quelle zitiert |
| **[O]** Offline getestet | in dieser Sandbox reproduzierbar ausgeführt (Fixtures/Dummies, kein Wine) |
| **[A]** Architekturvorschlag | begründeter Entwurf, noch ohne Laufzeitnachweis |
| **[N]** Noch nicht überprüft | offene Annahme/Hypothese, Messauftrag definiert |

## 0. Ausgangsbefund aus PR #47 und den vorhandenen Messberichten

Auftragsgemäß zuerst PR #47 und die CPU-/RAM-Berichte ausgewertet:

**[T]** Architektur A (öffentliche Flotte: 1 Server + 2 Clients à 4 lokale
Bots, Build04-NullRender, 20 Hz):

| Messung | Wert | Quelle |
|---|---|---|
| RSS Server | 51 368 KiB ≈ 50,2 MiB | `docs/reports/2026-10-21-human-cpu-final.md` §11 |
| RSS je Viererclient | 188 436 / 188 820 KiB ≈ 184 MiB | ebd. |
| Summe Spielprozesse | ≈ 419 MiB RSS | `docs/reports/2026-10-21-hetzner-capacity.md` |
| Öffentliche cgroup (Snapshot) | 530,9 MiB aktuell / 532,2 MiB Peak | ebd. |
| Test-cgroup-CPU (600 s Smoke) | 69,031 % eines Kerns | ebd. |
| Redstation-Smoke 25.10. | Server 10,5 %, Clients 23,7/22,4 %, cgroup 64,5 % | PR #51 `docs/reports/2026-10-25-redstation-public-results.json` |

**[T]** Architektur B (PR #47: je Bot ein vollständiger Retail-Client,
privater Server, Loopback-Namespace, Overlay-Mounts, private cgroup):

| Lauf | Bots | cgroup-RAM-Peak | cgroup-CPU (1 Kern) | Ausgang | Quelle |
|---|---:|---:|---:|---|---|
| Boundary 90 s | 1 | 555,8 MiB | 51,5 % | PASS_LIMITED | PR #47 `2026-10-21-session-execution-results.json` |
| Vierbot 360 s | 4 | 1158,0 MiB | 72,5 % | PASS_LIMITED | ebd. |
| Vierbot lowmem 150 s | 4 | 1047,4 MiB | 71,9 % | PASS_LIMITED | ebd. |
| Achtbot Versuch 1 | 5 erreicht | 1322,8 MiB | – | **BLOCKED_CAPACITY** (verfügbar 970,5 < Gate 1068 MiB) | ebd. |
| Achtbot Versuch 2 (lowmem) | 6 erreicht | 1389,9 MiB | – | **BLOCKED_CAPACITY** (verfügbar 921,1 MiB) | ebd. |
| Redstation-Versuch (ohne Publikflotte) | 7 joined + 1 joining | 1725,9 MiB | – | Drain-Timeout 311 s (**nicht** als RAM-Ursache belegt) | PR #51 `2026-10-25-redstation-public.md` |

**[T→abgeleitet]** Host: 3819 MiB RAM, 2 vCPU, **kein Swap**
(`2026-10-21-hetzner-eight-bot-cpu-headless-baseline.md`).

**Abgeleitete Kernzahlen** (Arithmetik auf [T], Formeln in
`poc/research/ram-efficiency/measurements.json`):

- Marginal pro unabhängigem Client (B): **(1158,0 − 555,8)/3 ≈ 200,7 MiB**.
- Basisaufwand erster Client inkl. privatem Server/Infrastruktur: **≈ 355 MiB**.
- Lineare Prognose 8 Clients: **≈ 1961 MiB**; der unabhängige
  Redstation-Lauf (7 joined + 1 joining, Peak 1725,9 MiB) liegt ~12 %
  darunter → der Fit ist konservativ, nicht geschönt.
- Architektur A kostet pro Bot ≈ 46–47 MiB **geteiltes** RSS; Architektur B
  kostet pro unabhängigem Bot ≈ 200 MiB cgroup-RAM: **Faktor ≈ 4,3**.
- CPU: A ≈ 69 % eines Kerns für 8 Bots; B ≈ 72,5 % für nur 4 Bots →
  pro unabhängigem Bot grob **2× CPU** gegenüber A (kurze Fenster, [T] mit
  Unsicherheit).

**Wichtig zur Blockade-Interpretation:** Versuch 1/2 scheiterten am
**Reserve-Gate** (1068 MiB verfügbar vor jedem weiteren Client), nicht an
einem OOM; der Redstation-Lauf scheiterte am **Admin-Drain-Timeout**, was PR
#51 ausdrücklich *nicht* als RAM-Ursache wertet. „Acht unabhängige Clients
passen nie in 4 GB“ ist damit **nicht** bewiesen — bewiesen ist, dass sie
unter den geltenden (sinnvollen) Schutzreserven neben der Publikflotte nicht
qualifizierbar waren. [T]

## Untersuchungspunkte 1–12

### 1. Wine-Prozessarchitektur

**[T aus Code/Berichten]** Pro Architektur-B-Client betreibt der PR-#47-Runner
einen privaten Loopback-Netzwerk-Namespace, Overlay-Mounts (12 Unmounts bei 4
Bots → 3 Mounts/Client) und eine private cgroup; Logging/Drain/Cleanup sind
gegated. **[N]** Die genaue Prozessliste pro Prefix (wineserver, services.exe,
winedevice.exe, plugplay.exe, explorer.exe, rpcss) ist auf dem Host nie
inventarisiert worden; `memsample.py --match` liefert diese Inventur
(Messauftrag M1 im Messprotokoll). Standard-Wine startet pro Prefix einen
`wineserver` plus 3–5 Service-Prozesse; ob der Runner je Client ein eigenes
Prefix (und damit N× Service-Prozesse) oder ein geteiltes Lower-Layer mit
privatem Upper nutzt, muss aus der Runner-Konfiguration bzw. M1 belegt werden.

### 2. Ressourcenverbrauch des Retail-Clients

**[T]** Siehe Tabellen oben. Zusätzlich: der Originalclient mit echtem
Software-Rendering kostete 88,2 % eines Kerns und 208,1 MiB RSS
(`2026-10-21-hetzner-capacity.md`) — der NullRender-Botclient mit 4 Bots
kostet 23–24 % und 184 MiB. **[N]** Die Aufteilung der 184 MiB in
Anon/File/Shared wurde nie gemessen (kein PSS/smaps-Beleg); das ist der
wichtigste fehlende Einzelwert für jede Optimierungsentscheidung (M2).

### 3. NullRender und Headless-Betrieb

**[T]** Level-2-Bypass (Präsentationspfad übersprungen) ist aktiv und
qualifiziert: `render_draw_total=0`, 20 Hz, `nullrender_fps=20` (PR #51
Telemetrie). Er ist primär eine **CPU-**Optimierung. **[N]** Sein
RAM-Effekt ist ungemessen: GL-Kontext, llvmpipe-Puffer und Menü-/Fonttexturen
werden weiterhin alloziert (`docs/research/2026-10-22-nullrender-and-headless-paths.md`).
**[A/N]** Level 3 (`GAT_NONE`, kontext-/fensterfrei) würde zusätzlich
GL-/Surface-Speicher einsparen, bleibt aber mit allen dort dokumentierten
Blockern unbewiesen; Reihenfolge der Experimente unverändert gemäß der
Leiter in jenem Dokument.

### 4. Xvfb-Abhängigkeiten

**[T]** Architektur A nutzt **ein** Xvfb (`:102`, 640×480×24) für beide
Clients — Xvfb ist also bereits geteilt und taucht in der cgroup-Differenz
(69,0 % − Spielprozesse) mit auf. **[N]** Ob der B-Runner je Client ein
eigenes Xvfb startet, ist nicht dokumentiert; ein Xvfb 640×480×24 kostet
typischerweise nur ~10–30 MiB, d. h. selbst 8 private Xvfb wären ≤ 240 MiB —
relevant, aber nicht der Haupttreiber. Messauftrag M1 erfasst Xvfb getrennt.
**[A]** Ein gemeinsames Xvfb mit 8 Fenstern ist möglich und spart N−1
Serverinstanzen, koppelt aber die Fehlerdomänen (X-Absturz trifft alle) —
nur sinnvoll, wenn M1 relevante Xvfb-Kosten zeigt.

### 5. Gemeinsame Bibliotheken und Speicherseiten

**[T physikalisch, N quantitativ]** File-backed Seiten (Wine-`.so`,
llvmpipe/Mesa, ntdll/… und die Spiel-DLLs im **gemeinsamen** Overlay-Lower)
teilt der Kernel automatisch über den Page-Cache, solange alle Clients
dieselben Inodes mappen. RSS zählt diese Seiten pro Prozess mehrfach — die
419 MiB RSS der Publikflotte sind deshalb eine **Obergrenze**, PSS wurde nie
erhoben (M2). Overlayfs-Hinweis: Seiten werden nur geteilt, wenn die Datei
im Lower unverändert bleibt; ein Copy-up in den privaten Upper (z. B. durch
Schreiben an Spieldateien) dupliziert die Datei und beendet das Sharing.
**Empfehlung [A]:** identisches Lower-Verzeichnis und identischer Wine-Build
für alle Clients; keine Schreibpfade auf große GRO-Dateien.

### 6. Private vs. gemeinsam genutzte Speicherseiten

**[A, fundiert]** Der ~200-MiB-Marginalclient besteht überwiegend aus
**anonymen** Seiten: entpackte Texturen/Weltdaten im Spielheap,
llvmpipe-Puffer, Wine-Heaps. Anonyme Seiten teilt der Kernel **nicht**
automatisch — genau hier setzt KSM an: 8 Clients, die dieselbe Map laden,
halten weitgehend identische entpackte Datenblöcke. **[O]**
`ksm_probe.py` (read-only, Fixtures getestet) liefert Verfügbarkeit,
Kernel-≥6.4-prctl-Fähigkeit (`PR_SET_MEMORY_MERGE` wird an Kindprozesse
vererbt → ein Launcher-Wrapper genügt, **keine** Wine-/Spieländerung) und die
kernel-dokumentierte Ersparnis (`pages_sharing`). **[N]** Tatsächliche
Dedup-Quote, ksmd-CPU-Kosten und 20-Hz-/Sync-Neutralität sind offen (K1–K3
im Messprotokoll). Kein produktiver Einsatz ohne diese Gates.

### 7. Wine-Prefix-Kosten

**[N]** Pro-Prefix-Kosten (wineserver + Services, Registry-Hives) sind auf
diesem Host nie isoliert gemessen worden; typisch sind 30–60 MiB RSS pro
Prefix-Prozessgruppe. **[A]** Optionen in aufsteigender Kopplung:
(a) Status quo: privates Prefix je Client — maximale Isolation;
(b) geteiltes Lower-Prefix + privater Upper (vermutlich bereits so) — teilt
Dateiseiten, nicht die Serviceprozesse;
(c) **ein** gemeinsames Prefix/eine wineserver-Instanz für alle 8 Clients —
spart 7× Servicegruppen (~200–400 MiB potenziell), aber: gemeinsamer
Fehlerort, PR-#47-PID/cgroup-Bindung und Ghost-Quarantäne müssten neu
qualifiziert werden; ein wineserver-Stall würde alle 8 Bots gleichzeitig aus
dem 20-Hz-Takt werfen (Sync-Risiko). Empfehlung: erst M1/M2 messen; (c) nur
angehen, wenn die Servicegruppen tatsächlich signifikant sind.

### 8. Cgroup-Ressourcenverwaltung

**[T]** PR #47 nutzt bereits private cgroups, Peak-Erfassung und ein
Reserve-Gate (1068 MiB vor jedem weiteren Client); 0 neue Throttles in allen
PASS-Läufen. **[A]** Ergänzungen: `memory.high` als weiche Bremse unterhalb
des Gates; `memory.peak`-Reset je Phase; **zram-Swap** als gezielter
Kältespeicher für Wine-Init-Seiten — der Host hat 0 Swap, ein 512-MiB-zram
könnte die effektive Kapazität um geschätzt 200–400 MiB heben. **[N]**
zram-Latenzeffekt auf die 20-Hz-Action-Pipeline ist ungemessen und
sync-kritisch; nur mit Telemetrie-Gate (ACTIVE_OK, keine SYNCBAD-Regression)
testen. Keine Produktivänderung ohne separate Freigabe.

### 9. Speicherlecks und vermeidbare Allokationen

**[T begrenzt]** 360 s Vierbot und 3600 s Publikflotte zeigen keinen
auffälligen Anstieg; ein Langzeit-RAM-Driftprofil je Einzelclient existiert
nicht (längster B-Lauf 389 s). **[O]** `memsample.py` erfasst Zeitreihen
(RSS/PSS/USS je Prozessgruppe), aus denen Drift pro Stunde ablesbar ist
(M3). **[N]** Ob `RetailAllocator`-Pfade oder Telemetrie-/Logpuffer über
Stunden wachsen, ist offen.

### 10. CPU-Aufwand der GameMP-Bot-KI

**[T]** Human-KI ≈ Legacy-KI: 21,3 % vs. 22,7 % je Viererclient (je ein
600-s-Fenster, keine Kausalaussage; `2026-10-21-human-cpu-final.md` §6).
Nach NullRender dominiert nicht mehr das Rendering: Viererclient 23–24 %
eines Kerns ≈ **5–6 % je Bot** inkl. Engine-/Netz-/Wine-Anteil. Die KI
selbst ist portabel mit 555 Checks getestet und billig; der verbleibende
Klientenaufwand liegt überwiegend in Engine-Mainloop/Timer/Wine. **[N]**
Eine Per-Thread-Aufschlüsselung (llvmpipe vs. Mainthread) steht aus
(vorhandener `tse_cpu_profile.py`-Sampler + M4).

### 11. Alternative Prozesseinteilungen

**[A, modellgestützt]** Die Engine erlaubt max. 4 lokale Spieler je Client
(`gm_lpLocalPlayers[4]`, `Game.cpp`). Damit existieren zwischen A (2×4) und
B (8×1) die Zwischenstufen 4×2 und 8×1-gemischt. Das Ressourcenmodell
(`resource_model.py`, [O]) preist 4×2 auf ≈ 4 Clientprozesse ≈ 787 MiB RSS-
Basis — **[N]** ob ein 2-Spieler-Client messbar weniger RSS braucht als ein
4-Spieler-Client, ist ungemessen (M5: 1/2/4-Spieler-RSS-Treppe). CPU-seitig
skaliert B schlechter als die Slotdichte: 4 Clients à 2 Bots ≈ 100 % eines
Kerns (Fit), 2 Clients à 4 Bots ≈ 69 % [T].

### 12. Unabhängige Sessions innerhalb von Viererclients (Kernfrage)

Kann ein einzelner Bot joinen/leaven, ohne dass pro Bot ein ganzer
Wine-Prozess läuft?

- **[T Quellcode]** `CGame::AddPlayers()` registriert lokale Spieler einzeln
  über `_pNetwork->AddPlayer_t(...)` (Engine-Export, `Game.cpp:1722 ff.`),
  wird aber nur beim Session-Start aufgerufen; `SetupLocalPlayers()` fixiert
  das Roster vorher. Ein Entfernen-Pfad existiert in GameMP nicht sichtbar.
- **[N] E1:** Funktioniert `AddPlayer_t` auf einer **bestehenden** Verbindung
  mid-session (Server-seitig kommen Spieler ohnehin mid-game dazu, wenn ein
  Client joint — offen ist nur der Zusatzspieler auf bestehender Verbindung)?
- **[N] E2:** Existiert ein Engine-Pfad zum sauberen Entfernen einer
  einzelnen `CPlayerSource` ohne Disconnect des Clients?
- **[N] E3:** Bleiben CRC/Sequenz/Sync bei E1/E2 für Vanilla-Gegenstellen
  neutral (harte Abnahme, `Too many bad syncs`-Historie beachten)?

**Verifikationsweg [A]:** zuerst statisch per GhidraMCP auf der originalen
`Engine.dll` (Xrefs auf `AddPlayer_t`/`MSG_REQ_ADDPLAYER`-Äquivalent,
Player-Source-Destruktion), dann ein isolierter Laufzeitversuch mit
Wegwerf-Kopie — exakt die im Repo etablierte Toolchain (AGENTS.md).

**Fallback ohne E1/E2 — sofort baubar [A, O-prototypisiert]:**
*Roster-Restart-Multiplexing*: Sessions werden auf 4-Slot-Clients gepackt;
Mitgliedschaftsänderungen werden in Zeitfenstern gebündelt und durch Neustart
des betroffenen Clients mit neuem Roster umgesetzt. Kosten: Join-Latenz ≤
Batchfenster + Clientstart, und Co-Residenten eines neu gestarteten Clients
werden kurz unterbrochen (Reconnect derselben Identität — die vorhandene
`bot_reconnect`-Mechanik und die PR-#47-Identitäts-/GUID-Persistenz decken
genau das ab). Der deterministische Scheduler dazu ist implementiert und
getestet: `poc/research/ram-efficiency/slotplan.py` ([O], 11 Tests).

## Beantwortung der Hauptfrage

Nach Messlage bietet **kurzfristig die Hybridarchitektur C
(Slot-Multiplexing auf Viererclients)** das beste Verhältnis aus
Session-Unabhängigkeit, RAM, CPU und Sicherheit: Sie erbt die **gemessenen**
A-Kosten (8 Bots ≈ 419 MiB RSS / 69 % Kern [T]) statt der B-Kosten
(≈ 1961 MiB / ≈ 100 % projiziert), liefert echte Einzel-Join/-Leave-Semantik
nach außen und benötigt in der Roster-Restart-Variante **keine** neue
Engine-Fähigkeit. Architektur B bleibt die sauberste Isolation, ist aber auf
dem 4-GB-Host neben der Publikflotte nachweislich nicht qualifizierbar
[T, Reserve-Gate] und sollte erst nach den D-Optimierungen (KSM/zram/
Footprint, alle [N]) erneut antreten. Details, Zahlenmodell und
Integrationsplan: [`2026-10-25-architecture-comparison.md`](2026-10-25-architecture-comparison.md);
reproduzierbares Messverfahren: [`2026-10-25-measurement-protocol.md`](2026-10-25-measurement-protocol.md);
Werkzeuge/Prototypen: [`poc/research/ram-efficiency/`](../../../poc/research/ram-efficiency/README.md).
