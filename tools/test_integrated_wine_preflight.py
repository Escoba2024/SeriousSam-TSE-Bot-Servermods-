"""Portable guards for isolated runtime preparation; synthetic bytes only."""
import struct
import tempfile
import unittest
from pathlib import Path
import qualify_integrated_wine as q

class PreflightTests(unittest.TestCase):
    def test_exact_local_slot_counts_preserve_tail(self):
        for count in (1,2,3,4):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as d:
                p=Path(d)/"Data/SeriousSam.gms";p.parent.mkdir()
                data=b"GAMEV012"+struct.pack("<I",13)+b"TCP/IP Client"+struct.pack("<7i",0,0,0,1,2,3,3)+b"TAIL"
                p.write_bytes(data);q.configure_count(Path(d),count)
                actual=p.read_bytes()
                self.assertEqual(len(actual),len(data))
                self.assertEqual(struct.unpack_from("<4i",actual,33),tuple(i if i<count else -1 for i in range(4)))
                self.assertEqual(struct.unpack_from("<i",actual,49)[0],count-1)
                self.assertEqual(actual[53:],b"TAIL")
    def test_retail_server_provider_is_changed_only_in_private_client_copy(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"Data/SeriousSam.gms";p.parent.mkdir()
            b=b"GAMEV012"+struct.pack("<I",13)+b"TCP/IP Server"+struct.pack("<7i",0,0,0,1,2,3,0)+b"TAIL"
            p.write_bytes(b);q.configure_count(Path(d),1)
            self.assertEqual(p.read_bytes()[12:25],b"TCP/IP Client")
            self.assertEqual(p.read_bytes()[53:],b"TAIL")
    def test_refuses_bad_shell_version(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"Data/SeriousSam.gms";p.parent.mkdir();p.write_bytes(b"WRONG")
            with self.assertRaises(AssertionError):q.configure_count(Path(d),4)
            self.assertEqual(p.read_bytes(),b"WRONG")
    def test_refuses_invalid_count_before_writing(self):
        for count in (0,5,-1):
            with self.assertRaises(ValueError):q.configure_count(Path("/nonexistent"),count)
    def test_new_profile_guid_and_name_match_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"Player0.plr";g=p.with_suffix(".plr.guid")
            old=bytes(range(16));name=b"OLD"
            p.write_bytes(b"PLC4"+struct.pack("<I",3)+name+b"TEAM"+old+b"TAIL");g.write_bytes(old)
            q.change_profile(p,"BOT-TEST")
            b=p.read_bytes();self.assertEqual(struct.unpack_from("<I",b,4)[0],8)
            self.assertEqual(b[8:16],b"BOT-TEST")
            self.assertEqual(b[16:20],b"TEAM")
            self.assertEqual(b[20:36],g.read_bytes())
            self.assertNotEqual(old,g.read_bytes())
            self.assertEqual(b[36:],b"TAIL")
if __name__=="__main__":unittest.main()
