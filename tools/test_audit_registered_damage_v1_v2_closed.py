"""Only new reader semantics; synthetic counters are not native evidence."""
import importlib.util
import json
from pathlib import Path
import unittest

TOOL=Path(__file__).with_name('audit_registered_damage_v1_v2_closed.py')
def summary(rows,S,F):
    if not TOOL.exists():raise AssertionError('new native/row/excluded audit semantics absent')
    spec=importlib.util.spec_from_file_location('registered_closed',TOOL);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.scope_summary(rows,S,F)

def sample(serial,seqs,excluded):
    return {'serial':serial,'accepted':True,'packet':{'measurement_scope':'REGISTERED_FIRST_STATE_DAMAGE_V1',
      'events':[{'sequence':s,'row_sequence':(serial-1)*2+i+1}for i,s in enumerate(seqs)],
      'scope_counters':{'entered_excluded':excluded,'completed_excluded':excluded,'pending':0,'incomplete_closed':0,
                        'native_edges':serial*4,'rows_attempted':serial*2,'entered_full':serial,'completed_full':serial},
      'counters':{'events_enqueued':serial*2,'events_drained':serial*2,'events_attempted':serial*4}}}

class ScopeSummary(unittest.TestCase):
    def test_reused_actual_cpu_function_has_its_json_dependency(self):
        spec=importlib.util.spec_from_file_location('cpu_reader_actual',TOOL);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        fn,_=m.cpu_reader()
        sample={'sample':{'epoch':'offline','clock_hz':100,'started':1.,'finished':1.,'processes':{},'cgroups':{}},'binding_errors':[],'known_case':None}
        end={'ended':True,'coverage_complete_to_reap':True,'controller_returncode':0,'samples':1,'bound_case':str(m.CASES['control'])}
        raw=b'\n'.join(json.dumps(x).encode()for x in(sample,end))
        fn.__globals__.update(read=lambda _:raw,load=lambda _:{'manifest_sha256':m.MANIFEST,'automatic_retry':False,'pid':1})
        result=fn('control',{'events':[]},None,None)
        self.assertEqual(result['samples'],1);self.assertEqual(result['domains'],{})

    def test_native_edges_are_not_retained_rows_or_excluded_calls(self):
        r=summary([sample(1,[1,4],1),sample(2,[5,8],2)],1,2)
        self.assertEqual(r['raw_full_rows'],4);self.assertEqual(r['native_edges_final'],8)
        self.assertEqual(r['excluded_calls_final'],2);self.assertEqual(r['positive_at_S']['native_edges'],4)
        self.assertEqual(r['positive_at_S']['rows_attempted'],2)

    def test_no_contiguous_native_sequence_assumption_or_afterS_credit(self):
        r=summary([sample(1,[1,4],1),sample(2,[5,8],2)],1,2)
        self.assertEqual(r['positive_full_rows'],2);self.assertEqual(r['tail_full_rows'],2)
        self.assertTrue(r['native_sequence_has_real_exclusion_gaps'])

    def test_scope_serial_and_row_gaps_are_not_accepted(self):
        for mutation in('scope','serial','row','counter'):
            values=[sample(1,[1,4],1),sample(2,[5,8],2)]
            if mutation=='scope':values[1]['packet']['measurement_scope']='FULL18'
            elif mutation=='serial':values[1]['serial']=3
            elif mutation=='row':values[1]['packet']['events'][0]['row_sequence']=99
            else:values[1]['packet']['scope_counters']['native_edges']+=1
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):summary(values,1,2)

if __name__=='__main__':unittest.main()
