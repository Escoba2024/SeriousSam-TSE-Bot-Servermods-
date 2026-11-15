"""Disabled030 Skulls timestamp parent -> one disabled031 Hole600 DIAG1 case."""
import argparse,ast,copy,difflib,json,os,struct,zipfile,zlib,hashlib
from pathlib import Path
from prepare_navigation_build030_skulls import read,sha,load,opened

PARENT=Path('/srv/tse-nav20-030-skulls600-diag1-timestamps-disabled-20261115')
PARENT_SHA='2b910ac7c2dc13faac888ea932e81644656dbef9f9963c6568590eb07fef6844'
OLD_BUILD=Path('/srv/tse-milestone-a-build-030-20261115')
OLD_BUILD_SHA='89eef08dfce8f2b5f40fba0290e5778bdb42831c7280731ad5cd44c21338a5d3'
OLD_DLL='bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412'
BUILD=Path('/srv/tse-milestone-a-build-031-20261115')
BUILD_SHA='9c8cabf8d2a3a56803ac25ce8af55a38884a14de47ebeb5b1399095a2d4b40c5'
DLL_SHA='5c5c21d651f5513bcba4c1c3cc8ddc6495fbfbe7cdbbee506c70853bd15bbb0b'
SPEC_SHA='e8db049024dc7d54c2e6beeac94714615d417ea74f5d1b6968ac2e68dab32dac'
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
DESTINATION=Path('/srv/tse-nav20-031-hole600-diag1-disabled-20261115')
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build031_hole.py','navigation_build031_hole_policy.py','build031_reset_candidate.json')
HOLE={'query_name':'Hole','world_path':'Levels\\LevelsMP\\Deathmatch\\Hole.wld','world_sha256':'cd2e73d8fe103e9d85e6498318e0c75d1f4b10f3b473a2a4d735d9a7eae8166d','world_crc32':'582bd040','nav_path':'Scripts/Cecil/Hole_1AD627D0.nav','nav_sha256':'6ae46f0a18e2f5071b981f111d1dcc338a02144b963da0bdbed777a3a1ff2646','nav_crc32':'d7cac057','cecil_path_hash':'1ad627d0','nodes':139,'private_nav_source':'/srv/tse-cecil-full-private-assets-20261107/Hole_1AD627D0.nav'}
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit='226276880c847ed145ee36f1415eb53fd3c01588',dll_sha256=DLL_SHA)
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(BUILD/'Sources/Game/GameMP.dll')),
  ("PREFIX=f'ssam-nav20-030-skulls-diag1-hard-ordered-","PREFIX=f'ssam-nav20-031-hole-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-030-skulls-diag1-hard-ordered-","E=BASE/f'nav20-031-hole-diag1-hard-ordered-"),
  ('PRIVATE A4 030 HARD DIAGNOSTIC','PRIVATE A4 031 HARD DIAGNOSTIC'),
  ('Private candidate030 Skulls diagnostic observation only','Private candidate031 Hole diagnostic observation only'),
  ("choices=('skulls',)","choices=('hole',)")],
 'adapter_policy.py':[(OLD_DLL,DLL_SHA),
  ('from navigation_build030_skulls_policy import options as validate','from navigation_build031_hole_policy import options as validate'),
  ("validate(map_key,duration,diag,'030')","validate(map_key,duration,diag,'031')"),
  ("return validate(logs,'030')","return validate(logs,'031')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate"," '031': "+repr(RECORD)+',\n}\n\n\ndef candidate')],
}

def candidate():
 p=Path(__file__).with_name('build031_reset_candidate.json')
 if sha(p)!=SPEC_SHA:raise ValueError('exact existing031 closure required')
 return load(p)

