'use strict';
const assert=require('assert'),{fixture,G}=require(process.argv[2]);
const which=process.argv[3];
function finish(x){x.api.stop();assert.equal(x.api.status().idle,true);assert.equal(x.api.finishstop().stopped,true);return x.api.drain();}
if(which==='getter'){
 const x=fixture();x.api.arm(x.cfg);
 const cb=x.callbacks.get(x.bases['Engine.dll']+G.modules['Engine.dll'].guards.current_tick.rva+15);
 assert.equal(typeof cb,'function');x.bind();assert.equal(x.api.drain().tls_binding.pointer,'0x900000');finish(x);
}else if(which==='active'){
 const x=fixture();x.arm();const t=x.startTick();const i=x.enter('initialize_player',0x300000);
 const prior=x.detaches;x.api.stop();assert.equal(x.detaches,prior);assert.equal(x.api.status().idle,false);
 assert.equal(x.api.finishstop().stopped,false);assert.equal(x.detaches,prior);
 const calls=x.api.drain().counters.order_calls;const ignored=x.enter('post_moving',0x300000);x.leave(ignored);
 assert.equal(x.api.drain().counters.order_calls,calls);
 x.leave(i);x.leave(t);const p=finish(x);
 assert.equal(p.in_flight,0);assert.equal(p.counters.aborted_leaves,0);assert.equal(p.counters.faults,0);
 assert(p.events.find(e=>e.edge==='leave'&&e.kind==='initialize_player'));
 assert.equal(p.detached,true);assert(Object.values(p.restored).every(Boolean));
}else if(which==='callback'){
 const x=fixture();x.arm();let seen=false;
 // The existing lifetime module lookup invokes stop inside actual onEnter.
 Object.defineProperty(x.moduleOverrides,'Engine.dll',{get(){
  if(!seen){seen=true;x.api.stop();assert.equal(x.api.status().callbacks,1);assert.equal(x.api.finishstop().stopped,false);}
  return {base:x.P(x.bases['Engine.dll']),size:G.modules['Engine.dll'].image_size};
 }});
 x.call('post_moving',0x300000);assert(seen);assert.equal(x.api.status().callbacks,0);
 const p=finish(x);assert.equal(p.counters.dropped,1);assert.equal(p.counters.aborted_leaves,1);assert.equal(p.counters.faults,0);
 assert.equal(p.terminal_record.edge,'enter');assert.equal(p.terminal_record.kind,'post_moving');assert.equal(p.counters.completed_calls,p.counters.order_calls);
 // This partial admission is terminal evidence, never a qualified trace.
}else if(which==='ttl'||which==='fault'){
 const x=fixture({ttl_ms:20});x.arm();const f=x.enter('initialize_player',0x300000);x.api.stop();
 if(which==='ttl')x.clock=1020;else x.u(0x12001c,8);
 x.leave(f);let p=x.api.drain();assert(p.counters.aborted_leaves>0||p.counters.faults>0);assert.equal(p.events.filter(e=>e.edge==='leave').length,0);
 assert.equal(x.api.status().idle,true);x.api.finishstop();p=x.api.drain();assert.equal(p.detached,true);
 assert(p.counters.aborted_leaves>0||p.counters.faults>0);
}else if(which==='detach'){
 const x=fixture();x.arm();x.failDetach.add(x.location('apply_action'));x.api.stop();
 assert.equal(x.api.finishstop().stopped,false);assert.equal(x.api.drain().counters.detach_failures,1);
 x.failDetach.clear();assert.equal(x.api.finishstop().stopped,true);assert.equal(x.api.drain().counters.detach_failures,1);
}else if(which==='schema'){
 const x=fixture();x.arm();const p=x.api.drain();
 assert.equal(Object.keys(p).sort().join(','),'active_calls,armed_ms,bounds,counters,detached,enabled,errors,expires_ms,first_processed_state_proven,identity,in_flight,native_qualified,restored,runtime_reviewed,schema,stop_reason,terminal_record,tls_binding,events'.split(',').sort().join(','));
 assert.equal(p.schema,'a1.first-state.observer.v2');assert.equal(p.bounds.max_order_calls,8192);assert.equal(p.bounds.max_events,16384);finish(x);
}else if(which==='chain'){
 const x=fixture();x.arm();const t=x.startTick();x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);
 const p=x.api.drain();assert.equal(p.counters.faults,0,JSON.stringify(p.errors));
 const r=p.events.find(e=>e.kind==='receive_damage'&&e.edge==='leave');assert.equal(r.player.health,80);assert.equal(r.player.valid_anchor.tick.call_id,t.ctx.frame.id);assert.equal(r.data.payload.chain_bound,true);assert.equal(r.data.payload.inflictor.id,566);finish(x);
}else if(which==='chainstop'){
 const x=fixture();x.arm();const t=x.startTick();x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();
 x.shot({duringReceive(){const old=x.detaches;x.api.stop();assert.equal(x.api.status().idle,false);assert.equal(x.api.finishstop().stopped,false);assert.equal(x.detaches,old);}});x.leave(t);
 const p=finish(x);const r=p.events.find(e=>e.kind==='receive_damage'&&e.edge==='leave');
 assert.equal(r.player.health,80);assert.equal(r.data.payload.chain_bound,true);assert.equal(p.counters.faults,0);assert.equal(p.counters.dropped,0);assert.equal(p.counters.aborted_leaves,0);assert.equal(p.in_flight,0);
}else if(which==='disabled'){
 const x=fixture({testReviewed:false});assert.throws(()=>x.api.arm(x.cfg),/gate false/);assert.equal(x.attaches,0);
}else throw Error(which);
console.log('PASS '+which);
