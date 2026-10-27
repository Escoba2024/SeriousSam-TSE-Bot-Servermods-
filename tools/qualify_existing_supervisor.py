#!/usr/bin/env python3
"""Thin private core qualification of the existing operations.Runtime.

Import/default CLI starts nothing. Explicit execution requires a reviewed policy,
actual accepted duration AND canonical fault evidence. This initial driver does
not implement every M1 probe and can NEVER declare all supervisor gates or M1
complete. No second supervisor, service or public startup is implemented.
"""
from __future__ import annotations
import argparse
import ctypes
import fcntl
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

REPO=Path(__file__).resolve().parents[1]
TOOLS=REPO/'tools'
FAULT_BASE=Path('/root/ssam-ai-backups/m1-prefilter-matrix-20261026-idle-r3')
LEGACY_BASE=Path('/root/ssam-ai-backups/m1-completion-20261026-0155')
LEGACY_NATIVE=Path('/srv/tse-cecil-guard-20261026/tools')
GLOBAL_HOLD=Path('/root/ssam-ai-backups/m1-supervisor-native-HOLD.json')
HOUR_SECONDS=3600
BASELINE_SECONDS=120
CLEANUP_SECONDS=990
TOTAL_BUDGET_SECONDS=7500
POLL_SECONDS=5
CORE_PHASES=('baseline','epoch_mismatch_no_signal','client_fault_rejoin','server_fault_recovery',
             'following_generation_hour','closed_writer_archives','originals','cleanup')
DEFERRED_PHASES=('unknown_original_guest_hold','stale_health_hold','duplicate_controller',
                 'persisted_backoff','three_per_hour_circuit','log_threshold_maintenance')
FAULT_ROOTS=(
 ('client',Path('/srv/tse-session-qualification-master-m1-client-fault-prefilter-20261026')),
 ('server_a',Path('/srv/tse-session-qualification-master-m1-server-fault-a-prefilter-20261026')),
 ('server_b',Path('/srv/tse-session-qualification-master-m1-server-fault-b-prefilter-20261026')))


def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
 with Path(path).open('rb') as stream:data=stream.read(16*1024**2+1)
 if len(data)>16*1024**2:raise ValueError('bounded JSON object required')
 value=json.loads(data)
 if not isinstance(value,dict):raise ValueError('JSON object required')
 return value


def atomic(path,value):
 path=Path(path);tmp=path.with_name(path.name+'.tmp')
 tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.chmod(0o600);tmp.replace(path)


def finite(value):
 return type(value) in (int,float) and math.isfinite(value)


def guard_sample(sample,overload):
 errors=[]
 for key,minimum in [('available_mib',768),('disk_free_gib',8)]:
  if not finite(sample.get(key)) or sample[key]<minimum:errors.append(key.upper())
 busy=sample.get('host_busy_percent')
 if not finite(busy) or not 0<=busy<=100:errors.append('CPU_SAMPLE_INVALID');overload=0
 else:overload=overload+1 if busy>=85 else 0
 if overload>=3:errors.append('THREE_CPU_SAMPLES_GE85')
 if sample.get('public_disabled') is not True:errors.append('PUBLIC_NOT_PROVEN_DISABLED')
 return dict(abort=bool(errors),overload=overload,reasons=errors)


def validate_fault_metadata(state):
 if (state.get('status')!='FAULT_QUALIFICATION_ACCEPTED' or state.get('m1_complete') is not False or
     'active' in state or state.get('client_recovery',{}).get('status')!='PASS_NATIVE_OWNED_CLIENT_RECOVERY' or
     state.get('client_recovery',{}).get('original_observer_preserved') is not True or
     state.get('server_recovery',{}).get('status')!='PASS_NATIVE_PRIVATE_GENERATION_RECOVERY' or
     state.get('server_recovery',{}).get('restored_bots')!=8 or
     state.get('server_recovery_admission',{}).get('action')!='RESTART_ONE_PRIVATE_GENERATION' or
     state.get('server_recovery_admission',{}).get('reasons')!=[]):
  raise ValueError('complete canonical native fault evidence required')


