"""Offline-only disabled own XRes method packaging; never opens a display."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
from xres_pid_method import LIMITS,require
from xres_pid_worker import abi_layout

PARENT=Path('/srv/tse-own-xrecord-cold-warm-root-frozen-20261114')
PARENT_SHA='5749113983ea2462e60d84630d5823ff04f6f8b1b7147c3effc600f6124d928c'
EV=Path('/srv/tse-cecil-rollout-evidence-20261114')
METHOD=EV/'own-xrecord-cold-warm-root-20261114/method-result.json'
METHOD_SHA='45adbbad603ab49fde34e3b20f51c8b38ba62a0cb403937a27d15458ccd7a7d2'
LIBRARIES={'/lib/x86_64-linux-gnu/libXRes.so.1':'c2aefa4bf373492430f48aec108c5ead95e1dc757d52968775e905e23a2ad56c','/lib/x86_64-linux-gnu/libX11.so.6':'edd2ddf6e00a81c40b8645f7dbb6d6603c6a0a78d583bdbe7491d8a84de6e3b6','/lib/x86_64-linux-gnu/libXext.so.6':'2907e6a996465de5b32a0dd10534d4416b87f1dee5670aaa7b19301a1fc93f44','/usr/bin/Xvfb':'6b27845931670c8c9b3ce7423696a452ce3cab1c7f316ce5f7ea7f1297fa2f84'}
SOURCES=('xres_pid_method.py','xres_pid_worker.py','xres_pid_controller.py','prepare_xres_pid_method.py','test_xres_pid_method.py','test_xres_pid_lifecycle.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(target):
 target=Path(target).resolve()
 if target.exists():raise FileExistsError(target)
 require(sha(PARENT/'source-manifest.json')==PARENT_SHA,'immutable parent manifest changed')
 parent=json.loads((PARENT/'source-manifest.json').read_bytes())
 evidence={str(PARENT/'source-manifest.json'):PARENT_SHA,str(METHOD):METHOD_SHA}
 for name,h in parent['files'].items():require(sha(PARENT/name)==h,'parent source pin:'+name);evidence[str(PARENT/name)]=h
 require(sha(METHOD)==METHOD_SHA,'qualified parent method result changed')
 provision=EV/'xres-dev-provision-after.json';layout=EV/'xres-abi-layout.json';csource=EV/'xres-abi-layout.c'
 supplied=json.loads(provision.read_bytes());require(supplied.get('existing_libraries_unchanged')is True,'regular provision changed pinned libraries')
 headers=supplied['headers'];require(len(headers)==4 and '/usr/include/X11/extensions/XRes.h'in headers,'public header pins missing')
 for name,h in dict(LIBRARIES,**headers).items():require(sha(name)==h,'installed pin:'+name)
 require(abi_layout()==json.loads(layout.read_bytes()),'Root public header ABI differs from ctypes')
 for path in(provision,layout,csource):evidence[str(path)]=sha(path)
 root=Path(__file__).resolve().parent
 for name in('xres_pid_controller.py','xres_pid_worker.py'):
  tree=ast.parse((root/name).read_text());gate=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='RUNTIME_REVIEWED'for v in n.targets));require(isinstance(gate.value,ast.Constant)and gate.value.value is False,'authored runtime gate must be false')
 target.mkdir(mode=0o700)
 files={}
 for name in SOURCES:
  data=(root/name).read_bytes()
  with os.fdopen(os.open(target/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as out:out.write(data)
  files[name]=sha(target/name)
 name='xrecord_core_process.py';shutil.copyfile(PARENT/name,target/name);os.chmod(target/name,0o600);files[name]=sha(target/name)
 manifest=dict(schema='OWN_XRES_PID_METHOD_V1',runtime_enabled=False,limits=LIMITS,files=files,library_sha256=LIBRARIES,header_sha256=headers,evidence_sha256=evidence,abi_layout=abi_layout(),evidence_prefix='own-xres-pid-method',parent_manifest_sha256=PARENT_SHA,qualified=False,historical_u_attributed=False,continuous_client_lifetime_proven=False,a1_pass=False,retail_qualified=False,root_prerequisites=['independent source/pin/no-input review','all four project locks plus own167 method lock','fresh display/socket/PID/namespace/disk preflight','backup and exclusive bounded native window','exactly one Root method execution; no automatic retry'])
 with os.fdopen(os.open(target/'source-manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as out:json.dump(manifest,out,allow_nan=False,indent=2)
 return manifest


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();prepare(a.output);print(json.dumps(dict(output=str(a.output),manifest_sha256=sha(a.output/'source-manifest.json'))))
