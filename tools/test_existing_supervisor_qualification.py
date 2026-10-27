"""Pure source/metadata tests. No fixture grants native acceptance."""
import contextlib,io,json,sys,unittest,gzip,tempfile,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import sys
sys.path.insert(0,str(Path(__file__).parent))
import qualify_existing_supervisor as qualifier

class SupervisorQualificationTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(qualifier,'thin existing Runtime qualification driver missing')
 def test_guard_preserves_exact_reserve_and_three_cpu_samples(self):
  s={'public_disabled':True,'available_mib':768,'disk_free_gib':8,'host_busy_percent':85}
  a=qualifier.guard_sample(s,0);b=qualifier.guard_sample(s,a['overload']);c=qualifier.guard_sample(s,b['overload'])
  self.assertFalse(a['abort']);self.assertFalse(b['abort']);self.assertTrue(c['abort'])
  for key,value in [('available_mib',767.9),('disk_free_gib',7.99),('public_disabled',False),('host_busy_percent',float('nan'))]:
   with self.subTest(key=key):self.assertTrue(qualifier.guard_sample(dict(s,**{key:value}),0)['abort'])
 def test_no_core_result_can_claim_all_native_gates_or_m1(self):
  phases={key:{'status':'PASS_NATIVE'} for key in qualifier.CORE_PHASES}
  verdict=qualifier.core_verdict(phases)
  self.assertFalse(verdict['m1_complete']);self.assertFalse(verdict['all_supervisor_gates_accepted'])
  self.assertTrue(set(qualifier.DEFERRED_PHASES)<=set(verdict['not_tested']))
  phases['following_generation_hour']={'status':'NOT_TESTED'}
  self.assertEqual(qualifier.core_verdict(phases)['status'],'BLOCKED')
 def test_fault_metadata_cannot_be_a_status_only_receipt(self):
  for x in [{},{'status':'FAULT_QUALIFICATION_ACCEPTED'},{'status':'BLOCKED','m1_complete':False}]:
   with self.assertRaises(ValueError):qualifier.validate_fault_metadata(x)
 def test_abort_is_once_pidfd_bound_and_never_interrupts_cleanup(self):
  child=SimpleNamespace(poll=lambda:None);owned=SimpleNamespace(process=child,pidfd=123)
  with patch.object(qualifier.signal,'pidfd_send_signal') as send:
   state={};qualifier.request_abort(owned,state,{'phase':'CLEANUP_IN_PROGRESS'});send.assert_not_called()
   qualifier.request_abort(owned,state,{'phase':'FOLLOWING_GENERATION_HOUR'});send.assert_called_once_with(123,qualifier.signal.SIGINT)
   qualifier.request_abort(owned,state,{});self.assertEqual(send.call_count,1)
 def test_inner_command_has_one_owned_exec_and_full_hour_budget(self):
  cmd=qualifier.build_inner_command(Path('/private/policy.json'),'a'*64,Path('/private/evidence'))
  self.assertEqual(cmd[:3],['unshare','--net','--']);self.assertNotIn('--fork',cmd)
  self.assertEqual(cmd.count('--inner'),1);self.assertGreaterEqual(qualifier.HOUR_SECONDS,3600)
  self.assertGreater(qualifier.TOTAL_BUDGET_SECONDS,qualifier.HOUR_SECONDS+qualifier.CLEANUP_SECONDS)
 def test_sampler_records_absent_role_without_reading_its_pid(self):
  supervisor,_,_=qualifier.modules()
  info={'pid':123,'start_ticks':1,'cwd':'/source-only/gamer-000','command':'SeriousSam.exe','cgroup':'0::/source-only'}
  runtime=SimpleNamespace(roles=['gamer-000'],root=Path('/source-only'),profile=None,r={'processes':{'gamer-000':info}},reconcile=lambda:{'status':'DEGRADED'})
  with patch.object(supervisor.h,'verify_process',return_value='ABSENT'):
   row=qualifier.sampled(runtime)
  self.assertIn('gamer-000',row['process_resources']);self.assertEqual(row['process_resources']['gamer-000']['status'],'ABSENT')
 def test_archive_proof_excludes_inherited_template_archive_rows(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'archives').mkdir();data=b'synthetic closed log fixture'
   archive=root/'archives/new.gz'
   with gzip.open(archive,'wb') as stream:stream.write(data)
   old={'archive':str(root/'archives/inherited-not-read.gz'),'source':str(root/'old'),'sha256':'a'*64}
   new={'archive':str(archive),'source':str(root/'new'),'sha256':hashlib.sha256(data).hexdigest()}
   (root/'archives/manifest.json').write_text(json.dumps([old,new]))
   result=qualifier.verify_archives(root,start_index=1)
   self.assertEqual(result['status'],'ARCHIVE_BYTES_VERIFIED');self.assertEqual(len(result['archives']),1)
 def test_full_hour_is_measured_from_first_actual_healthy_sample(self):
  fields={'status':'HEALTHY','safe_recovery':True,'query_fresh':True,'telemetry_fresh':True,'owned_sync_bad':0,'sync_scan_complete':True}
  frozen={'bot':{'pid':1}}
  rows=[{'mono':t,'health':dict(fields),'generations':frozen,'process_resources':{'bot':{'status':'LIVE','cpu_s':t,'rss_kib':1024}},'log_bytes':{}} for t in range(10,3611,10)]
  with patch.object(qualifier,'step',side_effect=rows) as step,patch.object(qualifier.time,'sleep'),patch.object(qualifier.time,'monotonic',return_value=0):
   result=qualifier.measure_healthy(None,None,{},3600,frozen)
  self.assertEqual(step.call_count,361);self.assertGreaterEqual(result['elapsed_s'],3600)
 def test_reviewed_driver_sources_enter_repeated_context_pins(self):
  self.assertTrue(hasattr(qualifier,'policy_source_pins'),'repeated driver-source pins missing')
  policy={'source_sha256':{'tools/qualify_existing_supervisor.py':'a'*64}}
  self.assertEqual(qualifier.policy_source_pins(policy),{qualifier.REPO/'tools/qualify_existing_supervisor.py':'a'*64})
 def test_abort_tolerates_owned_child_exit_race_without_second_signal(self):
  owned=SimpleNamespace(process=SimpleNamespace(poll=lambda:None),pidfd=456)
  state={}
  with patch.object(qualifier.signal,'pidfd_send_signal',side_effect=ProcessLookupError):qualifier.request_abort(owned,state,{})
  self.assertTrue(state['abort_requested'])
 def test_default_cli_performs_no_process_or_filesystem_action(self):
  out=io.StringIO()
  with patch.object(qualifier.subprocess,'Popen') as popen,patch.object(qualifier,'execute_outer') as execute,contextlib.redirect_stdout(out):qualifier.main([])
  self.assertEqual(json.loads(out.getvalue())['status'],'DRY_RUN_NO_NATIVE_ACTIONS');popen.assert_not_called();execute.assert_not_called()



