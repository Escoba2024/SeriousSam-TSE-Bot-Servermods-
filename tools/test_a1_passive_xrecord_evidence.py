"""Synthetic fixed-provenance records only."""
import copy
import unittest
import struct
import json
from pathlib import Path
import tempfile
from xrecord_core_method import CoreTrace

def fixture():
 rows=[];parser=CoreTrace(xtest_opcode=137);base=0x200000;window=0x400001;root=99
 def add(wire,category,seq=10,client=base):
  row=parser.accept(category=category,client_base=client,client_sequence=seq,server_time=10,client_swapped=False,wire=bytes(wire));row.update(callback_serial=len(rows)+1,received_monotonic=1.+len(rows)*.001);rows.append(row)
 wire=bytearray(36);struct.pack_into("<BBH",wire,0,137,2,9);wire[4]=6;wire[5]=1;struct.pack_into("<hh",wire,24,12,0);add(wire,1)
 for index,pos in enumerate(([412,300],[400,300])):
  if index:
   wire=bytearray(24);struct.pack_into("<BBHII",wire,0,41,0,6,0,root);struct.pack_into("<hh",wire,20,*pos);add(wire,1)
  for client in(0,base):
   wire=bytearray(32);wire[0]=6;struct.pack_into("<II",wire,8,root,window);struct.pack_into("<hh",wire,20,*pos);add(wire,0,client=client)
  seq=20+index;wire=bytearray(8);struct.pack_into("<BBHI",wire,0,38,0,2,window);add(wire,1,seq)
  wire=bytearray(32);wire[0]=1;wire[1]=1;struct.pack_into("<H",wire,2,seq);struct.pack_into("<I",wire,8,root);struct.pack_into("<hh",wire,16,*pos);add(wire,0,seq)
 return rows,None
import a1_passive_xrecord_evidence as e

