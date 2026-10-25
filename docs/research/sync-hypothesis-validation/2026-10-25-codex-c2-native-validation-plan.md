# Nativer Validierungsplan für Codex C2 — Sync-Ursachenklassen diskriminieren

**Datum:** 25.10.2026 · **Für:** Codex C2 (native Sync-Diagnosewerkzeuge) und den
ausführenden RDC-Entwickler · **Status:** Plan, nicht ausgeführt.
**Vorbedingung:** [Instrumentierungsanforderungen](2026-10-25-instrumentation-requirements.md),
Sync-Berichte vom 17.10.2026, AGENTS.md-Sicherheitsregeln.

---

## 1. Entscheidungsfrage

Der Plan beantwortet **eine** Frage, nicht mehrere:

> Wenn ein Lauf `Too many bad syncs` erzeugt: divergieren die **Actions**
> (H1/H2), divergiert die **Client-Simulation** (H3/H4/H5), oder täuscht die
> **Beobachtung** (H6)?

Alles andere (CPU, KI-Qualität, Navigation, 24/7) ist explizit **nicht** Teil
dieses Plans. Eine Antwort gilt nur für den **gemessenen Kandidaten-Hash**.

Erfolgskriterium des Plans ist **nicht** „kein SYNCBAD“, sondern: bei einem
Fehllauf liegt ein aligniertes Dump-Paar um den ersten divergenten Tick plus
Action-Byte-Bilder vor, sodass `verdict_engine.py` H2 oder H4 mit
`NATIVE_SUPPORTED` belegt und die jeweils andere Hypothese `REFUTED`.

---

## 2. Vorbedingungen (Gate 0)

| Gate | Inhalt | Abbruchkriterium |
|---|---|---|
| G0.1 | R1-Hash-Inventar aller Prozesse erstellt | unvollständig → Lauf nicht verwertbar |
| G0.2 | R2-Konfig-Snapshot, `ser_iKickOnSyncBad = 10` | abgesenkt → **nicht starten** |
| G0.3 | `cli_bDumpSync = 1` im Client, Dump-Zielverzeichnis leer und schreibbar | nicht gesetzt → S5 nicht möglich |
| G0.4 | R5-Action-Trace aktiv (nur im **eigenen Testbuild**) | nicht verfügbar → H2 bleibt `NOT_TESTED` |
| G0.5 | Private Kopie der Installation, eigene Ports, Backup/Restore geprüft (`poc/LOCAL-RELEASE.md`) | geteilte Installation → **nicht starten** |
| G0.6 | `tools/Test-TSEExternalVanillaPreflight.ps1` bzw. Fleet-Preflight `canStart=true` | `false` → **nicht starten** |
| G0.7 | Fixture-Marker nirgends im Bundle (`GENERATED_FIXTURE.txt`) | vorhanden → Bundle ist simuliert |

Kein Gate darf „vorläufig“ übersprungen werden. Ein Lauf ohne G0.1–G0.3 wird
als `NOT_TESTED` verbucht, nicht als Ergebnis.

---

## 3. Testmatrix

Jede Stufe: identische Map, identische Netzwerkparameter, gleiche Laufzeit,
**nicht instrumentierte Kontrollprobe** wo angegeben. `t` = Laufzeit.

