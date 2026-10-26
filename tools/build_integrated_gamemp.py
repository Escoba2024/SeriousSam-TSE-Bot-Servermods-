#!/usr/bin/env python3
"""Build a new, unqualified Retail-1.07 x86 candidate with an installed MSVC/Wine toolchain.

Never installs software or replaces runtime binaries. Run outside CPU measurement windows.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tarfile
import time
import xml.etree.ElementTree as ET

SDK_SHA="aa7869c2c2c4db0562281814d0ac3784e6b9d6f0"
INCLUDE_SHA="94ff8cd0e63941f8601294350b616472f772ed51"
ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stage_source_overlay(source,game):
    """Validate a flat source-only overlay before copying; return actual input pins."""
    source=Path(source).resolve();game=Path(game).resolve()
    if not source.is_dir() or not game.is_dir() or source==game:
        raise ValueError('separate existing source overlay and SDK game directory required')
    required={'Game.cpp','Game.vcxproj','BotDriver.cpp','BotDriver.h','bot_human.h'}
    entries=[p for p in source.iterdir() if p.suffix in ('.cpp','.h','.vcxproj')]
    if not required.issubset({p.name for p in entries}) or any(p.is_symlink() or not p.is_file() for p in entries):
        raise ValueError('complete regular flat GameMP source overlay required')
    pins={p.name:sha(p) for p in entries}
    for p in entries:
        shutil.copy2(p,game/p.name)
        if sha(game/p.name)!=pins[p.name]:raise RuntimeError('source overlay changed while staging')
    return pins


def build(args):
    out=args.output.resolve()
    out.mkdir(exist_ok=False)
    sdk=args.sdk.resolve()
    tools=args.toolchain.resolve()/"bin/x86"
    prefix=args.prefix.resolve()
    report={"qualified":False,"build_ok":False,"started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    env=dict(os.environ,WINEPREFIX=str(prefix),WINEARCH="win64",WINEDEBUG="-all")
    env.pop("DISPLAY",None)
    def run(cmd,cwd,log):
        with (out/log).open("wb") as stream:
            result=subprocess.run([str(x) for x in cmd],cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=600)
        print(log,"exit",result.returncode,flush=True)
        if result.returncode: raise RuntimeError(log+" failed: "+(out/log).read_text(errors="replace")[-3000:])
    try:
        for directory,expected in ((sdk,SDK_SHA),(sdk/"Sources/Includes",INCLUDE_SHA)):
            actual=subprocess.check_output(["git","-C",str(directory),"rev-parse","HEAD"],text=True).strip()
            if actual!=expected: raise RuntimeError("SDK revision mismatch: "+str(directory))
            if subprocess.check_output(["git","-C",str(directory),"status","--porcelain"]).strip():
                # SDK root may list a prepared external EntitiesTSE directory.
                if directory!=sdk: raise RuntimeError("modified include SDK")
        report["repo_commit"]=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
        report["repo_tree"]=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD^{tree}"],text=True).strip()
        archive=out/"sdk-game.tar"
        subprocess.run(["git","-C",str(sdk),"archive","--format=tar","-o",str(archive),"HEAD","Sources/Game","Sources/Properties"],check=True)
        with tarfile.open(archive) as t: t.extractall(out,filter="data")
        for name in ("Includes","EntitiesTSE"): (out/"Sources"/name).symlink_to(sdk/"Sources"/name,target_is_directory=True)
        overlay=getattr(args,'source_overlay',None)
        if overlay is None:
            overlay=out/"overlay"
            subprocess.run(["python3",str(ROOT/"poc/candidates/integrated-human-cpu-20261021/apply.py"),str(overlay)],check=True)
        game=out/"Sources/Game"
        report['overlay_sha256']=stage_source_overlay(overlay,game)
        report['source_overlay']=str(Path(overlay).resolve())
        shutil.copy2(sdk/"Sources/Includes/Engine107/EntitiesV.lib",game/"EntitiesMP.lib")
        ns={"m":"http://schemas.microsoft.com/developer/msbuild/2003"}
        files=[e.attrib["Include"] for e in ET.parse(game/"Game.vcxproj").findall(".//m:ClCompile",ns) if "Include" in e.attrib]
        include=[Path("."),Path(".."),sdk/"Sources/Includes/Engine107",sdk/"Sources/Includes/Engine107/EntitiesV",sdk/"Sources/Includes/Common",sdk/"Sources/Includes/CommonModels"]
        defines=["NDEBUG","WIN32","_WINDOWS","_WINDLL","_USRDLL","_USE_32BIT_TIME_T","SE1_D3D","DIRECT3D_VERSION=0x0800","SE1_VER=107","SE1_GAME='S'"]
        flags=["/nologo","/c","/MD","/O2","/Ob1","/Oy-","/Oi","/GF","/EHsc","/std:c++17","/W3","/wd4996","/wd4333","/Y-"]
        flags+=["/D"+d for d in defines]+["-I"+str(p) for p in include]
        report["source_sha256"]={p.name:sha(p) for p in game.iterdir() if p.suffix in (".cpp",".h",".vcxproj")}
        report["compiler_flags"]=flags
        report["sdk_commit"]=SDK_SHA
        report["include_commit"]=INCLUDE_SHA
        (out/"manifest.json").write_text(json.dumps(report,indent=2))
        for source in files:
            run([tools/"cl",*flags,source,"/Fo"+Path(source).stem+".obj"],game,"compile-"+source+".log")
        objects=[str(Path(f).with_suffix(".obj")) for f in files]
        run([tools/"link","/NOLOGO","/DLL","/MACHINE:X86","/OUT:GameMP.dll","/MAP:GameMP.map","-LIBPATH:"+str(game),"-LIBPATH:"+str(sdk/"Sources/Includes/Engine107"),"user32.lib",*objects],game,"link.log")
        candidate=game/"GameMP.dll"
        data=candidate.read_bytes()
        pe=struct.unpack_from("<I",data,0x3c)[0]
        if data[pe:pe+4]!=b"PE\0\0" or struct.unpack_from("<H",data,pe+4)[0]!=0x14c: raise RuntimeError("not PE32 x86")
        report.update(build_ok=True,candidate=str(candidate),dll_sha256=sha(candidate),source_count=len(files),configuration="Release_TSE107 equivalent direct cl/link, Win32")
        print(json.dumps(report),flush=True)
    except Exception as exc:
        report["error"]=str(exc)
        raise
    finally:
        report["finished_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        (out/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("sdk","toolchain","prefix","output"): p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--source-overlay",type=Path,help="explicit complete source-only candidate overlay; never a runtime directory")
    build(p.parse_args())
if __name__=="__main__": main()
