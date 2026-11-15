"""Fresh disabled method-window fork; exact parent bytes plus PE identity only.

The private parent is never edited. Hash values, not just closure keys, are
derived from the immutable parent; repinning a changed body cannot authorize it.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
try:
    from tools import first_state_wine_identity_patch as patch
except ModuleNotFoundError:
    import first_state_wine_identity_patch as patch

PARENT=Path('/srv/tse-a1-first-state-inputfree-method-final-disabled-20261115')
PARENT_SHA='51e1bc45eb312f3d9b03dd07640fa436a588f3363ed1d00d93454a01f1ceb365'
NESTED_SHA='075de9a579a22bc2807586eb454e30273f51ad6c01d2e8d53af89e6bb610d278'
RUNNER_SHA='2c79c51dcdd3c757c9fd190c56d33a21c0a1635aa16e0d55890f54783c6f7eef'
OUTPUT=Path('/srv/tse-a1-first-state-wine-identity-disabled-20261115')
TOOLS=Path(__file__).resolve().parent
SCOPE='DISABLED_INPUTFREE_TWO_ORIGINAL_WINE_HEADER_IDENTITY_METHOD_ONLY'
CHANGES=[("PREFIX='ssam-a1-first-state-method-disabled-20261115'","PREFIX='ssam-a1-first-state-wine-identity-disabled-20261115'"),
         ("E=BASE/('a1-first-state-method-disabled-'+arm+'-'","E=BASE/('a1-first-state-wine-identity-disabled-'+arm+'-'")]
BODY=Path('method-api/observer_body.js')
COMPILED=Path('method-api/vendor/observer/observer.js')
NESTED=Path('method-api/source-manifest.json')
OWN_SOURCES=('prepare_first_state_wine_identity.py','first_state_wine_identity_patch.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def dump(obj):return(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(data)
def mapped(name,root):
    p=Path(name);return str(root/p.relative_to(PARENT))if p.is_relative_to(PARENT)else name
def once(text,old,new):
    require(text.count(old)==1,'exact namespace anchor differs');return text.replace(old,new,1)


def patch_runner(text):
    require(hashlib.sha256(text.encode()).hexdigest()==RUNNER_SHA,'parent runner pin differs')
    for old,new in CHANGES:text=once(text,old,new)
    return text


def reverse_runner(text):
    for old,new in reversed(CHANGES):text=once(text,new,old)
    require(hashlib.sha256(text.encode()).hexdigest()==RUNNER_SHA,'entire runner inverse differs')
    return text


def parents():
    require(sha(PARENT/'source-manifest.json')==PARENT_SHA,'immutable window parent manifest differs')
    require(sha(PARENT/NESTED)==NESTED_SHA,'immutable nested72 parent manifest differs')
    parent=json.loads((PARENT/'source-manifest.json').read_text());nested=json.loads((PARENT/NESTED).read_text())
    require(len(parent['runtime_dependencies'])==151 and len(nested['runtime_dependencies'])==72,'exact parent closure size')
    return parent,nested


def derivation():
    return {'kind':'STRICT_READONLY_STANDARD_PE_HEADERS_AT_HOST_PINNED_BASES','parent_body_sha256':patch.BODY_SHA,
            'parent_compiled_sha256':patch.COMPILED_SHA,'header_pins':patch.HEADER_PINS,
            'nt_offset_bounds':[64,3848],'header_reads_per_module':8,'frida_module_list_used':False,
            'native_method_qualified':False,'no_additional_hooks_inputs_or_memory_writes':True,
            'host_38_body_highlow_11_iat_guards_unchanged':True}


def nested_manifest(root,nested):
    result=copy.deepcopy(nested)
    result['runtime_dependencies']={mapped(name,root):want for name,want in nested['runtime_dependencies'].items()}
    result['runtime_dependencies'][str(root/BODY)]=hashlib.sha256(patch.patch_body((PARENT/BODY).read_text()).encode()).hexdigest()
    result['runtime_dependencies'][str(root/COMPILED)]=hashlib.sha256(patch.patch_compiled((PARENT/COMPILED).read_text()).encode()).hexdigest()
    result['schema']='a1.first-state.wine-header-method-api.v1';result['scope']='DISABLED_WINE_HEADER_METHOD_ADAPTER_API_ONLY'
    result['wine_header_identity_derivation']=derivation()
    return result


def expected_manifest(root,parent,nested):
    result=copy.deepcopy(parent);cm=nested_manifest(root,nested)
    runtime={mapped(name,root):want for name,want in parent['runtime_dependencies'].items()}
    runtime[str(root/BODY)]=cm['runtime_dependencies'][str(root/BODY)]
    runtime[str(root/COMPILED)]=cm['runtime_dependencies'][str(root/COMPILED)]
    runtime[str(root/NESTED)]=hashlib.sha256(dump(cm)).hexdigest()
    runtime[str(root/'run_dual.py')]=hashlib.sha256(patch_runner((PARENT/'run_dual.py').read_text()).encode()).hexdigest()
    result.update(schema='a1.first-state.wine-header-inputfree-method-window.v1',scope=SCOPE,
        runtime_dependencies=runtime,method_api={'root':str(root/'method-api'),'manifest_sha256':runtime[str(root/NESTED)],'runtime_reviewed':False},
        wine_identity_parent={'path':str(PARENT),'manifest_sha256':PARENT_SHA},wine_header_identity_derivation=derivation(),
        wine_identity_source_pins={str(TOOLS/name):sha(TOOLS/name)for name in OWN_SOURCES})
    return result


def verify_package(root):
    root=Path(root).resolve(strict=True);parent,nested=parents();expected=expected_manifest(root,parent,nested)
    actual=json.loads((root/'source-manifest.json').read_text())
    require(actual==expected,'complete expected manifest/closure hash values differ')
    for path,want in actual['runtime_dependencies'].items():require(sha(path)==want,'actual dependency pin differs:'+path)
    cm=json.loads((root/NESTED).read_text());require(cm==nested_manifest(root,nested),'all72 exact nested mappings/hash values/guards differ')
    require(cm['runtime_reviewed']is False and actual['runtime_reviewed']is False,'disabled gates required')
    require(patch.reverse_body((root/BODY).read_text())==(PARENT/BODY).read_text(),'entire body inverse')
    require(patch.reverse_compiled((root/COMPILED).read_text())==(PARENT/COMPILED).read_text(),'entire compiled/G inverse')
    require(reverse_runner((root/'run_dual.py').read_text())==(PARENT/'run_dual.py').read_text(),'entire runner inverse')
    unchanged=[]
    for name in parent['runtime_dependencies']:
        source=Path(name)
        if source.is_relative_to(PARENT)and source.relative_to(PARENT)not in(BODY,COMPILED,NESTED,Path('run_dual.py')):
            require((root/source.relative_to(PARENT)).read_bytes()==source.read_bytes(),'unchanged source differs:'+name)
            unchanged.append(str(source.relative_to(PARENT)))
    return {'verified':True,'runtime_pins':151,'method_runtime_pins':72,'unchanged_parent_files':len(unchanged),
            'unchanged_parent_file_list':sorted(unchanged),'body_inverse_sha256':patch.BODY_SHA,
            'compiled_inverse_sha256':patch.COMPILED_SHA,'runner_inverse_sha256':RUNNER_SHA,
            'status':'DISABLED_WINE_HEADER_METHOD_PREPARATION_ONLY'}


def build(output=OUTPUT,*,parent_manifest_sha256=PARENT_SHA):
    require(parent_manifest_sha256==PARENT_SHA,'requested parent pin differs');parent,nested=parents()
    for name,want in parent['runtime_dependencies'].items():require(sha(name)==want,'immutable parent dependency differs:'+name)
    for name,want in nested['runtime_dependencies'].items():require(sha(name)==want,'immutable nested dependency differs:'+name)
    root=Path(output).absolute();expected=expected_manifest(root,parent,nested);root.mkdir(mode=0o700)
    changed={BODY:patch.patch_body((PARENT/BODY).read_text()).encode(),COMPILED:patch.patch_compiled((PARENT/COMPILED).read_text()).encode(),
             Path('run_dual.py'):patch_runner((PARENT/'run_dual.py').read_text()).encode(),NESTED:dump(nested_manifest(root,nested))}
    for name in parent['runtime_dependencies']:
        source=Path(name)
        if source.is_relative_to(PARENT):
            rel=source.relative_to(PARENT);write(root/rel,changed[rel]if rel in changed else source.read_bytes())
    write(root/'source-manifest.json',dump(expected));receipt={**verify_package(root),'manifest_sha256':sha(root/'source-manifest.json')}
    write(root/'build-receipt.json',dump(receipt));return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args()
    print(json.dumps(build(args.output),sort_keys=True))
