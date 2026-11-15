"""Prepare ONE DISABLED Build024 map600s case. Never launches any runtime."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile
import zlib
from prepare_navigation_build024 import validate_build,BUILD
from navigation_build024_maps_policy import MAPS

PARENT=Path('/srv/tse-nav20-024-red600-disabled-20261114')
PARENT_SHA='ea00456a147418f54db3b3b83c96a61a122ae8c5d652a3608317c5919c379f5a'
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
CHANGED=('run-a4.py','adapter_policy.py')
ADDITIONS=('prepare_navigation_build024_maps.py','navigation_build024_maps_policy.py','test_navigation_build024_maps.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def changes(name,case):
 if case not in MAPS:raise ValueError('fixed supported map case required')
 if name=='run-a4.py':
  return [("PREFIX=f'ssam-nav20-024-hard-ordered-","PREFIX=f'ssam-nav20-024-mapcase-hard-ordered-"),
          ("E=BASE/f'nav20-024-hard-ordered-","E=BASE/f'nav20-024-mapcase-hard-ordered-")]
 if name=='adapter_policy.py':
  return [('from navigation_comparison_policy import options as validate','from navigation_build024_maps_policy import options as validate'),
          ("validate(map_key,duration,diag,'024')","validate(map_key,duration,diag,'024',"+repr(case)+')')]
 raise ValueError('only two fixed retarget sources')


def apply(name,text,case,reverse=False):
 pairs=changes(name,case)
 if not reverse and any(after in text for before,after in pairs):raise ValueError('already/partly retargeted source')
 for before,after in (reversed(pairs)if reverse else pairs):
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact retarget anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text,case):return apply(name,text,case)
def reverse(name,text,case):return apply(name,text,case,True)


def validate_assets(case,catalog):
 if case not in MAPS:raise ValueError('fixed supported map case required')
 m=catalog['maps'][case]
 with zipfile.ZipFile(catalog['archive_readonly_source'])as z:
  world=z.read(m['world_path'].replace('\\','/'))
 nav=Path(m['private_nav_source']).read_bytes()
 for raw,kind in ((world,'world'),(nav,'nav')):
  if hashlib.sha256(raw).hexdigest()!=m[kind+'_sha256']or f'{zlib.crc32(raw):08x}'!=m[kind+'_crc32']:
   raise ValueError('selected asset hash/CRC changed: '+case+' '+kind)
 if struct.unpack_from('<4s4i',nav)[0:2]!=(b'BNMV',6)or struct.unpack_from('<i',nav,16)[0]!=m['nodes']:
  raise ValueError('selected nav header/nodes changed')
 return dict(map=case,world_sha256=m['world_sha256'],nav_sha256=m['nav_sha256'],nodes=m['nodes'],loaded_world_proven=False,archive_full_hash_recomputed=False)


def prepare(case,destination):
 if case not in MAPS:raise ValueError('fixed supported map case required')
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh disabled destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled024 parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text())
 if m['runtime_reviewed']is not False or m['comparison']['arm']!='024' or m['comparison']['map']!='redstation':
  raise ValueError('exact disabled024Red parent required')
 for key,base in [('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for name,h in m[key].items():
   if sha(base/name)!=h:raise ValueError('parent source pin changed: '+name)
 if sha(PARENT/'map-catalog.json')!=CATALOG_SHA:raise ValueError('parent catalog changed')
 catalog=json.loads((PARENT/'map-catalog.json').read_text())
 asset=validate_assets(case,catalog);pins=validate_build()
 changed={name:transform(name,(PARENT/name).read_text(),case)for name in CHANGED}
 for name,text in changed.items():
  if reverse(name,text,case)!=(PARENT/name).read_text():raise ValueError('exact inverse bytes differ')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():
  (dest/name).write_text(text)
  (dest/(name+'.map024.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),text.splitlines(True),fromfile='disabled024Red/'+name,tofile='disabled024-'+case+'/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps.update(pins);deps[str(dest/'navigation_build024_maps_policy.py')]=sha(dest/'navigation_build024_maps_policy.py')
 m['runtime_dependencies']=deps
 m.update(scope='DISABLED_SINGLE_NAV20_024_MAP600_V3',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['inherited_red_comparison_metadata']=m['comparison']
 m['comparison']=dict(m['comparison'],map=case,parent_manifest_sha256=PARENT_SHA,native_started=False)
 m['map_case']=dict(map=case,map_binding=catalog['maps'][case],parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,seconds=600,diagnostics=0,hard_difficulty=2,bot_tier=3,bot_count=8,original_observer_fps=20,single_case=True,automatic_sequence=False,automatic_retry=False,native_started=False,assets=asset,scope='independent functional observation; no cross-map comparison/acceptance/hazard/reset qualification',historical_statuses_unchanged=True)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,reference='PENDING independent Root review/freeze for this single map case')
 names=set(m['sources'])|set(ADDITIONS)|{name+'.map024.diff'for name in CHANGED}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={path.name:sha(path)for path in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),map=case,build='024',manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False,runtime_reviewed=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--map',choices=MAPS,required=True);p.add_argument('--destination',type=Path,required=True)
 args=p.parse_args();print(json.dumps(prepare(args.map,args.destination),indent=2))
