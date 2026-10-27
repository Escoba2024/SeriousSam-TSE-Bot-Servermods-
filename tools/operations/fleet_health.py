"""Read-only fleet health; unknown state never authorizes destructive recovery."""
import csv,hashlib,json,os,re,socket,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import qualify_integrated_wine as q
MIN_FREE=8*1024**3
DLL='7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835'

def bot_role(role,profile=None):
 return profile.is_bot(role) if profile else role.startswith('bot')

def local_count(role,bots,profile=None):
 return profile.local_players(role) if profile else (1 if bots==1 else 4)

def available_memory():
 return int(re.search(r'^MemAvailable:\s+(\d+) kB$',Path('/proc/meminfo').read_text(),re.M)[1])*1024

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

def telemetry_valid(path,now=None,expected_local=None):
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
  return -3<=age<=12 and 18<=ticks<=23 and lp in (1,4) and (expected_local is None or lp==expected_local) and 18*lp<=actions<=23*lp and int(r['renderdraw'])==0 and int(r['gameon'])==1 and int(r['enabled'])==1 and int(r['stall_s'])==0
 except (OSError,ValueError,KeyError):return False

def query_roster(query):
 try:
  names=[v for k,v in query.items() if re.fullmatch(r'player_\d+',k)]
  valid=query.get('gamever')=='1.07' and not query.get('activemod') and int(query.get('maxplayers',0))==16 and int(query.get('numplayers',-1))==len(names) and len(names)<=16 and len(names)==len(set(names))
 except (AttributeError,TypeError,ValueError):valid=False
 if not valid:raise ValueError('invalid Retail query roster')
 return names

def assess(s):
 alerts=[];blocked=[];humans=[];recover=[];expected=s.get('expected_names',q.ROSTER)
 for key,code in [('ports_owned','FOREIGN_PORT'),('mounts_owned','FOREIGN_MOUNT'),('dll_valid','INVALID_ARTIFACT'),('master_ok','MASTER_DNS'),('telemetry_ok','TELEMETRY_STALE')]:
  if not s.get(key):blocked.append(code)
 if s.get('disk_free',0)<MIN_FREE:blocked.append('LOW_DISK')
 blocked+=s.get('identity_errors',[])+s.get('cgroup_issues',[])+s.get('resource_issues',[])
 if not s.get('sync_scan_complete',True):blocked.append('SYNC_LOG_SCAN_PENDING')
 if s.get('owned_sync_bad',0):blocked.append('OWNED_CLIENT_SYNC')
 if s.get('external_sync_bad',0):alerts.append('EXTERNAL_CLIENT_SYNC')
 query=s.get('query')
 if query is None or not 0<=s['now']-s.get('query_time',0)<=5:blocked.append('QUERY_UNCERTAIN')
 else:
  names=[v for k,v in query.items() if re.fullmatch(r'player_\d+',k)]
  humans=[n for n in names if n not in expected]
  try:query_roster(query);valid=True
  except ValueError:valid=False
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

_SYNC_CACHE={}
def sync_counts(path,max_bytes=4*1024**2,generation=None):
 p=Path(path);st=p.stat();key=str(p);c=_SYNC_CACHE.get(key)
 if c is None or c['inode']!=(st.st_dev,st.st_ino) or c['generation']!=generation or st.st_size<c['offset'] or (st.st_size==c['offset'] and st.st_mtime_ns!=c['mtime']):
  c=dict(inode=(st.st_dev,st.st_ino),generation=generation,offset=0,partial=b'',owned=0,external=0,valid=True,mtime=st.st_mtime_ns)
 with p.open('rb') as f:
  f.seek(c['offset']);data=f.read(min(max_bytes,max(0,st.st_size-c['offset'])))
 c['offset']+=len(data);parts=(c['partial']+data).split(b'\n');c['partial']=parts.pop()
 if len(c['partial'])>65536:c['valid']=False;c['partial']=c['partial'][-65536:]
 for line in parts:
  m=re.search(rb"SYNCBAD: Client '([^']+)'",line)
  if m:c['owned' if m[1] in [b'127.0.0.1',b'91.99.75.33',b'Local machine'] else 'external']+=1
 c['mtime']=st.st_mtime_ns;_SYNC_CACHE[key]=c
 return dict(owned=c['owned'],external=c['external'],complete=c['offset']>=st.st_size and c['valid'] and not c['partial'],bytes_scanned=len(data))

def log_paths(root,r,profile=None):
 paths=[root/'xvfb.log',root/'server/Dedicated_BotTest.log']
 for role in r['processes']:
  paths.append(root/(role+'-wine.log'))
  if profile and role!='server':paths.append(root/role/'SeriousSam.log')
  if bot_role(role,profile):
   if not profile:paths.append(root/role/'SeriousSam.log')
   paths.append(root/role/'Bin/BotTelemetry.csv')
 return paths

def logs_over_limit(root,r,profile=None):
 limit=r.get('log_limit_bytes',32*1024**2)
 return any(p.exists() and p.stat().st_size>limit for p in log_paths(root,r,profile))

