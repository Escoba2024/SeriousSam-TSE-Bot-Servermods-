"""Offline graph and source-inverse tests; never import run-a4.py."""
import ast
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


GRAPH=r'''
import copy,io,json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import powerup_server_module_policy as policy
import powerup_server_native_fire as core
import a4_fire_observer_v2 as original
import a4_canonical_native_groups as groups
import a4_ordered_memory_v3 as v3
from test_a4_fire_observer_v2 import BoundObserverTests
f=BoundObserverTests();f.setUp()
contract=groups.declare(f.mapping,f.identity,f.offsets)
registry=copy.deepcopy(f.registry);registry['phase']=0;registry['native_fire_epoch']=core.epoch(0,f.identity,f.offsets)
registry['native_group_contract']=contract;registry['memory_observation_contract']=v3.read_contract(contract)
samples=[];full=[];journal=v3.AttemptJournal(io.StringIO())
for old in f.samples:
 raw=copy.deepcopy(old);raw.pop('observer_epoch');raw['hashes']['GameMP.dll']=policy.SERVER_SHA
 # Synthetic portable fixture adaptation only, never a rewrite of native data.
 full.append(core.bind_sample(raw,0,f.identity,f.offsets))
 for name,slots in contract['groups'].items():
  s=copy.deepcopy(raw);s['players']=[next(p for p in s['players']if p['slot']==slot)for slot in slots]
  for p in s['players']:p['placement']=[0.,0.,0.,0.,0.,0.]
  s['all_selected_present']=True;i=len(samples)+1;start=i*.01;end=start+.001
  journal.begin(i,name,start,'gameplay');journal.end(i,end,True)
  samples.append(v3.bind_sample(s,name,contract,i,start,end))
result=dict(missing_activity=['botA:0:fire_action_rows','unrelated:missing'],slots={f'{r}:{i}':dict(fire_action_rows=0)for r in('botA','botB')for i in range(4)},qualified=False,functional_pass=False)
out=v3.apply(result,f.logs,f.mapping,samples,registry,f.identity,contract,journal.records)
assert out['missing_activity']==['unrelated:missing']
assert len(core.evidence(f.logs,f.mapping,full,registry,f.identity))==8
assert out['memory_observation']['raw_samples']==9
assert not out['qualified']and not out['functional_pass']
raw=copy.deepcopy(full[0]);raw.pop('observer_epoch')
try:original.check_sample(raw,f.identity)
except ValueError as e:assert 'sample Original module hashes'in str(e)
else:raise AssertionError('original core weakened')
core.bind_sample(raw,0,f.identity,f.offsets)
for name in('Engine.dll','EntitiesMP.dll','GameMP.dll'):
 s=copy.deepcopy(raw);s['hashes'][name]='0'*64
 try:core.bind_sample(s,0,f.identity,f.offsets)
 except ValueError:pass
 else:raise AssertionError('wrong hash admitted')
for role in('botA','botB','vanilla'):
 try:policy.check_sample_hashes(raw,role,f.identity)
 except ValueError:pass
 else:raise AssertionError('wrong role admitted')
for field,value in [('process_identity',[100,201]),('consistency','unknown')]:
 s=copy.deepcopy(raw);s[field]=value
 try:core.bind_sample(s,0,f.identity,f.offsets)
 except ValueError:pass
 else:raise AssertionError('identity/consistency weakened')
# Excluded overlap is still checked at final validation, not silently discarded.
for digest in('0'*64,original.ORIGINAL_HASHES['GameMP.dll'],'ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530'):
 bad=copy.deepcopy(samples);bad[2]['hashes']['GameMP.dll']=digest
 try:v3.validate_all(bad,registry,f.mapping,f.identity,contract,journal.records)
 except ValueError:pass
 else:raise AssertionError('overlap hash weakened')
# Execute only the exact source-derived first-raw hook + its old bind statement.
source=(Path(sys.argv[1])/'run-a4.py').read_text();line=next(l for l in source.splitlines()if 'if read_serial==1:server_modules.archive_first_sample'in l)
bind=next(l for l in source.splitlines()if "assert snap['all_selected_present'];snap=canonical_groups.bind_sample"in l)
snap=copy.deepcopy(raw);snap['hashes']['Engine.dll']='0'*64;snap['all_selected_present']=True
scope=dict(read_serial=1,server_modules=policy,E=Path(sys.argv[2]),snap=snap,group='botA_actual',server=f.identity,sample_start=1.,sample_end=1.01,canonical_groups=v3,native_group_contract=contract,inventory_stream=io.StringIO(),json=json)
try:exec(line.lstrip()+'\n'+bind.lstrip(),scope)
except ValueError:pass
else:raise AssertionError('expected bind failure')
saved=json.loads((Path(sys.argv[2])/'first-unbound-server-inventory.jsonl').read_text())
assert saved['sample']==snap and scope['inventory_stream'].getvalue()==''
print(json.dumps(dict(raw_samples=9,canonical_samples=6,slots=8,original_core_unchanged=True,overlap_guards=True,negative_bind_raw_preserved=True,qualified=False)))
'''


