"""Pure lifecycle/PID fixtures only; no native calls or real process identities."""
import copy
import importlib
import struct
import unittest


def fixture():
 identities={role:dict(pid=pid,start_ticks=pid*10,pid_namespace='pid:[123]',display=':154')for role,pid in(('parent',100),('recorder',101),('display',102),('vanilla',103))}
 expected=dict(xtest_opcode=137,identities=identities,pid_namespace='pid:[123]',resources={'controller_transport':0x200001,'original_window_owner':0x400001})
 bindings={'controller_transport':0x200000,'original_window_owner':0x400000}
 rows=[dict(callback_serial=i+1,category=cat,kind=kind,client_base=base,client_sequence=i,server_time=100+i,received_monotonic=10.+i/10,wire_hex='')for i,(cat,kind,base)in enumerate([(4,'start',0),(1,'query_pointer_request',0x600000),(1,'warp_request',0x600000),(5,'end',0)])]
 for row in rows:row['client_swapped']=False
 rows[1]['wire_hex']=struct.pack('<BBHI',38,0,2,0x100).hex()
 warp=bytearray(24);struct.pack_into('<BBH',warp,0,41,0,6);rows[2]['wire_hex']=warp.hex()
 clients=[dict(resource_base=x,resource_mask=0x1fffff)for x in(0,0x200000,0x400000,0x600000,0x800000)]
 queries=[]
 for base,pid in((0x200000,100),(0x400000,103),(0x600000,103)):
  queries.append(dict(requested_kind='base',requested_xid=base,query_status=0,num_ids=1,ids=[dict(spec_client=base,mask=2,length=4,pid=pid)]))
 for kind,pid in(('controller_transport',100),('original_window_owner',103)):
  queries.append(dict(requested_kind=kind,requested_xid=expected['resources'][kind],query_status=0,num_ids=1,ids=[dict(spec_client=bindings[kind],mask=2,length=4,pid=pid)]))
 snaps=[]
 for i in range(2):
  snaps.append(dict(index=i,record_enabled=True,lifecycle_coverage=dict(client_started=True,client_died=True),bindings=bindings,context_clients=[2,0x200000,0x400000,0x600000],clients=clients,queries=copy.deepcopy(queries),xres_version=[1,2],query_clients_status=1,process_before=copy.deepcopy(identities),process_after=copy.deepcopy(identities),monotonic_started=10.05+i*.2,monotonic_finished=10.06+i*.2,callback_serial_before=1 if i==0 else 3,callback_serial_after=1 if i==0 else 3,free_counts=dict(client_arrays_allocated=1,client_arrays_freed=1,id_arrays_allocated=5,id_arrays_freed=5),errors=[]))
 native=dict(lifecycle_verified=True,calls=4,freed=4,records=4,start_count=1,end_count=1,malformed=0,dropped=0,budget_failed=False,end_verified=True,context_freed=True,connections_closed=True,errors=[],cleanup_errors=[])
 return rows,snaps,expected,native


def birth(base):
 wire=bytearray(40);struct.pack_into('<BBHHH',wire,0,1,0,11,0,8);struct.pack_into('<II',wire,12,base,0x1fffff)
 return dict(category=2,kind='client_started',client_base=base,client_sequence=0,server_time=101,received_monotonic=10.15,client_swapped=False,wire_hex=wire.hex())


