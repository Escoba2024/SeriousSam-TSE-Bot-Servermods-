"""Derive a fresh disabled matched arm; do not execute any game process."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

from navigation_comparison_policy import CANDIDATES,candidate

PARENT=Path('/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114')
PARENT_SHA='a4568cbe60716887e195f7996ffeed774c1035cadcb11660b644c1fe64b4b2d9'
UNCHANGED={
 'a4_ordered_memory_v3.py':'64f402a3fbb00463fb9b2ab112427fceffe0920a2a9983841ea322b62c1e021a',
 'audit_a4_ordered_memory_v3.py':'26f7aa23061e3b8be17f2972f1e92ebe892c95eb9696aeafcf9ed4da78e8a6bf',
 'a4_fire_observer_v2.py':'201ca2d0f3098637ffb129162d84e126062df24790cfa865693781683732e5fc',
 'audit_a4_native_fire_observer_v2.py':'3ac187c8775b2bd1ed7021dc7b4037b0eeda6aec2a0292f9d87e47c9d8f4b466',
}
ADDITIONS=('navigation_comparison_policy.py','prepare_navigation_comparison.py','test_navigation_comparison.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('nonunique inherited anchor:'+old)
 return text.replace(old,new,1)


def transform_controller(text,build):
 record=candidate(build)
 old="CANDIDATE_DLL=Path('/srv/tse-milestone-a-build-020-20261114/Sources/Game/GameMP.dll')"
 text=once(text,old,"CANDIDATE_DLL=Path('"+record['directory']+"/Sources/Game/GameMP.dll')")
 text=once(text,"PREFIX=f'ssam-a4-020-hard-ordered-",f"PREFIX=f'ssam-nav-{build}-hard-ordered-")
 text=once(text,"E=BASE/f'a4-020-hard-ordered-",f"E=BASE/f'nav-{build}-hard-ordered-")
 ast.parse(text);return text


def transform_adapter(text,build):
 record=candidate(build)
 text=once(text,"CANDIDATE_SHA='"+CANDIDATES['020']['dll_sha256']+"'","CANDIDATE_SHA='"+record['dll_sha256']+"'")
 replacements={
  'options':"def options(map_key,duration,diag):\n from navigation_comparison_policy import options as validate\n validate(map_key,duration,diag,"+repr(build)+")\n",
  'check_tiers':"def check_tiers(logs):\n from navigation_comparison_policy import check_tiers as validate\n return validate(logs,"+repr(build)+")\n",
 }
 tree=ast.parse(text);lines=text.splitlines(True)
 for node in sorted((n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in replacements),key=lambda n:n.lineno,reverse=True):
  lines[node.lineno-1:node.end_lineno]=[replacements.pop(node.name)]
 if replacements:raise ValueError('missing inherited policy function')
 output=''.join(lines);ast.parse(output);return output


def validate_build(build):
 record=candidate(build);base=Path(record['directory']);manifest=base/'manifest.json'
 if sha(manifest)!=record['manifest_sha256']:raise ValueError('candidate manifest SHA')
 m=json.loads(manifest.read_text())
 if m['build_ok']is not True or m['repo_commit']!=record['source_commit']or m['dll_sha256']!=record['dll_sha256']or m['candidate']!=str(base/'Sources/Game/GameMP.dll')or m['source_overlay']!=str(base/'overlay'):
  raise ValueError('candidate build provenance')
 if len(m['source_sha256'])!=47 or len(m['overlay_sha256'])!=28:raise ValueError('complete candidate source closure required')
 pins={str(manifest):record['manifest_sha256'],m['candidate']:record['dll_sha256']}
 for key,directory in [('source_sha256',base/'Sources/Game'),('overlay_sha256',base/'overlay')]:
  for name,h in m[key].items():
   path=Path(name)
   if path.is_absolute()or'..'in path.parts:raise ValueError('candidate source path')
   pins[str(directory/path)]=h
 for p,h in pins.items():
  if sha(p)!=h:raise ValueError('candidate DLL/source hash:'+p)
 return record,pins


def prepare(destination,build):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('new comparison arm required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled parent required')
 parent=json.loads((PARENT/'source-manifest.json').read_text())
 for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
  for p,h in parent[key].items():
   if sha(PARENT/p if relative else p)!=h:raise ValueError('parent source pin:'+p)
 for filename,h in UNCHANGED.items():
  if sha(PARENT/filename)!=h:raise ValueError('inherited observer pin')
 if parent['runtime_reviewed']is not False:raise ValueError('disabled parent only')
 record,pins=validate_build(build)
 controller=transform_controller((PARENT/'run-a4.py').read_text(),build)
 adapter=transform_adapter((PARENT/'adapter_policy.py').read_text(),build)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 (dest/'run-a4.py').write_text(controller);(dest/'adapter_policy.py').write_text(adapter)
 for name,new in [('run-a4.py',controller),('adapter_policy.py',adapter)]:
  (dest/(name+'.navigation.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),new.splitlines(True),fromfile='parent/'+name,tofile=build+'/'+name)))
 deps={}
 for p,h in parent['runtime_dependencies'].items():
  path=Path(p)
  if path.is_relative_to(Path(CANDIDATES['020']['directory'])):continue
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins);deps[str(dest/'navigation_comparison_policy.py')]=sha(dest/'navigation_comparison_policy.py')
 m=dict(parent);m.update(scope='DISABLED_MATCHED_NAV_'+build+'_RED600_V3',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=record['dll_sha256'],source_commit=record['source_commit'],build_manifest=record['directory']+'/manifest.json',build_manifest_sha256=record['manifest_sha256'])
 m['canonical_profile_migration']=dict(profiles=[7,7,7,7],legacy_tier=5,arena_override=False,
  resulting_tier=5 if build=='048'else 3,resulting_name='BOT-Expert-Rifle'if build=='048'else'DEMON',
  persona='marksman'if build=='048'else'duelist',required_log='exact actual version-bound attachment schema, all locals0..3 and both groups')
 m['comparison']=dict(order=['048','018','020'],arm=build,map='redstation',seconds=600,diagnostics=0,hard_difficulty=2,dedicated='ORIGINAL_1C41',same_config_nav=True,profile_semantics='WHOLE_CANDIDATE_DIFFERENCE',automatic_sequence=False,automatic_retry=False,parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['root_review']=dict(approved_for_private_a4=False,reference='PENDING Root independent review and freeze')
 m.pop('root_freeze',None)
 m['sources']={p.name:sha(p)for p in dest.iterdir()if p.is_file()and p.name not in('source-manifest.json','HANDOFF-disabled.json')}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),build=build,manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n')
 return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);p.add_argument('--build',choices=tuple(CANDIDATES),required=True)
 args=p.parse_args();print(json.dumps(prepare(args.destination,args.build)))
