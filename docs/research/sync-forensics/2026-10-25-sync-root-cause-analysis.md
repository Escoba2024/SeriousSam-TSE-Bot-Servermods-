# Multiplayer-Sync / CRC Root-Cause-Analyse – Serious Sam TSE Classic 1.07

**Datum:** 25.10.2026 · **Status:** Ursachenbaum mit belegten Befunden; **Root Cause selbst NICHT nachgewiesen** (Nachweisgrenze: keine aligned Sync-Dumps, kein erstes divergentes Tick)
**Scope:** Retail-1.07-Dedicated-Server + modifizierte BotClient-GameMP.dll (Alpha-Gaming)
**Schreibscope:** `poc/research/sync-forensics/**`, `docs/research/sync-forensics/**` (diese Datei)
**Vorgängerberichte:** [Retail-1.07-Sync-Check-Untersuchung](../reports/2026-10-17-retail107-sync-check-investigation.md), [PR #21 Sync-Dump-Pfad](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/21), [PR #54 CecilBotMod-Transferanalyse](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/54), [P0-Bot-Tick-Diagnose](../reports/2026-10-22-p0-bot-tick-diagnosis.md)

---

## 0. Executive Summary

Der historische Fehler **„Too many bad syncs“** ist ein **nachgewiesener Server-KICK-Mechanismus** (Retail-1.07-Engine.dll, Grenzwert 10, dekompiliert und in Ghidra verifiziert), dessen **ursächliche CRC-Divergenz zwischen Client- und Serversimulation nicht nachgewiesen** ist. Die vorhandenen Logbefunde belegen wiederholte fehlerhafte Sync-Prüfungen und Disconnects; die qualifizierten DLLs (61DC/7FC9) zeigen null SYNCBAD über 3600–3697 s, was die Fehlergeschichte **generationsabhängig** macht:

- **Generation A (qualifiziert, stabil):** 61DC27E0… (lokale 3697 s), 7FC94A39… (3600 s Acht-Bot-Stunde, 6430 SYNCOK, 0 SYNCBAD).
- **Generation B (historisch FAIL):** frühe BotClient-Kandidaten – zwei Läufe mit SYNCBAD 1→10 + Disconnect (Tick 83,40–92,40 und 23,50–37,15).
- **Generation C (ungeklärt FAIL):** Ground-Lookahead-DLL 53982F05… – Client-Log mit „Too many bad syncs“, keine Abnahme.

Die **stärkste priorisierte Hypothese** ist eine **Client-Physik-/Simulations-Modifikation (Ground-Lookahead)**, die den clientseitigen Entity-Zustand von der serverseitigen vanilla Simulation abweichen lässt – deckt mit der CRC-Prüfung (Entity-Zustände inkl. Position/Rotation) jedoch genau den divergenten Bereich. Eine zweite Hypothese ist ein **GameMP.dll-bedingter Simulationsunterschied** auf der Client-Seite (GameMP.dll ist **nicht** in der CRC-Liste, beeinflusst aber Action-Zusammensetzung und Entity-Simulation).

**Ohne echte aligned Sync-Dumps (cli_bDumpSync) und den ersten divergenten Tick ist eine Root-Cause-Bestätigung unmöglich.** Diese Grenze wird ausdrücklich dokumentiert; es wird keine Ursache erfunden.

---

## 1. Nachgewiesene Befunde (Belelegt, nicht hypothetisch)

| # | Befund | Quelle / Beleg |
|---|--------|----------------|
| B1 | String „Too many bad syncs“ an `0x602AADA0`, Xref `0x601A3550` in `FUN_601A2D10` (4.976 Bytes) in unveränderter Retail-1.07-`Engine.dll` (SHA256 `B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F`) | [Retail-1.07-Sync-Check-Untersuchung §2](../reports/2026-10-17-retail107-sync-check-investigation.md) |
| B2 | Message-Case `0x13`; `CNetworkMessage::Read(…, 0x10)` liest Sync-Block; `SYNCBAD` (Xref `0x601A3511`), `SYNCOK` (Xref `0x601A35BD`), `SYNCLATE`, `SYNCEARLY` im selben Handler | ebenda |
| B3 | Grenzwert **10**: Ghidra-Memory `0x602A7EB4` = `0a 00 00 00`; Xrefs aus Handler `0x601A353A` (READ) und `CNetworkLibrary::Init` `0x60196DF0`; Handler inkrementiert bei Abweichung, setzt bei bestehendem Vergleich auf 0, kickt bei ≥ Grenzwert | ebenda |
| B4 | `ser_iKickOnSyncBad`, `ser_bReportSyncBad/OK/Late/Early` als Konfigurationssymbole in Retail-1.07 | ebenda |
| B5 | Historische Serverlogs (10.10.2026, private Rohlogs, nicht public): `eight-hour`: 10 SYNCBAD, Tick 83,40→92,40, Counter 1→10, **1 Disconnect** (Logzeile 212); `eight-combat-only`: 10 SYNCBAD, Tick 23,50→37,15, **1 Disconnect** (Logzeile 177); jeweils **0 SYNCOK** | PR #21, Retail-Sync-Bericht §„Echte Logbelege“; `tools/analyze_sync_log.py` (in main) |
| B6 | Hetzner-Control 16.10.: `bot-previous.log`: `Disconnected: Too many bad syncs` um Bot-Tick 15400; `previous-SeriousSam.log` („vanilla isolated“): gleiche Disconnect-Meldung | Retail-Sync-Bericht |
| B7 | Qualifiziert: 61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9 → 3697,29 s lokale Acht-Bot-Abnahme, 6 CRC-Akzeptanzen | Retail-Sync-Bericht, Nachtrag |
| B8 | Qualifiziert: 7FC94A39… (Build04, PR #45) → 3600 s Acht-Bot-Stunde: 0 SYNCBAD/Disconnects/Throttling, 6430 SYNCOK, 3 CRC-OK; öffentliche 600-s-Smoke: ebenfalls 0 Sync-Fehler | [Human-CPU-Final-Bericht](../reports/2026-10-21-human-cpu-final.md) §9–11 |
| B9 | Ground-Lookahead-DLL `53982F05A1EEE73E52AF48C77301C67399D9EA38F5F5D23B8C549ADE2D0372C6`: aktivierter 600-s-Retry → „Too many bad syncs“ im privaten Client-Log, **keine Abnahme**, Quellen privat außerhalb des qualifizierten Releases | [Shadow-Dev-Status](../reports/2026-10-12-shadow-development-status.md), Retail-Sync-Bericht |
| B10 | `cli_bDumpSync` existiert in Retail-1.07 (Registerdatenadresse `0x602CD6EC`); `CSessionState::SessionStateLoop` schreibt `temp\syncdump.txt` mit `CRC: 0x%08X`; `cli_bDumpSyncEachTick` als Symbol belegt, Funktion nicht bestätigt; **kein nativer Dump je ausgeführt** | [PR #21 Bericht](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/blob/codex/chatgpt-syncdump-compare-20261017/docs/reports/2026-10-17-retail107-native-syncdump.md) |
| B11 | `CPlayerAction::ChecksumForSync` (`0x6019EC10`): **genau 4 aufeinanderfolgende Bytes** pro Aufruf (x86-Disassembly: `MOV CL,[EAX+ESI*1]`, `INC EAX`, `CMP EAX,0x4`, `JC`); `CSessionState::ChecksumForSync` ruft pro Spieler zweimal auf + Session-/Spieler-/Entity-Zustände | PR #21 |
| B12 | CRC-Pfad prüft `Classes\Player.ecl` + `EntitiesMP.dll` + geladene Spieldaten; **GameMP.dll nicht in CRC-Liste** | [CRC-Addendum](../research/2026-09-30-readiness-gamemp-crc-addendum.md) |
| B13 | Game-Tick 20 Hz; `pa_llCreated` wird von `CPlayerSource::SetAction` selbst gesetzt; `NET_MAXLOCALPLAYERS=4`; Server verarbeitet pro Client ≤4 Action-Slots | CRC-Addendum |
| B14 | BotDriver-Pfad: `CGame::GameHandleTimer` → `BotDriver_HandleTimer` (20 Hz) → `ctl_ComposeActionPacket` → `CPlayerSource::SetAction` → Netzwerk; Vanilla-Eingabeweg wird übersprungen | `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`, `poc/release/gamemp/Game.cpp:752-754` |
| B15 | botcore-KI ist deterministisch (Lcg mit Profil-Seed, nie geteilt); `make test` offline: 555 Human-AI-Checks, 0 Fehler | PR #54, `poc/botcore` |
| B16 | Vanilla-Client + Vanilla-Server (Hetzner, 155,93 s, 31/31 Queries): keine Sync-Fehler-Meldung; Client-Log zeigt Join ohne „Too many bad syncs“ | [Hetzner-Vanilla-Control](../reports/2026-10-17-hetzner-lowrender-vanilla-control.md) |
| B17 | Server prüft Major/Minor der Netzwerk-Build-Version beim Connect; 1.07 ≠ 1.10 Netzwerk-Build | CRC-Addendum |
| B18 | `Test-RetailJoin.ps1` sichert GameMP.dll vorab, **restauriert sie aber nicht automatisch** – nicht reversibel, nicht für isolierte Tests geeignet | Retail-Sync-Bericht §Sicherheitsprüfung |

---

## 2. Technischer Ursachenbaum (belegte Knoten, priorisierte Hypothesen)

```
„Too many bad syncs“                       [B1–B4: Kick-Mechanismus NACHWEISBAR]
│
├─ Server-Handler (Retail 1.07, FUN_601A2D10)
│   ├─ Compare (sc_iLevel / sc_ulCRC für denselben Tick)  [1.10-Referenz; Retail-Layout bis ABI-Validierung abgeleitet]
│   ├─ Bei Abweichung: Counter++ → SYNCBAD
│   ├─ Bei Übereinstimmung: Counter = 0 → SYNCOK
│   └─ Counter ≥ 10 → KICK „Too many bad syncs“            [B3: Grenzwert 10 in Ghidra gelesen]
│
├─ CRC-Divergenz (sc_ulCRC) – ROOT CAUSE: NICHT NACHGEWIESEN
│   │
│   ├─ H4 ★★★ Client-Physik-/Simulations-Modifikation (Ground-Lookahead)
│   │    ├─ Beleg: Ground-Lookahead-DLL → Client-Log „Too many bad syncs“ [B9]
│   │    ├─ Mechanismus: Client simuliert Entity-Bewegung/Boden-Erkennung anders
│   │    │   als Server (Server: vanilla EntitiesMP) → Client-Entity-Zustand ≠
│   │    │   Server-Entity-Zustand → CRC (Entity-Zustände) divergiert
│   │    ├─ Stütze: Vanilla-Clients zeigen keine Sync-Fehler [B16]; qualifizierte
│   │    │   DLLs ohne Ground-Feature stabil [B7, B8]
│   │    └─ Prüfung: aligned Dumps + Physics-Differenz am ersten divergenten Tick
│   │
│   ├─ H1 ★★ GameMP.dll-bedingte Client-Simulations-Differenz
│   │    ├─ GameMP.dll NICHT in CRC-Liste [B12] → CRC allein kein direktes GameMP-Gate
│   │    ├─ Aber: GameMP.dll steuert Action-Zusammensetzung (ctl_ComposeActionPacket)
│   │    │   und Entity-Verarbeitung auf der Client-Seite
│   │    ├─ BotDriver ist deterministisch [B15] → algorithmische Divergenz
│   │    │   aus der KI-Logic selbst unwahrscheinlich
│   │    └─ Prüfung: Action-Packet-Logging + Replay der Client-Simulation offline
│   │
│   ├─ H3 ★ Timing / Action-Packet-Zuordnung (pa_llCreated)
│   │    ├─ 20 Hz-Tick [B13]; Action-Paket mit pa_llCreated-Timestamp
│   │    ├─ Verzögerte/veraltete Actions können vom Server versetzt angewandt
│   │    │   werden → Entity-Zustand-Differenz
│   │    ├─ Netzwerk-Latenz allein NICHT als Ursache bewiesen [B5-Historie]
│   │    └─ Prüfung: Packet-Capture + Tick-Korrelation von Action-Empfang und Anwendung
│   │
│   ├─ H6 ☆ Action-Zusammensetzungs-Differenz (ctl_ComposeActionPacket)
│   │    ├─ Vanilla-Clamps/Physik-Konventionen [CRC-Addendum]
│   │    ├─ pa_aRotation als absolute Delta vs. Akkumulation – Konvention
│   │    │   muss exakt vanilla bleiben
│   │    └─ Prüfung: rohe Action-Bytes Client vs. Server-Replay vergleichen
│   │
│   ├─ H5 ☆ Engine-Build-Unterschiede (Client vs. Server)
│   │    ├─ Engine.dll SHA256 Server = Observer (B79BF8BB…) [B1]
│   │    ├─ BotClient-Engine.dll-Build nicht dokumentarisch gesichert
│   │    └─ Prüfung: SHA256 aller vier Vanilla-Dateien pro Prozess + Major/Minor-Check [B17]
│   │
│   └─ H2 ☆ Log-Fehlerinterpretation (Counter-Artefakt)
│        ├─ Counter-Sprünge >1 pro Ereignis = fehlende SYNCOK-Meldungen / Fragmentierung
│        ├─ Tool „sync_error_classifier.py“ unterscheidet E1–E6 (siehe §4)
│        └─ Keine Erfindung: E1 = sustained divergence, E2 = transient
│
├─ Ausschlüsse / negative Befunde (BELEGT)
│   ├─ Vanilla-Client + Vanilla-Server: keine Sync-Fehler in 155,93 s [B16]
│   ├─ 61DC: 3697,29 s Acht-Bot-Lauf, 0 SYNCBAD [B7]
│   ├─ 7FC9: 3600 s Acht-Bot-Stunde, 0 SYNCBAD, 6430 SYNCOK [B8]
│   ├─ GameMP.dll nicht in CRC-Liste [B12]
│   └─ Netzwerk-Latenz allein nicht bewiesen [B5-Historie]
│
└─ NACHWEISGRENZE (explizit, nicht übersprungen)
    ├─ Keine aligned Sync-Dumps (cli_bDumpSync nie nativ ausgeführt) [B10]
    ├─ Erster divergenter Tick nicht ermittelt
    ├─ Keine Client-State-Dumps (Server-/Client-Entity-Zustände pro Tick)
    ├─ Ground-Lookahead-Quellcode privat, nicht im qualifizierten Release [B9]
    └─ ohne diese Daten: Root Cause bleibt HYPOTHESE
```

---

## 3. Priorisierte Hypothesen

| Prio | Hypothese | Mechanismus | Sog. Beweis | Risiko |
|------|-----------|-------------|-------------|--------|
| **P1** | **H4: Client-Physik-/Simulations-Modifikation (Ground-Lookahead)** | Client simuliert Entity-Bewegung/Boden-Erkennung anders → Entity-Zustands-Differenz → CRC-Abweichung | Ground-Lookahead-DLL mit Sync-Fehlern [B9]; Vanilla stabil [B16]; qualifizierte DLLs ohne Ground-Feature stabil [B7, B8] | Hoch – deckt genau den CRC-geprüften Bereich |
| **P2** | **H1: GameMP.dll-Simulations-Differenz** | Modifizierte GameMP.dll verändert Client-seitige Entity-Simulation oder Action-Zusammensetzung | GameMP.dll nicht in CRC-Liste [B12] (direktes Gate fehlt), aber Action-Pfad geht über GameMP [B14] | Mittel – BotDriver-Logic deterministisch [B15] |
| **P3** | **H3: Timing / Action-Packet-Zuordnung** | Versetzte Anwendung veraltete Actions → Zustands-Differenz | 20 Hz + pa_llCreated [B13]; historische Counter-Monotonie [B5] | Mittel – Latenz allein nicht bewiesen |
| **P4** | **H6: Action-Zusammensetzung (ctl_ComposeActionPacket)** | Delta-Rotation-Konvention oder Clamp-Unterschiede | Vanilla-Clamp-Semantik dokumentiert [CRC-Addendum] | Niedrig–Mittel |
| **P5** | **H5: Engine-Build-Unterschiede** | Unterschiedliche Engine-Builds Client/Server | Server-/Observer-Engine.dll identisch [B1]; BotClient-Build nicht gesichert | Niedrig |
| **P6** | **H2: Log-Fehlerinterpretation** | Counter-Artefakt, kein echter Zustandsunterschied | Klassifikator E1–E6 (neues Tool) | Niedrig – wird durch Werkzeuge ausgeschlossen |

**Bewertung:** P1 (Ground-Lookahead) ist die einzige Hypothese, die **alle drei Generationen erklärt** (stabil ohne Ground-Feature, fail mit Ground-Feature, historische FAIL-Läufe als frühere Kandidaten mit unvollständiger Physics-Kompatibilität). Sie ist jedoch **nicht bewiesen**, weil die Ground-Lookahead-Quellen privat sind und kein aligned Dump existiert.

---

## 4. Vergleich der vorhandenen Sync-Reports

| Quelle | Inhalt | Status |Verwendung hier |
|---|---|---|---|
| `docs/reports/2026-10-17-retail107-sync-check-investigation.md` | Retail-Handler-Kette, Grenzwert 10, historische Logs, Sicherheitsprüfung, Kontrollmatrix | **VERIFIZIERT** (Ghidra-Dekompilation + Logs) | Grundlage für B1–B9, B16–B18 |
| PR #21 (`codex/chatgpt-syncdump-compare-20261017`) | `cli_bDumpSync`, 4-Byte-Action-CRC, `compare_sync_dumps.py`, EVIDENCE_GAP | **VERIFIZIERT** (statisch) | Grundlage für B10–B11; Werkzeugvergleich |
| PR #16 (`chatgpt-sync-log-regressions-20261017`) | `analyze_sync_log.py` (in main), Parser-Härtung | **VERIFIZIERT** (offline) | Grundlage für Tool-Vergleich |
| PR #54 (`arena/8317e1d6…`) | CecilBotMod-Transferanalyse, Ground-Lookahead-Sync-Risikoklasse, Test-/Abnahmekriterien G1–G6 | **VERIFIZIERT** (Quellcode, offline) | Grundlage für H4-Priorisierung |
| `docs/reports/2026-10-22-p0-bot-tick-diagnosis.md` | BotDriver-Stillstand (H1–H5), Telemetrie-Kandidat | **VERIFIZIERT** (Quellcode) |Ausschluss BotDriver-Logik als direkter Sync-Ursache |
| `docs/reports/2026-10-21-human-cpu-final.md` | 7FC9-Abnahme, 0 SYNCBAD, 600-s-Smoke | **VERIFIZIERT** (Retail-Runtime) | Generation-A-Stabilitätsbeleg |
| `docs/reports/2026-10-12-shadow-development-status.md` | Ground-Lookahead-Failure, DLL-SHA | **VERIFIZIERT** (Log-Befund) | Grundlage für B9 |
| `tools/analyze_sync_log.py` (main) | SYNCBAD/SYNCOK/Disconnect-Parser | **VERIFIZIERT** (offline) | Grundlage für Tool-Erweiterung |
| `docs/research/2026-09-30-readiness-gamemp-crc-addendum.md` | CRC-Pfad, GameMP nicht in CRC-Liste, Action-Semantik | **VERIFIZIERT** (Design-Doc + Quellcode) | Grundlage für B12–B13 |

**Konsens aller Berichte:** Der Kick-Mechanismus ist belegt; die **eigentliche CRC-Ursache ist offen** („EVIDENCE_GAP“ in PR #21, „offen“ in Retail-Sync-Bericht). Die neuen Werkzeuge (§5) operationalisieren diese Grenze fail-closed.

---

## 5. Neue Diagnosewerkzeuge (dieses PR)

Alle Werkzeuge liegen unter `poc/research/sync-forensics/tools/`, sind read-only und starten keine Prozesse.

| Werkzeug | Aufgabe | Tests |
|----------|---------|-------|
| `sync_correlator.py` | Server-SYNCBAD/KICK mit Client-Disconnect und BotTelemetry korrelieren; Kick-ohne-Disconnect erkennen | ✓ |
| `sync_tick_compare.py` | Tick-Serien, Counter-Jump-Erkennung (>+1 pro Ereignis), Monotonie | ✓ |
| `sync_crc_diff.py` | aligned Sync-Dump-Vergleich; UNALIGNED/INCOMPLETE fail-closed; Feld-Kategorisierung | ✓ |
| `sync_event_mapper.py` | Client/Server-Ereignischronologie; orphan-Events; Rejoin-Ketten | ✓ |
| `sync_error_classifier.py` | E1–E6-Fehlerklassifizierung basierend auf dem replizierbaren Handler-Verhalten | ✓ |
| `sync_incomplete_detector.py` | Unvollständigkeitserkennung in Logs/Dumps/Telemetrie (fail-closed) | ✓ |
| `make_synthetic_logs.py` | Deterministische synthetische Fixtures (keine echten Daten) | ✓ |

**Testergebnisse:** `python3 -m unittest discover -s poc/research/sync-forensics/tests -v` → **29/29 PASS** (Python 3.11, Linux-Sandbox).

**Fail-closed-Garantien:**
- `sync_crc_diff.py`: unterschiedliche Alignment-Keys → `UNALIGNED` (Exit 2), niemals veraenderter Vergleich; fehlende Gegenstucke → `INCOMPLETE`.
- `sync_tick_compare.py`: never behauptet einen divergenten Tick; nur `first_bad_tick`.
- `sync_error_classifier.py`: E1–E6 sind Log-Diagnosen, **keine Root-Cause-Bestätigungen**.

---

## 6. Konkreter Plan für den isolierten nativen Test

**Ziel:** Den ersten divergenten Tick und das betroffene Sync-Feld bei einer wiederholbaren CRC-Divergenz isolieren – mit minimalem Aufwand für den RDC-Hauptentwickler.

### 6.1 Vorbereitung (isolierte Installation)

1. **Eigene Kopie** des gesamten Spiels + Servers (eigene Ports, eigenes Prefix), niemals die qualifizierte Installation auf Shadow/Hetzner verändern.
2. **Backup/Restore-Verfahren**: `run-shadow-fleet.ps1` + unabhängiger Auditor oder separate Testinstallation (siehe `poc/LOCAL-RELEASE.md`). **Niemals** `Test-RetailJoin.ps1` ohne eigenständige Restore-Hülle verwenden [B18].
3. **SHA256-Inventur** aller vier Vanilla-Dateien pro Prozess (`SeriousSam.exe`, `GameMP.dll`, `Engine.dll`, `EntitiesMP.dll`) + Build-Version (Major/Minor) [B17].

### 6.2 Kontrollmatrix (identische Version, Map, Netzwerkparameter, Laufzeit)

| Stufe | BotClient-DLL | Erwartung |
|-------|---------------|-----------|
| S0 Vanilla-Baseline | Original-GameMP.dll | 0 SYNCBAD |
| S1 qualifiziert | 7FC94A39… (Build04) | 0 SYNCBAD (Reproduzierbarkeit) |
| S2 isoliert 1 Bot | 7FC94A39… | 0 SYNCBAD |
| S3 Combat/Navigation-Varianten | 7FC94A39… | 0 SYNCBAD |
| S4 mehrere Bots (4/8) | 7FC94A39… | 0 SYNCBAD |
| S5 **Ground-Lookahead-Kandidat** (privat) | 53982F05… | **erwarteter FAIL** – SYNCBAD-Starttick erfassen |

Jede Stufe mit **nicht instrumentierter Kontrollprobe**.

### 6.3 Erfassung pro Lauf

- `SYNCBAD`-Starttick, Sequence, fortlaufender Counter, `SYNCOK`-Reset-Ticks.
- Map-/Join-/Leave-Ereignisse, Action-Ticks (BotDriver-Log).
- **`cli_bDumpSync=1` auf Server und Client** → aligned `temp\syncdump.txt`-Paare pro Tick.
- Binary-Hashes, Prozessumgebung, Port, Uhrzeit.
- `ser_bReportSyncBad` aktiv (Loggröße kontrollieren); **`ser_iKickOnSyncBad` NICHT herunterregeln**.

### 6.4 Analyse-Pipeline (neue Werkzeuge)

```bash
python3 poc/research/sync-forensics/tools/sync_error_classifier.py server.log
python3 poc/research/sync-forensics/tools/sync_correlator.py --server-log server.log --client-log client.log --telemetry BotTelemetry.csv
python3 poc/research/sync-forensics/tools/sync_tick_compare.py --server-log server.log --client-log client.log --telemetry BotTelemetry.csv
python3 poc/research/sync-forensics/tools/sync_crc_diff.py --server-dir server-dumps --client-dir client-dumps
python3 poc/research/sync-forensics/tools/sync_incomplete_detector.py --server-log server.log --client-log client.log --telemetry BotTelemetry.csv --dump server-dumps/s1.txt --dump client-dumps/c1.txt
```

### 6.5 Entscheidungsregeln

- **aligned Dump-Paar mit CRC-Differenz** → `sync_crc_diff.py` liefert Feldkategorien (session/player_action/player_entity); isoliere das erste divergente Feld.
- **Feldkategorie `player_entity`** → H4/H1 (Physik/Simulation) – nächstes Schritt: Physics-Differenz am Tick vergleichen.
- **Feldkategorie `player_action`** → H6/H3 (Action-Zusammensetzung/Timing) – nächstes Schritt: Action-Bytes-Logging.
- **Feldkategorie `session`** → H5/Join-CRC – nächstes Schritt: Engine-Build-Vergleich.
- **Kein aligned Paar** → INCOMPLETE, kein Schluslimiter; Dump-Erfassung wiederholen.

### 6.6 Sicherheitsregeln

- Keine Änderung produktiven Servers; keine `ser_iKickOnSyncBad`-Änderung; keine Frida-Hooks vor Baseline-Test.
- Frida nur nach Baseline: RVA `0x601A2D10 - 0x600C0000 = 0x000E2D10`; nach Runtime-ASLR Modul-Base neu bestimmen; minimale passive Hooks an der geladenen Engine.
- Rohlogs/Dumps/DLLs privat, niemals in Git.

---

## 7. Zusätzliche Diagnosemöglichkeiten (empfohlen)

1. **`cli_bDumpSyncEachTick`** – prüfe, ob der Dump tatsächlich pro Tick erfolgt (Symbol belegt, Funktion nicht bestätigt [B10]).
2. **`ser_iExtensiveSyncCheck`** – erweiterter Sync-Check-Modus (Symbol belegt, Werte nicht bestätigt).
3. **Action-Packet-Logging**: Hook `WriteActionPacket` (GameMP.dll) mit `pa_llCreated`-Timestamp → Korrelation mit Server-Anwendungs-Tick.
4. **CRC-Berechnungs-Hook**: `ChecksumForSync` auf Client und Server passive Frida-Hooks → direkter CRC-Vergleich pro Tick.
5. **Netzwerk-Capture**: tcpdump/Wireshark UDP-Action-Pakete → Packet-Verzögerung/Reihenfolge messen.
6. **Deterministische Replay-Simulation**: Server-Simulation offline nachspielen (vanilla Engine) vs. Client-Dump → exakter Feldvergleich.

---

## 8. Nachweisgrenze (explizit)

**Die Root Cause des historischen „Too many bad syncs“ ist ohne echte Laufzeitdaten NICHT nachweisbar.** Fehlende Daten:

1. **aligned Server/Client-Sync-Dumps** (pro Tick) – erfordert `cli_bDumpSync=1` in isolierten Läufen.
2. **Erster divergenter Tick** und betroffenes Sync-Feld.
3. **Client-State-Dumps** (Entity-Zustände, Action-Bytes).
4. **Ground-Lookahead-Quellcode/Vergleichs-DLL** (privat).
5. **Engine-Build-Inventur** des BotClients.

**Sicher erfassbar** durch den in §6 beschriebenen isolierten Test mit Backup/Restore und SHA256-Inventur – ohne Produktionsveränderungen.

---

## 9. Quellen und Verweise

- [Retail-1.07-Sync-Check-Untersuchung](../reports/2026-10-17-retail107-sync-check-investigation.md)
- [PR #21 – Sync-Dump-Pfad](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/21)
- [PR #45 – Human-KI/NullRender-Abnahme](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/45)
- [PR #54 – CecilBotMod-Transferanalyse](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/54)
- [P0-Bot-Tick-Diagnose](../reports/2026-10-22-p0-bot-tick-diagnosis.md)
- [Human-CPU-Final-Bericht](../reports/2026-10-21-human-cpu-final.md)
- [Shadow-Dev-Status (Ground-Lookahead)](../reports/2026-10-12-shadow-development-status.md)
- [CRC-Addendum](../research/2026-09-30-readiness-gamemp-crc-addendum.md)
- [Hetzner-Vanilla-Control](../reports/2026-10-17-hetzner-lowrender-vanilla-control.md)
- [tools/analyze_sync_log.py (main)](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/blob/main/tools/analyze_sync_log.py)
