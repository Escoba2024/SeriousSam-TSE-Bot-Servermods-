"""Actual extracted admission/CLI/options, never import the runtime controller."""
import ast
import math
import copy
import hashlib
import json
import re
import tempfile
from pathlib import Path
import types
import unittest

from prepare_navigation_build030_skulls import read
PARENT=Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115')

def transformed(name):
 source=read(PARENT/name).decode()
 try:import prepare_a4_reset_build031 as builder
 except ModuleNotFoundError:return source
 return builder.transform(name,source)

def admission(source,gate=True):
 node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='main')
 node.body=node.body[:3] # global, disabled gate, fixed protocol admission only
 scope={'RUNTIME_REVIEWED':gate}
 exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'actual-admission','exec'),scope)
 return scope['main']

def options(source):
 node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='options')
 scope={'math':math,'prepared':types.SimpleNamespace(catalog=lambda:{'maps':{'redstation':{},'yodeller':{}}})}
 exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-options','exec'),scope)
 return scope['options']

class Admission(unittest.TestCase):
 def test_actual_new_diag1_admission(self):
  admission(transformed('run-mapreset.py'))('redstation',480,1)
 def test_actual_cli_is_diag1_not_merely_new_metadata(self):
  tree=ast.parse(transformed('run-mapreset.py'))
  calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='main']
  self.assertEqual([[ast.literal_eval(a)for a in n.args]for n in calls],[['redstation',480,1]])
 def test_options_reject_old_diag_and_other_window(self):
  fn=options(transformed('adapter_policy.py'))
  for args in [('redstation',480,0),('redstation',600,1),('yodeller',480,1)]:
   with self.subTest(args=args),self.assertRaises(ValueError):fn(*args)
 def test_disabled_gate_blocks_even_valid_diagnostic(self):
  with self.assertRaises(RuntimeError):admission(transformed('run-mapreset.py'),False)('redstation',480,1)

