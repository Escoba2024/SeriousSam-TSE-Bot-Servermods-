#!/usr/bin/env python3
"""Isolated Hetzner-only staged Retail-1.07 candidate qualification.
Default: isolated tests. Explicit --public-address retains a passed public smoke.
No installation; protected lower installations remain unchanged.
Private runtime files and raw logs must never be committed.
"""
import argparse,ctypes,fcntl,hashlib,ipaddress,json,os,re,shutil,signal,socket,struct,subprocess,sys,time,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bot_telemetry as bt
from bot_session_runtime import profile_bytes, guid_bytes, startup_script

PINS={"DedicatedServer.exe":"9596f53c260c6fe5f6b7b6666fdf210bcac9952e4eec4b2ee2ee82f37153052d","Engine.dll":"b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f","EntitiesMP.dll":"7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350","GameMP.dll":"1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208","SeriousSam.exe":"9f8f9a0b8fd718616036ed2c3584904e2dfd58e49515bf4c8ecc45175d02cc53"}
ROSTER=["BOT-Rookie-Rush","BOT-Rookie-Guard","BOT-Casual-Flaky","BOT-Casual-Holder","BOT-Average-Duelist","BOT-Average-Rifle","BOT-Veteran-Push","BOT-Expert-Rifle"]
BAD=re.compile(r"Identifier '(?!sam_strTechTestLevel')[^']+' is not declared|SYNCBAD|Too many bad syncs|CRC check failed|Cannot load script|[Uu]nknown symbol|[Uu]nrecognized symbol|Permission denied|[Ff]atal [Ee]rror")
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
def change_profile_identity(game, identity, *, color_probe=False):
    """Only after game has been mounted as a fresh isolated overlay."""
    assert game.is_mount(), "never write a lower/native or live installation"
    p=game/"Players/Player0.plr"; side=p.with_suffix(".plr.guid")
    source=p.read_bytes();old=side.read_bytes()
    assert len(old)==16 and source.count(old)==1, "profile/sidecar provenance mismatch"
    length=struct.unpack_from("<I",source,4)[0]
    assert source[12+length:28+length]==old, "unknown PLC4 GUID layout"
    rewritten=profile_bytes(source,identity,color_probe=color_probe);new=guid_bytes(identity)
    p.write_bytes(rewritten);side.write_bytes(new)
    assert p.read_bytes()==rewritten and side.read_bytes()==new
    return hashlib.sha256(rewritten).hexdigest()

def configure_count(game,count):
    if count not in (1,2,3,4):raise ValueError("local player count must be 1..4")
    p=game/"Data/SeriousSam.gms";b=bytearray(p.read_bytes());assert b[:8]==b"GAMEV012"
    n=struct.unpack_from("<I",b,8)[0];start=12+n;assert n==13 and b[12:start] in (b"TCP/IP Client",b"TCP/IP Server")
    b[12:start]=b"TCP/IP Client"
    for i in range(4):struct.pack_into("<i",b,start+8+4*i,i if i<count else -1)
    struct.pack_into("<i",b,start+24,count-1)
    p.write_bytes(b)
def validate_public_evidence(report,dll_sha):
    assert report.get("status")=="PASS_60MIN_WINE","completed eight-bot hour required"
    assert report.get("bots")==8 and report.get("human_ai") is True
    assert report.get("elapsed_s",0)>=3600 and report.get("dll_sha256")==dll_sha
    assert report.get("new_throttled_periods")==0
    assert report.get("unmounts") and all(x["exitcode"]==0 for x in report["unmounts"])
    for role in ("botA","botB"):
        check=report["checks"][role]
        assert check["telemetry"]["verdict"]=="ACTIVE_OK"
        assert set(check["slots"])=={"0","1","2","3"}
        assert all(x["moved"] and x["fired"] for x in check["slots"].values())

