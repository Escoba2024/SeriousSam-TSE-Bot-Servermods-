"""Compile extracted real Driver branches; SDK-shaped stubs are not Retail proof."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
CAND=ROOT/'poc/candidates/redstation-supply-20261107'

def extract(source,start,end):
    assert source.count(start)==1,start
    return source[source.index(start):source.index(end,source.index(start))]

class DriverWiringTests(unittest.TestCase):
    def test_four_review_facts_have_actual_driver_bindings(self):
        source=(CAND/'BotDriver.cpp').read_text()
        for name,needle in [
            ('actual Poll last buttons','finalDecision.pollLastButtons,player->m_ulLastButtons'),
            ('actual arbitration flags','finalDecision.arbitrationFlags=cecilFlags'),
            ('preSupply decision point','finalDecision.preSupplyModeBits='),
            ('cached target index','finalDecision.cachedTargetIndex=automatic?bs.bs_iCombatTarget:bot_iTestTarget'),
        ]:
            with self.subTest(name=name):self.assertTrue(needle in source,'missing '+name)

    def test_actual_arbitration_poll_safety_and_submit(self):
        source=(CAND/'BotDriver.cpp').read_text()
        self.assertTrue('CecilDriverFinalBegin(finalDecision,' in source,'Driver capture not wired')
        pre=extract(source,'    if(finalDecision.admitted){\n      finalDecision.preSupplyModeBits=', '    if(bot_bSupplyNavigation&&automatic&&combatDeathmatch){')
        supply=extract(source,'    if(bot_bSupplyNavigation&&automatic&&combatDeathmatch){','    // Stateful native selection')
        weapon=extract(source,'    if(automatic&&player!=NULL&&player->m_penWeapons!=NULL){','    if (bot_bObstacleAvoidance')
        safety=extract(source,'        const double maxStrafe=', '\n      }\n    }\n\n    // 3) compose')
        fire=extract(source,'        if(finalDecision.admitted)finalDecision.firePolled=true;', '\n        if(cecilUseControl)')
        submit=extract(source,'    ppls->SetAction(pa);\n', '    if(aimTraceCaptured && player)')
        program=r'''
#include "driver_final_decision.h"
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
using FLOAT=float;using INDEX=int;using ULONG=uint32_t;using BOOL=bool;
const bool FALSE=false,TRUE=true;
template<class T>T Clamp(T x,T low,T high){return x<low?low:(x>high?high:x);}
namespace botcore {enum class CecilItemKind {Weapon,Health,Other};}
struct SCecilMove {bool active=false,ownsMovement=false,itemGoal=false,urgent=false,followGoal=false,useControl=false,flightGoal=false,activeFlight=false;
 botcore::CecilItemKind itemKind=botcore::CecilItemKind::Weapon;double forward=0,strafe=0,up=0,yaw_delta=0,pitch_delta=0;uint32_t flags=0,buttons=0;};
struct Vec {float a[3]={0,0,0};float& operator()(int i){return a[i-1];}float operator()(int i)const{return a[i-1];}};
struct Action {Vec pa_vTranslation,pa_aRotation,pa_aViewRotation;uint32_t pa_ulButtons=0;};
struct Weapons {int m_iWantedWeapon=6,m_iCurrentWeapon=5;};
struct Player {Weapons* m_penWeapons=nullptr;Vec m_aLastRotation;int getters=0;
 Weapons* GetPlayerWeapons(){++getters;return m_penWeapons;}};
struct WeaponInput {int polls=0,wanted=0,weapon=0;uint32_t last=0;unsigned Poll(int tick,int w,int want,uint32_t buttons){assert(tick==20);++polls;weapon=w;wanted=want;last=buttons;return 0x400;}};
struct Settings {bool bStrafe=true;};
struct FireInput {int polls=0,current=0,wanted=0,weapon=0;bool Poll(double,int c,int w,int target,bool,bool,bool,double,Settings){++polls;current=c;wanted=w;weapon=target;return true;}};
struct State {unsigned generation=3,entity=555;};State supplyState;
State& BotSupplyState(int){return supplyState;}
struct BS {int bs_iTick=20,bs_iCombatTarget=7;float bs_aHeading=11,bs_aPitch=12;double bs_lastSeen=0;WeaponInput bs_weaponInput;FireInput bs_cecilFire;};
int _botSupplyMapReady=1,readyReads=0,supplyCalls=0,resolveCalls=0,travelCalls=0,refCalls=0,safeCalls=0,combatCalls=0;
int InterlockedCompareExchange(int* v,int,int){++readyReads;return *v;}
SCecilMove offered;bool resetInside=false;
SCecilMove BotSupplyTick(Player*,int,int,double,void*){++supplyCalls;if(resetInside)++supplyState.generation;return offered;}
void BotCecilLogReferences(Player*){++refCalls;}
void BotLog(const char*,...){}
Settings BotCecilSettings(){return Settings();}
namespace botcore {bool CecilTravelKnife(double,double,bool nav,bool){++travelCalls;return nav;}
int ResolveSupplyWeapon(int w,bool travel){++resolveCalls;return travel?1:w;}}
bool BotCecilCombatRecoveryRequested(bool,bool,bool,bool nav,float,float,float){++combatCalls;return !nav;}
bool passedReacquire=false,passedCombat=false;
int BotCecilSafeMotion(Player*,State&,double,float& f,float& s,float& u,double,double,bool reacquire,bool combat){++safeCalls;passedReacquire=reacquire;passedCombat=combat;f=.25f;s=-.1f;u=0;return 17;}
struct Source {int writes=0;Action submitted;void SetAction(const Action& a){++writes;submitted=a;}};
double baseline[7][28];int ordinal[2]={0,0};
void run(bool diag,bool ready,bool visible,bool urgent,bool traversal,bool active,bool withWeapons,bool safe,bool reset){
 readyReads=supplyCalls=resolveCalls=travelCalls=refCalls=safeCalls=combatCalls=0;
 _botSupplyMapReady=ready;resetInside=reset;supplyState=State();offered=SCecilMove();
 offered.active=active;offered.ownsMovement=true;offered.itemGoal=true;offered.urgent=urgent;offered.flightGoal=traversal;
 offered.forward=.7;offered.strafe=.2;offered.up=0;offered.yaw_delta=7;offered.pitch_delta=-3;
 offered.flags=16;offered.buttons=32;
 BS bs;int iLP=2;Player p;Weapons w;p.m_ulLastButtons=0x8001;p.m_penWeapons=withWeapons?&w:nullptr;p.m_aLastRotation(1)=100;p.m_aLastRotation(2)=20;
 Player* player=&p;bool automatic=true,humanMode=true,combatDeathmatch=true,bot_bSupplyNavigation=true,targetVisible=visible;
 bool cecilUseControl=false,combatHold=true,testAimReady=true,humanFire=true,supplyActive=false;
 float moveFactor=.9,humanStrafe=-.4,cecilUp=0;uint32_t cecilButtons=0,cecilFlags=0,combatSelect=0;
 int combatWeapon=6,cecilFloorStatus=-1,bot_iTestTarget=9;double humanTargetDistance=50,fTick=.05;int navFollow=0;uint32_t entityId=555;
 uint32_t playerLastButtons=0; // wrapper Player field initialized below in actual snippets
 (void)playerLastButtons;
 botcore::CecilDriverFinal finalDecision;botcore::CecilDriverFinalBegin(finalDecision,diag,iLP,20,entityId,3,9);
''' + pre + supply + weapon + r'''
 if(safe){double now=1,finalYaw=90;float bot_fStrafeScale=.5;
''' + safety + r'''
 }
 bool bFire=false;Weapons* fw=&w;Weapons* unused=fw;(void)unused;
 if(withWeapons){Weapons* w=fw;double now=1;
''' + fire + r'''
 }
 Source src;Source* ppls=&src;Action pa;pa.pa_vTranslation(1)=humanStrafe;pa.pa_vTranslation(3)=-moveFactor;
 pa.pa_aRotation(1)=7;pa.pa_aViewRotation(2)=9;pa.pa_ulButtons=combatSelect|cecilButtons;
''' + submit + r'''
 bool expected=ready&&withWeapons&&(!visible||urgent||traversal);
 assert(supplyActive==expected&&readyReads==1&&supplyCalls==(int)ready&&refCalls==(int)ready);
 assert(bs.bs_weaponInput.polls==(int)withWeapons&&resolveCalls==(int)withWeapons&&travelCalls==(int)withWeapons);
 assert(p.getters==(int)withWeapons);
 if(withWeapons){assert(bs.bs_weaponInput.wanted==6&&bs.bs_weaponInput.weapon==(expected?1:6));
  assert(bs.bs_weaponInput.last==0x8001);
  assert(bs.bs_cecilFire.current==5&&bs.bs_cecilFire.wanted==6&&bs.bs_cecilFire.weapon==combatWeapon);}
 assert(src.writes==1);assert(safeCalls==(int)safe&&combatCalls==(int)safe);
 if(diag){assert(finalDecision.submitted&&finalDecision.supplyCalled==ready&&finalDecision.proposalValid==ready);
  assert(finalDecision.supplyBlockEntered&&finalDecision.ready==ready);
  assert(finalDecision.preSupplyModeBits==(231u+(visible?8:0))&&finalDecision.cachedTargetIndex==7);
  assert(finalDecision.arbitrationFlags==(expected?16u:0u));
  assert(finalDecision.SameLife()==!reset);assert(finalDecision.weaponsEvaluated==ready);
  if(ready)assert(finalDecision.weaponsPresent==withWeapons);
  assert(finalDecision.weaponPolled==withWeapons&&finalDecision.firePolled==withWeapons);
  if(withWeapons)assert(finalDecision.pollLastButtons==bs.bs_weaponInput.last);
  assert(finalDecision.safeCalled==safe);if(safe){assert(finalDecision.safeStatus==17&&finalDecision.safeAfter[0]==.25);
   assert(finalDecision.safeReacquire==passedReacquire&&finalDecision.safeCombat==passedCombat);}
  assert(finalDecision.translation[0]==pa.pa_vTranslation(1)&&finalDecision.rotation[0]==7&&finalDecision.view[1]==9);
  assert(finalDecision.buttons==src.submitted.pa_ulButtons);
 }else assert(!finalDecision.submitted&&!finalDecision.proposalValid&&!finalDecision.safeCalled);
 double values[]={double(supplyActive),bs.bs_aHeading,bs.bs_aPitch,moveFactor,humanStrafe,cecilUp,
  double(combatWeapon),double(combatSelect),double(cecilButtons),double(humanFire),double(testAimReady),
  pa.pa_vTranslation(1),pa.pa_vTranslation(2),pa.pa_vTranslation(3),pa.pa_aRotation(1),pa.pa_aRotation(2),pa.pa_aRotation(3),
  pa.pa_aViewRotation(1),pa.pa_aViewRotation(2),pa.pa_aViewRotation(3),double(pa.pa_ulButtons),
  double(readyReads),double(supplyCalls),double(resolveCalls),double(travelCalls),double(p.getters),double(safeCalls),double(combatCalls)};
 int row=ordinal[diag]++;assert(row<7);
 for(int i=0;i<28;++i){if(!diag)baseline[row][i]=values[i];else assert(baseline[row][i]==values[i]);}
 std::printf("case diag=%d ready=%d visible=%d urgent=%d traversal=%d weapon=%d safe=%d reset=%d grants=%d getters=%d\n",diag,ready,visible,urgent,traversal,withWeapons,safe,reset,expected,p.getters);
 (void)humanMode;(void)bFire;(void)cecilFlags;
}
int main(){for(int diag=0;diag<2;++diag){
 run(diag,1,1,0,0,1,1,1,0);run(diag,1,0,0,0,0,1,1,0);
 run(diag,1,1,1,0,1,1,1,0);run(diag,1,1,0,1,1,1,0,0);
 run(diag,0,1,0,0,1,1,0,0);run(diag,1,1,0,0,1,0,0,0);
 run(diag,1,0,0,0,1,1,1,1);
}}
'''
        # Minimal fields/settings needed by actual snippets, without editing those snippets.
        program=program.replace('struct Player {Weapons*', 'struct Player {uint32_t m_ulLastButtons=0;Weapons*')
        with tempfile.TemporaryDirectory(prefix='driver-wiring-')as tmp:
            p=Path(tmp);(p/'test.cpp').write_text(program)
            subprocess.run(['g++','-std=c++14','-Wall','-Wextra','-Werror','-I',str(CAND),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True)

if __name__=='__main__':unittest.main()
