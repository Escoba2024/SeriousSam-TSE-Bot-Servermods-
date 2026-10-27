#!/usr/bin/env python3
"""Owner-guarded, loopback-only Wine lifecycle. Public fleet is monitor-only."""
import argparse,fcntl,gzip,hashlib,json,math,os,re,select,shutil,signal,subprocess,sys,time
from contextlib import contextmanager
from pathlib import Path
import fleet_health as h
q=h.q
BASE=Path('/srv/tse-ops-runtime-20261021')
TEMPLATE=Path('/srv/tse-wine-runtime-20261020/public-eight-20261020-2140')
VANILLA=Path('/srv/tse-wine-runtime-20261020/install/vanilla')
BUILD=Path('/srv/tse-integrated-build-20261021-04/manifest.json')
HOUR=Path('/srv/tse-integration-runtime-20261021/eight-100513/result.json')

def owned_pidfd(info):
 fd=os.pidfd_open(info['pid'])
 if h.verify_process(info)!='LIVE':os.close(fd);raise RuntimeError('process identity changed before action')
 return fd

def wait_pidfd(fd,seconds):
 return bool(select.select([fd],[],[],seconds)[0])

def atomic(path,value):
 path=Path(path);tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');os.chmod(tmp,0o600);os.replace(tmp,path)

def event(path,value,limit=1000):
 p=Path(path);rows=json.loads(p.read_text()) if p.exists() else [];rows.append(dict(value,utc=time.time()));atomic(p,rows[-limit:])

def acquire_lock(path):
 f=Path(path).open('a')
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BaseException:f.close();raise
 return f

def validate_log_limit(c):
 limit=c.get('log_limit_bytes',32*1024**2)
 if type(limit)!=int or not 65536<=limit<=32*1024**2:raise ValueError('log limit must be 64 KiB..32 MiB')
 return limit

def validate_window_owners(seen,allowed):
 if any(pid not in allowed for pid in seen):raise RuntimeError('unregistered Retail window; close own observer first')

def retail_window_owners(display):
 listing=subprocess.check_output(['xwininfo','-display',display,'-root','-tree'],text=True);seen=[]
 for wid in re.findall(r'(0x[0-9a-fA-F]+) "Serious Sam \(',listing):
  prop=subprocess.check_output(['xprop','-display',display,'-id',wid,'_NET_WM_PID'],text=True);m=re.search(r'=\s*(\d+)\s*$',prop);seen.append(int(m[1]) if m else None)
 return seen

def roles_for(c,profile=None):
 return list(profile.role_names) if profile else ['server','botA']+(['botB'] if c['bots']==8 else [])

def validate_config(c,profile=None):
 if profile:
  from private_candidate_profile import validate_location
  root=validate_location(c['root'],c['port'],c['display'])
  if root!=profile.root or c['bots']!=8 or c['port']!=profile.port or c['display']!=profile.display:raise ValueError('private instance/profile mismatch')
  validate_log_limit(c);profile.verify_pins();return root
 if 'private_profile' in c:raise ValueError('verified instance-bound private profile required')
 try:
  root=Path(c['root']);port=c['port'];display=c['display'];bots=c['bots'];validate_log_limit(c)
  if not root.is_absolute() or not root.resolve().is_relative_to(BASE) or root.resolve()==BASE:raise ValueError('private root required')
  if type(port)!=int or not 26800<=port<=26998 or port%2:raise ValueError('private even port required')
  if not re.fullmatch(r':12[0-9]',display) or bots not in (1,4,8):raise ValueError('invalid display/population')
  if Path(c.get('build_manifest',''))!=BUILD or Path(c.get('template',''))!=TEMPLATE:raise ValueError('unpinned dependencies')
  build=json.loads(BUILD.read_text())
  if not build['build_ok'] or build['dll_sha256']!=h.DLL or q.sha(Path(build['candidate']))!=h.DLL:raise ValueError('invalid candidate')
  q.validate_public_evidence(json.loads(HOUR.read_text()),h.DLL)
  return root
 except (KeyError,TypeError,OSError,AssertionError) as e:raise ValueError('invalid instance manifest: '+str(e)) from e

