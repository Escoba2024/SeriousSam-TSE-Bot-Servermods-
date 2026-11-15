"""Real temporary file lifecycle through the actual pinned transaction class."""
from pathlib import Path
import hashlib
import os
import tempfile
import unittest
from unittest import mock

PARENT=Path('/srv/tse-powerup-on1-048-red600-module-v2-root-frozen-20261115/transaction.py')
PARENT_SHA='6fd1825b1bfda8713b8669f01ea3ab4cb5747c2084c338575fb0b0dbbf5c5dfb'
TIMES=(1660000000123456789,1660000010987654321)

class TimestampTests(unittest.TestCase):
 def source(self):
  s=PARENT.read_text();self.assertEqual(hashlib.sha256(s.encode()).hexdigest(),PARENT_SHA);return s
 def setup_case(self,patched=True):
  s=self.source()
  if patched:
   import file_transaction_timestamp_patch as patch
   s=patch.transform(s)
  env={};exec(compile(s,'actual-pinned-transaction','exec'),env)
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);base=Path(tmp.name)
  root=base/'fixture';root.mkdir();evidence=base/'evidence';evidence.mkdir()
  file=root/'a';file.write_bytes(b'before');file.chmod(0o640);os.utime(file,ns=TIMES)
  checks=[];transaction=env['FileTransaction'](root,evidence,lambda:checks.append('quiescent'))
  return transaction,root,evidence,checks
 def test_old_actual_class_does_not_prove_timestamp_restoration(self):
  tx,root,_,_=self.setup_case(False);tx.snapshot_file('a');tx.seal();(root/'a').write_bytes(b'changed')
  self.assertTrue(tx.restore()['restored']);self.assertNotEqual((root/'a').stat().st_mtime_ns,TIMES[1])
 def test_both_ns_timestamps_are_captured_before_read_and_restored_after_hash(self):
  tx,root,evidence,checks=self.setup_case();tx.snapshot_file('a');tx.seal()
  self.assertEqual((tx.records['a']['atime_ns'],tx.records['a']['mtime_ns']),TIMES)
  (root/'a').write_bytes(b'changed');r=tx.restore();self.assertTrue(r['restored'])
  st=(root/'a').stat();self.assertEqual((st.st_atime_ns,st.st_mtime_ns),TIMES);self.assertEqual(st.st_mode&0o7777,0o640)
  self.assertEqual(r['verified_files']['a'],hashlib.sha256(b'before').hexdigest());self.assertEqual(len(checks),3)
 def test_time_failure_does_not_mask_error_or_block_other_restore(self):
  tx,root,_,_=self.setup_case();(root/'b').write_bytes(b'other');os.utime(root/'b',ns=TIMES)
  tx.snapshot_file('a');tx.snapshot_file('b');tx.seal();(root/'a').write_bytes(b'changed');(root/'b').write_bytes(b'changed')
  real=os.utime
  def fault(path,*args,**kwargs):
   if Path(path)==root/'a':raise PermissionError('time restoration denied')
   return real(path,*args,**kwargs)
  with mock.patch('os.utime',side_effect=fault):r=tx.restore()
  self.assertFalse(r['restored']);self.assertEqual(len(r['errors']),1);self.assertIn('time restoration denied',r['errors'][0])
  self.assertNotIn('a',r['verified_files']);self.assertIn('b',r['verified_files']);st=(root/'b').stat();self.assertEqual((st.st_atime_ns,st.st_mtime_ns),TIMES)
 def test_silent_wrong_time_is_failure(self):
  tx,root,_,_=self.setup_case();tx.snapshot_file('a');tx.seal();(root/'a').write_bytes(b'changed')
  with mock.patch('os.utime',return_value=None):r=tx.restore()
  self.assertFalse(r['restored']);self.assertIn('restored timestamps differ',r['errors'][0])
 def test_absent_and_new_tree_files_still_removed(self):
  tx,root,_,_=self.setup_case();(root/'tree').mkdir();tx.snapshot_file('absent');tx.snapshot_file('a');tx.snapshot_tree('tree');tx.seal()
  (root/'absent').write_bytes(b'new');(root/'tree'/'new').write_bytes(b'new');r=tx.restore();self.assertTrue(r['restored'])
  self.assertFalse((root/'absent').exists());self.assertFalse((root/'tree'/'new').exists())
 def test_backup_corruption_retains_failure_without_timestamp_success(self):
  tx,root,evidence,_=self.setup_case();tx.snapshot_file('a');tx.seal();(evidence/tx.records['a']['backup']).write_bytes(b'bad')
  r=tx.restore();self.assertFalse(r['restored']);self.assertIn('backup hash changed',r['errors'][0]);self.assertNotIn('a',r['verified_files'])
 def test_independent_byte_read_preserves_restored_atime_and_rejects_symlink(self):
  from file_transaction_timestamp_patch import read_bytes_noatime
  tx,root,_,_=self.setup_case();tx.snapshot_file('a');tx.seal();(root/'a').write_bytes(b'changed');self.assertTrue(tx.restore()['restored'])
  self.assertEqual(read_bytes_noatime(root/'a'),b'before');st=(root/'a').stat();self.assertEqual((st.st_atime_ns,st.st_mtime_ns),TIMES)
  (root/'alias').symlink_to(root/'a')
  with self.assertRaises(OSError):read_bytes_noatime(root/'alias')
 def test_whole_inverse_and_no_foreign_edits(self):
  import file_transaction_timestamp_patch as patch
  old=self.source();new=patch.transform(old);self.assertEqual(patch.reverse(new),old)
  with self.assertRaises(ValueError):patch.transform(old+'\n')
  with self.assertRaises(ValueError):patch.reverse(new.replace('self.quiescent();self.sealed=True','self.sealed=True'))

if __name__=='__main__':unittest.main()
