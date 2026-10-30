import importlib.util
from pathlib import Path
import tempfile
import unittest
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m2_duel',HERE/'m2_duel_preset.py')
class Preset(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
 def test_private_server_has_original_small_map_and_finite_ammo(self):
  text=self.m.server_begin()
  self.assertIn('DM_LittleTrouble.wld',text)
  self.assertIn('gam_bInfiniteAmmo=0;',text)
  self.assertIn('gam_iStartMode=2;',text)
  self.assertNotIn('ser_iKickOnSyncBad',text)
 def test_symbols_change_only_ammo_setting(self):
  original='persistent extern user INDEX gam_bInfiniteAmmo=(INDEX)1;\nnet_iPort=27280;\n'
  actual=self.m.symbols(original)
  self.assertEqual(actual,'persistent extern user INDEX gam_bInfiniteAmmo=(INDEX)0;\nnet_iPort=27280;\n')
  with self.assertRaises(ValueError):self.m.symbols('unknown format')
 def test_control_bindings_preserve_native_action_commands(self):
  actions=[('ctl_bMoveForward','W','Arrow Up'),('ctl_bMoveBackward','S','Arrow Down'),('ctl_bTurnLeft','None','None'),('ctl_bTurnRight','None','None'),('ctl_bTurnUp','Mouse Button 4','None'),('ctl_bTurnDown','Mouse Button 5','None'),('ctl_bMoveLeft','Arrow Left','None'),('ctl_bMoveRight','Arrow Right','None')]
  source='\n'.join('Button\n Name: TTRS Test\n Key1: '+key+'\n Key2: '+second+'\n Pressed: '+cmd+' = 1;\n Released: '+cmd+' = 0;\n' for cmd,key,second in actions)
  result=self.m.controls_for_probe(source)
  import re
  self.assertEqual(re.findall(r'(?:Pressed|Released):[^\n]+',result),re.findall(r'(?:Pressed|Released):[^\n]+',source))
  expected=['W','S','Arrow Left','Arrow Right','Arrow Up','Arrow Down','A','D']
  self.assertEqual(re.findall(r'Key1: ([^\n]+)',result),expected)
  self.assertEqual(re.findall(r'Key2: ([^\n]+)',result),['None']*8)
  with self.assertRaises(ValueError):self.m.controls_for_probe(source+source)
 def test_original_extra_strafe_aliases_are_disabled_without_changing_actions(self):
  commands=['ctl_bMoveForward','ctl_bMoveBackward','ctl_bTurnLeft','ctl_bTurnRight','ctl_bTurnUp','ctl_bTurnDown','ctl_bMoveLeft','ctl_bMoveRight','ctl_bMoveLeft','ctl_bMoveRight']
  source=''.join('Button\n Name: TTRS Test\n Key1: None\n Key2: None\n Pressed: '+cmd+' = 1;\n Released: '+cmd+' = 0;\n' for cmd in commands)
  result=self.m.controls_for_probe(source)
  import re
  self.assertEqual(re.findall(r'Key1: ([^\n]+)',result),['W','S','Arrow Left','Arrow Right','Arrow Up','Arrow Down','A','D','None','None'])
  self.assertEqual(re.findall(r'(?:Pressed|Released):[^\n]+',result),re.findall(r'(?:Pressed|Released):[^\n]+',source))
 def test_real_directory_is_never_treated_as_overlay(self):
  with tempfile.TemporaryDirectory() as temp:
   game=Path(temp);(game/'marker').write_text('preserve')
   with self.assertRaises(RuntimeError):self.m.configure_overlay(game,'vanilla')
   self.assertEqual((game/'marker').read_text(),'preserve')
 def test_keyboard_probe_removes_only_mouse_look_axes(self):
  source='Axis "look u/d" "mouse Y" 50 0 NotInverted Relative NotSmooth\nAxis "turn l/r" "mouse X" 50 0 NotInverted Relative NotSmooth\nAxis "move f/b" "None" 50 0 NotInverted Absolute NotSmooth\n'
  result=self.m.keyboard_look(source)
  self.assertEqual(result,source.replace('"mouse Y"','"None"').replace('"mouse X"','"None"'))
  with self.assertRaises(ValueError):self.m.keyboard_look(source+source)
  with self.assertRaises(ValueError):self.m.keyboard_look('unknown controls')
if __name__=='__main__':unittest.main()
