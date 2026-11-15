"""Fresh disabled monitor-only checkpoint; autonomous draining NOT implemented."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
try:
    from tools import first_state_method_monitor_patch as patch
    from tools.prepare_first_state_wine_identity import sha,require,dump,write
except ModuleNotFoundError:
    import first_state_method_monitor_patch as patch
    from prepare_first_state_wine_identity import sha,require,dump,write

PARENT=Path('/srv/tse-a1-first-state-getter-boundary-disabled-20261115')
PARENT_SHA='b365d06a882838ec06e2c61022fc141aa21595efa4b553749ab0e36d62bf03ea'
NESTED_SHA='1ba94da75fd8a4f11b10c8ac55569ccda774107e32863324ca89a84200fa8058'
OUTPUT=Path('/srv/tse-a1-first-state-method-monitor-disabled-20261115')
TOOLS=Path(__file__).resolve().parent;NESTED=Path('method-api/source-manifest.json')
OWN_SOURCES=('prepare_first_state_method_monitor.py','first_state_method_monitor_patch.py','prepare_first_state_wine_identity.py')


def mapped(name,root):
    p=Path(name);return str(root/p.relative_to(PARENT))if p.is_relative_to(PARENT)else name
def parents():
    require(sha(PARENT/'source-manifest.json')==PARENT_SHA and sha(PARENT/NESTED)==NESTED_SHA,'immutable monitor parent differs')
    p=json.loads((PARENT/'source-manifest.json').read_text());c=json.loads((PARENT/NESTED).read_text());require(len(p['runtime_dependencies'])==151 and len(c['runtime_dependencies'])==72,'parent closure count');return p,c
def nested_manifest(root,c):
    result=copy.deepcopy(c);result['runtime_dependencies']={mapped(n,root):w for n,w in c['runtime_dependencies'].items()}
    result.update(schema='a1.first-state.method-monitor-api.v1',scope='DISABLED_UNCHANGED_GETTER_BOUNDARY_METHOD_API_ONLY');return result
def expected_manifest(root,p,c):
    result=copy.deepcopy(p);runtime={mapped(n,root):w for n,w in p['runtime_dependencies'].items()}
    runtime[str(root/'run_dual.py')]=hashlib.sha256(patch.patch_runner((PARENT/'run_dual.py').read_text()).encode()).hexdigest()
    runtime[str(root/'first_state_inputfree_method.py')]=hashlib.sha256(patch.patch_helper((PARENT/'first_state_inputfree_method.py').read_text()).encode()).hexdigest()
    runtime[str(root/NESTED)]=hashlib.sha256(dump(nested_manifest(root,c))).hexdigest()
    result.update(schema='a1.first-state.method-monitor-window.v1',scope='DISABLED_INPUTFREE_METHOD_MONITOR_ONLY_SCHEDULER_PENDING',runtime_dependencies=runtime,
        method_api={'root':str(root/'method-api'),'manifest_sha256':runtime[str(root/NESTED)],'runtime_reviewed':False},
        method_monitor_parent={'path':str(PARENT),'manifest_sha256':PARENT_SHA},active_inventory_geometry_fixed_life_qualified=False,native_summary_scope='JOIN_PREARM_ONLY',
        new_matched_control_required=True,prior_control_transfer_authorized=False,native_ready=False,scheduler_implemented=False,scheduler_review_required=True,
        monitor_source_pins={str(TOOLS/name):sha(TOOLS/name)for name in OWN_SOURCES});return result
def verify_package(root):
    root=Path(root).resolve(strict=True);p,c=parents();m=json.loads((root/'source-manifest.json').read_text())
    require(m==expected_manifest(root,p,c),'entire monitor expected metadata/hash values differ')
    for n,w in m['runtime_dependencies'].items():require(sha(n)==w,'actual monitor dependency differs:'+n)
    require(json.loads((root/NESTED).read_text())==nested_manifest(root,c),'entire72 nested expected hash/path values differ')
    require(patch.reverse_runner((root/'run_dual.py').read_text())==(PARENT/'run_dual.py').read_text(),'whole runner inverse')
    require(patch.reverse_helper((root/'first_state_inputfree_method.py').read_text())==(PARENT/'first_state_inputfree_method.py').read_text(),'whole helper comment inverse')
    unchanged=[]
    for n in p['runtime_dependencies']:
        path=Path(n)
        if path.is_relative_to(PARENT)and path.relative_to(PARENT)not in(NESTED,Path('run_dual.py'),Path('first_state_inputfree_method.py')):
            rel=path.relative_to(PARENT);require((root/rel).read_bytes()==path.read_bytes(),'unchanged source differs:'+n);unchanged.append(str(rel))
    return {'verified':True,'runtime_pins':151,'method_runtime_pins':72,'unchanged_parent_files':len(unchanged),'unchanged_parent_file_list':sorted(unchanged),'runner_inverse_sha256':patch.RUNNER_SHA,'helper_inverse_sha256':patch.HELPER_SHA,'native_ready':False,'status':'DISABLED_METHOD_MONITOR_ONLY_SCHEDULER_PENDING'}
def build(output=OUTPUT,*,parent_manifest_sha256=PARENT_SHA):
    require(parent_manifest_sha256==PARENT_SHA,'requested monitor parent differs');p,c=parents()
    for group in(p,c):
        for n,w in group['runtime_dependencies'].items():require(sha(n)==w,'immutable parent dependency differs:'+n)
    root=Path(output).absolute();m=expected_manifest(root,p,c);root.mkdir(mode=0o700)
    changed={Path('run_dual.py'):patch.patch_runner((PARENT/'run_dual.py').read_text()).encode(),Path('first_state_inputfree_method.py'):patch.patch_helper((PARENT/'first_state_inputfree_method.py').read_text()).encode(),NESTED:dump(nested_manifest(root,c))}
    for n in p['runtime_dependencies']:
        path=Path(n)
        if path.is_relative_to(PARENT):
            rel=path.relative_to(PARENT);write(root/rel,changed[rel]if rel in changed else path.read_bytes())
    write(root/'source-manifest.json',dump(m));r={**verify_package(root),'manifest_sha256':sha(root/'source-manifest.json')};write(root/'build-receipt.json',dump(r));return r


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args();print(json.dumps(build(args.output),sort_keys=True))
