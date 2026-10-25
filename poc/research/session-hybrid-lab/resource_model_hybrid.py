#!/usr/bin/env python3
"""
resource_model_hybrid.py - RAM/CPU-Ressourcenmodell 1/4/8/16 TSE-Bots.

Erweitert das Architekturmodell von PR #56 (Architekturen A, B, C, D) um die
Hybrid-Architektur C1 (ROSTER_RESTART, Viererclient-Multiplexing) und bepreist
die kurzzeitigen Zusatzkosten von Roster-Restarts.

Alle Zahlen stammen aus zitierten Hetzner-/PR-Ankern (measurements.json).
Projektionszeilen sind explizit gekennzeichnet und KEINE Kapazitaetsfreigabe.
In der LMArena-Sandbox wurde kein Live-Wine-Benchmark ausgeführt.

Evidenzklassen:
  [T] MEASURED_HETZNER   reale Hetzner-Messung, Quelle zitiert
  [O] offline getestet   (Fixture, dieser Sandbox; Session-Scheduler)
  [D] DERIVED            Rechenoperation auf gemessenen Ankern
  [P] PROJECTED          lineare Extrapolation ausserhalb des Messbereichs
  [A] Architekturvorschlag
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
DEFAULT_MEASUREMENTS = HERE / "measurements.json"

MEASURED = "MEASURED_HETZNER"
DERIVED = "DERIVED"
PROJECTED = "PROJECTED"

# Planungsannahmen (keine Messungen):
OS_AND_MONITOR_RESERVE_MIB = 700
SLOTS_PER_CLIENT = 4
SERVER_SLOTS = 16  # Retail-Session-Spielerlimit

# C1-spezifisch: ein Roster-Restart stoppt den Client und startet ihn neu;
# konservativ wird ein kurzzeitiger +1-Client pro betroffenem Restart-Fenster
# kalkuliert (stop vor start). Der Faktor gilt pro gleichzeitig neuem Roster.
C1_TRANSIENT_EXTRA_CLIENTS_PER_RESTART = 1
C1_CLIENT_START_S = 8.0   # modellierter Viererclient-Start/Connect (ohne Wine)
C1_BATCH_WINDOW_S = 20.0


def load_measurements(path: Path = DEFAULT_MEASUREMENTS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    """Architektur A: shared 4-Slot-Clients, statischer Roster.

    Prozessanzahl = ceil(bots/4). Keine pro-Bot Join/Leave-Granularitaet.
    """
    a = m["arch_a_shared_clients"]
    clients = math.ceil(bots / SLOTS_PER_CLIENT)
    server_rss = a["server_rss_kib"] / 1024.0
    client_rss = sum(a["client_rss_kib"]) / len(a["client_rss_kib"]) / 1024.0
    ram = server_rss + clients * client_rss
    client_cpu = sum(a["client_cpu_core_percent"]) / len(a["client_cpu_core_percent"])
    residual = (a["cgroup_cpu_core_percent_600s"]
                - a["server_cpu_core_percent"] - 2 * client_cpu)
    server_cpu = 8.2 + 0.78 * bots
    cpu = server_cpu + clients * client_cpu + residual * max(1, clients) / 2.0
    if bots == 8:
        ram_ev = MEASURED
        cpu_ev = MEASURED
        cpu = a["cgroup_cpu_core_percent_600s"]
        ram_formula = ("gemessen: Server 50.2 + 2 Clients ~184.2 MiB (RSS, nicht PSS)")
        cpu_formula = "gemessene Test-cgroup, 600-s-oeffentlicher Smoke"
    else:
        ram_ev = DERIVED if clients <= 2 else PROJECTED
        cpu_ev = DERIVED if clients <= 2 else PROJECTED
        ram_formula = f"50.2 + {clients} x 184.2 (RSS-Basis gemessen bei 2 Clients)"
        cpu_formula = f"(8.2+0.78xN) + {clients} x 23.3 + residual; Anker bei 1/4/8 Bots"
    notes = "Roster fest bei Prozessstart; Join/Leave nur pro wholem 4-Bot-Client"
    if bots > SERVER_SLOTS - 2:
        notes += f"; >= {bots} Bots brauchen zweite 16-Slot-Serverinstanz"
    return _row("A", bots, clients, ram, ram_ev, ram_formula,
                cpu, cpu_ev, cpu_formula, "nein (nur ganzer Client)",
                notes)


def project_arch_b(m: dict, bots: int) -> dict:
    """Architektur B: ein voller Retail-Client pro Bot (PR #47)."""
    b = m["arch_b_individual_clients"]
    d = m["derived"]
    marginal = d["arch_b_marginal_client_mib"]
    base = d["arch_b_base_overhead_mib"]
    ram = base + marginal * bots
    if bots == 1:
        ram_ev = MEASURED
        cpu_ev = MEASURED
        cpu = b["one_client_cgroup_cpu_core_percent"]
        ram_formula = "gemessener Einzelclient cgroup-Peak"
        cpu_formula = "gemessener Boundary-Lauf (enthält Join/Leave-Churn)"
    elif bots == 4:
        ram_ev = MEASURED
        cpu_ev = MEASURED
        cpu = b["four_clients_cgroup_cpu_core_percent"]
        ram_formula = "gemessener Vier-Client cgroup-Peak"
        cpu_formula = "gemessener Vier-Client-Lauf"
    else:
        ram_ev = PROJECTED
        cpu_ev = PROJECTED
        cpu = None
        ram_formula = f"355.1 + 200.7 x N (lineares Fit der kurzen Anker)"
        cpu_formula = "44.5 + 7.0 x N (Fit kurzer Laufzeiten; grosse Unsicherheit)"
    return _row("B", bots, bots, ram, ram_ev, ram_formula,
                cpu, cpu_ev, cpu_formula, "ja (ein Prozess pro Bot)",
                "enthält privaten Server/Xvfb/wineserver in der cgroup; "
                "8-Client-Läufe auf dem 4-GB-Host blockiert (Reserve-Gate, "
                "Drain-Timeout)")


def project_arch_c1(m: dict, bots: int, simultaneous_restarts: int = 1) -> dict:
    """Architektur C1 (Hybrid, ROSTER_RESTART): Sessions multiplexen auf
    shared 4-Slot-Clients wie A; pro Restart-Fenster ein kurzzeitiger +1
    Client (stop vor start). Keine neue Engine-Faehigkeit erforderlich.

    Die Prozessanzahl entspricht A; Unabhängigkeit der Sessions kommt durch
    persistente Identitaet + Reconnect, nicht durch separate Prozesse.
    """
    row_a = project_arch_a(m, bots)
    clients = row_a["game_client_processes"]
    # Ein transienter +1-Client fällt nur an, wenn ein bereits bevolkter
    # Client neu gestartet wird (mindestens 2 Clients vorhanden).
    transient = min(simultaneous_restarts, max(0, clients - 1))
    peak_total = clients + C1_TRANSIENT_EXTRA_CLIENTS_PER_RESTART * transient
    ram = m["derived"]["server_rss_mib"] + peak_total * m["derived"]["client_rss_mib"]
    return _row(
        "C1", bots, clients, ram, DERIVED,
        f"50.2 + {peak_total} x 184.2 (A-Prozesszahl + {simultaneous_restarts}x transienter "
        "Client waehrend Roster-Restart-Fenster; RSS-Basis)",
        row_a["cpu_core_percent"], row_a["cpu_evidence"],
        row_a["cpu_formula"] + "; Restart-Fenster addieren keine dauerhaften Prozesse",
        "pro-Bot (Latenz = Batch-Fenster + Clientstart; Co-Residenten kurz unterbrochen)",
        ("ROSTER_RESTART: provenierte Primitive nur; "
         "Join-Latenz <= Batch-Fenster + Clientstart; "
         f"{simultaneous_restarts}x transienter +1-Client waehrend Swap-Fenster"))


def fit_assessment(ram_mib: Optional[float], host_total: int = 3819,
                   coexist_public_mib: float = 0.0) -> str:
    if ram_mib is None:
        return "unknown"
    budget = host_total - OS_AND_MONITOR_RESERVE_MIB - coexist_public_mib
    if ram_mib <= budget * 0.8:
        return f"fits (<80% von {budget:.0f} MiB Budget)"
    if ram_mib <= budget:
        return f"tight (80-100% von {budget:.0f} MiB Budget)"
    return f"exceeds {budget:.0f} MiB Budget"


def build_model(m: dict, bot_counts=(1, 4, 8, 16),
                coexist_public: bool = False,
                simultaneous_restarts: int = 1) -> dict:
    coexist = m["arch_a_shared_clients"]["public_cgroup_ram_snapshot_mib"] \
        if coexist_public else 0.0
    rows = []
    for n in bot_counts:
        rows.append(project_arch_a(m, n))
        rows.append(project_arch_b(m, n))
        rows.append(project_arch_c1(m, n, simultaneous_restarts))
    for r in rows:
        r["host_fit"] = fit_assessment(r["ram_mib"], m["host"]["total_mib"], coexist)
    return {
        "host": m["host"],
        "assumptions": {
            "os_and_monitor_reserve_mib": OS_AND_MONITOR_RESERVE_MIB,
            "coexist_public_fleet_mib": coexist,
            "slots_per_client": SLOTS_PER_CLIENT,
            "server_slots": SERVER_SLOTS,
            "c1_transient_clients_per_restart": C1_TRANSIENT_EXTRA_CLIENTS_PER_RESTART,
            "c1_simultaneous_restarts": simultaneous_restarts,
        },
        "rows": rows,
        "evidence_classes": {
            "T": "MEASURED_HETZNER - reale Hetzner-/PR-Messung, zitiert",
            "D": "DERIVED - Rechenoperation auf gemessenen Ankern",
            "P": "PROJECTED - lineare Extrapolation, keine Messung",
            "A": "Architekturvorschlag, kein Laufzeitnachweis",
        },
        "disclaimer": ("PROJECTED-Zeilen sind lineare Extrapolationen, keine "
                       "Kapazitaetsfreigaben. Kein Live-Wine-Benchmark in der "
                       "LMArena-Sandbox. Ressourcenmodelle sind eindeutig von "
                       "echten Wine-Messungen unterschieden (Evidenzklasse)."),
    }


def to_markdown(model: dict) -> str:
    lines = [
        "| Arch | Bots | Client-Prozesse | RAM MiB | RAM-Evidenz | CPU %Kern | CPU-Evidenz | Host-Fit | Pro-Bot Join/Leave |",
        "|---|---:|---:|---:|---|---:|---|---|---|",
    ]
    for r in model["rows"]:
        lines.append(
            "| {architecture} | {bots} | {processes} | {ram} | {rev} | {cpu} | {cev} | {fit} | {ind} |".format(
                architecture=r["architecture"], bots=r["bots"],
                processes=r["game_client_processes"],
                ram="n/a" if r["ram_mib"] is None else r["ram_mib"],
                rev=r["ram_evidence"],
                cpu="n/a" if r["cpu_core_percent"] is None else r["cpu_core_percent"],
                cev=r["cpu_evidence"], fit=r["host_fit"],
                ind=r["independent_join_leave"].split(";")[0]))
    lines.append("")
    lines.append(model["disclaimer"])
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="RAM/CPU-Ressourcenmodell 1/4/8/16 TSE-Bots (Architekturen A/B/C1).")
    p.add_argument("--measurements", default=str(DEFAULT_MEASUREMENTS))
    p.add_argument("--bots", default="1,4,8,16",
                   help="Komma-getrennte Bot-Anzahlen")
    p.add_argument("--coexist-public", action="store_true",
                   help="oeffentliche Acht-Bot-Flotte vom Budget abziehen")
    p.add_argument("--c1-restarts", type=int, default=1,
                   help="gleichzeitige C1-Roster-Restarts für transienten +1-Client")
    p.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = p.parse_args(argv)
    m = load_measurements(Path(args.measurements))
    counts = tuple(int(x) for x in args.bots.split(","))
    model = build_model(m, counts, coexist_public=args.coexist_public,
                        simultaneous_restarts=args.c1_restarts)
    if args.format == "json":
        print(json.dumps(model, indent=2))
    else:
        print(to_markdown(model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
