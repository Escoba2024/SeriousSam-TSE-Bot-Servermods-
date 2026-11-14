"""A common lower rendering cost, without changing native evidence gates."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import navigation_observer20 as observer
import prepare_navigation_observer20 as builder


class ObserverScript(unittest.TestCase):
 def test_exact_original_only_two_render_assignments_change(self):
  raw=observer.EXPECTED_PATH.read_bytes()
  actual=observer.transform(raw)
  self.assertEqual(actual,raw.replace(b'sam_iMaxFPSActive=30;',b'sam_iMaxFPSActive=20;').replace(b'sam_iMaxFPSInactive=30;',b'sam_iMaxFPSInactive=20;'))
  self.assertEqual(actual.count(b'=20;'),2)
 def test_any_changed_original_is_rejected(self):
  raw=observer.EXPECTED_PATH.read_bytes()
  for bad in [raw+b'//changed',raw.replace(b'=30;',b'=10;'),raw+raw]:
   with self.assertRaises(ValueError):observer.transform(bad)
 def test_other_paths_rejected_and_expected_fixture_restorable(self):
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'observer.ini';raw=observer.EXPECTED_PATH.read_bytes();path.write_bytes(raw)
   with self.assertRaises(ValueError):observer.stage(path)
   self.assertEqual(path.read_bytes(),raw)
   with patch.object(observer,'EXPECTED_PATH',path):receipt=observer.stage(path)
   self.assertEqual(receipt['before_sha256'],hashlib.sha256(raw).hexdigest())
   self.assertEqual(receipt['after_sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
   self.assertEqual(receipt['fps'],20)


class Derivation(unittest.TestCase):
 def test_stage_only_after_complete_snapshot_and_before_first_start(self):
  for build in ('048','018','020'):
   before=(builder.PARENTS[build][0]/'run-a4.py').read_text();after=builder.transform(before,build)
   self.assertLess(after.index('transaction.seal()'),after.index("report['observer_render_config']=stage_observer20("))
   self.assertLess(after.index("report['observer_render_config']=stage_observer20("),after.index("   launch('server')"))
   reverse=after.replace('from navigation_observer20 import stage as stage_observer20\n','')
   reverse=reverse.replace("   report['observer_render_config']=stage_observer20(R/'vanilla/Scripts/CecilObserver.ini')\n",'')
   reverse=reverse.replace(f'ssam-nav20-{build}-hard-ordered-',f'ssam-nav-{build}-hard-ordered-').replace(f'nav20-{build}-hard-ordered-',f'nav-{build}-hard-ordered-')
   self.assertEqual(reverse,before)
   self.assertIn('RUNTIME_REVIEWED=False',after)
 def test_parent_manifests_are_the_three_actual_immutable_arms(self):
  for path,expected in builder.PARENTS.values():self.assertEqual(builder.sha(path/'source-manifest.json'),expected)
 def test_ambiguous_transaction_anchor_rejected(self):
  text=(builder.PARENTS['048'][0]/'run-a4.py').read_text()
  with self.assertRaises(ValueError):builder.transform(text+'\n   transaction.seal()\n','048')


if __name__=='__main__':unittest.main()
