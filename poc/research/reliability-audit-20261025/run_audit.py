#!/usr/bin/env python3
"""Reproduce RED/GREEN using source copies; never applies patches to the repo.

Only unittest fixtures run. Retail, Wine commands, production ports, mounts,
services, firewall and cgroups are never started or modified by this harness.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PATCH = HERE / '0001-close-controller-archive-and-sync-gaps.patch'
PINS = {
    'tools/operations/fleet_supervisor.py': '83d2bec6507d9de87fa7c42a97af69501f8f77b4608122a6f954dbfae20c1242',
    'tools/operations/fleet_health.py': '152d2b71865d0649f977016701267ed17a086eb15a506c4113173a28f45e1800',
}
EXPECTED_RED = {
    'test_state_is_loaded_after_controller_lock_acquisition',
    'test_unregistered_native_role_in_owned_cgroup_blocks_actions',
    'test_hardlink_writer_prevents_source_unlink',
    'test_archive_budget_includes_manifest_before_source_unlink',
    'test_partial_owned_sync_record_holds_until_newline',
}
MARKER = 'C1_RESULT_JSON='


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def suite(source, kind):
    os.environ['TSE_AUDIT_SOURCE'] = str(source)
    sys.path.insert(0, str(source/'tools/operations'))
    import fleet_health
    import fleet_supervisor
    if kind == 'audit':
        spec = importlib.util.spec_from_file_location('c1_audit_tests', HERE/'test_reliability_audit.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        tests = unittest.defaultTestLoader.loadTestsFromModule(module)
    else:
        tests = unittest.defaultTestLoader.discover(str(source/'tools'), pattern='test_*.py')
        import test_operations_live_recovery
        method = test_operations_live_recovery.LiveRecoveryTests.test_native_absent_server_wait_with_remaining_process
        method.__unittest_skip__ = True
        method.__unittest_skip_why__ = 'C1 offline scope: no real Wine CLI'
    stream = io.StringIO()
    # Existing CLI tests intentionally print fixture failures. Keep synthetic
    # diagnostics separate from the machine-readable summary.
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    summary = dict(tests=result.testsRun, passed=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
                   failures=[case.id().rsplit('.', 1)[-1] for case, _ in result.failures],
                   errors=[case.id().rsplit('.', 1)[-1] for case, _ in result.errors],
                   skipped=[dict(test=case.id(), reason=reason) for case, reason in result.skipped])
    print(stream.getvalue(), end='')
    print(MARKER+json.dumps(summary, sort_keys=True))
    return int(not result.wasSuccessful())


def execute(source, kind):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    completed = subprocess.run([sys.executable, str(__file__), '--source-root', str(source), '--internal-suite', kind],
                               env=env, text=True, capture_output=True, timeout=90)
    output = completed.stdout+completed.stderr
    markers = [line.removeprefix(MARKER) for line in completed.stdout.splitlines() if line.startswith(MARKER)]
    if len(markers) != 1:
        raise RuntimeError('suite failed before its result: '+output)
    result = json.loads(markers[0])
    result['exit_code'] = completed.returncode
    return result, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=REPO)
    parser.add_argument('--report-dir', type=Path)
    parser.add_argument('--internal-suite', choices=['audit', 'inherited'], help=argparse.SUPPRESS)
    args = parser.parse_args()
    source = args.source_root.resolve()
    if args.internal_suite:
        return suite(source, args.internal_suite)
    before = {path: sha(source/path) for path in PINS}
    if before != PINS:
        raise RuntimeError('source differs from reviewed PR50 baseline; use test_reliability_audit.py directly for other revisions')
    report_dir = args.report_dir.resolve() if args.report_dir else None
    if report_dir:
        allowed = REPO/'docs/reports/reliability-audit-20261025'
        if not report_dir.is_relative_to(allowed):
            raise ValueError('report output must stay inside the C1 report scope')
        report_dir.mkdir(parents=True, exist_ok=True)
    runs = {}
    diagnostics = {}
    runs['red'], diagnostics['red'] = execute(source, 'audit')
    if set(runs['red']['failures']) != EXPECTED_RED or runs['red']['errors'] or runs['red']['exit_code'] != 1:
        raise RuntimeError('baseline failed differently from the five reviewed defects: '+diagnostics['red'])
    with tempfile.TemporaryDirectory(prefix='.scratch-', dir=HERE) as directory:
        candidate = Path(directory)
        (candidate/'tools/operations').mkdir(parents=True)
        for path in (source/'tools').glob('*.py'):
            shutil.copy2(path, candidate/'tools'/path.name)
        for path in PINS:
            shutil.copy2(source/path, candidate/path)
        subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(PATCH)], cwd=candidate,
                       capture_output=True, text=True, check=True)
        candidate_shas = {path: sha(candidate/path) for path in PINS}
        for kind in ['audit', 'inherited']:
            runs[kind], diagnostics[kind] = execute(candidate, kind)
            if runs[kind]['exit_code'] != 0 or runs[kind]['failures'] or runs[kind]['errors']:
                raise RuntimeError('patched suite failed: '+diagnostics[kind])
    after = {path: sha(source/path) for path in PINS}
    if after != before:
        raise RuntimeError('source changed during audit')
    report = dict(baseline_commit='b5dafb8', baseline=before, candidate=candidate_shas,
                  patch_sha256=sha(PATCH), patch=PATCH.name, runs=runs,
                  original_sources_unchanged=True, runtime='NOT_RUN',
                  scope='offline imported-code regressions; no Retail qualification')
    if report_dir:
        (report_dir/'results.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
        for kind, output in diagnostics.items():
            (report_dir/(kind+'-tests.txt')).write_text(output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
