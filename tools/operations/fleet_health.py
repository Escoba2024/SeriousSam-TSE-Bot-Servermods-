"""Read-only fleet health; unknown state never authorizes destructive recovery."""
import csv,hashlib,json,os,re,socket,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import qualify_integrated_wine as q
MIN_FREE=8*1024**3
DLL='7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835'

def process_identity(pid):
 p=Path('/proc')/str(pid);s=(p/'stat').read_text().rsplit(') ',1)[1].split()
 return dict(pid=pid,start_ticks=int(s[19]),cwd=str((p/'cwd').resolve()),command=(p/'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace'),cgroup=(p/'cgroup').read_text().strip())

def verify_process(info):
 try:
  p=Path('/proc')/str(info['pid']);s=(p/'stat').read_text().rsplit(') ',1)[1].split()
  if s[0]=='Z':return 'ABSENT'
  if int(s[19])!=info['start_ticks']:return 'PID_REUSED'
  if 'cwd' in info and str((p/'cwd').resolve())!=info['cwd']:return 'WRONG_CWD'
  if 'cgroup' in info and (p/'cgroup').read_text().strip()!=info['cgroup']:return 'WRONG_CGROUP'
  if 'command' in info and (p/'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace')!=info['command']:return 'WRONG_COMMAND'
  return 'LIVE'
 except FileNotFoundError:return 'ABSENT'
 except (OSError,KeyError,ValueError):return 'UNVERIFIED'

def udp_owners(port):
 inodes=set()
 for table in ['udp','udp6']:
  for line in Path('/proc/net/'+table).read_text().splitlines()[1:]:
   fields=line.split()
   if int(fields[1].split(':')[1],16)==port:inodes.add('socket:['+fields[9]+']')
 owners=set()
 for p in Path('/proc').glob('[0-9]*'):
  try:
   for fd in (p/'fd').iterdir():
    try:
     if os.readlink(fd) in inodes:owners.add(int(p.name))
    except FileNotFoundError:pass
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 return owners

def tail(path,limit=131072):
 with Path(path).open('rb') as f:
  f.seek(0,2);size=f.tell();f.seek(max(0,size-limit));return f.read().decode(errors='replace')

def telemetry_valid(path,now=None):
 now=time.time() if now is None else now
 try:
  p=Path(path);text=tail(p);header=None
  with p.open() as f:
   for _ in range(20):
    l=f.readline()
    if l.startswith('#columns,'):header=l.strip().split(',')[1:];break
  if not header:return False
  rows=[l.split(',') for l in text.splitlines() if l and not l.startswith('#') and len(l.split(','))==len(header)]
  if not rows:return False
  r=dict(zip(header,rows[-1]));age=now-int(r['t_ms'])/1000;lp=int(r['lp']);ticks=int(r['ticks']);actions=int(r['actions'])
  return -3<=age<=12 and 18<=ticks<=23 and lp in (1,4) and 18*lp<=actions<=23*lp and int(r['renderdraw'])==0 and int(r['gameon'])==1 and int(r['enabled'])==1 and int(r['stall_s'])==0
 except (OSError,ValueError,KeyError):return False

def assess(s):
 alerts=[];blocked=[];humans=[];recover=[];expected=s.get('expected_names',q.ROSTER)
 for key,code in [('ports_owned','FOREIGN_PORT'),('mounts_owned','FOREIGN_MOUNT'),('dll_valid','INVALID_ARTIFACT'),('master_ok','MASTER_DNS'),('telemetry_ok','TELEMETRY_STALE')]:
  if not s.get(key):blocked.append(code)
 if s.get('disk_free',0)<MIN_FREE:blocked.append('LOW_DISK')
 blocked+=s.get('identity_errors',[])
 if s.get('owned_sync_bad',0):blocked.append('OWNED_CLIENT_SYNC')
 if s.get('external_sync_bad',0):alerts.append('EXTERNAL_CLIENT_SYNC')
 query=s.get('query')
 if query is None or not 0<=s['now']-s.get('query_time',0)<=5:blocked.append('QUERY_UNCERTAIN')
 else:
  names=[v for k,v in query.items() if re.fullmatch(r'player_\d+',k)]
  humans=[n for n in names if n not in expected]
  try:valid=query.get('gamever')=='1.07' and not query.get('activemod') and int(query.get('maxplayers',0))==16 and int(query.get('numplayers',-1))==len(names) and len(names)<=16 and len(names)==len(set(names))
  except (TypeError,ValueError):valid=False
  if not valid:blocked.append('INVALID_QUERY')
  if not set(expected).issubset(names) and not s.get('missing'):blocked.append('MISSING_ROSTER')
 if humans:alerts.append('HUMAN_HOLD')
 if s.get('logs_over_limit'):alerts.append('LOG_LIMIT_MAINTENANCE_HOLD')
 if not blocked and not humans:recover=[r for r in s.get('missing',[]) if r!='server']
 return dict(status='BLOCKED' if blocked else ('DEGRADED' if s.get('missing') else ('ALERT' if alerts else 'HEALTHY')),alerts=blocked+alerts,humans=humans,safe_recovery=not blocked and not humans,recover_roles=recover)

