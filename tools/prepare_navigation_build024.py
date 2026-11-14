"""Prepare exactly one DISABLED Build024/RedStation600s arm; no runtime imports."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-nav20-023-red600-disabled-20261114')
PARENT_SHA='51d72a2cf233ff87d2f0cac0d3ad2a532f6f287e6ef62bd154b43e6e4ba8e5e8'
OLD_BUILD=Path('/srv/tse-milestone-a-build-023-20261114')
BUILD=Path('/srv/tse-milestone-a-build-024-20261114')
BUILD_SHA='8903d7db0437f8c9ff0f71e056523be35d9c6ef75c165e2f0491cb67818691c9'
SOURCE_COMMIT='100bda43eb46c7d671d71b7a50fae673a9e4406e'
DLL=BUILD/'Sources/Game/GameMP.dll'
DLL_SHA='192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c'
DLL_SIZE=438272
SOURCE_TREE='a1c049f440ed1600a718c07ef3fcd5477668250f'
OLD_DLL_SHA='4dec2aa434c50ad602f1f9f136bf7f8663e9d16c5896a17ea1d343db8faf4883'
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE_COMMIT,dll_sha256=DLL_SHA)
CATALOG_ENTRY=" '024': "+repr(RECORD)+',\n'
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build024.py','test_navigation_build024.py')
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(DLL)),
  ("PREFIX=f'ssam-nav20-023-hard-ordered-","PREFIX=f'ssam-nav20-024-hard-ordered-"),
  ("E=BASE/f'nav20-023-hard-ordered-","E=BASE/f'nav20-024-hard-ordered-"),
  ('PRIVATE A4 023 HARD','PRIVATE A4 024 HARD'),
  ('Private A4 candidate023 Hard normal gameplay','Private A4 candidate024 Hard normal gameplay')],
 'adapter_policy.py':[(OLD_DLL_SHA,DLL_SHA),("validate(map_key,duration,diag,'023')","validate(map_key,duration,diag,'024')"),("return validate(logs,'023')","return validate(logs,'024')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate",CATALOG_ENTRY+"}\n\n\ndef candidate")],
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('fixed retarget source only')
 if not reverse and any(after in text for before,after in DELTAS[name]):raise ValueError('already or partly retargeted source')
 pairs=reversed(DELTAS[name])if reverse else DELTAS[name]
 for before,after in pairs:
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact retarget anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text):return apply(name,text)
def reverse(name,text):return apply(name,text,True)


def validate_build():
 manifest=BUILD/'manifest.json'
 if sha(manifest)!=BUILD_SHA:raise ValueError('candidate manifest changed')
 m=json.loads(manifest.read_text())
 if m['build_ok']is not True or m['repo_commit']!=SOURCE_COMMIT or m['repo_tree']!=SOURCE_TREE or m['dll_sha256']!=DLL_SHA or m['candidate']!=str(DLL)or m['source_overlay']!=str(BUILD/'overlay')or DLL.stat().st_size!=DLL_SIZE:
  raise ValueError('candidate build provenance changed')
 if len(m['source_sha256'])!=47 or len(m['overlay_sha256'])!=28:raise ValueError('candidate complete closure required')
 pins={str(manifest):BUILD_SHA,str(DLL):DLL_SHA}
 for key,directory in [('source_sha256',BUILD/'Sources/Game'),('overlay_sha256',BUILD/'overlay')]:
  for name,h in m[key].items():
   path=Path(name)
   if path.is_absolute()or'..'in path.parts:raise ValueError('candidate source path')
   pins[str(directory/path)]=h
 for path,h in pins.items():
  if sha(path)!=h:raise ValueError('candidate DLL/source hash: '+path)
 return pins


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh disabled destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text())
 if m['runtime_reviewed']is not False or m['comparison']['arm']!='023':raise ValueError('exact disabled023 parent required')
 for key,base in [('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for name,h in m[key].items():
   if sha(base/name)!=h:raise ValueError('parent source pin changed: '+name)
 pins=validate_build();changed={name:transform(name,(PARENT/name).read_text())for name in CHANGED}
 for name,text in changed.items():
  if reverse(name,text)!=(PARENT/name).read_text():raise ValueError('exact reverse bytes differ')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():
  (dest/name).write_text(text)
  (dest/(name+'.024.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),text.splitlines(True),fromfile='disabled023/'+name,tofile='disabled024/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(OLD_BUILD):continue
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins);m['runtime_dependencies']=deps
 m.update(scope='DISABLED_SINGLE_NAV20_024_RED600_V3',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['candidate']=dict(dll_sha256=DLL_SHA,source_commit=SOURCE_COMMIT,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['build024_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,baseline_arm='023',single_arm=True,automatic_retry=False,native_started=False,important_origin_recovery='planning proposal only; actual original radius arrival and exit require separate native observations',grounded_replan='source replan/reset only; actual original radius arrival, movement and item gains require separate native observations',health_connector_proposal='planning proposal only; not accepted movement/health pickup',native_health_gain_attribution='UNKNOWN',old_weapon_unavailable_reason='UNKNOWN',historical_statuses_unchanged=True)
 m['prior_comparison_metadata']=m['comparison']
 m['comparison']=dict(m['comparison'],order=['024'],arm='024',parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,reference='PENDING independent Root review/freeze; one600s024 arm only')
 names=set(m['sources'])|set(ADDITIONS)|{name+'.024.diff'for name in CHANGED}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={name.name:sha(name)for name in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),build='024',manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_reviewed=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
