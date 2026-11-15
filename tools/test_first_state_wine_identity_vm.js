'use strict';
const assert=require('assert'),{fixture,G}=require(process.argv[2]);
const which=process.argv[3],x=fixture();
const name=process.argv[4]||'Engine.dll',base=x.bases[name],nt=name==='Engine.dll'?264:248,b=x.regions.get(base);
function finish(){x.api.stop();assert(x.api.status().idle);assert(x.api.finishstop().stopped);const p=x.api.drain();assert(p.detached);assert(Object.values(p.restored).every(Boolean));assert.equal(x.nativeWrites.length,0);return p;}
if(which==='wine'){
 x.arm();const t=x.startTick();x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);
 const p=finish();assert.equal(p.counters.faults,0);const r=p.events.find(e=>e.kind==='receive_damage'&&e.edge==='leave');assert.equal(r.player.health,80);assert(r.data.payload.chain_bound);
}else if(which==='lifetime'){
 x.arm();b[0]=0;x.call('post_moving',0x300000);const p=finish();assert(p.counters.faults>0);assert(JSON.stringify(p.errors).includes('module DOS header'));
}else if(which==='disabled'){
 const y=fixture({testReviewed:false});assert.throws(()=>y.api.arm(y.cfg),/gate false/);assert.equal(y.attaches,0);
}else{
 let reason;
 if(which==='base'){x.cfg.engine_base='0x600c1000';reason=/unmapped read/;}
 else if(which==='unaligned'){x.cfg.engine_base='0x600c0001';reason=/pointer bounds/;}
 else if(which==='overflow'){x.cfg.engine_base='0xfffff000';reason=/pointer bounds/;}
 else if(which==='mz'){b[0]=0;reason=/module DOS header/;}
 else if(which==='pe'){b[nt]=0;reason=/module PE signature/;}
 else if(which==='machine'){b.writeUInt16LE(0x8664,nt+4);reason=/module machine/;}
 else if(which==='optional_size'){b.writeUInt16LE(240,nt+20);reason=/module optional size/;}
 else if(which==='optional_magic'){b.writeUInt16LE(0x20b,nt+24);reason=/module optional magic/;}
 else if(which==='image_size'){b.writeUInt32LE(G.modules[name].image_size+4096,nt+80);reason=/module image size/;}
 else if(which==='nt_exact'){b.writeUInt32LE(256,0x3c);reason=/module NT offset/;}
 else if(which==='nt_bounds'){b.writeUInt32LE(0xfffffff0,0x3c);reason=/module NT offset/;}
 else if(which==='missing'){x.regions.delete(base);reason=/unmapped read/;}
 else if(which==='body'){const g=G.modules[name].guards.current_tick;x.regions.get(base+g.rva)[0]^=1;reason=/Original full-body\/HIGHLOW guard mismatch/;}
 else if(which==='iat'){const imp=G.verified_imports[0];x.u(x.bases[imp.module]+imp.iat_rva,0);reason=/original import target changed/;}
 else throw Error(which);
 assert.throws(()=>x.api.arm(x.cfg),reason);assert.equal(x.attaches,0);assert.equal(x.nativeWrites.length,0);
}
console.log('PASS '+which);
