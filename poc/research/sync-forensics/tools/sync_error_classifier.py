#!/usr/bin/env python3
"""Fehlerklassifizierung: weist jedem SYNCBAD-Muster eine genau definierte
Diagnose-Klasse zu, basierend auf dem replizierbaren Server-Handler-Verhalten
(Retail 1.07: Counter +1 pro abweichender Pruefung, Reset auf 0 bei SYNCOK,
KICK bei >= 10 - docs/reports/2026-10-17-retail107-sync-check-investigation.md).

Klassen (deterministisch, synthetische Logs reproduzierbar):
  E1_Sustained_CRC_Divergence  : Counter monoton bis KICK (10 aufeinanderfolgende
                                  abweichende Pruefungen -> Root-Cause-Kandidat:
                                   permanente Client/Server-Simulations-Differenz)
  E2_Transient_Divergence      : Counter steigt, kehrt aber per SYNCOK zurück
                                  (Schwingungen / Timing-bedingt, kein permanenter
                                   Zustandsunterschied)
  E3_Counter_Jump              : Counter springt um >1 pro Ereignis
                                  (fehlende SYNCOK-Meldungen oder Log-Fragmentierung;
                                  Engine kann nur +1 pro Pruefung inkrementieren)
  E4_Kick_Without_Root_Events  : KICK ohne davor liegende SYNCBAD-Zeilen
                                  (unvollstaendige Logs / andere Trennursache)
  E5_Log_Only_No_Kick         : SYNCBAD-Ereignisse, aber kein KICK
                                  (Counter unter Grenzwert oder Lauf abgebrochen)
  E6_No_Sync_Events           : kein einziges SYNCBAD/SYNCOK/KICK im Log
                                  (keine Sync-Pruefung stattgefunden oder Log falsch)

Das Klassifikator-Ergebnis ist eine Log-Diagnose und NICHT eine Root-Cause-
Bestätigung.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_forensics_common import (  # noqa: E402
    parse_server_log_events, EVIDENCE_NOTE,
)

KICK_LIMIT = 10  # Retail-1.07-Grenzwert, dokumentiert und in Ghidra verifiziert.


def classify(server_log: str) -> Dict[str, object]:
    events = parse_server_log_events(server_log)
    bads = [e for e in events if e.kind == "SYNCBAD"]
    oks = [e for e in events if e.kind == "SYNCOK"]
    kicks = [e for e in events if e.kind == "KICK"]

    classes: List[Dict[str, object]] = []

    if not bads and not kicks:
        classes.append({
            "class": "E6_No_Sync_Events",
            "detail": "keine SYNCBAD/SYNCOK/KICK-Zeilen gefunden",
        })
        return {"classes": classes, "evidence_note": EVIDENCE_NOTE}

    if kicks and not bads:
        classes.append({
            "class": "E4_Kick_Without_Root_Events",
            "detail": "KICK ohne vorherige SYNCBAD-Zeilen (Log unvollständig oder"
                      " andere Trennursache)",
            "kick_lines": [k.line_no for k in kicks],
        })

    if bads and not kicks:
        classes.append({
            "class": "E5_Log_Only_No_Kick",
            "detail": "SYNCBAD ohne KICK: Counter unter Grenzwert oder"
                      " Lauf abgebrochen",
            "max_counter": max((e.count or 0) for e in bads),
        })

    # pro Client Counter-Sequenz analysieren
    by_client: Dict[str, List] = {}
    for e in bads:
        by_client.setdefault(e.client, []).append(e)

    for client, series in sorted(by_client.items()):
        counts = [e.count or 0 for e in series]
        monotonic = all(b > a for a, b in zip(counts, counts[1:]))
        jumps = [b - a for a, b in zip(counts, counts[1:]) if b - a > 1]
        peak = max(counts) if counts else 0

        if jumps:
            classes.append({
                "class": "E3_Counter_Jump",
                "client": client,
                "detail": "Counter springt um >1 pro Ereignis (fehlende SYNCOK-"
                          "Meldungen oder Log-Fragmentierung)",
                "jumps": jumps, "peak": peak,
            })
        elif monotonic and peak >= KICK_LIMIT:
            classes.append({
                "class": "E1_Sustained_CRC_Divergence",
                "client": client,
                "detail": "Counter monoton auf/über den Grenzwert: dauerhafte"
                          " CRC-Divergenz -> Root-Cause-Kandidat",
                "peak": peak,
                "first_bad_tick": series[0].tick, "last_bad_tick": series[-1].tick,
            })
        elif monotonic and peak < KICK_LIMIT:
            classes.append({
                "class": "E2_Transient_Divergence",
                "client": client,
                "detail": "monoton ansteigend, aber vor dem Grenzwert"
                          " (kurzzeitig / abzubrechend)",
                "peak": peak,
            })

    if oks:
        classes.append({
            "class": "E2_Transient_Divergence",
            "detail": "SYNCOK-Ereignisse vorhanden: Counter kann sich erholen",
            "sync_ok_count": len(oks),
        })

    return {"classes": classes, "kick_limit": KICK_LIMIT,
            "evidence_note": EVIDENCE_NOTE}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logs", nargs="+", help="Server-Log(s)")
    ap.add_argument("--out", help="Optional: JSON-Ausgabepfad")
    args = ap.parse_args()

    result: Dict[str, object] = {}
    for raw in args.logs:
        path = Path(raw)
        if not path.is_file():
            ap.error("File not found: " + str(path))
        result[str(path)] = classify(path.read_text(encoding="utf-8", errors="replace"))

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
