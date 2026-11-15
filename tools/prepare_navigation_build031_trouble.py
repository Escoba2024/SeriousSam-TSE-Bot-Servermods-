"""Fixed Hole031-D -> one disabled LittleTrouble031600 diagnostic case."""
import argparse,ast,copy,difflib,hashlib,json,struct,zipfile,zlib
from pathlib import Path
import prepare_navigation_build031_hole as hole
from prepare_navigation_build031_hole import read,sha,load,write,opened
PARENT=Path('/srv/tse-nav20-031-hole600-diag1-disabled-20261115')
PARENT_SHA='f1557ca679ed5511a98fb6ece6863ea729be706d5846337f05f61d0d2e9224ca'
DESTINATION=Path('/srv/tse-nav20-031-trouble600-diag1-disabled-20261115')
CHANGED=('run-a4.py','adapter_policy.py')
ADDITIONS=('prepare_navigation_build031_trouble.py','navigation_build031_trouble_policy.py')
TROUBLE={'query_name':'Little Trouble','world_path':'Levels\\LevelsMP\\Deathmatch\\DM_LittleTrouble.wld','world_sha256':'e74e48e99bcc6e945500e1f28921c443515898791bfbca4d7ebf1ae61a26593c','world_crc32':'4060d0dd','nav_path':'Scripts/Cecil/DM_LittleTrouble_6C64BF87.nav','nav_sha256':'252d7e4c003804fe9ae2afef359843feb39b5dda29c1d6eadb0835fbe64a30ac','nav_crc32':'980013d4','cecil_path_hash':'6c64bf87','nodes':110,'private_nav_source':'/srv/tse-cecil-full-private-assets-20261107/DM_LittleTrouble_6C64BF87.nav'}
DELTAS={
 'run-a4.py':[("PREFIX=f'ssam-nav20-031-hole-diag1-hard-ordered-","PREFIX=f'ssam-nav20-031-trouble-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-031-hole-diag1-hard-ordered-","E=BASE/f'nav20-031-trouble-diag1-hard-ordered-"),
  ('Private candidate031 Hole diagnostic observation only','Private candidate031 LittleTrouble diagnostic observation only'),
  ("choices=('hole',)","choices=('trouble',)")],
 'adapter_policy.py':[('from navigation_build031_hole_policy import options as validate','from navigation_build031_trouble_policy import options as validate')],
}

