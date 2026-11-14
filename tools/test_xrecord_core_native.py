"""Pure ABI, callback ownership and protocol binding tests; never loads Xlib."""
import ctypes as C
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import xrecord_core_method as m
import xrecord_core_native as n

class NativeTests(unittest.TestCase):
 def test_native_state_layout_and_selected_ranges_roundtrip(self):
  self.assertEqual(C.sizeof(n.RecordState),24);self.assertEqual(C.sizeof(n.RecordClientInfo),24)
  ranges=n.selected_ranges(137);self.assertEqual(len(ranges),4)
  self.assertEqual(n.range_signature(ranges[0]),[38,38,38,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  self.assertEqual(ranges[2].ext_requests.ext_major.first,137)
  self.assertEqual(ranges[2].ext_requests.ext_minor.first,2)
  for bad in(0,127,256):
   with self.assertRaises(ValueError):n.selected_ranges(bad)
 def test_context_state_uses_expanded_clients_and_future_spec_not_allclients(self):
  ranges=n.selected_ranges(137);rp=(C.POINTER(m.RecordRange)*4)(*(C.pointer(r)for r in ranges));infos=[n.RecordClientInfo(client,4,rp)for client in(2,0x200000,0x400000,0x600000)]
  ip=(C.POINTER(n.RecordClientInfo)*4)(*(C.pointer(i)for i in infos));state=n.RecordState(0,7,4,ip)
  class Fake:
   freed=0
   def XRecordGetContext(self,d,context,out):C.cast(out,C.POINTER(C.POINTER(n.RecordState)))[0]=C.pointer(state);return 1
   def XRecordFreeState(self,p):self.freed+=1
  obj=n.Native.__new__(n.Native);obj.t=Fake();obj.errors=[]
  self.assertTrue(obj.context_state(1,2,ranges,enabled=False));self.assertEqual(obj.t.freed,1)
  state.datum_flags=3
  with self.assertRaises(ValueError):obj.context_state(1,2,ranges,enabled=False)
  self.assertEqual(obj.t.freed,2)
 def test_enabled_context_exact_semantic_ranges_and_data_client_exclusion(self):
  wanted=n.selected_ranges(137);packed=[m.RecordRange(),m.RecordRange()]
  packed[0].core_requests.first=packed[0].core_requests.last=38;packed[1].core_requests.first=packed[1].core_requests.last=41
  packed[0].core_replies.first=packed[0].core_replies.last=38;packed[0].ext_requests=wanted[2].ext_requests;packed[0].device_events=wanted[3].device_events;packed[0].delivered_events=wanted[3].delivered_events
  rp=(C.POINTER(m.RecordRange)*2)(*(C.pointer(r)for r in packed));infos=[n.RecordClientInfo(client,2,rp)for client in(2,0x200000,0x400000)];ip=(C.POINTER(n.RecordClientInfo)*3)(*(C.pointer(i)for i in infos));state=n.RecordState(1,7,3,ip)
  class Fake:
   freed=0
   def XRecordGetContext(self,d,context,out):C.cast(out,C.POINTER(C.POINTER(n.RecordState)))[0]=C.pointer(state);return 1
   def XRecordFreeState(self,p):self.freed+=1
  obj=n.Native.__new__(n.Native);obj.t=Fake();obj.errors=[]
  self.assertTrue(obj.context_state(1,2,wanted,enabled=True))
  packed[0].device_events.last=7
  with self.assertRaises(ValueError):obj.context_state(1,2,wanted,enabled=True)
  packed[0].device_events.last=6;packed[1].core_requests.first=packed[1].core_requests.last=0
  with self.assertRaises(ValueError):obj.context_state(1,2,wanted,enabled=True)
  packed[1].core_requests.first=38;packed[1].core_requests.last=41
  with self.assertRaises(ValueError):obj.context_state(1,2,wanted,enabled=True)
  self.assertEqual(obj.t.freed,4)
 def test_load_gate_precedes_cdll(self):
  with patch.object(C,'CDLL',side_effect=AssertionError('never load')),self.assertRaisesRegex(RuntimeError,'disabled'):n.Native()
 def test_callback_catches_parser_error_frees_data_and_sticks(self):
  class Fake:
   freed=0
   def XRecordFreeData(self,p):self.freed+=1
  fake=Fake()
  with tempfile.TemporaryDirectory()as d:
   sink=n.RecordSink(fake,Path(d)/'raw.jsonl',137,started=1.,clock=lambda:1.1)
   value=m.Intercept();value.category=1;value.data_len=5000
   sink.callback(None,C.pointer(value));sink.close()
   self.assertEqual(fake.freed,1);self.assertEqual(sink.freed,1);self.assertTrue(sink.errors);self.assertEqual(sink.budget.records,0);self.assertEqual(sink.receipt()['malformed'],1);self.assertEqual(sink.receipt()['dropped'],1)
 def test_callback_handles_control_and_freed_count_and_private_file(self):
  class Fake:
   def XRecordFreeData(self,p):pass
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'raw.jsonl';sink=n.RecordSink(Fake(),p,137,started=1.,clock=lambda:1.1)
   for category in(4,5):
    value=m.Intercept();value.category=category;sink.callback(None,C.pointer(value))
   sink.close();rows=[json.loads(x)for x in p.read_text().splitlines()]
   self.assertEqual([r['kind']for r in rows],['start','end']);self.assertEqual(sink.receipt()['freed'],2)
   self.assertEqual(p.stat().st_mode&0o777,0o600);self.assertEqual(sink.errors,[])
 def test_data_free_error_is_sticky_and_does_not_cross_c_boundary(self):
  class Fake:
   def XRecordFreeData(self,p):raise OSError('free')
  with tempfile.TemporaryDirectory()as d:
   sink=n.RecordSink(Fake(),Path(d)/'raw.jsonl',137,started=1.,clock=lambda:1.1)
   value=m.Intercept();value.category=4;sink.callback(None,C.pointer(value));sink.close()
   self.assertEqual(sink.freed,0);self.assertTrue(sink.errors)

if __name__=='__main__':unittest.main()
