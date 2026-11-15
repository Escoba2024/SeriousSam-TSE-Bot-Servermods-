"""Exact disabled031Trouble -> one disabled032Trouble600 source preparation."""
import argparse,ast,copy,difflib,json
from pathlib import Path
import prepare_navigation_build031_hole as base
import prepare_navigation_build031_trouble as parent_helper
from prepare_navigation_build031_hole import read,sha,load,write
PARENT=Path('/srv/tse-nav20-031-trouble600-diag1-disabled-20261115')
PARENT_SHA='122e1dee0e1b620b2f764a9226c219a750b2986b53f5b9bc809c4f6c903a7989'
OLD_BUILD=base.BUILD
BUILD=Path('/srv/tse-milestone-a-build-032-20261115')
BUILD_SHA='e71f11802e83e5b1743597da48e4579cdb201ddc541fa968abb0be188877ddf6'
DLL_SHA='403fa89e6be18642cc5a699ced5cca484031eb310d56b211537f077995bdf3ce'
DLL_SIZE=463360
SOURCE='1e0077a9b7c9c4696f10afdb3155d8d0cb911306'
TREE='2e1cbcb92ce777f30e228ee5bb82088598d9aabe'
DESTINATION=Path('/srv/tse-nav20-032-trouble600-diag1-disabled-20261115')
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build032_trouble.py','navigation_build032_trouble_policy.py')
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE,dll_sha256=DLL_SHA)
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(BUILD/'Sources/Game/GameMP.dll')),
  ("PREFIX=f'ssam-nav20-031-trouble-diag1-hard-ordered-","PREFIX=f'ssam-nav20-032-trouble-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-031-trouble-diag1-hard-ordered-","E=BASE/f'nav20-032-trouble-diag1-hard-ordered-"),
  ('PRIVATE A4 031 HARD DIAGNOSTIC','PRIVATE A4 032 HARD DIAGNOSTIC'),
  ('Private candidate031 LittleTrouble diagnostic observation only','Private candidate032 LittleTrouble diagnostic observation only')],
 'adapter_policy.py':[(base.DLL_SHA,DLL_SHA),
  ('from navigation_build031_trouble_policy import options as validate','from navigation_build032_trouble_policy import options as validate'),
  ("validate(map_key,duration,diag,'031')","validate(map_key,duration,diag,'032')"),
  ("return validate(logs,'031')","return validate(logs,'032')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate"," '032': "+repr(RECORD)+',\n}\n\n\ndef candidate')],
}
def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('three exact retarget sources only')
 for a,b in(reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:a,b=b,a
  if text.count(a)!=1 or(not reverse and b in text):raise ValueError('unique exact retarget anchor required')
  text=text.replace(a,b,1)
 ast.parse(text);return text

def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('fixed031Trouble disabled parent required')
 m=load(PARENT/'source-manifest.json');c=m['comparison'];p=m['map_case']
 if(any(m[k]is not False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass'])or
    c['arm']!='031'or c['order']!=['031']or c['map']!='trouble'or c['seconds']!=600 or c['diagnostics']!=1 or c['hard_difficulty']!=2 or c['observer_fps']!=20 or
    p['map']!='trouble'or p['seconds']!=600 or p['diagnostics']!=1 or p['hard_difficulty']!=2 or p['bot_tier']!=3 or p['bot_count']!=8 or p['original_observer_fps']!=20 or
    any(x.get(k)is not False for x in [c,p]for k in ['automatic_sequence','automatic_retry','native_started'])or
    m['candidate']['dll_sha256']!=base.DLL_SHA or m['candidate']['build_manifest']!=str(OLD_BUILD/'manifest.json')or
    sha(PARENT/'transaction.py')!=m['timestamp_restoration']['changed_transaction_sha256']):raise ValueError('exact031 inherited conditions required')
 base.verify_pins(m,PARENT)
 if sha(PARENT/'map-catalog.json')!=base.CATALOG_SHA:raise ValueError('immutable mapcatalog required')
 old=load(OLD_BUILD/'manifest.json');pins=base.build_pins(OLD_BUILD,base.BUILD_SHA,base.DLL_SHA,old,81)
 if{p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}!=pins:raise ValueError('all81 active031 build hashVALUES required')
 return m,old,pins

def validate_build(m):
 if(sha(BUILD/'manifest.json')!=BUILD_SHA or m.get('build_ok')is not True or m.get('qualified')is not False or
    m.get('repo_commit')!=SOURCE or m.get('repo_tree')!=TREE or m.get('dll_sha256')!=DLL_SHA or
    m.get('candidate')!=str(BUILD/'Sources/Game/GameMP.dll')or m.get('source_overlay')!=str(BUILD/'overlay')or
    m.get('source_count')!=15 or len(m.get('source_sha256',{}))!=49 or len(m.get('overlay_sha256',{}))!=30 or
    (BUILD/'Sources/Game/GameMP.dll').stat().st_size!=DLL_SIZE):raise ValueError('exact actual032 provenance and complete closure required')
 return base.build_pins(BUILD,BUILD_SHA,DLL_SHA,m,81)

def input_delta(old,new):
 out={}
 for key in ['source_sha256','overlay_sha256']:
  if set(old[key])!=set(new[key]):raise ValueError('exact031/032 closure keysets required')
  changed=sorted(k for k in old[key]if old[key][k]!=new[key][k])
  if changed!=['BotSupplyNative.h']:raise ValueError('only atomic-replacement Header input may change')
  out[key]=dict(changed=changed,added=[],removed=[],unchanged=sorted(k for k in old[key]if k not in changed))
 return out

def prepare(destination=DESTINATION):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in [PARENT,OLD_BUILD,BUILD]):raise ValueError('fresh independent disabled destination required')
 m,old,oldpins=validate_parent();new=load(BUILD/'manifest.json');pins=validate_build(new);delta=input_delta(old,new)
 assets=parent_helper.validate_assets(load(PARENT/'map-catalog.json'))
 before=base.inventory(PARENT);changed={n:apply(n,read(PARENT/n).decode())for n in CHANGED}
 if any(apply(n,t,True).encode()!=read(PARENT/n)for n,t in changed.items()):raise ValueError('whole three-source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('author runtime gate must remain False')
 dest.mkdir(mode=0o700)
 for n in before:
  if n not in ['source-manifest.json','HANDOFF-disabled.json']:write(dest/n,changed[n].encode()if n in changed else read(PARENT/n))
 diffs=[]
 for n,t in changed.items():
  name=n+'.032trouble.diff';diffs.append(name)
  write(dest/name,''.join(difflib.unified_diff(read(PARENT/n).decode().splitlines(True),t.splitlines(True),fromfile='immutable031Trouble/'+n,tofile='disabled032Trouble/'+n)).encode())
 for n in ADDITIONS:write(dest/n,read(Path(__file__).with_name(n)))
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 deps.update(pins)
 for n in ADDITIONS:deps[str(dest/n)]=sha(dest/n)
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps)or{p:h for p,h in deps.items()if Path(p).is_relative_to(BUILD)}!=pins:raise ValueError('all81 active031 deps removed and81 actual032 deps required')
 prior={k:copy.deepcopy(m.pop(k))for k in ['candidate','comparison','map_case','build031_trouble_derivation','root_review']}
 m['inherited_build031_trouble_metadata']=dict(scope='HISTORICAL_PROVENANCE_ONLY_NOT_ACTIVE_CANDIDATE_OR_RUNTIME_DEPENDENCIES',**prior)
 m.update(scope='DISABLED_SINGLE_BUILD032_TROUBLE600_DIAG1_SAME_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=DLL_SIZE,source_commit=SOURCE,source_tree=TREE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(prior['comparison'],order=['032'],arm='032',parent_manifest_sha256=PARENT_SHA)
 m['map_case']=dict(prior['map_case'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA)
 m['build032_trouble_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,input_delta=delta,old_build_targets_removed=oldpins,new_build_targets=pins,whole_three_source_inverse=True,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False,atomic_first_weapon_replacement='SDK-proven conditional Source change only; native target transition/movement/pickup require observation; no native improvement claimed',original_bodies_readers_limits_preserved=True)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING Root review/freeze; exactly one032Trouble600 observation')
 m['sources']={n:sha(dest/n)for n in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());base.verify_pins(m,dest)
 if base.inventory(PARENT)!=before:raise ValueError('immutable031 parent changed')
 equal={n:h for n,h in before.items()if n not in ['source-manifest.json','HANDOFF-disabled.json']and n not in CHANGED}
 if any(sha(dest/n)!=h for n,h in equal.items()):raise ValueError('other inherited source bytes changed')
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),old031_build_targets_removed=len(oldpins),new032_build_targets=len(pins),other_parent_files_byte_equal=len(equal),whole_three_source_inverse=True,build='032',map='trouble',seconds=600,diagnostics=1,native_started=False,runtime_reviewed=False,qualified=False)
 write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
