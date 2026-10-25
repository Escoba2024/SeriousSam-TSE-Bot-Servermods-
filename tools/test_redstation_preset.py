import unittest
from unittest.mock import patch
import qualify_integrated_wine as q
import redstation_preset as p
class RedStationPresetTests(unittest.TestCase):
 def test_changes_exactly_requested_native_values(self):
  source='\n'.join('persistent extern user INDEX '+k+'=(INDEX)'+str(v)+';' for k,v in [('gam_iStartDifficulty',1),('gam_bInfiniteAmmo',0),('gam_iBlood',2),('gam_bGibs',1)])+'\nother=73;'
  got=p.symbols(source)
  for k,v in [('gam_iStartDifficulty',2),('gam_bInfiniteAmmo',1),('gam_iBlood',3),('gam_bGibs',0)]:self.assertIn(k+'=(INDEX)'+str(v)+';',got)
  self.assertIn('other=73;',got)
 def test_rejects_missing_native_symbol(self):
  with self.assertRaises(ValueError):p.symbols('gam_iStartDifficulty=(INDEX)1;')
 def test_rejects_duplicate_native_symbol(self):
  text='\n'.join(k+'=(INDEX)1;' for k in ['gam_iStartDifficulty','gam_bInfiniteAmmo','gam_iBlood','gam_bGibs','gam_bGibs'])
  with self.assertRaises(ValueError):p.symbols(text)
 def test_actual_map_and_settings_are_in_start_script(self):
  t=p.server_begin()
  for s in ['RedStation.wld','gam_iStartDifficulty=2;','gam_bInfiniteAmmo=1;','gam_iBlood=3;','gam_bGibs=0;','gam_ctMaxPlayers=16;']:self.assertIn(s,t)
 def test_eight_colored_unique_names_reproducible_from_pool(self):
  pool=[dict(nickname='Player'+str(i),color='80D8FF') for i in range(24)]
  a=p.roster(pool,12);self.assertEqual(a,p.roster(pool,12));self.assertEqual(len(a),8);self.assertEqual(len(set(a)),8)
  self.assertNotEqual(a,p.roster(pool,13))
  self.assertTrue(all(x.startswith('BOT-^c80D8FF') and x.endswith('^r') and len(x)<=32 for x in a))
 def test_public_readiness_accepts_native_stripped_colors(self):
  names=['BOT-P'+str(i) for i in range(8)]
  with patch.object(q,'ROSTER',['BOT-^c80D8FFP'+str(i)+'^r' for i in range(8)]):
   self.assertTrue(q.population_ready({'numplayers':'8'},names,8,True))
 def test_public_readiness_rejects_color_only_duplicates(self):
  names=['BOT-P'+str(i) for i in range(7)]+['^c80D8FFBOT-P0^r']
  with patch.object(q,'ROSTER',['BOT-P'+str(i) for i in range(7)]):
   self.assertFalse(q.population_ready({'numplayers':'8'},names,8,True))
 def test_colored_roster_keeps_existing_bot_identification(self):
  a=p.roster([dict(nickname='Player'+str(i),color='80D8FF') for i in range(24)],12)
  self.assertTrue(all(x.startswith('BOT-') for x in a))
 def test_rejects_unsafe_or_duplicate_pool_names(self):
  for pool in [[dict(nickname='bad;Quit()',color='80D8FF')]*8,[dict(nickname='Same',color='80D8FF')]*8]:
   with self.assertRaises(ValueError):p.roster(pool,1)
if __name__=='__main__':unittest.main()

class SsamPublicMessagesTests(unittest.TestCase):
 def test_server_identity_and_motd(self):
  self.assertIn('gam_strSessionName="ssam.ai | Red Station | Human Bots";',p.server_begin())
  self.assertIn('ser_strMOTD="Welcome to ssam.ai',p.server_startup(''))
  self.assertIn('#SamIsBack',p.server_startup(''))
 def test_five_minute_announcement_has_guard(self):
  startup=p.server_startup('ORIGINAL;\n')
  self.assertTrue(startup.startswith('ORIGINAL;\n'))
  self.assertIn('cmd_cmdOnTick=',startup)
  self.assertIn('300',startup)
  self.assertIn('Say(',startup)
  self.assertIn('tmp_ai[9]',startup)
  self.assertNotIn('user INDEX tmp_ai[9]',startup)
 def test_dedicated_config_server_only(self):
  from pathlib import Path
  import tempfile
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp)
   for d in ['Scripts/Dedicated/BotTest']:(base/d).mkdir(parents=True)
   (base/'Scripts/PersistentSymbols.ini').write_text('\n'.join('persistent user INDEX '+k+'=(INDEX)0;' for k in p.VALUES))
   (base/'Scripts/Dedicated/BotTest/1_begin.ini').write_text('previous')
   (base/'Scripts/Dedicated_startup.ini').write_text('base=1;\n')
   with patch.object(Path,'is_mount',return_value=True):p.configure_overlay(base,'server')
   self.assertIn('ssam.ai', (base/'Scripts/Dedicated/BotTest/1_begin.ini').read_text())
   self.assertIn('ser_strMOTD', (base/'Scripts/Dedicated_startup.ini').read_text())
   self.assertEqual((base/'Scripts/PersistentSymbols.ini').read_text().count('gam_bInfiniteAmmo'),1)
