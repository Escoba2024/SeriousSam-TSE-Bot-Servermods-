"""Actual Parent staging/identity AST fixtures, no native role calls."""
import ast
import hashlib
import json
import os
from pathlib import Path
import struct
import types
import unittest
import tempfile
import importlib.util
from unittest.mock import patch as mockpatch
try:
    import first_state_natural_ai_patch as patch
except ImportError:
    patch=None
import first_state_natural_ai as N
from test_first_state_natural_ai import fixture

P=Path('/srv/tse-a1-first-state-qjs10-v4-disabled-20261115')
def read(p):
    with os.fdopen(os.open(p.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'r')as f:return f.read()
RUNNER=read(P/'run_dual.py');NATIVE=read(P/'method-api/native_first_state.py')
BINDINGS=json.loads(read(P/'method-api/vendor/observer/bindings/original-bindings.json'))
def read_bytes(p):
    with os.fdopen(os.open(p.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()

def draft_assets(draft):
    assets=Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115')
    base=read_bytes(P/'CecilObserver.ini') if (P/'CecilObserver.ini').exists() else read_bytes(P/'observer.ini')
    active=base.replace(b'sam_iMaxFPSActive=10;\n',b'').replace(b'sam_iMaxFPSInactive=10;\n',b'')+read_bytes(assets/'canonical.ini')
    (draft/'natural-ai/active.ini').write_bytes(active)
    for name in ('maps.txt','settings.txt'):(draft/'natural-ai'/name).write_bytes(read_bytes(assets/name))

def source(name):
    s=RUNNER if name=='run_dual.py'else NATIVE
    return s if patch is None else patch.transform(name,s)

def functions(s,names,ns):
    nodes=[n for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual-native-functions>','exec'),ns)

class ActualSourceTests(unittest.TestCase):
    def test_actual_control_status_names_natural_ai_and_preserves_fail(self):
        name='first_state_inputfree_method.py';original=read(P/name)
        text=patch.transform(name,original)if name in patch.PARENT_SHA else original
        ns={'ROLES':('server','vanilla','botA')};functions(text,['candidate_status'],ns)
        report={'status':'CLEANUP_PENDING','errors':[],'units_closed_verified':True,
                'cleanup':{role:{'closed':True}for role in ns['ROLES']},
                'restoration':{'restored':True},'post_close_logs':{'accepted':True}}
        window=types.SimpleNamespace(mode='control',proxy=None,record={'observation_complete':True,
                'observed_seconds':10,'input_emissions':0,'before_roles_cleanup_complete':True,'after_roles_cleanup_complete':True,'worker_created':False})
        self.assertEqual(ns['candidate_status'](report,window),'PASS_LIMITED_UNINSTRUMENTED_NATURAL_AI030_ORIGINAL_VICTIM_ONLY')
        report['errors'].append('actual error still fatal');self.assertEqual(ns['candidate_status'](report,window),'FAIL')
        self.assertEqual(patch.reverse(name,text),original)
    def test_staging_guards_precede_all_writes_and_victim_untouched(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'root';draft=Path(tmp)/'draft';ev=Path(tmp)/'ev'
            root.mkdir();ev.mkdir();(draft/'natural-ai').mkdir(parents=True);draft_assets(draft)
            for name in N.TARGETS:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old')
            victim=root/'vanilla/Bin/GameMP.dll';victim.parent.mkdir(parents=True);victim.write_bytes(b'protected original victim')
            class Tx:
                sealed=True
                def __init__(self):self.root=root;self.records={k:{'existed':True,'sha256':hashlib.sha256(b'old').hexdigest()}for k in N.TARGETS}
                def path(self,name):return root/name
            tx=Tx()
            def unchanged():self.assertTrue(all(read_bytes(root/n)==b'old'for n in N.TARGETS));self.assertEqual(read_bytes(victim),b'protected original victim')
            del tx.records[N.TARGETS[2]]
            with self.assertRaises(ValueError):N.stage_candidate(tx,root,draft,ev)
            unchanged();tx=Tx();(draft/'natural-ai/maps.txt').write_bytes(b'wrong nav catalog')
            with self.assertRaises(ValueError):N.stage_candidate(tx,root,draft,ev)
            unchanged();draft_assets(draft);tx.root=ev
            with self.assertRaises(ValueError):N.stage_candidate(tx,root,draft,ev)
            unchanged()

    def test_actual_module_pin_assignment_uses_exact_role_hash(self):
        tree=ast.parse(source('run_dual.py'))
        call=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)and isinstance(n.value,ast.Call)
                  and isinstance(n.value.func,ast.Attribute)and n.value.func.attr=='pin_modules')
        observed=[]
        for role in ('server','vanilla','botA'):
            ns={'pins':{},'role':role,'receipt':types.SimpleNamespace(identity=(10,20)),
                'P':types.SimpleNamespace(ORIGINALS={'GameMP.dll':N.ORIGINAL_GAME}),'NAI':N,
                'B':types.SimpleNamespace(pin_modules=lambda r,i,h:observed.append((r,h)))}
            exec(compile(ast.Module(body=[call],type_ignores=[]),'<actual-role-pin>','exec'),ns)
        self.assertEqual(observed,[('server',N.ORIGINAL_GAME),('vanilla',N.ORIGINAL_GAME),('botA',N.BOT_GAME)])

    def test_capture_real_files_positive_and_rejected_source_raw_preserved(self):
        self.assertTrue(hasattr(N,'capture_ownership'),'missing actual bounded source custody capture')
        frame,records,pins=fixture();q=frame.pop('natural_ai_ownership')
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'root';ev=Path(tmp)/'evidence';root.mkdir();ev.mkdir()
            files={N.TARGETS[0]:read_bytes(N.DLL_SOURCE),N.TARGETS[2]:read_bytes(N.NAV_SOURCE),
                   N.TARGETS[-1]:q['log_text'].encode(), 'botA/Data/SeriousSam.gms':bytes.fromhex(q['gms_hex'])}
            draft=Path(tmp)/'draft';(draft/'natural-ai').mkdir(parents=True);draft_assets(draft)
            files.update({N.TARGETS[1]:read_bytes(draft/'natural-ai/active.ini'),N.TARGETS[3]:read_bytes(draft/'natural-ai/maps.txt'),N.TARGETS[4]:read_bytes(draft/'natural-ai/settings.txt')})
            for name,data in files.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            staging={'schema':'NATURAL_AI030_STAGING_V1','log_epoch':q['log_epoch'],
                     'staged':{'dll_sha256':N.BOT_GAME,'config_sha256':N.ACTIVE_CONFIG_SHA,'nav_sha256':N.NAV_SHA}}
            discovered_ids={int(k):v for k,v in q['entity_ids'].items()}
            result=N.capture_ownership(root,ev,frame,records,pins,q['mapping'],discovered_ids,staging)
            self.assertEqual(N.roles_from_receipt(dict(frame,natural_ai_ownership=result),records,pins)['botA'],'bot')
            saved=json.loads(read_bytes(ev/'natural-ai-ownership.json'))
            self.assertEqual(saved['raw_log_sha256'],hashlib.sha256(files[N.TARGETS[-1]]).hexdigest())
            self.assertEqual((ev/'natural-ai-ownership.json').stat().st_mode&0o777,0o600)
            ev2=Path(tmp)/'rejected';ev2.mkdir();(root/N.TARGETS[-1]).write_bytes(b'no actual bot Source line\n')
            with self.assertRaises(ValueError):N.capture_ownership(root,ev2,frame,records,pins,q['mapping'],discovered_ids,staging)
            self.assertEqual(json.loads(read_bytes(ev2/'natural-ai-ownership.json'))['log_text'],'no actual bot Source line\n')

    def test_context_rejects_unproven_bot_before_host_or_memory(self):
        ns={'NAI':N};functions(source('method-api/native_first_state.py'),['NativeContext'],ns)
        frame,records,pins=fixture();frame.pop('natural_ai_ownership');calls=[]
        with self.assertRaises(ValueError):ns['NativeContext'](frame,records,pins,lambda:calls.append('guard'),Path('/never-open'))
        self.assertEqual(calls,[])

    def test_whole_sources_inverse_and_mutations(self):
        for name,s in [('run_dual.py',RUNNER),('method-api/native_first_state.py',NATIVE),('first_state_inputfree_method.py',read(P/'first_state_inputfree_method.py'))]:
            self.assertEqual(patch.reverse(name,patch.transform(name,s)),s)
            with self.assertRaises(ValueError):patch.transform(name,s+'\n')
            with self.assertRaises(ValueError):patch.reverse(name,patch.transform(name,s)+'\n')

    def test_real_transaction_staging_and_restore(self):
        self.assertTrue(hasattr(N,'stage_candidate'),'missing sealed real candidate staging')
        spec=importlib.util.spec_from_file_location('natural_ai_parent_transaction',P/'transaction.py')
        # Execute exact parent text loaded without changing external atime.
        tx=types.ModuleType(spec.name);exec(compile(read(P/'transaction.py'),str(P/'transaction.py'),'exec'),tx.__dict__)
        with tempfile.TemporaryDirectory()as tmp:
            base=Path(tmp);root=base/'root';ev=base/'evidence';draft=base/'draft'
            root.mkdir();ev.mkdir();(draft/'natural-ai').mkdir(parents=True)
            for relative in N.TARGETS:
                target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
                if relative.endswith(('GameMP.dll','CecilObserver.ini','SeriousSam.log')):
                    target.write_bytes(b'old '+relative.encode());target.chmod(0o640);os.utime(target,ns=(123456789012,234567890123))
            draft_assets(draft)
            before={str(f.relative_to(root)):(read_bytes(f),f.stat().st_mode&0o777,f.stat().st_uid,f.stat().st_gid,f.stat().st_atime_ns,f.stat().st_mtime_ns)for f in root.rglob('*')if f.is_file()}
            transaction=tx.FileTransaction(root,ev,lambda:None)
            N.snapshot_targets(transaction)
            with self.assertRaises(ValueError):N.stage_candidate(transaction,root,draft,ev)
            transaction.seal();staged=N.stage_candidate(transaction,root,draft,ev)
            self.assertEqual(hashlib.sha256(read_bytes(root/'botA/Bin/GameMP.dll')).hexdigest(),N.BOT_GAME)
            self.assertEqual(hashlib.sha256(read_bytes(root/'botA/Scripts/CecilObserver.ini')).hexdigest(),N.ACTIVE_CONFIG_SHA)
            self.assertEqual(staged['log_epoch']['empty_sha256'],hashlib.sha256(b'').hexdigest())
            self.assertEqual(read_bytes(root/'botA/SeriousSam.log'),b'')
            self.assertEqual((ev/'natural-ai-staging.json').stat().st_mode&0o777,0o600)
            result=transaction.restore();self.assertTrue(result['restored'],result)
            after={str(f.relative_to(root)):(read_bytes(f),f.stat().st_mode&0o777,f.stat().st_uid,f.stat().st_gid,f.stat().st_atime_ns,f.stat().st_mtime_ns)for f in root.rglob('*')if f.is_file()}
            self.assertEqual(before,after)

    def test_actual_parent_staging_must_stop_copying_original_to_bot(self):
        s=source('run_dual.py');tree=ast.parse(s);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        copy_node=next(n for n in ast.walk(main)if isinstance(n,ast.For)and isinstance(n.iter,ast.Tuple)
                       and [x.value for x in n.iter.elts]in(['server','botA'],['server'])
                       and any(isinstance(c,ast.Call)and isinstance(c.func,ast.Attribute)and c.func.attr=='copy2'for c in ast.walk(n)))
        store={'/fixture/vanilla/Bin/GameMP.dll':N.ORIGINAL_GAME}
        def cp(a,b):store[str(b)]=store[str(a)]
        def staged(*args):store['/fixture/botA/Bin/GameMP.dll']=N.BOT_GAME;return {'scope':'called-active-source'}
        ns={'R':Path('/fixture'),'shutil':types.SimpleNamespace(copy2=cp),'os':types.SimpleNamespace(chown=lambda *a:None),
            'NAI':types.SimpleNamespace(stage_candidate=staged),'transaction':None,'DRAFT':None,'E':None,'report':{},'save':lambda:None}
        exec(compile(ast.Module(body=[copy_node],type_ignores=[]),'<actual-dll-staging>','exec'),ns)
        calls=[n for n in ast.walk(main)if isinstance(n,ast.Assign)and isinstance(n.value,ast.Call)
               and isinstance(n.value.func,ast.Attribute)and isinstance(n.value.func.value,ast.Name)
               and n.value.func.value.id=='NAI'and n.value.func.attr=='stage_candidate']
        for call in calls:exec(compile(ast.Module(body=[call],type_ignores=[]),'<actual-stage-call>','exec'),ns)
        self.assertEqual(store['/fixture/botA/Bin/GameMP.dll'],N.BOT_GAME)
        self.assertEqual(store['/fixture/server/Bin/GameMP.dll'],N.ORIGINAL_GAME)
        self.assertEqual(len(calls),1)

    def test_actual_build_identity_changes_only_bound_bot_label(self):
        ns={'hashlib':hashlib,'json':json,'struct':struct,'NAI':N,
            'observer_policy':lambda:types.SimpleNamespace(BINDINGS=BINDINGS)}
        functions(source('method-api/native_first_state.py'),['NativeBindingError','require','sha','canonical','build_identity'],ns)
        frame,records,pins=fixture();frame['natural_ai_ownership']['staged']['config_sha256']=N.ACTIVE_CONFIG_SHA
        roles=N.roles_from_receipt(frame,records,pins)
        g=BINDINGS;engine=0x600c0000;entities=0x60310000;network=0x80000;session=0x90000
        mem={engine+g['network']['global_rva']:network,network+g['network']['session_pointer_offset']:session,
             network+g['network']['is_server_offset']:1,session+g['network']['session_level_offset']:1}
        registry={}
        for role,row in frame['roles'].items():
            ptr=row['entity_pointer'];registry[role]={'id':row['entity_id'],'pointer':hex(ptr),'world':hex(row['world_pointer'])}
            mem[ptr+g['offsets']['entity_id']]=row['entity_id'];mem[ptr+g['offsets']['entity_world']]=row['world_pointer'];mem[ptr+g['offsets']['entity_flags']]=0
        def read_mem(addr,size):self.assertEqual(size,4);return struct.pack('<I',mem[addr])
        args=[read_mem,{r:list(v['identity'])for r,v in records.items()},{'Engine.dll':engine,'EntitiesMP.dll':entities},registry,'fixture-epoch']
        value=ns['build_identity'](*args,**({'actor_roles':roles}if patch else {}))
        self.assertEqual({p['id']:p['role']for p in value['players']},{101:'vanilla',102:'bot'})

if __name__=='__main__':unittest.main()
