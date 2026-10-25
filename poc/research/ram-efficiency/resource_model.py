#!/usr/bin/env python3
"""resource_model.py - RAM/CPU model for 1/4/8/16 TSE bots per architecture.

The model is **parameterised exclusively by measured Hetzner anchors** stored
in ``measurements.json`` (each anchor cites its report). Every projected row
is tagged with an evidence level so nobody can read a projection as a
measurement:

* ``MEASURED_HETZNER``  - the value is a real measured anchor, echoed back.
* ``DERIVED``           - arithmetic on measured anchors (formula shown).
* ``PROJECTED``         - linear extrapolation outside the measured range.
* ``PROJECTED_UNVERIFIED_OPTIMIZATION`` - assumes an optimization that has
  never been run (architecture D); the savings band is an assumption.

Architectures
-------------
* **A**  - status quo: shared 4-local-player clients (ceil(N/4) processes),
  static roster, no per-bot join/leave.
* **B**  - PR #47: one full Wine client per bot, full independence.
* **C**  - hybrid proposal: sessions multiplexed onto 4-slot clients
  (see slotplan.py). Process counts equal A; independence depends on the
  unverified engine capabilities E1/E2 described in the research doc.
* **D**  - B plus page-sharing/footprint optimizations (KSM, smaller
  llvmpipe surfaces, texture downsizing, zram). Pure assumption band.

Nothing in this file was measured in the LMArena sandbox; run the harness on
the real Wine host to replace projections with measurements.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MEASUREMENTS = HERE / "measurements.json"

MEASURED = "MEASURED_HETZNER"
DERIVED = "DERIVED"
PROJECTED = "PROJECTED"
PROJECTED_OPT = "PROJECTED_UNVERIFIED_OPTIMIZATION"

# Stated planning assumptions (not measurements):
OS_AND_MONITOR_RESERVE_MIB = 700   # OS, sshd, monitoring, page cache minimum
SLOTS_PER_CLIENT = 4
SERVER_SLOTS = 16                  # retail session player limit


def load_measurements(path: Path = DEFAULT_MEASUREMENTS) -> dict:
    return json.loads(path.read_text())


def _row(arch, bots, processes, ram_mib, ram_ev, ram_formula,
         cpu_pct, cpu_ev, cpu_formula, independence, notes=""):
    return {
        "architecture": arch,
        "bots": bots,
        "game_client_processes": processes,
        "ram_mib": None if ram_mib is None else round(ram_mib, 1),
        "ram_evidence": ram_ev,
        "ram_formula": ram_formula,
        "cpu_core_percent": None if cpu_pct is None else round(cpu_pct, 1),
        "cpu_evidence": cpu_ev,
        "cpu_formula": cpu_formula,
        "independent_join_leave": independence,
        "notes": notes,
    }


def project_arch_a(m: dict, bots: int) -> dict:
    a = m["arch_a_shared_clients"]
    clients = math.ceil(bots / SLOTS_PER_CLIENT)
    server_rss = a["server_rss_kib"] / 1024.0
    client_rss = sum(a["client_rss_kib"]) / len(a["client_rss_kib"]) / 1024.0
    ram = server_rss + clients * client_rss
    # CPU: measured whole-test cgroup for 8 bots / 2 clients; split into
    # server (measured), per-client (measured mean) and residual wine/xvfb.
    client_cpu = sum(a["client_cpu_core_percent"]) / len(a["client_cpu_core_percent"])
    residual = a["cgroup_cpu_core_percent_600s"] - a["server_cpu_core_percent"] - 2 * client_cpu
    # server CPU grows with bots: 8.423% @1 bot, 10.255% @4, 14.686% @8
    # (docs/reports/2026-10-21-hetzner-capacity.md) -> ~0.78%/bot + 8.2 base.
    server_cpu = 8.2 + 0.78 * bots
    cpu = server_cpu + clients * client_cpu + residual * max(1, clients) / 2.0
    if bots == 8:
        ram_ev = MEASURED
        cpu_ev = MEASURED
        cpu = a["cgroup_cpu_core_percent_600s"]
        ram_formula = "sum of measured RSS: server 50.2 + 2 clients ~184.2 (RSS, not PSS)"
        cpu_formula = "measured whole test cgroup, 600 s public smoke"
    else:
        ram_ev = DERIVED if clients <= 2 else PROJECTED
        cpu_ev = DERIVED if clients <= 2 else PROJECTED
        ram_formula = f"50.2 + {clients} x 184.2 (RSS basis measured at 2 clients)"
        cpu_formula = f"(8.2+0.78xN) + {clients} x 23.3 + residual; anchors at 1/4/8 bots"
    notes = "roster fixed at process start; join/leave only per whole 4-bot client"
    if bots > SERVER_SLOTS - 2:
        notes += f"; >= {bots} bots needs a second 16-slot server instance and leaves <2 human seats"
    return _row("A", bots, clients, ram, ram_ev, ram_formula, cpu, cpu_ev,
                cpu_formula, "none (whole client only)", notes)


def project_arch_b(m: dict, bots: int) -> dict:
    b = m["arch_b_individual_clients"]
    d = m["derived"]
    base = d["arch_b_base_overhead_mib"]
    marginal = d["arch_b_marginal_client_mib"]
    ram = base + marginal * bots
    if bots == 1:
        ram, ram_ev = b["one_client_cgroup_peak_mib"], MEASURED
        ram_formula = "measured 90 s boundary run cgroup peak"
    elif bots == 4:
        ram, ram_ev = b["four_clients_cgroup_peak_mib"], MEASURED
        ram_formula = "measured 360 s four-client run cgroup peak"
    else:
        ram_ev = PROJECTED
        ram_formula = f"{base} + {marginal} x N (linear fit of 1/4-client peaks; redstation 7-8 client peak 1725.9 is ~12% below fit)"
    # CPU anchors: 51.5% @1 (short, join churn), 72.5% @4.
    cpu_base, cpu_marginal = 44.5, 7.0
    cpu = cpu_base + cpu_marginal * bots
    if bots == 1:
        cpu, cpu_ev = b["one_client_cgroup_cpu_core_percent"], MEASURED
        cpu_formula = "measured boundary run (includes join/leave churn)"
    elif bots == 4:
        cpu, cpu_ev = b["four_clients_cgroup_cpu_core_percent"], MEASURED
        cpu_formula = "measured four-client run"
    else:
        cpu_ev = PROJECTED
        cpu_formula = "44.5 + 7.0 x N (fit of short-run anchors; wide uncertainty)"
    return _row("B", bots, bots, ram, ram_ev, ram_formula, cpu, cpu_ev, cpu_formula,
                "full (one process per bot)",
                "includes private server/Xvfb/wineserver in the cgroup; "
                "8-client runs on the 4 GB host were BLOCKED/aborted (reserve gate, drain timeout)")


def project_arch_c(m: dict, bots: int) -> dict:
    row = project_arch_a(m, bots)
    row["architecture"] = "C"
    row["independent_join_leave"] = (
        "per-bot (claimed): dynamic-slot variant gated on unverified E1/E2; "
        "roster-restart variant proven primitives only, join latency = batch window"
    )
    row["ram_evidence"] = DERIVED if row["ram_evidence"] == MEASURED else row["ram_evidence"]
    row["cpu_evidence"] = DERIVED if row["cpu_evidence"] == MEASURED else row["cpu_evidence"]
    row["notes"] = ("process cost identical to A by construction (same client count); "
                    "roster-restart adds transient +1 client (~190-210 MiB) during a swap window; "
                    "see slotplan.py and the architecture comparison doc")
    return row


def project_arch_d(m: dict, bots: int) -> dict:
    d = m["derived"]
    base = d["arch_b_base_overhead_mib"]
    marginal = d["arch_b_marginal_client_mib"]
    # Assumption band: 15-40% of the marginal client becomes shareable or
    # avoidable (KSM on wine/game anon pages, 16-bpp 320x240 surfaces,
    # texture downsizing, trimmed wine services). Never measured.
    lo = base + marginal * (1 - 0.40) * bots
    hi = base + marginal * (1 - 0.15) * bots
    ram = (lo + hi) / 2
    return _row(
        "D", bots, bots, ram, PROJECTED_OPT,
        f"B fit with 15-40% marginal reduction assumption -> {lo:.0f}..{hi:.0f} MiB",
        None, PROJECTED_OPT,
        "no CPU anchor; KSM adds ksmd CPU cost that must be measured",
        "full (one process per bot)",
        "every optimization in this row is UNVERIFIED; run the harness phases K1-K3 first")


def fit_assessment(ram_mib, host_total=None, coexist_public_mib=0.0):
    host_total = host_total or 3819
    budget = host_total - OS_AND_MONITOR_RESERVE_MIB - coexist_public_mib
    if ram_mib is None:
        return "unknown"
    if ram_mib <= budget * 0.8:
        return "fits (<80% of budget {:.0f} MiB)".format(budget)
    if ram_mib <= budget:
        return "tight (80-100% of budget {:.0f} MiB)".format(budget)
    return "exceeds budget {:.0f} MiB".format(budget)


def build_model(m: dict, bot_counts=(1, 4, 8, 16), coexist_public=False):
    coexist = m["arch_a_shared_clients"]["public_cgroup_ram_snapshot_mib"] if coexist_public else 0.0
    rows = []
    for n in bot_counts:
        for fn in (project_arch_a, project_arch_b, project_arch_c, project_arch_d):
            row = fn(m, n)
            row["host_fit"] = fit_assessment(row["ram_mib"], m["host"]["total_mib"], coexist)
            rows.append(row)
    return {
        "host": m["host"],
        "assumptions": {
            "os_and_monitor_reserve_mib": OS_AND_MONITOR_RESERVE_MIB,
            "coexist_public_fleet_mib": coexist,
            "slots_per_client": SLOTS_PER_CLIENT,
            "server_slots": SERVER_SLOTS,
        },
        "rows": rows,
        "disclaimer": "PROJECTED rows are linear extrapolations, not capacity clearances; "
                      "no runtime benchmark was executed in the LMArena sandbox.",
    }


def to_markdown(model: dict) -> str:
    lines = [
        "| Arch | Bots | Clients | RAM MiB | RAM evidence | CPU %core | CPU evidence | Host fit | Independent join/leave |",
        "|---|---:|---:|---:|---|---:|---|---|---|",
    ]
    for r in model["rows"]:
        lines.append(
            "| {architecture} | {bots} | {game_client_processes} | {ram} | {rev} | {cpu} | {cev} | {fit} | {ind} |".format(
                architecture=r["architecture"], bots=r["bots"],
                game_client_processes=r["game_client_processes"],
                ram="n/a" if r["ram_mib"] is None else r["ram_mib"],
                rev=r["ram_evidence"],
                cpu="n/a" if r["cpu_core_percent"] is None else r["cpu_core_percent"],
                cev=r["cpu_evidence"], fit=r["host_fit"],
                ind=r["independent_join_leave"].split(";")[0].split(":")[0],
            ))
    lines.append("")
    lines.append(model["disclaimer"])
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--measurements", default=str(DEFAULT_MEASUREMENTS))
    p.add_argument("--bots", default="1,4,8,16", help="comma list of bot counts")
    p.add_argument("--coexist-public", action="store_true",
                   help="subtract the measured public eight-bot fleet cgroup from the budget")
    p.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = p.parse_args(argv)
    m = load_measurements(Path(args.measurements))
    counts = tuple(int(x) for x in args.bots.split(","))
    model = build_model(m, counts, coexist_public=args.coexist_public)
    if args.format == "json":
        print(json.dumps(model, indent=2))
    else:
        print(to_markdown(model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
