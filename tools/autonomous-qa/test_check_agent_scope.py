"""Self-contained synthetic Git tests; never touch an existing TSE repository."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_agent_scope import ScopeError, inspect, valid_path


ALLOW = ("tools/autonomous-qa/", "docs/reports/autonomous-qa/")


class AgentCommitScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tse-agent-scope-")
        self.addCleanup(self.temp.cleanup)
        self.repo = pathlib.Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "qa-fixture@example.invalid")
        self.git("config", "user.name", "QA Fixture")
        self.make("README.md", "baseline\n")
        self.git("add", "README.md")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            text=True, capture_output=True, timeout=15
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def make(self, name, content="example\n"):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def check(self):
        return inspect(self.repo, self.base, ALLOW)

    def test_allowed_untracked_new_test_file(self):
        self.make("tools/autonomous-qa/new test.py")
        allowed, denied = self.check()
        self.assertEqual(allowed, ["tools/autonomous-qa/new test.py"])
        self.assertEqual(denied, [])

    def test_lookalike_directory_rejected(self):
        self.make("tools/autonomous-qa-unsafe/fake.py")
        self.assertEqual(self.check()[1], ["tools/autonomous-qa-unsafe/fake.py"])

    def test_critical_gamefile_rejected(self):
        self.make("poc/scripts/PopulationSupervisor.ps1")
        self.assertEqual(self.check()[1], ["poc/scripts/PopulationSupervisor.ps1"])

    def test_staged_allowed_path(self):
        self.make("docs/reports/autonomous-qa/evidence.md")
        self.git("add", "-A")
        self.assertFalse(self.check()[1])

    def test_staged_rename_catches_original_path(self):
        self.make("poc/scripts/PopulationSupervisor.ps1")
        self.git("add", "-A")
        self.git("commit", "-qm", "original outside scope")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.make("tools/autonomous-qa/placeholder", "x")
        self.git("mv", "poc/scripts/PopulationSupervisor.ps1",
                 "tools/autonomous-qa/renamed.ps1")
        allowed, denied = self.check()
        self.assertIn("poc/scripts/PopulationSupervisor.ps1", denied)
        self.assertIn("tools/autonomous-qa/renamed.ps1", allowed)

    def test_committed_allowed_path(self):
        self.make("tools/autonomous-qa/committed.py")
        self.git("add", "-A")
        self.git("commit", "-qm", "new scoped fixture")
        self.assertEqual(self.check()[1], [])

    def test_committed_unauthorized_path(self):
        self.make("Engine.dll", "do not touch")
        self.git("add", "-A")
        self.git("commit", "-qm", "out of scope")
        self.assertEqual(self.check()[1], ["Engine.dll"])

    def test_missing_base_fails_closed(self):
        with self.assertRaises(ScopeError):
            inspect(self.repo, "does-not-exist", ALLOW)

    def test_nonroot_repo_path_fails_closed(self):
        (self.repo / "subdir").mkdir()
        with self.assertRaises(ScopeError):
            inspect(self.repo / "subdir", self.base, ALLOW)

    def test_prefix_traversal_fails_closed(self):
        with self.assertRaises(ScopeError):
            inspect(self.repo, self.base, ("tools/../poc/",))

    def test_empty_prefixes_fails_closed(self):
        with self.assertRaises(ScopeError):
            inspect(self.repo, self.base, ())

    def test_path_traversal_rejected(self):
        self.assertFalse(valid_path("tools/autonomous-qa/../secret", ALLOW))
        self.assertFalse(valid_path("tools/autonomous-qa-evil/hack", ALLOW))
        self.assertFalse(valid_path("C:\\Windows\\secret", ALLOW))


if __name__ == "__main__":
    unittest.main()
