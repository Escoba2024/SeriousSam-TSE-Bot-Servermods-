"""Standalone synthetic Git regression suite; never modifies TSE worktrees."""
import importlib.util
import os
import pathlib
import subprocess
import tempfile
import unittest

import check_agent_scope as module

ALLOW = ("tools/autonomous-qa/", "docs/reports/autonomous-qa/")
LINK_TARGET = "../../poc/scripts/PopulationSupervisor.ps1"


class TestNonRegularGitObjects(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="tse-scope-probe-")
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "fixture"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "offline-test@example.invalid")
        self.git("config", "user.name", "Scope QA")
        (self.repo / "README.txt").write_text("baseline\n", encoding="utf-8")
        self.git("add", "README.txt")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.path = "tools/autonomous-qa/link-entry"

    def git(self, *args, data=None):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            input=data, capture_output=True, timeout=15,
            text=data is None,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def stage_link(self, mode):
        if mode == "120000":
            blob = self.git("hash-object", "-w", "--stdin",
                            data=LINK_TARGET.encode("utf-8")).stdout.decode().strip()
        else:
            blob = "1" * 40
        self.git("update-index", "--add", "--cacheinfo",
                 f"{mode},{blob},{self.path}")

    def assert_denied(self):
        allowed, denied = module.inspect(self.repo, self.base, ALLOW)
        self.assertNotIn(self.path, allowed)
        self.assertIn(self.path, denied)

    def test_staged_symlink_rejected(self):
        self.stage_link("120000")
        self.assert_denied()

    def test_committed_symlink_rejected(self):
        self.stage_link("120000")
        self.git("commit", "-qm", "symlink object")
        self.assert_denied()

    def test_staged_gitlink_rejected(self):
        self.stage_link("160000")
        self.assert_denied()

    def test_committed_gitlink_rejected(self):
        self.stage_link("160000")
        self.git("commit", "-qm", "gitlink object")
        self.assert_denied()

    def test_safe_regular_file_accepted(self):
        target = self.repo / self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("normal regular file\n", encoding="utf-8")
        self.git("add", self.path)
        allowed, denied = module.inspect(self.repo, self.base, ALLOW)
        self.assertIn(self.path, allowed)
        self.assertEqual(denied, [])

    def test_safe_committed_regular_file_accepted(self):
        target = self.repo / self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("normal regular file\n", encoding="utf-8")
        self.git("add", self.path)
        self.git("commit", "-qm", "regular")
        allowed, denied = module.inspect(self.repo, self.base, ALLOW)
        self.assertIn(self.path, allowed)
        self.assertEqual(denied, [])

    def test_untracked_regular_file_accepted(self):
        target = self.repo / self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("not added yet\n", encoding="utf-8")
        allowed, denied = module.inspect(self.repo, self.base, ALLOW)
        self.assertIn(self.path, allowed)
        self.assertEqual(denied, [])

    def test_untracked_symlink_rejected_when_windows_permits(self):
        target = self.repo / self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.symlink_to(LINK_TARGET)
        except (OSError, NotImplementedError):
            self.skipTest("Windows system does not allow creating symlinks in test user context")
        self.assert_denied()

    @unittest.skipUnless(os.name == 'nt', 'Requires a real Windows NTFS junction')
    def test_parent_junction_rejected(self):
        outside = self.repo.parent / 'outside-fixture'
        outside.mkdir()
        (outside / 'entry.txt').write_text('fixture only\n', encoding='utf-8')
        junction = self.repo / 'tools/autonomous-qa/redirect'
        junction.parent.mkdir(parents=True)
        created = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J',
                                  str(junction), str(outside)], capture_output=True, timeout=15)
        self.assertEqual(created.returncode, 0, created.stderr)
        self.addCleanup(junction.rmdir)
        self.assertFalse(junction.is_symlink(), 'Fixture must exercise a junction, not a symlink')
        path = 'tools/autonomous-qa/redirect/entry.txt'
        self.assertIn(path, module.object_mode_gate(self.repo, {path}))

    def test_conflict_index_stages_rejected(self):
        blob = self.git('hash-object', '-w', '--stdin', data=b'fixture\n').stdout.decode().strip()
        for stage in (1, 2, 3):
            with self.subTest(stage=stage):
                record = f'100644 {blob} {stage}\t{self.path}\n'.encode()
                self.git('update-index', '--index-info', data=record)
                self.assert_denied()

    def test_allowed_directory_replaced_by_regular_file(self):
        directory = self.repo / 'tools/autonomous-qa/swap'
        directory.mkdir(parents=True)
        child = directory / 'old.txt'
        child.write_text('old fixture\n', encoding='utf-8')
        self.git('add', '-A')
        self.git('commit', '-qm', 'directory fixture')
        base = self.git('rev-parse', 'HEAD').stdout.strip()
        child.unlink()
        directory.rmdir()
        directory.write_text('regular replacement\n', encoding='utf-8')
        self.git('add', '-A')
        self.git('commit', '-qm', 'regular replacement')
        allowed, denied = module.inspect(self.repo, base, ALLOW)
        self.assertEqual(denied, [])
        self.assertEqual(allowed, ['tools/autonomous-qa/swap', 'tools/autonomous-qa/swap/old.txt'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
