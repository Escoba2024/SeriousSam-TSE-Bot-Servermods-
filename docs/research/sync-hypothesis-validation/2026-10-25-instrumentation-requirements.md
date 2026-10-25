# Instrumentierungsanforderungen für native Sync-Diagnose (TSE 1.07)

**Datum:** 25.10.2026 · **Adressat:** Codex C2 (native Sync-Diagnosewerkzeuge),
ausführender RDC-Entwickler · **Status:** Anforderungskatalog, offline geprüft,
**nativ ungetestet**.

Zweck: Diese Anforderungen beschreiben die **minimalen** Daten, die ein nativer
Lauf liefern muss, damit die Offline-Werkzeuge
(`poc/research/sync-hypothesis-validation/tools/`) eine Ursachenklasse
**diskriminieren** können — statt sie nur zu vermuten. Jede Anforderung nennt
das Feldformat, den Grund und die Hypothesen, die ohne sie `NOT_TESTED` bleiben.

Sie ersetzen keine Sicherheitsregeln aus [AGENTS.md](../../../AGENTS.md) und
keine der bestehenden Berichte; sie ergänzen sie.

---

## 0. Übersicht

| ID | Anforderung | Ohne sie nicht prüfbar | Aufwand |
|---|---|---|---|
| **R1** | Hash-Inventar pro Prozess | H5, jede Kandidatenzuordnung | gering (Skript) |
| **R2** | Konfigurations-Snapshot zur Laufzeit | A5, A4, Gültigkeit jedes Laufs | gering |
| **R3** | Alignierte Sync-Dumps (beide Seiten) | erster divergenter Tick, H4 | mittel (Shell-Symbole) |
| **R4** | Gemeinsame Tick-Herkunft (Tick **und** monotone Uhr) | jede Zeitkorrelation, `INCONSISTENT_TOO_LATE` | mittel |
| **R5** | Action-Byte-Bilder (Client und Server) | H2, A1 | mittel (Hook im eigenen Build) |
| **R6** | Telemetrie rev=2 mit `game_tick` + `t_mono_ms` | H1, H7 über Fenstergrenzen | gering (eigener Code) |
| **R7** | Sync-Ereignis-Erfassung inkl. Level/Join/Map | H6, E-Klassen | gering |
| **R8** | Evidenz-Bundle + Manifest | Nachweisbarkeit, Audit | gering |

Priorität: **R1, R2, R7** sofort (kein Code), **R3** ist der Kern (ohne Dumps
keine Ursache), **R4/R5** machen die Diskriminierung erst eindeutig.

---

## R1 — Hash-Inventar pro Prozess

Zu erfassen, **bevor** der Lauf startet, und im Manifest zu fixieren:

| Komponente | Feld | Quelle |
|---|---|---|
| Server | `SeriousSam.exe`, `Engine.dll`, `EntitiesMP.dll` | SHA256 der Dateien |
| Server | `GameMP.dll` (Dedicated) | SHA256 |
| Jeder Client | dieselben drei + `GameMP.dll` (Kandidat) | SHA256 |
| Beide | Netzwerk-Build-Version (Major/Minor) | Clientlog/Serverlog |

Regeln:

* Alle vier Vanilla-Komponenten müssen zwischen Server und jedem Client
  **byteidentisch** sein; jede Abweichung ist ein Befund (H5), kein Detail.
* Der GameMP-Hash wird als **Kandidaten-ID** geführt (z. B. `61DC27E0…`,
  `7FC94A39…`, `53982F05…`, `7dc961c8…`) und in jedem Ergebnis mitzitiert.
* Ein Lauf ohne vollständiges Inventar ist für H4/H5 nicht verwertbar.

Werkzeug: `tools/evidence_bundle_audit.py` prüft Vollständigkeit und Gleichheit
und erzeugt daraus die Beobachtung `build.hash_inventory_match`.

---

## R2 — Konfigurations-Snapshot zur Laufzeit

Nicht „was in der Ini steht“, sondern **was der Prozess tatsächlich benutzt**
(Shell-Werte nach Start, einmalig protokolliert):

```json
"config": {
  "cli_bDumpSync": 1,
  "cli_bDumpSyncEachTick": 0,
  "ser_bReportSyncBad": 1,
  "ser_iKickOnSyncBad": 10,
  "ser_iExtensiveSyncCheck": 0,
  "bot_bEnabled": 1,
  "bot_bAutoCombat": 1,
  "bot_iLogEvery": 20,
  "bot_iTelemetry": 1,
  "bot_iNullRender": 1,
  "frida_or_debugger_attached": false
}
```

Verbindlich:

* `ser_iKickOnSyncBad` **muss** 10 bleiben. Ein abgesenkter Wert macht „kein
  SYNCBAD“ bedeutungslos (AGENTS.md) und wird vom Audit als `INVALID` verworfen.
* `cli_bDumpSync` muss aktiv sein, `cli_bDumpSyncEachTick` nur bewusst und
  dokumentiert (Dump-Flut verändert Timing).
