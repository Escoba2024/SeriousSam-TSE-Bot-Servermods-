"""Offline profile/real adapter control-flow models; no Xlib/display/native load."""
import importlib
import json
import os
from pathlib import Path
import tempfile
import copy
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import sys

PARENT=Path('/srv/tse-a1-xres-lifecycle-root-frozen-20261115')
sys.path.append(str(PARENT))


class KeyboardInput(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('a1_keyboard_input'),'missing narrow keyboard adapter')
  return importlib.import_module('a1_keyboard_input')
 def test_profile_only_four_exact_Key1_tokens_change(self):
  m=self.module();before=Path('/srv/tse-milestone-a-evidence-20261111/a1-xres-lifecycle-root-20261115-005628/controls-profile-prepared.ctl').read_bytes()
  after=m.prepare_controls(before);reverse=after
  for control,key in m.KEY_NAMES.items():
   old=b'None'if control.startswith('yaw')else b'Mouse Button '+(b'4'if control=='pitch_up'else b'5')
   token=b' Name: TTRS '+m.BUTTONS[control].encode();start=reverse.index(token);pos=reverse.index(b' Key1: ',start)+7
   self.assertEqual(reverse[pos:pos+len(key)],key.encode());reverse=reverse[:pos]+old+reverse[pos+len(key):]
  self.assertEqual(reverse,before)
  for bad in(before+b'Button\n Name: TTRS Turn Left\n',before.replace(b'Key1: W',b'Key1: J'),before.replace(b'ctl_bTurnLeft = 0',b'ctl_bTurnLeft = 1')):
   with self.assertRaises(ValueError):m.prepare_controls(bad)
 def test_install_inside_sealed_transaction_preserves_metadata_and_restores(self):
  m=self.module();from transaction import FileTransaction
  base=Path('/srv/tse-milestone-a-evidence-20261111/a1-xres-lifecycle-root-20261115-005628/controls-profile-before.ctl').read_bytes()
  import a1_controls_diagnostic as controls
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp)/'arena';out=Path(tmp)/'e';root.mkdir();out.mkdir();path=root/'vanilla/Controls/Controls0.ctl';path.parent.mkdir(parents=True);path.write_bytes(base);path.chmod(0o640)
   tx=FileTransaction(root,out,lambda:None);tx.snapshot_file('vanilla/Controls/Controls0.ctl')
   with self.assertRaises(ValueError):m.install(tx,out)
   tx.seal();path.write_bytes(controls.disable_global_smoothing(base));st=path.stat();r=m.install(tx,out)
   self.assertEqual(r['prepared_sha256'],m.digest(path.read_bytes()));self.assertEqual((path.stat().st_mode,path.stat().st_uid,path.stat().st_gid),(st.st_mode,st.st_uid,st.st_gid))
   self.assertTrue(tx.restore()['restored']);self.assertEqual(path.read_bytes(),base)
 def test_keycodes_alias_and_unavailable_fail_closed(self):
  m=self.module();obj=m.KeyboardTransport.__new__(m.KeyboardTransport);obj.guard=Mock();obj.keys={'forward':25,'backward':39,'left':38,'right':40,'knife':10,'colt':11};obj.d=1
  obj.x=SimpleNamespace(XKeysymToKeycode=Mock(side_effect=[44,46,31,45]));obj.bind_keys();self.assertEqual([obj.keys[x]for x in m.KEY_NAMES],[44,46,31,45])
  for values in([0,46,31,45],[25,46,31,45],[44,44,31,45]):
   obj.keys={'forward':25,'backward':39,'left':38,'right':40,'knife':10,'colt':11};obj.x.XKeysymToKeycode=Mock(side_effect=values)
   with self.assertRaises(ValueError):obj.bind_keys()
 def test_native_counter_pointer_and_unsigned_long_abi_is_explicit_without_gc_probe(self):
  import ctypes as c
  m=self.module();t=m.KeyboardTransport.__new__(m.KeyboardTransport);t.c=c;t.x=SimpleNamespace(XNextRequest=Mock(),XQueryKeymap=Mock(),XSync=Mock());t.t=SimpleNamespace(XTestFakeKeyEvent=Mock())
  self.assertTrue(hasattr(t,'bind_counter_abi'),'missing inherited controller_gc counter ABI initialization')
  t.bind_counter_abi();self.assertEqual(t.x.XNextRequest.argtypes,[c.c_void_p]);self.assertIs(t.x.XNextRequest.restype,c.c_ulong)
  self.assertIs(t.x.XQueryKeymap.restype,c.c_int);self.assertIs(t.x.XSync.restype,c.c_int);self.assertIs(t.t.XTestFakeKeyEvent.restype,c.c_int)
  t.x.XNextRequest.assert_not_called();t.x.XQueryKeymap.assert_not_called();t.x.XSync.assert_not_called();t.t.XTestFakeKeyEvent.assert_not_called()
 def test_partial_down_guard_failure_still_executes_exact_native_keyup(self):
  m=self.module();calls=[];counter=[100];held=set()
  def native(d,key,down,delay):calls.append((key,down));counter[0]+=5 if down else 1;(held.add if down else held.discard)(key);return 1
  t=m.KeyboardTransport.__new__(m.KeyboardTransport);t.d=1;t.pin=SimpleNamespace(role='vanilla',display=':154');t.guard=lambda:None;t.keys={'forward':25,'yaw_left':44,'yaw_right':46,'pitch_up':31,'pitch_down':45}
  t.x=SimpleNamespace(XNextRequest=lambda d:counter[0],XSync=lambda *a:1);t.t=SimpleNamespace(XTestFakeKeyEvent=native)
  from a1_passive_xrecord import instrument_transport
  instrument_transport(t);j=m.KeyboardJournal(t);t.t.observer=j
  try:
   with self.assertRaises(ValueError):t.event('forward',True)
  finally:
   with self.assertRaises(RuntimeError):t.event('forward',False)
  self.assertEqual(calls,[(25,1),(25,0)]);self.assertEqual(held,set());self.assertTrue(j.failed);self.assertEqual(len(j.attempts),2)
 def test_mouse_fire_and_unrelated_movement_cannot_emit(self):
  m=self.module();t=m.KeyboardTransport.__new__(m.KeyboardTransport);t.guard=lambda:None;t.t=SimpleNamespace(XTestFakeKeyEvent=Mock())
  for control in('fire','left','knife','look_right'):
   with self.assertRaises(ValueError):t.event(control,True)
  with self.assertRaises(ValueError):t.look(12)
  t.t.XTestFakeKeyEvent.assert_not_called()
 def test_required_keyup_does_not_require_focus_but_neutral_bitmap_stays_strict(self):
  m=self.module();t=SimpleNamespace(event=Mock(),held=lambda c:True);pin=SimpleNamespace(window=9)
  e=m.KeyboardEndpoint(pin,t,Mock(side_effect=ValueError('process changed')),Mock());e.up('yaw_left');t.event.assert_called_once_with('yaw_left',False)
  with self.assertRaises(ValueError):e.released('yaw_left')
 def test_required_keyup_flushes_and_checks_real_bitmap_after_metadata_failure(self):
  # Fake C buffers an accepted event until actual XSync.  A native return alone
  # therefore cannot stand in for flush or neutral-state evidence.
  import ctypes as c
  from a1_passive_xrecord import instrument_transport
  m=self.module()
  for stage in ('after_native','first_counter','reserve'):
   with self.subTest(stage=stage):
    calls=[];pending=[];held={25};counter=[100];syncs=[];queries=[]
    def native(d,key,down,delay):
     calls.append((key,down));pending.append((key,down));counter[0]+=1;return 1
    def sync(d,discard):
     syncs.append(True)
     for key,down in pending:(held.add if down else held.discard)(key)
     pending.clear();return 1
    def keymap(d,bitmap):
     queries.append(True);bits=bytearray(32)
     for key in held:bits[key//8]|=1<<(key%8)
     for i,value in enumerate(bits):bitmap[i]=bytes([value])
     return 1
    t=m.KeyboardTransport.__new__(m.KeyboardTransport);t.c=c;t.d=1;t.pin=SimpleNamespace(role='vanilla',display=':154');t.guard=lambda:None
    t.keys={'forward':25,'yaw_left':44,'yaw_right':46,'pitch_up':31,'pitch_down':45}
    t.x=SimpleNamespace(XNextRequest=lambda d:counter[0],XSync=sync,XQueryKeymap=keymap);t.t=SimpleNamespace(XTestFakeKeyEvent=native)
    instrument_transport(t);journal=m.KeyboardJournal(t);t.t.observer=journal
    if stage=='after_native':journal.record_emission=Mock(side_effect=ValueError('metadata rejected after actual keyup'))
    elif stage=='first_counter':t.x.XNextRequest=Mock(side_effect=ValueError('first release counter unavailable'))
    else:journal.reserve_attempt=Mock(side_effect=RuntimeError('release reservation unavailable'))
    endpoint=m.KeyboardEndpoint(SimpleNamespace(window=9),t,Mock(side_effect=ValueError('focus/process not required for release')),Mock())
    with self.assertRaises((RuntimeError,ValueError)):endpoint.up('forward')
    self.assertEqual(calls,[(25,0)],'required native keyup must occur exactly once')
    self.assertEqual(syncs,[True],'actual flush must survive metadata rejection')
    self.assertEqual(queries,[True],'actual neutral bitmap must be observed after flush')
    self.assertEqual(held,set());self.assertTrue(journal.failed,'metadata failure remains sticky')
    with tempfile.TemporaryDirectory()as d:
     receipt=journal.close(d)['release_receipts'][0]
     self.assertIs(receipt['native_invoked'],True);self.assertEqual(receipt['return_value'],1);self.assertEqual(receipt['xsync_result'],1)
     self.assertIs(receipt['neutral_verified'],True);self.assertFalse(any(bytes.fromhex(receipt['bitmap_hex'])));self.assertTrue(receipt['errors'])
 def test_actual_bitmap_and_native_attempt_receipts_are_persisted_on_cleanup(self):
  import ctypes as c
  from a1_passive_xrecord import instrument_transport
  m=self.module();counter=[100];pending=[];held=set()
  def native(d,key,down,delay):pending.append((key,down));counter[0]+=1;return 1
  def sync(d,discard):
   for key,down in pending:(held.add if down else held.discard)(key)
   pending.clear();return 1
  def bitmap(d,out):
   data=bytearray(32)
   for key in held:data[key//8]|=1<<(key%8)
   for i,value in enumerate(data):out[i]=bytes([value])
   return 1
  t=m.KeyboardTransport.__new__(m.KeyboardTransport);t.c=c;t.d=1;t.pin=SimpleNamespace(role='vanilla',display=':154');t.guard=lambda:None;t.keys={'forward':25,'yaw_left':44,'yaw_right':46,'pitch_up':31,'pitch_down':45}
  t.x=SimpleNamespace(XNextRequest=lambda d:counter[0],XSync=sync,XQueryKeymap=bitmap);t.t=SimpleNamespace(XTestFakeKeyEvent=native)
  instrument_transport(t);journal=m.KeyboardJournal(t);t.t.observer=journal
  endpoint=m.KeyboardEndpoint(SimpleNamespace(window=9),t,Mock(),Mock());endpoint.check_focus=lambda:None
  endpoint.down('yaw_left');endpoint.up('yaw_left');endpoint.released('yaw_left')
  with tempfile.TemporaryDirectory()as d:
   r=journal.close(d);self.assertFalse(r['failed']);self.assertEqual(r['attempts'],2);self.assertEqual(r['emissions'],2)
   self.assertEqual([(p['native_attempt_index'],p['down'])for p in r['keymap_proofs']],[(0,True),(1,False)])
   self.assertTrue(bytes.fromhex(r['keymap_proofs'][0]['bitmap_hex'])[44//8]&(1<<(44%8)))
   self.assertFalse(any(bytes.fromhex(r['keymap_proofs'][1]['bitmap_hex'])))
   for name,h in r['files'].items():
    p=Path(d)/name;self.assertEqual(p.stat().st_mode&0o777,0o600);self.assertEqual(m.digest(p.read_bytes()),h)
 def test_completion_requires_all_twelve_native_calls_bitmap_ack_and_normal_restore(self):
  m=self.module();self.assertTrue(hasattr(m,'keyboard_journal_complete'),'missing real completion evidence auditor')
  keys={'forward':25,'yaw_left':44,'yaw_right':46,'pitch_up':31,'pitch_down':45};order=('yaw_left','forward','yaw_right','forward','pitch_up','pitch_down')
  journal=dict(failed=False,errors=[],attempts=12,emissions=12,keycodes=keys,no_wire_proof=True,attempt_rows=[],emission_rows=[],keymap_proofs=[])
  phases=[]
  for i,control in enumerate(order):
   at=float(i);event=dict(role='vanilla',control=control,request_confirmed=True,started=at,finished=at+.01)
   phases.append(dict(actions={'vanilla':control},status='PASS',requested_seconds=.1,held_started=at,release_started=at+.1,finished=at+.11,input_to_release_seconds=(at+.11)-at,emissions=[event],errors=[]))
   for down,start in((True,at+.001),(False,at+.101)):
    index=len(journal['emission_rows']);raw=dict(index=index,function='XTestFakeKeyEvent',arguments=[1,keys[control],int(down),0],return_value=1,started_monotonic=start,finished_monotonic=start+.001,sequence_interval=[100+index,101+index])
    journal['emission_rows'].append(raw);journal['attempt_rows'].append(dict(attempt_index=index,native_invoked=True,validation_status='ACCEPTED',sequence_before=100+index,sequence_after=101+index,metadata={k:v for k,v in raw.items()if k!='index'}))
    bits=bytearray(32)
    if down:bits[keys[control]//8]|=1<<(keys[control]%8)
    journal['keymap_proofs'].append(dict(control=control,keycode=keys[control],down=down,native_attempt_index=index,bitmap_hex=bits.hex()))
  prep=dict(status='PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY',**{k:6 for k in('actions_admitted','actions_attempted','actions_released','actions_acked','actions_completed')})
  report=dict(status=prep['status'],observer_mode='keyboard-qualification',qualified=False,normal_route_or_fire=False,diagnostic_only=True,collector_requested=False,errors=[],shooter_preparation=prep,input_phase_timings=phases,keyboard_journal=journal,restoration={'restored':True},post_close_logs={'accepted':True},cleanup={r:{'closed':True}for r in('server','vanilla','botA')},displays={str(n):{'closed':True}for n in(154,155)})
  verdict=SimpleNamespace(reasons=('window_not_passed',));self.assertTrue(m.keyboard_journal_complete(report,verdict))
  def malformed_actual_direction(r):
   r['keyboard_journal']['emission_rows'][0]['arguments'][2]=True;r['keyboard_journal']['attempt_rows'][0]['metadata']['arguments'][2]=True
  def reversed_actual_sequence(r):
   row=r['keyboard_journal']['emission_rows'][2];row['sequence_interval']=[1,2];attempt=r['keyboard_journal']['attempt_rows'][2];attempt.update(sequence_before=1,sequence_after=2);attempt['metadata']['sequence_interval']=[1,2]
  mutations=[lambda r:r['keyboard_journal']['attempt_rows'][1].update(native_invoked=False),lambda r:r['keyboard_journal']['attempt_rows'][0].update(sequence_after=999),lambda r:r['keyboard_journal']['keymap_proofs'][1].update(bitmap_hex='ff'*32),lambda r:r['keyboard_journal']['emission_rows'][0]['arguments'].__setitem__(1,99),lambda r:r['shooter_preparation'].update(actions_acked=5),lambda r:r['input_phase_timings'][0].update(input_to_release_seconds=.351),lambda r:r['restoration'].update(restored=False),lambda r:r.update(collector_arm={}),lambda r:r['errors'].append('sticky failure'),lambda r:r.update(observer_mode='instrumented-trace'),malformed_actual_direction,reversed_actual_sequence]
  for mutation,mutate in enumerate(mutations):
   with self.subTest(mutation=mutation):
    bad=copy.deepcopy(report);mutate(bad);self.assertFalse(m.keyboard_journal_complete(bad,verdict))
 def test_querykeymap_failed_return_cannot_claim_neutrality(self):
  import ctypes as c
  m=self.module();t=m.KeyboardTransport.__new__(m.KeyboardTransport);t.c=c;t.d=1;t.guard=lambda:None;t.keys={'forward':25,'yaw_left':44}
  t.x=SimpleNamespace(XQueryKeymap=lambda *args:0)
  with self.assertRaises(ValueError):t.held('yaw_left')


if __name__=='__main__':unittest.main()
