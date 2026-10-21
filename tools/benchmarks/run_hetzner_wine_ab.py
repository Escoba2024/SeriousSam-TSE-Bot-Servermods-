#!/usr/bin/env python3
"""Isolated Hetzner Wine A/B. Run as root via unshare --net; use a disposable runtime copy."""
import os, subprocess, time, json, pathlib, signal, shutil, traceback, re, argparse, fcntl, sys, math
from wine_cpu_gate import write_runtime_config, action_evidence, check_throttling
from statistics import median
args_parser=argparse.ArgumentParser(description=__doc__)
args_parser.add_argument('--runtime',required=True,type=pathlib.Path)
args_parser.add_argument('--cgroup',required=True,type=pathlib.Path)
args_parser.add_argument('--warmup',type=int,default=180)
args_parser.add_argument('--measure',type=int,default=600)
args_parser.add_argument('--repeats',type=int,default=3)
args=args_parser.parse_args()
assert args.warmup>=180 and args.measure>=600 and args.repeats>=3, 'qualification minimums'
assert os.geteuid()==0, 'root needed only for namespace, cgroup and runtime uid setup'
assert os.readlink('/proc/self/ns/net')!=os.readlink('/proc/1/ns/net'), 'run via unshare --net'
D=args.runtime.resolve()
lock=open(D/'.qualification.lock','w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
E=D/('qualification-'+time.strftime('%Y%m%d-%H%M%S',time.gmtime()))
E.mkdir()

CG=args.cgroup.resolve()
assert CG.parent==pathlib.Path("/sys/fs/cgroup") and CG.name.startswith("tse-"), "private cgroup required"
CG.mkdir(exist_ok=True)
assert not (CG/"cgroup.procs").read_text().strip(), "cgroup in use"
(CG/"cpu.max").write_text("max 100000")
ROOT=D.parent.parent/"tse-wine-runtime-20261020"
# HOME used solely for Wine cache; caller runtime files remain isolated.
ROOT=pathlib.Path(os.environ.get("TSE_WINE_HOME",str(D)))
OUT=E/"result.json"
assert D.exists() and (D/"botA/Bin/GameMP.dll").exists()
os.system("ip link set lo up; ip addr add 127.0.0.2/8 dev lo")
env_base=dict(os.environ, HOME=str(ROOT),USER="nobody",LOGNAME="nobody",
    XDG_CACHE_HOME=str(ROOT/".cache"),XDG_DATA_HOME=str(ROOT/".local/share"),
    XDG_CONFIG_HOME=str(ROOT/".config"),
    LIBGL_ALWAYS_SOFTWARE="1",GALLIUM_DRIVER="llvmpipe",
    WINEDEBUG="-all", DISPLAY=":116")
os.environ.update(env_base)
# Separate, unlimited benchmark cgroup; public fleet is stopped by user authorization.
assert CG.exists() and (CG/"cpu.max").read_text().strip()=="max 100000", "benchmark must be unthrottled"
(CG/"cgroup.procs").write_text(str(os.getpid()))
uid,gid=65534,65534
procs=[]
def demote():
    os.setgid(gid); os.setuid(uid)
def launch(args,cwd,env,log_name):
    f=open(E/log_name,"ab",buffering=0)
    p=subprocess.Popen(args,cwd=str(cwd),env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,
        preexec_fn=demote,start_new_session=True)
    f.close()
    procs.append(p)
    return p
def stop(p,timeout=6):
    if p is None: return
    try: os.killpg(p.pid,signal.SIGTERM)
    except ProcessLookupError: pass
    try: p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        try: p.wait(timeout=2)
        except subprocess.TimeoutExpired: pass
def stat(pid):
    s=pathlib.Path(f"/proc/{pid}/stat").read_text().split()
    return (int(s[13])+int(s[14]))/os.sysconf("SC_CLK_TCK")
def read(p):return p.read_text(errors="replace") if p.exists() else ""
def capture(stage):
    src=D/"botA/SeriousSam.log"
    if src.exists(): shutil.copy2(src,E/(stage+"-SeriousSam.log"))
    src=D/"server/Dedicated_BotTest.log"
    if src.exists(): shutil.copy2(src,E/(stage+"-server.log"))
def sigs(stage):
    slog=read(E/(stage+"-server.log")); blog=read(E/(stage+"-SeriousSam.log"))
    ticks=[int(x) for x in re.findall(r"\[BotDriver\] bot0 tick=(\d+)",blog)]
    return {"crc_ok":slog.count("CRC check OK"),"joined":slog.count(" joined"),
       "bot0_tick_max":max(ticks) if ticks else None,
       "local_bot_slots":len(set(re.findall(r"\[BotDriver\] local player (\d+)",blog))),
       "syncbad":len(re.findall(r"SYNCBAD|Too many bad syncs|bad sync|CRC check failed",slog+blog,re.I)),
       "gl_software":bool(re.search(r"llvmpipe|Mesa",blog,re.I))}
result={"benchmark_started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()), "result_dir":str(E),"qualification":"RUNNING", "host":"Hetzner ubuntu-4gb-nbg1-2","isolated_netns":True,
    "cgroup_cpu_max":"max 100000","config_fps":20,
    "scope":"single four-local-player client + isolated dedicated; never live server", "runs":[]}
x=None
try:
    x=launch(["Xvfb",":116","-screen","0","640x480x24","-nolisten","tcp","-noreset"],D,env_base,"xvfb.out")
    time.sleep(2)
    if x.poll() is not None: raise RuntimeError("Xvfb failed to start")
    # Refuse concurrent game instances outside this private test namespace.
    for proc in pathlib.Path('/proc').iterdir():
        if proc.name.isdigit():
            try:
                command=(proc/'cmdline').read_bytes().split(b'\0')[0].lower()
                assert not command.endswith((b'/serioussam.exe',b'/dedicatedserver.exe')), 'another game process is active'
            except (FileNotFoundError,PermissionError): pass
    # A fixed map has no scheduled transition during CPU samples.
    begin=D/'server/Scripts/Dedicated/BotTest/1_begin.ini'
    fixed=begin.read_text()
    fixed=re.sub(r'gam_iTimeLimit\s*=\s*\d+;', 'gam_iTimeLimit=0;',fixed)
    write_runtime_config(begin,fixed,uid,gid)
    config_path=D/"botA/Scripts/HetznerCPUBenchmark.ini"
    base=(D/"botA/Scripts/HetznerFleet.ini").read_text()
    # Disable noisy instrumentation, leave combat and obstacle avoidance as-is.
    base=re.sub(r"^bot_iLogEvery=.*?$","bot_iLogEvery=20;",base,flags=re.M)
    base=re.sub(r"^bot_bDiagnostics=.*?$","bot_bDiagnostics=0;",base,flags=re.M)
    base=re.sub(r"^net_strLocalHost=.*?$",'net_strLocalHost="127.0.0.2";',base,flags=re.M)
    for rep,stage,null in [(r,s,n) for r in range(args.repeats) for s,n in ([("render_on",0),("null_render",1)] if r%2==0 else [("null_render",1),("render_on",0)])]:
        stage=f"repeat{rep+1}-{stage}"
        config=base + "\n"+f"bot_bNullRender={null};\n" + "sam_iMaxFPSActive=20;\nsam_iMaxFPSInactive=10;\nsam_bPauseOnMinimize=0;\n"
        write_runtime_config(config_path,config,uid,gid)
        check=subprocess.run(["runuser","-u","nobody","--","test","-r",str(config_path)])
        assert check.returncode==0, "INI unreadable by runtime user"
        for old in (D/"botA/SeriousSam.log",D/"server/Dedicated_BotTest.log"):
            if old.exists(): old.unlink()
        serverenv=dict(env_base,WINEPREFIX=str(D/"prefix-server"))
        botenv=dict(env_base,WINEPREFIX=str(D/"prefix-botA"))
        sv=launch(["wine","Bin/DedicatedServer.exe","BotTest"],D/"server",serverenv,stage+"-server-wine.out")
        time.sleep(7)
        if sv.poll() is not None: raise RuntimeError(stage+" dedicated exited "+str(sv.returncode))
        bp=launch(["wine","Bin/SeriousSam.exe","+connect","127.0.0.1:26860","+quickjoin","+script","Scripts\\HetznerCPUBenchmark.ini"],D/"botA",botenv,stage+"-bot-wine.out")
        print(f"START {stage} server_pid={sv.pid} bot_pid={bp.pid}",flush=True)
        ready_deadline=time.monotonic()+120
        while True:
            assert bp.poll() is None and sv.poll() is None, 'process exited before warmup'
            capture(stage)
            ready=sigs(stage)
            if ready['crc_ok']>0 and ready['joined']>=4 and ready['bot0_tick_max'] is not None: break
            if time.monotonic()>ready_deadline: raise RuntimeError('bot actions/CRC/join not ready')
            time.sleep(1)
        print(f'WARMUP {stage} {args.warmup}s',flush=True)
        time.sleep(args.warmup)
        if bp.poll() is not None: raise RuntimeError(stage+" bot exited "+str(bp.returncode))
        capture(stage)
        preliminary=sigs(stage)
        if preliminary["crc_ok"]==0 or preliminary["joined"]<4 or preliminary["bot0_tick_max"] is None:
            raise RuntimeError(stage+" unable to validate bot join: "+json.dumps(preliminary))
        def cg_stat():
            return {k:int(v) for k,v in (line.split() for line in (CG/'cpu.stat').read_text().splitlines())}
        before_cg=cg_stat()
        def host_cpu():return list(map(int,pathlib.Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
        host_before=host_cpu()
        def thread_cpu(pid):
            values={}
            for item in pathlib.Path(f'/proc/{pid}/task').iterdir():
                try:
                    fields=(item/'stat').read_text().rsplit(') ',1)[1].split()
                    values[item.name]=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK')
                except FileNotFoundError:pass
            return values
        threads_before=thread_cpu(bp.pid)
        blog_path=D/'botA/SeriousSam.log'
        initial=read(blog_path)
        boundary='\n'.join(re.findall(r'^\[BotDriver\].*$',initial,re.M)[-4:])
        offset=len(initial)
        a=stat(bp.pid); sa=stat(sv.pid)
        t=time.monotonic();previous=t;previous_cpu=a
        samples=[]
        while time.monotonic()-t < args.measure:
            time.sleep(min(1,max(0,args.measure-(time.monotonic()-t))))
            assert bp.poll() is None and sv.poll() is None,'runtime exited'
            now=time.monotonic(); current=stat(bp.pid)
            samples.append((current-previous_cpu)/(now-previous)*100)
            previous=now;previous_cpu=current
        dt=time.monotonic()-t
        b=stat(bp.pid); sb=stat(sv.pid)
        after_cg=cg_stat()
        threads_after=thread_cpu(bp.pid)
        host_delta=[b-a for a,b in zip(host_before,host_cpu())]
        host_total=sum(host_delta)
        host_busy=(host_total-host_delta[3]-host_delta[4])/host_total*100
        assert host_busy<90,'host saturated; reject CPU comparison'
        check_throttling(before_cg,after_cg)
        actions=action_evidence(boundary+'\n'+read(blog_path)[offset:],dt)
        total_cpu=(after_cg['usage_usec']-before_cg['usage_usec'])/1e6/dt*100
        assert total_cpu < 180, '2-vCPU host saturation invalidates comparison'
        sorted_samples=sorted(samples)
        cpu_details={'client_cpu_median':round(median(samples),3),
            'client_cpu_p95':round(sorted_samples[math.ceil(len(samples)*.95)-1],3),
            'client_cpu_peak':round(max(samples),3),'samples':len(samples),
            'server_cpu_core_percent':round((sb-sa)/dt*100,3),
            'whole_test_cgroup_cpu_core_percent':round(total_cpu,3),
            'new_throttled_periods':after_cg['nr_throttled']-before_cg['nr_throttled'],
            'actions':actions,'warmup_s':args.warmup,
            'host_busy_percent':round(host_busy,3),'host_steal_percent':round(host_delta[7]/host_total*100,3),
            'client_threads_cpu_core_percent':{tid:round((value-threads_before[tid])/dt*100,3)
                for tid,value in threads_after.items() if tid in threads_before},
            'server_rss_kib':int(pathlib.Path(f'/proc/{sv.pid}/status').read_text().split('VmRSS:')[1].split()[0])}

        capture(stage)
        info=sigs(stage)
        info.update(cpu_details)
        assert info["syncbad"]==0 and info["joined"]>=4 and info["crc_ok"]>0, "CRC/join/sync gate failed"
        info.update({"p0_tick_delta":(info["bot0_tick_max"]-preliminary["bot0_tick_max"]) if info["bot0_tick_max"] else None, "stage":stage,"null_render":null,"elapsed_s":dt,"cpu_core_percent":round((b-a)/dt*100,2),
             "pid":bp.pid,"server_pid":sv.pid,"frame_pacing_20fps_config":True,
             "memory_rss_kib":int(pathlib.Path(f"/proc/{bp.pid}/status").read_text().split("VmRSS:")[1].split()[0])})
        result["runs"].append(info)
        OUT.write_text(json.dumps(result,indent=2))
        print("RESULT "+json.dumps(info,ensure_ascii=True),flush=True)
        stop(bp);time.sleep(2);stop(sv);time.sleep(6)
        assert bp.poll() is not None and sv.poll() is not None
    result["completed"]=True
    result["qualification"]="CPU_AB_ONLY_PASSED_PENDING_60MIN_VANILLA_ACCEPTANCE"
except Exception as exc:
    result["completed"]=False
    result["qualification"]="NOT_QUALIFIED"
    result["error"]=str(exc)
    traceback.print_exc()
finally:
    for p in procs[::-1]:stop(p)
    result["finished_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
    OUT.write_text(json.dumps(result,indent=2))
    print("FINAL "+json.dumps(result,ensure_ascii=True),flush=True)
