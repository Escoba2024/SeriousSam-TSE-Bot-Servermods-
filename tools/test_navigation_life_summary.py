"""Conservative denominators from ordered native observations, no game or /proc."""
import copy
import unittest
try:
 import navigation_life_summary as subject
except ImportError:
 subject=None

EXPECTED={0:dict(entity_id=9,entity_pointer=100,world_pointer=200)}


def sample(t,spawn=1,health=100,owned=3,serial=1,**changes):
 row=dict(slot=0,present=True,render_type=3,health=health,spawned_tick=spawn,
          weapons=dict(owned=owned),**EXPECTED[0]);row.update(changes)
 return dict(game_tick=t,memory_observation=dict(read_serial=serial),players=[row])


class LifeSummary(unittest.TestCase):
 def run_summary(self,*rows):
  self.assertIsNotNone(subject,'native life summary missing')
  return subject.summarize(list(rows),EXPECTED)
 def test_owned_at_left_boundary_is_possession_not_acquisition(self):
  r=self.run_summary(sample(2,owned=11),sample(4,health=-1,owned=11,serial=2))['lives'][0]
  self.assertTrue(r['left_censored']);self.assertEqual(r['useful_gain_events'],0)
  self.assertEqual(r['first_useful_observed_tick'],2)
 def test_only_strictly_later_same_life_gain_counts(self):
  r=self.run_summary(sample(1),sample(1,owned=11,serial=2),sample(2,owned=259,serial=3))['lives'][0]
  self.assertEqual(r['useful_gain_events'],1)
 def test_respawn_never_becomes_ownership_gain(self):
  r=self.run_summary(sample(1),sample(4,spawn=4,owned=11,serial=2))
  self.assertEqual(r['observed_lives'],2)
  self.assertEqual(sum(x['useful_gain_events']for x in r['lives']),0)
  self.assertEqual(r['lives'][0]['ending'],'next_spawn_observed')
 def test_first_dead_tick_does_not_slide_through_corpse_samples(self):
  r=self.run_summary(sample(1),sample(3,serial=2),sample(4,health=-1,serial=3),sample(8,health=-1,serial=4))['lives'][0]
  self.assertEqual(r['last_alive_observed_tick'],3);self.assertEqual(r['first_dead_observed_tick'],4)
  self.assertEqual(r['observed_alive_span_seconds'],2)
 def test_right_censored_and_corpse_only_denominators_survive(self):
  r=self.run_summary(sample(2,health=-1),sample(4,spawn=4,serial=2))
  self.assertEqual(r['corpse_only_lives'],1);self.assertEqual(r['right_censored_lives'],1)
  self.assertFalse(r['qualified'])
 def test_wrong_native_entity_is_rejected(self):
  with self.assertRaises(ValueError):self.run_summary(sample(1,entity_id=99))
 def test_observation_gap_is_reported_not_interpolated(self):
  r=self.run_summary(sample(1),sample(20,serial=2))['lives'][0]
  self.assertEqual(r['max_observation_gap_seconds'],19)
  self.assertFalse(r['continuous_observation_proven'])
 def test_nonfinite_clock_is_rejected(self):
  with self.assertRaises(ValueError):self.run_summary(sample(float('nan')))
 def test_input_is_unchanged(self):
  x=sample(1);before=copy.deepcopy(x);self.run_summary(x);self.assertEqual(x,before)

 def test_alive_after_observed_death_is_flagged_without_extending_life_or_pickup(self):
  r=self.run_summary(sample(1),sample(2,health=-1,serial=2),sample(3,owned=11,serial=3))['lives'][0]
  self.assertEqual(r['alive_after_dead_samples'],1)
  self.assertEqual(r['last_alive_observed_tick'],1)
  self.assertIsNone(r['first_useful_observed_tick'])
  self.assertEqual(r['useful_gain_events'],0)

class ValidatedLifeSummary(unittest.TestCase):
 def setUp(self):
  import test_a4_ordered_memory_v3 as fixture
  self.f=fixture.OrderedObservationTests();self.f.setUp()
 def analyze(self):
  self.assertTrue(hasattr(subject,'validated_summary'),'strict V3 adapter missing')
  return subject.validated_summary(self.f.samples,self.f.registry,self.f.f.f.mapping,
    self.f.f.f.identity,self.f.contract,self.f.journal.records)
 def test_fixed_sources_keep_eight_bots_and_exclude_overlap(self):
  r=self.analyze();self.assertEqual(r['expected_slots'],8)
  self.assertEqual(r['observed_lives'],8);self.assertEqual(r['unobserved_slots'],[])
 def test_corrupt_excluded_overlap_cannot_disappear(self):
  overlap=next(x for x in self.f.samples if x['native_group_provenance']['name']=='vanilla_plus_overlap')
  overlap['players'][0]['world_pointer']+=4
  with self.assertRaises(ValueError):self.analyze()
 def test_missing_attempt_cannot_become_a_clean_summary(self):
  self.f.journal.records.pop()
  with self.assertRaises(ValueError):self.analyze()

 def test_valid_paused_smoke_is_validated_but_not_gameplay_evidence(self):
  self.f.samples[0]['memory_observation']['phase']='paused_smoke'
  self.f.journal.records[0]['phase']='paused_smoke'
  self.assertEqual(self.analyze()['observed_lives'],8)
 def test_corrupt_paused_smoke_is_still_rejected(self):
  self.f.samples[0]['memory_observation']['phase']='paused_smoke'
  self.f.journal.records[0]['phase']='paused_smoke'
  self.f.samples[0]['players'][0]['world_pointer']+=4
  with self.assertRaises(ValueError):self.analyze()

 def test_boolean_nested_smoke_identity_is_not_an_integer_alias(self):
  self.f.samples[0]['memory_observation']['phase']='paused_smoke'
  self.f.journal.records[0]['phase']='paused_smoke'
  self.f.samples[0]['memory_observation']['id']['read_serial']=True
  with self.assertRaises(ValueError):self.analyze()
 def test_boolean_smoke_epoch_is_not_zero_phase(self):
  self.f.samples[0]['memory_observation']['phase']='paused_smoke'
  self.f.journal.records[0]['phase']='paused_smoke'
  self.f.samples[0]['memory_observation']['id']['observer_epoch']['phase']=False
  with self.assertRaises(ValueError):self.analyze()

class ArchiveEnvelope(unittest.TestCase):
 def setUp(self):
  import test_a4_ordered_memory_v3 as fixture
  f=fixture.OrderedObservationTests();f.setUp();self.raw=f.samples[0]
 def unpack(self,row):
  self.assertTrue(hasattr(subject,'unpack_rows'),'archived snapshot envelope missing')
  return subject.unpack_rows([row])
 def test_elapsed_wrapper_preserves_native_clock(self):
  r=self.unpack(dict(elapsed=1234,group=self.raw['native_group_provenance']['name'],snapshot=self.raw))
  self.assertEqual(r,[self.raw]);self.assertNotEqual(r[0]['game_tick'],1234)
 def test_wrong_outer_group_cannot_alias_correct_inner_group(self):
  with self.assertRaises(ValueError):self.unpack(dict(elapsed=1,group='vanilla_plus_overlap',snapshot=self.raw))
 def test_wrong_outer_phase_is_rejected(self):
  with self.assertRaises(ValueError):self.unpack(dict(phase='paused_smoke',group=self.raw['native_group_provenance']['name'],snapshot=self.raw))

if __name__=='__main__':unittest.main()
