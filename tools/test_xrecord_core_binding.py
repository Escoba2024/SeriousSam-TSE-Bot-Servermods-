"""Wire evidence binding with synthetic records, no display or library calls."""
import copy
import struct
import unittest
import xrecord_core_controller as c


def fixture():
 rows=[];base=0x200000;window=base+1;root=99
 def row(kind,wire,seq=10,client=base,**extra):
  v=dict(kind=kind,wire_hex=wire.hex(),client_base=client,client_sequence=seq,client_swapped=False,callback_serial=len(rows)+1,received_monotonic=1.+len(rows)*.001,**extra);rows.append(v)
 b=bytearray(36);struct.pack_into('<BBH',b,0,137,2,9);b[4]=6;b[5]=1;struct.pack_into('<hh',b,24,12,0);row('xtest_relative_motion',b,dx=12,dy=0)
 for index,pos in enumerate(([412,300],[400,300])):
  if index:
   b=bytearray(24);struct.pack_into('<BBHII',b,0,41,0,6,0,root);struct.pack_into('<hh',b,20,*pos);row('warp_request',b,dst_x=400,dst_y=300)
  for client,kind in((0,'device_motion'),(base,'delivered_motion')):
   b=bytearray(32);b[0]=6;struct.pack_into('<II',b,8,root,window);struct.pack_into('<hh',b,20,*pos);row(kind,b,client=client,root_x=pos[0],root_y=pos[1])
  seq=20+index;b=bytearray(8);struct.pack_into('<BBHI',b,0,38,0,2,window);row('query_pointer_request',b,seq)
  b=bytearray(32);b[0]=1;b[1]=1;struct.pack_into('<H',b,2,seq);struct.pack_into('<I',b,8,root);struct.pack_into('<hh',b,16,*pos);row('query_pointer_reply',b,seq,root_x=pos[0],root_y=pos[1],same_screen=True,request_sequence=seq)
 driver=dict(window=window,root=root,queries=[dict(window=window,root=root,sequence=20,position=[412,300]),dict(window=window,root=root,sequence=21,position=[400,300])])
 return rows,driver


class BindingTests(unittest.TestCase):
 def test_requests_actual_replies_own_window_and_sequences_bind_one_driver(self):
  rows,driver=fixture();out=c.bind_trace(rows,driver)
  self.assertTrue(out['request_client_bound']);self.assertEqual(out['query_positions'],[[412,300],[400,300]])
  self.assertEqual(out['device_motion_positions'],[[412,300],[400,300]])
 def test_wrong_client_window_sequence_root_or_position_rejected(self):
  for kind,key,value in(('xtest_relative_motion','client_base',0x400000),('query_pointer_reply','request_sequence',40),('query_pointer_reply','same_screen',False),('query_pointer_reply','root_x',411)):
   rows,driver=fixture();next(r for r in rows if r['kind']==kind)[key]=value
   with self.subTest(kind=kind,key=key),self.assertRaises(ValueError):c.bind_trace(rows,driver)
  rows,driver=fixture();driver['window']+=1
  with self.assertRaises(ValueError):c.bind_trace(rows,driver)
 def test_duplicate_or_out_of_order_observation_fails(self):
  for mode in('duplicate','reverse','extra'):
   rows,driver=fixture()
   if mode=='duplicate':rows[1]['callback_serial']=rows[0]['callback_serial']
   elif mode=='reverse':rows[1]['received_monotonic']=0.
   else:rows.append(copy.deepcopy(rows[0]))
   with self.subTest(mode=mode),self.assertRaises(ValueError):c.bind_trace(rows,driver)
 def test_device_event_is_not_claimed_as_client_origin(self):
  rows,driver=fixture();out=c.bind_trace(rows,driver)
  self.assertIsNone(out['device_motion_originating_client']);self.assertEqual(out['client_binding_basis'],'own_window_plus_recorded_query_request_reply_sequences')

if __name__=='__main__':unittest.main()
