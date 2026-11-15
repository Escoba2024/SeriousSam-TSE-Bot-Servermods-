"""Actual transformed Observer callbacks in the existing memory VM; no native API."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PARENT=Path('/srv/tse-a1-natural-ai030-two-actor-status-v2-disabled-20261115/method-api')
HARNESS=Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor/tests/observer_harness.js')
TOOL=Path(__file__).with_name('first_state_registered_damage_patch.py')

def read(path):
    with os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()

def transform(source):
    if not TOOL.exists():return source
    spec=importlib.util.spec_from_file_location('registered_patch',TOOL)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.patch_compiled(source)

def harness():
    # Reuse the already tested deferred-detach fixture, with explicit NOATIME reads.
    text=read(Path(__file__).with_name('test_first_state_getter_boundary_patch.py')).decode()
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='fixture_source')
    body=ast.get_source_segment(text,node).replace('HARNESS.read_text()','read(HARNESS).decode()')
    env={'HARNESS':HARNESS,'read':read};exec(body,env)
    s=env['fixture_source']()
    s=s.replace('return {commit,get pending()', 'return {sandbox,commit,get pending()',1)
    return s

BASE="""
const assert=require('assert'),vm=require('vm'),{fixture}=require(process.argv[2]);
function done(x){x.api.stop();assert(x.api.status().idle);assert(x.api.finishstop().stopped);return x.api.drain();}
const x=fixture();x.arm();
"""

class ActualRegisteredScope(unittest.TestCase):
    def run_js(self,code,*,legacy=False,mutate=None,extra=None):
        source=read(PARENT/'vendor/observer/observer.js').decode()
        result=source if legacy else transform(source)
        if mutate:result=mutate(result)
        with tempfile.TemporaryDirectory(prefix='a1-registered-scope-')as tmp:
            r=Path(tmp);(r/'tests').mkdir();(r/'bindings').mkdir()
            (r/'bindings/original-bindings.json').write_bytes(read(PARENT/'vendor/observer/bindings/original-bindings.json'))
            (r/'tests/observer_harness.js').write_text(harness())
            (r/'observer.js').write_text(result)
            for n,b in(extra or{}).items():(r/n).write_bytes(b)
            (r/'case.js').write_text(BASE+code)
            p=subprocess.run(['node',str(r/'case.js'),str(r/'tests/observer_harness.js')],capture_output=True,text=True,timeout=8)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            return p.stdout

    def test_worldcast_only_excluded_after_actual_leave(self):
        self.run_js("""
const t=x.startTick();x.api.drain();const c=x.enter('cast_ray',0x100000,[0x700000]);
let p=x.api.drain();assert.equal(p.events.length,0,'old FULL18 still queues worldcast entry');
assert.equal(p.measurement_scope,'REGISTERED_FIRST_STATE_DAMAGE_V1');
assert.equal(p.scope_counters.pending,1);assert.equal(p.scope_counters.entered_excluded,0);
x.leave(c);p=x.api.drain();assert.equal(p.events.length,0);
assert.equal(p.scope_counters.pending,0);assert.equal(p.scope_counters.entered_excluded,1);
assert.equal(p.scope_counters.completed_excluded,1);x.leave(t);p=done(x);assert.equal(p.counters.faults,0);
""")

    def test_relevant_descendant_under_pending_is_sticky_without_fake_row(self):
        self.run_js("""
const t=x.startTick(),c=x.enter('cast_ray',0x100000,[0x700000]);
const a=x.enter('apply_action',0x310000,[0x720000,['f',1]]);
let p=x.api.drain();assert(p.counters.faults>0,'pending parent must not hide a relevant descendant');
assert(p.errors.some(e=>e.message.includes('pending worldcast ancestor')));
assert(!p.events.some(e=>e.kind==='cast_ray'));assert(!p.events.some(e=>e.kind==='apply_action'));
x.leave(a);x.leave(c);x.leave(t);done(x);
""")

    def test_nested_worldcasts_share_actual_stack_and_finalize_both(self):
        self.run_js("""
