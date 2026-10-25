"""Synthetic byte fixtures only; no Retail content or native claims."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capture_gate", ROOT / "capture_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class CaptureGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest = {
            "schema": "tse-native-sync-capture/v1", "source_kind": "synthetic",
            "session_id": "session-fixture", "connection_id": "join-fixture",
            "level_id": "fixture-map", "level_epoch": 1,
            "map": self.artifact("map.fixture", b"map"),
            "config": self.artifact("config.fixture", b"config"),
            "tick_unit": "engine_tick_index",
            "window": {"first_sequence": 10, "last_sequence": 12,
                       "first_tick": 100, "tick_step": 1},
            "layout": {"id": "synthetic-layout", "phase": "before_sync_crc",
                       "players": ["slot0"], "action_bytes": 2,
                       "state_fields": {"session": 2, "entity": 2},
                       "binding_status": "synthetic", "evidence": self.artifact("layout.txt", b"fixture only")},
            "producer": {"id": "fixture-producer", "version": "1",
                         "artifact": self.artifact("producer.txt", b"fixture producer")},
            "participants": {},
        }
        self.rows = {}
        for role in ("server", "client"):
            self.rows[role] = [
                {"session_id": "session-fixture", "connection_id": "join-fixture",
                 "level_epoch": 1, "sequence": seq, "tick": seq + 90,
                 "crc32": "12345678", "actions": {"slot0": "0001"},
                 "state": {"session": "0100", "entity": "0200"}}
                for seq in range(10, 13)]
            self.manifest["participants"][role] = {
                "capture_id": role + "-fixture", "dropped_records": 0,
                "complete": True, "binaries": {
                    component: self.artifact(role + component + ".bin", component.encode())
                    for component in ("executable", "engine", "gamemp", "entities")}}

    def artifact(self, name, data):
        (self.root / name).write_bytes(data)
        return {"path": name, "sha256": sha(data)}

    def write(self):
        for role in self.manifest.get("participants", {}):
            data = "".join(json.dumps(row) + "\n" for row in self.rows[role]).encode()
            self.manifest["participants"][role]["records"] = self.artifact(role + ".jsonl", data)
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest))
        return path

    def compare(self):
        return gate.compare_capture(self.write())

    def blocked(self, code=None):
        result = self.compare()
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertNotIn("first_observed_difference", result)
        self.assertEqual(result["retail_runtime"], "NOT_TESTED")
        if code:
            self.assertIn(code, [issue["code"] for issue in result["issues"]], result)

    def test_identical_synthetic_window(self):
        result = self.compare()
        self.assertEqual(result["status"], "MATCHED_WINDOW", result)
        self.assertEqual(result["pairs_compared"], 3)
        self.assertEqual(result["source_kind"], "synthetic")
        self.assertEqual(result["retail_runtime"], "NOT_TESTED")
        self.assertIn("manifest_sha256", result["provenance"])
        self.assertNotIn("first_divergent_tick", result)

    def test_crc_action_state_difference_no_values_disclosed(self):
        row = self.rows["client"][1]
        row["crc32"] = "deadbeef"
        row["actions"]["slot0"] = "fffe"
        row["state"]["entity"] = "aabb"
        result = self.compare()
        self.assertEqual(result["status"], "DIFFERENT_WINDOW", result)
        self.assertEqual(result["pairs_compared"], 3)
        first = result["first_observed_difference"]
        self.assertEqual(first["sequence"], 11)
        self.assertEqual(first["tick"], 101)
        self.assertEqual(first["domains"], ["crc32", "actions", "state"])
        self.assertEqual(first["previous_pair_matched"], True)
        self.assertNotIn("deadbeef", json.dumps(result))
        self.assertNotIn("aabb", json.dumps(result))

    def test_start_difference_has_no_previous_boundary(self):
        self.rows["client"][0]["crc32"] = "00000000"
        result = self.compare()
        self.assertFalse(result["first_observed_difference"]["previous_pair_matched"])

    def test_state_difference_even_when_crc_equal(self):
        self.rows["client"][2]["state"]["entity"] = "aabb"
        result = self.compare()
        self.assertEqual(result["first_observed_difference"]["domains"], ["state"])

    def test_missing_crc(self):
        del self.rows["client"][1]["crc32"]
        self.blocked("RECORD_SCHEMA")

    def test_missing_middle_pair_blocks_even_with_later_difference(self):
        self.rows["client"].pop(1)
        self.rows["client"][-1]["crc32"] = "00000000"
        self.blocked("COVERAGE")

    def test_invalid_tail_blocks_even_after_early_difference(self):
        self.rows["client"][0]["crc32"] = "00000000"
        self.rows["client"][2]["state"]["entity"] = ""
        self.blocked("RECORD_SCHEMA")

    def test_bad_crc_is_not_partial_comparison(self):
        for value in (None, "0x12345678", "123", 12345678):
            with self.subTest(value=value):
                self.rows["client"][1]["crc32"] = value
                self.blocked("RECORD_SCHEMA")

    def test_unmatched_extra_record_and_wrong_tick(self):
        self.rows["client"].append(copy.deepcopy(self.rows["client"][-1]))
        self.blocked("COVERAGE")
        self.rows["client"].pop()
        self.rows["client"][1]["tick"] = 102
        self.blocked("ALIGNMENT")

    def test_both_sides_same_gap_blocks(self):
        for role in self.rows:
            self.rows[role].pop(1)
        self.blocked("COVERAGE")

    def test_duplicate_key_not_silently_overwritten(self):
        self.rows["client"].append(copy.deepcopy(self.rows["client"][1]))
        self.blocked("COVERAGE")

    def test_reordered_records(self):
        self.rows["client"].reverse()
        self.blocked("ALIGNMENT")

    def test_cross_session_connection_epoch(self):
        for key, value in (("session_id", "other"), ("connection_id", "rejoined"), ("level_epoch", 2)):
            with self.subTest(key=key):
                saved = self.rows["client"][0][key]
                self.rows["client"][0][key] = value
                self.blocked("ALIGNMENT")
                self.rows["client"][0][key] = saved

    def test_tick_not_float_wallclock_or_boolean(self):
        for value in (100.0, "100", True):
            with self.subTest(value=value):
                self.rows["client"][0]["tick"] = value
                self.blocked("RECORD_SCHEMA")

    def test_empty_or_unexpected_action_and_state_fields(self):
        for domain, value in (("actions", {}), ("state", {}),
                              ("actions", {"slot0": ""}),
                              ("state", {"session": "00", "entity": "zz"}),
                              ("state", {"session": "00", "entity": "00", "unknown": "00"})):
            with self.subTest(domain=domain, value=value):
                saved = self.rows["client"][0][domain]
                self.rows["client"][0][domain] = value
                self.blocked("RECORD_SCHEMA")
                self.rows["client"][0][domain] = saved

    def test_capture_must_be_complete_and_no_drops(self):
        for field, value in (("complete", False), ("complete", 1), ("dropped_records", 1)):
            with self.subTest(field=field):
                original = self.manifest["participants"]["client"][field]
                self.manifest["participants"]["client"][field] = value
                self.blocked("CAPTURE_INCOMPLETE")
                self.manifest["participants"]["client"][field] = original

    def test_binary_hash_mismatch(self):
        self.manifest["participants"]["client"]["binaries"]["engine"]["sha256"] = "0" * 64
        self.blocked("HASH_MISMATCH")

    def test_different_engine_between_roles(self):
        self.manifest["participants"]["client"]["binaries"]["engine"] = self.artifact("other.bin", b"other engine")
        self.blocked("SHARED_BINARY_MISMATCH")

    def test_candidate_gamemp_may_differ_from_vanilla(self):
        self.manifest["participants"]["client"]["binaries"]["gamemp"] = self.artifact("candidate.bin", b"candidate")
        self.assertEqual(self.compare()["status"], "MATCHED_WINDOW")

    def test_missing_binding_native_source(self):
        self.manifest["source_kind"] = "native"
        self.blocked("UNVERIFIED_BINDING")

    def test_native_label_is_never_native_acceptance(self):
        self.manifest["source_kind"] = "native"
        self.manifest["layout"]["binding_status"] = "verified-retail107"
        result = self.compare()
        self.assertEqual(result["status"], "MATCHED_WINDOW")
        self.assertEqual(result["retail_runtime"], "NOT_TESTED")
        self.assertIn("attestation", result["limitations"])

    def test_wrong_phase_or_tick_unit(self):
        self.manifest["layout"]["phase"] = "wallclock"
        self.blocked("MANIFEST_SCHEMA")
        self.manifest["layout"]["phase"] = "before_sync_crc"
        self.manifest["tick_unit"] = "bot_counter"
        self.blocked("MANIFEST_SCHEMA")

    def test_empty_manifest_and_missing_binary(self):
        saved = copy.deepcopy(self.manifest)
        self.manifest = {}
        self.blocked("MANIFEST_SCHEMA")
        self.manifest = saved
        del self.manifest["participants"]["server"]["binaries"]["entities"]
        self.blocked("MANIFEST_SCHEMA")

    def test_path_escape_and_missing_artifact(self):
        self.manifest["layout"]["evidence"]["path"] = "../elsewhere"
        self.blocked("ARTIFACT_PATH")
        self.manifest["layout"]["evidence"]["path"] = "missing.txt"
        self.blocked("ARTIFACT_IO")

    def test_nul_path_and_nonregular_artifact(self):
        self.manifest["layout"]["evidence"]["path"] = "nul\u0000file"
        self.blocked("ARTIFACT_PATH")
        self.manifest["layout"]["evidence"]["path"] = "."
        self.blocked("ARTIFACT_IO")

    def test_empty_provenance_artifact(self):
        self.manifest["layout"]["evidence"] = self.artifact("empty", b"")
        self.blocked("ARTIFACT_EMPTY")

    def test_artifact_tampering(self):
        path = self.write()
        (self.root / "client.jsonl").write_text("{}\n")
        result = gate.compare_capture(path)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["issues"][0]["code"], "HASH_MISMATCH")

    def test_truncated_action_and_state_bytes(self):
        self.rows["client"][0]["actions"]["slot0"] = "00"
        self.blocked("RECORD_SCHEMA")
        self.rows["client"][0]["actions"]["slot0"] = "0001"
        self.rows["client"][0]["state"]["entity"] = "02"
        self.blocked("RECORD_SCHEMA")

    def test_duplicate_record_json_key(self):
        path = self.write()
        data = (self.root / "client.jsonl").read_bytes().replace(b'"tick": 100', b'"tick": 100, "tick": 100', 1)
        self.manifest["participants"]["client"]["records"] = self.artifact("client.jsonl", data)
        path.write_text(json.dumps(self.manifest))
        self.assertEqual(gate.compare_capture(path)["issues"][0]["code"], "JSON_INVALID")

    def test_case_insensitive_hex_bytes(self):
        self.rows["client"][0]["actions"]["slot0"] = "abCD"
        self.rows["server"][0]["actions"]["slot0"] = "ABcd"
        self.assertEqual(self.compare()["status"], "MATCHED_WINDOW")

    def test_duplicate_json_key_and_malformed_json(self):
        path = self.write()
        path.write_text('{"schema": 1, "schema": 2}')
        self.assertEqual(gate.compare_capture(path)["status"], "BLOCKED")
        path.write_text('{')
        self.assertEqual(gate.compare_capture(path)["status"], "BLOCKED")

    def test_nonfinite_and_unknown_record_key(self):
        self.rows["client"][0]["tick"] = float("nan")
        self.blocked("JSON_INVALID")
        self.rows["client"][0]["tick"] = 100
        self.rows["client"][0]["unknown"] = "unexpected"
        self.blocked("RECORD_SCHEMA")

    def test_manifest_identity_layout_required(self):
        for field in ("session_id", "connection_id", "level_id", "map", "config", "producer"):
            with self.subTest(field=field):
                saved = self.manifest.pop(field)
                self.blocked("MANIFEST_SCHEMA")
                self.manifest[field] = saved

    def test_empty_window_layout_duplicates_and_oversized_window(self):
        self.manifest["window"]["last_sequence"] = 9
        self.blocked("MANIFEST_SCHEMA")
        self.manifest["window"]["last_sequence"] = 10**12
        self.blocked("MANIFEST_SCHEMA")
        self.manifest["window"]["last_sequence"] = 12
        self.manifest["layout"]["players"] = ["slot0", "slot0"]
        self.blocked("MANIFEST_SCHEMA")

    def test_cli_exit_codes_json_only_and_no_input_mutation(self):
        path = self.write()
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        for expected in (0, 3, 2):
            if expected == 3:
                self.rows["client"][1]["crc32"] = "00000000"
                path = self.write()
            elif expected == 2:
                self.rows["client"].pop()
                path = self.write()
            expected_files = {p.name: p.read_bytes() for p in self.root.iterdir()}
            result = subprocess.run([sys.executable, "-B", str(ROOT / "capture_gate.py"), str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)
            self.assertEqual(expected_files, {p.name: p.read_bytes() for p in self.root.iterdir()})
        self.rows["client"] = copy.deepcopy(self.rows["server"])
        self.write()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_synthetic_example_cli_and_refuse_existing_destination(self):
        destination = self.root / "example"
        command = [sys.executable, "-B", str(ROOT / "make_synthetic_bundle.py"), str(destination)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(gate.compare_capture(destination / "manifest.json")["status"], "MATCHED_WINDOW")
        self.assertEqual(gate.compare_capture(destination / "manifest.json")["source_kind"], "synthetic")
        retry = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(retry.returncode, 0)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "evidence"
            outside.write_bytes(b"fixture only")
            (self.root / "escaped").symlink_to(outside)
            self.manifest["layout"]["evidence"]["path"] = "escaped"
            self.blocked("ARTIFACT_PATH")


if __name__ == "__main__":
    unittest.main()
