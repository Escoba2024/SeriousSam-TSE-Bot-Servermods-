import unittest
from pathlib import Path
from export_rules import extract
ROOT=Path(__file__).resolve().parents[1]/'reference'
class RuleTests(unittest.TestCase):
 def test_weapon_schema_and_known_values(self):
  rows=extract(ROOT)
  self.assertEqual(len(rows),30)
  for mode in ('Deathmatch','Cooperative'):
   self.assertEqual({r['weapon_id'] for r in rows if r['mode']==mode},set(range(15)))
  dm={r['weapon']:r for r in rows if r['mode']=='Deathmatch'}
  self.assertEqual(dm['WEAPON_COLT']['max_distance'],500)
  self.assertEqual(dm['WEAPON_GRENADELAUNCHER']['shot_frequency'],1)
  self.assertEqual(dm['WEAPON_NONE']['shot_frequency'],-1)
  self.assertEqual(dm['WEAPON_SNIPER']['damage_rating'],150)
if __name__=='__main__':unittest.main()
