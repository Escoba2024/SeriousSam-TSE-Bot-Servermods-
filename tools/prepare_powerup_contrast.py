"""Build one FRESH DISABLED existing-Dedicated flag contrast; no runtime imports."""
import argparse
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import shutil

from powerup_contrast_policy import BOT_SHA,DEDICATED_SHA,checked_flag

PARENT=Path('/srv/tse-nav20-048-red600-root-frozen-20261114')
PARENT_SHA='91a3f9c02891b39512ca25484fb4fd82d41f650ef9b953c1d941e93b8c3e04f6'
BUILD=Path('/srv/tse-dev-powerup-build-001-20261111')
OVERLAY=Path('/srv/tse-dev-powerup-overlay-001-20261111')
BUILD_SHA='b3bbd208089a41271a518142de707429732c860761e8a2c4188efdc107b0bb7f'
DLL=BUILD/'Sources/Game/GameMP.dll'
DLL_SIZE=393728
SOURCE_COMMIT='4046a59c419d1a3a6323b8516f20cc5bfddf5203'
SOURCE_TREE='ca088e12060689d531c4ddc1d909dfa635e802e3'
ORIGINAL_SHA='1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
CHANGED=('run-a4.py','adapter_policy.py')
ADDITIONS=('powerup_contrast_policy.py','prepare_powerup_contrast.py','test_powerup_contrast.py','test_prepare_powerup_contrast.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def deltas(name,flag):
 checked_flag(flag)
 if name=='adapter_policy.py':return[
  ('from navigation_comparison_policy import options as validate','from powerup_contrast_policy import options as validate'),
  ("validate(map_key,duration,diag,'048')",f'validate(map_key,duration,diag,{flag})')]
 if name!='run-a4.py':raise ValueError('fixed two retarget sources only')
 return[
  ('import adapter_policy as policy','import adapter_policy as policy\nimport powerup_contrast_policy as powerups'),
  ('RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'),
  ("CANDIDATE_DLL=Path('/srv/tse-cecil-full-build-048-20261109/Sources/Game/GameMP.dll')",
   "CANDIDATE_DLL=Path('/srv/tse-cecil-full-build-048-20261109/Sources/Game/GameMP.dll')\n"+f"DEDICATED_DLL=Path('{DLL}')\nPOWERUP_FLAG={flag}"),
  ("PREFIX=f'ssam-nav20-048-root-{map_key}-20261114'",f"PREFIX=f'ssam-powerup-048-offon{flag}-{{map_key}}-20261115'"),
  ("E=BASE/f'nav20-048-root-",f"E=BASE/f'powerup-048-offon{flag}-"),
  (' def save():'," report['powerup_contrast']=dict(flag=POWERUP_FLAG,dedicated_sha256=powerups.DEDICATED_SHA,bot_sha256=powerups.BOT_SHA,profile='BOT-Expert-Rifle/tier5/marksman',causal_claim=False)\n def save():"),
  ("expected=policy.CANDIDATE_SHA if role in ('botA','botB')else '"+ORIGINAL_SHA+"'",'expected=powerups.game_sha(role)'),
  ("config.write_text('gam_strSessionName=", "config.write_text('dev_bRemoveDamageAndInvisibility='+str(POWERUP_FLAG)+';\\ngam_strSessionName="),
  ("shutil.copy2(R/'vanilla/Bin/GameMP.dll',R/'server/Bin/GameMP.dll')","shutil.copy2(DEDICATED_DLL,R/'server/Bin/GameMP.dll')"),
  ("inventory=InventoryReader(server[0],server[1],R/'server','"+ORIGINAL_SHA+"')","inventory=InventoryReader(server[0],server[1],R/'server',powerups.DEDICATED_SHA)"),
  ("'scope':'OWN_ORIGINAL_SERVER_READONLY_NONATOMIC'","'scope':'OWN_FILTER_DEDICATED_ORIGINAL_ENGINE_ENTITIES_READONLY_NONATOMIC'"),
  ("   policy.prepared.check_loads(map_data,load_logs,(R/'server/Dedicated_BotTest.log').read_text(errors='replace'))",
   "   server_log=(R/'server/Dedicated_BotTest.log').read_text(errors='replace');powerups.archive_log(E/'powerup-before-release.log',server_log)\n   report['powerup_census_before_release']=powerups.census(server_log,POWERUP_FLAG);save()\n   policy.prepared.check_loads(map_data,load_logs,server_log)"),
  ("report['scope']='A4_NATIVE_OBSERVATION_REQUIRES_FUNCTIONAL_REVIEW'","report['scope']='POWERUP_FLAG_SYNC_OBSERVATION_ONLY_NOT_FUNCTIONAL_OR_CAUSAL'"),
  ("   policy.prepared.check_loads(map_data,{role:(R/role/'SeriousSam.log').read_text(errors='replace')for role in ('botA','botB')},(R/'server/Dedicated_BotTest.log').read_text(errors='replace'))",
   "   server_log=(R/'server/Dedicated_BotTest.log').read_text(errors='replace');powerups.archive_log(E/'powerup-window-end.log',server_log)\n   report['powerup_census_window_end']=powerups.census(server_log,POWERUP_FLAG);save()\n   policy.prepared.check_loads(map_data,{role:(R/role/'SeriousSam.log').read_text(errors='replace')for role in ('botA','botB')},server_log)")]


def apply(name,text,flag,reverse=False):
 pairs=deltas(name,flag)
 for before,after in(reversed(pairs)if reverse else pairs):
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact retarget anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text,flag):return apply(name,text,flag)
def reverse(name,text,flag):return apply(name,text,flag,True)
def normalize_arm(text,flag):
 checked_flag(flag)
 return text.replace(f'POWERUP_FLAG={flag}','POWERUP_FLAG=ARM').replace(f'offon{flag}-','offonARM-').replace(f'validate(map_key,duration,diag,{flag})','validate(map_key,duration,diag,ARM)')


