"""Offline exact JSON-binding correction from the disabled author package."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-owned-sync018-yodeller-disabled-20261114')
PARENT_SHA='4e0a565fde1f040c95dbea89932b6511d6671cee5aa01bf02053dc56fb2a8e35'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh destination required; old FAIL and freezes remain immutable')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('disabled parent manifest')
 old=json.loads((PARENT/'source-manifest.json').read_text())
 for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
  for name,h in old[key].items():
   if sha(PARENT/name if relative else name)!=h:raise ValueError('parent pin '+name)
 tools=Path(__file__).resolve().parent
 before=(PARENT/'owned_sync_capture.py').read_text();after=(tools/'owned_sync_capture.py').read_text()
 if before.count('ports=selected)')!=1 or after!=before.replace('ports=selected)','ports=[list(pair)for pair in selected])'):raise ValueError('exact one-line runtime correction only')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in('owned_sync_capture.py','test_owned_sync_capture.py'):shutil.copy2(tools/name,dest/name)
 m=json.loads(json.dumps(old))
 def mapped(name):
  p=Path(name);return dest/p.relative_to(PARENT)if p.is_relative_to(PARENT)else p
 m['runtime_dependencies']={str(mapped(name)):sha(mapped(name))for name in old['runtime_dependencies']}
 for key in('sources','draft_source_sha256'):m[key]={name:sha(dest/name)for name in old[key]}
 m['json_binding_fix']=dict(parent_manifest_sha256=PARENT_SHA,parent=str(PARENT),plan='f78a1fd',runtime_change='observe_roles ports use JSON-stable lists at source; values and all guards unchanged',historical_failed_result='ae048d5fc51fa6bd564d7cf891a5681c16a644366bdb77b956394765e454fd75',independent_review='PENDING',runtime_performed=False)
 if any(m[k]for k in('runtime_reviewed','runtime_performed','qualified','functional_pass')):raise ValueError('disabled flags required')
 for name in('run-a4.py','owned_sync_capture.py','owned_capture_exec.py'):
  if 'RUNTIME_REVIEWED=False'not in(dest/name).read_text():raise ValueError('disabled execution gate '+name)
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_authorized=False,next='independent review and fresh Root freeze/preflight; at most one explicit run, no automatic retry')
 (dest/'HANDOFF-capture.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
