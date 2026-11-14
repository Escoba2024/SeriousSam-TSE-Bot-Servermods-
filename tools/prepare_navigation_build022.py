"""Prepare exactly one DISABLED Build022/RedStation600s arm; no runtime imports."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-nav20-020-red600-disabled-20261114')
PARENT_SHA='7c1bd1aef595adf3eb4abc1203414dbfe129ff0f722e998b5a181b6b5cf7e4d8'
OLD_BUILD=Path('/srv/tse-milestone-a-build-020-20261114')
BUILD=Path('/srv/tse-milestone-a-build-022-20261114')
BUILD_SHA='8557a3a3de831ed21ba99a74194c8060a1c346629f72bc9a1bd7d7f1184a07c1'
SOURCE_COMMIT='621e92faf1d84e0fe03892b07ab7db230d630390'
DLL=BUILD/'Sources/Game/GameMP.dll'
DLL_SHA='28028e448e514cae8589b078d06533c8934a4a12ca7ab52aaead77e1590ab8fc'
OLD_DLL_SHA='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE_COMMIT,dll_sha256=DLL_SHA)
CATALOG_ENTRY=" '022': "+repr(RECORD)+',\n'
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build022.py','test_navigation_build022.py')
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(DLL)),
  ("PREFIX=f'ssam-nav20-020-hard-ordered-","PREFIX=f'ssam-nav20-022-hard-ordered-"),
  ("E=BASE/f'nav20-020-hard-ordered-","E=BASE/f'nav20-022-hard-ordered-"),
  ('PRIVATE A4 020 HARD','PRIVATE A4 022 HARD'),
  ('Private A4 candidate020 Hard normal gameplay','Private A4 candidate022 Hard normal gameplay')],
 'adapter_policy.py':[(OLD_DLL_SHA,DLL_SHA),("validate(map_key,duration,diag,'020')","validate(map_key,duration,diag,'022')"),("return validate(logs,'020')","return validate(logs,'022')")],
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
 if m['build_ok']is not True or m['repo_commit']!=SOURCE_COMMIT or m['dll_sha256']!=DLL_SHA or m['candidate']!=str(DLL)or m['source_overlay']!=str(BUILD/'overlay')or DLL.stat().st_size!=434176:
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
 if m['runtime_reviewed']is not False or m['comparison']['arm']!='020':raise ValueError('exact disabled020 parent required')
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
  (dest/(name+'.022.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),text.splitlines(True),fromfile='disabled020/'+name,tofile='disabled022/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(OLD_BUILD):continue
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins);m['runtime_dependencies']=deps
 m.update(scope='DISABLED_SINGLE_NAV20_022_RED600_V3',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['candidate']=dict(dll_sha256=DLL_SHA,source_commit=SOURCE_COMMIT,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['build022_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,baseline_arm='020',single_arm=True,automatic_retry=False,native_started=False,health_connector_proposal='planning proposal only; not accepted movement/health pickup',native_health_gain_attribution='UNKNOWN',old_weapon_unavailable_reason='UNKNOWN',historical_statuses_unchanged=True)
 m['prior_comparison_metadata']=m['comparison']
 m['comparison']=dict(m['comparison'],order=['022'],arm='022',parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,reference='PENDING independent Root review/freeze; one600s022 arm only')
 names=set(m['sources'])|set(ADDITIONS)|{name+'.022.diff'for name in CHANGED}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={name.name:sha(name)for name in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),build='022',manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_reviewed=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
