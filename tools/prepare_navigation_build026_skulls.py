"""Prepare ONE fresh DISABLED026 Skulls600 diagnostic package; no runtime imports."""
import argparse
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import shutil
from prepare_navigation_build024_maps import validate_assets

PARENT=Path('/srv/tse-nav20-024-skulls600-disabled-20261115')
PARENT_SHA='9254b47fddb163bfc476df1198cab090c0c814bf16f59154d390919189389f0e'
OLD_BUILD=Path('/srv/tse-milestone-a-build-024-20261114')
OLD_DLL_SHA='192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c'
BUILD=Path('/srv/tse-milestone-a-build-026-20261115')
BUILD_SHA='be0513a059e2dcf5bda364ea70c4f2dee800fb084d2c44861912eaa22e186fd3'
SOURCE_COMMIT='05e1708abc8b886895157b57a28e35d7375c4f29'
SOURCE_TREE='1f96c7a6d439f9f894de0dca214d56a846ddc5c5'
DLL=BUILD/'Sources/Game/GameMP.dll'
DLL_SHA='2c9a238191b9642bf7f9613f01a461cf711f97fe62e581bdd7c93b5f58a9bcdd'
DLL_SIZE=443392
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE_COMMIT,dll_sha256=DLL_SHA)
CATALOG_ENTRY=" '026': "+repr(RECORD)+',\n'
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py','a4_hard_map_policy.py')
ADDITIONS=('prepare_navigation_build026_skulls.py','navigation_build026_skulls_policy.py','test_navigation_build026_skulls.py')
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(DLL)),
  ("PREFIX=f'ssam-nav20-024-mapcase-hard-ordered-","PREFIX=f'ssam-nav20-026-skulls-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-024-mapcase-hard-ordered-","E=BASE/f'nav20-026-skulls-diag1-hard-ordered-"),
  ("-{map_key}-20261114'","-{map_key}-20261115'"),
  ('PRIVATE A4 024 HARD','PRIVATE A4 026 HARD DIAGNOSTIC'),
  ('Private A4 candidate024 Hard normal gameplay','Private candidate026 Skulls diagnostic observation only'),
  ('PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED','PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY'),
  ("choices=tuple(policy.prepared.catalog()['maps'])","choices=('skulls',)"),
  ('choices=(0,1),default=0','choices=(1,),default=1')],
 'adapter_policy.py':[(OLD_DLL_SHA,DLL_SHA),
  ('from navigation_build024_maps_policy import options as validate','from navigation_build026_skulls_policy import options as validate'),
  ("validate(map_key,duration,diag,'024','skulls')","validate(map_key,duration,diag,'026')"),
  ("return validate(logs,'024')","return validate(logs,'026')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate",CATALOG_ENTRY+"}\n\n\ndef candidate")],
 'a4_hard_map_policy.py':[("type(diag)is int and diag==0,'fixed diagnostics0'","type(diag)is int and diag==1,'fixed diagnostics1'")],
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('fixed four retarget sources only')
 if not reverse and any(after in text for before,after in DELTAS[name]):raise ValueError('already/partly retargeted source')
 for before,after in (reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact retarget anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text):return apply(name,text)
def reverse(name,text):return apply(name,text,True)


def validate_build_manifest(m):
 if (m['build_ok']is not True or m['repo_commit']!=SOURCE_COMMIT or m['repo_tree']!=SOURCE_TREE
     or m['dll_sha256']!=DLL_SHA or m['candidate']!=str(DLL)
     or m['source_overlay']!=str(BUILD/'overlay')or m['source_count']!=15):
  raise ValueError('candidate026 build provenance changed')
 if len(m['source_sha256'])!=47 or len(m['overlay_sha256'])!=28:raise ValueError('candidate026 complete47/28 closure required')
 pins={str(BUILD/'manifest.json'):BUILD_SHA,str(DLL):DLL_SHA}
 for key,directory in [('source_sha256',BUILD/'Sources/Game'),('overlay_sha256',BUILD/'overlay')]:
  for name,h in m[key].items():
   path=Path(name)
   if path.is_absolute()or'..'in path.parts:raise ValueError('candidate026 source path')
   pins[str(directory/path)]=h
 if len(pins)!=77:raise ValueError('candidate026 unique77 target closure required')
 return pins


