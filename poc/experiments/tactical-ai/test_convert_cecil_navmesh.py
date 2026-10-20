"""Exact binary-format and failure-path tests for the Cecil BNMV-v6 converter."""
import io
import struct
import unittest
from pathlib import Path
from contextlib import redirect_stdout
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("convert_cecil_navmesh", HERE/"convert_cecil_navmesh.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample(links=(1,), lock=-1, polygon=False):
    b=bytearray(b"BNMV"+struct.pack("<iiii",6,1,2,2))
    for idx in (0,1):
        edges=links if idx==0 else ()
        b+=b"BPPH"
        b+=struct.pack("<i3ffIiii",idx,float(idx),0.,-4.,1.,0,-1,-1,
                       lock if idx==0 else -1)
        if idx==0 and lock!=-1:
            b+=struct.pack("<6f",0.,0.,0.,0.,0.,0.)
        b+=struct.pack("<i",len(edges))
        for e in edges:
            b+=struct.pack("<i",e)
        b+=struct.pack("<B",1 if polygon and idx==0 else 0)
        if polygon and idx==0:
            b+=b"PPO2"+struct.pack("<i3f",1,1.,2.,3.)
    return bytes(b)


class ConverterTests(unittest.TestCase):
    def test_graph_is_directed(self):
        result=mod.read_navmesh(sample())
        self.assertEqual(result["nodes"][1][0],1.)
        self.assertEqual(result["arcs"],[(0,1)])
        txt=mod.to_waypoints(result,"Map_123.nav")
        self.assertIn("arc 0 1\n",txt)
        self.assertNotIn("arc 1 0\n",txt)

    def test_locks_and_polygons(self):
        result=mod.read_navmesh(sample(lock=7,polygon=True))
        self.assertEqual(result["locks"],[0])

    def test_reject_bad_version(self):
        b=sample()
        with self.assertRaises(ValueError):
            mod.read_navmesh(b[:4]+struct.pack("<i",5)+b[8:])

    def test_reject_truncation_trailing_and_invalid_edges(self):
        b=sample()
        for broken in (b[:-1],b+b"X",sample((99,)),sample((0,))):
            with self.subTest(broken=broken[:20]):
                with self.assertRaises(ValueError):
                    mod.read_navmesh(broken)

    def test_reject_excessive_count(self):
        b=sample()
        with self.assertRaises(ValueError):
            mod.read_navmesh(b[:16]+struct.pack("<i",513)+b[20:])


if __name__=="__main__":
    unittest.main()
