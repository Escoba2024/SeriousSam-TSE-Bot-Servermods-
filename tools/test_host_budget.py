import unittest
from host_budget import HostBudget
class BudgetTests(unittest.TestCase):
 def test_real_delta_excludes_duplicate_guest(self):
  b=HostBudget();b.add(0,'cpu 100 0 20 800 0 0 0 0 70 0',2*2**30,10*2**30)
  r=b.add(1,'cpu 150 0 30 840 0 0 0 0 100 0',2*2**30,10*2**30)
  self.assertEqual(r['cpu_busy_percent'],60);self.assertEqual(b.summary()['max_sample_gap_seconds'],1)
 def test_exact_limits_and_all_three_failures(self):
  b=HostBudget();b.add(0,'cpu 0 0 0 0 0 0 0 0',int(1.5*2**30),8*2**30);b.add(1,'cpu 75 0 0 25 0 0 0 0',int(1.5*2**30),8*2**30)
  for stat,ram,disk in [('cpu 76 0 0 24 0 0 0 0',2*2**30,9*2**30),('cpu 0 0 0 100 0 0 0 0',1,9*2**30),('cpu 0 0 0 100 0 0 0 0',2*2**30,1)]:
   b=HostBudget();b.add(0,'cpu 0 0 0 0 0 0 0 0',2*2**30,9*2**30)
   with self.assertRaises(ValueError):b.add(1,stat,ram,disk)
   self.assertTrue(b.samples[-1]['violations'])
 def test_bad_counter_or_time_rejected(self):
  b=HostBudget();b.add(1,'cpu 100 0 0 100 0 0 0 0',2*2**30,9*2**30)
  for time,line in [(1,'cpu 110 0 0 110 0 0 0 0'),(2,'cpu 0 0 0 0 0 0 0 0')]:
   with self.assertRaises(ValueError):b.add(time,line,2*2**30,9*2**30)
if __name__=='__main__':unittest.main()