* Debugger/Frida im Messlauf sind erlaubt, aber zu deklarieren (Warnung im
  Audit, weil Timing/Perf beeinflusst werden).

---

## R3 — Alignierte Sync-Dumps

Ziel: Für denselben Tick liegen **Client- und Server-Dump** vor. Nur so kann
der *erste* divergente Tick bestimmt werden.

Format (Text, tolerant geparst; Header ist Pflicht):

```
CRC: 0x1A2B3C4D
Level: KarnakDemo
Sequence: 420
Tick: 121.00
Pause = 0
SessionTime = 121.00
PlayerActions = 0x00000000
PlayerEntitys = placement=1.0,2.0,3.0;health=100;...
```

Anforderungen:

* Ablage: `dumps/server/<name>.txt`, `dumps/client/<name>.txt`, Dateiname mit
  Tick, damit ein fehlender Dump sichtbar ist.
* Mindestens **ein** aligniertes Paar pro Fehlerfenster; besser: das Fenster um
  `first_bad_tick − 2 s … first_bad_tick + 2 s`.
* Kein Feld-Umschreiben, keine Nachbearbeitung durch Skripte vor der Ablage.

Werkzeuggrenze: Feld-Diff bleibt bei PR #58 (`sync_crc_diff.py`). Das Audit
zählt nur alignierte Paare, klassifiziert `entity`/`action`-Felddifferenzen grob
und kann `sync_crc_diff`-JSON per `--crc-diff` übernehmen.

---

## R4 — Gemeinsame Tick-Herkunft (**heute nicht erfüllt**)

Problem: Serverlog-Ticks, Dump-Ticks und `bs_iTick` des BotDrivers haben
**verschiedene Ursprünge**. `bs_iTick` zählt Timer-Aufrufe und wird bei
Spielerquellen-Wechsel auf 0 gesetzt (Befund F5). Eine Aussage wie „SYNCBAD ab
Bot-Tick 15400“ ist deshalb **keine** Simulationstick-Angabe.

Anforderung: Jedes Artefakt trägt **zwei** Stempel:

1. den Game-Tick-Zähler der Engine (derselbe, den der Sync-Check benutzt),
2. eine monotone Uhr in Millisekunden seit Prozessstart (`QueryPerformanceCounter`
   bzw. `clock_gettime(CLOCK_MONOTONIC)`).

Damit gilt für einen Tick T: `dump(server,T)` ↔ `dump(client,T)` ↔
`serverlog(T)` ↔ `telemetry(t_mono_ms)`. Ohne (1) ist keine Kausalitätsaussage
möglich; ohne (2) keine Fensterüberlappung zwischen Client und Server.

Beispiel für die Zuordnung, die dann zulässig wird:

```json
{"tick": 137, "t_mono_ms": 612340, "side": "client", "slot": 0}
```

Prüfregel für Werkzeuge: Fehlt der gemeinsame Tick, darf `--first-bad-tick`
**nicht** gegen Action-Trace-Ticks gestellt werden; der
`checksum_coverage_probe.py` liefert sonst `INCONSISTENT_TOO_LATE` aus einem
Artefaktfehler statt aus einem Befund.

---

## R5 — Action-Byte-Bilder

Ziel: Prüfen, ob die Bytes, die die Checksum liest, zwischen Client-Erzeugung
und Server-Anwendung identisch sind.

Erfassung:

* **Client:** unmittelbar nach `CPlayerSource::SetAction(pa)` im eigenen Build —
  die Bytes des `pa`-Objekts, **vor** dem Versand.
* **Server:** unmittelbar nach `ApplyActionPacket` bzw. vor
  `CPlayerEntity::ApplyAction`, derselbe Slot, derselbe Tick-Stempel (R4).
* Länge: `sizeof(CPlayerAction)` der 1.07-SDK (nicht raten!).

Format (`syncval-action-trace`, exakt der Parser des Probes):

```
#syncval-action-trace,rev=1
#source,client
#tick,slot,bytes_hex
137,0,00000000000000000000000000000000...
```

Wichtig:

* Es wird **nichts interpretiert**, nur die rohe Bytefolge gespeichert. Die
  Feldbedeutung kommt ausschließlich aus dem verifizierten Layout (A1).
* Rohbytes enthalten keine personenbezogenen Daten, aber ggf. Spielernamen in
  anderen Feldern — die Traces bleiben privat, wenn sie mehr als den
  Action-Block enthalten.

Layout-Hypothese (bis A1 geschlossen ist, **nicht** zitierfähig):

```json
{
  "status": "UNVERIFIED",
  "source": "Offsets aus dem 1.07-SDK-Header eintragen",
  "struct_size": 0,
  "fields": [],
  "checksum_calls": [{"offset": 0, "length": 4}, {"offset": 0, "length": 4}]
}
```

Erst mit `"status": "VERIFIED_107"` und echten Offsets liefert der Probe ein
zitierfähiges Ergebnis.

---

## R6 — Telemetrie rev=2

Die aktuelle `BotTelemetry.csv` (rev=1) hat 21 Spalten und **keinen** Game-Tick
und keine monotone Uhr. Für Fenstervergleiche fehlen:

