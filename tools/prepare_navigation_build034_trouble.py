"""Exact disabled032Trouble600 -> one disabled034Trouble300 diagnostic condition."""
import argparse,ast,copy,difflib,json
from pathlib import Path
import prepare_navigation_build031_hole as base
import prepare_navigation_build031_trouble as assets_helper
import prepare_navigation_build032_trouble as prior
from navigation_build034_trouble_policy import duration_source,DURATION_OLD,DURATION_NEW
from prepare_navigation_build031_hole import read,sha,load,write
PARENT=Path('/srv/tse-nav20-032-trouble600-diag1-disabled-20261115')
PARENT_SHA='c78fd3260893b330295b0b720e3ef20b291820cb094a4be9bdbad132919122d4'
OLD_BUILD=prior.BUILD
BUILD=Path('/srv/tse-milestone-a-build-034-20261115')
BUILD_SHA='6f37ef1df5cb93c65dd9bff5018aa1cf77d860f814328e67557894b4cfabe266'
DLL_SHA='2554e9c23b0875797ea03be770d182aa0bc3380f4fb5c98e2ed427f27719025d'
DLL_SIZE=467968
SOURCE='9fc6f79676e5eecf5a95aab4744576b23d456ccf'
TREE='88906c6a40edb850b8cd07ffeca35ea35ed62914'
DESTINATION=Path('/srv/tse-nav20-034-trouble300-diag1-disabled-20261115')
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py','a4_hard_map_policy.py')
ADDITIONS=('prepare_navigation_build034_trouble.py','navigation_build034_trouble_policy.py')
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE,dll_sha256=DLL_SHA)
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(BUILD/'Sources/Game/GameMP.dll')),
  ("PREFIX=f'ssam-nav20-032-trouble-diag1-hard-ordered-","PREFIX=f'ssam-nav20-034-trouble300-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-032-trouble-diag1-hard-ordered-","E=BASE/f'nav20-034-trouble300-diag1-hard-ordered-"),
  ('PRIVATE A4 032 HARD DIAGNOSTIC','PRIVATE A4 034 HARD DIAGNOSTIC'),
  ('Private candidate032 LittleTrouble diagnostic observation only','Private candidate034 LittleTrouble300 diagnostic observation only'),
  ('default=600','default=300')],
 'adapter_policy.py':[(prior.DLL_SHA,DLL_SHA),
  ('from navigation_build032_trouble_policy import options as validate','from navigation_build034_trouble_policy import options as validate'),
  ("validate(map_key,duration,diag,'032')","validate(map_key,duration,diag,'034')"),
  ("return validate(logs,'032')","return validate(logs,'034')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate"," '034': "+repr(RECORD)+',\n}\n\n\ndef candidate')],
 'a4_hard_map_policy.py':[(DURATION_OLD,DURATION_NEW)],
}

