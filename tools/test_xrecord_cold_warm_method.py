"""Wire fixtures from Xproto.h/geproto.h; no display, Xlib or native process."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

BASE=0x200000;WINDOW=BASE+1;ROOT=0x51f;XTEST=132;GE=128


def extension(name):
 data=name.encode('ascii');size=8+(len(data)+3)//4*4
 return struct.pack('<BBHHH',98,0,size//4,len(data),0)+data+b'\0'*(size-8-len(data))


def reply(sequence):
 raw=bytearray(32);raw[0]=1;struct.pack_into('<H',raw,2,sequence);return raw


def fixture():
 rows=[]
 def add(kind,category,seq,wire,client=BASE,**fields):
  rows.append(dict(category=category,client_base=client,client_sequence=seq,server_time=1000+len(rows),client_swapped=False,wire_hex=bytes(wire).hex(),kind=kind,callback_serial=len(rows)+1,received_monotonic=1.+len(rows)*.001,**fields))
 add('start',4,0,b'',client=0)
 for seq,name,opcode in [(26,'XInputExtension',131),(27,'XTEST',XTEST),(28,'Generic Event Extension',GE)]:
  add('query_extension_request',1,seq,extension(name),extension_name=name)
  raw=reply(seq);raw[8:12]=bytes([1,opcode,0,0]);add('query_extension_reply',0,seq,raw,extension_name=name,present=True,major_opcode=opcode,first_event=0,first_error=0,request_sequence=seq)
 raw=struct.pack('<BBHHH',GE,0,2,1,0);add('ge_version_request',1,29,raw,major_version=1,minor_version=0)
 raw=reply(29);struct.pack_into('<HH',raw,8,1,0);add('ge_version_reply',0,29,raw,major_version=1,minor_version=0,request_sequence=29)
 for seq,x in [(30,412),(33,424)]:
  raw=bytearray(36);raw[:6]=struct.pack('<BBHBB',XTEST,2,9,6,1);struct.pack_into('<hh',raw,24,12,0)
  add('xtest_relative_motion',1,seq,raw,dx=12,dy=0,requested_device=0)
  for client,kind in [(0,'device_motion'),(BASE,'delivered_motion')]:
   raw=bytearray(32);raw[0]=6;struct.pack_into('<III',raw,4,1010,ROOT,WINDOW);struct.pack_into('<hh',raw,20,x,300)
   add(kind,0,0,raw,client=client,root_x=x,root_y=300,originating_client=None,event_time=1010)
  query=seq+2;add('query_pointer_request',1,query,struct.pack('<BBHI',38,0,2,WINDOW))
  raw=reply(query);raw[1]=1;struct.pack_into('<I',raw,8,ROOT);struct.pack_into('<hh',raw,16,x,300)
  add('query_pointer_reply',0,query,raw,root_x=x,root_y=300,same_screen=True,request_sequence=query)
 add('end',5,0,b'',client=0)
 attempts=[dict(function='XTestFakeRelativeMotionEvent',arguments=[123,12,0,0],started_monotonic=2.+i,finished_monotonic=2.1+i,return_value=1,native_invoked=True,sequence_before=interval[0],sequence_after=interval[1],sequence_interval=interval)for i,interval in enumerate([[26,31],[33,34]])]
 driver=dict(window=WINDOW,root=ROOT,queries=[dict(window=WINDOW,root=ROOT,position=[x,300],sequence=seq,attempt=attempt)for x,seq,attempt in zip([412,424],[32,35],attempts)])
 return rows,driver


class WireMethod(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('xrecord_cold_warm_method'),'missing cold/warm wire auditor')
  return importlib.import_module('xrecord_cold_warm_method')
 def test_full_cold_and_warm_wire_proof_required_not_only_counter_span(self):
  m=self.module();rows,driver=fixture();answer=m.bind_trace(rows,driver)
  self.assertTrue(answer['request_client_bound']);self.assertEqual(answer['cold_sequence_interval'],[26,31]);self.assertEqual(answer['warm_sequence_interval'],[33,34])
  self.assertEqual(answer['cold_requests'],['QueryExtension:XInputExtension','QueryExtension:XTEST','QueryExtension:Generic Event Extension','GEQueryVersion','XTEST:RelativeMotion'])
  self.assertEqual(answer['query_positions'],[[412,300],[424,300]]);self.assertFalse(answer['xi2_complete']);self.assertFalse(answer['a1_pass'])
 def test_query_counter_must_follow_emission_and_precede_next_emission(self):
  m=self.module()
  for sequence in(25,34):
   with self.subTest(sequence=sequence):
    rows,driver=fixture();driver['queries'][0]['sequence']=sequence
    for row in rows:
     if row['kind']=='query_pointer_request'and row['client_sequence']==32:row['client_sequence']=sequence
     elif row['kind']=='query_pointer_reply'and row['request_sequence']==32:
      row['client_sequence']=sequence;row['request_sequence']=sequence
      raw=bytearray.fromhex(row['wire_hex']);struct.pack_into('<H',raw,2,sequence);row['wire_hex']=raw.hex()
    for i,row in enumerate(rows):row['callback_serial']=i+1;row['received_monotonic']=1.+i*.001
    with self.assertRaises(ValueError):m.bind_trace(rows,driver)
 def test_query_callbacks_must_follow_native_request_and_finish_before_next(self):
  m=self.module()
  for position in('before_cold_fake','after_warm_fake'):
   with self.subTest(position=position):
    rows,driver=fixture();pair=[r for r in rows if r['kind']in('query_pointer_request','query_pointer_reply')and r['client_sequence']==32]
    rows=[r for r in rows if r not in pair]
    target=next(i for i,r in enumerate(rows)if r['kind']=='xtest_relative_motion'and r['client_sequence']==(30 if position=='before_cold_fake'else 33))
    offset=target if position=='before_cold_fake'else target+1;rows[offset:offset]=pair
    for i,row in enumerate(rows):row['callback_serial']=i+1;row['received_monotonic']=1.+i*.001
    with self.assertRaises(ValueError):m.bind_trace(rows,driver)
 def test_actual_invocation_and_counter_copies_must_match_interval_exactly(self):
  m=self.module()
  for key,value in(('native_invoked',False),('native_invoked',1),('sequence_before',25),('sequence_before',True),('sequence_after',99),('sequence_after',True)):
   with self.subTest(key=key,value=value):
    rows,driver=fixture();driver['queries'][0]['attempt'][key]=value
    with self.assertRaises(ValueError):m.bind_trace(rows,driver)
 def test_missing_reordered_changed_or_extra_metadata_cannot_pass(self):
  m=self.module()
  for change in('missing','order','wire_name','derived_name','extra_fake','reply_major','foreign_client','wrong_window','cold1','warm5','native_false','position','unanswered','extra_query'):
   with self.subTest(change=change):
    rows,driver=fixture()
    if change=='missing':rows.pop(1)
    elif change=='order':rows[1],rows[3]=rows[3],rows[1]
    elif change=='wire_name':rows[1]['wire_hex']=extension('XWrongExtension').hex()
    elif change=='derived_name':rows[1]['extension_name']='wrong'
    elif change=='extra_fake':rows.insert(-1,copy.deepcopy(rows[9]))
    elif change=='reply_major':rows[4]['major_opcode']=133
    elif change=='foreign_client':rows[1]['client_base']+=BASE
    elif change=='wrong_window':driver['window']+=1
    elif change=='cold1':driver['queries'][0]['attempt']['sequence_interval']=[30,31]
    elif change=='warm5':driver['queries'][1]['attempt']['sequence_interval']=[33,38]
    elif change=='native_false':driver['queries'][0]['attempt']['return_value']=0
    elif change=='position':driver['queries'][1]['position']=[412,300]
    elif change=='unanswered':rows.pop(2)
    elif change=='extra_query':
     request=copy.deepcopy(next(r for r in rows if r['kind']=='query_pointer_request'));answer=copy.deepcopy(next(r for r in rows if r['kind']=='query_pointer_reply'))
     request['client_sequence']=40;answer['client_sequence']=40;answer['request_sequence']=40
     raw=bytearray.fromhex(answer['wire_hex']);struct.pack_into('<H',raw,2,40);answer['wire_hex']=raw.hex();rows[-1:-1]=[request,answer]
    for i,row in enumerate(rows):row['callback_serial']=i+1;row['received_monotonic']=1.+i*.001
    with self.assertRaises(ValueError):m.bind_trace(rows,driver)
 def test_native_headers_parse_exact_offsets_and_reject_unmatched_reply(self):
  m=self.module();trace=m.MethodTrace(xtest_opcode=XTEST,ge_opcode=GE)
  request=dict(category=1,client_base=BASE,client_sequence=26,server_time=1,client_swapped=False,wire=extension('XInputExtension'))
  row=trace.accept(**request);self.assertEqual(row['extension_name'],'XInputExtension')
  raw=reply(26);raw[8:12]=bytes([1,131,100,101])
  row=trace.accept(**dict(request,category=0,wire=bytes(raw)))
  self.assertEqual((row['present'],row['major_opcode'],row['first_event'],row['first_error']),(True,131,100,101))
  with self.assertRaises(ValueError):trace.accept(**dict(request,category=0,wire=bytes(raw)))
 def test_metadata_big_endian_is_decoded_and_malformed_boundaries_fail(self):
  m=self.module();trace=m.MethodTrace(xtest_opcode=XTEST,ge_opcode=GE);name=b'XTEST'
  raw=struct.pack('>BBHHH',98,0,4,len(name),0)+name+b'\0'*3
  common=dict(category=1,client_base=BASE,client_sequence=1,server_time=1,client_swapped=True)
  self.assertEqual(trace.accept(**common,wire=raw)['extension_name'],'XTEST')
  for bad in(raw[:-1],raw[:4]+struct.pack('>H',255)+raw[6:]):
   with self.assertRaises(ValueError):m.MethodTrace(xtest_opcode=XTEST,ge_opcode=GE).accept(**common,wire=bad)
 def test_only_complete_normal_cleanup_and_zero_errors_can_qualify_method(self):
  m=self.module();rows,driver=fixture();bound=m.bind_trace(rows,driver)
  row=dict(bound,errors=[],record_version=[1,13],xtest_version=[2,2],start_of_data=True,end_of_data=True,recorder_closed=True,driver_closed=True,display_closed=True,children_reaped=True,record_context_freed=True,record_data_freed=True,connections_closed=True,unknown_records=0,malformed=0,dropped=0,overflow=False,recorder_expired=False,tse_started=False,resources={'measured':True})
  self.assertEqual(m.method_verdict(row)['status'],'PASS_METHOD_COLD_WARM_LIBRARY_REQUESTS_ONLY')
  for key,value in [('errors',['fault']),('connections_closed',False),('overflow',True),('unknown_records',1),('tse_started',True)]:
   self.assertEqual(m.method_verdict(dict(row,**{key:value}))['status'],'FAIL_METHOD_COLD_WARM_EVIDENCE')


class Package(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_xrecord_cold_warm_method'),'missing disabled cold/warm fork builder')
  return importlib.import_module('prepare_xrecord_cold_warm_method')
 def test_disabled_fork_preserves_ownchild_and_core_parser_parent(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'disabled';m=b.prepare(p)
   self.assertFalse(m['runtime_enabled']);self.assertFalse(m['claims']['method_native_executed'])
   self.assertIn('library_sha256',m)
   self.assertEqual(m['library_sha256']['/lib/x86_64-linux-gnu/libXext.so.6'],'2907e6a996465de5b32a0dd10534d4416b87f1dee5670aaa7b19301a1fc93f44')
   for name in('xrecord_core_method.py','xrecord_core_process.py'):self.assertEqual((p/name).read_bytes(),(b.PARENT/name).read_bytes())
   for name in('xrecord_core_controller.py','xrecord_core_native.py','xrecord_core_worker.py'):self.assertIn('RUNTIME_REVIEWED=False',(p/name).read_text())
   self.assertEqual(m['limits'],json.loads((b.PARENT/'source-manifest.json').read_text())['limits'])
   self.assertEqual(m['program'],{'calls':2,'dx':12,'dy':0,'display':':167','driver_warmup':False})
   with self.assertRaises(ValueError):b.prepare(p)
 def test_fork_driver_has_exactly_two_real_relative_calls_and_no_driver_warmup(self):
  import ast
  from types import SimpleNamespace
  b=self.builder();old=(b.PARENT/'xrecord_core_worker.py').read_text();new=b.transform_worker(old)
  before=next(n for n in ast.walk(ast.parse(old))if isinstance(n,ast.FunctionDef)and n.name=='initialize')
  after=next(n for n in ast.walk(ast.parse(new))if isinstance(n,ast.FunctionDef)and n.name=='initialize')
  self.assertEqual(ast.dump(before,include_attributes=False),ast.dump(after,include_attributes=False))
  driver=next(n for n in ast.parse(new).body if isinstance(n,ast.ClassDef)and n.name=='Driver')
  namespace=dict(time=SimpleNamespace(monotonic=lambda:1.))
  exec(compile(ast.Module(body=[driver],type_ignores=[]),'<fork-driver>','exec'),namespace)
  calls=[];counter=iter([26,31,33,34]);x=[400];queryseq=iter([32,35])
  def native(*args):calls.append(args);x[0]+=12;return 1
  n=SimpleNamespace(x=SimpleNamespace(XNextRequest=lambda d:next(counter),XSync=lambda *a:None),t=SimpleNamespace(XTestFakeRelativeMotionEvent=native),query=lambda *a:dict(window=WINDOW,root=ROOT,position=[x[0],300],sequence=next(queryseq)))
  obj=namespace['Driver'](n);obj.d=123;obj.window=WINDOW;obj.root=ROOT;obj.stage=1
  one=obj.relative();two=obj.relative()
  self.assertEqual(calls,[(123,12,0,0),(123,12,0,0)]);self.assertEqual(one['attempt']['sequence_interval'],[26,31]);self.assertEqual(two['attempt']['sequence_interval'],[33,34])
  with self.assertRaises(ValueError):obj.relative()


if __name__=='__main__':unittest.main()
