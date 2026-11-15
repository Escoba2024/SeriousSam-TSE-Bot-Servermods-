"""Exact reversible restore-check relocation; no Retail codebytes authored."""
import hashlib

BODY_SHA='d80e65abaf9ef8e545435d83e564e556773fc8b5ec6420439cff00a520643fe4'
COMPILED_SHA='34e31ff811b9dc79cc741f742ace66bcf494df683632a9fd7bd3d2b0da9c7baf'
MARKER="'use strict';\n// G is composed from preserved PE32 bytes. No native function is invoked here.\n"
CHANGES=[
    ("      need(exact('Engine.dll',g),'getter restore mismatch after binding');\n",''),
    ('function emit(frame,edge,player,payload){\n',"function emit(frame,edge,player,payload){\n if(tls)need(exact('Engine.dll',G.modules['Engine.dll'].guards.current_tick),'bound getter changed');\n"),
    ("  if(enabled){try{bounded();lifetime();}catch(e){fail(e,null);}}\n",
     "  if(enabled||tls){try{if(enabled){bounded();lifetime();}else need(exact('Engine.dll',G.modules['Engine.dll'].guards.current_tick),'bound getter changed');}catch(e){fail(e,null);}}\n"),
]


def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)


def patch_body(text):
    require(digest(text)==BODY_SHA,'pinned Wine Observer body differs')
    for old,new in CHANGES:
        require(text.count(old)==1,'exact boundary source anchor differs');text=text.replace(old,new,1)
    return text


def reverse_body(text):
    # Empty replacement is restored at its exact surviving neighbour.
    for old,new in reversed(CHANGES[1:]):
        require(text.count(new)==1,'boundary inverse anchor differs');text=text.replace(new,old,1)
    anchor="      const h=hooks.get('getter_binding');h.detach();hooks.delete('getter_binding');\n"
    require(text.count(anchor)==1,'getter detach inverse anchor differs')
    text=text.replace(anchor,anchor+CHANGES[0][0],1)
    require(digest(text)==BODY_SHA,'entire boundary body inverse differs');return text


def patch_compiled(text):
    require(digest(text)==COMPILED_SHA,'pinned Wine compiled/G differs')
    require(text.count(MARKER)==1,'body marker differs');prefix,body=text.split(MARKER,1)
    return prefix+patch_body(MARKER+body)


def reverse_compiled(text):
    require(text.count(MARKER)==1,'compiled inverse marker differs');prefix,body=text.split(MARKER,1)
    result=prefix+reverse_body(MARKER+body)
    require(digest(result)==COMPILED_SHA,'entire boundary compiled/G inverse differs');return result
