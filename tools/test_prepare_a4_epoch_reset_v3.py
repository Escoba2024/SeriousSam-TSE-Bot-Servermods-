"""Exact prospective reset-controller boundaries; never executes runtime main."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest


class EpochResetControllerTests(unittest.TestCase):
 def source(self):
  import prepare_a4_epoch_reset_v3 as builder
  self.assertTrue(callable(getattr(builder,'transform_controller',None)), 'missing reviewed reset-controller adaptation')
  return builder,builder.transform_controller((builder.PARENT/'run-mapreset.py').read_text())
 def test_disabled_fixed_protocol_and_all_existing_read_input_sleep_calls(self):
  builder,s=self.source();parent=(builder.PARENT/'run-mapreset.py').read_text()
  self.assertIn('RUNTIME_REVIEWED=False',s);self.assertIn('duration==480 and diag==0',s)
  self.assertIn("main('redstation',480,0)",s)
  self.assertIn('protocol.complete(elapsed,snapshots[\'server\'][\'game_tick\']-phase_start_tick)',s)
  self.assertIn('observer.history_reasons(observer_history,complete=',s)
  def calls(text,ends):
   return [ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(text))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ends]
  self.assertEqual(calls(s,('sleep',)),calls(parent,('sleep',)))
  self.assertEqual(calls(s,('read_pause',)),calls(parent,('read_pause',)))
  def count(text,owner,name):
   return sum(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id==owner and n.func.attr==name for n in ast.walk(ast.parse(text)))
  self.assertEqual(count(parent,'inventory','sample'),3)
  self.assertEqual(count(s,'phase_reads','sample'),3)
  self.assertEqual(count(s,'inventory','sample'),0)
  self.assertEqual(count(s,'B','query'),1)
  self.assertIn("phase_reads.sample(inventory.sample,tuple(capture.mapping[group]),group+'_actual')",s)
  self.assertNotIn("groups=[('slots0to3'",s)
 def test_epoch_before_every_first_read_and_registry_before_persist(self):
  _,s=self.source()
  self.assertIn('phase_reads=begin_read_epoch(phase,next_mapping,early_capture.epoch[\'log_offsets\'])',s)
  self.assertIn('phase_reads=begin_read_epoch(0,mapping,dict(server=0,botA=0,botB=0))',s)
  self.assertLess(s.index('phase_reads=begin_read_epoch(phase,'),s.index('   inventory=InventoryReader',s.index('def arm_transition_inventory')))
  self.assertIn('phase_reads.bind_registry(reg)',s)
  self.assertIn('phase_reads.apply(result,',s)
  self.assertIn("groups=list(phase_reads.contract['groups'].items())",s)
 def test_corrected_none_query_renderer_and_original_deadline_guards_stay(self):
  b,s=self.source()
  for anchor in ('operation_deadline=min(start+480,start+protocol.ended+19)','operation_deadline=min(start+480,start+protocol.ended+50)',"observer.wait_lowrender_start(","if str(error)not in('state changed during read','tick changed during read'):raise"):
   self.assertIn(anchor,s)
  reset=b.reset_source();self.assertIn('if name is None:return False',reset)
  self.assertIn('gam_iStartDifficulty=2;',reset);self.assertNotIn('gam_iStartDifficulty=3;',reset)
  self.assertIn("MAPS=('redstation','redstation','redstation')",reset)
  self.assertIn('EXPECTED_TIME_LIMITS = (2, 2, 0)',reset)
  tree=ast.parse(s);method=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='checked_query')
  scope={}
  exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),'actual query','exec'),scope)
  class Backend:
   response={}
   def query(self,pid):return self.response
  class Rules:
   @staticmethod
   def validate_query(q):
    if q.get('difficulty')!='Hard':raise ValueError('wrong difficulty')
  backend=Backend();scope.update(B=backend,server=(123,456),hard_rules=Rules)
  self.assertEqual(scope['checked_query'](pending=True),{})
  with self.assertRaises(ValueError):scope['checked_query']()
  backend.response={'difficulty':'Serious'}
  with self.assertRaises(ValueError):scope['checked_query'](pending=True)
 def test_builder_fresh_disabled_complete_pins_and_unchanged_safety_sources(self):
  import prepare_a4_epoch_reset_v3 as builder
  self.assertTrue(callable(getattr(builder,'prepare',None)),'missing disabled package builder')
  with tempfile.TemporaryDirectory()as temp:
   dest=Path(temp)/'disabled';result=builder.prepare(dest)
   m=json.loads((dest/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['runtime_performed'])
   self.assertFalse(m['qualified']);self.assertFalse(m['functional_pass'])
   self.assertEqual((m['derivation']['duration_seconds'],m['derivation']['phases'],m['derivation']['bot_slotphases']),(480,3,24))
   self.assertEqual((result['build_source_pins'],result['build_overlay_pins']),(47,28))
   for p,h in m['runtime_dependencies'].items():self.assertEqual(hashlib.sha256(Path(p).read_bytes()).hexdigest(),h,p)
   for name,h in m['sources'].items():self.assertEqual(hashlib.sha256((dest/name).read_bytes()).hexdigest(),h,name)
   for name in ('strict_backend.py','transaction.py','host_budget.py','observer_policy.py','phase_inventory.py','round_script_io.py'):
    self.assertEqual((dest/name).read_bytes(),(builder.PARENT/name).read_bytes(),name)
   for name in builder.V3_FILES:self.assertEqual((dest/name).read_bytes(),(builder.V3/name).read_bytes(),name)
   self.assertEqual((dest/'canonical.ini').read_bytes(),(builder.V3/'canonical.ini').read_bytes())
   self.assertFalse(json.loads((dest/'HANDOFF-disabled.json').read_text())['runtime_authorized'])
   with self.assertRaises(ValueError):builder.prepare(dest)


if __name__=='__main__':unittest.main()
