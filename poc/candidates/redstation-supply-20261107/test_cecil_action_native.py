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
const BOOL TRUE=1,FALSE=0;
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
struct SafetyState {};
SafetyState& BotSupplyState(INDEX){static SafetyState state;return state;}
static bool safetyRecovery=true;
template<class T>int BotCecilSafeMotion(CPlayer*,SafetyState&,double,T&,T&,T&,double,double,bool recovery=true){
 safetyRecovery=recovery;return 17;
}
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
    native_source=(a.driver.parent/'BotSupplyNative.h').read_text()
    bodies+="\n"+function(native_source,"BotCecilUrgentItem")
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
    native_move=re.search(r'struct SCecilMove\s*\{[\s\S]*?\n\};',native_source)
    if not native_move:raise ValueError("native move structure missing")
    ownership=native_move[0]+"\nstatic bool selected(bool ready,const SCecilMove& supply,CPlayer* player,bool targetVisible,double humanTargetDistance){(void)humanTargetDistance;return "+choice[1]+";}\n"+r'''
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
 // A reachable but nonurgent pickup must not cancel a valid ranged fight.
 assert(!selected(true,s,&player,true,50));
 // Urgent health/ammo/first ranged weapon still owns the route after respawn.
 s.urgent=true;assert(selected(true,s,&player,true,50));
 s.urgent=false;s.useControl=true;assert(selected(true,s,&player,true,50));
 s=SCecilMove();assert(!selected(true,s,&player,false,1000));
 s.active=true;assert(selected(true,s,&player,false,1000));
 player.m_penWeapons=nullptr;assert(!selected(true,s,&player,false,1000));
}
static void acquisition_combat_paths(){
 using namespace botcore;
 // Compose actual policy + actual typed urgency + actual Driver ownership.
 // Route reachability itself remains the native-bridge suite's responsibility.
 for(int tier=1;tier<=3;++tier)for(double distance:{10.,30.}){
  BotProfile profile;assert(BuildRosterProfile(0,0,123,&profile,tier));
  HumanBotPolicy policy;auto settings=CecilPreset(2);policy.Configure(&profile,&settings);
  WorldView world;world.cecil=true;world.alive=true;world.health=100;
  world.current_weapon=3;world.usable_weapons=CecilWeaponMask(1)|CecilWeaponMask(3);
  SenseInput enemy;enemy.index=1;enemy.entity_id=1;enemy.alive=true;enemy.health=100;enemy.z=-distance;
  bool los=true;BotCommand command;
  for(int tick=0;tick<10;++tick){world.tick=tick;policy.BeginTick(world);command=policy.Step(world,&enemy,&los,1,.05);}
  assert(command.target_visible==(distance<=18));
  CPlayer player;CPlayerWeapons weapons;player.m_penWeapons=&weapons;
  CecilItem item;item.kind=CecilItemKind::Weapon;item.weapon=6;
  CecilItemInput input;input.enemy_distance=distance;input.owned=input.usable=world.usable_weapons;
  SCecilMove supply;supply.active=true;supply.ownsMovement=true;supply.itemGoal=true;
  supply.urgent=BotCecilUrgentItem(item,input);assert(supply.urgent);
  assert(selected(true,supply,&player,command.target_visible,distance));
  // Normal pickup: an owned, usable gun enables ranged combat, so an ordinary
  // subsequent pickup no longer discards its aim/fire. No entity state writes.
  input.owned=input.usable=world.usable_weapons|CecilWeaponMask(6);
  world.usable_weapons=input.usable;world.current_weapon=6;
  for(int tick=10;tick<20;++tick){world.tick=tick;policy.BeginTick(world);command=policy.Step(world,&enemy,&los,1,.05);}
  assert(command.target_visible&&command.weapon==6);
  supply.urgent=BotCecilUrgentItem(item,input);assert(!supply.urgent);
  assert(!selected(true,supply,&player,command.target_visible,distance));
 }
}
'''
    final_call=re.search(r'cecilFloorStatus\s*=\s*BotCecilSafeMotion\([^;]+;',source)
    if not final_call:raise ValueError("native final safety call missing")
    # Compile the actual final call. Its default argument deliberately models
    # existing callers so omission of final movement ownership is a behavioral RED.
    safety=r'''
static void safety_owner_paths(){
 CPlayer actual;CPlayer* player=&actual;int iLP=0,cecilFloorStatus=0;
 double now=0,finalYaw=0,maxStrafe=1;FLOAT moveFactor=.64f,humanStrafe=0,cecilUp=0;
 for(BOOL supplyActive:{FALSE,TRUE}){
 '''+final_call[0]+r'''
 assert(cecilFloorStatus==17);assert(safetyRecovery==(supplyActive!=FALSE));
 }
}
'''
    test=TEST.replace("int main(){","int main(){rejection_paths();ownership_paths();acquisition_combat_paths();safety_owner_paths();")
    with tempfile.TemporaryDirectory(prefix="cecil-action-contract-") as tmp:
        cpp=Path(tmp)/"test.cpp";exe=Path(tmp)/"test"
        cpp.write_text('#include <initializer_list>\n#include "bot_human.h"\n#define SDK_ZOOM '+str(1<<int(flag[1]))+"\n"+STUB+bodies+rejection+ownership+safety+test)
        subprocess.run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-I",str(a.driver.parent),str(cpp),"-o",str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
    print("PASS actual Driver action guards; SDK SHA256",hashlib.sha256(sdk).hexdigest())
    print("Driver SHA256",hashlib.sha256(source.encode()).hexdigest())
if __name__=="__main__":main()
