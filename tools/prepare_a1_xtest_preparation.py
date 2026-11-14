"""Build one fresh DISABLED ReleaseSafeAttempt metadata-preparation fork."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
from a1_passive_xrecord import method_fingerprints

PARENT=Path('/srv/tse-a1-passive-attempt-release-safe-disabled-20261114')
PARENT_SHA='f1cbd265f9b5ade97b8ec27748370b523f877524a6302118bf74fad3e8b18b18'
METHOD_RESULT=Path('/srv/tse-cecil-rollout-evidence-20261114/own-xrecord-cold-warm-root-20261114/method-result.json')
METHOD_SHA='45adbbad603ab49fde34e3b20f51c8b38ba62a0cb403937a27d15458ccd7a7d2'
METADATA_RESULT=Path('/srv/tse-cecil-rollout-evidence-20261114/a1-passive-metadata-method-root-20261114/result.json')
METADATA_SHA='81c402edfb083d957daa21b12d9901303fea97204c8b661506d2a1fce9dd8135'
CORE_FILES=('xrecord_core_method.py','xrecord_core_native.py','xrecord_core_worker.py','xrecord_core_process.py')
COPIES=('a1_passive_xrecord.py','test_a1_passive_xrecord.py','test_a1_xtest_preparation.py','prepare_a1_xtest_preparation.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact metadata preparation anchor changed: '+old)
 return text.replace(old,new,1)


def prepare(destination):
 dest=Path(destination).resolve();source=Path(__file__).resolve().parent
 if dest.exists():raise ValueError('fresh disabled destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('ReleaseSafeAttempt parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
 for pins,base in((m['runtime_dependencies'],Path('/')),(m['diagnostic_source_sha256'],PARENT),(cm['source_pins'],Path('/'))):
  for path,h in pins.items():
   if sha(base/path)!=h:raise ValueError('ReleaseSafeAttempt parent source pin changed: '+path)
 if sha(METHOD_RESULT)!=METHOD_SHA or sha(METADATA_RESULT)!=METADATA_SHA:raise ValueError('actual own method result changed')
 method=json.loads(METHOD_RESULT.read_text());metadata=json.loads(METADATA_RESULT.read_text())
 required=('start_of_data','end_of_data','request_client_bound','record_context_freed','record_data_freed','connections_closed','recorder_closed','driver_closed','display_closed','children_reaped')
 if method['status']!='PASS_METHOD_COLD_WARM_LIBRARY_REQUESTS_ONLY'or method['errors']or any(method[k]is not True for k in required)or method['xtest_version']!=[2,2]or method['query_positions']!=[[412,300],[424,300]]:raise ValueError('actual cold/warm method proof incomplete')
 expected=m['passive_xrecord']['method_fingerprints']
 if metadata['status']!='PASS_OWN_XRECORD_METADATA_BINDING_ONLY'or metadata['errors']or not metadata['normal_closes']or metadata['native']['fingerprints']!=expected:raise ValueError('actual metadata qualification differs')
 if method_fingerprints(source,PARENT/'passive-core')!=expected or m['passive_xrecord']['binding_qualification']['fingerprints']!=expected:raise ValueError('qualified metadata/Core fingerprint changed')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));dest.chmod(0o700)
 for name in COPIES:shutil.copy2(source/name,dest/name)
 main=dest/'run_dual.py';main.write_text(once(once(main.read_text(),"PREFIX='ssam-a1-passive-attempt-disabled-20261114'","PREFIX='ssam-a1-xtest-preparation-disabled-20261114'"),"E=BASE/('a1-passive-attempt-'","E=BASE/('a1-xtest-preparation-'"))
 c=dest/'collector/a1_original_input_collector.py';c.write_text(once(c.read_text(),str(PARENT/'collector'),str(dest/'collector')))
 def mapped(path):
  p=Path(path);return dest/p.relative_to(PARENT)if p.is_relative_to(PARENT)else p
 def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
 def write(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
 cm['source_pins']=repin(cm['source_pins']);write(dest/'collector/source-manifest.json',cm)
 m.update(schema='DISABLED_A1_PREARM_XTEST_METADATA_V1',runtime_reviewed=False,runtime_performed=False,gate='DISABLED_PREARM_XTEST_METADATA_ROOT_REVIEW_REQUIRED',collector_source=str(c))
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 m['diagnostic_source_sha256']={name:sha(dest/name)for name in m['diagnostic_source_sha256']}
 for name in COPIES:m['diagnostic_source_sha256'][name]=sha(dest/name)
 m['xtest_preparation_derivation']=dict(parent_manifest_sha256=PARENT_SHA,cold_warm_method_result_sha256=METHOD_SHA,metadata_method_result_sha256=METADATA_SHA,public_function='XTestQueryExtension',same_existing_transport=True,before_recorder_arm=True,xsync_before_arm=True,version=[2,2],additional_inputs=0,warmup_input=False,emission_guard_unchanged=True,cp_ack_gain_eps_deadlines_unchanged=True,method_ast_unchanged=True,native_performed=False,automatic_retry=False,a1_pass=False,qualified=False)
 for name in('run_dual.py','a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','collector/a1_original_input_collector.py'):
  text=(dest/name).read_text()
  if 'RUNTIME_REVIEWED=False'not in text and'RUNTIME_REVIEWED = False'not in text:raise ValueError('disabled source gate changed: '+name)
 write(dest/'source-manifest.json',m)
 changes=('a1_passive_xrecord.py','run_dual.py','collector/a1_original_input_collector.py')
 (dest/'xtest-preparation-source.diff').write_text(''.join(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),(dest/name).read_text().splitlines(True),fromfile='release-safe/'+name,tofile='disabled-prearm/'+name))for name in changes))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),runtime_reviewed=False,method_qualification_reused=True,cold_warm_method_sha256=METHOD_SHA,native_performed=False)
 write(dest/'XTEST-PREPARATION-HANDOFF.json',receipt)
 for path in dest.rglob('*'):
  if path.is_file():path.chmod(0o600)
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);print(json.dumps(prepare(p.parse_args().destination),indent=2))