def core_verdict(phases):
 good=all(phases.get(name,{}).get('status')=='PASS_NATIVE' for name in CORE_PHASES)
 return dict(status='CORE_QUALIFIED_MORE_NATIVE_GATES_REQUIRED' if good else 'BLOCKED',
             all_supervisor_gates_accepted=False,m1_complete=False,
             not_tested=list(DEFERRED_PHASES),scope='EXISTING_PRIVATE_SUPERVISOR_CORE_ONLY')


def build_inner_command(policy,digest,evidence):
 if not re.fullmatch('[0-9a-f]{64}',str(digest)):raise ValueError('caller-pinned policy required')
 return ['unshare','--net','--',sys.executable,str(Path(__file__).resolve()),'--execute','--inner',
         '--policy',str(policy),'--policy-sha256',digest,'--evidence-root',str(evidence)]


def request_abort(owned,state,inner):
 # Never use OwnedProcess.stop(): it escalates to KILL, which is forbidden for
 # the namespace parent while native cleanup may still be in progress.
 if owned is None or owned.process.poll() is not None or state.get('abort_requested'):return
 if inner.get('phase') in ('CLEANUP_IN_PROGRESS','CLEANUP_HOLD'):return
 try:signal.pidfd_send_signal(owned.pidfd,signal.SIGINT)
 except ProcessLookupError:pass
 state['abort_requested']=True
 state['abort_at_mono']=time.monotonic()


def modules():
 sys.path.insert(0,str(TOOLS/'operations'))
 import fleet_supervisor as supervisor
 import private_candidate_profile as profile
 from native_owned_process import OwnedProcess
 return supervisor,profile,OwnedProcess


def source_names(profile_module):
 return set(profile_module.OPERATIONS_SOURCES)|{
  'tools/qualify_existing_supervisor.py','tools/native_owned_process.py',
  'tools/qualify_prefilter_m1_recovery.py','performance/log_error_prefilter.py'}


def policy_source_pins(policy):
 return {REPO/name:digest for name,digest in policy['source_sha256'].items()}


def originals(supervisor,profile_module):
 for name,digest in supervisor.q.PINS.items():
  path=(profile_module.TEMPLATE/'server/Bin'/name if name=='DedicatedServer.exe'
        else profile_module.VANILLA/'Bin'/name)
  if sha(path)!=digest:raise ValueError('original Retail binary changed: '+name)
 return True


def public_absent():
 try:
  for table in ('udp','udp6'):
   for line in Path('/proc/1/net',table).read_text().splitlines()[1:]:
    if int(line.split()[1].rsplit(':',1)[1],16) in (25600,25601):return False
  host_ns=os.readlink('/proc/1/ns/net')
  for proc in Path('/proc').glob('[0-9]*'):
   try:
    comm=(proc/'comm').read_text().strip().casefold()
    if not comm.startswith(('serioussam','dedicatedserver')):continue
    fields=(proc/'stat').read_text().rsplit(') ',1)[1].split()
    if fields[0]!='Z' and os.readlink(proc/'ns/net')==host_ns:return False
   except FileNotFoundError:continue
  return True
 except (OSError,ValueError,IndexError):return False


def cpu():
 return list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))


def host_sample(before):
 after=cpu();d=[b-a for a,b in zip(before,after)]
 mem=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))/1024
 fs=os.statvfs('/srv')
 return dict(at=time.time(),host_busy_percent=100*(sum(d)-d[3]-d[4])/max(1,sum(d)),
             available_mib=mem,disk_free_gib=fs.f_bavail*fs.f_frsize/1024**3,
             public_disabled=public_absent()),after