class Tests(unittest.TestCase):
 def data(self):
  rows,_=fixture()
  for row in rows:
   if row['kind']in('warp_request','delivered_motion'):row['client_base']=0x400000
  emission=dict(index=0,function='XTestFakeRelativeMotionEvent',arguments=[123,12,0,0],return_value=1,sequence_interval=[10,11],started_monotonic=1.,finished_monotonic=1.1)
  return rows,[emission],dict(controller_transport=0x200000,original_window_owner=0x400000)
 def test_exact_controller_source_and_query_warp_event_copies_are_separate(self):
  rows,emissions,bases=self.data();out=e.bind_emissions(rows,emissions,bases,xtest_opcode=137)
  self.assertEqual(out['bound_emissions'],1);self.assertEqual(out['controller_query_records'],4);self.assertEqual(out['window_owner_warp_records'],1)
  self.assertEqual(out['device_motion_records'],2);self.assertEqual(out['delivered_motion_records'],2);self.assertFalse(out['pid_equals_clientbase']);self.assertFalse(out['xi2_complete'])
 def test_matching_foreign_client_is_not_a_source_fallback(self):
  rows,emissions,bases=self.data();rows[0]['client_base']=0x400000
  with self.assertRaises(ValueError):e.bind_emissions(rows,emissions,bases,xtest_opcode=137)
 def test_duplicate_missing_or_changed_controller_emission_is_hard_fail(self):
  for change in('duplicate','missing','wrong_pixels','wrong_seq'):
   rows,emissions,bases=self.data()
   if change=='duplicate':rows.append(copy.deepcopy(rows[0]))
   elif change=='missing':rows.pop(0)
   elif change=='wrong_pixels':emissions[0]['arguments'][1]=11
   else:emissions[0]['sequence_interval']=[11,12]
   with self.subTest(change=change),self.assertRaises(ValueError):e.bind_emissions(rows,emissions,bases,xtest_opcode=137)
 def test_different_extension_major_is_not_typed_as_xtest(self):
  rows,emissions,bases=self.data();wire=bytearray.fromhex(rows[0]['wire_hex']);wire[0]=138;rows[0]['wire_hex']=wire.hex()
  with self.assertRaises(ValueError):e.bind_emissions(rows,emissions,bases,xtest_opcode=137)
 def test_actual_proxy_call_is_nested_in_the_existing_calibration_emission(self):
  rows,emissions,bases=self.data();phases=[dict(index=0,actions={'vanilla':'look_right'},emissions=[dict(role='vanilla',control='look_right',pixels=12,started=.99,finished=1.11,request_confirmed=True)],release_started=1.2,finished=1.3)]
  self.assertEqual(e.bind_phases(emissions,phases,25),1)
  phases[0]['emissions'][0]['pixels']=11
  with self.assertRaises(ValueError):e.bind_phases(emissions,phases,25)
  phases[0]['emissions'][0]['pixels']=12;phases[0]['emissions'][0]['started']=1.01
  with self.assertRaises(ValueError):e.bind_phases(emissions,phases,25)
 def test_forward_release_is_the_same_key_within_the_existing_release_interval(self):
  events=[dict(index=0,function='XTestFakeKeyEvent',arguments=[123,25,1,0],started_monotonic=1.,finished_monotonic=1.1),dict(index=1,function='XTestFakeKeyEvent',arguments=[123,25,0,0],started_monotonic=1.21,finished_monotonic=1.22)]
  phases=[dict(index=0,actions={'vanilla':'forward'},emissions=[dict(role='vanilla',control='forward',started=.99,finished=1.11,request_confirmed=True)],release_started=1.2,finished=1.3)]
  self.assertEqual(e.bind_phases(events,phases,25),1)
  events[1]['arguments'][1]=26
  with self.assertRaises(ValueError):e.bind_phases(events,phases,25)
 def test_failed_native_call_cannot_become_actual_input_proof(self):
  rows,emissions,bases=self.data();emissions[0]['error']='failed'
  with self.assertRaises(ValueError):e.bind_emissions(rows,emissions,bases,xtest_opcode=137)
 def audit_fixture(self):
  rows,emissions,bases=self.data();boundary=dict(client_base=0,wire_hex='',client_swapped=False)
  rows=[dict(boundary,kind='start')]+rows+[dict(boundary,kind='end')]
  for i,row in enumerate(rows):row.update(callback_serial=i+1,received_monotonic=1.+i*.001)
  native=dict(errors=[],cleanup_errors=[],records=len(rows),calls=len(rows),freed=len(rows),malformed=0,dropped=0,budget_failed=False,context_freed=True,connections_closed=True,end_verified=True,unknown_records=0,start_count=1,end_count=1)
  arm=dict(bindings=bases,xtest_opcode=137,forward_keycode=25)
  phases=[dict(index=0,actions={'vanilla':'look_right'},emissions=[dict(role='vanilla',control='look_right',pixels=12,started=.99,finished=1.11,request_confirmed=True)],release_started=1.2,finished=1.3)]
  return rows,emissions,arm,native,phases
 def run_audit(self,data):
  rows,emissions,arm,native,phases=data
  with tempfile.TemporaryDirectory()as d:
   raw=b''.join((json.dumps(r)+'\n').encode()for r in rows);Path(d,'record-raw.jsonl').write_bytes(raw)
   native.setdefault('bytes',len(raw));return e.audit_trace(d,emissions,arm,native,phases)
 def test_complete_trace_binds_existing_phase_and_keeps_partial_claims(self):
  out=self.run_audit(self.audit_fixture());self.assertEqual(out['bound_existing_a1_phases'],1);self.assertEqual(out['bound_emissions'],1)
  self.assertFalse(out['a1_pass']);self.assertFalse(out['gain_fixed']);self.assertFalse(out['xi2_complete'])
 def test_raw_serial_clock_boundary_and_native_cleanup_fail_closed(self):
  for change in('serial','nan','reverse','start','end','free','error','context','drop','budget','unsupported'):
   data=self.audit_fixture();rows,_,_,native,_=data
   if change=='serial':rows[2]['callback_serial']=2
   elif change=='nan':rows[2]['received_monotonic']=float('nan')
   elif change=='reverse':rows[2]['received_monotonic']=0.
   elif change=='start':rows[0]['kind']='end'
   elif change=='end':rows[-1]['kind']='start'
   elif change=='free':native['freed']-=1
   elif change=='error':native['cleanup_errors']=['free failed']
   elif change=='context':native['context_freed']=False
   elif change=='drop':native['dropped']=1
   elif change=='budget':native['budget_failed']=True
   else:native['unknown_records']=1
   with self.subTest(change=change),self.assertRaises(ValueError):self.run_audit(data)
 def test_native_serialized_bytes_and_boundary_counts_must_match_raw(self):
  for key,value in(('bytes',1),('start_count',0),('end_count',2)):
   data=self.audit_fixture();data[3][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):self.run_audit(data)

if __name__=='__main__':unittest.main()
