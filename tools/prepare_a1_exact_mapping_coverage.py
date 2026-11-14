"""Offline A1 fork using the exact historically reviewed mapping helper."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

from prepare_a1_mapping_failure_receipt import once,sha,write_json

PARENT=Path('/srv/tse-a1-mapping-failure-root-frozen-20261114')
PARENT_SHA='bd83f6e3ad7320e7eed5b9059ec1d107dc295dd60168803eb2cef78f607750ae'
BACKEND_SHA='ea5fd332cbf07f9ebfd52e164a6cd8789b0cd5774e5b5277cbc6863fb1c6aa3d'
COLLECTOR_SHA='9070b44ff3b50e6c3e7eaf3db393ec36c8f9cc3dae5fe8004f4ee7d057f1ca6d'
HISTORICAL=Path('/srv/tse-milestone-a-evidence-20261111/a3-damage013-normalized-root-frozen-20261112')
HISTORICAL_MANIFEST_SHA='d13a063c8fb6f51cd1706c2275b6d50a4eafc143a6420606ca052235e204acd3'
HELPER_SHA='e2c194c1dc06ea463317be074d153d6679564e173fa9ef97bf1a3bfa53a93064'
HISTORICAL_TEST_SHA='7fe77063bb6aa084786a86a2df781c9884cea42d1c775494d4fbcf42d2e97b00'
ADDITIONS=('mapped_rows.py','prepare_a1_exact_mapping_coverage.py',
           'test_exact_module_mapping_coverage.py','test_a1_exact_mapping_backend.py',
           'test_prepare_a1_exact_mapping_coverage.py')


def transform_backend(source):
    if hashlib.sha256(source.encode()).hexdigest()!=BACKEND_SHA:
        raise ValueError('exact same-read failure-receipt backend required')
    source=once(source,'from a1_mapping_failure_receipt import mapping_mismatch',
                'from a1_mapping_failure_receipt import mapping_mismatch\nfrom mapped_rows import canonical_mapped_rows')
    return once(source,"   if actual!=pin['mapped_rows']:","""   try:equal_coverage=canonical_mapped_rows(actual)==canonical_mapped_rows(pin['mapped_rows'])
   except ValueError:equal_coverage=False
   if not equal_coverage:""")


def prepare(destination):
    dest=Path(destination).resolve()
    if dest.exists():raise ValueError('fresh destination required; old results/freezes unchanged')
    if sha(PARENT/'source-manifest.json')!=PARENT_SHA or sha(PARENT/'collector/source-manifest.json')!=COLLECTOR_SHA:
        raise ValueError('exact reviewed A1 parent manifests changed')
    if sha(HISTORICAL/'source-manifest.json')!=HISTORICAL_MANIFEST_SHA:
        raise ValueError('historical reviewed manifest changed')
    if sha(HISTORICAL/'mapped_rows.py')!=HELPER_SHA or sha(Path(__file__).with_name('mapped_rows.py'))!=HELPER_SHA:
        raise ValueError('byte-identical reviewed helper required')
    if sha(HISTORICAL/'test_mapped_rows.py')!=HISTORICAL_TEST_SHA:
        raise ValueError('historical regression source changed')
    history=json.loads((HISTORICAL/'source-manifest.json').read_text())
    fixture='actual-module-rows-private.json'
    if sha(HISTORICAL/fixture)!=history['sources'][fixture]:raise ValueError('historical private fixture changed')
    m=json.loads((PARENT/'source-manifest.json').read_text())
    cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
    for p,h in m['runtime_dependencies'].items():
        if sha(p)!=h:raise ValueError('parent runtime pin '+p)
    for p,h in m['diagnostic_source_sha256'].items():
        if sha(PARENT/p)!=h:raise ValueError('parent diagnostic pin '+p)
    for p,h in cm['source_pins'].items():
        if sha(p)!=h:raise ValueError('parent collector pin '+p)
    def mapped(path):
        q=Path(path);return dest/q.relative_to(PARENT)if q.is_relative_to(PARENT)else q
    def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
    shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
    for name in('test_mapped_rows.py',fixture):shutil.copy2(HISTORICAL/name,dest/name)
    old=(PARENT/'strict_backend.py').read_text();new=transform_backend(old)
    (dest/'strict_backend.py').write_text(new)
    runner=(dest/'run_dual.py').read_text()
    runner=once(runner,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
    runner=once(runner,"PREFIX='ssam-a1-mapping-failure-root-20261114'","PREFIX='ssam-a1-exact-coverage-disabled-20261114'")
    runner=once(runner,"E=BASE/('a1-mapping-failure-'","E=BASE/('a1-exact-coverage-'")
    (dest/'run_dual.py').write_text(runner)
    worker=(dest/'a1_input_worker.py').read_text()
    (dest/'a1_input_worker.py').write_text(once(worker,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'))
    collector=(dest/'collector/a1_original_input_collector.py').read_text()
    collector=once(collector,'RUNTIME_REVIEWED = True','RUNTIME_REVIEWED = False')
    collector=once(collector,str(PARENT/'collector'),str(dest/'collector'))
    (dest/'collector/a1_original_input_collector.py').write_text(collector)
    cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins'])
    cm['exact_coverage_derivation']=dict(parent_manifest_sha256=COLLECTOR_SHA,hook_source_unchanged=True,native_performed=False)
    write_json(dest/'collector/source-manifest.json',cm)
    m['schema']='disabled-a1-reviewed-exact-module-coverage-v1'
    m['runtime_reviewed']=False;m['runtime_performed']=False
    m['gate']='DISABLED_INDEPENDENT_REVIEW_ROOT_FREEZE_PREFLIGHT_REQUIRED'
    m['collector_source']=str(dest/'collector/a1_original_input_collector.py')
    m['runtime_dependencies']=repin(m['runtime_dependencies'])
    m['runtime_dependencies'][str(dest/'mapped_rows.py')]=HELPER_SHA
    m['diagnostic_source_sha256']={p:sha(dest/p)for p in m['diagnostic_source_sha256']}
    for name in ADDITIONS+('test_mapped_rows.py',fixture):m['diagnostic_source_sha256'][name]=sha(dest/name)
    m['exact_coverage_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,
        historical_helper=str(HISTORICAL/'mapped_rows.py'),historical_helper_sha256=HELPER_SHA,
        historical_manifest_sha256=HISTORICAL_MANIFEST_SHA,historical_helper_byte_identical=True,
        original_pins_unchanged=True,additional_process_reads=0,additional_memory_reads=0,
        comparison='exact virtual address domain + permissions/device/inode/path/affine file offset; only adjacent partition boundaries ignored',
        private_failure_receipt_retained=True,malformed_coverage_is_failure=True,
        no_frida_exception=True,no_rebaseline=True,inputs_hooks_bounds_changed=False,
        parent_native_result_unchanged='FAIL',native_started=False,automatic_retry=False,independent_review='PENDING')
    write_json(dest/'source-manifest.json',m)
    (dest/'exact-coverage-backend.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='reviewed-failure-parent/strict_backend.py',tofile='disabled-exact-coverage/strict_backend.py',n=3)))
    receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),runtime_reviewed=False,native_started=False)
    write_json(dest/'EXACT-COVERAGE-HANDOFF.json',dict(**receipt,next='independent review then Root freeze/preflight; one NoFire diagnostic, no automatic retry',qualified=False))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
    print(json.dumps(prepare(p.parse_args().destination),indent=2))
