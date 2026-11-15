"""One fresh disabled Build030 ResetV3 fork; source preparation only."""
import argparse
import ast
import copy
import difflib
import json
from pathlib import Path
from prepare_navigation_build030_skulls import read, sha, write
import prepare_navigation_build030_skulls as build030
import file_transaction_timestamp_patch as timestamps
import native_cgroup_exit_patch as cgroup
import cleanup_failure_receipt as cleanup

PARENT=Path('/srv/tse-a4-build020-hard-reset-v3-disabled-review-20261114')
PARENT_SHA='2a93b4f03c560e6f7364ca8cac06002d28b1157dbc7d0f6226d2dc6af381e9fb'
OLD_BUILD=Path('/srv/tse-milestone-a-build-020-20261114')
OLD_MANIFEST='3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6'
OLD_DLL='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'
DESTINATION=Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115')
PAIRS={
 'run-mapreset.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(build030.DLL)),
  ("PREFIX='ssam-a4-reset020-v3-20261114'","PREFIX='ssam-a4-reset030-v3-20261115'"),
  ("E=BASE/f'a4-reset020-v3-","E=BASE/f'a4-reset030-v3-")],
 'adapter_policy.py':[(OLD_DLL,build030.DLL_SHA)],
 'reset_policy.py':[('PRIVATE A4 RESET 020','PRIVATE A4 RESET 030')],
}
ADDITIONS=('prepare_a4_reset_build030.py','test_a4_reset_build030_cleanup.py',
 'prepare_navigation_build030_skulls.py','navigation_build030_skulls_policy.py',
 'file_transaction_timestamp_patch.py','test_file_transaction_timestamp_patch.py',
 'native_cgroup_exit_patch.py','test_native_cgroup_exit_patch.py',
 'cleanup_failure_receipt.py','test_cleanup_failure_receipt.py')


def literal(name,source,reverse=False):
 for a,b in (reversed(PAIRS[name])if reverse else PAIRS[name]):
  if reverse:a,b=b,a
  if source.count(a)!=1 or (not reverse and b in source):raise ValueError('unique retarget anchor: '+a)
  source=source.replace(a,b,1)
 ast.parse(source);return source


def controller(source):
 result=cleanup.transform_controller(literal('run-mapreset.py',source))
 if literal('run-mapreset.py',cleanup.reverse_controller(result),True)!=source:
  raise ValueError('whole ResetV3 controller inverse differs')
 return result


