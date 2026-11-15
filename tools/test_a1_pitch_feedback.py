"""Synthetic native-frame/normal-input callbacks only, never native input."""
import copy
import ast
import importlib
from pathlib import Path
import sys
import unittest
import tempfile
import json
import types

PARENT=Path('/srv/tse-a1-xres-lifecycle-root-frozen-20261115')
sys.path.append(str(PARENT))
from test_colt_preparation import ColtCase


class FeedbackCase(ColtCase):
 def __init__(self,*,detour_gain=-.5,unit_gain=-.25,mode='normal'):
  super().__init__();self.detour_gain=detour_gain;self.unit_gain=unit_gain;self.feedback_mode=mode;self.calls=[];self.call_times=[];self.before_motion=None;self.frame_mutation=None;self.hold=.1;self.latency=0.;self.due=None;self.old_pitch=0.
 def frame(self):
  actual=self.pitch
  if self.due is not None and self.now<self.due:self.pitch=self.old_pitch
  try:f=super().frame()
  finally:self.pitch=actual
  if self.frame_mutation:self.frame_mutation(f)
  return f
 def step(self,role,control,seconds,*,before_press=lambda:None,pixels=None):
  if self.before_motion:self.before_motion()
  before_press();at=self.now;self.calls.append((role,control,seconds,pixels));self.call_times.append(at);self.now+=self.hold
  gain=self.detour_gain if len(self.calls)==1 else self.unit_gain
  self.old_pitch=self.pitch
  if self.feedback_mode=='reverse':gain=abs(gain)
  if self.feedback_mode=='missing_ack'or(self.feedback_mode=='plateau'and len(self.calls)>1):gain=0.
  self.pitch+=pixels*gain;self.due=at+self.latency
  event=dict(role=role,control=control,pixels=pixels,axis='y',started=at,finished=at,request_confirmed=True)
  return dict(released=True,actual_shot_proven=False,input_phase_timing=dict(status='PASS',requested_seconds=seconds,held_started=at,release_started=self.now,finished=self.now,input_to_release_seconds=self.now-at,errors=[],emissions=[event]))
 def run_feedback(self,**kw):
  module=importlib.import_module('a1_pitch_feedback')
  return module.run(self.frame,self.step,lambda:self.now,self.sleep,self.receipt,started=0.,runner_deadline=kw.get('runner_deadline',90.))