def collect(result_path,profile=None):
 result_path=Path(result_path);r=json.loads(result_path.read_text())
 if 'private_profile_sha256' in r and profile is None:raise ValueError('private candidate profile required for private result')
 if profile:
  profile.require_namespace();profile.verify_settings()
 root=result_path.parent;now=time.time();missing=[];errors=[];infos=r['processes'];cg=Path(r['cgroup']);allowed={int(p) for p in (cg/'cgroup.procs').read_text().split()} if cg.exists() else set()
 if profile and (root!=profile.root or r.get('private_profile_sha256')!=profile.profile_sha256 or set(infos)!=set(profile.role_names)):
  raise ValueError('private health root/profile/role generation mismatch')
 for role,info in infos.items():
  status=verify_process(info)
  if status=='ABSENT':missing.append(role)
  elif status!='LIVE':errors.append(role+':'+status)
  elif info['pid'] not in allowed:errors.append(role+':WRONG_CGROUP')
 try:query=q.query(r['query_port']);qt=time.time()
 except (OSError,RuntimeError):query=None;qt=0
 mounts_ok=True
 for target in r.get('production_mounts',r.get('mounts',[])):
  role=Path(target).name;src=profile.source(role) if profile else (Path(r.get('template','/srv/tse-wine-runtime-20261020/public-eight-20261020-2140'))/('prefix-botA' if role=='prefix-botB' else role))
  mounts_ok &= mount_matches(mount_spec(root,role,src))
 expected_dll=profile.candidate_sha256 if profile else DLL
 dll_ok=r.get('dll_sha256')==expected_dll
 for role in infos:
  if role in missing:continue
  game=root/role
  pins={k:v for k,v in q.PINS.items() if k in ('Engine.dll','GameMP.dll','EntitiesMP.dll','DedicatedServer.exe' if role=='server' else 'SeriousSam.exe')}
  if bot_role(role,profile):pins['GameMP.dll']=expected_dll
  try:dll_ok &= all(q.sha(game/'Bin'/name)==want for name,want in pins.items())
  except OSError:dll_ok=False
 try:
  if profile:master_ok=profile.master_isolation_ok()
  else:master_ok=bool(q.validate_master_resolution())
 except (OSError,AssertionError,ValueError):master_ok=False
 logs=root/'server/Dedicated_BotTest.log';counts=dict(owned=0,external=0,complete=False)
 if logs.exists():counts=sync_counts(logs,generation=infos.get('server',{}).get('start_ticks'))
 owned=counts['owned'];external=counts['external']
 telemetry=all(telemetry_valid(root/role/'Bin/BotTelemetry.csv',expected_local=local_count(role,r.get('bots'),profile)) for role in infos if bot_role(role,profile) and role not in missing)
 cpu_stat={k:int(v) for k,v in (line.split() for line in (cg/'cpu.stat').read_text().splitlines())} if cg.exists() else {}
 memory_events={k:int(v) for k,v in (line.split() for line in (cg/'memory.events').read_text().splitlines())} if cg.exists() else {}
 cgroup_issues=[]
 if cpu_stat.get('nr_throttled',0):cgroup_issues.append('CGROUP_THROTTLED')
 if memory_events.get('oom_kill',0) or memory_events.get('oom',0):cgroup_issues.append('CGROUP_OOM')
 available=available_memory();memory_current=int((cg/'memory.current').read_text()) if cg.exists() else None;memory_peak=int((cg/'memory.peak').read_text()) if cg.exists() else None
 resource_issues=['HOST_RAM_RESERVE'] if available<768*1024**2 else []
 snap=dict(now=time.time(),query=query,query_time=qt,identity_errors=errors,missing=missing,ports_owned=all(udp_owners(port)<=allowed for port in [r['game_port'],r['query_port']]),mounts_owned=mounts_ok,dll_valid=bool(dll_ok),disk_free=os.statvfs('/').f_bavail*os.statvfs('/').f_frsize,master_ok=master_ok,telemetry_ok=telemetry,owned_sync_bad=owned,external_sync_bad=external,logs_over_limit=logs_over_limit(root,r,profile),cgroup_issues=cgroup_issues,resource_issues=resource_issues,sync_scan_complete=counts['complete'],expected_names=profile.expected_names if profile else q.ROSTER[:r.get('bots',8)])
 verdict=assess(snap)
 # No player names or peer addresses in persisted public-facing health status.
 if profile:verdict['master_policy']='PRIVATE_LOOPBACK_ADVERTISING_DISABLED'
 verdict.update(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),players=int(query['numplayers']) if query else None,expected_bots=r.get('bots',8),missing_roles=missing,disk_free_bytes=snap['disk_free'],owned_sync_bad=owned,external_sync_bad=external,processes_verified=not errors,query_fresh=query is not None and 0<=snap['now']-qt<=5,query_age_s=snap['now']-qt if query is not None else None,telemetry_fresh=telemetry,cgroup_cpu=cpu_stat,cgroup_memory_events=memory_events,cgroup_memory_current=memory_current,cgroup_memory_peak=memory_peak,host_memory_available=available,sync_scan_complete=counts['complete'])
 return snap,verdict
