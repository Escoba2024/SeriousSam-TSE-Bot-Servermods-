"""Fail-closed safeguards for the experimental Retail sync-handler reachability probe."""
import unittest
from pathlib import Path
from native_sync_handler_probe import validate_binding, summarize_observation, find_pinned_engine_entry, summarize_server_operands, run, ProbeBlocked

ROOT = Path("/srv/tse-session-qualification-master-sync-20261026")

def baseline():
    return (
        dict(status="MEASURING", scope="ISOLATED_NETNS_RETAIL_WINE",
             network_namespace="net:[4026532999]", cgroup="/sys/fs/cgroup/tse-sessions-20261026"),
        dict(pid=901, uid=65534, comm="DedicatedServer", cwd=str(ROOT / "server"),
             netns="net:[4026532999]", cgroup="0::/tse-sessions-20261026",
             start_ticks=830123),
        "net:[4026532000]",
        "b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f",
    )

class GuardTest(unittest.TestCase):
    def binding(self, *, change_result=None, change_record=None, host_ns=None, hash_value=None, root=ROOT):
        report, record, known_host, verified_hash = baseline()
        report.update(change_result or {})
        record.update(change_record or {})
        return validate_binding(root, report, record,
                                known_host if host_ns is None else host_ns,
                                verified_hash if hash_value is None else hash_value)

    def blocked(self, code, **kwargs):
        with self.assertRaisesRegex(ProbeBlocked, code):
            self.binding(**kwargs)

    def test_private_valid_metadata_admitted_without_runtime_claim(self):
        self.assertTrue(self.binding())

    def test_rejects_stale_status(self):
        self.blocked("ACTIVE", change_result=dict(status="PASS_LIMITED_SESSION_LIFECYCLE"))

    def test_rejects_fake_scope(self):
        self.blocked("ACTIVE", change_result=dict(scope="FIXTURE"))

    def test_rejects_public_namespace(self):
        self.blocked("PRIVATE_NETNS", host_ns="net:[4026532999]")

    def test_rejects_namespace_mismatch(self):
        self.blocked("PRIVATE_NETNS", change_record=dict(netns="net:[4026537777]"))

    def test_rejects_server_role_swapped_for_client(self):
        self.blocked("OWNED_SERVER", change_record=dict(comm="SeriousSam.exe"))

    def test_rejects_cwd_forgery(self):
        self.blocked("OWNED_SERVER", change_record=dict(cwd="/srv/tse-experimental-public-20261025/runtime/server"))

    def test_rejects_wrong_uid(self):
        self.blocked("OWNED_SERVER", change_record=dict(uid=0))

    def test_rejects_missing_process_epoch(self):
        self.blocked("PROCESS_EPOCH", change_record=dict(start_ticks=None))

    def test_rejects_wrong_cgroup(self):
        self.blocked("PROCESS_CGROUP", change_record=dict(cgroup="0::/other"))

    def test_rejects_mismatched_engine_hash(self):
        self.blocked("ENGINE_HASH", hash_value="f" * 64)

    def test_rejects_root_outside_owned_sandbox(self):
        self.blocked("PRIVATE_ROOT", root=Path("/srv/tse-experimental-public-20261025"))

    def test_pinned_engine_target_resolution_from_wine_maps(self):
        maps = ("600c0000-600fe000 r-xp 00000000 00:42 1559826 /private/server/Bin/Engine.dll\n"
                "601a0000-60254000 r-xp 000e0000 00:42 1559826 /private/server/Bin/Engine.dll\n")
        self.assertEqual(find_pinned_engine_entry(maps, "/private/server/Bin/Engine.dll"), 0x601a2d10)

    def test_wrong_mapping_path_or_non_executable_blocked(self):
        maps = "601a0000-60254000 r--p 000e0000 00:42 1559826 /foreign/Bin/Engine.dll\n"
        with self.assertRaisesRegex(ProbeBlocked, "ENGINE_MAPPING"):
            find_pinned_engine_entry(maps, "/private/server/Bin/Engine.dll")

    def test_missing_offset_zero_mapping_blocked(self):
        maps = "601a0000-60254000 r-xp 000e0000 00:42 1559826 /private/server/Bin/Engine.dll\n"
        with self.assertRaisesRegex(ProbeBlocked, "ENGINE_MAPPING"):
            find_pinned_engine_entry(maps, "/private/server/Bin/Engine.dll")

    def test_wine_pe_discontinuous_file_offsets_do_not_invalidate_image(self):
        # Native Wine maps may have PE section gaps: mapping offset is NOT
        # necessarily identical to RVA for every segment after image base.
        maps = ("600c0000-600fe000 r-xp 00000000 00:42 1559826 /private/server/Bin/Engine.dll\n"
                "601a0000-60254000 r-xp 000e0000 00:42 1559826 /private/server/Bin/Engine.dll\n"
                "602d5000-602d6000 rwxp 001f1000 00:42 1559826 /private/server/Bin/Engine.dll\n")
        self.assertEqual(find_pinned_engine_entry(maps, "/private/server/Bin/Engine.dll"), 0x601a2d10)

    def test_conflicting_engine_map_inode_blocked(self):
        maps = ("600c0000-600fe000 r-xp 00000000 00:42 1559826 /private/server/Bin/Engine.dll\n"
                "601a0000-60254000 r-xp 000e0000 00:42 9999999 /private/server/Bin/Engine.dll\n")
        with self.assertRaisesRegex(ProbeBlocked, "ENGINE_MAPPING"):
            find_pinned_engine_entry(maps, "/private/server/Bin/Engine.dll")

    def test_conflicting_image_bases_blocked(self):
        maps = ("600c0000-600fe000 r-xp 00000000 00:42 1559826 /private/server/Bin/Engine.dll\n"
                "610c0000-610fe000 r-xp 00000000 00:42 1559826 /private/server/Bin/Engine.dll\n"
                "601a0000-60254000 r-xp 000e0000 00:42 1559826 /private/server/Bin/Engine.dll\n")
        with self.assertRaisesRegex(ProbeBlocked, "ENGINE_MAPPING"):
            find_pinned_engine_entry(maps, "/private/server/Bin/Engine.dll")

    def test_native_register_operands_remain_server_only(self):
        rows = [
            {"event": "level_operands", "lhs": 4, "rhs": 4, "tag": 1},
            {"event": "crc_operands", "lhs": 0x1234, "rhs": 0x1234, "tag": 1},
            {"event": "level_operands", "lhs": 5, "rhs": 5, "tag": 1},
            {"event": "crc_operands", "lhs": 0x1234, "rhs": 0x5678, "tag": 1},
        ]
        report = summarize_server_operands(rows)
        self.assertEqual(report["server_crc_comparisons"], 2)
        self.assertEqual(report["server_crc_mismatches"], 1)
        self.assertEqual(report["status"], "SERVER_OPERANDS_ONLY")
        self.assertEqual(report["native_crc_causation"], "NOT_ESTABLISHED")
        self.assertEqual(report["release_qualification"], "NOT_ESTABLISHED")
        self.assertNotIn("4660", str(report))  # 0x1234 raw operand not leaked.

    def test_missing_operand_evidence_does_not_get_promoted(self):
        report = summarize_server_operands([])
        self.assertEqual(report["status"], "NO_CRC_OPERANDS_CAPTURED")
        self.assertEqual(report["server_crc_comparisons"], 0)

    def test_invalid_crc_operands_cannot_be_promoted(self):
        with self.assertRaisesRegex(ProbeBlocked, "OPERAND"):
            summarize_server_operands([{"event": "crc_operands", "lhs": -1, "rhs": 0}])

    def test_unsafe_comparison_instrumentation_rejected_before_process_access(self):
        with self.assertRaisesRegex(ProbeBlocked, "COMPARISON_HOOK_DISABLED_AFTER_CRASH"):
            run(ROOT, 901, 20, comparisons=True)

    def test_never_grants_crc_or_release_even_with_handler_hits(self):
        report = summarize_observation(221, 30.1, True)
        self.assertEqual(report["status"], "HANDLER_REACHED_ONLY")
        self.assertEqual(report["native_crc_causation"], "NOT_ESTABLISHED")
        self.assertEqual(report["release_qualification"], "NOT_ESTABLISHED")
        self.assertNotIn("COMPLETE", str(report))

    def test_empty_observation_is_not_success(self):
        self.assertEqual(summarize_observation(0, 30.1, True)["status"], "NO_HANDLER_REACHABILITY_PROVEN")

    def test_detach_failure_does_not_pass(self):
        self.assertEqual(summarize_observation(999, 15.0, False)["status"], "PROBE_FAILED")

if __name__ == "__main__":
    unittest.main()
