import sys,unittest,tempfile,json
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).parent/'operations'))
import fleet_supervisor as supervisor
import fleet_health as health
import private_candidate_profile as candidate

class Contract:
 roles=candidate.role_contract({f'gamer-{i:03}':f'name{i}' for i in range(8)})
 role_names=tuple(r.name for r in roles)
 expected_names=tuple(r.nickname for r in roles if r.nickname)
 candidate_sha256=candidate.CANDIDATE
 def role(self,name):return next(r for r in self.roles if r.name==name)
 def source(self,role):return candidate.PrivateProfile.source(self,role)
 def is_bot(self,name):return self.role(name).kind=='bot'
 def local_players(self,name):return self.role(name).local_players
 def recovery_action(self,role,names,seconds):return candidate.PrivateProfile.recovery_action(self,role,names,seconds)

class PrivateSupervisorTests(unittest.TestCase):
 def test_private_config_cannot_fall_through_to_legacy_validation(self):
  with self.assertRaisesRegex(ValueError,'verified instance-bound private profile required'):
   supervisor.validate_config({'private_profile':{'path':'unverified','sha256':'a'*64}})
 def test_profile_log_budget_includes_observer_and_all_individual_bots(self):
  root=Path('/synthetic-private')
  paths=health.log_paths(root,{'processes':dict.fromkeys(Contract.role_names)},Contract())
  self.assertIn(root/'vanilla/SeriousSam.log',paths)
  self.assertEqual(sum(x.name=='BotTelemetry.csv' for x in paths),8)
 def test_private_state_rejects_another_profile_generation(self):
  p=Contract();p.profile_sha256='a'*64
  with self.assertRaisesRegex(ValueError,'generation mismatch'):
   supervisor.validate_state({'root':'/srv/tse-ops-m1-20261027/test','bots':8},{'private_profile_sha256':'b'*64},p)

 def test_profile_roles_keep_eight_clients_and_original_observer(self):
  self.assertTrue(hasattr(supervisor,'roles_for'),'instance-bound roles helper missing')
  self.assertEqual(supervisor.roles_for({'bots':8},Contract()),list(Contract.role_names))
 def test_private_ghost_name_never_authorizes_fleet_eviction(self):
  self.assertEqual(supervisor.recovery_action('gamer-007',['name7'],8,120,profile=Contract()),'WAIT_GHOSTS')
 def test_owned_observer_is_known_but_additional_client_holds(self):
  runtime=supervisor.Runtime.__new__(supervisor.Runtime);runtime.profile=Contract();runtime.c={'port':26820,'bots':8}
  def query(names):
   value={'gamever':'1.07','activemod':'','maxplayers':'16','numplayers':str(len(names))}
   value.update({f'player_{i}':name for i,name in enumerate(names)});return value
  with patch.object(supervisor.q,'query',return_value=query(list(Contract.expected_names))):
   self.assertIsNone(runtime.no_humans())
  with patch.object(supervisor.q,'query',return_value=query([*Contract.expected_names,'Unknown_Player'])):
   with self.assertRaisesRegex(RuntimeError,'human/unknown player hold'):runtime.no_humans()
 def test_health_rejects_private_metadata_without_explicit_profile(self):
  with tempfile.TemporaryDirectory() as td:
   result=Path(td)/'result.json';result.write_text(json.dumps({'private_profile_sha256':'a'*64}))
   with self.assertRaisesRegex(ValueError,'private candidate profile required'):health.collect(result)
 def test_read_only_profile_binds_config_and_result(self):
  self.assertTrue(hasattr(supervisor,'read_only_profile'),'read-only profile binding missing')
  with tempfile.TemporaryDirectory() as td:
   config=Path(td)/'config.json';config.write_text(json.dumps({'private_profile':{'path':'fixture'}}))
   p=Contract();p.root=Path('/srv/tse-ops-m1-20261027/test')
   with patch.object(candidate,'load',return_value=p):
    self.assertIs(supervisor.read_only_profile(config,p.root/'result.json'),p)
    with self.assertRaisesRegex(ValueError,'result/profile mismatch'):supervisor.read_only_profile(config,Path('/another/result.json'))
 def test_monitor_forwards_immutable_instance_profile(self):
  self.assertTrue(hasattr(supervisor,'read_only_profile'),'read-only profile binding missing')
  with tempfile.TemporaryDirectory() as td:
   p=Contract();result=Path(td)/'result.json'
   with patch.object(health,'collect',return_value=({}, {'status':'BLOCKED','safe_recovery':False})) as collect,patch.object(supervisor.time,'sleep',side_effect=StopIteration):
    with self.assertRaises(StopIteration):supervisor.monitor(result,Path(td)/'monitor',10,profile=p)
    collect.assert_called_once_with(result,p)
 def test_stop_closes_every_owned_private_prefix_before_unmount(self):
  # Actual Runtime.stop control flow; only native process/mount boundaries stubbed.
  with tempfile.TemporaryDirectory() as td:
   runtime=supervisor.Runtime.__new__(supervisor.Runtime)
   runtime.root=Path(td);runtime.profile=Contract();runtime.roles=list(Contract.role_names)
   runtime.r={'processes':{}};runtime.c={'port':26820,'display':':125','bots':8};runtime.cg=runtime.root/'tse-ops-test'
   runtime.ownership=lambda:None;runtime.stop_role=lambda role:None
   runtime.save=lambda:None;runtime.log=lambda kind:None
   closed=[]
   def matches(spec):
    return Path(spec['lower'])==runtime.profile.source(Path(spec['target']).name)
   with patch.object(health,'mount_matches',side_effect=matches),patch.object(supervisor,'close_prefix',side_effect=closed.append),patch.object(supervisor.subprocess,'run',return_value=SimpleNamespace(returncode=1)):
    runtime.stop()
   self.assertEqual(closed,[runtime.root/('prefix-'+role) for role in runtime.roles])
   self.assertEqual(runtime.r['status'],'OWNED_ISOLATED_STOPPED')
 def test_legacy_roles_unchanged(self):
  self.assertTrue(hasattr(supervisor,'roles_for'),'instance-bound roles helper missing')
  self.assertEqual(supervisor.roles_for({'bots':8}),['server','botA','botB'])
 def test_profile_bot_and_localplayer_mapping(self):
  self.assertTrue(hasattr(health,'bot_role'),'instance-bound health role helper missing')
  p=Contract()
  self.assertTrue(health.bot_role('gamer-007',p));self.assertFalse(health.bot_role('vanilla',p))
  self.assertEqual(health.local_count('gamer-007',8,p),1)
  self.assertEqual(health.local_count('botA',8),4)
 def test_candidate_recovery_uses_profile_names_without_global_mutation(self):
  before=(health.DLL,tuple(supervisor.q.ROSTER),supervisor.BUILD,supervisor.HOUR)
  p=Contract()
  self.assertEqual(supervisor.recovery_action('gamer-007',['name0','Retail_Control'],8,40,profile=p),'RESTART_ROLE')
  self.assertEqual(supervisor.recovery_action('gamer-007',['name7'],8,2,profile=p),'WAIT_GHOSTS')
  self.assertEqual(supervisor.recovery_action('gamer-007',['unowned-player'],8,40,profile=p),'HOLD_HUMANS')
  self.assertEqual(before,(health.DLL,tuple(supervisor.q.ROSTER),supervisor.BUILD,supervisor.HOUR))
if __name__=='__main__':unittest.main()
