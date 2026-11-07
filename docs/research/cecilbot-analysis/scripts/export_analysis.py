#!/usr/bin/env python3
"""GPL-2.0-only. CecilBotMod read-only analysis export, never a game installer.
Format: Dreamy Cecil, 953b477, Navmesh.cpp/PathPoint.cpp/PathPolygon.cpp.
Reuses ssam parser from dev commit ed08e2, preserving additional serialized fields.
"""
import argparse,csv,hashlib,json,re,struct
from pathlib import Path
from collections import Counter
from parse_cecil_navmesh import parse_bytes
PIN='953b477e53fdc5a5d84c8ae8d759c84fdf6c973c'
FLAGS={1:'WALK',2:'JUMP',4:'CROUCH',8:'OVERRIDE',16:'UNREACHABLE',32:'TELEPORT',64:'IMPORTANT'}
def encode_mesh(m):
 b=b'BNMV'+struct.pack('<4i',m['version'],int(m['generated']),m['next_point_id'],len(m['points']))
 for p in m['points']:
  b+=b'BPPH'+struct.pack('<i3ffI3i',p['idx'],*p['pos'],p['range'],p['flags'],p['important_entity'],p['next_slot'],p['lock_entity'])
  if p['lock_entity']!=-1:b+=struct.pack('<6f',*p['lock_origin'])
  b+=struct.pack('<i',len(p['links']))+b''.join(struct.pack('<i',i) for i in p['links'])
  b+=struct.pack('<B',int(p['polygon_kind'] is not None))
  if p['polygon_kind']:
   b+=p['polygon_kind'].encode()
   if p['polygon_kind']=='PPO2':b+=struct.pack('<i',p['polygon_vertices'])
   b+=b''.join(struct.pack('<3f',*v) for v in p['polygon_coordinates'])
 return b

def components(points,strong=False):
 n=len(points);adj=[set(p['links']) for p in points]
 if strong:
  # Bounded transitive reachability; sufficient for these <=335-node datasets.
  reach=[]
  for i in range(n):
   seen={i};todo=[i]
   while todo:
    for j in adj[todo.pop()]-seen:seen.add(j);todo.append(j)
   reach.append(seen)
  remain=set(range(n));out=[]
  while remain:
   i=min(remain);group={j for j in remain if j in reach[i] and i in reach[j]};out.append(sorted(group));remain-=group
 else:
  for i in range(n):
   for j in list(adj[i]):adj[j].add(i)
  remain=set(range(n));out=[]
  while remain:
   i=min(remain);seen={i};todo=[i]
   while todo:
    for j in adj[todo.pop()]-seen:seen.add(j);todo.append(j)
   out.append(sorted(seen));remain-=seen
 return out

