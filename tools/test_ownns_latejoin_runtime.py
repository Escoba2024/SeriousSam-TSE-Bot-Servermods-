"""Offline lifecycle/guard adapter tests; no subprocess, network or display."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch


class RuntimeAdapter(unittest.TestCase):
 def test_missing_adapter_is_red(self):self.assertIsNotNone(importlib.util.find_spec('ownns_latejoin_runtime'))
 def test_launcher_progresses_between_bounded_polls_and_retains_child(self):
  import ownns_latejoin_runtime as p
  child=Mock();child.communicate.side_effect=[subprocess.TimeoutExpired('own',.1),('ok','')];child.poll.return_value=0;child.returncode=0
  owners=[];progress=Mock();p.run_owned_launcher(['own'],1.,progress,owners,popen=Mock(return_value=child),monotonic=Mock(side_effect=[0.,.1,.2]))
  self.assertEqual(owners,[child]);self.assertGreaterEqual(progress.call_count,2);self.assertEqual(child.communicate.call_count,2)
  child.terminate.assert_not_called()
 def test_guard_failure_still_closes_only_owned_launcher_child(self):
  import ownns_latejoin_runtime as p
  child=Mock();child.poll.return_value=None;child.wait.return_value=-15
  with self.assertRaisesRegex(ValueError,'guard'):
   p.run_owned_launcher(['own'],1.,Mock(side_effect=ValueError('guard')),[],popen=Mock(return_value=child),monotonic=lambda:0.)
  child.terminate.assert_called_once();child.wait.assert_called_once_with(timeout=3);child.kill.assert_not_called()
 def test_launcher_timeout_never_claims_success_after_cleanup(self):
  import ownns_latejoin_runtime as p
  child=Mock();child.poll.return_value=None;child.wait.side_effect=[subprocess.TimeoutExpired('own',3),-9]
  with self.assertRaises(TimeoutError):p.run_owned_launcher(['own'],1.,Mock(),[],popen=Mock(return_value=child),monotonic=Mock(side_effect=[0.,2.]))
  child.terminate.assert_called_once();child.kill.assert_called_once()
 def test_sync_activity_cannot_relabel_a4_pickup_as_pass(self):
  import ownns_latejoin_runtime as p
  mapping=dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8])
  slots={r+':'+str(i):dict(memory_flag_observations=dict(native_fire_flag_observations_with_same_life_source_growth=2))for r in ('botA','botB')for i in range(4)}
  active=dict(slots=slots,server_reported_foreign_kills=[{'fixture':'own kill'}],missing_activity=['botA:0:native_bound_useful_pickup_gains'])
  samples=[]
  for n in (0,2):samples.append(dict(players=[dict(slot=i,present=True,entity_id=i+1,entity_pointer=100000+i,world_pointer=99999,spawned_tick=1.,health=100,placement=[float(n),0.,0.])for i in range(8)]))
  result=p.sync_activity(active,samples,mapping)
  self.assertFalse(result['a4_accepted']);self.assertFalse(result['functional_pass']);self.assertTrue(result['sync_activity_observed'])
  self.assertEqual(result['open_a4_diagnostics'],active['missing_activity'])
  slots['botB:3']['memory_flag_observations']['native_fire_flag_observations_with_same_life_source_growth']=False
  with self.assertRaises(ValueError):p.sync_activity(active,samples,mapping)
 def test_teleport_between_lives_cannot_prove_same_life_motion(self):
  import ownns_latejoin_runtime as p
  mapping=dict(botA=list(range(4)),botB=list(range(4,8)),vanilla=[8]);active=dict(slots={},server_reported_foreign_kills=[{}],missing_activity=[])
  for r in ('botA','botB'):
   for i in range(4):active['slots'][r+':'+str(i)]=dict(memory_flag_observations=dict(native_fire_flag_observations_with_same_life_source_growth=True))
  samples=[dict(players=[dict(slot=i,present=True,entity_id=i+1,entity_pointer=100000+i,world_pointer=99999,spawned_tick=float(n+1),health=100,placement=[float(n*10),0.,0.])for i in range(8)])for n in (0,1)]
  with self.assertRaises(ValueError):p.sync_activity(active,samples,mapping)
 def test_native_frame_binds_two_real_reads_to_exact_role_and_loaded_pins(self):
  import ownns_latejoin_runtime as p
  from test_ownns_latejoin_preflight import fixture
  e=fixture();B=Mock();B.identity.return_value=(100,200);B.same.return_value=True
  pins={n:dict(sha256=h)for n,h in e['frames'][0]['server']['hashes'].items()}
  probe=Mock();probe.read.return_value=e['frames'][0]['server']
  with tempfile.TemporaryDirectory()as directory:
   run=p.LatejoinRuntime(root=Path(directory),evidence=Path(directory),backend=B,records={'server':dict(identity=(100,200))},module_pins={'server':pins},unit=lambda r:'own.service',probe=probe,pauseprobe=Mock(),map_name='Yodeller',slot_mapping=Mock(),sample_host=Mock(),host_budget=Mock())
   frame=run.native_frame('server')
   self.assertEqual(frame['process_identity_before'],[100,200]);self.assertEqual(frame['hashes'],e['frames'][0]['server']['hashes'])
   self.assertEqual(B.verify_modules.call_count,2);self.assertEqual(probe.read.call_count,2)
   B.identity.side_effect=[(100,200),(999,200)]
   with self.assertRaises(ValueError):run.native_frame('server')
   self.assertEqual(len(list(Path(directory).glob('private-native-frame-*.json'))),2)
 def test_expired_original_prestart_blocks_actual_launcher_boundary(self):
  import ownns_latejoin_runtime as p
  from test_ownns_latejoin_preflight import fixture
  run=p.LatejoinRuntime.__new__(p.LatejoinRuntime);run.root=Path('/fixture');run.capture=Mock(stage='ADMITTING');run.capture.admission_remaining.return_value=5.
  run.original_prestart=dict(evidence=fixture(),names=['own-'+str(i)for i in range(8)]);run.original_launch_consumed=False;run.launch_helpers=[];run.progress=Mock()
  with patch.object(p.time,'monotonic',return_value=10.),patch.object(p,'run_owned_launcher')as launch:
   with self.assertRaises(ValueError):run.run_command(['/bin/bash','/fixture/launch-vanilla.sh'],20)
   launch.assert_not_called()
 def test_readiness20s_timeout_closes_reader_and_retains_failure_without_retry(self):
  import ownns_latejoin_runtime as p
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);evidence=root/'evidence';evidence.mkdir()
   run=p.LatejoinRuntime.__new__(p.LatejoinRuntime);run.root=root;run.evidence=evidence
   run.capture=None;run.records={r:dict(identity=(100+i,200+i))for i,r in enumerate(('server','botA','botB'))}
   run.unit=lambda r:'own-'+r;run.progress=Mock();run.B=Mock();run.map_name='Yodeller'
   from test_ownns_latejoin_preflight import fixture
   run.B.query.return_value=fixture()['query']
   for role in run.records:
    path=root/role;path.mkdir();(path/('Dedicated_BotTest.log'if role=='server'else'SeriousSam.log')).write_text('')
   reader=Mock();factory=Mock();factory.return_value.__enter__=Mock(return_value=reader);factory.return_value.__exit__=Mock(return_value=False)
   with patch.object(p,'observe_three_roles',return_value={}),patch.object(p.time,'monotonic',side_effect=[0.,21.,22.]):
    with self.assertRaisesRegex(ValueError,'readiness20s deadline'):
     run.prejoin_readiness(factory,ValueError,Mock(),dict(botA=list(range(4)),botB=list(range(4,8))))
   factory.assert_called_once();factory.return_value.__exit__.assert_called_once();reader.sample.assert_not_called()
   receipt=json.loads((evidence/'private-prejoin-readiness.json').read_text())
   self.assertEqual(receipt['status'],'FAIL');self.assertEqual(receipt['deadline_monotonic'],20.)
   for name in ('prejoin-inventory.jsonl','prejoin-read-attempts.jsonl'):
    self.assertEqual((evidence/name).stat().st_mode&0o777,0o600)
   self.assertIsNone(run.capture);self.assertFalse(receipt['qualified'])


if __name__=='__main__':unittest.main()
