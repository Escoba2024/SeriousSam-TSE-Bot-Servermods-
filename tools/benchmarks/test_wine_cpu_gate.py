"""Regression gates for real Wine CPU comparisons, not simulated native acceptance."""
import os
import re
from pathlib import Path
import tempfile
import unittest
import wine_cpu_gate as gate

def log(rate=20, slots=4):
    return "\n".join(f"[BotDriver] bot{i} tick={t} pos=({t/20},0,0) heading=1 fire=1"
        for t in (20,20+rate*10) for i in range(slots))
class GateTests(unittest.TestCase):
    def test_runtime_owner_can_read_private_ini(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"config.ini"
            gate.write_runtime_config(p,"bot_bEnabled=1;\n",os.getuid(),os.getgid())
            self.assertEqual(p.read_text(),"bot_bEnabled=1;\n")
            self.assertEqual(p.stat().st_mode & 0o777,0o600)
            self.assertEqual(p.stat().st_uid,os.getuid())
    def test_valid_four_slot_ticks_pass(self):
        self.assertEqual(gate.action_evidence(log(),10)["rates_hz"],[20.0]*4)
    def test_permission_error_rejected_even_with_join(self):
        with self.assertRaisesRegex(ValueError,"script"):
            gate.action_evidence(log()+"\nCannot load script file: Permission denied",10)
    def test_missing_slot_rejected(self):
        with self.assertRaisesRegex(ValueError,"slot"):
            gate.action_evidence(log(slots=3),10)
    def test_stalled_actions_rejected(self):
        with self.assertRaisesRegex(ValueError,"rate"):
            gate.action_evidence(log(rate=2),10)
    def test_sync_failure_rejected(self):
        with self.assertRaisesRegex(ValueError,"sync"):
            gate.action_evidence(log()+"\nToo many bad syncs",10)
    def test_new_throttling_rejected(self):
        with self.assertRaisesRegex(ValueError,"throttl"):
            gate.check_throttling({"nr_throttled":2},{"nr_throttled":3})
    def test_historical_throttling_does_not_reject_new_clean_run(self):
        gate.check_throttling({"nr_throttled":2528},{"nr_throttled":2528})
    def test_no_motion_rejected(self):
        with self.assertRaisesRegex(ValueError,"motion"):
            gate.action_evidence(re.sub(r"pos=\([^)]+\)","pos=(0,0,0)",log()),10)
if __name__=="__main__":unittest.main()