def dump(p,value):p.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def table(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('reference',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 if a.output.exists():raise SystemExit('Use a new output directory; refusing overwrite')
 manifest_path=Path(__file__).resolve().parents[1]/'exports/reference-manifest.json'
 for row in json.loads(manifest_path.read_text()):
  source=a.reference/row['path']
  if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=row['sha256']:
   raise ValueError('Pinned reference hash mismatch: '+row['path'])
 files=sorted((a.reference/'Cecil/Navmeshes').glob('*.nav'))
 if len(files)!=9:raise SystemExit('Expected nine pinned master navmeshes')
 prepared=[]
 for f in files:
  raw=f.read_bytes();m=parse_bytes(raw)
  if encode_mesh(json.loads(json.dumps(m)))!=raw:raise ValueError('roundtrip mismatch '+f.name)
  prepared.append((f,m,raw))
 a.output.mkdir(parents=True);summary=[]
 for f,m,raw in prepared:
  points=m['points'];arcs=[(i,j) for i,p in enumerate(points) for j in p['links']];arcset=set(arcs)
  m.update(source_commit=PIN,source_path='Cecil/Navmeshes/'+f.name,map_name=f.stem.rsplit('_',1)[0],level_path_hash=f.stem.rsplit('_',1)[1],coordinate_system='Serious Engine world FLOAT3D (x,y,z), ordinary gravity -Y; no coordinate transform; units as stored',license='Repository contains GPLv2; separate NAV rights declaration not found; redistribution status UNRESOLVED',native_status='NOT_TESTED',hash_is_map_content_hash=False)
  for i,p in enumerate(points):p['slot']=i;p['flag_names']=[v for k,v in FLAGS.items() if p['flags']&k]
  dump(a.output/(f.stem+'.json'),m)
  table(a.output/(f.stem+'.points.csv'),[dict(slot=i,id=p['idx'],x=p['pos'][0],y=p['pos'][1],z=p['pos'][2],radius=p['range'],flags=p['flags'],flag_names='|'.join(p['flag_names']),important_entity=p['important_entity'],next_slot=p['next_slot'],lock_entity=p['lock_entity'],lock_origin=json.dumps(p['lock_origin']),polygon_kind=p['polygon_kind'],polygon_coordinates=json.dumps(p['polygon_coordinates'])) for i,p in enumerate(points)])
  table(a.output/(f.stem+'.edges.csv'),[dict(source_slot=i,target_slot=j,source_id=points[i]['idx'],target_id=points[j]['idx'],reciprocal=(j,i) in arcset,source_flags=points[i]['flags'],target_flags=points[j]['flags']) for i,j in arcs])
  weak=components(points);strong=components(points,True)
  summary.append(dict(file=f.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),version=m['version'],generated=m['generated'],points=len(points),directed_links=len(arcs),reciprocal_pairs=sum((j,i) in arcset for i,j in arcs)//2,one_way_arcs=sum((j,i) not in arcset for i,j in arcs),weak_component_sizes=sorted(map(len,weak),reverse=True),strong_component_sizes=sorted(map(len,strong),reverse=True),flags={v:sum(bool(p['flags']&k) for p in points) for k,v in FLAGS.items()},locked=sum(p['lock_entity']!=-1 for p in points),important_entities=sum(p['important_entity']!=-1 for p in points),polygons=sum(p['polygon_vertices']>0 for p in points),bounds={xyz:[min(p['pos'][i] for p in points),max(p['pos'][i] for p in points)] for i,xyz in enumerate('xyz')},roundtrip='BYTE_IDENTICAL'))
 dump(a.output/'navmesh-summary.json',summary)
 settings=(a.reference/'Sources/Bots/Logic/BotSettings.cpp').read_text()
 header=(a.reference/'Sources/Bots/Logic/BotSettings.h').read_text()
 defs={k:dict(type=t,description=c) for t,k,c in re.findall(r'^\s+(INDEX|FLOAT) (\w+);\s*// (.*)$',header,re.M)}
 rows=[]
 for preset,body in re.findall(r'static void Preset(\w+)\(SBotSettings &sbs\) \{(.*?)\n\};',settings,re.S):
  for key,val in re.findall(r'sbs\.(\w+) = ([^;]+);',body):rows.append(dict(preset=preset,parameter=key,source_value=val,**defs.get(key,{})))
 for key,val in [('b3rdPerson','TRUE'),('iCrosshair','-1'),('bAvoidPits','FALSE')]:rows.append(dict(preset='ConstructorOnly',parameter=key,source_value=val,**defs[key]))
 dump(a.output/'settings.json',dict(source_commit=PIN,source_files=['Sources/Bots/Logic/BotSettings.cpp','Sources/Bots/Logic/BotSettings.h'],reset_does_not_change_constructor_only_values=True,rows=rows));table(a.output/'settings.csv',rows)
 manifest=[]
 for f in sorted(a.reference.rglob('*')):
  if f.is_file():manifest.append(dict(path=f.relative_to(a.reference).as_posix(),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),source_commit=PIN))
 dump(a.output/'reference-manifest.json',manifest)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
