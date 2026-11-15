"""Exact disabled034Trouble300 -> one disabled035Trouble300; no runtime."""
import argparse,ast,copy,difflib,json,os
from pathlib import Path
import prepare_navigation_build031_hole as base
import prepare_navigation_build031_trouble as assets_helper
import prepare_navigation_build034_trouble as prior
from prepare_navigation_build031_hole import read,sha,load,write

PARENT=Path('/srv/tse-nav20-034-trouble300-diag1-disabled-20261115')
PARENT_SHA='933f1c3d670aae78c28b26d1ec7178e5253313274cdc713081322c2719f4c870'
OLD_BUILD=prior.BUILD
BUILD=Path('/srv/tse-milestone-a-build-035-20261115')
BUILD_SHA='942b4922d1b36b64e96ed998661d2ce23b9ce04508210639bf65425c5c98aa7b'
DLL_SHA='e76395a7cb9fc4ea436cc09e9d86b0774f64b8b8df100fa722f4790afe19cae5'
DLL_SIZE=468480
SOURCE='a3af688863da3c11122e441710602ea80ea24db7'
TREE='5700f0c281b0104567e0652a7d332be614071982'
DESTINATION=Path('/srv/tse-nav20-035-trouble300-diag1-disabled-20261115')
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build035_trouble.py','navigation_build035_trouble_policy.py')
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE,dll_sha256=DLL_SHA)
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(BUILD/'Sources/Game/GameMP.dll')),
  ("PREFIX=f'ssam-nav20-034-trouble300-diag1-hard-ordered-","PREFIX=f'ssam-nav20-035-trouble300-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-034-trouble300-diag1-hard-ordered-","E=BASE/f'nav20-035-trouble300-diag1-hard-ordered-"),
  ('PRIVATE A4 034 HARD DIAGNOSTIC','PRIVATE A4 035 HARD DIAGNOSTIC'),
  ('Private candidate034 LittleTrouble300 diagnostic observation only','Private candidate035 LittleTrouble300 diagnostic observation only')],
 'adapter_policy.py':[(prior.DLL_SHA,DLL_SHA),
  ('from navigation_build034_trouble_policy import options as validate','from navigation_build035_trouble_policy import options as validate'),
  ("validate(map_key,duration,diag,'034')","validate(map_key,duration,diag,'035')"),
  ("return validate(logs,'034')","return validate(logs,'035')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate"," '035': "+repr(RECORD)+',\n}\n\n\ndef candidate')],
}

