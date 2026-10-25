"""Shared helpers for the sync-hypothesis-validation test suite.

No third-party dependencies, no network, no game files. Fixtures are generated
on demand by ``tools/make_synthetic_cases.py``.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

# Structural claim guards. Prose may legitimately say "this is not a stability
# pass", so the check looks at machine-readable claim fields only.
FALSE_CLAIM_KEYS = ("root_cause_confirmed", "stability_pass", "native_acceptance",
                    "acceptance_passed", "is_pass")


def run_tool(name: str, *args: str) -> subprocess.CompletedProcess:
    """Run a tool as a user would, returning the completed process."""
    return subprocess.run(
        [sys.executable, str(TOOLS / name), *args],
        capture_output=True, text=True, timeout=120,
    )


def run_json(name: str, *args: str):
    """Run a tool and parse stdout as JSON; returns (payload, exit_code)."""
    result = run_tool(name, *args)
    if not result.stdout.strip():
        raise AssertionError("%s produced no stdout (exit %d): %s"
                             % (name, result.returncode, result.stderr))
    return json.loads(result.stdout), result.returncode


class FixtureDir:
    """Context manager generating the synthetic fixture tree once."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="syncval-fixtures-")
        self.path = Path(self._tmp.name) / "fixtures"
        _generate(self.path)

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, *exc_info) -> None:
        self._tmp.cleanup()


def _generate(path: Path) -> None:
    sys.path.insert(0, str(TOOLS))
    import make_synthetic_cases as generator
    generator.generate(path)


def make_bundle(destination: Path, simulated: bool = False, with_dumps: bool = True,
                kick_limit: int = 10, marker: bool = False,
                break_hash: bool = False) -> Path:
    """Build a bundle for audit tests.

    ``marker=False`` deliberately omits GENERATED_FIXTURE.txt so the *audit
    logic* (not the marker guard) is exercised. Such a bundle is still synthetic
    and is never published or presented as native evidence.
    """
    sys.path.insert(0, str(TOOLS))
    import make_synthetic_cases as generator
    generator._write_bundle(destination, simulated=simulated, with_dumps=with_dumps,
                            kick_limit=kick_limit)
    if not marker:
        marker_file = destination / "GENERATED_FIXTURE.txt"
        if marker_file.exists():
            marker_file.unlink()
    if break_hash:
        manifest_path = destination / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"]["server_log"]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return destination


def assert_no_false_claim(testcase, payload) -> None:
    """Fail if a payload claims a pass, an acceptance or a confirmed cause."""
    def walk(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                here = "%s.%s" % (path, key) if path else str(key)
                if key in FALSE_CLAIM_KEYS:
                    testcase.assertFalse(value is True,
                                         "payload claims %s at %s" % (key, here))
                if key == "stability_claim":
                    testcase.assertEqual(value, "NONE",
                                         "stability_claim at %s" % here)
                if key == "root_cause_status":
                    testcase.assertEqual(value, "NOT_ESTABLISHED",
                                         "root_cause_status at %s" % here)
                if key.endswith("_pass") or key.endswith("_passed"):
                    testcase.assertFalse(value is True,
                                         "payload claims %s at %s" % (key, here))
                walk(value, here)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, "%s[%d]" % (path, index))

    walk(payload)
    if payload.get("schema") == "syncval/1":
        testcase.assertEqual(payload.get("stability_claim"), "NONE")
