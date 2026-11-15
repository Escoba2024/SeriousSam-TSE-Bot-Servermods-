import unittest
from yodeller035_ram_detail import stationary_witness
class Witness(unittest.TestCase):
 def r(self,t,p):return dict(tick=t,position=[p,0,0])
 def test_same_original_anchor_and_reset(self):
  x=stationary_witness([self.r(0,0),self.r(.2,.5),self.r(.4,1),self.r(.6,1.1),self.r(.8,1.2)])
  self.assertEqual(x['seconds'],.4);self.assertEqual(x['first']['tick'],0);self.assertEqual(x['last']['tick'],.4)
 def test_gap_breaks_continuity(self):
  x=stationary_witness([self.r(0,0),self.r(.2,0),self.r(2,0),self.r(2.1,0)])
  self.assertEqual(x['seconds'],.2)
