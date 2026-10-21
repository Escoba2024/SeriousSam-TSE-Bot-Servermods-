"""Immutable 61DC reference has status rows but no new CSV/fire counters."""
import unittest
import qualify_integrated_wine as q
def log(step=20):
    return "\n".join("[BotDriver] bot%d tick=%d pos=(%.1f,0,0) heading=0 fire=0"%(slot,tick,slot+tick/20) for tick in [step,step*2,step*3] for slot in range(4))
class ReferenceActivity(unittest.TestCase):
    def analyze(self,logs):
        if not hasattr(q,"reference_slot_activity"):
            # Exercise the existing counter-only reader to reproduce the gap.
            return q.slot_activity(logs,4)
        return q.reference_slot_activity(logs,4,2)
    def test_original_status_proves_rate_and_movement_without_invented_shots(self):
        result=self.analyze(log())
        self.assertEqual(set(result),{"0","1","2","3"})
        for slot in result.values():
            self.assertEqual(slot["tick_hz"],20)
            self.assertTrue(slot["moved"])
            self.assertFalse(slot["combat_fire_counter_available"])
    def test_slow_timer_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,"rate"):
            self.analyze(log(10))
    def test_one_stationary_slot_is_rejected(self):
        rows=log().splitlines()
        rows=[line.replace("pos=(4.0,0,0)","pos=(3.0,0,0)").replace("pos=(5.0,0,0)","pos=(3.0,0,0)") if "bot2 " in line else line for line in rows]
        with self.assertRaisesRegex(AssertionError,"movement"):
            self.analyze("\n".join(rows))
if __name__=="__main__":unittest.main()
