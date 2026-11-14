"""Generate PRIVATE Original input guards from pinned files. No runtime access."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

PE_HELPER = Path('/srv/tse-a1-nosmooth-root-frozen-20261114/pe_original.py')
PE_SHA = 'e7e396daa3db837e31bc7d4531cdfab991fa6afbbe8091f1c6143314263c48fb'
SHAS = {'Engine.dll':'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f',
        'GameMP.dll':'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'}
# Preferred VAs copied from the archived Original disassembly, not guessed RVAs.
SITES = {
    'input':('Engine.dll',0x600cd200,'558bec81ec30010000'),
    'cursor_return':('Engine.dll',0x600cd2b2,'85c00f8486020000'),
    'recenter_call':('Engine.dll',0x600cd56a,'ff15e8422560'),
    'recenter_return':('Engine.dll',0x600cd570,'a180172b60'),
    'action':('GameMP.dll',0x60850470,'558bec53568bf157'),
    'compose_call':('GameMP.dll',0x608504fe,'ff1504148660'),
}


def original_exports(image):
    def string(rva):
        start=image.offset(rva)
        return image.b[start:image.b.index(b'\0',start)].decode('ascii')
    directory,size=struct.unpack_from('<II',image.b,image.opt+96)
    count,functions,names,ordinals=struct.unpack_from('<4I',image.region(directory+24,16))
    result={}
    for index in range(count):
        name=string(struct.unpack('<I',image.region(names+index*4,4))[0])
        ordinal=struct.unpack('<H',image.region(ordinals+index*2,2))[0]
        result[name]=struct.unpack('<I',image.region(functions+ordinal*4,4))[0]
    return result


def original_imports(image):
    directory,size=struct.unpack_from('<II',image.b,image.opt+104)
    result={}
    for offset in range(0,size,20):
        original,stamp,forward,name,iat=struct.unpack('<5I',image.region(directory+offset,20))
        if not any((original,name,iat)):break
        table=original or iat;index=0
        while True:
            entry=struct.unpack('<I',image.region(table+index*4,4))[0]
            if not entry:break
            if not entry&0x80000000:
                start=image.offset(entry+2)
                result[iat+index*4]=image.b[start:image.b.index(b'\0',start)].decode('ascii')
            index+=1
    return result


def generate(originals, output):
    if hashlib.sha256(PE_HELPER.read_bytes()).hexdigest() != PE_SHA:
        raise ValueError('inherited PE helper pin differs')
    spec=importlib.util.spec_from_file_location('a1_input_original_pe',PE_HELPER)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    pe={name:helper.PE(Path(originals)/name,sha)for name,sha in SHAS.items()}
    modules={name:dict(sha256=SHAS[name],preferred_base=p.base,image_size=p.image)
             for name,p in pe.items()}
    regions=[('Engine.dll',0x600cd200,0x725,'Original full GetInput including cursor/recenter'),
             ('GameMP.dll',0x60850470,0x9e,'Original full CreateAction'),
             ('GameMP.dll',0x60850390,0xe0,'Original full GetAxisValue'),
             ('GameMP.dll',0x60851190,11,'Original Game pointer getter'),
             ('GameMP.dll',0x60851231,0xd6,'Original timer input/action callers and character offset'),
             ('GameMP.dll',0x608511a0,0x3b,'Original GameHandleTimer prologue binds EDI Game'),
             ('GameMP.dll',0x6086156c,36,'Original CControls vtable through CreateAction'),
             ('Engine.dll',0x600cb020,4,'Original IsInputEnabled getter'),
             ('Engine.dll',0x6019ab60,29,'Original IsPaused including fallback'),
             ('Engine.dll',0x6019ac30,26,'Original GetLocalPause including fallback')]
    guards=[]
    for name,va,length,label in regions:
        guard=pe[name].guard(va-pe[name].base,length)
        guard.update(module=name,label=label);guards.append(guard)
    assert guards[0]['hex'].endswith('c20400')
    assert guards[1]['hex'].endswith('c20c00')
    sites={}
    for key,(name,va,prefix)in SITES.items():
        rva=va-pe[name].base
        if pe[name].region(rva,len(bytes.fromhex(prefix))).hex()!=prefix:
            raise ValueError('Original instruction boundary differs: '+key)
        sites[key]=dict(module=name,preferred_va=va,rva=rva,entry_bytes=prefix)
    exports=original_exports(pe['Engine.dll']);imports=original_imports(pe['GameMP.dll'])
    for symbol,rva in [('?IsInputEnabled@CInput@@QBEHXZ',0xb020),
                       ('?IsPaused@CNetworkLibrary@@QAEHXZ',0xdab60),
                       ('?GetLocalPause@CNetworkLibrary@@QAEHXZ',0xdac30)]:
        if exports.get(symbol)!=rva:raise ValueError('Original export binding differs: '+symbol)
    for rva,symbol in [(0x2129c,'?IsPaused@CNetworkLibrary@@QAEHXZ'),
                       (0x21298,'?GetLocalPause@CNetworkLibrary@@QAEHXZ')]:
        if imports.get(rva)!=symbol:raise ValueError('Original timer IAT binding differs')
    # Same Original image pins as all existing sites; file-level opcode and
    # export/IAT evidence is retained privately. No new callback/call is added.
    if struct.unpack('<I',pe['GameMP.dll'].region(0x2158c,4))[0]!=0x60850470:
        raise ValueError('Original vtable CreateAction target differs')
    timer_gate=dict(schema='original107-timer-guard-observation-v1',
        game_on_offset=0xf54,game_menu_offset=0xf58,input_enabled_offset=4,
        network_pointer_rva=0x20d6a4,network_guard_rva=0x20d6b8,
        network_session_offset=0x20,session_pause_offset=0xa8,
        network_local_pause_offset=0x854,controls_vtable_rva=0x2156c,
        controls_action_slot_offset=0x20,caller_game_register='edi',
        original_getters={
            'is_input_enabled':dict(module='Engine.dll',va=0x600cb020,rva=0xb020),
            'is_paused':dict(module='Engine.dll',va=0x6019ab60,rva=0xdab60,game_iat_rva=0x2129c),
            'get_local_pause':dict(module='Engine.dll',va=0x6019ac30,rva=0xdac30,game_iat_rva=0x21298)},
        basis='SDK107 GameHandleTimer plus hash-pinned Original file/export/IAT/opcode cross-check; not native branch proof')
    result=dict(schema='a1-original-input-static-guards-v1',modules=modules,
                guards=guards,sites=sites,
                callers=dict(input_return_rva=0x60851241-pe['GameMP.dll'].base,
                             action_return_rva=0x608512fb-pe['GameMP.dll'].base),
                timer_gate=timer_gate,native_abi_qualified=False)
    with Path(output).open('x')as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    Path(output).chmod(0o600)
    return dict(scope='STATIC_FILE_PINS_ONLY',sites_verified=len(sites),
                sha256=hashlib.sha256(Path(output).read_bytes()).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--originals',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(generate(args.originals,args.output)))
