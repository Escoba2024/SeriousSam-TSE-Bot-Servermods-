"""Prepare ONE fresh DISABLED029 Skulls600 diagnostic package; no runtime imports."""
import argparse
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import shutil
from prepare_navigation_build024_maps import validate_assets
from navigation_build029_skulls_policy import EXPECTED_SOURCES, EXPECTED_OVERLAY
from cleanup_failure_receipt import transform_controller, reverse_controller
import native_cgroup_exit_patch as cgroup_patch
from verify_driver_final_source import verify as verify_driver
from verify_contention_diag_source import verify as verify_header

PARENT=Path('/srv/tse-nav20-027-skulls600-diag1-disabled-20261115')
PARENT_SHA='85d8ef512c8901cb5a021ac3dff4d4d5b00e55fc950d5b892f87a650f6239432'
OLD_BUILD=Path('/srv/tse-milestone-a-build-027-20261115')
OLD_BUILD_SHA='ca235d88b0e20ed98fed83d9adf16e731feaec286f4da8f9dde0defe96d3c551'
OLD_DLL_SHA='f5bf76801cade78803c6f4bcf97837390329fc30d2a016d202a9f4b96bbfc17e'
BUILD=Path('/srv/tse-milestone-a-build-029-20261115')
BUILD_SHA='aed7a9325b1cfe3af3cb77ca897901e48236de83d9b5ff0bb5d48eab23e046a9'
SOURCE_COMMIT='7dfda985fe547cf6496cc18aaa713568fafcc9fa'
SOURCE_TREE='a8aa60561d0c642346eaac4f6784e85eb0546427'
DLL=BUILD/'Sources/Game/GameMP.dll'
DLL_SHA='a043de1e0fc647d2805c20ea01e9f52eada3fdaa0b55caad8be6df5302ded971'
DLL_SIZE=451584
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE_COMMIT,dll_sha256=DLL_SHA)
CATALOG_ENTRY=" '029': "+repr(RECORD)+',\n'
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build029_skulls.py','navigation_build029_skulls_policy.py','test_navigation_build029_skulls.py','cleanup_failure_receipt.py','test_cleanup_failure_receipt.py','native_cgroup_exit_patch.py','test_native_cgroup_exit_patch.py','verify_driver_final_source.py','verify_contention_diag_source.py')
DIFF_NAMES=tuple(name+'.029skulls-diag1.diff'for name in CHANGED)+('run-a4.py.cleanup-receipt.diff','strict_backend.py.cgroup-exit.diff')
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(DLL)),
  ("PREFIX=f'ssam-nav20-027-skulls-diag1-hard-ordered-","PREFIX=f'ssam-nav20-029-skulls-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-027-skulls-diag1-hard-ordered-","E=BASE/f'nav20-029-skulls-diag1-hard-ordered-"),
  ('PRIVATE A4 027 HARD DIAGNOSTIC','PRIVATE A4 029 HARD DIAGNOSTIC'),
  ('Private candidate027 Skulls diagnostic observation only','Private candidate029 Skulls diagnostic observation only')],
 'adapter_policy.py':[(OLD_DLL_SHA,DLL_SHA),
  ('from navigation_build027_skulls_policy import options as validate','from navigation_build029_skulls_policy import options as validate'),
  ("validate(map_key,duration,diag,'027')","validate(map_key,duration,diag,'029')"),
  ("return validate(logs,'027')","return validate(logs,'029')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate",CATALOG_ENTRY+"}\n\n\ndef candidate")],
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('fixed three retarget sources only')
 if not reverse and any(after in text for before,after in DELTAS[name]):raise ValueError('already/partly retargeted source')
 for before,after in (reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact retarget anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text):return apply(name,text)
def reverse(name,text):return apply(name,text,True)


