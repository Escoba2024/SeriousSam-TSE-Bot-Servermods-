"""Execute the real pinned backend method under deterministic file lifecycles."""
import ast
import errno
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
import tempfile

PARENT=Path('/srv/tse-powerup-on1-048-red600-module-v2-root-frozen-20261115/strict_backend.py')
PARENT_SHA='b4d57b35ce54f74185e3d891c17676a374ab3e892e148400a0a6ac712a9a1158'
CGROUP='/sys/fs/cgroup/system.slice/owned.service/cgroup.procs'

class ExitTests(unittest.TestCase):
 def source(self):
  s=PARENT.read_text();self.assertEqual(hashlib.sha256(s.encode()).hexdigest(),PARENT_SHA);return s
 def call(self,mode,patched=True):
  source=self.source()
  if patched:
   import native_cgroup_exit_patch as patch
   source=patch.transform(source)
  node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef)and n.name=='empty')
  calls=[]
  class File:
   def __init__(self,s):self.s=str(s)
   def __truediv__(self,v):return File(self.s+'/'+v)
   def __str__(self):return self.s
   def exists(self):
    calls.append(('exists',self.s))
    return mode not in ('missing','disappears') or calls.count(('exists',self.s))==1 and mode=='disappears'
   def read_text(self):
    calls.append(('read',self.s))
    if mode in ('missing','disappears','reappears'):raise FileNotFoundError(errno.ENOENT,'gone',self.s)
    if mode=='foreignmissing':raise FileNotFoundError(errno.ENOENT,'foreign','/other/file')
    if mode=='permission':raise PermissionError(errno.EACCES,'denied',self.s)
    if mode=='io':raise OSError(errno.EIO,'I/O',self.s)
    return '  456\n' if mode=='busy' else ' \n'
  env={'Path':File};exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'actual-backend-empty','exec'),env)
  # For the new read-first method, disappearance has already happened by read.
  if patched and mode=='disappears':mode='missing'
  result=env['empty'](SimpleNamespace(),'owned.service');return result,calls
 def test_old_actual_body_reproduces_exists_then_read_race(self):
  with self.assertRaises(FileNotFoundError):self.call('disappears',patched=False)
 def test_disappearing_or_missing_file_is_empty(self):
  for mode in ('disappears','missing'):
   with self.subTest(mode=mode):
    result,calls=self.call(mode);self.assertTrue(result);self.assertEqual(calls,[('read',CGROUP),('exists',CGROUP)])
 def test_reappeared_cgroup_is_not_empty(self):
  result,calls=self.call('reappears');self.assertFalse(result)
  self.assertEqual(calls,[('read',CGROUP),('exists',CGROUP)])
 def test_existing_busy_or_empty_uses_one_read(self):
  for mode,expected in [('busy',False),('empty',True)]:
   result,calls=self.call(mode);self.assertIs(result,expected);self.assertEqual(calls,[('read',CGROUP)])
 def test_foreign_missing_permission_io_not_hidden(self):
  for mode,kind in [('foreignmissing',FileNotFoundError),('permission',PermissionError),('io',OSError)]:
   with self.subTest(mode=mode),self.assertRaises(kind):self.call(mode)
 def test_real_file_unlink_between_old_exists_and_read(self):
  source=self.source();node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef)and n.name=='empty')
  with tempfile.TemporaryDirectory()as directory:
   file=Path(directory)/'cgroup.procs';file.write_text('')
   class RealFile:
    def __init__(self,*args):pass
    def __truediv__(self,value):return self
    def exists(self):
     result=file.exists();file.unlink();return result
    def read_text(self):return file.read_text()
   env={'Path':RealFile};exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'actual-backend-real-unlink','exec'),env)
   with self.assertRaises(FileNotFoundError):env['empty'](SimpleNamespace(),'owned.service')
 def test_missing_error_without_exact_filename_is_not_hidden(self):
  import native_cgroup_exit_patch as patch
  source=patch.transform(self.source());node=next(n for n in ast.walk(ast.parse(source))if isinstance(n,ast.FunctionDef)and n.name=='empty')
  class NoFilename:
   def __init__(self,*args):pass
   def __truediv__(self,value):return self
   def read_text(self):raise FileNotFoundError('ambiguous')
   def exists(self):raise AssertionError('ambiguous missing error swallowed')
  env={'Path':NoFilename};exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'actual-backend-ambiguous-error','exec'),env)
  with self.assertRaises(FileNotFoundError):env['empty'](SimpleNamespace(),'owned.service')
 def test_full_source_inverse_and_foreign_changes_rejected(self):
  import native_cgroup_exit_patch as patch
  old=self.source();new=patch.transform(old);self.assertEqual(patch.reverse(new),old)
  for changed in (old+'\n',old.replace('return p,int','return p+1,int'),new.replace('def ready','def unsafe_ready')):
   if changed==old:continue
   with self.assertRaises(ValueError):
    if 'unsafe_ready' in changed:patch.reverse(changed)
    else:patch.transform(changed)

if __name__=='__main__':unittest.main()
