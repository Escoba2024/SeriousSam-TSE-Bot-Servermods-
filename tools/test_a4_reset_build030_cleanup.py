"""Actual inherited ResetV3 cleanup loop; no game/runtime imports."""
import ast
import os
from pathlib import Path
import unittest


class ResetCleanupHook(unittest.TestCase):
 def test_actual_role_loop_keeps_observer_and_later_closes_on_receipt_failure(self):
  from prepare_a4_reset_build030 import PARENT, read, controller
  old=read(PARENT/'run-mapreset.py').decode()
  source=controller(old)
  tree=ast.parse(source)
  loop=next(n for n in ast.walk(tree)if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='role'and isinstance(n.iter,ast.Tuple)and [x.value for x in n.iter.elts]==['vanilla','botB','botA','server'])
  for archive_fails in (False,True):
   calls=[];archives=[];observed=[];report={'errors':[]}
   def close(role):
    calls.append(role)
    if role=='botB':raise FileNotFoundError(2,'gone','/owned/cgroup.procs')
   def archive_observer():observed.append('vanilla')
   class Receipt:
    def record(self,role,error):
     archives.append((role,type(error).__name__,error.filename))
     if archive_fails:raise OSError(5,'receipt disk')
   env=dict(records={},close=close,archive_observer=archive_observer,report=report,cleanup_failures=Receipt())
   exec(compile(ast.fix_missing_locations(ast.Module(body=[loop],type_ignores=[])),'actual-reset-cleanup','exec'),env)
   self.assertEqual(calls,['vanilla','botB','botA','server'])
   self.assertEqual(observed,['vanilla'])
   self.assertEqual(archives,[('botB','FileNotFoundError','/owned/cgroup.procs')])
   self.assertTrue(report['errors'][0].startswith('cleanup botB:FileNotFoundError'))
   self.assertEqual(len(report['errors']),2 if archive_fails else 1)
   if archive_fails:self.assertTrue(report['errors'][1].startswith('cleanup exception receipt botB:'))


if __name__=='__main__':unittest.main()
