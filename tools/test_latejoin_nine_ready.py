"""Bounded startup observations and private raw receipts; no native IO."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

import ownns_latejoin_runtime as runtime
from owned_latejoin_capture import exclusive_json
from test_ownns_latejoin_preflight import fixture


class Clock:
 def __init__(self):self.now=1.
 def __call__(self):return self.now
 def sleep(self,seconds):self.now+=seconds


def scenario(directory,counts=(8,9,9),ticks=None):
 e=fixture();binding=copy.deepcopy(e['binding_before'])
 binding['vanilla']=dict(identity=[103,203],unit='own-vanilla.service',namespace=900,ports=[[31003,9003]])
 run=runtime.LatejoinRuntime.__new__(runtime.LatejoinRuntime);run.root=Path(directory);run.evidence=Path(directory)
 run.records={r:dict(identity=tuple(row['identity']))for r,row in binding.items()};run.unit=lambda r:binding[r]['unit']
 run.original_prestart=dict(evidence=e);run.frame_serial=0;run.progress=Mock();run.B=Mock();run.map_name='Yodeller'
 run.capture=Mock(stage='ADMITTING',before=copy.deepcopy(e['binding_before']));clock=Clock()
 def remaining():
  runtime.require(clock.now<30,'Original admission exceeded30s budget');return 30-clock.now
 run.capture.admission_remaining.side_effect=remaining
 run.original_launch_consumed=True;run.launch_helpers=[];run.pauseprobe=Mock();run.pauseprobe.read_pause.return_value=dict(actual_pause=0)
 run.B.query.return_value=copy.deepcopy(e['query']);run.B.query.return_value.update(numplayers='9',player_8='own-original')
 frames=[]
 for n,count in enumerate(counts):
  frame={}
  for role in binding:
   sample=copy.deepcopy(e['frames'][0]['server'if role=='vanilla'else role]);sample['game_tick']=23.+n*.2 if ticks is None else ticks[n]
   if role=='vanilla':sample['process_identity_before']=sample['process_identity_after']=binding[role]['identity']
   for s in range(8,9 if role!='vanilla'else count):sample['players'].append(dict(slot=s,entity_pointer=0x20000+s,health=100,spawned_tick=1.))
   pairs=[[p['slot'],p['entity_pointer']]for p in sample['players']];sample.update(slot_binding_before=copy.deepcopy(pairs),slot_binding_after=copy.deepcopy(pairs))
   frame[role]=sample
  frames.append(frame)
 reads=[]
 def native(role):
  n=len(reads)//4;sample=copy.deepcopy(frames[min(n,len(frames)-1)][role]);clock.now+=.01
  sample['read_interval']=[clock.now-.009,clock.now];reads.append(role);run.frame_serial+=1
  exclusive_json(run.evidence/f'private-native-frame-{run.frame_serial}-{role}.json',dict(native_first=sample,status='MODEL_READ'))
  return sample
 run.native_frame=native
 return run,clock,binding,frames,reads


class NineSlotStartup(unittest.TestCase):
 def collect(self,run,clock,binding):
  self.assertTrue(hasattr(run,'admission_frames'),'bounded complete-nine readiness is missing')
  registry={r:dict(identity=list(rec['identity']),unit=run.unit(r))for r,rec in run.records.items()};history=[]
  with patch.object(runtime.time,'monotonic',clock),patch.object(runtime.time,'sleep',clock.sleep),patch.object(runtime,'observe_roles',return_value=binding):
   result=run.admission_frames(registry,binding,1.,history)
  return result,history
 def test_original_eight_then_nine_requires_second_complete_progressing_nine(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,_,reads=scenario(d);pair,history=self.collect(run,clock,binding)
   self.assertEqual(len(reads),12);self.assertEqual(len(history),3)
   self.assertEqual([len(f['vanilla']['players'])for f in pair],[9,9]);self.assertGreater(pair[1]['vanilla']['game_tick'],pair[0]['vanilla']['game_tick'])
   self.assertEqual(len(list(Path(d).glob('private-native-frame-*.json'))),12)
   self.assertFalse(history[0]['complete_nine']);self.assertTrue(history[-1]['complete_nine'])
 def test_permanently_eight_expires_original_absolute30s_without_launch_retry(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,_,reads=scenario(d,(8,));clock.now=29.8
   with self.assertRaisesRegex(ValueError,'30s'):self.collect(run,clock,binding)
   self.assertEqual(reads,['server','botA','botB','vanilla']);self.assertTrue(run.original_launch_consumed);self.assertEqual(run.launch_helpers,[])
 def test_two_complete_but_frozen_native_ticks_are_not_progress(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,_,reads=scenario(d,(9,),ticks=(23.,));clock.now=29.4
   with self.assertRaisesRegex(ValueError,'30s'):self.collect(run,clock,binding)
   self.assertGreater(len(reads),4)
 def test_existing_slots_identity_modules_and_rules_fail_immediately(self):
  for change in ('old_pointer','pid','hash','session','server_missing8','original_missing7','extra_slot'):
   with self.subTest(change=change),tempfile.TemporaryDirectory()as d:
    run,clock,binding,frames,reads=scenario(d);frame=frames[0];s=frame['server']
    if change=='old_pointer':
     s['players'][0]['entity_pointer']+=4;s['slot_binding_before'][0][1]+=4;s['slot_binding_after'][0][1]+=4
    elif change=='pid':s['process_identity_after']=[999,1]
    elif change=='hash':s['hashes']['Engine.dll']='0'*64
    elif change=='session':s['session156_hex']='00'*156
    else:
     s=frame['vanilla']if change!='server_missing8'else s
     if change in('original_missing7','server_missing8'):
      slot=7 if change=='original_missing7'else 8;s['players']=[r for r in s['players']if r['slot']!=slot]
     else:s['players'].append(dict(slot=9,entity_pointer=0x30009))
     pairs=[[r['slot'],r['entity_pointer']]for r in s['players']];s['slot_binding_before']=copy.deepcopy(pairs);s['slot_binding_after']=copy.deepcopy(pairs)
    with self.assertRaises(ValueError):self.collect(run,clock,binding)
    self.assertLessEqual(len(reads),4)
 def test_original_slot8_loss_pointer_change_or_time_reversal_is_not_notready(self):
  for change in ('loss','pointer','clock'):
   with self.subTest(change=change),tempfile.TemporaryDirectory()as d:
    run,clock,binding,frames,reads=scenario(d,(9,9))
    s=frames[1]['vanilla']
    if change=='loss':
     s['players'].pop();s['slot_binding_before'].pop();s['slot_binding_after'].pop()
    elif change=='pointer':
     s['players'][-1]['entity_pointer']+=4;s['slot_binding_before'][-1][1]+=4;s['slot_binding_after'][-1][1]+=4
    else:s['game_tick']=22.
    with self.assertRaises(ValueError):self.collect(run,clock,binding)
    self.assertEqual(len(reads),8)
 def test_old_endpoint_binding_cannot_rebaseline_while_waiting(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,_,reads=scenario(d);run.capture.before['botA']['ports']=[[39999,9999]]
   with self.assertRaises(ValueError):self.collect(run,clock,binding)
   self.assertEqual(reads,[])
 def test_original8_appearing_between_two_raw_reads_is_not_a_complete_frame(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,frames,reads=scenario(d)
   frames[0]['vanilla']['slot_binding_after'].append([8,0x20008])
   pair,history=self.collect(run,clock,binding)
   self.assertEqual(len(reads),12);self.assertFalse(history[0]['complete_nine']);self.assertEqual(len(pair),2)
 def test_old_entity_changing_between_raw_reads_is_always_failure(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,frames,reads=scenario(d)
   frames[0]['vanilla']['slot_binding_after'][0][1]+=4
   with self.assertRaisesRegex(ValueError,'slot/entity'):self.collect(run,clock,binding)
   self.assertEqual(len(reads),4)
 def test_endpoint_change_during_pending_round_stops_before_more_reads(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,frames,reads=scenario(d);changed=copy.deepcopy(binding);changed['vanilla']['ports']=[[39998,9999]]
   registry={r:dict(identity=list(rec['identity']),unit=run.unit(r))for r,rec in run.records.items()}
   with patch.object(runtime.time,'monotonic',clock),patch.object(runtime.time,'sleep',clock.sleep),patch.object(runtime,'observe_roles',side_effect=[binding,changed]):
    with self.assertRaisesRegex(ValueError,'endpoint'):run.admission_frames(registry,binding,1.,[])
   self.assertEqual(len(reads),4)
 def test_query_or_injected_launch_is_never_used_to_fill_missing_native_slot(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,_,reads=scenario(d,(8,));clock.now=29.8;run.run_command=Mock()
   with self.assertRaises(ValueError):self.collect(run,clock,binding)
   run.B.query.assert_not_called();run.run_command.assert_not_called()


class AdmissionRawReceipts(unittest.TestCase):
 def test_late_frame_failure_retains_successful_local_and_inventory_reads0600(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,frames,_=scenario(d,(9,9));pair=copy.deepcopy(frames)
   for n,frame in enumerate(pair):
    for s in frame.values():s['read_interval']=[1.+n*.2,1.1+n*.2]
   run.frames=Mock(return_value=pair);run.admission_frames=Mock(return_value=pair)
   local=dict(process_identity=binding['vanilla']['identity'],locals=[dict(local=0,global_slot=8,source_pointer=0x50000)],native_abi_qualified=False)
   class Reader:
    def __init__(self,pid,start,root,expected):self.identity=[pid,start]
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def sample(self,slots):return dict(process_identity=self.identity,hashes={k:runtime.ORIGINALS[k]for k in('Engine.dll','EntitiesMP.dll','GameMP.dll')},players=[dict(slot=8,present=True,entity_pointer=0x20008,entity_id=6008)])
   def validate(*args):raise ValueError('late exact frame failure')
   with patch.object(runtime,'observe_roles',return_value=binding),patch.object(runtime.local_source,'sample',return_value=local),patch.object(runtime,'validate_frames',side_effect=validate),patch.object(runtime.time,'monotonic',return_value=2.):
    with self.assertRaisesRegex(ValueError,'late exact frame failure'):run.admission(['own-'+str(i)for i in range(8)],Reader)
   expected=['private-original-local-source-sample.json','private-original-slot8-server-inventory.json','private-original-slot8-vanilla-inventory.json','private-original-slot8-failure.json']
   for name in expected:
    p=Path(d)/name;self.assertTrue(p.exists(),name);self.assertEqual(p.stat().st_mode&0o777,0o600)
   receipt=json.loads((Path(d)/expected[-1]).read_text());self.assertEqual(receipt['local_source'],local)
   self.assertEqual(set(receipt['partial_inventory']),{'server','vanilla'});self.assertEqual(receipt['status'],'FAIL');self.assertFalse(receipt['qualified'])
 def test_startup_failure_also_has_exclusive_failure_receipt_without_inventory(self):
  with tempfile.TemporaryDirectory()as d:
   run,clock,binding,_,_=scenario(d);reader=Mock();run.admission_frames=Mock(side_effect=ValueError('native slot failure'))
   with patch.object(runtime,'observe_roles',return_value=binding),patch.object(runtime.time,'monotonic',clock):
    with self.assertRaisesRegex(ValueError,'native slot failure'):run.admission([],reader)
   reader.assert_not_called();p=Path(d)/'private-original-slot8-failure.json';receipt=json.loads(p.read_text())
   self.assertEqual(receipt['partial_inventory'],{});self.assertIsNone(receipt['local_source']);self.assertEqual(p.stat().st_mode&0o777,0o600)


if __name__=='__main__':unittest.main()
