"""Pure private-eight-slot policy tests; never reads /proc or a display."""
import copy
import struct
import unittest


def fixture():
 import ownns_latejoin_preflight as p
 raw=bytearray(156)
 for fmt,offset,value in [('<i',0x1c,2),('<i',0x54,1),('<i',0x88,3)]:struct.pack_into(fmt,raw,offset,value)
 roles=('server','botA','botB')
 binding={r:dict(identity=[100+i,200+i],unit='own-'+r+'.service',namespace=900,ports=[[27850,40],[27851,41]]if r=='server'else[[30000+i,41+i]])for i,r in enumerate(roles)}
 frames=[{r:dict(game_tick=10.+n,session156_hex=raw.hex(),players=[dict(slot=s,entity_pointer=0x20000+s,placement=[s+n,0,0,0,0,0],health=100,spawned_tick=1.)for s in range(8)])for r in roles}for n in range(2)]
 for n,frame in enumerate(frames):
  for role,sample in frame.items():
   sample.update(process_identity_before=binding[role]['identity'],process_identity_after=binding[role]['identity'],hashes={'Engine.dll':p.ORIGINALS['Engine.dll'],'EntitiesMP.dll':p.ORIGINALS['EntitiesMP.dll'],'GameMP.dll':p.ORIGINALS['GameMP.dll']if role=='server'else '6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a'},read_interval=[1.+n*.4,1.1+n*.4],slot_binding_before=[[x['slot'],x['entity_pointer']]for x in sample['players']],slot_binding_after=[[x['slot'],x['entity_pointer']]for x in sample['players']])
 return dict(protocol=p.PROTOCOL,window=[1.,2.],deadline=3.,binding_before=binding,binding_after=copy.deepcopy(binding),host_namespace=901,
  query=dict(gamename='serioussamse',gamever='1.07',hostport='27850',numplayers='8',maxplayers='9',dedicatedserver='yes',activemod='',difficulty='Hard',mapname='Yodeller',**{'player_'+str(i):'own-'+str(i)for i in range(8)}),
  map_name='Yodeller',mapping={'botA':[0,1,2,3],'botB':[4,5,6,7]},frames=frames,pauses={r:0 for r in roles},
  original_hashes=dict(p.ORIGINALS),vanilla_quiescent=True,lock_held=True,
  resources=dict(cpu_busy_percent=40.,mem_available_bytes=2*1024**3,disk_free_bytes=9*1024**3))


class PrivateEightPreflight(unittest.TestCase):
 def check(self,value):
  import ownns_latejoin_preflight as p
  return p.validate_prestart(value,expected_names={'own-'+str(i)for i in range(8)},now=2.1)
 def test_missing_checker_is_an_explicit_red(self):
  import importlib.util
  self.assertIsNotNone(importlib.util.find_spec('ownns_latejoin_preflight'),'private checker has not been implemented')
 def test_valid_private_protocol_is_not_external_canstart_or_qualification(self):
  report=self.check(fixture())
  self.assertEqual(report['status'],'PRIVATE_EIGHT_READY_AT_CHECK_TIME')
  self.assertNotIn('canStart',report)
  for key in ('qualified','functional_pass','a4_accepted'):self.assertIs(report[key],False)
 def test_wrong_query_or_extra_name_fails(self):
  for field,value in [('numplayers','9'),('mapname','Red Station'),('gamever','1.10'),('difficulty','Serious'),('hostport','25650'),('activemod','mod')]:
   e=fixture();e['query'][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(e)
  e=fixture();e['query']['player_8']='extra'
  with self.assertRaises(ValueError):self.check(e)
 def test_eight_query_rows_do_not_prove_correct_native_slots(self):
  for role in ('server','botA','botB'):
   e=fixture();e['frames'][1][role]['players'][-1]['slot']=8
   with self.subTest(role=role),self.assertRaises(ValueError):self.check(e)
 def test_local_slot_mapping_cannot_be_inferred_from_query(self):
  e=fixture();e['mapping']['botB']=[5,6,7,8]
  with self.assertRaises(ValueError):self.check(e)
 def test_pid_port_inode_namespace_or_unit_rebaseline_fails(self):
  for field in ('identity','ports','namespace','unit'):
   e=fixture();e['binding_after']['botA'][field]=[999,1]if field=='identity'else [[31111,999]]if field=='ports'else 999 if field=='namespace'else'new.service'
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(e)
 def test_host_namespace_or_duplicate_role_pid_fails(self):
  e=fixture();e['host_namespace']=900
  with self.assertRaises(ValueError):self.check(e)
  e=fixture();e['binding_before']['botB']['identity']=e['binding_before']['botA']['identity'];e['binding_after']=copy.deepcopy(e['binding_before'])
  with self.assertRaises(ValueError):self.check(e)
 def test_paused_frozen_or_wrong_native_rules_fail(self):
  for field in ('pause','tick','session','nan'):
   e=fixture()
   if field=='pause':e['pauses']['server']=1
   elif field=='tick':e['frames'][1]['botA']['game_tick']=10.
   elif field=='nan':e['frames'][1]['server']['game_tick']=float('nan')
   else:e['frames'][1]['server']['session156_hex']='00'*156
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(e)
 def test_lock_original_or_quiescence_failure_stays_failure(self):
  for field in ('lock_held','vanilla_quiescent','original_hashes'):
   e=fixture();e[field]=False if field!='original_hashes'else{}
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(e)
 def test_resource_limits_require_measured_cpu_delta(self):
  for field,value in [('cpu_busy_percent',75.01),('cpu_busy_percent',None),('mem_available_bytes',1610612735),('disk_free_bytes',8589934591)]:
   e=fixture();e['resources'][field]=value
   with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.check(e)
 def test_wrong_or_reversed_observation_window_fails(self):
  for window in ([2.,1.],[1.,float('nan')]):
   e=fixture();e['window']=window
   with self.assertRaises(ValueError):self.check(e)
 def test_no_claim_of_atomic_entity_or_life_snapshot(self):
  e=fixture();e['frames'][1]['server']['players'][0].update(health=0,spawned_tick=11.,entity_pointer=99999)
  e['frames'][1]['server']['slot_binding_before'][0][1]=99999;e['frames'][1]['server']['slot_binding_after'][0][1]=99999
  result=self.check(e)
  self.assertIs(result['atomic_snapshot_proven'],False)
 def test_stale_ready_check_cannot_be_replayed(self):
  e=fixture();e['window']=[0.,.5];e['deadline']=1.5
  with self.assertRaises(ValueError):self.check(e)
 def test_actual_now_is_required_not_a_caller_fresh_boolean(self):
  import inspect,ownns_latejoin_preflight as p
  self.assertIn('now',inspect.signature(p.validate_prestart).parameters)
 def test_matching_native_frames_from_wrong_pid_or_original_hash_fail(self):
  for field in ('process_identity_before','process_identity_after','hashes','slot_binding_after','read_interval'):
   e=fixture();s=e['frames'][0]['botA']
   if field.startswith('process_identity'):s[field]=[999,88]
   elif field=='hashes':s[field]['Engine.dll']='0'*64
   elif field=='slot_binding_after':s[field][0][1]+=4
   else:s[field]=[0.,.5]
   with self.subTest(field=field),self.assertRaises(ValueError):self.check(e)


if __name__=='__main__':unittest.main()
