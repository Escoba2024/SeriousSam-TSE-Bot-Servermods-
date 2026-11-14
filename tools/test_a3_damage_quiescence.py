"""Node VM of the actual patched JS; mocked memory, no Frida/native game."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from a3_damage_quiescence_patch import patch

ORIGINAL=os.environ.get('TSE_ORIGINAL_DAMAGE_JS')


@unittest.skipUnless(ORIGINAL,'explicit frozen Originaldamage JS source required')
class DamageQuiescenceTests(unittest.TestCase):
    def run_model(self,body):
        original=Path(ORIGINAL).read_text();source=patch(original)
        # Evaluate the actual onLeave expression, including its counter wrapper.
        start=source.index('onLeave:tracked(function(){')+len('onLeave:')
        end=source.index("if(total>=cfg.max_calls)stop('damage call bound');}})",start)+len("if(total>=cfg.max_calls)stop('damage call bound');}})")
        expression=source[start:end]
        setup='''
let detachCount=0;enabled=true;used=true;armedMs=1;expiresMs=200;bindingExpiresMs=150;
tls={};cfg={max_calls:1024,max_records:64};faults=0;dropped=0;records=[];active=[];inFlight=0;
getterHook={detach(){detachCount++;}};damageHook={detach(){detachCount++;}};
getterRestored=()=>true;
const r={before:{health:100,armor:0,spawn_clock:1,current_tick:1},player_id:1,
 tls_bound_at_entry:true,nested:false};
snapshot=()=>({health:0,armor:0,spawn_clock:1,current_tick:1});
'''
        program="const vm=require('vm'),assert=require('assert');const ctx=vm.createContext({rpc:{},Date:{now:()=>100}});\n"
        program+='vm.runInContext('+repr(source+setup)+' ,ctx);\n'
        program+='vm.runInContext('+repr('const leave='+expression+';'+body)+',ctx);\n'
        # The assertions execute inside the same JS lexical context.
        program=program.replace("{rpc:{},Date:","{assert,rpc:{},Date:")
        with tempfile.TemporaryDirectory()as directory:
            path=Path(directory)/'model.js';path.write_text(program)
            done=subprocess.run(['node',str(path)],capture_output=True,text=True,timeout=5)
        self.assertEqual(done.returncode,0,done.stderr[-2000:])

    def test_disarm_retains_hook_and_admitted_record_until_real_leave_then_detaches(self):
        self.run_model('''
inFlight=1;active=[r];stop('host requested');
assert.equal(enabled,false);assert.equal(detachCount,0);
assert.throws(()=>finishStop());assert.equal(detachCount,0);
leave.call({record:r,counted:true,player:{}});
assert.equal(inFlight,0);assert.equal(active.length,0);assert.equal(records.length,1);
assert.equal(records[0].after.health,0);assert.equal(records[0].same_spawn_tick_health_decrease,true);
assert.equal(finishStop().stopped,true);assert.equal(detachCount,2);
''')

    def test_active_getter_or_other_callback_cannot_detach(self):
        self.run_model('''
tracked(function(){stop('host requested');assert.throws(()=>finishStop());assert.equal(detachCount,0);},true)();
assert.equal(listenerCallbacks,0);assert.equal(getterCallbacks,0);
assert.equal(finishStop().stopped,true);assert.equal(detachCount,2);
''')

    def test_expired_admitted_pair_is_not_completed_beyond_original_ttl(self):
        self.run_model('''
inFlight=1;active=[r];stop('host requested');Date.now=()=>201;
leave.call({record:r,counted:true,player:{}});
assert.equal(records.length,0);assert.equal(inFlight,0);assert.equal(active.length,0);
assert.equal(finishStop().stopped,true);
''')

    def test_faulted_admitted_pair_does_not_read_more_game_state(self):
        self.run_model('''
inFlight=1;active=[r];stop('host requested');faults=1;
snapshot=()=>{throw Error('must not read');};leave.call({record:r,counted:true,player:{}});
assert.equal(records.length,0);assert.equal(inFlight,0);assert.equal(active.length,0);
assert.equal(finishStop().stopped,true);assert.equal(faults,1);
''')

    def test_original_queue_bound_is_not_relaxed_and_detach_error_stays_sticky(self):
        self.run_model('''
inFlight=1;active=[r];records=Array.from({length:64},()=>({}));stop('host requested');
leave.call({record:r,counted:true,player:{}});assert.equal(records.length,64);assert.equal(dropped,1);
getterHook={detach(){throw Error('synthetic detach');}};assert.equal(finishStop().stopped,false);
assert.equal(detachErrors.length,1);assert.equal(faults,1);
getterHook={detach(){}};assert.equal(finishStop().stopped,true);assert.equal(faults,1);assert.equal(detachErrors.length,1);
''')

    def test_private_original_guard_header_and_getter_binding_body_unchanged(self):
        old=Path(ORIGINAL).read_text();new=patch(old)
        self.assertEqual(old.splitlines()[1],new.splitlines()[1])
        start="if(!enabled||tls)return;try{";end="}catch(e){fault(e);}}"
        self.assertEqual(old[old.index(start):old.index(end,old.index(start))+len(end)],
                         new[new.index(start):new.index(end,new.index(start))+len(end)])
        for bound in ["limit(c.max_records,1,64", "limit(c.max_calls,1,1024", "limit(c.ttl_ms,1,125000", "limit(c.binding_ms,1,2000", "limit(c.binding_calls,1,256"]:
            self.assertIn(bound,new)


if __name__=='__main__':unittest.main()
