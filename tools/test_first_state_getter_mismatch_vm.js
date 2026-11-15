'use strict';
const assert=require('assert'),{fixture,G}=require(process.argv[2]),which=process.argv[3];
function prepare(options={}){const x=fixture(options);x.arm();return x;}
function address(x){return x.bases['Engine.dll']+G.modules['Engine.dll'].guards.current_tick.rva;}
function expected(x){return x.guardBytes('Engine.dll',G.modules['Engine.dll'].guards.current_tick).toString('hex');}
function invoke(x){return typeof x.sandbox.requireGetterOriginal==='function'?x.sandbox.requireGetterOriginal():x.sandbox.lifetime();}
function detail(x,actual,raw){assert(raw&&typeof raw==='object','old getter mismatch has no actual raw detail');assert.equal(raw.actual_hex,actual);assert.equal(raw.expected_rebased_hex,expected(x));assert.equal(raw.rva,G.modules['Engine.dll'].guards.current_tick.rva);assert.equal(raw.length,22);assert.equal(raw.getter_registered,false);assert.equal(raw.getter_callbacks,0);assert.equal(raw.tls_bound,true);assert.equal(raw.tls_binding.pointer,'0x900000');}
function captured(x){let error;try{invoke(x);}catch(e){error=e;}assert(error,'mutation must still fail');assert(String(error).includes('bound getter changed'));return error;}
if(which==='fault'){
 const x=prepare(),region=x.regions.get(address(x));region[8]^=1;const actual=region.toString('hex');
 const f=x.enter('post_moving',0x300000);x.leave(f);const p=x.api.drain();
 assert(p.counters.faults>0);assert.equal(p.events.length,0);assert(p.errors[0].raw.detail,'first actual fail-path detail absent');detail(x,actual,p.errors[0].raw.detail);
}else if(which==='allbytes'){
 for(const engine_base of ['0x600c0000','0x610c0000'])for(let offset=0;offset<22;offset++){
  const x=prepare({engine_base}),region=x.regions.get(address(x));region[offset]^=1;
  const before=x.getterReads,error=captured(x);assert.equal(x.getterReads-before,1);detail(x,region.toString('hex'),error.raw);
 }
}else if(which==='pass'){
 const x=prepare(),before=x.getterReads;invoke(x);assert.equal(x.getterReads-before,1);
 const p=x.api.drain();assert.equal(p.counters.faults,0);assert.equal(p.counters.getter_calls,1);assert.equal(x.callbacks.size,18);assert.equal(x.nativeWrites.length,0);
 assert.equal(p.runtime_reviewed,false);assert.equal(p.native_qualified,false);assert.equal(p.first_processed_state_proven,false);assert.equal(p.bounds.max_records,64);
 const y=fixture({testReviewed:false});assert.throws(()=>y.api.arm(y.cfg),/runtime review gate false/);assert.equal(y.reads,0);
}else if(which==='sameread'){
 const x=prepare(),region=x.regions.get(address(x));region[17]^=1;const actual=region.toString('hex');
 x.afterGetterRead=()=>{region[17]^=1;};const before=x.getterReads,error=captured(x);
 assert.equal(x.getterReads-before,1);assert.equal(region.toString('hex'),expected(x));detail(x,actual,error.raw);assert.equal(x.lastGetterRead,actual);
}else if(which==='otherpaths'){
 for(const mode of ['stopped','nonmain']){
  const x=prepare(),region=x.regions.get(address(x));region[0]^=1;const actual=region.toString('hex');
  if(mode==='stopped')x.api.stop();else{const f=x.enter('post_moving',0x300000,[],0x12345678,445);x.leave(f);}
  const p=x.api.drain();assert(p.counters.faults>0);assert.equal(p.events.length,0);detail(x,actual,p.errors[0].raw.detail);
 }
}else if(which==='pending'){
 const x=fixture();let seen=false;
 x.onPending=()=>{seen=true;const before=x.getterReads,error=captured(x);assert.equal(x.getterReads-before,1);assert.equal(error.raw.getter_registered,true);assert.equal(error.raw.getter_callbacks,1);assert.equal(error.raw.tls_bound,true);assert.equal(error.raw.actual_hex,x.lastGetterRead);};
 x.arm();assert(seen);assert.equal(x.pending,0);const p=x.api.drain();assert.equal(p.counters.faults,0);
}else throw Error(which);
console.log('PASS '+which);
