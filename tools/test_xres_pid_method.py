"""Pure and fake-C tests only; no X server or native library is loaded."""
import copy
import importlib
import unittest


def fixture():
 identities={role:dict(pid=pid,start_ticks=pid*10,argv=[role,':167'],display=':167',pid_namespace='pid:[123]')for role,pid in [('display',100),('driver',101),('peer',102),('attributor',103)]}
 resources=[dict(role='driver',connection_index=0,resource=0x200001),dict(role='driver',connection_index=1,resource=0x400001),dict(role='peer',connection_index=0,resource=0x600001)]
 expected=dict(pid_namespace='pid:[123]',identities=identities,resources=resources)
 clients=[dict(resource_base=base,resource_mask=0x1fffff)for base in(0x200000,0x400000,0x600000,0x800000)]
 results=[]
 for resource in resources:
  base=resource['resource']&~0x1fffff
  for kind,xid in [('resource',resource['resource']),('base',base)]:
   results.append(dict(requested_kind=kind,requested_xid=xid,query_status=0,num_ids=1,ids=[dict(spec_client=base,mask=2,length=4,pid=identities[resource['role']]['pid'])]))
 snapshot=dict(index=0,monotonic_started=10.,monotonic_finished=10.1,parent_started=9.9,parent_finished=10.2,ipc_request_serial=2,xres_version=[1,2],query_clients_status=1,clients=clients,results=results,errors=[],free_counts=dict(client_arrays_allocated=1,client_arrays_freed=1,id_arrays_allocated=6,id_arrays_freed=6),process_before=copy.deepcopy(identities),process_after=copy.deepcopy(identities))
 return snapshot,expected