| Neue Spalte | Typ | Bedeutung |
|---|---|---|
| `t_mono_ms` | int64 | monotone Prozesszeit |
| `game_tick` | int64 | Engine-Tick-Zähler (SessionState-Level) |
| `net_sends` | int64 | Anzahl `TimerLoop`-Aufrufe (Versandchancen) |
| `actions_slot0..3` | int64 | `SetAction`-Zähler **pro Slot** (statt Summe) |

Bestehende Spalten bleiben unverändert; `rev=2` ist additiv, damit
`tools/bot_telemetry.py` (P0, main) weiter funktioniert. Der
`cadence_model.py` liest rev=1 und nutzt die neuen Spalten, sobald vorhanden
(Spalten werden über `#columns` aufgelöst, nicht über Positionen).

Bis R6 existiert, gilt: Kadenzbefunde sind **innerhalb** eines Artefakts gültig,
eine Überlappung mit SYNCBAD-Fenstern wird **nicht** behauptet.

---

## R7 — Sync-Ereignis-Erfassung

Serverlog muss enthalten (Standardverhalten, nur nicht abschalten):

* `SYNCBAD: Client '<ip>', Sequence <n> Tick <t> - bad <k>`
* `SYNCOK: Client '<ip>', Tick <t>` (falls `ser_bReportSyncBad=1` ausreicht;
  `ser_bReportSyncOK` nur kurzzeitig und mit Loggrößenkontrolle)
* `Client '<ip>' ordered to disconnect: Too many bad syncs`
* Join/Leave, Mapwechsel (`Level ... started`)

Zusätzlich für H6 nützlich: `SYNCLATE`/`SYNCEARLY`, weil sie einen
**Level-Offset** (Client hinter/vor dem Server) belegen und damit transiente
Mismatches erklären, ohne eine Zustandsdifferenz zu behaupten (vgl. PR #50:
105 Mismatch-Ticks mit eigenem SYNCOK).

---

## R8 — Evidenz-Bundle

Ablage (privat, **nicht** in Git):

```
<bundle>/
  manifest.json
  server.log
  client.log
  BotTelemetry.csv
  dumps/server/*.txt
  dumps/client/*.txt
  traces/client-actions.csv
  traces/server-actions.csv
```

`manifest.json`-Schema (Template erzeugen:
`python3 tools/evidence_bundle_audit.py --bundle <dir> --emit-template manifest.json`):

```json
{
  "bundle_id": "syncval-native-<run>-<yyyymmdd>-<hhmm>",
  "simulated": false,
  "run": {"id": "...", "date_utc": "...", "operator": "...", "platform": "windows-native",
          "tick_hz": 20, "map": "...", "bots": 1, "clients": 1},
  "config": {"cli_bDumpSync": 1, "cli_bDumpSyncEachTick": 0, "ser_bReportSyncBad": 1,
             "ser_iKickOnSyncBad": 10, "frida_or_debugger_attached": false},
  "processes": {
    "server": {"exe_sha256": "...", "engine_sha256": "...", "entities_sha256": "...",
               "network_version": "1.07"},
    "clients": [{"name": "botclient-1", "exe_sha256": "...", "engine_sha256": "...",
                 "entities_sha256": "...", "gamemp_sha256": "...", "role": "bot"}]
  },
  "artifacts": {
    "server_log": {"path": "server.log", "sha256": "..."},
    "client_logs": [{"path": "client.log", "sha256": "..."}],
    "telemetry": [{"path": "BotTelemetry.csv", "sha256": "..."}],
    "server_dumps": ["dumps/server/t0121.txt"],
    "client_dumps": ["dumps/client/t0121.txt"],
    "action_traces": {"client": ["traces/client-actions.csv"],
                      "server": ["traces/server-actions.csv"]}
  }
}
```

Verboten im Bundle-Ordner: `GENERATED_FIXTURE.txt` (markiert Fixtures; das Audit
verweigert dann `SIMULATED_NEVER_NATIVE`). Rohlogs, Profile und Binaries bleiben
privat (AGENTS.md).

---

## 9. Beobachtungsmatrix: Anforderung → Hypothese

| Beobachtung | kommt aus | prüft |
|---|---|---|
| `build.hash_inventory_match` | R1 | H5 |
| `build.fp_provenance_match` | R2 + Build-Log | H3 |
| `evidence.bundle_complete` | R8 | Voraussetzung für alle `NATIVE_SUPPORTED` |
| `cadence.*` | R6 | H1, H7 |
| `coverage.*` | R4 + R5 + A1 | H2 |
| `dumps.*` | R3 | H4 |
| `log.counter_jumps`, `log.disconnect_after_kick` | R7 | H6 |
| `fp.*` | offline (`fp_determinism_probe.py`) | H3 (Modellseite) |

Ohne R3 und R5 kann **keine** Hypothese `NATIVE_SUPPORTED` erreichen; das ist
beabsichtigt und im Verdikt-System erzwungen.
