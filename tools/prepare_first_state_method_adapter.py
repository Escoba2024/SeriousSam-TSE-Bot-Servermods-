"""Build ONLY a fresh private disabled method API package; no launcher/runtime.

All machine-byte bindings come from the pinned private parent at build time.
The public repository contains only authored source transforms and transport.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
try:
    from . import first_state_method_patch as PATCH
except ImportError:
    import first_state_method_patch as PATCH

PARENT=Path('/srv/tse-a1-first-state-controller-v2-completion-20261112')
OBSERVER_PARENT=Path('/srv/tse-a1-first-state-respawn-completion-20261112')
PARENT_SHA='fdd1b2598e21b4367e8a406d13ba3b64a22814fc40072e9377f05cbf20c8a8b3'
OBSERVER_MANIFEST_SHA='766485c5b28200b8523e74b1c597146eb2dfc905c087855d1dcc8c7f39701c00'
BINDINGS_SHA='6cc163c5f171f013d25026f659f00b3c596b8c11e931eca32c8cfa8c951245c8'
TOOLS=Path(__file__).resolve().parent
DEFAULT_OUTPUT=Path('/srv/tse-a1-first-state-method-adapter-final-disabled-20261115')
BASE_WORKER_SHA='acf3fa017447c9eea0431c996196d01d0d7d04a8f9029c81caeec3af23c4015b'
QUALIFIED_WORKER=Path('/srv/tse-a3-instruction-probe-root-frozen-20261114/original_damage_worker.py')
QUALIFIED_WORKER_SHA='806d4c33a3db0f5c208ee235319850513715c6144ed30912e95cf554e38b677c'


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def require(condition,message):
    if not condition:raise ValueError(message)


def write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(data)


def dump(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def verify_package(root):
    root=Path(root).resolve(strict=True);m=json.loads((root/'source-manifest.json').read_text())
    require(m['scope']=='DISABLED_METHOD_ADAPTER_API_ONLY' and m['runtime_reviewed']is False and m['qualified']is False,'disabled package gate/scope')
    require(m['runner_integrated']is False and m['ai_population_adapter']is False,'unintegrated historical runner only')
    require(digest(PARENT/'source-manifest.json')==PARENT_SHA,'parent manifest changed')
    parent=json.loads((PARENT/'source-manifest.json').read_text())
    expected={str(root/Path(name).relative_to(PARENT))if Path(name).is_relative_to(PARENT)else name for name in parent['runtime_dependencies']}
    expected.update(str(root/name)for name in('first_state_method_transport.py','original_damage_worker.py','first_state_method_patch.py','observer_body.js'))
    require(set(m['runtime_dependencies'])==expected,'complete runtime closure differs')
    for name,want in m['runtime_dependencies'].items():require(digest(name)==want,'runtime source pin:'+name)
    require(digest(root/'vendor/observer/bindings/original-bindings.json')==BINDINGS_SHA,'38 binding bytes changed')
    body=(root/'observer_body.js').read_text();inverse=PATCH.reverse_body(body)
    old=(OBSERVER_PARENT/'successor/observer_body.js').read_text();require(inverse==old,'observer full body inverse differs')
    generated=(root/'vendor/observer/observer.js').read_text();parent_generated=(PARENT/'vendor/observer/observer.js').read_text()
    require(parent_generated.endswith(old)and generated==parent_generated[:-len(old)]+body,'generated observer/G-prefix differs')
    require(digest(root/'run_first_state.py')==digest(PARENT/'run_first_state.py'),'legacy runner changed')
    require('RUNTIME_REVIEWED=False' in(root/'run_first_state.py').read_text(),'legacy runner gate changed')
    require('RUNTIME_REVIEWED=False' in(root/'first_state_method_transport.py').read_text(),'worker gate changed')
    require(digest(root/'original_damage_worker.py')==BASE_WORKER_SHA and 'RUNTIME_REVIEWED=True'not in(root/'original_damage_worker.py').read_text(),'unused legacy CLI gate/source changed')
    require('const RUNTIME_REVIEWED = false;'in body and 'const RUNTIME_REVIEWED = true;'not in body,'observer gate changed')
    require(m['transport_limits']=={'observer_payload_bytes':2097152,'ipc_envelope_bytes':16384},'transport limits differ')
    return {'verified':True,'runtime_pins':len(m['runtime_dependencies']),'body_inverse_sha256':hashlib.sha256(inverse.encode()).hexdigest()}


def build(output=DEFAULT_OUTPUT,*,parent_manifest_sha256=PARENT_SHA):
    output=Path(output).absolute()
    require(digest(PARENT/'source-manifest.json')==parent_manifest_sha256==PARENT_SHA,'parent manifest pin differs')
    require(digest(OBSERVER_PARENT/'source-manifest.json')==OBSERVER_MANIFEST_SHA,'observer parent manifest pin differs')
    parent=json.loads((PARENT/'source-manifest.json').read_text())
    require(parent['runtime_reviewed']is False and parent['qualified']is False,'parent gates differ')
    require(parent['observer']['full_original_restore_regions']==38 and parent['observer']['bound_iat_targets']==11,'parent bindings scope differs')
    for name,want in parent['runtime_dependencies'].items():require(digest(name)==want,'parent runtime pin:'+name)
    body=(OBSERVER_PARENT/'successor/observer_body.js').read_text();new=PATCH.patch_body(body)
    bindings=PARENT/'vendor/observer/bindings/original-bindings.json';require(digest(bindings)==BINDINGS_SHA,'private binding pin differs')
    generated=(PARENT/'vendor/observer/observer.js').read_text();require(generated.endswith(body),'parent generated body differs')
    require(digest(TOOLS/'original_damage_worker.py')==BASE_WORKER_SHA,'disabled base worker source differs')
    require(digest(QUALIFIED_WORKER)==QUALIFIED_WORKER_SHA,'qualified lifecycle reference pin differs')
    require((TOOLS/'original_damage_worker.py').read_text()==QUALIFIED_WORKER.read_text().replace('RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'),'qualified lifecycle inverse differs')
    output.mkdir(mode=0o700)  # fresh only; never mutate any prior package
    runtime={};unchanged=[]
    for name,want in parent['runtime_dependencies'].items():
        source=Path(name)
        if source.is_relative_to(PARENT):
            relative=source.relative_to(PARENT);target=output/relative
            data=(generated[:-len(body)]+new).encode()if relative==Path('vendor/observer/observer.js')else source.read_bytes()
            write(target,data);runtime[str(target)]=digest(target)
            if digest(target)==want:unchanged.append(str(relative))
        else:runtime[name]=want
    for relative in('first_state_method_transport.py','original_damage_worker.py','first_state_method_patch.py'):
        write(output/relative,(TOOLS/relative).read_bytes());runtime[str(output/relative)]=digest(output/relative)
    write(output/'observer_body.js',new.encode());runtime[str(output/'observer_body.js')]=digest(output/'observer_body.js')
    write(output/'inherited-source-manifest.json',(PARENT/'source-manifest.json').read_bytes())
    m={'schema':'a1.first-state.disabled-method-adapter.v1','scope':'DISABLED_METHOD_ADAPTER_API_ONLY',
       'runtime_reviewed':False,'qualified':False,'native_qualified':False,'first_processed_state_proven':False,
       'runner_integrated':False,'ai_population_adapter':False,'runtime_dependencies':runtime,
       'parent':{'path':str(PARENT),'manifest_sha256':PARENT_SHA},
       'observer_parent_manifest_sha256':OBSERVER_MANIFEST_SHA,'bindings_sha256':BINDINGS_SHA,
       'original_restore_regions':38,'bound_iat_targets':11,'call_listener_kinds':18,'registry_actors':2,
       'legacy_limits':{'max_records':64,'max_order_calls':8192,'max_events':16384,'ttl_ms':125000},
       'transport_limits':{'observer_payload_bytes':2097152,'ipc_envelope_bytes':16384},
       'gates':{'worker':'RUNTIME_REVIEWED=False','observer':'const RUNTIME_REVIEWED = false;','legacy_runner':'RUNTIME_REVIEWED=False','unused_legacy_worker_cli':'RUNTIME_REVIEWED=False'},
       'worker_lifecycle_base':{'qualified_sha256':QUALIFIED_WORKER_SHA,'disabled_sha256':BASE_WORKER_SHA,'exact_inverse':'one RUNTIME_REVIEWED=True to False','cli_used':False},
       'unchanged_parent_files':unchanged,
       'source_pins':{str(TOOLS/name):digest(TOOLS/name)for name in('prepare_first_state_method_adapter.py','first_state_method_patch.py','first_state_method_transport.py','original_damage_worker.py')}}
    write(output/'source-manifest.json',dump(m))
    receipt={**verify_package(output),'status':m['scope'],'runner_integrated':False,
             'manifest_sha256':digest(output/'source-manifest.json'),'original_restore_regions':38,
             'unchanged_parent_files':len(unchanged),'modified_parent_files':['vendor/observer/observer.js'],
             'new_files':['first_state_method_transport.py','original_damage_worker.py','first_state_method_patch.py','observer_body.js']}
    write(output/'build-receipt.json',dump(receipt))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);args=parser.parse_args()
    print(json.dumps(build(args.output),sort_keys=True))
