"""Own-method controller models, no native/display/Xlib execution."""
import copy
import hashlib
import importlib
import json
import struct
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_a1_xres_attribution_evidence import fixture,birth


def method_fixture(*,driver_requests=True):
 rows,s,e,n=fixture();e['scope']='OWN_METHOD_167';e['resource_roles']={'controller_transport':'vanilla','original_window_owner':'vanilla'}
 e['identities']={role:dict(pid=pid,start_ticks=pid*10,display=':167',pid_namespace='pid:[123]')for role,pid in(('parent',99),('display',100),('vanilla',101),('recorder',103))}
 for snap in s:
  snap['process_before']=copy.deepcopy(e['identities']);snap['process_after']=copy.deepcopy(e['identities'])
  for query in snap['queries']:
   base=query['ids'][0]['spec_client'];query['ids'][0]['pid']=103 if base==0x600000 else 101
  snap['monotonic_started']=10.05+snap['index']*.1;snap['monotonic_finished']=10.06+snap['index']*.1
  snap['callback_serial_before']=snap['callback_serial_after']=snap['index']+1
 peer_query=dict(requested_kind='base',requested_xid=0x800000,query_status=0,num_ids=1,ids=[dict(spec_client=0x800000,mask=2,length=4,pid=102)])
 s[1]['context_clients'].append(0x800000);s[1]['queries'].insert(3,peer_query);s[1]['free_counts'].update(id_arrays_allocated=6,id_arrays_freed=6)
 started=birth(0x800000);started.update(callback_serial=2,received_monotonic=10.1)
 died=dict(callback_serial=3,category=3,kind='client_died',client_base=0x800000,client_sequence=2,server_time=102,received_monotonic=10.2,wire_hex='',client_swapped=False)
 rows=[rows[0],started,died,rows[-1]]
 if driver_requests:
  request=dict(category=1,kind='query_pointer_request',client_base=0x200000,client_sequence=7,server_time=102,received_monotonic=10.12,client_swapped=False,wire_hex=struct.pack('<BBHI',38,0,2,0x200001).hex())
  wire=bytearray(32);struct.pack_into('<BBHII',wire,0,1,1,7,0,0x100);struct.pack_into('<hh',wire,16,400,300)
  reply=dict(category=0,kind='query_pointer_reply',client_base=0x200000,client_sequence=7,server_time=102,received_monotonic=10.13,client_swapped=False,wire_hex=wire.hex())
  rows[2:2]=[request,reply];s[1]['callback_serial_before']=s[1]['callback_serial_after']=4
 for i,row in enumerate(rows):row['callback_serial']=i+1
 n.update(calls=len(rows),freed=len(rows),records=len(rows))
 return rows,dict(expected=e,snapshots=s,attempts=[{},{}],errors=[]),n


