"""Exact own filter-Dedicated module contract; one bounded first-read sidecar."""
import json
import math
import os

MAX_FIRST_SAMPLE_BYTES=65536
ENGINE_SHA='b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
ENTITIES_SHA='7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'
SERVER_SHA='fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0'


def identity(value):
 if not isinstance(value,(list,tuple))or len(value)!=2 or any(type(v)is not int or v<=0 for v in value):
  raise ValueError('powerup inventory: exact server PID/start required')
 return list(value)


def check_sample_hashes(sample,role,server_identity):
 if role!='server':raise ValueError('powerup inventory: server role only')
 expected=identity(server_identity)
 if identity(sample.get('process_identity'))!=expected:raise ValueError('powerup inventory: sample server identity differs')
 if sample.get('hashes')!={'Engine.dll':ENGINE_SHA,'EntitiesMP.dll':ENTITIES_SHA,'GameMP.dll':SERVER_SHA}:
  raise ValueError('powerup inventory: exact server module hashes required')


def archive_first_sample(path,sample,*,read_serial,group,phase,server_identity,started,ended):
 """First paused success only. Preserve before bind; no validation of sample hash."""
 if type(read_serial)is not int or read_serial!=1 or group!='botA_actual'or phase!='paused_smoke':
  raise ValueError('powerup inventory: only first paused successful read archival')
 expected=identity(server_identity)
 if any(type(t)not in(int,float)or not math.isfinite(t)or t<0 for t in(started,ended))or ended<started:
  raise ValueError('powerup inventory: existing read interval invalid')
 row=dict(schema='powerup-server-first-unbound-read-v1',role='server',read_serial=read_serial,
          group=group,phase=phase,server_identity=expected,read_interval=[started,ended],sample=sample)
 # Preserve the original Python JSON value convention, including a malformed
 # nonfinite value if present. Existing downstream finite-clock guards still fail.
 raw=(json.dumps(row,separators=(',',':'))+'\n').encode('utf-8')
 if len(raw)>MAX_FIRST_SAMPLE_BYTES:raise ValueError('powerup inventory: first raw record exceeds64KiB')
 flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_APPEND|os.O_CLOEXEC
 with os.fdopen(os.open(path,flags,0o600),'wb')as output:output.write(raw)
