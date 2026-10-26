import copy,importlib.util,json,os,socket,subprocess,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'operations'))
try:import fleet_health as h
except ImportError:h=None

class HealthTests(unittest.TestCase):
 def require(self):self.assertIsNotNone(h,'guarded fleet health subsystem is missing')
 def snapshot(self):
  return dict(now=1000,query_time=999,query=dict(gamever='1.07',numplayers='8',maxplayers='16',activemod='',**{'player_'+str(i):n for i,n in enumerate(['BOT-Rookie-Rush','BOT-Rookie-Guard','BOT-Casual-Flaky','BOT-Casual-Holder','BOT-Average-Duelist','BOT-Average-Rifle','BOT-Veteran-Push','BOT-Expert-Rifle'])}),identity_errors=[],missing=[],ports_owned=True,mounts_owned=True,dll_valid=True,disk_free=12*1024**3,master_ok=True,telemetry_ok=True,owned_sync_bad=0,external_sync_bad=0,logs_over_limit=False)
 def test_healthy(self):
  self.require();r=h.assess(self.snapshot());self.assertEqual(r['status'],'HEALTHY');self.assertTrue(r['safe_recovery'])
 def test_unknown_is_never_empty(self):
  self.require();s=self.snapshot();s['query']=None;r=h.assess(s);self.assertFalse(r['safe_recovery']);self.assertIn('QUERY_UNCERTAIN',r['alerts'])
 def test_stale_query_blocks(self):
  self.require();s=self.snapshot();s['query_time']=900;self.assertFalse(h.assess(s)['safe_recovery'])
 def test_human_hold(self):
  self.require();s=self.snapshot();s['query']['numplayers']='9';s['query']['player_8']='Human';r=h.assess(s);self.assertTrue(r['humans']);self.assertFalse(r['safe_recovery'])
 def test_missing_bot_is_recoverable_only_with_confirmed_ownership(self):
  self.require();s=self.snapshot();del s['query']['player_7'];s['query']['numplayers']='7';s['missing']=['botB'];r=h.assess(s);self.assertEqual(r['status'],'DEGRADED');self.assertTrue(r['safe_recovery'])
 def test_identity_pid_reuse_cwd_cgroup_each_blocks(self):
  self.require()
  for error in ['PID_REUSED','WRONG_CWD','WRONG_CGROUP']:
   s=self.snapshot();s['identity_errors']=[error];self.assertEqual(h.assess(s)['status'],'BLOCKED');self.assertFalse(h.assess(s)['safe_recovery'])
 def test_foreign_port_and_mount_block(self):
  self.require()
  for key in ['ports_owned','mounts_owned','dll_valid','master_ok']:
   s=self.snapshot();s[key]=False;self.assertFalse(h.assess(s)['safe_recovery'],key)
 def test_low_disk_and_stale_telemetry_block(self):
  self.require()
  for key,value in [('disk_free',7*1024**3),('telemetry_ok',False)]:
   s=self.snapshot();s[key]=value;self.assertFalse(h.assess(s)['safe_recovery'])
 def test_external_sync_alert_never_requests_restart(self):
  self.require();s=self.snapshot();s['external_sync_bad']=21;r=h.assess(s);self.assertIn('EXTERNAL_CLIENT_SYNC',r['alerts']);self.assertEqual(r['recover_roles'],[])
 def test_owned_sync_is_blocker(self):
  self.require();s=self.snapshot();s['owned_sync_bad']=1;self.assertFalse(h.assess(s)['safe_recovery'])
 def test_lookalike_duplicate_names_cannot_mask_human(self):
  self.require();s=self.snapshot();s['query']['player_7']='BOT-Rookie-Rush';self.assertFalse(h.assess(s)['safe_recovery'])

class ProcessTests(unittest.TestCase):
 def test_process_identity_real_process(self):
  self.assertIsNotNone(h,'process identity guard is missing')
  with tempfile.TemporaryDirectory() as d:
   p=subprocess.Popen(['sleep','30'],cwd=d)
   try:
    info=h.process_identity(p.pid);self.assertEqual(h.verify_process(info),'LIVE')
    bad=dict(info,start_ticks=info['start_ticks']+1);self.assertEqual(h.verify_process(bad),'PID_REUSED')
    bad=dict(info,cwd='/nonexistent');self.assertEqual(h.verify_process(bad),'WRONG_CWD')
    bad=dict(info,cgroup='/wrong');self.assertEqual(h.verify_process(bad),'WRONG_CGROUP')
   finally:p.terminate();p.wait()
   self.assertEqual(h.verify_process(info),'ABSENT')
 def test_udp_owner_real_socket(self):
  self.assertIsNotNone(h,'UDP ownership guard is missing')
  with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
   s.bind(('127.0.0.1',0));owners=h.udp_owners(s.getsockname()[1]);self.assertEqual(owners,{os.getpid()})
 def test_telemetry_freshness_and_draw(self):
  self.assertIsNotNone(h,'telemetry validation missing')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'t.csv';p.write_text('#columns,t_ms,ticks,actions,renderdraw,lp,gameon,enabled,stall_s\n1000000,20,80,0,4,1,1,0\n')
   self.assertTrue(h.telemetry_valid(p,now=1000));self.assertFalse(h.telemetry_valid(p,now=1100))
   p.write_text(p.read_text().replace(',80,0,4,',',80,1,4,'));self.assertFalse(h.telemetry_valid(p,now=1000))


