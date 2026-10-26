#!/usr/bin/env python3
"""Private bounded Retail 1.07 exported-function sync snapshots.

Instrumented diagnostic observations only. No interior instructions, state
writes, injected actions, altered kick settings, production or release claims.
All raw snapshots and process records must remain outside Git.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import time
import native_sync_handler_probe as h

ENGINE_SHA256 = h.ENGINE_SHA256
# Exact original PE exports, confirmed with objdump against ENGINE_SHA256.
ENTRIES = {
    'session': (0xe5b10, '558bec6aff'),
    'entity': (0x101c90, '558bec8b450c'),
    'rational': (0x102a00, '558bec538b5d0c'),
    'movable': (0x1575d0, '558bec538b5d0c'),
    'movable_model': (0x1634f0, '558bec538b5d0c'),
    'player': (0x1664f0, '558bec8b450c'),
}


def approved_entry(rva, prologue):
    expected = next((bytes.fromhex(raw) for addr, raw in ENTRIES.values() if addr == rva), None)
    if expected is None or not prologue.startswith(expected):
        raise ValueError('UNAPPROVED_OR_MODIFIED_EXPORT_ENTRY')
    return True


def validate_capture_binding(runtime, report, proc, host_netns, engine_sha):
    root = Path(runtime)
    if (root.parent != Path('/srv') or not re.fullmatch(r'tse-session-qualification-master-[A-Za-z0-9_-]+', root.name)):
        raise ValueError('PRIVATE_ROOT')
    if (report.get('status') != 'MEASURING' or report.get('scope') != h.EXPECTED_SCOPE or
            not h.EXPECTED_CGROUP.fullmatch(str(report.get('cgroup', '')))):
        raise ValueError('ACTIVE_PRIVATE_RUNTIME_REQUIRED')
    ns = report.get('network_namespace')
    if (not h.EXPECTED_NETNS.fullmatch(str(ns)) or ns == host_netns or proc.get('netns') != ns or
            proc.get('cgroup') != '0::' + report['cgroup'].removeprefix('/sys/fs/cgroup')):
        raise ValueError('PRIVATE_NAMESPACE_AND_CGROUP_REQUIRED')
    cwd = Path(proc.get('cwd', '/'))
    role = cwd.name
    if cwd.parent != root or not re.fullmatch(r'server|vanilla|gamer-[0-9]{3}', role):
        raise ValueError('OWNED_RUNTIME_ROLE_REQUIRED')
    if (proc.get('comm') != ('DedicatedServer' if role == 'server' else 'SeriousSam.exe') or
            proc.get('uid') != 65534 or type(proc.get('pid')) is not int or proc['pid'] < 2 or
            type(proc.get('start_ticks')) is not int or proc['start_ticks'] <= 0):
        raise ValueError('PROCESS_IDENTITY_REQUIRED')
    if engine_sha != ENGINE_SHA256:
        raise ValueError('ENGINE_HASH')
    return role


def _index(rows):
    result = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('event') != 'snapshot':
            raise ValueError('INVALID_SNAPSHOT_EVENT')
        for field in ('tick_bits', 'sequence', 'level', 'pause', 'extensive', 'crc'):
            value = row.get(field)
            if type(value) is not int or not 0 <= value <= 0xffffffff:
                raise ValueError('INVALID_SNAPSHOT_FIELD:' + field)
        tick = struct.unpack('<f', struct.pack('<I', row['tick_bits']))[0]
        if not math.isfinite(tick) or tick < 0:
            raise ValueError('INVALID_TICK')
        actions = row.get('actions')
        if not isinstance(actions, list) or len(actions) > 128:
            raise ValueError('INVALID_ACTIONS')
        seen = set()
        for action in actions:
            if (not isinstance(action, dict) or type(action.get('slot')) is not int or
                    not 0 <= action['slot'] < 64 or action.get('kind') not in ('last', 'previous') or
                    not re.fullmatch(r'[0-9a-f]{80}', str(action.get('bytes', '')))):
                raise ValueError('INVALID_ACTION_BYTES')
            key = (action['slot'], action['kind'])
            if key in seen:
                raise ValueError('DUPLICATE_ACTION_SLOT')
            seen.add(key)
        if not isinstance(row.get('components'), list):
            raise ValueError('INVALID_COMPONENTS')
        key = (row['tick_bits'], row['sequence'])
        if key in result and result[key] != row:
            raise ValueError('CONFLICTING_DUPLICATE_SNAPSHOT')
        result[key] = row
    return result


def compare_snapshots(server, client):
    a, b = _index(server), _index(client)
    keys = sorted(a.keys() & b.keys())
    result = dict(status='BOUNDED_SNAPSHOT_MATCH' if keys else 'INCOMPLETE',
                  paired=len(keys), first_difference=None, release_qualified=False,
                  scope='BOUNDED_INPUT_COMPARISON_NOT_NATIVE_AUTHENTICATION_OR_RELEASE')
    for key in keys:
        for field in ('level', 'pause', 'extensive', 'actions', 'components', 'crc'):
            if a[key][field] != b[key][field]:
                result.update(status='DIVERGENT', first_difference=field,
                              tick_bits=key[0], sequence=key[1])
                return result
    return result


FRIDA_JS = r"""
if(Process.arch!=='ia32'||Process.pointerSize!==4)throw Error('RETAIL_IA32_REQUIRED');
const addresses=ADDRESS_JSON;
const active={}; const hooks=[]; let snapshots=0;
const hex=p=>Array.from(new Uint8Array(p.readByteArray(40))).map(v=>v.toString(16).padStart(2,'0')).join('');
function fail(e){send({event:'capture_error',message:String(e)});}
hooks.push(Interceptor.attach(ptr(addresses.session),{
 onEnter(){
  this.used=false;
  try{
   if(snapshots>=256)return;
   const s=this.context.ecx; const stack=this.context.esp;
   const n=s.readS32();if(n<0||n>64)throw Error('PLAYER_ARRAY_BOUND');
   const base=s.add(4).readPointer();const ref=stack.add(4).readPointer();
   const row={event:'snapshot',tick_bits:s.add(0x4c).readU32(),sequence:s.add(0x20).readU32(),
    level:s.add(0x1c).readU32(),pause:s.add(0xa8).readU32(),
    extensive:stack.add(8).readU32(),actions:[],components:[]};
   const slots={};
   for(let i=0;i<n;i++){
    const target=base.add(i*0x88);if(target.readU32()===0)continue;
    slots[target.add(4).readPointer().toString()]=i;
    row.actions.push({slot:i,kind:'last',bytes:hex(target.add(0x10))});
    row.actions.push({slot:i,kind:'previous',bytes:hex(target.add(0x40))});
   }
   active[this.threadId]={row,ref,slots}; this.used=true;
  }catch(e){fail(e);}
 },
 onLeave(){if(!this.used)return;try{const a=active[this.threadId];a.row.crc=a.ref.readU32();
  send(a.row);snapshots++;delete active[this.threadId];}catch(e){fail(e);}}
}));
for(const kind of ['entity','rational','movable','movable_model','player']){
 hooks.push(Interceptor.attach(ptr(addresses[kind]),{
  onEnter(){this.used=false;try{const a=active[this.threadId];if(!a)return;
   const slot=a.slots[this.context.ecx.toString()];if(slot===undefined)return;
   this.ref=this.context.esp.add(4).readPointer();this.before=this.ref.readU32();
   this.slot=slot;this.used=true;
  }catch(e){fail(e);}},
  onLeave(){if(!this.used)return;try{const a=active[this.threadId];
   if(a)a.row.components.push({slot:this.slot,kind,before:this.before,after:this.ref.readU32()});
  }catch(e){fail(e);}}
 }));
}
send({event:'ready',exports:Object.keys(addresses)});
"""


def capture(runtime, pid, duration):
    root = Path(runtime).resolve()
    if not 5 <= duration <= 180 or root.is_symlink():
        raise ValueError('BOUNDED_PRIVATE_CAPTURE_REQUIRED')
    report = json.loads((root / 'result.json').read_text())
    proc = h.read_process_record(pid)
    engine = Path(proc['cwd']) / 'Bin/Engine.dll'
    digest = hashlib.sha256(engine.read_bytes()).hexdigest()
    role = validate_capture_binding(root, report, proc, os.readlink('/proc/1/ns/net'), digest)
    game_sha = hashlib.sha256((engine.parent / 'GameMP.dll').read_bytes()).hexdigest()
    expected = '1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208' if role in ('server', 'vanilla') else report.get('dll_sha256')
    if game_sha != expected:
        raise ValueError('GAMEMP_HASH')
    maps = (Path('/proc') / str(pid) / 'maps').read_text()
    base = h.find_pinned_engine_entry(maps, str(engine)) - h.HANDLER_RVA
    addresses = {}
    with (Path('/proc') / str(pid) / 'mem').open('rb', buffering=0) as memory:
        for kind, (rva, _) in ENTRIES.items():
            address = base + rva
            if not any(len(f := line.split(maxsplit=5)) == 6 and f[5] == str(engine) and 'x' in f[1] and
                       int(f[0].split('-')[0], 16) <= address < int(f[0].split('-')[1], 16) for line in maps.splitlines()):
                raise ValueError('EXPORT_NOT_IN_EXECUTABLE_ENGINE_MAPPING')
            memory.seek(address); approved_entry(rva, memory.read(16))
            addresses[kind] = hex(address)
    path = root / ('private-sync-snapshot-' + role + '.jsonl')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    import frida
    session = script = None
    errors = []; counts = {'ready': 0, 'snapshot': 0}; start = time.monotonic()
    with os.fdopen(fd, 'w') as out:
        out.write(json.dumps(dict(event='native_binding', producer='retail107-export-snapshot/1',
                   engine_sha256=digest, gamemp_sha256=game_sha, process=proc,
                   runtime=str(root), namespace=report['network_namespace'],
                   source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())) + '\n'); out.flush()
        def message(msg, data):
            if msg.get('type') != 'send':
                errors.append(msg); return
            row = msg.get('payload', {})
            if row.get('event') == 'capture_error': errors.append(row)
            if row.get('event') in counts: counts[row['event']] += 1
            out.write(json.dumps(row) + '\n'); out.flush()
        try:
            if h.read_process_record(pid) != proc: raise ValueError('PROCESS_EPOCH_CHANGED')
            session = frida.attach(pid)
            script = session.create_script(FRIDA_JS.replace('ADDRESS_JSON', json.dumps(addresses)))
            script.on('message', message); script.load()
            while time.monotonic() - start < duration:
                time.sleep(0.5)
                if h.read_process_record(pid) != proc or errors: raise ValueError('CAPTURE_STATE_INVALID')
        except BaseException as exc:
            errors.append(dict(event='host_error',error=type(exc).__name__,message=str(exc)))
        finally:
            if script:
                try: script.unload()
                except Exception as exc: errors.append(dict(error='UNLOAD_FAILED',message=str(exc)))
            if session:
                try: session.detach()
                except Exception as exc: errors.append(dict(error='DETACH_FAILED',message=str(exc)))
            summary = dict(event='capture_finished',status='BOUNDED_NATIVE_CAPTURE' if counts['ready']==1 and counts['snapshot']>0 and not errors else 'CAPTURE_FAILED',
                           counts=counts,errors=errors,elapsed_s=time.monotonic()-start,release_qualified=False)
            out.write(json.dumps(summary)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',type=Path,required=True);p.add_argument('--pid',type=int,required=True)
    p.add_argument('--duration',type=int,default=30)
    args=p.parse_args(); result=capture(args.runtime,args.pid,args.duration)
    print(json.dumps(result));return 0 if result['status']=='BOUNDED_NATIVE_CAPTURE' else 3

if __name__=='__main__': raise SystemExit(main())