def dedicated_pins(m):
 if(m['build_ok']is not True or m['repo_commit']!=SOURCE_COMMIT or m['repo_tree']!=SOURCE_TREE
    or m['candidate']!=str(DLL)or m['dll_sha256']!=DEDICATED_SHA
    or m['source_overlay']!=str(OVERLAY)or m['source_count']!=15):raise ValueError('existing dedicated provenance changed')
 if len(m['source_sha256'])!=49 or len(m['overlay_sha256'])!=30:raise ValueError('complete existing49/30 dedicated closure required')
 pins={str(BUILD/'manifest.json'):BUILD_SHA,str(DLL):DEDICATED_SHA}
 for key,directory in[('source_sha256',BUILD/'Sources/Game'),('overlay_sha256',OVERLAY)]:
  for name,h in m[key].items():
   path=Path(name)
   if path.is_absolute()or'..'in path.parts:raise ValueError('dedicated closure path')
   pins[str(directory/path)]=h
 if len(pins)!=81:raise ValueError('unique81 dedicated closure required')
 return pins


def validate_dedicated():
 if sha(BUILD/'manifest.json')!=BUILD_SHA:raise ValueError('dedicated manifest changed')
 pins=dedicated_pins(json.loads((BUILD/'manifest.json').read_text()))
 if DLL.stat().st_size!=DLL_SIZE:raise ValueError('dedicated DLL size changed')
 for path,h in pins.items():
  if sha(path)!=h:raise ValueError('dedicated source/DLL changed: '+path)
 return pins


def validate_parent_manifest(m):
 c=m['comparison']
 if(m['runtime_reviewed']is not True or m['runtime_performed']is not False or m['qualified']is not False or m['functional_pass']is not False
    or c['arm']!='048'or c['map']!='redstation'or c['seconds']!=600 or c['diagnostics']!=0
    or c['hard_difficulty']!=2 or c['observer_fps']!=20 or c['dedicated']!='ORIGINAL_1C41'
    or c['automatic_retry']is not False or c['automatic_sequence']is not False
    or m['candidate']['dll_sha256']!=BOT_SHA):raise ValueError('exact frozen048 Red600 parent conditions required')


def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());validate_parent_manifest(m)
 for group,base in[('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for name,h in m[group].items():
   if sha(base/name)!=h:raise ValueError('parent source/config/dependency changed: '+name)
 return m


def prepare(destination,flag):
 checked_flag(flag);dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in(PARENT,BUILD,OVERLAY)):raise ValueError('fresh independent disabled destination required')
 m=validate_parent();pins=validate_dedicated();changed={name:transform(name,(PARENT/name).read_text(),flag)for name in CHANGED}
 for name,text in changed.items():
  if reverse(name,text,flag)!=(PARENT/name).read_text():raise ValueError('exact whole-source inverse failed')
  other=transform(name,(PARENT/name).read_text(),1-flag)
  if normalize_arm(text,flag)!=normalize_arm(other,1-flag):raise ValueError('uncontrolled arm source difference')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():
  (dest/name).write_text(text)
  (dest/(name+'.powerup.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),text.splitlines(True),fromfile='frozen048/'+name,tofile=f'disabledOFFON{flag}/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins);deps[str(dest/'powerup_contrast_policy.py')]=sha(dest/'powerup_contrast_policy.py')
 inherited={k:copy.deepcopy(m[k])for k in('comparison','root_review','root_freeze')}
 m['inherited048_powerup_parent_metadata']=inherited
 m['runtime_dependencies']=deps
 m.update(scope='DISABLED_EXISTING_DEDICATED_POWERUP_FLAG_CONTRAST_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['comparison']=dict(inherited['comparison'],arm=f'OFFON{flag}',order=[f'OFFON{flag}'],dedicated=DEDICATED_SHA,profile_semantics='IDENTICAL_048_EXPERT_RIFLE_BOTH_ARMS',parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['root_review']=dict(approved_for_private_nav_comparison=False,approved_for_private_a4=False,approved_for_private_powerup_contrast=False,native_qualified=False,reference='PENDING Root review and own freeze; no automatic runtime')
 m.pop('root_freeze',None)
 m['powerup_contrast']=dict(flag=flag,dedicated_sha256=DEDICATED_SHA,dedicated_size=DLL_SIZE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,closure_targets=81,parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,bot_sha256=BOT_SHA,profile=dict(name='BOT-Expert-Rifle',tier=5,persona='marksman',canonical_index=7),single_gameplay_contrast='dev_bRemoveDamageAndInvisibility=0/1 before NewGame',other_arm_not_automatically_run=True,causal_claim=False,original_dedicated_control_repeated=False,zero_affected_result='UNINFORMATIVE_FAIL',inherited_limited_status_is_not_functional_qualification=True)
 names=set(m['sources'])|set(ADDITIONS)|{name+'.powerup.diff'for name in CHANGED}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={path.name:sha(path)for path in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),flag=flag,manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),dedicated_closure_pins=81,native_started=False,runtime_reviewed=False,qualified=False,functional_pass=False)
 (dest/'HANDOFF-disabled-powerup.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);p.add_argument('--flag',type=int,choices=(0,1),required=True)
 args=p.parse_args();print(json.dumps(prepare(args.destination,args.flag),indent=2))
