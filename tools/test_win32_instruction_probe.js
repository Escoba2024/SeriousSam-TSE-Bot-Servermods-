'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const file=__dirname+'/win32_instruction_probe.js';
assert(fs.existsSync(file),'missing passive own-method observer');
const source=fs.readFileSync(file,'utf8');
function fixture(){
 const memory=new Map(),hooks=[];let clock=1000,onRead=null;
 const header=Buffer.alloc(256);header.write('MZ');header.writeUInt32LE(0x80,0x3c);
 header.write('PE\0\0',0x80);header.writeUInt16LE(0x14c,0x84);header.writeUInt16LE(0x10b,0x98);memory.set(0x400000,header);
 for(const rva of [0x1000,0x2000])memory.set(0x400000+rva,Buffer.alloc(17,0x90));
 class Pointer{
  constructor(n){this.n=n;}add(n){return new Pointer(this.n+n);}toString(){return '0x'+this.n.toString(16);}
  readByteArray(n){for(const [at,bytes]of memory)if(this.n>=at&&this.n+n<=at+bytes.length)return Uint8Array.from(bytes.subarray(this.n-at,this.n-at+n)).buffer;throw Error('unmapped synthetic read');}
  readU16(){return Buffer.from(this.readByteArray(2)).readUInt16LE(0);}
  readU32(){if(this.n<0x800000)return Buffer.from(this.readByteArray(4)).readUInt32LE(0);if(onRead){const fn=onRead;onRead=null;fn();}return 0x12345678;}
 }
 const ctx=vm.createContext({ptr:n=>new Pointer(Number(n)),rpc:{},Date:{now:()=>clock},setTimeout(){return 1;},clearTimeout(){},
 Process:{id:99,arch:'ia32',pointerSize:4,mainModule:{name:'wine-preloader',base:new Pointer(0x700000)}},
 Interceptor:{flush(){},attach(at,callback){const buf=memory.get(at.n),old=buf[0];buf[0]=0xe9;
 const h={callback,detached:false,detach(){buf[0]=old;this.detached=true;}};hooks.push(h);return h;}}});
 vm.runInContext(source,ctx);const raw=ctx.rpc.exports;
 const api={status:raw.status,stop:raw.stop,arm:(mode,sites)=>raw.arm(mode,sites,{pid:99,image_base:'0x400000'})};
 const sites=[{name:'saved',rva:0x1000,hex:'90'.repeat(17)},{name:'arguments',rva:0x2000,hex:'90'.repeat(17)}];
 function hit(i){const h=hooks[i],state={threadId:44,context:{esp:new Pointer(0x800000),edi:new Pointer(0x12345678)}};
  (typeof h.callback==='function'?h.callback:h.callback.onEnter).call(state);}
 return {api,sites,hooks,hit,setClock:n=>clock=n,duringRead:fn=>onRead=fn};
}
let passed=0;function test(name,run){run();passed++;}
test('two exact function probes register without return callbacks',()=>{const t=fixture();t.api.arm('function-probe',t.sites);assert.equal(t.hooks.length,2);assert(t.hooks.every(h=>typeof h.callback==='function'));t.api.stop();});
test('historical control deliberately registers two call listener objects',()=>{const t=fixture();t.api.arm('historical-object',t.sites);assert(t.hooks.every(h=>typeof h.callback==='object'&&typeof h.callback.onEnter==='function'));t.api.stop();});
test('no baseline or unrecognized mode may attach',()=>{for(const mode of ['baseline','all','fire']){const t=fixture();assert.throws(()=>t.api.arm(mode,t.sites));assert.equal(t.hooks.length,0);}});
test('actual two site callbacks remain bounded and detach restores own bytes',()=>{const t=fixture();t.api.arm('function-probe',t.sites);t.hit(0);t.hit(1);const p=t.api.stop();assert.equal(p.records.length,2);assert.equal(p.faults,0);assert.equal(p.dropped,0);assert.equal(p.idle,true);assert.equal(p.detached,true);assert.equal(p.restored,true);});
test('duplicate callbacks stay failed rather than supplying extra evidence',()=>{const t=fixture();t.api.arm('function-probe',t.sites);t.hit(0);t.hit(0);assert(t.api.status().faults>0);assert(t.api.status().records.length<=2);t.api.stop();});
test('stop cannot detach while a callback is executing',()=>{const t=fixture();t.api.arm('function-probe',t.sites);t.duringRead(()=>{assert.equal(t.api.stop().idle,false);assert(t.hooks.every(h=>!h.detached));});t.hit(0);assert.equal(t.api.stop().idle,true);assert(t.hooks.every(h=>h.detached));});
test('expired admission cannot read stack or yield callback evidence',()=>{const t=fixture();t.api.arm('function-probe',t.sites);t.setClock(12000);let read=false;t.duringRead(()=>read=true);t.hit(0);assert.equal(read,false);assert.equal(t.api.status().records.length,0);assert(t.api.status().faults>0);t.api.stop();});
console.log(JSON.stringify({own_method_js_checks:passed,native_execution:false}));
