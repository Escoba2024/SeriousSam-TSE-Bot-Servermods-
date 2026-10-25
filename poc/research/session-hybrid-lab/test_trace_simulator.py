#!/usr/bin/env python3
"""Reproduzierbare Tests für trace_simulator.py (offline, keine Messung)."""

from __future__ import annotations

import unittest

import trace_simulator as ts


class OrderedJoinsTests(unittest.TestCase):
    def test_four_bots_one_group(self):
        events = ts.scenario_four_bots_one_group(interval_s=60.0)
        self.assertEqual(len(events), 4)
        self.assertTrue(all(e["action"] == ts.JOIN for e in events))
        self.assertEqual([e["t"] for e in events], [0.0, 60.0, 120.0, 180.0])
        self.assertEqual([e["ident"] for e in events],
                         ["player-01", "player-02", "player-03", "player-04"])

    def test_eight_bots_two_groups(self):
        events = ts.scenario_eight_bots_two_groups(interval_s=60.0)
        self.assertEqual(len(events), 8)

    def test_sixteen_bots_four_groups(self):
        events = ts.scenario_sixteen_bots_four_groups(interval_s=30.0)
        self.assertEqual(len(events), 16)
        self.assertEqual(events[-1]["t"], 450.0)

    def test_custom_bots_and_interval(self):
        events = ts.ordered_joins(["a", "b", "c"], interval_s=10.0,
                                  start_at=5.0)
        self.assertEqual([e["t"] for e in events], [5.0, 15.0, 25.0])


class RandomTraceTests(unittest.TestCase):
    def test_deterministic_same_seed(self):
        t1 = ts.random_join_leave(3600.0, 12.0,
                                  bots=[f"b{i}" for i in range(1, 9)],
                                  seed=7)
        t2 = ts.random_join_leave(3600.0, 12.0,
                                  bots=[f"b{i}" for i in range(1, 9)],
                                  seed=7)
        self.assertEqual(t1, t2)

    def test_different_seed_differs(self):
        t1 = ts.random_join_leave(3600.0, 12.0,
                                  bots=[f"b{i}" for i in range(1, 9)],
                                  seed=7)
        t2 = ts.random_join_leave(3600.0, 12.0,
                                  bots=[f"b{i}" for i in range(1, 9)],
                                  seed=8)
        self.assertNotEqual(t1, t2)

    def test_actions_and_balance(self):
        events = ts.random_join_leave(7200.0, 60.0,
                                      bots=[f"b{i}" for i in range(1, 9)],
                                      seed=3)
        joins = [e for e in events if e["action"] == ts.JOIN]
        leaves = [e for e in events if e["action"] == ts.LEAVE]
        self.assertTrue(all(e["action"] in (ts.JOIN, ts.LEAVE) for e in events))
        # Jeder Join hat einen passenden Leave (außer evtl. am Ende)
        self.assertGreaterEqual(len(joins), len(leaves))
        self.assertLessEqual(len(leaves), len(joins))
        self.assertTrue(all(e["t"] <= 7200.0 for e in events))


class CrashCooldownRejoinTests(unittest.TestCase):
    def test_shape_and_stable_intent(self):
        events = ts.crash_cooldown_rejoin("player-07", join_at=10.0,
                                          crash_at=40.0, rejoin_at=200.0)
        self.assertEqual([e["action"] for e in events],
                         [ts.JOIN, "CRASH", "REJOIN"])
        self.assertTrue(all(e["ident"] == "player-07" for e in events))
        self.assertEqual([e["t"] for e in events], [10.0, 40.0, 200.0])


class ServerRestartTests(unittest.TestCase):
    def test_shape(self):
        events = ts.server_restart(["b1", "b2"], join_interval=30.0,
                                   restart_at=300.0, rejoin_delay=60.0)
        actions = [e["action"] for e in events]
        self.assertEqual(actions.count(ts.JOIN), 2)
        self.assertIn("RESTART_SERVER", actions)
        self.assertEqual(actions.count("REJOIN"), 2)
        rs = actions.index("RESTART_SERVER")
        self.assertLess(actions.index(ts.JOIN), rs)
        self.assertGreater(actions.index("REJOIN"), rs)
        # RESTART_SERVER hat keinen bekannten Bot-Ident
        restart_ev = [e for e in events if e["action"] == "RESTART_SERVER"][0]
        self.assertEqual(restart_ev["ident"], "__server__")


class SaveLoadTests(unittest.TestCase):
    def test_roundtrip(self):
        import tempfile
        events = ts.scenario_four_bots_one_group()
        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/trace.json"
            ts.save_trace(events, path)
            loaded = ts.load_trace(path)
            self.assertEqual(loaded, events)


if __name__ == "__main__":
    unittest.main(verbosity=2)