def validate_build_manifest(m):
 if (m['build_ok']is not True or m['qualified']is not False or m['repo_commit']!=SOURCE_COMMIT or m['repo_tree']!=SOURCE_TREE
     or m['dll_sha256']!=DLL_SHA or m['candidate']!=str(DLL)
     or m['source_overlay']!=str(BUILD/'overlay')or m['source_count']!=15):
  raise ValueError('candidate029 build provenance changed')
 if m['source_sha256']!=EXPECTED_SOURCES or m['overlay_sha256']!=EXPECTED_OVERLAY:
  raise ValueError('candidate029 exact complete48/29 hash maps required')
 pins={str(BUILD/'manifest.json'):BUILD_SHA,str(DLL):DLL_SHA}
 for key,directory in [('source_sha256',BUILD/'Sources/Game'),('overlay_sha256',BUILD/'overlay')]:
  for name,h in m[key].items():
   path=Path(name)
   if path.is_absolute()or'..'in path.parts:raise ValueError('candidate029 source path')
   pins[str(directory/path)]=h
 if len(pins)!=79:raise ValueError('candidate029 unique79 target closure required')
 return pins


def validate_build():
 if sha(BUILD/'manifest.json')!=BUILD_SHA:raise ValueError('candidate029 manifest changed')
 pins=validate_build_manifest(json.loads((BUILD/'manifest.json').read_text()))
 if DLL.stat().st_size!=DLL_SIZE:raise ValueError('candidate029 DLL size changed')
 for path,h in pins.items():
  if sha(path)!=h:raise ValueError('candidate029 DLL/source hash changed: '+path)
 return pins


def validate_productive_delta():
 old=json.loads((OLD_BUILD/'manifest.json').read_text())
 new=json.loads((BUILD/'manifest.json').read_text());result={}
 for key in ('source_sha256','overlay_sha256'):
  if set(new[key])!=set(old[key])|{'driver_final_decision.h'}:raise ValueError('029 exact added formatter closure required')
  changed=sorted(name for name in old[key]if new[key][name]!=old[key][name])
  if changed!=['BotDriver.cpp','BotSupplyNative.h']:raise ValueError('029 source delta must be Header and Driver only')
  directory='Sources/Game'if key=='source_sha256'else'overlay'
  before=OLD_BUILD/directory;after=BUILD/directory
  if verify_driver((after/'BotDriver.cpp').read_text(),(after/'BotSupplyNative.h').read_bytes())!=(before/'BotDriver.cpp').read_text():raise ValueError('full029 Driver inverse differs from027')
  if verify_header((after/'BotSupplyNative.h').read_text())!=(before/'BotSupplyNative.h').read_text():raise ValueError('full029 Header inverse differs from027')
  result[key]=dict(changed=changed,added=['driver_final_decision.h'],unchanged=sorted(set(old[key])-set(changed)))
 return result


def validate_parent_manifest(m):
 c=m['comparison'];case=m['map_case']
 if (m['runtime_reviewed']is not False or m['qualified']is not False
     or m['runtime_performed']is not False or m['functional_pass']is not False
     or c['arm']!='027'or c['map']!='skulls'or c['seconds']!=600 or c['diagnostics']!=1
     or c['hard_difficulty']!=2 or c['observer_fps']!=20
     or case['map']!='skulls'or case['seconds']!=600 or case['diagnostics']!=1
     or case['hard_difficulty']!=2 or case['bot_count']!=8 or case['bot_tier']!=3 or case['original_observer_fps']!=20
     or m['candidate']['dll_sha256']!=OLD_DLL_SHA or m['candidate']['build_manifest']!=str(OLD_BUILD/'manifest.json')):
  raise ValueError('exact disabled027 Skulls600 diag1 parent conditions required')


