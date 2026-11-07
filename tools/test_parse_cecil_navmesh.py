"""Pure offline tests for CecilBotMod BNMV v6: strict and fail-closed."""
import struct
import unittest
from pathlib import Path
from tools import parse_cecil_navmesh as nav

def point(i,xyz=(1.,2.,3.),links=(),lock=-1,poly=()):
    a=bytearray(b'BPPH'+struct.pack('<i3ffIiii',i,*xyz,2.,0,-1,-1,lock))
    if lock!=-1:a+=struct.pack('<6f',1.,2.,3.,4.,5.,6.)
    a+=struct.pack('<i',len(links))
    for n in links:a+=struct.pack('<i',n)
    a+=struct.pack('<B',int(bool(poly)))
    if poly:
        a+=b'PPO2'+struct.pack('<i',len(poly))
        for v in poly:a+=struct.pack('<3f',*v)
    return bytes(a)
def mesh(points):
    return b'BNMV'+struct.pack('<4i',6,0,len(points)+1,len(points))+b''.join(points)

class BinaryNavmeshTests(unittest.TestCase):
    def test_two_connected_points_are_converted(self):
        buf=mesh([point(0,links=(1,)),point(1,(4.,5.,6.),links=(0,))])
        decoded=nav.parse_bytes(buf)
        self.assertEqual(decoded['version'],6)
        self.assertEqual(len(decoded['points']),2)
        self.assertEqual(decoded['points'][0]['idx'],0)
        self.assertEqual(decoded['points'][0]['links'],[1])
        self.assertEqual(decoded['points'][1]['pos'],[4.,5.,6.])
        rendered=nav.to_graph_text(decoded)
        self.assertEqual(sum(s.startswith('node ') for s in rendered.splitlines()),2)
        self.assertEqual(sum(s.startswith('edge ') for s in rendered.splitlines()),1)
        self.assertIn('edge 0 1',rendered)
    def test_optional_lock_placement_and_polygon_are_parsed(self):
        buf=mesh([point(0,lock=13,poly=((1.,2.,3.),(4.,5.,6.),(7.,8.,9.)))])
        result=nav.parse_bytes(buf)
        self.assertEqual(result['points'][0]['lock_entity'],13)
        self.assertEqual(result['points'][0]['polygon_vertices'],3)
    def test_invalid_inputs_fail(self):
        good=mesh([point(0)])
        bads=[good[:6],b'NOPE'+good[4:],good[:4]+struct.pack('<i',7)+good[8:],
              good[:16]+struct.pack('<i',40000)+good[20:],good+b'JUNK',
              mesh([point(0,links=(100,))]),mesh([point(0,xyz=(float('nan'),2.,3.))]),
              mesh([point(0),point(0)]),good[:-1]]
        for bad in bads:
            with self.subTest(bad=bad[:24]),self.assertRaises(ValueError):
                nav.parse_bytes(bad)
    @unittest.skipUnless(Path('/srv/tse-cecilbot-reference-20261020/Cecil/Navmeshes').is_dir(), 'local licensed reference absent')
    def test_all_nine_local_references(self):
        root=Path('/srv/tse-cecilbot-reference-20261020/Cecil/Navmeshes')
        for file in root.glob('*.nav'):
            with self.subTest(file=file.name):
                parsed=nav.parse_bytes(file.read_bytes())
                self.assertGreater(len(parsed['points']),50)
        red=nav.parse_bytes((root/'RedStation_5AF1A276.nav').read_bytes())
        self.assertEqual(len(red['points']),193)
if __name__=='__main__':unittest.main()
