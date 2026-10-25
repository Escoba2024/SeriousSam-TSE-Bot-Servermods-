# Sync-Hypothesis-Validation (TSE 1.07)

Offline-Werkzeuge, die Sync-Hypothesen **falsifizierbar** machen: statt einer
weiteren Log-Auswertung liefert dieses Paket pruefbare Modelle, eine
Evidenz-Graduierung und einen maschinenpruefbaren Vertrag fuer native Laeufe.

**Stand:** 25.10.2026 · **Status:** offline, synthetische Fixtures, **keine**
Aussage ueber Retail-Stabilitaet und **keine** Root-Cause-Bestaetigung.

## Abgrenzung zu PR #58 (`poc/research/sync-forensics`)

| Ebene | Werkzeug | Frage |
|---|---|---|
| Log/Dump-Forensik | `poc/research/sync-forensics` (PR #58) | *Was steht in den Logs?* E1–E6, Korrelation, Dump-Diff |
| **Hypothesen-Validierung (hier)** | `poc/research/sync-hypothesis-validation` | *Welche Ursache waere mit welcher Beobachtung vereinbar — und welche ist schon widerlegt?* |

Dieses Paket importiert **keinen** Code aus PR #58. Es liest dessen JSON-Ergebnisse
optional (`result_compare.py --input crc_diff=...`) und schreibt in keinen fremden
Pfad. Log-Parsing existiert hier nur minimal (SYNCBAD/Kick) und ist ausdruecklich
kein Ersatz fuer die Forensic-Tools.

## Sicherheit

* Nur lesend; startet keine Prozesse, aendert keine DLL, keinen Server, kein
  Spiel-Dateisystem.
* Alle Tests laufen auf **synthetischen** Fixtures (kein echtes Log, keine
  Binaerdaten, keine Spieldaten).
* Fail-closed: fehlende Daten ergeben `INCOMPLETE` / `UNMEASURABLE` /
  `NOT_TESTED` — nie „sauber“.
* Offline-Modelle koennen **nie** `NATIVE_SUPPORTED` erzeugen; generierte
  Bundles tragen `GENERATED_FIXTURE.txt` und werden vom Audit als
  `SIMULATED_NEVER_NATIVE` abgelehnt.
* Es gibt keinen Zustand „bestaetigt“/„proven“: `root_cause_status` ist immer
  `NOT_ESTABLISHED`.

## Werkzeuge

| Werkzeug | Aufgabe | Exit-Codes |
|---|---|---|
| `tools/hypothesis_registry.py` | Hypothesen H1–H7 + Annahmen A1–A5 als gepruefte Daten | 0 gueltig / 5 ungueltig |
| `tools/cadence_model.py` | 20-Hz-Takt und Single-Slot-Action-Verlust aus `BotTelemetry.csv` | 0 OK / 3 Divergenz / 4 unmessbar |
| `tools/checksum_coverage_probe.py` | Checksum-Scope (4 Byte × 2 Aufrufe) gegen alignierte Action-Byte-Bilder | 0 keine / 3 Divergenz / 4 unvollstaendig / 5 Layout unbelegt |
| `tools/fp_determinism_probe.py` | Float-Modell-Divergenz (binary32 / x87-artig / fast-math / float64) | 0 deterministisch / 3 divergent |
| `tools/evidence_bundle_audit.py` | Instrumentierungsvertrag fuer native Laeufe; Template mit `--emit-template` | 0 COMPLETE / 4 INSUFFICIENT / 5 INVALID oder SIMULIERT |
| `tools/verdict_engine.py` | Beobachtungen → Hypothesen-Verdikte (6 Zustaende, Evidenz-Grading) | 0 aufgeloest / 4 nichts testbar / 6 Konflikt |
| `tools/result_compare.py` | Zusammenfuehrung + Konflikterkennung + Evidenz-Inventar | 0 kein Konflikt / 4 unzureichend / 6 Konflikt |
| `tools/make_synthetic_cases.py` | deterministische Fixtures inkl. Negativkontrollen | 0 |

## Tests

```bash
cd poc/research/sync-hypothesis-validation
python3 -m unittest discover -s tests -v    # 92 Tests
./run_all_tests.sh                          # Registry-Check + Tests + Smoke
```

Ergebnis am 25.10.2026 (Python 3.11.2, Linux-Sandbox): **92/92 PASS**.

## Dokumentation

* [Hauptbericht](../../../docs/research/sync-hypothesis-validation/2026-10-25-sync-hypothesis-validation-report.md)
* [Instrumentierungsanforderungen](../../../docs/research/sync-hypothesis-validation/2026-10-25-instrumentation-requirements.md)
* [Nativer Validierungsplan fuer Codex C2](../../../docs/research/sync-hypothesis-validation/2026-10-25-codex-c2-native-validation-plan.md)

## Typischer Analysepfad

```bash
# 1) native Evidenz pruefen (vor jeder Interpretation)
python3 tools/evidence_bundle_audit.py --bundle /pfad/zum/bundle \
    --out audit.json

# 2) Takt/Action-Treue
python3 tools/cadence_model.py --telemetry BotTelemetry.csv \
    --source-class telemetry --out cadence.json

# 3) Action-Bytes gegen Checksum-Scope
python3 tools/checksum_coverage_probe.py \
    --client-trace traces/client-actions.csv \
    --server-trace traces/server-actions.csv \
    --layout layout_107.json --first-bad-tick 83.4 \
    --trace-class telemetry --out coverage.json

# 4) Hypothesen auswerten
python3 tools/verdict_engine.py audit.json cadence.json coverage.json \
    --out verdicts.json

# 5) Gesamtbild inkl. Konflikten
python3 tools/result_compare.py \
    --input audit=audit.json --input cadence=cadence.json \
    --input coverage=coverage.json --input verdicts=verdicts.json \
    --out compare.json
```

`--source-class` / `--trace-class` sind bewusst standardmaessig `simulation`:
ein echter Lauf muss seine Herkunft **erklaeren**, nicht umgekehrt.