def census(root,cgroup,*,allow_missing_cgroup=False):
 """Independent read-only census; discovered PIDs are NEVER signal targets."""
 root=Path(root).resolve();cgroup=Path(cgroup);errors=[];live=[];mounts=[]
 if cgroup.parent!=Path('/sys/fs/cgroup') or not re.fullmatch(r'tse-(ops-[0-9a-f]{12}|sessions-[0-9]+)',cgroup.name):
  errors.append('UNBOUND_CGROUP')
 else:
  try:
   if (cgroup/'cgroup.procs').read_text().strip():errors.append('CGROUP_NOT_EMPTY')
  except FileNotFoundError:
   if not allow_missing_cgroup:errors.append('CGROUP_MISSING')
  except OSError:errors.append('CGROUP_UNREADABLE')
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   fields=(proc/'stat').read_text().rsplit(') ',1)[1].split()
   if fields[0]=='Z':continue
   cwd=Path(os.readlink(proc/'cwd'))
   belongs=cwd.is_relative_to(root) or ('0::'+str(cgroup).removeprefix('/sys/fs/cgroup')) in (proc/'cgroup').read_text().splitlines()
   if not belongs:
    prefix=b'WINEPREFIX='+str(root).encode()+b'/'
    belongs=any(item.startswith(prefix) for item in (proc/'environ').read_bytes().split(b'\0'))
   if belongs:live.append(int(proc.name))
  except FileNotFoundError:continue
  except ProcessLookupError:continue
  except (OSError,ValueError,IndexError):errors.append('INCOMPLETE_PROC_CENSUS')
 try:
  for line in Path('/proc/self/mountinfo').read_text().splitlines():
   fields=line.split(' - ',1)[0].split()
   if len(fields)<5:raise ValueError('malformed mount table')
   if Path(fields[4]).is_relative_to(root):mounts.append(fields[4])
 except (OSError,ValueError):errors.append('INCOMPLETE_MOUNT_CENSUS')
 if live:errors.append('LIVE_OWNED_PROCESSES')
 if mounts:errors.append('MOUNTS_REMAIN')
 return dict(clean=not errors,errors=sorted(set(errors)),cgroup=str(cgroup),live_processes=live,mounts=mounts)


def fault_pins():
 """Verify canonical fault source policies and direct preserved native receipts."""
 expected={LEGACY_BASE/'duration-policy.json':'8dc8d542291bd52ef204d9bacf9cd922a9fc67b7162bc6427552cf46c655d399',
           LEGACY_BASE/'manus-stage8-policy.json':'9e76b236c0dd92bd58cd48b5638eade95d8974a23dd81f1c24924f700fa0cdbd'}
 for path,digest in expected.items():
  if sha(path)!=digest:raise ValueError('canonical fault policy drift')
 policy=read(LEGACY_BASE/'duration-policy.json')
 for name,digest in policy['harness_sha256'].items():
  expected[LEGACY_NATIVE/name]=digest
 for name,digest in read(LEGACY_BASE/'manus-stage8-policy.json')['stage8_additional_input_sha256'].items():
  path=TOOLS/name if name=='native_owned_process.py' else LEGACY_NATIVE.parent/name if name.startswith('poc/') else LEGACY_NATIVE/name
  expected[path]=digest
 for kind,root in FAULT_ROOTS:
  result=read(root/'result.json');guard=read(root/'host-guard.json')
  if (result.get('dll_sha256')!='7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf' or
      result.get('original_client') is not True or result.get('cecil_p1') is not True or
      guard.get('status')!='FINISHED' or guard.get('error') is not None or guard.get('public_disabled') is not True):
   raise ValueError('direct canonical fault evidence mismatch')
  if kind=='server_a':
   if result.get('status')!='FAIL' or result.get('error')!='query uncertain for more than 15 seconds' or guard.get('child_exitcode')!=1:
    raise ValueError('canonical injected server loss mismatch')
  elif result.get('status')!='PASS_LIMITED_SESSION_LIFECYCLE' or guard.get('child_exitcode')!=0 or result.get('all_bots_drained') is not True:
   raise ValueError('canonical successful native fault generation mismatch')
  check=census(root,result['cgroup'])
  if not check['clean']:raise ValueError('canonical fault cleanup not clean')
  for name in ('result.json','host-guard.json'):expected[root/name]=sha(root/name)
 for path,digest in expected.items():
  if sha(path)!=digest:raise ValueError('canonical fault source/receipt drift: '+str(path))
 return expected


