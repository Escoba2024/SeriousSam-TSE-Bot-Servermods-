"""Offline disabled fork; change only admission readiness/raw receipts."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-owned-sync018-latejoin-disabled-20261114')
PARENT_SHA='0d6b16609f7d4356a6f127e219f23e9f61b2363dac1a169c1b09986337180920'
ADDITIONS=('ownns_latejoin_runtime.py','test_latejoin_nine_ready.py','prepare_latejoin_nine_ready.py','test_prepare_latejoin_nine_ready.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate_adapter(before,after):
 old,new=ast.parse(before),ast.parse(after)
 def methods(tree):return next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='LatejoinRuntime')
 a,b=methods(old),methods(new)
 if {n.name for n in b.body if isinstance(n,ast.FunctionDef)}-{n.name for n in a.body if isinstance(n,ast.FunctionDef)}!={'admission_frames'}:raise ValueError('only new admission readiness method allowed')
 for cls in (a,b):cls.body=[n for n in cls.body if not(isinstance(n,ast.FunctionDef)and n.name in('admission','admission_frames'))]
 if ast.dump(old)!=ast.dump(new):raise ValueError('non-admission adapter source changed')


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh destination required; failed parent/evidence remains immutable')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact prior disabled latejoin parent')
 m=json.loads((PARENT/'source-manifest.json').read_text())
 for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
  for name,h in m[key].items():
   if sha(PARENT/name if relative else name)!=h:raise ValueError('inherited pin mismatch: '+name)
 for key in ('runtime_reviewed','runtime_performed','qualified','functional_pass','a4_accepted'):
  if m[key]is not False:raise ValueError('disabled parent contract')
 tools=Path(__file__).resolve().parent;old=(PARENT/'ownns_latejoin_runtime.py').read_text();new=(tools/'ownns_latejoin_runtime.py').read_text();validate_adapter(old,new)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(tools/name,dest/name)
 controller=(dest/'run-a4.py').read_text();oldprefix='own-latejoin018-yodeller-';newprefix='own-latejoin018-nine-ready-yodeller-'
 if controller.count(oldprefix)!=2:raise ValueError('exact service/evidence namespace anchors')
 (dest/'run-a4.py').write_text(controller.replace(oldprefix,newprefix));ast.parse((dest/'run-a4.py').read_text())
 (dest/'nine-ready-runtime.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='disabled-latejoin-parent/ownns_latejoin_runtime.py',tofile='disabled-nine-ready/ownns_latejoin_runtime.py')))
 def mapped(path):
  path=Path(path);return dest/path.relative_to(PARENT)if path.is_relative_to(PARENT)else path
 m['runtime_dependencies']={str(mapped(p)):sha(mapped(p))for p in m['runtime_dependencies']}
 m.update(scope='DISABLED_PRIVATE_OWNNS_018_LATEJOIN_COMPLETE_NINE_READINESS_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,a4_accepted=False)
 m['nine_slot_readiness_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,changed_runtime='ownns_latejoin_runtime.py admission only',native_performed=False,
  admission_deadline_seconds=30,original_launch_retry=False,new_originallaunch=False,round_wait_seconds=.2,existing_frame_predicate_unchanged=True,
  pending='only Original initially lacks slot8; all old bindings unchanged',raw_receipts='exclusive0600 before further validations',historical_run_remains='FAIL')
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_latejoin=False,reference='PENDING independent review and Root-only fresh freeze/retest')
 m.pop('root_freeze',None)
 source_names=set(m['sources'])|set(ADDITIONS)|{'nine-ready-runtime.diff'}
 m['sources']={name:sha(dest/name)for name in sorted(source_names)}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 for name in ('run-a4.py','owned_sync_capture.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py'):
  if 'RUNTIME_REVIEWED=False'not in(dest/name).read_text():raise ValueError('disabled runtime gate '+name)
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),runtime_performed=False,qualified=False,functional_pass=False,a4_accepted=False)
 (dest/'HANDOFF-nine-ready.json').write_text(json.dumps(dict(**receipt,next='Root review/fresh freeze; no automatic native retry; earlier HANDOFF files are retained parent history'),indent=2)+'\n')
 return receipt


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',required=True,type=Path)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
