#!/usr/bin/env python3
"""Reproducible offline QA regressions for Session Management & Feature Flags.

Covers:
  - QA-05: TSE format-code / Unicode / duplicate-"Serious Sam" snapshot poisoning
           bypassing human_capacity eviction & crashing SessionExecutor.player_names.
  - QA-06: Global LEAVING deadlock when a JOINING->LEAVING client hangs at menu
           (alive=True, connected=False -> infinite 'wait_leave_ready').
  - QA-09: PR #68 validate_config discarding normalized identity dicts +
           PR #57 vs PR #63 tools/redstation_preset.py semantic collision.
  - QA-10: cecil_p1 rejected by bot_sessions.validate_config, runtime flags
           (exploratory_search, strafe_scale, debug_logging, log_every_ticks)
           ignored by startup_script, and BotDriver live flag reload gap.

IMPORTANT: Pure offline reproduction suite. Native Retail 1.07 status: NOT_TESTED_RETAIL.
"""
import re
import unittest

VISIBLE_CAP = 24


def clean_name_pr57_buggy(value):
    """Exact PR #57 tools/bot_sessions.py:24-37 (misses ^aXX, ^o/^O, ^R & non-ASCII)."""
    if not isinstance(value, str):
        raise ValueError("nickname must be text")
    value = re.sub(r"\^c[0-9a-fA-F]{6}|\^f[0-9]|\^[biIBFr]", "", value)
    value = re.sub(r"[^A-Za-z0-9 ._\[\]-]", "", value)
    value = " ".join(value.split())[:VISIBLE_CAP].strip()
    if not value or not any(c.isalnum() for c in value):
        raise ValueError("empty visible nickname")
    return value


def clean_name_pr68_buggy(value):
    """Exact PR #68 session_hybrid_lab.py:207-216 (broken double-escaped raw regex!)."""
    if not isinstance(value, str):
        raise ValueError("nickname must be text")
    value = re.sub(r"\^c[0-9a-fA-F]{6}|\^r", "", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9 ._\\[\\]-]", "", value)
    value = " ".join(value.split())[:VISIBLE_CAP].strip()
    if not value or not any(c.isalnum() for c in value):
        raise ValueError("empty visible nickname")
    return value


def clean_tse_visible_name_fixed(value):
    """Fixed TSE markup stripper for human/query observation (never rejects humans)."""
    if not isinstance(value, str):
        return ""
    # Strip all Serious Engine 1.07 text control codes:
    # ^cXXXXXX (RGB), ^aXX (alpha), ^fX (flash), ^b/^B (bold), ^i/^I (italic),
    # ^r/^R (reset), ^o/^O (contrast), ^^ (escaped caret).
    s = value.replace("^^", "\x00")
    s = re.sub(r"\^c[0-9a-fA-F]{0,6}|\^a[0-9a-fA-F]{0,2}|\^f[0-9]|\^[bBiIrRoO]", "", s)
    s = s.replace("\x00", "^")
    return " ".join(s.split()).strip()


def snapshot_pr57_buggy(snapshot_dict, now, max_bots=8, reserved_human_slots=2):
    """Exact PR #57 Planner.snapshot (tools/bot_sessions.py:239-248)."""
    at = snapshot_dict.get("observed_at")
    maximum = snapshot_dict.get("maxplayers")
    names = snapshot_dict.get("human_names")
    if (not isinstance(at, (int, float)) or not 0 <= now - at <= 15
            or type(maximum) is not int or not 1 <= maximum <= 16
            or not isinstance(names, list) or len(names) > maximum):
        return None
    try:
        keys = [clean_name_pr57_buggy(n).casefold() for n in names]
    except ValueError:
        return None
    if len(set(keys)) != len(keys):
        return None
    humans = set(keys)
    return max(0, min(max_bots, maximum - reserved_human_slots - len(humans))), humans


def snapshot_fixed(snapshot_dict, now, max_bots=8, reserved_human_slots=2):
    """Fixed Planner.snapshot counting ALL human slots regardless of name collisions/encoding."""
    at = snapshot_dict.get("observed_at")
    maximum = snapshot_dict.get("maxplayers")
    names = snapshot_dict.get("human_names")
    if (not isinstance(at, (int, float)) or not 0 <= now - at <= 15
            or type(maximum) is not int or not 1 <= maximum <= 16
            or not isinstance(names, list) or len(names) > maximum):
        return None
    human_count = len(names)
    known_visible = {
        clean_tse_visible_name_fixed(n).casefold()
        for n in names
        if isinstance(n, str) and clean_tse_visible_name_fixed(n)
    }
    return max(0, min(max_bots, maximum - reserved_human_slots - human_count)), known_visible


