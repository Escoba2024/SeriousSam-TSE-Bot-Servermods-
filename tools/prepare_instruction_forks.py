"""Offline five-midpoint-only forks. No game, Wine, Frida or compiler calls."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENTS={
 'a1':(Path('/srv/tse-a1-guard-cleanup-root-frozen-20261114'),'27972cdd295fc7a81f3177e4745bffc4c91bea32b4c71f918ce716c59b0db80b'),
 'a3':(Path('/srv/tse-a3-direct020-hard-worker-final-20261114'),'3e9a93ac6f06503f84f8f914b5a6b45aec03a35dfce7ed6552b9905676c39a5e')}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
textsha=lambda s:hashlib.sha256(s.encode()).hexdigest()


def once(source,old,new):
 if source.count(old)!=1:raise ValueError('nonunique reviewed source anchor')
 return source.replace(old,new,1)


def patch_a1(source):
 if textsha(source)!='9659853a687739ec48a6c31b1f90894b0868867bb1165f474a7c9800a0070afa':raise ValueError('exact last full A1 JS required')
 fixed=Path(__file__).with_name('a1_original_input_readonly.js')
 if sha(fixed)!='11c264e1e879bc8c186f9af1817a469d7c2eac22245fe03def54502480104a9c':raise ValueError('exact reviewed four-midpoint source required')
 return fixed.read_text()


def patch_a3(source):
 if textsha(source)!='4312c2e4c41c4c1207dcc54d5ae3c2e6239502fdb812ba4bec4e0a689706fc5d':raise ValueError('exact last full A3 lifecycle JS required')
 source=once(source,'engine.add(G.engine.current_tick.rva+15),{onEnter:tracked(function(){','engine.add(G.engine.current_tick.rva+15),tracked(function(){')
 return once(source,'}catch(e){fault(e);}},true)});','}catch(e){fault(e);}},true));')


def write_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def prepare(kind,destination):
 parent,parent_sha=PARENTS[kind];dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh destination required; old packages stay immutable')
 if sha(parent/'source-manifest.json')!=parent_sha:raise ValueError('parent manifest changed')
 m=json.loads((parent/'source-manifest.json').read_text())
 for p,h in m['runtime_dependencies'].items():
  if sha(p)!=h:raise ValueError('parent runtime pin changed: '+p)
 sourcekey='diagnostic_source_sha256'if kind=='a1'else'sources'
 for p,h in m[sourcekey].items():
  if sha(parent/p)!=h:raise ValueError('parent source pin changed: '+p)
 if kind=='a1':
  cm=json.loads((parent/'collector/source-manifest.json').read_text())
  for p,h in cm['source_pins'].items():
   if sha(p)!=h:raise ValueError('parent collector pin changed: '+p)
 def mapped(p):
  q=Path(p);return dest/q.relative_to(parent)if q.is_relative_to(parent)else q
 def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
 shutil.copytree(parent,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 hook='collector/a1_original_input_readonly.js'if kind=='a1'else'frozen-v2/damage_readonly.js'
 old=(parent/hook).read_text();new=(patch_a1 if kind=='a1'else patch_a3)(old)
 (dest/hook).write_text(new)
 changes={hook}
 if kind=='a1':
  for n in('run_dual.py','a1_input_worker.py','collector/a1_original_input_collector.py'):
   s=(dest/n).read_text();s=once(s,'RUNTIME_REVIEWED = True','RUNTIME_REVIEWED = False')if n.startswith('collector/')else once(s,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
   if n=='run_dual.py':
    s=once(s,"PREFIX='ssam-a1-guard-cleanup-root-20261114'","PREFIX='ssam-a1-instruction-probe-disabled-20261114'")
    s=once(s,"E=BASE/('a1-input-trace-'","E=BASE/('a1-instruction-probe-'")
   if n.startswith('collector/'):s=once(s,str(parent/'collector'),str(dest/'collector'))
   (dest/n).write_text(s);changes.add(n)
  cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins'])
  cm['instruction_probe_derivation']=dict(parent_manifest_sha256=sha(parent/'collector/source-manifest.json'),old_native_result_unchanged=True,retail_qualified=False)
  write_json(dest/'collector/source-manifest.json',cm);changes.add('collector/source-manifest.json')
  m['collector_source']=str(dest/'collector/a1_original_input_collector.py')
  m['schema']='disabled-a1-five-midpoint-method-fork-v1';m['gate']='DISABLED_ROOT_REVIEW_FREEZE_AND_NEW_NATIVE_REQUIRED'
 else:
  n='run-a3-direct020.py';s=(dest/n).read_text()
  s=once(s,"PREFIX=f'ssam-direct020-hard-worker-pair","PREFIX=f'ssam-direct020-hard-probe-pair")
  s=once(s,"E=BASE/f'direct020-hard-worker-pair","E=BASE/f'direct020-hard-probe-pair")
  s=once(s,"'damage_readonly.js': '"+textsha(old)+"'","'damage_readonly.js': '"+textsha(new)+"'")
  (dest/n).write_text(s);changes.add(n)
  m['scope']='DISABLED_DIRECT_BUILD020_HARD_INSTRUCTION_PROBE_DAMAGE_WORKER'
  m['worker_derivation']['new_hook_sha256']=sha(dest/hook)
 m['runtime_reviewed']=False;m['runtime_performed']=False
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 m[sourcekey]={p:sha(dest/p)for p in m[sourcekey]}
 if kind=='a3':m['sources'][hook]=sha(dest/hook)
 m['instruction_probe_derivation']=dict(parent=str(parent),parent_manifest_sha256=parent_sha,
  source_commit='1bbd3a658cd2b00cedb9edbfb97b94a9573eed78',native_qualified=False,
  changed_files=sorted(changes),new_inputs=0,new_sites=0,bounds_changed=False,
  own_baseline_result_sha256='c76101bc3ec95fa3bf7eea7483d51783181652cfadec3551d75ffb101f384b4e',
  own_function_result_sha256='42b2f249ac55b968bf7ae36c87c3723454d1755ab7600d4ee869fb6f40d299b0',
  historical_object_status='FAIL_METHOD_EVIDENCE; native corruption observed, cleanup RPC timeout; no combined PASS',
  root_freeze_required=True,automatic_retry=False)
 write_json(dest/'source-manifest.json',m)
 (dest/'instruction-probe.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='pinned-parent/'+hook,tofile='disabled-fork/'+hook,n=0)))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),runtime_reviewed=False,native_started=False)
 write_json(dest/'INSTRUCTION-PROBE-HANDOFF.json',dict(**receipt,next='Root independent review/freeze/preflight; separate prospective Retail diagnostic only',retail_qualified=False))
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=tuple(PARENTS),required=True);p.add_argument('--destination',required=True,type=Path)
 a=p.parse_args();print(json.dumps(prepare(a.kind,a.destination),indent=2))
