"""Generate PRIVATE Original input guards from pinned files. No runtime access."""
import argparse
import hashlib
import importlib.util
import json
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
             ('GameMP.dll',0x60851231,0xd6,'Original timer input/action callers and character offset')]
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
    result=dict(schema='a1-original-input-static-guards-v1',modules=modules,
                guards=guards,sites=sites,
                callers=dict(input_return_rva=0x60851241-pe['GameMP.dll'].base,
                             action_return_rva=0x608512fb-pe['GameMP.dll'].base),
                native_abi_qualified=False)
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