class ServerModuleBuilder(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_powerup_server_modules'),'missing disabled server-module fork builder')
  import prepare_powerup_server_modules as b
  return b
 def test_exact_inverse_core_copy_and_two_modified_import_paths(self):
  b=self.builder();self.assertEqual(b.CHANGED,('run-a4.py','a4_canonical_native_groups.py'))
  for flag in(0,1):
   parent=b.PARENTS[flag][0]
   for name in b.CHANGED:
    old=(parent/name).read_text();new=b.transform(name,old,flag);ast.parse(new)
    self.assertEqual(b.reverse(name,new,flag),old)
    with self.assertRaises(ValueError):b.transform(name,new,flag)
    with self.assertRaises(ValueError):b.transform(name,old+old,flag)
   old=(parent/'a4_fire_observer_v2.py').read_text();new=b.server_core(old)
   self.assertEqual(b.reverse_core(new),old)
   self.assertIn("server_modules.check_sample_hashes(sample, 'server', server_identity)",new)
   self.assertIn("require(sample.get('consistency') == 'two_equal_reads_not_atomic'",new)
   with self.assertRaises(ValueError):b.server_core(new)
   run=b.transform('run-a4.py',(parent/'run-a4.py').read_text(),flag)
   old_run=(parent/'run-a4.py').read_text()
   self.assertEqual(run[run.index('  finally:\n   was_raising='):],old_run[old_run.index('  finally:\n   was_raising='):])
   self.assertEqual(run.count('server_modules.archive_first_sample('),1)
   self.assertLess(run.index('server_modules.archive_first_sample('),run.index("snap=canonical_groups.bind_sample(snap,"))
 def test_parent_mutants_and_no_destination_on_bad_hash(self):
  b=self.builder()
  for flag in(0,1):
   parent,expected=b.PARENTS[flag];original=json.loads((parent/'source-manifest.json').read_text())
   for key in('runtime_reviewed','runtime_performed','qualified','functional_pass'):
    m=copy.deepcopy(original);m[key]=True
    with self.assertRaises(ValueError):b.validate_parent_manifest(m,flag)
   for key,value in[('flag',1-flag),('dedicated_sha256','0'*64),('bot_sha256','0'*64),('closure_targets',80)]:
    m=copy.deepcopy(original);m['powerup_contrast'][key]=value
    with self.assertRaises(ValueError):b.validate_parent_manifest(m,flag)
   real=b.sha
   for target in(parent/'source-manifest.json',parent/'a4_fire_observer_v2.py',parent/'a4_ordered_memory_v3.py'):
    with tempfile.TemporaryDirectory()as d,patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
     dest=Path(d)/'none'
     with self.assertRaisesRegex(ValueError,'parent'):b.prepare(dest,flag)
     self.assertFalse(dest.exists())
 def test_fresh_disabled_all_pins_unchanged_originals_and_graph(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as d:
   for flag in(0,1):
    parent=b.PARENTS[flag][0];pm=json.loads((parent/'source-manifest.json').read_text());dest=Path(d)/f'arm{flag}'
    result=b.prepare(dest,flag);m=json.loads((dest/'source-manifest.json').read_text())
    for key in('runtime_reviewed','runtime_performed','qualified','functional_pass'):self.assertIs(m[key],False)
    self.assertEqual(m['powerup_contrast'],pm['powerup_contrast'])
    for key in('host_budget','read_contract','candidate','comparison','canonical_profile_migration'):self.assertEqual(m[key],pm[key])
    self.assertEqual((dest/'a4_fire_observer_v2.py').read_bytes(),(parent/'a4_fire_observer_v2.py').read_bytes())
    for name in pm['sources']:
     if name in b.CHANGED:self.assertEqual(b.reverse(name,(dest/name).read_text(),flag),(parent/name).read_text())
     else:self.assertEqual((dest/name).read_bytes(),(parent/name).read_bytes(),name)
    self.assertEqual(b.reverse_core((dest/'powerup_server_native_fire.py').read_text()),(parent/'a4_fire_observer_v2.py').read_text())
    for key,base in[('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
     for name,h in m[key].items():self.assertEqual(b.sha(base/name),h,(key,name))
    self.assertEqual(result['dedicated_closure_pins'],81)
    self.assertFalse(result['native_started'])
    raw=Path(d)/f'raw{flag}';raw.mkdir()
    completed=subprocess.run([sys.executable,'-c',GRAPH,str(dest),str(raw)],capture_output=True,text=True,timeout=10)
    self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
    self.assertTrue(json.loads(completed.stdout)['negative_bind_raw_preserved'])
    with self.assertRaises(ValueError):b.prepare(dest,flag)


if __name__=='__main__':unittest.main()
