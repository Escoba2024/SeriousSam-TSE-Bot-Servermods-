"""Regressions for observed native cleanup and recovery boundary failures."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / 'operations'))
import fleet_health as h
import fleet_supervisor as v
import test_fleet_operations as fixtures


def stopped_runtime(root):
    runtime = v.Runtime.__new__(v.Runtime)
    runtime.root = root
    runtime.result = root / 'result.json'
    runtime.c = dict(root=str(root), bots=1, port=26880, display=':128')
    runtime.roles = ['server', 'botA']
    runtime.cg = Path('/sys/fs/cgroup') / ('tse-ops-' + hashlib.sha256(str(root).encode()).hexdigest()[:12])
    runtime.boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    runtime.r = dict(processes={}, mounts=[], status='OWNED_ISOLATED_STOPPED', left_running=False)
    runtime.save()
    return runtime


class CompletionTests(unittest.TestCase):
    def test_launch_resource_reserve_rejects_pressure_and_unknown_samples(self):
        self.assertTrue(hasattr(v, 'check_resource_reserve'), 'host admission gate missing')
        mib = 1024**2
        v.check_resource_reserve({'available_bytes': 1200*mib, 'busy_percent': 65}, 320*mib)
        for sample in ({'available_bytes': 1000*mib, 'busy_percent': 65},
                       {'available_bytes': 1200*mib, 'busy_percent': 71},
                       {'available_bytes': 1200*mib, 'busy_percent': float('nan')},
                       {'available_bytes': 1200*mib}, {}):
            with self.subTest(sample=sample), self.assertRaises(RuntimeError):
                v.check_resource_reserve(sample, 320*mib)

    def test_private_rules_block_nonloopback_ingress_without_public_ports(self):
        self.assertTrue(hasattr(v, 'private_rules'), 'private ingress isolation missing')
        rules = v.private_rules(26880, 'fixture')
        ingress = [r for r in rules if r[0] == 'INPUT']
        self.assertEqual(len(ingress), 1)
        rule = ingress[0]
        self.assertIn('26880:26881', rule)
        self.assertIn('DROP', rule)
        self.assertEqual(rule[1:4], ['!', '-i', 'lo'])
        self.assertFalse(any('25600' in part or '25601' in part for r in rules for part in r))
        with self.assertRaises(ValueError):
            v.private_rules(25600, 'fixture')

    def test_live_runtime_holds_if_private_isolation_rule_is_lost(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = stopped_runtime(Path(directory))
            runtime.r['xvfb'] = dict(pid=999999, cwd=str(runtime.root), command='Xvfb',
                                    cgroup='0::' + str(runtime.cg).removeprefix('/sys/fs/cgroup'))
            with patch.object(h, 'verify_process', return_value='LIVE'), patch.object(v.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1)), self.assertRaises(RuntimeError):
                runtime.ownership()

    def test_second_stop_does_not_enter_unmounted_wine_prefixes(self):
        # The native outer harness called stop twice. Entering an unmounted
        # prefix invokes Wine against the empty mountpoint, causing exit 1.
        with tempfile.TemporaryDirectory() as directory:
            runtime = stopped_runtime(Path(directory))
            def firewall(command, **kwargs):
                self.assertEqual(command[:3], ['iptables', '-w', '-C'])
                return subprocess.CompletedProcess(command, 1)
            with patch.object(v, 'close_prefix', side_effect=AssertionError('unmounted prefix touched')), patch.object(v.subprocess, 'run', side_effect=firewall):
                runtime.stop()
                runtime.stop()
            self.assertFalse(json.loads(runtime.result.read_text())['left_running'])
            self.assertEqual(len(json.loads((runtime.root / 'events.json').read_text())), 2)

    def test_server_loss_does_not_bypass_oom_or_throttle_hold(self):
        # A confirmed dead server must not defeat a host/cgroup safety hold.
        for issue in ('CGROUP_OOM', 'CGROUP_THROTTLED', 'HOST_RESOURCE_HOLD'):
            with self.subTest(issue=issue), tempfile.TemporaryDirectory() as directory:
                runtime = stopped_runtime(Path(directory))
                runtime.r['last_no_humans'] = v.time.time()
                snapshot = fixtures.HealthTests().snapshot()
                snapshot.update(missing=['server'], query=None, cgroup_issues=[issue])
                with patch.object(h, 'collect', return_value=(snapshot, h.assess(snapshot))), patch.object(runtime, 'start', side_effect=AssertionError('unsafe restart')), patch.object(runtime, 'stop', side_effect=AssertionError('unsafe teardown')):
                    runtime.reconcile()
                self.assertFalse(runtime.r.get('attempts'))

    def test_server_loss_does_not_bypass_owned_sync_or_incomplete_scan(self):
        for update in ({'owned_sync_bad': 1}, {'sync_scan_complete': False}):
            with self.subTest(update=update), tempfile.TemporaryDirectory() as directory:
                runtime = stopped_runtime(Path(directory))
                runtime.r['last_no_humans'] = v.time.time()
                snapshot = fixtures.HealthTests().snapshot()
                snapshot.update(missing=['server'], query=None, **update)
                with patch.object(h, 'collect', return_value=(snapshot, h.assess(snapshot))), patch.object(runtime, 'stop', side_effect=AssertionError('sync hold bypassed')):
                    runtime.reconcile()
                self.assertFalse(runtime.r.get('attempts'))

    def test_action_guard_rejects_duplicate_roster_mod_and_wrong_capacity(self):
        status = fixtures.HealthTests().snapshot()['query']
        invalid = [dict(status, numplayers='9', player_8=status['player_0']),
                   dict(status, activemod='unknown'), dict(status, maxplayers='32')]
        for response in invalid:
            with self.subTest(response=response), tempfile.TemporaryDirectory() as directory:
                runtime = stopped_runtime(Path(directory))
                runtime.c['bots'] = 8
                with patch.object(v.q, 'query', return_value=response), self.assertRaises(RuntimeError):
                    runtime.no_humans()

    def test_changed_query_is_revalidated_before_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = stopped_runtime(Path(directory))
            runtime.c['bots'] = 8
            snapshot = fixtures.HealthTests().snapshot()
            snapshot.update(missing=['botA'])
            response = dict(snapshot['query'], numplayers='9', player_8=snapshot['query']['player_0'])
            with patch.object(h, 'collect', return_value=(snapshot, h.assess(snapshot))), patch.object(v.q, 'query', return_value=response), patch.object(runtime, 'launch', side_effect=AssertionError('changed roster launched')):
                with self.assertRaises(RuntimeError):
                    runtime.reconcile()


if __name__ == '__main__':
    unittest.main()
