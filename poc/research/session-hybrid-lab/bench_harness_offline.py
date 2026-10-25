#!/usr/bin/env python3
"""
bench_harness_offline.py - Offline-Harness für das Session-Hybrid-Lab.

Keine Live-Benchmarks, keine Wine-/Retail-Prozesse, keine echten Messwerte.
Der Harness fährt simulierte Szenarien (4/8/16 Bots, geordnete + zufällige
Joins, Crash/Cooldown/Rejoin, Server-Neustart, Human-Slot-Reserve) durch den
Hybrid-Scheduler und den Ressourcen-Rechner und schreibt ein reproduzierbares
Protokoll mit Provenienz.

Designregeln (übernommen von poc/research/ram-efficiency/bench_harness.sh):
* Read-only: schreibt nur --out / --ledger, signalisiert nie Prozesse.
* Simulate-Modus ist der einzige Modus; ein realer Wine-Lauf ist hier nicht
  vorgesehen und würde ohne autorisierte Isolierung abgelehnt.
* Jede Ausführung erzeugt Provenienz (Host, UTC, Modus, Parameter, Seed).
* Ergebnisse ohne Provenienz sind ungültig.

Usage:
    python3 bench_harness_offline.py --scenario 8b_ordered --out result.json
"""

from __future__ import annotations

import argparse
import json
import platform
import time
import uuid
from pathlib import Path

import session_hybrid_lab as sh
import trace_simulator as ts
import resource_model_hybrid as rm


def _provenance(mode: str, scenario: str, seed: int, config: dict) -> dict:
    return {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": platform.node(),
        "python": platform.python_version(),
        "mode": mode,
        "scenario": scenario,
        "seed": seed,
        "wine_used": False,
        "retail_binary_used": False,
        "evidence": sh.O,
        "run_id": uuid.uuid4().hex,
    }


def run_scenario(name: str, seed: int, config: dict) -> dict:
    runner = sh.SimRunner(config, mode=sh.ROSTER_RESTART, seed_offset=seed)
    if name == "4b_ordered":
        events = runner.ordered_join_trace(
            [f"player-{i:02d}" for i in range(1, 5)], interval_s=60.0)
        end_time = 700.0
    elif name == "8b_ordered":
        events = runner.ordered_join_trace(
            [f"player-{i:02d}" for i in range(1, 9)], interval_s=60.0)
        end_time = 1200.0
    elif name == "16b_ordered":
        events = runner.ordered_join_trace(
            [f"player-{i:02d}" for i in range(1, 17)], interval_s=30.0)
        end_time = 1200.0
    elif name == "8b_random":
        events = runner.random_trace(1800.0, join_rate_per_hour=24.0)
        end_time = 1800.0
    elif name == "crash_cooldown_rejoin":
        events = runner.crash_cooldown_rejoin_trace(
            "player-01", join_at=10.0, crash_at=40.0, rejoin_at=200.0)
        end_time = 400.0
    elif name == "server_restart":
        events = runner.server_restart_trace(
            [f"player-{i:02d}" for i in range(1, 5)], join_interval=30.0,
            restart_at=300.0, rejoin_delay=60.0)
        end_time = 900.0
    else:
        raise ValueError(f"unbekanntes Szenario: {name}")
    result = runner.run_trace(events, end_time=end_time)
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Offline-Harness für das Session-Hybrid-Lab (simuliert).")
    p.add_argument("--scenario", required=True,
                   choices=["4b_ordered", "8b_ordered", "16b_ordered",
                            "8b_random", "crash_cooldown_rejoin",
                            "server_restart"])
    p.add_argument("--seed", type=int, default=20261025)
    p.add_argument("--max-bots", type=int, default=8)
    p.add_argument("--min-bots", type=int, default=0)
    p.add_argument("--reserved-human-slots", type=int, default=2)
    p.add_argument("--max-clients", type=int, default=4)
    p.add_argument("--batch-window", type=float, default=20.0)
    p.add_argument("--out", required=True, help="Ergebnis-JSON")
    p.add_argument("--ledger", default=None, help="Detailliertes Ledger-JSON")
    args = p.parse_args(argv)

    config = dict(sh.DEFAULT_CONFIG)
    config.update(seed=args.seed, max_bots=args.max_bots,
                  min_bots=args.min_bots,
                  reserved_human_slots=args.reserved_human_slots,
                  max_clients=args.max_clients,
                  batch_window_s=args.batch_window,
                  pool_id="bench-harness-v1",
                  identities=[
                      {"id": f"player-{i:02d}", "nickname": f"Bot{i:02d}",
                       "profile": i % 8, "regular_weight": 3 if i < 4 else 1}
                      for i in range(1, 33)])

    result = run_scenario(args.scenario, args.seed, config)
    sched = result.scheduler.summary()

    # Ressourcenmodell für die Spitzen-Client-Anzahl des Szenarios (C1)
    m = rm.load_measurements()
    bots_requested = {
        "4b_ordered": 4, "8b_ordered": 8, "16b_ordered": 16,
        "8b_random": args.max_bots, "crash_cooldown_rejoin": 1,
        "server_restart": 4,
    }.get(args.scenario, args.max_bots)
    model_8 = rm.build_model(m, (bots_requested,),
                             simultaneous_restarts=sched["client_restarts"] or 1)

    out = {
        "provenance": _provenance("simulate", args.scenario, args.seed, config),
        "scenario": args.scenario,
        "config": {k: v for k, v in result.config.items() if k != "identities"},
        "scheduler": sched,
        "resource_model_c1": model_8["rows"],
        "sessions": {k: v.as_dict() for k, v in result.sessions.items()},
        "ghost_events": result.ghost_events,
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    if args.ledger:
        runner2 = sh.SimRunner(config, mode=sh.ROSTER_RESTART,
                               seed_offset=args.seed)
        # Führe noch einmal für den Ledger (deterministisch gleich)
        events = None
        # Re-laufen ist unnötig; Ledger aus dem vorhandenen Result bauen.
        runner2.save_ledger(args.ledger, result)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
