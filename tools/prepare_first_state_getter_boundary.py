"""Fresh disabled input-free method fork; deferred getter restore verification.

All expected hash VALUES derive from pinned immutable parent manifests. This
does not activate any runtime or authorize a control/trace transfer.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
try:
    from tools import first_state_getter_boundary_patch as patch
    from tools.prepare_first_state_wine_identity import sha,require,dump,write
except ModuleNotFoundError:
    import first_state_getter_boundary_patch as patch
    from prepare_first_state_wine_identity import sha,require,dump,write

PARENT=Path('/srv/tse-a1-first-state-wine-identity-disabled-20261115')
PARENT_SHA='87d4c55adeeab514856d5b763b08355ef35db04b11f490314c3a85ad5fc6a2e9'
NESTED_SHA='24d85258f6f7af733af8e4014acff1f9b502591572d1332f894b54d3b9c090e6'
RUNNER_SHA='6bfe753dbedd05e88b03eb1ee2caf82ea3cee2dde0fdff04a5edfe77e0ee673a'
OUTPUT=Path('/srv/tse-a1-first-state-getter-boundary-disabled-20261115')
TOOLS=Path(__file__).resolve().parent
BODY=Path('method-api/observer_body.js');COMPILED=Path('method-api/vendor/observer/observer.js');NESTED=Path('method-api/source-manifest.json')
CHANGES=[("PREFIX='ssam-a1-first-state-wine-identity-disabled-20261115'","PREFIX='ssam-a1-first-state-getter-boundary-disabled-20261115'"),
         ("E=BASE/('a1-first-state-wine-identity-disabled-'+arm+'-'","E=BASE/('a1-first-state-getter-boundary-disabled-'+arm+'-'")]
OWN_SOURCES=('prepare_first_state_getter_boundary.py','first_state_getter_boundary_patch.py','prepare_first_state_wine_identity.py')


def mapped(name,root):
    p=Path(name);return str(root/p.relative_to(PARENT))if p.is_relative_to(PARENT)else name
def once(text,old,new):
    require(text.count(old)==1,'boundary namespace anchor differs');return text.replace(old,new,1)
def patch_runner(text):
    require(hashlib.sha256(text.encode()).hexdigest()==RUNNER_SHA,'immutable runner differs')
    for old,new in CHANGES:text=once(text,old,new)
    return text
def reverse_runner(text):
    for old,new in reversed(CHANGES):text=once(text,new,old)
    require(hashlib.sha256(text.encode()).hexdigest()==RUNNER_SHA,'entire runner inverse differs');return text


def parents():
    require(sha(PARENT/'source-manifest.json')==PARENT_SHA,'immutable parent manifest differs')
    require(sha(PARENT/NESTED)==NESTED_SHA,'immutable nested parent manifest differs')
    p=json.loads((PARENT/'source-manifest.json').read_text());c=json.loads((PARENT/NESTED).read_text())
    require(len(p['runtime_dependencies'])==151 and len(c['runtime_dependencies'])==72,'parent closure count differs');return p,c


def derivation():
    return {'kind':'FULL_GETTER_RESTORE_AFTER_AUTOMATIC_RUNTIME_COMMIT','parent_body_sha256':patch.BODY_SHA,'parent_compiled_sha256':patch.COMPILED_SHA,
        'inside_getter_eager_check_removed':True,'lifetime_byte_unchanged':True,'full_getter_check_before_emit':True,'full_getter_check_in_stopped_drain':True,
        'no_flush_nativefunction_memorywrites_or_new_hooks':True,'schema_counters_ttl_and_limits_unchanged':True,'native_method_qualified':False}


def nested_manifest(root,parent):
    c=copy.deepcopy(parent);c['runtime_dependencies']={mapped(p,root):w for p,w in parent['runtime_dependencies'].items()}
    c['runtime_dependencies'][str(root/BODY)]=hashlib.sha256(patch.patch_body((PARENT/BODY).read_text()).encode()).hexdigest()
    c['runtime_dependencies'][str(root/COMPILED)]=hashlib.sha256(patch.patch_compiled((PARENT/COMPILED).read_text()).encode()).hexdigest()
    c.update(schema='a1.first-state.getter-boundary-method-api.v1',scope='DISABLED_GETTER_BOUNDARY_METHOD_ADAPTER_API_ONLY',getter_boundary_derivation=derivation());return c


def expected_manifest(root,parent,nested):
    m=copy.deepcopy(parent);c=nested_manifest(root,nested)
    runtime={mapped(p,root):w for p,w in parent['runtime_dependencies'].items()}
    for rel in(BODY,COMPILED):runtime[str(root/rel)]=c['runtime_dependencies'][str(root/rel)]
    runtime[str(root/NESTED)]=hashlib.sha256(dump(c)).hexdigest()
    runtime[str(root/'run_dual.py')]=hashlib.sha256(patch_runner((PARENT/'run_dual.py').read_text()).encode()).hexdigest()
    m.update(schema='a1.first-state.getter-boundary-inputfree-method-window.v1',scope='DISABLED_INPUTFREE_TWO_ORIGINAL_GETTER_RESTORE_BOUNDARY_METHOD_ONLY',runtime_dependencies=runtime,
        method_api={'root':str(root/'method-api'),'manifest_sha256':runtime[str(root/NESTED)],'runtime_reviewed':False},
        getter_boundary_parent={'path':str(PARENT),'manifest_sha256':PARENT_SHA},getter_boundary_derivation=derivation(),
        getter_boundary_source_pins={str(TOOLS/name):sha(TOOLS/name)for name in OWN_SOURCES});return m


def verify_package(root):
    root=Path(root).resolve(strict=True);p,c=parents();m=json.loads((root/'source-manifest.json').read_text())
    require(m==expected_manifest(root,p,c),'complete expected manifest/path/hash values differ')
    for name,w in m['runtime_dependencies'].items():require(sha(name)==w,'actual dependency differs:'+name)
    cm=json.loads((root/NESTED).read_text());require(cm==nested_manifest(root,c),'all72 nested values differ')
    require(cm['runtime_reviewed']is False and m['runtime_reviewed']is False,'disabled gate required')
    require(patch.reverse_body((root/BODY).read_text())==(PARENT/BODY).read_text(),'entire body inverse differs')
    require(patch.reverse_compiled((root/COMPILED).read_text())==(PARENT/COMPILED).read_text(),'entire compiled/G inverse differs')
    require(reverse_runner((root/'run_dual.py').read_text())==(PARENT/'run_dual.py').read_text(),'entire runner inverse differs')
    unchanged=[]
    for name in p['runtime_dependencies']:
        source=Path(name)
        if source.is_relative_to(PARENT)and source.relative_to(PARENT)not in(BODY,COMPILED,NESTED,Path('run_dual.py')):
            rel=source.relative_to(PARENT);require((root/rel).read_bytes()==source.read_bytes(),'unchanged source differs:'+name);unchanged.append(str(rel))
    return {'verified':True,'runtime_pins':151,'method_runtime_pins':72,'unchanged_parent_files':len(unchanged),'unchanged_parent_file_list':sorted(unchanged),
            'body_inverse_sha256':patch.BODY_SHA,'compiled_inverse_sha256':patch.COMPILED_SHA,'runner_inverse_sha256':RUNNER_SHA,'status':'DISABLED_GETTER_RESTORE_BOUNDARY_METHOD_PREPARATION_ONLY'}


def build(output=OUTPUT,*,parent_manifest_sha256=PARENT_SHA):
    require(parent_manifest_sha256==PARENT_SHA,'requested parent pin differs');p,c=parents()
    for group in(p,c):
        for name,w in group['runtime_dependencies'].items():require(sha(name)==w,'immutable parent dependency differs:'+name)
    root=Path(output).absolute();m=expected_manifest(root,p,c);root.mkdir(mode=0o700)
    changed={BODY:patch.patch_body((PARENT/BODY).read_text()).encode(),COMPILED:patch.patch_compiled((PARENT/COMPILED).read_text()).encode(),NESTED:dump(nested_manifest(root,c)),Path('run_dual.py'):patch_runner((PARENT/'run_dual.py').read_text()).encode()}
    for name in p['runtime_dependencies']:
        source=Path(name)
        if source.is_relative_to(PARENT):
            rel=source.relative_to(PARENT);write(root/rel,changed[rel]if rel in changed else source.read_bytes())
    write(root/'source-manifest.json',dump(m));receipt={**verify_package(root),'manifest_sha256':sha(root/'source-manifest.json')};write(root/'build-receipt.json',dump(receipt));return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args();print(json.dumps(build(args.output),sort_keys=True))