def validate_master_resolution(resolve=socket.gethostbyname):
    target=resolve("master.333networks.com")
    assert ipaddress.ip_address(target).is_global,"public master must resolve globally"
    assert resolve("master.gamespy.com")==target,"Retail hardcoded master.gamespy.com must resolve to selected 333networks master; see official HOSTS guidance"
    return target

def dedicated_script(base,host,port,public):
    # Retail 1.07 GameSpy uses a hardcoded hostname; newer patch symbols do not apply.
    return base+'\nnet_strLocalHost="%s";\nnet_iPort=%d;\nser_bHeartbeatGameSpy=1;\nser_bEnumeration=1;\nser_bReportSyncBad=1;\nser_bReportSyncOK=%d;\n'%(host,port,int(public))

def population_ready(status,names,expected,public):
    count=int(status.get("numplayers",-1))
    if public:
        return expected<=count<=16 and len(names)==count and set(ROSTER).issubset(names)
    return count==expected and len(names)==expected

def make_run_directory(runtime,stage):
    return Path(tempfile.mkdtemp(prefix=stage+"-"+time.strftime("%H%M%S",time.gmtime())+"-",dir=runtime))

def reference_slot_activity(logs,count,elapsed):
    assert elapsed>0,"invalid measurement duration"
    slots={}
    for slot in range(count):
        rows=re.findall(r"\[BotDriver\] bot"+str(slot)+r" tick=(\d+) pos=\(([^)]+)\).*?fire=(\d)",logs)
        assert len(rows)>2,"missing reference status rows"
        ticks=[int(x[0]) for x in rows]
        assert all(b>a for a,b in zip(ticks,ticks[1:])),"reference tick reset"
        rate=(ticks[-1]-ticks[0])/elapsed
        assert 18<=rate<=22,"reference action rate outside 18..22Hz"
        moved=len(set(x[1] for x in rows))>1
        assert moved,"reference movement missing"
        slots[str(slot)]={"max_tick":ticks[-1],"tick_span":ticks[-1]-ticks[0],"tick_hz":rate,"samples":len(rows),"moved":moved,"combat_fire_counter_available":False}
    return slots

