"""Execute both SHA-pinned RuntimeBackend.empty bodies, without runtime import."""
import ast
import errno
import hashlib
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path('/srv/tse-a1-first-state-method-monitor-disabled-20261115')
PARENTS = {
    'strict_backend.py': 'fb759339e7de8b31dd0fc490a0f3152be78a00d9e13f0ecb39443bc7cf7f8c1c',
    'method-api/vendor/colt/strict_backend.py': '13394a9cb3a69d081f9071861d36a5663367995e4b62c00738d6c4e869ef121a',
}
CGROUP = '/sys/fs/cgroup/system.slice/owned.service/cgroup.procs'

def sources():
    for relative, expected in PARENTS.items():
        source = (ROOT / relative).read_text()
        assert hashlib.sha256(source.encode()).hexdigest() == expected
        yield relative, source

def target(source):
    if os.environ.get('TSE_A1_CGROUP_USE_PARENT') == '1':
        return source
    from tools.a1_dual_cgroup_exit_patch import transform
    return transform(source)

def actual_empty(source, path_class):
    backend = next(n for n in ast.parse(source).body
                   if isinstance(n, ast.ClassDef) and n.name == 'RuntimeBackend')
    node = next(n for n in backend.body if isinstance(n, ast.FunctionDef) and n.name == 'empty')
    env = {'Path': path_class}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'actual-sha-pinned-backend-empty', 'exec'), env)
    return env['empty']

class DualExitTests(unittest.TestCase):
    def call(self, source, mode, owner=None):
        calls = []
        class File:
            def __init__(self, value): self.value = str(value)
            def __truediv__(self, value): return File(self.value + '/' + value)
            def __str__(self): return self.value
            def exists(self):
                calls.append(('exists', self.value))
                if mode == 'exists_permission': raise PermissionError(errno.EACCES, 'denied', self.value)
                return mode != 'missing'
            def read_text(self):
                calls.append(('read', self.value))
                if mode in ('missing', 'reappears', 'exists_permission'):
                    raise FileNotFoundError(errno.ENOENT, 'gone', self.value)
                if mode == 'foreign': raise FileNotFoundError(errno.ENOENT, 'foreign', '/other/file')
                if mode == 'no_filename': raise FileNotFoundError('ambiguous')
                if mode == 'permission': raise PermissionError(errno.EACCES, 'denied', self.value)
                if mode == 'io': raise OSError(errno.EIO, 'I/O', self.value)
                return ' 456\n' if mode == 'busy' else ' \n'
        return actual_empty(source, File)(owner or SimpleNamespace(pid=None), 'owned.service'), calls

    def test_read_first_missing_reappearance_busy_empty_and_none_pid(self):
        for relative, source in sources():
            for mode, expected in [('missing', True), ('reappears', False), ('busy', False), ('empty', True)]:
                with self.subTest(parent=relative, mode=mode):
                    value, calls = self.call(target(source), mode, SimpleNamespace(pid=None))
                    self.assertIs(value, expected)
                    wanted = [('read', CGROUP)]
                    if mode in ('missing', 'reappears'): wanted.append(('exists', CGROUP))
                    self.assertEqual(calls, wanted)

    def test_wrong_filename_none_filename_permission_io_propagate(self):
        for relative, source in sources():
            for mode, kind in [('foreign', FileNotFoundError), ('no_filename', FileNotFoundError),
                               ('permission', PermissionError), ('io', OSError),
                               ('exists_permission', PermissionError)]:
                with self.subTest(parent=relative, mode=mode), self.assertRaises(kind):
                    self.call(target(source), mode)

    def test_real_unlink_before_read_has_no_exists_to_read_race(self):
        for relative, source in sources():
            with self.subTest(parent=relative), tempfile.TemporaryDirectory() as directory:
                file = Path(directory) / 'cgroup.procs'
                file.write_text('')
                calls = []
                class RealFile:
                    def __init__(self, *args): pass
                    def __truediv__(self, value): return self
                    def __str__(self): return str(file)
                    def exists(self):
                        calls.append('exists')
                        result = file.exists()
                        if result: file.unlink()
                        return result
                    def read_text(self):
                        calls.append('read')
                        if file.exists(): file.unlink()
                        return file.read_text()
                self.assertTrue(actual_empty(target(source), RealFile)(SimpleNamespace(pid=None), 'owned.service'))
                self.assertEqual(calls, ['read', 'exists'])

    def test_unmodified_parent_really_exhibits_unlink_race(self):
        for relative, source in sources():
            class Vanishing:
                def __init__(self, *args): pass
                def __truediv__(self, value): return self
                def exists(self): return True
                def read_text(self): raise FileNotFoundError(errno.ENOENT, 'unlinked', CGROUP)
            with self.subTest(parent=relative), self.assertRaises(FileNotFoundError):
                actual_empty(source, Vanishing)(SimpleNamespace(pid=None), 'owned.service')

    @unittest.skipIf(os.environ.get('TSE_A1_CGROUP_USE_PARENT') == '1', 'transform not installed for RED')
    def test_two_exact_sources_inverse_other_bytes_and_rejections(self):
        from tools import a1_dual_cgroup_exit_patch as patch
        self.assertEqual(set(patch.PARENT_SHAS), set(PARENTS.values()))
        for relative, source in sources():
            with self.subTest(parent=relative):
                changed = patch.transform(source)
                self.assertEqual(patch.reverse(changed), source)
                self.assertEqual(changed.replace(patch.AFTER, patch.BEFORE), source)
                before_ast = ast.parse(source)
                after_ast = ast.parse(changed)
                for tree in (before_ast, after_ast):
                    backend = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RuntimeBackend')
                    backend.body = [n for n in backend.body if not isinstance(n, ast.FunctionDef) or n.name != 'empty']
                self.assertEqual(ast.dump(before_ast), ast.dump(after_ast))
                for wrong in (source + '\n', source.replace('def ready', 'def not_ready'), changed):
                    with self.assertRaises(ValueError): patch.transform(wrong)
                for wrong in (changed + '\n', changed.replace('def ready', 'def not_ready'), source):
                    with self.assertRaises(ValueError): patch.reverse(wrong)

if __name__ == '__main__': unittest.main()