class Policy(unittest.TestCase):
 def module(self):return importlib.import_module('xres_pid_method')
 def test_success_zero_and_exact_resource_base_pid_pairs(self):
  s,e=fixture();r=self.module().validate_snapshot(s,e)
  self.assertEqual(r['matched_connections'],3);self.assertEqual(r['pid_rows'],6)
  self.assertEqual(r['resource_bases'],[0x200000,0x400000,0x600000])
  self.assertFalse(r['continuous_client_lifetime_proven']);self.assertFalse(r['historical_u_attributed'])
 def test_empty_ids_wrong_status_mask_length_and_foreign_spec_rejected(self):
  for key,value in [('query_status',1),('num_ids',0),('num_ids',True),('ids',[])]:
   with self.subTest(key=key,value=value):
    s,e=fixture();s['results'][0][key]=value
    with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
  for key,value in [('pid',-1),('pid',0),('pid',True),('pid',102),('mask',3),('mask',True),('length',8),('length',True),('spec_client',0x600001)]:
   with self.subTest(key=key,value=value):
    s,e=fixture();s['results'][0]['ids'][0][key]=value
    with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
 def test_64_client_bound_and_ambiguous_or_missing_range_rejected(self):
  for kind in('65','missing','duplicate','badmask'):
   with self.subTest(kind=kind):
    s,e=fixture()
    if kind=='65':s['clients']*=17
    elif kind=='missing':s['clients'].pop(0)
    elif kind=='duplicate':s['clients'].append(copy.deepcopy(s['clients'][0]))
    else:s['clients'][0]['resource_mask']=True
    with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
 def test_both_resource_and_base_exactly_six_queries_no_pid_or_order_fallback(self):
  for kind in('missing','extra','swap','samebase','kind','resource'):
   with self.subTest(kind=kind):
    s,e=fixture()
    if kind=='missing':s['results'].pop()
    elif kind=='extra':s['results'].append(copy.deepcopy(s['results'][0]))
    elif kind=='swap':s['results'][0],s['results'][2]=s['results'][2],s['results'][0]
    elif kind=='samebase':e['resources'][1]['resource']=e['resources'][0]['resource']+1
    elif kind=='kind':s['results'][0]['requested_kind']='base'
    else:s['results'][0]['requested_xid']+=1
    with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
 def test_wrong_pid_namespace_start_or_role_before_after_is_rejected(self):
  for section in('process_before','process_after'):
   for key,value in [('pid',999),('start_ticks',999),('start_ticks',True),('pid_namespace','pid:[987]'),('display',':154'),('argv',['foreign'])]:
    with self.subTest(section=section,key=key):
     s,e=fixture();s[section]['driver'][key]=value
     with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
  s,e=fixture();e['identities']['display']['pid_namespace']='pid:[987]'
  with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
 def test_version_error_or_incomplete_array_free_cannot_pass(self):
  for key,value in [('xres_version',[1,1]),('xres_version',[True,2]),('errors',['native X error']),('query_clients_status',0)]:
   with self.subTest(key=key):
    s,e=fixture();s[key]=value
    with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
  for key in('client_arrays_freed','id_arrays_freed'):
   s,e=fixture();s['free_counts'][key]-=1
   with self.assertRaises(ValueError):self.module().validate_snapshot(s,e)
 def test_two_snapshots_need_distinct_actual_serial_and_ordered_clocks(self):
  first,e=fixture();second=copy.deepcopy(first)
  second.update(index=1,monotonic_started=11.,monotonic_finished=11.1,parent_started=10.9,parent_finished=11.2,ipc_request_serial=3)
  row=dict(errors=[],expected=e,snapshots=[first,second],children={role:dict(closed=True,reaped=True,forced=False,errors=[],exit_code=0)for role in e['identities']},display_absent=True,native_closed=True,inputs_emitted=0,tse_started=False,xrecord_started=False)
  self.assertEqual(self.module().method_verdict(row)['status'],'PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY')
  for flag in('historical_u_attributed','continuous_client_lifetime_proven','a1_pass','retail_qualified'):
   changed=copy.deepcopy(row);changed[flag]=True;self.assertEqual(self.module().method_verdict(changed)['status'],'FAIL_METHOD_XRES_PID_EVIDENCE')
  for key,value in [('index',0),('index',True),('ipc_request_serial',2),('monotonic_started',9.),('monotonic_finished',float('nan')),('parent_finished',10.)]:
   with self.subTest(key=key,value=value):
    changed=copy.deepcopy(row);changed['snapshots'][1][key]=value
    self.assertEqual(self.module().method_verdict(changed)['status'],'FAIL_METHOD_XRES_PID_EVIDENCE')


