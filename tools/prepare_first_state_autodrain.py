"""Fresh disabled method-only autonomous drain package; never starts a process."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
try:
    from tools import first_state_autodrain_window_patch as patch
except ModuleNotFoundError:
    import first_state_autodrain_window_patch as patch

PARENT = Path('/srv/tse-a1-first-state-method-monitor-disabled-20261115')
PARENT_SHA = 'eb7f2632df14f7b0ce424b4b5ad6d9b3c8e918baf2e648159bcf176e279d5622'
NESTED_SHA = 'e1e785faf541b1ffb9f666c86df772be28be7c1428199688df7ce988f62244e8'
OUTPUT = Path('/srv/tse-a1-first-state-autodrain-disabled-20261115')
TOOLS = Path(__file__).resolve().parent
NESTED = Path('method-api/source-manifest.json')
NEW_API = ('first_state_autodrain_protocol.py', 'first_state_autodrain_worker.py',
           'first_state_autodrain_session.py')
OWN_SOURCES = NEW_API + ('first_state_autodrain_window_patch.py', 'prepare_first_state_autodrain.py')


def require(value, message):
    if not value: raise ValueError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(value): return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def write(path, data):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd = os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream: stream.write(data); stream.flush(); os.fsync(stream.fileno())


def mapped(name, root):
    path = Path(name)
    return str(root/path.relative_to(PARENT)) if path.is_relative_to(PARENT) else name


def parents():
    require(sha(PARENT/'source-manifest.json') == PARENT_SHA and sha(PARENT/NESTED) == NESTED_SHA,
            'immutable monitor parent manifest differs')
    parent = json.loads((PARENT/'source-manifest.json').read_text())
    nested = json.loads((PARENT/NESTED).read_text())
    require(len(parent['runtime_dependencies']) == 151 and len(nested['runtime_dependencies']) == 72,
            'immutable parent closure count')
    return parent, nested


def nested_manifest(root, parent):
    result = copy.deepcopy(parent)
    result['runtime_dependencies'] = {mapped(name,root):digest for name,digest in parent['runtime_dependencies'].items()}
    result['runtime_dependencies'].update({str(root/'method-api'/name):sha(TOOLS/name) for name in NEW_API})
    result.update(schema='a1.first-state.autodrain-api.v1',
        scope='DISABLED_METHOD_ONLY_AUTONOMOUS_DRAIN_API_NO_NATIVE_QUALIFICATION',runtime_reviewed=False,
        active_worker='first_state_autodrain_worker.py',unused_legacy_method_transport_cli=True)
    result['gates']['autodrain_worker'] = 'RUNTIME_REVIEWED = False'
    return result


def expected_manifest(root, parent, nested):
    result = copy.deepcopy(parent)
    runtime = {mapped(name,root):digest for name,digest in parent['runtime_dependencies'].items()}
    runtime[str(root/'run_dual.py')] = hashlib.sha256(patch.patch_runner((PARENT/'run_dual.py').read_text()).encode()).hexdigest()
    runtime[str(root/'first_state_inputfree_method.py')] = hashlib.sha256(patch.patch_helper((PARENT/'first_state_inputfree_method.py').read_text()).encode()).hexdigest()
    runtime.update({str(root/'method-api'/name):sha(TOOLS/name) for name in NEW_API})
    runtime[str(root/NESTED)] = hashlib.sha256(dump(nested_manifest(root,nested))).hexdigest()
    result.update(schema='a1.first-state.autodrain-window.v1',
        scope='DISABLED_INPUTFREE_AUTODRAIN_METHOD_WINDOW_SOURCE_ONLY',runtime_dependencies=runtime,
        method_api={'root':str(root/'method-api'),'manifest_sha256':runtime[str(root/NESTED)],'runtime_reviewed':False},
        autodrain_parent={'path':str(PARENT),'manifest_sha256':PARENT_SHA,'nested_manifest_sha256':NESTED_SHA},
        autodrain_source_pins={str(TOOLS/name):sha(TOOLS/name) for name in OWN_SOURCES},
        scheduler_implemented=True,scheduler_review_required=True,native_ready=False,
        new_matched_control_required=True,prior_control_transfer_authorized=False,
        active_inventory_geometry_fixed_life_qualified=False,native_summary_scope='JOIN_PREARM_ONLY',
        autodrain_limits={'target_interval_seconds':.02,'capture_service_max_seconds':.1,
            'max_captures':1024,'journal_max_bytes':512*1024*1024,'payload_max_bytes':2*1024*1024,
            'envelope_max_bytes':16*1024,'arm_ipc_seconds':3,'batch_ipc_seconds':.1,
            'cleanup_ipc_seconds':2,'active_seconds':10,'inner_absolute_seconds':85,
            'outer_admission_seconds':90,'ttl_ms':15000},
        buffer_scope='ONE_INDEXED_TRANSPORT_WIRE_BUFFER_NOT_WHOLE_PYTHON_HEAP',
        stop_guard_order='OWN_WORKER_BINDING_THEN_ADMISSION_CLOSE_THEN_FULL_PARENT_GUARD',
        ordinary_batch_guard_order='FULL_PARENT_BEFORE_AND_AFTER',
        historical_native_failures_unchanged=True)
    return result


def verify_package(root):
    root = Path(root).resolve(strict=True); p,c = parents()
    m = json.loads((root/'source-manifest.json').read_text())
    require(m == expected_manifest(root,p,c), 'entire expected manifest/hash VALUES differ')
    require(json.loads((root/NESTED).read_text()) == nested_manifest(root,c),
            'all75 nested expected hash VALUES differ')
    for name,digest in m['runtime_dependencies'].items(): require(sha(name)==digest,'actual source pin:'+name)
    require(patch.reverse_runner((root/'run_dual.py').read_text()) == (PARENT/'run_dual.py').read_text(),
            'whole runner namespace inverse')
    require(patch.reverse_helper((root/'first_state_inputfree_method.py').read_text()) ==
            (PARENT/'first_state_inputfree_method.py').read_text(),'whole helper intended-delta inverse')
    unchanged = []
    for name in p['runtime_dependencies']:
        path = Path(name)
        if path.is_relative_to(PARENT):
            rel = path.relative_to(PARENT)
            if rel not in (NESTED,Path('run_dual.py'),Path('first_state_inputfree_method.py')):
                require((root/rel).read_bytes()==path.read_bytes(),'unchanged parent bytes:'+str(rel))
                unchanged.append(str(rel))
    # These unused CLIs and all old input collectors remain disabled byte-for-byte.
    require('RUNTIME_REVIEWED=False' in (root/'method-api/first_state_method_transport.py').read_text(),
            'unused old method worker enabled')
    require('RUNTIME_REVIEWED=False' in (root/'method-api/original_damage_worker.py').read_text(),
            'unused base CLI enabled')
    require('RUNTIME_REVIEWED = False' in (root/'method-api/first_state_autodrain_worker.py').read_text(),
            'author autonomous worker enabled')
    return {'status':'DISABLED_AUTODRAIN_METHOD_SOURCE_ONLY_REVIEW_REQUIRED','verified':True,
        'runtime_pins':len(m['runtime_dependencies']),
        'method_runtime_pins':len(nested_manifest(root,c)['runtime_dependencies']),
        'unchanged_parent_files':len(unchanged),'unchanged_parent_file_list':sorted(unchanged),
        'runner_inverse_sha256':patch.RUNNER_SHA,'helper_inverse_sha256':patch.HELPER_SHA,
        'native_ready':False,'new_matched_control_required':True}


def build(output=OUTPUT, *, parent_manifest_sha256=PARENT_SHA):
    require(parent_manifest_sha256 == PARENT_SHA,'requested immutable parent differs')
    p,c = parents()
    for group in (p,c):
        for name,digest in group['runtime_dependencies'].items(): require(sha(name)==digest,'actual parent pin:'+name)
    root = Path(output).absolute(); m = expected_manifest(root,p,c)
    root.mkdir(mode=0o700)
    changed = {Path('run_dual.py'):patch.patch_runner((PARENT/'run_dual.py').read_text()).encode(),
        Path('first_state_inputfree_method.py'):patch.patch_helper((PARENT/'first_state_inputfree_method.py').read_text()).encode(),
        NESTED:dump(nested_manifest(root,c))}
    for name in p['runtime_dependencies']:
        path = Path(name)
        if path.is_relative_to(PARENT):
            rel = path.relative_to(PARENT); write(root/rel,changed[rel] if rel in changed else path.read_bytes())
    for name in NEW_API: write(root/'method-api'/name,(TOOLS/name).read_bytes())
    write(root/'source-manifest.json',dump(m))
    receipt = {**verify_package(root),'manifest_sha256':sha(root/'source-manifest.json')}
    write(root/'build-receipt.json',dump(receipt))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    args=parser.parse_args();print(json.dumps(build(args.output),sort_keys=True))
