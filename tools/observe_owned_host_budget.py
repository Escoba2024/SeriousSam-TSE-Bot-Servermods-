"""Outer read-only host observation while one own pinned Python child runs.

Reuses the earlier private observe-mapreset-resources.py Popen/wait pattern.
No signals, shell, threads, retries, gameplay control or qualification claim.
The child must retain its own bounded lifecycle, cleanup and runtime locks.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from host_budget import HostBudget


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_host():
 when=time.monotonic()
 cpu=Path('/proc/stat').read_text().splitlines()[0]
 mem=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()
              if x.startswith('MemAvailable:')))*1024
 return when,cpu,mem,shutil.disk_usage('/srv').free


def private_open(path):
 return os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')


def observe(source:Path,expected_sha:str,directory:Path)->dict:
 source=Path(source).absolute();directory=Path(directory).absolute()
 if (source!=source.resolve(strict=True)or source.suffix!='.py'
     or type(expected_sha)is not str or len(expected_sha)!=64
     or digest(source)!=expected_sha):raise ValueError('exact own Python source pin required')
 directory.mkdir(mode=0o700)
 budget=HostBudget();errors=[];error_count=0;child=None;pending=None
 report={'scope':'OWN_CHILD_LIFETIME_BRACKETED_HOST_INTERVAL_OBSERVATION_ONLY',
         'source':str(source),'expected_source_sha256':expected_sha,
         'observer_sha256':digest(__file__),'host_budget_source_sha256':digest(Path(__file__).with_name('host_budget.py')),
         'child_identity':None,'child_exit_code':None,'child_reaped':False,
         'spawn_before_monotonic':None,'spawn_after_monotonic':None,
         'exit_observed_monotonic':None,'qualified':False,'budget_pass_claim':False,
         'signals_sent':0,'automatic_retries':0}
 def error(message):
  nonlocal error_count
  error_count+=1
  if len(errors)<1024:errors.append(str(message)[:1024])
 try:
  with private_open(directory/'host-samples.jsonl')as journal,private_open(directory/'child.log')as child_log:
   def sample(phase):
    old=len(budget.samples);ok=True
    try:budget.add(*read_host())
    except Exception as exc:
     error('host sample: '+repr(exc));ok=False
    if len(budget.samples)>old:
     row=budget.samples[-1];row['phase']=phase
     try:journal.write(json.dumps(row,allow_nan=False)+'\n');journal.flush()
     except Exception as exc:error('host journal:'+repr(exc));ok=False
    return ok
   try:
    if sample('before-spawn-baseline'):
     if digest(source)!=expected_sha:raise ValueError('own source changed before spawn')
     report['spawn_before_monotonic']=time.monotonic()
     child=subprocess.Popen([sys.executable,'-B',str(source)],cwd=source.parent,
                            stdout=child_log,stderr=subprocess.STDOUT)
     report['spawn_after_monotonic']=time.monotonic()
     fields=(Path('/proc')/str(child.pid)/'stat').read_text().rsplit(') ',1)[1].split()
     report['child_identity']=[child.pid,int(fields[19])]
     if digest(source)!=expected_sha:error('own source changed after spawn')
     while True:
      try:child.wait(timeout=HostBudget.LIMITS['target_sample_interval_seconds'])
      except subprocess.TimeoutExpired:sample('own-child-running');continue
      report['exit_observed_monotonic']=time.monotonic();sample('after-observed-exit');break
   except BaseException as exc:
    pending=exc;error('own observer: '+repr(exc))
   finally:
    # This wrapper never abandons or signals the controller. That controller
    # remains responsible for its own bounded normal runtime cleanup.
    if child is not None:
     report['child_exit_code']=child.wait();report['child_reaped']=True
     if report['exit_observed_monotonic']is None:
      report['exit_observed_monotonic']=time.monotonic();sample('after-error-and-observed-exit')
     if child.returncode!=0:error('own child exit '+str(child.returncode))
    try:
     report['source_post_sha256']=digest(source)
     if report['source_post_sha256']!=expected_sha:error('own source pin differs after exit')
    except Exception as exc:error('own source post-check: '+repr(exc))
 except BaseException as exc:
  pending=exc;error('own output stream:'+repr(exc))
 report.update(status='FAIL_HOST_OBSERVATION'if error_count or not report['child_reaped']else'PASS_HOST_OBSERVATION_ONLY',
               errors=errors,error_count=error_count,samples=budget.samples,summary=budget.summary())
 with private_open(directory/'receipt.json')as output:json.dump(report,output,indent=2,allow_nan=False);output.write('\n')
 if pending is not None and not isinstance(pending,Exception):raise pending
 return report
