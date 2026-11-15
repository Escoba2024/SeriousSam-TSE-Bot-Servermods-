"""Actual pinned Observer in Gum-style deferred-detach VM; no native code run."""
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PARENT=Path('/srv/tse-a1-first-state-wine-identity-disabled-20261115/method-api')
HARNESS=Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor/tests/observer_harness.js')
TOOL=Path(__file__).with_name('first_state_getter_boundary_patch.py')
BODY_SHA='d80e65abaf9ef8e545435d83e564e556773fc8b5ec6420439cff00a520643fe4'
COMPILED_SHA='34e31ff811b9dc79cc741f742ace66bcf494df683632a9fd7bd3d2b0da9c7baf'


def module():
    spec=importlib.util.spec_from_file_location('getterboundary',TOOL)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def fixture_source():
    s=HARNESS.read_text()
    def once(old,new):
        nonlocal s
        assert s.count(old)==1,old;s=s.replace(old,new,1)
    once(' const failDetach=new Set(),attemptDetach=[],nativeWrites=[];',
        """ const failDetach=new Set(),attemptDetach=[],nativeWrites=[];
 let depth=0,pending=[],holdCommit=false,onPending=null,pendingReads=0,commits=0;
 function commit(){const jobs=pending;pending=[];for(const f of jobs)f();commits++;}
 function boundary(fn){depth++;try{return fn();}finally{depth--;if(depth===0&&!holdCommit)commit();}}
""")
    once('function bytes(n,len){reads++;clock+=readCost;', 'function bytes(n,len){if(depth>0&&pending.length>0)pendingReads++;reads++;clock+=readCost;')
    anchor=" const bases={'Engine.dll':Number(cfg.engine_base),'EntitiesMP.dll':Number(cfg.entities_base)};"
    once(anchor,anchor+"""
 for(const[name,base]of Object.entries(bases)){
  const b=Buffer.alloc(4096),nt=name==='Engine.dll'?264:248;
  b.writeUInt16LE(0x5a4d,0);b.writeUInt32LE(nt,0x3c);b.writeUInt32LE(0x4550,nt);
  b.writeUInt16LE(0x14c,nt+4);b.writeUInt16LE(224,nt+20);b.writeUInt16LE(0x10b,nt+24);
  b.writeUInt32LE(G.modules[name].image_size,nt+80);put(base,b);
 }
""")
    once('getModuleByName:n=>moduleOverrides[n]||{base:P(bases[n]),size:G.modules[n].image_size}',
        "getModuleByName:n=>{throw Error('unable to find module '+n);}")
    once('if(!detached){b.set(old,i);callbacks.delete(n);detached=true;detaches++;}',
        'if(!detached){pending.push(()=>{b.set(old,i);callbacks.delete(n);});detached=true;detaches++;if(onPending)onPending(n);}')
    once('const api=sandbox.rpc.exports;',
        'const api=Object.fromEntries(Object.entries(sandbox.rpc.exports).map(([k,f])=>[k,(...args)=>boundary(()=>f(...args))]));')
    once('cb.onEnter.call(ctx,[]);return {cb,ctx};','boundary(()=>cb.onEnter.call(ctx,[]));return {cb,ctx};')
    once('function leave(frame,returned=0){frame.cb.onLeave.call(frame.ctx,P(returned));}',
        'function leave(frame,returned=0){boundary(()=>frame.cb.onLeave.call(frame.ctx,P(returned)));}')
    once('cb.onEnter.call({threadId:thread,context:{eax:P(2),edx:P(0x900000)}});',
        "boundary(()=>(typeof cb==='function'?cb:cb.onEnter).call({threadId:thread,context:{eax:P(2),edx:P(0x900000)}}));")
    once('return {api,cfg,G,P,regions,bases,callbacks,guardBytes,',
        'return {commit,get pending(){return pending.length},get depth(){return depth},get commits(){return commits},get pendingReads(){return pendingReads},set holdCommit(v){holdCommit=v},set onPending(v){onPending=v},api,cfg,G,P,regions,bases,callbacks,guardBytes,')
    return s


