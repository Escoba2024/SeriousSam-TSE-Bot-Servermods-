from pathlib import Path
import subprocess,time,json,hashlib,resource
root=Path(__file__).resolve().parent
rows=[]
for instrumented in (False,True):
 start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
 target=subprocess.Popen([str(root/'probe')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 row={'instrumented':instrumented,'pid':target.pid}
 try:
  if instrumented:
   worker=subprocess.run(['/usr/bin/python3',str(root/'worker.py'),str(target.pid)],capture_output=True,text=True,timeout=8)
   assert worker.returncode==0,(worker.returncode,worker.stderr)
   row['frida']=json.loads(worker.stdout)
  stdout,stderr=target.communicate(timeout=6)
  assert target.returncode==0 and stdout=='45150\n' and stderr==''
  row.update(returncode=target.returncode,result=int(stdout),wall_seconds=time.monotonic()-start)
 finally:
  if target.poll() is None:
   target.terminate()
   target.wait(timeout=2)
 after=resource.getrusage(resource.RUSAGE_CHILDREN)
 row['children_user_cpu_s']=after.ru_utime-before.ru_utime
 row['children_system_cpu_s']=after.ru_stime-before.ru_stime
 rows.append(row)
receipt={'scope':'OWN_LINUX_ELF64_METHOD_SMOKE_ONLY_NOT_RETAIL107_ABI_OR_INPUT_QUALIFICATION','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'probe.c',root/'probe',root/'worker.py',root/'run.py')},'runs':rows,'limitations':['Different process and ABI from Wine/Retail107','CPU includes short-lived worker in instrumented row; not isolated callback overhead','No TSE process accessed or modified']}
(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
