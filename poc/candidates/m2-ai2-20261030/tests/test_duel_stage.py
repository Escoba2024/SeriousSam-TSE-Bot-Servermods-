import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import sqlite3
from types import SimpleNamespace
import unittest
HERE=Path(__file__).resolve().parents[1]
class DuelStage(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('duel_stager',HERE/'stage_duel.py');cls.m=importlib.util.module_from_spec(s);s.loader.exec_module(cls.m)
  cls.temp=tempfile.TemporaryDirectory();cls.root=cls.m.stage(Path(cls.temp.name)/'harness')
  sys.path.insert(0,str(cls.root/'tools'))
  from test_bot_session_executor import config
  cls.config=staticmethod(config)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def cli(self,count=1,duration=120):
  c=self.config(count);c['strafe_scale']=.5;p=self.root/'config.json';p.write_text(json.dumps(c))
  return subprocess.run(['python3',self.root/'tools/qualify_bot_sessions.py','--config',p,'--runtime','/srv/tse-session-qualification-m2-unit-duel','--duration',str(duration),'--m2-combat','--cecil-p1','--preset','duel'],capture_output=True,text=True)
 def test_private_duel_dry_run_is_inert(self):
  r=self.cli();self.assertEqual(r.returncode,0,r.stderr)
  self.assertEqual(json.loads(r.stdout)['status'],'DRY_RUN_NO_RUNTIME')
  self.assertFalse(Path('/srv/tse-session-qualification-m2-unit-duel').exists())
 def test_actual_native_transport_accepts_duel_without_launching(self):
  s=importlib.util.spec_from_file_location('m2_staged_runner',self.root/'tools/qualify_bot_sessions.py')
  m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  with sqlite3.connect(':memory:') as db:
   transport=m.WineTransport(self.root,SimpleNamespace(db=db),27280,':178',None,preset='duel',cecil_p1=True,m2_combat=True)
   self.assertEqual(transport.preset,'duel');self.assertFalse(transport.procs)
  source=(self.root/'tools/qualify_bot_sessions.py').read_text()
  self.assertIn("state.get('mapname')!='Little Trouble'",source)
  self.assertIn("observer_fps_cap=20 if",source)
 def test_original_two_bot_and_duration_caps_are_preserved(self):
  self.assertNotEqual(self.cli(count=3).returncode,0)
  self.assertNotEqual(self.cli(duration=301).returncode,0)
 def test_existing_stage_is_never_overwritten(self):
  with self.assertRaises(ValueError):self.m.stage(self.root)
 def test_manifest_pins_staged_source_bytes(self):
  import hashlib
  m=json.loads((self.root/'SOURCE_MANIFEST.json').read_text())
  self.assertEqual(m['scenario'],'ORIGINAL_RETAIL_LITTLE_TROUBLE_FINITE_AMMO_OWN_INPUT')
  for name,digest in m['files_sha256'].items():
   self.assertEqual(hashlib.sha256((self.root/name).read_bytes()).hexdigest(),digest)
 def test_explicit_original_redstation_keeps_finite_ammo_and_query_pin(self):
  with tempfile.TemporaryDirectory() as temp:
   root=self.m.stage(Path(temp)/'harness',map_name='redstation')
   runner=(root/'tools/qualify_bot_sessions.py').read_text()
   self.assertIn("state.get('mapname')!='Red Station'",runner)
   preset=(root/'tools/m2_duel_preset.py').read_text()
   # Exact basename from pinned PR73 redstation_preset.server_begin(), rather
   # than extrapolating LittleTrouble's DM_ naming convention.
   self.assertIn('Deathmatch\\\\RedStation.wld',preset)
   self.assertNotIn('DM_RedStation.wld',preset)
   self.assertIn('gam_bInfiniteAmmo=0;',preset)
   self.assertEqual(json.loads((root/'SOURCE_MANIFEST.json').read_text())['map'],'redstation')
 def test_unknown_map_is_rejected_before_creating_output(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)/'harness'
   with self.assertRaises(ValueError):self.m.stage(root,map_name='unverified')
   self.assertFalse(root.exists())
 def test_original_hole_map_has_explicit_level_and_query_name(self):
  # Filename and WLIF title checked in the licensed original level archive.
  with tempfile.TemporaryDirectory() as temp:
   root=self.m.stage(Path(temp)/'harness',map_name='hole')
   self.assertIn("state.get('mapname')!='Hole'",(root/'tools/qualify_bot_sessions.py').read_text())
   preset=(root/'tools/m2_duel_preset.py').read_text()
   self.assertIn('Deathmatch\\\\Hole.wld',preset)
   self.assertIn('gam_bInfiniteAmmo=0;',preset)
   self.assertEqual(json.loads((root/'SOURCE_MANIFEST.json').read_text())['map'],'hole')
 def test_original_compound_query_uses_kuntakinte_level_filename(self):
  # Original Retail level discovery reports KuntaKinte.wld as 'Compound'.
  with tempfile.TemporaryDirectory() as temp:
   root=self.m.stage(Path(temp)/'harness',map_name='compound')
   self.assertIn("state.get('mapname')!='Compound'",(root/'tools/qualify_bot_sessions.py').read_text())
   preset=(root/'tools/m2_duel_preset.py').read_text()
   self.assertIn('KuntaKinte.wld',preset)
   self.assertIn('gam_bInfiniteAmmo=0;',preset)
if __name__=='__main__':unittest.main()
