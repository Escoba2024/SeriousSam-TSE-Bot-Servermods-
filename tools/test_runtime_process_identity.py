"""Own-process identity checks; no game or signals are used."""
import os,tempfile,unittest
from pathlib import Path
class ProcessIdentity(unittest.TestCase):
    def test_start_time_and_working_directory_must_both_match(self):
        import stop_integrated_public_wine as s
        pid=os.getpid();stamp=int(Path("/proc/%d/stat"%pid).read_text().rsplit(") ",1)[1].split()[19])
        good={"pid":pid,"start_ticks":stamp,"cwd":str(Path.cwd())}
        self.assertTrue(s.verify_process(good))
        bad=dict(good,start_ticks=stamp+1)
        with self.assertRaises(AssertionError):s.verify_process(bad)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(AssertionError):s.verify_process(dict(good,cwd=d))
    def test_missing_process_is_not_signalled(self):
        import stop_integrated_public_wine as s
        self.assertFalse(s.verify_process({"pid":999999999,"start_ticks":1,"cwd":"/"}))
if __name__=="__main__":unittest.main()
