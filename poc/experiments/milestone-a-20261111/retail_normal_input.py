"""Normal keyboard/mouse input exclusively to the PID-verified Retail test client."""
import argparse,ctypes,json,pathlib,re,subprocess,time
p=argparse.ArgumentParser()
p.add_argument("--result",type=pathlib.Path,required=True)
p.add_argument("--key",choices=["w","a","s","d","space","Tab","Left","Right","Escape","Return","Up","Down","Home","End","Pause"])
p.add_argument("--button",type=int,choices=[1])
p.add_argument("--pointer",type=int,nargs=2)
p.add_argument("--seconds",type=float,default=1)
a=p.parse_args();assert 0<a.seconds<=10 and bool(a.key)!=bool(a.button)
r=json.loads(a.result.read_text());assert r["status"]=="OBSERVING"
display=r["display"]
role=r["processes"]["vanilla"];pid=role["pid"]
assert pathlib.Path("/proc/%d/cwd"%pid).resolve()==pathlib.Path(role["cwd"])
assert b"SeriousSam.exe" in pathlib.Path("/proc/%d/cmdline"%pid).read_bytes()
listing=subprocess.check_output(["xwininfo","-display",display,"-root","-tree"],text=True)
window=None
for wid in re.findall(r'(0x[0-9a-fA-F]+) "Serious Sam \(',listing):
    prop=subprocess.check_output(["xprop","-display",display,"-id",wid,"_NET_WM_PID"],text=True)
    if re.search(r"=\s*"+str(pid)+r"\s*$",prop):window=int(wid,16);break
assert window,"no PID-verified game window"
x=ctypes.CDLL("libX11.so.6");t=ctypes.CDLL("libXtst.so.6");D=ctypes.c_void_p
x.XOpenDisplay.argtypes=[ctypes.c_char_p];x.XOpenDisplay.restype=D
x.XSetInputFocus.argtypes=[D,ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
x.XRaiseWindow.argtypes=[D,ctypes.c_ulong]
x.XKeysymToKeycode.argtypes=[D,ctypes.c_ulong];x.XKeysymToKeycode.restype=ctypes.c_uint
x.XFlush.argtypes=[D];x.XCloseDisplay.argtypes=[D]
t.XTestFakeKeyEvent.argtypes=[D,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
t.XTestFakeButtonEvent.argtypes=[D,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
t.XTestFakeMotionEvent.argtypes=[D,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong]
d=x.XOpenDisplay(display.encode());assert d;x.XRaiseWindow(d,window);x.XSetInputFocus(d,window,2,0);x.XFlush(d);time.sleep(.5)
sym={"space":0x20,"Tab":0xff09,"Left":0xff51,"Right":0xff53,"Escape":0xff1b,"Return":0xff0d,"Up":0xff52,"Down":0xff54,"Home":0xff50,"End":0xff57,"Pause":0xff13}
code=x.XKeysymToKeycode(d,sym.get(a.key,ord(a.key) if a.key and len(a.key)==1 else 0)) if a.key else a.button
event=t.XTestFakeKeyEvent if a.key else t.XTestFakeButtonEvent
if a.pointer:
    assert all(0<=v<1024 for v in a.pointer)
    t.XTestFakeMotionEvent(d,-1,*a.pointer,0);x.XFlush(d);time.sleep(.1)
try:event(d,code,1,0);x.XFlush(d);time.sleep(a.seconds)
finally:event(d,code,0,0);x.XFlush(d);x.XCloseDisplay(d)
with (a.result.parent/"retail-control.jsonl").open("a") as out:out.write(json.dumps({"utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"pid":pid,"window":hex(window),"key":a.key,"button":a.button,"seconds":a.seconds,"purpose":"normal unmodified Retail control; no simulation changes"})+"\n")
print("Retail control completed",a.key or a.button,a.seconds)
