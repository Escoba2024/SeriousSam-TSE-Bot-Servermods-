'use strict';
const assert=require('assert'),{fixture}=require(process.argv[2]),which=process.argv[3];
const x=fixture({testReviewed:false});
assert.equal(typeof x.api.runtimeidentity,'function','actual compiled Observer lacks cold Runtimeidentity RPC');
const before={reads:x.reads,attaches:x.attaches};
if(which==='qjs')x.sandbox.Script.runtime='QJS';
const actual=x.api.runtimeidentity();
assert.deepStrictEqual(JSON.parse(JSON.stringify(actual)),{runtime:which==='qjs'?'QJS':'V8',pid:444,arch:'ia32',pointer_size:4});
assert.equal(x.reads,before.reads);assert.equal(x.attaches,before.attaches);assert.equal(x.nativeWrites.length,0);
if(which==='gate'){assert.throws(()=>x.api.arm(x.cfg),/gate false/);assert.equal(x.attaches,0);assert.equal(x.reads,0);}
console.log('PASS '+which);
