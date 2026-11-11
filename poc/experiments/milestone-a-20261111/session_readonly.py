"""Read-only on hash-pinned original Retail Engine; no hooks or writes."""
import pathlib,struct,hashlib
_validated={}
ENGINE_SHA='b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
def read(pid,root):
 root=pathlib.Path(root);dll=root/'Bin/Engine.dll';st=dll.stat();signature=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
 if _validated.get(str(dll))!=signature:
  assert hashlib.sha256(dll.read_bytes()).hexdigest()==ENGINE_SHA;_validated[str(dll)]=signature
 proc=pathlib.Path('/proc')/str(pid);assert (proc/'cwd').resolve()==root
 rows=[r.split() for r in (proc/'maps').read_text().splitlines() if str(dll) in r];assert rows and all(int(r[4])==dll.stat().st_ino for r in rows)
 base=int(next(r[0].split('-')[0] for r in rows if int(r[2],16)==0),16)
 with (proc/'mem').open('rb',buffering=0) as m:
  def data(a,n):m.seek(a);b=m.read(n);assert len(b)==n;return b
  def u(a):return struct.unpack('<I',data(a,4))[0]
  # Export GetSessionProperties RVA0xdca00 ends lea eax,[esi+0x96c].
  assert data(base+0xdca1f,6)==bytes.fromhex('8d866c090000')
  # GetPlayerEntity RVA0xf9d70 and GetHealth RVA0x17020 verified separately.
  assert data(base+0x17020,7)==bytes.fromhex('d981cc000000c3')
  network=u(base+0x20d6a4);assert network>0x10000
  block=data(network+0x96c,156);state=u(network+0x20);table=u(state+4);players=[]
  if table>0x10000:
   for i in range(16):
    slot=table+i*136
    if not u(slot):continue
    entity=u(slot+4)
    if entity>0x10000:players.append({'slot':i,'entity_pointer':entity,'health':struct.unpack('<f',data(entity+0xcc,4))[0],'placement':struct.unpack('<6f',data(entity+0x20,24)),'spawned_tick':struct.unpack('<f',data(entity+0xc14,4))[0]})
  return {'game_tick':struct.unpack('<f',data(state+0x4c,4))[0],'spawn_value':struct.unpack_from('<f',block,0x84)[0],'session156_sha256':hashlib.sha256(block).hexdigest(),'session156_hex':block.hex(),'players':players}
