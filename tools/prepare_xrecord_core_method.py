"""Build a fresh DISABLED own Core-XRecord review package, never execute it."""
import hashlib
import json
import os
from pathlib import Path

SOURCE=Path(__file__).resolve().parent
WIP_INITIAL={
 'xrecord_core_method.py':'ca4de66b67603924d00fb0acb4cf381f46877a76fc4e798784309649c52b27cf',
 'test_xrecord_core_method.py':'fba18e1de8fe47767d8066c6f87ee250e028f1d6d0475cd23c64fbac1d5caffe',
 'test_xrecord_core_controller.py':'73957ef1618fecad5a2a03b872595308be42431b5a9cfa64ddffa930eaa9989c'}
FILES=['xrecord_core_method.py','xrecord_core_process.py','xrecord_core_controller.py','xrecord_core_native.py','xrecord_core_worker.py','prepare_xrecord_core_method.py','test_xrecord_core_method.py','test_xrecord_core_process.py','test_xrecord_core_controller.py','test_xrecord_core_native.py','test_xrecord_core_worker.py','test_xrecord_core_binding.py','test_xrecord_core_orchestration.py','test_prepare_xrecord_core_method.py']
PRIMARY_SOURCES={
 'libXtst-1.2.3.tar.bz2':'4655498a1b8e844e3d6f21f3b2c4e2b571effb5fd83199d428a6ba7ea4bf5204',
 'xorgproto-2024.1.tar.xz':'372225fd40815b8423547f5d890c5debc72e88b91088fbfb13158c20495ccb59',
 'libX11-1.8.7.tar.xz':'05f267468e3c851ae2b5c830bcf74251a90f63f04dd7c709ca94dc155b7e99ee',
 'Xlib.h':'748265b305975ae8396cdb310bcafa47d338211c977bfda9bf88d187a3a37c03',
 'xorg-server-21.1.12.tar.xz':'1e016e2be1b5ccdd65eac3ea08e54bd13ce8f4f6c3fb32ad6fdac4e71729a90f',
 'record-server.c':'c0b7908a5b6ed6c852ca76571043aaaf32d2800cda9185d8af98badb340e8a80',
 'recordlib.html':'aea9fa484ff73de0ddcaf3160048d73da5f203171e2a7495c1b0adb9555388bd',
 'record.h':'744232d2fa7c64d158ef3bd535fe723c0f55d9cb1bebf65408d385002efc391c',
 'XRecord.c':'e502689fb91a37d7778eca8ef606c1ff7f84ef0acd0aad9f66067fe9722534c4',
 'x11_endpoint.py':'652147c86c52ce3a49afa7ef39c499df7c7a16a357259b4e09b66b2b8d40cb2b'}


def prepare(destination):
 for name,sha in WIP_INITIAL.items():
  if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()!=sha:raise ValueError('initial WIP copy changed:'+name)
 for name in('xrecord_core_controller.py','xrecord_core_native.py','xrecord_core_worker.py'):
  if (SOURCE/name).read_text().count('RUNTIME_REVIEWED=False')!=1:raise ValueError('author source gate must be false')
 destination=Path(destination);destination.mkdir(mode=0o700,exist_ok=False)
 pins={}
 for name in FILES:
  data=(SOURCE/name).read_bytes()
  with os.fdopen(os.open(destination/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(data)
  pins[name]=hashlib.sha256(data).hexdigest()
 manifest=dict(schema='OWN_CORE_XRECORD_METHOD_V1',runtime_enabled=False,base_commit='0ab3774',files=pins,wip_initial_sha256=WIP_INITIAL,primary_source_sha256=PRIMARY_SOURCES,limits=dict(display=':167',recorder_seconds=15,records=1024,total_bytes=2097152,record_bytes=16384,arm_seconds=3,stop_seconds=3,driver_seconds=2,controller_seconds=30,cleanup_seconds=5),claims=dict(retail_qualified=False,xi2_complete=False,a1_pass=False,method_native_executed=False))
 data=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
 with os.fdopen(os.open(destination/'source-manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(data)
 return manifest

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path);a=p.parse_args();prepare(a.destination)
 print(hashlib.sha256((a.destination/'source-manifest.json').read_bytes()).hexdigest())
