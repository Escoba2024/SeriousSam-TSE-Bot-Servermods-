"""Exact029 timestamp-parent -> ONE DISABLED030 Skulls600 retarget. No runtime imports."""
import argparse
import ast
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import zipfile
import zlib
from navigation_build030_skulls_policy import EXPECTED_SOURCES, EXPECTED_OVERLAY

PARENT=Path('/srv/tse-nav20-029-skulls600-diag1-timestamps-disabled-20261115')
PARENT_SHA='cb35162436f466b697f00b53cc04ace272c04f059a8a6464dcaed4aead406c36'
OLD_BUILD=Path('/srv/tse-milestone-a-build-029-20261115')
OLD_BUILD_SHA='aed7a9325b1cfe3af3cb77ca897901e48236de83d9b5ff0bb5d48eab23e046a9'
OLD_DLL_SHA='a043de1e0fc647d2805c20ea01e9f52eada3fdaa0b55caad8be6df5302ded971'
BUILD=Path('/srv/tse-milestone-a-build-030-20261115')
BUILD_SHA='89eef08dfce8f2b5f40fba0290e5778bdb42831c7280731ad5cd44c21338a5d3'
SOURCE_COMMIT='7aedcdb21f7180b9abfeed2ea9e8bbbf5553564e'
SOURCE_TREE='e48736240423b15d0d31af8508418b9dae8e1ae3'
DLL=BUILD/'Sources/Game/GameMP.dll'
DLL_SHA='bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412'
DLL_SIZE=454144
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
CHANGED=('run-a4.py','adapter_policy.py','navigation_comparison_policy.py')
ADDITIONS=('prepare_navigation_build030_skulls.py','navigation_build030_skulls_policy.py')
DIFF_NAMES=tuple(name+'.030skulls-diag1.diff'for name in CHANGED)
RECORD=dict(directory=str(BUILD),manifest_sha256=BUILD_SHA,source_commit=SOURCE_COMMIT,dll_sha256=DLL_SHA)
CATALOG_ENTRY=" '030': "+repr(RECORD)+',\n'
DELTAS={
 'run-a4.py':[(str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(DLL)),
  ("PREFIX=f'ssam-nav20-029-skulls-diag1-hard-ordered-","PREFIX=f'ssam-nav20-030-skulls-diag1-hard-ordered-"),
  ("E=BASE/f'nav20-029-skulls-diag1-hard-ordered-","E=BASE/f'nav20-030-skulls-diag1-hard-ordered-"),
  ('PRIVATE A4 029 HARD DIAGNOSTIC','PRIVATE A4 030 HARD DIAGNOSTIC'),
  ('Private candidate029 Skulls diagnostic observation only','Private candidate030 Skulls diagnostic observation only')],
 'adapter_policy.py':[(OLD_DLL_SHA,DLL_SHA),
  ('from navigation_build029_skulls_policy import options as validate','from navigation_build030_skulls_policy import options as validate'),
  ("validate(map_key,duration,diag,'029')","validate(map_key,duration,diag,'030')"),
  ("return validate(logs,'029')","return validate(logs,'030')")],
 'navigation_comparison_policy.py':[("}\n\n\ndef candidate",CATALOG_ENTRY+"}\n\n\ndef candidate")],
}


def opened(path):
 # Explicitly resolve symlinks, then refuse another final-component symlink.
 # No fallback: independent fixture checks must not change access timestamps.
 return os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')


def read(path):
 with opened(path)as f:
  before=os.fstat(f.fileno());data=f.read();after=os.fstat(f.fileno())
 if (not stat.S_ISREG(before.st_mode)or
     (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_atime_ns)!=
     (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_atime_ns)):
  raise ValueError('source changed during no-atime read: '+str(path))
 return data