def admission(args):
 if os.geteuid()!=0 or os.uname().nodename!='ubuntu-4gb-nbg1-2':raise ValueError('authorized private Hetzner host required')
 if GLOBAL_HOLD.exists():raise ValueError('persistent supervisor cleanup HOLD requires manual verified resolution')
 if args.policy is None or not re.fullmatch('[0-9a-f]{64}',str(args.policy_sha256)) or sha(args.policy)!=args.policy_sha256:
  raise ValueError('explicit reviewed source policy required')
 policy=read(args.policy)
 if set(policy)!={'schema','config','config_sha256','fault_sha256','source_sha256'} or policy['schema']!='PARENT_REVIEWED_EXISTING_SUPERVISOR_CORE_V1':
  raise ValueError('reviewed qualifier policy schema required')
 supervisor,profile_module,owned_class=modules()
 if set(policy['source_sha256'])!=source_names(profile_module):raise ValueError('complete exact qualifier source inventory required')
 for name,digest in policy['source_sha256'].items():
  if not re.fullmatch('[0-9a-f]{64}',str(digest)) or sha(REPO/name)!=digest:raise ValueError('reviewed qualifier source drift')
 config=Path(policy['config'])
 if not config.is_absolute() or sha(config)!=policy['config_sha256']:raise ValueError('private config pin mismatch')
 fault=FAULT_BASE/'recovery-qualification.json'
 if sha(fault)!=policy['fault_sha256']:raise ValueError('canonical fault receipt pin required')
 validate_fault_metadata(read(fault))
 # profile.load performs the complete accepted matrix/source/DLL/config audit.
 profile=profile_module.load(read(config));profile.verify_pins();originals(supervisor,profile_module)
 pins=fault_pins();pins.update(policy_source_pins(policy));pins[fault]=policy['fault_sha256'];pins[config]=policy['config_sha256'];pins[Path(args.policy)]=args.policy_sha256
 if not public_absent():raise ValueError('public game runtime not proven disabled')
 return supervisor,profile_module,owned_class,profile,config,policy,pins


def verify_context(context):
 supervisor,profile_module,_,profile,_,_,pins=context
 profile.verify_pins();originals(supervisor,profile_module)
 for path,digest in pins.items():
  if sha(path)!=digest:raise ValueError('canonical qualification input drift')


def generations(runtime):
 return {role:{k:runtime.r['processes'][role][k] for k in ('pid','start_ticks','cwd','command','cgroup')} for role in runtime.roles}


def sampled(runtime):
 import fleet_health as health_module
 health=runtime.reconcile();now=time.monotonic();resources={}
 for role,info in runtime.r['processes'].items():
  status=health_module.verify_process(info)
  resource=dict(status=status)
  if status=='LIVE':
   try:
    text=Path('/proc',str(info['pid']),'status').read_text()
    resource.update(cpu_s=health_module.q.cpu(info['pid']),rss_kib=int(re.search(r'^VmRSS:\s+(\d+)',text,re.M)[1]))
   except (OSError,ValueError,TypeError):resource=dict(status='EXITED_DURING_RESOURCE_READ')
  resources[role]=resource
 return dict(at=time.time(),mono=now,health=health,generations=generations(runtime),process_resources=resources,
             log_bytes={str(p.relative_to(runtime.root)):p.stat().st_size for p in runtime_specs(runtime) if p.is_file()})


def runtime_specs(runtime):
 # Profile-aware read-only list; existing Runtime owns every action.
 import fleet_health as health
 return health.log_paths(runtime.root,runtime.r,runtime.profile)


