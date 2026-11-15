"""Pure diagnostic denominator tests; no case, native, process or API access."""
import unittest
try:
    from audit_natural_ai030_v2_closed import capture_summary
except ImportError:
    def capture_summary(captures):return {'events':[],'first_sticky':None}

class DiagnosticDenominatorTests(unittest.TestCase):
    def test_failed_packet_events_and_terminal_are_preserved_without_acceptance(self):
        enter={'sequence':3,'kind':'cast_ray','edge':'enter','call_id':2,'parent_call_id':1,'tick':{'ordinal':7}}
        terminal=dict(enter,sequence=4,edge='leave')
        captures=[{'serial':1,'accepted':True,'packet':{'events':[{'sequence':1},{'sequence':2}],'counters':{'dropped':0},'errors':[],'stop_reason':None,'terminal_record':None}},
                  {'serial':2,'accepted':False,'packet':{'events':[enter],'counters':{'dropped':1},'errors':[],'stop_reason':'queue overflow','terminal_record':terminal}}]
        result=capture_summary(captures)
        self.assertEqual(len(result['events']),3)
        self.assertEqual(result['first_sticky'],{'serial':2,'stop_reason':'queue overflow','dropped':1,'terminal_record':terminal})
        self.assertEqual(result['accepted_events'],2)
        self.assertEqual(result['failed_packet_events'],1)
        self.assertEqual(result['terminal_records'],[terminal])
    def test_noncontiguous_or_boolean_serial_fails(self):
        for serial in (True,2):
            with self.subTest(serial=serial):
                with self.assertRaises(ValueError):capture_summary([{'serial':serial,'accepted':True,'packet':{'events':[]}}])

if __name__=='__main__':unittest.main()
