"""Own temporary files and actual cleanup source fixtures; no runtime import."""
import ast
import errno
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

class CleanupReceiptTests(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('cleanup_failure_receipt'),'bounded cleanup receipt missing')
  import cleanup_failure_receipt as m
  return m
 def test_private_append_current_exception_and_role_bounds(self):
  m=self.module()
  with tempfile.TemporaryDirectory()as tmp:
   path=Path(tmp)/'private.jsonl';journal=m.CleanupFailureReceipt(path)
   self.assertFalse(path.exists())
   for role in ('vanilla','botB','botA','server'):
    try:raise FileNotFoundError(errno.ENOENT,'gone','/owned/cgroup.procs')
    except FileNotFoundError as error:journal.record(role,error)
   rows=[json.loads(x)for x in path.read_text().splitlines()]
   self.assertEqual([r['role']for r in rows],['vanilla','botB','botA','server'])
   self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)
   for row in rows:
    self.assertEqual(row['exception_type'],'builtins.FileNotFoundError');self.assertEqual(row['errno'],errno.ENOENT)
    self.assertEqual(row['filename'],'/owned/cgroup.procs');self.assertIn('raise FileNotFoundError',row['traceback'])
    self.assertIn('FileNotFoundError',row['traceback']);self.assertTrue(row['current_exception_only'])
   self.assertTrue(all(len(x)+1<=65536 for x in path.read_bytes().splitlines()))
   before=path.read_bytes()
   for role in ('server','foreign'):
    with self.assertRaises(ValueError):journal.record(role,RuntimeError('duplicate/foreign'))
   self.assertEqual(path.read_bytes(),before)
 def test_preexisting_symlink_changed_file_and_oversize_fail(self):
  m=self.module()
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'exists';p.write_text('foreign')
   with self.assertRaises(FileExistsError):m.CleanupFailureReceipt(p).record('server',RuntimeError('no'))
   link=Path(tmp)/'link';link.symlink_to(p)
   with self.assertRaises(OSError):m.CleanupFailureReceipt(link).record('server',RuntimeError('no'))
   self.assertEqual(p.read_text(),'foreign')
   big=Path(tmp)/'big'
   with self.assertRaises(ValueError):m.CleanupFailureReceipt(big).record('server',RuntimeError('x'*65536))
   self.assertFalse(big.exists())
   own=Path(tmp)/'own';j=m.CleanupFailureReceipt(own);j.record('vanilla',RuntimeError('one'));own.chmod(0o644)
   with self.assertRaises(ValueError):j.record('server',RuntimeError('two'))
 def test_short_write_propagates_and_fd_closed(self):
  m=self.module()
  with tempfile.TemporaryDirectory()as tmp:
   j=m.CleanupFailureReceipt(Path(tmp)/'short')
   real_close=m.os.close;closed=[]
   with patch.object(m.os,'write',return_value=0),patch.object(m.os,'close',side_effect=lambda fd:(closed.append(fd),real_close(fd))[1]):
    with self.assertRaises(OSError):j.record('server',RuntimeError('short'))
   self.assertEqual(len(closed),1)
 def test_actual_except_preserves_original_and_continues_after_archive_error(self):
  m=self.module();parent=Path('/srv/tse-nav20-027-skulls600-diag1-disabled-20261115/run-a4.py').read_text()
  for archive_fails in (False,True):
   source=m.transform_controller(parent);self.assertEqual(m.reverse_controller(source),parent)
   tree=ast.parse(source);loop=next(n for n in ast.walk(tree)if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='role'and isinstance(n.iter,ast.Tuple)and [x.value for x in n.iter.elts]==['vanilla','botB','botA','server'])
   calls=[];archived=[];report={'errors':[]}
   class Archive:
    def record(self,role,error):
     archived.append((role,type(error).__name__))
     if archive_fails:raise OSError(errno.EIO,'archive disk')
   def close(role):
    calls.append(role)
    if role=='botB':raise FileNotFoundError(errno.ENOENT,'closed file gone','/owned/cgroup.procs')
   env={'records':{},'close':close,'report':report,'cleanup_failures':Archive()}
   exec(compile(ast.fix_missing_locations(ast.Module(body=[loop],type_ignores=[])),'actual-cleanup-role-loop','exec'),env)
   self.assertEqual(calls,['vanilla','botB','botA','server']);self.assertEqual(archived,[('botB','FileNotFoundError')])
   self.assertTrue(report['errors'][0].startswith('cleanup botB:FileNotFoundError'))
   self.assertEqual(len(report['errors']),2 if archive_fails else 1)
   if archive_fails:self.assertTrue(report['errors'][1].startswith('cleanup exception receipt botB:'))
 def test_controller_inverse_rejects_foreign_changes(self):
  m=self.module();old=Path('/srv/tse-nav20-027-skulls600-diag1-disabled-20261115/run-a4.py').read_text();new=m.transform_controller(old)
  self.assertEqual(m.reverse_controller(new),old)
  with self.assertRaises(ValueError):m.transform_controller(new)
  with self.assertRaises(ValueError):m.transform_controller(old+old)
  self.assertNotEqual(m.reverse_controller(new.replace('expected_roles=roles','expected_roles=()')),old)
 def test_successful_actual_cleanup_has_no_archival_call(self):
  m=self.module();source=m.transform_controller(Path('/srv/tse-nav20-027-skulls600-diag1-disabled-20261115/run-a4.py').read_text())
  loop=next(n for n in ast.walk(ast.parse(source))if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='role'and isinstance(n.iter,ast.Tuple)and [x.value for x in n.iter.elts]==['vanilla','botB','botA','server'])
  with tempfile.TemporaryDirectory()as tmp:
   path=Path(tmp)/'none';journal=m.CleanupFailureReceipt(path);calls=[];report={'errors':[]}
   env=dict(records={},close=calls.append,report=report,cleanup_failures=journal)
   exec(compile(ast.fix_missing_locations(ast.Module(body=[loop],type_ignores=[])),'actual-successful-cleanup-loop','exec'),env)
   self.assertEqual(calls,['vanilla','botB','botA','server']);self.assertEqual(report['errors'],[]);self.assertFalse(path.exists())

if __name__=='__main__':unittest.main()
