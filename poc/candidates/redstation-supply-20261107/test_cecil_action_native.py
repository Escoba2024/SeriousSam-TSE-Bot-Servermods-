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
const BOOL TRUE=1;
struct FLOAT3D {float v[3];FLOAT3D(float x=0,float y=0,float z=0):v{x,y,z}{}float& operator()(int i){return v[i-1];}
 float operator()(int i)const{return v[i-1];}};
struct CPlacement3D {FLOAT3D pl_OrientationAngle;};
struct CPlayerWeapons {float m_fSniperFOV=20,m_fSniperMaxFOV=80;};
struct CPlayer {unsigned m_ulFlags=0;CPlayerWeapons* m_penWeapons=nullptr;
 CPlayerWeapons* GetPlayerWeapons(){return m_penWeapons;}CPlacement3D en_plViewpoint;};
struct CPlayerAction {FLOAT3D pa_vTranslation,pa_aRotation,pa_aViewRotation;unsigned pa_ulButtons=0;
 void Clear(){*this=CPlayerAction();}};
struct CPlayerSource {CPlayerAction pls_paAction;int pls_csAction=0,writes=0;
 void SetAction(const CPlayerAction& action){pls_paAction=action;++writes;}};
struct CTSingleLock {CTSingleLock(int*,BOOL){}};
void BotLog(const char*,...){}
struct State {int bs_iTick=20;};
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
    if "static void BotCecilNeutralAction(" in source:
        bodies+="\n"+function(source,"BotCecilNeutralAction")
    guards=[]
    for reason in ("rotation_state","nonfinite_input","nonfinite"):
        guard=re.search(r'if\(![^\n]+\)\{\s*BotLog\("\[CecilInvalidAction\][^\n]*rejected='+reason+r'\\n"[^\n]*\n[\s\S]*?continue;\s*\}',source)
        if not guard:raise ValueError("rejection path missing: "+reason)
        condition=guard[0]
        guards.append("""
 { CPlayerSource src;CPlayerSource* ppls=&src;State bs;int iLP=0;bool bActed=false;
   src.pls_paAction.pa_ulButtons=1;src.pls_paAction.pa_vTranslation(3)=-1;
   src.pls_paAction.pa_aRotation(1)=37;src.pls_paAction.pa_aViewRotation(2)=12;
   for(int once=0;once<1;++once){CPlayerAction pa;pa.pa_aRotation(1)=NAN;double finalYaw=NAN;
   (void)finalYaw;(void)ppls;"""+condition+"""}
   assert(src.writes==1);assert(BotCecilActionFinite(src.pls_paAction));
   assert(src.pls_paAction.pa_ulButtons==0);
   for(int axis=1;axis<=3;++axis)assert(src.pls_paAction.pa_vTranslation(axis)==0);
   assert(src.pls_paAction.pa_aRotation(1)==37);assert(src.pls_paAction.pa_aViewRotation(2)==12);
   (void)bActed;
 }
""")
    if "static void BotCecilNeutralAction(" in source:
        guards.append("""
 { CPlayerSource src;src.pls_paAction.pa_ulButtons=0xffffffffu;
   src.pls_paAction.pa_vTranslation(1)=INFINITY;
   src.pls_paAction.pa_aRotation(2)=NAN;
   BotCecilNeutralAction(&src);
   assert(src.writes==1&&BotCecilActionFinite(src.pls_paAction));
   assert(src.pls_paAction.pa_ulButtons==0);
   for(int axis=1;axis<=3;++axis)assert(src.pls_paAction.pa_vTranslation(axis)==0);
 }
""")
    rejection="static void rejection_paths(){\n"+"\n".join(guards)+"\n}\n"
    # Compile the actual Driver ownership condition. Neutral route ownership
    # must suppress no-target wandering while preserving visible combat policy.
    choice=re.search(r'if\((ready&&[\s\S]*?)\)\{\s*bs\.bs_aHeading=player->m_aLastRotation',source)
    if not choice:raise ValueError("native supply arbitration missing")
    native_move=re.search(r'struct SCecilMove\s*\{[\s\S]*?\n\};',(a.driver.parent/'BotSupplyNative.h').read_text())
    if not native_move:raise ValueError("native move structure missing")
    ownership=native_move[0]+"\nstatic bool selected(bool ready,const SCecilMove& supply,CPlayer* player,bool targetVisible,double humanTargetDistance){return "+choice[1]+";}\n"+r'''
static void ownership_paths(){
 CPlayer player;CPlayerWeapons weapon;player.m_penWeapons=&weapon;SCecilMove s;
 s.ownsMovement=true;
 assert(selected(true,s,&player,false,1000));
 assert(!selected(true,s,&player,true,5));
 assert(!selected(true,s,&player,true,50));
 assert(!selected(false,s,&player,false,1000));
 assert(!selected(true,s,nullptr,false,1000));
 s.itemGoal=true;s.urgent=true;assert(selected(true,s,&player,true,5));
 s.urgent=false;assert(!selected(true,s,&player,true,5));
 assert(selected(true,s,&player,true,50));
 s=SCecilMove();assert(!selected(true,s,&player,false,1000));
 s.active=true;assert(selected(true,s,&player,false,1000));
 player.m_penWeapons=nullptr;assert(!selected(true,s,&player,false,1000));
}
'''
    test=TEST.replace("int main(){","int main(){rejection_paths();ownership_paths();")
    with tempfile.TemporaryDirectory(prefix="cecil-action-contract-") as tmp:
        cpp=Path(tmp)/"test.cpp";exe=Path(tmp)/"test"
        cpp.write_text('#include <initializer_list>\n#include "cecil_rules.h"\n#define SDK_ZOOM '+str(1<<int(flag[1]))+"\n"+STUB+bodies+rejection+ownership+test)
        subprocess.run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-I",str(a.driver.parent),str(cpp),"-o",str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
    print("PASS actual Driver action guards; SDK SHA256",hashlib.sha256(sdk).hexdigest())
    print("Driver SHA256",hashlib.sha256(source.encode()).hexdigest())
if __name__=="__main__":main()
