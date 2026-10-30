"""Engine observations must remain separate from policy/input acknowledgements."""
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[1]

def snapshot(tick,player,entity,health,frags=0):
 return f'[BotSnapshot] tick={tick} player={player} entity={entity} pos=(0,0,0) yaw=0 health={health} buttons=0 \\frags_{player}\\{frags}\n'

class Evidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('m2_combat_evidence',HERE/'combat_evidence.py')
  cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
 def test_fire_inputs_alone_never_establish_shots_or_hits(self):
  d=self.m.analyze('[BotDriver] bot0 tick=20 pos=(0,0,0) fire=1 combat_fire_actions=90\n')
  self.assertEqual(d['emitted_fire_input_max'],90)
  self.assertEqual(d['sampled_colt_clip_decrease'],0)
  self.assertEqual(d['actors'],{})
  self.assertFalse(d['full_m2_acceptance'])
 def test_engine_health_death_respawn_and_frag_counters(self):
  text=snapshot(20,0,10,100)+snapshot(40,0,10,70)+snapshot(60,0,10,-20)+snapshot(80,0,11,100)
  text+=snapshot(20,1,12,100)+snapshot(60,1,12,100,1)
  d=self.m.analyze(text)
  self.assertEqual(d['actors']['0']['observed_health_loss'],120)
  self.assertEqual(d['actors']['0']['deaths'],1)
  self.assertEqual(d['actors']['0']['alive_after_death'],1)
  self.assertEqual(d['actors']['1']['frag_increments'],1)
 def test_living_replacement_does_not_inherit_health_or_frags(self):
  d=self.m.analyze(snapshot(20,0,10,100,1)+snapshot(40,0,11,40,5))
  self.assertEqual(d['actors']['0']['observed_health_loss'],0)
  self.assertEqual(d['actors']['0']['frag_increments'],0)
  self.assertEqual(d['actors']['0']['alive_after_death'],0)
 def test_colt_clip_decreases_and_other_weapons_do_not_relabel_ammo(self):
  def weapon(tick,w,ammo):
   return f'[BotWeapon] tick={tick} eye=(0,0,0) yaw=0 pitch=0 weapon={w} wanted={w} available=3 ammo={ammo} firing=0 rayDistance=10\n'
  text=weapon(20,2,6)+weapon(40,2,3)+weapon(60,2,6)+weapon(80,12,0)
  d=self.m.analyze(text)
  self.assertEqual(d['sampled_colt_clip_decrease'],3)
  self.assertEqual(d['observed_current_weapons'],[2,12])
 def test_tick_reset_does_not_manufacture_respawn_or_ammo_consumption(self):
  d=self.m.analyze(snapshot(60,0,10,-20)+snapshot(20,0,11,100))
  self.assertEqual(d['actors']['0']['alive_after_death'],0)
  self.assertGreater(d['nonmonotonic_samples'],0)
 def test_nonfinite_or_truncated_samples_cannot_prove_damage(self):
  d=self.m.analyze(snapshot(20,0,10,100)+snapshot(40,0,10,'nan')+snapshot(60,0,10,-20).rstrip('\n'))
  self.assertEqual(d['actors']['0']['deaths'],0)
  self.assertTrue(d['incomplete_final_line'])
 def test_native_reserve_decreases_and_empty_pool_are_observations_only(self):
  def ammo(tick,rockets,shells):
   return f'[BotAmmo] tick={tick} local=0 current=8 wanted=8 available=139 colt=6 bullets=0 shells={shells} rockets={rockets} grenades=4 napalm=5 cells=6 sniper=7 cannon=8\n'
  d=self.m.analyze(ammo(20,2,10)+ammo(40,1,9)+ammo(60,0,9))
  self.assertEqual(d['ammo_pools']['rockets']['sampled_decrease'],2)
  self.assertEqual(d['ammo_pools']['rockets']['zero_samples'],1)
  self.assertEqual(d['ammo_pools']['shells']['sampled_decrease'],1)
  self.assertEqual(set(d['ammo_pools']),{'colt','bullets','shells','rockets','grenades','napalm','cells','sniper','cannon'})
  self.assertFalse(d['full_m2_acceptance'])
 def test_native_ammo_tick_reset_does_not_manufacture_depletion(self):
  line='[BotAmmo] tick={tick} local=0 current=8 wanted=8 available=139 colt=6 bullets=0 shells=0 rockets={rockets} grenades=0 napalm=0 cells=0 sniper=0 cannon=0\n'
  d=self.m.analyze(line.format(tick=40,rockets=5)+line.format(tick=20,rockets=0))
  self.assertEqual(d['ammo_pools']['rockets']['sampled_decrease'],0)
 def test_projectile_sightings_are_deduplicated_per_entity_not_counted_as_shots(self):
  d=self.m.analyze('[BotProjectileWitness] tick=20 entity=570 type=0 launcher=1 speed=30.00\n[BotProjectileWitness] tick=40 entity=570 type=0 launcher=1 speed=0.00\n[BotProjectileWitness] tick=40 entity=572 type=0 launcher=1 speed=0.00\n')
  self.assertEqual(d['projectile_witnesses'],[{'type':0,'launcher':1,'distinct_entities':2,'sampled_sightings':3,'max_sampled_speed':30.0}])
  self.assertFalse(d['full_m2_acceptance'])
 def test_invalid_projectile_speed_is_rejected_without_aborting_evidence_scan(self):
  for speed in ('garbage','1.#QNAN','nan','-1'):
   d=self.m.analyze(f'[BotProjectileWitness] tick=20 entity=570 type=0 launcher=1 speed={speed}\n')
   self.assertEqual(d['invalid_samples'],1)
   self.assertEqual(d['projectile_witnesses'],[])

if __name__=='__main__':unittest.main()
