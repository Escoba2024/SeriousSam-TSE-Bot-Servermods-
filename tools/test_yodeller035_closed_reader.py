import copy,json,unittest
import audit_yodeller035_closed as a
class Admission(unittest.TestCase):
 def metadata(self):
  return {k:json.loads(a.small(p))for k,p in {'result':a.CASE/'result.json','manifest':a.PACKAGE/'source-manifest.json','host':a.HOST,'restore':a.RESTORE,'build':a.BUILD/'manifest.json'}.items()}
 def test_actual_yodeller600_diag0_closed_case(self):self.assertTrue(a.validate_metadata(self.metadata()))
 def test_wrong_map_diag_duration_or_case_rejected(self):
  original=self.metadata()
  for target,key,value in [('result','map_key','trouble'),('result','diagnostics_enabled',True),('restore','case_result','old-case')]:
   m=copy.deepcopy(original);m[target][key]=value
   with self.assertRaises(ValueError):a.validate_metadata(m)
  m=copy.deepcopy(original);m['manifest']['comparison']['seconds']=300
  with self.assertRaises(ValueError):a.validate_metadata(m)
 def test_whole_source_inverse_and_mutation(self):
  raw=a.small(a.BASE);changed=a.adapt(raw);self.assertEqual(a.adapt(changed,True),raw)
  with self.assertRaises(ValueError):a.adapt(raw+b'\n')
  self.assertIn(str(a.HOST).encode(),changed);self.assertIn(str(a.RESTORE).encode(),changed)
  self.assertNotIn(b"map='hole'",changed)