class FeedbackPolicyTests(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('a1_pitch_feedback'),'missing separate pure pitch-feedback policy')
  return importlib.import_module('a1_pitch_feedback')
 def test_asymmetric_detour_and_one_pixel_feedback_returns_without_gain_or_fire(self):
  self.module();c=FeedbackCase();r=c.run_feedback()
  self.assertEqual(c.calls,[('vanilla','look_vertical',.1,12)]+[('vanilla','look_vertical',.1,-1)]*21)
  self.assertEqual(r['status'],'PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY');self.assertEqual(r['return_error_deg'],.75)
  self.assertEqual(r['corrections_acked'],21);self.assertEqual(r['actions_acked'],22)
  self.assertEqual(r['actions'][0]['axis_ack']['delta_deg'],-6.)
  for key in('qualified','a1_pass','mouse_gain_fixed','input_once_proven','actual_shot_proven','foreign_hit_proven','first_processed_state_proven'):self.assertIs(r[key],False)
 def test_alternate_actual_response_uses_measured_endpoints_not_fixed_opposite(self):
  self.module();c=FeedbackCase(detour_gain=-.25,unit_gain=-.5);r=c.run_feedback()
  self.assertEqual([x[3]for x in c.calls],[12]+[-1]*5);self.assertEqual(r['return_error_deg'],.5)
 def test_zero_feedback_opportunity_never_passes_without_actual_unit_input(self):
  self.module();c=FeedbackCase(detour_gain=-.02)
  with self.assertRaisesRegex(ValueError,'FEEDBACK_NOT_EXERCISED'):c.run_feedback()
  self.assertEqual(len(c.calls),1);self.assertEqual(c.receipt['status'],'FAIL')
 def test_plateau_reverse_missing_ack_stop_without_any_extra_input(self):
  self.module()
  for mode,count in(('plateau',2),('reverse',1),('missing_ack',1)):
   c=FeedbackCase(mode=mode)
   with self.subTest(mode=mode),self.assertRaises(ValueError):c.run_feedback()
   self.assertEqual(len(c.calls),count);self.assertEqual(c.receipt['status'],'FAIL')
 def test_fixed_scope_refuses_wrong_role_control_pixels_or_49th_action(self):
  m=self.module();scope=m.FeedbackScope();scope.admit('vanilla','look_vertical',.1,12)
  for unused in range(47):scope.admit('vanilla','look_vertical',.1,-1)
  with self.assertRaises(ValueError):scope.admit('vanilla','look_vertical',.1,-1)
  for args in(('botA','look_vertical',.1,12),('vanilla','fire',.1,12),('vanilla','look_vertical',.2,12),('vanilla','look_vertical',.1,-12),('vanilla','look_horizontal',.1,12)):
   with self.subTest(args=args),self.assertRaises(ValueError):m.FeedbackScope().admit(*args)
 def test_48_actions_do_not_authorize_49th_correction(self):
  self.module();c=FeedbackCase(unit_gain=-.02)
  with self.assertRaisesRegex(ValueError,'action bound|scope exhausted'):c.run_feedback()
  self.assertEqual(len(c.calls),48);self.assertGreater(abs(c.pitch),.75)
 def test_identity_stale_reused_and_other_axis_changes_cannot_supply_ack(self):
  self.module()
  for mutation in('identity','stale','reused','other_axis'):
   c=FeedbackCase()
   def change(f):
    if not c.calls:return
    if mutation=='identity':f['roles']['botA']['colt_preparation']['animator_id']+=1
    elif mutation=='stale':f['monotonic_started']-=.201
    elif mutation=='reused':f['successful_read_sequence']['index']=0
    else:f['client_roles']['vanilla']['rotation_diagnostic']['local_action_yaw_deg']+=1.
   c.frame_mutation=change
   with self.subTest(mutation=mutation),self.assertRaises(ValueError):c.run_feedback()
   self.assertEqual(len(c.calls),1);self.assertEqual(c.receipt['status'],'FAIL')
 def test_actual_through_release_over_350ms_is_not_a_valid_step(self):
  self.module();c=FeedbackCase();c.hold=.350001
  with self.assertRaisesRegex(ValueError,'release|hold'):c.run_feedback()
  self.assertEqual(len(c.calls),1)
 def test_two_second_ack_late_favorable_read_is_retained_and_rejected(self):
  self.module();c=FeedbackCase()
  def late(f):
   if c.calls and c.receipt.get('role_observations',[{}])[-1].get('phase','').startswith('ack-'):
    c.now=c.call_times[0]+2.001;f['monotonic_started']=f['monotonic_finished']=c.now
    for source in('roles','client_roles'):
     for row in f[source].values():row['game_tick']=c.now+1
  c.frame_mutation=late
  with self.assertRaisesRegex(ValueError,'deadline'):c.run_feedback()
  self.assertEqual(len(c.calls),1);self.assertTrue(c.receipt['role_observations'][-1].get('frame'))
 def test_global_and_runner_deadlines_never_reset_at_entry(self):
  self.module()
  for at in(85.,90.):
   c=FeedbackCase();c.now=at
   with self.subTest(at=at),self.assertRaisesRegex(ValueError,'deadline'):c.run_feedback()
   self.assertEqual(c.calls,[])
 def test_active_twenty_second_deadline_checked_after_slow_preinput_guard(self):
  self.module();c=FeedbackCase();c.before_motion=lambda:setattr(c,'now',20.)
  with self.assertRaisesRegex(ValueError,'deadline|reserve|budget'):c.run_feedback()
  self.assertEqual(c.calls,[])
 def test_worst_case_near_two_second_acks_stop_before_budget_not_after_48(self):
  self.module();c=FeedbackCase(unit_gain=-.02);c.latency=1.7
  with self.assertRaisesRegex(ValueError,'deadline|reserve|budget'):c.run_feedback()
  self.assertTrue(1<=len(c.calls)<=10);self.assertLess(c.now,20.2)
  self.assertTrue(all(t+2.35<=c.receipt['active_deadline']for t in c.call_times))
 def test_copied_observe_act_settled_and_ack_are_exact_parent_ast(self):
  self.module()
  parent=ast.parse((PARENT/'colt_preparation.py').read_text())
  copied=ast.parse(Path(__file__).with_name('a1_pitch_feedback.py').read_text())
  for name in('observe','act','settled','acknowledge'):
   a=[n for n in ast.walk(parent)if isinstance(n,ast.FunctionDef)and n.name==name]
   b=[n for n in ast.walk(copied)if isinstance(n,ast.FunctionDef)and n.name==name]
   self.assertEqual(len(a),1);self.assertEqual(len(b),1)
   self.assertEqual(ast.dump(a[0],include_attributes=False),ast.dump(b[0],include_attributes=False),name)
 def test_direct_native_pitch_delta_cannot_alias_an_extra_360_degrees(self):
  self.module();c=FeedbackCase();original=c.step
  def extra(*args,**kwargs):
   result=original(*args,**kwargs)
   if len(c.calls)==1:c.pitch+=360.
   return result
  c.step=extra
  with self.assertRaisesRegex(ValueError,'unsupported pitch wrap in native ACK'):c.run_feedback()
  self.assertEqual(len(c.calls),1)
 def test_final_actual_pitch_distance_does_not_yaw_normalize_360(self):
  self.module();c=FeedbackCase()
  def extra(frame):
   if c.receipt['role_observations'][-1]['phase']!='pitch-feedback-return':return
   for source in('roles','client_roles'):
    g=frame[source]['vanilla']['colt_preparation']
    g['viewpoint'][4]+=360.;g['last_action_pitch_deg']+=360.
    if source=='client_roles':g['local_action_pitch_deg']+=360.
  c.frame_mutation=extra
  with self.assertRaisesRegex(ValueError,'unsupported pitch wrap in actual endpoint'):c.run_feedback()


