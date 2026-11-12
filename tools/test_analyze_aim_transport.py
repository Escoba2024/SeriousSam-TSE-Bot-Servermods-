import unittest
from analyze_aim_transport import analyze
A='[BotAimTrace] local=3 tick={tick} entity=572 generation=5 valid=1 target=4 visible=1 intent=(-1.68,0.18) residual=(0.8,0.1) human_fire=0 weapon=2\n'
T='[BotAimTransport] local=3 tick={tick} entity=572 input_entity=572 same_entity=1 last=(25.38,34.40) local_before=(-47.2,34.30) requested=(23.70,34.58) precompose=(70.90,0.28) local_after=(23.70,34.58) composed=(23.70,34.58) nav=0 human_fire=0 final_fire=0 current=2 wanted=2\n'
class Analysis(unittest.TestCase):
 def test_transport_rebases_large_delta_without_claiming_hit_or_cause(self):
  r=analyze((A+T).format(tick=540));self.assertEqual(r['matched'],1)
  self.assertAlmostEqual(r['events'][0]['local_accumulator_delta'][0],70.9)
  self.assertAlmostEqual(r['events'][0]['policy_to_request_error'][0],0)
  self.assertFalse(r['native_execution_proven']);self.assertFalse(r['cause_proven'])
 def test_gaps_missing_and_duplicate_rows(self):
  self.assertEqual(analyze(A.format(tick=1))['missing_transport'],1)
  with self.assertRaises(ValueError):analyze(A.format(tick=1)*2)
  r=analyze((A+T).format(tick=1)+(A+T).format(tick=3));self.assertEqual(r['consecutive_pairs'],0)
 def test_nonfinite_and_identity_mismatch_rejected(self):
  for bad in (T.replace('70.90','nan'),T.replace('entity=572 input','entity=111 input')):
   with self.assertRaises(ValueError):analyze((A+bad).format(tick=1))
 def test_nav_and_invalid_geometry_do_not_become_aim_transport_claims(self):
  r=analyze((A.replace('valid=1','valid=0')+T).format(tick=1));self.assertIsNone(r['events'][0]['policy_to_request_error'])
  r=analyze((A+T.replace('nav=0','nav=1')).format(tick=1));self.assertIsNone(r['events'][0]['policy_to_request_error'])
if __name__=='__main__':unittest.main()
