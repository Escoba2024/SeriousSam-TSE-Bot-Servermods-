"""Execute actual nested periodic bodies with bounded dependency fixtures."""
import ast
import copy
import hashlib
import importlib.util
from pathlib import Path
import types
import unittest

PARENT=Path('/srv/tse-a1-first-state-getter-boundary-disabled-20261115')
TOOL=Path(__file__).with_name('first_state_method_monitor_patch.py')


def module():
    spec=importlib.util.spec_from_file_location('monitorpatch',TOOL);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def source():
    old=(PARENT/'run_dual.py').read_text();return module().patch_runner(old)if TOOL.exists()else old
def node(text,name):
    main=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='main')
    return next(n for n in ast.walk(main)if isinstance(n,ast.FunctionDef)and n.name==name)


def make_periodic(text,name,*,fail=None,sample_fails=False):
    """The real AST is executed; fixtures only replace OS/guard dependencies."""
    events=[];clock=[10.0]
    def record(*row):
        events.append(row)
        if fail==row[0]:raise ValueError('guard rejected:'+row[0])
    class FakePath:
        def __init__(self,name='arena'):self.name=name
        def __truediv__(self,other):return FakePath(self.name+'/'+other)
        def read_text(self,**kw):record('log',self.name);return 'clean'
    def sample():
        record('sample')
        if sample_fails:raise ValueError('loaded Colt Original instructions differ: own active hook')
    windows={'vanilla':100,'botA':101}
    def window(role):record('window',role);return windows[role]+(1 if fail=='wrong_window'else 0)
    scope={'time':types.SimpleNamespace(monotonic=lambda:clock[0]),'P':types.SimpleNamespace(ROLES=('server','vanilla','botA')),
           'R':FakePath(),'BAD':types.SimpleNamespace(search=lambda text:fail=='bad_log'),'host':lambda phase:record('host',phase),
           'own_identity':lambda role:record('identity',role),'display_guard':lambda number:record('display',number),
           'window':window,'method_windows':windows,'collector':None,'query':lambda count:record('query',count),'sample':sample}
    fn=copy.deepcopy(node(text,name));fn.name='periodic_under_test'
    wrapper=ast.parse('def factory():\n last_host=-100.\n last_query=-100.\n').body[0]
    wrapper.body.extend([fn,ast.Return(ast.Name('periodic_under_test',ast.Load()))]);tree=ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[]))
    exec(compile(tree,'actual-private-periodic.py','exec'),scope)
    return scope['factory'](),events,clock


class ActualMethodMonitor(unittest.TestCase):
    def target(self):
        text=source();return text,'method_periodic'if TOOL.exists()else'periodic'
    def test_active_monitor_does_not_call_conflicting_original_colt_sample(self):
        text,name=self.target();call,events,clock=make_periodic(text,name,sample_fails=True)
        try:call()
        except ValueError as error:self.fail('actual periodic called conflicting reader: '+str(error))
        self.assertNotIn(('sample',),events)
    def test_identical_common_guards_and_one_hz_schedule(self):
        old=(PARENT/'run_dual.py').read_text();text,name=self.target()
        baseline,old_events,old_clock=make_periodic(old,'periodic');actual,new_events,new_clock=make_periodic(text,name)
        for t in(10.,10.02,11.02):old_clock[0]=new_clock[0]=t;baseline();actual()
        self.assertEqual(new_events,[e for e in old_events if e[0]!='sample']);self.assertNotIn(('sample',),new_events)
        self.assertEqual(sum(e[0]=='query'for e in new_events),2)
    def test_all_common_guards_still_fail_closed(self):
        for fail in('host','log','identity','display','window','query','bad_log','wrong_window'):
            with self.subTest(fail=fail):
                text,name=self.target();call,events,_=make_periodic(text,name,fail=fail)
                with self.assertRaises((ValueError,AssertionError)):call()
                self.assertNotIn(('sample',),events)
    def test_actual_new_ast_is_exact_parent_common_guard_body(self):
        if not TOOL.exists():self.fail('monitor transform missing')
        old=(PARENT/'run_dual.py').read_text();new=module().patch_runner(old)
        before=copy.deepcopy(node(old,'periodic'));after=copy.deepcopy(node(new,'method_periodic'))
        self.assertEqual(ast.unparse(before.body[-1]),'sample()');before.body.pop();after.name=before.name
        self.assertEqual(ast.dump(before,include_attributes=False),ast.dump(after,include_attributes=False))
        self.assertEqual(ast.dump(node(new,'periodic'),include_attributes=False),ast.dump(node(old,'periodic'),include_attributes=False))
    def test_both_arms_receive_only_method_monitor_and_no_inputs(self):
        text=source();self.assertIn('unit=unit,periodic=method_periodic,save=save,',text)
        self.assertIn("report['native_summary_scope']='JOIN_PREARM_ONLY'",text)
        self.assertIn("report['new_matched_control_required']=True",text)
        monitor=node(text,'method_periodic');calls={ast.unparse(n.func)for n in ast.walk(monitor)if isinstance(n,ast.Call)}
        for forbidden in('sample','native_rotation_pair','action_step','Endpoint','X11Transport','load_trace_api'):self.assertNotIn(forbidden,calls)
    def test_whole_inverse_helper_ast_and_prearm_cleanup_functions_unchanged(self):
        if not TOOL.exists():self.fail('monitor transform missing')
        m=module();old=(PARENT/'run_dual.py').read_text();new=m.patch_runner(old);self.assertEqual(m.reverse_runner(new),old)
        for name in('native_roles','native_rotation_pair','close','own_identity','host','query','display_guard','window'):
            self.assertEqual(ast.dump(node(new,name),include_attributes=False),ast.dump(node(old,name),include_attributes=False),name)
        helper=(PARENT/'first_state_inputfree_method.py').read_text();changed=m.patch_helper(helper);self.assertEqual(m.reverse_helper(changed),helper)
        self.assertEqual(ast.dump(ast.parse(changed),include_attributes=False),ast.dump(ast.parse(helper),include_attributes=False))
        with self.assertRaises(ValueError):m.reverse_runner(new.replace("'own window identity changed'","'mutated'"))


if __name__=='__main__':unittest.main()