def slot_activity(logs,count):
    slots={}
    for slot in range(count):
        markers=re.findall(r"\[BotDriver\] bot"+str(slot)+r" tick=(\d+) pos=\(([^)]+)\).*?fire=(\d) combat_fire_actions=(\d+)",logs)
        assert len(markers)>2,"missing measured per-slot activity/counters"
        ticks=[int(m[0]) for m in markers];fires=[int(m[3]) for m in markers]
        assert all(b>a for a,b in zip(ticks,ticks[1:])),"tick reset/stall"
        assert all(b>=a for a,b in zip(fires,fires[1:])),"fire counter reset"
        delta=fires[-1]-fires[0]
        slots[str(slot)]={"max_tick":ticks[-1],"tick_span":ticks[-1]-ticks[0],"samples":len(markers),"moved":len(set(m[1] for m in markers))>1,"fired":delta>0,"fire_actions_delta":delta}
    return slots

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
    for name in ("runtime","template","vanilla"):parser.add_argument("--"+name,required=True,type=Path)
    artifact=parser.add_mutually_exclusive_group(required=True)
    artifact.add_argument("--build-manifest",type=Path)
    artifact.add_argument("--reference-dll",type=Path)
    parser.add_argument("--port",type=int,default=26980);parser.add_argument("--display",default=":117")
    parser.add_argument("--stage",choices=("one","four","eight","legacy-four","reference-four"),required=True)
    parser.add_argument("--duration",type=int,required=True)
    parser.add_argument("--prepare-only",action="store_true")
    parser.add_argument("--public-address",help="Public IPv4; requires a passed same-DLL hour and leaves successful eight-bot smoke running")
    parser.add_argument("--acceptance-report",type=Path)
    parser.add_argument("--identity-record",type=Path,help="isolated one-bot smoke only; private serialized Planner identity")
    parser.add_argument("--color-probe",action="store_true",help="private one-bot native markup test, NEVER production activation")
    parser.add_argument("--identity-rejoin-smoke",action="store_true",help="private in-place orderly bot disconnect and rejoin on the SAME live test server")
    args=parser.parse_args()
    expected={"one":1,"four":4,"eight":8,"legacy-four":4,"reference-four":4}[args.stage];human=args.stage in ("one","four","eight")
    reference=args.stage=="reference-four"
    assert not reference or args.duration>=600,"reference CPU minimum is 600s"
    public=args.public_address is not None
    if public:
        assert args.stage=="eight" and args.duration>=600 and args.port==25600
        address=ipaddress.ip_address(args.public_address)
        assert address.version==4 and address.is_global,"a public IPv4 is required"
        assert args.acceptance_report is not None
    observer=args.stage in ("one","eight") and not public;population=expected+int(observer)
    identity=None
    assert not args.color_probe or args.identity_record, "color probe requires private identity"
    assert not args.identity_rejoin_smoke or (args.identity_record and args.stage=="one" and not public and not reference and not args.color_probe), "identity rejoin requires private one-bot plain-name isolation"
    if args.identity_record:
        assert args.stage=="one" and not reference and not public, "identity record only for private single-bot stage"
        identity=json.loads(args.identity_record.read_text())
        # Validate all identity fields before mounting or creating any test resources.
        guid_bytes(identity);startup_script(identity)
        if args.color_probe:
            profile_bytes(b"PLC4"+struct.pack("<I",3)+b"Old"+b"TEAM"+bytes(range(16))+b"TAIL",identity,color_probe=True)
    assert args.duration>0 and (args.stage!="eight" or public or args.duration>=3600)
    runtime=args.runtime.resolve();runtime.mkdir(exist_ok=True);os.chmod(runtime,0o755);os.chown(runtime,65534,65534)
    lock=open(runtime/"runtime.lock","w");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if reference:
        assert args.reference_dll is not None,"reference-four requires --reference-dll"
        dll=args.reference_dll.resolve()
        assert sha(dll)=="61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9","immutable reference hash mismatch"
    else:
        assert args.build_manifest is not None,"integrated stages require --build-manifest"
        build=json.loads(args.build_manifest.read_text());assert build["build_ok"] and not build["qualified"]
        dll=Path(build["candidate"]);assert sha(dll)==build["dll_sha256"]
    if public:
        validate_public_evidence(json.loads(args.acceptance_report.read_text()),sha(dll))
        master_ipv4=validate_master_resolution()
    E=make_run_directory(runtime,args.stage)
    result={"status":"PREPARING","stage":args.stage,"human_ai":human,"bots":expected,"required_s":args.duration,"dll_sha256":sha(dll),"processes":{},"scope":"ISOLATED_LOCAL_RETAIL_WINE_NOT_PUBLIC_ACCEPTANCE"}
    def save(**kw):
        result.update(kw);result["utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime());(E/"result.json").write_text(json.dumps(result,indent=2)+"\n");print(result["status"],flush=True)
    roles={};procs={};x=None;mounts=[];keep_running=False
    connect_host=args.public_address if public else "127.0.0.1"
    result["public_address"]=args.public_address
    result["game_port"]=args.port;result["query_port"]=args.port+1
    result["display"]=args.display
    if public:
        result["scope"]="PUBLIC_HETZNER_EIGHT_BOT_SMOKE_NOT_INDEPENDENT_WINDOWS_JOIN"
        result["legacy_master_ipv4"]=master_ipv4
    result["storage"]="private overlayfs copy-on-write; lower installations unchanged"
    result["artifact_kind"]="immutable_prior_qualified_reference" if reference else "integrated_msvc_candidate"
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
        for host,port in ((connect_host,args.port),("0.0.0.0",args.port+1)):
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:s.bind((host,port))
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
                if identity:
                    assert role=="botA" and expected==1
                    result["identity_profile_sha256"]=change_profile_identity(game,identity,color_probe=args.color_probe)
                    result["identity_mode"]="SINGLE_BOT_PRIVATE_COLOR_PROBE" if args.color_probe else "SINGLE_BOT_PRIVATE_NO_COLORS"
                else:
                    for i in range(4):change_profile(game/"Players"/("Player%d.plr"%i),ROSTER[offset+i])
                configure_count(game,1 if expected==1 else 4)
                if reference:
                    script=text(game/"Scripts/HetznerFleet.ini")
                    script=re.sub(r"bot_iLogEvery\s*=\s*\d+;","bot_iLogEvery=20;",script)
                    script+="\nsam_iMaxFPSActive=20;\nsam_iMaxFPSInactive=10;\nsam_bPauseOnMinimize=0;\nnet_strLocalHost=\"\";\n"
                else:
                    script=(Path(__file__).resolve().parents[1]/"poc/scripts/Phase1HumanAI.ini").read_text()
                    script+="\nbot_bHumanAI=%d;\nbot_iRosterOffset=%d;\nbot_bNullRender=1;\nbot_iNullRenderFps=20;\nbot_iTelemetry=1;\nbot_iLogEvery=20;\nbot_bDiagnostics=0;\nbot_bDiag=1;\nsam_iMaxFPSActive=20;\nsam_iMaxFPSInactive=10;\nsam_bPauseOnMinimize=0;\nnet_strLocalHost=\"\";\n"%(int(human),offset)
                if identity:
                    script+="\n"+startup_script(identity)
                if public:script+="\nbot_iLogEvery=200;\nbot_bDiag=0;\n"
                (game/"Scripts/Integrated.ini").write_text(script)
                for old in (game/"SeriousSam.log",game/"Bin/BotTelemetry.csv"):
                    if old.exists():old.unlink()
            elif role=="vanilla":
                configure_count(game,1)
                change_profile(game/"Players/Player0.plr","Retail_Control")
                if (game/"SeriousSam.log").exists():(game/"SeriousSam.log").unlink()
            else:
                p=game/"Scripts/Dedicated_startup.ini"
                p.write_text(dedicated_script(text(p),connect_host,args.port,public))
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
        result["cgroup"]=str(cg)
        with (E/"xvfb.log").open("wb") as out:x=subprocess.Popen(["Xvfb",args.display,"-screen","0","640x480x24","-nolisten","tcp","-noreset"],stdout=out,stderr=subprocess.STDOUT,preexec_fn=demote)
        time.sleep(2);assert x.poll() is None
        result["xvfb"]={"pid":x.pid,"start_ticks":int(Path("/proc/%d/stat"%x.pid).read_text().rsplit(") ",1)[1].split()[19])}
        def launch(role):
            game=roles[role];env=dict(common,WINEPREFIX=str(E/("prefix-"+role)))
            cmd=["wine","Bin/DedicatedServer.exe","BotTest"] if role=="server" else ["wine","Bin/SeriousSam.exe","+connect","%s:%d"%(connect_host,args.port),"+quickjoin"]+(["+script","Scripts\\Integrated.ini"] if role.startswith("bot") else [])
            with (E/(role+"-wine.log")).open("wb") as out:p=subprocess.Popen(cmd,cwd=game,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,preexec_fn=demote,start_new_session=True)
            procs[role]=p;result["processes"][role]={"pid":p.pid,"cwd":str(game),"start_ticks":int(Path("/proc/%d/stat"%p.pid).read_text().rsplit(") ",1)[1].split()[19])};save(status="JOINING")
        launch("server");time.sleep(8);launch("botA")
        if expected==8:time.sleep(5);launch("botB")
        if observer:time.sleep(5);launch("vanilla")
        deadline=time.monotonic()+120
        while True:
            assert all(p.poll() is None for p in procs.values()),"process exited during join"
            try:r=query(args.port+1)
            except (OSError,RuntimeError):r={}
            names=[v for k,v in r.items() if re.fullmatch(r"player_\d+",k)]
            if population_ready(r,names,population,public):break
            if time.monotonic()>deadline:raise RuntimeError("population readiness timeout")
            time.sleep(2)
        assert r.get("gamever")=="1.07" and not r.get("activemod")
        if args.identity_rejoin_smoke:
            own=procs["botA"]
            own_record=result["processes"]["botA"].copy()
            assert own_record["pid"]==own.pid
            assert Path("/proc/%d/cwd"%own.pid).resolve()==roles["botA"]
            original_profile=sha(roles["botA"]/"Players/Player0.plr")
            original_guid=sha(roles["botA"]/"Players/Player0.plr.guid")
            assert original_profile==result["identity_profile_sha256"]
            sent=close_window(own.pid,args.display)
            assert sent>0,"own bot had no regular WM_DELETE_WINDOW"
            own.wait(timeout=25)
            assert own.poll() is not None
            absence_queries=0
            absent_start=time.monotonic()
            while time.monotonic()-absent_start<35:
                state=query(args.port+1)
                observed=[v for k,v in state.items() if re.fullmatch(r"player_\d+",k)]
                if (state.get("gamever")=="1.07" and observed==["Retail_Control"]
                        and state.get("numplayers")=="1"):
                    absence_queries+=1
                    if absence_queries>=3:break
                else:absence_queries=0
                time.sleep(2)
            assert absence_queries>=3,"own quit was not durably absent from original Retail query"
            assert procs["server"].poll() is None and procs["vanilla"].poll() is None
            assert sha(roles["botA"]/"Players/Player0.plr")==original_profile
            assert sha(roles["botA"]/"Players/Player0.plr.guid")==original_guid
            # Keep both private raw phases; restarting must never hide first-run evidence.
            for old,new in (("SeriousSam.log","botA-before-rejoin.log"),
                            ("Bin/BotTelemetry.csv","botA-before-rejoin-telemetry.csv"),
                            ("botA-wine.log","botA-before-rejoin-wine.log")):
                source=(E/old) if old=="botA-wine.log" else (roles["botA"]/old)
                if source.exists():shutil.move(str(source),str(E/new))
            launch("botA")
            deadline=time.monotonic()+100
            while time.monotonic()<deadline:
                assert procs["server"].poll() is None and procs["vanilla"].poll() is None
                assert procs["botA"].poll() is None,"rejoined client exited"
                try:
                    state=query(args.port+1)
                    observed=[v for k,v in state.items() if re.fullmatch(r"player_\d+",k)]
                    if (state.get("numplayers")=="2" and set(observed)==
                            {identity["nickname"],"Retail_Control"}):break
                except (OSError,RuntimeError):pass
                time.sleep(2)
            else:raise RuntimeError("same GUID rejoin did not show in original Retail query")
            result["identity_rejoin"]=dict(old_pid=own.pid,
                       new_pid=procs["botA"].pid,
                       old_start_ticks=own_record["start_ticks"],
                       old_exitcode=own.returncode,
                       old_wm_close_sent=sent,absence_queries=absence_queries,
                       profile_sha256=original_profile,guid_sidecar_sha256=original_guid,
                       same_server_pid=procs["server"].pid,
                       returned_name=identity["nickname"],
                       new_guid_stable=sha(roles["botA"]/"Players/Player0.plr.guid")==original_guid)
            assert result["identity_rejoin"]["new_guid_stable"]
            assert result["identity_rejoin"]["new_pid"]!=own.pid
            save(status="REJOINED_ON_SAME_SERVER")
        save(status="WARMUP");time.sleep(180 if args.duration>=600 else 30)
        # Preserve the final warmup row as each slot's counter boundary.
        activity_offsets={};activity_boundaries={}
        for role,game in roles.items():
            if role.startswith("bot"):
                logs=text(game/"SeriousSam.log")
                activity_offsets[role]=len(logs)
                count=1 if expected==1 else 4
                activity_boundaries[role]="\n".join(re.findall(r"^\[BotDriver\].*$",logs,re.M)[-count:])
        def cgstat():return {k:int(v) for k,v in (line.split() for line in (cg/"cpu.stat").read_text().splitlines())}
        cgstart=cgstat()
        def hostcpu():return list(map(int,Path("/proc/stat").read_text().splitlines()[0].split()[1:9]))
        hoststart=hostcpu()
        begin=time.monotonic();cpustart={role:cpu(p.pid) for role,p in procs.items()}
        rows=[];save(status="MEASURING")
        while time.monotonic()-begin<args.duration:
            assert all(p.poll() is None for p in procs.values()),"runtime process exited"
            r=query(args.port+1);names=[v for k,v in r.items() if re.fullmatch(r"player_\d+",k)]
            assert population_ready(r,names,population,public),"population drift or missing bot"
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
        result["whole_test_cgroup_cpu_core_percent"]=(cgend["usage_usec"]-cgstart["usage_usec"])/1e6/elapsed*100
        result["host_busy_percent"]=busy;result["new_throttled_periods"]=cgend["nr_throttled"]-cgstart["nr_throttled"]
        for role,game in roles.items():
            logs=text(game/("Dedicated_BotTest.log" if role=="server" else "SeriousSam.log"))
            if role.startswith("bot"):
                count=1 if expected==1 else 4
                telemetry=None
                if not reference:
                    telemetry=bt.analyze(bt.parse((game/"Bin/BotTelemetry.csv").read_text()),warmup_s=190 if args.duration>=600 else 40,expect_bots=count,expect_nullrender=1)
                    assert telemetry["verdict"]=="ACTIVE_OK" and telemetry["lp_median"]==count
                    assert telemetry["config"].get("nullrender")=="1"
                    assert telemetry["render_skip_total"]>0 and telemetry["render_draw_total"]==0
                if human:
                    profiles=re.findall(r"\[BotHuman\] local=(\d+) profile=(\S+) tier=(\d+) persona=(\S+)",logs)
                    assert len(set(p[0] for p in profiles))==count
                    assert "[BotHuman] local=0 tick=" in logs
                measured_logs=activity_boundaries[role]+"\n"+logs[activity_offsets[role]:]
                slots=reference_slot_activity(measured_logs,count,elapsed) if reference else slot_activity(measured_logs,count)
                if expected>=4 and not reference:assert all(v["moved"] and v["fired"] for v in slots.values()),"inactive movement/combat"
                checks[role]={"telemetry":telemetry,"slots":slots}
            elif role=="vanilla":assert "joined" in logs,"original client did not join"
        score_changed=any(row["frags"]!=rows[0]["frags"] for row in rows)
        if expected>=4:assert score_changed,"no scoring activity"
        save(status="PASS_PUBLIC_SMOKE" if public else ("PASS_LIMITED" if expected<8 else "PASS_60MIN_WINE"),elapsed_s=elapsed,samples=len(rows),checks=checks,score_changed=score_changed,rss_kib={role:rss(p.pid) for role,p in procs.items()},cpu_core_percent={role:round((cpu(p.pid)-cpustart[role])/elapsed*100,3) for role,p in procs.items()})
        keep_running=public
    except (Exception,KeyboardInterrupt) as exc:
        save(status="FAIL",error=str(exc) or type(exc).__name__)
        raise
    finally:
        if keep_running:
            result["left_running"]=True
            result["production_mounts"]=[str(p) for p in mounts]
            result["private_raw_logs"]=str(E/"layers")
            save()
        else:
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