def mount_spec(root,role,source):
 return dict(target=str(root/role),lower=str(source),upper=str(root/'layers'/role/'upper'),work=str(root/'layers'/role/'work'))

def mount_matches(m):
 lines=[l for l in Path('/proc/self/mountinfo').read_text().splitlines() if l.split()[4]==m['target']]
 return len(lines)==1 and ' - overlay ' in lines[0] and all(k+'='+m[v] in lines[0].split(' - ',1)[1].split()[2].split(',') for k,v in [('lowerdir','lower'),('upperdir','upper'),('workdir','work')])

def collect(result_path):
 result_path=Path(result_path);r=json.loads(result_path.read_text());root=result_path.parent;now=time.time();missing=[];errors=[];infos=r['processes'];cg=Path(r['cgroup']);allowed={int(p) for p in (cg/'cgroup.procs').read_text().split()} if cg.exists() else set()
 for role,info in infos.items():
  status=verify_process(info)
  if status=='ABSENT':missing.append(role)
  elif status!='LIVE':errors.append(role+':'+status)
  elif info['pid'] not in allowed:errors.append(role+':WRONG_CGROUP')
 try:query=q.query(r['query_port']);qt=time.time()
 except (OSError,RuntimeError):query=None;qt=0
 mounts_ok=True
 for target in r.get('production_mounts',r.get('mounts',[])):
  role=Path(target).name;src=(Path(r.get('template','/srv/tse-wine-runtime-20261020/public-eight-20261020-2140'))/('prefix-botA' if role=='prefix-botB' else role))
  mounts_ok &= mount_matches(mount_spec(root,role,src))
 dll_ok=r.get('dll_sha256')==DLL
 for role in infos:
  if role in missing:continue
  game=root/role
  pins={k:v for k,v in q.PINS.items() if k in ('Engine.dll','GameMP.dll','EntitiesMP.dll','DedicatedServer.exe' if role=='server' else 'SeriousSam.exe')}
  if role.startswith('bot'):pins['GameMP.dll']=DLL
  try:dll_ok &= all(q.sha(game/'Bin'/name)==want for name,want in pins.items())
  except OSError:dll_ok=False
 try:master_ok=bool(q.validate_master_resolution())
 except (OSError,AssertionError):master_ok=False
 logs=root/'server/Dedicated_BotTest.log';owned=external=0
 if logs.exists():
  # Scan full current generation, preserving historical alerts instead of silently resetting.
  for client in re.findall(r"SYNCBAD: Client '([^']+)'",logs.read_text(errors='replace')):
   if client in ['127.0.0.1','91.99.75.33','Local machine']:owned+=1
   else:external+=1
 telemetry=all(telemetry_valid(root/role/'Bin/BotTelemetry.csv') for role in infos if role.startswith('bot') and role not in missing)
 paths=[root/'server/Dedicated_BotTest.log']+[root/role/'SeriousSam.log' for role in infos if role.startswith('bot')]+[root/role/'Bin/BotTelemetry.csv' for role in infos if role.startswith('bot')]
 snap=dict(now=time.time(),query=query,query_time=qt,identity_errors=errors,missing=missing,ports_owned=all(udp_owners(port)<=allowed for port in [r['game_port'],r['query_port']]),mounts_owned=mounts_ok,dll_valid=bool(dll_ok),disk_free=os.statvfs('/').f_bavail*os.statvfs('/').f_frsize,master_ok=master_ok,telemetry_ok=telemetry,owned_sync_bad=owned,external_sync_bad=external,logs_over_limit=any(p.exists() and p.stat().st_size>32*1024**2 for p in paths),expected_names=q.ROSTER[:r.get('bots',8)])
 verdict=assess(snap)
 # No player names or peer addresses in persisted public-facing health status.
 verdict.update(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),players=int(query['numplayers']) if query else None,expected_bots=r.get('bots',8),missing_roles=missing,disk_free_bytes=snap['disk_free'],owned_sync_bad=owned,external_sync_bad=external,processes_verified=not errors,query_fresh=query is not None,telemetry_fresh=telemetry)
 return snap,verdict