def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled027 Skulls parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());validate_parent_manifest(m)
 for key,base in [('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for name,h in m[key].items():
   if sha(base/name)!=h:raise ValueError('parent source/config pin changed: '+name)
 if sha(PARENT/'map-catalog.json')!=CATALOG_SHA:raise ValueError('parent catalog changed')
 return m


def validate_old_targets(m):
 if sha(OLD_BUILD/'manifest.json')!=OLD_BUILD_SHA:raise ValueError('exact027 build manifest required')
 old=json.loads((OLD_BUILD/'manifest.json').read_text())
 expected={str(OLD_BUILD/'manifest.json'):OLD_BUILD_SHA,str(OLD_BUILD/'Sources/Game/GameMP.dll'):OLD_DLL_SHA}
 for key,directory in [('source_sha256',OLD_BUILD/'Sources/Game'),('overlay_sha256',OLD_BUILD/'overlay')]:
  for name,value in old[key].items():expected[str(directory/name)]=value
 actual={p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}
 if len(expected)!=77 or actual!=expected:raise ValueError('complete exact77 old027 targets required')
 return actual


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists()or dest.is_relative_to(PARENT)or dest.is_relative_to(BUILD)or dest.is_relative_to(OLD_BUILD):
  raise ValueError('fresh independent disabled destination required')
 m=validate_parent();pins=validate_build();productive_delta=validate_productive_delta()
 catalog=json.loads((PARENT/'map-catalog.json').read_text());asset=validate_assets('skulls',catalog)
 retargeted={name:transform(name,(PARENT/name).read_text())for name in CHANGED}
 changed=dict(retargeted)
 for name,text in changed.items():
  if reverse(name,text)!=(PARENT/name).read_text():raise ValueError('exact inverse bytes differ')
 changed['run-a4.py']=transform_controller(retargeted['run-a4.py'])
 if reverse_controller(changed['run-a4.py'])!=retargeted['run-a4.py']:raise ValueError('cleanup receipt whole source inverse differs')
 changed['strict_backend.py']=cgroup_patch.transform((PARENT/'strict_backend.py').read_text())
 if cgroup_patch.reverse(changed['strict_backend.py'])!=(PARENT/'strict_backend.py').read_text():raise ValueError('backend whole source inverse differs')
 old_targets=validate_old_targets(m)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():(dest/name).write_text(text)
 def diff(name,before,after):(dest/name).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='disabled027-parent',tofile='disabled029-source')))
 for name,text in retargeted.items():diff(name+'.029skulls-diag1.diff',(PARENT/name).read_text(),text)
 diff('run-a4.py.cleanup-receipt.diff',retargeted['run-a4.py'],changed['run-a4.py'])
 diff('strict_backend.py.cgroup-exit.diff',(PARENT/'strict_backend.py').read_text(),changed['strict_backend.py'])
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(OLD_BUILD)or path==PARENT/'navigation_build027_skulls_policy.py':continue
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins)
 for name in ('navigation_build029_skulls_policy.py','cleanup_failure_receipt.py'):deps[str(dest/name)]=sha(dest/name)
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps):raise ValueError('old027 build dependency retained')
 inherited={key:copy.deepcopy(m[key])for key in ('candidate','comparison','map_case')}
 for key in list(m):
  if key.startswith('build')and key.endswith('_derivation'):inherited[key]=m.pop(key)
 m['inherited_build027_skulls_metadata']=inherited
 m['runtime_dependencies']=deps
 m.update(scope='DISABLED_SINGLE_BUILD029_SKULLS600_REACQUIRE_DIAG1_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=DLL_SIZE,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(inherited['comparison'],order=['029'],arm='029',diagnostics=1,parent_manifest_sha256=PARENT_SHA,native_started=False,profile_semantics='DIAGNOSTIC_OBSERVATION_ONLY_NO_COMPARISON')
 m['map_case']=dict(inherited['map_case'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,diagnostics=1,assets=asset,scope='diagnostic observation only; no map/functional/comparison qualification')
 m['build029_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,build_closure_targets=79,removed_old027_build_targets=old_targets,source_condition_changes=['Build029'],productive_delta=productive_delta,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False,accepted_proposal='proposal only; movement, original radius arrival, SafeMotion and pickup require separate observations',missing_throttled_or_unreached_fields='UNKNOWN',historical_statuses_unchanged=True)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_reacquire_diagnostic=False,reference='PENDING independent Root review/freeze; one029 Skulls600 diag1 observation only')
 m['cleanup_failure_receipt']=dict(current_exception_only=True,max_records=4,max_record_bytes=65536,max_traceback_frames=32,private_mode='0600',successful_cleanup_file_created=False,source_inverse='separate exact three-anchor controller inverse',archive_failure='original error remains first; append archive error and continue existing role order',old_ON_exception_site='UNKNOWN')
 m['backend_cgroup_exit']=dict(parent_sha256=cgroup_patch.PARENT_SHA,changed_sha256=sha(dest/'strict_backend.py'),whole_source_inverse=True,concrete_ON_cause_proven=False)
 names=set(m['sources'])|set(ADDITIONS)|set(DIFF_NAMES)
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={path.name:sha(path)for path in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),build='029',map='skulls',seconds=600,diagnostics=1,manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_reviewed=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
