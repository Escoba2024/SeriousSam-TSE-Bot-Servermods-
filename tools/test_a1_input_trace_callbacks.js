'use strict';
// Synthetic Frida API model only. No Frida import, process access or native call.
const assert=require('assert'),fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(__dirname+'/a1_original_input_readonly.js','utf8');
function fixture(options={}) {
  const memory=Buffer.alloc(0x800000),hooks=new Map(),immediates=[]; let clock=1000,timer=null;
  class Pointer {
    constructor(n) { this.n=Number(n); }
    add(n) { return new Pointer(this.n+Number(n)); }
    sub(n) { return new Pointer(this.n-Number(n)); }
    equals(p) { return this.n===p.n; }
    toUInt32() { return this.n>>>0; }
    toString() { return '0x'+this.n.toString(16); }
    readU32() { return memory.readUInt32LE(this.n); }
    readS32() { return memory.readInt32LE(this.n); }
    readFloat() { return memory.readFloatLE(this.n); }
    readPointer() { return new Pointer(this.readU32()); }
    readByteArray(n) { return Uint8Array.from(memory.subarray(this.n,this.n+n)).buffer; }
  }
  const ptr=n=>new Pointer(n),u=(a,v)=>memory.writeUInt32LE(v,a),f=(a,v)=>memory.writeFloatLE(v,a);
  const eb=0x100000,gb=0x400000,inp=0x50000,go=0x60000,ctl=go+0x2d4,pl=0x70000,wo=0x74000,so=0x75000,net=0x78000,session=0x79000;
  u(eb+0x1f178c,inp);u(gb+0x2fba4,go);u(go+0xfa0,0);u(go+0xfa4,so);u(ctl+0x15c,0);
  u(inp+4,1);u(go+0xf54,1);u(go+0xf58,0);u(eb+0x20d6a4,net);u(eb+0x20d6b8,0);u(net+0x20,session);u(net+0x854,0);u(session+0xa8,0);u(ctl,gb+0x2156c);u(gb+0x2158c,gb+0x10470);
  u(pl+0x1c,559);u(pl+4,3);u(pl+0x10,0);u(pl+0x8c,wo);f(pl+0xc14,.25);f(pl+0xcc,100);f(pl+0xcc4,-27);
  u(eb+0x1e7f48,0);f(eb+0x1e7f4c,.25);u(eb+0x1e7f5c,0);u(eb+0x20d760,0);u(eb+0x20d768,0);
  for(const [index,binding] of [[4,1],[3,2]]) {
    const a=ctl+0x10+index*36;u(a,binding);f(a+4,50);f(a+8,0);u(a+0xc,0);u(a+0x10,1);u(a+0x14,0);f(a+0x18,1);f(a+0x1c,0);f(a+0x20,0);
  }
  const context=vm.createContext({ptr,Process:{id:99,arch:'ia32',pointerSize:4},rpc:{exports:{}},
    Date:{now:()=>clock},setTimeout(fn){timer=fn;return 1;},clearTimeout(){timer=null;},setImmediate(fn){immediates.push(fn);},Interceptor:{flush(){},attach(at,callbacks){
      const n=at.n;hooks.set(n,callbacks);const saved=memory[n];memory[n]=0xe9;
      return {detach(){if(options.detachError)throw Error('synthetic detach error');memory[n]=saved;hooks.delete(n);}};
    }}});
  vm.runInContext(source,context);
  const c={pid:99,max_records:256,max_calls:1024,ttl_ms:20000,engine_base:ptr(eb).toString(),game_base:ptr(gb).toString(),input:ptr(inp).toString(),game:ptr(go).toString(),controls:ptr(ctl).toString(),source:ptr(so).toString(),player:ptr(pl).toString(),world:ptr(wo).toString(),player_id:559,spawn_clock:.25};
  const g={modules:{'Engine.dll':{preferred_base:eb},'GameMP.dll':{preferred_base:gb}},guards:[{module:'Engine.dll',rva:0xd200,hex:'0000000000000000',length:8,highlow_offsets:[]},{module:'GameMP.dll',rva:0x10470,hex:'0000000000000000',length:8,highlow_offsets:[]}]};
  g.sites={input:{rva:0xd200},cursor_return:{rva:0xd2b2},recenter_call:{rva:0xd56a},recenter_return:{rva:0xd570},action:{rva:0x10470},compose_call:{rva:0x104fe}};
  g.timer_gate={schema:'original107-timer-guard-observation-v2',game_on_offset:0xf54,game_menu_offset:0xf58,input_enabled_offset:4,network_pointer_rva:0x20d6a4,network_guard_rva:0x20d6b8,network_session_offset:0x20,session_pause_offset:0xa8,network_local_pause_offset:0x854,controls_vtable_rva:0x2156c,controls_action_slot_offset:0x20};
  g.callers={input_return_rva:0x11241,action_return_rva:0x112fb};
  const api=context.rpc.exports;
  function invoke(at,state,leave=false) { const h=hooks.get(at); if(h) (typeof h==='function'?h:(leave?h.onLeave:h.onEnter)).call(state); }
  function flushImmediates(){while(immediates.length)immediates.shift()();}
  function input(dx=12,{recenter=true,thread=99,cursor=true,stopDuring=false,callerGame=go,returnEDI=null,rawThis=inp,callerReturn=gb+0x11241,prescan=0,mutateAfterEntry=null}={}) {
    const sp=0x80000,bp=sp-4;u(sp,callerReturn);u(sp+4,prescan);u(bp-0x20,dx);u(bp-0x1c,0);
    const s={threadId:thread,context:{ecx:ptr(rawThis),edi:ptr(callerGame),esp:ptr(sp),ebp:ptr(bp),eax:ptr(cursor?1:0)}};
    const enter=hooks.get(eb+0xd200);if(!enter)return;enter.onEnter.call(s);
    if(mutateAfterEntry)mutateAfterEntry(s);
    if(stopDuring){api.stop();assert(hooks.size>0);assert.equal(api.drain().in_flight,1);}
    invoke(eb+0xd2b2,s);
    if(recenter) {u(0x81000,0);u(0x81004,0);s.context.esp=ptr(0x81000);invoke(eb+0xd56a,s);s.context.eax=ptr(options.recenterFail?0:1);}
    invoke(eb+0xd570,s);f(inp+0x24,dx*.25);f(inp+0x38,0);if(returnEDI!==null)s.context.edi=ptr(returnEDI);enter.onLeave.call(s);flushImmediates();
  }
  function action(delta=-3,thread=99) {
    const sp=0x82000,a=0x83000;u(sp,gb+0x112fb);u(sp+4,go+0x114);u(sp+8,a);u(sp+12,0);
    const s={threadId:thread,context:{ecx:ptr(ctl),esp:ptr(sp),edi:ptr(a)}};
    const h=hooks.get(gb+0x10470);if(!h)return;h.onEnter.call(s);
    f(a+0xc,delta);f(a+0x18,0);invoke(gb+0x104fe,s);
    f(pl+0xcc4,memory.readFloatLE(pl+0xcc4)+delta);f(a+0xc,memory.readFloatLE(pl+0xcc4));h.onLeave.call(s);flushImmediates();
  }
  return {api,c,g,input,action,hooks,u,f,ptr,eb,gb,inp,go,ctl,pl,net,session,setClock:x=>clock=x,
    flushImmediates,fireTTL(){clock=22000;const fn=timer;if(fn)fn();}};
}
let passed=0;
function test(name,run){run();passed++;}
test('instruction sites register true probes while real entries keep enter leave pairs',()=>{
  const t=fixture();t.api.arm(t.c,t.g);
  for(const at of [t.eb+0xd2b2,t.eb+0xd56a,t.eb+0xd570,t.gb+0x104fe]) {
    assert.equal(typeof t.hooks.get(at),'function','instruction point must not register a call listener');
  }
  for(const at of [t.eb+0xd200,t.gb+0x10470]) {
    const hook=t.hooks.get(at);assert.equal(typeof hook.onEnter,'function');assert.equal(typeof hook.onLeave,'function');
  }
  assert.equal(t.hooks.size,6);t.api.stop();
});
test('not armed at load',()=>{const t=fixture();assert.equal(t.hooks.size,0);});
test('observer covers existing90s controller budget with fixed caps',()=>{
  const t=fixture();t.c.max_calls=4096;t.c.ttl_ms=90000;t.api.arm(t.c,t.g);t.api.stop();
  for(const [key,value]of [['max_calls',4097],['ttl_ms',90001],['max_records',257]]){
    const bad=fixture();bad.c[key]=value;assert.throws(()=>bad.api.arm(bad.c,bad.g));assert.equal(bad.hooks.size,0);
  }
});
test('old metadata fails before installing any listener',()=>{const t=fixture();delete t.g.timer_gate;assert.throws(()=>t.api.arm(t.c,t.g),/timer guard metadata/);assert.equal(t.hooks.size,0);});
test('records timer guards without changing readiness or calling game',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.input(0,{recenter:false});
  const p=t.api.drain();assert.equal(p.ready,false);const r=p.records[0];
  for(const gate of [r.timer_guard_entry,r.timer_guard_return]) {
    assert.equal(gate.observed_game,'0x60000');assert.equal(gate.game_binding,'ARM_GLOBAL_LIFETIME_VERIFIED');assert.equal(gate.caller_game_binding_proven,false);assert.equal(gate.game_on,1);assert.equal(gate.input_enabled,1);
    assert.equal(gate.menu_on,0);assert.equal(gate.network,'0x78000');assert.equal(gate.network_global_guard,0);
    assert.equal(gate.session_pause_word,0);assert.equal(gate.local_pause_word,0);
    assert.equal(gate.controls_vtable,'0x42156c');assert.equal(gate.virtual_action_target,'0x410470');
    assert.equal(gate.derived_create_action_gate_open,true);assert.equal(gate.actual_branch_proven,false);
  }
  t.action(0);assert.equal(t.api.drain().ready,true);t.api.stop();
});
test('entry and return snapshots retain an intervening guard change',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.input(0,{recenter:false,mutateAfterEntry:()=>t.u(t.net+0x854,1)});
  const row=t.api.drain().records[0];assert.equal(row.timer_guard_entry.local_pause_word,0);assert.equal(row.timer_guard_return.local_pause_word,1);t.api.stop();
});
test('raw EDI is separate per callback and never dereferenced as Game',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.input(0,{recenter:false,callerGame:0,returnEDI:0x61003});
  const p=t.api.drain();assert.equal(p.ready,false);assert.equal(p.faults,0);assert.equal(p.enabled,true);
  const r=p.records[0];assert.equal(r.timer_guard_entry.callback_phase,'entry');assert.equal(r.timer_guard_return.callback_phase,'return');
  assert.equal(r.timer_guard_entry.raw_edi,'0x0');assert.equal(r.timer_guard_return.raw_edi,'0x61003');
  for(const g of [r.timer_guard_entry,r.timer_guard_return]) {
    assert.equal(g.observed_game,'0x60000');assert.equal(g.raw_edi_matches_bound_game,false);assert.equal(g.game_on,1);
    assert.equal(g.caller_game_binding_proven,false);assert.equal(g.actual_branch_proven,false);
  }
  t.action(0);assert.equal(t.api.drain().ready,true);t.api.stop();
});
test('raw EDI observation cannot replace changed Arm Game global lifetime',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.u(t.gb+0x2fba4,0x61000);t.input(0,{recenter:false,callerGame:0});
  const p=t.api.drain();assert(p.faults>0);assert.equal(p.ready,false);assert.equal(p.enabled,false);t.api.stop();
});
test('diagnostic EDI cannot relax actual this caller or prescan guards',()=>{
  for(const options of [{rawThis:0x61000},{callerReturn:0x411250},{prescan:1}]) {
    const t=fixture();t.api.arm(t.c,t.g);t.input(0,{recenter:false,callerGame:0,...options});
    const p=t.api.drain();assert(p.faults>0);assert.equal(p.enabled,false);assert.equal(p.ready,false);t.api.stop();
  }
});
test('each observed post-input pause/game guard is visible without readiness',()=>{
  for(const which of ['game','global','session','local']) {
    const t=fixture();t.api.arm(t.c,t.g);
    t.u(which==='game'?t.go+0xf54:which==='global'?t.eb+0x20d6b8:which==='session'?t.session+0xa8:t.net+0x854,which==='game'?0:1);
    t.input(0,{recenter:false});const p=t.api.drain();assert.equal(p.ready,false);assert.equal(p.faults,0);
    assert.equal(p.records[0].timer_guard_return.derived_create_action_gate_open,false);t.api.stop();
  }
});
test('null network retains getter fallback without unsafe dereference',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.u(t.eb+0x20d6a4,0);t.input(0,{recenter:false});
  const p=t.api.drain(),g=p.records[0].timer_guard_return;assert.equal(p.faults,0);
  assert.equal(g.network,'0x0');assert.equal(g.session_pause_word,null);assert.equal(g.local_pause_word,null);
  assert.equal(g.derived_is_paused,1);assert.equal(g.derived_local_pause,1);assert.equal(g.derived_create_action_gate_open,false);t.api.stop();
});
test('virtual target drift is an observation, not evidence that body executed',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.u(t.gb+0x2158c,t.gb+0x10510);t.input(0,{recenter:false});
  const p=t.api.drain();assert.equal(p.ready,false);assert.equal(p.records[0].timer_guard_return.virtual_action_target,'0x410510');
  assert.equal(p.records[0].timer_guard_return.expected_action_target_matches,false);t.api.stop();
});
test('ordinary and reused input keep exact IDs',()=>{
  const t=fixture();t.api.arm(t.c,t.g);t.input();t.action();t.action();
  const p=t.api.drain();assert.equal(p.faults,0);assert.equal(p.records.length,3);
  assert.equal(p.records[0].cursor.raw_dx,12);assert.equal(p.records[0].engine_x,3);
  assert.equal(p.records[1].input_id,p.records[0].id);assert.equal(p.records[2].input_id,p.records[0].id);
  assert.equal(p.records[1].entity_local_accumulator_before,-27);assert.equal(p.records[2].entity_local_accumulator_after,-33);
  assert.equal(p.records[1].raw_action_yaw,-3);assert.equal(p.records[1].action_yaw,-30);
  assert.equal(p.ready,true);
  t.api.stop();const end=t.api.drain();assert.equal(end.restored,true);assert.equal(end.in_flight,0);
});
test('distinct cursor invocations stay distinct',()=>{const t=fixture();t.api.arm(t.c,t.g);t.input();t.action();t.input();t.action();const p=t.api.drain();assert.notEqual(p.records[0].id,p.records[2].id);assert.equal(p.records[3].input_id,p.records[2].id);t.api.stop();});
test('zero motion needs no recenter call',()=>{const t=fixture();t.api.arm(t.c,t.g);t.input(0,{recenter:false});assert.equal(t.api.drain().faults,0);t.api.stop();});
test('TTL detaches even without any native call or drain',()=>{const t=fixture();t.api.arm(t.c,t.g);t.fireTTL();assert.equal(t.hooks.size,0);assert.equal(t.api.drain().stop_reason,'TTL/clock');});
test('observed timer TID may differ from PID',()=>{const t=fixture();t.api.arm(t.c,t.g);t.input(12,{thread:77});t.action(-3,77);const p=t.api.drain();assert.equal(p.faults,0);assert.equal(p.input_thread,77);assert.equal(p.records[1].thread,77);t.api.stop();});
test('ARM between input/action waits for next complete pair',()=>{const t=fixture();t.api.arm(t.c,t.g);t.action(0);const p=t.api.drain();assert.equal(p.faults,0);assert.equal(p.ready,false);assert.equal(p.warmup_skipped,1);t.input();t.action();assert.equal(t.api.drain().ready,true);t.api.stop();});
test('stop retains admitted pair until leave and then restores',()=>{const t=fixture();t.api.arm(t.c,t.g);t.input(12,{stopDuring:true});const p=t.api.drain();assert.equal(p.in_flight,0);assert.equal(p.restored,true);assert.equal(p.records.length,1);assert.equal(p.faults,0);});
for(const mode of ['cursor','recenter','thread','profile','flags','world','life','queue','ttl','nested','guard']) {
  test(mode+' fails closed',()=>{
    const t=fixture({recenterFail:mode==='recenter'});
    if(mode==='guard'){t.g.guards[0].hex='1100000000000000';assert.throws(()=>t.api.arm(t.c,t.g));assert.equal(t.hooks.size,0);return;}
    if(mode==='queue')t.c.max_records=1;t.api.arm(t.c,t.g);
    if(mode==='profile')t.u(t.go+0xfa0,1);
    if(mode==='flags')t.u(t.ctl+0x15c,1);
    if(mode==='world')t.u(t.pl+0x8c,0x76000);
    if(mode==='life')t.f(t.pl+0xc14,2);
    if(mode==='ttl')t.setClock(22000);
    if(mode==='thread')t.input();
    let pending=null;
    if(mode==='nested'){
      const h=t.hooks.get(t.eb+0xd200),sp=0x80000;t.u(sp,t.gb+0x11241);t.u(sp+4,0);
      const s={threadId:99,context:{ecx:t.ptr(t.inp),edi:t.ptr(t.go),esp:t.ptr(0x80000)}};
      h.onEnter.call(s);h.onEnter.call({threadId:99,context:s.context});
      pending=()=>h.onLeave.call(s);
    } else {t.input(12,{cursor:mode!=='cursor',thread:mode==='thread'?77:99});if(mode==='queue')t.action();}
    const p=t.api.drain();assert.equal(p.enabled,false);assert(p.faults>0||p.dropped>0||p.stop_reason==='TTL/clock');
    t.api.stop();if(pending){assert(t.hooks.size>0);pending();t.flushImmediates();}assert.equal(t.hooks.size,0);
  });
}
test('detach fault retained',()=>{const t=fixture({detachError:true});t.api.arm(t.c,t.g);t.api.stop();const p=t.api.drain();assert(p.faults>0);assert(p.detach_errors.length>0);assert.equal(p.restored,false);});
console.log(JSON.stringify({synthetic_callbacks_passed:passed,native_execution:false}));