def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('exact two retarget sources only')
 for a,b in (reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:a,b=b,a
  if text.count(a)!=1 or(not reverse and b in text):raise ValueError('exact unique retarget anchor required')
  text=text.replace(a,b,1)
 ast.parse(text);return text

def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact Hole031 disabled parent required')
 m=load(PARENT/'source-manifest.json');c=m['comparison'];p=m['map_case']
 if (any(m[k]is not False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass'])or
     c['arm']!='031'or c['map']!='hole'or c['seconds']!=600 or c['diagnostics']!=1 or c['hard_difficulty']!=2 or c['observer_fps']!=20 or
     p['map']!='hole'or p['seconds']!=600 or p['diagnostics']!=1 or p['bot_count']!=8 or p['bot_tier']!=3 or p['original_observer_fps']!=20 or
     m['candidate']['dll_sha256']!=hole.DLL_SHA or m['candidate']['build_manifest']!=str(hole.BUILD/'manifest.json')):
  raise ValueError('exact031 Hole inherited conditions required')
 hole.verify_pins(m,PARENT)
 if sha(PARENT/'map-catalog.json')!=hole.CATALOG_SHA:raise ValueError('immutable catalog required')
 spec=hole.candidate();build=hole.load(hole.BUILD/'manifest.json');hole.validate_build(build,spec)
 pins=hole.build_pins(hole.BUILD,hole.BUILD_SHA,hole.DLL_SHA,build,81)
 if (hole.BUILD/'Sources/Game/GameMP.dll').stat().st_size!=spec['dll_size']or{p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(hole.BUILD)}!=pins:
  raise ValueError('all81 identical active031 build pins required')
 if sha(PARENT/'transaction.py')!=m['timestamp_restoration']['changed_transaction_sha256']:raise ValueError('unchanged both-ns transaction required')
 return m,pins

def validate_assets(c):
 if c['maps']['trouble']!=TROUBLE:raise ValueError('exact existing LittleTrouble metadata required')
 with opened(c['archive_readonly_source'])as f,zipfile.ZipFile(f)as archive:world=archive.read(TROUBLE['world_path'].replace('\\','/'))
 nav=read(TROUBLE['private_nav_source'])
 for raw,key in [(world,'world'),(nav,'nav')]:
  if hashlib.sha256(raw).hexdigest()!=TROUBLE[key+'_sha256']or f'{zlib.crc32(raw):08x}'!=TROUBLE[key+'_crc32']:raise ValueError('selected LittleTrouble bytes differ')
 if struct.unpack_from('<4s4i',nav)[0:2]!=(b'BNMV',6)or struct.unpack_from('<i',nav,16)[0]!=110:raise ValueError('LittleTrouble nav header/nodes differ')
 return dict(map='trouble',world_sha256=TROUBLE['world_sha256'],nav_sha256=TROUBLE['nav_sha256'],nodes=110,loaded_world_proven=False,archive_full_hash_recomputed=False)

def prepare(destination=DESTINATION):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in [PARENT,hole.PARENT,hole.BUILD,hole.OLD_BUILD]):raise ValueError('fresh independent disabled destination required')
 m,pins=validate_parent();assets=validate_assets(load(PARENT/'map-catalog.json'))
 changed={n:apply(n,read(PARENT/n).decode())for n in CHANGED}
 if any(apply(n,t,True).encode()!=read(PARENT/n)for n,t in changed.items()):raise ValueError('whole two-source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('disabled author gate required')
 before=hole.inventory(PARENT);dest.mkdir(mode=0o700)
 for n in before:
  if n not in ['source-manifest.json','HANDOFF-disabled.json']:write(dest/n,changed[n].encode()if n in changed else read(PARENT/n))
 diffs=[]
 for n,t in changed.items():
  name=n+'.031trouble.diff';diffs.append(name)
  write(dest/name,''.join(difflib.unified_diff(read(PARENT/n).decode().splitlines(True),t.splitlines(True),fromfile='immutable031-hole-parent',tofile='disabled031-LittleTrouble')).encode())
 for n in ADDITIONS:write(dest/n,read(Path(__file__).with_name(n)))
 deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 for n in ADDITIONS:deps[str(dest/n)]=sha(dest/n)
 if {p:h for p,h in deps.items()if Path(p).is_relative_to(hole.BUILD)}!=pins:raise ValueError('unchanged81 build dependency values required')
 prior={k:copy.deepcopy(m.pop(k))for k in ['comparison','map_case','build031_hole_derivation','root_review']}
 m['inherited_build031_hole_metadata']=prior
 m.update(scope='DISABLED_SINGLE_BUILD031_LITTLE_TROUBLE600_DIAG1_WITH_EXACT_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
 m['comparison']=dict(prior['comparison'],map='trouble',parent_manifest_sha256=PARENT_SHA)
 m['map_case']=dict(prior['map_case'],map='trouble',map_binding=TROUBLE,assets=assets,parent=str(PARENT),parent_manifest_sha256=PARENT_SHA)
 m['build031_trouble_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,unchanged_build_targets=pins,whole_two_source_inverse=True,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING Root review/freeze; exactly one031 LittleTrouble600 diag1 observation')
 m['sources']={n:sha(dest/n)for n in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
 m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());hole.verify_pins(m,dest)
 if hole.inventory(PARENT)!=before:raise ValueError('immutable Hole parent changed')
 equal={n:h for n,h in before.items()if n not in ['source-manifest.json','HANDOFF-disabled.json']and n not in CHANGED}
 if any(sha(dest/n)!=h for n,h in equal.items()):raise ValueError('other inherited bytes changed')
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),other_parent_files_byte_equal=len(equal),unchanged_build_targets=len(pins),whole_two_source_inverse=True,build='031',map='trouble',seconds=600,diagnostics=1,native_started=False,qualified=False,runtime_reviewed=False)
 write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=DESTINATION)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