def leave_step_pr57_buggy(*, alive, connected, close_sent, since_close_s=0.0):
    """Exact PR #57 tools/bot_session_runtime.py:221-227."""
    if not alive:
        return "confirm_absent"
    if not connected and not close_sent:
        return "wait_leave_ready"
    if not close_sent:
        return "send_wm_delete_window"
    return "wait_clean_exit" if since_close_s < 10.0 else "terminate_process_group"


def leave_step_fixed(*, alive, connected, close_sent, since_close_s=0.0,
                     since_leave_requested_s=0.0, ready_timeout_s=15.0):
    """Fixed leave_step closing unconnected menu-stuck clients after bounded wait."""
    if not alive:
        return "confirm_absent"
    if not connected and not close_sent and since_leave_requested_s < ready_timeout_s:
        return "wait_leave_ready"
    if not close_sent:
        return "send_wm_delete_window"
    return "wait_clean_exit" if since_close_s < 10.0 else "terminate_process_group"


class SessionAndFlagsRegressionTests(unittest.TestCase):

    def test_qa05a_duplicate_default_serious_sam_names_disable_eviction(self):
        """Two vanilla humans with default name 'Serious Sam' poison snapshot() -> None."""
        # 8 bots active on a 16-slot server (reserved_human_slots=2).
        # 9 humans join, including two unconfigured players named 'Serious Sam'.
        humans = ["Serious Sam", "Serious Sam"] + [f"Player{i}" for i in range(7)]
        snap = {"observed_at": 100.0, "maxplayers": 16, "human_names": humans}

        observed_buggy = snapshot_pr57_buggy(snap, now=101.0, max_bots=8, reserved_human_slots=2)
        self.assertIsNone(observed_buggy)

        # In PR #57 bot_sessions.py:279, `due` checks `observed is not None and len(active) > capacity`:
        active_bots = 8
        evict_buggy = (observed_buggy is not None and active_bots > observed_buggy[0])
        self.assertFalse(evict_buggy, "Bug reproduced: 0 bots evicted despite 9 humans + 8 bots > 16!")

        observed_fixed = snapshot_fixed(snap, now=101.0, max_bots=8, reserved_human_slots=2)
        self.assertIsNotNone(observed_fixed)
        capacity_fixed, _ = observed_fixed
        self.assertEqual(capacity_fixed, 5)  # 16 - 2 - 9 = 5 bots allowed -> evict 3 bots!
        self.assertTrue(active_bots > capacity_fixed)

    def test_qa05b_unicode_player_name_poisons_snapshot_and_crashes_executor(self):
        """A single non-ASCII human player ('Игрок') raises ValueError in clean_name."""
        with self.assertRaises(ValueError):
            # Mirrors bot_session_executor.py:56: [clean_name(v) for _, v in pairs]
            _ = [clean_name_pr57_buggy(n) for n in ["Jax", "Игрок"]]

        snap = {"observed_at": 50.0, "maxplayers": 16, "human_names": ["Игрок"] + [f"H{i}" for i in range(8)]}
        self.assertIsNone(snapshot_pr57_buggy(snap, now=51.0))

        cap_fixed, names_fixed = snapshot_fixed(snap, now=51.0)
        self.assertEqual(cap_fixed, 5)
        self.assertIn("игрок", names_fixed)

    def test_qa05c_tse_format_codes_and_pr68_broken_whitelist_regex(self):
        """PR #57 misses ^aXX/^o/^R; PR #68 double-escaped raw regex fails to sanitize at all."""
        corrupted_pr57 = clean_name_pr57_buggy("^aFF^oJax^R").casefold()
        self.assertEqual(corrupted_pr57, "affojaxr")
        corrupted_pr68 = clean_name_pr68_buggy("^b^iJax^r")
        self.assertEqual(corrupted_pr68, "^b^iJax")
        unsanitized_injection = clean_name_pr68_buggy('Bot"; Quit(); //')
        self.assertEqual(unsanitized_injection, 'Bot"; Quit(); //')

        cleaned = clean_tse_visible_name_fixed("^b^i^f2^aFF^oJax^R").casefold()
        self.assertEqual(cleaned, "jax")

    def test_qa06_stuck_menu_leaving_client_deadlocks_all_servers(self):
        """JOINING->LEAVING client stuck at menu (alive=True, connected=False) blocks forever."""
        # Even after 3600 seconds, PR #57 leave_step returns 'wait_leave_ready':
        action_buggy = leave_step_pr57_buggy(alive=True, connected=False, close_sent=False, since_close_s=0.0)
        self.assertEqual(action_buggy, "wait_leave_ready")

        # Planner.plan (bot_sessions.py:282) checks `not any(r["status"] == "LEAVING" for r in rows.values())`
        # across ALL servers in the SQLite DB, permanently starving server B's human_capacity leaves!
        all_rows = [
            {"id": "bot-a1", "server": "server-a", "status": "LEAVING"},  # stuck at menu
            {"id": "bot-b1", "server": "server-b", "status": "PLAYING"},  # needs human_capacity eviction!
        ]
        can_evict_server_b_buggy = not any(r["status"] == "LEAVING" for r in all_rows)
        self.assertFalse(can_evict_server_b_buggy)

        # Fixed leave_step escalates to WM_DELETE_WINDOW once ready_timeout_s elapses:
        action_fixed = leave_step_fixed(
            alive=True, connected=False, close_sent=False,
            since_leave_requested_s=16.0, ready_timeout_s=15.0,
        )
        self.assertEqual(action_fixed, "send_wm_delete_window")

    def test_qa09_pr68_validate_config_discards_normalized_identities(self):
        """PR #68 session_hybrid_lab.py:288-310 normalizes copy `i` then assigns raw `pool`."""
        raw_pool = [{"id": "player-01", "nickname": "  ^cff00aaJax^r  ", "profile": 0, "color": "ff00aa"}]
        # Mirror PR #68 lines 288-310:
        for raw in raw_pool:
            i = dict(raw)
            i["nickname"] = clean_name_pr57_buggy(i["nickname"])
            i.setdefault("regular_weight", 1)
            i["color"] = i["color"].upper()
        buggy_saved_pool = raw_pool  # PR #68 line 310: `c["identities"] = pool`!
        self.assertEqual(buggy_saved_pool[0]["nickname"], "  ^cff00aaJax^r  ")
        self.assertNotIn("regular_weight", buggy_saved_pool[0])
        self.assertEqual(buggy_saved_pool[0]["color"], "ff00aa")

    def test_qa10_session_flag_schema_and_startup_script_disconnect(self):
        """PR #57 validate_config rejects cecil_p1 & startup_script drops 4 runtime CVars."""
        pr57_defaults = {
            "pool_id": "tse-bot-pool-v1",
            "seed": 20261022,
            "enabled": False,
            "colors_enabled": False,
            "exploratory_search": False,
            "strafe_scale": 0.0,
            "debug_logging": False,
            "log_every_ticks": 0,
        }
        # 1. Passing cecil_p1 raises ValueError because set(config) - set(DEFAULTS) != empty:
        candidate_cfg = dict(pr57_defaults, cecil_p1=True, exploratory_search=True, strafe_scale=0.65)
        unknown_keys = set(candidate_cfg) - set(pr57_defaults)
        self.assertEqual(unknown_keys, {"cecil_p1"})

        # 2. PR #57 bot_session_runtime.py:92-103 startup_script(server_addr, identity)
        #    accepts ONLY (server_addr, identity) and hardcodes neither exploratory_search,
        #    cecil_p1, strafe_scale, debug_logging, nor log_every_ticks!
        pr57_script = (
            'bot_bEnabled=1;\nbot_bHumanAI=1;\nbot_bSkipLocalPlayers=0;\n'
            'bot_iProfile0=3;\nbot_iSeed=12345;\n'
        )
        for missing_cvar in (
            "bot_bExploratorySearch",
            "bot_bCecilP1",
            "bot_fStrafeScale",
            "bot_bDebugLog",
            "bot_iLogEvery",
        ):
            self.assertNotIn(missing_cvar, pr57_script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
