import copy
import importlib.util
from pathlib import Path
import unittest
import tempfile
from unittest.mock import Mock, patch
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('opponent_input',HERE/'retail_opponent_input.py')
ROOT=Path('/srv/tse-session-qualification-m2-input-fixture')
class Guards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
 def evidence(self):
  return dict(runtime=ROOT,expected_dll='860ae6d7fbc91de301f80a963599d970692b872a51d0e0330dbd30ccd11e134b',result={'dll_sha256':'860ae6d7fbc91de301f80a963599d970692b872a51d0e0330dbd30ccd11e134b','status':'MEASURING','scope':'ISOLATED_NETNS_RETAIL_WINE','m2_combat':True,'cecil_p1':True,'network_namespace':'net:[123]','cgroup':'/sys/fs/cgroup/tse-sessions-123'},guard={'status':'MONITORING','error':None,'samples':[dict(at=100,available_mib=1600,disk_free_gib=8.5,host_busy_percent=40)]},sample={'processes':{'vanilla':{'start_ticks':999}}},now=101,result_mtime=100,guard_mtime=100,sample_mtime=100)
 def test_current_private_context_requires_live_original_actor_sample(self):
  self.assertEqual(self.m.validate_evidence(**self.evidence())['start_ticks'],999)
 def test_stale_future_or_inactive_receipts_are_rejected(self):
  for field,value in [('result_mtime',50),('guard_mtime',90),('sample_mtime',95),('sample_mtime',103)]:
   e=self.evidence();e[field]=value
   with self.assertRaises(ValueError):self.m.validate_evidence(**e)
  for key,value in [('status','FINISHED'),('status','STOPPED_GUARD'),('error','resource failure')]:
   e=self.evidence();e['guard'][key]=value
   with self.assertRaises(ValueError):self.m.validate_evidence(**e)
 def test_foreign_runtime_or_missing_actor_is_rejected(self):
  for path in ['/srv/tse-public-anything','/tmp/tse-session-qualification-m2-input-fixture']:
   e=self.evidence();e['runtime']=Path(path)
   with self.assertRaises(ValueError):self.m.validate_evidence(**e)
  e=self.evidence();e['sample']['processes'].clear()
  with self.assertRaises(ValueError):self.m.validate_evidence(**e)
 def test_failed_resource_gate_prevents_input(self):
  for key,value in [('available_mib',767),('disk_free_gib',7.99),('host_busy_percent',85),('at',90)]:
   e=self.evidence();e['guard']['samples'][0][key]=value
   with self.assertRaises(ValueError):self.m.validate_evidence(**e)
 def test_process_generation_uid_path_namespace_and_group_are_bound(self):
  expected=self.m.validate_evidence(**self.evidence())
  record=dict(pid=777,start_ticks=999,uid=65534,cwd=str(ROOT/'vanilla'),cgroup='/tse-sessions-123',network_namespace='net:[123]',command='Bin/SeriousSam.exe')
  self.m.validate_process(record,expected,ROOT)
  for key,value in [('start_ticks',998),('uid',0),('cwd',str(ROOT/'m2bot0')),('cgroup','/foreign'),('network_namespace','net:[987]'),('command','DedicatedServer.exe')]:
   changed=dict(record,**{key:value})
   with self.assertRaises(ValueError):self.m.validate_process(changed,expected,ROOT)
 def test_partial_or_malformed_newest_sample_cannot_refresh_old_actor(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp)/'samples.jsonl'
   for tail in [b'{"unfinished":',b'not-json\n',b'']:
    p.write_bytes(b'{"processes":{"vanilla":{"start_ticks":999}}}\n'+tail)
    if tail:
     with self.assertRaises(ValueError):self.m.latest_sample(p)
    else:self.assertEqual(self.m.latest_sample(p)['processes']['vanilla']['start_ticks'],999)
 def test_foreign_dispatch_has_no_filesystem_or_input_side_effect(self):
  with tempfile.TemporaryDirectory() as temp,patch.object(self.m,'_dispatch') as send:
   with self.assertRaises(ValueError):self.m.dispatch(Path(temp),None,':178','w',None,.1)
   self.assertEqual(list(Path(temp).iterdir()),[]);send.assert_not_called()
 def fake_x(self,focus=42):
  x=Mock()
  def focused(d,f,r):f._obj.value=focus;return 1
  def pointer(d,w,root,child,rx,ry,px,py,mask):px._obj.value=10;py._obj.value=10;return 1
  x.XGetInputFocus.side_effect=focused;x.XQueryPointer.side_effect=pointer
  return x
 def test_focus_loss_denies_press_and_releases_server_grab(self):
  x=self.fake_x(focus=99);event=Mock(return_value=1)
  with self.assertRaises(ValueError):self.m.send_input(x,1,42,100,100,event,7,.05,lambda:None)
  event.assert_not_called();x.XUngrabServer.assert_called_once()
 def test_failed_release_is_retried_and_never_reported_successful(self):
  x=self.fake_x();event=Mock(side_effect=[1,0,0,0])
  with patch.object(self.m.time,'sleep'),self.assertRaises(ValueError):
   self.m.send_input(x,1,42,100,100,event,7,.05,lambda:None)
  self.assertEqual(event.call_count,4);x.XUngrabServer.assert_called_once()
 def test_interruption_after_press_still_releases(self):
  x=self.fake_x();event=Mock(return_value=1)
  with patch.object(self.m.time,'sleep',side_effect=InterruptedError),self.assertRaises(InterruptedError):
   self.m.send_input(x,1,42,100,100,event,7,.05,lambda:None)
  self.assertEqual([c.args[2] for c in event.call_args_list],[True,False])
 def test_interruption_inside_press_attempt_still_releases(self):
  x=self.fake_x();event=Mock(side_effect=[InterruptedError,1])
  with self.assertRaises(InterruptedError):self.m.send_input(x,1,42,100,100,event,7,.05,lambda:None)
  self.assertEqual([c.args[2] for c in event.call_args_list],[True,False])
 def test_pointer_outside_original_denies_mouse_press(self):
  x=self.fake_x();x.XQueryPointer.return_value=0;x.XQueryPointer.side_effect=None;event=Mock(return_value=1)
  with self.assertRaises(ValueError):self.m.send_input(x,1,42,100,100,event,1,.05,lambda:None)
  event.assert_not_called()
if __name__=='__main__':unittest.main()
