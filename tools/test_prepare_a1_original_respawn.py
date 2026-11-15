"""Actual disabled-parent transforms; no controller/Native execution."""
import ast
import hashlib
import importlib.util
import json
import os
import copy
import math
import struct
import types
import tempfile
from pathlib import Path
import unittest

ROOT=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115')
HELPER=Path(__file__).with_name('prepare_a1_original_respawn.py')

def read(p):
    with os.fdopen(os.open(Path(p).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()

class Preparation(unittest.TestCase):
    def helper(self):
        self.assertTrue(HELPER.exists(),'new normal Original respawn preparer absent')
        spec=importlib.util.spec_from_file_location('prepare_respawn',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

    def test_actual_complete_sources_inverse_no_shared_core_change(self):
        m=self.helper();old={n:read(ROOT/n)for n in m.CHANGED};new=m.changed_sources(old)
        self.assertEqual(set(new),set(m.CHANGED))
        for n in old:
            self.assertEqual(m.reverse_source(n,new[n]),old[n]);
            with self.assertRaises(ValueError):m.reverse_source(n,new[n]+b'\n#foreign mutation\n')
        s=new['run_dual.py'].decode();ast.parse(s)
        self.assertEqual(s.count('colt_preparation=False'),2)
        self.assertIn('original_replica',s);self.assertIn('read_roles=native_roles',s)
        self.assertIn('journal=fire_journal',s);self.assertIn('RP.bind(IMW)',s)
        self.assertIn('FireTransport(pin,',s);self.assertIn('RP.publish_attempts(report,method)',s)
        self.assertIn('RUNTIME_REVIEWED=False',s)
        self.assertNotIn('CP.run_preparation(',s);self.assertNotIn('MW.MethodWindow =',s)
        self.assertNotIn("normal_route_or_fire=False,input_once_proven=False",s)
        self.assertNotIn('OWN_TWO_ORIGINAL_INPUTFREE_FIRST_STATE_METHOD_ONLY',s)
        self.assertEqual(new['natural-ai/active.ini'],old['natural-ai/active.ini'].replace(b'bot_iTestTarget=-1;',b'bot_iTestTarget=0;'))
        self.assertIn(hashlib.sha256(new['natural-ai/active.ini']).hexdigest().encode(),new['first_state_natural_ai.py'])
        self.assertIn(b'ORIGINAL_RESPAWN030_SOURCE_OWNERSHIP_V1',new['first_state_natural_ai.py'])
        self.assertEqual(new['method-api/first_state_natural_ai.py'],new['first_state_natural_ai.py'])

    def test_new_condition_metadata_is_truthful_and_limits_exact(self):
        m=self.helper();outer=json.loads(read(ROOT/'source-manifest.json'));nested=json.loads(read(ROOT/'method-api/source-manifest.json'))
        a,b=m.contracts(outer,nested)
        for old,new in((outer,a),(nested,b)):
            self.assertIs(new['runtime_reviewed'],False);self.assertIs(new['native_qualified'],False)
            self.assertEqual(new['original_respawn_condition']['native_input_attempts'],2)
            self.assertIs(new['original_respawn_condition']['readiness_changed'],True)
            self.assertIs(new['original_respawn_condition']['first_valid_state_damage_proven'],False)
            self.assertIs(new['original_respawn_condition']['basis_reader_colt_preparation'],False)
            self.assertIs(new['original_respawn_condition']['basis_reader_mouse_input_profile'],False)
            self.assertIs(new['original_respawn_condition']['per_frame_mouse_gain_prescan_globals_requested'],False)
            self.assertIs(new['original_respawn_condition']['separate_nosmooth_controls_effective_double_read_unchanged'],True)
            self.assertEqual(new['registered_damage_contract']['inputs'],2)
            self.assertEqual(new['registered_damage_contract']['queue_full_rows'],64)
            self.assertEqual(new['registered_damage_contract']['max_native_edges'],16384)
            for key in('host_budget','autodrain_limits','transport_limits','legacy_limits'):
                if key in old:self.assertEqual(old[key],new[key])
        self.assertFalse(a['native_ready']);self.assertFalse(a['prior_control_transfer_authorized'])

    def test_source_planner_pins_actual_parent_not_an_arbitrary_fixture(self):
        m=self.helper();old={n:read(ROOT/n)for n in m.CHANGED}
        bad=dict(old);bad['run_dual.py']+=b'\n#unrelated mutation\n'
        with self.assertRaises(ValueError):m.changed_sources(bad)

    def actual_roles_fixture(self,root,evidence):
        from test_first_state_natural_ai import fixture,gms,raw_log
        m=self.helper();changed=m.changed_sources({n:read(ROOT/n)for n in m.CHANGED})
        nai={'__file__':str(root/'first_state_natural_ai.py')}
        exec(compile(changed['first_state_natural_ai.py'],'actual_transformed_NAI','exec'),nai)
        frame,records,pins=fixture();payloads=[b'fake-own-dll',b'fake-config',b'fake-nav',b'fake-maps',b'fake-settings',raw_log().encode()]
        for name,data in zip(nai['TARGETS'],payloads):
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        p=root/'botA/Data/SeriousSam.gms';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gms())
        for key,data in zip(('BOT_GAME','ACTIVE_CONFIG_SHA','NAV_SHA','MAPS_SHA','SETTINGS_SHA'),payloads):nai[key]=hashlib.sha256(data).hexdigest()
        pins['botA']['GameMP.dll']['sha256']=nai['BOT_GAME']
        staging={'schema':'ORIGINAL_RESPAWN030_STAGING_V1','log_epoch':frame['natural_ai_ownership']['log_epoch'],
                 'staged':{k:hashlib.sha256(v).hexdigest()for k,v in zip(('dll_sha256','config_sha256','nav_sha256'),payloads)}}
        nai=types.SimpleNamespace(**nai)
        server=dict(frame['roles']['vanilla'],game_tick=5.,process_identity=records['server']['identity'])
        pair={'server':server,'vanilla':dict(server,process_identity=records['vanilla']['identity']),
              'monotonic_started':1.,'monotonic_finished':1.01}
        samples=[{'game_tick':5.,'process_identity':records['server']['identity'],'players':[
          dict(row,slot=slot,present=True)for slot,row in enumerate(frame['roles'].values())]}]
        rotations=[];identities=[];clock=types.SimpleNamespace(t=1.,monotonic=lambda:1.)
        def paired():rotations.append(pair);return pair
        spec=importlib.util.spec_from_file_location('actual_RP',HELPER.with_name('a1_original_respawn_method.py'))
        rp=importlib.util.module_from_spec(spec);spec.loader.exec_module(rp)
        report={'natural_ai_staging':staging}
        ns={'R':root,'E':evidence,'NAI':nai,'RP':rp,'time':clock,'parent_started':0.,'report':report,
            'native_rotation_pair':paired,'samples':samples,'rotation_samples':rotations,
            'mapping':{'vanilla':0,'botA':1},'entity_ids':{0:101,1:102},'records':records,'pins':pins,
            'own_identity':identities.append,'S':types.SimpleNamespace(key=lambda x:x['entity_id'])}
        tree=ast.parse(changed['run_dual.py'])
        nodes=[n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name in('native_roles','native_roles_in_scope')]
        setup=[n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ownership_reads'for t in n.targets)]
        exec(compile(ast.Module(body=setup+nodes,type_ignores=[]),'actual_runner_native_roles_closure','exec'),ns)
        return ns,identities

    def test_actual_native_roles_capture_twice_is_fresh_exclusive_not_cached(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d)/'arena';root.mkdir();evidence=Path(d)/'evidence';evidence.mkdir()
            ns,identities=self.actual_roles_fixture(root,evidence)
            try:
                first=ns['native_roles']();second=ns['native_roles']()
            except FileExistsError as error:self.fail('actual second native_roles capture collides: '+str(error))
            self.assertIsNot(first,second);self.assertIsNot(first['natural_ai_ownership'],second['natural_ai_ownership'])
            self.assertEqual(identities,['botA']*4)
            paths=sorted(evidence.glob('respawn-role-reads/*/natural-ai-ownership.json'))
            self.assertEqual(len(paths),2);self.assertEqual(len(ns['ownership_reads'].attempts),2)
            for p in paths:self.assertEqual(p.stat().st_mode&0o777,0o600)
            (root/ns['NAI'].TARGETS[-1]).write_bytes(b'bad fresh log')
            with self.assertRaisesRegex(ValueError,'source/player-index'):ns['native_roles']()
            self.assertEqual(len(list(evidence.glob('respawn-role-reads/*/natural-ai-ownership.json'))),3)
            self.assertTrue(ns['ownership_reads'].failed)

    def test_fresh_roles_feed_actual_native_context_and_strict_sample_twice(self):
        from test_retail_inventory_animator_context_patch import Memory
        with tempfile.TemporaryDirectory()as d:
            root=Path(d)/'arena';root.mkdir();evidence=Path(d)/'evidence';evidence.mkdir()
            ns,unused=self.actual_roles_fixture(root,evidence);memory=Memory(animator=0)
            bindings=json.loads(read(ROOT/'method-api/vendor/observer/bindings/original-bindings.json'))
            rows=ns['samples'][0]['players']
            for row in rows:
                row.update(spawned_tick=2.5,health=100.,last_buttons=0)
                for key,value in [('entity_flags',8),('player_flags',1),('may_respawn',0),('buttons_now',0)]:
                    memory.put(row['entity_pointer']+bindings['offsets'][key],'I',value)
                for key,value in [('spawn_clock',2.5),('health',100.)]:memory.put(row['entity_pointer']+bindings['offsets'][key],'f',value)
            pair=ns['native_rotation_pair']();ns['rotation_samples'].clear()
            pair['server'].update(spawned_tick=2.5,health=100.,last_buttons=0,present=True,slot=0)
            pair['vanilla'].update(spawned_tick=2.5,health=100.,last_buttons=0,present=True,slot=0)
            tree=ast.parse(read(ROOT/'method-api/native_first_state.py'))
            fn=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='input_frame')
            now=[1.01]
            env={'struct':struct,'math':math,'time':types.SimpleNamespace(monotonic=lambda:now[0]),
                 'observer_policy':lambda:types.SimpleNamespace(BINDINGS=bindings),'require':ns['NAI'].require}
            exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_NativeContext_input_frame','exec'),env)
            registry={role:{'id':row['entity_id'],'pointer':hex(row['entity_pointer']),'world':hex(row['world_pointer'])}
                      for role,row in zip(('vanilla','botA'),rows)}
            ctx=types.SimpleNamespace(registry=registry,read=memory.read,guard=lambda:None,
                host={r:v['identity']for r,v in ns['records'].items()},
                expected={'world':hex(rows[0]['world_pointer']),'session':'0x310000','session_level':0})
            ctx.input_frame=types.MethodType(env['input_frame'],ctx)
            initial=ns['native_roles']()
            cls=ns['RP'].make_window_class(types.SimpleNamespace(MethodWindow=object));window=object.__new__(cls)
            window.record={'readiness_reads':[]};window.context=ctx;window.prep_context=None
            window.read_roles=ns['native_roles'];window.now=lambda:now[0]
            first=window._sample();second=window._sample()
            self.assertEqual(first,second);self.assertEqual(len(ns['ownership_reads'].attempts),3)
            self.assertIsNot(initial['natural_ai_ownership'],window.record['readiness_reads'][0]['frame'])
            for row in rows:
                for key in('may_respawn','buttons_now'):
                    self.assertEqual(memory.calls.count((row['entity_pointer']+bindings['offsets'][key],4)),4)
            # Fresh custody does not refresh the paired sample timestamp or relax .2s.
            now[0]=1.21
            with self.assertRaisesRegex(ValueError,'fresh .2s frame'):window._sample()
            self.assertIn('error',window.record['readiness_reads'][-1])
            self.assertEqual(len(ns['ownership_reads'].attempts),4)

    def reader_functions(self):
        tree=ast.parse(read(ROOT/'tools/retail_inventory_readonly.py'))
        nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in('EvidenceError','require','unpack','snapshot')]
        ctor=copy.deepcopy(next(n for n in next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='InventoryReader').body if isinstance(n,ast.FunctionDef)and n.name=='__init__'))
        # Exact executed constructor prefix, stopping before filesystem/proc work;
        # all production flag guards are unchanged. Not a fake full-reader PASS.
        stop=next(i for i,n in enumerate(ctor.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Attribute)and t.attr=='root'for t in n.targets))
        ctor.body=ctor.body[:stop];ctor.name='actual_constructor_flag_prefix'
        env={'Path':Path,'math':math,'struct':struct}
        exec(compile(ast.Module(body=nodes+[ctor],type_ignores=[]),'actual_reader_guard_and_snapshot','exec'),env)
        return env

    def test_actual_transformed_constructor_and_snapshot_flags_are_compatible(self):
        m=self.helper();s=m.changed_sources({n:read(ROOT/n)for n in m.CHANGED})['run_dual.py']
        calls=[n for n in ast.walk(ast.parse(s))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='InventoryReader'and any(k.arg=='mouse_input_profile'for k in n.keywords)]
        self.assertEqual(len(calls),1)
        flags={k.arg:ast.literal_eval(k.value)for k in calls[0].keywords}
        ns=self.reader_functions();receiver=types.SimpleNamespace()
        ns['actual_constructor_flag_prefix'](receiver,11,12,'unused_no_runtime','unused_hash',**flags)
        self.assertIs(receiver.colt_preparation,False);self.assertIs(receiver.mouse_input_profile,False)
        from test_retail_inventory_animator_context_patch import Memory
        memory=Memory(animator=0);memory.put(memory.entity+0xcc,'f',0.)
        value=ns['snapshot'](memory.read,memory.engine,(4,5,6,7),**flags)
        self.assertEqual(value['players'][0]['health'],0.)
        self.assertNotIn('colt_preparation',value['players'][0]);self.assertIsNone(value['players'][0]['weapons'])
        self.assertNotIn((memory.entity+0x388,4),memory.calls)
        bad={'rotation_diagnostics':True,'colt_preparation':False,'mouse_input_profile':True}
        with self.assertRaisesRegex(ns['EvidenceError'],'mouse input profile requires explicit Colt mode'):
            ns['actual_constructor_flag_prefix'](types.SimpleNamespace(),11,12,'unused','unused',**bad)
        memory.calls.clear()
        with self.assertRaisesRegex(ns['EvidenceError'],'mouse input profile requires explicit Colt mode'):
            ns['snapshot'](memory.read,memory.engine,(4,5,6,7),**bad)
        self.assertEqual(memory.calls,[])

    def test_actual_basis_snapshot_fields_feed_unchanged_context_double_reads(self):
        from test_retail_inventory_animator_context_patch import Memory
        ns=self.reader_functions();m=Memory(animator=0);other=m.entity+0x10000
        bindings=json.loads(read(ROOT/'method-api/vendor/observer/bindings/original-bindings.json'))
        for slot,pointer,id,hp,flags,may in[(4,m.entity,321,0.,0,2),(5,other,322,100.,8,0)]:
            m.put(m.table+136*slot,'II',1,pointer);m.put(pointer+0x1c,'I',id);m.put(pointer+0x8c,'I',m.world)
            for k,v in [('entity_flags',flags),('player_flags',1),('may_respawn',may),('buttons_now',0)]:m.put(pointer+bindings['offsets'][k],'I',v)
            m.put(pointer+bindings['offsets']['health'],'f',hp);m.put(pointer+bindings['offsets']['spawn_clock'],'f',2.5)
        raw=ns['snapshot'](m.read,m.engine,(4,5,6,7),rotation_diagnostics=True,colt_preparation=False,mouse_input_profile=False)
        rows={role:r for role,r in zip(('vanilla','botA'),[x for x in raw['players']if x['present']])}
        source=ast.parse(read(ROOT/'method-api/native_first_state.py'))
        cls=next(n for n in source.body if isinstance(n,ast.ClassDef)and n.name=='NativeContext')
        fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='input_frame')
        env={'struct':struct,'math':math,'copy':copy,'time':types.SimpleNamespace(monotonic=lambda:1.01),
             'observer_policy':lambda:types.SimpleNamespace(BINDINGS=bindings),'require':ns['require']}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'exact_NativeContext_input_frame','exec'),env)
        registry={r:{'id':a['entity_id'],'pointer':hex(a['entity_pointer']),'world':hex(a['world_pointer'])}for r,a in rows.items()}
        ctx=types.SimpleNamespace(registry=registry,read=m.read,guard=lambda:None,host={'server':[11,12],'vanilla':[21,22],'botA':[31,32]},expected={'world':hex(m.world),'session':'0x310000','session_level':0})
        m.calls.clear();v=env['input_frame'](ctx,{'monotonic_started':1.,'roles':rows})
        self.assertEqual(v['actors']['vanilla']['may_respawn'],2);self.assertEqual(v['actors']['vanilla']['buttons_now'],0)
        for p in(m.entity,other):
            for k in('may_respawn','buttons_now'):self.assertEqual(m.calls.count((p+bindings['offsets'][k],4)),2)

    def test_unchanged_nosmooth_controls_sample_accepts_basis_reader_and_checks_guards(self):
        from test_a1_controls_diagnostic import ControlsTests
        memory,gb,eb,controls,inp=ControlsTests('runTest').fixture()
        binding=json.loads(read(ROOT/'a1_controls_original_bindings.json'))
        for guard in binding['guards']:
            base={'GameMP.dll':gb,'Engine.dll':eb}[guard['module']];data=bytearray.fromhex(guard['hex'])
            for offset in guard['highlow_offsets']:
                struct.pack_into('<I',data,offset,(struct.unpack_from('<I',data,offset)[0]+base-guard['preferred_base'])&0xffffffff)
            for i,b in enumerate(data):memory.bytes[base+guard['rva']+i]=b
        env={'__file__':str(ROOT/'a1_controls_diagnostic.py')};exec(compile(read(ROOT/'a1_controls_diagnostic.py'),'actual_controls_source','exec'),env)
        env['BINDINGS']=types.SimpleNamespace(read_text=lambda:json.dumps(binding))
        checks=[];reader=types.SimpleNamespace(colt_preparation=False,mouse_input_profile=False,_guard=lambda:checks.append('guard'),_read=memory,
            bases={'GameMP.dll':gb,'Engine.dll':eb},pins={n:types.SimpleNamespace(sha256=sha)for n,sha in binding['original_sha256'].items()},identity=[21,22])
        observation=env['sample'](reader,local_slot=0)
        actual={};exec(compile(read(ROOT/'a1_nosmooth_intervention.py'),'actual_NIP_source','exec'),actual)
        actual['require_effective'](observation);self.assertEqual(checks,['guard','guard'])
        self.assertEqual(observation['process_identity'],[21,22]);self.assertTrue(observation['raw_reads'])
        memory.put(controls+0x15c,'i',1)
        with self.assertRaisesRegex(ValueError,'global_smooth'):actual['require_effective'](env['sample'](reader,local_slot=0))

if __name__=='__main__':unittest.main()