try:import fleet_supervisor as v
except ImportError:v=None
class SupervisorTests(unittest.TestCase):
 def require(self):self.assertIsNotNone(v,'isolated supervisor missing')
 def test_config_refuses_public_paths_and_ports(self):
  self.require()
  for root,port in [('/srv/tse-integration-public-20261021',26820),('/tmp/test',25600)]:
   with self.assertRaises(ValueError):v.validate_config(dict(root=root,port=port,display=':125',bots=8))
 def test_config_requires_pinned_build_and_absolute_template(self):
  self.require()
  with self.assertRaises(ValueError):v.validate_config(dict(root='/srv/tse-ops-runtime-20261021/test',port=26820,display=':125',bots=8,build_manifest='/tmp/unknown'))
 def test_attempt_budget_persisted_and_backoff(self):
  self.require();state={'attempts':[100,110,120]}
  self.assertFalse(v.retry_allowed(state,130));self.assertTrue(v.retry_allowed(state,4000));self.assertFalse(v.retry_allowed({'attempts':[100]},101))
 def test_exclusive_lock_no_double_controller(self):
  self.require()
  with tempfile.TemporaryDirectory() as d:
   a=v.acquire_lock(Path(d)/'lock')
   try:
    with self.assertRaises(BlockingIOError):v.acquire_lock(Path(d)/'lock')
   finally:a.close()
 def test_archive_refuses_live_writer(self):
  self.require()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'log';f=p.open('wb');f.write(b'proof');f.flush()
   try:
    with self.assertRaises(RuntimeError):v.archive_closed([p],Path(d)/'archive')
   finally:f.close()
   self.assertEqual(p.read_bytes(),b'proof')
 def test_archive_restores_exact_bytes_and_budget_fail_closed(self):
  self.require()
  with tempfile.TemporaryDirectory() as d:
   import gzip
   p=Path(d)/'log';payload=b'evidence\n'*200;p.write_bytes(payload);a=Path(d)/'archive';r=v.archive_closed([p],a);self.assertEqual(gzip.decompress(Path(r[0]['archive']).read_bytes()),payload);self.assertFalse(p.exists())
   p.write_bytes(b'untouched')
   with self.assertRaises(RuntimeError):v.archive_closed([p],a,budget=1)
   self.assertEqual(p.read_bytes(),b'untouched')
 def test_private_master_guard_uses_only_own_query_port(self):
  self.require();self.assertTrue(hasattr(v,'master_rule'),'private master guard missing');rule=v.master_rule(26820,'fixture')
  self.assertIn('26821',rule);self.assertIn('27900',rule);self.assertNotIn('25601',rule)
  with self.assertRaises(ValueError):v.master_rule(25600,'fixture')
 def test_ghost_roster_wait_then_safe_full_recovery(self):
  self.require();self.assertTrue(hasattr(v,'recovery_action'),'ghost-aware recovery is missing')
  self.assertEqual(v.recovery_action('botA',h.q.ROSTER,8,0),'WAIT_GHOSTS')
  self.assertEqual(v.recovery_action('botA',h.q.ROSTER,8,31),'RESTART_FLEET')
  self.assertEqual(v.recovery_action('botA',h.q.ROSTER[4:],8,0),'RESTART_ROLE')
  self.assertEqual(v.recovery_action('botA',h.q.ROSTER+['Human'],8,100),'HOLD_HUMANS')
 def test_state_cannot_point_recovery_at_production_process(self):
  self.require();self.assertTrue(hasattr(v,'validate_state'),'manifest ownership boundary missing')
  c={'root':'/srv/tse-ops-runtime-20261021/test','bots':8}
  for r in [{'processes':{'server':{'cwd':'/srv/tse-integration-public-20261021/server'}}},{'processes':{'foreign':{'cwd':c['root']+'/foreign'}}},{'processes':{},'cgroup':'/sys/fs/cgroup/foreign'}]:
   with self.assertRaises(ValueError):v.validate_state(c,r)
 def test_log_threshold_has_guarded_maintenance_action(self):
  self.require();self.assertTrue(hasattr(v,'maintenance_action'),'log limit maintenance missing')
  self.assertEqual(v.maintenance_action(True,False,False,True),'HOLD')
  self.assertEqual(v.maintenance_action(True,True,True,True),'HOLD')
  self.assertEqual(v.maintenance_action(True,True,False,True),'RESTART_FLEET')
  self.assertEqual(v.maintenance_action(True,True,False,False),'STOP_BUDGET_HOLD')
  self.assertEqual(v.maintenance_action(False,True,False,True),'NONE')
 def test_pidfd_wait_survives_exit_command_transition(self):
  self.require();self.assertTrue(hasattr(v,'owned_pidfd'),'pidfd shutdown wait missing')
  with tempfile.TemporaryDirectory() as d:
   ready=Path(d)/'ready';code="import os,signal,time;from pathlib import Path;signal.signal(signal.SIGTERM,lambda a,b:os.execl('/bin/sleep','exit-transition','0.1'));Path("+repr(str(ready))+").touch();time.sleep(20)"
   p=subprocess.Popen([sys.executable,'-c',code],cwd=d)
   try:
    deadline=time.monotonic()+3
    while not ready.exists() and time.monotonic()<deadline:time.sleep(.01)
    self.assertTrue(ready.exists());info=h.process_identity(p.pid)
    with self.assertRaises(RuntimeError):v.owned_pidfd(dict(info,start_ticks=info['start_ticks']+1))
    fd=v.owned_pidfd(info)
    try:
     import signal
     signal.pidfd_send_signal(fd,signal.SIGTERM);self.assertTrue(v.wait_pidfd(fd,3))
    finally:os.close(fd)
   finally:
    if p.poll() is None:p.kill()
    p.wait()
 def test_bounded_event_log(self):
  self.require()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'events.json'
   for i in range(30):v.event(p,{'n':i},limit=10)
   r=json.loads(p.read_text());self.assertEqual(len(r),10);self.assertEqual(r[0]['n'],20)

if __name__=='__main__':unittest.main()