class Evidence(unittest.TestCase):
 def module(self):return importlib.import_module('a1_xres_attribution_evidence')
 def check(self,*args):return self.module().attribute(*args)
 def test_two_snapshots_and_complete_lifecycle_bind_only_current_original_requests(self):
  r=self.check(*fixture());self.assertEqual(r['own_original_request_rows'],2);self.assertEqual(r['original_bases'],[0x400000,0x600000]);self.assertFalse(r['old_u_attributed']);self.assertFalse(r['gain_fixed'])
 def test_same_pid_after_base_died_and_started_is_unknown_not_interval_proof(self):
  rows,s,e,n=fixture();rows.insert(2,dict(category=3,kind='client_died',client_base=0x600000,client_sequence=2,server_time=101,client_swapped=False,wire_hex=''));rows.insert(3,birth(0x600000))
  for i,row in enumerate(rows):row['callback_serial']=i+1;row.setdefault('received_monotonic',10.15)
  n.update(calls=6,freed=6,records=6);s[1]['callback_serial_before']=s[1]['callback_serial_after']=5
  r=self.check(rows,s,e,n);self.assertNotIn(0x600000,r['original_bases']);self.assertEqual(r['own_original_request_rows'],0);self.assertEqual(r['unknown_request_rows'],2)
 def test_missing_disabled_flags_or_end_drain_never_become_interval_proof(self):
  for change in('flags','native','end','free','drop','serial','outside_arm','outside_stop'):
   with self.subTest(change=change):
    rows,s,e,n=fixture()
    if change=='flags':s[0]['lifecycle_coverage']['client_died']=False
    elif change=='native':n['lifecycle_verified']=False
    elif change=='end':rows[-1]['kind']='warp_request'
    elif change=='free':n['freed']=3
    elif change=='drop':n['dropped']=1
    elif change=='serial':rows[1]['callback_serial']=3
    elif change=='outside_arm':s[0]['callback_serial_before']=0
    else:s[1]['callback_serial_after']=4
    with self.assertRaises(ValueError):self.check(rows,s,e,n)
 def test_pid_tid_start_namespace_changes_cannot_be_original(self):
  for key,value in(('pid',999),('start_ticks',1040),('pid_namespace','pid:[456]')):
   rows,s,e,n=fixture();s[1]['process_after']['vanilla'][key]=value
   with self.assertRaises(ValueError):self.check(rows,s,e,n)
  rows,s,e,n=fixture();s[0]['queries'][2]['ids'][0]['pid']=999;s[1]['queries'][2]['ids'][0]['pid']=999
  r=self.check(rows,s,e,n);self.assertEqual(r['own_original_request_rows'],0);self.assertEqual(r['unknown_request_rows'],2)
 def test_snapshot_only_unknown_new_or_changed_pid_no_fallback(self):
  rows,s,e,n=fixture();s[1]['queries'][2]['ids'][0]['pid']=104
  self.assertEqual(self.check(rows,s,e,n)['own_original_request_rows'],0)
  rows,s,e,n=fixture();s[0]['queries'].pop(2);s[0]['context_clients'].remove(0x600000);s[0]['free_counts'].update(id_arrays_allocated=4,id_arrays_freed=4)
  self.assertEqual(self.check(rows,s,e,n)['own_original_request_rows'],0)
 def test_query_status_count_length_mask_arrays_and_resource_owner_are_strict(self):
  for key,value in(('query_status',1),('num_ids',0),('requested_xid',0)):
   rows,s,e,n=fixture();s[0]['queries'][0][key]=value
   with self.assertRaises(ValueError):self.check(rows,s,e,n)
  for key,value in(('pid',0),('pid',True),('mask',3),('length',8),('spec_client',0x800000)):
   rows,s,e,n=fixture();s[0]['queries'][0]['ids'][0][key]=value
   with self.assertRaises(ValueError):self.check(rows,s,e,n)
  rows,s,e,n=fixture();s[0]['queries'][-1]['ids'][0]['pid']=100
  with self.assertRaises(ValueError):self.check(rows,s,e,n)
 def test_32_targets_34_queries_64_clients_and_ambiguous_zero_ranges_fail_closed(self):
  for kind in('65clients','33targets','duplicate','overlap','free','version','enabled','extra_query'):
   rows,s,e,n=fixture()
   if kind=='65clients':s[0]['clients']*=14
   elif kind=='33targets':s[0]['context_clients']=[2]+[i*0x200000 for i in range(1,34)]
   elif kind=='duplicate':s[0]['clients'].append(copy.deepcopy(s[0]['clients'][0]))
   elif kind=='overlap':s[0]['clients'][0]['resource_mask']=0xffffffff
   elif kind=='free':s[0]['free_counts']['id_arrays_freed']-=1
   elif kind=='version':s[0]['xres_version']=[1,1]
   elif kind=='enabled':s[0]['record_enabled']=False
   else:s[0]['queries'].append(copy.deepcopy(s[0]['queries'][0]))
   with self.subTest(kind=kind),self.assertRaises(ValueError):self.check(rows,s,e,n)
 def test_snapshots_must_also_be_inside_same_worker_callback_monotonic_interval(self):
  for key,value in(('monotonic_started',9.99),('monotonic_finished',10.31)):
   rows,s,e,n=fixture();s[0 if key=='monotonic_started'else 1][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):self.check(rows,s,e,n)
 def test_missing_native_client_swapped_type_is_not_inferred(self):
  rows,s,e,n=fixture();rows[1].pop('client_swapped')
  with self.assertRaises(ValueError):self.check(rows,s,e,n)
 def test_separate_own167_method_can_use_driver_resources_without_relaxing_a1(self):
  rows,s,e,n=fixture();e['scope']='OWN_METHOD_167';e['resource_roles']={'controller_transport':'vanilla','original_window_owner':'vanilla'}
  for pin in e['identities'].values():pin['display']=':167'
  for snap in s:
   snap['process_before']=copy.deepcopy(e['identities']);snap['process_after']=copy.deepcopy(e['identities']);snap['queries'][0]['ids'][0]['pid']=103;snap['queries'][-2]['ids'][0]['pid']=103
  self.assertEqual(self.check(rows,s,e,n)['own_original_request_rows'],2)
  e['scope']='A1_154'
  with self.assertRaises(ValueError):self.check(rows,s,e,n)
 def test_unvalidated_started_wire_cannot_hide_same_base_generation_boundary(self):
  rows,s,e,n=fixture();b=birth(0x600000);b['wire_hex']='00000000';rows.insert(2,b)
  for i,row in enumerate(rows):row['callback_serial']=i+1
  n.update(calls=5,freed=5,records=5);s[1]['callback_serial_before']=s[1]['callback_serial_after']=4
  with self.assertRaises(ValueError):self.check(rows,s,e,n)


if __name__=='__main__':unittest.main()
