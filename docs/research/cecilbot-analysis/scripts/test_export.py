import json,struct,unittest
from pathlib import Path
from parse_cecil_navmesh import parse_bytes
from export_analysis import encode_mesh
ROOT=Path(__file__).resolve().parents[1]/'reference/Cecil/Navmeshes'
class ExportTests(unittest.TestCase):
 def test_nine_originals_roundtrip(self):
  files=sorted(ROOT.glob('*.nav')); self.assertEqual(len(files),9)
  for f in files:
   with self.subTest(f=f.name):
    raw=f.read_bytes(); m=json.loads(json.dumps(parse_bytes(raw)))
    self.assertEqual(encode_mesh(m),raw)
 def test_lock_and_polygon_survive(self):
  raw=b'BNMV'+struct.pack('<4i',6,0,1,1)+b'BPPH'+struct.pack('<i3ffI3i',0,1,2,3,1,8,-1,-1,42)+struct.pack('<6f',1,2,3,4,5,6)+struct.pack('<iB',0,1)+b'PPO2'+struct.pack('<i9f',3,1,2,3,4,5,6,7,8,9)
  m=json.loads(json.dumps(parse_bytes(raw)))
  self.assertEqual(m['points'][0]['lock_origin'],[1,2,3,4,5,6])
  self.assertEqual(m['points'][0]['polygon_coordinates'],[[1,2,3],[4,5,6],[7,8,9]])
  self.assertEqual(encode_mesh(m),raw)
 def test_truncation_and_trailing(self):
  raw=(ROOT/'RedStation_5AF1A276.nav').read_bytes()
  for b in [raw[:19],raw[:-1],raw+b'X']:
   with self.assertRaises(ValueError):parse_bytes(b)
 def test_invalid_link_and_float(self):
  raw=bytearray((ROOT/'RedStation_5AF1A276.nav').read_bytes())
  struct.pack_into('<f',raw,28,float('nan'))
  with self.assertRaises(ValueError):parse_bytes(bytes(raw))
  raw=bytearray((ROOT/'RedStation_5AF1A276.nav').read_bytes());struct.pack_into('<i',raw,64,100000)
  with self.assertRaises(ValueError):parse_bytes(bytes(raw))
if __name__=='__main__':unittest.main()