def write(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 v=os.statvfs(p.parent)
 if v.f_bavail*v.f_frsize < 8*1024**3+64*1024**2+len(data):raise ValueError('8GiB plus64MiB write reserve')
 with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:
  f.write(data);f.flush();os.fsync(f.fileno())

def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('fixed three retarget files')
 for a,b in (reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:a,b=b,a
  if text.count(a)!=1 or (not reverse and b in text):raise ValueError('unique exact retarget anchor required')
  text=text.replace(a,b,1)
 ast.parse(text);return text

def validate_build(m,s):
 if (s!=candidate() or m.get('build_ok')is not True or m.get('qualified')is not False or
     m.get('repo_commit')!=s['source_commit']or m.get('repo_tree')!=s['source_tree']or
     m.get('dll_sha256')!=DLL_SHA or m.get('candidate')!=str(BUILD/'Sources/Game/GameMP.dll')or
     m.get('source_overlay')!=str(BUILD/'overlay')or m.get('source_count')!=15 or
     m.get('source_sha256')!=s['source_sha256']or m.get('overlay_sha256')!=s['overlay_sha256']or
     len(m['source_sha256'])!=49 or len(m['overlay_sha256'])!=30):raise ValueError('exact031 provenance/closure required')

def build_pins(directory,manifest_hash,dll_hash,m,count):
 if sha(directory/'manifest.json')!=manifest_hash:raise ValueError('build manifest changed')
 pins={str(directory/'manifest.json'):manifest_hash,str(directory/'Sources/Game/GameMP.dll'):dll_hash}
 for key,sub in [('source_sha256','Sources/Game'),('overlay_sha256','overlay')]:
  for name,h in m[key].items():
   p=Path(name)
   if p.is_absolute()or'..'in p.parts:raise ValueError('unsafe build source path')
   pins[str(directory/sub/p)]=h
 if len(pins)!=count:raise ValueError('full build target count required')
 for p,h in pins.items():
  if sha(p)!=h:raise ValueError('build target changed: '+p)
 return pins

def input_delta(old,new):
 out={}
 for key in ['source_sha256','overlay_sha256']:
  changed=sorted(p for p in old[key]if old[key][p]!=new[key].get(p));added=sorted(set(new[key])-set(old[key]))
  if changed!=['BotDriver.cpp','BotSupplyNative.h']or added!=['picker_custody.h']or set(old[key])-set(new[key]):raise ValueError('exact030->031 diagnostic delta required')
  out[key]=dict(changed=changed,added=added,unchanged=sorted(set(old[key])-set(changed)))
 return out

def verify_pins(m,root):
 for key,base in [('runtime_dependencies',Path('/')),('sources',root),('draft_source_sha256',root)]:
  for p,h in m[key].items():
   if sha(base/p)!=h:raise ValueError('full pin value differs: '+p)

def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled030 timestamp parent required')
 m=load(PARENT/'source-manifest.json');c=m['comparison'];p=m['map_case']
 if (any(m[k]is not False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass'])or
     c['arm']!='030'or c['map']!='skulls'or c['seconds']!=600 or c['diagnostics']!=1 or c['hard_difficulty']!=2 or c['observer_fps']!=20 or
     p['bot_count']!=8 or p['bot_tier']!=3 or m['candidate']['dll_sha256']!=OLD_DLL or
     sha(PARENT/'transaction.py')!=m['timestamp_restoration']['changed_transaction_sha256']):raise ValueError('exact parent conditions required')
 verify_pins(m,PARENT)
 if sha(PARENT/'map-catalog.json')!=CATALOG_SHA:raise ValueError('immutable map catalog required')
 return m

def validate_assets(c):
 if c['maps']['hole']!=HOLE:raise ValueError('exact Hole world/nav metadata required')
 with opened(c['archive_readonly_source'])as source,zipfile.ZipFile(source)as archive:
  world=archive.read(HOLE['world_path'].replace('\\','/'))
 nav=read(HOLE['private_nav_source'])
 for raw,key in [(world,'world'),(nav,'nav')]:
  if hashlib.sha256(raw).hexdigest()!=HOLE[key+'_sha256']or f'{zlib.crc32(raw):08x}'!=HOLE[key+'_crc32']:raise ValueError('selected Hole asset bytes differ')
 if struct.unpack_from('<4s4i',nav)[0:2]!=(b'BNMV',6)or struct.unpack_from('<i',nav,16)[0]!=139:raise ValueError('exact Hole nav header/nodes')
 return dict(map='hole',world_sha256=HOLE['world_sha256'],nav_sha256=HOLE['nav_sha256'],nodes=139,loaded_world_proven=False,archive_full_hash_recomputed=False)

def inventory(root):
 return {str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}

def prepare(destination=DESTINATION):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in [PARENT,BUILD,OLD_BUILD]):raise ValueError('fresh isolated disabled destination required')
 m=validate_parent();spec=candidate();new=load(BUILD/'manifest.json');validate_build(new,spec)
 if (BUILD/'Sources/Game/GameMP.dll').stat().st_size!=spec['dll_size']:raise ValueError('actual DLL size differs')
 old=load(OLD_BUILD/'manifest.json');oldpins=build_pins(OLD_BUILD,OLD_BUILD_SHA,OLD_DLL,old,79)
 if {p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}!=oldpins:raise ValueError('all79 active030 build pins required')
 pins=build_pins(BUILD,BUILD_SHA,DLL_SHA,new,81);delta=input_delta(old,new);assets=validate_assets(load(PARENT/'map-catalog.json'))
 changed={n:apply(n,read(PARENT/n).decode())for n in CHANGED}
 if any(apply(n,t,True).encode()!=read(PARENT/n)for n,t in changed.items()):raise ValueError('whole source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('false runtime gate required')
 before=inventory(PARENT);dest.mkdir(mode=0o700)
 for n in before:
  if n not in ['source-manifest.json','HANDOFF-disabled.json']:write(dest/n,changed[n].encode()if n in changed else read(PARENT/n))
 diffs=[]
 for n,t in changed.items():
  name=n+'.031hole.diff';diffs.append(name)
  write(dest/name,''.join(difflib.unified_diff(read(PARENT/n).decode().splitlines(True),t.splitlines(True),fromfile='disabled030-skulls-timestamp-parent',tofile='disabled031-hole600')).encode())
 for n in ADDITIONS:write(dest/n,read(Path(__file__).with_name(n)))
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 deps.update(pins)
 for n in ADDITIONS:deps[str(dest/n)]=sha(dest/n)
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps):raise ValueError('active030 build target retained')
 inherited={k:copy.deepcopy(m.pop(k))for k in ['candidate','comparison','map_case','build030_derivation','root_review']}
 m['inherited_build030_skulls_timestamp_metadata']=inherited
 m.update(scope='DISABLED_SINGLE_BUILD031_HOLE600_DIAG1_WITH_EXACT_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=spec['dll_size'],source_commit=spec['source_commit'],source_tree=spec['source_tree'],build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(inherited['comparison'],order=['031'],arm='031',map='hole',parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['map_case']=dict(inherited['map_case'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,map='hole',map_binding=HOLE,assets=assets)
 m['build031_hole_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,removed_old_build_targets=oldpins,new_build_targets=pins,input_delta=delta,whole_three_source_inverse=True,other_parent_files_byte_equal=True,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING Root review/freeze; one031 Hole600 diag1 diagnostic observation only')
 m['sources']={n:sha(dest/n)for n in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());verify_pins(m,dest)
 if inventory(PARENT)!=before:raise ValueError('immutable parent changed')
 equal=sum(n not in ['source-manifest.json','HANDOFF-disabled.json']and n not in CHANGED and sha(dest/n)==h for n,h in before.items())
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),build='031',map='hole',seconds=600,diagnostics=1,runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),other_parent_files_byte_equal=equal,whole_three_source_inverse=True,removed030_targets=len(oldpins),new031_targets=len(pins),parent_preserved=True,native_started=False,qualified=False,runtime_reviewed=False)
 write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
