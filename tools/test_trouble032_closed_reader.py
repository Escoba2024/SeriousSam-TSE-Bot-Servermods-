"""Case binding/pure audit only; no runtime or heavy source imports."""
import ast,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def source():
 p=HERE/'audit_trouble032_closed.py'
 if not p.exists():
  import audit_trouble031_closed as old
  return old.adapt((HERE/'audit_hole031_closed.py').read_bytes())
 import audit_trouble032_closed as m
 return m.adapt((HERE/'audit_hole031_closed.py').read_bytes())
def constants(raw):
 out={}
 for n in ast.parse(raw).body:
  if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['CASE','PACKAGE','OUT','RESULT','LIMIT','OUTPUT']:
   v=n.value;out[n.targets[0].id]=ast.literal_eval(v.args[0])if isinstance(v,ast.Call)else eval(compile(ast.Expression(v),'pure','eval'),{})
 return out
class Binding(unittest.TestCase):
 def test_actual_new_case_result(self):
  c=constants(source());self.assertEqual(c['CASE'],'/srv/tse-milestone-a-evidence-20261111/nav20-032-trouble-root-trouble-20261115-163515');self.assertEqual(c['RESULT'],'9bf131da4f9091abdb90a45c70100ddccf120a6039665ced497f5409e8fc175d')
 def test_bounds_preserved(self):
  c=constants(source());self.assertEqual(c['LIMIT'],128*1024*1024);self.assertEqual(c['OUTPUT'],5*1024*1024)
 def test_whole_source_inverse(self):
  if not(HERE/'audit_trouble032_closed.py').exists():self.skipTest('actual old-case binding RED')
  import audit_trouble032_closed as m
  raw=(HERE/'audit_hole031_closed.py').read_bytes();changed=m.adapt(raw);self.assertEqual(m.adapt(changed,True),raw)
  for bad in [raw+b'\n',changed,raw.replace(b'LIMIT=128',b'LIMIT=129')]:
   with self.assertRaises(ValueError):m.adapt(bad)
if __name__=='__main__':unittest.main()