def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('three exact retarget sources only')
 original=read(PARENT/name).decode()
 if not reverse and text!=original:raise ValueError('entire immutable034 source required')
 for a,b in(reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:a,b=b,a
  if text.count(a)!=1 or(not reverse and b in text):raise ValueError('unique exact retarget anchor required')
  text=text.replace(a,b,1)
 ast.parse(text)
 if reverse and text!=original:raise ValueError('entire035 inverse must equal034 source')
 return text

def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('fixed034Trouble300 disabled parent required')
 m=load(PARENT/'source-manifest.json');c=m['comparison'];p=m['map_case']
 if(any(m[k]is not False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass'])or
    c['arm']!='034'or c['order']!=['034']or c['map']!='trouble'or c['seconds']!=300 or c['diagnostics']!=1 or c['hard_difficulty']!=2 or c['observer_fps']!=20 or
    p['map']!='trouble'or p['seconds']!=300 or p['diagnostics']!=1 or p['hard_difficulty']!=2 or p['bot_tier']!=3 or p['bot_count']!=8 or p['original_observer_fps']!=20 or
    any(x.get(k)is not False for x in [c,p]for k in ['automatic_sequence','automatic_retry','native_started'])or
    m['observation_contract']['seconds']!=300 or m['candidate']['dll_sha256']!=prior.DLL_SHA or m['candidate']['build_manifest']!=str(OLD_BUILD/'manifest.json')or
    sha(PARENT/'transaction.py')!=m['timestamp_restoration']['changed_transaction_sha256']):raise ValueError('exact034 inherited300s conditions required')
 base.verify_pins(m,PARENT)
 if sha(PARENT/'map-catalog.json')!=base.CATALOG_SHA:raise ValueError('immutable mapcatalog required')
 old=load(OLD_BUILD/'manifest.json');pins=base.build_pins(OLD_BUILD,prior.BUILD_SHA,prior.DLL_SHA,old,81)
 if{p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}!=pins:raise ValueError('all81 active034 build hashVALUES required')
 return m,old,pins

def validate_build(m):
 if(sha(BUILD/'manifest.json')!=BUILD_SHA or m.get('build_ok')is not True or m.get('qualified')is not False or
    m.get('repo_commit')!=SOURCE or m.get('repo_tree')!=TREE or m.get('dll_sha256')!=DLL_SHA or
    m.get('candidate')!=str(BUILD/'Sources/Game/GameMP.dll')or m.get('source_overlay')!=str(BUILD/'overlay')or
    m.get('source_count')!=15 or len(m.get('source_sha256',{}))!=49 or len(m.get('overlay_sha256',{}))!=30 or
    (BUILD/'Sources/Game/GameMP.dll').stat().st_size!=DLL_SIZE):raise ValueError('exact actual035 provenance and full81 closure required')
 return base.build_pins(BUILD,BUILD_SHA,DLL_SHA,m,81)

def input_delta(old,new):
 # Same strict keyset/Header-only comparison already used by034 preparation.
 return prior.input_delta(old,new)

def prepare(destination=DESTINATION):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in [PARENT,OLD_BUILD,BUILD]):raise ValueError('fresh independent disabled destination required')
 m,old,oldpins=validate_parent();new=load(BUILD/'manifest.json');pins=validate_build(new);delta=input_delta(old,new)
 assets=assets_helper.validate_assets(load(PARENT/'map-catalog.json'))
 before=base.inventory(PARENT);changed={n:apply(n,read(PARENT/n).decode())for n in CHANGED}
 if any(apply(n,t,True).encode()!=read(PARENT/n)for n,t in changed.items()):raise ValueError('whole three-source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('author runtime gate must remain False')
 additions={n:read(Path(__file__).with_name(n))for n in ADDITIONS}
 diffs={n+'.035trouble300.diff':''.join(difflib.unified_diff(read(PARENT/n).decode().splitlines(True),t.splitlines(True),fromfile='immutable034Trouble300/'+n,tofile='disabled035Trouble300/'+n)).encode()for n,t in changed.items()}
 copy_bound=sum((PARENT/n).stat().st_size for n in before)+sum(map(len,additions.values()))+sum(map(len,diffs.values()))+1024**2
 v=os.statvfs(dest.parent)
 if v.f_bavail*v.f_frsize<8*1024**3+64*1024**2+copy_bound:raise ValueError('8GiB floor +64MiB safety +whole bounded copy reserve')
 dest.mkdir(mode=0o700)
 for n in before:
  if n not in ['source-manifest.json','HANDOFF-disabled.json']:write(dest/n,changed[n].encode()if n in changed else read(PARENT/n))
 for n,b in diffs.items():write(dest/n,b)
 for n,b in additions.items():write(dest/n,b)
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 deps.update(pins)
 for n in ADDITIONS:deps[str(dest/n)]=sha(dest/n)
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps)or{p:h for p,h in deps.items()if Path(p).is_relative_to(BUILD)}!=pins:raise ValueError('all81 old034 targets removed and81 actual035 hashVALUES required')
 inherited={k:copy.deepcopy(m.pop(k))for k in ['candidate','comparison','map_case','build034_trouble_derivation','root_review']}
 m['inherited_build034_trouble_metadata']=dict(scope='HISTORICAL_PROVENANCE_ONLY_NOT_ACTIVE_CANDIDATE_OR_RUNTIME_DEPENDENCIES',**inherited)
 m.update(scope='DISABLED_SINGLE_BUILD035_TROUBLE300_DIAG1_SAME_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=DLL_SIZE,source_commit=SOURCE,source_tree=TREE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(inherited['comparison'],order=['035'],arm='035',parent_manifest_sha256=PARENT_SHA)
 m['map_case']=dict(inherited['map_case'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA)
 m['build035_trouble_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,input_delta=delta,old_build_targets_removed=oldpins,new_build_targets=pins,whole_three_source_inverse=True,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False,duration_changed=False,diagnostics_changed=False,selected_assets_checked=assets,all_other_guards_readers_limits_preserved=True)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING Root review/freeze; exactly one035Trouble300 diagnostic observation')
 m['sources']={n:sha(dest/n)for n in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());base.verify_pins(m,dest)
 if base.inventory(PARENT)!=before:raise ValueError('immutable034 parent changed')
 equal={n:h for n,h in before.items()if n not in ['source-manifest.json','HANDOFF-disabled.json']and n not in CHANGED}
 if any(sha(dest/n)!=h for n,h in equal.items()):raise ValueError('other inherited source bytes changed')
 actual_bytes=sum(p.stat().st_size for p in dest.rglob('*')if p.is_file())
 if actual_bytes>copy_bound:raise ValueError('declared copy bound exceeded')
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),old034_build_targets_removed=len(oldpins),new035_build_targets=len(pins),other_parent_files_byte_equal=len(equal),whole_three_source_inverse=True,build='035',map='trouble',seconds=300,diagnostics=1,copy_bound=copy_bound,copied_bytes=actual_bytes,native_started=False,runtime_reviewed=False,qualified=False,functional_pass=False)
 write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