const t=x.startTick(),a=x.enter('cast_ray',0x100000,[0x700000]),b=x.enter('continue_cast',0x100000,[0x700000]);
let p=x.api.drain();assert.equal(p.scope_counters.pending,2);
x.leave(b);p=x.api.drain();assert.equal(p.scope_counters.pending,1);assert.equal(p.scope_counters.entered_excluded,1);
x.leave(a);x.leave(t);p=done(x);assert.equal(p.scope_counters.entered_excluded,2);assert.equal(p.scope_counters.pending,0);
assert.equal(p.counters.order_calls,3);assert.equal(p.counters.completed_calls,3);assert.equal(p.counters.events_attempted,6);
assert.equal(p.events.length,1);assert.equal(p.counters.events_enqueued,2);assert.equal(p.counters.faults,0);
""")

    def test_registered_full_chain_keeps_actual_payloads_and_no_exclusions(self):
        self.run_js("""
const t=x.startTick();x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);
const p=done(x);assert.equal(p.counters.faults,0,JSON.stringify(p.errors));
const d=p.events.find(e=>e.kind==='receive_damage'&&e.edge==='leave');assert.equal(d.player.health,80);
assert.equal(d.data.payload.chain_bound,true);assert.equal(p.scope_counters.entered_excluded,0);
assert.equal(p.scope_counters.native_edges,p.events.length);assert.equal(x.nativeWrites.length,0);
""")

    def test_differential_original_anchor_sequence_after_worldcast_is_unchanged(self):
        script="""
const t=x.startTick();x.call('cast_ray',0x100000,[0x700000]);
x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);
const p=done(x);assert.equal(p.counters.faults,0,JSON.stringify(p.errors));
console.log(JSON.stringify(p.events.filter(e=>!(e.kind==='cast_ray'&&e.data.scope==='unregistered')).map(e=>{delete e.row_sequence;delete e.native_sequence;delete e.excluded_calls_before;delete e.pending_before;return e;})));
"""
        old=json.loads(self.run_js(script,legacy=True));new=json.loads(self.run_js(script))
        self.assertEqual(new,old,'native sequence/first-state anchors and all retained payloads must equal FULL18')

    def test_deep_registered_ancestor_never_excluded_or_reparented(self):
        script="""
const t=x.startTick();x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();
x.shot({duringReceive(){x.call('continue_cast',0x100000,[0x700000]);}});x.leave(t);
const p=done(x);assert.equal(p.counters.faults,0,JSON.stringify(p.errors));
const e=p.events.filter(e=>e.kind==='continue_cast');assert.equal(e.length,2,'deep Launch/Colt ancestor was lost');
assert.equal(p.scope_counters.entered_excluded,0);assert.equal(e[0].parent_call_id,p.events.find(e=>e.kind==='receive_damage').call_id);
"""
        self.run_js(script)
        # Mutant actually executes and must fail the same production assertion.
        with self.assertRaises(AssertionError):
            self.run_js(script,mutate=lambda s:s.replace('for(let p=f.parent;p;p=p.parent)','for(let p=f.parent;p;p=null)',1))

    def test_excluded_edges_keep_queue_event_ttl_getter_world_guards(self):
        cases={
          'queue':"const t=x.startTick();for(let i=0;i<31;i++)x.call('post_moving',0x300000);const a=x.enter('post_moving',0x300000);x.call('cast_ray',0x100000,[0x700000]);const p=x.api.drain();assert.equal(p.counters.dropped,1);assert.equal(p.stop_reason,'queue overflow');",
          'event':"const t=x.startTick();vm.runInContext('cfg.max_events=2',x.sandbox);x.call('cast_ray',0x100000,[0x700000]);const p=x.api.drain();assert.equal(p.counters.dropped,1);assert.equal(p.stop_reason,'event bound');",
          'ttl':"const t=x.startTick(),c=x.enter('cast_ray',0x100000,[0x700000]);x.clock=6000;x.leave(c);const p=x.api.drain();assert.equal(p.counters.aborted_leaves,1);assert.equal(p.scope_counters.entered_excluded,0);",
          'getter':"const t=x.startTick();x.regions.get(x.bases['Engine.dll']+x.G.modules['Engine.dll'].guards.current_tick.rva)[0]^=1;x.call('cast_ray',0x100000,[0x700000]);const p=x.api.drain();assert(p.counters.faults>0);assert(p.errors.some(e=>e.message.includes('bound getter changed')));",
          'world':"const t=x.startTick();x.u(0x12001c,8);x.call('cast_ray',0x100000,[0x700000]);const p=x.api.drain();assert(p.counters.faults>0);assert(p.errors.some(e=>e.message.includes('session level/epoch changed')));",
          'stack':"const t=x.startTick();for(let i=0;i<x.G.limits.max_stack;i++)x.enter('cast_ray',0x100000,[0x700000]);const p=x.api.drain();assert(p.counters.faults>0);assert(p.errors.some(e=>e.message.includes('callback stack bound')));",
        }
        for name,script in cases.items():
            with self.subTest(guard=name):self.run_js(script)

    def test_missing_leave_and_nonmain_are_never_confirmed_exclusions(self):
        self.run_js("""
