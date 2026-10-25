#!/usr/bin/env python3
"""
trace_simulator.py - reine Join/Leave-Trace-Generatoren für das Session-Hybrid-Lab.

Erzeugt Trace-Dateien im Format des Hybrid-Schedulers:
    <t_s> <bot_id> <JOIN|LEAVE|CRASH|RESTART_SERVER|REJOIN>

Alle Generatoren sind deterministisch (ge Seeder PRNG), offline und enthalten
keine Wine-, Retail- oder Netzwerk-Logik. Sie dienen dazu, wiederholbare
Szenarien für den Hybrid-Scheduler (Architektur C1) zu erzeugen:

  * geordnete Joins (4 Bots in einer Clientgruppe, 8 Bots in zwei Gruppen)
  * zufällige Joins/Leaves (Poisson-Ankunft, Band-Sessiondauern)
  * Crash + Cooldown + Rejoin mit stabiler Identität
  * Server-Neustart-Simulation (alle PLAYING trennen, stabiler Rejoin)
  * Human-Slot-Reserve und Mindestpopulation
  * Kapazitätserschöpfung (Warteschlange bei max_clients)

Keine Zeile ist eine Live-Messung oder Retail-Aussage. [O]
"""

from __future__ import annotations

import random
from typing import Optional

JOIN = "JOIN"
LEAVE = "LEAVE"


def ordered_joins(bots: list[str], interval_s: float = 60.0,
                  start_at: float = 0.0) -> list[dict]:
    """Geordnete Joins, ein Bot pro Intervall.

    z. B. 4 Bots -> eine Clientgruppe; 8 Bots -> zwei Clientgruppen.
    """
    return [
        {"t": round(start_at + i * interval_s, 3), "ident": b, "action": JOIN}
        for i, b in enumerate(bots)
    ]


def random_join_leave(duration_s: float, join_rate_per_hour: float,
                      bots: Optional[list[str]] = None, seed: int = 20261025,
                      session_bands: Optional[list[list]] = None
                      ) -> list[dict]:
    """Zufälliger Join/Leave-Trace (Poisson-Joins, Band-Sessiondauern).

    Reine Simulation [O]; keinerlei Retail-Messung. Deterministisch bei gleichem
    Seed.
    """
    if bots is None:
        bots = [f"player-{i:02d}" for i in range(1, 33)]
    if session_bands is None:
        session_bands = [[0.1, 300, 1199], [0.8, 1200, 5400], [0.1, 5401, 10800]]
    rng = random.Random(seed)
    events: list[dict] = []
    t = 0.0
    active_bots: dict[str, float] = {}
    while t < duration_s:
        gap = rng.expovariate(join_rate_per_hour / 3600.0)
        t += gap
        if t >= duration_s:
            break
        idle = [b for b in bots if b not in active_bots]
        if not idle:
            continue
        ident = rng.choice(idle)
        band = rng.choices(
            session_bands, weights=[b[0] for b in session_bands])[0]
        end = t + rng.randint(band[1], band[2])
        events.append({"t": round(t, 3), "ident": ident, "action": JOIN})
        events.append({"t": round(min(end, duration_s), 3),
                       "ident": ident, "action": LEAVE})
        active_bots[ident] = end
    events.sort(key=lambda e: e["t"])
    return events


def crash_cooldown_rejoin(ident: str, join_at: float = 10.0,
                          crash_at: float = 40.0, rejoin_at: float = 200.0
                          ) -> list[dict]:
    """Crash + Cooldown + Rejoin mit identischer Identität (gleiche GUID)."""
    return [
        {"t": join_at, "ident": ident, "action": JOIN},
        {"t": crash_at, "ident": ident, "action": "CRASH"},
        {"t": rejoin_at, "ident": ident, "action": "REJOIN"},
    ]


def server_restart(bots: list[str], join_interval: float = 30.0,
                   restart_at: float = 300.0, rejoin_delay: float = 60.0
                   ) -> list[dict]:
    """Alle Bots joinen, Server-Neustart trennt alle PLAYING, stabiler Rejoin.

    RESTART_SERVER entkoppelt die Sessions; keine eigenen LEAVE-Events nötig.
    """
    events = ordered_joins(bots, join_interval)
    events.append({"t": restart_at, "ident": "__server__", "action": "RESTART_SERVER"})
    for i, b in enumerate(bots):
        events.append({"t": restart_at + rejoin_delay + i * 10.0, "ident": b,
                       "action": "REJOIN"})
    events.sort(key=lambda e: e["t"])
    return events


def scenario_four_bots_one_group(interval_s: float = 60.0) -> list[dict]:
    """Vier Bots in einer Clientgruppe (Testanforderung: 4 Bots / 1 Client)."""
    return ordered_joins([f"player-{i:02d}" for i in range(1, 5)],
                         interval_s=interval_s)


def scenario_eight_bots_two_groups(interval_s: float = 60.0) -> list[dict]:
    """Acht Bots in zwei Clientgruppen (Testanforderung: 8 Bots / 2 Clients)."""
    return ordered_joins([f"player-{i:02d}" for i in range(1, 9)],
                         interval_s=interval_s)


def scenario_sixteen_bots_four_groups(interval_s: float = 30.0) -> list[dict]:
    """16 Bots in vier Clientgruppen (Größere Population, Projektion)."""
    return ordered_joins([f"player-{i:02d}" for i in range(1, 17)],
                         interval_s=interval_s)


def save_trace(events: list[dict], path: str) -> None:
    import json
    from pathlib import Path
    Path(path).write_text(json.dumps(events, indent=2), encoding="utf-8")


def load_trace(path: str) -> list[dict]:
    import json
    from pathlib import Path
    return json.loads(Path(path).read_text(encoding="utf-8"))
