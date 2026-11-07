"""Strict parser and conservative walk-only export (GPL-2.0-only).

Reuses the existing ssam.ai audit parser; format attributable to Dreamy Cecil
(CecilBotMod 953b477, copyright 2018-2023, GPL-2.0).

Strict read-only parser for DreamyCecil/CecilBotMod BNMV v6 navmesh.

Format source: CecilBotMod PathFinding/Navmesh.cpp and PathPoint.cpp.
No reliance on game engine; never writes to a live game-client installation.
"""
from pathlib import Path
import hashlib
import math
import struct

class Reader:
    def __init__(self, data):
        self.data=data
        self.cursor=0
    def take(self, size):
        if size < 0 or self.cursor+size>len(self.data):
            raise ValueError('truncated navmesh')
        chunk=self.data[self.cursor:self.cursor+size]
        self.cursor+=size
        return chunk
    def unpack(self, fmt):
        size=struct.calcsize(fmt)
        return struct.unpack(fmt,self.take(size))
    def tag(self, value):
        if self.take(4)!=value:
            raise ValueError('invalid navmesh chunk')
    def coords(self):
        vec=list(self.unpack('<3f'))
        if any(not math.isfinite(n) or abs(n)>1e5 for n in vec):
            raise ValueError('invalid waypoint geometry')
        return vec

def parse_bytes(raw: bytes) -> dict:
    if not isinstance(raw, bytes) or len(raw)>10_000_000:
        raise ValueError('invalid navmesh input')
    r=Reader(raw)
    r.tag(b'BNMV')
    version,generated,next_point_id,count=r.unpack('<4i')
    if version!=6 or generated not in (0,1) or not 1<=count<=4096:
        raise ValueError('unsupported navmesh header')
    if next_point_id<count or next_point_id>1_000_000:
        raise ValueError('invalid next id')
    points=[]
    seen=set()
    for slot in range(count):
        r.tag(b'BPPH')
        idx=r.unpack('<i')[0]
        pos=r.coords()
        radius=r.unpack('<f')[0]
        flags=r.unpack('<I')[0]
        important_entity,next_slot,lock_entity=r.unpack('<3i')
        if idx<0 or idx>=next_point_id or idx in seen or not math.isfinite(radius) or radius<=0 or radius>1000:
            raise ValueError('duplicate or invalid waypoint')
        if next_slot!=-1 and not 0<=next_slot<count:
            raise ValueError('invalid navigation next link')
        seen.add(idx)
        if lock_entity!=-1:
            placement=r.unpack('<6f')
            if any(not math.isfinite(n) for n in placement):
                raise ValueError('invalid lock transform')
        nlinks=r.unpack('<i')[0]
        if nlinks<0 or nlinks>count:
            raise ValueError('invalid connection count')
        links=list(r.unpack('<'+'i'*nlinks)) if nlinks else []
        if len(set(links))!=len(links) or any(x<0 or x>=count or x==slot for x in links):
            raise ValueError('invalid connected waypoint index')
        polygon=r.unpack('<B')[0]
        if polygon not in (0,1):
            raise ValueError('invalid polygon tag')
        vertices=0
        if polygon:
            kind=r.take(4)
            if kind==b'PPO1':
                vertices=3
            elif kind==b'PPO2':
                vertices=r.unpack('<i')[0]
                if not 3<=vertices<=1024:
                    raise ValueError('invalid polygon vertices')
            else:
                raise ValueError('unknown Cecil polygon type')
            for _ in range(vertices):
                r.coords()
        points.append(dict(idx=idx,pos=pos,range=radius,flags=flags,
                           important_entity=important_entity,next_slot=next_slot,
                           lock_entity=lock_entity,links=links,polygon_vertices=vertices))
    if r.cursor!=len(raw):
        raise ValueError('navmesh has unrecognized trailing bytes')
    return dict(version=version,generated=bool(generated),next_point_id=next_point_id,
                points=points,file_sha256=hashlib.sha256(raw).hexdigest())

def walk_subset(mesh: dict) -> dict:
    """Conservative adapter, not full Cecil navigation parity.

    Do not infer new edges, reverse one-way arcs or convert any flagged/locked
    transition into walking. Original radii stay in metadata; current runtime
    uses its existing arrival tolerance and needs separate native validation.
    """
    points=mesh['points']
    allowed=[i for i,p in enumerate(points)
             if p['flags']==0 and p['lock_entity']==-1
             and p['important_entity']==-1 and p['next_slot']==-1
             and p['polygon_vertices']==0]
    if not allowed or len(allowed)>256:
        raise ValueError('empty safe subset or runtime node capacity exceeded')
    mapping={old:new for new,old in enumerate(allowed)}
    edges=set()
    for i in allowed:
        for j in points[i]['links']:
            if j in mapping and i in points[j]['links']:
                edges.add(tuple(sorted((mapping[i],mapping[j]))))
    degree=[0]*len(allowed)
    for a,b in edges:
        degree[a]+=1;degree[b]+=1
    if max(degree,default=0)>24:
        raise ValueError('runtime edge capacity exceeded')
    return {'source_indices':allowed,'edges':sorted(edges),
            'excluded_indices':[i for i in range(len(points)) if i not in mapping],
            'max_degree':max(degree,default=0)}

def to_graph_text(mesh: dict) -> str:
    subset=walk_subset(mesh)
    points=mesh['points']
    lines=[
        '# CecilBotMod derived walk-only subset; Dreamy Cecil; GPL-2.0-only.',
        '# Original reference commit: 953b477e53fdc5a5d84c8ae8d759c84fdf6c973c',
        '# Source SHA256: '+mesh['file_sha256'],
        '# NATIVE_NOT_VERIFIED: data conversion alone does not prove traversal.',
        '# Only reciprocal unflagged links; special/entity/locked points omitted.',
        '# Original coordinates retained; existing arrival tolerance, not Cecil radius parity.',
    ]
    lines.extend('node '+' '.join(format(x,'.9g') for x in points[i]['pos'])
                 for i in subset['source_indices'])
    lines.extend(f'edge {i} {j}' for i,j in subset['edges'])
    return '\n'.join(lines)+'\n'

def summarize(filename) -> dict:
    p=Path(filename)
    b=p.read_bytes()
    parsed=parse_bytes(b)
    links={tuple(sorted((i,j))) for i,q in enumerate(parsed['points']) for j in q['links']}
    reciprocal={e for e in links if e[0] in parsed['points'][e[1]]['links']
                and e[1] in parsed['points'][e[0]]['links']}
    return dict(filename=p.name,sha256=parsed['file_sha256'],
                points=len(parsed['points']),undirected_links=len(links),
                reciprocal_edges=len(reciprocal),
                max_neighbors=max(len(q['links']) for q in parsed['points']))
