#!/usr/bin/env python3
"""Bounded normal input to our live original opponent in an owned M2 test only."""
import argparse
import ctypes
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import time

ORIGINAL_GAMEMP='1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
KEYS={'w':ord('w'),'a':ord('a'),'s':ord('s'),'d':ord('d'),
      'Left':0xff51,'Up':0xff52,'Right':0xff53,'Down':0xff54,'Home':0xff50,
      'space':0x20,'1':ord('1'),'2':ord('2'),'3':ord('3'),'4':ord('4'),
      '5':ord('5'),'6':ord('6'),'7':ord('7')}

def finite(value):return type(value) in (int,float) and math.isfinite(value)

def validate_evidence(*,runtime,result,guard,sample,now,result_mtime,guard_mtime,sample_mtime,expected_dll):
    runtime=Path(runtime)
    if runtime.parent!=Path('/srv') or not runtime.name.startswith('tse-session-qualification-m2-'):
        raise ValueError('private M2 runtime required')
    for mtime,maximum in [(result_mtime,20),(guard_mtime,8),(sample_mtime,3)]:
        if not finite(mtime) or not -1<=now-mtime<=maximum:raise ValueError('stale/future runtime evidence')
    if (result.get('status')!='MEASURING' or result.get('scope')!='ISOLATED_NETNS_RETAIL_WINE' or
        result.get('m2_combat') is not True or result.get('cecil_p1') is not True or
        result.get('dll_sha256')!=expected_dll):raise ValueError('inactive/wrong M2 campaign')
    if guard.get('status')!='MONITORING' or guard.get('error'):raise ValueError('native guard is not active')
    samples=guard.get('samples',[])
    if not samples:raise ValueError('missing native resource sample')
    last=samples[-1]
    if not all(finite(last.get(k)) for k in ('at','available_mib','disk_free_gib','host_busy_percent')):
        raise ValueError('invalid native resource sample')
    if not -1<=now-last['at']<=8 or last['available_mib']<768 or last['disk_free_gib']<8 or last['host_busy_percent']>=85:
        raise ValueError('native resource evidence does not permit input')
    ns=result.get('network_namespace','');cg=result.get('cgroup','')
    if not re.fullmatch(r'net:\[\d+\]',ns) or not re.fullmatch(r'/sys/fs/cgroup/tse-sessions-\d+',cg):
        raise ValueError('missing private namespace/cgroup binding')
    start=sample.get('processes',{}).get('vanilla',{}).get('start_ticks')
    if type(start) is not int or start<=0:raise ValueError('missing original actor sample')
    return {'start_ticks':start,'network_namespace':ns,'cgroup':cg.removeprefix('/sys/fs/cgroup')}

def validate_process(record,expected,runtime):
    if (record.get('start_ticks')!=expected['start_ticks'] or record.get('uid')!=65534 or
        record.get('cwd')!=str(Path(runtime)/'vanilla') or record.get('cgroup')!=expected['cgroup'] or
        record.get('network_namespace')!=expected['network_namespace'] or
        not re.search(r'(?i)(?:^|[ /\\])SeriousSam\.exe(?:\s|$)',record.get('command',''))):
        raise ValueError('original actor identity/ownership changed')

