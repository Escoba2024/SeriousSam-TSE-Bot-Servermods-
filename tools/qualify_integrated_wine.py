#!/usr/bin/env python3
"""Isolated Hetzner-only staged Retail-1.07 candidate qualification.
No installation, no public port changes, no production deployment.
Private runtime files and raw logs must never be committed.
"""
import argparse,ctypes,fcntl,hashlib,json,os,re,shutil,signal,socket,struct,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bot_telemetry as bt

PINS={"DedicatedServer.exe":"9596f53c260c6fe5f6b7b6666fdf210bcac9952e4eec4b2ee2ee82f37153052d","Engine.dll":"b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f","EntitiesMP.dll":"7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350","GameMP.dll":"1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208","SeriousSam.exe":"9f8f9a0b8fd718616036ed2c3584904e2dfd58e49515bf4c8ecc45175d02cc53"}
ROSTER=["BOT-Rookie-Rush","BOT-Rookie-Guard","BOT-Casual-Flaky","BOT-Casual-Holder","BOT-Average-Duelist","BOT-Average-Rifle","BOT-Veteran-Push","BOT-Expert-Rifle"]
BAD=re.compile(r"SYNCBAD|Too many bad syncs|CRC check failed|Cannot load script|[Uu]nknown symbol|[Uu]nrecognized symbol|Permission denied|[Ff]atal [Ee]rror")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p):return p.read_text(errors="replace") if p.exists() else ""
def params(raw):
    fields=raw.split("\\")
    return {fields[i]:fields[i+1] for i in range(1,len(fields)-1,2) if fields[i]}
def query(port):
    chunks=[]
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as q:
        q.settimeout(1);q.connect(("127.0.0.1",port));q.send(b"\\status\\")
        for _ in range(16):
            data=q.recv(65535).decode("latin1");chunks.append(data)
            if "\\final\\" in data:break
        else:raise RuntimeError("query has no final marker")
    raw="".join(chunks)
    if "\\final\\" not in raw:raise RuntimeError("query incomplete")
    return params(raw)
def cpu(pid):
    fields=(Path("/proc")/str(pid)/"stat").read_text().rsplit(") ",1)[1].split()
    return (int(fields[11])+int(fields[12]))/os.sysconf("SC_CLK_TCK")
def copy_file(src,dst):
    if str(src).lower().endswith(".gro"):os.symlink(str(Path(src).resolve()),dst)
    else:shutil.copy2(src,dst)
    return dst
def chown_tree(root):
    os.chown(root,65534,65534)
    for base,dirs,files in os.walk(root,followlinks=False):
        for name in dirs+files:
            p=Path(base)/name
            if not p.is_symlink():os.chown(p,65534,65534)
def change_profile(p,name):
    b=p.read_bytes();assert b[:4]==b"PLC4"
    n=struct.unpack_from("<I",b,4)[0];assert n<256
    side=p.with_suffix(p.suffix+".guid")
    old=side.read_bytes();assert len(old)==16 and b.count(old)==1
    new=os.urandom(16);name=name.encode("ascii")
    p.write_bytes(b[:4]+struct.pack("<I",len(name))+name+b[8+n:])
    p.write_bytes(p.read_bytes().replace(old,new,1));side.write_bytes(new)
def configure_count(game,count):
    if count not in (1,2,3,4):raise ValueError("local player count must be 1..4")
    p=game/"Data/SeriousSam.gms";b=bytearray(p.read_bytes());assert b[:8]==b"GAMEV012"
    n=struct.unpack_from("<I",b,8)[0];start=12+n;assert n==13 and b[12:start] in (b"TCP/IP Client",b"TCP/IP Server")
    b[12:start]=b"TCP/IP Client"
    for i in range(4):struct.pack_into("<i",b,start+8+4*i,i if i<count else -1)
    struct.pack_into("<i",b,start+24,count-1)
    p.write_bytes(b)