def sha(path):return hashlib.sha256(read(path)).hexdigest()
def load(path):return json.loads(read(path))
def write(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:
  f.write(data);f.flush();os.fsync(f.fileno())


def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('fixed three retarget sources only')
 if not reverse and any(after in text for _,after in DELTAS[name]):raise ValueError('already/partly retargeted source')
 for a,b in (reversed(DELTAS[name])if reverse else DELTAS[name]):
  if reverse:a,b=b,a
  if text.count(a)!=1:raise ValueError('unique retarget anchor required: '+a)
  text=text.replace(a,b,1)
 ast.parse(text);return text


def build_pins(directory,manifest_hash,dll_hash,m):
 if sha(directory/'manifest.json')!=manifest_hash:raise ValueError('build manifest changed')
 result={str(directory/'manifest.json'):manifest_hash,str(directory/'Sources/Game/GameMP.dll'):dll_hash}
 for key,sub in (('source_sha256','Sources/Game'),('overlay_sha256','overlay')):
  for name,pin in m[key].items():
   p=Path(name)
   if p.is_absolute()or'..'in p.parts:raise ValueError('build source path changed')
   result[str(directory/sub/p)]=pin
 if len(result)!=79:raise ValueError('exact79 build targets required')
 for path,pin in result.items():
  if sha(path)!=pin:raise ValueError('build target changed: '+path)
 return result


def validate_builds(m):
 old=load(OLD_BUILD/'manifest.json');new=load(BUILD/'manifest.json')
 if (new['build_ok']is not True or new['qualified']is not False or new['repo_commit']!=SOURCE_COMMIT or
     new['repo_tree']!=SOURCE_TREE or new['dll_sha256']!=DLL_SHA or new['candidate']!=str(DLL)or
     new['source_overlay']!=str(BUILD/'overlay')or new['source_count']!=15 or DLL.stat().st_size!=DLL_SIZE or
     new['source_sha256']!=EXPECTED_SOURCES or new['overlay_sha256']!=EXPECTED_OVERLAY):
  raise ValueError('complete exact030 build provenance/maps required')
 oldpins=build_pins(OLD_BUILD,OLD_BUILD_SHA,OLD_DLL_SHA,old)
 actual={p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(OLD_BUILD)}
 if actual!=oldpins:raise ValueError('complete exact79 old029 build targets required')
 delta={}
 for key in ('source_sha256','overlay_sha256'):
  if set(old[key])!=set(new[key]):raise ValueError('build closure file set changed')
  changed=sorted(k for k in old[key]if old[key][k]!=new[key][k])
  if changed!=['BotSupplyNative.h']or old[key]['BotSupplyNative.h']!='72cea9c22d1a781bac8e1b733f63c22368f4cee8e0f3c3677067e571af8040bd':
   raise ValueError('030 only existing Header correction allowed')
  delta[key]=dict(changed=changed,unchanged=sorted(set(old[key])-set(changed)))
 return oldpins,build_pins(BUILD,BUILD_SHA,DLL_SHA,new),delta


def validate_parent():
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact timestamp029 parent manifest required')
 m=load(PARENT/'source-manifest.json');c=m['comparison'];case=m['map_case']
 if (m['runtime_reviewed']is not False or m['qualified']is not False or m['functional_pass']is not False or
     m['runtime_performed']is not False or c['arm']!='029'or c['map']!='skulls'or c['seconds']!=600 or
     c['diagnostics']!=1 or c['hard_difficulty']!=2 or c['observer_fps']!=20 or
     case['map']!='skulls'or case['seconds']!=600 or case['diagnostics']!=1 or case['hard_difficulty']!=2 or
     case['bot_count']!=8 or case['bot_tier']!=3 or case['original_observer_fps']!=20 or
     m['candidate']['dll_sha256']!=OLD_DLL_SHA or m['candidate']['build_manifest']!=str(OLD_BUILD/'manifest.json')or
     m['timestamp_restoration']['changed_transaction_sha256']!=sha(PARENT/'transaction.py')):
  raise ValueError('disabled029 exact inherited conditions required')
 for key,base in (('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)):
  for path,pin in m[key].items():
   if sha(base/path)!=pin:raise ValueError('parent pin changed: '+path)
 if sha(PARENT/'map-catalog.json')!=CATALOG_SHA:raise ValueError('map catalog changed')
 return m


def validate_assets(catalog):
 # Same selected-world/nav hash+CRC/header/nodes predicates as the inherited
 # qualified map builder, with only explicit no-atime file handles substituted.
 m=catalog['maps']['skulls']
 with opened(catalog['archive_readonly_source'])as source,zipfile.ZipFile(source)as archive:
  world=archive.read(m['world_path'].replace('\\','/'))
 nav=read(m['private_nav_source'])
 for raw,kind in ((world,'world'),(nav,'nav')):
  if hashlib.sha256(raw).hexdigest()!=m[kind+'_sha256']or f'{zlib.crc32(raw):08x}'!=m[kind+'_crc32']:
   raise ValueError('selected Skulls asset hash/CRC changed')
 if struct.unpack_from('<4s4i',nav)[0:2]!=(b'BNMV',6)or struct.unpack_from('<i',nav,16)[0]!=m['nodes']:
  raise ValueError('selected nav header/nodes changed')
 return dict(map='skulls',world_sha256=m['world_sha256'],nav_sha256=m['nav_sha256'],nodes=m['nodes'],loaded_world_proven=False,archive_full_hash_recomputed=False)


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists()or any(dest.is_relative_to(p)for p in (PARENT,BUILD,OLD_BUILD)):
  raise ValueError('fresh independent disabled destination required')
 m=validate_parent();oldpins,pins,delta=validate_builds(m);assets=validate_assets(load(PARENT/'map-catalog.json'))
 changed={name:apply(name,read(PARENT/name).decode())for name in CHANGED}
 for name,text in changed.items():
  if apply(name,text,True)!=read(PARENT/name).decode():raise ValueError('whole retarget source inverse differs')
 if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('disabled runtime gate required')
 dest.mkdir(mode=0o700)
 for path in PARENT.rglob('*'):
  if path.is_file()and '__pycache__'not in path.parts and path.suffix!='.pyc':
   rel=path.relative_to(PARENT)
   if str(rel)not in ('source-manifest.json','HANDOFF-disabled.json')and str(rel)not in CHANGED:write(dest/rel,read(path))
 for name,text in changed.items():
  write(dest/name,text.encode())
  write(dest/(name+'.030skulls-diag1.diff'),''.join(difflib.unified_diff(read(PARENT/name).decode().splitlines(True),text.splitlines(True),fromfile='disabled029-timestamp-parent',tofile='disabled030-source')).encode())
 for name in ADDITIONS:write(dest/name,read(Path(__file__).with_name(name)))
 deps={}
 for path,pin in m['runtime_dependencies'].items():
  q=Path(path)
  if q.is_relative_to(OLD_BUILD):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);pin=sha(q)
  deps[str(q)]=pin
 deps.update(pins);deps[str(dest/'navigation_build030_skulls_policy.py')]=sha(dest/'navigation_build030_skulls_policy.py')
 if any(Path(p).is_relative_to(OLD_BUILD)for p in deps):raise ValueError('old029 active build target retained')
 inherited={k:copy.deepcopy(m[k])for k in ('candidate','comparison','map_case')}
 m['inherited_build029_timestamp_metadata']=inherited
 m.update(scope='DISABLED_SINGLE_BUILD030_SKULLS600_DIAG1_WITH_EXACT_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['runtime_dependencies']=deps
 m['candidate']=dict(dll_sha256=DLL_SHA,dll_size=DLL_SIZE,source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['comparison']=dict(inherited['comparison'],order=['030'],arm='030',parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['map_case']=dict(inherited['map_case'],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,assets=assets)
 m['build030_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,removed_old029_build_targets=oldpins,build_closure_targets=79,productive_delta=delta,single_case=True,automatic_retry=False,automatic_sequence=False,native_started=False,historical_statuses_unchanged=True,whole_three_source_inverse=True,no_new_native_or_functional_qualification=True)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_reacquire_diagnostic=False,reference='PENDING independent Root review/freeze; one030 Skulls600 diag1 observation only')
 names=set(m['sources'])|set(ADDITIONS)|set(DIFF_NAMES)
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={path.name:sha(path)for path in sorted(dest.glob('*.py'))}
 write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode())
 # Fresh full expected-value checks after all writes, not key-count assertions.
 for key,base in (('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)):
  for path,pin in m[key].items():
   if sha(base/path)!=pin:raise ValueError('new package pin changed: '+path)
 result=dict(package=str(dest),build='030',map='skulls',seconds=600,diagnostics=1,manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_reviewed=False)
 write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode());return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