def validate_state(c,r,profile=None):
 root=Path(c['root']);roles=roles_for(c,profile)
 if profile and r.get('private_profile_sha256')!=profile.profile_sha256:raise ValueError('state/private profile generation mismatch')
 cg='/sys/fs/cgroup/tse-ops-'+hashlib.sha256(str(root).encode()).hexdigest()[:12]
 if r.get('cgroup',cg)!=cg:raise ValueError('state cgroup outside owned instance')
 for role,info in r.get('processes',{}).items():
  if role not in roles or info.get('cwd')!=str(root/role):raise ValueError('state process outside owned instance')
  expected='DedicatedServer.exe' if role=='server' else 'SeriousSam.exe'
  if info.get('command','').replace('\\','/').split('/')[-1]!=expected or info.get('cgroup')!='0::'+cg.removeprefix('/sys/fs/cgroup'):raise ValueError('state command/cgroup outside owned instance')
 x=r.get('xvfb')
 if x and (x.get('cwd')!=str(root) or x.get('command')!='Xvfb' or x.get('cgroup')!='0::'+cg.removeprefix('/sys/fs/cgroup')):raise ValueError('state display outside owned instance')
 allowed={str(root/x) for role in roles for x in [role,'prefix-'+role]}
 if any(x not in allowed for x in r.get('mounts',[])):raise ValueError('state mount outside owned instance')

def recovery_action(role,names,bots,missing_seconds,profile=None):
 if profile:return profile.recovery_action(role,names,missing_seconds)
 if any(n not in q.ROSTER[:bots] for n in names):return 'HOLD_HUMANS'
 offset=4 if role=='botB' else 0;owned=q.ROSTER[offset:offset+(1 if bots==1 else 4)]
 if not set(owned)&set(names):return 'RESTART_ROLE'
 return 'WAIT_GHOSTS' if missing_seconds<30 else 'RESTART_FLEET'

def maintenance_action(over_limit,safe,humans,retry):
 if not over_limit:return 'NONE'
 if not safe or humans:return 'HOLD'
 return 'RESTART_FLEET' if retry else 'STOP_BUDGET_HOLD'

def retry_allowed(state,now=None):
 now=time.time() if now is None else now
 if any(t>now for t in state.get('attempts',[])):return False
 recent=[t for t in state.get('attempts',[]) if 0<=now-t<3600]
 return len(recent)<3 and (not recent or now-max(recent)>=30*(2**(len(recent)-1)))

def open_writers(paths):
 targets={(st.st_dev,st.st_ino) for p in paths for st in [Path(p).stat()]};found=[]
 if not targets:return found
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   for fd in (proc/'fd').iterdir():
    try:
     st=fd.stat()
     if (st.st_dev,st.st_ino) in targets:
      info=(proc/'fdinfo'/fd.name).read_text();flags=int(re.search(r'^flags:\s+(\d+)',info,re.M).group(1),8)
      if flags&os.O_ACCMODE != os.O_RDONLY:found.append(int(proc.name))
    except FileNotFoundError:pass
  except (FileNotFoundError,ProcessLookupError):pass
  except PermissionError:raise RuntimeError('cannot verify all open handles')
 return found

def archive_closed(paths,directory,budget=256*1024**2):
 paths=[Path(p) for p in paths if Path(p).exists()]
 if open_writers(paths):raise RuntimeError('live file handle; no copytruncate permitted')
 directory=Path(directory);directory.mkdir(exist_ok=True)
 used=sum(p.stat().st_size for p in directory.iterdir() if p.is_file())
 # Worst-case raw+gzip overhead: do not delete old evidence to make room.
 if used+sum(p.stat().st_size+1024 for p in paths)>budget:raise RuntimeError('archive budget exceeded; maintenance required')
 rows=[]
 for p in paths:
  digest=q.sha(p);name=p.parent.name+'-'+p.name+'-'+str(time.time_ns())+'.gz';dst=directory/name;tmp=dst.with_suffix('.tmp')
  with p.open('rb') as source,gzip.open(tmp,'wb',compresslevel=6) as out:shutil.copyfileobj(source,out)
  check=hashlib.sha256()
  with gzip.open(tmp,'rb') as f:
   for chunk in iter(lambda:f.read(1048576),b''):check.update(chunk)
  if check.hexdigest()!=digest or open_writers([p]) or q.sha(p)!=digest:tmp.unlink();raise RuntimeError('archive verification changed')
  row=dict(source=str(p),sha256=digest,archive=str(dst));manifest=directory/'manifest.json'
  history=json.loads(manifest.read_text()) if manifest.exists() else []
  history=(history+[dict(row,utc=time.time())])[-10000:]
  manifest_bytes=len((json.dumps(history,indent=2)+'\n').encode())
  committed=sum(f.stat().st_size for f in directory.iterdir() if f.is_file() and f not in [tmp,manifest])+tmp.stat().st_size+manifest_bytes
  if committed>budget:tmp.unlink();raise RuntimeError('archive budget exceeded including manifest')
  os.replace(tmp,dst);atomic(manifest,history);p.unlink();rows.append(row)
 return rows