class ClosureAndInverses(unittest.TestCase):
 def setUp(self):
  import prepare_a4_reset_build031 as b
  self.b=b;self.spec=b.candidate()
  self.manifest=json.loads(read(b.BUILD/'manifest.json'))
  self.parent=json.loads(read(PARENT/'source-manifest.json'))
 def test_actual_manifest_and_fixed_closure_values(self):
  self.b.validate_build(self.manifest,self.spec)
  self.assertEqual((len(self.spec['source_sha256']),len(self.spec['overlay_sha256'])),(49,30))
 def test_wrong_provenance_manifest_and_each_closure_class_fail(self):
  for key,bad in [('build_ok',False),('qualified',True),('repo_commit','0'*40),('repo_tree','1'*40),('candidate','elsewhere.dll'),('source_overlay','elsewhere'),('source_count',16),('dll_sha256','0'*64)]:
   m=copy.deepcopy(self.manifest);m[key]=bad
   with self.subTest(key=key),self.assertRaises(ValueError):self.b.validate_build(m,self.spec)
  for key in ('source_sha256','overlay_sha256'):
   for change in ('hash','missing','extra'):
    m=copy.deepcopy(self.manifest);name=next(iter(m[key]))
    if change=='hash':m[key][name]='0'*64
    elif change=='missing':del m[key][name]
    else:m[key]['extra.h']='0'*64
    with self.subTest(key=key,change=change),self.assertRaises(ValueError):self.b.validate_build(m,self.spec)
  for key in ('manifest_sha256','dll_size','source_commit'):
   spec=copy.deepcopy(self.spec);spec[key]=0
   with self.subTest(caller=key),self.assertRaises(ValueError):self.b.validate_build(self.manifest,spec)
 def test_manifest_hash_mismatch_before_target_reads(self):
  with tempfile.TemporaryDirectory()as tmp:
   Path(tmp,'manifest.json').write_text('{}')
   with self.assertRaisesRegex(ValueError,'manifest changed'):
    self.b.build_pins(Path(tmp),'0'*64,'0'*64,81)
 def test_guarded_old_parent_conditions(self):
  self.b.validate_parent(self.parent)
  mutations=[('rounds',['yodeller']*3),('observation_cap_seconds',600),('runtime_reviewed',True),('transition_cap_seconds',51)]
  for k,v in mutations:
   m=copy.deepcopy(self.parent);m[k]=v
   with self.subTest(key=k),self.assertRaises(ValueError):self.b.validate_parent(m)
  for k,v in [('diagnostics',1),('hard_difficulty',3),('bot_slotphases',23),('actual_resets',1),('original_restarts',1)]:
   m=copy.deepcopy(self.parent);m['derivation'][k]=v
   with self.subTest(key=k),self.assertRaises(ValueError):self.b.validate_parent(m)
 def test_three_whole_source_inverses_and_staging_rejection(self):
  for name in self.b.replacements():
   before=read(PARENT/name).decode();after=self.b.transform(name,before)
   self.assertEqual(self.b.transform(name,after,True),before)
   with self.assertRaises(ValueError):self.b.transform(name,after)
   first=self.b.replacements()[name][0][0]
   with self.assertRaises(ValueError):self.b.transform(name,before.replace(first,'mutated fragment'))
 def test_exact_two_changed_one_added_input_delta(self):
  old=json.loads(read(self.b.OLD_BUILD/'manifest.json'))
  delta=self.b.input_delta(old,self.manifest)
  self.assertEqual([delta[k]['changed']for k in delta],[['BotDriver.cpp','BotSupplyNative.h']]*2)
  for key in ('source_sha256','overlay_sha256'):
   m=copy.deepcopy(self.manifest);m[key]['cecil_motion.h']='0'*64
   with self.assertRaises(ValueError):self.b.input_delta(old,m)
 def test_configuration_and_original_video_preserved(self):
  source=transformed('adapter_policy.py')
  names=('assignments','replace','cohort')
  nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name in names]
  scope={'re':re,'hashlib':hashlib,'canonical':lambda:read(PARENT/'canonical.ini').decode(),'CANDIDATE_SHA':self.spec['dll_sha256']}
  exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual-cohort','exec'),scope)
  for role,offset in [('botA','0'),('botB','4')]:
   config=scope['cohort'](role,1)
   rows=scope['assignments'](config['config'])
   self.assertEqual(rows['bot_bDiagnostics'],'1');self.assertEqual(rows['bot_iRosterOffset'],offset)
   self.assertEqual([rows['bot_iProfile'+str(i)]for i in range(4)],['7']*4)
   self.assertEqual(rows['bot_iNullRenderFps'],'20')
   self.assertEqual(rows['bot_iProfileSeed'],'2026110750')
  old=read(PARENT/'run-mapreset.py').decode();new=transformed('run-mapreset.py')
  self.assertIn("'fps_active':30,'fps_inactive':30",new)
  self.assertEqual([n for n in old.splitlines()if 'lowrender_persistent' in n],[n for n in new.splitlines()if 'lowrender_persistent' in n])
  self.assertEqual([n for n in old.splitlines()if 'finalize_trial_evidence' in n],[n for n in new.splitlines()if 'finalize_trial_evidence' in n])
  fn=options(source)
  for bad in [False,True,0,2,None,'1']:
   with self.assertRaises(ValueError):fn('redstation',480,bad)
  for bad in [True,float('nan'),float('inf'),479,481,'480']:
   with self.assertRaises(ValueError):fn('redstation',bad,1)
 def test_round_script_only_label_changes(self):
  source=transformed('reset_policy.py')
  node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='round_files')
  scope={'MAPS':('redstation',)*3}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-roundfiles','exec'),scope)
  files=scope['round_files']({'redstation':{'world_path':'Worlds\\Multi\\RedStation.wld'}})
  for i,limit in [(1,2),(2,2),(3,0)]:
   self.assertIn('gam_iTimeLimit='+str(limit)+';',files[str(i)+'_begin.ini'])
   self.assertIn('gam_iStartDifficulty=2;',files[str(i)+'_begin.ini'])
   self.assertIn('gam_ctMaxPlayers=9;',files[str(i)+'_begin.ini'])
   self.assertIn('PRIVATE A4 RESET 031 DIAGNOSTIC',files[str(i)+'_begin.ini'])
 def test_fresh_destination_and_wrong_caller_rejected_before_mutation(self):
  with tempfile.TemporaryDirectory()as tmp:
   with self.assertRaises(ValueError):self.b.prepare(tmp)
  wrong=copy.deepcopy(self.spec);wrong['dll_sha256']='0'*64
  with tempfile.TemporaryDirectory()as tmp:
   dest=Path(tmp)/'fresh'
   with self.assertRaises(ValueError):self.b.prepare(dest,wrong)
   self.assertFalse(dest.exists())

if __name__=='__main__':unittest.main()
