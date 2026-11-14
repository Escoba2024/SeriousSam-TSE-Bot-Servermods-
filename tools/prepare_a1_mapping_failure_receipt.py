"""Offline disabled derivation retaining exact mapping failure; no native calls."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-a1-instruction-probe-root-frozen-20261114')
PARENT_SHA='7521e53cec5bdfac3263adef82dd6ed6a2d654ee53259ce5c3505beacfec0c39'
COLLECTOR_SHA='b5f5f6c51fdd5248c9616e7fd1e4c0eaa57219ced7181832cdbae43418861f2f'
BACKEND_SHA='13394a9cb3a69d081f9071861d36a5663367995e4b62c00738d6c4e869ef121a'
RUNNER_SHA='a7b5346f3704a841faf1b67085a5538c6433b23f80f5b538a881d5cc5411a014'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(source,old,new):
    if source.count(old)!=1:
        raise ValueError('nonunique exact parent source anchor')
    return source.replace(old,new,1)


def transform_backend(source):
    if hashlib.sha256(source.encode()).hexdigest()!=BACKEND_SHA:
        raise ValueError('exact original strict backend required')
    source=once(source,'import json,runpy,subprocess,time',
                'import json,runpy,subprocess,time\nfrom a1_mapping_failure_receipt import mapping_mismatch')
    old="   assert [r for r in rows if len(r.split(maxsplit=5))==6 and r.split(maxsplit=5)[5]==str(p)]==pin['mapped_rows']"
    new="""   actual=[r for r in rows if len(r.split(maxsplit=5))==6 and r.split(maxsplit=5)[5]==str(p)]
   if actual!=pin['mapped_rows']:
    raise mapping_mismatch(role,identity,name,p,pin,rows,actual,(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns))"""
    return once(source,old,new)


def transform_runner(source):
    if hashlib.sha256(source.encode()).hexdigest()!=RUNNER_SHA:
        raise ValueError('exact full instruction probe runner required')
    source=once(source,'from a1_trace_scope import InputScope,trace_complete',
                'from a1_trace_scope import InputScope,trace_complete\nfrom a1_mapping_failure_receipt import preserve_mapping_failure')
    return once(source,"  B.verify_modules(role,tuple(rec['identity']),pins[role])", """  try:B.verify_modules(role,tuple(rec['identity']),pins[role])
  except AssertionError as error:
   preserve_mapping_failure(error,E/'module-mapping-failure.json')
   raise""")


def write_json(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def prepare(destination):
    dest=Path(destination).resolve()
    if dest.exists():
        raise ValueError('fresh disabled destination required; old freezes stay immutable')
    if sha(PARENT/'source-manifest.json')!=PARENT_SHA or sha(PARENT/'collector/source-manifest.json')!=COLLECTOR_SHA:
        raise ValueError('reviewed parent manifest changed')
    m=json.loads((PARENT/'source-manifest.json').read_text())
    cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
    for field in('runtime_dependencies',):
        for p,h in m[field].items():
            if sha(p)!=h:raise ValueError('parent runtime pin '+p)
    for p,h in m['diagnostic_source_sha256'].items():
        if sha(PARENT/p)!=h:raise ValueError('parent source pin '+p)
    for p,h in cm['source_pins'].items():
        if sha(p)!=h:raise ValueError('parent collector pin '+p)
    def mapped(path):
        q=Path(path)
        return dest/q.relative_to(PARENT)if q.is_relative_to(PARENT)else q
    def repin(pins):
        return{str(mapped(p)):sha(mapped(p))for p in pins}
    shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    backend=(PARENT/'strict_backend.py').read_text();runner=(PARENT/'run_dual.py').read_text()
    (dest/'strict_backend.py').write_text(transform_backend(backend))
    runner=transform_runner(runner)
    runner=once(runner,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
    runner=once(runner,"PREFIX='ssam-a1-instruction-probe-root-20261114'","PREFIX='ssam-a1-mapping-failure-disabled-20261114'")
    runner=once(runner,"E=BASE/('a1-instruction-probe-'","E=BASE/('a1-mapping-failure-'")
    (dest/'run_dual.py').write_text(runner)
    worker=(dest/'a1_input_worker.py').read_text()
    (dest/'a1_input_worker.py').write_text(once(worker,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'))
    collector=(dest/'collector/a1_original_input_collector.py').read_text()
    collector=once(collector,'RUNTIME_REVIEWED = True','RUNTIME_REVIEWED = False')
    collector=once(collector,str(PARENT/'collector'),str(dest/'collector'))
    (dest/'collector/a1_original_input_collector.py').write_text(collector)
    additions=('a1_mapping_failure_receipt.py','prepare_a1_mapping_failure_receipt.py','test_a1_mapping_failure_receipt.py','test_prepare_a1_mapping_failure_receipt.py')
    for name in additions:
        shutil.copy2(Path(__file__).with_name(name),dest/name)
    cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins'])
    cm['mapping_receipt_derivation']=dict(parent_manifest_sha256=COLLECTOR_SHA,hook_source_unchanged=True,new_native_performed=False)
    write_json(dest/'collector/source-manifest.json',cm)
    m['schema']='disabled-a1-existing-mapping-failure-receipt-v1'
    m['runtime_reviewed']=False;m['runtime_performed']=False
    m['gate']='DISABLED_ROOT_REVIEW_FREEZE_AND_PREFLIGHT_REQUIRED'
    m['collector_source']=str(dest/'collector/a1_original_input_collector.py')
    m['runtime_dependencies']=repin(m['runtime_dependencies'])
    m['runtime_dependencies'][str(dest/additions[0])]=sha(dest/additions[0])
    m['diagnostic_source_sha256']={p:sha(dest/p)for p in m['diagnostic_source_sha256']}
    for name in additions:m['diagnostic_source_sha256'][name]=sha(dest/name)
    m['mapping_receipt_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,
        parent_result_sha256='3d33b79367b718bb9b38acc38bcf4634ed3493c23b566e27d18b464ce957fea5',
        new_process_reads=0,new_memory_reads=0,unchanged_acceptance='exact original selected module mapping rows',
        failure_receipt='private Evidence/module-mapping-failure.json from existing failed comparison',
        accepted_new_mappings=False,new_inputs=0,new_sites=0,bounds_changed=False,
        native_started=False,automatic_retry=False,independent_review='PENDING')
    write_json(dest/'source-manifest.json',m)
    for name in('strict_backend.py','run_dual.py'):
        before=(PARENT/name).read_text();after=(dest/name).read_text()
        (dest/(name+'.mapping-receipt.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='reviewed-parent/'+name,tofile='disabled-failure-receipt/'+name,n=3)))
    receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),runtime_reviewed=False,native_started=False)
    write_json(dest/'MAPPING-FAILURE-HANDOFF.json',dict(**receipt,next='independent review then Root freeze/preflight; unequal mappings still immediately FAIL',qualified=False))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
    print(json.dumps(prepare(p.parse_args().destination),indent=2))
