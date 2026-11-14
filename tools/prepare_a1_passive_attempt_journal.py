"""Disabled fork of closed A1 attempt; no Xlib or game process is loaded."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
from a1_passive_xrecord import method_fingerprints

PARENT=Path('/srv/tse-a1-passive-xrecord-root-frozen-20261114')
PARENT_SHA='c41b8f20c88eac6a7dc2a135d75580c29b99578e38819ba83ced0244386ce04f'
METHOD_RESULT=Path('/srv/tse-cecil-rollout-evidence-20261114/a1-passive-metadata-method-root-20261114/result.json')
METHOD_SHA='81c402edfb083d957daa21b12d9901303fea97204c8b661506d2a1fce9dd8135'
CORE_FILES=('xrecord_core_method.py','xrecord_core_native.py','xrecord_core_worker.py','xrecord_core_process.py')
COPIES=('a1_passive_xrecord.py','test_a1_passive_xrecord.py','test_a1_passive_attempt_journal.py','prepare_a1_passive_attempt_journal.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact single source anchor required: '+old)
 return text.replace(old,new,1)


def prepare(destination):
 dest=Path(destination).resolve();source=Path(__file__).resolve().parent
 if dest.exists():raise ValueError('fresh disabled destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('closed parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
 for pins,base in((m['runtime_dependencies'],Path('/')),(m['diagnostic_source_sha256'],PARENT),(cm['source_pins'],Path('/'))):
  for path,h in pins.items():
   if sha(base/path)!=h:raise ValueError('closed parent source pin changed: '+path)
 if sha(METHOD_RESULT)!=METHOD_SHA:raise ValueError('actual own167 method result changed')
 native=json.loads(METHOD_RESULT.read_text())
 if native['status']!='PASS_OWN_XRECORD_METADATA_BINDING_ONLY'or native['errors']or not native['normal_closes']:raise ValueError('actual method normal cleanup missing')
 expected=m['passive_xrecord']['method_fingerprints']
 if method_fingerprints(source,PARENT/'passive-core')!=expected:raise ValueError('method fingerprint changed; cannot inherit qualification')
 if m['passive_xrecord']['binding_qualification']['fingerprints']!=expected or native['native']['fingerprints']!=expected:raise ValueError('method fingerprint qualification differs')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in COPIES:shutil.copy2(source/name,dest/name)
 for name in('run_dual.py','a1_input_worker.py','a1_passive_xrecord_worker.py'):
  q=dest/name;q.write_text(once(q.read_text(),'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'))
 main=dest/'run_dual.py';main.write_text(once(once(main.read_text(),"PREFIX='ssam-a1-passive-xrecord-root-20261114'","PREFIX='ssam-a1-passive-attempt-disabled-20261114'"),"E=BASE/('a1-passive-xrecord-'","E=BASE/('a1-passive-attempt-'"))
 c=dest/'collector/a1_original_input_collector.py'
 c.write_text(once(once(c.read_text(),'RUNTIME_REVIEWED = True','RUNTIME_REVIEWED = False'),str(PARENT/'collector'),str(dest/'collector')))
 def mapped(path):
  p=Path(path);return dest/p.relative_to(PARENT)if p.is_relative_to(PARENT)else p
 def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
 def write(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
 cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins']);write(dest/'collector/source-manifest.json',cm)
 m.update(schema='DISABLED_A1_PASSIVE_ATTEMPT_RECEIPT_V1',runtime_reviewed=False,runtime_performed=False,gate='DISABLED_ATTEMPT_RECEIPT_REVIEW_ROOT_FREEZE_REQUIRED',collector_source=str(dest/'collector/a1_original_input_collector.py'))
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 m['diagnostic_source_sha256']={name:sha(dest/name)for name in m['diagnostic_source_sha256']}
 for name in COPIES:m['diagnostic_source_sha256'][name]=sha(dest/name)
 m['attempt_receipt_derivation']=dict(parent_manifest_sha256=PARENT_SHA,parent_native_result_remains='FAIL',changes='bounded in-memory attempted metadata reserved before native path; exclusive cleanup journal',journal='controller-emission-attempts.json',attempts_max=96,valid_emissions_guard_unchanged=True,method_ast_unchanged=True,actual_method_result_sha256=METHOD_SHA,additional_native_reads=0,additional_clock_reads=0,additional_inputs=0,warmup=False,native_performed=False,automatic_retry=False)
 write(dest/'source-manifest.json',m)
 (dest/'attempt-receipt-source.diff').write_text(''.join(difflib.unified_diff((PARENT/'a1_passive_xrecord.py').read_text().splitlines(True),(dest/'a1_passive_xrecord.py').read_text().splitlines(True),fromfile='closed-A1/a1_passive_xrecord.py',tofile='disabled-attempt/a1_passive_xrecord.py')))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),runtime_reviewed=False,method_qualification_reused=True,native_performed=False)
 write(dest/'ATTEMPT-HANDOFF.json',receipt);return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);print(json.dumps(prepare(p.parse_args().destination),indent=2))
