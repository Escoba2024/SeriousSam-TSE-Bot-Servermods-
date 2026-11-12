#!/usr/bin/env python3
"""Run actual Driver attach/entity/compose statements against native-shaped state.

This is an offline regression for retired requested angles, not a Retail runtime
or first-action-order proof. No native player rotation field is reset by the SUT.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

from test_cecil_action_native import function


def balanced(source, marker):
    start = source.index(marker)
    brace = source.index('{', start)
    masked = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                    lambda m: ' ' * len(m[0]), source)
    depth = 1
    for end in range(brace + 1, len(masked)):
        depth += (masked[end] == '{') - (masked[end] == '}')
        if depth == 0:
            return source[start:end + 1]
    raise ValueError('unbalanced production block')


STUB = r'''
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdarg>
#include <cstring>
#include <limits>
#include <vector>
#include <string>
using FLOAT=float;using ANGLE=float;using ULONG=unsigned long;
using INDEX=int;using BOOL=int;using LONG=long;
const BOOL TRUE=1,FALSE=0;
struct Vec {FLOAT v[3]={0,0,0};Vec()=default;Vec(float x,float y,float z):v{x,y,z}{}
 FLOAT& operator()(int i){return v[i-1];}FLOAT operator()(int i)const{return v[i-1];}
 Vec& operator+=(const Vec& x){for(int i=0;i<3;++i)v[i]+=x.v[i];return *this;}};
using FLOAT3D=Vec;using ANGLE3D=Vec;
struct CPlacement3D {Vec pl_OrientationAngle;};
struct CWorld {};
struct CPlayer {ULONG en_ulID=1;Vec m_aLastRotation,m_aLocalRotation;FLOAT m_tmSpawned=0;
 CPlacement3D en_plViewpoint;CWorld* world=nullptr;CWorld* GetWorld()const{return world;}};
struct CPlayerAction {Vec pa_aRotation,pa_aViewRotation,pa_vTranslation;ULONG pa_ulButtons=0;
 void Clear(){*this=CPlayerAction();}};
struct CPlayerSource {CPlayerAction pls_paAction;};
static std::vector<std::string> logs;
static void BotLog(const char* format,...){char line[2048];va_list ap;va_start(ap,format);
 std::vsnprintf(line,sizeof(line),format,ap);va_end(ap);logs.emplace_back(line);}
static int RotationLogs(){int n=0;for(const auto& line:logs){
 if(line.rfind("[BotRotationBaseline]",0)==0)++n;}return n;}
namespace botcore {
struct Resettable {int resets=0;void Reset(){++resets;}};
using CombatWeaponInput=Resettable;using ObstacleRecovery=Resettable;using CecilFireState=Resettable;
struct BotProfile {const char* name="test";int tier=3,persona=0;uint32_t seed=1;};
struct HumanBotPolicy:Resettable {void Configure(const BotProfile*,const int*){Reset();}};
static bool BuildRosterProfile(int,int,uint32_t,BotProfile*,int){return true;}
static const char* PersonalityName(int){return "test";}
}
static int bot_bSupplyNavigation=1,bot_bDiagnostics=0;
static int bot_iRosterOffset=0,bot_iProfileSeed=1,bot_iArenaTier=3;
static int bot_iProfile0=0,bot_iProfile1=1,bot_iProfile2=2,bot_iProfile3=3;
static volatile LONG _botSupplyMapSerial=1;
static LONG InterlockedCompareExchange(volatile LONG* p,LONG,LONG){return *p;}
static int& BotCecilSettings(){static int settings=0;return settings;}
static void BotSupplyReset(INDEX){}
static void BotCecilNeutralAction(CPlayerSource* p){p->pls_paAction.pa_vTranslation=Vec();p->pls_paAction.pa_ulButtons=0;}
'''

TEST = r'''
static int checks=0,failures=0;
static void Check(bool condition,const char* name){++checks;if(!condition){++failures;std::fprintf(stderr,"FAIL %s\n",name);}}
static CWorld world;
static CPlayerSource sources[4];
static CPlayer player(ULONG id,float lastYaw,float lastPitch){CPlayer p;p.en_ulID=id;p.world=&world;
 p.m_aLastRotation=Vec(lastYaw,lastPitch,0);p.m_aLocalRotation=p.m_aLastRotation;return p;}
static void OldState(int slot,ULONG id,float yaw,float pitch){
 _absBots[slot]=SBotState();auto& b=_absBots[slot];b.bs_ppls=&sources[slot];b.bs_supplyEntity=id;
 b.bs_aHeading=yaw;b.bs_aPitch=pitch;b.bs_iTick=3554;b.bs_ulCombatFireActions=172;
}
int main(){
 // Exact prior-phase requested pitch, fresh native entity/source baseline.
 OldState(0,560,220,173.4698792f);CPlayer fresh=player(559,0,0);
 CPlayer predictor=fresh;BotHumanAttach(0);
 auto a=Step(0,&predictor,&fresh);
 Check(a.pa_aRotation(1)==0,"new-map yaw must use fresh native baseline");
 Check(a.pa_aRotation(2)==0,"new-map pitch must not inject retired 173-degree request");
 Check(predictor.m_aLastRotation(2)==0&&predictor.en_plViewpoint.pl_OrientationAngle(2)==0,
       "baseline adoption must not write native LastRotation or View");
 Check(fresh.m_aLocalRotation(2)==0,"composer receives neutral fresh-map pitch");
 Check(_absBots[0].bs_ulCombatFireActions==172,"diagnostic fire counter is not reset by angle adoption");
 // Same source, same entity ID/address, different map; attach must still rebase.
 _absBots[0].bs_aHeading=99;_absBots[0].bs_aPitch=173.4698792f;
 ++_botSupplyMapSerial;fresh.m_aLocalRotation=Vec();predictor.m_aLastRotation=Vec();
 BotHumanAttach(0);a=Step(0,&predictor,&fresh);
 Check(a.pa_aRotation(1)==0&&a.pa_aRotation(2)==0,"map boundary with reused source/id/address");
 // An ordinary same-entity respawn retains the native cumulative baseline.
 predictor.m_aLastRotation=Vec(41,173.4698792f,0);fresh.m_aLocalRotation=predictor.m_aLastRotation;
 predictor.en_plViewpoint.pl_OrientationAngle(2)=0;
 _absBots[0].bs_aHeading=41;_absBots[0].bs_aPitch=173.4698792f;
 a=Step(0,&predictor,&fresh);
 Check(a.pa_aRotation(2)==173.4698792f,"same-entity respawn must preserve nonzero cumulative pitch");
 Check(a.pa_aRotation(2)-predictor.m_aLastRotation(2)==0,"respawn emits zero native pitch delta");
 // Existing same-epoch decisions are not overwritten on every tick.
 _absBots[0].bs_aHeading=47;_absBots[0].bs_aPitch=174.25f;
 a=Step(0,&predictor,&fresh);
 Check(a.pa_aRotation(1)==47&&a.pa_aRotation(2)==174.25f,"ordinary requested angle remains unchanged");
 // Entity replacement without an Attach call adopts its actual nonzero baseline.
 CPlayer replacement=player(700,-35,21.25f);CPlayer replacementPredictor=replacement;
 a=Step(0,&replacementPredictor,&replacement);
 Check(a.pa_aRotation(1)==-35&&a.pa_aRotation(2)==21.25f,"entity replacement uses observed native baseline, not zero");
 // Native original and predicted entities may be distinct objects of one identity.
 Check(&replacement!=&replacementPredictor,"fixture includes distinct original/predicted objects");
 Check(replacementPredictor.m_aLastRotation(1)==-35&&replacementPredictor.m_aLastRotation(2)==21.25f,
       "predicted native last-rotation is read-only");
 // Every local bot is independent; adopting one slot cannot touch another.
 for(int slot=1;slot<4;++slot){OldState(slot,800+slot,100+slot,170+slot);BotHumanAttach(slot);}
 for(int slot=1;slot<4;++slot){
   CPlayer p=player(900+slot,slot*3.f,-slot*2.f);CPlayer pred=p;
   auto otherBefore=_absBots[(slot%3)+1].bs_aPitch;
   auto out=Step(slot,&pred,&p);
   Check(out.pa_aRotation(1)==slot*3.f&&out.pa_aRotation(2)==-slot*2.f,"per-slot native baseline");
   Check(_absBots[(slot%3)+1].bs_aPitch==otherBefore,"no cross-slot rotation write");
 }
 // A map serial is an independent boundary, even before a new Attach call.
 _absBots[0].bs_aHeading=71;_absBots[0].bs_aPitch=173;
 ++_botSupplyMapSerial;replacementPredictor.m_aLastRotation=Vec(3,-7,0);
 a=Step(0,&replacementPredictor,&replacement);
 Check(a.pa_aRotation(1)==3&&a.pa_aRotation(2)==-7,"map serial alone retires prior decisions");
 // A changed original input object is a boundary; a new predictor is not.
 CPlayer sameIdReplacement=player(700,-9,16);CPlayer sameIdPredictor=sameIdReplacement;
 _absBots[0].bs_aHeading=71;_absBots[0].bs_aPitch=173;
 a=Step(0,&sameIdPredictor,&sameIdReplacement);
 Check(a.pa_aRotation(1)==-9&&a.pa_aRotation(2)==16,"reused ID with different original allocation");
 CPlayer transientPredictor=sameIdPredictor;transientPredictor.m_aLastRotation=Vec(-8,15,0);
 _absBots[0].bs_aHeading=33;_absBots[0].bs_aPitch=17;
 a=Step(0,&transientPredictor,&sameIdReplacement);
 Check(a.pa_aRotation(1)==33&&a.pa_aRotation(2)==17,"transient predictor replacement retains current decision");
 Check(RotationLogs()==0,"disabled diagnostics emit no baseline records");
 // Rejection never marks a new basis accepted or changes native angle fields.
 auto Reject=[&](CPlayer* predicted,CPlayer* original,const char* name){
   BotHumanAttach(0);_absBots[0].bs_aHeading=80;_absBots[0].bs_aPitch=37;
   auto& prior=sources[0].pls_paAction;prior.pa_aRotation=Vec(12,13,0);
   prior.pa_vTranslation=Vec(5,6,7);prior.pa_ulButtons=1;
   Vec localBefore=original->m_aLocalRotation;
   Vec lastBefore=predicted?predicted->m_aLastRotation:Vec();
   Vec viewBefore=predicted?predicted->en_plViewpoint.pl_OrientationAngle:Vec();
   const int count=RotationLogs();auto out=Step(0,predicted,original);
   Check(out.pa_aRotation(1)==12&&out.pa_aRotation(2)==13&&out.pa_ulButtons==0&&
         out.pa_vTranslation(1)==0&&out.pa_vTranslation(2)==0&&out.pa_vTranslation(3)==0,name);
   Check(_absBots[0].bs_aHeading==80&&_absBots[0].bs_aPitch==37&&
         std::memcmp(&original->m_aLocalRotation,&localBefore,sizeof(Vec))==0&&
         (!predicted||(std::memcmp(&predicted->m_aLastRotation,&lastBefore,sizeof(Vec))==0&&
           std::memcmp(&predicted->en_plViewpoint.pl_OrientationAngle,&viewBefore,sizeof(Vec))==0)),name);
   Check(RotationLogs()==count,name);
 };
 CPlayer good=player(900,3,4);CPlayer bad=good;
 bad.en_ulID=901;Reject(&bad,&good,"mismatched identity rejected without native writes");
 CWorld wrongWorld;bad=good;bad.world=&wrongWorld;
 Reject(&bad,&good,"mismatched world rejected without native writes");
 bad=good;bad.world=nullptr;Reject(&bad,&good,"missing world rejected");
 bad=good;bad.en_ulID=0;good.en_ulID=0;Reject(&bad,&good,"zero identity rejected");
 good.en_ulID=900;bad=good;bad.m_aLastRotation(1)=std::numeric_limits<float>::infinity();
 Reject(&bad,&good,"nonfinite heading rejected");
 bad=good;bad.m_aLastRotation(2)=std::numeric_limits<float>::quiet_NaN();
 Reject(&bad,&good,"nonfinite pitch rejected");
 Reject(nullptr,&good,"temporarily absent predicted entity remains neutral");
 bad=good;bad.m_aLastRotation=Vec(30,40,0);a=Step(0,&bad,&good);
 Check(a.pa_aRotation(1)==30&&a.pa_aRotation(2)==40,"rejected basis can be accepted when a valid observation arrives");
 // Log the previous request and actual native inputs before adopting, once.
 OldState(0,900,88,173);CPlayer diag=player(999,-12,9),diagPred=diag;
 diag.m_aLocalRotation=Vec(-10,11,0);diagPred.en_plViewpoint.pl_OrientationAngle(2)=4;
 diagPred.m_tmSpawned=2.5f;BotHumanAttach(0);logs.clear();bot_bDiagnostics=1;
 auto traced=Step(0,&diagPred,&diag);
 Check(RotationLogs()==1&&logs.back().find("requested_before=(88,173)")!=std::string::npos&&
       logs.back().find("native_last=(-12,9)")!=std::string::npos&&
       logs.back().find("local_before=(-10,11)")!=std::string::npos&&
       logs.back().find("view=(0,4)")!=std::string::npos&&
       logs.back().find("spawn_clock=2.5")!=std::string::npos,
       "one boundary receipt contains values from before adoption");
 diagPred.m_tmSpawned=3.5f;diagPred.en_plViewpoint.pl_OrientationAngle(2)=0;
 a=Step(0,&diagPred,&diag);
 Check(RotationLogs()==1&&a.pa_aRotation(2)==9,"ordinary respawn retains basis without a new map receipt");
 OldState(0,900,88,173);CPlayer quiet=player(999,-12,9),quietPred=quiet;
 quiet.m_aLocalRotation=Vec(-10,11,0);quietPred.en_plViewpoint.pl_OrientationAngle(2)=4;
 quietPred.m_tmSpawned=2.5f;BotHumanAttach(0);logs.clear();bot_bDiagnostics=0;
 auto untraced=Step(0,&quietPred,&quiet);
 Check(RotationLogs()==0&&std::memcmp(&traced.pa_aRotation,&untraced.pa_aRotation,sizeof(Vec))==0,
       "diagnostic flag does not change composed rotation");
 std::printf("rotation-epoch actual Driver: %d checks, %d failures\n",checks,failures);
 return failures?1:0;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--driver', type=Path, default=Path(__file__).with_name('BotDriver.cpp'))
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    source = args.driver.read_text()
    state = balanced(source, 'struct SBotState') + ';\n'
    helpers = '\n'.join(function(source, name) for name in ('BotHumanPolicy', 'BotHumanProfile', 'BotHumanAttach'))
    rebase = function(source, 'BotAdoptRotationBaseline') if 'static bool BotAdoptRotationBaseline(' in source else ''
    start = source.index('    const ULONG entityId=player?player->en_ulID:0;')
    end = source.index('    // ponytail:', start)
    entity_boundary = source[start:end]
    compose = '\n'.join(re.findall(r'^    pa\.pa_aRotation\([12]\) = [^;]+;', source, re.M))
    if len(compose.splitlines()) != 2:
        raise ValueError('exact actual yaw/pitch compose statements required')
    wrapper = r'''
static CPlayerAction Step(INDEX iLP,CPlayer* player,CPlayer* localInput){
 SBotState& bs=_absBots[iLP];CPlayerSource* ppls=bs.bs_ppls;BOOL bActed=FALSE;
 (void)ppls;(void)bActed;
 for(int once=0;once<1;++once){
''' + entity_boundary + r'''
 CPlayerAction pa;pa.Clear();
''' + compose + r'''
 // Same additive native composer contract; no direct SUT native rotation write.
 localInput->m_aLocalRotation+=pa.pa_aRotation;pa.pa_aRotation=localInput->m_aLocalRotation;
 return pa;
 }
 return ppls->pls_paAction;
}
'''
    text = STUB + state + '\nstatic SBotState _absBots[4];\n' + rebase + r'''
static INDEX* const _apiProfileSlot[4]={&bot_iProfile0,&bot_iProfile1,&bot_iProfile2,&bot_iProfile3};
''' + helpers + wrapper + TEST
    with tempfile.TemporaryDirectory(prefix='tse-rotation-epoch-') as directory:
        cpp = Path(directory)/'actual-driver.cpp'; exe = Path(directory)/'actual-driver'
        cpp.write_text(text)
        command = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wno-unused-function', '-I', str(args.driver.parent)]
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        subprocess.run(command+[str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    main()
