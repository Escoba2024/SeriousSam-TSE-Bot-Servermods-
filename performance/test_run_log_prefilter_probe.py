"""Portable tests for run_log_prefilter_probe; no /srv, /root, network, or native game.

Fixtures are intentionally synthetic.  They validate supervisor contracts, not
Retail/Wine behavior or any M1 acceptance condition.
"""
from __future__ import annotations

import contextlib
import fcntl
import io
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


LEAD_DIR = next(parent for parent in Path(__file__).resolve().parents
                if (parent / 'run_eight_duration_hardened.py').is_file() or
                   (parent / 'tools/run_eight_duration_hardened.py').is_file())
SUPPORT_SOURCE = (LEAD_DIR / 'run_eight_duration_hardened.py' if
                  (LEAD_DIR / 'run_eight_duration_hardened.py').is_file() else
                  LEAD_DIR / 'tools/run_eight_duration_hardened.py')
RECEIPT_SOURCE = (LEAD_DIR / 'snapshot/tools/native_receipt_io.py' if
                  (LEAD_DIR / 'snapshot/tools/native_receipt_io.py').is_file() else
                  LEAD_DIR / 'tools/native_receipt_io.py')


spec = importlib.util.spec_from_file_location(
    'log_prefilter_probe', Path(__file__).with_name('run_log_prefilter_probe.py'))
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
assert spec.loader is not None
spec.loader.exec_module(p)


class FakeChild:
    def __init__(self, *, live: bool = True) -> None:
        self.pid = 424242
        self.returncode = None if live else 0
        self.wait_calls: list[float | None] = []

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)
        self.returncode = 0
        return 0


class LocalSyntheticFiles:
    """Local /proc and cgroup fixture; no host process data is read or written."""
    def __init__(self, root: Path) -> None:
        self.proc = root / 'proc'
        self.cgroup_root = root / 'cgroup'
        self.proc.mkdir(parents=True, exist_ok=True)
        self.cgroup_root.mkdir(parents=True, exist_ok=True)

    def write_process(self, pid: int, *, ppid: int, start_ticks: int) -> None:
        directory = self.proc / str(pid)
        directory.mkdir(parents=True, exist_ok=True)
        # /proc stat tail indexes: state=0, PPID=1, starttime=19.
        fields = ['S', str(ppid)] + ['0'] * 17 + [str(start_ticks)] + ['0'] * 3
        (directory / 'stat').write_text(f'{pid} (synthetic) ' + ' '.join(fields) + '\n')
        (directory / 'comm').write_text('synthetic\n')

    def make_cgroup(self, inner_pid: int, members: list[int]) -> Path:
        cgroup = self.cgroup_root / f'tse-sessions-{inner_pid}'
        cgroup.mkdir(exist_ok=True)
        self.write_members(cgroup, members)
        (cgroup / 'cpu.stat').write_text('usage_usec 10\n')
        return cgroup

    @staticmethod
    def write_members(cgroup: Path, members: list[int]) -> None:
        (cgroup / 'cgroup.procs').write_text(''.join(f'{pid}\n' for pid in members))


class ProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.temp = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.base = self.temp / 'base'
        self.candidate = self.temp / 'candidate'
        self.native = self.candidate / 'performance/native/tools'
        self.tools = self.candidate / 'tools'
        self.root = self.temp / 'runtime'
        self.manifest = self.temp / 'manifest.json'
        self.candidate_binary = self.temp / 'GameMP.dll'
        self.base.mkdir()
        self.native.mkdir(parents=True)
        self.tools.mkdir(parents=True)
        self.candidate_binary.write_bytes(b'synthetic candidate only')
        (self.base / 'matrix.lock').write_text('synthetic shared matrix lock\n')

        paths = {
            'BASE': self.base,
            'CANDIDATE_ROOT': self.candidate,
            'NATIVE': self.native,
            'TOOLS': self.tools,
            'BASE_SUPPORT': self.temp / 'hardened_support.py',
            'DIAGNOSTIC_EVIDENCE': self.candidate / 'performance/diagnostic_native_evidence.py',
            'ROOT': self.root,
            'MANIFEST': self.manifest,
            'CONFIG': self.base / '8-duration-config.json',
            'BASELINE_POLICY': self.base / 'duration-policy.json',
            'POLICY_PATH': self.base / 'manus-log-prefilter-probe-policy.json',
            'PROTECTED_ORIGINAL_QUALIFIER': self.temp / 'protected/tools/qualify_bot_sessions.py',
            'OFFLINE_MARKER': self.temp / 'public-disabled.json',
            'CONTROLLER_LOCK': self.base / 'manus-log-prefilter-probe-controller.lock',
            'MATRIX_LOCK': self.base / 'matrix.lock',
            'STATE': self.base / 'manus-log-prefilter-probe-progress.json',
            'COMMAND_RECEIPT': self.base / 'manus-log-prefilter-probe-command.json',
            'INPUT_SIDECAR': self.base / 'manus-log-prefilter-probe-inputs.json',
            'CPU_EVIDENCE': self.base / 'manus-log-prefilter-probe-cpu-attribution.jsonl',
            'FINAL_RECEIPT': self.base / 'manus-log-prefilter-probe-final.json',
            'HOLD': self.base / 'manus-log-prefilter-probe-HOLD.json',
            'LOG': self.base / 'manus-log-prefilter-probe-controller.log',
        }
        for name, value in paths.items():
            self.stack.enter_context(patch.object(p, name, value))
        self._write_fixture_tree()
        self.popen = self.stack.enter_context(patch.object(p.subprocess, 'Popen'))

    def _write_fixture_tree(self) -> None:
        p.BASE_SUPPORT.write_text(
            'def derive_budget(config): return {"total_s": 2000, "cleanup_s": 1, "abort_wait_s": 1}\n'
            'def check_live_heartbeat(reader, **kwargs): return {}\n'
            'def census_native_residue(root, result): return {"clean": True, "errors": []}\n'
            'def wait_for_clean_census(root, result, *, timeout): return {"clean": True, "errors": []}\n'
            'def request_orderly_abort(owned, *, timeout): return None\n'
            'def _load_module_from_path(name, path):\n'
            ' import importlib.util, sys\n'
            ' s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m\n')
        for name in p.DIAGNOSTIC_INPUT_NAMES:
            path = p._diagnostic_input_paths()[name]
            path.parent.mkdir(parents=True, exist_ok=True)
            if name == 'qualify_bot_sessions.py':
                # The supervisor checks that the outer source still carries its
                # global flock and builds its inner command only internally.
                path.write_text("lock='/srv/tse-session-qualification.lock'\nmode=fcntl.LOCK_EX\ncmd+['--inner']\n")
            elif name == 'native_owned_process.py':
                path.write_text(
                    'class OwnedProcess:\n'
                    ' def __init__(self, process): self.process=process; self.pidfd=99; self.start_ticks=77\n'
                    ' def close(self): return None\n')
            else:
                path.write_text('# synthetic fixture ' + name + '\n')
        config = {
            'enabled': True, 'max_bots': 8,
            'identities': [{'id': 'bot' + str(i)} for i in range(8)],
            'servers': [{'id': 'synthetic'}], 'leave_interval_s': 0,
            'max_log_mib': 1,
        }
        p.CONFIG.write_text(json.dumps(config))
        self.manifest.write_text(json.dumps({
            'build_ok': True, 'dll_sha256': p.sha(self.candidate_binary),
            'candidate': str(self.candidate_binary),
        }))
        (p.TOOLS / 'native_receipt_io.py').write_bytes(
            RECEIPT_SOURCE.read_bytes())
        p.DIAGNOSTIC_EVIDENCE.write_bytes((LEAD_DIR / 'performance/diagnostic_native_evidence.py').read_bytes())
        p.BASELINE_POLICY.write_text('{"synthetic":"baseline policy"}\n')
        p.PROTECTED_ORIGINAL_QUALIFIER.parent.mkdir(parents=True, exist_ok=True)
        p.PROTECTED_ORIGINAL_QUALIFIER.write_text('# synthetic protected original qualifier\n')
        policy = {
            'status': p.POLICY_STATUS,
            'm1_complete': False,
            'hardened_support_sha256': p.sha(p.BASE_SUPPORT),
            'diagnostic_evidence_sha256': p.sha(p.DIAGNOSTIC_EVIDENCE),
            'protected_original_qualifier_sha256': p.sha(p.PROTECTED_ORIGINAL_QUALIFIER),
            'harness_sha256': {name: p.sha(path) for name, path in p._producer_paths().items()},
            'stage8_additional_input_sha256': {name: p.sha(path) for name, path in p._diagnostic_input_paths().items()},
            'stage8_config_sha256': p.sha(p.CONFIG),
            'build_manifest_sha256': p.sha(self.manifest),
            'candidate_sha256': p.sha(self.candidate_binary),
            'acceptance_sha256': 'a' * 64,
            'receipt_reader_sha256': p.sha(p.TOOLS / 'native_receipt_io.py'),
            'baseline_policy_sha256': p.sha(p.BASELINE_POLICY),
            'diagnostic_duration_s': 1500,
            'diagnostic_min_full_population_s': 1200,
        }
        p.POLICY_PATH.write_text(json.dumps(policy))
        p.OFFLINE_MARKER.write_text('{"status":"DISABLED_BY_USER"}\n')

    def test_pin_context_has_new_producer_and_complete_eleven_input_inventory(self) -> None:
        context = p.bootstrap_pins()
        self.assertEqual(set(context.producer_sha256), set(p.PRODUCER_SOURCE_NAMES))
        self.assertEqual(set(context.input_sha256), set(p.DIAGNOSTIC_INPUT_NAMES))
        self.assertEqual(len(context.input_sha256), 11)
        self.assertEqual(context.candidate_sha256, p.sha(self.candidate_binary))
        p.verify_pins(context)

    def test_production_support_path_is_hetzner_worktree_not_sandbox(self) -> None:
        original = p._load_pinned_module('probe_production_constants_test',
                                         Path(__file__).with_name('run_log_prefilter_probe.py'))
        self.assertEqual(original.BASE_SUPPORT, original.TOOLS / 'run_eight_duration_hardened.py')

    def test_receipt_reader_drift_is_rejected_before_dynamic_import(self) -> None:
        (p.TOOLS / 'native_receipt_io.py').write_text('raise RuntimeError("untrusted reader")\n')
        with patch.object(p, '_load_pinned_module') as loader:
            with self.assertRaisesRegex(p.PinError, 'PIN_RECEIPT_READER_DRIFT'):
                p.bootstrap_pins()
        loader.assert_not_called()
        self.popen.assert_not_called()

    def test_live_receipt_reader_retries_truncate_write_race(self) -> None:
        context = p.bootstrap_pins()
        reader = p.load_pinned_receipt_reader(context)
        path = self.temp / 'live-result.json'
        path.write_text('{"status":')
        pauses = []
        def complete_write(seconds):
            pauses.append(seconds)
            path.write_text('{"status":"MEASURING"}')
        self.assertEqual(reader(path, pause=complete_write), {'status': 'MEASURING'})
        self.assertEqual(pauses, [0.1])

    def test_fixed_outer_argv_is_exact_diagnostic_outer_command(self) -> None:
        argv = p.build_fixed_outer_argv()
        self.assertEqual(argv[0:2], ['/usr/bin/python3', '-u'])
        self.assertEqual(argv[argv.index('--duration') + 1], '1500')
        self.assertEqual(argv[argv.index('--preset') + 1], 'redstation')
        self.assertEqual(argv[argv.index('--port') + 1], '27160')
        self.assertEqual(argv[argv.index('--display') + 1], ':157')
        self.assertNotIn('--inner', argv)
        p.validate_fixed_outer_argv(argv)
        with self.assertRaisesRegex(RuntimeError, 'FIXED_OUTER_ARGV_REQUIRED'):
            p.validate_fixed_outer_argv(argv + ['--inner'])

    def test_source_drift_blocks_before_spawn(self) -> None:
        (p.NATIVE / 'bot_sessions.py').write_text('drift\n')
        with self.assertRaisesRegex(p.PinError, 'PIN_INPUT_DRIFT'):
            p.run_probe_locked(None)
        self.popen.assert_not_called()

    def test_config_drift_blocks_before_spawn(self) -> None:
        config = json.loads(p.CONFIG.read_text())
        config['leave_interval_s'] = 7
        p.CONFIG.write_text(json.dumps(config))
        with self.assertRaisesRegex(p.PinError, 'PIN_STAGE8_CONFIG_DRIFT'):
            p.run_probe_locked(None)
        self.popen.assert_not_called()

    def test_policy_drift_between_bootstrap_and_spawn_blocks_before_spawn(self) -> None:
        original = p.verify_pins
        calls = 0

        def mutate_then_verify(context):
            nonlocal calls
            calls += 1
            if calls == 1:
                policy = json.loads(p.POLICY_PATH.read_text())
                policy['m1_complete'] = True
                p.POLICY_PATH.write_text(json.dumps(policy))
            return original(context)

        with patch.object(p, 'verify_pins', side_effect=mutate_then_verify):
            with self.assertRaisesRegex(p.PinError, 'PIN_POLICY_DRIFT'):
                p.run_probe_locked(None)
        self.popen.assert_not_called()

    def test_reused_result_root_is_rejected_before_spawn(self) -> None:
        p.ROOT.mkdir()
        (p.ROOT / 'result.json').write_text('{"old":true}\n')
        with patch.object(p.os, 'geteuid', return_value=0), patch.object(
                p.os, 'uname', return_value=types.SimpleNamespace(nodename='ubuntu-4gb-nbg1-2')):
            with self.assertRaisesRegex(RuntimeError, 'fresh diagnostic root required'):
                p.main()
        self.popen.assert_not_called()

    def test_unknown_cleanup_persists_hold_and_fresh_guard_refuses_restart(self) -> None:
        state = {'status': 'BLOCKED'}
        census = {'clean': False, 'errors': ['CENSUS_CGROUP_UNREADABLE']}
        p._persist_hold(state, p.CleanupHold('unclear cleanup'), census, None, [])
        self.assertEqual(json.loads(p.HOLD.read_text())['status'], 'HOLD')
        with self.assertRaisesRegex(p.CleanupHold, 'PERSISTENT_CLEANUP_HOLD_PRESENT'):
            p._fresh_start_guard()

    def test_owned_abort_contract_is_pidfd_sigint_and_bounded_wait(self) -> None:
        # The reusable hardened primitive is exercised against a simulated direct
        # child; neither terminate nor kill is present on this object.
        support = p._load_pinned_module('probe_test_real_support',
                                        SUPPORT_SOURCE)
        child = FakeChild(live=True)
        owned = types.SimpleNamespace(process=child, pidfd=123)
        with patch.object(support.signal, 'pidfd_send_signal') as send:
            support.request_orderly_abort(owned, timeout=3)
        send.assert_called_once_with(123, signal.SIGINT)
        self.assertEqual(child.wait_calls, [3])
        self.assertFalse(hasattr(child, 'terminate'))

    def test_native_failure_cleanup_uses_hardened_no_repeat_signal_state(self) -> None:
        support = p._load_pinned_module('probe_test_failure_support',
                                        SUPPORT_SOURCE)
        support.ROOT = self.temp / 'heartbeats'
        support.ROOT.mkdir()
        (support.ROOT / 'host-guard.json').write_text(json.dumps(
            {'status': 'MONITORING', 'samples': [{'at': 1000.0}]}))
        (support.ROOT / 'result.json').write_text(json.dumps(
            {'status': 'FAIL', 'scope': 'ISOLATED_NETNS_RETAIL_WINE', 'error': 'synthetic'}))
        state = support.check_live_heartbeat(lambda path: json.loads(Path(path).read_text()),
            launched_mono=0, now_mono=200, now_epoch=1000,
            budget={'cleanup_s': 3}, previous={})
        self.assertEqual(state['phase'], 'NATIVE_FAILURE_CLEANUP')
        self.assertIn('native_failure_cleanup_until', state)

    def test_near_complete_measurement_enters_bounded_hardened_drain_grace(self) -> None:
        support = p._load_pinned_module('probe_test_drain_support',
                                        SUPPORT_SOURCE)
        support.ROOT = self.temp / 'drain-heartbeats'
        support.ROOT.mkdir()
        support.DURATION_S = 1500
        (support.ROOT / 'host-guard.json').write_text(json.dumps(
            {'status': 'MONITORING', 'samples': [{'at': 1000.0}]}))
        receipt = {'status': 'MEASURING', 'elapsed_s': 1485,
                   'utc': '1970-01-01T00:16:40Z'}
        (support.ROOT / 'result.json').write_text(json.dumps(receipt))
        reader = lambda path: json.loads(Path(path).read_text())
        budget = {'drain_s': 3, 'cleanup_s': 3}
        state = support.check_live_heartbeat(reader, launched_mono=0, now_mono=200,
                                             now_epoch=1000, budget=budget, previous={})
        self.assertEqual(state['phase'], 'DRAIN_GRACE')
        receipt['status'] = 'DRAINING'
        (support.ROOT / 'result.json').write_text(json.dumps(receipt))
        still_draining = support.check_live_heartbeat(reader, launched_mono=0, now_mono=201,
                                                       now_epoch=1000, budget=budget, previous=state)
        self.assertEqual(still_draining['phase'], 'DRAIN_GRACE')

    def test_dataclass_generation_contracts_are_importable_and_explicit(self) -> None:
        self.assertTrue(is_dataclass(p.PinContext))
        self.assertTrue(is_dataclass(p.ProcessGeneration))
        self.assertTrue(is_dataclass(p.CgroupBinding))
        self.assertEqual([entry.name for entry in fields(p.ProcessGeneration)], ['pid', 'start_ticks'])
        self.assertEqual([entry.name for entry in fields(p.CgroupBinding)], ['cgroup', 'outer', 'inner'])

    def test_collector_records_unavailable_without_scanning_foreign_processes(self) -> None:
        evidence = self.temp / 'cpu.jsonl'
        with evidence.open('x') as stream:
            collector = p.CpuAttributionCollector(stream, p.ProcessGeneration(99, 1), set())
            with patch.object(p, '_host_cpu_ticks', return_value=[10, 0, 0, 5, 0, 0, 0, 0]):
                collector.maybe_sample(now_mono=1.0, now_epoch=2.0)
        row = json.loads(evidence.read_text())
        self.assertEqual(row['availability'], 'UNAVAILABLE_CGROUP_UNBOUND')
        self.assertEqual(row['members'], [])
        self.assertNotIn('cmdline', evidence.read_text())

    def test_collector_records_host_procstat_unavailable_without_abort(self) -> None:
        evidence = self.temp / 'cpu-host-unavailable.jsonl'
        with evidence.open('x') as stream:
            collector = p.CpuAttributionCollector(stream, p.ProcessGeneration(99, 1), set())
            with patch.object(p, '_host_cpu_ticks', side_effect=OSError('synthetic unavailable')):
                collector.maybe_sample(now_mono=1.0, now_epoch=2.0)
        row = json.loads(evidence.read_text())
        self.assertTrue(row['host_procstat_unavailable'])
        self.assertIsNone(row['host_procstat_delta'])
        self.assertEqual(row['availability'], 'UNAVAILABLE_CGROUP_UNBOUND')

    def _write_post_stop_artifacts(self) -> tuple[dict, dict, types.SimpleNamespace]:
        p.ROOT.mkdir()
        config = json.loads(p.CONFIG.read_text())
        identities = [entry['id'] for entry in config['identities']]
        for role in ['server', 'vanilla', *identities]:
            upper = p.ROOT / 'layers' / role / 'upper'
            upper.mkdir(parents=True)
            (upper / ('Dedicated_BotTest.log' if role == 'server' else 'SeriousSam.log')).write_text('synthetic\n')
        for role in identities:
            telemetry = p.ROOT / 'layers' / role / 'upper/Bin/BotTelemetry.csv'
            telemetry.parent.mkdir(parents=True)
            telemetry.write_text('synthetic telemetry\n')
        roles = ['server', 'vanilla', *identities]
        context = p.bootstrap_pins()
        (p.ROOT / 'source-sha256.json').write_text(json.dumps(context.producer_sha256))
        with (p.ROOT / 'samples.jsonl').open('w') as stream:
            for elapsed in range(1202):
                stream.write(json.dumps({'elapsed_s': elapsed, 'active': 8, 'population': 9,
                    'processes': {r: {'start_ticks': i+1, 'pss_mib': 1} for i, r in enumerate(roles)},
                    'decisions': [{'id': i, 'action': 'healthy'} for i in identities]}) + '\n')
        report = {'verdict': 'ACTIVE_OK', 'exit_code': 0, 'lp_median': 1, 'tick_hz_median': 20,
                  'render_skip_total': 1, 'render_draw_total': 0, 'config': {'nullrender': '1'}}
        result = {
            'status': 'PASS_LIMITED_SESSION_LIFECYCLE', 'scope': 'ISOLATED_NETNS_RETAIL_WINE',
            'dll_sha256': context.candidate_sha256, 'max_bots': 8, 'peak_playing': 8,
            'original_client': True, 'measured_s': 1500, 'elapsed_s': 1530,
            'utc': datetime.fromtimestamp(1700001540, timezone.utc).isoformat(), 'new_throttled_periods': 0,
            'cgroup': '/sys/fs/cgroup/tse-sessions-42', 'all_bots_drained': True,
            'telemetry': {role: [{'playing_s': 1500, 'reports': [report]}] for role in identities},
            'cleanup': [{'role': role, 'errors': []} for role in ['server', 'vanilla', *identities]],
            'unmounts': [{'path': str(p.ROOT / (prefix + role)), 'exitcode': 0}
                         for role in roles for prefix in ('', 'prefix-')],
        }
        guard = {'status': 'FINISHED', 'child_exitcode': 0, 'error': None,
                 'public_guard_mode': 'USER_DISABLED', 'public_disabled': True,
                 'samples': [{'at': 1700000000+i*5, 'available_mib': 1100,
                              'disk_free_gib': 8.3, 'host_busy_percent': 60} for i in range(310)]}
        collector = types.SimpleNamespace(
            binding=types.SimpleNamespace(cgroup=Path('/sys/fs/cgroup/tse-sessions-42')),
            summary=lambda: {'records': 3})
        return result, guard, collector

    def test_final_verdict_is_diagnostic_only_never_m1_acceptance_or_matrix_write(self) -> None:
        result, guard, collector = self._write_post_stop_artifacts()
        verdict = p.evaluate_diagnostic_final(result=result, guard=guard, exitcode=0,
                                              config=json.loads(p.CONFIG.read_text()),
                                              census={'clean': True}, collector=collector,
                                              context=p.bootstrap_pins())
        self.assertEqual(verdict['status'], 'DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE')
        self.assertFalse(verdict['m1_complete'])
        self.assertTrue(verdict['no_m1_matrix_or_acceptance_evaluated'])
        self.assertEqual(verdict['log_inventory']['complete_log_count'], 10)
        self.assertEqual(verdict['telemetry']['count'], 8)
        self.assertGreaterEqual(verdict['full_population']['longest_contiguous_full_population_s'], 1200)
        self.assertEqual({path.name for path in self.base.iterdir() if 'matrix' in path.name}, {'matrix.lock'})

    def test_final_verdict_rejects_less_than_1200_seconds_even_when_native_passes(self) -> None:
        result, guard, collector = self._write_post_stop_artifacts()
        # Replace the final samples with only 1,199 seconds of contiguous full population.
        with (p.ROOT / 'samples.jsonl').open('w') as stream:
            for elapsed in range(1200):
                stream.write(json.dumps({'elapsed_s': elapsed, 'active': 8}) + '\n')
        with self.assertRaisesRegex(RuntimeError, 'FULL_POPULATION_BELOW_1200S'):
            p.evaluate_diagnostic_final(result=result, guard=guard, exitcode=0,
                                        config=json.loads(p.CONFIG.read_text()),
                                        census={'clean': True}, collector=collector,
                                        context=p.bootstrap_pins())

    def _install_controller_mocks(self, child, reader, *, bind_fails: bool = False):
        """Install a synthetic support module; no native process is started."""
        calls: dict[str, object] = {'request': 0, 'census': 0}

        class Owned:
            def __init__(self, process):
                if bind_fails:
                    raise RuntimeError('synthetic owned bind failure')
                self.process = process
                self.pidfd = 77
                self.start_ticks = 88

            def close(self):
                calls['owned_closed'] = True

        def request_orderly_abort(owned, *, timeout):
            calls['request'] = int(calls['request']) + 1
            calls['request_timeout'] = timeout
            owned.process.wait(timeout=timeout)

        def residue(root, result):
            calls['census'] = int(calls['census']) + 1
            return {'clean': True, 'errors': []}

        def wait_census(root, result, *, timeout):
            calls['wait_census'] = timeout
            return {'clean': True, 'errors': []}

        support = types.SimpleNamespace(
            derive_budget=lambda config: {'total_s': 10, 'cleanup_s': 3, 'abort_wait_s': 2},
            check_live_heartbeat=lambda receipt_reader, **kwargs: {'phase': 'MONITORING'},
            request_orderly_abort=request_orderly_abort,
            census_native_residue=residue,
            wait_for_clean_census=wait_census,
        )
        self.stack.enter_context(patch.object(p, 'load_pinned_support', return_value=(support, Owned)))
        self.stack.enter_context(patch.object(p, 'load_pinned_receipt_reader', return_value=reader))
        self.stack.enter_context(patch.object(p, '_new_cgroup_names', return_value=set()))
        self.stack.enter_context(patch.object(p, '_open_cpu_evidence', return_value=io.StringIO()))
        self.popen.side_effect = lambda *args, **kwargs: child
        return support, calls

    def _write_post_stop_result(self, status='FAIL') -> None:
        p.ROOT.mkdir(exist_ok=True)
        (p.ROOT / 'result.json').write_text(json.dumps({'status': status, 'scope': p.NATIVE_SCOPE}))

    def _current_reader(self, status='MEASURING'):
        def reader(receipt_path):
            if Path(receipt_path).name == 'host-guard.json':
                return {'status': 'MONITORING'}
            return {'status': status, 'scope': p.NATIVE_SCOPE}
        return reader

    def test_existing_matrix_lock_busy_blocks_before_popen(self) -> None:
        with p.MATRIX_LOCK.open('r+') as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch.object(p.os, 'geteuid', return_value=0), patch.object(
                    p.os, 'uname', return_value=types.SimpleNamespace(nodename='ubuntu-4gb-nbg1-2')):
                with self.assertRaisesRegex(RuntimeError, 'SHARED_MATRIX_LOCK_BUSY_BEFORE_SPAWN'):
                    p.main()
        self.popen.assert_not_called()
        blocked = json.loads(p.STATE.read_text())
        self.assertEqual(blocked['phase'], 'PRE_SPAWN')
        self.assertFalse((self.base / 'duration-matrix.json').exists())
        self.assertFalse((self.base / 'm1-duration-matrix.json').exists())

    def test_runner_holds_existing_matrix_lock_across_its_cleanup_span(self) -> None:
        observed: list[str] = []

        def fake_run(controller_lock, matrix_lock):
            observed.append('before_cleanup')
            with p.MATRIX_LOCK.open('r+') as contender:
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # This marks the simulated post-stop census phase.  The same lock
            # remains held because its context belongs to main(), not run body.
            observed.append('after_census')

        with patch.object(p, 'run_probe_locked', side_effect=fake_run), patch.object(
                p.os, 'geteuid', return_value=0), patch.object(
                p.os, 'uname', return_value=types.SimpleNamespace(nodename='ubuntu-4gb-nbg1-2')):
            p.main()
        self.assertEqual(observed, ['before_cleanup', 'after_census'])
        self.assertEqual({path.name for path in self.base.iterdir() if 'matrix' in path.name}, {'matrix.lock'})

    def test_missing_matrix_lock_is_never_created(self) -> None:
        p.MATRIX_LOCK.unlink()
        with self.assertRaisesRegex(RuntimeError, 'SHARED_MATRIX_LOCK_OPEN_FAILED'):
            p._open_existing_matrix_lock(p.MATRIX_LOCK)
        self.assertFalse(p.MATRIX_LOCK.exists())

    def test_actual_cleanup_census_runs_while_shared_matrix_lock_is_still_held(self) -> None:
        child = FakeChild(live=True)
        support, _calls = self._install_controller_mocks(child, self._current_reader('MEASURING'))
        observed: list[str] = []

        def census_while_locked(root, result):
            with p.MATRIX_LOCK.open('r+') as contender:
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            observed.append('census_under_matrix_lock')
            return {'clean': True, 'errors': []}

        support.census_native_residue = census_while_locked
        with patch.object(p.CpuAttributionCollector, 'maybe_sample', side_effect=p.SafetyAbort('synthetic cleanup path')), patch.object(
                p.os, 'geteuid', return_value=0), patch.object(
                p.os, 'uname', return_value=types.SimpleNamespace(nodename='ubuntu-4gb-nbg1-2')):
            with self.assertRaisesRegex(p.SafetyAbort, 'synthetic cleanup path'):
                p.main()
        self.assertEqual(observed, ['census_under_matrix_lock'])
        self.assertTrue(p.HOLD.exists())

    def test_matrix_lock_must_be_regular_and_no_follow(self) -> None:
        p.MATRIX_LOCK.unlink()
        p.MATRIX_LOCK.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'SHARED_MATRIX_LOCK_OPEN_FAILED'):
            p._open_existing_matrix_lock(p.MATRIX_LOCK)
        p.MATRIX_LOCK.rmdir()
        target = self.base / 'matrix-target'
        target.write_text('target')
        p.MATRIX_LOCK.symlink_to(target)
        with self.assertRaisesRegex(RuntimeError, 'SHARED_MATRIX_LOCK_OPEN_FAILED'):
            p._open_existing_matrix_lock(p.MATRIX_LOCK)

    def test_loaded_reader_is_wired_to_heartbeat_and_live_cgroup_bind_after_race(self) -> None:
        child = FakeChild(live=True)
        reader_calls: list[str] = []
        captured: dict[str, object] = {}

        def loaded_reader(receipt_path):
            # Model a truncate/write race hidden inside the already-loaded bounded
            # reader: neither caller receives partial JSON.
            reader_calls.append(Path(receipt_path).name)
            if Path(receipt_path).name == 'host-guard.json':
                return {'status': 'MONITORING'}
            return {'status': 'MEASURING', 'scope': p.NATIVE_SCOPE}

        support, calls = self._install_controller_mocks(child, loaded_reader)

        def heartbeat(receipt_reader, **kwargs):
            captured['heartbeat_reader'] = receipt_reader
            receipt_reader(p.ROOT / 'host-guard.json')
            receipt_reader(p.ROOT / 'result.json')
            return {'phase': 'MONITORING'}

        def reject_after_capture(collector, result, outer):
            captured['bind_result'] = result
            raise p.SafetyAbort('synthetic after live bind')

        support.check_live_heartbeat = heartbeat
        with patch.object(p.CpuAttributionCollector, 'bind_from_result', new=reject_after_capture):
            with self.assertRaisesRegex(p.SafetyAbort, 'synthetic after live bind'):
                p.run_probe_locked(None)
        self.assertIs(captured['heartbeat_reader'], loaded_reader)
        self.assertEqual(captured['bind_result']['status'], 'MEASURING')
        self.assertGreaterEqual(reader_calls.count('result.json'), 2)
        self.assertEqual(calls['request'], 1)

    def test_state_write_failure_after_owned_bind_signals_once_then_censuses_even_if_all_later_persistence_fails(self) -> None:
        child = FakeChild(live=True)
        _support, calls = self._install_controller_mocks(child, self._current_reader('MEASURING'))
        original_atomic = p.atomic_json
        spawned = {'value': False}
        original_popen = self.popen.side_effect

        def popen_then_mark(*args, **kwargs):
            spawned['value'] = True
            return original_popen(*args, **kwargs)

        def fail_after_popen(path, value, **kwargs):
            if spawned['value']:
                raise OSError('synthetic persistence unavailable')
            return original_atomic(path, value, **kwargs)

        self.popen.side_effect = popen_then_mark
        with patch.object(p, 'atomic_json', side_effect=fail_after_popen), patch('sys.stderr', new_callable=io.StringIO) as stderr:
            with self.assertRaisesRegex(p.SafetyAbort, 'PERSISTENCE_FAILED_STATE_RUNNING'):
                p.run_probe_locked(None)
        self.assertEqual(calls['request'], 1)
        self.assertEqual(child.wait_calls, [2])
        self.assertGreaterEqual(int(calls['census']), 1)
        self.assertIn('PERSISTENCE_FAILURE', stderr.getvalue())
        state = {'status': 'synthetic'}
        errors: list[dict[str, str]] = []
        self.assertFalse(p.robust_best_effort_persist(errors, 'SYNTHETIC',
                         lambda: (_ for _ in ()).throw(OSError('fail')), state=state))
        self.assertEqual(state['persistence_errors'][0]['label'], 'SYNTHETIC')

    def test_confirmed_current_native_fail_waits_without_second_signal_and_ends_blocked_when_clean(self) -> None:
        self._write_post_stop_result('FAIL')
        child = FakeChild(live=True)
        _support, calls = self._install_controller_mocks(child, self._current_reader('FAIL'))
        with patch.object(p.CpuAttributionCollector, 'maybe_sample', side_effect=p.SafetyAbort('synthetic monitor error')):
            with self.assertRaisesRegex(p.SafetyAbort, 'synthetic monitor error'):
                p.run_probe_locked(None)
        self.assertEqual(calls['request'], 0)
        self.assertEqual(child.wait_calls, [3])
        self.assertEqual(json.loads(p.STATE.read_text())['status'], 'BLOCKED')
        self.assertFalse(p.HOLD.exists())

    def test_ambiguous_live_receipt_holds_and_waits_without_signal(self) -> None:
        self._write_post_stop_result('FAIL')
        child = FakeChild(live=True)

        def unreadable(_path):
            raise RuntimeError('partial receipt remained unreadable')

        _support, calls = self._install_controller_mocks(child, unreadable)
        with patch.object(p.CpuAttributionCollector, 'maybe_sample', side_effect=p.SafetyAbort('synthetic monitor error')):
            with self.assertRaisesRegex(p.SafetyAbort, 'synthetic monitor error'):
                p.run_probe_locked(None)
        self.assertEqual(calls['request'], 0)
        self.assertEqual(child.wait_calls, [3])
        self.assertEqual(json.loads(p.HOLD.read_text())['status'], 'HOLD')

    def test_owned_bind_failure_after_popen_never_signals_and_persists_hold_after_wait_census(self) -> None:
        self._write_post_stop_result('FAIL')
        child = FakeChild(live=True)
        _support, calls = self._install_controller_mocks(child, self._current_reader(), bind_fails=True)
        with self.assertRaisesRegex(p.CleanupHold, 'DIRECT_CHILD_PIDFD_OWNERSHIP_BIND_FAILED'):
            p.run_probe_locked(None)
        self.assertEqual(calls['request'], 0)
        self.assertEqual(child.wait_calls, [3])
        self.assertEqual(json.loads(p.HOLD.read_text())['status'], 'HOLD')

    def _cgroup_fixture(self):
        files = LocalSyntheticFiles(self.temp / 'synthetic-kernel')
        outer_pid, inner_pid = 400, 4242
        outer = p.ProcessGeneration(outer_pid, 70)
        files.write_process(outer_pid, ppid=1, start_ticks=70)
        files.write_process(inner_pid, ppid=outer_pid, start_ticks=80)
        cgroup = files.make_cgroup(inner_pid, [inner_pid])
        collector = p.CpuAttributionCollector(io.StringIO(), outer, set())
        return files, collector, FakeChild(live=True), outer_pid, inner_pid, cgroup

    def test_cgroup_bind_commits_only_stable_same_stat_generation_ppid_and_membership(self) -> None:
        files, collector, child, outer_pid, inner_pid, cgroup = self._cgroup_fixture()
        with patch.object(p, 'PROC_ROOT', files.proc), patch.object(p, 'CGROUP_ROOT', files.cgroup_root):
            collector.bind_from_result({'cgroup': str(cgroup)}, child)
        self.assertEqual(cgroup.name, f'tse-sessions-{inner_pid}')
        self.assertEqual(collector.binding.inner, p.ProcessGeneration(inner_pid, 80))
        self.assertEqual(collector.binding.outer, p.ProcessGeneration(outer_pid, 70))

    def test_cgroup_bind_rejects_inner_generation_change_before_commit(self) -> None:
        files, collector, child, outer_pid, inner_pid, cgroup = self._cgroup_fixture()
        original_members = p._read_cgroup_pids
        calls = {'value': 0}

        def mutate_before_commit(path):
            calls['value'] += 1
            if calls['value'] == 2:
                files.write_process(inner_pid, ppid=outer_pid, start_ticks=81)
            return original_members(path)

        with patch.object(p, 'PROC_ROOT', files.proc), patch.object(p, 'CGROUP_ROOT', files.cgroup_root), patch.object(
                p, '_read_cgroup_pids', side_effect=mutate_before_commit):
            with self.assertRaisesRegex(p.SafetyAbort, 'INNER_GENERATION_CHANGED_DURING_BIND'):
                collector.bind_from_result({'cgroup': str(cgroup)}, child)

    def test_cgroup_bind_rejects_inner_ppid_or_membership_change_before_commit(self) -> None:
        files, collector, child, outer_pid, inner_pid, cgroup = self._cgroup_fixture()
        original_members = p._read_cgroup_pids
        calls = {'value': 0}

        def mutate_ppid_before_commit(path):
            calls['value'] += 1
            if calls['value'] == 2:
                files.write_process(inner_pid, ppid=999, start_ticks=80)
            return original_members(path)

        with patch.object(p, 'PROC_ROOT', files.proc), patch.object(p, 'CGROUP_ROOT', files.cgroup_root), patch.object(
                p, '_read_cgroup_pids', side_effect=mutate_ppid_before_commit):
            with self.assertRaisesRegex(p.SafetyAbort, 'INNER_PPID_CHANGED_DURING_BIND'):
                collector.bind_from_result({'cgroup': str(cgroup)}, child)

        files, collector, child, _outer_pid, inner_pid, cgroup = self._cgroup_fixture()
        calls = {'value': 0}

        def remove_before_commit(path):
            calls['value'] += 1
            if calls['value'] == 2:
                LocalSyntheticFiles.write_members(cgroup, [])
            return original_members(path)

        with patch.object(p, 'PROC_ROOT', files.proc), patch.object(p, 'CGROUP_ROOT', files.cgroup_root), patch.object(
                p, '_read_cgroup_pids', side_effect=remove_before_commit):
            with self.assertRaisesRegex(p.SafetyAbort, 'INNER_PID_NOT_MEMBER_AT_COMMIT'):
                collector.bind_from_result({'cgroup': str(cgroup)}, child)

    def test_bound_collector_drops_member_that_leaves_cgroup_during_cpu_read(self) -> None:
        files, collector, _child, outer_pid, inner_pid, cgroup = self._cgroup_fixture()
        collector.binding = p.CgroupBinding(cgroup, p.ProcessGeneration(outer_pid, 70),
                                            p.ProcessGeneration(inner_pid, 80))
        original_members = p._read_cgroup_pids
        calls = {'value': 0}

        def remove_after_cpu_read(path):
            calls['value'] += 1
            if calls['value'] == 2:
                LocalSyntheticFiles.write_members(cgroup, [])
            return original_members(path)

        with patch.object(p, 'PROC_ROOT', files.proc), patch.object(p, 'CGROUP_ROOT', files.cgroup_root), patch.object(
                p, '_read_cgroup_pids', side_effect=remove_after_cpu_read):
            sample = collector._bound_sample()
        self.assertEqual(sample['members'], [])


if __name__ == '__main__':
    unittest.main()
