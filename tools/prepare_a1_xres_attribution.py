"""Prepare fresh DISABLED current-XRes/lifecycle NoFire evidence fork only."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-a1-xtest-preparation-root-frozen-20261114')
PARENT_SHA='71b9c896e068e473d0fd8317871b0fa3ccc5f4a43828c87e8b1b09619c60170a'
PID_PARENT=Path('/srv/tse-own-xres-pid-v2-root-frozen-20261114')
PID_PARENT_SHA='09be57b6b0eec29a598b68a612376ebdb4939857b7fbc69342ecbdb2e924f687'
PID_RESULT=Path('/srv/tse-cecil-rollout-evidence-20261114/own-xres-pid-v2-method-root-20261114/method-result.json')
PID_RESULT_SHA='18d16f195c64d2d5f6564b0166422d63aa72011c4dcd71284f05d1d9a1afc953'
CORE_FILES=('xrecord_core_method.py','xrecord_core_native.py','xrecord_core_worker.py','xrecord_core_process.py')
ADAPTER_FILES=('a1_xres_attribution.py','a1_xres_attribution_worker.py','a1_xres_attribution_evidence.py')
TEST_FILES=('test_a1_xres_attribution.py','test_a1_xres_attribution_worker.py','test_a1_xres_attribution_evidence.py','test_a1_xres_lifecycle_method.py','test_prepare_a1_xres_lifecycle.py')
PID_FILES=('xres_pid_method.py','xres_pid_worker.py','xres_pid_controller.py')
SOURCE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact lifecycle fork anchor changed: '+old)
 return text.replace(old,new,1)


def verify_parents():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA or sha(PID_PARENT/'source-manifest.json')!=PID_PARENT_SHA:raise ValueError('reviewed lifecycle parent changed')
 m=json.loads((PARENT/'source-manifest.json').read_bytes());cm=json.loads((PARENT/'collector/source-manifest.json').read_bytes());pm=json.loads((PID_PARENT/'source-manifest.json').read_bytes())
 for pins,base in((m['runtime_dependencies'],Path('/')),(m['diagnostic_source_sha256'],PARENT),(cm['source_pins'],Path('/')),(pm['files'],PID_PARENT),(pm['library_sha256'],Path('/')),(pm['header_sha256'],Path('/')),(pm['evidence_sha256'],Path('/'))):
  for p,h in pins.items():
   if sha(base/p)!=h:raise ValueError('inherited lifecycle source/external pin changed: '+p)
 if sha(PID_RESULT)!=PID_RESULT_SHA:raise ValueError('qualified public XRes result changed')
 result=json.loads(PID_RESULT.read_bytes())
 if result['status']!='PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY'or result['errors']or result['qualified']is not False:raise ValueError('public XRes metadata qualification absent')
 return m,cm,pm


def copy_dependencies(dest):
 for name in ADAPTER_FILES+('a1_xres_lifecycle_method.py','prepare_a1_xres_attribution.py','prepare_a1_xres_lifecycle_method.py')+TEST_FILES:shutil.copy2(SOURCE/name,dest/name)
 for name in PID_FILES:shutil.copy2(PID_PARENT/name,dest/name)


def package_fingerprints(dest):
 # Pure AST/hash computation only. Never imports generated controllers/native.
 from a1_xres_attribution import fingerprints
 return fingerprints(dest,dest/'passive-core')


def validate_qualification(row,expected):
 if not isinstance(row,dict)or row.get('status')!='PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY'or row.get('errors')!=[]:raise ValueError('actual lifecycle method result absent')
 if any(row.get(k)is not True for k in('no_inputs','normal_closes','lifecycle_started','lifecycle_died','exactly_two_snapshots','driver_requests_bound','peer_interval_unknown','display_absent')):raise ValueError('actual lifecycle method proof incomplete')
 if row.get('fingerprints')!=expected or row.get('inputs_emitted')!=0 or row.get('tse_started')is not False or row.get('wine_started')is not False or row.get('frida_started')is not False:raise ValueError('method source/no-input scope differs')
 children=row.get('children',{})
 if set(children)!={'display','driver','peer','recorder'}or any(c.get('closed')is not True or c.get('reaped')is not True or c.get('forced')is not False or c.get('errors')!=[]for c in children.values()):raise ValueError('actual four role normal cleanup absent')
 return row


def prepare(destination,qualification=None):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh disabled destination required')
 m,cm,pm=verify_parents();shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));dest.chmod(0o700);copy_dependencies(dest)
 changed=[]
 for name in('run_dual.py','a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','collector/a1_original_input_collector.py'):
  p=dest/name;text=p.read_text();old='RUNTIME_REVIEWED = True'if'RUNTIME_REVIEWED = True'in text else'RUNTIME_REVIEWED=True';text=once(text,old,old.replace('True','False'))
  if name=='run_dual.py':
   text=once(text,'from a1_passive_xrecord import PassiveRecorder,instrument_transport,require_method_qualification','from a1_xres_attribution import PassiveRecorder,instrument_transport,require_method_qualification')
   text=once(text,"PREFIX='ssam-a1-xtest-preparation-root-20261114'","PREFIX='ssam-a1-xres-lifecycle-disabled-20261114'")
   text=once(text,"E=BASE/('a1-xtest-preparation-'","E=BASE/('a1-xres-lifecycle-'")
  if name.startswith('collector/'):text=once(text,str(PARENT/'collector'),str(dest/'collector'))
  p.write_text(text);changed.append(name)
 def mapped(p):
  p=Path(p);return dest/p.relative_to(PARENT)if p.is_relative_to(PARENT)else p
 def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
 cm['source_pins']=repin(cm['source_pins']);cm['runtime_reviewed']=False;write(dest/'collector/source-manifest.json',cm)
 m.update(schema='DISABLED_A1_XRES_RECORD_LIFECYCLE_V1',runtime_reviewed=False,runtime_performed=False,gate='DISABLED_LIFECYCLE_METHOD_AND_ROOT_REVIEW_REQUIRED',collector_source=str(dest/'collector/a1_original_input_collector.py'))
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 for name in ADAPTER_FILES+PID_FILES:m['runtime_dependencies'][str(dest/name)]=sha(dest/name)
 m['diagnostic_source_sha256']={name:sha(dest/name)for name in m['diagnostic_source_sha256']}
 for name in ADAPTER_FILES+TEST_FILES+('a1_xres_lifecycle_method.py','prepare_a1_xres_attribution.py','prepare_a1_xres_lifecycle_method.py'):m['diagnostic_source_sha256'][name]=sha(dest/name)
 m['xres_attribution']=dict(allowed_scope='A1_154',abi_layout=pm['abi_layout'],library_sha256=pm['library_sha256'],header_sha256=pm['header_sha256'],evidence_sha256=pm['evidence_sha256'],snapshots=2,context_bases_max=32,queries_max=34,metadata_bytes_max=262144,pid_method_sha256=PID_RESULT_SHA,no_snapshot_only_fallback=True,original_core_byte_identical=True,old_u_attributed=False,gain_fixed=False)
 for pins in(pm['library_sha256'],pm['header_sha256'],pm['evidence_sha256']):m['runtime_dependencies'].update(pins)
 fps=package_fingerprints(dest);m['passive_xrecord']['xres_lifecycle_qualification']=None
 if qualification is not None:
  path=Path(qualification).resolve();row=validate_qualification(json.loads(path.read_bytes()),fps);m['passive_xrecord']['xres_lifecycle_qualification']=row;m['runtime_dependencies'][str(path)]=sha(path)
 m['xres_lifecycle_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,public_pid_parent_manifest_sha256=PID_PARENT_SHA,native_performed=False,automatic_retry=False,additional_inputs=0,cp_ack_gain_eps_deadlines_unchanged=True,changed_runtime_files=changed,new_runtime_files=list(ADAPTER_FILES+PID_FILES),lifecycle_method_pending=qualification is None,qualified=False,a1_pass=False)
 write(dest/'source-manifest.json',m)
 (dest/'xres-lifecycle-source.diff').write_text(''.join(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),(dest/name).read_text().splitlines(True),fromfile='parent/'+name,tofile='disabled/'+name))for name in changed))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),fingerprints=fps,runtime_reviewed=False,qualified=False,method_qualification_pending=qualification is None,native_performed=False)
 write(dest/'XRES-LIFECYCLE-HANDOFF.json',receipt)
 for p in dest.rglob('*'):
  if p.is_file():p.chmod(0o600)
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);p.add_argument('--qualification',type=Path);args=p.parse_args();print(json.dumps(prepare(args.destination,args.qualification),indent=2))
