"""Passive Original107 local0→source→global8 probe. No attach, hooks or writes.

Only the exact original GameMP image is supported. New Retail ABI observation,
not yet natively qualified; Root must cross-check it before a600s window.
"""
import struct
import time
from ownns_latejoin_preflight import ORIGINALS,require

# Original GameMP TimerHandler VAs6085127d/60851297/6085132f at preferred
# base60840000. All bytes below are relocation-free; see the decision report.
GUARDS=((0x1127d,'8d9fa40f0000833b00'),(0x11297,'8b138d73048b02'),(0x1132f,'81c30c08000083f804'))


def snapshot(read,game_base):
 observed=[]
 def require(condition,message):
  if not condition:
   error=ValueError('Original local-source: '+message)
   error.raw_reads=[dict(address=a,size=n,raw_hex=b.hex())for a,n,b in observed]
   raise error
 require(type(game_base)is int and 0x10000<=game_base<0xff000000,'Original GameMP base')
 def take(address,size):
  require(0x10000<=address<=0xffffffff-size and 0<size<=16,'local-source read bound')
  raw=read(address,size);require(len(raw)==size,'short local-source read')
  observed.append((address,size,raw));return raw
 def u(address):return struct.unpack('<I',take(address,4))[0]
 def pointer(value):require(0x10000<=value<0xff000000 and value%4==0,'local-source pointer');return value
 for rva,hexbytes in GUARDS:require(take(game_base+rva,len(bytes.fromhex(hexbytes)))==bytes.fromhex(hexbytes),'Original local-source code guard')
 game=pointer(u(game_base+0x2fba4));locals=[]
 for local in range(4):
  source=u(game+0xfa4+local*0x80c)
  if source:
   pointer(source);slot=struct.unpack('<i',take(source,4))[0]
   require(0<=slot<16,'actual global index out of bounds')
   locals.append(dict(local=local,source_pointer=source,global_slot=slot))
 require(len(locals)==1 and locals[0]['local']==0 and locals[0]['global_slot']==8,'Original must have only local0 bound to actual global8')
 for address,size,raw in list(observed):require(read(address,size)==raw,'local-source changed during read')
 return dict(locals=locals,game_pointer=game,consistency='two_equal_reads_not_atomic',native_abi_qualified=False,raw_reads=[dict(address=a,size=n,raw_hex=b.hex())for a,n,b in observed])


def sample(reader):
 require(reader.root.name=='vanilla','only own Original role')
 require({name:pin.sha256 for name,pin in reader.pins.items()}=={n:ORIGINALS[n]for n in ('Engine.dll','EntitiesMP.dll','GameMP.dll')},'exact Original module pins')
 start=time.monotonic();reader.maps=reader._guard();reader._fingerprints()
 try:result=snapshot(reader._read,reader.bases['GameMP.dll']);reader._guard()
 except BaseException as error:
  error.local_source_evidence=dict(process_identity=list(reader.identity),hashes={n:p.sha256 for n,p in reader.pins.items()},read_interval=[start,time.monotonic()],raw_reads=getattr(error,'raw_reads',[]),error=repr(error))
  raise
 result.update(process_identity=list(reader.identity),hashes={n:p.sha256 for n,p in reader.pins.items()},read_interval=[start,time.monotonic()])
 return result
