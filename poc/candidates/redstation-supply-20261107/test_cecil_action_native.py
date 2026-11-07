#!/usr/bin/env python3
"""Compile actual Driver action guards with SDK-shaped stubs; no runtime/ABI proof."""
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile

def function(source, name):
    # Mask comments/strings without moving offsets; nested braces remain balanced.
    masked = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                    lambda m: " " * len(m[0]), source)
    match = re.search(r"^static[^\n;]*\b" + name + r"\s*\([^;{}]*\)\s*\{", masked, re.M)
    if not match:
        raise ValueError("Driver helper missing: " + name)
    depth = 1
    for end in range(match.end(), len(masked)):
        depth += (masked[end] == "{") - (masked[end] == "}")
        if depth == 0:
            return source[match.start():end + 1]
    raise ValueError("Unbalanced Driver helper: " + name)

STUB = r'''
#include <cassert>
#include <cmath>
#include <limits>
using FLOAT=float;using ULONG=unsigned long;using INDEX=int;using BOOL=int;
struct FLOAT3D {float v[3]={0,0,0};float& operator()(int i){return v[i-1];}
 float operator()(int i)const{return v[i-1];}};
struct CPlacement3D {FLOAT3D pl_OrientationAngle;};
struct CPlayerWeapons {float m_fSniperFOV=20,m_fSniperMaxFOV=80;};
struct CPlayer {unsigned m_ulFlags=0;CPlayerWeapons* m_penWeapons=nullptr;
 CPlayerWeapons* GetPlayerWeapons(){return m_penWeapons;}CPlacement3D en_plViewpoint;};
struct CPlayerAction {FLOAT3D pa_vTranslation,pa_aRotation,pa_aViewRotation;};
'''
TEST = r'''
int main(){
 CPlayer p;CPlayerWeapons w;p.m_penWeapons=&w;p.en_plViewpoint.pl_OrientationAngle(1)=30;
 assert(BotCecilFinalBodyYaw(&p,8)==38);
 p.m_ulFlags=SDK_ZOOM;assert(BotCecilFinalBodyYaw(&p,8)==32);
 assert(std::isnan(BotCecilFinalBodyYaw(nullptr,8)));
 p.m_penWeapons=nullptr;assert(std::isnan(BotCecilFinalBodyYaw(&p,8)));p.m_penWeapons=&w;
 const float invalid[]={0,-1,NAN,INFINITY};
 for(float bad:invalid){w.m_fSniperFOV=bad;assert(std::isnan(BotCecilFinalBodyYaw(&p,8)));}
 w.m_fSniperFOV=20;
 for(float bad:invalid){w.m_fSniperMaxFOV=bad;assert(std::isnan(BotCecilFinalBodyYaw(&p,8)));}
 w.m_fSniperMaxFOV=80;p.m_ulFlags=0;w.m_fSniperFOV=NAN;w.m_fSniperMaxFOV=0;
 assert(BotCecilFinalBodyYaw(&p,8)==38);
 p.m_penWeapons=nullptr;assert(BotCecilFinalBodyYaw(&p,8)==38);
 for(float bad:{NAN,INFINITY,-INFINITY}){
  assert(std::isnan(BotCecilFinalBodyYaw(&p,bad)));
  p.en_plViewpoint.pl_OrientationAngle(1)=bad;assert(std::isnan(BotCecilFinalBodyYaw(&p,8)));
  p.en_plViewpoint.pl_OrientationAngle(1)=30;
  for(int group=0;group<3;++group)for(int axis=1;axis<=3;++axis){
   CPlayerAction a;assert(BotCecilActionFinite(a));
   FLOAT3D* vectors[]={&a.pa_vTranslation,&a.pa_aRotation,&a.pa_aViewRotation};
   (*vectors[group])(axis)=bad;assert(!BotCecilActionFinite(a));
  }
 }
}
'''
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--driver",type=Path,default=Path(__file__).with_name("BotDriver.cpp"))
    p.add_argument("--sdk-player",type=Path,required=True)
    a=p.parse_args();sdk=a.sdk_player.read_bytes();source=a.driver.read_text()
    flag=re.search(rb"^#define\s+PLF_ISZOOMING\s+\(1UL\s*<<\s*(\d+)\)",sdk,re.M)
    if not flag: raise ValueError("SDK zoom flag missing")
    bodies="\n".join(function(source,n) for n in ("BotCecilFinalBodyYaw","BotCecilActionFinite"))
    with tempfile.TemporaryDirectory(prefix="cecil-action-contract-") as tmp:
        cpp=Path(tmp)/"test.cpp";exe=Path(tmp)/"test"
        cpp.write_text("#include <initializer_list>\n#define SDK_ZOOM "+str(1<<int(flag[1]))+"\n"+STUB+bodies+TEST)
        subprocess.run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-I",str(a.driver.parent),str(cpp),"-o",str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
    print("PASS actual Driver action guards; SDK SHA256",hashlib.sha256(sdk).hexdigest())
    print("Driver SHA256",hashlib.sha256(source.encode()).hexdigest())
if __name__=="__main__":main()
