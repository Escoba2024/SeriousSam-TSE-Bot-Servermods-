"""Regression tests for the read-only Retail session A/B comparability gate."""
import json
import tempfile
import unittest
from pathlib import Path
from native_ab_comparability import compare_runs, main

HEX_A = "a" * 64
HEX_B = "b" * 64
HARNESS = {
    "qualify_bot_sessions.py": HEX_A,
    "bot_session_executor.py": HEX_A,
    "bot_session_runtime.py": HEX_A,
    "bot_sessions.py": HEX_A,
    "qualify_integrated_wine.py": HEX_A,
}

def receipt(p1):
    return {
        "status": "FAIL" if p1 else "PASS_LIMITED_SESSION_LIFECYCLE",
        "scope": "ISOLATED_NETNS_RETAIL_WINE",
        "dll_sha256": HEX_A,
        "max_bots": 4,
        "peak_playing": 4,
        "cecil_p1": p1,
        "accelerated": False,
        "original_client": True,
        "colors_enabled": False,
        "private_color_probe": False,
        "low_memory_rendering": True,
        "observer_fps_cap": 5,
        "preset": "redstation",
        "elapsed_s": 125.0,
        "private_guid_sidecars": {"person": "DO_NOT_PRINT"},
        "error": "sensitive test string that must never escape",
    }

class ComparabilityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.control = Path(self.tmp.name) / "control"
        self.candidate = Path(self.tmp.name) / "candidate"
        self.write(self.control, receipt(False), HARNESS)
        self.write(self.candidate, receipt(True), HARNESS)

    def write(self, folder, result, harness):
        folder.mkdir(exist_ok=True)
        (folder / "result.json").write_text(json.dumps(result), encoding="utf8")
        (folder / "source-sha256.json").write_text(json.dumps(harness), encoding="utf8")

    def edit(self, folder, name, key, value, remove=False):
        f = folder / name
        d = json.loads(f.read_text())
        if remove:
            d.pop(key, None)
        else:
            d[key] = value
        f.write_text(json.dumps(d))

    def assert_confounded(self, expected):
        result = compare_runs(self.control, self.candidate)
        self.assertEqual(result["verdict"], "CONFOUNDED")
        self.assertIn(expected, result["reasons"])
        self.assertEqual(result["release_qualification"], "NOT_ESTABLISHED")

    def test_explicit_one_flag_switch_same_dll_harness_and_config_is_comparable_only(self):
        r = compare_runs(self.control, self.candidate)
        self.assertEqual(r["verdict"], "CONTROLLED_TOGGLE_RECEIPTS_ONLY")
        self.assertEqual(r["reasons"], [])
        self.assertEqual(r["release_qualification"], "NOT_ESTABLISHED")
        text = json.dumps(r)
        self.assertNotIn("DO_NOT_PRINT", text)
        self.assertNotIn("sensitive test string", text)
        self.assertNotIn(str(self.control), text)

    def test_different_dll_not_clean_ab(self):
        self.edit(self.candidate, "result.json", "dll_sha256", HEX_B)
        self.assert_confounded("DLL_SHA256_MISMATCH")

    def test_colored_names_difference_not_clean_ab(self):
        self.edit(self.control, "result.json", "colors_enabled", True)
        self.assert_confounded("colors_enabled_MISMATCH")

    def test_harness_difference_not_clean_ab(self):
        self.edit(self.candidate, "source-sha256.json", "qualify_bot_sessions.py", HEX_B)
        self.assert_confounded("HARNESS_qualify_bot_sessions.py_MISMATCH")

    def test_missing_cecil_flag_never_inferred_off(self):
        self.edit(self.control, "result.json", "cecil_p1", None, remove=True)
        self.assert_confounded("CECIL_P1_NOT_EXPLICIT_OFF_ON")

    def test_no_flag_contrast_is_not_controlled(self):
        self.edit(self.candidate, "result.json", "cecil_p1", False)
        self.assert_confounded("CECIL_P1_NOT_EXPLICIT_OFF_ON")

    def test_non_native_scope_confounded(self):
        self.edit(self.candidate, "result.json", "scope", "SYNTHETIC_FIXTURE")
        self.assert_confounded("scope_MISMATCH_OR_NON_NATIVE")

    def test_missing_harness_file_fails_closed(self):
        self.edit(self.control, "source-sha256.json", "bot_sessions.py", None, remove=True)
        self.assert_confounded("HARNESS_bot_sessions.py_MISSING")

    def test_unrecognized_status_does_not_leak_private_text(self):
        self.edit(self.candidate, "result.json", "status", "PRIVATE_IP_OR_GUID_DO_NOT_PRINT")
        with self.assertRaises(ValueError):
            compare_runs(self.control, self.candidate)

    def test_bad_sha_invalid_input(self):
        self.edit(self.candidate, "result.json", "dll_sha256", "bad")
        with self.assertRaises(ValueError):
            compare_runs(self.control, self.candidate)

    def test_bad_json_invalid_input(self):
        (self.control / "result.json").write_text("{bad")
        with self.assertRaises(ValueError):
            compare_runs(self.control, self.candidate)

    def test_insufficient_population_rejected(self):
        self.edit(self.candidate, "result.json", "peak_playing", 1)
        self.assert_confounded("peak_playing_NOT_FOUR")

    def test_cli_exit_codes(self):
        self.assertEqual(main(["--control", str(self.control), "--candidate", str(self.candidate)]), 0)
        self.edit(self.candidate, "result.json", "dll_sha256", HEX_B)
        self.assertEqual(main(["--control", str(self.control), "--candidate", str(self.candidate)]), 3)
        self.edit(self.candidate, "result.json", "dll_sha256", "bad")
        self.assertEqual(main(["--control", str(self.control), "--candidate", str(self.candidate)]), 2)

if __name__ == "__main__":
    unittest.main()
