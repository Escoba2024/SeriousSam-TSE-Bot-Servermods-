"""Portable mocked tests for run_eight_duration_hardened; no /srv, /root, or native game use."""
from __future__ import annotations

import contextlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


spec = importlib.util.spec_from_file_location(
    'eight_duration_hardened', Path(__file__).with_name('run_eight_duration_hardened.py'))
d = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = d
spec.loader.exec_module(d)


class FakeChild:
    def __init__(self, *, live=False):
        self.pid = 424242
        self.returncode = None if live else 0
        self.wait_calls = []

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.temp = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.base = self.temp / 'base'
        self.tools = self.temp / 'tools'
        self.native = self.temp / 'native-root' / 'tools'
        self.runtime_parent = self.temp / 'prior-runtimes'
        for directory in (self.base, self.tools, self.native, self.runtime_parent):
            directory.mkdir(parents=True, exist_ok=True)
        self.root = self.temp / 'stage-eight'
        self.manifest = self.temp / 'manifest.json'
        self.config = self.base / '8-duration-config.json'
        self.offline = self.temp / 'public-disabled.json'
        self.offline.write_text('{"status":"DISABLED_BY_USER"}')

        patches = {
            'BASE': self.base,
            'TOOLS': self.tools,
            'NATIVE': self.native,
            'ROOT': self.root,
            'MANIFEST': self.manifest,
            'CONFIG': self.config,
            'POLICY_PATH': self.base / 'duration-policy.json',
            'OFFLINE_MARKER': self.offline,
            'MATRIX_LOCK': self.base / 'matrix.lock',
            'STATE': self.base / 'progress.json',
            'NEW_MATRIX': self.base / 'new-matrix.json',
            'COMMAND_RECEIPT': self.base / 'command.json',
            'INPUT_SIDECAR': self.base / 'inputs.json',
            'HOLD': self.base / 'HOLD.json',
            'LOG': self.base / 'native.log',
            'CANONICAL_BLOCKED_MATRIX': self.base / 'duration-matrix.json',
            'PRIOR_RUNTIME_PARENT': self.runtime_parent,
        }
        for name, value in patches.items():
            self.stack.enter_context(patch.object(d, name, value))
        self.stack.enter_context(patch.object(d.os, 'geteuid', return_value=0))
        self.stack.enter_context(patch.object(
            d.os, 'uname', return_value=types.SimpleNamespace(nodename='ubuntu-4gb-nbg1-2')))
        (d.MATRIX_LOCK).touch()
        d.CANONICAL_BLOCKED_MATRIX.write_text('{"status":"BLOCKED","protected":true}\n')
        self.canonical_before = d.CANONICAL_BLOCKED_MATRIX.read_bytes()

        self._write_pinned_source_tree()
        self._write_policy_and_inputs()
        self._write_prior_receipts()
        self.child = FakeChild()
        self.popen = self.stack.enter_context(patch.object(d.subprocess, 'Popen', side_effect=self._spawn))
        self.real_census = d.census_native_residue
        self.census = self.stack.enter_context(patch.object(
            d, 'census_native_residue', return_value={'clean': True, 'errors': [], 'mounts': [],
                                                       'live_processes': [], 'cgroup': 'fixture'}))
        self.stack.enter_context(patch.object(d, 'CENSUS_POLL_S', 0))
        self.stack.enter_context(patch('builtins.print'))

    def _write_pinned_source_tree(self):
        # The actual dynamic loader executes only these tiny test fixtures.
        (d.TOOLS / 'native_receipt_io.py').write_text(
            'import json\nfrom pathlib import Path\ndef read_receipt(path, **_): return json.loads(Path(path).read_text())\n')
        (d.TOOLS / 'm1_duration_acceptance.py').write_text(
            'def evaluate_runtime(root, *, bots, required_s, dll_sha256, harness_sha256):\n'
            '    return {"status":"DURATION_RECEIPTS_ACCEPTED","bots":bots,"required_s":required_s,'
            '"dll_sha256":dll_sha256,"m1_complete":False}\n')
        for name in d.ORIGINAL_SOURCE_NAMES:
            (d.NATIVE / name).write_text('# fixture ' + name + '\n')
        for name in ('bot_telemetry.py', 'redstation_preset.py', 'gaming_names.py'):
            (d.NATIVE / name).write_text('# fixture ' + name + '\n')
        (d.TOOLS / 'native_owned_process.py').write_text(
            'class OwnedProcess:\n'
            '    def __init__(self, process):\n'
            '        self.process=process; self.pidfd=71; self.closed=False\n'
            '    def close(self):\n'
            '        if self.process.poll() is None: raise RuntimeError("live fixture child")\n'
            '        self.closed=True\n')
        phase = d.NATIVE.parent / 'poc/scripts/Phase1HumanAI.ini'
        phase.parent.mkdir(parents=True, exist_ok=True)
        phase.write_text('// fixture Human AI\n')

    def _write_policy_and_inputs(self):
        config = dict(enabled=True, max_bots=8, identities=[{'id': str(i)} for i in range(8)],
                      servers=[{'id': 'private'}], leave_interval_s=20)
        d.CONFIG.write_text(json.dumps(config))
        candidate = self.temp / 'candidate.bin'
        candidate.write_bytes(b'candidate fixture')
        self.manifest.write_text(json.dumps(dict(build_ok=True, dll_sha256=d.sha(candidate),
                                                 candidate=str(candidate))))
        harness = {name: d.sha(d.NATIVE / name) for name in d.ORIGINAL_SOURCE_NAMES}
        additional = {}
        for name, path in d._additional_input_paths().items():
            additional[name] = d.sha(path)
        policy = dict(receipt_reader_sha256=d.sha(d.TOOLS / 'native_receipt_io.py'),
                      acceptance_sha256=d.sha(d.TOOLS / 'm1_duration_acceptance.py'),
                      harness_sha256=harness,
                      stage8_additional_input_sha256=additional,
                      stage8_config_sha256=d.sha(d.CONFIG),
                      build_manifest_sha256=d.sha(self.manifest),
                      candidate_sha256=d.sha(candidate))
        d.POLICY_PATH.write_text(json.dumps(policy))

    def _write_prior_receipts(self):
        for _bots, label in d.PRIOR_STAGES:
            root = d.PRIOR_RUNTIME_PARENT / ('tse-session-qualification-master-m1-' + label + '-20261026')
            root.mkdir()
            for name in d.PRIOR_RECEIPT_NAMES:
                (root / name).write_text(json.dumps({'fixture': label, 'name': name}) + '\n')

    def _spawn(self, *args, **kwargs):
        self.assertEqual(args[0], d.build_fixed_outer_argv())
        self.assertNotIn('--inner', args[0])
        self.root.mkdir()
        (self.root / 'result.json').write_text(json.dumps({
            'status': 'PASS_LIMITED_SESSION_LIFECYCLE', 'cgroup': str(self.temp / 'cgroup/tse-sessions-99'),
            'utc': '2026-10-26T07:00:00Z'}))
        (self.root / 'host-guard.json').write_text(json.dumps({'status': 'FINISHED', 'samples': []}))
        return self.child

    def test_success_uses_one_exact_outer_argv_and_preserves_canonical_block(self):
        d.main()
        self.assertEqual(self.popen.call_count, 1)
        argv = self.popen.call_args.args[0]
        self.assertEqual(argv[argv.index('--duration') + 1], '7680')
        self.assertNotIn('--inner', argv)
        self.assertEqual(d.CANONICAL_BLOCKED_MATRIX.read_bytes(), self.canonical_before)
        result = json.loads(d.NEW_MATRIX.read_text())
        self.assertEqual(result['status'], 'DURATION_MATRIX_ACCEPTED_PRIVATE_ONLY')
        self.assertFalse(result['m1_complete'])
        self.assertEqual([(row['verdict']['bots'], row['verdict']['required_s']) for row in result['stages']],
                         [(1, 3600), (4, 3600), (8, 7200)])
        inventory = json.loads(d.INPUT_SIDECAR.read_text())
        self.assertEqual(inventory['phase'], 'AFTER_SUCCESS')
        self.assertTrue(inventory['formal_source_inventory_unchanged'])
        self.assertEqual(set(inventory['original_harness_sha256']), set(d.ORIGINAL_SOURCE_NAMES))
        self.assertEqual(set(inventory['additional_input_sha256']), set(d.ADDITIONAL_INPUT_NAMES))

    def test_source_drift_is_explicit_pin_error_not_assertion_and_prevents_spawn(self):
        (d.NATIVE / 'qualify_bot_sessions.py').write_text('drift\n')
        with self.assertRaisesRegex(d.PinError, 'PIN_INPUT_DRIFT'):
            d.main()
        self.popen.assert_not_called()

    def test_unpinned_acceptance_is_rejected_before_any_import_code(self):
        marker = self.temp / 'must-not-execute'
        (d.TOOLS / 'm1_duration_acceptance.py').write_text(
            'from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("executed")\n')
        with self.assertRaisesRegex(d.PinError, 'PIN_ACCEPTANCE_DRIFT'):
            d.main()
        self.assertFalse(marker.exists())
        self.popen.assert_not_called()

    def test_nested_gaming_names_drift_is_blocked_before_spawn(self):
        (d.NATIVE / 'gaming_names.py').write_text('drift\n')
        with self.assertRaisesRegex(d.PinError, 'PIN_INPUT_DRIFT_gaming_names'):
            d.main()
        self.popen.assert_not_called()

    def test_missing_additional_inventory_is_a_block_not_an_implicit_baseline(self):
        policy = json.loads(d.POLICY_PATH.read_text())
        policy['stage8_additional_input_sha256'].pop('redstation_preset.py')
        d.POLICY_PATH.write_text(json.dumps(policy))
        with self.assertRaisesRegex(d.PinError, 'EXACT_KEYS_REQUIRED'):
            d.main()
        self.popen.assert_not_called()

    def test_config_drift_prevents_spawn(self):
        config = json.loads(d.CONFIG.read_text())
        config['leave_interval_s'] = 99
        d.CONFIG.write_text(json.dumps(config))
        with self.assertRaisesRegex(d.PinError, 'PIN_STAGE8_CONFIG_DRIFT'):
            d.main()
        self.popen.assert_not_called()

    def test_prior_receipt_drift_before_start_prevents_spawn(self):
        prior = d.PRIOR_RUNTIME_PARENT / 'tse-session-qualification-master-m1-one-hour-20261026/result.json'
        # Change after snapshots are made by wrapping validation, proving the
        # driver checks preservation both before spawn and later in the run.
        original_validate = d.validate_prior_stages
        def mutate_then_validate(*args, **kwargs):
            prior.write_text('{"changed":true}\n')
            return original_validate(*args, **kwargs)
        with patch.object(d, 'validate_prior_stages', side_effect=mutate_then_validate):
            with self.assertRaisesRegex(d.PinError, 'PRIOR_RECEIPT_DRIFT'):
                d.main()
        self.popen.assert_not_called()

    def test_deadline_covers_full_lifecycle_not_measurement_only(self):
        budget = d.derive_budget(json.loads(d.CONFIG.read_text()))
        self.assertEqual(budget['measure_s'], 7680)
        self.assertGreater(budget['total_s'], 8910)
        self.assertGreaterEqual(budget['cleanup_s'], 990)
        self.assertGreaterEqual(budget['drain_s'], 120 + 8 * 20)

    def test_orderly_abort_sends_pidfd_sigint_not_parent_terminate(self):
        child = FakeChild(live=True)
        owned = types.SimpleNamespace(process=child, pidfd=999)
        with patch.object(d.signal, 'pidfd_send_signal') as send:
            d.request_orderly_abort(owned, timeout=12)
        send.assert_called_once_with(999, d.signal.SIGINT)
        self.assertEqual(child.wait_calls, [12])
        self.assertFalse(hasattr(child, 'terminate'))

    def test_wrapper_sigterm_enters_owned_pidfd_sigint_abort_path(self):
        self.child = FakeChild(live=True)
        handlers = {}
        def install(signum, handler):
            previous = handlers.get(signum)
            handlers[signum] = handler
            return previous
        def trigger_signal(_seconds):
            handlers[d.signal.SIGTERM](d.signal.SIGTERM, None)
        with patch.object(d.signal, 'signal', side_effect=install), \
             patch.object(d.signal, 'pidfd_send_signal') as send, \
             patch.object(d.time, 'sleep', side_effect=trigger_signal):
            with self.assertRaisesRegex(d.SafetyAbort, 'DRIVER_SIGNAL'):
                d.main()
        send.assert_called_once_with(71, d.signal.SIGINT)
        self.assertEqual(json.loads(d.STATE.read_text())['status'], 'BLOCKED')
        self.assertFalse(d.HOLD.exists())

    def test_heartbeat_requires_fresh_guard_after_startup_grace(self):
        self.root.mkdir()
        now = 1_000.0
        (self.root / 'host-guard.json').write_text(json.dumps({
            'status': 'MONITORING', 'samples': [{'at': now - 4}]}))
        (self.root / 'result.json').write_text(json.dumps({
            'status': 'MEASURING', 'elapsed_s': 42,
            'utc': '1970-01-01T00:16:40Z'}))
        reader = lambda path: json.loads(Path(path).read_text())
        state = d.check_live_heartbeat(reader, launched_mono=0, now_mono=d.STARTUP_GRACE_S + 1,
                                       now_epoch=now, budget=d.derive_budget(json.loads(d.CONFIG.read_text())),
                                       previous={})
        self.assertEqual(state['phase'], 'MONITORING')
        (self.root / 'host-guard.json').write_text(json.dumps({
            'status': 'MONITORING', 'samples': [{'at': now - d.GUARD_STALE_S - 1}]}))
        with self.assertRaisesRegex(d.SafetyAbort, 'HOST_GUARD_HEARTBEAT_STALE'):
            d.check_live_heartbeat(reader, launched_mono=0, now_mono=d.STARTUP_GRACE_S + 2,
                                   now_epoch=now, budget=d.derive_budget(json.loads(d.CONFIG.read_text())),
                                   previous=state)

    def test_drain_grace_cannot_be_extended_by_stagnant_elapsed_time(self):
        self.root.mkdir()
        now = 1000.0
        (self.root / 'host-guard.json').write_text(json.dumps(
            {'status': 'MONITORING', 'samples': [{'at': now - 4}]}))
        (self.root / 'result.json').write_text(json.dumps(
            {'status': 'MEASURING', 'elapsed_s': d.DURATION_S - 20,
             'utc': '1970-01-01T00:16:40Z'}))
        reader = lambda p: json.loads(Path(p).read_text())
        budget = d.derive_budget(json.loads(d.CONFIG.read_text()))
        state = d.check_live_heartbeat(reader, launched_mono=0,
            now_mono=d.STARTUP_GRACE_S + 1, now_epoch=now, budget=budget, previous={})
        expiry = state['drain_grace_until']
        again = d.check_live_heartbeat(reader, launched_mono=0,
            now_mono=d.STARTUP_GRACE_S + 100, now_epoch=now, budget=budget, previous=state)
        self.assertEqual(again['drain_grace_until'], expiry)
        with self.assertRaisesRegex(d.SafetyAbort, 'RESULT_PROGRESS_STALE'):
            d.check_live_heartbeat(reader, launched_mono=0, now_mono=expiry + 1,
                                  now_epoch=now, budget=budget, previous=again)

    def test_native_failure_waits_for_existing_cleanup_without_repeated_signal(self):
        self.root.mkdir()
        (self.root / 'host-guard.json').write_text(json.dumps(
            {'status': 'MONITORING', 'samples': [{'at': 0}]}))
        (self.root / 'result.json').write_text(json.dumps(
            {'status': 'FAIL', 'scope': 'ISOLATED_NETNS_RETAIL_WINE', 'error': 'outer guard stopped test'}))
        reader = lambda p: json.loads(Path(p).read_text())
        budget = d.derive_budget(json.loads(d.CONFIG.read_text()))
        with patch.object(d.signal, 'pidfd_send_signal') as send:
            state = d.check_live_heartbeat(reader, launched_mono=0,
                now_mono=200, now_epoch=1000, budget=budget, previous={})
        send.assert_not_called()
        self.assertEqual(state['phase'], 'NATIVE_FAILURE_CLEANUP')
        with self.assertRaisesRegex(d.SafetyAbort, 'NATIVE_FAILURE_CLEANUP_DEADLINE'):
            d.check_live_heartbeat(reader, launched_mono=0,
                now_mono=state['native_failure_cleanup_until']+1, now_epoch=1000,
                budget=budget, previous=state)

    def test_final_receipt_allows_only_bounded_outer_exit_window(self):
        self.root.mkdir()
        (self.root / 'host-guard.json').write_text(json.dumps(
            {'status': 'FINISHED', 'child_exitcode': 0, 'error': None, 'samples': []}))
        (self.root / 'result.json').write_text(json.dumps(
            {'status': 'PASS_LIMITED_SESSION_LIFECYCLE'}))
        reader = lambda p: json.loads(Path(p).read_text())
        budget = d.derive_budget(json.loads(d.CONFIG.read_text()))
        state = d.check_live_heartbeat(reader, launched_mono=0,
            now_mono=200, now_epoch=1000, budget=budget, previous={})
        self.assertEqual(state['phase'], 'FINALIZING')
        with self.assertRaisesRegex(d.SafetyAbort, 'FINAL_RECEIPT_WITHOUT_OUTER_EXIT'):
            d.check_live_heartbeat(reader, launched_mono=0, now_mono=216,
                                  now_epoch=1000, budget=budget, previous=state)

    def test_census_is_read_only_and_flags_nonempty_known_cgroup(self):
        proc_root = self.temp / 'proc'
        cgroup_root = self.temp / 'cgroups'
        proc_root.mkdir()
        cgroup = cgroup_root / 'tse-sessions-88'
        cgroup.mkdir(parents=True)
        (cgroup / 'cgroup.procs').write_text('')
        mountinfo = proc_root / 'self/mountinfo'
        mountinfo.parent.mkdir(exist_ok=True)
        mountinfo.write_text('')
        with patch.object(d, 'PROC_ROOT', proc_root), patch.object(d, 'MOUNTINFO', mountinfo), \
             patch.object(d, 'CGROUP_ROOT', cgroup_root):
            clean = self.real_census(self.root, {'cgroup': str(cgroup)})
            self.assertTrue(clean['clean'])
            (cgroup / 'cgroup.procs').write_text('123\n')
            blocked = self.real_census(self.root, {'cgroup': str(cgroup)})
        self.assertFalse(blocked['clean'])
        self.assertIn('CENSUS_CGROUP_NOT_EMPTY', blocked['errors'])

    def test_persistent_hold_rejects_start_without_spawn(self):
        d.HOLD.write_text('{"status":"HOLD"}\n')
        with self.assertRaisesRegex(d.CleanupHold, 'PERSISTENT_CLEANUP_HOLD_PRESENT'):
            d.main()
        self.popen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
