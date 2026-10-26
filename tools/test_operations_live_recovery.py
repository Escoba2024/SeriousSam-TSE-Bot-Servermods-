"""Regressions for the retained Wine-helper failure and Xvfb exec race."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).parent / 'operations'))
import fleet_supervisor as v

class LiveRecoveryTests(unittest.TestCase):
    def test_remaining_prefix_client_without_server_only_waits(self):
        with tempfile.TemporaryDirectory() as directory:
            child = subprocess.Popen(['sleep', '20'], env=dict(os.environ, WINEPREFIX=directory))
            try:
                with patch.object(v.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
                    v.close_prefix(Path(directory))
                self.assertEqual([c.args[0][-1] for c in run.call_args_list], ['-w'])
            finally:
                child.terminate()
                child.wait()

    def test_live_prefix_server_kill_error_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            proc = Path(directory) / '123'
            proc.mkdir()
            (proc / 'comm').write_text('wineserver64\n')
            (proc / 'environ').write_bytes(b'WINEPREFIX=/owned\0')
            (proc / 'stat').write_text('123 (wineserver64) S ' + '0 ' * 30)
            failure = subprocess.CalledProcessError(1, ['wineserver', '-k'])
            with patch.object(Path, 'glob', return_value=[proc]), patch.object(v.subprocess, 'run', side_effect=failure), self.assertRaises(subprocess.CalledProcessError):
                v.close_prefix(Path('/owned'))

    def test_live_server_is_killed_then_waited_and_zombie_is_only_waited(self):
        for state, expected in [('S', ['-k', '-w']), ('Z', ['-w'])]:
            with self.subTest(state=state), tempfile.TemporaryDirectory() as directory:
                proc = Path(directory) / '123'
                proc.mkdir()
                (proc / 'comm').write_text('wineserver64\n')
                (proc / 'environ').write_bytes(b'WINEPREFIX=/owned\0')
                (proc / 'stat').write_text('123 (wineserver64) ' + state + ' ' + '0 ' * 30)
                with patch.object(Path, 'glob', return_value=[proc]), patch.object(v.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
                    v.close_prefix(Path('/owned'))
                self.assertEqual([c.args[0][-1] for c in run.call_args_list], expected)

    def test_executable_identity_waits_through_preexec(self):
        process = Mock(pid=123)
        process.poll.return_value = None
        before = dict(pid=123, start_ticks=100, command='python3')
        after = dict(before, command='Xvfb')
        self.assertTrue(hasattr(v, 'settled_process'), 'Xvfb exec identity must settle before persisting')
        with patch.object(v.h, 'process_identity', side_effect=[before, after]), patch.object(v.time, 'sleep'):
            self.assertEqual(v.settled_process(process, 'Xvfb'), after)

    def test_executable_identity_rejects_exited_child(self):
        process = Mock(pid=123)
        process.poll.return_value = 1
        self.assertTrue(hasattr(v, 'settled_process'), 'settled process identity missing')
        with patch.object(v.h, 'process_identity', return_value=dict(command='python3')), self.assertRaises(RuntimeError):
            v.settled_process(process, 'Xvfb')

    def test_native_absent_server_wait_with_remaining_process(self):
        import shutil
        if os.geteuid() != 0 or not shutil.which('wineserver') or not shutil.which('runuser'):
            self.skipTest('Linux root and Wine are needed for this native CLI check')
        with tempfile.TemporaryDirectory(prefix='tse-no-server-') as directory:
            os.chown(directory, 65534, 65534)
            child = subprocess.Popen(['sleep', '20'], env=dict(os.environ, WINEPREFIX=directory))
            try:
                # No game or Wine process is started. The real Wine CLI must
                # handle an absent server while a leftover prefix user exists.
                v.close_prefix(Path(directory))
            finally:
                child.terminate()
                child.wait()

    def test_native_exec_transition_identity_is_live(self):
        child = subprocess.Popen([sys.executable, '-c', "import os; os.execl('/bin/sleep', 'sleep', '20')"])
        try:
            info = v.settled_process(child, 'sleep')
            self.assertEqual(v.h.verify_process(info), 'LIVE')
        finally:
            child.terminate()
            child.wait()

if __name__ == '__main__':
    unittest.main()