const t=x.startTick(),c=x.enter('cast_ray',0x100000,[0x700000]);
x.api.stop();assert.equal(x.api.finishstop().stopped,false);assert.equal(x.api.status().idle,false);
let p=x.api.drain();assert.equal(p.scope_counters.pending,1);assert.equal(p.scope_counters.entered_excluded,0);
x.leave(c);x.leave(t);done(x);
""")
        self.run_js("""
const n=x.enter('cast_ray',0x100000,[0x700000],0x12345678,445);x.leave(n);
const p=done(x);assert.equal(p.events.length,2);assert.equal(p.events[0].data.scope,'non_main');
assert.equal(p.scope_counters.entered_excluded,0);assert.equal(p.counters.non_main_calls,1);
""")

    def test_complete_inverses_and_protected_all_registered_semantics(self):
        from tools import first_state_registered_damage_patch as m
        old=read(PARENT/'observer_body.js').decode();compiled=read(PARENT/'vendor/observer/observer.js').decode()
        new=m.patch_body(old);joined=m.patch_compiled(compiled)
        self.assertEqual(m.reverse_body(new),old);self.assertEqual(m.reverse_compiled(joined),compiled)
        self.assertTrue(joined.endswith(new));self.assertEqual(joined[:-len(new)],compiled[:-len(old)])
        for a,b in [('function requireGetterOriginal(){','function addError('),
                    ('function entity(','function attachKind('),('function restored(){','rpc.exports=')]:
            self.assertEqual(new[new.index(a):new.index(b)],old[old.index(a):old.index(b)])
        guard="if(!bounded(edge==='leave')||counters.events_attempted>cfg.max_events||queue.length>=cfg.max_records)"
        self.assertEqual(new.count(guard),1);self.assertEqual(new.count('clock()'),old.count('clock()'))
        self.assertEqual(new.count('requireGetterOriginal();'),old.count('requireGetterOriginal();'))
        self.assertNotIn('NativeFunction',m.SCOPE_JS)
        for a,b in [("'TLS index changed'","'mutated'"),('const RUNTIME_REVIEWED = false;','const RUNTIME_REVIEWED = true;')]:
            with self.assertRaises(ValueError):m.reverse_body(new.replace(a,b,1))

    def test_actual_failed_leave_is_closed_incomplete_not_still_pending(self):
        self.run_js("""
const t=x.startTick(),c=x.enter('cast_ray',0x100000,[0x700000]);x.clock=6000;x.leave(c);
const p=x.api.drain();assert.equal(p.counters.aborted_leaves,1);assert.equal(p.scope_counters.entered_excluded,0);
assert.equal(p.scope_counters.pending,0,'actual returned candidate is no longer an open pending frame');
assert.equal(p.scope_counters.incomplete_closed,1);assert(!p.active_calls.some(a=>a.kind==='cast_ray'));
""")

    def test_pending_mark_has_no_hidden_full_row_payload_buffer(self):
        self.run_js("""
const t=x.startTick(),a=x.enter('cast_ray',0x100000,[0x700000]),b=x.enter('continue_cast',0x100000,[0x700000]);
assert.equal(vm.runInContext('stack.filter(f=>f.scopePending).some(f=>f.partial!==null)',x.sandbox),false,
 'excluded candidate must not retain full row payloads outside Queue64');
x.leave(b);x.leave(a);x.leave(t);done(x);
""")

if __name__=='__main__':unittest.main()
