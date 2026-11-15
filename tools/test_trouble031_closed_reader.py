"""New closed-case retarget only; do not execute acquire/main/Raw readers."""
import ast,hashlib,importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE/'audit_hole031_closed.py'
def actual_source():
 p=HERE/'audit_trouble031_closed.py'
 if not p.exists():return BASE.read_bytes()
 import audit_trouble031_closed as t
 return t.adapt(BASE.read_bytes())
def constants(source):
 tree=ast.parse(source);out={}
 for n in tree.body:
  if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name):
   if n.targets[0].id in ['CASE','PACKAGE','OUT','RESULT','LIMIT','OUTPUT']:
    v=n.value
    out[n.targets[0].id]=ast.literal_eval(v.args[0])if isinstance(v,ast.Call)else eval(compile(ast.Expression(v),'pure-constant','eval'),{})
 return out
class ClosedBinding(unittest.TestCase):
 def test_actual_case_and_result_retarget(self):
  c=constants(actual_source())
  self.assertEqual(c['CASE'],'/srv/tse-milestone-a-evidence-20261111/nav20-031-trouble-root-trouble-20261115-153818')
  self.assertEqual(c['RESULT'],'fba9d4a9c276e7dd3612c36ecbd81941ab67cf284a920810a5d3942bce4d7b1f')
 def test_bounds_unchanged(self):
  c=constants(actual_source());self.assertEqual(c['LIMIT'],128*1024*1024);self.assertEqual(c['OUTPUT'],5*1024*1024)
 def test_exact_whole_inverse_and_tampered_parent(self):
  if not(HERE/'audit_trouble031_closed.py').exists():self.skipTest('behavior RED uses actual parent')
  import audit_trouble031_closed as t
  raw=BASE.read_bytes();changed=t.adapt(raw);self.assertEqual(t.adapt(changed,True),raw)
  for bad in [raw+b'\n',raw.replace(b'LIMIT=128',b'LIMIT=129'),changed]:
   with self.assertRaises(ValueError):t.adapt(bad)
  self.assertIn(b'map=\'trouble\'',changed)
  self.assertNotIn(b'navigation031-hole-host/receipt.json',changed)
if __name__=='__main__':unittest.main()
