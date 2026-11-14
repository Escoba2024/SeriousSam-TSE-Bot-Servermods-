'use strict';
// Own disposable PE only. No native calls, context assignments or memory writes.
let used=false,enabled=false,expires=0,inCallbacks=0,faults=0,dropped=0;
let handles=[],sites=[],records=[],seen=new Set(),timer=null;
let imageBase=null;
function need(v,msg){if(!v)throw Error(msg);}
function exact(site){
 const bytes=new Uint8Array(imageBase.add(site.rva).readByteArray(site.hex.length/2));
 return Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('')===site.hex;
}
function status(){return {records:records.slice(),faults,dropped,idle:inCallbacks===0,
 enabled,detached:handles.length===0,restored:handles.length===0&&sites.every(exact)};}
function observe(site){
 return function(){
  if(!enabled)return;
  if(Date.now()>=expires){enabled=false;faults++;return;}
  inCallbacks++;
  try{
   need(records.length<2&&!seen.has(site.name),'duplicate/extra own native callback');
   seen.add(site.name);
   const top=this.context.esp.readU32();
   records.push({site:site.name,thread:this.threadId,stack_top:top,
                 raw_edi:this.context.edi.toString()});
  }catch(e){faults++;enabled=false;}
  finally{inCallbacks--;}
 };
}
rpc.exports={
 arm(mode,definitions,binding){
  need(!used,'single own observer arm');
  need(mode==='function-probe'||mode==='historical-object','two fixed instrumented modes');
  need(Process.arch==='ia32'&&Process.pointerSize===4,'own IA32 only');
  need(binding&&binding.pid===Process.id&&binding.image_base==='0x400000','host-bound own PE identity');
  imageBase=ptr(binding.image_base);
  need(imageBase.readU16()===0x5a4d,'own live MZ header');
  const peOffset=imageBase.add(0x3c).readU32();need(peOffset>=0x40&&peOffset<=0x1000,'own PE header range');
  need(imageBase.add(peOffset).readU32()===0x4550&&imageBase.add(peOffset+4).readU16()===0x14c&&
       imageBase.add(peOffset+24).readU16()===0x10b,'own live IA32 PE header');
  need(Array.isArray(definitions)&&definitions.length===2,'two own midpoint definitions');
  need(new Set(definitions.map(s=>s.name)).size===2&&definitions.every(s=>s.name==='saved'||s.name==='arguments'),'own midpoint names');
  sites=JSON.parse(JSON.stringify(definitions));need(sites.every(exact),'own Original code differs');
  used=true;enabled=true;expires=Date.now()+10000;
  for(const site of sites){
   const callback=observe(site);
   // Deliberate negative control: never use object form for a real instruction.
   handles.push(Interceptor.attach(imageBase.add(site.rva),
     mode==='function-probe'?callback:{onEnter:callback}));
  }
  Interceptor.flush();
  timer=setTimeout(()=>{enabled=false;faults++;},10000);
  return {armed:true,sites:handles.length,expires,mode};
 },
 status,
 stop(){
  enabled=false;
  if(inCallbacks!==0)return status();
  if(timer!==null){clearTimeout(timer);timer=null;}
  for(const handle of handles)handle.detach();
  handles=[];Interceptor.flush();
  return status();
 }
};
