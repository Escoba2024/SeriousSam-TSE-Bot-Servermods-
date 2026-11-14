"""Focused offline ownership, limits and cleanup regressions; no capture."""
import io
import json
from pathlib import Path
import signal
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch


def udp(port,inode):
 return ' 0: 0100007F:%04X 00000000:0000 07 00000000:00000000 00:00000000 00000000 65534 0 %d 2 0 0'%(port,inode)


class OwnedCaptureTests(unittest.TestCase):
 def module(self):
  import owned_sync_capture as capture
  return capture
 def test_only_actual_socket_fd_intersection_owns_a_port(self):
  c=self.module();table='header\n'+udp(27850,100)+'\n'+udp(30000,200)+'\n'
  self.assertEqual(c.socket_rows(table,{200}),[(30000,200)])
  self.assertEqual(c.socket_rows(table,{999}),[])
  with self.assertRaises(ValueError):c.socket_rows('header\nbroken',{200})
 def test_exact_four_roles_ports_namespace_and_unique_ownership(self):
  c=self.module()
  rows={r:dict(identity=[100+i,1000+i],namespace=500,ports=[(p,200+i)])for i,(r,p)in enumerate([('server',27850),('botA',30001),('botB',30002),('vanilla',30003)])}
  rows['server']['ports'].append((27851,250))
  self.assertEqual(c.validate_role_ports(rows)['vanilla'],30003)
  for change in ('multiple','duplicate','ns','pid','server','fd','missing'):
   import copy
   bad=copy.deepcopy(rows)
   if change=='multiple':bad['vanilla']['ports'].append((30004,260))
   elif change=='duplicate':bad['vanilla']['ports']=[(30002,260)]
   elif change=='ns':bad['vanilla']['namespace']+=1
   elif change=='pid':bad['vanilla']['identity']=list(bad['botA']['identity'])
   elif change=='server':bad['server']['ports'].pop()
   elif change=='fd':bad['vanilla']['ports']=[(30003,201)]
   else:bad.pop('vanilla')
   with self.subTest(change=change),self.assertRaises(ValueError):c.validate_role_ports(bad)
 def test_ready_header_and_zero_drop_stats_are_strict(self):
  c=self.module();header=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,262144,1)
  log='tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes\n'
  self.assertTrue(c.ready(log,header));self.assertFalse(c.ready('',header));self.assertFalse(c.ready(log,b''))
  with self.assertRaises(ValueError):c.ready(log,header[:-4]+struct.pack('<I',113))
  stats='12 packets captured\n24 packets received by filter\n0 packets dropped by kernel\n'
  self.assertEqual(c.capture_stats(stats)['dropped'],0)
  for bad in ('',stats.replace('0 packets dropped','1 packets dropped')):
   with self.assertRaises(ValueError):c.capture_stats(bad)
 def test_scope_size_packet_and_wall_bounds_never_rotate(self):
  c=self.module();argv=c.capture_argv(123)
  self.assertEqual(argv[:4],['/usr/bin/nsenter','--target','123','--net'])
  self.assertIn('-w',argv);self.assertEqual(argv[argv.index('-w')+1],'-')
  self.assertNotIn('-C',argv);self.assertNotIn('-W',argv)
  self.assertEqual(argv[argv.index('-c')+1],str(c.MAX_PACKETS))
  for name,value in [('size',c.MAX_BYTES),('packets',c.MAX_PACKETS),('seconds',c.MAX_SECONDS)]:
   with self.subTest(name=name),self.assertRaises(ValueError):c.check_limits(**{name:value})
 def test_normal_stop_waits_and_timeout_stays_failure_after_own_cleanup(self):
  c=self.module();p=Mock();p.poll.return_value=None;p.wait.return_value=0
  signals=[];c.stop_owned(p,lambda sig:signals.append(sig))
  self.assertEqual(signals,[signal.SIGINT]);p.wait.assert_called_once_with(timeout=10)
  p=Mock();p.poll.return_value=None;p.wait.side_effect=[subprocess.TimeoutExpired('capture',10),0]
  signals=[]
  with self.assertRaises(RuntimeError):c.stop_owned(p,lambda sig:signals.append(sig))
  self.assertEqual(signals,[signal.SIGINT,signal.SIGTERM])
 def test_premature_exit_or_changed_ownership_is_never_accepted(self):
  c=self.module()
  with self.assertRaises(ValueError):c.check_running(0,1,1,2,2)
  with self.assertRaises(ValueError):c.check_running(None,1,2,2,2)
  with self.assertRaises(ValueError):c.check_running(None,1,1,2,3)
 def test_only_exact_setup_transition_is_pending_before_tcpdump_namespace_binding(self):
  c=self.module();args=c.capture_argv(123);helper=['/usr/bin/python3','-B','/private/owned_capture_exec.py','/private/config.json']
  self.assertFalse(c.exec_ready(helper,args,helper,1,2))
  self.assertFalse(c.exec_ready(args,args,helper,1,2))
  self.assertTrue(c.exec_ready(args[4:],args,helper,2,2))
  for actual,ns in [(['/foreign'],2),(args[4:],1)]:
   with self.assertRaises(ValueError):c.exec_ready(actual,args,helper,ns,2)
 def test_closed_receipt_is_still_archived_and_audited_after_role_guard_error(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   cap=c.OwnedSyncCapture(directory,{})
   cap.started=1.;cap.process=Mock();cap.process.poll.return_value=None;cap.process.wait.return_value=0
   cap.signal_group=Mock();cap.before={'fixture':'before'};cap.ports={'botA':1,'botB':2,'vanilla':3}
   cap.pcap.write_bytes(b'raw retained')
   cap.log.write_text('12 packets captured\n24 packets received by filter\n0 packets dropped by kernel\n')
   with patch.object(c,'observe_roles',side_effect=ValueError('role changed')),patch.object(c,'audit_pairs',return_value={'evidence':'retained'})as audits,patch.object(c.time,'monotonic',return_value=2.):
    with self.assertRaises(RuntimeError):cap.close()
   cap.process.wait.assert_called_once_with(timeout=10);audits.assert_called_once()
   receipt=json.loads((Path(directory)/'owned-sync-capture.json').read_text())
   self.assertIn('pcap_sha256',receipt);self.assertEqual(receipt['pair_audits'],{'evidence':'retained'})
   self.assertTrue(receipt['errors']);self.assertFalse(receipt['protocol_complete'])
 def test_actual_main_pid_fd_reader_rejects_identity_and_namespace_changes(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);proc=root/'proc';arena=root/'arena';arena.mkdir()
   (proc/'1/ns').mkdir(parents=True);(proc/'1/ns/net').write_text('host')
   ns=root/'shared-netns';ns.write_text('owned')
   registry={};table='header\n'+''.join(udp(p,i)+'\n'for p,i in[(27850,200),(27851,250),(30001,201),(30002,202),(30003,203)])
   for i,role in enumerate(c.ROLES):
    pid=100+i;start=1000+i;p=proc/str(pid);(p/'fd').mkdir(parents=True);(p/'ns').mkdir();(p/'net').mkdir();(arena/role).mkdir()
    (p/'cwd').symlink_to(arena/role);(p/'ns/net').hardlink_to(ns)
    (p/'comm').write_text('DedicatedServer'if role=='server'else'SeriousSam.exe')
    unit='own-'+role+'.service';(p/'cgroup').write_text('0::/system.slice/'+unit+'\n')
    (p/'net/udp').write_text(table);(p/'net/udp6').write_text('header\n')
    for index,inode in enumerate([200,250]if role=='server'else[200+i]):(p/'fd'/str(index)).symlink_to('socket:[%d]'%inode)
    registry[role]=dict(identity=[pid,start],unit=unit)
   def fake_path(value):
    value=str(value)
    return proc/value.removeprefix('/proc/').removeprefix('/proc')if value.startswith('/proc')else Path(value)
   with patch.object(c,'Path',side_effect=fake_path),patch.object(c,'ARENA',arena),patch.object(c,'read_start',side_effect=lambda pid:1000+pid-100):
    rows=c.observe_roles(registry);self.assertEqual(c.validate_role_ports(rows)['vanilla'],30003)
    with patch.object(c,'read_start',return_value=999):
     with self.assertRaises(ValueError):c.observe_roles(registry)
    (proc/'103/ns/net').unlink();(proc/'103/ns/net').write_text('other')
    with self.assertRaises(ValueError):c.observe_roles(registry)
 def test_partial_popen_identity_failure_keeps_handle_for_regular_cleanup(self):
  c=self.module();rows={r:dict(identity=[100+i,1000+i],namespace=500,ports=[(p,200+i)])for i,(r,p)in enumerate([('server',27850),('botA',30001),('botB',30002),('vanilla',30003)])};rows['server']['ports'].append((27851,250))
  with tempfile.TemporaryDirectory()as directory:
   cap=c.OwnedSyncCapture(directory,{})
   proc=Mock(pid=123);proc.poll.return_value=None;proc.wait.return_value=0
   with patch.object(c,'RUNTIME_REVIEWED',True),patch.object(c,'observe_roles',return_value=rows),patch.object(c.subprocess,'Popen',return_value=proc),patch.object(c,'read_start',side_effect=FileNotFoundError('start unavailable')):
    with self.assertRaises(FileNotFoundError):cap.start()
   self.assertIs(cap.process,proc);self.assertEqual(cap.receipt['supervisor_pid'],123)
   cap.signal_group=Mock()
   with patch.object(c,'observe_roles',return_value=rows):
    with self.assertRaises(RuntimeError):cap.close() # zero-byte capture remains failed
   proc.wait.assert_called_once_with(timeout=10);cap.signal_group.assert_called_once_with(signal.SIGINT)
 def test_already_exited_supervisor_does_not_leave_its_verified_child_running(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   cap=c.OwnedSyncCapture(directory,{});cap.process=Mock();cap.process.poll.return_value=124;cap.process.wait.return_value=124
   cap.owner=dict(identity=[123,456]);cap.before={};cap.started=1.;cap.ports={};cap.pcap.write_bytes(b'raw');cap.log.write_text('')
   with patch.object(c,'read_start',return_value=456),patch.object(c.os,'getpgid',return_value=cap.process.pid),patch.object(c.os,'kill')as kill,patch.object(c,'wait_capture_end',return_value=None)as wait,patch.object(c,'observe_roles',return_value={}),patch.object(c.time,'monotonic',return_value=2.):
    with self.assertRaises(RuntimeError):cap.close()
   kill.assert_called_once_with(123,signal.SIGINT);wait.assert_called_once_with([123,456],10)
   cap.process.wait.assert_called_once_with(timeout=0)
 def test_actual_exec_helper_records_owner_and_limits_before_mocked_exec(self):
  c=self.module();import owned_capture_exec as helper
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);config=root/'config.json';owner=root/'owned-sync-owner.json'
   c.exclusive_json(config,dict(source_pins={},registry={'server':{'identity':[123,456]}},binding={'fixture':True},owner_path=str(owner)))
   def exec_stub(path,argv):
    self.assertEqual(path,'/usr/bin/nsenter');self.assertTrue(owner.is_file());raise RuntimeError('mocked exec only')
   with patch.object(helper,'RUNTIME_REVIEWED',True),patch.object(helper,'observe_roles',return_value={'fixture':True}),patch.object(helper,'read_start',return_value=456),patch.object(helper.os,'execv',side_effect=exec_stub),patch.object(helper.resource,'setrlimit')as limit:
    with self.assertRaisesRegex(RuntimeError,'mocked exec only'):helper.main(config)
   limit.assert_called_once_with(helper.resource.RLIMIT_FSIZE,(c.MAX_BYTES,c.MAX_BYTES))
   self.assertEqual(owner.stat().st_mode&0o777,0o600)
 def test_three_explicit_pairs_and_no_auto_port_selection(self):
  c=self.module();ports={'botA':1,'botB':2,'vanilla':3}
  calls=[]
  def audit(stream,source_ports,destination_port):
   calls.append((tuple(source_ports),destination_port));return {'qualified':False,'paired_checks':1,'matching_pairs':1,'differing_pairs':0,'status':'MATCHING_SAMPLED_SYNCCHECKS_ONLY','first_differing_sampled_synccheck':None}
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'private.pcap';path.write_bytes(b'fixture')
   out=c.audit_pairs(path,ports,audit)
  self.assertEqual(calls,[((1,2),27850),((1,3),27850),((2,3),27850)])
  self.assertEqual(len(out),3)


if __name__=='__main__':unittest.main()
