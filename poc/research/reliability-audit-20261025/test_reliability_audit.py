"""Offline behavior regressions against real imported operations modules.

Select the source tree with TSE_AUDIT_SOURCE. Only dependency boundaries for
privileged operations and timing are replaced; no Retail process is started.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('TSE_AUDIT_SOURCE', HERE.parents[2]))
sys.path.insert(0, str(SOURCE / 'tools' / 'operations'))
import fleet_health as h
import fleet_supervisor as v


def temporary():
    return tempfile.TemporaryDirectory(prefix='.fixture-', dir=HERE)


def runtime(root):
    obj = v.Runtime.__new__(v.Runtime)
    obj.root = root
    obj.result = root / 'result.json'
    obj.c = dict(root=str(root), bots=1, port=26880, display=':128')
    obj.cg = Path('/sys/fs/cgroup') / ('tse-ops-' + hashlib.sha256(str(root).encode()).hexdigest()[:12])
    obj.r = dict(processes={})
    obj.roles = ['server', 'botA']
    obj.boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    return obj


def snapshot():
    return dict(now=1000, query_time=999, query=dict(gamever='1.07', numplayers='1',
                maxplayers='16', activemod='', player_0='BOT-Rookie-Rush'),
                expected_names=['BOT-Rookie-Rush'], identity_errors=[], missing=[],
                ports_owned=True, mounts_owned=True, dll_valid=True,
                disk_free=12*1024**3, master_ok=True, telemetry_ok=True,
                owned_sync_bad=0, external_sync_bad=0, logs_over_limit=False)


class RegressionTests(unittest.TestCase):
    def test_state_is_loaded_after_controller_lock_acquisition(self):
        # A previous controller can publish a new generation between our read
        # and lock acquisition. The next controller must observe that state.
        with temporary() as directory:
            root = Path(directory)
            config = root / 'instance.json'
            config.write_text(json.dumps(dict(root=str(root), bots=1)))
            result = root / 'result.json'
            result.write_text(json.dumps(dict(processes={}, generation='old')))
            real_acquire = v.acquire_lock
            def acquire(path):
                result.write_text(json.dumps(dict(processes={}, generation='new')))
                return real_acquire(path)
            with patch.object(v, 'validate_config', return_value=root), patch.object(v, 'acquire_lock', side_effect=acquire):
                obj = v.Runtime(config)
            try:
                self.assertEqual(obj.r['generation'], 'new', 'controller consumed stale pre-lock state')
            finally:
                obj.lock.close()

    def test_unregistered_native_role_in_owned_cgroup_blocks_actions(self):
        # Simulate a crash between successful exec and result.json persistence.
        # Membership in our cgroup alone must not authorize a duplicate launch.
        with temporary() as directory:
            root = Path(directory)
            obj = runtime(root)
            proc = root / '991001'
            proc.mkdir()
            (proc / 'environ').write_bytes(('WINEPREFIX='+str(root)+'/prefix-botA').encode()+b'\0')
            orphan = dict(pid=991001, start_ticks=80, command='Bin/SeriousSam.exe',
                          cwd=str(root/'botA'), cgroup='0::'+str(obj.cg).removeprefix('/sys/fs/cgroup'))
            actual_read = Path.read_text
            actual_exists = Path.exists
            def read(path, *args, **kwargs):
                return '991001\n' if path == obj.cg/'cgroup.procs' else actual_read(path, *args, **kwargs)
            def exists(path):
                return True if path == obj.cg else actual_exists(path)
            with patch.object(obj, 'specs', return_value=[]), patch.object(h, 'udp_owners', return_value=set()), patch.object(Path, 'glob', return_value=[proc]), patch.object(Path, 'exists', exists), patch.object(Path, 'read_text', read), patch.object(h, 'process_identity', return_value=orphan):
                with self.assertRaises(RuntimeError, msg='unregistered native role was silently adopted'):
                    obj.ownership()

    def test_hardlink_writer_prevents_source_unlink(self):
        with temporary() as directory:
            root = Path(directory)
            source = root / 'SeriousSam.log'
            source.write_bytes(b'active generation\n')
            alias = root / 'alias.log'
            os.link(source, alias)
            with alias.open('ab') as writer:
                writer.write(b'write through alias\n')
                writer.flush()
                with self.assertRaises(RuntimeError, msg='archive removed a file with an active alias writer'):
                    v.archive_closed([source], root/'archives')
            self.assertTrue(source.exists())

    def test_archive_budget_includes_manifest_before_source_unlink(self):
        with temporary() as directory:
            root = Path(directory)
            for n in range(8):
                root = root / (str(n)+'x'*99)
            root.mkdir(parents=True)
            source = root / 'log'
            source.write_bytes(b'x')
            with self.assertRaises(RuntimeError, msg='manifest pushed archive over its declared budget'):
                v.archive_closed([source], root/'archives', budget=1025)
            self.assertEqual(source.read_bytes(), b'x')

    def test_partial_owned_sync_record_holds_until_newline(self):
        with temporary() as directory:
            source = Path(directory) / 'Dedicated.log'
            source.write_bytes(b"SYNCBAD: Client '127.0.0.1', bad 1")
            status = h.sync_counts(source)
            self.assertFalse(status['complete'], 'unterminated sync record authorized a complete scan')
            with source.open('ab') as writer:
                writer.write(b'\n')
            status = h.sync_counts(source)
            self.assertTrue(status['complete'])
            self.assertEqual(status['owned'], 1)


class ExistingSafetyTests(unittest.TestCase):
    def test_unknown_stale_malformed_human_and_duplicate_query_hold(self):
        changes = [dict(query=None), dict(query_time=990),
                   dict(query=dict(gamever='1.07', numplayers='0', maxplayers='16', player_0='BOT-Rookie-Rush')),
                   dict(query=dict(gamever='1.07', numplayers='2', maxplayers='16', player_0='BOT-Rookie-Rush', player_1='synthetic-human')),
                   dict(query=dict(gamever='1.07', numplayers='2', maxplayers='16', player_0='BOT-Rookie-Rush', player_1='BOT-Rookie-Rush'))]
        for change in changes:
            with self.subTest(change=change):
                state = snapshot()
                state.update(change)
                self.assertFalse(h.assess(state)['safe_recovery'])

    def test_owned_sync_incomplete_scan_oom_throttle_and_low_reserve_hold(self):
        changes = [dict(owned_sync_bad=1), dict(sync_scan_complete=False),
                   dict(cgroup_issues=['CGROUP_OOM']), dict(cgroup_issues=['CGROUP_THROTTLED']),
                   dict(resource_issues=['HOST_RAM_RESERVE']), dict(disk_free=7*1024**3)]
        for change in changes:
            with self.subTest(change=change):
                state = snapshot()
                state.update(change)
                self.assertFalse(h.assess(state)['safe_recovery'])

    def test_action_time_query_revalidates_human_and_unknown(self):
        for response in [dict(gamever='1.07', maxplayers='16', numplayers='1', player_0='synthetic-human'), {}]:
            with temporary() as directory, self.subTest(response=response):
                obj = runtime(Path(directory))
                with patch.object(v.q, 'query', return_value=response), self.assertRaises(RuntimeError):
                    obj.no_humans()

    def test_resource_budget_boundaries_and_invalid_samples(self):
        mib = 1024**2
        v.check_resource_reserve(dict(available_bytes=1152*mib, busy_percent=70), 384*mib)
        for sample in [dict(available_bytes=1152*mib-1, busy_percent=70),
                       dict(available_bytes=1152*mib, busy_percent=70.01),
                       dict(available_bytes=1152*mib, busy_percent=float('nan')),
                       dict(available_bytes=True, busy_percent=1), {}]:
            with self.subTest(sample=sample), self.assertRaises(RuntimeError):
                v.check_resource_reserve(sample, 384*mib)

    def test_reused_pidfd_is_closed_before_any_signal(self):
        # A real pidfd for this test process is safe to open and never signaled.
        info = h.process_identity(os.getpid())
        info['start_ticks'] += 1
        opened = []
        real_open = os.pidfd_open
        def pidfd(pid):
            fd = real_open(pid)
            opened.append(fd)
            return fd
        with patch.object(v.os, 'pidfd_open', side_effect=pidfd), self.assertRaises(RuntimeError):
            v.owned_pidfd(info)
        for fd in opened:
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_controller_lock_rejects_second_owner(self):
        with temporary() as directory:
            lock = v.acquire_lock(Path(directory)/'controller.lock')
            try:
                with self.assertRaises(BlockingIOError):
                    v.acquire_lock(Path(directory)/'controller.lock')
            finally:
                lock.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
