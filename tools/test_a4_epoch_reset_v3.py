"""Offline epoch contracts using the actual derived V3 bodies; no native access."""
import copy
import importlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_a4_canonical_native_groups as fixtures


class ResetEpochTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import prepare_a4_epoch_reset_v3 as builder
  cls.directory=tempfile.TemporaryDirectory()
  root=Path(cls.directory.name)
  for name,text in builder.observer_sources().items():(root/name).write_text(text)
  for name,text in builder.rule_sources().items():(root/name).write_text(text)
  (root/'a4_epoch_reset_observation.py').write_text(Path(builder.__file__).with_name('a4_epoch_reset_observation.py').read_text())
  sys.path.insert(0,str(root));cls.v3=importlib.import_module('a4_reset_ordered_memory_v3')
  cls.groups=importlib.import_module('a4_reset_groups_v3')
  cls.rules=importlib.import_module('a4_reset_hard_rules')
  cls.reads=importlib.import_module('a4_epoch_reset_observation')
 @classmethod
 def tearDownClass(cls):
  sys.path.pop(0)
  for name in ('a4_reset_ordered_memory_v3','a4_reset_groups_v3','a4_reset_hard_rules','a4_epoch_reset_observation'):sys.modules.pop(name,None)
  cls.directory.cleanup()
 def fixture(self,phase):
  f=fixtures.CanonicalGroupTests();f.setUp();mapping=f.f.mapping;identity=f.f.identity
  offsets={r:phase*100 for r in ('server','botA','botB')}
  contract=self.groups.declare(mapping,identity,offsets,phase)
  registry=copy.deepcopy(f.f.registry);registry.update(phase=phase,native_fire_epoch=contract['observer_epoch'],native_group_contract=contract,memory_observation_contract=self.v3.read_contract(contract))
  journal=self.v3.AttemptJournal(io.StringIO());samples=[]
  for i,s in enumerate(f.samples,1):
   raw=copy.deepcopy(s);name=raw.pop('native_group_provenance')['name'];raw.pop('observer_epoch')
   start=phase*10+i*.01;end=start+.001
   journal.begin(i,name,start,'gameplay');journal.end(i,end,True)
   samples.append(self.v3.bind_sample(raw,name,contract,i,start,end))
  return f,contract,registry,journal,samples
 def apply(self,data):
  f,c,r,j,s=data
  return self.v3.apply(f.result(),f.f.logs,f.f.mapping,s,r,f.f.identity,c,j.records)
 def test_all_three_real_epoch_contracts_prove_exactly_24_slots(self):
  keys=[]
  for phase in range(3):
   data=self.fixture(phase);out=self.apply(data)
   self.assertEqual(out['memory_observation_epoch']['phase'],phase)
   for slot in out['slots'].values():
    proof=slot['memory_flag_observations']
    self.assertGreater(proof['actual_useful_inventory_gains'],0)
    self.assertGreater(proof['native_fire_flag_observations_with_same_life_source_growth'],0)
   keys.extend((phase,k)for k in out['slots'])
  self.assertEqual(len(set(keys)),24)
 def test_foreign_epoch_even_identical_process_pointer_and_ticks_fails_before_evidence(self):
  a=self.fixture(0);b=self.fixture(1);b[-1][0]=copy.deepcopy(a[-1][0])
  with patch.object(self.v3.audit,'slot_evidence',side_effect=AssertionError('hulls first')):
   with self.assertRaises(ValueError):self.apply(b)
 def test_wrong_phase_offsets_group_registry_and_omitted_early_rows_fail(self):
  for change in ('offset','group','phase','registry','missing','serial'):
   data=self.fixture(2);f,c,r,j,s=data
   if change=='offset':s[0]['observer_epoch']['log_offsets']['botA']=0
   elif change=='group':s[0]['native_group_provenance']['name']='botB_actual'
   elif change=='phase':c['observer_epoch']['phase']=False
   elif change=='registry':r['players'][0]['entity_pointer']+=4
   elif change=='missing':s.pop(0)
   else:s[0]['memory_observation']['read_serial']=0
   with self.subTest(change=change),self.assertRaises(ValueError):self.apply(data)
 def test_phase_scope_does_not_bless_nonatomic_or_weapon_call_claim(self):
  out=self.apply(self.fixture(1))
  self.assertFalse(out['memory_observation']['atomic_snapshot'])
  self.assertFalse(out['memory_observation']['weapon_function_call_proven'])
  self.assertFalse(out['qualified']);self.assertFalse(out['functional_pass'])
 def test_old_v3_and_canonical_bodies_only_change_phase_and_dependency(self):
  import prepare_a4_epoch_reset_v3 as builder
  sources=builder.observer_sources()
  self.assertEqual(sources['a4_reset_ordered_memory_v3.py'].replace('import a4_reset_groups_v3 as groups','import a4_canonical_native_groups as groups'),(builder.V3/'a4_ordered_memory_v3.py').read_text())
 def test_hard2_and_exact_phase_time_limits_without_ignored_fields(self):
  import struct
  for phase,minutes in enumerate((2,2,0)):
   raw=bytearray(156)
   for key,(fmt,offset)in self.rules.FIELDS.items():
    struct.pack_into(fmt,raw,offset,minutes if key=='timelimit'else self.rules.EXPECTED[key])
   self.assertEqual(self.rules.validate_session({'session156_hex':raw.hex()},phase)['timelimit'],minutes)
   for field,(fmt,offset)in self.rules.FIELDS.items():
    bad=bytearray(raw);old=struct.unpack_from(fmt,bad,offset)[0];struct.pack_into(fmt,bad,offset,old+1)
    with self.subTest(phase=phase,field=field),self.assertRaises(ValueError):self.rules.validate_session({'session156_hex':bad.hex()},phase)
  for phase in (-1,3,False):
   with self.assertRaises(ValueError):self.rules.validate_session({'session156_hex':raw.hex()},phase)
 def test_actual_read_body_calls_reader_once_and_journals_failure(self):
  f,c,r,j,s=self.fixture(1);raw=copy.deepcopy(f.samples[0]);raw.pop('native_group_provenance');raw.pop('observer_epoch')
  stream=io.StringIO();times=iter((10.,10.001,10.01,10.011))
  obs=self.reads.PhaseReads(1,f.f.mapping,f.f.identity,c['observer_epoch']['log_offsets'],stream,clock=lambda:next(times))
  calls=[]
  def reader(slots):calls.append(slots);return raw
  out=obs.sample(reader,tuple(f.f.mapping['botA']),'botA_actual')
  self.assertEqual(calls,[tuple(f.f.mapping['botA'])]);self.assertEqual(out['memory_observation']['read_serial'],1)
  error=RuntimeError('state changed during read')
  def fail(slots):calls.append(slots);raise error
  with self.assertRaises(RuntimeError)as caught:obs.sample(fail,tuple(f.f.mapping['botA']),'botA_actual')
  self.assertIs(caught.exception,error);self.assertEqual(len(calls),2)
  self.assertEqual(obs.journal.records[-1]['status'],'error');self.assertIsNone(obs.journal.pending)
  self.assertNotIn('snapshot',stream.getvalue());self.assertFalse(obs.finished)
 def registry_fixture(self,phase):
  f,c,r,j,s=self.fixture(phase)
  ids=dict(server=list(f.f.identity),botA=[901,1001],botB=[902,1002])
  r['persistent_identities']=ids
  r['round_begin_order']=list(range(1,phase+2))
  if phase:
   slots=f.f.mapping['botA']+f.f.mapping['botB'];rows={p['slot']:p for p in r['players']}
   r['reset_epoch_receipt']=dict(state='REGISTRY_CONFIRMED',registry_confirmed=True,phase=phase,
    epoch=copy.deepcopy(c['observer_epoch']),identities=ids,mapping=f.f.mapping,
    begin_order=list(range(1,phase+2)),scan_offsets={role:(phase-1)*100 for role in ids},
    log_offsets=copy.deepcopy(c['observer_epoch']['log_offsets']),prior_end_tick=121.,
    anchor_server=dict(game_tick=.1,players=[dict(slot=slot,entity_pointer=rows[slot]['entity_pointer'])for slot in slots]),
    bindings={str(slot):[rows[slot][k]for k in ('entity_id','entity_pointer','world_pointer')]for slot in slots},
    entity_ids={slot:rows[slot]['entity_id']for slot in slots},accepted_samples=2)
  return f,c,r,j,s
 def test_actual_early_eight_to_nine_receipt_required_before_binding_each_reset(self):
  for phase in range(3):
   f,c,r,j,s=self.registry_fixture(phase)
   obs=self.reads.PhaseReads(phase,f.f.mapping,f.f.identity,c['observer_epoch']['log_offsets'],io.StringIO())
   obs.bind_registry(r)
   self.assertEqual(obs.registry['reset_observation_proof']['actual_begin_order'],list(range(1,phase+2)))
  for change in ('missing','unconfirmed','old_epoch','identity','order','offset','clock','entity','world','early_missing','registry_phase','registry_map','registry_begin'):
   f,c,r,j,s=self.registry_fixture(2);early=r['reset_epoch_receipt']
   if change=='missing':del r['reset_epoch_receipt']
   elif change=='unconfirmed':early['registry_confirmed']=False
   elif change=='old_epoch':early['phase']=1
   elif change=='identity':early['identities']=dict(early['identities'],botB=[999,1002])
   elif change=='order':early['begin_order']=[1,3]
   elif change=='offset':early['log_offsets']['botA']=0
   elif change=='clock':early['anchor_server']['game_tick']=early['prior_end_tick']
   elif change=='entity':early['bindings']['0'][0]+=1
   elif change=='world':early['bindings']['0'][2]+=4
   elif change=='early_missing':early['bindings'].pop('0')
   elif change=='registry_phase':r['phase']=1
   elif change=='registry_map':r['actual_slot_mapping']=dict(r['actual_slot_mapping'],botA=[3,2,1,0])
   else:r['round_begin_order']=[1]
   obs=self.reads.PhaseReads(2,f.f.mapping,f.f.identity,c['observer_epoch']['log_offsets'],io.StringIO())
   with self.subTest(change=change),self.assertRaises(ValueError):obs.bind_registry(r)
 def test_full_sequence_requires_three_real_cuts_and_persistent_roles_even_with_pointer_reuse(self):
  results=[];ids=None
  for phase in range(3):
   f,c,r,j,s=self.registry_fixture(phase);ids=r['persistent_identities']
   proof=self.reads.reset_receipt(r,c)
   results.append(dict(phase=phase,slots={str(i):{}for i in range(8)},reset_observation_proof=proof))
  self.assertEqual(self.reads.validate_sequence(results,ids)['bot_slotphases'],24)
  for change in ('missing','pid','begin','offset','slot'):
   bad=copy.deepcopy(results)
   if change=='missing':bad.pop()
   elif change=='pid':bad[1]['reset_observation_proof']['persistent_identities']['botA'][1]+=1
   elif change=='begin':bad[1]['reset_observation_proof']['actual_begin_order']=[1]
   elif change=='offset':bad[1]['reset_observation_proof']['observer_epoch']['log_offsets']['server']=0
   else:bad[1]['slots'].pop('0')
   with self.subTest(change=change),self.assertRaises(ValueError):self.reads.validate_sequence(bad,ids)


if __name__=='__main__':unittest.main()
