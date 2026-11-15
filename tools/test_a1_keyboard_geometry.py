"""Pure policy replay only: simulated frames never qualify native input."""
import copy
import importlib
from pathlib import Path
import sys
import unittest
sys.path.append('/srv/tse-a1-xres-lifecycle-root-frozen-20261115')
from test_colt_preparation import ColtCase


class KeyCase(ColtCase):
 def __init__(self,mode='normal'):
  super().__init__();self.key_mode=mode;self.x=-12.;self.hook=None
 def frame(self):
  frame=super().frame()
  for source in('roles','client_roles'):frame[source]['vanilla']['placement'][0]=self.x
  if self.hook:self.hook(frame)
  return frame
 def step(self,role,control,seconds,*,before_press=lambda:None):
  before_press();at=self.now;self.actions.append((control,seconds));self.now+=seconds
  delta={'yaw_left':3.,'yaw_right':-3.,'pitch_up':3.,'pitch_down':-3.}.get(control)
  if self.key_mode=='missing_ack'and control=='yaw_left':delta=0.
  if self.key_mode=='coarse_return'and control=='yaw_right':delta=-6.
  if control.startswith('yaw'):
   self.local+=delta;self.server=self.local;self.view+=delta
  elif control=='forward':
   self.body+=self.view;self.view=0.;self.x+=.5
   if self.key_mode=='extra_after_forward':self.local+=1.;self.server=self.local
  else:self.pitch+=delta
  if self.key_mode=='partial_step':raise RuntimeError('actual step failure model')
  event=dict(role=role,control=control,pixels=None,started=at,finished=at,request_confirmed=True)
  return dict(released=True,input_phase_timing=dict(status='PASS',finished=self.now,release_started=self.now,emissions=[event]))
 def run_keys(self):
  m=importlib.import_module('a1_keyboard_geometry');return m.run(self.frame,self.step,lambda:self.now,self.sleep,self.receipt,started=0.)


class KeyboardGeometry(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('a1_keyboard_geometry'),'missing keyboard angle policy')
  return importlib.import_module('a1_keyboard_geometry')
 def test_exact_six_action_order_and_no_fire_or_mouse_or_extra_forward(self):
  m=self.module();scope=m.KeyboardScope()
  for c in m.ORDER:scope.admit('vanilla',c,.1)
  with self.assertRaises(ValueError):scope.admit('vanilla','yaw_left',.1)
  for role,control,seconds in(('botA','yaw_left',.1),('vanilla','fire',.1),('vanilla','forward',.1),('vanilla','yaw_left',.1001),('vanilla','look_left',.1)):
   with self.assertRaises(ValueError):m.KeyboardScope().admit(role,control,seconds)
 def test_six_steps_use_forward_before_body_comparison_and_allow_actual_translation(self):
  m=self.module();c=KeyCase();r=c.run_keys();self.assertEqual([a for a,t in c.actions],list(m.ORDER));self.assertEqual(r['status'],'PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY')
  self.assertEqual(len(r['yaw']),2);self.assertEqual(len(r['pitch']),2);self.assertEqual(r['yaw'][0]['body_delta_yaw_deg'],3.)
  self.assertGreater(r['yaw'][0]['after']['roles']['vanilla']['placement'][0],r['yaw'][0]['before']['roles']['vanilla']['placement'][0])
  for key in('qualified','a1_pass','mouse_gain_fixed','input_once_proven','actual_shot_proven'):self.assertIs(r[key],False)
 def test_missing_ack_coarse_return_and_extra_after_forward_stop_without_retry(self):
  self.module()
  for mode in('missing_ack','coarse_return','extra_after_forward','partial_step'):
   c=KeyCase(mode)
   with self.subTest(mode=mode),self.assertRaises((ValueError,RuntimeError)):c.run_keys()
   self.assertEqual(c.receipt['status'],'FAIL');self.assertLessEqual(len(c.actions),4);self.assertNotIn(('fire',.1),c.actions)
 def test_stale_life_world_and_wrong_process_frames_never_count_as_ack(self):
  self.module()
  for what in('stale','life','process','other_axis','moving','uninitialized'):
   c=KeyCase()
   def mutate(f):
    if not c.actions:return
    if what=='stale':f['monotonic_started']-=.3
    elif what=='life':f['client_roles']['vanilla']['spawned_tick']=.5
    elif what=='process':f['vanilla_process_identity']=[999,1999]
    elif what=='other_axis':f['client_roles']['vanilla']['colt_preparation']['local_action_pitch_deg']=1.
    elif what=='moving':f['roles']['vanilla']['placement'][0]+=1.
    else:f['roles']['vanilla']['rotation_diagnostic']['player_flags']=0x401
   c.hook=mutate
   with self.subTest(what=what),self.assertRaises(ValueError):c.run_keys()
   self.assertEqual(len(c.actions),1)
 def test_late_or_missing_release_receipt_cannot_complete(self):
  self.module();c=KeyCase();step=c.step
  def missing(*args,**kwargs):r=step(*args,**kwargs);r['released']=False;return r
  c.step=missing
  with self.assertRaises(ValueError):c.run_keys()
  self.assertEqual(len(c.actions),1)
 def test_shared85second_window_not_reset_at_keyboard_entry(self):
  self.module();c=KeyCase();c.now=85.
  with self.assertRaises(ValueError):c.run_keys()
  self.assertEqual(c.actions,[])
 def test_failure_counts_distinguish_admission_step_release_and_native_ack(self):
  self.module()
  for mode,released in(('partial_step',0),('missing_ack',1)):
   c=KeyCase(mode)
   with self.subTest(mode=mode),self.assertRaises((ValueError,RuntimeError)):c.run_keys()
   self.assertEqual(c.receipt['actions_admitted'],1)
   self.assertEqual(c.receipt['actions_attempted'],1)
   self.assertEqual(c.receipt['actions_released'],released)
   self.assertEqual(c.receipt['actions_acked'],0)
   self.assertEqual(c.receipt['actions_completed'],0)
  c=KeyCase();r=c.run_keys()
  self.assertEqual([r[k]for k in('actions_admitted','actions_attempted','actions_released','actions_acked','actions_completed')],[6]*5)


if __name__=='__main__':unittest.main()