def pins(directory,manifest_hash,dll_hash,count):
 if sha(directory/'manifest.json')!=manifest_hash:raise ValueError('build manifest differs')
 m=json.loads(read(directory/'manifest.json'))
 result={str(directory/'manifest.json'):manifest_hash,str(directory/'Sources/Game/GameMP.dll'):dll_hash}
 for key,sub in [('source_sha256','Sources/Game'),('overlay_sha256','overlay')]:
  for name,h in m[key].items():
   p=Path(name)
   if p.is_absolute()or'..'in p.parts:raise ValueError('build source path')
   result[str(directory/sub/p)]=h
 if len(result)!=count:raise ValueError('complete build target set required')
 for path,h in result.items():
  if sha(path)!=h:raise ValueError('build pin differs: '+path)
 return m,result


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in (PARENT,OLD_BUILD,build030.BUILD)):
  raise ValueError('fresh isolated destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact ResetV3 parent required')
 m=json.loads(read(PARENT/'source-manifest.json'))
 if (m['runtime_reviewed']is not False or m['qualified']is not False or m['functional_pass']is not False or
     m['runtime_performed']is not False or m['rounds']!=['redstation']*3 or
     m['observation_cap_seconds']!=480 or m['observer_close_operation_cap_seconds']!=19 or
     m['transition_cap_seconds']!=50 or m['third_phase_min_wall_and_game_seconds']!=120 or
     m['derivation']['hard_difficulty']!=2 or m['derivation']['diagnostics']!=0 or
     m['derivation']['bot_slotphases']!=24 or m['derivation']['actual_resets']!=2 or
     m['candidate']['dll_sha256']!=OLD_DLL):raise ValueError('fixed disabled ResetV3 conditions differ')
 for key,base in [('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for p,h in m[key].items():
   if sha(base/p)!=h:raise ValueError('parent pin differs: '+p)
 old,oldpins=pins(OLD_BUILD,OLD_MANIFEST,OLD_DLL,77)
 if {p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}!=oldpins:
  raise ValueError('exact old77 active build targets required')
 new,newpins=pins(build030.BUILD,build030.BUILD_SHA,build030.DLL_SHA,79)
 if (new['build_ok']is not True or new['qualified']is not False or
     new['repo_commit']!=build030.SOURCE_COMMIT or new['repo_tree']!=build030.SOURCE_TREE or
     new['candidate']!=str(build030.DLL)or new['dll_sha256']!=build030.DLL_SHA or
     new['source_overlay']!=str(build030.BUILD/'overlay')or new['source_count']!=15 or
     new['source_sha256']!=build030.EXPECTED_SOURCES or new['overlay_sha256']!=build030.EXPECTED_OVERLAY or
     build030.DLL.stat().st_size!=build030.DLL_SIZE):raise ValueError('exact030 build provenance required')
 delta={}
 for key in ('source_sha256','overlay_sha256'):
  changed=sorted(p for p in old[key]if old[key][p]!=new[key].get(p))
  if set(new[key])!=set(old[key])|{'driver_final_decision.h'}or changed!=['BotDriver.cpp','BotSupplyNative.h','cecil_motion.h']:
   raise ValueError('exact020 to030 source delta required')
  delta[key]=dict(changed=changed,added=['driver_final_decision.h'],unchanged=sorted(set(old[key])-set(changed)))
 changed={'run-mapreset.py':controller(read(PARENT/'run-mapreset.py').decode())}
 for name in ('adapter_policy.py','reset_policy.py'):
  oldtext=read(PARENT/name).decode();changed[name]=literal(name,oldtext)
  if literal(name,changed[name],True)!=oldtext:raise ValueError('whole literal inverse differs')
 for name,patch in [('transaction.py',timestamps),('strict_backend.py',cgroup)]:
  oldtext=read(PARENT/name).decode();changed[name]=patch.transform(oldtext)
  if patch.reverse(changed[name])!=oldtext:raise ValueError('whole reviewed fix inverse differs')
 # Both reviewed fixes must equal the existing030 navigation package byte-for-byte.
 nav=Path('/srv/tse-nav20-030-skulls600-diag1-timestamps-disabled-20261115')
 for name in ('transaction.py','strict_backend.py'):
  if changed[name].encode()!=read(nav/name):raise ValueError('existing030 navigation fix differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-mapreset.py']:raise ValueError('runtime gate must stay false')
 before={str(p.relative_to(PARENT)):sha(p)for p in PARENT.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc'}
 dest.mkdir(mode=0o700)
 for rel in before:
  if rel!='source-manifest.json':write(dest/rel,(changed[rel].encode()if rel in changed else read(PARENT/rel)))
 diffnames=[]
 for name,source in changed.items():
  rel=name+'.030-reset.diff';diffnames.append(rel)
  write(dest/rel,''.join(difflib.unified_diff(read(PARENT/name).decode().splitlines(True),source.splitlines(True),fromfile='immutable020-reset-v3',tofile='disabled030-reset-v3')).encode())
 for name in ADDITIONS:write(dest/name,read(Path(__file__).with_name(name)))
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 deps.update(newpins);deps[str(dest/'cleanup_failure_receipt.py')]=sha(dest/'cleanup_failure_receipt.py')
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps):raise ValueError('stale active020 build pin')
 m['inherited_build020_reset_metadata']={k:copy.deepcopy(m[k])for k in ('candidate','scope','derivation','root_review')}
 m.update(scope='DISABLED_BUILD030_HARD2_DIAG0_RESET_V3_480S_24_SLOTPHASES_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=build030.DLL_SHA,dll_size=build030.DLL_SIZE,source_commit=build030.SOURCE_COMMIT,repo_tree=build030.SOURCE_TREE,build_manifest=str(build030.BUILD/'manifest.json'),build_manifest_sha256=build030.BUILD_SHA)
 m['derivation']=dict(m['derivation'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,independent_review='PENDING_ROOT',source_inputs_verified=48,overlay_inputs_verified=29)
 m['build030_reset_retarget']=dict(removed_old_build_targets=oldpins,new_build_targets=newpins,productive_delta=delta,whole_source_inverses=True,unchanged_reset_protocol=True,automatic_retry=False,automatic_sequence=False,native_started=False,terminal_watchdog_positive_native_case='OPEN_NOT_TRANSFERRED')
 m['timestamp_restoration']=dict(parent_transaction_sha256=timestamps.PARENT_SHA,changed_transaction_sha256=sha(dest/'transaction.py'),whole_inverse=True,historical_timestamp_claim=False)
 m['cgroup_cleanup']=dict(parent_backend_sha256=cgroup.PARENT_SHA,changed_backend_sha256=sha(dest/'strict_backend.py'),whole_inverse=True,concrete_old_failure_location='UNKNOWN',failure_receipt='cleanup-close-failures-private.jsonl',max_four_roles=True,max_bytes_per_record=65536)
 m['root_review']=dict(approved_for_native=False,independent_review='PENDING',runtime_reviewed=False)
 m['sources']={p:sha(dest/p)for p in sorted(set(m['sources'])|set(ADDITIONS)|set(diffnames))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode())
 for key,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
  for p,h in m[key].items():
   if sha(base/p)!=h:raise ValueError('new complete expected hash differs: '+p)
 after={rel:sha(PARENT/rel)for rel in before}
 if before!=after:raise ValueError('immutable parent changed')
 same=[rel for rel in before if rel!='source-manifest.json'and sha(dest/rel)==before[rel]]
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-mapreset.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),old_build_pins_removed=len(oldpins),new_build_pins=len(newpins),changed_inherited_files=sorted(changed),other_inherited_files_byte_equal=len(same),parent_preserved=True,qualified=False,runtime_reviewed=False,native_started=False)
 write(dest/'BUILD030-HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
