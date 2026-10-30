"""Exercise real staged CLI/config output; never pass --execute."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import re
from types import SimpleNamespace
import unittest
HERE=Path(__file__).resolve().parents[1]
class Staging(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)/'harness'
  if '--baseline-stage' in sys.argv:
   cls.root.mkdir()
   data=subprocess.check_output(['git','-C',str(HERE.parents[2]),'archive','c798853db18e39504cc9ab565d3ef78292610155','tools','poc/scripts/Phase1HumanAI.ini'])
   subprocess.run(['tar','-x','-C',str(cls.root)],input=data,check=True)
  else:
   s=importlib.util.spec_from_file_location('m2_stage',HERE/'stage_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.stage(cls.root)
  sys.path.insert(0,str(cls.root/'tools'))
  from test_bot_session_executor import config
  cls.config=staticmethod(config)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def cli(self,count,duration,extra=()):
  p=self.root/'test-config.json';config=self.config(count);config['strafe_scale']=.5;p.write_text(json.dumps(config))
  return subprocess.run(['python3',self.root/'tools/qualify_bot_sessions.py','--config',p,'--runtime','/srv/tse-session-qualification-m2-fixture','--duration',str(duration),*extra],capture_output=True,text=True)
 def test_refuses_more_than_two_bots_even_without_execute(self):
  self.assertNotEqual(self.cli(3,180).returncode,0)
 def test_refuses_long_run_even_without_execute(self):
  self.assertNotEqual(self.cli(1,301).returncode,0)
 def test_explicit_small_m2_dry_run_is_inert(self):
  p=self.cli(2,180,['--m2-combat','--cecil-p1']);self.assertEqual(p.returncode,0,p.stderr)
  self.assertEqual(json.loads(p.stdout)['status'],'DRY_RUN_NO_RUNTIME')
  self.assertFalse(Path('/srv/tse-session-qualification-m2-fixture').exists())
 def test_m2_requires_explicit_p1(self):
  self.assertNotEqual(self.cli(2,180,['--m2-combat']).returncode,0)
 def test_explicit_profiles_are_accepted_without_starting_runtime(self):
  for tier,persona in ((1,0),(5,5)):
   p=self.cli(1,60,['--m2-combat','--cecil-p1','--m2-skill',str(tier),'--m2-persona',str(persona)])
   self.assertEqual(p.returncode,0,p.stderr)
   self.assertEqual(json.loads(p.stdout)['status'],'DRY_RUN_NO_RUNTIME')
 def test_out_of_range_profiles_are_rejected(self):
  for flag,value in (('--m2-skill','0'),('--m2-skill','6'),('--m2-persona','-1'),('--m2-persona','6')):
   self.assertNotEqual(self.cli(1,60,['--m2-combat','--cecil-p1',flag,value]).returncode,0)
 def test_all_thirty_profiles_reach_generated_script_before_enable(self):
  path=self.root/'tools/qualify_bot_sessions.py';source=path.read_text()
  begin=source.index('                script=(Path(__file__)')
  end=source.index("                (game/'Scripts/Session.ini').write_text(script)",begin)
  for tier in range(1,6):
   for persona in range(6):
    scope=dict(re=re,Path=Path,__file__=str(path),startup_script=lambda _:'bot_iProfile0=0;\n',
      self=SimpleNamespace(p=SimpleNamespace(config=dict(log_every_ticks=20,debug_logging=True,exploratory_search=False,strafe_scale=.5)),
      identities={'bot':{}},cecil_p1=True,m2_combat=True,m2_skill=tier,m2_persona=persona),role='bot')
    exec(textwrap.dedent(source[begin:end]),scope)
    script=scope['script']
    self.assertIn('bot_iSkillTier='+str(tier)+';',script)
    self.assertIn('bot_iPersonality='+str(persona)+';',script)
    self.assertTrue(script.rstrip().endswith('bot_bEnabled=1;'))
 def test_generated_configuration_enables_only_after_all_latched_settings(self):
  path=self.root/'tools/qualify_bot_sessions.py';source=path.read_text()
  begin=source.index('                script=(Path(__file__)')
  end=source.index("                (game/'Scripts/Session.ini').write_text(script)",begin)
  config=dict(log_every_ticks=20,debug_logging=True,exploratory_search=False,strafe_scale=.5)
  scope=dict(re=re,Path=Path,__file__=str(path),startup_script=lambda _:'bot_iProfile0=0;\n',role='bot',
             self=SimpleNamespace(p=SimpleNamespace(config=config),identities={'bot':{}},cecil_p1=True,m2_combat=True,m2_skill=5,m2_persona=2))
  exec(textwrap.dedent(source[begin:end]),scope)
  script=scope['script'];assignments=re.findall(r'(?m)^\s*(bot_\w+)\s*=\s*([^;]+);',script)
  enables=[i for i,pair in enumerate(assignments) if pair[0]=='bot_bEnabled' and pair[1].strip()=='1']
  self.assertEqual(enables,[len(assignments)-1])
  effective={k:v.strip() for k,v in assignments}
  for key in ('bot_bCecilP1','bot_bCombatWeapon2','bot_bCombatLead2','bot_bCombatStrafe2'):
   self.assertEqual(effective[key],'1')
  self.assertEqual(effective['bot_iSkillTier'],'5');self.assertEqual(effective['bot_iPersonality'],'2')
 def test_no_overwrite(self):
  if '--baseline-stage' in sys.argv:self.skipTest('baseline has no M2 stager')
  s=importlib.util.spec_from_file_location('m2_stage_again',HERE/'stage_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  with self.assertRaises(ValueError):m.stage(self.root)
if __name__=='__main__':
 baseline='--baseline-stage' in sys.argv
 args=[x for x in sys.argv if x!='--baseline-stage']
 # Keep baseline mode available to setUpClass without forwarding it to unittest.
 runner=unittest.TextTestRunner(verbosity=2)
 result=runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(Staging));raise SystemExit(not result.wasSuccessful())
