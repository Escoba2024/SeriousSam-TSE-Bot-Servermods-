'use strict';
const assert=require('assert'),{fixture,G}=require(process.argv[2]),which=process.argv[3];
const x=fixture(),engine=x.bases['Engine.dll'],g=G.modules['Engine.dll'].guards.current_tick;
function mutate(){x.regions.get(engine+g.rva)[0]^=1;}
function close(){x.holdCommit=false;x.commit();x.api.stop();assert(x.api.status().idle);assert(x.api.finishstop().stopped);const p=x.api.drain();assert.equal(p.in_flight,0);assert.equal(x.nativeWrites.length,0);return p;}
function noFault(p){assert.equal(p.counters.faults,0,JSON.stringify(p.errors));assert.equal(p.counters.dropped,0);assert.equal(p.counters.aborted_leaves,0);}
if(which==='legacyfault'){
 x.arm();const p=x.api.drain();assert.equal(p.counters.faults,1);assert.equal(p.counters.getter_calls,1);assert(JSON.stringify(p.errors).includes('getter restore mismatch after binding'));assert.equal(x.pendingReads,1);assert.equal(p.restored['Engine.dll:current_tick'],true);close();
}else if(which==='commit'){
 x.arm();noFault(x.api.drain());assert.equal(x.pendingReads,0);assert.equal(x.pending,0);assert.equal(x.callbacks.size,18);
 const t=x.startTick();x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);const p=close();noFault(p);assert(Object.values(p.restored).every(Boolean));assert(p.events.find(e=>e.kind==='receive_damage'&&e.edge==='leave'&&e.data.payload.chain_bound));
}else if(which==='drainonly'){
 x.arm();const p=x.api.drain();noFault(p);assert.equal(p.events.length,0);assert.equal(p.restored['Engine.dll:current_tick'],true);close();
}else if(which==='main'||which==='nonmain'){
 x.arm();mutate();const frame=x.enter('post_moving',0x300000,[],0x12345678,which==='main'?444:445);x.leave(frame);let p=x.api.drain();assert(p.counters.faults>0);assert.equal(p.events.length,0);assert(JSON.stringify(p.errors).includes('bound getter changed'));mutate();p=close();assert(p.counters.faults>0);
}else if(which==='stoppeddrift'){
 x.arm();x.api.stop();mutate();let p=x.api.drain();assert(p.counters.faults>0);assert.equal(p.events.length,0);assert.equal(p.restored['Engine.dll:current_tick'],false);mutate();p=close();assert(p.counters.faults>0);
}else if(which==='nonmainleave'){
 x.arm();const frame=x.enter('post_moving',0x300000,[],0x12345678,445);mutate();x.leave(frame);let p=x.api.drain();assert(p.counters.faults>0);assert.equal(p.events.filter(e=>e.edge==='enter').length,1);assert.equal(p.events.filter(e=>e.edge==='leave').length,0);assert.equal(p.in_flight,0);mutate();p=close();assert(p.counters.faults>0);
}else if(which==='nocommit'){
 x.holdCommit=true;x.onPending=()=>{x.onPending=null;x.api.stop();assert.equal(x.api.status().idle,false);assert.equal(x.api.finishstop().stopped,false);};x.arm();assert.equal(x.pending,1);
 let p=x.api.drain();assert(p.counters.faults>0);assert.equal(p.restored['Engine.dll:current_tick'],false);assert.equal(p.events.length,0);p=close();assert(p.counters.faults>0);
}else if(which==='stopinside'){
 let seen=false;x.onPending=()=>{x.onPending=null;seen=true;assert(x.depth>0);x.api.stop();assert.equal(x.api.status().getter_callbacks,1);assert.equal(x.api.finishstop().stopped,false);};x.arm();assert(seen);assert.equal(x.pending,0);const p=close();noFault(p);assert.equal(p.restored['Engine.dll:current_tick'],true);
}else if(which==='leave'||which==='ttl'||which==='identity'){
 x.arm();const t=x.startTick();x.api.stop();if(which==='leave')mutate();else if(which==='ttl')x.clock=6000;else x.u(0x12001c,8);
 x.leave(t);let p=x.api.drain();assert(p.counters.faults>0||p.counters.aborted_leaves>0);assert.equal(p.events.filter(e=>e.edge==='leave').length,0);assert.equal(p.in_flight,0);
 if(which==='leave')mutate();else if(which==='identity')x.u(0x12001c,7);p=close();assert(p.counters.faults>0||p.counters.aborted_leaves>0);
}else if(which==='header'||which==='body'||which==='iat'){
 let reason;if(which==='header'){x.regions.get(engine)[0]=0;reason=/module DOS header/;}else if(which==='body'){mutate();reason=/Original full-body\/HIGHLOW guard mismatch/;}else{const imp=G.verified_imports[0];x.u(x.bases[imp.module]+imp.iat_rva,0);reason=/original import target changed/;}
 assert.throws(()=>x.api.arm(x.cfg),reason);assert.equal(x.attaches,0);
}else if(which==='disabled'){
 const y=fixture({testReviewed:false});assert.throws(()=>y.api.arm(y.cfg),/gate false/);assert.equal(y.attaches,0);assert.equal(y.reads,0);
}else throw Error(which);
console.log('PASS '+which);
