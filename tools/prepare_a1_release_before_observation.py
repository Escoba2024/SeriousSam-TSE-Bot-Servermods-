"""Offline pinned derivation: release at the planned end before late observation."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

from prepare_a1_mapping_failure_receipt import once,sha,write_json

PARENT=Path('/srv/tse-a1-exact-coverage-root-frozen-20261114')
PARENT_SHA='6534c8b447418f4a2a5310160ff0672b3b41aa742cbc3eb9389bfb648fef919a'
COLLECTOR_SHA='931f7c0dd35f84233cdbe9fd67c2c1d02e53b5f21a00b81e38fa892962ef9936'
RUNNER_SHA='8db8f4212e3ed191fd5cbfa30cd1a333570436d8753976333001f88edc08f26e'
ADDITIONS=('prepare_a1_release_before_observation.py','test_a1_release_before_observation.py',
           'test_prepare_a1_release_before_observation.py')


def transform_runner(source):
    if hashlib.sha256(source.encode()).hexdigest()!=RUNNER_SHA:
        raise ValueError('exact original timing-failure runner required')
    source=once(source,"timing.update(status='IN_PROGRESS',requested_seconds=step['seconds'],preparation_started=last,held_started=None)",
        "timing.update(status='IN_PROGRESS',requested_seconds=step['seconds'],preparation_started=last,held_started=None,held_observations=0)")
    return once(source,"""   now=bounded('input clock')
   for e in endpoints.values():e.verify();e.check_focus()
   bounded('held guard');observe();now=bounded('observation')""","""   now=bounded('input clock')
   if now-start>=step['seconds']:
    phase='capture';before_release();bounded('capture')
    break
   for e in endpoints.values():e.verify();e.check_focus()
   now=bounded('held guard')
   if now-start>=step['seconds']:
    phase='capture';before_release();bounded('capture')
    break
   timing['held_observations']+=1;observe();now=bounded('observation')""")


def disabled_runner(source):
    source=once(source,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
    source=once(source,"PREFIX='ssam-a1-exact-coverage-root-20261114'","PREFIX='ssam-a1-release-deadline-disabled-20261114'")
    return once(source,"E=BASE/('a1-exact-coverage-'","E=BASE/('a1-release-deadline-'")


def prepare(destination):
    dest=Path(destination).resolve()
    if dest.exists():raise ValueError('fresh destination required; previous freezes remain unchanged')
    if sha(PARENT/'source-manifest.json')!=PARENT_SHA or sha(PARENT/'collector/source-manifest.json')!=COLLECTOR_SHA:
        raise ValueError('exact reviewed parent manifests changed')
    m=json.loads((PARENT/'source-manifest.json').read_text())
    cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
    for p,h in m['runtime_dependencies'].items():
        if sha(p)!=h:raise ValueError('parent runtime pin '+p)
    for p,h in m['diagnostic_source_sha256'].items():
        if sha(PARENT/p)!=h:raise ValueError('parent diagnostic pin '+p)
    for p,h in cm['source_pins'].items():
        if sha(p)!=h:raise ValueError('parent collector pin '+p)
    old=(PARENT/'run_dual.py').read_text();runner=disabled_runner(transform_runner(old))
    def mapped(path):
        q=Path(path);return dest/q.relative_to(PARENT)if q.is_relative_to(PARENT)else q
    def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
    shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (dest/'run_dual.py').write_text(runner)
    for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
    worker=(dest/'a1_input_worker.py').read_text()
    (dest/'a1_input_worker.py').write_text(once(worker,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'))
    collector=(dest/'collector/a1_original_input_collector.py').read_text()
    collector=once(collector,'RUNTIME_REVIEWED = True','RUNTIME_REVIEWED = False')
    collector=once(collector,str(PARENT/'collector'),str(dest/'collector'))
    (dest/'collector/a1_original_input_collector.py').write_text(collector)
    cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins'])
    cm['release_deadline_derivation']=dict(parent_manifest_sha256=COLLECTOR_SHA,hook_source_unchanged=True,native_performed=False)
    write_json(dest/'collector/source-manifest.json',cm)
    m['schema']='disabled-a1-release-before-late-observation-v1'
    m['runtime_reviewed']=False;m['runtime_performed']=False
    m['gate']='DISABLED_INDEPENDENT_REVIEW_ROOT_FREEZE_PREFLIGHT_REQUIRED'
    m['collector_source']=str(dest/'collector/a1_original_input_collector.py')
    m['runtime_dependencies']=repin(m['runtime_dependencies'])
    m['diagnostic_source_sha256']={p:sha(dest/p)for p in m['diagnostic_source_sha256']}
    for name in ADDITIONS:m['diagnostic_source_sha256'][name]=sha(dest/name)
    m['release_deadline_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,
        parent_native_result_sha256='f66266f97f9eadf008f42aa557e1a3aa2c25778d7c6ed9a04efbb76a0392bf74',
        prospective_checks='planned input end before and after existing held guards; existing post-observe check retained',
        unchanged_hard_overrun_seconds=.25,unchanged_ack_gain_clock_guard_capture_release=True,
        held_observations='number of actual started held observe calls; zero stays zero; no fabricated frame',
        cp_after_release_observer_unchanged=True,collector_hooks_inputs_bounds_unchanged=True,
        native_started=False,automatic_retry=False,independent_review='PENDING')
    write_json(dest/'source-manifest.json',m)
    (dest/'release-before-observation.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),runner.splitlines(True),fromfile='reviewed-parent/run_dual.py',tofile='disabled-release-deadline/run_dual.py',n=3)))
    receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),
        diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),runtime_reviewed=False,native_started=False)
    write_json(dest/'RELEASE-DEADLINE-HANDOFF.json',dict(**receipt,qualified=False,
        next='independent review then Root freeze/preflight; historical FAIL remains FAIL; one unchanged NoFire diagnostic'))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
    print(json.dumps(prepare(p.parse_args().destination),indent=2))
