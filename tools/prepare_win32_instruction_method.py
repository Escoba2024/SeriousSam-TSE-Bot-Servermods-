"""Offline own-source/PE preparation. Never runs Wine, Frida or a compiler."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys

from win32_instruction_probe_controller import pe32_base

BUILD=Path('/srv/tse-win32-instruction-method-build-stdin-fixed-20261114')
EXE_SHA='4305c136f460f6fec4ff8b6ccb9419394514e2cee808b5ab5865b12b59f5acf4'
FRIDA=Path('/srv/tse-frida-probe-20261111/lib/python3.12/site-packages')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def own_sites(data):
    pe32_base(data);pe=struct.unpack_from('<I',data,0x3c)[0];opt=pe+24
    count=struct.unpack_from('<H',data,pe+6)[0];optional=struct.unpack_from('<H',data,pe+20)[0]
    assert 1<=count<=32
    sections=[struct.unpack_from('<IIII',data,opt+optional+i*40+8)for i in range(count)]
    def read(rva,size):
        ranges=[raw+rva-start for _,start,rawsize,raw in sections if start<=rva and rva+size<=start+rawsize]
        assert len(ranges)==1,'own PE range';offset=ranges[0]
        assert 0<=offset and offset+size<=len(data)
        return data[offset:offset+size]
    directory,_=struct.unpack_from('<II',data,opt+96)
    num,functions,names,ordinals=struct.unpack('<4I',read(directory+24,16));assert num==2
    exports={}
    for i in range(num):
        name_rva=struct.unpack('<I',read(names+i*4,4))[0];name=bytearray()
        for n in range(128):
            byte=read(name_rva+n,1)
            if byte==b'\0':break
            name.extend(byte)
        else:raise ValueError('own export name bound')
        ordinal=struct.unpack('<H',read(ordinals+i*2,2))[0]
        exports[name.decode('ascii')]=struct.unpack('<I',read(functions+ordinal*4,4))[0]
    assert exports=={'ProbeSavedMidpoint':0x1000,'ProbeArgumentMidpoint':0x1070}
    return [dict(name='saved',rva=0x1000,hex=read(0x1000,17).hex()),
            dict(name='arguments',rva=0x1070,hex=read(0x1070,14).hex())]


def prepare(destination):
    root=Path(destination).resolve();tools=Path(__file__).resolve().parent
    if root.exists():raise ValueError('fresh disabled destination required; no prefix copying')
    build=json.loads((BUILD/'manifest.json').read_text())
    assert build['build_ok']is True and build['runtime_performed']is False
    assert sha(BUILD/'win32_instruction_probe.exe')==EXE_SHA==build['exe_sha256']
    for n in('win32_instruction_probe.cpp','win32_instruction_probe.def'):
        assert sha(tools/n)==build['source_sha256'][n]
    sites=own_sites((BUILD/'win32_instruction_probe.exe').read_bytes())
    assert all(s['hex'].startswith('90'*8)for s in sites)
    root.mkdir(mode=0o700)
    names=('win32_instruction_probe.cpp','win32_instruction_probe.def','win32_instruction_probe.js',
           'win32_instruction_probe_controller.py','win32_instruction_probe_policy.py',
           'original_damage_worker.py','test_win32_instruction_probe_policy.py',
           'test_win32_instruction_probe_controller.py','test_win32_instruction_probe.js',
           'prepare_win32_instruction_method.py','test_prepare_win32_instruction_method.py',
           'test_win32_command_reader.py')
    for name in names:shutil.copy2(tools/name,root/name)
    shutil.copy2(BUILD/'win32_instruction_probe.exe',root/'win32_instruction_probe.exe')
    deps={str(root/name):sha(root/name)for name in names+('win32_instruction_probe.exe',)}
    for name in('frida/__init__.py','frida/_frida.abi3.so','frida/aio.py','frida-17.26.2.dist-info/METADATA'):
        path=FRIDA/name;deps[str(path)]=sha(path)
    assert '\nVersion: 17.26.2\n'in(FRIDA/'frida-17.26.2.dist-info/METADATA').read_text()
    wine=Path('/usr/bin/wine').resolve(strict=True)
    for path in(wine,Path(sys.executable).resolve(),BUILD/'manifest.json'):
        deps[str(path)]=sha(path)
    m=dict(scope='OWN_WIN32_IA32_INSTRUCTION_METHOD',runtime_reviewed=False,
           runtime_performed=False,retail_qualified=False,method_qualified=False,
           wine=str(wine),runtime_dependencies=deps,sites=sites,
           build=dict(source_sha256=sha(root/'win32_instruction_probe.cpp'),exe_sha256=EXE_SHA,
                      original_manifest=str(BUILD/'manifest.json'),original_manifest_sha256=sha(BUILD/'manifest.json')),
           modes=['baseline','historical-object','function-probe'],automatic_series=False,
           automatic_retry=False,frida_version='17.26.2',prefix='wineprefix',winearch='win64',
           limits=dict(arm_seconds=3,drain_seconds=.1,close_seconds=2,
                       ready_seconds=10,result_seconds=3,native_exit_seconds=17,
                       worker_reap_seconds=2,callback_records=2,callback_ttl_seconds=10,
                       native_command_wait_seconds=15,minimum_disk_bytes=8*2**30),
           review='PENDING independent source, PE, freeze and own Win32 methods')
    (root/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    (root/'HANDOFF-disabled.json').write_text(json.dumps(dict(runtime_allowed=False,
        manifest_sha256=sha(root/'source-manifest.json'),prefix_copied=False,
        next=['independent source review','Root own namespace freeze/pin retarget',
              'Root preinitialized win64 prefix quiescence and >=8GiB disk',
              'Root selects one mode per invocation; no automatic retry',
              'retain exact three mode receipts; destroy reproducible own prefix only after closed/quiescent'],
        invocation_after_root_freeze='python3 win32_instruction_probe_controller.py --mode MODE',
        retail_qualified=False),indent=2)+'\n')
    return dict(package=str(root),manifest_sha256=sha(root/'source-manifest.json'),runtime_pins=len(deps),runtime_reviewed=False,native_started=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
    print(json.dumps(prepare(p.parse_args().destination),indent=2))
