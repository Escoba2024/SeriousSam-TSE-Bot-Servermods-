#!/usr/bin/env python3
"""Bounded passive Frida probe of an OWN isolated AI2 Retail server only.

Requires a separately qualified local Frida Python environment. Never hooks a
public server, changes arguments/returns/state, or claims hits from fire input.
The SDK layout must be measured by the x86 helper and cross-checked with actual
BotSnapshot IDs/health. Logs and pointers are PRIVATE, not publication artifacts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from bot_session_executor import process_record, probe_process
from qualify_integrated_wine import PINS
from qualify_integrated_wine import cpu

DAMAGE='?ReceiveDamage@CPlayer@@UAEXPAVCEntity@@W4DamageType@@MABV?$Vector@M$02@@2@Z'
BULLET='?LaunchBullet@CBullet@@QAEXHHH@Z'


def export_rvas(text, names):
    addresses={int(i):int(rva,16) for i,rva in re.findall(
        r'^\s*\[\s*(\d+)\]\s+\+base\[\s*\d+\]\s+([0-9a-fA-F]+) Export RVA',text,re.M)}
    ordinals={name:int(i) for i,name in re.findall(r'^\s*\[\s*(\d+)\]\s+(\?\S+)\s*$',text,re.M)}
    if any(name not in ordinals or ordinals[name] not in addresses for name in names):
        raise ValueError('missing/ambiguous required Retail export')
    return {name:addresses[ordinals[name]] for name in names}


def validate_runtime(root, report):
    if (root.parent!=Path('/srv') or not root.name.startswith('tse-session-qualification-ai2-') or
        report.get('status')!='MEASURING' or report.get('scope')!='ISOLATED_NETNS_RETAIL_WINE' or
        not re.fullmatch(r'/sys/fs/cgroup/tse-sessions-\d+',str(report.get('cgroup'))) or
        not re.fullmatch(r'net:\[\d+\]',str(report.get('network_namespace')))):
        raise ValueError('only an active isolated owned AI2 test may be instrumented')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--layout',type=Path,required=True)
    p.add_argument('--duration',type=int,default=90)
    args=p.parse_args()
    if not 5<=args.duration<=120:raise ValueError('probe duration must be 5..120 s')
    root=args.runtime.resolve();report=json.loads((root/'result.json').read_text())
    validate_runtime(root,report)
    game=root/'server'
    candidates=[]
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit():continue
        try:
            if os.path.realpath(directory/'cwd')!=str(game):continue
            if (directory/'comm').read_text().strip()!='DedicatedServer':continue
            candidates.append(process_record(int(directory.name)))
        except (OSError,ValueError):continue
    if len(candidates)!=1:raise RuntimeError('exactly one owned private Dedicated required')
    record=candidates[0];pid=record['pid']
    if (record['uid']!=65534 or record['cgroup'].strip()!='0::'+report['cgroup'].removeprefix('/sys/fs/cgroup') or
        os.readlink(f'/proc/{pid}/ns/net')!=report['network_namespace'] or
        report['network_namespace']==os.readlink('/proc/1/ns/net')):
        raise RuntimeError('private ownership/namespace binding failed')
    hashes={}
    for name in ('Engine.dll','EntitiesMP.dll','GameMP.dll','DedicatedServer.exe'):
        hashes[name]=hashlib.sha256((game/'Bin'/name).read_bytes()).hexdigest()
        if hashes[name]!=PINS[name]:raise RuntimeError('original server binary pin drift')
    maps=Path(f'/proc/{pid}/maps').read_text().splitlines()
    mapped=[int(line.split('-')[0],16) for line in maps if line.endswith(str(game/'Bin/EntitiesMP.dll'))]
    if not mapped:raise RuntimeError('cannot identify original private PE mapping')
    base=min(mapped)
    exports=export_rvas(subprocess.check_output(['objdump','-p',str(game/'Bin/EntitiesMP.dll')],text=True),[DAMAGE,BULLET])
    layout=json.loads(args.layout.read_text())
    if (set(layout)!={'entity_id','health','armor','bullet_owner','projectile_owner','player_name'} or
        any(type(v) is not int or not 0<v<16384 for v in layout.values())):
        raise ValueError('complete measured x86 layout required')
    script_source='const layout='+json.dumps(layout)+';\n'+r'''
if(Process.arch!=='ia32'||Process.pointerSize!==4)throw Error('Retail probe requires IA32 target');
const threadShots={};let sequence=0;
function id(p){return p.isNull()?null:p.add(layout.entity_id).readU32();}
function name(p){const b=new Uint8Array(p.add(layout.player_name).readPointer().readByteArray(33));
 const end=b.indexOf(0);if(end<0)throw Error('unbounded player name');return String.fromCharCode(...b.subarray(0,end));}
function farg(p){const b=new ArrayBuffer(4),v=new DataView(b);v.setUint32(0,p.toUInt32(),true);return v.getFloat32(0,true);}
Interceptor.attach(ptr(DAMAGE_ADDRESS),{
 onEnter(args){
  this.p=this.context.ecx;this.tid=Process.getCurrentThreadId();
  this.data={event:'damage',target:id(this.p),name:name(this.p),inflictor:id(args[0]),type:args[1].toInt32(),
   requested:farg(args[2]),health_before:this.p.add(layout.health).readFloat(),
   armor_before:this.p.add(layout.armor).readFloat(),shot:threadShots[this.tid]||null};
 },
 onLeave(){
  this.data.health_after=this.p.add(layout.health).readFloat();
  this.data.armor_after=this.p.add(layout.armor).readFloat();
  send(this.data);
 }
});
Interceptor.attach(ptr(BULLET_ADDRESS),{
 onEnter(args){this.tid=Process.getCurrentThreadId();this.previous=threadShots[this.tid];
  this.shot=++sequence;threadShots[this.tid]=this.shot;
  send({event:'hitscan_trace',shot:this.shot,owner:id(this.context.ecx.add(layout.bullet_owner).readPointer())});},
 onLeave(){threadShots[this.tid]=this.previous;}
});
send({event:'hook_ready',arch:Process.arch});
'''
    script_source=script_source.replace('DAMAGE_ADDRESS',json.dumps(hex(base+exports[DAMAGE]))).replace('BULLET_ADDRESS',json.dumps(hex(base+exports[BULLET])))
    if probe_process(record)!='LIVE':raise RuntimeError('private process changed before attach')
    import frida
    session=None;script=None;started=time.monotonic();errors=[];cpu_start=cpu(pid)
    with (root/'frida-combat.jsonl').open('x') as out:
        def emit(data):out.write(json.dumps(dict(at=time.time(),**data))+'\n');out.flush()
        def message(data,_blob):
            if data.get('type')=='error':errors.append(data)
            emit(dict(message=data))
        emit(dict(event='attach_preflight',record=record,hashes=hashes,base=hex(base),exports=exports,
                  layout=layout,frida_version=frida.__version__))
        try:
            session=frida.attach(pid);script=session.create_script(script_source)
            script.on('message',message);script.load()
            while time.monotonic()-started<args.duration:
                if probe_process(record)!='LIVE':raise RuntimeError('private target exited/changed')
                if errors:raise RuntimeError('native hook error; see private evidence')
                time.sleep(.2)
        finally:
            emit(dict(event='unloading'))
            if script:script.unload()
            emit(dict(event='unloaded'))
            if session:session.detach()
            elapsed=time.monotonic()-started
            emit(dict(event='detached',elapsed_s=elapsed,errors=errors,
                      server_cpu_core_percent=100*(cpu(pid)-cpu_start)/elapsed))


if __name__=='__main__':main()