class FeedbackJournalTests(unittest.TestCase):
 def test_first_counter_failure_retains_reserved_attempt_without_motion(self):
  m=importlib.import_module('a1_pitch_feedback')
  from a1_passive_xrecord import instrument_transport
  calls=[]
  def fail(unused):raise OSError('counter unavailable')
  t=types.SimpleNamespace(d=123,x=types.SimpleNamespace(XNextRequest=fail),t=types.SimpleNamespace(XTestFakeRelativeMotionEvent=lambda*args:calls.append(args)or 1))
  proxy=instrument_transport(t);j=m.FeedbackJournal(t);proxy.observer=j
  with self.assertRaisesRegex(OSError,'counter unavailable'):proxy.XTestFakeRelativeMotionEvent(123,0,12,0)
  self.assertEqual(calls,[]);self.assertEqual(len(j.attempts),1);self.assertTrue(j.failed)
  self.assertIs(j.attempts[0]['native_invoked'],False);self.assertEqual(j.attempts[0]['failure_stage'],'first_counter')
 def test_native_exception_remains_primary_when_metadata_also_rejects(self):
  m=importlib.import_module('a1_pitch_feedback')
  from a1_passive_xrecord import instrument_transport
  counters=iter((26,31));primary=OSError('original native failure')
  def native(*unused):raise primary
  t=types.SimpleNamespace(d=123,x=types.SimpleNamespace(XNextRequest=lambda unused:next(counters)),t=types.SimpleNamespace(XTestFakeRelativeMotionEvent=native))
  proxy=instrument_transport(t);j=m.FeedbackJournal(t);proxy.observer=j
  with self.assertRaises(OSError)as caught:proxy.XTestFakeRelativeMotionEvent(123,0,12,0)
  self.assertIs(caught.exception,primary);self.assertTrue(j.failed);self.assertEqual(j.attempts[0]['validation_status'],'REJECTED')
 def test_cleanup_cannot_overwrite_previous_private_attempt_file(self):
  m=importlib.import_module('a1_pitch_feedback');t=types.SimpleNamespace(_passive_xrecord_proxy=types.SimpleNamespace(observer=None));j=m.FeedbackJournal(t)
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'pitch-input-attempts.json';p.write_text('preserve')
   r=j.close(d);self.assertTrue(r['errors']);self.assertEqual(p.read_text(),'preserve')
 def test_actual_inherited_proxy_keeps_native_return_on_counter_rejection(self):
  m=importlib.import_module('a1_pitch_feedback')
  from a1_passive_xrecord import instrument_transport
  calls=[];counters=iter((26,31))
  t=types.SimpleNamespace(d=123,x=types.SimpleNamespace(XNextRequest=lambda unused:next(counters)),t=types.SimpleNamespace(XTestFakeRelativeMotionEvent=lambda*args:calls.append(args)or 1))
  proxy=instrument_transport(t);j=m.FeedbackJournal(t);proxy.observer=j
  with self.assertRaisesRegex(ValueError,'counter/clock'):proxy.XTestFakeRelativeMotionEvent(123,0,12,0)
  self.assertEqual(calls,[(123,0,12,0)]);self.assertEqual(j.emissions,[]);self.assertTrue(j.failed)
  self.assertEqual(j.attempts[0]['validation_status'],'REJECTED');self.assertIs(j.attempts[0]['native_invoked'],True)
  self.assertEqual(j.attempts[0]['metadata']['return_value'],1)
 def test_journal_retains_rejected_attempts_without_wire_or_child(self):
  m=importlib.import_module('a1_pitch_feedback')
  self.assertTrue(hasattr(m,'FeedbackJournal'),'missing bounded actual metadata journal')
  transport=types.SimpleNamespace(_passive_xrecord_proxy=types.SimpleNamespace(observer=None))
  j=m.FeedbackJournal(transport);transport._passive_xrecord_proxy.observer=j
  row=dict(function='XTestFakeRelativeMotionEvent',arguments=[123,0,12,0],started_monotonic=1.,finished_monotonic=1.001,sequence_interval=[26,31],return_value=1)
  attempt=j.reserve_attempt(row);attempt.update(native_invoked=True,sequence_before=26,sequence_after=31,validation_status='REJECTED')
  with self.assertRaises(ValueError):j.record_emission(row)
  j.failed=True
  with self.assertRaises(RuntimeError):j.before_input()
  with tempfile.TemporaryDirectory()as d:
   r=j.close(d);self.assertTrue(r['failed']);self.assertEqual(r['attempts'],1);self.assertEqual(r['emissions'],0)
   p=Path(d)/'pitch-input-attempts.json';self.assertEqual(p.stat().st_mode&0o777,0o600)
   self.assertEqual(json.loads(p.read_text())[0]['sequence_after'],31)
   self.assertIsNone(transport._passive_xrecord_proxy.observer);self.assertEqual(j.close(d),r)
 def test_journal_97th_call_stops_before_any_native_invocation(self):
  m=importlib.import_module('a1_pitch_feedback');self.assertTrue(hasattr(m,'FeedbackJournal'))
  j=m.FeedbackJournal(types.SimpleNamespace())
  for unused in range(96):j.reserve_attempt({})
  with self.assertRaises(RuntimeError):j.reserve_attempt({})
  self.assertEqual(len(j.attempts),96);self.assertFalse(any(a['native_invoked']for a in j.attempts))
 def report(self):
  c=FeedbackCase();prep=c.run_feedback();rows=[];attempts=[];phases=[]
  for index,event in enumerate(prep['actions']):
   phase=copy.deepcopy(event['output']['input_phase_timing']);phase['actions']={'vanilla':'look_vertical'};phases.append(phase)
   a=phase['emissions'][0]['started'];row=dict(index=index,function='XTestFakeRelativeMotionEvent',arguments=[123,0,event['pixels'],0],return_value=1,sequence_interval=[index*2+1,index*2+2],started_monotonic=a,finished_monotonic=a,host_epoch_ms=123.)
   rows.append(row);attempts.append(dict(attempt_index=index,native_invoked=True,validation_status='ACCEPTED',sequence_before=index*2+1,sequence_after=index*2+2,metadata={k:v for k,v in row.items()if k!='index'}))
  return dict(status=prep['status'],shooter_preparation=prep,observer_mode='pitch-feedback',qualified=False,normal_route_or_fire=False,diagnostic_only=True,collector_requested=False,errors=[],restoration={'restored':True},post_close_logs={'accepted':True},cleanup={x:{'closed':True}for x in('server','vanilla','botA')},displays={154:{'closed':True},155:{'closed':True}},input_phase_timings=phases,pitch_journal=dict(errors=[],failed=False,no_wire_proof=True,attempts=len(attempts),emissions=len(rows),attempt_rows=attempts,emission_rows=rows))
 def test_completed_result_requires_actual_motion_metadata_and_cleanup(self):
  m=importlib.import_module('a1_pitch_feedback');self.assertTrue(hasattr(m,'journal_complete'))
  report=self.report();verdict=types.SimpleNamespace(reasons=('window_not_passed',))
  self.assertTrue(m.journal_complete(report,verdict))
  for change in('missing','wrong_pixels','wrong_counter','rejected','late','frida','restore','no_acked'):
   r=copy.deepcopy(report)
   if change=='missing':r['pitch_journal']['attempt_rows'].pop()
   elif change=='wrong_pixels':r['pitch_journal']['emission_rows'][0]['arguments'][2]=-12
   elif change=='wrong_counter':r['pitch_journal']['attempt_rows'][0]['sequence_after']+=1
   elif change=='rejected':r['pitch_journal']['attempt_rows'][0]['validation_status']='REJECTED'
   elif change=='late':r['pitch_journal']['emission_rows'][0]['finished_monotonic']+=1
   elif change=='frida':r['collector_arm']={}
   elif change=='restore':r['restoration']['restored']=False
   else:r['shooter_preparation']['actions_acked']-=1
   with self.subTest(change=change):self.assertFalse(m.journal_complete(r,verdict))


if __name__=='__main__':unittest.main()
