"""Exact disabled030 ResetV3 -> one disabled031 DIAG1 observation. No runtime imports."""
import argparse
import ast
import copy
import difflib
import json
from pathlib import Path
from prepare_navigation_build030_skulls import read, sha, write

PARENT=Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115')
PARENT_SHA='98294d1ca2c21df380cc10c43a66a9c1b6c0a97500dceae7d3faf854fd15ba11'
OLD_BUILD=Path('/srv/tse-milestone-a-build-030-20261115')
OLD_MANIFEST='89eef08dfce8f2b5f40fba0290e5778bdb42831c7280731ad5cd44c21338a5d3'
OLD_DLL='bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412'
BUILD=Path('/srv/tse-milestone-a-build-031-20261115')
DESTINATION=Path('/srv/tse-a4-build031-hard-reset-v3-diag1-disabled-20261115')
SPEC_SHA='e8db049024dc7d54c2e6beeac94714615d417ea74f5d1b6968ac2e68dab32dac'
ADDITIONS=('prepare_a4_reset_build031.py','test_prepare_a4_reset_build031.py','build031_reset_candidate.json')
SCOPE='DIAG1_PICKER_CUSTODY_OBSERVATION_ONLY_NO_A4_QUALIFICATION_TRANSFER'


def candidate():
 path=Path(__file__).with_name('build031_reset_candidate.json')
 if sha(path)!=SPEC_SHA:raise ValueError('exact actual031 closure specification required')
 return json.loads(read(path))


def replacements():
 spec=candidate()
 return {
  'run-mapreset.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(BUILD/'Sources/Game/GameMP.dll')),
   ("and diag==0,'fixed Red-only three-round480s diagnostic protocol'","and diag==1,'fixed Red-only three-round480s diagnostic protocol'"),
   ("PREFIX='ssam-a4-reset030-v3-20261115'","PREFIX='ssam-a4-reset031-diag1-v3-20261115'"),
   ("E=BASE/f'a4-reset030-v3-","E=BASE/f'a4-reset031-diag1-v3-"),
   ("args=parser.parse_args();main('redstation',480,0)","args=parser.parse_args();main('redstation',480,1)"),
   ("'diagnostics_enabled':bool(DIAG)","'observation_scope':'"+SCOPE+"','qualification_transfer':False,'diagnostics_enabled':bool(DIAG)")],
  'adapter_policy.py':[(OLD_DLL,spec['dll_sha256']),
   ('def options(map_key,duration,diag):\n',"def options(map_key,duration,diag):\n if map_key!='redstation'or type(duration)not in(int,float)or duration!=480 or type(diag)is not int or diag!=1:raise ValueError('fixed031 Red480 DIAG1 observation only')\n")],
  'reset_policy.py':[('PRIVATE A4 RESET 030','PRIVATE A4 RESET 031 DIAGNOSTIC')],
 }


def transform(name,text,reverse=False):
 pairs=replacements()[name]
 for a,b in (reversed(pairs)if reverse else pairs):
  if reverse:a,b=b,a
  # An insertion's replacement contains its original anchor intentionally.
  if text.count(a)!=1 or (not reverse and b in text):raise ValueError('exact unique retarget fragment required: '+name)
  text=text.replace(a,b,1)
 ast.parse(text);return text


def validate_build(m,spec,directory=BUILD):
 if spec!=candidate():raise ValueError('caller closure is not the pinned actual031 candidate')
 if (m.get('build_ok')is not True or m.get('qualified')is not False or
     m.get('repo_commit')!=spec['source_commit']or m.get('repo_tree')!=spec['source_tree']or
     m.get('candidate')!=str(directory/'Sources/Game/GameMP.dll')or
     m.get('source_overlay')!=str(directory/'overlay')or m.get('source_count')!=15 or
     m.get('dll_sha256')!=spec['dll_sha256']or m.get('source_sha256')!=spec['source_sha256']or
     m.get('overlay_sha256')!=spec['overlay_sha256']or len(m['source_sha256'])!=49 or len(m['overlay_sha256'])!=30):
  raise ValueError('exact actual031 build provenance/closure required')


def build_pins(directory,manifest_sha,dll_sha,expected_count):
 if sha(directory/'manifest.json')!=manifest_sha:raise ValueError('build manifest changed')
 m=json.loads(read(directory/'manifest.json'))
 pins={str(directory/'manifest.json'):manifest_sha,str(directory/'Sources/Game/GameMP.dll'):dll_sha}
 for key,sub in [('source_sha256','Sources/Game'),('overlay_sha256','overlay')]:
  for name,pin in m[key].items():
   p=Path(name)
   if p.is_absolute()or'..'in p.parts:raise ValueError('unsafe build source path')
   pins[str(directory/sub/p)]=pin
 if len(pins)!=expected_count:raise ValueError('complete exact build target count required')
 for p,h in pins.items():
  if sha(p)!=h:raise ValueError('actual build target differs: '+p)
 return m,pins


def input_delta(old,new):
 result={}
 for key in ('source_sha256','overlay_sha256'):
  changed=sorted(p for p in old[key]if old[key][p]!=new[key].get(p))
  added=sorted(set(new[key])-set(old[key]))
  if changed!=['BotDriver.cpp','BotSupplyNative.h']or added!=['picker_custody.h']or set(old[key])-set(new[key]):
   raise ValueError('exact030 to031 diagnostic-only input delta required')
  result[key]={'changed':changed,'added':added,'unchanged':sorted(set(old[key])-set(changed))}
 return result


