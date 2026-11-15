"""Exact reversible read-only PE header identity for the pinned private body.

Only standard PE metadata is authored here. Original code/bindings remain private.
This is a source adaptation, not native ABI or first-state qualification.
"""
import hashlib

BODY_SHA='7d93b441ca9657fa09771a011440c4e651136c656e8c0504a2ddf9420f681158'
COMPILED_SHA='fec627f202376fae1a5682102fb8344f4ef814ab6ba3e462080e4099adc329a6'
MARKER="'use strict';\n// G is composed from preserved PE32 bytes. No native function is invoked here.\n"
HEADER_PINS={
    'Engine.dll':{'file_sha256':'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f','e_lfanew':264,'optional_size':224,'image_size':2285568},
    'EntitiesMP.dll':{'file_sha256':'7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350','e_lfanew':248,'optional_size':224,'image_size':2539520},
}
OLD="""function moduleIdentity(){
 for(const [name,m]of Object.entries(G.modules)){const loaded=Process.getModuleByName(name);need(loaded&&loaded.base.equals(mods[name])&&loaded.size===m.image_size,'module identity changed',name);}
}
"""
NEW="""function moduleIdentity(){
 // Original PE metadata at host-pinned bases; Wine need not expose PE modules.
 const ntOffsets={'Engine.dll':264,'EntitiesMP.dll':248};
 for(const [name,m]of Object.entries(G.modules)){
  const base=mods[name],value=base.toUInt32();
  need(value%4096===0&&value+m.image_size<=0x100000000,'module base bounds',name);
  need(rawHex(base,2)==='4d5a','module DOS header',name);
  const offset=base.add(0x3c).readU32();
  need(offset>=64&&offset<=4096-248&&offset===ntOffsets[name],'module NT offset',name);
  const nt=base.add(offset);
  need(nt.readU32()===0x4550,'module PE signature',name);
  need(rawHex(nt.add(4),2)==='4c01','module machine',name);
  need(rawHex(nt.add(20),2)==='e000','module optional size',name);
  need(rawHex(nt.add(24),2)==='0b01','module optional magic',name);
  need(nt.add(80).readU32()===m.image_size,'module image size',name);
 }
}
"""


def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)


def patch_body(text):
    require(digest(text)==BODY_SHA,'Original body source pin differs')
    require(text.count(OLD)==1,'module identity source anchor differs')
    return text.replace(OLD,NEW,1)


def reverse_body(text):
    require(text.count(NEW)==1,'Wine identity inverse anchor differs')
    result=text.replace(NEW,OLD,1)
    require(digest(result)==BODY_SHA,'entire Original body inverse differs')
    return result


def patch_compiled(text):
    require(digest(text)==COMPILED_SHA,'compiled Original/G pin differs')
    require(text.count(MARKER)==1,'compiled body marker differs')
    prefix,body=text.split(MARKER,1)
    return prefix+patch_body(MARKER+body)


def reverse_compiled(text):
    require(text.count(MARKER)==1,'compiled inverse body marker differs')
    prefix,body=text.split(MARKER,1)
    result=prefix+reverse_body(MARKER+body)
    require(digest(result)==COMPILED_SHA,'entire compiled/G inverse differs')
    return result