class Native(unittest.TestCase):
 def module(self):return importlib.import_module('xres_pid_worker')
 def fake(self,*,count=4,id_count=1,id_length=4,id_mask=2,null_value=False,status=0):
  import ctypes as C
  from types import SimpleNamespace
  m=self.module();n=m.Native.__new__(m.Native);n.errors=[];n.total_free_counts={};calls=[]
  clients=(m.Client*max(4,count))(*[m.Client(v,0x1fffff)for v in(0x200000,0x400000,0x600000,0x800000)])
  values=[];payload=[]
  def query_clients(d,num,out):
   calls.append('clients');num._obj.value=count;C.cast(out,C.POINTER(C.POINTER(m.Client)))[0]=C.cast(clients,C.POINTER(m.Client));return 1
  def query_ids(d,num,spec,nids,out):
   calls.append('ids');base=spec._obj.client&~0x1fffff;pid=102 if base==0x600000 else 101
   data=C.c_uint32(pid);payload.append(data);arr=(m.Value*max(1,id_count))();values.append(arr)
   for v in arr:v.spec=m.Spec(base,id_mask);v.length=id_length;v.value=None if null_value else C.cast(C.pointer(data),C.c_void_p)
   nids._obj.value=id_count;C.cast(out,C.POINTER(C.POINTER(m.Value)))[0]=C.cast(arr,C.POINTER(m.Value));return status
  n.x=SimpleNamespace(XFree=lambda p:calls.append('free_clients'))
  n.r=SimpleNamespace(XResQueryClients=query_clients,XResQueryClientIds=query_ids,XResGetClientPid=lambda p:C.cast(p.contents.value,C.POINTER(C.c_uint32)).contents.value,XResClientIdsDestroy=lambda num,p:calls.append(('free_ids',num)))
  return n,calls
 def test_fake_c_snapshot_frees_every_return_array_and_reads_card32(self):
  n,calls=self.fake();s=n.snapshot(123,[0x200001,0x400001,0x600001],[1,2])
  self.assertEqual(calls.count('clients'),1);self.assertEqual(calls.count('free_clients'),1)
  self.assertEqual(calls.count('ids'),6);self.assertEqual(calls.count(('free_ids',1)),6)
  self.assertEqual([v['ids'][0]['pid']for v in s['results']],[101,101,101,101,102,102])
 def test_count_status_mask_length_null_fail_before_pid_read_but_free(self):
  for kw in(dict(count=65),dict(id_count=0),dict(id_count=2),dict(id_length=8),dict(id_mask=3),dict(null_value=True),dict(status=1)):
   with self.subTest(kw=kw):
    n,calls=self.fake(**kw);n.r.XResGetClientPid=lambda p:self.fail('invalid payload must not reach native PID getter')
    with self.assertRaises(ValueError):n.snapshot(123,[0x200001,0x400001,0x600001],[1,2])
    self.assertEqual(calls.count('free_clients'),1)
    if 'count'not in kw:self.assertEqual(sum(isinstance(v,tuple)and v[0]=='free_ids'for v in calls),1)
 def test_destroy_failure_sticky_and_original_payload_error_preserved(self):
  n,calls=self.fake(id_length=8)
  def bad_free(*args):raise OSError('fake destroy failure')
  n.r.XResClientIdsDestroy=bad_free
  with self.assertRaisesRegex(ValueError,'mask/length'):n.snapshot(123,[0x200001,0x400001,0x600001],[1,2])
  self.assertEqual(n.total_free_counts.get('id_arrays_freed',0),0);self.assertTrue(n.errors)
 def test_resource_partial_open_and_close_are_idempotent_and_continue(self):
  from types import SimpleNamespace
  m=self.module();calls=[];opened=[]
  def op():opened.append(len(opened)+1);return opened[-1]
  def create(d,*args):return 0 if d==2 else 0x200001
  n=SimpleNamespace(open=op,check=lambda:None,x=SimpleNamespace(XDefaultRootWindow=lambda d:1,XCreateSimpleWindow=create,XSync=lambda *args:1,XDestroyWindow=lambda d,w:calls.append(('destroy',d)),XCloseDisplay=lambda d:calls.append(('close',d))))
  owner=m.Resources(n,2)
  with self.assertRaises(ValueError):owner.initialize()
  first=owner.close();self.assertIs(first,owner.close());self.assertEqual(calls,[('destroy',1),('close',1),('close',2)]);self.assertTrue(first['connections_closed'])
 def test_native_gates_before_loading_and_root_c_layout_matches_declarations(self):
  from unittest.mock import patch
  m=self.module()
  with patch.object(m.C,'CDLL',side_effect=AssertionError('must not load')):
   with self.assertRaisesRegex(RuntimeError,'disabled'):m.Native()
  layout=m.abi_layout();self.assertEqual(layout['XID'],8);self.assertEqual(layout['Spec']['size'],16);self.assertEqual(layout['Value']['size'],32)
 def test_failure_retains_actual_alloc_free_totals_for_closed_receipt(self):
  n,calls=self.fake(id_length=8)
  with self.assertRaises(ValueError):n.snapshot(123,[0x200001,0x400001,0x600001],[1,2])
  self.assertEqual(n.total_free_counts,dict(client_arrays_allocated=1,client_arrays_freed=1,id_arrays_allocated=1,id_arrays_freed=1))


if __name__=='__main__':unittest.main()
