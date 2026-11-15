import unittest
from yodeller035_kill_tokens import parse_kills
class Tokens(unittest.TestCase):
 def test_exact_token_custody_and_unique_join(self):
  row=parse_kills('Alpha poured lead into Beta',{'Alpha':{0},'Beta':{2}})[0]
  self.assertEqual(row.get('tokens'),['Alpha','Beta']);self.assertEqual((row['killer_slot'],row['victim_slot']),(0,2))
 def test_colour_whitespace_not_blindly_normalized(self):
  row=parse_kills('^cFF0000Alpha^r poured lead into Beta ',{'Alpha':{0},'Beta':{2}})[0]
  self.assertEqual(row.get('tokens'),['^cFF0000Alpha^r','Beta ']);self.assertIsNone(row['killer_slot']);self.assertIsNone(row['victim_slot'])
 def test_duplicate_query_name_stays_unknown(self):
  row=parse_kills('Alpha poured lead into Beta',{'Alpha':{0,5},'Beta':{2}})[0]
  self.assertIsNone(row['killer_slot'])
 def test_selfblast_priority(self):
  row=parse_kills('Alpha blew himself away',{'Alpha':{0}})
  self.assertEqual(len(row),1);self.assertEqual(row[0]['kind'],'selfblast');self.assertEqual(row[0]['tokens'],['Alpha']);self.assertIsNone(row[0]['killer_slot']);self.assertEqual(row[0]['victim_slot'],0)
 def test_environment_and_unknown_format(self):
  rows=parse_kills('Alpha went over the edge\nnot a death record',{'Alpha':{0}})
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['kind'],'abyss')
