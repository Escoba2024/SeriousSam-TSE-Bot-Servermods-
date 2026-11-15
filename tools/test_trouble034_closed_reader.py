"""Exact closed-case Source binding and new budgets, no Native/evidence reads."""
import ast,unittest
from pathlib import Path
import audit_trouble034_closed as reader
class Adapter(unittest.TestCase):
 def test_coordinator_json_dependency_before_raw(self):
  self.assertEqual(reader.json.dumps({"no_raw":True}),'{"no_raw": true}')
 def test_whole_existing_reader_inverse(self):
  raw=reader.BASE.read_bytes();new=reader.adapt(raw)
  self.assertEqual(reader.adapt(new,True),raw)
  for bad in [raw+b'\n',new,raw.replace(b'LIMIT=128',b'LIMIT=129')]:
   with self.assertRaises(ValueError):reader.adapt(bad)
 def test_actual_root_host_and_restore_paths_are034(self):
  raw=reader.adapt(reader.BASE.read_bytes());tree=ast.parse(raw)
  strings=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and isinstance(n.value,str)]
  for name in ['navigation034-trouble-host/receipt.json','navigation034-trouble-root-restore.json']:
   self.assertIn('/srv/tse-cecil-rollout-evidence-20261114/'+name,strings)
  self.assertFalse(any('navigation032-trouble'in s for s in strings))
 def test_actual_new_case_and_unchanged_life_methods(self):
  raw=reader.adapt(reader.BASE.read_bytes());tree=ast.parse(raw);out={}
  for n in tree.body:
   if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['CASE','PACKAGE','OUT','RESULT','LIMIT','OUTPUT']:
    v=n.value;out[n.targets[0].id]=ast.literal_eval(v.args[0])if isinstance(v,ast.Call)else eval(compile(ast.Expression(v),'pure','eval'),{})
  self.assertEqual(out['RESULT'],'bb91a86973a2241ef0eddaf541c3f3160c73ec380811236534068dbf92a458e5')
  self.assertEqual(out['LIMIT'],128*1024*1024);self.assertEqual(out['OUTPUT'],8*1024*1024)
  self.assertEqual(out['OUT'],'/srv/tse-trouble034-closed-audit-evidence-20261115')
  self.assertIn('183149',out['CASE']);self.assertIn('034-trouble300',out['PACKAGE'])
if __name__=='__main__':unittest.main(verbosity=2)
