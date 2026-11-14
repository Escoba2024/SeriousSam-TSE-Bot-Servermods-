#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute the real Driver observer against SDK-shaped read-only snapshots.
No game, runtime memory, hook, Windows ABI or qualification claim.
"""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile

STUB = r'''
#include <cstdio>
#include <cstdarg>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <limits>
#include "bot_weapon_input.h"
using INDEX=int;using ULONG=unsigned long;using FLOAT=float;
static int calls=0,clockCalls=0,failures=0,checks=0;static bool actionWritten=false;static std::vector<bool> actionOrders;static std::vector<std::string> logs;
__attribute__((format(printf,1,2))) static void BotLog(const char* f,...){char b[2048];va_list a;va_start(a,f);vsnprintf(b,sizeof b,f,a);va_end(a);logs.emplace_back(b);actionOrders.push_back(actionWritten);}
struct CWorld{};struct CEntity{unsigned en_ulID=9,flags=0;CWorld* world=nullptr;unsigned GetFlags()const{return flags;}CWorld* GetWorld()const{return world;}};
const unsigned ENF_DELETED=1;
struct CAnimData{int ad_NumberOfAnims=4;void* ad_Anims=(void*)1;};
struct CModelObject{CAnimData* ao_AnimData=nullptr;int ao_iCurrentAnim=0;float ao_tmAnimStart=0;unsigned ao_ulFlags=0;float GetAnimLength(int i)const{++calls;if(!ao_AnimData||!ao_AnimData->ad_Anims||i<0||i>=ao_AnimData->ad_NumberOfAnims){++failures;return NAN;}return float(i+1)*.25f;}};
struct Stack{int sa_Count=16;long* sa_Array=nullptr;int sa_UsedCount=0;};
struct CPlayerWeapons:CEntity{CEntity* m_penPlayer=nullptr;int m_iCurrentWeapon=2,m_iWantedWeapon=2,m_iPreviousWeapon=1,m_iAvailableWeapons=0x3fff,m_bChangeWeapon=0,m_iAnim=0;float en_timeTimer=-1;Stack en_stslStateStack;CModelObject m_moWeapon,m_moWeaponSecond;};
struct CPlayer:CEntity{float health=100;CPlayerWeapons* m_penWeapons=nullptr;unsigned m_ulLastButtons=0;float GetHealth()const{return health;}CPlayerWeapons* GetPlayerWeapons(){return m_penWeapons;}};
struct CPlayerAction{unsigned pa_ulButtons=0;};struct CPlayerSource{unsigned last=0;int writes=0;void SetAction(const CPlayerAction& a){last=a.pa_ulButtons;++writes;actionWritten=true;}};
struct ObservationSupply{unsigned generation=5;};static ObservationSupply supply;static ObservationSupply& BotSupplyState(int){return supply;}
struct ObservationSettings{double fWeaponCD=3;};static ObservationSettings settings;static ObservationSettings& BotCecilSettings(){return settings;}
struct Network{float time=1;float GetGameTime(){++clockCalls;return time;}};static Network net;static Network* _pNetwork=&net;
static void check(bool p,const char* n){++checks;if(!p){++failures;std::printf("FAIL %s\n",n);}}
static bool has(const char* s){for(const auto& l:logs)if(l.find(s)!=std::string::npos)return true;return false;}
#define max(a,b) WINDOWS_MAX_MUST_NOT_EXPAND
'''
BASELINE = r'''
static void BotWeaponObserverReset(int){}
static void BotWeaponObserverAfterAction(CPlayer*,CPlayerSource*,int,int,unsigned,int,unsigned,unsigned,bool,double){}
'''
TESTS = r'''
int main(){
 (void)&BotLog;(void)_pNetwork;BotWeaponObserverReset(0);
 CWorld world;CPlayer p;CPlayerWeapons w;CPlayerSource owner;CAnimData data;long states[16]={0x019200c9};
 p.world=w.world=&world;p.m_penWeapons=&w;w.m_penPlayer=&p;w.en_stslStateStack.sa_Array=states;w.en_stslStateStack.sa_UsedCount=1;w.m_moWeapon.ao_AnimData=w.m_moWeaponSecond.ao_AnimData=&data;
 auto frame=[&](int tick,int wanted,unsigned final=0,unsigned pulse=0,bool enabled=true){net.time=1+tick*.05f;const int before=calls;const auto eventCount=logs.size();BotWeaponObserverAfterAction(&p,&owner,0,tick,5,wanted,final,pulse,enabled,3.0);check(calls-before<=2&&logs.size()-eventCount<=1,"one event and at most two native length calls per slot/tick");};
 frame(1,2);logs.clear();
 frame(2,8,5u<<14,5u<<14);
 check(has("desired=8")&&has("pulse=81920")&&has("final=81920"),"actual new choice and accepted group pulse observed");
 w.m_iWantedWeapon=8;w.m_bChangeWeapon=0;states[0]=0x01920008;states[1]=0x01920014;w.en_stslStateStack.sa_UsedCount=2;w.en_timeTimer=1.6f;w.m_moWeapon.ao_tmAnimStart=1.15f;frame(3,8);logs.clear();
 w.m_iCurrentWeapon=8;states[1]=0x0192001b;w.m_moWeapon.ao_iCurrentAnim=1;w.m_moWeapon.ao_tmAnimStart=1.2f;frame(4,8);
 check(!has("completed=1"),"early current==wanted and change=false is not BringUp completion");logs.clear();
 states[0]=0x0192001d;w.en_stslStateStack.sa_UsedCount=1;frame(5,8);
 check(has("completed=1")&&has("saw_phase=1"),"entire native switch family exits before readiness is reported");
 check(calls<=10,"at most two model-length calls per emitted transition");
 int base=100;
 auto fresh=[&](){BotWeaponObserverReset(0);logs.clear();calls=0;w.flags=p.flags=0;p.health=100;p.m_penWeapons=&w;w.m_penPlayer=&p;w.world=p.world=&world;w.en_stslStateStack={16,states,1};states[0]=0x019200c9;w.m_iCurrentWeapon=w.m_iWantedWeapon=2;w.m_iPreviousWeapon=1;w.m_moWeapon=w.m_moWeaponSecond=CModelObject();w.m_moWeapon.ao_AnimData=w.m_moWeaponSecond.ao_AnimData=&data;base+=100;frame(base,2);logs.clear();calls=0;};
 auto start=[&](bool final=true){frame(base+1,8,final?5u<<14:0,5u<<14);w.m_iWantedWeapon=8;states[0]=0x01920008;states[1]=0x0192001b;w.en_stslStateStack.sa_UsedCount=2;frame(base+2,8);};
 auto finish=[&](){w.m_iCurrentWeapon=8;states[0]=0x0192001d;w.en_stslStateStack.sa_UsedCount=1;logs.clear();frame(base+3,8);};
 fresh();start(false);finish();check(!has("completed=1"),"Poll pulse rejected by final action cannot complete a transmitted chain");
 fresh();start();w.m_moWeapon.ao_iCurrentAnim=-1;logs.clear();const int oldCalls=calls;frame(base+3,8);check(has("censored=1")&&calls-oldCalls<=1,"negative primary animation censors without calling invalid native API");
 fresh();start();w.m_iPreviousWeapon=3;w.m_moWeaponSecond.ao_AnimData=nullptr;logs.clear();frame(base+3,8);check(has("censored=1"),"DoubleColt transition requires second model evidence");
 fresh();start();w.en_stslStateStack.sa_UsedCount=17;logs.clear();frame(base+3,8);check(has("valid=0")&&has("censored=1"),"deeper than bounded stack is OPEN rather than partial family absence");
 fresh();start();w.m_penPlayer=nullptr;logs.clear();frame(base+3,8);check(has("valid=0")&&has("censored=1"),"foreign or missing native owner cancels chain");
 fresh();start();w.flags=ENF_DELETED;logs.clear();frame(base+3,8);check(has("valid=0")&&has("censored=1"),"deleted weapons are not observed as a ready weapon");
 fresh();start();p.health=0;logs.clear();frame(base+3,8);check(has("valid=0")&&has("censored=1"),"death cancels same-life switch chain");
 fresh();start();logs.clear();frame(base+3,8,0,0,false);check(has("censored=1"),"owner disable cancels chain");
 fresh();start();logs.clear();frame(base+4,8);check(has("censored=1"),"missing action frame censors native animation interval");
 fresh();start();logs.clear();net.time=-1;BotWeaponObserverAfterAction(&p,&owner,0,base+3,5,8,0,0,true,3);check(has("censored=1"),"native simulation clock rewind censors interval");
 fresh();start();logs.clear();net.time=1+(base+3)*.05f;BotWeaponObserverAfterAction(&p,&owner,0,base+3,6,8,0,0,true,3);check(has("censored=1"),"generation changes cannot finish old chain");
 fresh();start();logs.clear();net.time=1+(base+3)*.05f;BotWeaponObserverAfterAction(&p,&owner,0,base+3,5,8,0,0,true,5);check(has("censored=1"),"configured cooldown change cancels old timing context");
 fresh();start();finish();logs.clear();calls=0;
 for(int n=4;n<50;++n){w.m_moWeapon.ao_tmAnimStart+=.05f;states[0]=0x0192001d+(n&1);frame(base+n,8);}
 check(logs.empty()&&calls==0,"attack animation restarts outside measured chain do not log or call animation API");
 fresh();start();logs.clear();frame(base+2,8);check(logs.empty(),"duplicate slot/tick cannot emit second observation");logs.clear();frame(base+3,8);check(has("dropped=1")&&!has("completed=1"),"dropped event is explicit OPEN on next emitted record");
 fresh();w.en_stslStateStack.sa_UsedCount=0;w.en_stslStateStack.sa_Array=nullptr;frame(base+1,2);check(!has("completed=1"),"empty stack does not independently prove switch animation completion");
 fresh();start();w.m_moWeapon.ao_iCurrentAnim=data.ad_NumberOfAnims;logs.clear();const int previous=calls;frame(base+3,8);check(has("censored=1")&&calls-previous<=1,"high animation index never reaches unchecked native method");
 fresh();start();w.m_penPlayer=nullptr;frame(base+3,8);logs.clear();frame(base+4,8);check(logs.empty(),"unchanged invalid owner does not produce unbounded per-frame event logs");
 fresh();start();w.m_iCurrentWeapon=8;w.en_stslStateStack.sa_UsedCount=1;states[0]=0x0192001d;w.m_moWeapon.ao_AnimData=nullptr;logs.clear();frame(base+3,8);check(!has("completed=1")&&has("censored=1"),"missing model on phase exit is conservative OPEN");
 fresh();frame(base+1,8,5u<<14,5u<<14);w.m_iCurrentWeapon=w.m_iWantedWeapon=8;states[0]=0x0192001d;logs.clear();frame(base+2,8);check(has("censored=1")&&!has("completed=1"),"unobserved or skipped native family is OPEN and terminates chain");logs.clear();calls=0;for(int n=3;n<30;++n){w.m_moWeapon.ao_tmAnimStart+=.05f;frame(base+n,8);}check(logs.empty()&&calls==0,"missing-phase chain cannot log all later attack animations forever");
 fresh();start();w.m_iWantedWeapon=9;frame(base+3,8);w.m_iWantedWeapon=w.m_iCurrentWeapon=8;states[0]=0x0192001d;w.en_stslStateStack.sa_UsedCount=1;logs.clear();frame(base+4,8);
 check(!has("completed=1"),"REVIEW native wanted changes away from acknowledged target censors chain even if later restored");
 fresh();start();w.m_iCurrentWeapon=8;states[0]=0x0192001d;w.en_stslStateStack.sa_UsedCount=1;w.m_moWeapon.ao_AnimData=nullptr;frame(base+3,8);w.m_moWeapon.ao_AnimData=&data;logs.clear();calls=0;
 for(int n=4;n<15;++n){w.m_moWeapon.ao_tmAnimStart+=.05f;frame(base+n,8);}
 check(logs.empty()&&calls==0,"REVIEW censored missing-model family exit must terminate before later unrelated attack animation restarts");
 fresh();start();++w.en_ulID;w.m_iCurrentWeapon=8;states[0]=0x0192001d;w.en_stslStateStack.sa_UsedCount=1;logs.clear();frame(base+3,8);
 check(has("censored=1")&&!has("completed=1"),"REVIEW changed native weapon entity identity cannot complete old instance chain at same address");

 fresh();start();data.ad_Anims=nullptr;logs.clear();const int nullCalls=calls;frame(base+3,8);check(has("censored=1")&&calls==nullCalls,"positive animation count with null record array never calls native length API");data.ad_Anims=(void*)1;
 for(int ending=0;ending<2;++ending){fresh();start();w.m_iCurrentWeapon=8;w.en_stslStateStack.sa_UsedCount=ending?1:0;states[0]=0x12345678;logs.clear();frame(base+3,8);check(has("censored=1")&&!has("completed=1"),"empty or unknown native exit state cannot corroborate BringUp completion");}
 fresh();const int rateBase=base;logs.clear();for(int n=1;n<=100;++n){net.time=10000;BotWeaponObserverAfterAction(&p,&owner,0,rateBase+n,5,(n&1)?8:9,0,0,true,3);}
 check(logs.size()<=40,"at most forty events per native second even with paused clock and increasing action ticks");logs.clear();net.time=10001;BotWeaponObserverAfterAction(&p,&owner,0,rateBase+101,5,8,0,0,true,3);check(has("dropped=")&&has("censored=1")&&!has("dropped=0"),"rate-limit drops are explicit OPEN on next window");
 fresh();BotWeaponObserverReset(0);++p.en_ulID;logs.clear();frame(base,2);check(logs.size()==1&&!has("dropped=1"),"fresh lifecycle first tick may equal previous life tick without losing baseline");

 fresh();start();w.m_iWantedWeapon=w.m_iCurrentWeapon=9;states[0]=0x0192001d;w.en_stslStateStack.sa_UsedCount=1;frame(base+3,8);logs.clear();calls=0;for(int n=4;n<20;++n){w.m_moWeapon.ao_tmAnimStart+=.05f;frame(base+n,8);}check(logs.empty()&&calls==0,"acknowledged native target loss terminates censored chain even if it never returns");
 fresh();logs.clear();for(int n=1;n<=100;++n){net.time=(n&1)?20000:19999;BotWeaponObserverAfterAction(&p,&owner,0,base+n,5,(n&1)?8:9,0,0,true,3);}check(logs.size()<=40,"clock rewinds cannot refill a native-second event budget");

 fresh();unsigned char beforeW[sizeof w],beforeP[sizeof p];std::memcpy(beforeW,&w,sizeof w);std::memcpy(beforeP,&p,sizeof p);frame(base+1,8,5u<<14,5u<<14);check(std::memcmp(beforeW,&w,sizeof w)==0&&std::memcmp(beforeP,&p,sizeof p)==0,"observer mutates no native player/weapon/model/state snapshot bytes");
 fresh();start();w.en_timeTimer=NAN;logs.clear();const int timerCalls=calls;frame(base+3,8);check(has("valid=0")&&calls==timerCalls,"nonfinite native timer cancels without animation API calls");w.en_timeTimer=-1;
 fresh();start();w.m_moWeapon.ao_tmAnimStart=NAN;logs.clear();const int animCalls=calls;frame(base+3,8);check(has("censored=1")&&calls-animCalls<=1,"nonfinite animation start never reaches native API");
 fresh();CWorld replacement;start();p.world=w.world=&replacement;logs.clear();frame(base+3,8);check(has("censored=1")&&!has("completed=1"),"new world epoch cancels old native interval");
 fresh();start();CPlayerSource replacementOwner;logs.clear();net.time=1+(base+3)*.05f;BotWeaponObserverAfterAction(&p,&replacementOwner,0,base+3,5,8,0,0,true,3);check(has("censored=1"),"new accepted source ownership cancels old interval");
 fresh();net.time=1+(base+1)*.05f;actionWritten=false;actionOrders.clear();CPlayerSource emitted;driverAfterAction(&p,&emitted,base+1,8,5u<<14,5u<<14);check(emitted.writes==1&&emitted.last==(5u<<14)&&!actionOrders.empty()&&actionOrders.back()&&has("final=81920"),"real Driver hook observes exact packet only after its SetAction call");
 fresh();w.m_iWantedWeapon=8;states[0]=0x01920008;frame(base+1,2);frame(base+2,8,5u<<14,5u<<14);w.m_iCurrentWeapon=8;states[0]=0x0192001d;logs.clear();frame(base+3,8);
 check(!has("completed=1"),"REVIEW choice and pulse starting after acknowledged family was already active is left-censored");

 fresh();frame(base+1,8,0,5u<<14);logs.clear();calls=0;for(int n=2;n<30;++n){states[0]=0x0192001d+(n&1);w.m_moWeapon.ao_tmAnimStart+=.05f;frame(base+n,8);}check(logs.empty()&&calls==0,"old gun attack animation while awaiting first native switch is not switch telemetry");
 std::printf("checks=%d failures=%d\n",checks,failures);return failures?1:0;
}
'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--driver',type=Path,default=Path(__file__).with_name('BotDriver.cpp'));ap.add_argument('--sanitize',action='store_true');args=ap.parse_args()
    source=args.driver.read_text(encoding='latin1')
    start='// BEGIN CECIL WEAPON OBSERVER';end='// END CECIL WEAPON OBSERVER'
    # The unchanged Driver has no observation hook: its actual baseline emits
    # no observer events. This no-op supplies only the absent function boundary.
    block=source.split(start,1)[1].split(end,1)[0]if start in source else BASELINE
    after_action=source.split('    ppls->SetAction(pa);',1)[1].split('    // Count emitted combat',1)[0]
    calls=re.findall(r'BotWeaponObserverAfterAction\([^;]+;',after_action)
    if len(calls)!=1:raise ValueError('exactly one actual observer call required after SetAction')
    hook='ppls->SetAction(pa);'+calls[0]
    integration='static void driverAfterAction(CPlayer* player,CPlayerSource* ppls,int tick,int desired,unsigned final,unsigned pulse){struct {int bs_iTick;}bs={tick};const int iLP=0;const int combatWeapon=desired;const unsigned combatSelect=pulse;const bool automatic=true,bot_bSupplyNavigation=true;CPlayerAction pa;pa.pa_ulButtons=final;'+hook+'}'
    with tempfile.TemporaryDirectory(prefix='cecil-weapon-observer-')as d:
        path=Path(d)/'test.cpp';path.write_text(STUB+'\n'+block+'\n'+integration+'\n'+TESTS);exe=Path(d)/'test'
        flags=['-I'+str(args.driver.parent),'-std=c++17','-Wall','-Wextra','-Werror','-O1','-g']
        if args.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
        subprocess.run(['g++',*flags,str(path),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
if __name__=='__main__':main()
