"""Disposable files and synthetic /proc only; never query or run a game."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("external_vanilla_preflight.py")
COMPONENTS = ("SeriousSam.exe", "GameMP.dll", "Engine.dll", "EntitiesMP.dll")


class ExternalVanillaPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = None
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location("external_preflight", SCRIPT)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def setUp(self):
        self.assertIsNotNone(self.module, "Linux preflight is not implemented")
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name); self.observer = self.base / "observer"
        (self.observer / "Bin").mkdir(parents=True)
        self.proc = self.base / "proc"; self.proc.mkdir()
        entries = []
        for name in COMPONENTS:
            content = ("original-" + name).encode()
            (self.observer / "Bin" / name).write_bytes(content)
            entries.append({"Path": "C:\\OriginalRetail\\Bin\\" + name,
                            "Hash": hashlib.sha256(content).hexdigest().upper()})
        self.entries = entries
        self.manifest = self.base / "manifest.json"
        self.manifest.write_text(json.dumps(entries), encoding="utf-8-sig")
        self.status = {"gamename": "serioussamse", "gamever": "1.07", "hostport": "25650",
                       "numplayers": "1", "player_0": "Dev-1", "dedicatedserver": "yes", "activemod": ""}

    def check(self, **kwargs):
        scanner = self.module.scan_occupancy
        # Replace only the /proc and UDP boundaries; execute real scanning,
        # manifest validation, hashing and the public preflight decision.
        with patch.object(self.module, "scan_occupancy", side_effect=lambda root: scanner(root, self.proc)), \
             patch.object(self.module, "query", return_value=self.status):
            return self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650, **kwargs)

    def process(self, cwd=None, argv=b"wine\0Bin/SeriousSam.exe\0", maps=None, comm="SeriousSam.exe"):
        root = self.proc / "123"; root.mkdir()
        (root / "cmdline").write_bytes(argv); (root / "comm").write_text(comm + "\n")
        (root / "cwd").symlink_to(cwd or self.observer, target_is_directory=True)
        (root / "stat").write_text("123 (Serious Sam) S " + "0 " * 18 + "12345 0\n")
        (root / "maps").write_text(maps or "1000-2000 r-xp 0 00:00 0 /unrelated/Engine.dll\n")
        return root

    def test_live_ready_requires_four_originals_clear_processes_and_exact_bot(self):
        result = self.check()
        self.assertTrue(result["canStart"])
        self.assertEqual(result["status"], "READY_AT_CHECK_TIME")
        self.assertEqual(result["filesVerified"], 4)
        self.assertTrue(result["live"])
        self.assertFalse(result["simulated"])
        self.assertIn("checkedUtc", result)

    def test_missing_or_changed_binary_blocks(self):
        for remove in (False, True):
            with self.subTest(remove=remove):
                path = self.observer / "Bin/GameMP.dll"
                if remove: path.unlink()
                else: path.write_bytes(b"changed")
                result = self.check()
                self.assertFalse(result["canStart"])
                self.assertEqual(result["filesVerified"], 3)

    def test_invalid_incomplete_duplicate_or_unexpected_manifest_blocks(self):
        malformed = [self.entries[:3], self.entries + self.entries[:1],
                     self.entries[:3] + [dict(self.entries[0])],
                     self.entries[:3] + [{"Path": "Unknown.dll", "Hash": "a" * 64}],
                     self.entries[:3] + [{"Path": "EntitiesMP.dll", "Hash": "invalid"}],
                     {"files": self.entries}]
        for entries in malformed:
            with self.subTest(entries=entries):
                self.manifest.write_text(json.dumps(entries))
                self.assertFalse(self.check()["canStart"])
        self.manifest.unlink()
        self.assertFalse(self.check()["canStart"])

    def test_wrong_game_version_port_dedicated_or_mod_blocks(self):
        for key, value in (("gamename", "other"), ("gamever", "1.10"), ("hostport", "25600"),
                           ("dedicatedserver", "no"), ("activemod", "Cecil"), ("player_0", "Other")):
            original = self.status[key]; self.status[key] = value
            with self.subTest(key=key): self.assertFalse(self.check()["canStart"])
            self.status[key] = original
        self.status.pop("activemod")
        self.assertFalse(self.check()["canStart"])

    def test_extra_human_or_inconsistent_player_count_blocks(self):
        for extra in ({"numplayers": "2", "player_1": "Human"}, {"player_1": "Human"},
                      {"player_2": "Human"}, {"numplayers": "0"}):
            original = dict(self.status); self.status.update(extra)
            with self.subTest(extra=extra): self.assertFalse(self.check()["canStart"])
            self.status = original

    def test_occupied_cwd_or_executable_mapping_blocks(self):
        self.process()
        self.assertFalse(self.check()["canStart"])
        (self.proc / "123/cwd").unlink(); (self.proc / "123/cwd").symlink_to(self.base)
        (self.proc / "123/maps").write_text("1000-2000 r-xp 0 00:00 0 " + str(self.observer / "Bin/SeriousSam.exe") + "\n")
        self.assertFalse(self.check()["canStart"])

    def test_other_installation_is_not_occupied(self):
        self.process(cwd=self.base)
        self.assertTrue(self.check()["canStart"])

    def test_windows_absolute_command_path_detects_occupancy_from_other_cwd(self):
        exe = "Z:" + str(self.observer / "Bin/SeriousSam.exe").replace("/", "\\")
        self.process(cwd=self.base, argv=b"wine\0" + exe.encode() + b"\0")
        self.assertFalse(self.check()["canStart"])

    def test_unreadable_relevant_process_fails_closed(self):
        proc = self.process(cwd=self.base)
        (proc / "maps").unlink()
        self.assertFalse(self.check()["canStart"])
        (proc / "cmdline").unlink()
        self.assertFalse(self.check()["canStart"])

    def test_permission_denied_on_relevant_command_or_maps_blocks(self):
        proc = self.process(cwd=self.base)
        original_bytes, original_text = Path.read_bytes, Path.read_text
        def read_bytes(path, *args, **kwargs):
            if path == proc / "cmdline": raise PermissionError("synthetic inaccessible command")
            return original_bytes(path, *args, **kwargs)
        def read_text(path, *args, **kwargs):
            if path == proc / "maps": raise PermissionError("synthetic inaccessible mappings")
            return original_text(path, *args, **kwargs)
        with patch.object(Path, "read_bytes", read_bytes):
            self.assertFalse(self.check()["canStart"])
        with patch.object(Path, "read_text", read_text):
            self.assertFalse(self.check()["canStart"])

    def test_query_failure_blocks(self):
        scanner = self.module.scan_occupancy
        with patch.object(self.module, "scan_occupancy", side_effect=lambda root: scanner(root, self.proc)), \
             patch.object(self.module, "query", side_effect=RuntimeError("offline timeout")):
            result = self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650)
        self.assertFalse(result["canStart"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_real_gamespy_timeout_is_reported_as_blocked_json(self):
        from gamespy_query import QueryError
        scanner = self.module.scan_occupancy
        with patch.object(self.module, "scan_occupancy", side_effect=lambda root: scanner(root, self.proc)), \
             patch.object(self.module, "query", side_effect=QueryError("no answer")):
            result = self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650)
        self.assertFalse(result["canStart"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_binary_change_during_query_blocks(self):
        scanner = self.module.scan_occupancy
        def response(*args, **kwargs):
            (self.observer / "Bin/Engine.dll").write_bytes(b"changed during query")
            return self.status
        with patch.object(self.module, "scan_occupancy", side_effect=lambda root: scanner(root, self.proc)), \
             patch.object(self.module, "query", side_effect=response):
            result = self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650)
        self.assertFalse(result["canStart"])

    def test_process_start_during_query_blocks(self):
        scanner = self.module.scan_occupancy
        def response(*args, **kwargs):
            self.process()
            return self.status
        with patch.object(self.module, "scan_occupancy", side_effect=lambda root: scanner(root, self.proc)), \
             patch.object(self.module, "query", side_effect=response):
            result = self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650)
        self.assertFalse(result["canStart"])

    def test_status_fixture_and_synthetic_proc_never_authorize_launch(self):
        fixture = self.base / "status.txt"
        fixture.write_text("".join("\\" + k + "\\" + v for k, v in self.status.items()))
        result = self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650,
                                             status_fixture=fixture, proc_root=self.proc)
        self.assertEqual(result["status"], "FIXTURE_MATCH_ONLY")
        self.assertFalse(result["canStart"])
        self.assertTrue(result["simulated"])
        self.assertFalse(result["live"])
        result = self.check(status_fixture=fixture)
        self.assertFalse(result["canStart"])
        self.assertTrue(result["simulated"])
        with patch.object(self.module, "query", return_value=self.status):
            result = self.module.check_preflight(self.observer, self.manifest, "127.0.0.1", 25651, 25650,
                                                 proc_root=self.proc)
        self.assertFalse(result["canStart"])
        self.assertTrue(result["simulated"])

    def test_cli_fixture_is_json_and_cannot_start(self):
        fixture = self.base / "status.txt"
        fixture.write_text("".join("\\" + k + "\\" + v for k, v in self.status.items()))
        args = [sys.executable, "-B", str(SCRIPT), "--observer-dir", str(self.observer),
                "--manifest", str(self.manifest), "--server", "127.0.0.1", "--query-port", "25651",
                "--game-port", "25650", "--status-fixture", str(fixture), "--proc-root", str(self.proc)]
        process = subprocess.run(args, capture_output=True, text=True)
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(result["status"], "FIXTURE_MATCH_ONLY")
        self.assertFalse(result["canStart"])

    def test_cli_does_not_write_import_caches_without_python_B_flag(self):
        scripts = self.base / "scripts"; scripts.mkdir()
        for source in (SCRIPT, SCRIPT.with_name("gamespy_query.py")):
            (scripts / source.name).write_bytes(source.read_bytes())
        fixture = self.base / "status.txt"
        fixture.write_text("".join("\\" + k + "\\" + v for k, v in self.status.items()))
        before = sorted(str(p.relative_to(self.base)) for p in self.base.rglob("*"))
        process = subprocess.run([sys.executable, str(scripts / SCRIPT.name),
                                  "--observer-dir", str(self.observer), "--manifest", str(self.manifest),
                                  "--server", "127.0.0.1", "--query-port", "25651", "--game-port", "25650",
                                  "--status-fixture", str(fixture), "--proc-root", str(self.proc)],
                                 capture_output=True, text=True)
        self.assertFalse(json.loads(process.stdout)["canStart"])
        self.assertEqual(sorted(str(p.relative_to(self.base)) for p in self.base.rglob("*")), before)


if __name__ == "__main__":
    unittest.main()
