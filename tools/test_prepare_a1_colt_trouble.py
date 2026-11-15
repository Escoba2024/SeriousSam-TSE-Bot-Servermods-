"""Actual pinned source/temporary transaction tests; never execute a controller."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

PARENT=Path('/srv/tse-a1-original-respawn-fixedtarget030-v5-disabled-20261115')
HELPER=Path(__file__).with_name('prepare_a1_colt_trouble.py')


def read(path):
    with os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()


def helper():
    if not HELPER.exists():return None
    s=importlib.util.spec_from_file_location('prepare_trouble',HELPER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def namespace(source,name):
    m=types.ModuleType(name);m.__file__=str(PARENT/(name+'.py'))
    exec(compile(source,name,'exec'),m.__dict__);return m


class PreparationTests(unittest.TestCase):
    def test_actual_builder_active_NAI_metadata_matches_exact_generated_nav_targets(self):
        m=helper();generated=m.generated_sources()
        nai=namespace(generated['first_state_natural_ai.py'],'actual_metadata_NAI')
        self.assertEqual(nai.NAV_SOURCE,m.NAV)
        outer=json.loads(read(PARENT/'source-manifest.json'));nested=json.loads(read(PARENT/'method-api/source-manifest.json'))
        originals={'outer':copy.deepcopy(outer['natural_ai_condition']),'nested':copy.deepcopy(nested['natural_ai_condition'])}
        # Execute the real prepare() metadata statements, without copying a fork
        # or replacing them with a second implementation in this test.
        tree=ast.parse(read(HELPER));prepare=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='prepare')
        statements=[]
        for node in prepare.body:
            if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='condition'for t in node.targets):statements.append(node)
            elif isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and isinstance(node.value.func.value,ast.Name)and node.value.func.value.id=='condition':statements.append(node)
            elif isinstance(node,ast.For)and isinstance(node.target,ast.Name)and node.target.id=='item':statements.append(node)
        self.assertEqual(len(statements),4)
        import a1_colt_trouble_condition as condition
        env=dict(m.__dict__,m=outer,nm=nested,files=generated,TC=condition)
        exec(compile(ast.fix_missing_locations(ast.Module(body=statements,type_ignores=[])),'actual_builder_metadata','exec'),env)
        for label,manifest in(('outer',outer),('nested',nested)):
            active=manifest['natural_ai_condition'];original=originals[label]
            with self.subTest(manifest=label,field='nav'):self.assertEqual(active['nav_sha256'],nai.NAV_SHA)
            with self.subTest(manifest=label,field='snapshots'):self.assertEqual(active['snapshots_before_seal'],list(nai.TARGETS))
            with self.subTest(manifest=label,field='historical'):
                self.assertTrue(active['parent_control_status_historical_only'])
                self.assertEqual(active['inputs_scope'],'HISTORICAL_PREARM_AI_OWNERSHIP_ONLY_NOT_CURRENT_CONDITION_TOTAL')
                for field in('inputs','control_status','source_pins'):
                    if field in original:self.assertEqual(active[field],original[field])
                    else:self.assertNotIn(field,active)
                self.assertEqual(active['historical_parent_context_reference'],'outer natural_ai_condition control_status/inputs; not current method status/input total')
                self.assertEqual(active['current_condition_native_input_attempts'],2)
                self.assertEqual(active['current_condition'],m.CONDITION)
                self.assertEqual(active['config_sha256'],hashlib.sha256(generated['natural-ai/active.ini']).hexdigest())

    def test_RAM_evidence_only_volume_budgets_fail_closed_and_keep_BASE_tools(self):
        import a1_colt_trouble_condition as condition
        self.assertTrue(callable(getattr(condition,'volume_budget',None)),'RAM evidence reservation policy absent')
        disk=8*1024**3+128*1024**2;memory=1536*1024**2+(64+512+64+512)*1024**2;ram=640*1024**2
        row={'disk_free_bytes':disk,'mem_available_bytes':memory}
        value=condition.volume_budget(row,True,ram)
        self.assertEqual(value['fixture_disk_minimum_bytes'],disk);self.assertEqual(value['mem_available_minimum_bytes'],memory)
        for bad,mode,free in[({'disk_free_bytes':disk-1,'mem_available_bytes':memory},True,ram),
             ({'disk_free_bytes':disk,'mem_available_bytes':memory-1},True,ram),(row,True,ram-1),
             ({'disk_free_bytes':True,'mem_available_bytes':memory},True,ram),(row,1,ram),
             ({'disk_free_bytes':disk},True,ram),(row,False,ram)]:
            with self.subTest(row=bad,mode=mode),self.assertRaises(ValueError):condition.volume_budget(bad,mode,free)
        runner=helper().generated_sources()['run_dual.py'].decode()
        self.assertIn('evidence_ram_base=None',runner);self.assertIn('TC.select_case_base(BASE,evidence_ram_base)',runner)
        self.assertIn('E=CASE_BASE/',runner);self.assertIn("BASE/'session-readonly.py'",runner)
        self.assertIn('TC.volume_budget(host_sample,evidence_ram_base is not None',runner)
        self.assertIn("'--evidence-ram-base'",runner)

    def test_RAM_path_is_explicit_owned_directory_no_symlink_or_relocation(self):
        import a1_colt_trouble_condition as condition
        self.assertTrue(callable(getattr(condition,'select_case_base',None)),'explicit evidence-only RAM base absent')
        with patch.object(condition,'require_disk',return_value={'mode':'disk'})as default:
            base,receipt=condition.select_case_base(Path('/unused'),None)
            self.assertEqual(base,Path('/unused'));default.assert_called_once_with(Path('/unused'))
        for wrong in('/srv/not-ram','/dev/shm','relative'):
            with self.subTest(path=wrong),self.assertRaises(ValueError):condition.select_case_base(Path('/unused'),wrong)
        owner=os.geteuid();good=types.SimpleNamespace(st_mode=0o40700,st_uid=owner,st_dev=7)
        root=types.SimpleNamespace(st_dev=7);capacity=types.SimpleNamespace(f_bavail=10*1024**3,f_frsize=1)
        for mutation in(None,{'st_uid':owner+1},{'st_mode':0o40755},{'st_dev':8},{'st_mode':0o100700}):
            selected=copy.copy(good)
            if mutation:selected.__dict__.update(mutation)
            with self.subTest(mutation=mutation),patch.object(Path,'resolve',lambda self,**kwargs:self),\
                 patch.object(Path,'stat',lambda self,**kwargs:root if self==Path('/dev/shm')else selected),\
                 patch.object(condition.os,'statvfs',return_value=capacity),patch.object(condition,'_mem_available',return_value=10*1024**3):
                if mutation:
                    with self.assertRaises(ValueError):condition.select_case_base(Path('/unused'),'/dev/shm/owned')
                else:
                    base,receipt=condition.select_case_base(Path('/unused'),'/dev/shm/owned')
                    self.assertEqual(base,Path('/dev/shm/owned'));self.assertEqual(receipt['mode'],'explicit_ram_evidence_only')
        with patch.object(Path,'resolve',return_value=Path('/dev/shm/alias-target')):
            with self.assertRaises(ValueError):condition.select_case_base(Path('/unused'),'/dev/shm/alias')

    def test_actual_host_closure_reuses_each_existing_measurement_once_and_preserves_failure(self):
        import a1_colt_trouble_condition as condition
        tree=ast.parse(helper().generated_sources()['run_dual.py']);host=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='host')
        text=ast.unparse(host)
        self.assertEqual(text.count('budget.add('),1);self.assertEqual(text.count('time.monotonic('),1)
        self.assertEqual(text.count("Path('/proc/meminfo')"),1);self.assertEqual(text.count("Path('/proc/stat')"),1)
        self.assertEqual(text.count('os.statvfs('),1)
        budget_module=namespace(read(PARENT/'host_budget.py'),'actual_host_budget')
        with tempfile.TemporaryDirectory()as td:
            for enough in(True,False):
                report={};budget=budget_module.HostBudget();memory=condition.RAM_MEMORY_MINIMUM if enough else condition.RAM_MEMORY_MINIMUM-1
                def path(value):
                    if value=='/proc/stat':return types.SimpleNamespace(read_text=lambda:'cpu 1 2 3 4 5 6 7 8')
                    if value=='/proc/meminfo':return types.SimpleNamespace(read_text=lambda:'MemAvailable: '+str(memory//1024)+' kB')
                    return Path(value)
                env={'budget':budget,'report':report,'time':types.SimpleNamespace(monotonic=lambda:1.),'Path':path,'int':int,
                  'shutil':types.SimpleNamespace(disk_usage=lambda _:types.SimpleNamespace(free=condition.RAM_FIXTURE_DISK_MINIMUM)),
                  'TC':condition,'evidence_ram_base':'/dev/shm/own','CASE_BASE':Path('/dev/shm/own'),
                  'os':types.SimpleNamespace(statvfs=lambda _:types.SimpleNamespace(f_bavail=condition.RAM_VOLUME_MINIMUM,f_frsize=1)),
                  'E':Path(td),'json':json,'save':lambda:None}
                exec(compile(ast.fix_missing_locations(ast.Module(body=[host],type_ignores=[])),'actual_generated_host','exec'),env)
                if enough:self.assertIs(env['host']('fixture'),budget.samples[0])
                else:
                    with self.assertRaisesRegex(ValueError,'MemAvailable'):env['host']('fixture')
                self.assertEqual(len(budget.samples),1);self.assertEqual(len(report['evidence_volume_samples']),1)
                self.assertIs(report['evidence_volume_samples'][0]['host_sample'],budget.samples[0])
                self.assertEqual(json.loads(read(Path(td)/'host-resources.json'))['samples'],budget.samples)

    def test_actual_disk_guard_reserves_metadata_raw_case_before_case_creation(self):
        import a1_colt_trouble_condition as condition
        self.assertTrue(callable(getattr(condition,'require_disk',None)),'explicit prospective case reservation absent')
        minimum=8*1024**3+(64+64+512+64)*1024**2
        with patch.object(condition.os,'statvfs',return_value=types.SimpleNamespace(f_bavail=minimum-1,f_frsize=1)):
            with self.assertRaises(ValueError):condition.require_disk('/unused')
        with patch.object(condition.os,'statvfs',return_value=types.SimpleNamespace(f_bavail=minimum,f_frsize=1)):
            self.assertEqual(condition.require_disk('/unused')['minimum_free_bytes'],minimum)
        runner=helper().generated_sources()['run_dual.py'].decode()
        self.assertLess(runner.index('TC.select_case_base(BASE,evidence_ram_base)'),runner.index('E=CASE_BASE/'))

    def test_actual_generated_prepare_collects_existing_geometry_then_hp_drop(self):
        from test_a1_colt_trouble_condition import frame,native
        from test_a1_original_respawn_method import Clock
        unused,policy,method=self.modules();clock=Clock();dead=[False]
        legacy=namespace(read(PARENT/'first_state_inputfree_method.py'),'actual_legacy_window')
        class Context:
            def require_original_regions(self):return {'fixture_only':'not native proof'}
            def input_frame(self,unused):
                f=frame(0. if dead[0]else 100.);f['started']=f['finished']=clock()
                return f
        context=Context()
        with tempfile.TemporaryDirectory()as td,patch.dict(sys.modules,{'a1_colt_trouble_policy':policy}):
            w=method.make_window_class(legacy)(mode='control',api_root=Path(td),arena=td,evidence=td,parent_started=0.,
              frame={},records={r:{}for r in('server','vanilla','botA')},pins={},own_identity=lambda r:None,
              unit=lambda r:r,periodic=lambda:dead.__setitem__(0,True),save=lambda:None,record={},clock=clock,sleep=clock.sleep,
              read_roles=lambda:native(context.input_frame(None)),endpoint=None,journal=None,context_factory=lambda w:context)
            w._prepare()
            self.assertEqual(len(w.record['readiness_reads']),2)
            self.assertTrue(w.record['pre_arm_hp_drop']['hp_drop_observed'])
            self.assertTrue(all(row['normal_role_geometry']['los_proven']is False for row in w.record['readiness_reads']))
            self.assertFalse(w.record.get('input_emissions',0));self.assertFalse(w.record.get('observation_complete',False))

    def test_both_actual_map_population_guards_accept_only_little_trouble(self):
        tree=ast.parse(helper().generated_sources()['run_dual.py'])
        nodes=[n for n in ast.walk(tree)if isinstance(n,ast.Assert)and 'mapname'in ast.unparse(n)]
        self.assertEqual(len(nodes),2)
        for node in nodes:
            code=compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'actual_map_guard','exec')
            exec(code,{'q':{'mapname':'Little Trouble','numplayers':'2'},'expected':2,'n':2})
            for q in({'mapname':'Red Station','numplayers':'2'},{'mapname':'Little Trouble','numplayers':'3'}):
                with self.assertRaises(AssertionError):exec(code,{'q':q,'expected':2,'n':2})

    def modules(self):
        m=helper()
        if m is None:
            policy=namespace(read(PARENT/'a1_original_respawn_policy.py'),'a1_colt_trouble_policy')
            source=read(PARENT/'a1_original_respawn_method.py')
        else:
            generated=m.generated_sources()
            policy=namespace(generated['a1_colt_trouble_policy.py'],'a1_colt_trouble_policy')
            source=generated['a1_colt_trouble_method.py']
        with patch.dict(sys.modules,{'a1_colt_trouble_policy':policy}):
            method=namespace(source,'a1_colt_trouble_method')
        return m,policy,method

    def test_actual_generated_ownership_guard_has_separate_64MiB_not_old3MiB(self):
        unused,policy,method=self.modules()
        with tempfile.TemporaryDirectory()as td:
            r=method.OwnershipReads(td,lambda:1.,85.);r.payload_bytes=2*1024**2
            def actual_receipt(directory):
                # Existing exclusive private_json executes, not a dummy success.
                nai=namespace(read(PARENT/'first_state_natural_ai.py'),'actual_old_NAI')
                nai.private_json(directory/'natural-ai-ownership.json',{'actual':'receipt'})
                return {'fresh':True}
            try:value=r.read(actual_receipt)
            except ValueError as error:self.fail('new condition still uses old ownership budget: '+str(error))
            self.assertTrue(value['fresh']);self.assertEqual(method.OWNERSHIP_TOTAL_LIMIT,64*1024**2)
            self.assertEqual(r.receipt['maximum_reads_including_initial'],1024)
            self.assertEqual(r.receipt['single_receipt_limit'],1536*1024)
            self.assertEqual(policy.CONDITION,'NORMAL_ORIGINAL_RESPAWN030_COLT_LITTLE_TROUBLE_V1')
            # No guarantee for1024 large receipts: the same full reservation remains fatal.
            r.payload_bytes=64*1024**2-1536*1024+1
            with self.assertRaisesRegex(ValueError,'payload budget'):r.read(actual_receipt)

    def test_whole_source_inverses_and_old_RP_reader_observer_unchanged(self):
        m=helper();self.assertIsNotNone(m,'new exact LittleTrouble preparer absent')
        generated=m.generated_sources()
        expected={'run_dual.py','first_state_natural_ai.py','method-api/first_state_natural_ai.py',
                  'natural-ai/active.ini','a1_colt_trouble_method.py','a1_colt_trouble_policy.py'}
        self.assertEqual(set(generated),expected)
        for name,data in generated.items():
            parent=m.PARENT_SOURCE[name]
            self.assertEqual(m.reverse_source(name,data),read(PARENT/parent))
            with self.assertRaises(ValueError):m.reverse_source(name,data+b'\n#foreign mutation\n')
        self.assertEqual(generated['natural-ai/active.ini'],read(PARENT/'natural-ai/active.ini').replace(b'bot_fMoveFactor=1;',b'bot_fMoveFactor=0;'))
        self.assertEqual(generated['first_state_natural_ai.py'],generated['method-api/first_state_natural_ai.py'])
        runner=generated['run_dual.py'].decode();ast.parse(runner)
        self.assertIn('import a1_colt_trouble_method as RP',runner)
        self.assertIn('TC.stage_startup(transaction,R,E)',runner)
        self.assertIn('RP.OwnershipReads(E,time.monotonic,parent_started+85.)',runner)
        method=generated['a1_colt_trouble_method.py'].decode()
        self.assertIn("TC.role_geometry(native,frame)",method)
        self.assertIn("TC.require_hp_drop(first,self.record['readiness_reads'])",method)
        self.assertNotIn('PASS_LIMITED_NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_CONTROL_ONLY',method)
        self.assertEqual(read(PARENT/'a1_original_respawn_method.py'),m.read(PARENT/'a1_original_respawn_method.py'))

    def test_actual_NAI_accepts_only_new_map_tuple_and_same_strict_roles(self):
        from test_first_state_natural_ai import fixture
        m=helper()
        source=read(PARENT/'first_state_natural_ai.py')if m is None else m.generated_sources()['first_state_natural_ai.py']
        nai=namespace(source,'actual_trouble_NAI');f,records,pins=fixture();q=f['natural_ai_ownership']
        q['schema']='ORIGINAL_COLT_TROUBLE030_SOURCE_OWNERSHIP_V1'
        q['staged'].update(config_sha256=nai.ACTIVE_CONFIG_SHA,nav_sha256='252d7e4c003804fe9ae2afef359843feb39b5dda29c1d6eadb0835fbe64a30ac')
        q['log_text']=q['log_text'].replace('RedStation.wld','DM_LittleTrouble.wld').replace('nodes=193','nodes=110').replace('ff3776e0','4060d0dd').replace('e4571656','980013d4')
        try:self.assertEqual(nai.roles_from_receipt(f,records,pins),{'vanilla':'vanilla','botA':'bot'})
        except ValueError as error:self.fail('actual LittleTrouble ownership still rejected: '+str(error))
        mutations=[lambda a,b,c:a['natural_ai_ownership'].update(log_text=q['log_text'].replace('4060d0dd','ff3776e0')),
                   lambda a,b,c:a['natural_ai_ownership']['staged'].update(nav_sha256='0'*64),
                   lambda a,b,c:c['server']['GameMP.dll'].update(sha256=c['botA']['GameMP.dll']['sha256'])]
        for change in mutations:
            a,b,c=copy.deepcopy((f,records,pins));change(a,b,c)
            with self.assertRaises(ValueError):nai.roles_from_receipt(a,b,c)

    def test_actual_startup_transaction_requires_seal_and_restores_exactly(self):
        import a1_colt_trouble_condition as condition
        self.assertTrue(callable(getattr(condition,'stage_startup',None)),'explicit sealed startup-map staging absent')
        m=helper();self.assertIsNotNone(m)
        tx=namespace(read(PARENT/'transaction.py'),'actual_unchanged_transaction')
        script=read(m.STARTUP_FIXTURE)
        with tempfile.TemporaryDirectory()as td:
            root=Path(td)/'arena';evidence=Path(td)/'evidence';root.mkdir();evidence.mkdir()
            path=root/m.STARTUP_REL;path.parent.mkdir(parents=True);path.write_bytes(script);path.chmod(0o640)
            t=tx.FileTransaction(root,evidence,lambda:None);t.snapshot_file(m.STARTUP_REL)
            original=copy.deepcopy(t.records[str(m.STARTUP_REL)])
            with self.assertRaises(ValueError):condition.stage_startup(t,root,evidence)
            t.seal();receipt=condition.stage_startup(t,root,evidence)
            self.assertEqual(read(path),script.replace(b'RedStation.wld',b'DM_LittleTrouble.wld'))
            self.assertEqual(receipt['start_difficulty'],3);self.assertEqual(receipt['spawn_invulnerability'],0)
            self.assertIs(receipt['spawn_marker_selected'],False)
            with self.assertRaises(FileExistsError):
                # Restore exact original bytes to reach the actual O_EXCL receipt guard.
                path.write_bytes(script);condition.stage_startup(t,root,evidence)
            self.assertTrue(t.restore()['restored']);self.assertEqual(read(path),script)
            current=path.stat();self.assertEqual((current.st_uid,current.st_gid,current.st_mode&0o777,current.st_mtime_ns),
                (original['uid'],original['gid'],original['mode'],original['mtime_ns']))


if __name__=='__main__':unittest.main()
