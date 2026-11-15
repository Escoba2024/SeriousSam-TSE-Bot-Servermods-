"""Exact fault-only getter receipt transform. No Original bytes are authored."""
import hashlib

BODY_SHA='206a232ea1cdb847657f2ba2c6a89fa95b31a701dfc5c77c89df95f39a7f4a02'
COMPILED_SHA='7108529ae5e306ee8cf6d926596bb16f2366ba2924b2841acbff215e9e7b6eb6'
MARKER="'use strict';\n// G is composed from preserved PE32 bytes. No native function is invoked here.\n"
GUARD="need(exact('Engine.dll',G.modules['Engine.dll'].guards.current_tick),'bound getter changed')"
CALL='requireGetterOriginal()'
HELPER="""function requireGetterOriginal(){
 const g=G.modules['Engine.dll'].guards.current_tick;
 const actual=new Uint8Array(mods['Engine.dll'].add(g.rva).readByteArray(g.length)),expected=rebased('Engine.dll',g);
 if(!(actual.length===expected.length&&expected.every((v,i)=>actual[i]===v))){
  need(false,'bound getter changed',{
   actual_hex:Array.from(actual,x=>x.toString(16).padStart(2,'0')).join(''),
   expected_rebased_hex:Array.from(expected,x=>x.toString(16).padStart(2,'0')).join(''),
   rva:g.rva,length:g.length,getter_registered:hooks.has('getter_binding'),
   getter_callbacks:getterCallbacks,tls_bound:tls!==null,tls_binding:clone(tlsBinding)});
 }
}
"""

def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)

def patch_body(text):
    require(digest(text)==BODY_SHA,'exact disabled getter-boundary Observer body required')
    require(text.count(GUARD)==3 and text.count('function lifetime(){')==1,
            'exact three getter guards and helper insertion required')
    return text.replace(GUARD,CALL).replace('function lifetime(){',HELPER+'function lifetime(){',1)

def reverse_body(text):
    require(text.count(HELPER)==1 and text.count(CALL)==4,
            'exact helper and three getter calls required')
    result=text.replace(HELPER,'',1).replace(CALL,GUARD)
    require(digest(result)==BODY_SHA,'entire getter receipt body inverse differs')
    return result

def patch_compiled(text):
    require(digest(text)==COMPILED_SHA,'exact disabled compiled Observer required')
    require(text.count(MARKER)==1,'exact compiled body marker required')
    prefix,body=text.split(MARKER,1)
    return prefix+patch_body(MARKER+body)

def reverse_compiled(text):
    require(text.count(MARKER)==1,'exact compiled inverse marker required')
    prefix,body=text.split(MARKER,1)
    result=prefix+reverse_body(MARKER+body)
    require(digest(result)==COMPILED_SHA,'entire compiled/G inverse differs')
    return result