def save_inner(evidence,state):
 state['heartbeat_mono']=time.monotonic();state['utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
 atomic(evidence/'inner.json',state)


def step(runtime,evidence,state):
 row=sampled(runtime)
 with (evidence/'native-samples.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
 save_inner(evidence,state)
 return row


def healthy(row):
 h=row['health']
 return set(row['process_resources'])==set(row['generations']) and all(r.get('status')=='LIVE' for r in row['process_resources'].values()) and h.get('status')=='HEALTHY' and h.get('safe_recovery') is True and h.get('query_fresh') is True and h.get('telemetry_fresh') is True and h.get('owned_sync_bad')==0 and h.get('sync_scan_complete') is True


def wait_healthy(runtime,evidence,state,seconds,condition=lambda row:True):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  row=step(runtime,evidence,state)
  if healthy(row) and condition(row):return row
  time.sleep(POLL_SECONDS)
 raise RuntimeError('bounded native healthy/identity restoration timeout')


def measure_healthy(runtime,evidence,state,seconds,frozen):
 begin=None;previous=None;first=None;last=None;count=0;peak_rss={};minimum_host_memory=None
 while True:
  row=step(runtime,evidence,state)
  if not healthy(row) or row['generations']!=frozen:raise RuntimeError('healthy generation/roster/telemetry continuity lost')
  if previous is not None and row['mono']-previous>15:raise RuntimeError('native measurement gap exceeds15seconds')
  if begin is None:begin=row['mono']
  previous=row['mono'];count+=1;first=first or row;last=row
  for role,resource in row['process_resources'].items():peak_rss[role]=max(peak_rss.get(role,0),resource.get('rss_kib',0))
  mem=row['health'].get('host_memory_available')
  if finite(mem):minimum_host_memory=mem if minimum_host_memory is None else min(minimum_host_memory,mem)
  if row['mono']-begin>=seconds:break
  time.sleep(min(POLL_SECONDS,max(.01,seconds-(time.monotonic()-begin))))
 return dict(status='PASS_NATIVE',elapsed_s=last['mono']-begin,samples=count,generations=frozen,
             first_log_bytes=first['log_bytes'],last_log_bytes=last['log_bytes'],
             peak_rss_kib=peak_rss,minimum_host_memory_bytes=minimum_host_memory,
             process_cpu_percent={role:100*(last['process_resources'][role]['cpu_s']-first['process_resources'][role]['cpu_s'])/(last['mono']-first['mono']) for role in frozen})


def scan_logs(runtime):
 sys.path.insert(0,str(REPO))
 from performance.log_error_prefilter import make_runtime_error_matcher
 matcher=make_runtime_error_matcher()
 import fleet_health as health
 if matcher.pattern.pattern!=health.q.BAD.pattern+r'|FatalError:':raise RuntimeError('unreviewed native log expression')
 scanned=[]
 for role in runtime.roles:
  path=runtime.root/role/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log')
  if not path.is_file() or not path.stat().st_size:raise RuntimeError('complete native logs missing')
  if path.stat().st_size>32*1024**2:raise RuntimeError('native log exceeds bounded scan')
  if matcher.search(path.read_text(errors='replace')):raise RuntimeError('native error/SYNCBAD marker in complete log')
  scanned.append(dict(role=role,sha256=sha(path),bytes=path.stat().st_size))
 return scanned


def verify_archives(root,*,start_index=0):
 root=Path(root);rows=json.loads((root/'archives/manifest.json').read_text());proof=[];total=0
 if not isinstance(rows,list) or type(start_index) is not int or not 0<=start_index<len(rows):raise RuntimeError('actual new closed-writer archives absent')
 for row in rows[start_index:]:
  archive=Path(row['archive']);source=Path(row['source'])
  if archive.parent!=root/'archives' or not source.is_relative_to(root) or archive.is_symlink():raise RuntimeError('unbound native archive')
  digest=hashlib.sha256();size=0
  with gzip.open(archive,'rb') as stream:
   while True:
    chunk=stream.read(1024**2)
    if not chunk:break
    size+=len(chunk);total+=len(chunk)
    if size>32*1024**2 or total>256*1024**2:raise RuntimeError('bounded native archive verification exceeded')
    digest.update(chunk)
  if digest.hexdigest()!=row['sha256']:raise RuntimeError('native archived bytes fail SHA256')
  proof.append(dict(archive=str(archive),sha256=row['sha256'],bytes=size))
 return dict(status='ARCHIVE_BYTES_VERIFIED',archives=proof,scope='CONTENT_VERIFICATION_ONLY_NOT_NATIVE_ACCEPTANCE')


def wrong_epoch_probe(runtime,evidence,state,role):
 before=generations(runtime);original=dict(runtime.r['processes'][role]);bad=dict(original,start_ticks=original['start_ticks']+1)
 runtime.r['processes'][role]=bad
 try:
  try:runtime.signal_role(role,signal.SIGTERM)
  except RuntimeError as exc:
   if 'PID_REUSED' not in str(exc):raise
   rejected=str(exc)
  else:raise RuntimeError('wrong epoch unexpectedly authorized a native signal')
 finally:runtime.r['processes'][role]=original
 row=wait_healthy(runtime,evidence,state,60)
 if row['generations']!=before:raise RuntimeError('wrong-epoch no-signal probe changed live generation')
 return dict(status='PASS_NATIVE',rejection=rejected,scope='REAL_PID_WRONG_START_TICKS_NOT_ACTUAL_KERNEL_PID_REUSE')


def arm_parent_abort():
 # Parent death requests Python finally cleanup; it never kills the namespace.
 if ctypes.CDLL(None).prctl(1,signal.SIGTERM,0,0,0)!=0:raise RuntimeError('cannot arm parent-death cleanup signal')


def inner(args):
 evidence=Path(args.evidence_root);state=dict(status='IN_PROGRESS',phase='INNER_ADMISSION',m1_complete=False,
  all_supervisor_gates_accepted=False,native_start_attempted=False,
  phases={name:dict(status='NOT_TESTED',reason='not implemented in this reviewed core driver') for name in DEFERRED_PHASES})
 runtime=None;cleaning=[False];context=None;error=None
 def interrupted(*_):
  if not cleaning[0]:raise RuntimeError('owned outer requested qualification abort')
 signal.signal(signal.SIGINT,interrupted);signal.signal(signal.SIGTERM,interrupted)
 try:
  arm_parent_abort();context=admission(args);supervisor,profile_module,_,profile,config,_,_=context
  # The direct parent is the outer namespace owner, not an arbitrary adopter.
  start=read(evidence/'controller-start.json')
  parent=Path('/proc')/str(os.getppid());fields=(parent/'stat').read_text().rsplit(') ',1)[1].split()
  if start['outer_pid']!=os.getppid() or int(fields[19])!=start['outer_start_ticks']:raise ValueError('outer owner epoch mismatch')
  profile.require_namespace()
  if os.readlink('/proc/self/ns/net')==start['outer_namespace']:raise ValueError('fresh network namespace required')
  subprocess.run(['ip','link','set','lo','up'],check=True,capture_output=True)
  state['network_namespace']=os.readlink('/proc/self/ns/net');state['phase']='STARTUP';save_inner(evidence,state)
  runtime=supervisor.Runtime(config)
  state['native_start_attempted']=True;save_inner(evidence,state);runtime.start()
  row=wait_healthy(runtime,evidence,state,600);frozen=row['generations']
  state['phase']='BASELINE';save_inner(evidence,state)
  state['phases']['baseline']=measure_healthy(runtime,evidence,state,BASELINE_SECONDS,frozen)
  archive_manifest=runtime.root/'archives/manifest.json'
  archive_start=len(json.loads(archive_manifest.read_text())) if archive_manifest.exists() else 0
  role=next(r.name for r in profile.roles if r.kind=='bot')
  state['phase']='EPOCH_MISMATCH';save_inner(evidence,state)
  verify_context(context)
  state['phases']['epoch_mismatch_no_signal']=wrong_epoch_probe(runtime,evidence,state,role)
  state['phase']='CLIENT_FAULT_RECOVERY';save_inner(evidence,state);before=generations(runtime)
  verify_context(context);runtime.no_humans();runtime.signal_role(role,signal.SIGTERM)
  row=wait_healthy(runtime,evidence,state,600,lambda r:r['generations'][role]!=before[role])
  if any(row['generations'][k]!=v for k,v in before.items() if k!=role):raise RuntimeError('client recovery changed a protected other role')
  state['phases']['client_fault_rejoin']=dict(status='PASS_NATIVE',before=before[role],after=row['generations'][role],other_generations_preserved=True)
  # Do not inject a server fault during the existing30/60-second cooldown.
  wait_healthy(runtime,evidence,state,120,lambda r:supervisor.retry_allowed(runtime.r))
  state['phase']='SERVER_FAULT_RECOVERY';save_inner(evidence,state);before=generations(runtime)
  verify_context(context);runtime.no_humans();runtime.signal_role('server',signal.SIGTERM)
  row=wait_healthy(runtime,evidence,state,900,lambda r:r['generations']['server']!=before['server'])
  if any(row['generations'][k]==v for k,v in before.items()):raise RuntimeError('server recovery did not create a complete new generation')
  state['phases']['server_fault_recovery']=dict(status='PASS_NATIVE',before=before,after=row['generations'])
  state['phase']='FOLLOWING_GENERATION_HOUR';save_inner(evidence,state)
  state['phases']['following_generation_hour']=measure_healthy(runtime,evidence,state,HOUR_SECONDS,row['generations'])
  state['complete_native_logs']=scan_logs(runtime)
  archive_proof=verify_archives(runtime.root,start_index=archive_start)
  state['phases']['closed_writer_archives']=dict(archive_proof,status='PASS_NATIVE',scope='REAL_OWNED_RECOVERY_ARCHIVES_NOT_LOG_THRESHOLD_PROBE')
  verify_context(context);state['phases']['originals']=dict(status='PASS_NATIVE',retail_binary_pins_match=True)
 except BaseException as exc:
  error=str(exc) or type(exc).__name__;state['error']=error;state['status']='BLOCKED'
 finally:
  cleaning[0]=True;state['phase']='CLEANUP_IN_PROGRESS';save_inner(evidence,state)
  root=runtime.root if runtime else (context[3].root if context else None)
  if runtime:
   try:runtime.stop()
   except BaseException as exc:state['cleanup_error']=str(exc)
   finally:runtime.close()
  if root is not None:
   cg=Path('/sys/fs/cgroup')/('tse-ops-'+hashlib.sha256(str(root).encode()).hexdigest()[:12])
   state['cleanup']=census(root,cg,allow_missing_cgroup=not state['native_start_attempted'])
  else:state['cleanup']=dict(clean=not state['native_start_attempted'],errors=['ADMISSION_NO_RUNTIME_ROOT'] if state['native_start_attempted'] else [])
  state['phases']['cleanup']=dict(status='PASS_NATIVE' if state['cleanup']['clean'] else 'NOT_VERIFIED',census=state['cleanup'])
  if not state['cleanup']['clean']:
   state['status']='CLEANUP_HOLD';state['phase']='CLEANUP_HOLD'
  elif error:state['status']='BLOCKED';state['phase']='FINISHED'
  else:state.update(core_verdict(state['phases']));state['phase']='FINISHED'
  save_inner(evidence,state)
 return 0 if state['status']=='CORE_QUALIFIED_MORE_NATIVE_GATES_REQUIRED' else 1


def evidence_location(value):
 root=Path(value)
 if root.parent!=Path('/root/ssam-ai-backups') or not re.fullmatch(r'm1-supervisor-native-20261027-[A-Za-z0-9_-]+',root.name) or root!=root.resolve():
  raise ValueError('fresh private supervisor evidence root required')
 return root


def hold(evidence,state,reason):
 state['status']='CLEANUP_HOLD';state['hold_reason']=str(reason);state['m1_complete']=False
 atomic(evidence/'HOLD.json',state)
 if not GLOBAL_HOLD.exists():
  with GLOBAL_HOLD.open('x') as stream:json.dump(dict(evidence=str(evidence),reason=str(reason),m1_complete=False),stream,indent=2)
  GLOBAL_HOLD.chmod(0o600)


def execute_outer(args):
 evidence=evidence_location(args.evidence_root);context=admission(args)
 supervisor,profile_module,owned_class,profile,config,_,_=context
 if evidence.exists() or profile.root.exists():raise ValueError('fresh evidence AND runtime root required; no adoption')
 lock=supervisor.acquire_lock('/run/tse-existing-supervisor-qualification.lock')
 try:evidence.mkdir(mode=0o700)
 except BaseException:lock.close();raise
 state=dict(status='PREPARING',m1_complete=False,all_supervisor_gates_accepted=False)
 child=None;owned=None;started=time.monotonic();abort_deadline=None;overload=0;inner_state={};failure=None
 try:
  # Accepted-profile-only preparation writes upper files but starts no process.
  profile_module.prepare(read(config));verify_context(context)
  fields=Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()
  atomic(evidence/'controller-start.json',dict(outer_pid=os.getpid(),outer_start_ticks=int(fields[19]),
      outer_namespace=os.readlink('/proc/self/ns/net'),policy_sha256=args.policy_sha256))
  command=build_inner_command(args.policy,args.policy_sha256,evidence)
  atomic(evidence/'command.json',dict(argv=command,m1_complete=False))
  with (evidence/'inner-controller.log').open('wb') as stream:
   child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT)
  try:owned=owned_class(child)
  except BaseException as exc:
   # Retain an unbound direct child for bounded natural cleanup. Never raw-PID signal.
   failure='direct-child pidfd binding failed: '+str(exc)
   abort_deadline=time.monotonic()+CLEANUP_SECONDS
   child.wait(timeout=CLEANUP_SECONDS)
  previous=cpu()
  while child.poll() is None:
   time.sleep(POLL_SECONDS)
   sample,previous=host_sample(previous);verdict=guard_sample(sample,overload);overload=verdict['overload']
   with (evidence/'host-samples.jsonl').open('a') as stream:stream.write(json.dumps(sample)+'\n')
   try:
    verify_context(context)
    if (evidence/'inner.json').exists():inner_state=read(evidence/'inner.json')
    phase=inner_state.get('phase','INNER_ADMISSION')
    age=time.monotonic()-inner_state.get('heartbeat_mono',started)
    max_age=990 if phase=='CLEANUP_IN_PROGRESS' else 930 if phase=='SERVER_FAULT_RECOVERY' else 600 if phase in ('STARTUP','INNER_ADMISSION') else 180
    if age>max_age:raise RuntimeError('bounded native heartbeat stalled')
    if verdict['abort']:raise RuntimeError('host protection gate: '+','.join(verdict['reasons']))
    if time.monotonic()-started>TOTAL_BUDGET_SECONDS:raise RuntimeError('total native budget exceeded')
   except BaseException as exc:
    failure=failure or str(exc)
    request_abort(owned,state,inner_state)
    abort_deadline=abort_deadline or time.monotonic()+CLEANUP_SECONDS
   if abort_deadline and time.monotonic()>abort_deadline:raise RuntimeError('namespace cleanup deadline exceeded; no parent kill')
  if (evidence/'inner.json').exists():inner_state=read(evidence/'inner.json')
  cg=Path('/sys/fs/cgroup')/('tse-ops-'+hashlib.sha256(str(profile.root).encode()).hexdigest()[:12])
  final=census(profile.root,cg,allow_missing_cgroup=inner_state.get('native_start_attempted') is False)
  state.update(child_exitcode=child.returncode,inner=inner_state,cleanup=final)
  if not final['clean'] or inner_state.get('status')=='CLEANUP_HOLD':hold(evidence,state,'independent final native census incomplete')
  elif failure or child.returncode!=0:state.update(status='BLOCKED',error=failure or inner_state.get('error','inner failed'))
  else:
   verify_context(context);state.update(core_verdict(inner_state.get('phases',{})))
 except BaseException as exc:
  failure=str(exc) or type(exc).__name__;state.update(status='BLOCKED',error=failure)
  if child is not None and child.poll() is None:
   try:
    request_abort(owned,state,inner_state)
    remaining=CLEANUP_SECONDS if abort_deadline is None else max(0,abort_deadline-time.monotonic())
    if remaining<=0:raise RuntimeError('existing namespace cleanup deadline exhausted')
    child.wait(timeout=remaining)
   except BaseException as cleanup_error:hold(evidence,state,'owned namespace parent retained: '+str(cleanup_error))
  if child is not None:
   cg=Path('/sys/fs/cgroup')/('tse-ops-'+hashlib.sha256(str(profile.root).encode()).hexdigest()[:12])
   final=census(profile.root,cg)
   state['cleanup']=final
   if not final['clean']:hold(evidence,state,'exception-path independent native census incomplete')
 finally:
  if owned is not None and child.poll() is not None:owned.close()
  try:atomic(evidence/'result.json',state)
  finally:lock.close()
 print(json.dumps(dict(status=state['status'],m1_complete=False,all_supervisor_gates_accepted=False,evidence=str(evidence))))
 return 0 if state['status']=='CORE_QUALIFIED_MORE_NATIVE_GATES_REQUIRED' else 1


def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--execute',action='store_true');parser.add_argument('--inner',action='store_true',help=argparse.SUPPRESS)
 parser.add_argument('--policy',type=Path);parser.add_argument('--policy-sha256');parser.add_argument('--evidence-root',type=Path)
 args=parser.parse_args(argv)
 if not args.execute:
  print(json.dumps(dict(status='DRY_RUN_NO_NATIVE_ACTIONS',m1_complete=False,all_supervisor_gates_accepted=False)));return 0
 if args.evidence_root is None:raise ValueError('explicit private evidence root required')
 evidence_location(args.evidence_root)
 return inner(args) if args.inner else execute_outer(args)

if __name__=='__main__':raise SystemExit(main())
