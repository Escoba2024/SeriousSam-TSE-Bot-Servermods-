"""Own lifecycle model only. All children, process reads and display guards fake."""
import ast
import copy
import importlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from test_xres_pid_method import fixture


class Lifecycle(unittest.TestCase):
 def module(self):return importlib.import_module('xres_pid_controller')
 def run_fake(self,directory,*,bad_pid=False,timeout=False,partial=False,bad_close=False,wrong_serial=False):
  m=self.module();created=[];called=[];cleaned=[]
  class Child:
   def __init__(self,argv,root,display,*,ttl,role):
    self.role=role;self.directory=Path(root);self.serial=0;self.identity=dict(pid={'display':100,'driver':101,'peer':102,'attributor':103}[role],start_ticks={'display':1000,'driver':1010,'peer':1020,'attributor':1030}[role],argv=argv,display=display);created.append(self)
   def guard(self):pass
   def call(self,command,*,timeout,**kw):
    called.append((self.role,command,timeout));self.serial+=1
    if partial and self.role=='peer'and command=='initialize':raise OSError('partial peer initialization')
    if command=='initialize':value=dict(xres_version=[1,2])if self.role=='attributor'else dict(resources=[0x200001,0x400001]if self.role=='driver'else[0x600001],connections=2 if self.role=='driver'else 1,mapped=False,inputs_emitted=0)
    elif command=='snapshot':
     if timeout_mode:raise TimeoutError('bounded metadata reply')
     value,_=fixture();value['index']=self.serial-2;value['monotonic_started']=time.monotonic();value['monotonic_finished']=time.monotonic()
     if bad_pid:value['results'][0]['ids'][0]['pid']=999
     for key in('process_before','process_after','parent_started','parent_finished','ipc_request_serial'):value.pop(key)
    else:raise AssertionError('no other program commands')
    return dict(id=0 if wrong_serial else self.serial,ok=True,value=value)
   def cleanup(self,**kw):
    cleaned.append((self.role,kw));native=dict(connections_closed=True,inputs_emitted=0,errors=[])
    if self.role=='attributor':native.update(snapshots=2,free_counts=dict(client_arrays_allocated=2,client_arrays_freed=2,id_arrays_allocated=12,id_arrays_freed=12))
    else:native.update(windows_created=2 if self.role=='driver'else 1,windows_destroyed=2 if self.role=='driver'else 1)
    if self.role!='display':(self.directory/(self.role+'-native-close.json')).write_text(json.dumps(dict(errors=[],native=native,handler=dict(error_handler_restored=True,errors=[]))))
    return dict(role=self.role,identity=self.identity,closed=True,reaped=True,forced=bad_close,exit_code=0,errors=[])
  timeout_mode=timeout
  with patch.object(m,'RUNTIME_REVIEWED',True),patch.object(m,'fresh_display_available'),patch.object(m,'wait_display'),patch.object(m,'guard_display',side_effect=lambda child:child.guard()),patch.object(m,'display_absent',return_value=True),patch.object(m,'own_namespace',return_value='pid:[123]'),patch.object(m,'role_identity',side_effect=lambda child:dict(child.identity,pid_namespace='pid:[123]')):
   answer=m.execute(Path(directory),child_factory=Child)
  return answer,created,called,cleaned
 def test_fixed_driver_two_peer_one_two_snapshots_and_four_normal_closes(self):
  with tempfile.TemporaryDirectory()as tmp:
   r,kids,calls,closed=self.run_fake(tmp)
   self.assertEqual(r['status'],'PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY')
   self.assertEqual([v.role for v in kids],['display','driver','peer','attributor'])
   self.assertEqual([(a,b)for a,b,_ in calls],[('driver','initialize'),('peer','initialize'),('attributor','initialize'),('attributor','snapshot'),('attributor','snapshot')])
   self.assertEqual([role for role,_ in closed],['attributor','peer','driver','display'])
   self.assertTrue(all(timeout<=3 for _,_,timeout in calls));self.assertFalse(r['continuous_client_lifetime_proven'])
 def test_bad_first_snapshot_saved_before_reject_and_no_second_call(self):
  with tempfile.TemporaryDirectory()as tmp:
   r,kids,calls,closed=self.run_fake(tmp,bad_pid=True)
   self.assertEqual(r['status'],'FAIL_METHOD_XRES_PID_EVIDENCE')
   self.assertEqual(sum(command=='snapshot'for _,command,_ in calls),1)
   self.assertEqual(json.loads((Path(tmp)/'snapshot-0.json').read_text())['results'][0]['ids'][0]['pid'],999)
   self.assertEqual(len(closed),4)
 def test_timeout_and_partial_start_keep_normal_own_cleanup(self):
  for kw in(dict(timeout=True),dict(partial=True),dict(bad_close=True),dict(wrong_serial=True)):
   with self.subTest(kw=kw),tempfile.TemporaryDirectory()as tmp:
    r,kids,calls,closed=self.run_fake(tmp,**kw)
    self.assertEqual(r['status'],'FAIL_METHOD_XRES_PID_EVIDENCE');self.assertEqual(len(closed),len(kids));self.assertTrue(r['errors'])
 def test_disabled_gate_precedes_path_reads_or_child_start(self):
  m=self.module()
  with patch.object(m,'verify_package',side_effect=AssertionError('must not reach package read')):
   with self.assertRaisesRegex(RuntimeError,'disabled'):m.run_method('/does/not/exist')
 def test_guard_functions_remain_exact_reviewed_parent_ast(self):
  m=self.module();old=ast.parse(Path('/srv/tse-own-xrecord-cold-warm-root-frozen-20261114/xrecord_core_controller.py').read_text());new=ast.parse(Path(m.__file__).read_text())
  names={'validate_display','display_absent','fresh_display_available','check_disk','listening_inode','guard_display','wait_display','bounded_json'}
  for name in names:
   a=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name==name);b=next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name==name)
   self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
 def test_no_input_cdll_in_parent_or_legacy_execute_in_program(self):
  m=self.module();parent=ast.parse(Path(m.__file__).read_text())
  attrs={n.attr for n in ast.walk(parent)if isinstance(n,ast.Attribute)}
  self.assertFalse(attrs&{'CDLL','XOpenDisplay','XTestFakeRelativeMotionEvent','XWarpPointer','XSetInputFocus'})
  worker=importlib.import_module('xres_pid_worker');tree=ast.parse(Path(worker.__file__).read_text())
  attrs={n.attr for n in ast.walk(tree)if isinstance(n,ast.Attribute)}
  self.assertFalse(attrs&{'XTestFakeRelativeMotionEvent','XTestFakeKeyEvent','XWarpPointer','XSetInputFocus','XMapWindow'})
  self.assertNotIn('xrecord_core_native',Path(worker.__file__).read_text())