def process_record(pid):
    proc=Path('/proc')/str(pid)
    if (proc/'comm').read_text().strip().lower()!='serioussam.exe':raise ValueError('not the game executable')
    stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
    uid=int(re.search(r'(?m)^Uid:\s*(\d+)',(proc/'status').read_text())[1])
    cgroups=(proc/'cgroup').read_text().splitlines()
    if len(cgroups)!=1 or not cgroups[0].startswith('0::'):raise ValueError('unexpected cgroup topology')
    return dict(pid=pid,start_ticks=int(stat[19]),uid=uid,cwd=str((proc/'cwd').resolve()),
                cgroup=cgroups[0][3:],network_namespace=str((proc/'ns/net').readlink()),
                command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace').strip())

def latest_sample(path):
    with path.open('rb') as stream:
        stream.seek(max(0,path.stat().st_size-65536));data=stream.read()
    if not data.endswith(b'\n'):raise ValueError('incomplete newest process sample')
    try:return json.loads(data.splitlines()[-1])
    except (ValueError,UnicodeError,IndexError) as error:raise ValueError('invalid newest process sample') from error

def current_context(runtime,manifest):
    runtime=Path(runtime).resolve();build=json.loads(Path(manifest).read_text())
    if build.get('build_ok') is not True or build.get('qualified') is not False:
        raise ValueError('explicit unqualified successful build manifest required')
    if hashlib.sha256(Path(build['candidate']).read_bytes()).hexdigest()!=build.get('dll_sha256'):
        raise ValueError('candidate DLL drift')
    paths=[runtime/n for n in ('result.json','host-guard.json','samples.jsonl')]
    result=json.loads(paths[0].read_text());guard=json.loads(paths[1].read_text());sample=latest_sample(paths[2])
    expected=validate_evidence(runtime=runtime,result=result,guard=guard,sample=sample,now=time.time(),
        result_mtime=paths[0].stat().st_mtime,guard_mtime=paths[1].stat().st_mtime,
        sample_mtime=paths[2].stat().st_mtime,expected_dll=build['dll_sha256'])
    if not (runtime/'vanilla').is_mount():raise ValueError('original actor overlay is not mounted')
    if hashlib.sha256((runtime/'vanilla/Bin/GameMP.dll').read_bytes()).hexdigest()!=ORIGINAL_GAMEMP:
        raise ValueError('target is not the original Retail actor')
    return expected

def discover(runtime,expected):
    found=[]
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            if (entry/'cwd').resolve()!=Path(runtime)/'vanilla':continue
            record=process_record(int(entry.name));validate_process(record,expected,runtime);found.append(record)
        except (OSError,ValueError,TypeError,IndexError):continue
    if len(found)!=1:raise ValueError('one current owned original actor required')
    return found[0]

def send_input(x,d,window,width,height,event,code,seconds,revalidate):
    """Final routing check and press are atomic with respect to other X clients."""
    revalidate()
    U=ctypes.c_ulong;I=ctypes.c_int;C=ctypes.c_uint
    pressed=False
    try:
        x.XGrabServer(d)
        try:
            focus=U();revert=I();x.XGetInputFocus(d,ctypes.byref(focus),ctypes.byref(revert))
            root=U();child=U();rx=I();ry=I();px=I();py=I();mask=C()
            inside=x.XQueryPointer(d,window,ctypes.byref(root),ctypes.byref(child),ctypes.byref(rx),ctypes.byref(ry),ctypes.byref(px),ctypes.byref(py),ctypes.byref(mask))
            if focus.value!=window or not inside or not (0<=px.value<width and 0<=py.value<height):
                raise ValueError('original actor lost focus/pointer before press')
            # A signal may arrive immediately after ctypes accepted the event.
            # Release even an interrupted/rejected attempt; never lose a keyup.
            pressed=True
            if not event(d,code,True,0):raise ValueError('input dispatch rejected')
            x.XSync(d,False)
        finally:x.XUngrabServer(d);x.XFlush(d)
        time.sleep(seconds)
    finally:
        if pressed:
            released=False
            for _ in range(3):
                if event(d,code,False,0):released=True;break
            x.XSync(d,False)
            if not released:raise ValueError('input release rejected; acceptance denied')

def dispatch(runtime,manifest,display,key,button,seconds):
    runtime=Path(runtime).resolve()
    if runtime.parent!=Path('/srv') or not runtime.name.startswith('tse-session-qualification-m2-'):
        raise ValueError('private M2 runtime required before locking')
    current_context(runtime,manifest)
    # A separate cooperating helper must never overlap a held input.
    fd=os.open(runtime/'opponent-input.lock',os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'a') as lock:
        if not stat.S_ISREG(os.fstat(lock.fileno()).st_mode):raise ValueError('regular owned input lock required')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return _dispatch(runtime,manifest,display,key,button,seconds)

def _dispatch(runtime,manifest,display,key,button,seconds):
    if not re.fullmatch(r':1[3-9]\d',display) or not 0.05<=seconds<=2 or (key is None)==(button is None):
        raise ValueError('bounded private-display key or button input required')
    if key is not None and key not in KEYS or button is not None and button!=1:raise ValueError('unsupported input')
    expected=current_context(runtime,manifest);record=discover(runtime,expected)
    # Read only DISPLAY from the actor environment; never log its other contents.
    actor_display=next((v[8:].decode() for v in (Path('/proc')/str(record['pid'])/'environ').read_bytes().split(b'\0') if v.startswith(b'DISPLAY=')),None)
    if actor_display!=display:raise ValueError('display is not bound to the original actor')
    listing=subprocess.check_output(['xwininfo','-display',display,'-root','-tree'],text=True,timeout=3)
    windows=[]
    for wid in re.findall(r'(0x[0-9a-fA-F]+) "Serious Sam \(',listing):
        prop=subprocess.check_output(['xprop','-display',display,'-id',wid,'_NET_WM_PID'],text=True,timeout=3)
        if re.search(r'=\s*'+str(record['pid'])+r'\s*$',prop):windows.append(int(wid,16))
    if len(windows)!=1:raise ValueError('one PID-bound original game window required')
    window=windows[0];x=ctypes.CDLL('libX11.so.6');xt=ctypes.CDLL('libXtst.so.6')
    D=ctypes.c_void_p;U=ctypes.c_ulong;I=ctypes.c_int;C=ctypes.c_uint
    signatures={'XOpenDisplay':([ctypes.c_char_p],D),'XCloseDisplay':([D],I),
      'XRaiseWindow':([D,U],I),'XSetInputFocus':([D,U,I,U],I),
      'XGetInputFocus':([D,ctypes.POINTER(U),ctypes.POINTER(I)],I),'XSync':([D,I],I),
      'XFlush':([D],I),'XKeysymToKeycode':([D,U],ctypes.c_ubyte),
      'XGrabServer':([D],I),'XUngrabServer':([D],I),
      'XQueryPointer':([D,U,ctypes.POINTER(U),ctypes.POINTER(U),ctypes.POINTER(I),ctypes.POINTER(I),ctypes.POINTER(I),ctypes.POINTER(I),ctypes.POINTER(C)],I),
      'XGetGeometry':([D,U,ctypes.POINTER(U),ctypes.POINTER(I),ctypes.POINTER(I),ctypes.POINTER(C),ctypes.POINTER(C),ctypes.POINTER(C),ctypes.POINTER(C)],I),
      'XWarpPointer':([D,U,U,I,I,C,C,I,I],I)}
    for name,(args,result) in signatures.items():getattr(x,name).argtypes=args;getattr(x,name).restype=result
    for name in ('XTestFakeKeyEvent','XTestFakeButtonEvent'):
        getattr(xt,name).argtypes=[D,C,I,U];getattr(xt,name).restype=I
    d=x.XOpenDisplay(display.encode())
    if not d:raise ValueError('private display unavailable')
    old_handler=signal.getsignal(signal.SIGTERM);started=time.time()
    try:
        x.XRaiseWindow(d,window);x.XSetInputFocus(d,window,2,0);x.XSync(d,False)
        focus=U();revert=I();x.XGetInputFocus(d,ctypes.byref(focus),ctypes.byref(revert))
        if focus.value!=window:raise ValueError('original actor did not receive focus')
        root=U();px=I();py=I();w=C();h=C();border=C();depth=C()
        if not x.XGetGeometry(d,window,ctypes.byref(root),ctypes.byref(px),ctypes.byref(py),ctypes.byref(w),ctypes.byref(h),ctypes.byref(border),ctypes.byref(depth)):
            raise ValueError('original window geometry unavailable')
        x.XWarpPointer(d,0,window,0,0,0,0,w.value//2,h.value//2);x.XSync(d,False)
        event=xt.XTestFakeKeyEvent if key else xt.XTestFakeButtonEvent
        code=x.XKeysymToKeycode(d,KEYS[key]) if key else button
        if not code:raise ValueError('input key unavailable')
        def interrupted(*_):raise InterruptedError('test input interrupted')
        signal.signal(signal.SIGTERM,interrupted)
        send_input(x,d,window,w.value,h.value,event,code,seconds,
                   lambda:validate_process(process_record(record['pid']),current_context(runtime,manifest),runtime))
    finally:
        try:signal.signal(signal.SIGTERM,old_handler)
        finally:x.XCloseDisplay(d)
    receipt=dict(status='INPUT_DISPATCHED_ENGINE_EFFECT_UNVERIFIED',at=started,seconds=seconds,
                 pid=record['pid'],start_ticks=record['start_ticks'],window=hex(window),key=key,button=button,
                 focus_verified=True,release_sent=True)
    with (Path(runtime)/'opponent-input.jsonl').open('a') as stream:stream.write(json.dumps(receipt)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--build-manifest',type=Path,required=True);p.add_argument('--display',required=True)
    choice=p.add_mutually_exclusive_group(required=True);choice.add_argument('--key',choices=KEYS);choice.add_argument('--button',type=int,choices=[1])
    p.add_argument('--seconds',type=float,default=.2);a=p.parse_args()
    print(dispatch(a.runtime,a.build_manifest,a.display,a.key,a.button,a.seconds)['status'])
