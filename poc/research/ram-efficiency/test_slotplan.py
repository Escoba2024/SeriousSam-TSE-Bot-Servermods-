#!/usr/bin/env python3
"""Tests for slotplan.py - the hybrid architecture C scheduler prototype."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from slotplan import (  # noqa: E402
    DYNAMIC_SLOT,
    JOIN,
    LEAVE,
    ROSTER_RESTART,
    SessionEvent,
    SlotPlanner,
    estimate_ram_mib,
)


def ev(t, bot, action):
    return SessionEvent(t, bot, action)


class DynamicSlotTests(unittest.TestCase):
    def test_eight_bots_pack_into_two_clients(self):
        events = [ev(i, f"bot{i}", JOIN) for i in range(8)]
        planner = SlotPlanner(mode=DYNAMIC_SLOT, max_clients=4)
        m = planner.run(events).summary()
        self.assertEqual(m["peak_clients"], 2)
        self.assertEqual(m["joins_served"], 8)
        self.assertEqual(m["client_restarts"], 0)

    def test_leave_frees_slot_for_next_join_without_new_client(self):
        events = [
            ev(0, "a", JOIN), ev(1, "b", JOIN), ev(2, "c", JOIN), ev(3, "d", JOIN),
            ev(10, "a", LEAVE),
            ev(11, "e", JOIN),
        ]
        planner = SlotPlanner(mode=DYNAMIC_SLOT, max_clients=4)
        m = planner.run(events).summary()
        self.assertEqual(m["peak_clients"], 1)
        self.assertEqual(m["client_starts"], 1)

    def test_idle_client_stops_after_hysteresis(self):
        events = [
            ev(0, "a", JOIN),
            ev(5, "a", LEAVE),
            ev(100, "b", JOIN),  # long after idle_stop_s
        ]
        planner = SlotPlanner(mode=DYNAMIC_SLOT, max_clients=4, idle_stop_s=30)
        m = planner.run(events).summary()
        # client stopped after 'a' left + idle window; a fresh start for 'b'
        # ('b' never leaves, so its client keeps running at the end)
        self.assertEqual(m["client_stops"], 1)
        self.assertEqual(m["client_starts"], 2)

    def test_never_exceeds_max_clients_joins_queue(self):
        # 20 joins but only 2 clients x 4 slots capacity
        events = [ev(i, f"bot{i}", JOIN) for i in range(20)]
        planner = SlotPlanner(mode=DYNAMIC_SLOT, max_clients=2)
        metrics = planner.run(events)
        self.assertLessEqual(metrics.peak_clients, 2)
        self.assertEqual(metrics.summary()["joins_served"], 8)
        self.assertEqual(len(planner.pending), 12)  # queued, not dropped

    def test_churn_causes_no_restarts(self):
        events = []
        for i in range(10):
            events.append(ev(i * 10, f"bot{i}", JOIN))
            events.append(ev(i * 10 + 5, f"bot{i}", LEAVE))
        planner = SlotPlanner(mode=DYNAMIC_SLOT, max_clients=4)
        m = planner.run(events).summary()
        self.assertEqual(m["client_restarts"], 0)
        self.assertEqual(m["co_resident_interruptions"], 0)


class RosterRestartTests(unittest.TestCase):
    def test_batching_limits_restarts(self):
        # four joins inside one batch window -> one flush, no restart of a
        # populated client (they all land in the initial roster)
        events = [ev(t, f"bot{t}", JOIN) for t in (0, 2, 4, 6)]
        planner = SlotPlanner(mode=ROSTER_RESTART, max_clients=4, batch_window_s=20)
        m = planner.run(events).summary()
        self.assertEqual(m["joins_served"], 4)
        self.assertEqual(m["peak_clients"], 1)

    def test_late_join_interrupts_co_residents_and_is_counted(self):
        events = [
            ev(0, "a", JOIN), ev(1, "b", JOIN),
            ev(100, "c", JOIN),  # second batch -> restart of populated client
        ]
        planner = SlotPlanner(mode=ROSTER_RESTART, max_clients=4, batch_window_s=10)
        m = planner.run(events).summary()
        self.assertEqual(m["joins_served"], 3)
        self.assertGreaterEqual(m["client_restarts"], 1)
        self.assertGreaterEqual(m["co_resident_interruptions"], 2)

    def test_join_latency_bounded_by_batch_window(self):
        events = [ev(0, "a", JOIN), ev(1, "b", JOIN)]
        planner = SlotPlanner(mode=ROSTER_RESTART, max_clients=4, batch_window_s=20)
        m = planner.run(events).summary()
        self.assertLessEqual(m["join_wait_max_s"], 20.0 + 1e-9)

    def test_dynamic_mode_beats_roster_mode_on_interruptions(self):
        events = []
        for i in range(8):
            events.append(ev(i * 30, f"bot{i}", JOIN))
        for i in range(4):
            events.append(ev(300 + i * 30, f"bot{i}", LEAVE))
        dyn = SlotPlanner(mode=DYNAMIC_SLOT, max_clients=4).run(list(events)).summary()
        ros = SlotPlanner(mode=ROSTER_RESTART, max_clients=4, batch_window_s=20).run(list(events)).summary()
        self.assertEqual(dyn["co_resident_interruptions"], 0)
        self.assertGreater(ros["co_resident_interruptions"], 0)


class RamEstimateTests(unittest.TestCase):
    def test_two_clients_cost_matches_arch_a_coefficients(self):
        self.assertAlmostEqual(estimate_ram_mib(2), 50.2 + 2 * 184.2, places=3)

    def test_zero_clients_is_server_only(self):
        self.assertAlmostEqual(estimate_ram_mib(0), 50.2, places=3)


if __name__ == "__main__":
    unittest.main()