class Method(unittest.TestCase):
 def module(self):return importlib.import_module('a1_xres_lifecycle_method')
 def run_fake(self,directory,*,bad_peer=False,peer_init_error=False,capture_error=False,driver_requests=True,bad_query=False):
  m=self.module();events=[];kids=[];root=Path(directory)
  class Child:
   def __init__(self,argv,directory,display,*,ttl,role):
    self.role=role;self.serial=0;self.identity=dict(pid={'display':100,'driver':101,'peer':102,'recorder':103}[role],start_ticks={'display':1000,'driver':1010,'peer':1020,'recorder':1030}[role],argv=argv,display=display);kids.append(self);events.append((role,'start'))
   def guard(self):pass
   def call(self,command,*,timeout,**fields):
    self.serial+=1;events.append((self.role,command));self.assert_timeout=timeout
    if self.role=='peer'and peer_init_error:raise OSError('peer partial init')
    if command=='capture_final'and capture_error:raise TimeoutError('bounded capture RPC failure')
    if command=='initialize':value=dict(resources=[0x200001,0x400001]if self.role=='driver'else[0x800001],mapped=False,inputs_emitted=0)
    elif command=='query':value=dict(window=0x200001,sequence=99 if bad_query else 7,position=[400,300],root=0x100)
    else:value=dict(lifecycle_verified=True)
    return dict(id=self.serial,ok=True,value=value)
   def cleanup(self,**kwargs):
    events.append((self.role,'close'));native=dict(errors=[],inputs_emitted=0,connections_closed=True)
    if self.role=='recorder':
     rows,metadata,native=method_fixture(driver_requests=driver_requests)
     if bad_peer:rows[-2]['client_base']=0xa00000
     wire=b''.join((json.dumps(r)+'\n').encode()for r in rows);(root/'record-raw.jsonl').write_bytes(wire)
     side=json.dumps(metadata).encode();(root/'xres-attribution.json').write_bytes(side);native['xres_evidence']=dict(path='xres-attribution.json',bytes=len(side),sha256=hashlib.sha256(side).hexdigest())
     (root/'recorder-native-close.json').write_text(json.dumps(native))
    elif self.role!='display':
     native.update(windows_created=2 if self.role=='driver'else 1,windows_destroyed=2 if self.role=='driver'else 1)
     (root/(self.role+'-native-close.json')).write_text(json.dumps(dict(errors=[],native=native,handler=dict(error_handler_restored=True,errors=[]))))
    return dict(role=self.role,identity=self.identity,closed=True,reaped=True,forced=False,exit_code=0,errors=[])
  with patch.object(m,'RUNTIME_REVIEWED',True),patch.object(m,'fresh_display_available'),patch.object(m,'wait_display'),patch.object(m,'guard_display'),patch.object(m,'display_absent',return_value=True),patch.object(m,'display_owner',return_value={}),patch.object(m,'self_identity',return_value=dict(pid=99,start_ticks=990)),patch.object(m,'role_identity',side_effect=lambda c:dict(c.identity,pid_namespace='pid:[123]')):
   result=m.execute(root,child_factory=Child)
  return result,events
 def test_one_bounded_peer_start_leave_with_driver_alive_through_end(self):
  with tempfile.TemporaryDirectory()as d:
   r,events=self.run_fake(d);self.assertEqual(r['status'],'PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY')
   self.assertLess(events.index(('recorder','arm')),events.index(('peer','start')))
   self.assertLess(events.index(('recorder','capture_final')),events.index(('peer','close')))
   self.assertLess(events.index(('peer','close')),events.index(('recorder','close')))
   self.assertLess(events.index(('recorder','close')),events.index(('driver','close')))
   self.assertTrue(r['lifecycle_started']);self.assertTrue(r['lifecycle_died']);self.assertFalse(r['a1_pass']);self.assertEqual(r['attribution']['own_original_request_rows'],2);self.assertTrue(r['driver_requests_bound']);self.assertTrue(r['peer_interval_unknown'])
   self.assertEqual(events.count(('driver','query')),1)
   self.assertLess(events.index(('recorder','arm')),events.index(('driver','query')))
   self.assertLess(events.index(('driver','query')),events.index(('recorder','capture_final')))
 def test_missing_matching_peer_died_or_partial_init_cannot_qualify_but_all_close(self):
  for kw in(dict(bad_peer=True),dict(peer_init_error=True)):
   with self.subTest(kw=kw),tempfile.TemporaryDirectory()as d:
    r,events=self.run_fake(d,**kw);self.assertNotEqual(r['status'],'PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY');self.assertEqual(sum(event=='close'for role,event in events),4)
 def test_disabled_method_before_any_path_read_or_process(self):
  with self.assertRaisesRegex(RuntimeError,'disabled'):self.module().run_method('/never-read')
 def test_capture_final_rpc_failure_still_closes_all_four_without_another_capture(self):
  with tempfile.TemporaryDirectory()as d:
   r,events=self.run_fake(d,capture_error=True);self.assertTrue(r['status'].startswith('FAIL'))
   self.assertEqual(events.count(('recorder','capture_final')),1);self.assertEqual(sum(event=='close'for role,event in events),4)
   self.assertLess(events.index(('recorder','close')),events.index(('driver','close')))
 def test_zero_bound_driver_requests_cannot_qualify_method(self):
  with tempfile.TemporaryDirectory()as d:
   r,events=self.run_fake(d,driver_requests=False);self.assertNotEqual(r['status'],'PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY')
 def test_driver_query_native_sequence_must_match_actual_selected_wire(self):
  with tempfile.TemporaryDirectory()as d:
   r,events=self.run_fake(d,bad_query=True);self.assertNotEqual(r['status'],'PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY')
 def test_method_query_reuses_qualified_read_body_and_allows_exactly_one(self):
  from types import SimpleNamespace
  from unittest.mock import Mock
  import xrecord_core_native as core
  m=self.module();self.assertIs(m.MethodNative.query,core.Native.query)
  obj=m.MethodDriver(SimpleNamespace(query=Mock(return_value={'sequence':7})),2)
  obj.initialized=True;obj.connections=[1,2];obj.windows=[0x200001,0x400001]
  self.assertEqual(obj.query(),{'sequence':7})
  with self.assertRaises(ValueError):obj.query()
  obj.n.query.assert_called_once_with(1,0x200001)


if __name__=='__main__':unittest.main()