def validate_parent(m):
 if (any(m[k]is not False for k in ('runtime_reviewed','runtime_performed','qualified','functional_pass'))or
     m['rounds']!=['redstation']*3 or m['observation_cap_seconds']!=480 or
     m['observer_close_operation_cap_seconds']!=19 or m['transition_cap_seconds']!=50 or
     m['third_phase_min_wall_and_game_seconds']!=120 or m['first_two_time_limit_minutes']!=2 or
     m['post_round_timeout_seconds']!=20 or m['derivation']['hard_difficulty']!=2 or
     m['derivation']['diagnostics']!=0 or m['derivation']['bot_slotphases']!=24 or
     m['derivation']['actual_resets']!=2 or m['derivation']['original_restarts']!=2 or
     m['candidate']['dll_sha256']!=OLD_DLL):raise ValueError('exact disabled030 reset conditions required')


def verify_pins(manifest,root):
 for key,base in [('runtime_dependencies',Path('/')),('sources',root),('draft_source_sha256',root)]:
  for p,h in manifest[key].items():
   if sha(base/p)!=h:raise ValueError('full hash value differs: '+p)


def file_inventory(root):
 return {str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}


def prepare(destination=DESTINATION,spec=None):
 spec=candidate()if spec is None else spec
 if spec!=candidate():raise ValueError('pinned actual031 closure required')
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in (PARENT,OLD_BUILD,BUILD)):
  raise ValueError('fresh isolated destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled030 timestamp reset parent required')
 m=json.loads(read(PARENT/'source-manifest.json'));validate_parent(m);verify_pins(m,PARENT)
 old,oldpins=build_pins(OLD_BUILD,OLD_MANIFEST,OLD_DLL,79)
 if {p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}!=oldpins:
  raise ValueError('all79 active030 build pins required')
 new,newpins=build_pins(BUILD,spec['manifest_sha256'],spec['dll_sha256'],81)
 validate_build(new,spec)
 if (BUILD/'Sources/Game/GameMP.dll').stat().st_size!=spec['dll_size']:raise ValueError('candidate DLL size differs')
 delta=input_delta(old,new)
 changed={name:transform(name,read(PARENT/name).decode())for name in replacements()}
 for name,text in changed.items():
  if transform(name,text,True).encode()!=read(PARENT/name):raise ValueError('whole source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-mapreset.py']:raise ValueError('author gate must remain false')
 before=file_inventory(PARENT)
 dest.mkdir(mode=0o700)
 for rel in before:
  if rel!='source-manifest.json':write(dest/rel,changed[rel].encode()if rel in changed else read(PARENT/rel))
 diffs=[]
 for name,text in changed.items():
  rel=name+'.031-reset-diag1.diff';diffs.append(rel)
  write(dest/rel,''.join(difflib.unified_diff(read(PARENT/name).decode().splitlines(True),text.splitlines(True),fromfile='immutable030-diag0-reset',tofile='disabled031-diag1-reset')).encode())
 for name in ADDITIONS:write(dest/name,read(Path(__file__).with_name(name)))
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 deps.update(newpins)
 for name in ADDITIONS:deps[str(dest/name)]=sha(dest/name)
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps):raise ValueError('active030 target remains')
 historical=('candidate','scope','derivation','root_review','build030_reset_retarget')
 m['inherited_build030_reset_metadata']={k:copy.deepcopy(m.pop(k))for k in historical}
 m.update(scope='DISABLED_BUILD031_HARD2_DIAG1_RESET_V3_480S_24_SLOTPHASES_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=spec['dll_sha256'],dll_size=spec['dll_size'],source_commit=spec['source_commit'],repo_tree=spec['source_tree'],build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=spec['manifest_sha256'])
 m['derivation']=dict(m['inherited_build030_reset_metadata']['derivation'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,diagnostics=1,independent_review='PENDING_ROOT',source_inputs_verified=49,overlay_inputs_verified=30)
 m['root_review']=dict(approved_for_native=False,independent_review='PENDING',runtime_reviewed=False)
 m['build031_reset_retarget']=dict(removed_old_build_targets=oldpins,new_build_targets=newpins,diagnostic_input_delta=delta,whole_source_inverses=True,other_reset_conditions_unchanged=True,automatic_retry=False,automatic_sequence=False,native_started=False)
 m['diagnostic_observation']=dict(scope=SCOPE,maximum_native_windows=1,acceptance_transfer=False,picker_row_audit='NOT_IMPLEMENTED_YET',accepted_proposal_is_not_movement_or_pickup=True,unobserved_or_throttled_details='UNKNOWN')
 m['sources']={p:sha(dest/p)for p in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());verify_pins(m,dest)
 if before!=file_inventory(PARENT):raise ValueError('immutable030 parent changed')
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-mapreset.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),old_build_pins_removed=len(oldpins),new_build_pins=len(newpins),changed_inherited_files=sorted(changed),other_inherited_files_byte_equal=sum(rel!='source-manifest.json'and rel not in changed for rel in before),parent_preserved=True,qualified=False,runtime_reviewed=False,native_started=False)
 write(dest/'BUILD031-HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
