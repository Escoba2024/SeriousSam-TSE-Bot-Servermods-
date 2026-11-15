"""Only new closed031 event-custody cases; no archive/controller imports."""
import unittest
import audit_hole031_closed as audit
class SourceCoverage(unittest.TestCase):
 def test_actual_goal_support_and_motion_events_not_silently_dropped(self):
  predicate=getattr(audit,'event_tag',lambda tag:tag in audit.EVENTS or tag.startswith(('CecilFlight','CecilBouncer','CecilTele','CecilJump')))
  for tag in ['CecilGoal','CecilGoalEnd','CecilGoalBudget','CecilReacquireSupport','CecilMotionProbe']:
   with self.subTest(tag=tag):self.assertTrue(predicate(tag))
 def test_existing_and_unknown_source_tags_stay_distinct(self):
  predicate=getattr(audit,'event_tag',lambda tag:tag in audit.EVENTS or tag.startswith(('CecilFlight','CecilBouncer','CecilTele','CecilJump')))
  for tag in ['CecilReacquireDecision','CecilGroundReplan','CecilFlightFinish']:self.assertTrue(predicate(tag))
  for tag in ['CecilState','CecilWeaponObserve','CecilPickerDecision','PlayerChat']:self.assertFalse(predicate(tag))

class InvocationBinding(unittest.TestCase):
 def test_actual_missing_arbitration_key_matches_driver_invocation(self):
  import ast,inspect
  # Execute the actual guard-key expression, not a parallel reconstruction.
  tree=ast.parse(inspect.getsource(audit.derive))
  node=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='t'for t in n.targets))
  expression=compile(ast.Expression(body=node.value),'actual-driver-key','eval')
  b={'key':[0,'botA',1,708,28,10453]}
  key=eval(expression,{},dict(b=b))
  actual_driver={(1,10453,708,28):18512}
  self.assertIn(key,actual_driver)
  self.assertNotIn(key,{(1,10453,708,29):18512})

if __name__=='__main__':unittest.main()
