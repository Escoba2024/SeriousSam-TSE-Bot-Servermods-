#!/usr/bin/env python3
"""Tests for tools/bot_telemetry.py (synthetic fixtures, no game required)."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import bot_telemetry as bt


def row(
    t_ms,
    ticks=20,
    actions=80,
    frames=20,
    lp=4,
    enabled=1,
    gameon=1,
    disabled=0,
    gameoff=0,
    nolocal=0,
    noentity=0,
    reason=0,
    lock_ms=0.5,
    stall=0,
):
    return [
        t_ms,
        ticks,
        actions,
        frames,
        0 if not (enabled and gameon) else frames,
        frames,
        lp,
        gameon,
        enabled,
        disabled,
        gameoff,
        nolocal,
        noentity,
        lock_ms,
        0.2,
        52.0,
        50.0,
        120,
        15,
        stall,
        reason,
    ]


def make_csv(rows, config="bot_enabled=1,bot_iTelemetry=1,nullrender=0", build="p0-telemetry-20261022"):
    lines = [
        "#bot-telemetry,rev=1",
        "#build,tag=%s,built=Oct 22 2026 10:00:00" % build,
        "#exe,Z:\\game\\Bin\\SeriousSam.exe",
        "#config,%s" % config,
        "#columns," + ",".join(bt.COLUMNS),
    ]
    for values in rows:
        lines.append(",".join(str(value) for value in values))
    return "\n".join(lines) + "\n"


class ParseTests(unittest.TestCase):
    def test_parses_manifest_and_rows(self):
        text = make_csv([row(1000), row(2000)])
        recording = bt.parse(text)
        self.assertEqual(recording.build["tag"], "p0-telemetry-20261022")
        self.assertEqual(recording.config["bot_enabled"], "1")
        self.assertEqual(len(recording.rows), 2)
        self.assertEqual(recording.rows[0].actions, 80)

    def test_state_and_note_lines_are_kept(self):
        text = make_csv([row(1000)]) + "#state,t_ms=1000,reason=0\n#note,CONFIG,x=1\n"
        recording = bt.parse(text)
        self.assertEqual(len(recording.states), 1)
        self.assertEqual(recording.notes, ["CONFIG,x=1"])

    def test_rejects_wrong_column_layout(self):
        text = make_csv([row(1000)]).replace("renderdraw,lp", "renders,lp")
        with self.assertRaises(bt.TelemetryError):
            bt.parse(text)

    def test_rejects_missing_header(self):
        with self.assertRaises(bt.TelemetryError):
            bt.parse("1000,20,80\n")

    def test_rejects_short_row(self):
        text = make_csv([row(1000)])
        text = text.rstrip("\n") + "\n1000,20,80\n"
        with self.assertRaises(bt.TelemetryError):
            bt.parse(text)


class AnalyzeTests(unittest.TestCase):
    def test_active_ok(self):
        rows = [row(1000 * i) for i in range(1, 11)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "ACTIVE_OK")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["tick_hz_median"], 20)
        self.assertAlmostEqual(result["action_ratio"], 1.0)
        self.assertEqual(result["lp_median"], 4)

    def test_disabled_by_config(self):
        rows = [row(1000 * i, ticks=20, actions=0, lp=0, disabled=20, reason=1) for i in range(1, 6)]
        result = bt.analyze(bt.parse(make_csv(rows, config="bot_enabled=0")))
        self.assertEqual(result["verdict"], "INACTIVE")
        self.assertEqual(result["exit_code"], bt.EXIT_INACTIVE)
        self.assertTrue(any("bot_bEnabled=0" in w for w in result["warnings"]))

    def test_game_off(self):
        rows = [row(1000 * i, ticks=20, actions=0, lp=4, gameon=0, gameoff=20, reason=2) for i in range(1, 6)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "INACTIVE")
        self.assertIn("GAMEOFF", result["reasons"])

    def test_no_local_players(self):
        rows = [row(1000 * i, ticks=20, actions=0, lp=0, nolocal=20, reason=3) for i in range(1, 6)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "INACTIVE")
        self.assertIn("NOLOCAL", result["reasons"])

    def test_stalled_timer_is_not_confused_with_disabled(self):
        rows = [row(1000 * i, ticks=0, actions=0, stall=i) for i in range(1, 5)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "STALLED")
        self.assertEqual(result["exit_code"], bt.EXIT_STALLED)
        self.assertTrue(any("timer stall" in w for w in result["warnings"]))

    def test_action_starved(self):
        rows = [row(1000 * i, ticks=20, actions=0) for i in range(1, 6)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "ACTION_STARVED")
        self.assertEqual(result["exit_code"], bt.EXIT_STALLED)

    def test_entity_missing_ratio(self):
        rows = [row(1000 * i, ticks=20, actions=20, noentity=10) for i in range(1, 6)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "ACTION_STARVED")
        self.assertEqual(result["reasons"], {"ACTIVE": 5})

    def test_missing_entity_is_reported_as_inactive(self):
        rows = [row(1000 * i, ticks=20, actions=0, noentity=80, reason=4) for i in range(1, 6)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertEqual(result["verdict"], "INACTIVE")
        self.assertEqual(result["exit_code"], bt.EXIT_INACTIVE)
        self.assertIn("NOENTITY", result["reasons"])

    def test_no_data(self):
        result = bt.analyze(bt.parse(make_csv([])))
        self.assertEqual(result["verdict"], "NO_DATA")
        self.assertEqual(result["exit_code"], bt.EXIT_NO_DATA)

    def test_warmup_skips_early_rows(self):
        rows = [row(1000, ticks=0, actions=0, stall=1)] + [row(1000 * i) for i in range(2, 12)]
        result = bt.analyze(bt.parse(make_csv(rows)), warmup_s=0.5)
        self.assertEqual(result["samples"], 10)
        self.assertEqual(result["verdict"], "ACTIVE_OK")

    def test_duration_caps_the_window(self):
        rows = [row(1000 * i) for i in range(1, 21)]
        result = bt.analyze(bt.parse(make_csv(rows)), warmup_s=1.0, duration_s=5.0)
        self.assertEqual(result["samples"], 6)
        self.assertEqual(result["verdict"], "ACTIVE_OK")

    def test_expectations_and_nullrender(self):
        rows = [row(1000 * i) for i in range(1, 6)]
        text = make_csv(rows, config="bot_enabled=1,nullrender=1")
        result = bt.analyze(bt.parse(text), expect_bots=4, expect_nullrender=1)
        self.assertEqual(result["warnings"], [])
        mismatch = bt.analyze(bt.parse(text), expect_bots=2, expect_nullrender=0)
        self.assertTrue(any("local players" in w for w in mismatch["warnings"]))
        self.assertTrue(any("nullrender" in w for w in mismatch["warnings"]))

    def test_lock_stall_warning(self):
        rows = [row(1000 * i, lock_ms=1500.0) for i in range(1, 4)]
        result = bt.analyze(bt.parse(make_csv(rows)))
        self.assertTrue(any("ga_csNetwork" in w for w in result["warnings"]))


class CliTests(unittest.TestCase):
    def _run(self, text, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BotTelemetry.csv"
            path.write_text(text, encoding="utf-8")
            out_json = Path(tmp) / "out.json"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = bt.main([str(path), "--json", str(out_json), *extra])
            payload = json.loads(out_json.read_text(encoding="utf-8")) if out_json.exists() else None
            return code, buffer.getvalue(), payload

    def test_cli_active(self):
        code, text, payload = self._run(make_csv([row(1000 * i) for i in range(1, 6)]))
        self.assertEqual(code, 0)
        self.assertIn("ACTIVE_OK", text)
        self.assertEqual(payload["verdict"], "ACTIVE_OK")

    def test_cli_malformed_returns_usage(self):
        code, _, _ = self._run("#bot-telemetry,rev=1\n")
        self.assertEqual(code, bt.EXIT_USAGE)


if __name__ == "__main__":
    unittest.main()
