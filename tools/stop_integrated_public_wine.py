#!/usr/bin/env python3
"""Stop only an identified retained public overlay; lower installations remain intact."""
import argparse,json,os,re,signal,subprocess,time
from pathlib import Path
from qualify_integrated_wine import close_window
def verify_process(info):
    p=Path("/proc")/str(info["pid"])
    try:fields=(p/"stat").read_text().rsplit(") ",1)[1].split()
    except FileNotFoundError:return False
    if fields[0]=="Z":return False
    assert int(fields[19])==info["start_ticks"],"PID start-time mismatch"
    if "cwd" in info:assert (p/"cwd").resolve()==Path(info["cwd"]),"PID working-directory mismatch"
    return True
def wait_exit(info,seconds):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if not verify_process(info):return True
        time.sleep(.2)
    return not verify_process(info)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--result",required=True,type=Path);a=p.parse_args()
    state=a.result.resolve();r=json.loads(state.read_text());root=state.parent
    assert r.get("left_running") and r["status"]=="PASS_PUBLIC_SMOKE","not a retained qualified public runtime"
    mounts=[Path(x) for x in r["production_mounts"]]
    assert all(x.parent==root for x in mounts)
    allowed={x["pid"] for x in r["processes"].values()}
    # Do not tear down a display containing an unregistered Retail observer.
    listing=subprocess.check_output(["xwininfo","-display",r["display"],"-root","-tree"],text=True)
    for wid in re.findall(r'(0x[0-9a-fA-F]+) "Serious Sam \(',listing):
        prop=subprocess.check_output(["xprop","-display",r["display"],"-id",wid,"_NET_WM_PID"],text=True)
        match=re.search(r"=\s*(\d+)\s*$",prop)
        if match:assert int(match[1]) in allowed,"close separately owned observer before stopping this display"
    for role,info in r["processes"].items():
        assert Path(info["cwd"]).parent==root
        if verify_process(info):
            name=Path("/proc/%d/cmdline"%info["pid"]).read_bytes().split(b"\0")[0].replace(b"\\",b"/").lower()
            assert name.endswith(b"/"+(b"dedicatedserver.exe" if role=="server" else b"serioussam.exe"))
    stopped={}
    for role,info in reversed(list(r["processes"].items())):
        if not verify_process(info):continue
        sent=close_window(info["pid"],r["display"]) if role!="server" else 0
        if not wait_exit(info,15 if sent else 1):
            assert verify_process(info);os.kill(info["pid"],signal.SIGTERM)
            if not wait_exit(info,10):
                assert verify_process(info);os.kill(info["pid"],signal.SIGKILL)
                assert wait_exit(info,5)
        stopped[role]={"closed":True,"wm_close_sent":sent}
    for role in r["processes"]:
        prefix=root/("prefix-"+role)
        for arg in ["-k","-w"]:
            subprocess.run(["runuser","-u","nobody","--","env","WINEPREFIX="+str(prefix),"wineserver",arg],check=True,capture_output=True,timeout=15)
    x=r["xvfb"]
    if verify_process(x):
        cmd=Path("/proc/%d/cmdline"%x["pid"]).read_bytes()
        assert b"Xvfb\0"+r["display"].encode()+b"\0" in cmd
        os.kill(x["pid"],signal.SIGTERM);assert wait_exit(x,10)
    unmounts=[]
    for target in reversed(mounts):
        # Each path must still be our overlay, not a replacement mount.
        lines=Path("/proc/self/mountinfo").read_text().splitlines()
        own=[l for l in lines if l.split()[4]==str(target)]
        assert len(own)==1 and " - overlay " in own[0] and "upperdir="+str(root/"layers")+"/" in own[0]
        proc=subprocess.run(["umount",str(target)],capture_output=True,text=True)
        unmounts.append({"path":str(target),"exitcode":proc.returncode,"error":proc.stderr})
        assert proc.returncode==0
    r.update(left_running=False,stopped=stopped,unmounts=unmounts,stopped_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()))
    state.write_text(json.dumps(r,indent=2)+"\n")
    print("STOPPED_OWN_PUBLIC_OVERLAY; original lower DLL/configuration unchanged")
if __name__=="__main__":main()