def close_window(pid,display):
    listing=subprocess.check_output(["xwininfo","-display",display,"-root","-tree"],text=True)
    x=ctypes.CDLL("libX11.so.6")
    x.XOpenDisplay.argtypes=[ctypes.c_char_p];x.XOpenDisplay.restype=ctypes.c_void_p
    x.XInternAtom.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int];x.XInternAtom.restype=ctypes.c_ulong
    class Data(ctypes.Union):_fields_=[("l",ctypes.c_long*5)]
    class Client(ctypes.Structure):_fields_=[("type",ctypes.c_int),("serial",ctypes.c_ulong),("send_event",ctypes.c_int),("display",ctypes.c_void_p),("window",ctypes.c_ulong),("message_type",ctypes.c_ulong),("format",ctypes.c_int),("data",Data)]
    class Event(ctypes.Union):_fields_=[("client",Client),("pad",ctypes.c_long*24)]
    x.XSendEvent.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_int,ctypes.c_long,ctypes.POINTER(Event)]
    x.XFlush.argtypes=[ctypes.c_void_p];x.XCloseDisplay.argtypes=[ctypes.c_void_p]
    d=x.XOpenDisplay(display.encode());assert d;sent=0
    try:
        for value in set(re.findall(r"0x[0-9a-fA-F]+",listing)):
            prop=subprocess.run(["xprop","-display",display,"-id",value,"_NET_WM_PID"],capture_output=True,text=True).stdout
            if not re.search(r"=\s*"+str(pid)+r"\s*$",prop):continue
            e=Event();e.client.type=33;e.client.display=d;e.client.window=int(value,16);e.client.message_type=x.XInternAtom(d,b"WM_PROTOCOLS",0);e.client.format=32;e.client.data.l[0]=x.XInternAtom(d,b"WM_DELETE_WINDOW",0)
            if x.XSendEvent(d,e.client.window,0,0,ctypes.byref(e)):sent+=1
        x.XFlush(d)
    finally:x.XCloseDisplay(d)
    return sent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("runtime","template","vanilla","build-manifest"):parser.add_argument("--"+name,required=True,type=Path)
    parser.add_argument("--port",type=int,default=26980);parser.add_argument("--display",default=":117")
    parser.add_argument("--stage",choices=("one","four","eight","legacy-four"),required=True)
    parser.add_argument("--duration",type=int,required=True)
    parser.add_argument("--prepare-only",action="store_true")
    args=parser.parse_args()
    expected={"one":1,"four":4,"eight":8,"legacy-four":4}[args.stage];human=args.stage!="legacy-four"
    observer=args.stage in ("one","eight");population=expected+int(observer)
    assert args.duration>0 and (args.stage!="eight" or args.duration>=3600)
    runtime=args.runtime.resolve();runtime.mkdir(exist_ok=True);os.chmod(runtime,0o755);os.chown(runtime,65534,65534)
    lock=open(runtime/"runtime.lock","w");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    build=json.loads(args.build_manifest.read_text());assert build["build_ok"] and not build["qualified"]
    dll=Path(build["candidate"]);assert sha(dll)==build["dll_sha256"]
    E=runtime/(args.stage+"-"+time.strftime("%H%M%S",time.gmtime()));E.mkdir()
    result={"status":"PREPARING","stage":args.stage,"human_ai":human,"bots":expected,"required_s":args.duration,"dll_sha256":sha(dll),"processes":{},"scope":"ISOLATED_LOCAL_RETAIL_WINE_NOT_PUBLIC_ACCEPTANCE"}
    def save(**kw):
        result.update(kw);result["utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime());(E/"result.json").write_text(json.dumps(result,indent=2)+"\n");print(result["status"],flush=True)
    roles={};procs={};x=None;mounts=[]
    result["storage"]="private overlayfs copy-on-write; lower installations unchanged"
    def overlay(src,target,label):
        layer=E/"layers"/label;layer.mkdir(parents=True)
        for name in ("upper","work"):(layer/name).mkdir()
        target.mkdir()
        subprocess.run(["mount","-t","overlay","overlay","-o","lowerdir="+str(src)+",upperdir="+str(layer/"upper")+",workdir="+str(layer/"work"),str(target)],check=True)
        mounts.append(target)
        os.chown(target,65534,65534)
        return target
    def rss(pid):
        return int((Path("/proc")/str(pid)/"status").read_text().split("VmRSS:")[1].split()[0])
    try:
        for port in (args.port,args.port+1):
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:s.bind(("127.0.0.1",port))
        for role in ["server","botA"]+(["botB"] if expected==8 else [])+(["vanilla"] if observer else []):
            src=(args.vanilla if role=="vanilla" else args.template/role).resolve()
            game=overlay(src,E/role,role);roles[role]=game
            prefix=E/("prefix-"+role)
            sourceprefix=args.template/("prefix-server" if role=="server" else "prefix-botA")
            overlay(sourceprefix.resolve(),prefix,"prefix-"+role)
            for name,want in PINS.items():
                if name=="GameMP.dll" and role.startswith("bot"):continue
                assert sha(game/"Bin"/name)==want,role+" original mismatch "+name
            if role.startswith("bot"):
                shutil.copy2(dll,game/"Bin/GameMP.dll")
                offset=4 if role=="botB" else 0
                for i in range(4):change_profile(game/"Players"/("Player%d.plr"%i),ROSTER[offset+i])
                configure_count(game,1 if expected==1 else 4)
                script=(Path(__file__).resolve().parents[1]/"poc/scripts/Phase1HumanAI.ini").read_text()
                script+="\nbot_bHumanAI=%d;\nbot_iRosterOffset=%d;\nbot_bNullRender=1;\nbot_iNullRenderFps=20;\nbot_iTelemetry=1;\nbot_iLogEvery=20;\nbot_bDiagnostics=0;\nbot_bDiag=1;\nsam_iMaxFPSActive=20;\nsam_iMaxFPSInactive=10;\nsam_bPauseOnMinimize=0;\nnet_strLocalHost=\"\";\n"%(int(human),offset)
                (game/"Scripts/Integrated.ini").write_text(script)
                for old in (game/"SeriousSam.log",game/"Bin/BotTelemetry.csv"):
                    if old.exists():old.unlink()
            elif role=="vanilla":
                configure_count(game,1)
                change_profile(game/"Players/Player0.plr","Retail_Control")
                if (game/"SeriousSam.log").exists():(game/"SeriousSam.log").unlink()
            else:
                p=game/"Scripts/Dedicated_startup.ini"
                p.write_text(text(p)+"\nnet_strLocalHost=\"127.0.0.1\";\nnet_iPort=%d;\nser_bHeartbeatGameSpy=0;\nser_bEnumeration=1;\nser_bReportSyncBad=1;\nser_bReportSyncOK=0;\n"%args.port)
                if (game/"Dedicated_BotTest.log").exists():(game/"Dedicated_BotTest.log").unlink()
            if role.startswith("bot"):os.chown(game/"Scripts/Integrated.ini",65534,65534)
        os.chown(E,65534,65534)
        if args.prepare_only:
            save(status="PREFLIGHT_ONLY_NO_GAME_STARTED",runtime_qualified=False)
            return
        def demote():os.setgid(65534);os.setuid(65534)
        common=dict(os.environ,HOME=str(runtime),WINEARCH="win32",WINEDEBUG="-all",DISPLAY=args.display,LIBGL_ALWAYS_SOFTWARE="1",GALLIUM_DRIVER="llvmpipe",LP_NUM_THREADS="1",XDG_CACHE_HOME=str(runtime/"cache"))
        cg=Path("/sys/fs/cgroup")/("tse-integration-"+str(os.getpid()))
        cg.mkdir();(cg/"cpu.max").write_text("max 100000");(cg/"cgroup.procs").write_text(str(os.getpid()))
        with (E/"xvfb.log").open("wb") as out:x=subprocess.Popen(["Xvfb",args.display,"-screen","0","640x480x24","-nolisten","tcp","-noreset"],stdout=out,stderr=subprocess.STDOUT,preexec_fn=demote)
        time.sleep(2);assert x.poll() is None
        def launch(role):
            game=roles[role];env=dict(common,WINEPREFIX=str(E/("prefix-"+role)))
            cmd=["wine","Bin/DedicatedServer.exe","BotTest"] if role=="server" else ["wine","Bin/SeriousSam.exe","+connect","127.0.0.1:%d"%args.port,"+quickjoin"]+(["+script","Scripts\\Integrated.ini"] if role.startswith("bot") else [])
            with (E/(role+"-wine.log")).open("wb") as out:p=subprocess.Popen(cmd,cwd=game,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,preexec_fn=demote,start_new_session=True)
            procs[role]=p;result["processes"][role]={"pid":p.pid,"cwd":str(game)};save(status="JOINING")
        launch("server");time.sleep(8);launch("botA")
        if expected==8:time.sleep(5);launch("botB")
        if observer:time.sleep(5);launch("vanilla")
        deadline=time.monotonic()+120
        while True:
            assert all(p.poll() is None for p in procs.values()),"process exited during join"
            try:r=query(args.port+1)
            except (OSError,RuntimeError):r={}
            if int(r.get("numplayers",-1))==population:break
            if time.monotonic()>deadline:raise RuntimeError("population readiness timeout")
            time.sleep(2)
        assert r.get("gamever")=="1.07" and not r.get("activemod")
        save(status="WARMUP");time.sleep(180 if args.duration>=600 else 30)
        def cgstat():return {k:int(v) for k,v in (line.split() for line in (cg/"cpu.stat").read_text().splitlines())}
        cgstart=cgstat()
        def hostcpu():return list(map(int,Path("/proc/stat").read_text().splitlines()[0].split()[1:9]))
        hoststart=hostcpu()
        begin=time.monotonic();cpustart={role:cpu(p.pid) for role,p in procs.items()}
        rows=[];save(status="MEASURING")
        while time.monotonic()-begin<args.duration:
            assert all(p.poll() is None for p in procs.values()),"runtime process exited"
            r=query(args.port+1);names=[v for k,v in r.items() if re.fullmatch(r"player_\d+",k)]
            assert int(r.get("numplayers",-1))==population and len(names)==population,"population drift"
            assert r.get("gamever")=="1.07" and not r.get("activemod"),"version/mod drift"
            for role,game in roles.items():
                logs=text(game/("Dedicated_BotTest.log" if role=="server" else "SeriousSam.log"))
                match=BAD.search(logs)
                if match:raise RuntimeError(role+" runtime failure "+match.group())
            row={"elapsed_s":time.monotonic()-begin,"players":names,"frags":{k:v for k,v in r.items() if k.startswith("frags_")},"cpu_s":{role:cpu(p.pid)-cpustart[role] for role,p in procs.items()},"rss_kib":{role:rss(p.pid) for role,p in procs.items()}}
            with (E/"measurements.jsonl").open("a") as out:out.write(json.dumps(row)+"\n")
            rows.append(row);result["elapsed_s"]=row["elapsed_s"];save(status="MEASURING")
            time.sleep(min(5,max(0,args.duration-(time.monotonic()-begin))))
        elapsed=time.monotonic()-begin;checks={}
        cgend=cgstat();assert cgend["nr_throttled"]==cgstart["nr_throttled"],"cgroup throttled"
        hd=[b-a for a,b in zip(hoststart,hostcpu())];busy=(sum(hd)-hd[3]-hd[4])/sum(hd)*100
        assert busy<90,"host saturated"
        result["host_steal_percent"]=hd[7]/sum(hd)*100
        result["host_busy_percent"]=busy;result["new_throttled_periods"]=cgend["nr_throttled"]-cgstart["nr_throttled"]
        for role,game in roles.items():
            logs=text(game/("Dedicated_BotTest.log" if role=="server" else "SeriousSam.log"))
            if role.startswith("bot"):
                count=1 if expected==1 else 4
                telemetry=bt.analyze(bt.parse((game/"Bin/BotTelemetry.csv").read_text()),warmup_s=190 if args.duration>=600 else 40,expect_bots=count,expect_nullrender=1)
                assert telemetry["verdict"]=="ACTIVE_OK" and telemetry["lp_median"]==count
                assert telemetry["config"].get("nullrender")=="1"
                assert telemetry["render_skip_total"]>0 and telemetry["render_draw_total"]==0
                if human:
                    profiles=re.findall(r"\[BotHuman\] local=(\d+) profile=(\S+) tier=(\d+) persona=(\S+)",logs)
                    assert len(set(p[0] for p in profiles))==count
                    assert "[BotHuman] local=0 tick=" in logs
                slots={}
                for slot in range(count):
                    markers=re.findall(r"\[BotDriver\] bot"+str(slot)+r" tick=(\d+) pos=\(([^)]+)\).*?fire=(\d)",logs)
                    assert len(markers)>2
                    slots[str(slot)]={"max_tick":max(int(m[0]) for m in markers),"moved":len(set(m[1] for m in markers))>1,"fired":any(m[2]=="1" for m in markers)}
                if expected>=4:assert all(v["moved"] and v["fired"] for v in slots.values()),"inactive movement/combat"
                checks[role]={"telemetry":telemetry,"slots":slots}
            elif role=="vanilla":assert "joined" in logs,"original client did not join"
        score_changed=any(row["frags"]!=rows[0]["frags"] for row in rows)
        if expected>=4:assert score_changed,"no scoring activity"
        save(status="PASS_LIMITED" if expected<8 else "PASS_60MIN_WINE",elapsed_s=elapsed,samples=len(rows),checks=checks,score_changed=score_changed,rss_kib={role:rss(p.pid) for role,p in procs.items()},cpu_core_percent={role:round((cpu(p.pid)-cpustart[role])/elapsed*100,3) for role,p in procs.items()})
    except Exception as exc:
        save(status="FAIL",error=str(exc))
        raise
    finally:
        cleanup={}
        for role,p in reversed(list(procs.items())):
            if p.poll() is None:
                try:sent=close_window(p.pid,args.display) if role!="server" else 0
                except Exception:sent=0
                try:p.wait(timeout=15 if sent else 1)
                except subprocess.TimeoutExpired:
                    if Path("/proc/%d/cwd"%p.pid).resolve()!=roles[role]:raise RuntimeError("cleanup PID ownership mismatch")
                    p.terminate()
                    try:p.wait(timeout=10)
                    except subprocess.TimeoutExpired:p.kill();p.wait()
                cleanup[role]={"exitcode":p.poll(),"wm_close_sent":sent}
        if x is not None and x.poll() is None:x.terminate();x.wait(timeout=10)
        for role in procs:
            prefix=E/("prefix-"+role)
            subprocess.run(["runuser","-u","nobody","--","env","WINEPREFIX="+str(prefix),"wineserver","-k"],capture_output=True,timeout=15)
            subprocess.run(["runuser","-u","nobody","--","env","WINEPREFIX="+str(prefix),"wineserver","-w"],capture_output=True,timeout=15)
        unmounts=[]
        for target in reversed(mounts):
            proc=subprocess.run(["umount",str(target)],capture_output=True,text=True)
            unmounts.append({"path":str(target),"exitcode":proc.returncode,"error":proc.stderr.strip()})
        result["cleanup"]=cleanup;result["unmounts"]=unmounts;result["private_raw_logs"]=str(E/"layers");save()
if __name__=="__main__":main()
