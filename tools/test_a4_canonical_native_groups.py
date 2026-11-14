"""Pure prospective group provenance tests. Never requalify archived runs."""
import copy
import unittest
from unittest.mock import patch
import a4_fire_observer_v2 as core
import a4_canonical_native_groups as groups
import test_a4_fire_observer_v2 as fixtures


class CanonicalGroupTests(unittest.TestCase):
 def setUp(self):
  f=fixtures.BoundObserverTests();f.setUp();self.f=f
  self.contract=groups.declare(f.mapping,f.identity,f.offsets)
  f.registry['phase']=0;f.registry['native_fire_epoch']=core.epoch(0,f.identity,f.offsets)
  f.registry['native_group_contract']=copy.deepcopy(self.contract)
  self.samples=[]
  for old in f.samples:
   for group,slots in self.contract['groups'].items():
    raw=copy.deepcopy(old);raw.pop('observer_epoch')
    raw['players']=[next(p for p in raw['players']if p['slot']==slot)for slot in slots]
    for p in raw['players']:p['placement']=[0.,0.,0.,0.,0.,0.]
    raw['all_selected_present']=True
    self.samples.append(groups.bind_sample(raw,group,self.contract))
 def result(self):
  return dict(missing_activity=['botA:0:fire_action_rows','unrelated:missing'],
              slots={f'{r}:{i}':dict(fire_action_rows=0)for r in ('botA','botB')for i in range(4)},qualified=False,functional_pass=False)
 def apply(self,samples=None):
  return groups.apply(self.result(),self.f.logs,self.f.mapping,
        self.samples if samples is None else samples,self.f.registry,self.f.identity,self.contract)
 def test_fixed_groups_and_same_canonical_stream_for_fire_and_pickups(self):
  out=self.apply();self.assertEqual(out['missing_activity'],['unrelated:missing'])
  self.assertEqual(out['native_group_observation']['raw_samples'],9)
  self.assertEqual(out['native_group_observation']['canonical_samples'],6)
  self.assertEqual(out['native_group_observation']['fixed_sources'],{'botA':'botA_actual','botB':'botB_actual'})
  for v in out['slots'].values():
   self.assertEqual(v['native_fire_v2']['native_fire_with_same_life_source_growth'],2)
   self.assertEqual(v['native_fire_v2']['actual_useful_inventory_gains'],1)
  self.assertFalse(out['qualified']);self.assertFalse(out['functional_pass'])
 def test_different_whole_rows_across_overlap_keep_canonical_stream_unchanged(self):
  for s in self.samples:
   if s['native_group_provenance']['name']=='vanilla_plus_overlap':
    for p in s['players']:p['placement'][0]=1.
  out=self.apply();self.assertEqual(out['missing_activity'],['unrelated:missing'])
  # The historical full-stream contract still rejects this input unchanged.
  with self.assertRaisesRegex(ValueError,'conflicting duplicate'):
   core.apply(self.result(),self.f.logs,self.f.mapping,self.samples,self.f.registry,self.f.identity)
 def test_whole_row_conflict_inside_canonical_group_stays_hard(self):
  extra=copy.deepcopy(self.samples[0]);extra['players'][0]['placement'][0]=1.
  with self.assertRaisesRegex(ValueError,'conflicting duplicate'):self.apply(self.samples+[extra])
 def test_all_envelopes_checked_before_selection_including_excluded_overlap(self):
  bad=[s for s in self.samples if s['native_group_provenance']['name']=='vanilla_plus_overlap'][0]
  mutations=[lambda s:s.pop('native_group_provenance'),
    lambda s:s['hashes'].__setitem__('GameMP.dll','0'*64),
    lambda s:s['process_identity'].__setitem__(1,999),
    lambda s:s['observer_epoch']['log_offsets'].__setitem__('botA',999),
    lambda s:s['players'][0].__setitem__('world_pointer',123456),
    lambda s:s['native_group_provenance'].__setitem__('contract_sha256','0'*64),
    lambda s:s['native_group_provenance'].__setitem__('name','botA_actual')]
  original=copy.deepcopy(bad)
  for mutate in mutations:
   bad.clear();bad.update(copy.deepcopy(original));mutate(bad)
   with self.subTest(mutate=mutate),patch.object(core,'apply',side_effect=AssertionError('must validate all before core')):
    with self.assertRaises(ValueError):self.apply()
  bad.clear();bad.update(original)
 def test_missing_any_expected_group_fails(self):
  for missing in self.contract['groups']:
   with self.subTest(missing=missing),self.assertRaises(ValueError):
    self.apply([s for s in self.samples if s['native_group_provenance']['name']!=missing])
 def test_excluded_overlap_invalid_observed_clocks_are_not_hidden(self):
  for field in ('game_tick','spawned_tick'):
   samples=copy.deepcopy(self.samples)
   excluded=next(s for s in samples if s['native_group_provenance']['name']=='vanilla_plus_overlap')
   if field=='game_tick':excluded[field]=float('nan')
   else:excluded['players'][0][field]=float('nan')
   with self.subTest(field=field),patch.object(core,'apply',side_effect=AssertionError('all raw clocks first')):
    with self.assertRaises(ValueError):self.apply(samples)
 def test_false_group_slots_order_duplicate_or_missing_player_fails(self):
  for mutation in ('duplicate','missing','wrong_order','wrong_provenance_slots','wrong_present'):
   samples=copy.deepcopy(self.samples);s=samples[0]
   if mutation=='duplicate':s['players'][1]=copy.deepcopy(s['players'][0])
   if mutation=='missing':s['players'].pop()
   if mutation=='wrong_order':s['players'].reverse()
   if mutation=='wrong_provenance_slots':s['native_group_provenance']['read_slots']=[0,1,2,8]
   if mutation=='wrong_present':s['players'][0]['present']=False
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):self.apply(samples)
 def test_no_crossgroup_favorable_fire_or_pickup_fallback(self):
  for s in self.samples:
   if s['native_group_provenance']['name']=='botA_actual':
    for p in s['players']:p['weapons'].update(owned=259,fire_requested=0);p['last_buttons']=0
  out=self.apply()
  for i in range(4):
   p=out['slots'][f'botA:{i}']['native_fire_v2']
   self.assertEqual(p['native_fire_with_same_life_source_growth'],0)
   self.assertEqual(p['actual_useful_inventory_gains'],0)
   self.assertIn(f'botA:{i}:native_bound_fire_actions',out['missing_activity'])
   self.assertIn(f'botA:{i}:native_bound_useful_pickup_gains',out['missing_activity'])
 def test_unchanged_source_epoch_and_life_rules_still_fail_evidence(self):
  for s in self.samples:
   if s['native_group_provenance']['name']=='botA_actual':
    for p in s['players']:p['spawned_tick']=1.9999999
  self.f.logs['botA']=self.f.logs['botA'].replace('native_time=2.000000','native_time=1.000000')
  out=self.apply()
  self.assertTrue(all(out['slots'][f'botA:{i}']['native_fire_v2']['native_fire_with_same_life_source_growth']==0 for i in range(4)))
 def test_registry_contract_cannot_be_reassigned_after_sampling(self):
  self.f.registry['native_group_contract']['fixed_sources']['botA']='vanilla_plus_overlap'
  with self.assertRaises(ValueError):self.apply()
 def test_binding_does_not_mutate_original_sample(self):
  raw=copy.deepcopy(self.samples[0]);raw.pop('observer_epoch');raw.pop('native_group_provenance')
  before=copy.deepcopy(raw);groups.bind_sample(raw,'botA_actual',self.contract);self.assertEqual(raw,before)

if __name__=='__main__':unittest.main()
