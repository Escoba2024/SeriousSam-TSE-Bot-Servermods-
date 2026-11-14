"""Offline staged capture and byte-exact prospective cut regressions."""
import copy
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import Mock,patch

from test_ownns_latejoin_preflight import fixture

HEADER=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,262144,1)
def record(payload=b'x'*14):return struct.pack('<IIII',1,0,len(payload),len(payload))+payload


class LateCapture(unittest.TestCase):
 def module(self):
  import owned_latejoin_capture as c
  return c
 def test_staged_capture_missing_is_explicit_red(self):
  self.assertIsNotNone(importlib.util.find_spec('owned_latejoin_capture'),'staged capture not implemented')
 def cap(self,directory):
  c=self.module();before=fixture()['binding_before']
  cap=c.OwnedLatejoinCapture(directory,{r:dict(identity=v['identity'],unit=v['unit'])for r,v in before.items()})
  cap.before=copy.deepcopy(before);cap.initial_binding=copy.deepcopy(before);cap.ports={'botA':30001,'botB':30002};cap.started=100.;cap.guard=Mock()
  return cap,before
 def test_ordinary_capture_and_port_validator_still_require_four_roles(self):
  import owned_sync_capture as base
  with self.assertRaises(ValueError):base.validate_role_ports(fixture()['binding_before'])
  with self.assertRaises(ValueError):base.observe_roles({})
 def test_shared_reader_extraction_exposes_only_the_two_closed_schemas(self):
  import owned_sync_capture as base
  rows=fixture()['binding_before'];rows.pop('botB')
  with self.assertRaises(ValueError):base._validate_role_ports(rows,('server','botA'))
 def test_single_real_admission_preserves_three_initial_bindings(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   cap,before=self.cap(directory);after=copy.deepcopy(before)
   spec=dict(identity=[500,600],unit='own-vanilla.service');after['vanilla']=dict(**spec,namespace=900,ports=[[30003,99]])
   with patch.object(c.time,'monotonic',return_value=105.):cap.begin_admission(spec['unit'])
   with patch.object(c,'observe_roles',return_value=after),patch.object(c.time,'monotonic',return_value=110.):cap.admit(spec)
   self.assertEqual(cap.initial_binding,before);self.assertEqual(cap.before,after)
   self.assertEqual(cap.registry['vanilla'],spec);self.assertEqual(cap.stage,'FOUR_ROLES')
   self.assertEqual(json.loads((Path(directory)/'owned-sync-admission.json').read_text())['old_binding'],before)
   self.assertEqual((Path(directory)/'owned-sync-admission.json').stat().st_mode&0o777,0o600)
   with self.assertRaises(ValueError):cap.admit(spec)
 def test_begin_admission_does_not_create_a_fake_pid_or_port(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   cap,before=self.cap(directory)
   with patch.object(c.time,'monotonic',return_value=101.):cap.begin_admission('own-vanilla.service')
   self.assertNotIn('vanilla',cap.registry);self.assertNotIn('vanilla',cap.ports)
 def test_changed_old_pid_unit_port_inode_or_namespace_never_rebases(self):
  c=self.module()
  for field,value in [('identity',[99,9]),('unit','foreign.service'),('ports',[[31111,999]]),('namespace',999)]:
   with self.subTest(field=field),tempfile.TemporaryDirectory()as directory:
    cap,before=self.cap(directory);after=copy.deepcopy(before);after['botA'][field]=value
    spec=dict(identity=[500,600],unit='own-vanilla.service');after['vanilla']=dict(**spec,namespace=900,ports=[[30003,99]])
    with patch.object(c.time,'monotonic',return_value=105.):cap.begin_admission(spec['unit'])
    with patch.object(c,'observe_roles',return_value=after),patch.object(c.time,'monotonic',return_value=110.),self.assertRaises(ValueError):cap.admit(spec)
    self.assertEqual(cap.before,before);self.assertNotIn('vanilla',cap.registry)
 def test_join_cannot_consume_the_600plus10_capture_budget(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   cap,before=self.cap(directory)
   with patch.object(c.time,'monotonic',return_value=130.),self.assertRaises(ValueError):cap.begin_admission('own-vanilla.service')
 def test_partial_record_tail_is_reported_not_invented(self):
  c=self.module();raw=HEADER+record()+record()[:20]
  self.assertEqual(c.complete_boundary(raw),dict(offset=54,observed_bytes=len(raw),pending_bytes=20))
  for bad in (b'bad',HEADER+struct.pack('<IIII',1,1000000,14,14)+b'x'*14,HEADER+struct.pack('<IIII',1,0,262145,262145)):
   with self.assertRaises(ValueError):c.complete_boundary(bad)
 def test_cuts_retain_header_and_exact_chosen_records_not_outcome_selection(self):
  c=self.module();raw=HEADER+record(b'a'*14)+record(b'b'*14)+record(b'c'*14)
  self.assertEqual(c.phase_bytes(raw,54,84),HEADER+record(b'b'*14))
  for start,end in [(25,84),(54,85),(84,54),(0,54),(54,999)]:
   with self.subTest(start=start,end=end),self.assertRaises(ValueError):c.phase_bytes(raw,start,end)
 def test_end_before_600_seconds_cannot_be_complete(self):
  c=self.module()
  with tempfile.TemporaryDirectory()as directory:
   cap,before=self.cap(directory);cap.stage='FOUR_ROLES';cap.post_started=110.;cap.post_start=24
   with patch.object(c.time,'monotonic',return_value=709.99),self.assertRaises(ValueError):cap.gameplay_complete()
   self.assertFalse(cap.complete)
 def test_missing_original_still_stops_own_capture_and_retains_pcap(self):
  c=self.module();import owned_sync_capture as base
  with tempfile.TemporaryDirectory()as directory:
   cap,before=self.cap(directory);cap.process=Mock();cap.process.poll.return_value=None;cap.process.wait.return_value=0;cap.signal_group=Mock()
   cap.pcap.write_bytes(HEADER+record());cap.log.write_text('1 packet captured\n1 packet received by filter\n0 packets dropped by kernel\n')
   with patch.object(c,'observe_three_roles',return_value=before),patch.object(base.time,'monotonic',return_value=110.):
    with self.assertRaises(RuntimeError):cap.close()
   cap.process.wait.assert_called_once_with(timeout=10)
   self.assertIn('pcap_sha256',cap.receipt);self.assertFalse(cap.receipt['protocol_complete'])
   self.assertEqual(cap.receipt['missing_pairs'],['A_Original','B_Original'])
 def test_new_exec_helper_checks_real_three_binding_before_exec(self):
  c=self.module();import owned_latejoin_capture_exec as helper
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);binding=fixture()['binding_before'];registry={r:{'identity':v['identity'],'unit':v['unit']}for r,v in binding.items()}
   config=root/'config.json';c.exclusive_json(config,dict(protocol=c.PROTOCOL,source_pins={},registry=registry,binding=binding,owner_path=str(root/'owned-sync-owner.json')))
   with patch.object(helper,'RUNTIME_REVIEWED',True),patch.object(helper,'observe_three_roles',return_value=binding),patch.object(helper,'read_start',return_value=77),patch.object(helper.resource,'setrlimit'),patch.object(helper.os,'execv',side_effect=RuntimeError('exec boundary'))as execute:
    with self.assertRaisesRegex(RuntimeError,'exec boundary'):helper.main(config)
    execute.assert_called_once();(root/'owned-sync-owner.json').unlink()
    bad=copy.deepcopy(binding);bad['botA']['ports'][0][1]+=1
    with patch.object(helper,'observe_three_roles',return_value=bad),self.assertRaises(ValueError):helper.main(config)
 def test_prejoin_difference_cannot_be_hidden_by_a_clean_fixed_postjoin_cut(self):
  c=self.module();from test_analyze_retail_sync_pcap import capture,packet
  with tempfile.TemporaryDirectory()as directory:
   cap,_=self.cap(directory);cap.stage='FOUR_ROLES';cap.ports.update(vanilla=30003)
   before=capture(packet(30001,destination=27850),packet(30002,crc=999,destination=27850))
   after=capture(*(packet(p,tick=2,destination=27850)for p in (30001,30002,30003)))
   cap.pcap.write_bytes(before+after[24:]);cap.post_start=len(before);cap.post_end=cap.pcap.stat().st_size
   with self.assertRaisesRegex(ValueError,'full capture differs'):cap.run_audits()
   self.assertEqual(cap.receipt['pair_audits']['A_B']['differing_pairs'],1)
 def test_prejoin_missing_original_remains_visible_and_postjoin_decoder_is_strict(self):
  c=self.module();from test_analyze_retail_sync_pcap import capture,packet
  with tempfile.TemporaryDirectory()as directory:
   cap,_=self.cap(directory);cap.stage='FOUR_ROLES';cap.ports.update(vanilla=30003)
   before=capture(packet(30001,destination=27850),packet(30002,destination=27850))
   for peers in ((30001,30002,30003),(30001,30002)):
    after=capture(*(packet(p,tick=2,destination=27850)for p in peers));cap.pcap.write_bytes(before+after[24:]);cap.post_start=len(before);cap.post_end=cap.pcap.stat().st_size
    if len(peers)==3:
     cap.run_audits();self.assertTrue(cap.comparison_complete())
     self.assertEqual(cap.receipt['pair_audits']['A_Original']['status'],'INCOMPLETE_SAMPLED_COMPARISON')
    else:
     with self.assertRaisesRegex(ValueError,'missing postjoin pair'):cap.run_audits()
     self.assertFalse(cap.comparison_complete())
 def test_real_three_fd_reader_uses_same_twice_bound_socket_observations(self):
  c=self.module();import owned_sync_capture as base
  from test_owned_sync_capture import udp
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);proc=root/'proc';arena=root/'arena';arena.mkdir()
   (proc/'1/ns').mkdir(parents=True);(proc/'1/ns/net').write_text('host')
   ns=root/'namespace';ns.write_text('own');registry={}
   table='header\n'+''.join(udp(p,i)+'\n'for p,i in [(27850,200),(27851,250),(30001,201),(30002,202)])
   for i,role in enumerate(('server','botA','botB')):
    pid=100+i;p=proc/str(pid);(p/'fd').mkdir(parents=True);(p/'ns').mkdir();(p/'net').mkdir();(arena/role).mkdir()
    (p/'cwd').symlink_to(arena/role);(p/'ns/net').hardlink_to(ns);unit='own-'+role+'.service'
    (p/'comm').write_text('DedicatedServer'if role=='server'else'SeriousSam.exe');(p/'cgroup').write_text('0::/system.slice/'+unit+'\n')
    (p/'net/udp').write_text(table);(p/'net/udp6').write_text('header\n')
    for index,inode in enumerate([200,250]if role=='server'else[200+i]):(p/'fd'/str(index)).symlink_to('socket:[%d]'%inode)
    registry[role]=dict(identity=[pid,1000+i],unit=unit)
   def fake_path(value):
    value=str(value);return proc/value.removeprefix('/proc/').removeprefix('/proc')if value.startswith('/proc')else Path(value)
   with patch.object(base,'Path',side_effect=fake_path),patch.object(base,'ARENA',arena),patch.object(base,'read_start',side_effect=lambda pid:1000+pid-100):
    rows=c.observe_three_roles(registry);self.assertEqual(rows['botB']['ports'],[[30002,202]])
    with self.assertRaises(ValueError):base.observe_roles(registry)
    (proc/'102/fd/0').unlink()
    with self.assertRaises(ValueError):c.observe_three_roles(registry)


if __name__=='__main__':unittest.main()
