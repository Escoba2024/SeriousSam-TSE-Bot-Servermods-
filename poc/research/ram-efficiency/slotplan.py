#!/usr/bin/env python3
"""slotplan.py - hybrid architecture C prototype: independent bot sessions
multiplexed onto shared 4-local-player Retail clients.

This is a **deterministic, offline scheduler prototype**. It contains no
Wine, no network and no game code; it answers the architectural question
"how many client processes does a given join/leave trace actually need, and
what does that cost in RAM?" before anybody spends Hetzner time on it.

Two operating modes map to the two technical paths described in
``docs/research/ram-efficiency/2026-10-25-architecture-comparison.md``:

* ``DYNAMIC_SLOT``  - assumes engine capability **E1/E2** (mid-session
  ``_pNetwork->AddPlayer_t`` / player-source removal on a connected retail
  client) works. Sessions bind to a free slot of a running client at join
  time; a client with zero active slots is stopped after ``idle_stop_s``.
  E1/E2 are **NOT verified** on Retail 1.07 - this mode is a planning tool,
  not a capability claim.

* ``ROSTER_RESTART`` - uses **only primitives that are already proven** on
  the Hetzner runtime (start a client with a fixed roster, stop a client,
  per-client join confirmation): membership changes are batched inside
  ``batch_window_s`` and applied by restarting the affected client with the
  new roster. Bots on an unchanged client are never interrupted if the
  packing allows it; joins pay up to ``batch_window_s`` of latency plus the
  client start time.

Both modes guarantee:
* never more than ``max_clients`` concurrent client processes;
* at most ``slots_per_client`` sessions per client;
* a session is never silently dropped (joins beyond capacity queue).

Output metrics: peak concurrent clients, client starts/stops/restarts,
per-join waiting time, and a client-process timeline that can be priced with
``resource_model.py`` coefficients.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field

DYNAMIC_SLOT = "DYNAMIC_SLOT"
ROSTER_RESTART = "ROSTER_RESTART"

JOIN = "JOIN"
LEAVE = "LEAVE"


@dataclass(frozen=True)
class SessionEvent:
    time_s: float
    bot_id: str
    action: str  # JOIN | LEAVE


@dataclass
class Client:
    index: int
    slots: dict = field(default_factory=dict)   # slot -> bot_id
    running: bool = False
    empty_since: float | None = None
    starts: int = 0
    restarts: int = 0

    def free_slot(self, slots_per_client: int):
        for s in range(slots_per_client):
            if s not in self.slots:
                return s
        return None


@dataclass
class Metrics:
    peak_clients: int = 0
    client_starts: int = 0
    client_stops: int = 0
    client_restarts: int = 0
    joins_served: int = 0
    leaves_served: int = 0
    join_wait_s: list = field(default_factory=list)
    interrupted_bot_ticks: int = 0  # ROSTER_RESTART: co-residents restarted
    timeline: list = field(default_factory=list)  # (time_s, running_clients)

    def snapshot(self, t: float, running: int):
        self.peak_clients = max(self.peak_clients, running)
        self.timeline.append((t, running))

    def summary(self) -> dict:
        waits = sorted(self.join_wait_s)
        return {
            "peak_clients": self.peak_clients,
            "client_starts": self.client_starts,
            "client_stops": self.client_stops,
            "client_restarts": self.client_restarts,
            "joins_served": self.joins_served,
            "leaves_served": self.leaves_served,
            "join_wait_max_s": waits[-1] if waits else 0.0,
            "join_wait_mean_s": sum(waits) / len(waits) if waits else 0.0,
            "co_resident_interruptions": self.interrupted_bot_ticks,
        }


class SlotPlanner:
    def __init__(self, mode=DYNAMIC_SLOT, slots_per_client=4, max_clients=4,
                 idle_stop_s=30.0, batch_window_s=20.0):
        if mode not in (DYNAMIC_SLOT, ROSTER_RESTART):
            raise ValueError("unknown mode: %r" % mode)
        self.mode = mode
        self.slots_per_client = slots_per_client
        self.max_clients = max_clients
        self.idle_stop_s = idle_stop_s
        self.batch_window_s = batch_window_s
        self.clients = [Client(i) for i in range(max_clients)]
        self.metrics = Metrics()
        self.pending = []           # queued (event_time, bot_id) joins
        self.bot_location = {}      # bot_id -> (client_index, slot)
        self.batch = []             # ROSTER_RESTART: buffered events
        self.batch_deadline = None

    # -- shared helpers ----------------------------------------------------
    def _running(self):
        return sum(1 for c in self.clients if c.running)

    def _start(self, client: Client):
        client.running = True
        client.empty_since = None
        client.starts += 1
        self.metrics.client_starts += 1

    def _stop(self, client: Client):
        client.running = False
        client.empty_since = None
        self.metrics.client_stops += 1

    def _place(self, t_event: float, t_now: float, bot_id: str) -> bool:
        """Place a bot on any client with a free slot; start one if needed."""
        # Prefer running clients with free slots (densest first for packing).
        candidates = [c for c in self.clients if c.running and
                      c.free_slot(self.slots_per_client) is not None]
        candidates.sort(key=lambda c: -len(c.slots))
        if not candidates:
            stopped = [c for c in self.clients if not c.running]
            if not stopped:
                return False
            client = stopped[0]
            self._start(client)
            candidates = [client]
        client = candidates[0]
        slot = client.free_slot(self.slots_per_client)
        client.slots[slot] = bot_id
        client.empty_since = None
        self.bot_location[bot_id] = (client.index, slot)
        self.metrics.joins_served += 1
        self.metrics.join_wait_s.append(max(0.0, t_now - t_event))
        return True

    def _remove(self, bot_id: str, t: float):
        loc = self.bot_location.pop(bot_id, None)
        if loc is None:
            return
        client = self.clients[loc[0]]
        client.slots.pop(loc[1], None)
        self.metrics.leaves_served += 1
        if not client.slots and client.running:
            client.empty_since = t

    def _reap_idle(self, t: float):
        for client in self.clients:
            if (client.running and not client.slots and
                    client.empty_since is not None and
                    t - client.empty_since >= self.idle_stop_s):
                self._stop(client)

    def _drain_pending(self, t: float):
        remaining = []
        for t_event, bot_id in self.pending:
            if not self._place(t_event, t, bot_id):
                remaining.append((t_event, bot_id))
        self.pending = remaining

    # -- ROSTER_RESTART batching -------------------------------------------
    def _flush_batch(self, t: float):
        joins = [e for e in self.batch if e.action == JOIN]
        leaves = [e for e in self.batch if e.action == LEAVE]
        self.batch = []
        self.batch_deadline = None
        touched = set()
        for ev in leaves:
            loc = self.bot_location.get(ev.bot_id)
            if loc is not None:
                touched.add(loc[0])
            self._remove(ev.bot_id, t)
        for ev in joins:
            before = {c.index: dict(c.slots) for c in self.clients}
            if self._place(ev.time_s, t, ev.bot_id):
                cidx = self.bot_location[ev.bot_id][0]
                # restarting an already-populated client interrupts residents
                if before.get(cidx):
                    touched.add(cidx)
            else:
                self.pending.append((ev.time_s, ev.bot_id))
        for cidx in touched:
            client = self.clients[cidx]
            if client.running:
                client.restarts += 1
                self.metrics.client_restarts += 1
                # all current co-residents of a restarted client are interrupted
                self.metrics.interrupted_bot_ticks += len(client.slots)

    # -- event loop ----------------------------------------------------------
    def run(self, events) -> Metrics:
        events = sorted(events, key=lambda e: e.time_s)
        for ev in events:
            t = ev.time_s
            if (self.mode == ROSTER_RESTART and self.batch_deadline is not None
                    and t >= self.batch_deadline):
                self._flush_batch(self.batch_deadline)
            self._reap_idle(t)
            self._drain_pending(t)
            if self.mode == DYNAMIC_SLOT:
                if ev.action == JOIN:
                    if not self._place(t, t, ev.bot_id):
                        self.pending.append((t, ev.bot_id))
                elif ev.action == LEAVE:
                    self._remove(ev.bot_id, t)
            else:
                self.batch.append(ev)
                if self.batch_deadline is None:
                    self.batch_deadline = t + self.batch_window_s
            self.metrics.snapshot(t, self._running())
        # final flush/reap
        if self.mode == ROSTER_RESTART and self.batch:
            self._flush_batch(self.batch_deadline or (events[-1].time_s if events else 0.0))
        last_t = events[-1].time_s if events else 0.0
        self._drain_pending(last_t)
        self._reap_idle(last_t + self.idle_stop_s)
        self.metrics.snapshot(last_t + self.idle_stop_s, self._running())
        return self.metrics


def estimate_ram_mib(peak_clients: int, server_rss_mib=50.2, client_rss_mib=184.2) -> float:
    """Price a timeline with architecture-A RSS coefficients (DERIVED basis).

    RSS basis double-counts shared pages; replace with PSS once the harness
    has produced real per-architecture PSS numbers.
    """
    return server_rss_mib + peak_clients * client_rss_mib


def parse_trace(path) -> list:
    events = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        t, bot, action = line.split()[:3]
        events.append(SessionEvent(float(t), bot, action.upper()))
    return events


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("trace", help="trace file: '<time_s> <bot_id> <JOIN|LEAVE>' per line")
    p.add_argument("--mode", choices=(DYNAMIC_SLOT, ROSTER_RESTART), default=ROSTER_RESTART)
    p.add_argument("--max-clients", type=int, default=4)
    p.add_argument("--slots-per-client", type=int, default=4)
    p.add_argument("--idle-stop-s", type=float, default=30.0)
    p.add_argument("--batch-window-s", type=float, default=20.0)
    args = p.parse_args(argv)
    planner = SlotPlanner(mode=args.mode, slots_per_client=args.slots_per_client,
                          max_clients=args.max_clients, idle_stop_s=args.idle_stop_s,
                          batch_window_s=args.batch_window_s)
    metrics = planner.run(parse_trace(args.trace))
    out = metrics.summary()
    out["estimated_peak_ram_mib_rss_basis"] = round(estimate_ram_mib(out["peak_clients"]), 1)
    out["mode"] = args.mode
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
