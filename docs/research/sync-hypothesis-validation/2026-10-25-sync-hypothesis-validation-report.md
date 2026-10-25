# Sync-Hypothesen-Validierung — Serious Sam TSE Classic 1.07

**Datum:** 25.10.2026 · **Rolle:** unabhängige Forschungs- und Entwicklungsarbeit
(LMArena A1) · **Branch:** `arena/2a42754c-serioussam-tse-bot-servermods`
**Schreibbereich:** ausschließlich `poc/research/sync-hypothesis-validation/**`,
`docs/research/sync-hypothesis-validation/**`.
**Ergebnis:** 7 falsifizierbare Hypothesen + 5 deklarierte Annahmen, 8 Werkzeuge,
**92/92 Offline-Tests PASS**, native Evidenz fehlt weiterhin.
**Root Cause: NICHT bestätigt.** `root_cause_status = NOT_ESTABLISHED` ist in
jedem Werkzeug-Ausgang erzwungen.

---

## 0. Kurzfassung

Der historische Fehler „Too many bad syncs“ ist als **Server-Kick-Mechanismus**
belegt (Retail-1.07-`Engine.dll`, Handler `FUN_601A2D10`, Grenzwert 10). Offen
ist die **Ursache der CRC-Divergenz**. Die bisherige Projektarbeit hat das
Log-/Dump-Forensik-Niveau erreicht (PR #58: E1–E6, Korrelation, Dump-Diff,
29/29 Tests). Was fehlte, war die **Gegenrichtung**: Hypothesen so formulieren,
dass eine Beobachtung sie *widerlegen* kann, und die Beobachtung selbst
verbindlich einfordern.

Dieser Beitrag liefert genau das:

1. **Sieben Hypothesen** (H1–H7) mit Claim, Vorhersage, Falsifizierer und
   Mindest-Evidenzklasse; **fünf Annahmen** (A1–A5), die bewusst *nicht* als
   Hypothesen geführt werden, weil sie nicht daten-, sondern statisch zu
   klären sind.
2. **Drei prüfbare Offline-Modelle**, die quantitative Vorhersagen machen:
   Takt-/Action-Treue (20 Hz, Single-Slot), Checksum-Scope (4 Byte × 2 Aufrufe),
   Float-Modell-Divergenz (binary32 vs. x87-artig vs. fast-math vs. float64).
3. **Einen maschinenprüfbaren Evidenzvertrag** für native Läufe, der
   `SIMULATED_NEVER_NATIVE` erzwingt und einen abgesenkten
   `ser_iKickOnSyncBad` als `INVALID` verwirft.
4. **Ein Verdikt- und Konflikt-System**, das Offline-Evidenz niemals als nativ
   ausgibt und widersprüchliche Artefakte als `CONFLICT` blockiert.

Ein **belastbares Nebenergebnis** (Modell-Beweis, §6.1): der im BotDriver
benutzte Composer-Round-Trip `acc += (target - acc)` ist für die modellierten
Fälle **bit-exakt** (Sterbenz-Differenz + exakt darstellbare Summe). Die
naheliegende Vermutung „Float-Rundung im Composer verursacht CRC-Divergenz“ ist
damit für diesen Pfad **widerlegt**; Float-Divergenz kann nur über
**Akkumulation** (Ziel-Heading, Geschwindigkeit) und **Integration** entstehen —
dort aber sofort und bit-sichtbar (Tick 1 bzw. 3 im Modell).

---

## 1. Auftrag, Vorgehen, Abgrenzung

### 1.1 Vorgehen

1. Repository-Inventar: `README.md`, `AGENTS.md`, alle Sync-Berichte, PR-Stände.
2. Prüfung von PR #58 (offen), #45 (merged), #50/#57 (offen) auf Überschneidung.
3. Quellcodestudium des tatsächlichen Action-Pfads (`Game.cpp`, `BotDriver.cpp`,
   `BotTelemetry.h`, `botcore.h`) und der Takt-/Handler-Reihenfolge.
4. Bau der Werkzeuge **erst nach** der Abgrenzung, damit nichts doppelt
   implementiert wird (Tabelle 2.3).
5. Tests zuerst gegen Negativkontrollen (identische Dumps, cadence-clean,
   unalignierte Traces, gefälschte native Behauptung).

### 1.2 Was hier ausdrücklich **nicht** getan wurde