class ActualDeferredGetterVM(unittest.TestCase):
    def run_case(self,case,legacy=False):
        body=(PARENT/'observer_body.js').read_text();compiled=(PARENT/'vendor/observer/observer.js').read_text()
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),BODY_SHA);self.assertEqual(hashlib.sha256(compiled.encode()).hexdigest(),COMPILED_SHA)
        source=compiled if legacy or not TOOL.exists()else module().patch_compiled(compiled)
        if not legacy and os.environ.get('FIRST_STATE_BOUNDARY_REMOVAL_ONLY')=='1':
            # Deliberately incomplete actual-source mutation: proves why merely
            # deleting the eager check leaves the two Root-reviewed holes.
            eager="      need(exact('Engine.dll',g),'getter restore mismatch after binding');\n"
            self.assertEqual(compiled.count(eager),1);source=compiled.replace(eager,'',1)
        with tempfile.TemporaryDirectory(prefix='first-state-getter-boundary-')as tmp:
            root=Path(tmp);(root/'tests').mkdir();(root/'bindings').mkdir()
            shutil.copyfile(PARENT/'vendor/observer/bindings/original-bindings.json',root/'bindings/original-bindings.json')
            (root/'tests/observer_harness.js').write_text(fixture_source());(root/'observer.js').write_text(source)
            r=subprocess.run(['node',str(Path(__file__).with_name('test_first_state_getter_boundary_vm.js')),str(root/'tests/observer_harness.js'),case],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_old_actual_inside_getter_check_faults_before_commit(self):self.run_case('legacyfault',legacy=True)
    def test_commit_only_after_callback_exit_then_exact_i1_i2(self):self.run_case('commit')
    def test_no_following_callback_drain_proves_full_getter(self):self.run_case('drainonly')
    def test_mutation_before_first_main_row_is_sticky(self):self.run_case('main')
    def test_mutation_before_first_nonmain_row_is_sticky(self):self.run_case('nonmain')
    def test_mutation_before_nonmain_admitted_leave_is_sticky(self):self.run_case('nonmainleave')
    def test_mutation_after_hoststop_without_any_callback_is_sticky(self):self.run_case('stoppeddrift')
    def test_missing_commit_after_hoststop_is_not_restore(self):self.run_case('nocommit')
    def test_stop_during_getter_defers_finish_until_callback_exit(self):self.run_case('stopinside')
    def test_admitted_leave_keeps_full_getter_guard_after_hoststop(self):self.run_case('leave')
    def test_ttl_after_hoststop_stays_failure(self):self.run_case('ttl')
    def test_epoch_identity_after_hoststop_stays_failure(self):self.run_case('identity')
    def test_wine_header_guard_before_attach_unchanged(self):self.run_case('header')
    def test_full_body_guard_before_attach_unchanged(self):self.run_case('body')
    def test_iat_guard_before_attach_unchanged(self):self.run_case('iat')
    def test_default_disabled_unchanged(self):self.run_case('disabled')

    def test_full_body_compiled_g_inverses(self):
        if not TOOL.exists():self.fail('boundary transform absent')
        m=module();old=(PARENT/'observer_body.js').read_text();compiled=(PARENT/'vendor/observer/observer.js').read_text();new=m.patch_body(old);joined=m.patch_compiled(compiled)
        self.assertEqual(m.reverse_body(new),old);self.assertEqual(m.reverse_compiled(joined),compiled)
        self.assertEqual(joined[:-len(new)],compiled[:-len(old)])
        self.assertEqual(new[new.index('function lifetime(){'):new.index('function addError(')],old[old.index('function lifetime(){'):old.index('function addError(')])
        with self.assertRaises(ValueError):m.reverse_body(new.replace("'TLS index changed'","'mutated'"))
        with self.assertRaises(ValueError):m.reverse_compiled(joined.replace('const G=','const G= ',1))


if __name__=='__main__':unittest.main()
