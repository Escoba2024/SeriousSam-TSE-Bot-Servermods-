"""Pure20s prejoin readiness evidence, using unchanged V3 source/life decoder."""
import copy
import io
import unittest

import ownns_latejoin_runtime as runtime
import a4_ordered_memory_v3 as v3
import test_audit_a4_native_fire_observer_v2 as legacy
from test_ownns_latejoin_preflight import fixture


def evidence():
 old=legacy.NativeFireReviewTests();old.setUp();identity=[100,200]
 groups=dict(botA_actual=list(range(4)),botB_actual=list(range(4,8)))
 contract=dict(schema='OWNNS_PREJOIN8_ORDERED_V1',server_identity=identity,groups=groups,entities=[])
 samples=[];journal=v3.AttemptJournal(io.StringIO());serial=0
 for n,(_,sample)in enumerate(old.snapshots):
  for group,slots in groups.items():
   rows=[]
   for slot in slots:
    row=copy.deepcopy(sample['players'][0]);row.update(slot=slot,entity_id=7+slot,entity_pointer=65536+slot*256,placement=[n*2.,0.,0.]);rows.append(row)
   serial+=1;start=serial*.01;end=start+.001;journal.begin(serial,group,start,'gameplay');journal.end(serial,end,True)
   samples.append(dict(game_tick=sample['game_tick'],players=rows,process_identity=identity,hashes={k:runtime.ORIGINALS[k]for k in ('Engine.dll','EntitiesMP.dll','GameMP.dll')},consistency='two_equal_reads_not_atomic',all_selected_present=True,prejoin_observation=dict(group=group,read_serial=serial,monotonic_start=start,monotonic_end=end)))
 for sample in samples[:2]:contract['entities'].extend({k:row[k]for k in ('slot','entity_id','entity_pointer','world_pointer')}for row in sample['players'])
 q=fixture()['query'];q.update({'frags_'+str(i):'0'for i in range(8)});last=copy.deepcopy(q);last['frags_0']='1'
 return dict(logs={'botA':old.text,'botB':''},mapping=dict(botA=list(range(4)),botB=list(range(4,8))),samples=samples,queries=[q,last],contract=contract,attempts=journal.records,server_log='',active_evidence=lambda *args:dict(server_reported_foreign_kills=[]))


class PrejoinReadiness(unittest.TestCase):
 def test_missing_readiness_contract_is_red(self):self.assertTrue(hasattr(runtime,'readiness_evidence'))
 def test_only_one_own_fire_witness_and_positive_frag_suffice_not_all_eight(self):
  result=runtime.readiness_evidence(**evidence())
  self.assertTrue(result['ready']);self.assertEqual(result['moved_slots'],list(range(8)))
  self.assertEqual(result['firing_slots'],[0]);self.assertFalse(result['a4_accepted'])
 def test_native_motion_from_all_eight_and_actual_fire_are_both_required(self):
  for change in ('motion','fire','counter','frag'):
   e=evidence()
   if change=='motion':
    for sample in e['samples']:
     for row in sample['players']:
      if row['slot']==7:row['placement']=[0.,0.,0.]
   elif change=='fire':
    for sample in e['samples']:
     for row in sample['players']:row['last_buttons']=0
   elif change=='counter':e['logs']['botA']=e['logs']['botA'].replace('shots=2','shots=0')
   else:e['queries'][-1]['frags_0']='0'
   with self.subTest(change=change):self.assertFalse(runtime.readiness_evidence(**e)['ready'])
 def test_real_serverkill_is_an_alternative_to_positive_own_frag(self):
  e=evidence();e['queries'][-1]['frags_0']='0';e['server_log']='own current-window event';e['active_evidence']=lambda *args:dict(server_reported_foreign_kills=[{'private':'own'}])
  self.assertTrue(runtime.readiness_evidence(**e)['ready'])
 def test_wrong_pid_module_entity_or_omitted_successful_attempt_fails(self):
  for change in ('pid','hash','entity','omitted','time'):
   e=evidence();s=e['samples'][2]
   if change=='pid':s['process_identity']=[999,200]
   elif change=='hash':s['hashes']['Engine.dll']='0'*64
   elif change=='entity':s['players'][0]['entity_pointer']+=4
   elif change=='omitted':e['samples'].pop(2)
   else:s['prejoin_observation']['monotonic_end']=0.
   with self.subTest(change=change),self.assertRaises(ValueError):runtime.readiness_evidence(**e)


if __name__=='__main__':unittest.main()