* Kein Zugriff auf Produktionsserver, keine Serverneustarts, keine DLL-Änderung.
* Keine echten Logs, Binaries oder Spieldaten in Git; alle Fixtures synthetisch.
* Keine Änderung an `poc/research/sync-forensics/**` (PR #58), `poc/botcore/**`,
  `poc/release/**`, `poc/candidates/**`, `poc/patch/**`, `tools/**`.
* Keine Root-Cause-Behauptung, keine „PASS“-Sprache für Offline-Ergebnisse.

---

## 2. Bestandsaufnahme

### 2.1 Bereits belegte Fakten (nicht erneut erarbeitet)

| Befund | Quelle | Verwendung hier |
|---|---|---|
| Kick-Mechanismus, Handler `FUN_601A2D10` (4.976 B), Strings `SYNCBAD`/`SYNCOK`/`SYNCLATE`/`SYNCEARLY`, Grenzwert **10** bei `0x602A7EB4`, `ser_iKickOnSyncBad` | `docs/reports/2026-10-17-retail107-sync-check-investigation.md` (Ghidra-Dekompilation, `Engine.dll` `B79BF8BB…`) | Rahmen aller Hypothesen; A5 |
| Zwei reale Fehlläufe (`eight-hour`: SYNCBAD 1→10, Tick 83,40–92,40; `eight-combat-only`: 23,50–37,15; je 1 Disconnect, je 0 SYNCOK) | ebenda (private Rohlogs) | Beobachtungsfenster für Modellvergleiche |
| `CPlayerAction::ChecksumForSync` (`0x6019EC10`) liest **genau 4 aufeinanderfolgende Bytes** je Aufruf; `CSessionState::ChecksumForSync` ruft zweimal pro Spieler | PR #21, referiert in PR #58 §B10–B11 | Kern von H2/A1 |
| `cli_bDumpSync` (`0x602CD6EC`), `temp\syncdump.txt` mit `CRC: 0x%08X`; `cli_bDumpSyncEachTick` als Symbol, Funktion unbelegt | PR #21, referiert in PR #58 §B10 | Evidenzvertrag (R3) |
| CRC-Pfad umfasst `Classes\Player.ecl`, `EntitiesMP.dll`, geladene Spieldaten; **GameMP.dll nicht** in der CRC-Liste | `docs/research/2026-09-30-readiness-gamemp-crc-addendum.md` | H2, H3 |
| 20 Hz (`CTimer::TickQuantum = 1/20 s`), `NET_MAXLOCALPLAYERS = 4`, `pa_llCreated` wird von `SetAction` gestempelt | ebenda + `poc/VERIFIKATION.md` | H1, A2, A3 |
| Handler-Reihenfolge pro Tick: erst `CNetworkTimerHandler` (`TimerLoop`, versendet Actions des Vor-Ticks), dann `CGameTimerHandler` (`GameHandleTimer`) | `docs/research/2026-10-21-independent-review-cpu-optimization.md` §1.1 (**Referenz-Annahme** aus SE 1.10) | H1 |
| Qualifizierte Kandidaten: `61DC27E0…` (3.697,29 s, 8 Bots, 6 CRC-Akzeptanzen), `7FC94A39…` (3.600 s, 6.430 SYNCOK, 0 SYNCBAD) | `README.md`, `docs/reports/2026-10-21-human-cpu-final.md` | Generationen-Trennung |
| Ground-Lookahead `53982F05…`: aktivierter 600-s-Retry → „Too many bad syncs“, keine Abnahme | `README.md`, `docs/reports/2026-10-12-shadow-development-status.md` | H4 |
| PR #50: 105 historische externe SYNCBAD, 9 Disconnects, **alle 105 Mismatch-Ticks haben zusätzlich ein eigenes SYNCOK**; CRC-Ursache offen | PR #50-Beschreibung | *transientes* Muster → gegen H1/H2/H3 abzugleichen |
| PR #57: Kandidat `7dc961c8…`, isolierter Ein-Bot-Lifecycle `PASS_LIMITED_SESSION_LIFECYCLE` (131,87 s, SYNCOK, kein SYNCBAD) | PR #57-Beschreibung | Kandidatenmatrix |

### 2.2 Offene Punkte (unverändert)

* Erster divergenter Tick und betroffenes Sync-Feld: **unbekannt** (kein
  nativer `cli_bDumpSync`-Lauf).
* Genaue Byte-Offsets der beiden 4-Byte-Checksum-Aufrufe im 1.07-`CPlayerAction`:
  **unbekannt** → A1 bleibt `OPEN`.
* Ob `SetAction` in 1.07 wirklich Single-Slot ist: nur 1.10-Referenz → A2 `OPEN`.
* FP-Modell des BotClient-Builds (MSVC-Flags, x87 vs. SSE2): nicht dokumentiert.

### 2.3 Abgrenzung gegen bestehende Werkzeuge (keine Doppelimplementierung)

| Bestehendes Werkzeug | Eigentümer | Was hier **nicht** neu gebaut wurde | Ergänzung hier |
|---|---|---|---|
| `tools/analyze_sync_log.py`, `sync_forensics_common.py`, `sync_error_classifier.py` (E1–E6) | main / PR #58 | Kein zweiter vollständiger Log-Parser, keine neue E-Klassifikation | `result_compare.py` konsumiert solche JSONs; lokaler Mini-Parser nur für Kick/Counter-Fakten im Bundle-Audit |
| `sync_crc_diff.py`, `sync_tick_compare.py`, `sync_correlator.py` | PR #58 | Kein Dump-Feld-Diff, keine Ereignis-Chronologie | `checksum_coverage_probe.py` vergleicht **Action-Byte-Bilder** gegen einen **Checksum-Scope**, nicht Dumps |
| `tools/bot_telemetry.py` (P0) | main | Keine Neuimplementierung der Telemetrie-Validierung | `cadence_model.py` liest dieselbe CSV, beantwortet aber die 1:1:1-Kadenzfrage |
| `poc/botcore`-Tests, Human-KI-Tests | main / A2 | Keine KI-/Combat-Tests | reine Sync-/Zeit-Modelle |
| Supervisor/Recovery (C1, PR #46/#49/#50) | Codex C1 | nichts | keine Betriebslogik |

---

## 3. Quellcode-Befunde zum tatsächlichen Action-Pfad

Labels: **[Fakt]** = im Repository-Quellcode gelesen · **[Referenz-Annahme]** =
aus SE-1.10-Dokumentation abgeleitet, für 1.07 nicht binär verifiziert ·
**[Hypothese]** = daraus abgeleitete, ungeprüfte Behauptung.

| # | Befund | Label | Beleg |
|---|---|---|---|
| F1 | `CGame::GameHandleTimer()` beginnt mit `if (BotDriver_HandleTimer(this)) return;` — bei aktivem Treiber wird der gesamte Vanilla-Eingabepfad (Input-Polling, `CreateAction`, `SetAction`, Clear-Zweig) übersprungen | [Fakt] | `poc/release/gamemp/Game.cpp:754` |
| F2 | Der Vanilla-Zweig erzeugt pro lokalem Slot **eine** Action pro Timer-Aufruf: `ctrls.CreateAction(...)` → `SetAction(paAction)` | [Fakt] | `Game.cpp:780-805` |
| F3 | Der Clear-Zweig (kein DirectInput) setzt Translation auf 0, lässt Rotation stehen, Buttons 0 | [Fakt] | `Game.cpp:826-843` |
| F4 | `CControls::CreateAction` setzt zunächst **Achsen** (normalisierte Werte), dann Buttons, dann `ctl_ComposeActionPacket` | [Fakt] | `Game.cpp:430-452` |
| F5 | Der Treiber erhöht `bs.bs_iTick` **einmal pro Timer-Aufruf**, nicht pro Netz-Tick, und setzt ihn bei Wechsel des Player-Source-Objekts (Join/Rejoin/Mapwechsel) auf 0 zurück | [Fakt] | `poc/release/gamemp/BotDriver.cpp:296-307` |
| F6 | Der Treiber setzt `pa.pa_vTranslation(3) = -moveFactor` (normalisierte Achse) und `pa.pa_aRotation(1) = bs.bs_aHeading - localInput->m_aLocalRotation(1)` (Differenz zum Akkumulator) | [Fakt] | `BotDriver.cpp:459-466` |
| F7 | Vor `ctl_ComposeActionPacket` wird `ctl_pvPlayerControls` **genullt** und danach restauriert — der Composer sieht also einen künstlichen Control-Buffer | [Fakt] | `BotDriver.cpp:470-476` |
| F8 | Buttons werden erst **nach** dem Composer gesetzt (`BOT_PLACT_FIRE`, Waffengruppe) | [Fakt] | `BotDriver.cpp:477-479` |
| F9 | Heading-Akkumulation geschieht im Treiber: `bs.bs_aHeading += bot_fYawSpeed*fTick` bzw. Rebasierung auf `player->m_aLastRotation(1)` | [Fakt] | `BotDriver.cpp:380, 398-406` |
| F10 | `pa_llCreated` wird von `SetAction` gestempelt; der Treiber setzt es nicht | [Fakt] | `BotDriver.cpp:23,478` |
| F11 | `SetAction` ist „latest wins“ mit einem Slot; Actions werden erst im **nächsten** `TimerLoop` versendet | [Referenz-Annahme] | `docs/research/2026-10-21-independent-review-cpu-optimization.md` §1.1 (SE 1.10 `PlayerSource.cpp`) |
| F12 | Der Timer läuft über WinMM `timeSetEvent(50 ms)`; Handler werden bei jedem Callback aufgerufen. Unter Last kann der Callback ausfallen | [Referenz-Annahme] | ebenda (`Timer.cpp`) |
| F13 | Per-Tick-Logzeilen sind durch `bot_iLogEvery` gegated; fehlende Zeile ≠ fehlende Action | [Fakt] | `BotDriver.cpp:481-495`, `BotTelemetry.h` |

**Konsequenz aus F5+F11+F12:** Jede Abweichung von „1 Timer-Aufruf → 1 Action
pro Slot → 1 Netzversand“ verändert die Actions, die der Server sieht —
entweder durch **Wiederholung** (Timer langsamer als Netz) oder durch
**stilles Verwerfen** (mehr `SetAction` als Timer-Ticks). Das ist die einzige
Klasse von Fehlern, die ohne Simulationsänderung auskommt (→ H1, H7).
Und: aus F13 folgt, dass „keine SyncBAD-Zeile im Client-Log“ **kein** Beleg für
saubere Kadenz ist.

---

## 4. Priorisierter Ursachenbaum

```
„Too many bad syncs“ (Kick)                        [BELEGT: Handler, Grenzwert 10]
│
├─ A) Der Client sieht/erzeugt andere Actions als der Server
│   ├─ A1 Kadenzverlust (Timer < 20 Hz, Doppelaufruf, Slot-Drift)      H1, H7   [prüfbar: Telemetrie]
│   ├─ A2 Action-Bytes divergieren trotz gleicher Absicht             H2        [prüfbar: Byte-Bilder + Scope]
│   │     └─ eingeschränkt durch A1_CHECKSUM_SCOPE (4 B × 2)
│   └─ A3 Zeitstempel-/Reihenfolge-Effekt (pa_llCreated, Level-Offset) H1        [offen: kein Level-Log]
│
├─ B) Der Client simuliert anders als der Server (Actions identisch)
│   ├─ B1 Client-Gameplay-Änderung (Ground-Lookahead/Physik)          H4        [prüfbar: Dumps]
│   ├─ B2 Float-Modell/Build-Flags (x87 vs. SSE2, /fp:fast)           H3        [prüfbar: Modell + Build-Beleg]
│   └─ B3 Binär-/Netzwerk-Build-Mismatch                             H5        [prüfbar: Hash-Inventar]
│
└─ C) Die Beobachtung selbst täuscht
    └─ C1 Counter-Artefakt / unvollständiges Log                      H6        [prüfbar: PR #58 E1–E6]
```

Priorisierung folgt drei Kriterien: (a) erklärt die Hypothese die vorhandenen
**drei** Fehlergenerationen, (b) ist sie mit **diesem** Repository-Stand
falsifizierbar, (c) kostet die Prüfung keinen Produktionszugriff.

| Rang | Hypothese | Begründung |
|---|---|---|
| 1 | H1 (Kadenz/Single-Slot) + H2 (Action-Bytes) | einzige Klasse ohne Simulationsänderung; erklären transiente Muster (PR #50: Mismatch-Tick **mit** SYNCOK) besser als eine dauerhafte Physikdifferenz |
| 1 | H4 (Client-Simulationsänderung) | einzige Hypothese mit **direktem** Fehlbeleg (Ground-Lookahead-Kandidat) plus Gegenbeleg (qualifizierte Kandidaten stabil) |
| 2 | H3 (Float-Modell) | mechanisch plausibel, im Modell sofort bit-sichtbar; braucht Build-Provenienz als Beleg |
| 2 | H5 (Binär-Inventar) | billig zu prüfen, harte Ausschlusswirkung |
| 2 | H7 (Tick-Semantik) | keine Ursache, aber Ursache für **Fehlinterpretation** der Tick-Skalen (z. B. „Tick 15400“) |
| 3 | H6 (Log-Artefakt) | durch PR #58 weitgehend abgedeckt |

---

## 5. Hypothesen- und Annahmenregister

Vollständig maschinenlesbar in `tools/hypothesis_registry.py`
(`python3 tools/hypothesis_registry.py --ids`). „Status“ = Stand **ohne**
native Evidenz, d. h. systematisch `NOT_TESTED`/`INCONCLUSIVE`.

### 5.1 Hypothesen

| ID | Prio | Kurzfassung | Falsifizierer (Auszug) | Mindest-Evidenz | Status heute |
|---|---|---|---|---|---|
| **H1_ACTION_CADENCE** | 1 | Takt ≠ 20 Hz oder Actions/Tick ≠ Slots → Server wendet andere Actionfolge an | saubere Kadenz in **allen** aktiven Fenstern bei gleichzeitigem SYNCBAD | `telemetry` | `NOT_TESTED` (keine Telemetrie eines Fehllaufs) |
| **H2_ACTION_COMPOSITION** | 1 | komponierte Action-Bytes ≠ vanilla-äquivalente Bytes | keine checksum-sichtbare Differenz **oder** Differenz erst **nach** erstem SYNCBAD-Tick | `telemetry` | `NOT_TESTED` (keine Action-Byte-Bilder) |
| **H3_FP_MODEL** | 2 | unterschiedliche Float-Modelle → Bit-Differenz im Zustand | identische Build-Provenienz **oder** Modell divergiert nicht | `telemetry` | `MODEL_SUPPORTED` nur mit Provenienz-Beleg; heute `INCONCLUSIVE` |
| **H4_CLIENT_SIM_MODIFICATION** | 1 | Client-Physik/Gameplay weicht ab, Actions identisch | Entity-Zustände in alignierten Dumps identisch | `native` | `NOT_TESTED` |
| **H5_BINARY_INVENTORY** | 2 | Binär-/Netzwerk-Build-Mismatch | alle vier Hashes + Netzwerkversion identisch | `telemetry` | `NOT_TESTED` |
| **H6_LOG_ARTIFACT** | 3 | Counter-/Log-Artefakt statt echter Divergenz | monotoner +1-Counter mit SYNCOK-Resets | `log` | durch PR #58-Werkzeuge bearbeitbar; hier `NOT_TESTED` |
| **H7_BOT_TICK_SEMANTICS** | 2 | `bs_iTick` zählt Timer-Aufrufe, nicht Netz-Ticks; Log-Gating täuscht | 20,0 Aufrufe/s und exakt 1 `SetAction`/Slot | `telemetry` | `NOT_TESTED` |

### 5.2 Annahmen (bewusst **nicht** als Hypothesen geführt)

| ID | Aussage | Status | Offene Frage |
|---|---|---|---|
| **A1_CHECKSUM_SCOPE** | nur die 4×2 gelesenen Bytes können die Action-Checksum ändern | `OPEN` | Offsets im 1.07-Struct fehlen (SDK-Header nötig) |
| **A2_SINGLE_SLOT_ACTION** | `SetAction` = ein Slot, „latest wins“ | `OPEN` | nur 1.10-Referenz |
| **A3_TICK_20HZ** | Tick = 1/20 s, `GameHandleTimer` einmal pro Tick | `OPEN` | WinMM-Koaleszenz unter Last; gemessene Rate zählt |
| **A4_VANILLA_COMPONENTS** | Server/Humans/4 Vanilla-Dateien unverändert | `OPEN` | SHA256-Inventar pro Prozess (R1) |
| **A5_KICK_LIMIT_UNTOUCHED** | `ser_iKickOnSyncBad` bleibt 10 | `ENFORCED` | keiner; vom Bundle-Audit erzwungen |

Warum die Trennung? A1 ist kein Kandidat für „die Ursache“, sondern eine
**Scope-Schranke**: sie entscheidet, welche H2-Beobachtungen überhaupt relevant
sind. Würde man A1 als Hypothese führen, könnte ein Datenlauf sie „stützen“ —
obwohl sie nur statisch klärbar ist.

---

## 6. Offline-Ergebnisse (reproduzierbar)

Umgebung: Python 3.11.2, Linux-Sandbox, keine Spielprozesse. Alle Zahlen sind
**Modell-/Fixture-Ausgaben**, keine Runtime-Messung.

### 6.1 Float-Modell-Divergenz (`fp_determinism_probe.py`)

Szenario: 20 Hz, Vorwärtsfahrt, Heading-Rampe; Zustand = (Ziel-Heading,
Akkumulator, Position). Modi: `f32_strict` (jede Operation binary32),
`f32_extended` (double-Zwischenwerte, binary32-Speicherung — x87-artig),
`f32_simplified` (algebraische Vereinfachung des Round-Trips — /fp:fast-artig),
`f64_ideal` (keine 32-Bit-Rundung).

```bash
python3 tools/fp_determinism_probe.py --ticks 400          # yaw 45,7 °/s
python3 tools/fp_determinism_probe.py --ticks 400 --yaw-rate 45.0
```

| Fragestellung | Ergebnis |
|---|---|
| Erste Bit-Differenz Zustand (yaw 45,7) | **Tick 1** (gegen `f64_ideal`), **Tick 3** (`f32_strict` vs `f32_extended`) |
| Erste **action-sichtbare** Differenz | Tick 3 (d. h. die Action-Bytes selbst divergieren) |
| Composer-Round-Trip `acc += (target-acc)` | **exakt gleich** in `f32_strict` und `f32_simplified` (auch bei 200 Ticks) — Sterbenz-Differenz + exakt darstellbare Summe |
| yaw 45,0 (binär exakt): alle 32-Bit-Modi | **bitidentisch** über 200 Ticks; nur `f64_ideal` weicht ab (Tick 5) |
| 1-ULP-Störung im **Akkumulator** | wird **absorbiert** (keine Propagation in Position/Winkel) |
| 1-ULP-Störung in der **Geschwindigkeit** | propagiert ab Tick 1; Drift 1,1444·10⁻⁵ Einheiten (400 Ticks) |
| Drift `f32_strict` vs `f64_ideal` | 60 s: 0,005332 E · 0,016602° — 360 s: 0,251629 E · 0,775391° |

**Interpretation (Beweisgrenze beachten):**

* Der Composer-Round-Trip ist als Divergenzquelle **unwahrscheinlich** — genau
  der Pfad, den H2 früher als Float-Problem verdächtigt hätte.
* Float-Divergenz ist dort möglich, wo **akkumuliert/integriert** wird
  (Heading-Ziel, Geschwindigkeit, Position). Sie ist dann aber **ab Tick 1–3
  bit-sichtbar**, also lange vor den historischen SYNCBAD-Fenstern
  (Tick 23,5–37,15 und 83,4–92,4).
* Damit ist H3 **nicht** als Erklärung für ein spätes Einsetzen geeignet, wohl
  aber für ein sofortiges. Das ist eine prüfbare Vorhersage für C2:
  *Divergenz ab Tick 1–5 → FP-/Simulationsklasse; Divergenz erst ab Tick > 20 →
  eher Action-/Kadenz-/Ereignisklasse.*

**Grenze:** modelliert ist Kinematik (Translation, Heading, Position), **keine**
Entity-Physik (Gravitation, Kollision, Waffen). Das Modell kann H3 daher nur für
diese Zustandsanteile beurteilen.

### 6.2 Kadenz-/Action-Treue (`cadence_model.py`)

Quelle: `BotTelemetry.csv` in der in `BotTelemetry.h` veröffentlichten,
festen Spaltenfolge. Fenster = aufeinanderfolgende Zeilen (1 s).

```bash
python3 tools/make_synthetic_cases.py --out /tmp/fx
python3 tools/cadence_model.py --telemetry /tmp/fx/telemetry_starved.csv
```

| Fixture | Verdikt | Kernzahlen |
|---|---|---|
| `telemetry_ok` | `CADENCE_OK` | 59 Fenster, 20,0 Hz, Action-Fidelity 1,0 |
| `telemetry_starved` (8 statt 20 Ticks/s, 20–30 s) | `CADENCE_DIVERGENCE` | 10 Fenster `TIMER_STARVED`, Rate 0,8983, schlechtestes Fenster 0,4 |
| `telemetry_dead` (3 s ohne Tick) | `CADENCE_DIVERGENCE` | `TIMER_DEAD` |
| `telemetry_coalesced` (40 Actions bei 20 Ticks) | `CADENCE_DIVERGENCE` | `ACTION_COALESCED` |
| `telemetry_inactive` | `CADENCE_OK` | alle Fenster `INACTIVE`, nicht als Divergenz gezählt |
| `telemetry_malformed` (kein `#columns`) | **Exit 2** | „telemetry rejected“ — kein stilles Raten |
| keine Datenzeilen | `CADENCE_UNMEASURABLE` (Exit 4) | „Stille ist kein Gesundheitsbeweis“ |

**Wichtige Ableitung:** Die Interpretation „Timestamp-Fenster“ ist nur zulässig,
wenn Client und Server eine **gemeinsame Uhr** haben. Das ist heute **nicht**
der Fall → Anforderung **R6** (siehe Instrumentierungsdokument). Bis dahin wird
keine zeitliche Überlappung mit einem SYNCBAD-Fenster behauptet.

### 6.3 Checksum-Scope (`checksum_coverage_probe.py`)

Vergleicht **rohe Action-Byte-Bilder** (Client vs. Server) und trennt
Differenzen in „innerhalb“ und „außerhalb“ der vom Checksum gelesenen Bytes.
Fixtures nutzen ein **synthetisches** Layout (40 B, Aufrufe bei Offset 4 und 16);
das ist ausdrücklich **kein** 1.07-Offset.

| Fixture | Verdikt | Exit | Aussage |
|---|---|---|---|
| identische Traces | `NO_ACTION_DIVERGENCE` | 0 | Actions können die Divergenz nicht erklären |
| Differenz bei Tick 137 in `pa_aRotation` | `CHECKSUM_VISIBLE_DIVERGENCE` | 3 | eine Action-Differenz **existiert** |
| dieselbe Differenz, `--first-bad-tick 83.4` | `INCONSISTENT_TOO_LATE` | 3 | sie **erklärt den Fehlschlag nicht** (erst später) |
| Differenz nur in `pa_aViewRotation` (Tick ≥ 90) | `DIVERGENCE_OUTSIDE_CHECKSUM_SCOPE` | 3 | sichtbar im Byte-Bild, **unsichtbar** für die Checksum |
| Server-Trace endet bei Tick 100 | `INCOMPLETE` | 4 | unvollständige Paare ergeben keine Aussage |
| Layout `UNVERIFIED` | `LAYOUT_UNVERIFIED` | 5 | Ergebnis nur layout-bedingt, nicht zitierfähig |

Die Coverage-Tabelle ist der eigentliche Erkenntnisgewinn: bei den
Fixture-Offsets sind `pa_vTranslation` und `pa_aRotation` **nur teilweise**
abgedeckt (je ein Float), `pa_aViewRotation` und `pa_ulButtons` **gar nicht**.
→ Ein Bot, der nur Buttons/ViewRotation anders setzt, kann über diesen Pfad
**keine** Checksum-Differenz erzeugen.

### 6.4 Evidenzvertrag und Konflikterkennung

`evidence_bundle_audit.py`:

| Fall | Verdikt | Exit |
|---|---|---|
| generiertes Fixture (`GENERATED_FIXTURE.txt`) | `SIMULATED_NEVER_NATIVE` | 5 |
| `manifest.simulated != false` | `SIMULATED_NEVER_NATIVE` | 5 |
| `ser_iKickOnSyncBad = 0` | `INVALID` | 5 |
| SHA256 eines Artefakts falsch | `INVALID` | 5 |
| keine Dumps | `INSUFFICIENT` (Evidenz auf `telemetry` gedeckelt) | 4 |
| vollständig | `COMPLETE`, Beobachtungen `native` | 0 |

`result_compare.py` erkennt u. a. `GRADE_INFLATION`,
`NATIVE_CLAIM_WITHOUT_COMPLETE_BUNDLE`, `SIMULATED_INPUT_MIXED`,
`TOOL_DISAGREEMENT`, `INCONSISTENT_TIMELINE`, `HYPOTHESIS_CONFLICT`,
`OBSERVATION_DISAGREEMENT` und liefert `next_actions`.

### 6.5 Zwei durchgespielte Diskriminierungsszenarien (End-to-End-Test)

| Szenario | Beobachtungen | Verdikte |
|---|---|---|
| Entity-Divergenz, Actions identisch | Dumps 2 alignierte Paare, `PlayerEntitys` differiert bei Tick 121; Actions `NO_ACTION_DIVERGENCE`; Counter monoton; Kick mit Disconnect | **H4 `NATIVE_SUPPORTED`**, H2 `REFUTED`, H6 `REFUTED`, `root_cause_status = NOT_ESTABLISHED` |
| Action-Divergenz, Entity identisch | Dumps identisch; Actions sichtbar different ab Tick 137, `--first-bad-tick 200` | **H2 `NATIVE_SUPPORTED`**, H4 `REFUTED` |

Damit ist die Mechanik belegt: ein einziger nativer Lauf mit Byte-Bildern und
alignierten Dumps **entscheidet** zwischen den beiden Hauptklassen. Genau das
ist der Kern des C2-Plans.

---

## 7. Werkzeuge und Tests

| Datei | Zeilen | Zweck |
|---|---|---|
| `tools/syncval_common.py` | 513 | Parser (Telemetrie, Action-Traces, Layout, Sync-Zeilen), binary32-Helfer, Evidenzklassen, Exit-Codes |
| `tools/cadence_model.py` | 263 | 20-Hz-/Single-Slot-Modell |
| `tools/checksum_coverage_probe.py` | 268 | Checksum-Scope-Vergleich |
| `tools/fp_determinism_probe.py` | 327 | Float-Modell-Divergenz + ULP-Propagation |
| `tools/evidence_bundle_audit.py` | 522 | Instrumentierungsvertrag |
| `tools/hypothesis_registry.py` | 563 | H1–H7, A1–A5 |
| `tools/verdict_engine.py` | 295 | Verdikte mit Evidenz-Grading |
| `tools/result_compare.py` | 283 | Zusammenführung/Konflikte |
| `tools/make_synthetic_cases.py` | 388 | 20 Fixtures inkl. Negativkontrollen |
| `tests/*` (9 Dateien) | 1.235 | 92 Tests |

Summe: 3.422 Zeilen Werkzeuge, 1.235 Zeilen Tests.

```bash
cd poc/research/sync-hypothesis-validation
python3 -m unittest discover -s tests -v     # Ran 92 tests ... OK
./run_all_tests.sh
```

Getestete Eigenschaften (Auszug):

* Jede Hypothese hat Falsifizierer und Evidenz-Untergrenze; unbekannte Operatoren
  und nicht deklarierte Beobachtungen werden abgelehnt.
* Offline-Beobachtungen erzeugen **nie** `NATIVE_SUPPORTED`.
* Fehlende Telemetrie → `UNMEASURABLE`, nicht „OK“.
* Unalignierte/abgeschnittene Traces → `INCOMPLETE`, keine erfundene Divergenz.
* Generierte Bundles → `SIMULATED_NEVER_NATIVE`; abgesenkter Kick-Limit →
  `INVALID`.
* Widersprüchliche Beobachtungen → `CONFLICT` (Exit 6), nie Mehrheitsentscheid.
* Kein Ausgabefeld behauptet jemals „stability pass“ oder
  „root cause confirmed“ (strukturell geprüft).

---

## 8. Beweisgrenzen (explizit)

1. **Kein natives Artefakt geprüft.** Alle Aussagen sind Modell/Fixture.
2. **A1 ist unbelegt.** Ohne verifizierte 1.07-Offsets bleibt jedes
   Scope-Ergebnis `LAYOUT_UNVERIFIED` und ist nicht zitierfähig.
3. **Kein erster divergenter Tick.** Ohne `cli_bDumpSync`-Paare (R3) gibt es
   keinen Beleg für *irgendeine* Ursache.
4. **Keine Zeitkorrelation.** Telemetrie und Serverlog teilen keine Uhr (R6).
5. **Modellumfang.** Kinematik, keine Entity-Physik, keine Projektile, keine
   Waffenlogik.
6. **Kandidaten-Generationen.** Die stabile 61DC/7FC9-Lage widerlegt keine
   Fehlschläge anderer Kandidaten (53982F05, 7dc961c8) und umgekehrt.

Was einen Verdacht **belegen** würde: aligned Dump-Paar, das am *ersten*
divergenten Tick genau einen Feldtyp zeigt, plus Byte-Bild-Nachweis, dass die
Checksum-Scope-Bytes zu diesem Tick übereinstimmen (dann Simulationsklasse) oder
nicht (dann Actionklasse), reproduziert in **zwei** unabhängigen Läufen mit
identischem Kandidaten-Hash.

---

## 9. Risiken

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| `cli_bDumpSync` schreibt pro Tick → Log-/Dump-Flut, Timing-Verzerrung | Messartefakt statt Ursache | Dump-Intervall begrenzen (R3), instrumentierte von nicht-instrumentierter Kontrolle trennen |
| `ser_iKickOnSyncBad` „zum Testen“ senken | macht jeden Lauf scheinbar stabil | vom Audit als `INVALID` verworfen (A5) |
| Frida/Debugger im Messlauf | Timingänderung | im Manifest deklarieren; Audit warnt |
| Fixtures werden als native Evidenz zitiert | Wissenschaftlicher Fehler | Marker + `SIMULATED_NEVER_NATIVE` + Evidenz-Grading |
| Veraltete Kandidaten-Hashes | falsche Zuordnung | Hash-Inventar pro Prozess (R1) |
| Divergenzursache wird vorschnell „bestätigt“ | Projektrisiko | `root_cause_status` strukturell `NOT_ESTABLISHED` |

---

## 10. Handoff

### 10.1 Artefakte

```
poc/research/sync-hypothesis-validation/
  README.md
  run_all_tests.sh
  tools/{syncval_common,cadence_model,checksum_coverage_probe,
         fp_determinism_probe,evidence_bundle_audit,hypothesis_registry,
         verdict_engine,result_compare,make_synthetic_cases}.py
  tests/{_support,test_registry,test_cadence,test_checksum_coverage,
         test_fp_probe,test_bundle_audit,test_verdict_engine,
         test_result_compare,test_end_to_end}.py
docs/research/sync-hypothesis-validation/
  2026-10-25-sync-hypothesis-validation-report.md      (dieses Dokument)
  2026-10-25-instrumentation-requirements.md
  2026-10-25-codex-c2-native-validation-plan.md
```

Keine Datei außerhalb der beiden Bereiche wurde verändert.

### 10.2 Branch / Commit / PR

* Branch: `arena/2a42754c-serioussam-tse-bot-servermods`
* Basis: `ab0c740` (`main`)
* Commit: `3a2a239` (Toolkit + Dokumentation), Handoff-Update als Folge-Commit
* PR: **#65** gegen `main` —
  <https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/65>
* Tests: `92/92 PASS`, ausgeführt am 25.10.2026 (Python 3.11.2, Linux-Sandbox).
* Umfang: 23 Dateien, +5.766 Zeilen (9 Werkzeuge, 9 Testdateien, 4 Dokumente).

### 10.3 Nächste Schritte (Reihenfolge)

1. **A1 schließen:** Offsets der beiden 4-Byte-Aufrufe aus dem 1.07-SDK-Header
   bestimmen (read-only, statisch) → `layout_107.json` mit `status:
   VERIFIED_107`. Erst dann werden Scope-Ergebnisse zitierfähig.
2. **R3/R4 umsetzen** (Dumps + gemeinsame Tick-Herkunft) und einen Lauf mit
   **einem** Bot gegen den **qualifizierten** Kandidaten fahren → Baseline.
3. Denselben Lauf mit dem Ground-Lookahead-Kandidaten wiederholen → erwartete
   Diskriminierung (§6.5).
4. Erst danach: Hypothesen-Verdikte aus echten Daten, Vergleich mit PR #58.

### 10.4 Blocker

* Kein Zugriff auf Retail-Binaries/Windows-Runtime in dieser Session → alle
  nativen Schritte sind **`NOT_TESTED`**.
* A1 braucht den SDK-Header (nicht im Repository).
* Zeitkorrelation Telemetrie ↔ Serverlog braucht Codeänderung an der
  Telemetrie (**nicht** mein Schreibbereich, Vorschlag als R6 dokumentiert).