def validate_build():
 if sha(BUILD/'manifest.json')!=BUILD_SHA:raise ValueError('candidate026 manifest changed')
 pins=validate_build_manifest(json.loads((BUILD/'manifest.json').read_text()))
 if DLL.stat().st_size!=DLL_SIZE:raise ValueError('candidate026 DLL size changed')
 for path,h in pins.items():
  if sha(path)!=h:raise ValueError('candidate026 DLL/source hash changed: '+path)
 return pins


def validate_parent_manifest(m):
 c=m['comparison'];case=m['map_case']
 if (m['runtime_reviewed']is not False or m['qualified']is not False
     or m['runtime_performed']is not False or m['functional_pass']is not False
     or c['arm']!='024'or c['map']!='skulls'or c['seconds']!=600 or c['diagnostics']!=0
     or c['hard_difficulty']!=2 or c['observer_fps']!=20
     or case['map']!='skulls'or case['seconds']!=600 or case['diagnostics']!=0
     or case['hard_difficulty']!=2 or case['bot_count']!=8 or case['bot_tier']!=3 or case['original_observer_fps']!=20
     or m['candidate']['dll_sha256']!=OLD_DLL_SHA or m['candidate']['build_manifest']!=str(OLD_BUILD/'manifest.json')):
  raise ValueError('exact disabled024 Skulls600 diag0 parent conditions required')


def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled024 Skulls parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());validate_parent_manifest(m)
 for key,base in [('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for name,h in m[key].items():
   if sha(base/name)!=h:raise ValueError('parent source/config pin changed: '+name)
 if sha(PARENT/'map-catalog.json')!=CATALOG_SHA:raise ValueError('parent catalog changed')
 return m


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists()or dest.is_relative_to(PARENT)or dest.is_relative_to(BUILD)or dest.is_relative_to(OLD_BUILD):
  raise ValueError('fresh independent disabled destination required')
 m=validate_parent();pins=validate_build()
 catalog=json.loads((PARENT/'map-catalog.json').read_text());asset=validate_assets('skulls',catalog)
 changed={name:transform(name,(PARENT/name).read_text())for name in CHANGED}
 for name,text in changed.items():
  if reverse(name,text)!=(PARENT/name).read_text():raise ValueError('exact inverse bytes differ')
 old_targets={p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}
 if len(old_targets)!=77:raise ValueError('parent complete77 old024 target closure required')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():
  (dest/name).write_text(text)
  (dest/(name+'.026skulls-diag1.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),text.splitlines(True),fromfile='disabled024-Skulls/'+name,tofile='disabled026-Skulls-diag1/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(OLD_BUILD)or path==PARENT/'navigation_build024_maps_policy.py':continue
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins);deps[str(dest/'navigation_build026_skulls_policy.py')]=sha(dest/'navigation_build026_skulls_policy.py')
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps):raise ValueError('old024 build dependency retained')
 inherited={key:copy.deepcopy(m[key])for key in ('candidate','comparison','map_case')}
 for key in list(m):
  if key.startswith('build')and key.endswith('_derivation'):inherited[key]=m.pop(key)
 m['inherited_build024_skulls_metadata']=inherited
 m['runtime_dependencies']=deps
 m.update(scope='DISABLED_SINGLE_BUILD026_SKULLS600_REACQUIRE_DIAG1_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=DLL_SIZE,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(inherited['comparison'],order=['026'],arm='026',diagnostics=1,parent_manifest_sha256=PARENT_SHA,native_started=False,profile_semantics='DIAGNOSTIC_OBSERVATION_ONLY_NO_COMPARISON')
 m['map_case']=dict(inherited['map_case'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,diagnostics=1,assets=asset,scope='diagnostic observation only; no map/functional/comparison qualification')
 m['build026_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,build_closure_targets=77,removed_old024_build_targets=old_targets,source_condition_changes=['Build026','diagnostics1'],single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False,accepted_proposal='proposal only; movement, original radius arrival, SafeMotion and pickup require separate observations',missing_throttled_or_unreached_fields='UNKNOWN',historical_statuses_unchanged=True)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_reacquire_diagnostic=False,reference='PENDING independent Root review/freeze; one026 Skulls600 diag1 observation only')
 names=set(m['sources'])|set(ADDITIONS)|{name+'.026skulls-diag1.diff'for name in CHANGED}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={path.name:sha(path)for path in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),build='026',map='skulls',seconds=600,diagnostics=1,manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_reviewed=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