class Package(unittest.TestCase):
 def test_disabled_manifest_actual_provision_headers_abi_and_unchanged_ownchild(self):
  import hashlib
  builder=importlib.import_module('prepare_xres_pid_method')
  with tempfile.TemporaryDirectory()as tmp:
   target=Path(tmp)/'disabled';m=builder.prepare(target)
   self.assertFalse(m['runtime_enabled']);self.assertEqual(m['schema'],'OWN_XRES_PID_METHOD_V1')
   for name,sha in m['files'].items():self.assertEqual(hashlib.sha256((target/name).read_bytes()).hexdigest(),sha)
   for section in('header_sha256','library_sha256','evidence_sha256'):
    self.assertTrue(m[section])
    for path,sha in m[section].items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),sha)
   self.assertEqual((target/'xrecord_core_process.py').read_bytes(),Path('/srv/tse-own-xrecord-cold-warm-root-frozen-20261114/xrecord_core_process.py').read_bytes())
   self.assertEqual(m['abi_layout'],json.loads(Path('/srv/tse-cecil-rollout-evidence-20261114/xres-abi-layout.json').read_bytes()))
   for name in('xres_pid_controller.py','xres_pid_worker.py'):
    tree=ast.parse((target/name).read_text());gate=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='RUNTIME_REVIEWED'for v in n.targets));self.assertIs(gate.value.value,False)
   with self.assertRaises(FileExistsError):builder.prepare(target)


if __name__=='__main__':unittest.main()