| Stufe | Client-DLL | Bots | t | Instrumentierung | Erwartung / Zweck |
|---|---|---|---|---|---|
| **S0** | Original-GameMP | 0 (Human/Observer) | 10 min | keine | Netz-/Umgebungsbaseline: 0 SYNCBAD. Schlägt S0 fehl, ist die Umgebung schuld, nicht der Bot |
| **S1** | `7FC94A39…` (Build04) | 1 | 10 min | **keine** | Reproduzierbarkeit des qualifizierten Zustands |
| **S2** | `7FC94A39…` | 4 | 10 min | keine | Skalierungsbaseline |
| **S3** | `7FC94A39…` | 4 | 10 min | **voll** (R3+R5+R6) | **Messartefakt-Kontrolle**: S2 vs. S3 müssen beide 0 SYNCBAD zeigen. Tritt in S3 SYNCBAD auf, ist die Instrumentierung selbst verdächtig |
| **S4** | `7FC94A39…` | 1 | 30 min | keine | Langzeitkontrolle; prüft spätes Einsetzen (vgl. PR #50-Muster) |
| **S5** | `53982F05…` (Ground-Lookahead) | 1 | bis Fehler oder 10 min | **voll** | **Diskriminierung**: erwarteter FAIL; Dumps + Traces um `first_bad_tick` |
| **S6** | derselbe Hash wie S5 | 1 | wie S5 | **voll** | Reproduzierbarkeit des Ergebnisses (gleicher Hash, gleiche Konfiguration) |
| **S7** *(optional)* | `7dc961c8…` (PR #57) | 1 | 10 min | voll | zusätzliche Generation; prüft, ob der Befund kandidatenspezifisch ist |

Regeln:

* **S3 ist Pflicht.** Ohne S3 ist jede Aussage aus S5 mit dem Verdacht
  „Instrumentierung verändert das Timing“ belastet (R3/R5 kosten Zeit im
  Timer-Pfad).
* S5/S6 müssen mit **identischem** Hash und identischer Konfiguration laufen;
  jede Änderung erzeugt eine neue Stufe.
* S0 darf nicht durch einen Bot-Lauf ersetzt werden.
* Läufe dürfen **nie** auf dem öffentlichen Server oder auf einer geteilten
  Installation stattfinden.

---

## 4. Ablauf je instrumentierter Stufe (S3, S5, S6, S7)

```bash
# 0) Bundle-Gerüst + Template
python3 poc/research/sync-hypothesis-validation/tools/evidence_bundle_audit.py \
    --bundle /pfad/bundle-s5 --emit-template /pfad/bundle-s5/manifest.json

# 1) vor dem Start: Hashes, Konfig, Ports, Preflight dokumentieren (R1/R2)
#    -> manifest.json füllen, Artefakt-Hashes erst NACH dem Lauf eintragen

# 2) Lauf starten (private Installation, eigene Ports)
#    Client: cli_bDumpSync=1, bot_bEnabled=1, bot_iTelemetry=1, Action-Trace an
#    Server: ser_bReportSyncBad=1, ser_iKickOnSyncBad=10 (unverändert)

# 3) nach dem Lauf: Artefakte einsammeln, Hashes eintragen, dann auditieren
python3 .../tools/evidence_bundle_audit.py --bundle /pfad/bundle-s5 \
    --out /pfad/audit-s5.json

# 4) Kadenz (nur wenn Telemetrie aus dem Lauf stammt!)
python3 .../tools/cadence_model.py --telemetry /pfad/bundle-s5/BotTelemetry.csv \
    --source-class telemetry --out /pfad/cadence-s5.json

# 5) Action-Bytes gegen Checksum-Scope (Layout erst nach A1!)
python3 .../tools/checksum_coverage_probe.py \
    --client-trace /pfad/bundle-s5/traces/client-actions.csv \
    --server-trace /pfad/bundle-s5/traces/server-actions.csv \
    --layout /pfad/layout_107.json \
    --first-bad-tick <Tick aus server.log> \
    --trace-class telemetry --out /pfad/coverage-s5.json

# 6) Hypothesen
python3 .../tools/verdict_engine.py /pfad/audit-s5.json /pfad/cadence-s5.json \
    /pfad/coverage-s5.json --out /pfad/verdicts-s5.json

# 7) Gesamtbericht inkl. Konflikten
python3 .../tools/result_compare.py \
    --input audit=/pfad/audit-s5.json \
    --input cadence=/pfad/cadence-s5.json \
    --input coverage=/pfad/coverage-s5.json \
    --input verdicts=/pfad/verdicts-s5.json --out /pfad/compare-s5.json
```

Alle Werkzeuge sind read-only und schreiben nur JSON. Exit-Codes:
`0` ohne Befund, `3` Divergenz, `4` unvollständig/unmessbar, `5` ungültig
(inkl. simuliert), `6` Konflikt, `2` Bedienfehler.

---

## 5. Entscheidungsregeln

Nach `audit` + `coverage` + `cadence` (Reihenfolge = Beweiskraft):

| # | Beobachtung | Klasse | Nächster Schritt |
|---|---|---|---|
| D1 | `audit.verdict != COMPLETE` | **keine Aussage** | Bundle reparieren; nichts interpretieren |
| D2 | aligniertes Dump-Paar, `action_state_divergence=false`, `entity_state_divergence=true` am ersten divergenten Tick | **Simulationsklasse** (H4/H3) | Float-Provenienz prüfen (R2), dann Physik-Diff der Entity-Felder |
| D3 | `coverage.verdict = CHECKSUM_VISIBLE_DIVERGENCE` und `CONSISTENT_PRECEDES` | **Actionklasse** (H2) | Feld aus der Coverage-Tabelle benennen; BotDriver-Komposition dieses Feldes prüfen |
| D4 | `coverage… = DIVERGENCE_OUTSIDE_CHECKSUM_SCOPE` | **nicht Actionklasse** | Dump-Pfad (D2) verfolgen; die Action-Differenz ist irrelevant |
| D5 | `coverage… = INCONSISTENT_TOO_LATE` | **Widerspruch** | zuerst R4 (Tick-Herkunft) prüfen; nicht als Befund zitieren |
| D6 | `cadence.verdict = CADENCE_DIVERGENCE` und `coverage = NO_ACTION_DIVERGENCE` | **Kadenklasse** (H1/H7) | Fenster gegen SYNCBAD-Fenster prüfen (**nur** mit R6-Uhr) |
| D7 | `cadence = CADENCE_OK` und `coverage = NO_ACTION_DIVERGENCE` und `entity_state_divergence=true` | **starke Simulationsklasse** | H1/H2/H7 `REFUTED`; Physik/FP fokussieren |
| D8 | Counter-Sprünge > 1, Kick ohne SYNCBAD | **Log-Artefakt** (H6) | PR #58-Klassifikator, Lauf wiederholen |
| D9 | unterschiedliche Hashes zwischen Läufen | **Zuordnungsfehler** | Ergebnis verwerfen |

Zwei unabhängige Läufe (S5+S6) müssen **dieselbe** Klasse ergeben. Weichen sie
ab, gilt das Ergebnis als `CONFLICT` und wird nicht als Befund veröffentlicht.

---

## 6. Abnahmekriterien für eine belastbare Diagnose

Ein Ergebnis ist nur dann zitierfähig, wenn **alle** Punkte erfüllt sind:

1. `audit.verdict = COMPLETE`, `manifest.simulated = false`, kein Fixture-Marker.
2. `ser_iKickOnSyncBad = 10` (unverändert), `cli_bDumpSync = 1` — im Snapshot,
   nicht in einer Ini.
3. Hash-Inventar vollständig; Client/Server-Vanilla-Komponenten identisch.
4. Mindestens **ein** aligniertes Dump-Paar mit `Tick` **vor** und **nach** dem
   ersten divergenten Tick.
5. `layout_107.json` mit `status = VERIFIED_107` (sonst bleibt jedes
   Action-Ergebnis `LAYOUT_UNVERIFIED`).
6. Zwei unabhängige Läufe mit demselben Kandidaten-Hash, gleiche Klasse.
7. S3 zeigt, dass die Instrumentierung selbst kein SYNCBAD erzeugt.
8. Rohlogs/Dumps/Binaries bleiben privat; im Repository stehen nur
   JSON-Ergebnisse ohne personenbezogene oder urheberrechtlich geschützte Daten.

Punkt 5 ist der häufigste Stolperstein: **ohne verifizierte Offsets ist H2 nicht
abschließbar.** Bis dahin bleibt der Output ehrlich `LAYOUT_UNVERIFIED`.

---

## 7. Sicherheit und Grenzen

* Keine produktiven Hetzner-Prozesse, keine Serverneustarts, keine DLL-Änderung
  an der qualifizierten Installation.
* Kein `ser_iKickOnSyncBad`-Tuning, keine „stabilen“ Läufe durch Abschalten der
  Prüfung.
* Kein `Test-RetailJoin.ps1` ohne eigenständigen Restore (es stellt die
  gesicherte `GameMP.dll` nicht automatisch zurück).
* Frida/Debugger nur nach Baseline (S0–S2), deklariert im Manifest, minimale
  passive Hooks; RVA des Handlers statisch `0x601A2D10 − 0x600C0000 = 0x000E2D10`,
  Modulbasis nach ASLR neu bestimmen.
* Offline-Modelle sind **keine** native Abnahme. Fixtures tragen einen Marker
  und werden vom Audit abgelehnt.
* Keine Übertragung von Ergebnissen auf andere Kandidaten-Hashes.

---

## 8. Offene Fragen, die C2 statisch/technisch beantworten muss

| # | Frage | Warum blockierend |
|---|---|---|
| Q1 | Byte-Offsets der beiden 4-Byte-Checksum-Aufrufe im 1.07-`CPlayerAction` | A1; ohne sie ist H2 nicht prüfbar |
| Q2 | Ist `CPlayerSource::SetAction` in 1.07 wirklich Single-Slot? | A2; trägt H1/H7 |
| Q3 | Ruft `CTimer` die Handler bei verzögertem WinMM-Callback mehrfach (Catch-up) oder gar nicht? | bestimmt, ob Kadenzverlust „Wiederholung“ oder „Versatz“ bedeutet |
| Q4 | Schreibt `cli_bDumpSyncEachTick` tatsächlich pro Tick oder nur pro Sync-Check? | Dump-Dichte und Timingkosten |
| Q5 | Welche Felder umfasst `CSessionState::ChecksumForSync` in 1.07 (Reihenfolge, Spielerzahl, Pause)? | entscheidet, ob `session`-Felder Dumps brauchen |
| Q6 | Wird der Sync-Check-Intervall (1,0 s laut 1.10-Referenz) in 1.07 durch eine andere Konfiguration bestimmt? | bestimmt, wie viele Ticks zwischen zwei Prüfungen liegen |

Antworten gehören mit Adresse, Datei-Hash und Gegenprüfung in den jeweiligen
Bericht (AGENTS.md: Ghidra-Erkenntnisse immer mit Funktionsadresse belegen).

---

## 9. Was diesen Plan widerlegen würde

* S3 erzeugt selbst SYNCBAD → Instrumentierung ist nicht neutral; Plan muss auf
  rein passive Beobachtung reduziert werden.
* Dumps lassen sich nicht pro Tick alignieren (Q4) → Diskriminierung über
  Dump-Felder scheitert; Alternative: nur Action-Byte-Bilder + Telemetrie, dann
  bleibt H4 `NOT_TESTED`.
* Die Checksum umfasst in 1.07 mehr als 8 Action-Bytes (Q1/Q5) → A1 wird
  verworfen, die Scope-Tabelle muss neu berechnet werden.
* Kein Kandidat erzeugt innerhalb von 30 min einen Fehler → der Plan braucht
  eine längere Stufe oder einen provozierten Fehlerfall (z. B. bewusst
  abweichende Map-Daten) — **nicht** durch Kick-Abschaltung.

---

## 10. Übergabe zurück (Was C2 liefern soll)

1. `audit-<stufe>.json`, `cadence-<stufe>.json`, `coverage-<stufe>.json`,
   `verdicts-<stufe>.json`, `compare-<stufe>.json` je instrumentierter Stufe.
2. `layout_107.json` (mit `status`), `manifest.json` je Lauf.
3. Kurzbericht: Stufe, Kandidaten-Hash, Laufzeit, `first_bad_tick`,
   Klassifikation nach §5, Abweichungen, offene Punkte.
4. **Keine** Rohlogs/Dumps/Binaries im Repository; nur die JSON-Ausgaben und
   der Bericht.
5. Explizite Kennzeichnung `NOT_TESTED` für alles, was nicht gelaufen ist.

Damit ist der Anschluss an PR #58 eindeutig: PR #58 sagt, *was* in den Logs
steht; dieser Plan und die Werkzeuge sagen, *welche Ursache damit vereinbar ist
und welche nicht*.