def master_rule(port,owner):
 if type(port)!=int or not 26800<=port<=26998 or port%2:raise ValueError('private port required')
 if not re.fullmatch('[A-Za-z0-9-]+',owner):raise ValueError('invalid owner')
 return ['OUTPUT','-p','udp','--sport',str(port+1),'--dport','27900','-m','comment','--comment','tse-ops-'+owner,'-j','DROP']

def private_rules(port,owner):
 master=master_rule(port,owner)
 return [master,['INPUT','!','-i','lo','-p','udp','-m','multiport','--dports',str(port)+':'+str(port+1),'-m','comment','--comment','tse-ops-'+owner,'-j','DROP']]

def check_resource_reserve(sample,additional_bytes):
 available=sample.get('available_bytes');busy=sample.get('busy_percent')
 if type(available)!=int or available<0 or type(busy) not in (int,float) or not math.isfinite(busy) or not 0<=busy<=100 or type(additional_bytes)!=int or additional_bytes<0:raise RuntimeError('unverified host reserve')
 if available<768*1024**2+additional_bytes or busy>70:raise RuntimeError('host reserve below admission budget')

def host_resources():
 def cpu():return list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
 before=cpu();time.sleep(1);delta=[b-a for a,b in zip(before,cpu())]
 if sum(delta)<=0 or any(x<0 for x in delta):raise RuntimeError('unverified host CPU sample')
 return dict(available_bytes=h.available_memory(),busy_percent=100*(sum(delta)-delta[3]-delta[4])/sum(delta))

def close_prefix(prefix):
 alive=False
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   # Clients/helpers can outlive a crashed server. Only a live wineserver
   # makes -k valid; Wine9 returns1 for -k without a server, but -w returns0.
   if (proc/'comm').read_text().strip() not in ('wineserver','wineserver64'):continue
   if (proc/'stat').read_text().rsplit(') ',1)[1].split()[0]=='Z':continue
   alive |= ('WINEPREFIX='+str(prefix)).encode() in (proc/'environ').read_bytes().split(b'\0')
  except (FileNotFoundError,ProcessLookupError):pass
 # Preserve inaccessible-prefix and real command errors before any unmount.
 for arg in (['-k','-w'] if alive else ['-w']):
  subprocess.run(['runuser','-u','nobody','--','env','WINEPREFIX='+str(prefix),'wineserver',arg],check=True,capture_output=True,timeout=15)

def settled_process(process,executable,timeout=15):
 deadline=time.monotonic()+timeout
 while process.poll() is None:
  info=h.process_identity(process.pid)
  if info['command'].replace('\\','/').rsplit('/',1)[-1]==executable:return info
  if time.monotonic()>=deadline:break
  time.sleep(.1)
 raise RuntimeError('native executable did not settle: '+executable)

def _demote(cg):
 def child():
  (cg/'cgroup.procs').write_text(str(os.getpid()));os.setgid(65534);os.setuid(65534)
 return child

