"""Offline exact FD-readlink correction from the immutable JSON author."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-owned-sync018-json-binding-disabled-20261114')
PARENT_SHA='dbf38d5df34c33831342209f767fdf28bfac58b1561dc24ee26dde17466e9fb8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def corrected(source):
 edits=[
  ("   target=str(f.readlink());match=re.fullmatch(r'socket:\\[(\\d+)\\]',target)",
   "   try:target=str(f.readlink())\n   except FileNotFoundError:continue\n   match=re.fullmatch(r'socket:\\[(\\d+)\\]',target)"),
  ("   match=re.fullmatch(r'socket:\\[(\\d+)\\]',str(f.readlink()))",
   "   try:target=str(f.readlink())\n   except FileNotFoundError:continue\n   match=re.fullmatch(r'socket:\\[(\\d+)\\]',target)")]
 for before,after in edits:
  if source.count(before)!=1:raise ValueError('exact historical readlink anchor')
  source=source.replace(before,after,1)
 return source


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh destination required; old FAIL and freezes remain immutable')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('disabled JSON parent manifest')
 old=json.loads((PARENT/'source-manifest.json').read_text())
 for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
  for n,h in old[key].items():
   if sha(PARENT/n if relative else n)!=h:raise ValueError('parent pin '+n)
 tools=Path(__file__).resolve().parent
 if (tools/'owned_sync_capture.py').read_text()!=corrected((PARENT/'owned_sync_capture.py').read_text()):raise ValueError('only two individual readlink catches allowed')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for n in('owned_sync_capture.py','test_owned_capture_fd_churn.py'):shutil.copy2(tools/n,dest/n)
 m=json.loads(json.dumps(old))
 def mapped(n):
  p=Path(n);return dest/p.relative_to(PARENT)if p.is_relative_to(PARENT)else p
 m['runtime_dependencies']={str(mapped(n)):sha(mapped(n))for n in old['runtime_dependencies']}
 for key in('sources','draft_source_sha256'):m[key]={n:sha(dest/n)for n in list(old[key])+['test_owned_capture_fd_churn.py']}
 m['fd_churn_fix']=dict(parent_manifest_sha256=PARENT_SHA,parent=str(PARENT),plan='7fd2180',runtime_change='Only FileNotFoundError from each existing individual FD readlink is skipped; unchanged full socket and role binding',historical_failed_result='75eb5fa3333f7962463f58df98030336f3e5538e038094689b20f14cd783880e',independent_review='PENDING',runtime_performed=False,automatic_retry=False)
 if any(m[k]for k in('runtime_reviewed','runtime_performed','qualified','functional_pass')):raise ValueError('disabled flags required')
 for n in('run-a4.py','owned_sync_capture.py','owned_capture_exec.py'):
  if 'RUNTIME_REVIEWED=False'not in(dest/n).read_text():raise ValueError('disabled execution gate '+n)
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_authorized=False,next='independent review; Root decides a separately justified next diagnostic; no automatic retry')
 (dest/'HANDOFF-capture.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
