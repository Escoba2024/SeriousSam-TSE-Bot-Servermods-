"""DISABLED NoFire adapter: current RECORD/XRes metadata, never a gain fix."""
import ast
import hashlib
import json
from pathlib import Path
import sys

CORE=Path(__file__).resolve().parent/'passive-core'
if CORE.is_dir():sys.path.insert(0,str(CORE))
from xrecord_core_process import OwnChild
import a1_passive_xrecord as legacy
from a1_xres_attribution_evidence import attribute
from xres_pid_method import require

RUNTIME_REVIEWED=False
instrument_transport=legacy.instrument_transport


def fingerprints(source=None,core=None):
 source=Path(__file__).resolve().parent if source is None else Path(source);core=(source/'passive-core'if(source/'passive-core').is_dir()else source)if core is None else Path(core)
 names={'PublicPID','LifecycleRecorder','lifecycle_ranges','read_processes','require_scope','run_worker'};tree=ast.parse((source/'a1_xres_attribution_worker.py').read_bytes())
 result={node.name:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()for node in tree.body if isinstance(node,(ast.ClassDef,ast.FunctionDef))and node.name in names}
 require(set(result)==names,'all actual lifecycle method bodies required')
 for name in('xrecord_core_process.py','xrecord_core_native.py','xrecord_core_worker.py','xrecord_core_method.py'):result['immutable_core:'+name]=hashlib.sha256((core/name).read_bytes()).hexdigest()
 result['qualified_pid_adapter']=hashlib.sha256((source/'xres_pid_worker.py').read_bytes()).hexdigest()
 return result


def require_method_qualification(scope):
 legacy.require_method_qualification(scope)
 q=scope.get('xres_lifecycle_qualification')
 require(isinstance(q,dict)and q.get('status')=='PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY','actual own lifecycle qualification required')
 require(all(q.get(k)is True for k in('no_inputs','normal_closes','lifecycle_started','lifecycle_died','exactly_two_snapshots','driver_requests_bound')),'actual lifecycle/cleanup/request proof absent')
 require(q.get('fingerprints')==fingerprints(),'actual lifecycle method fingerprints changed')
 return q


def audit_attribution(directory,native):
 directory=Path(directory);pin=native.get('xres_evidence');require(isinstance(pin,dict)and pin.get('path')=='xres-attribution.json','native metadata sidecar binding absent')
 path=directory/'xres-attribution.json';require(not path.is_symlink()and path.stat().st_size<=262144,'bounded own metadata file')
 raw=path.read_bytes();require(type(pin.get('bytes'))is int and pin['bytes']==len(raw)and hashlib.sha256(raw).hexdigest()==pin.get('sha256'),'metadata sidecar hash/length differs')
 evidence=json.loads(raw);require(evidence.get('errors')==[],'metadata attempt failure')
 trace=directory/'record-raw.jsonl';require(not trace.is_symlink()and trace.stat().st_size<=2097152,'bounded actual RECORD file')
 wire=trace.read_bytes();require(wire.endswith(b'\n')and len(wire.splitlines())<=1024,'actual RECORD row boundaries')
 rows=[json.loads(line)for line in wire.splitlines()]
 return attribute(rows,evidence['snapshots'],evidence['expected'],native)


class PassiveRecorder(legacy.PassiveRecorder):
 @classmethod
 def start(cls,evidence,manifest,old_config,transport):
  if not RUNTIME_REVIEWED:raise RuntimeError('disabled A1 XRes lifecycle adapter')
  scope=manifest['passive_xrecord'];require_method_qualification(scope)
  require(transport.pin.role=='vanilla'and transport.pin.display==':154','exact own Original transport')
  directory=Path(evidence)/'passive-xrecord';directory.mkdir(mode=0o700,exist_ok=False)
  cfg={k:old_config[k]for k in('controller_root','arena','parent','roles')}
  cfg['passive']=dict(mode='a1',display=':154',display_owner=scope['current_display_owner'],original_window=transport.pin.window,controller_gc=legacy.controller_gc(transport),evidence=str(directory))
  path=directory/'config.json';legacy.private_json(path,cfg);root=Path(__file__).resolve().parent
  kid=OwnChild(['/usr/bin/python3','-E','-s','-B',str(root/'a1_xres_attribution_worker.py'),'--config',str(path),'--display',':154'],directory,':154',ttl=15,role='recorder')
  return cls(kid,directory,transport)
 def close(self,phases):
  if self.closed:return self.final
  result=super().close(phases)
  try:result['xres_attribution']=audit_attribution(self.directory,result['native'])
  except BaseException as error:result['errors'].append('xres attribution:'+repr(error));result['status']='FAIL_PASSIVE_XRECORD_DIAGNOSTIC'
  self.final=result;return result
