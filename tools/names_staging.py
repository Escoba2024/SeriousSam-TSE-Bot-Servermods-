"""Offline byte plans only. No process API, shell interpolation or live writer."""
import hashlib,json,struct
from gaming_names import validate_native,name_id
INSTANCES=('redstation','yodeller','skulls','trouble','hole','development')
def sha(data):return hashlib.sha256(data).hexdigest()
def parse_plc(data):
 if not isinstance(data,bytes)or len(data)<61 or data[:4]!=b'PLC4':raise ValueError('PLC4 header/length')
 n=struct.unpack_from('<I',data,4)[0]
 if not 1<=n<=32 or len(data)!=60+n:raise ValueError('PLC4 name length/exact52 tail')
 data[8:8+n].decode('ascii') # Old flash spellings are retained, not interpreted.
 tail=data[8+n:]
 if struct.unpack_from('<I',tail)[0]!=0:raise ValueError('unsupported nonempty team')
 guid=tail[4:20]
 if guid==bytes(16):raise ValueError('empty GUID')
 return n,tail,guid

def patch_name(before,sidecar,name):
 validate_native(name);n,tail,guid=parse_plc(before)
 if sidecar!=guid:raise ValueError('GUID sidecar mismatch; no repair permitted')
 raw=name.encode('ascii');after=b'PLC4'+struct.pack('<I',len(raw))+raw+tail
 _,newtail,newguid=parse_plc(after)
 if newtail!=tail or newguid!=guid:raise ValueError('non-name mutation')
 return after,dict(before_sha256=sha(before),after_sha256=sha(after),guid_hex=guid.hex(),guid_sidecar_sha256=sha(sidecar),tail_sha256=sha(tail),tail_bytes=52,tail_unchanged=True,guid_unchanged=True,sidecar_unchanged=True)

def validate_assignments(rows):
 if not isinstance(rows,list)or len(rows)!=48:raise ValueError('exact48 required; drift cannot truncate')
 expected={(i,r,n)for i in INSTANCES for r in ('botA','botB')for n in range(4)};seen=set();names=set()
 for row in rows:
  i,r,n=row['instance'],row['role'],row['local'];key=(i,r,n)
  if type(n)is not int or key not in expected or key in seen:raise ValueError('fleet slot identity')
  ordinal=n+(4 if r=='botB' else 0)
  if row['bot_id']!=f'{i}.bot.{ordinal:03d}':raise ValueError('stable ID binding')
  visible=validate_native(row['native_name'])
  if visible!=row['nickname']or row['name_id']!=name_id(visible)or visible.casefold()in names:raise ValueError('name identity/collision')
  seen.add(key);names.add(visible.casefold())
 if seen!=expected:raise ValueError('incomplete fleet')

def patch_launcher(before,root,side,expected_sha):
 if side not in ('A','B')or sha(before)!=expected_sha:raise ValueError('launcher hash/side drift')
 line=f'/usr/bin/python3 {root}/rotate-live-identities.py --client {side} || exit 87\n'.encode('ascii')
 generator=f'/usr/bin/python3 {root}/generate-bot-roster.py --client {side} || exit 88\n'.encode('ascii')
 if before.splitlines(keepends=True).count(line)!=1 or before.splitlines(keepends=True).count(generator)!=1:raise ValueError('exact launcher line mismatch')
 after=before.replace(line,b'# Stable fleet names: startup rotator deliberately bypassed; GUID-only roster follows.\n',1)
 if generator not in after:raise ValueError('GUID generator changed')
 return after

def plan(rows,files,roots,launcher_pins):
 validate_assignments(rows)
 if set(roots)!=set(INSTANCES)or len(set(roots.values()))!=6:raise ValueError('six distinct roots required')
 changes={};receipts=[];instance_guids={i:set()for i in INSTANCES}
 for row in rows:
  i,r,n=row['instance'],row['role'],row['local'];path=f'{roots[i]}/{r}/Players/Player{n}.plr'
  after,receipt=patch_name(files[path],files[path+'.guid'],row['native_name'])
  guid=receipt['guid_hex']
  if guid in instance_guids[i]:raise ValueError('same-instance GUID duplicate; no repair')
  instance_guids[i].add(guid);changes[path]=after;receipts.append(dict(row,path=path,**receipt))
 red=roots['redstation']
 for side in ('A','B'):
  path=f'{red}/launch-bot{side}.sh';changes[path]=patch_launcher(files[path],red,side,launcher_pins[path])
 path=red+'/roster100.json';roster=json.loads(files[path]);roster['active']=[dict(id=r['bot_id'],bot_id=r['bot_id'],name_id=r['name_id'],nickname=r['nickname'],formatted=r['native_name'],slot=r['local']+(4 if r['role']=='botB'else 0))for r in rows if r['instance']=='redstation']
 roster['active'].sort(key=lambda r:r['slot']);roster['rotate_policy']='stable_assignment_no_start_rotation'
 changes[path]=(json.dumps(roster,indent=2,ensure_ascii=True)+'\n').encode('ascii')
 return changes,receipts