class ExistingRuntimeSafetyContracts(unittest.TestCase):
 """Fixture-only checks of existing Runtime paths; no native gate is granted."""
 def setUp(self):
  self.supervisor,_,_=qualifier.modules()
  self.directory=tempfile.TemporaryDirectory()
  self.addCleanup(self.directory.cleanup)
  self.root=Path(self.directory.name)
 def snapshot(self,**updates):
  query={'gamever':'1.07','maxplayers':'16','numplayers':'0'}
  if updates.get('missing')==[]:query.update(numplayers='1',player_0=self.supervisor.q.ROSTER[0])
  sample=dict(now=1000,query_time=1000,query=query,
   expected_names=self.supervisor.q.ROSTER[:1],ports_owned=True,mounts_owned=True,dll_valid=True,
   master_ok=True,telemetry_ok=True,disk_free=self.supervisor.h.MIN_FREE,
   identity_errors=[],cgroup_issues=[],resource_issues=[],sync_scan_complete=True,
   owned_sync_bad=0,external_sync_bad=0,missing=['botA'],logs_over_limit=False)
  sample.update(updates)
  return sample
 def runtime(self,attempts=()):
  v=self.supervisor
  runtime=v.Runtime.__new__(v.Runtime)
  runtime.root=self.root;runtime.result=self.root/'result.json'
  runtime.c={'bots':1,'port':26800};runtime.profile=None
  # Close/reopen the real fixture file to exercise persisted restart history.
  runtime.result.write_text(json.dumps({'attempts':list(attempts),'last_no_humans':979}))
  runtime.r=json.loads(runtime.result.read_text())
  for name in ['ownership','save','log','no_humans','stop','start','launch']:
   setattr(runtime,name,Mock())
  return runtime
 def reconcile(self,runtime,snapshot):
  v=self.supervisor;health=v.h.assess(snapshot)
  with patch.object(v.h,'collect',return_value=(snapshot,health)),patch.object(v.time,'time',return_value=snapshot['now']):
   runtime.reconcile()
  return health
 def assert_no_actions(self,runtime):
  for name in ['no_humans','stop','start','launch']:
   getattr(runtime,name).assert_not_called()
 def test_duplicate_actual_runtime_lock_rejects_before_process_actions(self):
  v=self.supervisor;config=self.root/'config.json'
  config.write_text(json.dumps({'root':str(self.root),'bots':1}))
  (self.root/'result.json').write_text('{}')
  with patch.object(v,'validate_config',return_value=self.root),patch.object(v.subprocess,'Popen') as popen:
   first=v.Runtime(config)
   try:
    with self.assertRaises(BlockingIOError):v.Runtime(config)
    popen.assert_not_called()
   finally:first.close()
   second=v.Runtime(config);second.close()
 def test_unknown_roster_blocks_existing_recovery_and_maintenance(self):
  for over in [False,True]:
   with self.subTest(over_limit=over):
    runtime=self.runtime()
    health=self.reconcile(runtime,self.snapshot(query={'gamever':'1.07','maxplayers':'16','numplayers':'1','player_0':'UnknownGuest'},logs_over_limit=over))
    self.assertIn('HUMAN_HOLD',health['alerts'])
    self.assertFalse(health['safe_recovery']);self.assert_no_actions(runtime)
 def test_stale_and_future_query_block_existing_recovery(self):
  for timestamp in [994,1001]:
   with self.subTest(query_time=timestamp):
    runtime=self.runtime()
    health=self.reconcile(runtime,self.snapshot(query_time=timestamp))
    self.assertIn('QUERY_UNCERTAIN',health['alerts']);self.assert_no_actions(runtime)
 def test_server_loss_cannot_use_expired_no_human_snapshot(self):
  runtime=self.runtime()
  with patch.object(self.supervisor.h,'udp_owners',return_value=set()):
   health=self.reconcile(runtime,self.snapshot(query=None,missing=['server']))
  self.assertFalse(health['safe_recovery']);self.assert_no_actions(runtime)
 def test_persisted_backoff_rejects_before_boundary_then_recovers(self):
  runtime=self.runtime([971])
  self.reconcile(runtime,self.snapshot())
  self.assert_no_actions(runtime)
  runtime=self.runtime([970])
  self.reconcile(runtime,self.snapshot())
  runtime.launch.assert_called_once_with('botA')
  self.assertEqual(runtime.r['attempts'],[970,1000])
 def test_three_recent_attempts_hold_after_reopening_state(self):
  runtime=self.runtime([900,920,940])
  self.reconcile(runtime,self.snapshot())
  runtime.log.assert_called_once_with('CIRCUIT_OPEN')
  self.assertEqual(runtime.r['attempts'],[900,920,940]);self.assert_no_actions(runtime)
 def test_log_maintenance_uses_existing_stop_restart_path(self):
  runtime=self.runtime()
  self.reconcile(runtime,self.snapshot(logs_over_limit=True,missing=[]))
  runtime.no_humans.assert_called_once();runtime.stop.assert_called_once();runtime.start.assert_called_once()
  runtime.launch.assert_not_called()
  runtime.log.assert_called_once_with('LOG_MAINTENANCE',action='RESTART_FLEET')
 def test_log_maintenance_with_open_circuit_stops_without_restart(self):
  runtime=self.runtime([900,920,940])
  self.reconcile(runtime,self.snapshot(logs_over_limit=True,missing=[]))
  runtime.stop.assert_called_once();runtime.start.assert_not_called();runtime.launch.assert_not_called()
  runtime.log.assert_called_once_with('LOG_MAINTENANCE',action='STOP_BUDGET_HOLD')
 def test_unsafe_log_scan_cannot_authorize_maintenance(self):
  runtime=self.runtime()
  self.reconcile(runtime,self.snapshot(logs_over_limit=True,sync_scan_complete=False))
  self.assert_no_actions(runtime)

if __name__=='__main__':unittest.main()
