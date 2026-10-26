import os
import signal
import subprocess
import sys
import unittest
from native_owned_process import OwnedProcess

@unittest.skipUnless(hasattr(os,'pidfd_open'),'Linux pidfd required')
class OwnedProcessTests(unittest.TestCase):
    def test_stop_terminates_only_owned_child_and_keeps_unrelated_process(self):
        child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);other=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
        try:
            guard=OwnedProcess(child);guard.stop(timeout=1)
            self.assertIsNotNone(child.poll());self.assertIsNone(other.poll())
        finally:
            for p in (child,other):
                if p.poll() is None:p.terminate()
                p.wait(timeout=3)
    def test_owned_ignoring_child_has_bounded_pidfd_kill_fallback(self):
        child=subprocess.Popen([sys.executable,'-u','-c',"import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print('READY',flush=True);time.sleep(30)"],stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(),'READY');guard=OwnedProcess(child);guard.stop(timeout=.1)
            self.assertEqual(child.returncode,-signal.SIGKILL)
        finally:
            if child.poll() is None:child.kill()
            child.wait(timeout=3);child.stdout.close()
    def test_arbitrary_process_record_cannot_be_adopted(self):
        with self.assertRaises(ValueError):OwnedProcess({'pid':os.getpid()})

if __name__=='__main__':unittest.main()
