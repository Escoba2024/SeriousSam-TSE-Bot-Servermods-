"""Offline contract checks. No process, input, compiler or runtime access."""
import copy
import io
import unittest
from unittest.mock import patch

import test_a4_canonical_native_groups as fixtures
import test_audit_a4_native_fire_observer_v2 as old_tests
import a4_ordered_memory_v3 as v3
import audit_a4_ordered_memory_v3 as audit


class OrderedObservationTests(unittest.TestCase):
 def setUp(self):
  self.f=fixtures.CanonicalGroupTests();self.f.setUp()
  self.contract=self.f.contract;self.registry=self.f.f.registry
  self.registry['memory_observation_contract']=v3.read_contract(self.contract)
  self.rebind(self.f.samples)
 def rebind(self,samples):
  self.journal=v3.AttemptJournal(io.StringIO());self.samples=[]
  for i,sample in enumerate(samples,1):
   name=sample['native_group_provenance']['name'];start=i*.01;end=start+.001
   self.journal.begin(i,name,start,'gameplay');self.journal.end(i,end,True)
   raw=copy.deepcopy(sample);raw.pop('memory_observation',None)
   self.samples.append(v3.bind_observation(raw,self.contract,i,start,end))
 def apply(self):
  return v3.apply(self.f.result(),self.f.f.logs,self.f.f.mapping,self.samples,self.registry,
                  self.f.f.identity,self.contract,self.journal.records)
 def test_same_tick_different_whole_rows_are_distinct_preserved_observations(self):
  raw=copy.deepcopy(self.f.samples);extra=copy.deepcopy(raw[3]);extra['players'][0]['placement'][1]-=.075
  raw.insert(4,extra);self.rebind(raw);out=self.apply()
  self.assertEqual(out['memory_flag_observer_version'],3)
  self.assertEqual(out['slots']['botA:0']['memory_flag_observations']['native_fire_flag_observations_with_same_life_source_growth'],3)
  self.assertEqual(out['memory_observation']['canonical_samples'],7)
  self.assertFalse(out['memory_observation']['atomic_snapshot']);self.assertFalse(out['memory_observation']['weapon_function_call_proven'])
  self.assertFalse(out['qualified']);self.assertFalse(out['functional_pass'])
 def test_duplicate_or_reverse_serial_rejected_before_evidence(self):
  for serial in (1,0,-1,True):
   previous=copy.deepcopy(self.samples)
   self.samples[1]['memory_observation']['read_serial']=serial
   with self.subTest(serial=serial),patch.object(audit,'slot_evidence',side_effect=AssertionError('envelopes first')):
    with self.assertRaises(ValueError):self.apply()
   self.samples=previous
 def test_boolean_nested_id_is_not_integer_serial(self):
  self.samples[0]['memory_observation']['id']['read_serial']=True
  with self.assertRaises(ValueError):self.apply()
 def test_all_invalid_clocks_bindings_and_failed_attempts_fail_before_evidence(self):
  for change in ('nan','inf','reverse','pid','epoch','raw_false_phase','group','id','serial','missing','failed','world'):
   saved=copy.deepcopy(self.samples);saved_attempts=copy.deepcopy(self.journal.records)
   s=self.samples[2];m=s['memory_observation']
   if change=='nan':m['monotonic_start']=float('nan')
   elif change=='inf':m['monotonic_end']=float('inf')
   elif change=='reverse':m['monotonic_end']=0.
   elif change=='pid':m['id']['server_identity'][1]+=1
   elif change=='epoch':m['id']['observer_epoch']['phase']=1
   elif change=='raw_false_phase':s['observer_epoch']['phase']=False
   elif change=='group':m['id']['group']='botA_actual'
   elif change=='id':m['id']['read_serial']=1
   elif change=='serial':m['read_serial']=1
   elif change=='missing':self.journal.records.pop(5)
   elif change=='failed':self.journal.records[5].update(status='error',error='state changed during read')
   elif change=='world':s['players'][0]['world_pointer']+=4
   with self.subTest(change=change),patch.object(audit,'slot_evidence',side_effect=AssertionError('envelopes first')):
    with self.assertRaises(ValueError):self.apply()
   self.samples=saved;self.journal.records=saved_attempts
 def test_excluded_overlap_bad_hull_or_clock_is_not_hidden(self):
  self.samples[2]['hashes']['GameMP.dll']='0'*64
  with self.assertRaises(ValueError):self.apply()
 def test_same_tick_inventory_transition_is_never_pickup(self):
  raw=copy.deepcopy(self.f.samples)
  for s in raw:
   if s['game_tick']==1.5:s['game_tick']=2.
  self.rebind(raw);out=self.apply()
  self.assertEqual(out['slots']['botA:0']['memory_flag_observations']['actual_useful_inventory_gains'],0)
 def test_counter_reset_does_not_gain_evidence(self):
  self.f.f.logs['botA']=self.f.f.logs['botA'].replace('shots=2','shots=-1')
  out=self.apply();self.assertEqual(out['slots']['botA:0']['memory_flag_observations']['native_fire_flag_observations_with_same_life_source_growth'],0)
 def test_no_overlap_fallback(self):
  for s in self.samples:
   if s['native_group_provenance']['name']=='botA_actual':
    for p in s['players']:p['last_buttons']=0;p['weapons']['owned']=259
  out=self.apply()
  for i in range(4):
   p=out['slots'][f'botA:{i}']['memory_flag_observations']
   self.assertEqual(p['native_fire_flag_observations_with_same_life_source_growth'],0)
   self.assertEqual(p['actual_useful_inventory_gains'],0)
 def test_attempt_sequence_time_and_budget_are_strict(self):
  for invalid in ('duplicate','missing','reverse','nan'):
   previous=copy.deepcopy(self.journal.records)
   if invalid=='duplicate':self.journal.records.insert(2,copy.deepcopy(self.journal.records[0]))
   elif invalid=='missing':self.journal.records.pop(0)
   elif invalid=='reverse':self.journal.records[2]['monotonic_start']=0.
   else:self.journal.records[0]['monotonic_start']=float('nan')
   with self.subTest(invalid=invalid),self.assertRaises(ValueError):self.apply()
   self.journal.records=previous
  j=v3.AttemptJournal(io.StringIO());j.bytes_written=v3.MAX_JOURNAL_BYTES
  with self.assertRaises(ValueError):j.begin(1,'botA_actual',1.,'gameplay')
 def test_failed_read_is_logged_without_becoming_evidence(self):
  self.journal.begin(10,'botA_actual',.10,'gameplay');self.journal.end(10,.101,False,'state changed during read')
  out=self.apply();self.assertEqual(out['memory_observation']['failed_attempts'],1)
 def test_successful_gameplay_attempt_cannot_be_silently_dropped(self):
  self.samples.pop()
  with self.assertRaises(ValueError):self.apply()


class UnchangedSourceAndLifeRules(old_tests.NativeFireReviewTests):
 def result(self):
  result=audit.slot_evidence(audit.source_rows(self.text),self.snapshots,0,0,self.expected)
  # Compatibility for the unchanged assertions only; V3 never emits the old claim.
  result['native_fire_with_same_life_source_growth']=result['native_fire_flag_observations_with_same_life_source_growth']
  return result


if __name__=='__main__':unittest.main()
