"""Exact prospective035 Source bindings; no Native stream or runtime reads."""
import ast
import copy
import importlib
import importlib.util
import unittest
from pathlib import Path

# Run the actual034 implementation before the new adapter exists: a genuine
# wrong-case behavior RED, rather than an ImportError counted as a test.
NAME='audit_trouble035_closed' if importlib.util.find_spec('audit_trouble035_closed') else 'audit_trouble034_closed'
reader=importlib.import_module(NAME)


class Binding(unittest.TestCase):
    def source(self):
        return reader.adapt(reader.BASE.read_bytes())

    def literals(self):
        return [n.value for n in ast.walk(ast.parse(self.source()))
                if isinstance(n,ast.Constant) and isinstance(n.value,str)]

    def test_actual_case_binding(self):
        self.assertIn('/srv/tse-milestone-a-evidence-20261111/nav20-035-trouble-root-trouble-20261115-200004',self.literals())

    def test_actual_result_binding(self):
        self.assertIn('7da99dace3e09fcd8ea843ed053f6cd0e7642265d85b318af10fb8259826fe9b',self.literals())

    def test_actual_host_and_restore_binding(self):
        for suffix in ['navigation035-trouble-host/receipt.json','navigation035-trouble-root-restore.json']:
            self.assertIn('/srv/tse-cecil-rollout-evidence-20261114/'+suffix,self.literals())

    def test_actual_header_source_binding(self):
        self.assertIn('/srv/tse-milestone-a-build-035-20261115/Sources/Game/BotSupplyNative.h',self.literals())
        self.assertIn('a2cf922bdd05058e50b633282a4ebb21be6f25ef01e1482c5dd56b710a8c88d9',self.literals())

    def test_whole_coordinator_inverse_and_mutations(self):
        raw=reader.BASE.read_bytes();new=reader.adapt(raw)
        self.assertEqual(reader.adapt(new,True),raw)
        for bad in [raw+b'\n',new,raw.replace(b'closed',b'closedX',1)]:
            with self.assertRaises(ValueError):reader.adapt(bad)

    def test_corrected_finalizer_full_inverse_and_status_scope(self):
        raw=reader.FINAL.read_bytes();new=reader.adapt_finalizer(raw)
        self.assertEqual(reader.adapt_finalizer(new,True),raw)
        self.assertIn(b'COMPLETE_CLOSED035_FUNCTIONAL_AUDIT_WITH_TRANSIT_CUSTODY_ONLY',new)
        self.assertIn(b'test_trouble034_ram_conclusions.py',new)
        self.assertIn(b'printed_9g_interval',new)
        for bad in [raw+b'\n',new,raw.replace(b'adjusted()-8',b'adjusted()-7')]:
            with self.assertRaises(ValueError):reader.adapt_finalizer(bad)

    def fixture(self):
        return dict(result=dict(status='PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY',errors=[],controller_sha256=reader.RUNNER,candidate_sha256=reader.DLL,map_key='trouble',diagnostics_enabled=True,functional_pass=False,qualified=False,cleanup={r:dict(closed=True)for r in ['server','botA','botB','vanilla']}),
            manifest=dict(comparison=dict(order=['035'],map='trouble',seconds=300,diagnostics=1,observer_fps=20,hard_difficulty=2,automatic_retry=False,automatic_sequence=False),map_case=dict(bot_count=8,bot_tier=3,automatic_retry=False,automatic_sequence=False),candidate=dict(build_manifest_sha256=reader.BUILD_MANIFEST,dll_sha256=reader.DLL)),
            restore=dict(status='PASS_RESTORE',result_sha256=reader.RESULT,case_result=str(reader.CASE/'result.json'),counts=dict(files=640,absences=0,closed_logs=4),parent_returncode=0,closed_log_scope_complete=True,started_roles=['server','botA','botB','vanilla']),
            host=dict(status='PASS_HOST_OBSERVATION_ONLY',child_exit_code=0,child_reaped=True,errors=[],signals_sent=0,automatic_retries=0),build=dict(dll_sha256=reader.DLL,build_ok=True,qualified=False))

    def test_bound_metadata_and_stale_or_changed_conditions(self):
        good=self.fixture();self.assertTrue(reader.validate_metadata(good))
        cases=[('restore','case_result','stale034/result.json'),('restore','result_sha256','0'*64),('host','status','FAIL'),('result','controller_sha256','0'*64),('result','candidate_sha256','0'*64),('result','diagnostics_enabled',False),('build','dll_sha256','0'*64)]
        for group,key,value in cases:
            bad=copy.deepcopy(good);bad[group][key]=value
            with self.subTest(group=group,key=key),self.assertRaises(ValueError):reader.validate_metadata(bad)
        for key,value in [('order',['034']),('map','hole'),('seconds',600),('diagnostics',0),('observer_fps',30),('hard_difficulty',1),('automatic_retry',True),('automatic_sequence',True)]:
            bad=copy.deepcopy(good);bad['manifest']['comparison'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):reader.validate_metadata(bad)

    def test_output_admission_and_unchanged_runtime_write_guard(self):
        floor=2**33+2**26+8*2**20
        self.assertIsNone(reader.output_guard(floor))
        for free,exists in [(floor-1,False),(floor,True),(64*2**20,False)]:
            with self.assertRaises(ValueError):reader.output_guard(free,exists)
        # The real nested save remains the unchanged Hole031 save apart from
        # the already034-authorized8MiB cap/error text; no tempfs bypass.
        scope=reader.coordinator_scope();raw=scope['adapt'](scope['BASE'].read_bytes())
        tree=ast.parse(raw)
        constants=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        self.assertIn(str(reader.OUT),constants)
        self.assertIn(reader.RESULT,constants)
        save=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='save')
        self.assertIn('O_EXCL',ast.unparse(save));self.assertIn('fsync',ast.unparse(save))
        self.assertIn('f_bavail',ast.unparse(save))


if __name__=='__main__':unittest.main(verbosity=2)