def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('four exact retarget sources only')
 if name=='a4_hard_map_policy.py':return duration_source(text,reverse)
 for a,b in(reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:a,b=b,a
  if text.count(a)!=1 or(not reverse and b in text):raise ValueError('unique exact retarget anchor required')
  text=text.replace(a,b,1)
 ast.parse(text);return text

def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('fixed032Trouble disabled parent required')
 m=load(PARENT/'source-manifest.json');c=m['comparison'];p=m['map_case']
 if(any(m[k]is not False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass'])or
    c['arm']!='032'or c['order']!=['032']or c['map']!='trouble'or c['seconds']!=600 or c['diagnostics']!=1 or c['hard_difficulty']!=2 or c['observer_fps']!=20 or
    p['map']!='trouble'or p['seconds']!=600 or p['diagnostics']!=1 or p['hard_difficulty']!=2 or p['bot_tier']!=3 or p['bot_count']!=8 or p['original_observer_fps']!=20 or
    any(x.get(k)is not False for x in [c,p]for k in ['automatic_sequence','automatic_retry','native_started'])or
    m['candidate']['dll_sha256']!=prior.DLL_SHA or m['candidate']['build_manifest']!=str(OLD_BUILD/'manifest.json')or
    sha(PARENT/'transaction.py')!=m['timestamp_restoration']['changed_transaction_sha256']):raise ValueError('exact032 inherited conditions required')
 base.verify_pins(m,PARENT)
 if sha(PARENT/'map-catalog.json')!=base.CATALOG_SHA:raise ValueError('immutable mapcatalog required')
 old=load(OLD_BUILD/'manifest.json');pins=base.build_pins(OLD_BUILD,prior.BUILD_SHA,prior.DLL_SHA,old,81)
 if{p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}!=pins:raise ValueError('all81 active032 build hashVALUES required')
 return m,old,pins

def validate_build(m):
 if(sha(BUILD/'manifest.json')!=BUILD_SHA or m.get('build_ok')is not True or m.get('qualified')is not False or
    m.get('repo_commit')!=SOURCE or m.get('repo_tree')!=TREE or m.get('dll_sha256')!=DLL_SHA or
    m.get('candidate')!=str(BUILD/'Sources/Game/GameMP.dll')or m.get('source_overlay')!=str(BUILD/'overlay')or
    m.get('source_count')!=15 or len(m.get('source_sha256',{}))!=49 or len(m.get('overlay_sha256',{}))!=30 or
    (BUILD/'Sources/Game/GameMP.dll').stat().st_size!=DLL_SIZE):raise ValueError('exact actual034 provenance and complete closure required')
 return base.build_pins(BUILD,BUILD_SHA,DLL_SHA,m,81)

def input_delta(old,new):
 out={}
 for key in ['source_sha256','overlay_sha256']:
  if set(old[key])!=set(new[key]):raise ValueError('exact032/034 closure keysets required')
  changed=sorted(k for k in old[key]if old[key][k]!=new[key][k])
  if changed!=['BotSupplyNative.h']:raise ValueError('only actual attempt/history Header input may change')
  out[key]=dict(changed=changed,added=[],removed=[],unchanged=sorted(k for k in old[key]if k not in changed))
 return out

def prepare(destination=DESTINATION):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in [PARENT,OLD_BUILD,BUILD]):raise ValueError('fresh independent disabled destination required')
 m,old,oldpins=validate_parent();new=load(BUILD/'manifest.json');pins=validate_build(new);delta=input_delta(old,new)
 assets=assets_helper.validate_assets(load(PARENT/'map-catalog.json'))
 before=base.inventory(PARENT);changed={n:apply(n,read(PARENT/n).decode())for n in CHANGED}
 if any(apply(n,t,True).encode()!=read(PARENT/n)for n,t in changed.items()):raise ValueError('whole four-source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('author runtime gate must remain False')
 dest.mkdir(mode=0o700)
 for n in before:
  if n not in ['source-manifest.json','HANDOFF-disabled.json']:write(dest/n,changed[n].encode()if n in changed else read(PARENT/n))
 diffs=[]
 for n,t in changed.items():
  name=n+'.034trouble300.diff';diffs.append(name)
  write(dest/name,''.join(difflib.unified_diff(read(PARENT/n).decode().splitlines(True),t.splitlines(True),fromfile='immutable032Trouble600/'+n,tofile='disabled034Trouble300/'+n)).encode())
 for n in ADDITIONS:write(dest/n,read(Path(__file__).with_name(n)))
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 deps.update(pins)
 for n in ADDITIONS:deps[str(dest/n)]=sha(dest/n)
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps)or{p:h for p,h in deps.items()if Path(p).is_relative_to(BUILD)}!=pins:raise ValueError('all81 active032 deps removed and81 actual034 deps required')
 inherited={k:copy.deepcopy(m.pop(k))for k in ['candidate','comparison','map_case','build032_trouble_derivation','root_review']}
 m['inherited_build032_trouble_metadata']=dict(scope='HISTORICAL_PROVENANCE_ONLY_NOT_ACTIVE_CANDIDATE_OR_RUNTIME_DEPENDENCIES',**inherited)
 m.update(scope='DISABLED_SINGLE_BUILD034_TROUBLE300_DIAG1_SAME_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=DLL_SIZE,source_commit=SOURCE,source_tree=TREE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(inherited['comparison'],order=['034'],arm='034',seconds=300,parent_manifest_sha256=PARENT_SHA)
 m['map_case']=dict(inherited['map_case'],seconds=300,parent=str(PARENT),parent_manifest_sha256=PARENT_SHA)
 m['build034_trouble_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,input_delta=delta,old_build_targets_removed=oldpins,new_build_targets=pins,whole_four_source_inverse=True,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False,bounded_history_diagnostic='UNADMITTED/ARM/DISARM/END explain custody only; revisited_edges/newGoal/actualSameLifeUsefulGain require separate bindings; no native improvement claimed',all_other_guards_readers_limits_preserved=True,prospective_duration_change=dict(parent_seconds=600,new_seconds=300),selected_assets_checked=assets)
 m['observation_contract']=dict(seconds=300,new_condition=True,a4_qualification=False,ordinary_new_goal_and_same_life_useful_gain_required=True,missing_marker_or_native_binding='UNKNOWN_UNEXERCISED',cap_or_format_fault_or_serial_gap='FAIL_INCOMPLETE_CUSTODY',source_tick_native_clock_fusion=False,pointer_text_contract='MSVC32 eight-hex/no0x or POSIX0x/(nil); Knownbits and native identity binding remain required',accepted_proposal_is_not_movement_or_pickup=True,automatic_retry=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING Root review/freeze; exactly one034Trouble300 diagnostic observation')
 m['sources']={n:sha(dest/n)for n in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());base.verify_pins(m,dest)
 if base.inventory(PARENT)!=before:raise ValueError('immutable032 parent changed')
 equal={n:h for n,h in before.items()if n not in ['source-manifest.json','HANDOFF-disabled.json']and n not in CHANGED}
 if any(sha(dest/n)!=h for n,h in equal.items()):raise ValueError('other inherited source bytes changed')
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),old032_build_targets_removed=len(oldpins),new034_build_targets=len(pins),other_parent_files_byte_equal=len(equal),whole_four_source_inverse=True,build='034',map='trouble',seconds=300,diagnostics=1,native_started=False,runtime_reviewed=False,qualified=False)
 write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