class Runtime:
 profile=None
 def __init__(self,config):
  self.config=Path(config);self.c=json.loads(self.config.read_text());self.native_locks=[]
  if 'private_profile' in self.c:
   from private_candidate_profile import load
   self.profile=load(self.c)
  self.root=validate_config(self.c,self.profile) if self.profile else validate_config(self.c);self.result=self.root/'result.json'
  self.lock=None
  try:
   if self.profile:
    # Share the existing M1 matrix/recovery ownership locks, including gaps
    # between their native stages. Nonblocking acquisition cannot deadlock.
    for path in ['/root/ssam-ai-backups/m1-completion-20261026-0155/matrix.lock','/srv/tse-session-qualification.lock']:
     self.native_locks.append(acquire_lock(path))
   self.lock=acquire_lock(self.root/'supervisor.lock')
   self.r=json.loads(self.result.read_text());self.roles=roles_for(self.c,self.profile)
   self.cg=Path('/sys/fs/cgroup')/('tse-ops-'+hashlib.sha256(str(self.root).encode()).hexdigest()[:12])
   self.boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
   self.r['log_limit_bytes']=validate_log_limit(self.c)
  except BaseException:
   self.close();raise
 def close(self):
  if self.lock:self.lock.close()
  for lock in reversed(getattr(self,'native_locks',[])):lock.close()
  self.native_locks=[]

 def save(self):atomic(self.result,self.r)
 def log(self,kind,**kw):event(self.root/'events.json',dict(kind=kind,**kw))
 def resources(self,additional_bytes):
  sample=host_resources();check_resource_reserve(sample,additional_bytes);self.log('RESOURCE_ADMISSION',additional_bytes=additional_bytes,**sample)
 @contextmanager
 def admission(self):
  if getattr(self,'_admitting',False):yield;return
  # Host-wide admission serializes separate instance controllers, including
  # their full startup, not just the instant when memory was sampled.
  with acquire_lock('/run/tse-ops-admission.lock'):
   self._admitting=True
   try:yield
   finally:self._admitting=False
 def specs(self):
  return [h.mount_spec(self.root,role,self.profile.source(role) if self.profile else TEMPLATE/('prefix-botA' if role=='prefix-botB' else role)) for game in self.roles for role in [game,'prefix-'+game]]
 def ownership(self):
  if self.profile:validate_state(self.c,self.r,self.profile)
  else:validate_state(self.c,self.r)
  if self.profile:self.profile.require_namespace();self.profile.verify_pins()
  for role,info in self.r.get('processes',{}).items():
   status=h.verify_process(info)
   if status not in ['LIVE','ABSENT']:raise RuntimeError(role+':'+status)
   if status=='LIVE' and self.r.get('boot_id')!=self.boot:raise RuntimeError('boot identity mismatch with live PID')
  x=self.r.get('xvfb')
  if x and h.verify_process(x) not in ['LIVE','ABSENT']:raise RuntimeError('Xvfb identity mismatch')
  if any(h.verify_process(i)=='LIVE' for i in list(self.r.get('processes',{}).values())+([x] if x else [])):
   for rule in private_rules(self.c['port'],self.cg.name):
    if subprocess.run(['iptables','-w','-C']+rule,capture_output=True).returncode:raise RuntimeError('private isolation rule missing/unverified')
  for m in self.specs():
   mounted=any(l.split()[4]==m['target'] for l in Path('/proc/self/mountinfo').read_text().splitlines())
   if mounted and not h.mount_matches(m):raise RuntimeError('foreign/replaced mount')
  allowed=set(map(int,(self.cg/'cgroup.procs').read_text().split())) if self.cg.exists() else set()
  # A controller can die after exec but before saving the new identity. Do not
  # treat unrecorded native roles in our cgroup as permission to start another.
  registered={info['pid'] for info in self.r.get('processes',{}).values()}
  if x:registered.add(x['pid'])
  for pid in allowed-registered:
   try:info=h.process_identity(pid)
   except FileNotFoundError:continue
   command=info['command'].replace('\\','/').rsplit('/',1)[-1]
   if command in ('DedicatedServer.exe','SeriousSam.exe','Xvfb'):raise RuntimeError('unregistered native process in owned cgroup')
  for port in [self.c['port'],self.c['port']+1]:
   if not h.udp_owners(port)<=allowed:raise RuntimeError('foreign port owner')
  for proc in Path('/proc').glob('[0-9]*'):
   try:
    env=(proc/'environ').read_bytes().split(b'\0')
    own=any(x.startswith(b'WINEPREFIX='+str(self.root).encode()+b'/prefix-') for x in env)
    if own and int(proc.name) not in allowed:raise RuntimeError('foreign process uses own Wine prefix')
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 def mounts(self):
  self.ownership()
  for m in self.specs():
   if not h.mount_matches(m):
    target=Path(m['target'])
    if not target.is_dir() or any(target.iterdir()):raise RuntimeError('mount target not empty')
    subprocess.run(['mount','-t','overlay','overlay','-o',','.join(k+'='+m[v] for k,v in [('lowerdir','lower'),('upperdir','upper'),('workdir','work')]),m['target']],check=True,capture_output=True)
   if not h.mount_matches(m):raise RuntimeError('mount replay failed')
  self.r['mounts']=[m['target'] for m in self.specs()];self.r['template']=str(TEMPLATE);self.save()
 def launch(self,role):
  with self.admission():self._launch(role)
 def _launch(self,role):
  self.ownership();info=self.r.get('processes',{}).get(role)
  if info and h.verify_process(info)=='LIVE':raise RuntimeError('refusing duplicate launch')
  self.resources((192 if role=='server' else (300 if self.profile else 384))*1024**2)
  game=self.root/role
  for name,want in q.PINS.items():
   if name=='GameMP.dll' and h.bot_role(role,self.profile):want=self.profile.candidate_sha256 if self.profile else h.DLL
   if q.sha(game/'Bin'/name)!=want:raise RuntimeError('runtime binary mismatch '+role+'/'+name)
  if role=='server':
   for port in [self.c['port'],self.c['port']+1]:
    with h.socket.socket(h.socket.AF_INET,h.socket.SOCK_DGRAM) as s:s.bind(('0.0.0.0',port))
  prefix=self.root/('prefix-'+role)
  close_prefix(prefix)
  logs=[self.root/(role+'-wine.log'),game/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log')]
  if h.bot_role(role,self.profile):logs.append(game/'Bin/BotTelemetry.csv')
  archive_closed(logs,self.root/'archives')
  if self.profile:self.profile.verify_settings()
  env=dict(os.environ,HOME=str(self.root/'home' if self.profile else self.root.parent),WINEARCH='win32',WINEDEBUG='-all',DISPLAY=self.c['display'],LIBGL_ALWAYS_SOFTWARE='1',GALLIUM_DRIVER='llvmpipe',LP_NUM_THREADS='1',XDG_CACHE_HOME=str(self.root/'home/cache' if self.profile else self.root.parent/'cache'),WINEPREFIX=str(prefix))
  cmd=['wine','Bin/DedicatedServer.exe','BotTest'] if role=='server' else ['wine','Bin/SeriousSam.exe','+connect','127.0.0.1:'+str(self.c['port']),'+quickjoin','+script','Scripts\\Session.ini' if self.profile else 'Scripts\\Integrated.ini']
  with (self.root/(role+'-wine.log')).open('wb') as out:p=subprocess.Popen(cmd,cwd=game,env=env,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,preexec_fn=_demote(self.cg))
  expected='DedicatedServer.exe' if role=='server' else 'SeriousSam.exe'
  info=settled_process(p,expected)
  self.r.setdefault('processes',{})[role]=info;self.save();self.log('LAUNCH',role=role,pid=p.pid)
 def start(self):
  with self.admission():self._start()
 def _start(self):
  if self.profile:validate_config(self.c,self.profile)
  else:validate_config(self.c)
  if os.statvfs('/').f_bavail*os.statvfs('/').f_frsize<h.MIN_FREE:raise RuntimeError('disk reserve below 8 GiB')
  if self.profile:self.profile.require_namespace()
  else:q.validate_master_resolution()
  self.ownership()
  live=[role for role,info in self.r.get('processes',{}).items() if h.verify_process(info)=='LIVE']
  if live:
   if set(live)!=set(self.roles):raise RuntimeError('partial fleet: reconcile with monitor; no duplicate startup')
   for m in self.specs():
    if not h.mount_matches(m):raise RuntimeError('live fleet lost own mount')
   self.log('ADOPT');return
  self.resources(self.profile.startup_budget_bytes if self.profile else (128+192+384*(len(self.roles)-1))*1024**2)
  for rule in private_rules(self.c['port'],self.cg.name):
   probe=subprocess.run(['iptables','-w','-C']+rule,capture_output=True)
   if probe.returncode==1:subprocess.run(['iptables','-w','-I']+rule,check=True,capture_output=True)
   elif probe.returncode:raise RuntimeError('cannot verify private isolation rule')
  self.r['private_network_guards']=private_rules(self.c['port'],self.cg.name);self.save()
  self.mounts();self.cg.mkdir(exist_ok=True);(self.cg/'cpu.max').write_text('max 100000');self.r.update(cgroup=str(self.cg),boot_id=self.boot,game_port=self.c['port'],query_port=self.c['port']+1,display=self.c['display'],bots=self.c['bots'],dll_sha256=self.profile.candidate_sha256 if self.profile else h.DLL)
  xinfo=self.r.get('xvfb')
  if xinfo and h.verify_process(xinfo) not in ['ABSENT','LIVE']:raise RuntimeError('display PID mismatch')
  if not xinfo or h.verify_process(xinfo)=='ABSENT':
   display=self.c['display'][1:]
   if Path('/tmp/.X'+display+'-lock').exists() or Path('/tmp/.X11-unix/X'+display).exists():raise RuntimeError('display is occupied/stale; no blind lock deletion')
   archive_closed([self.root/'xvfb.log'],self.root/'archives')
   with (self.root/'xvfb.log').open('ab') as out:x=subprocess.Popen(['Xvfb',self.c['display'],'-screen','0','640x480x24','-nolisten','tcp','-noreset'],cwd=self.root,stdout=out,stderr=subprocess.STDOUT,preexec_fn=_demote(self.cg),start_new_session=True)
   self.r['xvfb']=settled_process(x,'Xvfb');self.save();time.sleep(2)
   if h.verify_process(self.r['xvfb'])!='LIVE':raise RuntimeError('Xvfb failed')
  if self.profile:
   for role in self.roles:
    self.launch(role);time.sleep(8 if role in ('server','vanilla') else 20)
  else:
   self.launch('server');time.sleep(8);self.launch('botA')
   if 'botB' in self.roles:time.sleep(5);self.launch('botB')
  self.r.update(status='OWNED_ISOLATED_RUNNING',left_running=True);self.save()
 def signal_role(self,role,sig):
  self.ownership();info=self.r['processes'][role]
  if h.verify_process(info)=='LIVE':
   # pidfd binds the signal to the checked kernel process, closing PID reuse races.
   fd=os.pidfd_open(info['pid'])
   try:
    if h.verify_process(info)!='LIVE':raise RuntimeError('identity changed before signal')
    signal.pidfd_send_signal(fd,sig)
   finally:os.close(fd)
 def stop_role(self,role):
  info=self.r['processes'].get(role)
  if not info or h.verify_process(info)=='ABSENT':return
  self.ownership();fd=owned_pidfd(info)
  try:
   if role!='server':
    try:q.close_window(info['pid'],self.c['display'])
    except (OSError,subprocess.SubprocessError):self.log('WM_CLOSE_FAILED',role=role)
    if wait_pidfd(fd,15):return
   if h.verify_process(info)!='LIVE':raise RuntimeError('identity changed before TERM')
   signal.pidfd_send_signal(fd,signal.SIGTERM)
   if wait_pidfd(fd,10):return
   if h.verify_process(info)!='LIVE':raise RuntimeError('identity changed before KILL')
   signal.pidfd_send_signal(fd,signal.SIGKILL)
   if not wait_pidfd(fd,5):raise RuntimeError('owned process did not exit')
  finally:os.close(fd)
 def no_humans(self):
  try:names=h.query_roster(q.query(self.c['port']+1))
  except ValueError as e:raise RuntimeError('human/unknown player hold') from e
  if any(n not in (self.profile.expected_names if self.profile else q.ROSTER[:self.c['bots']]) for n in names):raise RuntimeError('human/unknown player hold')
 def stop(self):
  self.ownership()
  xinfo=self.r.get('xvfb')
  if xinfo and h.verify_process(xinfo)=='LIVE':validate_window_owners(retail_window_owners(self.c['display']),{i['pid'] for i in self.r.get('processes',{}).values()})
  if any(h.verify_process(i)=='LIVE' for role,i in self.r.get('processes',{}).items() if role=='server'):self.no_humans()
  for role in reversed(self.roles):self.stop_role(role)
  for role in self.roles:
   prefix=self.root/('prefix-'+role)
   # A repeated stop sees empty, unmounted prefix targets. Never ask Wine
   # to enter those directories; ownership/cgroup checks still hold below.
   source=self.profile.source('prefix-'+role) if self.profile else TEMPLATE/('prefix-botA' if role=='botB' else 'prefix-'+role)
   if h.mount_matches(h.mount_spec(self.root,'prefix-'+role,source)):close_prefix(prefix)
  x=self.r.get('xvfb')
  if x and h.verify_process(x)=='LIVE':
   fd=owned_pidfd(x)
   try:
    signal.pidfd_send_signal(fd,signal.SIGTERM)
    if not wait_pidfd(fd,10):raise RuntimeError('Xvfb exit timeout')
   finally:os.close(fd)
  self.ownership()
  if self.cg.exists() and (self.cg/'cgroup.procs').read_text().strip():raise RuntimeError('owned cgroup not empty; no unmount')
  for m in reversed(self.specs()):
   if h.mount_matches(m):subprocess.run(['umount',m['target']],check=True,capture_output=True)
  for rule in reversed(private_rules(self.c['port'],self.cg.name)):
   probe=subprocess.run(['iptables','-w','-C']+rule,capture_output=True)
   if probe.returncode==0:subprocess.run(['iptables','-w','-D']+rule,check=True,capture_output=True)
   elif probe.returncode!=1:raise RuntimeError('cannot verify private isolation cleanup')
  self.r.update(status='OWNED_ISOLATED_STOPPED',left_running=False);self.save();self.log('STOP')
 def reconcile(self):
  self.ownership();snap,health=h.collect(self.result,self.profile) if self.profile else h.collect(self.result);atomic(self.root/'health.json',health)
  if health['status']=='HEALTHY':self.r['last_no_humans']=time.time();self.save()
  maintenance=maintenance_action(snap['logs_over_limit'],health['safe_recovery'],bool(health['humans']),retry_allowed(self.r))
  if maintenance in ['RESTART_FLEET','STOP_BUDGET_HOLD']:
   self.no_humans();self.stop()
   if maintenance=='RESTART_FLEET':
    self.r.setdefault('attempts',[]).append(time.time());self.save();self.start()
   self.log('LOG_MAINTENANCE',action=maintenance);return health
  if health['safe_recovery'] and health['recover_roles']:
   if not retry_allowed(self.r):self.log('CIRCUIT_OPEN');return health
   self.no_humans();now=time.time();names=[n for k,n in snap['query'].items() if re.fullmatch(r'player_\d+',k)];plans={}
   for role in health['recover_roles']:
    since=self.r.setdefault('missing_since',{}).setdefault(role,now);plans[role]=recovery_action(role,names,self.c['bots'],now-since,profile=self.profile)
   self.save()
   if 'WAIT_GHOSTS' in plans.values() or 'HOLD_HUMANS' in plans.values():return health
   self.r.setdefault('attempts',[]).append(now);self.r['attempts']=self.r['attempts'][-3:];self.save()
   if 'RESTART_FLEET' in plans.values():
    self.stop();self.start();self.r['missing_since']={};self.save();self.log('RECOVER_GHOST_FLEET',roles=health['recover_roles']);return health
   for role in health['recover_roles']:self.launch(role)
   self.r['missing_since']={};self.save();self.log('RECOVER',roles=health['recover_roles'])
  if 'server' in snap['missing']:
   # Query uncertainty alone cannot restart anything. A confirmed exited server,
   # recent no-human snapshot and empty own ports are all necessary.
   now=time.time()
   # Only loss-of-server observations are expected here. All other safety
   # holds, including OOM/throttle, owned sync faults and incomplete scans,
   # must also block this separate recovery path.
   blocking=set(health['alerts'])-{'QUERY_UNCERTAIN','TELEMETRY_STALE','EXTERNAL_CLIENT_SYNC','LOG_LIMIT_MAINTENANCE_HOLD'}
   if not blocking and not health['humans'] and not snap['identity_errors'] and snap['disk_free']>=h.MIN_FREE and snap['dll_valid'] and snap['mounts_owned'] and snap['master_ok'] and 0<=now-self.r.get('last_no_humans',0)<=20 and not h.udp_owners(self.c['port']) and not h.udp_owners(self.c['port']+1) and retry_allowed(self.r):
    self.r.setdefault('attempts',[]).append(now);self.save();self.stop();self.start();self.log('RECOVER_SERVER')
  return health

def prepare(parent,port,display,bots):
 parent=Path(parent).resolve()
 if not parent.is_relative_to(BASE) or parent==BASE:raise ValueError('private preparation parent required')
 validate_config(dict(root=str(parent/'preflight'),port=port,display=display,bots=bots,build_manifest=str(BUILD),template=str(TEMPLATE)))
 BASE.mkdir(mode=0o755,exist_ok=True)
 if BASE.is_symlink() or BASE.stat().st_uid!=0:raise ValueError('private base ownership mismatch')
 os.chmod(BASE,0o755)
 parent.mkdir(parents=True,exist_ok=True);stage={1:'one',4:'four',8:'eight'}[bots]
 before=set(parent.glob(stage+'-*/result.json'))
 cmd=[sys.executable,str(Path(q.__file__)), '--runtime',str(parent),'--template',str(TEMPLATE),'--vanilla',str(VANILLA),'--build-manifest',str(BUILD),'--stage',stage,'--duration','3600','--port',str(port),'--display',display,'--prepare-only']
 subprocess.run(cmd,check=True,capture_output=True);after=set(parent.glob(stage+'-*/result.json'))-before
 if len(after)!=1:raise RuntimeError('ambiguous prepared result')
 result=after.pop();root=result.parent;c=dict(root=str(root),port=port,display=display,bots=bots,build_manifest=str(BUILD),template=str(TEMPLATE));validate_config(c)
 # Overlay upper files already contain only private changes. No live mount is modified.
 startup=root/'layers/server/upper/Scripts/Dedicated_startup.ini'
 with startup.open('a') as f:f.write('\nser_bHeartbeatGameSpy=1;\nser_bReportSyncOK=1;\n')
 for role in ['botA']+(['botB'] if bots==8 else []):
  script=root/('layers/'+role+'/upper/Scripts/Integrated.ini')
  with script.open('a') as f:f.write('\nbot_iLogEvery=200;\nbot_bDiag=0;\n')
 os.chown(parent,0,0);os.chmod(parent,0o755);os.chown(root,0,0);os.chmod(root,0o755)
 cache=parent/'cache';cache.mkdir(exist_ok=True);os.chown(cache,65534,65534)
 atomic(root/'instance.json',c);r=json.loads(result.read_text());r.update(template=str(TEMPLATE),mounts=[],boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip());atomic(result,r);print(str(root/'instance.json'))

def read_only_profile(config,result):
 if config is None:return None
 from private_candidate_profile import load
 c=json.loads(Path(config).read_text())
 if 'private_profile' not in c:return None
 profile=load(c)
 if Path(result).resolve()!=profile.root/'result.json':raise ValueError('read-only result/profile mismatch')
 return profile

def monitor(result,output,interval,profile=None):
 output=Path(output);output.mkdir(parents=True,exist_ok=True);lock=acquire_lock(output/'monitor.lock')
 try:
  while True:
   try:_,status=h.collect(result,profile) if profile else h.collect(result)
   except Exception as e:status=dict(status='BLOCKED',alerts=['MONITOR_EXCEPTION:'+type(e).__name__],safe_recovery=False,utc=time.time())
   atomic(output/'health.json',status);event(output/'events.json',status,limit=256);time.sleep(interval)
 finally:lock.close()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','start','stop','run','health','monitor']);p.add_argument('--config',type=Path);p.add_argument('--parent',type=Path);p.add_argument('--port',type=int,default=26820);p.add_argument('--display',default=':125');p.add_argument('--bots',type=int,choices=[1,4,8],default=8);p.add_argument('--result',type=Path);p.add_argument('--output',type=Path);p.add_argument('--interval',type=float,default=10);a=p.parse_args()
 if a.action=='prepare':
  if a.config:
   from private_candidate_profile import prepare as prepare_private
   config=json.loads(a.config.read_text())
   if 'private_profile' not in config:raise ValueError('explicit private candidate configuration required')
   print(prepare_private(config))
  else:prepare(a.parent,a.port,a.display,a.bots)
  return
 if a.action in ('health','monitor'):
  profile=read_only_profile(a.config,a.result)
  if a.action=='health':
   result=h.collect(a.result,profile) if profile else h.collect(a.result)
   print(json.dumps(result[1],indent=2))
  else:monitor(a.result,a.output,a.interval,profile=profile)
  return
 runtime=Runtime(a.config)
 try:
  if a.action=='stop':runtime.stop()
  else:
   runtime.start()
   if a.action=='run':
    while True:
     try:health=runtime.reconcile()
     except Exception as e:runtime.log('BLOCKED',error=str(e));health=dict(status='BLOCKED',alerts=[str(e)],safe_recovery=False);atomic(runtime.root/'health.json',health)
     time.sleep(a.interval)
 finally:runtime.close()
if __name__=='__main__':main()
