"""Bounded own-namespace packet capture addon; importing launches nothing."""
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import struct
import subprocess
import time

RUNTIME_REVIEWED=False
ROLES=('server','botA','botB','vanilla')
ARENA=Path('/srv/tse-arena-isolated-20261111')
MAX_BYTES=64*1024*1024
MAX_PACKETS=250000
MAX_SECONDS=640
MAX_LOG=65536


def need(ok,message):
 if not ok:raise ValueError('Owned sync capture: '+message)


def read_start(pid):
 return int((Path('/proc')/str(pid)/'stat').read_text().rsplit(') ',1)[1].split()[19])


def exclusive_json(path,value):
 path=Path(path);pending=path.with_name(path.name+'.pending')
 fd=os.open(pending,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:
  with os.fdopen(fd,'w')as stream:json.dump(value,stream,indent=2,allow_nan=False)
  os.link(pending,path) # Atomic complete visibility and no overwrite/link follow.
 finally:pending.unlink()


def socket_rows(table,inodes):
 out=[]
 for line in table.splitlines()[1:]:
  fields=line.split();need(len(fields)>=10,'malformed UDP table')
  try:address,port=fields[1].split(':');port=int(port,16);inode=int(fields[9])
  except (ValueError,IndexError)as error:raise ValueError('malformed UDP endpoint')from error
  if inode in inodes:
   need(address in('00000000','0100007F')and 1<=port<=65535,'non-loopback or invalid owned UDP endpoint')
   out.append((port,inode))
 return out


def validate_role_ports(rows):
 need(set(rows)==set(ROLES),'exact four roles')
 need(all(type(r['identity'])is list and len(r['identity'])==2 and all(type(x)is int and x>0 for x in r['identity'])for r in rows.values()),'PID/start bounds')
 need(len({r['identity'][0]for r in rows.values()})==4,'duplicate role PIDs')
 need(len({r['namespace']for r in rows.values()})==1 and all(type(r['namespace'])is int and r['namespace']>0 for r in rows.values()),'role namespace changed')
 need(sorted(p for p,i in rows['server']['ports'])==[27850,27851],'exact owned server game/query ports')
 ports={}
 for role in ROLES[1:]:
  owned=rows[role]['ports'];need(len(owned)==1,'ambiguous/missing own client socket: '+role)
  ports[role]=owned[0][0]
 all_rows=[pair for r in rows.values()for pair in r['ports']]
 need(all(type(p)is int and 1<=p<=65535 and type(i)is int and i>0 for p,i in all_rows),'invalid socket identity')
 need(len({p for p,i in all_rows})==len(all_rows)and len({i for p,i in all_rows})==len(all_rows),'shared role ports/socket inodes')
 return ports


def observe_roles(registry):
 """Actual main-process FD inodes intersect its namespace UDP table, twice bound."""
 need(set(registry)==set(ROLES),'role registry')
 rows={}
 for role in ROLES:
  spec=registry[role];pid,start=spec['identity'];proc=Path('/proc')/str(pid)
  def guard():
   need(read_start(pid)==start,'role PID reused')
   need((proc/'cwd').resolve(strict=True)==ARENA/role,'role CWD changed')
   need((proc/'comm').read_text().strip()==('DedicatedServer'if role=='server'else'SeriousSam.exe'),'wrong native role')
   need(any(x.split(':',2)[-1].rstrip('/').endswith('/'+spec['unit'])for x in(proc/'cgroup').read_text().splitlines()),'role cgroup changed')
   return (proc/'ns/net').stat().st_ino
  namespace=guard();inodes=set()
  for f in(proc/'fd').iterdir():
   target=str(f.readlink());match=re.fullmatch(r'socket:\[(\d+)\]',target)
   if match:inodes.add(int(match[1]))
  table=(proc/'net/udp').read_text();selected=socket_rows(table,inodes)
  # The auditor supports IPv4 only; never hide an owned IPv6 socket.
  ipv6=(proc/'net/udp6').read_text()
  need(not any(len(v:=line.split())>=10 and int(v[9])in inodes for line in ipv6.splitlines()[1:]),'unsupported owned IPv6 socket')
  after_inodes=set()
  for f in(proc/'fd').iterdir():
   match=re.fullmatch(r'socket:\[(\d+)\]',str(f.readlink()))
   if match:after_inodes.add(int(match[1]))
  need(all(inode in after_inodes for port,inode in selected),'owned UDP fd vanished during binding')
  need(guard()==namespace,'role namespace changed during read')
  rows[role]=dict(identity=[pid,start],unit=spec['unit'],namespace=namespace,ports=[list(pair)for pair in selected])
 validate_role_ports(rows)
 need(rows['server']['namespace']!=(Path('/proc/1/ns/net')).stat().st_ino,'host namespace forbidden')
 return rows


def capture_argv(server_pid):
 return ['/usr/bin/nsenter','--target',str(server_pid),'--net','/usr/bin/tcpdump',
         '-n','-U','--time-stamp-precision=micro','-i','lo','-s','262144',
         '-c',str(MAX_PACKETS),'-w','-','udp','and','port','27850']


def check_limits(*,size=0,packets=0,seconds=0):
 need(size<MAX_BYTES and packets<MAX_PACKETS and seconds<MAX_SECONDS,'size/packet/wall cap reached')


def check_running(returncode,current_start,expected_start,current_namespace,expected_namespace):
 need(returncode is None,'capture supervisor exited before normal stop')
 need(current_start==expected_start,'capture PID reused')
 need(current_namespace==expected_namespace,'capture namespace changed')


def exec_ready(actual,argv,helper,namespace,expected_namespace):
 if actual==argv[4:]:
  need(namespace==expected_namespace,'tcpdump in wrong namespace');return True
 need(actual in(helper,argv),'unknown capture exec transition')
 return False


def ready(log,header):
 if 'listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes'not in log or len(header)<24:return False
 magic,major,minor,zone,accuracy,snaplen,link=struct.unpack('<IHHIIII',header[:24])
 need((magic,major,minor,snaplen,link)==(0xa1b2c3d4,2,4,262144,1),'unsupported PCAP header')
 return True


def capture_stats(log):
 out={}
 for name,pattern in [('captured',r'(?m)^(\d+) packets? captured$'),('received',r'(?m)^(\d+) packets? received by filter$'),('dropped',r'(?m)^(\d+) packets? dropped by kernel$')]:
  values=re.findall(pattern,log);need(len(values)==1,'missing/ambiguous capture statistics: '+name);out[name]=int(values[0])
 need(out['dropped']==0,'capture kernel drops')
 check_limits(packets=out['captured']);return out


def stop_owned(process,send):
 """Caller binds signals to its fresh dedicated capture process group."""
 need(process.poll()is None,'premature capture exit')
 send(signal.SIGINT)
 try:
  code=process.wait(timeout=10);need(code==0,'capture exit code '+str(code));return code
 except subprocess.TimeoutExpired:
  send(signal.SIGTERM)
  try:process.wait(timeout=3)
  except subprocess.TimeoutExpired:
   send(signal.SIGKILL);process.wait(timeout=3)
  raise RuntimeError('normal capture stop timeout; own capture group terminated')


def wait_capture_end(identity,timeout):
 pid,start=identity;deadline=time.monotonic()+timeout
 while True:
  try:
   if read_start(pid)!=start:return
  except FileNotFoundError:return
  if time.monotonic()>=deadline:raise TimeoutError('owned capture child remains')
  time.sleep(.05)


def audit_pairs(path,ports,audit):
 out={}
 for name,a,b in [('A_B','botA','botB'),('A_Original','botA','vanilla'),('B_Original','botB','vanilla')]:
  with Path(path).open('rb')as stream:out[name]=audit(stream,[ports[a],ports[b]],destination_port=27850)
 return out


class OwnedSyncCapture:
 def __init__(self,evidence,registry):
  self.evidence=Path(evidence);self.registry=registry;self.process=None;self.supervisor_start=None;self.owner=None;self.before=None;self.ports=None;self.started=None;self.complete=False;self.closed=False;self.errors=[]
  self.receipt=dict(scope='OWN018_YODELLER_SAMPLED_SYNC_PROTOCOL_ONLY',qualified=False,first_simulation_tick_proven=False,initial_handshake_captured=False,limits=dict(seconds=MAX_SECONDS,bytes=MAX_BYTES,packets=MAX_PACKETS),errors=self.errors)
  self.pcap=self.evidence/'owned-sync.pcap';self.log=self.evidence/'owned-sync-tcpdump.log';self.config=self.evidence/'owned-sync-config.json';self.owner_path=self.evidence/'owned-sync-owner.json'
 def save(self):
  (self.evidence/'owned-sync-capture.json').write_text(json.dumps(self.receipt,indent=2,allow_nan=False))
 def text(self):
  need(self.log.stat().st_size<=MAX_LOG,'capture log bound')
  return self.log.read_text(errors='replace')
 def start(self):
  need(RUNTIME_REVIEWED,'disabled capture library')
  need(self.process is None,'capture already started')
  self.before=observe_roles(self.registry);self.ports=validate_role_ports(self.before)
  self.receipt.update(role_binding_before=self.before,role_ports=self.ports);self.save()
  source=Path(__file__).resolve().parent
  config=dict(registry=self.registry,binding=self.before,owner_path=str(self.owner_path),
              source_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(source/'owned_capture_exec.py',source/'owned_sync_capture.py')})
  exclusive_json(self.config,config)
  outfd=os.open(self.pcap,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  try:logfd=os.open(self.log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  except BaseException:os.close(outfd);raise
  try:
   self.started=time.monotonic()
   args=['/usr/bin/timeout','--signal=INT','--kill-after=3',str(MAX_SECONDS),'/usr/bin/python3','-B',str(source/'owned_capture_exec.py'),str(self.config)]
   self.process=subprocess.Popen(args,stdout=outfd,stderr=logfd,start_new_session=True)
   # Retain the actual child handle before any identity read can fail.
   self.receipt['supervisor_pid']=self.process.pid;self.save()
   self.supervisor_start=read_start(self.process.pid)
   self.receipt.update(supervisor_identity=[self.process.pid,self.supervisor_start],supervisor_argv=args,started_monotonic=self.started);self.save()
   deadline=self.started+5
   while True:
    need(self.process.poll()is None,'capture startup exited')
    if self.owner_path.exists():
     self.owner=json.loads(self.owner_path.read_text());need(self.owner['supervisor_identity']==[self.process.pid,self.supervisor_start]and self.owner['pgrp']==self.process.pid,'capture not child of own supervisor')
     pid,start=self.owner['identity'];proc=Path('/proc')/str(pid)
     need(read_start(pid)==start and os.getpgid(pid)==self.process.pid,'setup identity/group changed')
     actual=[x.decode()for x in(proc/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
     helper=['/usr/bin/python3','-B',str(source/'owned_capture_exec.py'),str(self.config)]
     if exec_ready(actual,capture_argv(self.registry['server']['identity'][0]),helper,(proc/'ns/net').stat().st_ino,self.before['server']['namespace']):
      self.guard()
      with self.pcap.open('rb')as stream:header=stream.read(24)
      if ready(self.text(),header):break
    need(time.monotonic()<deadline,'capture readiness timeout')
    time.sleep(.05) # paused startup only; no gameplay sleeps/reads are added
   self.receipt.update(ready=True,ready_monotonic=time.monotonic(),owner=self.owner);self.save()
  finally:os.close(outfd);os.close(logfd)
 def guard(self):
  need(self.process is not None and self.owner is not None,'capture owner not established')
  pid,start=self.owner['identity'];proc=Path('/proc')/str(pid)
  expected_ns=self.before['server']['namespace']
  check_running(self.process.poll(),read_start(pid),start,(proc/'ns/net').stat().st_ino,expected_ns)
  need(read_start(self.process.pid)==self.supervisor_start and os.getpgid(self.process.pid)==self.process.pid,'supervisor identity/group changed')
  need(os.getpgid(pid)==self.process.pid,'capture left own group')
  expected=capture_argv(self.registry['server']['identity'][0])[4:]
  need((proc/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')==[a.encode()for a in expected],'capture command not exact tcpdump')
  need(observe_roles(self.registry)==self.before,'own UDP role binding changed')
  check_limits(size=self.pcap.stat().st_size,seconds=time.monotonic()-self.started)
  self.text()
 def gameplay_complete(self):
  self.guard();self.complete=True;self.receipt['gameplay_completed_monotonic']=time.monotonic();self.save()
 def signal_group(self,sig):
  need(self.process is not None and self.process.poll()is None,'own supervisor absent')
  # A live Popen child cannot be reaped/reused; its fresh session contains only
  # timeout -> setup -> nsenter -> tcpdump, never a game role.
  if self.supervisor_start is not None:need(read_start(self.process.pid)==self.supervisor_start,'supervisor PID reused')
  need(os.getpgid(self.process.pid)==self.process.pid,'own capture group changed')
  os.killpg(self.process.pid,sig)
 def close(self):
  if self.closed:
   if self.errors:raise RuntimeError('; '.join(self.errors))
   return self.receipt
  self.closed=True
  self.receipt['protocol_complete']=False
  def attempt(label,operation):
   try:return operation()
   except BaseException as error:self.errors.append(label+':'+repr(error));return None
  def after_binding():
   rows=observe_roles(self.registry);self.receipt['role_binding_after']=rows
   need(rows==self.before,'own ports changed at capture end')
  def hash_pcap():
   size=self.pcap.stat().st_size
   need(size<=MAX_BYTES,'unexpected PCAP exceeds OS file bound')
   self.receipt['pcap_sha256']=hashlib.sha256(self.pcap.read_bytes()).hexdigest()
   self.receipt['pcap_bytes']=size
   check_limits(size=size,seconds=time.monotonic()-self.started)
  def audits():
   from analyze_retail_sync_pcap import analyze
   self.receipt['pair_audits']=audit_pairs(self.pcap,self.ports,analyze)
   need(all(v.get('paired_checks',0)>0 for v in self.receipt['pair_audits'].values()),'missing required pair observations')
  def child_ended():
   if self.owner is None:return
   pid,start=self.owner['identity']
   try:
    if read_start(pid)!=start:return
   except FileNotFoundError:return
   # Even a premature supervisor exit cannot bypass cleanup of its precisely
   # recorded child. This never signals a game process or a reused PID.
   need(os.getpgid(pid)==self.process.pid,'remaining child left capture group')
   os.kill(pid,signal.SIGINT)
   try:wait_capture_end([pid,start],10)
   except TimeoutError:
    self.errors.append('capture child required forced cleanup')
    for sig in(signal.SIGTERM,signal.SIGKILL):
     need(read_start(pid)==start and os.getpgid(pid)==self.process.pid,'remaining capture identity changed')
     os.kill(pid,sig)
     try:wait_capture_end([pid,start],3);break
     except TimeoutError:
      if sig==signal.SIGKILL:raise
  try:
   if self.process is not None:
    if self.owner is None and self.owner_path.exists():
     def retain_owner():
      owner=json.loads(self.owner_path.read_text())
      need(owner['supervisor_identity'][0]==self.process.pid and owner['pgrp']==self.process.pid,'partial capture owner not in own child group')
      if self.supervisor_start is not None:need(owner['supervisor_identity'][1]==self.supervisor_start,'partial supervisor start differs')
      self.owner=owner;self.receipt['owner']=owner
     attempt('retain partial owner',retain_owner)
    # Signal the owned capture child normally; timeout waits and reports its
    # actual exit0. Force fallback uses the dedicated fresh capture group only.
    def send(sig):
     if sig==signal.SIGINT and self.owner is not None:
      pid,start=self.owner['identity'];need(read_start(pid)==start and os.getpgid(pid)==self.process.pid,'capture identity changed before signal');os.kill(pid,sig)
     else:self.signal_group(sig)
    if self.process.poll()is None:
     self.receipt['exit_code']=attempt('capture stop',lambda:stop_owned(self.process,send))
    else:
     self.errors.append('capture exited before requested stop')
     self.receipt['exit_code']=attempt('supervisor reap',lambda:self.process.wait(timeout=0))
    attempt('capture child end',child_ended)
    # Failure of a role check, statistics or parsing must not skip independent
    # retention of the already owned raw PCAP and its actual comparisons.
    attempt('role binding after',after_binding)
    stats=attempt('capture statistics',lambda:capture_stats(self.text()))
    if stats is not None:self.receipt['stats']=stats
    attempt('capture hash',hash_pcap)
    if self.ports is not None:attempt('pair comparisons',audits)
    self.receipt['normal_capture_closed']=self.receipt.get('exit_code')==0 and not self.errors
    self.receipt['protocol_complete']=self.complete and not self.errors and all(v['status']=='MATCHING_SAMPLED_SYNCCHECKS_ONLY'for v in self.receipt.get('pair_audits',{}).values())
  finally:
   self.receipt.update(full_gameplay_requested_window=self.complete,finished_monotonic=time.monotonic());self.save()
  if self.errors:raise RuntimeError('; '.join(self.errors))
  return self.receipt
