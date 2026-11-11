"""Offline provenance/packaging test; does not compile or install a DLL."""
import tempfile
import unittest
from pathlib import Path
import build_supply_gamemp as build

class CandidateOverlayTest(unittest.TestCase):
    def test_default_build_uses_complete_current_candidate_without_data_or_tests(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"overlay"
            build.materialize_candidate_overlay(target)
            candidate=build.ROOT/"poc/candidates/redstation-supply-20261107"
            sources=[p for p in candidate.iterdir() if p.suffix in (".h",".cpp",".vcxproj") and not p.name.startswith("test_")]
            self.assertGreater(len(sources),10)
            self.assertEqual({p.name for p in target.iterdir()},{p.name for p in sources})
            for path in sources:
                self.assertEqual((target/path.name).read_bytes(),path.read_bytes(),path.name)
            self.assertTrue((target/"Game.vcxproj").exists())
            self.assertTrue((target/"RetailAllocator.cpp").exists())
            self.assertFalse(any(p.name.startswith("test_") or p.suffix in (".nav",".dll",".gro") for p in target.iterdir()))
            with self.assertRaises(Exception):
                build.materialize_candidate_overlay(target)

if __name__=="__main__":
    unittest.main()
