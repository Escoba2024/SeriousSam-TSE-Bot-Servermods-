#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile real native bridge decisions against deterministic world/ray stubs.
The main-thread loader and native item decoding are excluded (separate tests/build).
This is portable behavioral evidence, not Retail collision/runtime qualification.
"""
import argparse
import re
import hashlib
from pathlib import Path
import subprocess
import tempfile

STUBS = r'''
#include <cstdio>
#include <cstdarg>
#include <cstdlib>
#include <new>
#include <vector>
#include <cmath>
#include "cecil_motion.h"
#include "cecil_rules.h"
static bool measuring=false;static size_t allocations=0;
void* operator new(size_t n){if(measuring)++allocations;void* p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();return p;}
void operator delete(void* p)noexcept{std::free(p);}
void operator delete(void* p,size_t)noexcept{std::free(p);}
using INDEX=int;using BOOL=int;using FLOAT=float;using ULONG=unsigned long;
const int TRUE=1,FALSE=0,ENF_DELETED=1,BPOF_PASSABLE=1<<11,BPOF_SHOOTTHRU=1<<4;
int normalizeCalls=0;
const unsigned EPF_TRANSLATEDBYGRAVITY=1u<<1,EPF_MOVABLE=1u<<9;
struct FLOAT3D {
 float a[3];FLOAT3D(float x=0,float y=0,float z=0):a{x,y,z}{}
 float operator()(int i)const{return a[i-1];} float& operator()(int i){return a[i-1];}
 FLOAT3D operator+(const FLOAT3D& b)const{return {a[0]+b.a[0],a[1]+b.a[1],a[2]+b.a[2]};}
 FLOAT3D operator-(const FLOAT3D& b)const{return {a[0]-b.a[0],a[1]-b.a[1],a[2]-b.a[2]};}
 FLOAT3D operator*(float s)const{return {a[0]*s,a[1]*s,a[2]*s};}
 double Length()const{return std::sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);}
 FLOAT3D& Normalize(){++normalizeCalls;const float length=(float)Length();for(float& v:a)v/=length;return *this;}
};
struct FLOATmatrix3D {double m[3][3]={{1,0,0},{0,1,0},{0,0,1}};};
FLOAT3D operator*(const FLOAT3D& v,const FLOATmatrix3D& m){
 return {float(v(1)*m.m[0][0]+v(2)*m.m[0][1]+v(3)*m.m[0][2]),
         float(v(1)*m.m[1][0]+v(2)*m.m[1][1]+v(3)*m.m[1][2]),
         float(v(1)*m.m[2][0]+v(2)*m.m[2][1]+v(3)*m.m[2][2])};
}
struct CPlacement3D {FLOAT3D pl_PositionVector,pl_OrientationAngle;};
struct StubClass {const char* name="Entity";const char* GetName()const{return name;}};
int worldLookups=0;struct CWorld;struct CBrushPolygon;
struct CEntity {
 CWorld* en_pwoWorld=nullptr;unsigned entityPhysicsFlags=0;
 unsigned GetPhysicsFlags()const{return entityPhysicsFlags;}
 enum {RT_BRUSH=4,RT_MODEL=2,RT_TERRAIN=11};
 StubClass cls;CEntity* target=nullptr;bool marker=false;
 StubClass* GetClass(){return &cls;}CEntity* GetTarget()const{return target;}bool IsMarker()const{return marker;}
 unsigned en_ulID=0,flags=0;int type=RT_MODEL;CPlacement3D pl;
 bool pickable=false;botcore::CecilItem item;
 const CPlacement3D& GetPlacement()const{return pl;}
 unsigned GetFlags()const{return flags;}int GetRenderType(){return type;}
};
bool IsDerivedFromClass(CEntity*,const char*){return false;}
struct CWeaponItem:CEntity {int m_ulPickedMask=0,m_bPickupOnce=0,m_bDropped=0,m_bRespawn=0,m_EwitType=1;};
struct CSwitch:CEntity {bool m_bUseable=true;CSwitch(){cls.name="Classes/Switch.ecl";}};
struct CMovingBrush:CEntity {CEntity* m_penSwitch=nullptr;CMovingBrush(){cls.name="Classes/MovingBrush.ecl";}};
struct CMarker:CEntity {CMarker(){cls.name="Classes/Marker.ecl";marker=true;}};
struct CWorld {
 std::vector<CEntity*> wo_cenEntities;
 CEntity* EntityFromID(ULONG id){++worldLookups;for(auto e:wo_cenEntities)if(e->en_ulID==id)return e;return nullptr;}
};
#define FOREACHINDYNAMICCONTAINER(c,t,it) for(auto it : c)
struct CPlayerWeapons {CEntity* m_penRayHit=nullptr;float m_fRayHitDistance=1000;unsigned m_iAvailableWeapons=3;int m_iCurrentWeapon=2;unsigned usable=3,ammo=0;};
enum PlayerState {PST_STAND=0,PST_CROUCH=1,PST_SWIM=2,PST_DIVE=3,PST_FALL=4};
struct CPlayer:CEntity {
 int GetMyPlayerIndex()const{return 5;}
 CBrushPolygon* en_pbpoStandOn=nullptr;float en_fStepUpHeight=1,en_fStepDnHeight=1.5f;
 PlayerState m_pstState=PST_STAND;FLOATmatrix3D body;CPlacement3D en_plViewpoint;FLOAT3D m_aLastRotation;
 const FLOATmatrix3D& GetRotationMatrix()const{return body;}
 CPlayerWeapons w;CPlayerWeapons* m_penWeapons=&w;CWorld world;CEntity* en_penReference=nullptr;
 float health=100,m_fArmor=0,en_fImmersionFactor=0;FLOAT3D en_vGravityDir{0,-1,0};
 FLOAT3D en_vCurrentTranslationAbsolute;unsigned physicsFlags=EPF_TRANSLATEDBYGRAVITY;
 unsigned GetPhysicsFlags()const{return physicsFlags;}
 float GetHealth()const{return health;}CPlayerWeapons* GetPlayerWeapons(){return &w;}
 bool hasWorld=true;CWorld* worldOverride=nullptr;
 CWorld* GetWorld(){return hasWorld?(worldOverride?worldOverride:&world):nullptr;}
};
struct CSessionProperties {BOOL sp_bInfiniteAmmo=FALSE,sp_bWeaponsStay=TRUE;};
struct Network {CSessionProperties session;const void* GetSessionProperties(){return &session;}} network,*_pNetwork=&network;
struct Timer {double TickQuantum=.05;} timer,*_pTimer=&timer;
int _botRayBudget=20,bot_iRosterOffset=0;
bool bot_bDiagnostics=false;int supplyDiagLines=0;std::string supplyDiagText;
long _botSupplyMapSerial=7,_botSupplyMapReady=1;bool bot_bEnabled=true,bot_bSupplyNavigation=true;
long InterlockedCompareExchange(long* p,long,long){return *p;}
int hopCheckpointEvents=0;
int lockApproachEvents=0,lastApproachNode=-1,lastApproachHop=-1;unsigned long lastApproachRef=0;int lockEvents=0,lastLocked=-1,lastPresent=-1;int goalEvents=0,endEvents=0,groundReplanEvents=0;char lastEnd[32]={0};
void BotLog(const char* format,...){
 if(std::strstr(format,"[CecilSupplyDiag")){++supplyDiagLines;char text[2048];va_list a;va_start(a,format);std::vsnprintf(text,sizeof(text),format,a);va_end(a);supplyDiagText+=text;}
 if(std::strstr(format,"[CecilHopCheckpoint]"))++hopCheckpointEvents;
 if(std::strstr(format,"[CecilGroundReplan]"))++groundReplanEvents;
 if(std::strstr(format,"[CecilLockApproach]")){
  ++lockApproachEvents;va_list args;va_start(args,format);(void)va_arg(args,int);(void)va_arg(args,int);
  (void)va_arg(args,unsigned long);lastApproachRef=va_arg(args,unsigned long);lastApproachNode=va_arg(args,int);
  (void)va_arg(args,double);(void)va_arg(args,double);(void)va_arg(args,int);lastApproachHop=va_arg(args,int);va_end(args);
 }
 if(std::strstr(format,"[CecilLock]")){
  ++lockEvents;va_list args;va_start(args,format);(void)va_arg(args,int);(void)va_arg(args,int);
  lastLocked=va_arg(args,int);lastPresent=va_arg(args,int);va_end(args);
 }
 if(std::strstr(format,"[CecilGoal]"))++goalEvents;
 if(std::strstr(format,"[CecilGoalEnd]")){
  ++endEvents;va_list args;va_start(args,format);
  (void)va_arg(args,int);(void)va_arg(args,int);(void)va_arg(args,unsigned long);
  std::snprintf(lastEnd,sizeof(lastEnd),"%s",va_arg(args,const char*));va_end(args);
 }
}
CPlacement3D BotCombatEye(CPlayer* p){return p->GetPlacement();}
unsigned BotCecilUsableWeapons(CPlayerWeapons* p,bool){return p->usable;}
unsigned BotCecilAmmoNeed(CPlayerWeapons* p){return p->ammo;}
bool BotCecilWeaponGoalPicked(CPlayer*,CEntity*){return false;}
bool BotCecilReadItem(CPlayer*,CEntity* e,unsigned generation,unsigned,botcore::CecilItem* out,const char** reason=nullptr){
 if(reason)*reason="ok";
 if(!e||!e->pickable||(e->flags&ENF_DELETED)){if(reason)*reason="stub_unpickable";return false;}
 *out=e->item;out->id=e->en_ulID;out->generation=generation;out->pickable=true;
 out->x=e->pl.pl_PositionVector(1);out->y=e->pl.pl_PositionVector(2);out->z=e->pl.pl_PositionVector(3);return true;
}
struct StubPlane:FLOAT3D {
 float pl_distance=0;StubPlane(float x=0,float y=1,float z=0):FLOAT3D(x,y,z){}
 StubPlane& operator=(const FLOAT3D& v){static_cast<FLOAT3D&>(*this)=v;return *this;}
};
struct CBrushPlane {StubPlane bpl_plAbsolute{0,1,0};};
struct CBrush3D {CEntity* br_penEntity=nullptr;};
struct CBrushMip {CBrush3D* bm_pbrBrush=nullptr;};
struct CBrushSector {CBrushMip* bsc_pbmBrushMip=nullptr;};
struct CBrushPolygon {CBrushPlane* bpo_pbplPlane=nullptr;unsigned bpo_ulFlags=0;CBrushSector* bpo_pbscSector=nullptr;};
CEntity obstruction,floorEntity;CBrushPlane floorPlane;CBrushPolygon floorPolygon;
float floorHitDistance=1;CBrushPolygon* floorHitPolygon=&floorPolygon;
int liquidAxisQueries=0;bool liquidAxisBlocked=false,liquidAxisInvalid=false;
int floorMode=0,rayCount=0,blockedItems=0,floorPattern=0,wallMode=0,wallCount=0;FLOAT3D lastFrom,lastTo,wallFrom,wallTo;
int nearFootMode=0,nearFootRays=0;float nearFootDistance=.26f;bool invalidateAfterFloor=false;float physicalHitDistanceOverride=-1;
int legacyCastCalls=0,sectorAdds=0,sectorTests=0,worldTests=0;unsigned wallPolygonFlags=0;
int capturedWalls=0;bool captureWalls=false;double capturedWorld[4096][2];
bool forcePassableHit=false;int rayConstructions=0,lastModels=-1;ULONG lastMask=0;
bool lastPhysical=false,lastOverHit=true;bool invalidHitDistance=false;
FLOAT3D nearFootFrom,nearFootTo;bool nearFootPhysical=false,nearFootOverHit=true;
struct CCastRay {
 enum {TT_NONE=0,TT_COLLISIONBOX=2};
 bool cr_bAllowOverHit=false,cr_bPhysical=false;int cr_ttHitModels=TT_NONE;
 CEntity* cr_penHit=nullptr;CBrushPolygon* cr_pbpoBrushPolygon=nullptr;FLOAT3D from,to;CPlayer* owner;
 FLOAT cr_fHitDistance=0;ULONG cr_ulPassablePolygons=0;CEntity* cr_penOrigin;
 CBrushSector* cr_pbscBrushSector=nullptr;FLOAT3D cr_vOrigin,cr_vTarget,cr_vHit;
 CCastRay(CPlayer* p,const FLOAT3D& a,const FLOAT3D& b):from(a),to(b),owner(p),cr_penOrigin(p),cr_vOrigin(a),cr_vTarget(b),cr_vHit(b){++rayConstructions;cr_fHitDistance=(FLOAT)(b-a).Length();}
 void AddSectorsAroundEntity(CEntity*){++sectorAdds;}
 void TestThroughSectors(){++sectorTests;Query();if(cr_penHit&&physicalHitDistanceOverride>=0)cr_fHitDistance=physicalHitDistanceOverride;if(invalidHitDistance)cr_fHitDistance=NAN;}
 void TestWholeWorld(CWorld*){++worldTests;Query();if(invalidHitDistance)cr_fHitDistance=NAN;}
 void Cast(CWorld*){++legacyCastCalls;cr_penHit=nullptr;cr_pbpoBrushPolygon=nullptr;cr_pbscBrushSector=nullptr;
  // Retail033 measured Cast overwriting BOTH initial0 and initialPASSABLE.
  cr_ulPassablePolygons=cr_bPhysical?2064u:1077936128u;Query();}
 bool Passes(unsigned flags)const{return (flags&cr_ulPassablePolygons)!=0&&!(forcePassableHit&&(flags&BPOF_PASSABLE));}
 void Query(){
  ++rayCount;lastFrom=from;lastTo=to;lastMask=cr_ulPassablePolygons;lastModels=cr_ttHitModels;
  lastPhysical=cr_bPhysical;lastOverHit=cr_bAllowOverHit;
  if(cr_ttHitModels==TT_NONE&&(to-from).Length()<1){
   ++nearFootRays;nearFootFrom=from;nearFootTo=to;nearFootPhysical=cr_bPhysical;nearFootOverHit=cr_bAllowOverHit;
   if(nearFootMode&&!(nearFootMode==2&&Passes(floorPolygon.bpo_ulFlags))){cr_penHit=&floorEntity;cr_fHitDistance=nearFootDistance;
    if(nearFootMode==2)cr_pbpoBrushPolygon=&floorPolygon;}
   return;
  }
  if(cr_ttHitModels==TT_NONE&&(to-from).Length()>4){
   if(invalidateAfterFloor)owner->en_plViewpoint.pl_OrientationAngle(1)=NAN;
   if(floorPattern==1&&from(3)<=0)return;
   if(floorPattern==2&&from(3)<0&&from(1)<2)return;
   if(floorPattern==3&&(from(1)<=.1f||from(3)>=-.1f))return;
   if(floorPattern==4&&!(from(1)<-.2f&&from(3)<-.2f))return;
   if(floorPattern==5&&!(std::fabs(from(1))<.1f&&from(3)<1.8f))return;
   if(floorMode&&!(floorMode==2&&Passes(floorPolygon.bpo_ulFlags))){cr_penHit=&floorEntity;cr_fHitDistance=floorHitDistance;
    if(floorMode==2)cr_pbpoBrushPolygon=floorHitPolygon;}
  }else{
   ++wallCount;wallFrom=from;wallTo=to;
   const bool liquidAxis=std::fabs(to(2)-from(2))>1e-5&&std::hypot(to(1)-from(1),to(3)-from(3))<1e-5;
   if(liquidAxis){++liquidAxisQueries;if(liquidAxisInvalid){cr_fHitDistance=NAN;return;}if(liquidAxisBlocked){cr_penHit=&obstruction;return;}}
   if(captureWalls&&capturedWalls<4096){capturedWorld[capturedWalls][0]=to(1)-from(1);capturedWorld[capturedWalls++][1]=to(3)-from(3);}
   if(!Passes(wallPolygonFlags)&&(wallMode==2||(wallMode==1&&to(3)<from(3))||
      (wallMode==6&&to(1)<from(1))||
      (wallMode==3&&(std::fabs(to(1)-from(1))<1e-5||std::fabs(to(3)-from(3))<1e-5))||
      (wallMode==4&&!(std::fabs(to(1)-from(1))<1e-5&&to(3)<from(3)))||
      (wallMode==5&&std::fabs(to(2)-from(2))>1e-5&&std::hypot(to(1)-from(1),to(3)-from(3))>1e-5)||
      (to(1)>0 && to(1)<=blockedItems)))cr_penHit=&obstruction;
  }
 }
};
'''
TESTS = r'''
static int checks=0,failures=0;
void check(bool yes,const char* name){++checks;if(!yes){++failures;std::printf("FAIL %s\n",name);}}
bool near(double a,double b){return std::fabs(a-b)<1e-5;}
CPlayer player;std::vector<CEntity> items;
void setup(int nodes=3){
 liquidAxisQueries=0;liquidAxisBlocked=liquidAxisInvalid=false;captureWalls=false;capturedWalls=0;
 player=CPlayer();player.m_penWeapons=&player.w;items.clear();items.reserve(140);
 auto& g=BotSupplyGraph();g=botcore::CecilNavGraph();g.points.resize(nodes);
 for(int i=0;i<nodes;++i){g.points[i].id=i;g.points[i].z=-10*i;g.points[i].radius=1;if(i+1<nodes)g.points[i].links.push_back(i+1);}
 auto& s=BotSupplyState(0);s=SSupplyState();s.navigator.Prepare(nodes);s.goals.Prepare(nodes);s.patrolSearch.Prepare(nodes);s.blocked.resize(nodes);s.worldLock.assign(nodes,3);
 s.playable=true;s.generation=1;s.anchor=0;s.owned=3;
 BotCecilSettings()=botcore::CecilPreset(2);BotCecilSettings().fItemSearchCD=0;
 // Existing support/recovery fixtures explicitly exercise opt-in, off-graph pit avoidance.
 BotCecilSettings().bAvoidPits=1;
 hopCheckpointEvents=0;lockApproachEvents=0;lockEvents=0;lastLocked=lastPresent=-1;goalEvents=endEvents=groundReplanEvents=0;lastEnd[0]=0;_botSupplyMapSerial=7;_botRayBudget=40;rayCount=0;blockedItems=0;floorMode=0;floorPattern=0;wallMode=wallCount=0;physicalHitDistanceOverride=-1;floorEntity.type=CEntity::RT_MODEL;
 worldLookups=0;floorPlane.bpl_plAbsolute.pl_distance=0;floorHitDistance=1;floorHitPolygon=&floorPolygon;floorPolygon.bpo_pbscSector=nullptr;floorEntity.en_pwoWorld=nullptr;floorEntity.entityPhysicsFlags=0;
 floorPlane.bpl_plAbsolute=FLOAT3D(0,1,0);floorPolygon.bpo_pbplPlane=&floorPlane;floorPolygon.bpo_ulFlags=0;
 nearFootMode=nearFootRays=0;nearFootDistance=.26f;floorEntity.flags=0;invalidateAfterFloor=false;
 legacyCastCalls=sectorAdds=sectorTests=worldTests=normalizeCalls=0;wallPolygonFlags=0;forcePassableHit=false;
 rayConstructions=0;lastModels=-1;lastMask=0;lastPhysical=false;lastOverHit=true;invalidHitDistance=false;
}
CEntity& addItem(unsigned id,float x,float z,botcore::CecilItemKind kind=botcore::CecilItemKind::Health){
 items.emplace_back();auto& e=items.back();e.en_ulID=id;e.pickable=true;
 e.pl.pl_PositionVector=FLOAT3D(x,0,z);e.item.kind=kind;e.item.value=25;e.item.weapon=4;
 player.world.wo_cenEntities.push_back(&e);return e;
}
template<class T>auto typed(const T& m,int)->decltype(m.itemGoal&&m.urgent){return m.itemGoal&&m.urgent;}
template<class T>bool typed(const T&,long){return false;}
template<class T>auto owns(const T& m,int)->decltype(m.ownsMovement){return m.ownsMovement;}
template<class T>bool owns(const T&,long){return false;}
template<class T>auto finalSafety(T& f,T& st,T& up,double now,bool accepted,int)
 ->decltype(BotCecilSafeMotion(&player,BotSupplyState(0),now,f,st,up,0,1,accepted)){
 return BotCecilSafeMotion(&player,BotSupplyState(0),now,f,st,up,0,1,accepted);
}
template<class T>int finalSafety(T& f,T& st,T& up,double now,bool,long){
 return BotCecilSafeMotion(&player,BotSupplyState(0),now,f,st,up,0,1);
}
void relocationFixture(bool longRoute=false){
 setup(7);auto& g=BotSupplyGraph();
 const FLOAT3D positions[7]={{0,0,0},{0,0,-10},{40,0,0},{40,0,-30},{40,0,-60},{0,0,-20},{100,0,100}};
 for(int i=0;i<7;++i){g.points[i].x=positions[i](1);g.points[i].y=positions[i](2);g.points[i].z=positions[i](3);g.points[i].links.clear();}
 g.points[0].links={1};g.points[1].links={5};g.points[2].links={3};g.points[3].links={4};g.points[4].links={5};g.points[6].links={2};
 if(longRoute)g.points[4].x=400;
 addItem(991,0,-20,botcore::CecilItemKind::Weapon);
 auto& s=BotSupplyState(0);s.goal=5;s.goalEntity=991;s.goalSince=0;s.scanTick=999;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
}
SCecilMove relocateTo(int node,int tick,int budget=16){
 const auto& point=BotSupplyGraph().points[node];player.pl.pl_PositionVector=FLOAT3D(point.x,point.y,point.z);
 BotSupplyState(0).anchor=node;_botRayBudget=budget;return BotSupplyTick(&player,0,tick,1000);
}
void nullReferenceFixture(){
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);
 nearFootMode=2;floorEntity.type=CEntity::RT_BRUSH;
}
SCecilMove recoveryFloorFixture(){
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,0);player.en_penReference=&floorEntity;
 auto& graph=BotSupplyGraph();graph.points[0].x=0;graph.points[0].z=-4;
 graph.points[1].x=8;graph.points[1].z=-8;
 floorMode=2;floorPattern=3;floorEntity.type=CEntity::RT_BRUSH;_botRayBudget=16;
 return BotSupplyTick(&player,0,1,1000);
}
int recoverySafety(const SCecilMove& move,double now,bool accepted=true,int budget=16){
 double f=move.forward,st=move.strafe,up=move.up;_botRayBudget=budget;
 const double yaw=player.en_plViewpoint.pl_OrientationAngle(1)+move.yaw_delta;
 const int result=BotCecilSafeMotion(&player,BotSupplyState(0),now,f,st,up,yaw,1,accepted);
 if(std::isfinite(yaw))player.en_plViewpoint.pl_OrientationAngle(1)=(FLOAT)yaw;
 check(result!=0||(f==0&&st==0&&up==0),"failed final recovery safety emits only neutral axes");
 return result;
}
template<class R>auto physicalCast(R& ray,CWorld* world,int)->decltype(BotCecilPhysicalCast(ray,world)){
 return BotCecilPhysicalCast(ray,world);
}
template<class R>bool physicalCast(R& ray,CWorld* world,long){ray.Cast(world);return true;}
CMovingBrush lift;
void liftFixture(){
 setup(6);auto& g=BotSupplyGraph();
 const float positions[6][3]={{-8,.5,0},{0,1.639451f,0},{0,12.5,0},{10,12.5,0},{-5.5,1,0},{0,0,100}};
 for(int i=0;i<6;++i){g.points[i].x=positions[i][0];g.points[i].y=positions[i][1];g.points[i].z=positions[i][2];g.points[i].links.clear();}
 g.points[0].links={1};g.points[1].links={2};g.points[2].links={3};g.points[4].links={0,5};g.points[5].links={3};
 lift=CMovingBrush();lift.type=CEntity::RT_BRUSH;lift.en_ulID=9;player.world.wo_cenEntities.push_back(&lift);g.points[1].lock_entity=9;
 auto& item=addItem(991,10,0,botcore::CecilItemKind::Weapon);item.pl.pl_PositionVector(2)=12.5;
 auto& state=BotSupplyState(0);state.goal=3;state.goalEntity=991;state.goalDeadline=11;state.scanTick=999;
 player.pl.pl_PositionVector=FLOAT3D(-8,.5,0);BotSupplyTick(&player,0,1,1000);
 state.anchor=4;player.pl.pl_PositionVector=FLOAT3D(-1.584377f,1.080671f,.991288f);
 player.en_penReference=&lift;player.en_vCurrentTranslationAbsolute=FLOAT3D(13.135438f,6.670916f,-9.632113f);
 lift.pl.pl_PositionVector(2)=.1906f;_botRayBudget=16;
}
void liftOccupancyBridge(){
 liftFixture();auto& state=BotSupplyState(0);const auto move=BotSupplyTick(&player,0,2,1000);
 check(move.active&&state.hop==1,"native matching grounded lift at1.95m retains fresh locked hop instead of reverse anchor");
 check(state.anchor==4&&state.blocked[1]&&state.goalEntity==991&&state.goalSince==0&&state.goalDeadline==11&&!state.goalRelocationBudgeted,
  "lift contact never rewrites anchor global lock goal or ordinary weapon budget");
 check(lockApproachEvents==1&&lastApproachRef==9&&lastApproachNode==1&&lastApproachHop==1&&rayCount==0&&_botRayBudget==16,"fresh supported approach logs once without adding physical casts");
 _botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(state.hop==1&&lockApproachEvents==1,"current continuous native support holds same edge without repeated log");
 player.pl.pl_PositionVector=FLOAT3D(0,1.1f,0);state.anchor=1;_botRayBudget=16;BotSupplyTick(&player,0,4,1000);
 check(state.hop==2&&state.blocked[1]&&state.goalDeadline==11&&!state.goalRelocationBudgeted,
  "actual original radius arrival advances upward without fabricating relocation budget");
 auto denied=[&](const char* label){const auto m=BotSupplyTick(&player,0,2,1000);check((!m.active||BotSupplyState(0).hop!=1)&&lockApproachEvents==0,label);};
 liftFixture();player.en_penReference=nullptr;denied("NULL native reference cannot start supported lock approach");
 liftFixture();player.en_penReference=&floorEntity;denied("foreign native reference cannot start supported lock approach");
 liftFixture();CMovingBrush sameID;sameID.en_ulID=9;sameID.type=CEntity::RT_BRUSH;player.en_penReference=&sameID;
 denied("equal entity ID with wrong world pointer cannot prove current lift support");
 liftFixture();lift.flags=ENF_DELETED;denied("deleted lock entity never grants supported approach");
 liftFixture();lift.type=CEntity::RT_MODEL;denied("model lock entity is not supporting brush contact");
 liftFixture();lift.cls.name="Classes/Brush.ecl";denied("static nonmoving brush support cannot waive locked approach");
 for(PlayerState mode:{PST_FALL,PST_SWIM,PST_DIVE}){liftFixture();player.m_pstState=mode;denied("air and liquid native states cannot claim grounded moving lift");}
 liftFixture();player.m_pstState=PST_CROUCH;BotSupplyTick(&player,0,2,1000);
 check(BotSupplyState(0).hop==1&&lockApproachEvents==1,"native crouch and finite moving-platform velocity preserve current approach");
 liftFixture();player.en_vCurrentTranslationAbsolute(2)=NAN;denied("nonfinite velocity rejects supported approach without a speed cap");
 liftFixture();lift.pl.pl_OrientationAngle(2)=NAN;denied("nonfinite lock placement rejects supported approach");
 liftFixture();player.pl.pl_PositionVector=FLOAT3D(0,BotSupplyGraph().points[1].y-2.01f,0);
 denied("same mover reference on another floor beyond bounded 3D range grants no approach");
 liftFixture();player.pl.pl_PositionVector(1)=100;denied("distant support on same broad moving brush grants no approach");
 liftFixture();BotSupplyGraph().points[1].radius=.5f;denied("small original point radius tightens occupied approach bound");
 liftFixture();BotSupplyGraph().points[1].radius=1.5f;player.pl.pl_PositionVector(1)=-2.1f;
 denied("large original point radius cannot exceed absolute two metre occupied bound");
 liftFixture();BotSupplyGraph().points[1].radius=NAN;denied("nonfinite original radius fails closed");
 liftFixture();lift.pl.pl_PositionVector(2)=0;BotSupplyState(0).avoidNode=1;BotSupplyState(0).avoidUntil=10;
 denied("temporary avoidance with physically open reference is not a moving lock event");
 liftFixture();player.hasWorld=false;check(BotCecilSupportedLockNode(&player,BotSupplyState(0))==-1,"missing world rejects native support helper without a query");
 for(int loss=0;loss<3;++loss){
   liftFixture();BotSupplyTick(&player,0,2,1000);
   if(loss==0)player.en_penReference=nullptr;
   if(loss==1)player.en_penReference=&floorEntity;
   if(loss==2)player.pl.pl_PositionVector(1)=-2.1f;
   _botRayBudget=16;const auto dropped=BotSupplyTick(&player,0,3,1000);
   check(dropped.active&&BotSupplyState(0).hop==4&&lockApproachEvents==1,
     "NULL foreign or out-of-range support loss immediately drops locked edge before next replan timer");
   player.en_penReference=&lift;player.pl.pl_PositionVector=FLOAT3D(-1.584377f,1.080671f,.991288f);_botRayBudget=16;
   BotSupplyTick(&player,0,4,1000);
   check(BotSupplyState(0).hop==4&&lockApproachEvents==1,"later contact cannot revive an already closed dropped edge");
 }
 liftFixture();BotSupplyState(0).mappedWeaponGoal=true;BotSupplyState(0).goalDeadline=40;BotSupplyTick(&player,0,2,1000);
 check(BotSupplyState(0).hop==1&&BotSupplyState(0).goalDeadline==40&&!BotSupplyState(0).goalRelocationBudgeted,
  "supported mapped weapon approach preserves its original fixed deadline");
 liftFixture();BotSupplyTick(&player,0,2,1000);_botRayBudget=16;BotSupplyTick(&player,0,241,1000);
 check(endEvents==1&&std::strcmp(lastEnd,"timeout")==0&&BotSupplyState(0).goalEntity==0,
  "ordinary weapon deadline still expires while contact stays on a locked approach");

}

// Replay the observed 044 anchored route cycle through actual Tick + final-owner safety.
void hopCheckpoint45Fixture(){
 setup(3);auto& graph=BotSupplyGraph();
 const float xyz[3][3]={{-6.5f,-64,-56},{-29,-29.5f,-64},{-114,25.5f,14}};
 for(int i=0;i<3;++i){auto& p=graph.points[i];p.x=xyz[i][0];p.y=xyz[i][1];p.z=xyz[i][2];p.radius=i==0?2:(i==1?5:3);}
 graph.points[2].flags=botcore::CECIL_UNREACHABLE|botcore::CECIL_CROUCH;
 auto& s=BotSupplyState(0);s.goal=2;s.goalSince=7;s.goalDeadline=47;s.scanTick=999999;s.anchor=0;
 BotCecilSettings().bAvoidPits=0;
 floorEntity.en_ulID=1;floorEntity.type=CEntity::RT_BRUSH;floorEntity.cls.name="Classes/WorldBase.ecl";
 floorEntity.en_pwoWorld=&player.world;player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 player.pl.pl_PositionVector=FLOAT3D(xyz[0][0],xyz[0][1],xyz[0][2]);
 _botRayBudget=16;const auto move=BotSupplyTick(&player,0,1,1000);
 double f=move.forward,st=move.strafe,u=move.up;BotCecilSafeMotion(&player,s,.05,f,st,u,0,1,true);
}
SCecilMove hopCheckpoint45Tick(int tick,bool accepted=true,int budget=16){
 _botRayBudget=budget;auto move=BotSupplyTick(&player,0,tick,1000);
 double f=move.forward,st=move.strafe,u=move.up;
 BotCecilSafeMotion(&player,BotSupplyState(0),tick*_pTimer->TickQuantum,f,st,u,0,1,accepted);
 move.forward=f;move.strafe=st;move.up=u;return move;
}
void hopCheckpoint45(){
 hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;
 check(s.navigator.SourceSlot(2)==0&&s.hop==1,"044 source radius establishes the genuine 112 to 107 committed edge");
 const float cycle[3][3]={{-11.821f,-64.496f,-60.495f},{-11.137f,-64.496f,-57.992f},{-11.996f,-64.496f,-57.378f}};
 bool reacquired=false,bounded=true,neutralReset=false;int first=-1;
 for(int tick=2;tick<=4142;++tick){
  const int at=((tick-2)/20)%3;player.pl.pl_PositionVector=FLOAT3D(cycle[at][0],cycle[at][1],cycle[at][2]);
  // Native movement is not stationary: this must not have the old speed <=.1 gate.
  player.en_vCurrentTranslationAbsolute=FLOAT3D(2,0,-3);
  const int before=rayCount;hopCheckpoint45Tick(tick);
  if(s.navigator.SourceSlot(2)<0&&s.goal==2){neutralReset=true;if(first<0)first=tick;}
  if(s.hop==0)reacquired=true;
  bounded&=rayCount-before<=16&&_botRayBudget>=0;
 }
 check(reacquired&&neutralReset&&first>=100&&first<=122,
  "207 second real three-pose wiggle must reacquire original source within the five second checkpoint");
 check(s.goal==2&&s.goalSince==7&&s.goalDeadline==47&&!s.goalRelocationBudgeted&&endEvents==0,
  "route checkpoint preserves goal timing and goal UNREACHABLE flags without fake item relocation");
 check(bounded,"route checkpoint keeps all existing exact casts inside shared sixteen ray budget");
}
void hopCheckpoint45Wiggle(int tick);
void hopCheckpoint45Freshness(){
 hopCheckpoint45Fixture();auto& cached=BotSupplyState(0);
 for(int tick=2;tick<=125;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 check(cached.navigator.SourceSlot(2)==0&&cached.hop==1,
  "cached bounded anchor without same-tick normal nearest LOS cannot authorize a checkpoint reset");
 // No forced scan: the next regularly scheduled real nearest success grants it.
 cached.scanTick=126;hopCheckpoint45Tick(126);
 check(cached.navigator.SourceSlot(2)<0&&cached.hop==-1&&cached.goal==2,
  "expired checkpoint waits for actual ordinary nearest acquisition with unchanged cadence");
 hopCheckpoint45Tick(127);check(cached.hop==0,
  "next navigator call approaches the freshly acquired source at its original radius");
}
void hopCheckpoint45Wiggle(int tick){
 const float cycle[3][3]={{-11.821f,-64.496f,-60.495f},{-11.137f,-64.496f,-57.992f},{-11.996f,-64.496f,-57.378f}};
 const int at=((tick-2)/20)%3;player.pl.pl_PositionVector=FLOAT3D(cycle[at][0],cycle[at][1],cycle[at][2]);
}
void hopCheckpoint46Flicker(){
 // Actual Tick + final-owner safety at20Hz: a reference is not progress.
 // This isolates the observed long-cycle mechanism without asserting the
 // unlogged native reference520 class or inventing native collision geometry.
 for(int mode=0;mode<3;++mode){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;
  CMovingBrush mover;mover.type=CEntity::RT_BRUSH;mover.entityPhysicsFlags=EPF_MOVABLE;
  mover.en_pwoWorld=&player.world;bool reacquired=false,bounded=true;int first=-1;
  for(int tick=2;tick<=4562;++tick){
   hopCheckpoint45Wiggle(tick);player.en_vCurrentTranslationAbsolute=FLOAT3D(2,0,-3);
   player.en_penReference=&floorEntity;
   if(mode==0&&tick%20==0)player.en_penReference=nullptr;
   if(mode==1&&tick%20==0)player.en_penReference=&mover;
   if(mode==2)player.en_penReference=tick%3==0?nullptr:(tick%3==1?&mover:&floorEntity);
   const int rays=rayCount;hopCheckpoint45Tick(tick);
   if(hopCheckpointEvents&&first<0)first=tick;
   reacquired|=s.hop==0;bounded&=rayCount-rays<=16&&_botRayBudget>=0;
  }
  check(first>=102&&first<=122&&reacquired,
   "228s same-hop wiggle across sparse or dense NULL and moving-reference flicker keeps passive five-second observation");
  check(bounded,"reference-flicker observation preserves shared sixteen-ray budget");
  check(s.goal==2&&s.goalSince==7&&s.goalDeadline==47&&!s.goalRelocationBudgeted&&endEvents==0,
   "reference-flicker checkpoint does not renew goal attempt or fabricate relocation");
 }
}
void hopCheckpoint46Authority(){
 // An expired passive interval is neither a NULL nor a moving-ground permit.
 for(int kind=0;kind<3;++kind){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;
  CMovingBrush mover;mover.type=CEntity::RT_BRUSH;mover.en_pwoWorld=&player.world;
  mover.entityPhysicsFlags=kind==1?EPF_MOVABLE:0;
  for(int tick=2;tick<=121;++tick){
   hopCheckpoint45Wiggle(tick);player.en_penReference=kind==0?nullptr:&mover;hopCheckpoint45Tick(tick);
  }
  check(hopCheckpointEvents==0&&s.hopCheckpointSince>=0&&s.hopCheckpointSince<=.15&&
    near(s.hopCheckpointLast,6.05)&&s.navigator.SourceSlot(2)==0&&s.hop==1,
   "NULL and movable or non-WorldBase brush preserve passive history but never authorize checkpoint");
  player.en_penReference=&floorEntity;hopCheckpoint45Wiggle(122);const auto reset=hopCheckpoint45Tick(122);
  check(hopCheckpointEvents==1&&s.hop==-1&&reset.forward==0&&reset.strafe==0&&reset.up==0,
   "current static WorldBase and actual fresh nearest grant expired observation without another five second wait");
 }
 // A different valid static brush pointer in the same world is not progress.
 hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;
 CEntity second=floorEntity;second.en_ulID=2;
 for(int tick=2;tick<=102;++tick){
  hopCheckpoint45Wiggle(tick);player.en_penReference=tick%2?&second:&floorEntity;hopCheckpoint45Tick(tick);
 }
 check(hopCheckpointEvents==1,"same-world static reference identity changes cannot erase ineffective edge history");
 for(int denied=0;denied<3;++denied){
  hopCheckpoint45Fixture();auto& state=BotSupplyState(0);state.scanTick=2;
  for(int tick=2;tick<=121;++tick){hopCheckpoint45Wiggle(tick);player.en_penReference=nullptr;hopCheckpoint45Tick(tick);}
  player.en_penReference=&floorEntity;
  if(denied==0)wallMode=2;
  if(denied==2)state.scanTick=99999; // A cached anchor is not this tick's LOS.
  hopCheckpoint45Wiggle(122);hopCheckpoint45Tick(122,true,denied==1?2:16);
  check(hopCheckpointEvents==0&&state.hopCheckpointSince<=.15&&state.hop==1,
   "expired mixed-reference observation waits through blocked budget or cached nearest without dropping committed edge");
  wallMode=0;state.scanTick=142;
  for(int tick=123;tick<=142;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
  check(hopCheckpointEvents==1,"later ordinary fresh LOS authorizes retained observation without forcing a scan");
 }
 // The current passive-only final helper adds no queries or allocation.
 hopCheckpoint45Fixture();auto& passive=BotSupplyState(0);passive.scanTick=2;
 for(int tick=2;tick<=121;++tick){hopCheckpoint45Wiggle(tick);player.en_penReference=nullptr;hopCheckpoint45Tick(tick);}
 const int casts=rayCount,lookups=worldLookups,budget=_botRayBudget;
 allocations=0;measuring=true;const bool granted=BotCecilHopCheckpoint(&player,passive,6.05,true,true);measuring=false;
 check(!granted&&hopCheckpointEvents==0&&casts==rayCount&&lookups==worldLookups&&budget==_botRayBudget&&allocations==0,
  "expired passive NULL observation performs no cast World lookup heap allocation or action authorization");
}
void hopCheckpoint46Resets(){
 // Every loss starts a new accepted interval, even if previous support was NULL.
 for(int loss=0;loss<15;++loss){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;CWorld alternate;
  for(int tick=2;tick<=100;++tick){hopCheckpoint45Wiggle(tick);player.en_penReference=nullptr;hopCheckpoint45Tick(tick);}
  player.en_penReference=&floorEntity;int next=101;
  if(loss==0)next=110;
  if(loss==1)++s.generation;
  if(loss==2){s.ClearGoal();s.goal=2;s.scanTick=101;}
  if(loss==3){player.worldOverride=&alternate;floorEntity.en_pwoWorld=&alternate;}
  if(loss==4){player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;}
  hopCheckpoint45Wiggle(next);
  if(loss==5)player.m_pstState=static_cast<PlayerState>(5); // Unknown native state still cancels; FALL is covered separately.
  if(loss==6)player.m_pstState=PST_SWIM;
  if(loss==7)player.m_pstState=PST_DIVE;
  if(loss==8)floorEntity.flags=ENF_DELETED;
  if(loss==9)floorEntity.type=CEntity::RT_MODEL;
  if(loss==10)floorEntity.en_pwoWorld=&alternate;
  if(loss==11)player.en_vCurrentTranslationAbsolute(2)=NAN;
  if(loss==12)s.useReleaseTick=999;
  if(loss==13)s.followEntity=777;
  hopCheckpoint45Tick(next,loss!=14);
  check(hopCheckpointEvents==0,"context loss cannot spend old NULL-reference progress history");
  player.m_pstState=PST_STAND;floorEntity.flags=0;floorEntity.type=CEntity::RT_BRUSH;
  floorEntity.en_pwoWorld=player.GetWorld();player.en_vCurrentTranslationAbsolute=FLOAT3D();
  s.useReleaseTick=-1;s.followEntity=0;
  for(int tick=next+1;tick<=next+95;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
  check(hopCheckpointEvents==0,"world life goal owner medium metadata or clock loss requires new five second history");
 }
 // Positive crouch control: observation is native grounded context, not speed.
 hopCheckpoint45Fixture();auto& crouch=BotSupplyState(0);crouch.scanTick=2;player.m_pstState=PST_CROUCH;
 for(int tick=2;tick<=122;++tick){
  hopCheckpoint45Wiggle(tick);player.en_penReference=tick<122?nullptr:&floorEntity;hopCheckpoint45Tick(tick);
 }
 check(hopCheckpointEvents==1,"native crouch passive observation survives NULL and waits for current static acquisition");
}
void hopCheckpoint46ProgressAndProtection(){
 hopCheckpoint45Fixture();auto& g=BotSupplyGraph();auto& s=BotSupplyState(0);
 g.points[0].x=g.points[0].y=g.points[0].z=0;
 g.points[1].x=g.points[1].y=0;g.points[1].z=-100;
 s.ClearGoal();s.goal=2;s.scanTick=2;
 for(int tick=2;tick<=250;++tick){
  player.pl.pl_PositionVector=FLOAT3D(0,0,float(-(tick-2)*.05));
  player.en_penReference=tick%20?&floorEntity:nullptr;hopCheckpoint45Tick(tick);
 }
 check(hopCheckpointEvents==0&&s.hopCheckpointSince>11.4&&s.hop==1,
  "actual monotonic hop gain resets passive clock despite support flicker, preserving valid long-edge travel");
 for(int protection=0;protection<9;++protection){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);auto& graph=BotSupplyGraph();s.scanTick=2;
  for(int tick=2;tick<=100;++tick){hopCheckpoint45Wiggle(tick);player.en_penReference=nullptr;hopCheckpoint45Tick(tick);}
  if(protection==0)graph.points[0].flags=botcore::CECIL_TELEPORT;
  if(protection==1)graph.points[1].flags=botcore::CECIL_UNREACHABLE;
  if(protection==2)graph.points[0].flags=botcore::CECIL_IMPORTANT;
  if(protection==3)graph.points[1].flags=botcore::CECIL_JUMP;
  if(protection==4)graph.points[0].lock_entity=777;
  if(protection==5)graph.points[1].lock_entity=777;
  if(protection==6){s.importantGoal=true;graph.points[1].important_entity=777;}
  if(protection==7)s.interactionPoint=1;
  if(protection==8){graph.points[1].x=player.pl.pl_PositionVector(1);graph.points[1].z=player.pl.pl_PositionVector(3);}
  hopCheckpoint45Tick(101);
  check(hopCheckpointEvents==0&&s.hopCheckpointSince<0,
   "current protected edge or intentional stay erases passive history before any later static authorization");
 }
 for(int mapped=0;mapped<2;++mapped){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);const auto& goal=BotSupplyGraph().points[2];
  auto& item=addItem(991,goal.x,goal.z,botcore::CecilItemKind::Weapon);item.item.weapon=4;item.pl.pl_PositionVector(2)=goal.y;
  s.goalEntity=991;s.goalSince=0;s.goalDeadline=mapped?20:12;s.mappedWeaponGoal=mapped;s.scanTick=2;
  for(int tick=2;tick<=122;++tick){
   hopCheckpoint45Wiggle(tick);player.en_penReference=tick<122?nullptr:&floorEntity;hopCheckpoint45Tick(tick);
  }
  check(hopCheckpointEvents==1&&s.goalEntity==991&&s.goalSince==0&&s.goalDeadline==(mapped?20:12)&&!s.goalRelocationBudgeted,
   "mixed-reference checkpoint preserves ordinary and mapped fixed item deadline without relocation grant");
  if(!mapped){
   for(int tick=123;tick<=240;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
   check(endEvents==1&&std::strcmp(lastEnd,"timeout")==0&&s.ItemRejected(991,12),
    "ordinary item still expires at twelve seconds after reference-flicker checkpoint");
  }
 }
}
void patrolAlternate46Fixture(int nodes=4){
 setup(nodes);auto& g=BotSupplyGraph();
 const FLOAT3D xyz[4]={{0,0,0},{20,6,0},{0,0,-16},{18,0,-16}};
 for(int i=0;i<4;++i){g.points[i].x=xyz[i](1);g.points[i].y=xyz[i](2);g.points[i].z=xyz[i](3);g.points[i].radius=1;g.points[i].links.clear();}
 g.points[0].links={1};g.points[2].links={3};g.points[3].links={1};
 for(int i=4;i<nodes;++i){g.points[i].x=1000;g.points[i].links.clear();}
 auto& s=BotSupplyState(0);s.goal=1;s.anchor=0;s.scanTick=2;
 floorEntity.type=CEntity::RT_BRUSH;floorEntity.cls.name="Classes/WorldBase.ecl";floorEntity.en_ulID=1;
 floorEntity.en_pwoWorld=&player.world;player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 floorMode=2;BotCecilSettings().bAvoidPits=0;hopCheckpoint45Tick(1);
}
void patrolAlternate46Pose(int tick){
 // Real original-source reapproach follows a checkpoint; a selected hint is
 // never substituted for an anchor or a physically reached original point.
 const auto& s=BotSupplyState(0);
 player.pl.pl_PositionVector=s.hop==0?FLOAT3D(.25f,0,0):FLOAT3D(5,0,float(((tick/20)%3-1)*2));
}
void patrolAlternate46Red(){
 patrolAlternate46Fixture();auto& s=BotSupplyState(0);bool guided=false,bounded=true,ordinaryOnlySource=true,sourceApproached=false;int first=-1;
 double firstDistance=0,bestDistance=1e9;
 for(int tick=2;tick<=300;++tick){
  patrolAlternate46Pose(tick);
  const bool insideSource=s.hop==0&&player.pl.pl_PositionVector.Length()<1;
  const double distance=(FLOAT3D(20,6,0)-player.pl.pl_PositionVector).Length();
  if(tick==2)firstDistance=distance;
  bestDistance=std::fmin(bestDistance,distance);
  if(tick%20==0){_botRayBudget=16;ordinaryOnlySource&=BotSupplyNearest(&player,player.pl.pl_PositionVector,TRUE)==0;}
  const int rays=rayCount;const auto move=hopCheckpoint45Tick(tick);
  sourceApproached|=insideSource&&s.hop==1;
  bounded&=rayCount-rays<=16&&_botRayBudget>=0;
  if(s.anchor==0&&s.goal==1&&s.hop<0&&move.active&&move.forward>.15&&
     std::hypot(move.forward,move.strafe)<=.300001&&move.up==0){guided=true;first=tick;break;}
 }
 check(ordinaryOnlySource,"ordinary twelve/three acquisition has only the failed original source in repeated-edge fixture");
 check(hopCheckpointEvents>=2&&sourceApproached,"repeated-edge fixture actually has two accepted checkpoints and original-radius source reapproach");
 check(firstDistance-bestDistance<.75,"two-checkpoint wiggle has less than the genuine monotonic best-distance gain threshold");
 check(guided&&hopCheckpointEvents>=2&&first>=202,
  "two accepted failed checkpoints across real source reapproach offer bounded alternative original hint without fake anchor");
 check(bounded,"repeated-edge proposal and final safety retain sixteen shared ray bound");
}

int patrolAlternate46Enter(int nodes=4,int variant=0){
 patrolAlternate46Fixture(nodes);auto& g=BotSupplyGraph();
 if(variant==1)for(int i=2;i<nodes;++i){g.points[i].x=float(i-1);g.points[i].z=float(-16-2*(i-2));g.points[i].links={1};}
 if(variant==2){g.points[4].x=50;g.points[4].y=10;g.points[4].z=0;g.points[4].flags=botcore::CECIL_UNREACHABLE|botcore::CECIL_CROUCH;g.points[1].links={4};BotSupplyState(0).goal=4;}
 auto& s=BotSupplyState(0);
 for(int tick=2;tick<=300;++tick){patrolAlternate46Pose(tick);hopCheckpoint45Tick(tick);if(s.patrolAlternate)return tick;}
 check(false,"alternative guard fixture must enter from two actual accepted original-edge checkpoints");return 300;
}
void patrolAlternate46Gain(){
 patrolAlternate46Fixture();auto& s=BotSupplyState(0);int first=-1,second=-1;double base=0;
 for(int tick=2;tick<=600;++tick){
  patrolAlternate46Pose(tick);
  if(first>=0&&tick>first+3&&s.hop!=0){
   const double distance=base-.764778;
   player.pl.pl_PositionVector(1)=float(20-std::sqrt(distance*distance-36));
  }
  hopCheckpoint45Tick(tick);
  if(first<0&&hopCheckpointEvents==1){first=tick;base=s.patrolBest;}
  if(hopCheckpointEvents>=2){second=tick;break;}
 }
 check(first>0&&second>first&&base-s.patrolBest>.7647&&base-s.patrolBest<.7649,
  "real .764778 fixed-hop gain is observed across original source reapproach");
 check(!s.patrolAlternate&&s.patrolStrikes==1,
  "genuine .764778 gain resets first strike so second accepted checkpoint cannot enter alternate mode");
}
void patrolAlternate46Safety(){
 for(int denial=0;denial<7;++denial){
  const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  if(denial==0)floorMode=0;
  if(denial==1)wallMode=2;
  if(denial==2)invalidHitDistance=true;
  if(denial==3)player.en_penReference=nullptr;
  if(denial==4)floorEntity.entityPhysicsFlags=EPF_MOVABLE;
  if(denial==5)floorEntity.cls.name="Classes/MovingBrush.ecl";
  if(denial==6)floorEntity.flags=ENF_DELETED;
  const double deadline=s.patrolSince;const int rays=rayCount;
  const auto move=hopCheckpoint45Tick(tick,true,denial==2?3:16);
  check(move.forward==0&&move.strafe==0&&move.up==0,
   "alternate guidance is neutral without fresh full wall floor valid query and current static reference even when AvoidPits0");
  check(rayCount-rays<=16&&_botRayBudget>=0&&s.goal==1&&s.anchor==0,
   "alternate denial preserves real source goal and bounded shared budget");
  if(denial<6)check(s.patrolAlternate&&s.patrolSince==deadline,
   "temporary unsupported or rejected alternative never renews the fixed six second episode");
 }
 for(int cap=0;cap<3;++cap){
  const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  if(cap==1)BotCecilSettings().bStrafe=0;
  _botRayBudget=16;const auto move=BotSupplyTick(&player,0,tick,1000);
  double f=move.forward,st=move.strafe,u=move.up;const int before=rayCount;
  const int ok=BotCecilSafeMotion(&player,s,tick*.05,f,st,u,cap==2?90:0,cap==0?.05:1,true);
  check(ok==1&&std::hypot(f,st)<=.300001&&std::fabs(st)<=(cap==0?.050001:1)&&u==0&&(!cap||cap!=1||st==0),
   "alternate final safety uniformly caps movement honors strafe setting and emits no up");
  check(rayCount-before==2&&s.probe.wallRays==1&&s.probe.floorRays==1,
   "accepted alternative checks exactly fresh final-yaw wall plus mandatory floor");
  if(cap==2)check(std::fabs(wallTo(3)-wallFrom(3))>.05,
   "alternate wall probe follows actual final composed yaw rather than cached planner heading");
 }
}
void patrolAlternate46Lifecycle(){
 for(int loss=0;loss<21;++loss){
  const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;CWorld foreign;
  switch(loss){
   case 0:player.m_pstState=static_cast<PlayerState>(5);break; // Unknown state; passive FALL has dedicated authority tests.
   case 1:player.m_pstState=PST_SWIM;break;
   case 2:player.health=0;break;
   case 3:s.goal=3;break;
   case 4:s.goalEntity=991;break;
   case 5:s.followEntity=991;break;
   case 6:s.importantGoal=true;BotSupplyGraph().points[1].flags=botcore::CECIL_IMPORTANT;break;
   case 7:s.interactionPoint=0;break;
   case 8:s.useReleaseTick=tick+1;break;
   case 9:player.en_vCurrentTranslationAbsolute(2)=NAN;break;
   case 10:player.en_vGravityDir=FLOAT3D(0,0,-1);break;
   case 11:++s.generation;break;
   case 12:++player.en_ulID;break;
   case 13:player.worldOverride=&foreign;break;
   case 14:BotSupplyGraph().points[0].flags=botcore::CECIL_JUMP;break;
   case 15:BotSupplyGraph().points[1].important_entity=77;break;
   case 16:BotSupplyGraph().points[0].lock_entity=77;break;
   case 17:BotSupplyGraph().points[0].links.clear();break;
   case 19:++_botSupplyMapSerial;break;
   case 20:player.pl.pl_PositionVector=FLOAT3D(20,0,0);break;
  }
  const int before=rayCount;double f=.3,st=0,u=0;
  BotCecilSafeMotion(&player,s,tick*.05,f,st,u,0,1,loss!=18);
  check(!s.patrolAlternate&&s.patrolSource<0,
   "alternate episode clears on owner world life goal medium gravity invalid special lock interaction or topology context loss");
  if(loss!=18)check(f==0&&st==0&&u==0&&rayCount==before,
   "invalid alternate context emits no unverified recovery action or query");
 }
 for(int badTime=0;badTime<3;++badTime){
  const int tick=patrolAlternate46Enter();auto& s=BotSupplyState(0);double f=.3,st=0,u=0;
  const double now=badTime==0?tick*.05-.1:(badTime==1?tick*.05+.3:NAN);
  BotCecilSafeMotion(&player,s,now,f,st,u,0,1,true);
  check(!s.patrolAlternate&&f==0&&st==0,"alternate rewind gap or nonfinite clock cannot retain episode authority");
 }
}
void patrolAlternate46Search(){
 // A suffix that simply returns via the failed edge is not a bypass.
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;auto& g=BotSupplyGraph();
  g.points[2].links={0};g.points[3].links={0};const auto move=hopCheckpoint45Tick(tick);
  check(s.patrolAlternate&&s.patrolHint<0&&move.forward==0&&move.strafe==0,
   "different original hint whose directed suffix reuses failed edge cannot claim recovery");
  check((s.patrolTried[0]&4)!=0&&(s.patrolTried[0]&8)==0,
   "at most one newly LOS clear suffix search rejects one candidate in a frame");
  hopCheckpoint45Tick(tick+1);check(s.patrolAlternate&&(s.patrolTried[0]&12)==12,
   "second rejected suffix gets its separate next-frame search before sweep exhaustion");
  hopCheckpoint45Tick(tick+2);check(!s.patrolAlternate&&s.goal<0,
   "only fully exhausted finite suffix sweep terminates failed patrol attempt");
 }
 {const int tick=patrolAlternate46Enter(6,1)+1;auto& s=BotSupplyState(0);s.scanTick=99999;blockedItems=3;
  const int before=rayCount;const auto first=hopCheckpoint45Tick(tick);
  check(s.patrolAlternate&&s.goal==1&&rayCount-before==3&&!first.active,
   "three physical LOS rejections leave later eligible candidates for a later frame");
  const auto next=hopCheckpoint45Tick(tick+1);
  check(s.patrolAlternate&&s.patrolHint==5&&next.active&&std::hypot(next.forward,next.strafe)>.15,
   "fourth original candidate gets fair bounded next-frame opportunity after first three blocked LOS");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  const int before=rayCount;const auto defer=hopCheckpoint45Tick(tick,true,2);
  check(s.patrolAlternate&&s.patrolHint<0&&s.patrolTried[0]==0&&rayCount==before&&defer.forward==0,
   "reserved-budget deferral neither blacklists candidate nor falsely exhausts sweep");
  const auto go=hopCheckpoint45Tick(tick+1);
  check(s.patrolHint==2&&go.active&&std::hypot(go.forward,go.strafe)>.15,
   "deferred candidate can pass fresh LOS suffix and final probes next frame");
  s.goals.Run(BotSupplyGraph(),1,s.blocked.data(),s.blocked.size());
  const auto cached=hopCheckpoint45Tick(tick+2);
  check(s.patrolHint==2&&cached.active&&std::hypot(cached.forward,cached.strafe)>.15,
   "dedicated prepared suffix survives ordinary goal-search parent overwrite");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  hopCheckpoint45Tick(tick);s.avoidNode=3;s.avoidUntil=100;
  const auto locked=hopCheckpoint45Tick(tick+1);
  check(s.patrolHint<0&&locked.forward==0&&locked.strafe==0,
   "current blocked intermediate invalidates cached finite suffix before guidance");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  allocations=0;measuring=true;const auto go=hopCheckpoint45Tick(tick);measuring=false;
  check(go.active&&allocations==0,"prepared alternative ranking suffix and safety allocate no heap during accepted tick");
 }
}

void patrolAlternate46ExtraGuards(){
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  s.reacquireRejected=2;s.reacquireRetryAfter=100;
  const auto move=hopCheckpoint45Tick(tick);
  check(s.patrolHint!=2&&move.active,"active original recovery rejection backoff excludes its node from alternate selection");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  _botRayBudget=16;const auto proposal=BotSupplyTick(&player,0,tick,1000);
  double f=proposal.forward,st=proposal.strafe,u=proposal.up;const int rays=rayCount;
  BotCecilSafeMotion(&player,s,tick*.05+.05,f,st,u,0,1,true);
  check(f==0&&st==0&&u==0&&rayCount==rays,"stale alternative proposal never authorizes even a single final ray or action");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  _botRayBudget=16;const auto proposal=BotSupplyTick(&player,0,tick,1000);
  player.en_penReference=nullptr;double f=proposal.forward,st=proposal.strafe,u=proposal.up;const int rays=rayCount;
  BotCecilSafeMotion(&player,s,tick*.05,f,st,u,0,1,true);
  check(f==0&&st==0&&u==0&&rayCount==rays,"support lost after alternative proposal cannot emit from remembered static authority");
 }
}

void patrolAlternate46Metadata(){
 for(int invalid=0;invalid<9;++invalid){
  const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;auto& p=BotSupplyGraph().points[2];
  switch(invalid){
   case 0:p.flags=botcore::CECIL_JUMP;break;
   case 1:p.flags=botcore::CECIL_UNREACHABLE;break;
   case 2:p.important_entity=77;break;
   case 3:p.lock_entity=77;break;
   case 4:p.z=-33;break;
   case 5:p.y=8.01f;break;
   case 6:p.radius=0;break;
   case 7:s.reacquireTried[0]|=4;break;
   case 8:s.reacquireRejected=2;s.reacquireRetryAfter=tick*.05+6;break;
  }
  const auto move=hopCheckpoint45Tick(tick);
  check(s.patrolAlternate&&s.patrolHint==3&&move.active&&std::hypot(move.forward,move.strafe)>.15,
   "alternate hints respect original flags important locks 32m 8height radius tried and live rejection metadata");
 }
 {const int tick=patrolAlternate46Enter(5,2)+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  const auto move=hopCheckpoint45Tick(tick);
  check(s.goal==4&&s.patrolAlternate&&s.patrolHint==2&&move.active,
   "remote patrol goal flags do not exclude a current ordinary failed edge or rewrite that goal");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;invalidHitDistance=true;
  hopCheckpoint45Tick(tick);check(s.patrolAlternate&&s.patrolTried[0]==0&&s.patrolHint<0,
   "invalid physical LOS result cannot blacklist a candidate as a real geometric failure");
 }
 {patrolAlternate46Fixture();auto& s=BotSupplyState(0);int tick=2;
  for(;tick<200&&hopCheckpointEvents==0;++tick){patrolAlternate46Pose(tick);hopCheckpoint45Tick(tick);}
  check(s.patrolStrikes==1,"real first checkpoint establishes one durable failed-edge strike");
  player.pl.pl_PositionVector=FLOAT3D(0,0,-16);s.scanTick=tick;hopCheckpoint45Tick(tick);
  check(s.patrolSource<0&&!s.patrolAlternate&&s.anchor==2&&s.hop==3,
   "actual relocation onto a different original directed route clears old failed-edge strikes");
 }
 {patrolAlternate46Fixture();auto& g=BotSupplyGraph();auto& s=BotSupplyState(0);
  for(auto& p:g.points){const float x=p.x;p.x=-p.y;p.y=x;}
  player.en_vGravityDir=FLOAT3D(1,0,0);player.body.m[0][0]=0;player.body.m[0][1]=-1;player.body.m[1][0]=1;player.body.m[1][1]=0;
  floorPlane.bpl_plAbsolute=FLOAT3D(-1,0,0);s.navigator.Reset();bool moved=false;
  for(int tick=2;tick<300;++tick){
   patrolAlternate46Pose(tick);const auto p=player.pl.pl_PositionVector;player.pl.pl_PositionVector=FLOAT3D(-p(2),p(1),p(3));
   const auto move=hopCheckpoint45Tick(tick);
   if(s.patrolAlternate&&move.active&&std::hypot(move.forward,move.strafe)>.15){moved=true;break;}
  }
  check(moved&&s.patrolHint==2&&s.anchor==0&&s.goal==1,
   "alternative bounds guidance and mandatory floor use actual rotated gravity without world-up assumptions");
 }
}
void patrolAlternate46Exit(){
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  // Real acquisition can precede original radius arrival. It must not become a fake reached point.
  player.pl.pl_PositionVector=FLOAT3D(0,0,-10);s.scanTick=tick;const auto acquire=hopCheckpoint45Tick(tick);
  check(!s.patrolAlternate&&s.anchor==2&&s.goal==1&&s.hop==2&&acquire.active,
   "fresh ordinary alternative acquisition ends episode but navigator still approaches original hint radius");
  player.pl.pl_PositionVector=FLOAT3D(0,0,-15.5);const auto reached=hopCheckpoint45Tick(tick+1);
  check(s.hop==3&&s.anchor==2&&s.goal==1&&reached.active,
   "only actual original-radius arrival at acquired alternative advances to its directed next edge");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  player.pl.pl_PositionVector=FLOAT3D(20,6,0);const auto arrived=hopCheckpoint45Tick(tick,true,0);
  check(!s.patrolAlternate&&s.patrolSource<0&&arrived.forward==0&&arrived.strafe==0&&s.goal==1,
   "actual original failed-hop arrival ends alternate episode even without nearest scan budget");
 }
 {const int tick=patrolAlternate46Enter();auto& s=BotSupplyState(0);const double since=s.patrolSince;bool kept=true;
  for(int next=tick+1;next<tick+120;++next){player.en_penReference=next%2?nullptr:&floorEntity;s.scanTick=next;
   hopCheckpoint45Tick(next,true,next%3?2:16);kept&=s.patrolAlternate&&s.patrolSince==since&&s.goal==1&&s.anchor==0;}
  check(kept,"support scan hint and budget changes do not renew fixed six second alternate attempt");
  hopCheckpoint45Tick(tick+120);check(!s.patrolAlternate&&s.goal<0&&s.goalEntity==0,
   "six second unsuccessful patrol attempt explicitly ends without fabricating recovery or item success");
 }
 {const int tick=patrolAlternate46Enter()+1;auto& s=BotSupplyState(0);s.scanTick=99999;
  auto& g=BotSupplyGraph();g.points[2].flags=botcore::CECIL_JUMP;g.points[3].important_entity=77;
  const auto failed=hopCheckpoint45Tick(tick);check(s.goal<0&&!s.patrolAlternate&&!failed.active,
   "complete absence of eligible ordinary hints fails only this patrol goal explicitly");
 }
}

//047 separates passive committed-hop history from current ground authority.
void hopCheckpoint47Passive(){
 for(int mode=0;mode<2;++mode){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;bool expiredInAir=false;int first=-1;
  for(int tick=2;tick<=145;++tick){
   hopCheckpoint45Wiggle(tick);
   // Real20Hz accepted Tick+Safety. NativeFALL need not imply new edge/life.
   player.m_pstState=(mode==0?(tick%80>=32&&tick%80<=44):(tick<=121))?PST_FALL:PST_STAND;
   hopCheckpoint45Tick(tick);
   if(player.m_pstState==PST_FALL){
    expiredInAir|=tick>=102&&s.hopCheckpointSince>=0&&s.hopCheckpointSince<=.15;
    check(hopCheckpointEvents==0,"passive FALL never authorizes grounded checkpoint even with nonNULL static reference");
   }
   if(hopCheckpointEvents){first=tick;break;}
  }
  check(first>=102&&first<=142,"accepted20Hz FALL intervals retain five-second committed-hop history until actual grounded fresh LOS");
  if(mode==1)check(expiredInAir,"fully airborne expired history is observed but has no checkpoint authority");
  check(s.goal==2&&s.goalSince==7&&s.goalDeadline==47&&!s.goalRelocationBudgeted,
   "passive FALL history never extends original item or patrol goal lifetime");
 }
 // Real pureNavigator STUCK is an existing .5s action, not a changed hop.
 hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=99999;
 player.pl.pl_PositionVector=FLOAT3D(-11.821f,-64.496f,-60.495f);
 bool sawStuck=false,preserved=false;
 for(int tick=2;tick<=47;++tick){
  _botRayBudget=16;const auto move=BotSupplyTick(&player,0,tick,1000);
  const bool stuck=!s.currentNavTravel&&s.currentNavGoal==2&&s.currentNavTime==tick*.05&&s.navigator.SourceSlot(2)==0&&s.hop==1;
  double f=move.forward,st=move.strafe,u=move.up;BotCecilSafeMotion(&player,s,tick*.05,f,st,u,0,1,true);
  if(stuck){sawStuck=true;preserved|=s.hopCheckpointSince>=0&&s.hopCheckpointSince<=.15&&near(s.hopCheckpointLast,tick*.05);}
 }
 check(sawStuck,"stationary actual navigator fixture reaches its real STUCK interval on the unchanged committed edge");
 check(preserved,"existing navigator STUCK interval preserves passive committed-hop history without checkpoint authority");
 check(hopCheckpointEvents==0,"currentNavTravel false STUCK cannot authorize a checkpoint despite preserved observation");
}
void patrolAlternate47Passive(){
 patrolAlternate46Fixture();auto& s=BotSupplyState(0);int first=-1,entered=-1;bool retained=false,sourceApproach=false;
 for(int tick=2;tick<=360;++tick){
  patrolAlternate46Pose(tick);player.m_pstState=tick%80>=32&&tick%80<=44?PST_FALL:PST_STAND;
  const bool approached=s.hop==0;
  hopCheckpoint45Tick(tick);
  if(hopCheckpointEvents&&first<0)first=tick;
  if(first>=0&&player.m_pstState==PST_FALL)retained|=s.patrolStrikes==1&&s.patrolSource==0&&s.patrolHop==1;
  sourceApproach|=first>=0&&approached;
  if(s.patrolAlternate){entered=tick;break;}
 }
 check(first>=102&&retained&&sourceApproach,"two-strike history survives real source reapproach and later passive FALL");
 check(entered>first&&hopCheckpointEvents>=2,"second actual accepted checkpoint can enter fixed alternate episode across repeated FALL");
 if(!s.patrolAlternate)return;
 const double since=s.patrolSince;const int tick=entered+1;
 player.m_pstState=PST_FALL;s.scanTick=99999;const int rays=rayCount;
 _botRayBudget=16;const auto air=BotSupplyTick(&player,0,tick,1000);double f=.3,st=0,u=0;
 BotCecilSafeMotion(&player,s,tick*.05,f,st,u,0,1,true);
 check(s.patrolAlternate&&s.patrolSince==since&&s.goal==1&&s.anchor==0,
  "active alternate FALL pauses action but preserves original episode deadline and real anchor goal");
 check(!air.active&&f==0&&st==0&&u==0&&rayCount==rays,
  "passive alternate FALL with nonNULL static ref authorizes no hint query wall floor or remembered motion");
 player.m_pstState=PST_STAND;const auto grounded=hopCheckpoint45Tick(tick+1);
 check(s.patrolAlternate&&s.patrolSince==since&&grounded.active&&std::hypot(grounded.forward,grounded.strafe)>.15,
  "return to current proved ground resumes freshly tested alternate movement without renewed deadline");
 check(s.probe.wallRays==1&&s.probe.floorRays==1,"resumed alternate action still needs mandatory fresh wall and floor");
}

void patrolObservation47Freshness(){
 for(int defect=0;defect<3;++defect){
  patrolAlternate46Fixture();auto& s=BotSupplyState(0);int tick=2;
  for(;tick<180&&!hopCheckpointEvents;++tick){patrolAlternate46Pose(tick);hopCheckpoint45Tick(tick);}
  check(s.patrolStrikes==1,"freshness guard begins after one genuine accepted checkpoint");
  player.pl.pl_PositionVector=FLOAT3D(.25f,0,0);_botRayBudget=16;BotSupplyTick(&player,0,tick,1000);
  check(s.navigator.SourceSlot(1)==0&&s.hop==1,"freshness counterexample keeps the genuine committed original edge");
  if(defect==0)s.currentNavTime=NAN;
  if(defect==1)s.currentNavTime-=.05;
  if(defect==2)s.currentNavGoal=-1;
  BotCecilPatrolObserve(&player,s,tick*.05,true);
  check(s.patrolStrikes==0&&s.patrolSource<0,
   "nonfinite stale or wrong-goal derived navigation stamp cannot preserve failed-edge strikes");
 }
}

void hopCheckpoint45Guards(){
 // Positive control: expiry cancels only the old movement context, not the goal.
 hopCheckpoint45Fixture();auto& held=BotSupplyState(0);held.scanTick=2;
 for(int tick=2;tick<102;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 held.escapeUntil=9;held.escapeWorld[0]=.4;held.RejectItem(888,1);held.worldLock[0]=0;
 hopCheckpoint45Wiggle(102);const auto reset=hopCheckpoint45Tick(102);
 check(hopCheckpointEvents==1&&reset.forward==0&&reset.strafe==0&&reset.up==0&&held.escapeUntil==0,
  "fresh accepted checkpoint emits neutral and cancels legacy world-held side motion");
 check(held.goal==2&&held.goalSince==7&&held.goalDeadline==47&&held.ItemRejected(888,5.1)&&held.worldLock[0]==0,
  "checkpoint leaves item attempt rejection and physical locks intact");
 // Existing world displacement need not be small: continuous real best gain wins.
 for(int vertical=0;vertical<2;++vertical){
  hopCheckpoint45Fixture();auto& g=BotSupplyGraph();auto& state=BotSupplyState(0);
  g.points[0].x=g.points[0].y=g.points[0].z=0;
  g.points[1].x=vertical?10:0;g.points[1].y=vertical?100:0;g.points[1].z=vertical?0:-100;
  g.points[2].x=10;g.points[2].y=100;g.points[2].z=-120;
  state.ClearGoal();state.goal=2;state.scanTick=2;player.pl.pl_PositionVector=FLOAT3D(0,0,0);
  bool committed=true;
  for(int tick=2;tick<=202;++tick){
   if(vertical)player.pl.pl_PositionVector(2)=float((tick-2)*.01);
   else player.pl.pl_PositionVector(3)=float(-(tick-2)*.05);
   hopCheckpoint45Tick(tick);committed&=state.navigator.SourceSlot(2)==0&&state.hop==1;
  }
  check(hopCheckpointEvents==0&&committed,vertical?
   "actual vertical gain keeps a normal directed approach committed beyond five seconds":
   "small cumulative monotonic best-distance gain preserves the long committed edge");
 }
 for(int invalid=0;invalid<23;++invalid){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);auto& graph=BotSupplyGraph();s.scanTick=2;CWorld foreign;
  for(int tick=2;tick<=145;++tick){
   hopCheckpoint45Wiggle(tick);
   if(invalid==0)player.m_pstState=PST_FALL;
   if(invalid==1)player.m_pstState=PST_SWIM;
   if(invalid==2)player.m_pstState=PST_DIVE;
   if(invalid==3)player.en_penReference=nullptr;
   if(invalid==4)floorEntity.cls.name="Classes/MovingBrush.ecl";
   if(invalid==5)floorEntity.entityPhysicsFlags=EPF_MOVABLE;
   if(invalid==6)floorEntity.flags=ENF_DELETED;
   if(invalid==7)floorEntity.type=CEntity::RT_MODEL;
   if(invalid==8)floorEntity.en_pwoWorld=&foreign;
   if(invalid==9)floorEntity.cls.name="Classes/WorldBaseFake.ecl";
   if(invalid==10){s.importantGoal=true;graph.points[1].flags=botcore::CECIL_IMPORTANT;}
   if(invalid==11)s.interactionPoint=1;
   if(invalid==12)s.useReleaseTick=999;
   if(invalid==13)graph.points[0].flags=botcore::CECIL_TELEPORT;
   if(invalid==14)graph.points[1].flags=botcore::CECIL_UNREACHABLE;
   if(invalid==15)graph.points[0].flags=botcore::CECIL_IMPORTANT;
   if(invalid==16)graph.points[1].flags=botcore::CECIL_JUMP;
   if(invalid==17)graph.points[0].important_entity=777;
   if(invalid==18)graph.points[1].important_entity=777;
   if(invalid==19)graph.points[0].lock_entity=777;
   if(invalid==20)graph.points[1].lock_entity=777;
   if(invalid==21)player.en_vCurrentTranslationAbsolute(2)=std::numeric_limits<float>::quiet_NaN();
   hopCheckpoint45Tick(tick,invalid!=22);
  }
  check(hopCheckpointEvents==0,"air moving unknown foreign special USE lock invalid or Human context cannot acquire a ground checkpoint");
 }
 // Current-hop high stay, not the remote goal's flags, remains intentional.
 hopCheckpoint45Fixture();auto& stay=BotSupplyState(0);stay.scanTick=2;
 auto& high=BotSupplyGraph().points[1];high.x=-11.821f;high.z=-60.495f;
 player.pl.pl_PositionVector=FLOAT3D(high.x,-64.496f,high.z);
 for(int tick=2;tick<=130;++tick)hopCheckpoint45Tick(tick);
 check(hopCheckpointEvents==0,"original horizontal high-stay instruction cannot be overridden by checkpoint");
 // Loss of final owner must restart the whole accepted observation interval.
 hopCheckpoint45Fixture();auto& owner=BotSupplyState(0);owner.scanTick=2;
 for(int tick=2;tick<=100;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 hopCheckpoint45Wiggle(101);hopCheckpoint45Tick(101,false);
 for(int tick=102;tick<202;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 check(hopCheckpointEvents==0,"Human ownership gap erases accumulated five-second edge observation");
 hopCheckpoint45Wiggle(202);hopCheckpoint45Tick(202);
 check(hopCheckpointEvents==1,"five new accepted seconds and fresh normal acquisition authorize later checkpoint");
 // Context gaps, generation changes and goal clears cannot carry old edge time.
 for(int loss=0;loss<4;++loss){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;
  for(int tick=2;tick<=100;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
  int next=101;
  if(loss==0)next=110;
  if(loss==1)++s.generation;
  if(loss==2){s.ClearGoal();s.goal=2;s.goalSince=9;s.scanTick=101;}
  if(loss==3){player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;}
  for(int tick=next;tick<next+95;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
  check(hopCheckpointEvents==0,"time gap life goal or gravity change cannot reuse prior checkpoint time");
 }
 // No hidden allocation or ray/World query is added to the final checkpoint guard.
 hopCheckpoint45Fixture();auto& bounded=BotSupplyState(0);bounded.scanTick=2;
 for(int tick=2;tick<102;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 hopCheckpoint45Wiggle(102);_botRayBudget=16;auto m=BotSupplyTick(&player,0,102,1000);
 const int casts=rayCount,lookups=worldLookups;double f=m.forward,st=m.strafe,u=m.up;allocations=0;measuring=true;
 BotCecilSafeMotion(&player,bounded,5.1,f,st,u,0,1,true);measuring=false;
 check(hopCheckpointEvents==1&&rayCount==casts&&worldLookups==lookups&&allocations==0,
  "actual fresh expiry performs no extra cast World lookup or heap allocation");
}
void hopCheckpoint45Deferral(){
 for(int denied=0;denied<2;++denied){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);s.scanTick=2;
  for(int tick=2;tick<=121;++tick){
   hopCheckpoint45Wiggle(tick);wallMode=denied==0&&tick==102?2:0;
   hopCheckpoint45Tick(tick,true,denied==1&&tick==102?2:16);
  }
  check(hopCheckpointEvents==0&&s.navigator.SourceSlot(2)==0&&s.hop==1,
   "expired checkpoint waits through actual nearest LOS or budget denial without discarding edge");
  wallMode=0;hopCheckpoint45Wiggle(122);hopCheckpoint45Tick(122);
  check(hopCheckpointEvents==1&&s.hop==-1,
   "later regular successful acquisition grants deferred checkpoint without renewing the five-second clock");
 }
 hopCheckpoint45Fixture();auto& g=BotSupplyGraph();auto& s=BotSupplyState(0);
 g.points[0].x=g.points[0].y=g.points[0].z=0;g.points[1].x=g.points[1].y=0;g.points[1].z=-100;
 s.ClearGoal();s.goal=2;s.scanTick=2;player.pl.pl_PositionVector=FLOAT3D(0,0,0);hopCheckpoint45Tick(2);
 for(int tick=3;tick<=143;++tick){player.pl.pl_PositionVector(3)=((tick-3)/20)%3==1?-7:-5;hopCheckpoint45Tick(tick);}
 check(hopCheckpointEvents==1,
  "returning to an old best distance after moving away cannot refresh the progress checkpoint");
 // Invalid final-frame inputs erase the accumulated clock, even before the helper.
 hopCheckpoint45Fixture();auto& invalid=BotSupplyState(0);invalid.scanTick=2;
 for(int tick=2;tick<=100;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 double f=.2,st=0,u=0;BotCecilSafeMotion(&player,invalid,5.05,f,st,u,0,std::numeric_limits<double>::quiet_NaN(),true);
 for(int tick=102;tick<=200;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 check(hopCheckpointEvents==0,"invalid final safety frame cannot preserve an old edge-progress clock");
 hopCheckpoint45Fixture();auto& dead=BotSupplyState(0);dead.scanTick=2;
 for(int tick=2;tick<=100;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 player.health=0;hopCheckpoint45Tick(101);player.health=100;
 check(dead.goal<0&&dead.navigator.SourceSlot(2)<0,
  "actual death clears route checkpoint with the ordinary lifecycle context");
}
void hopCheckpoint45ItemDeadline(){
 hopCheckpoint45Fixture();auto& s=BotSupplyState(0);const auto& goal=BotSupplyGraph().points[2];
 auto& item=addItem(991,goal.x,goal.z,botcore::CecilItemKind::Weapon);item.item.weapon=4;item.pl.pl_PositionVector(2)=goal.y;
 s.goalEntity=991;s.goalSince=0;s.goalDeadline=12;s.scanTick=2;
 for(int tick=2;tick<=102;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 check(hopCheckpointEvents==1&&s.goalEntity==991&&s.goalSince==0&&s.goalDeadline==12&&!s.goalRelocationBudgeted,
  "actual live ordinary weapon checkpoint preserves its original twelve-second attempt deadline");
 for(int tick=103;tick<=240;++tick){hopCheckpoint45Wiggle(tick);hopCheckpoint45Tick(tick);}
 check(endEvents==1&&std::strcmp(lastEnd,"timeout")==0&&s.goalEntity!=991&&s.ItemRejected(991,12),
  "actual original ordinary timeout still ends and rejects the attempt after navigator checkpoint");
}
void hopCheckpoint45Arrival(){
 hopCheckpoint45Fixture();auto& graph=BotSupplyGraph();auto& s=BotSupplyState(0);
 graph.points[0].links={2};graph.points[2].flags=0;
 s.ClearGoal();s.goal=2;s.scanTick=99999;
 player.pl.pl_PositionVector=FLOAT3D(graph.points[0].x,graph.points[0].y,graph.points[0].z);
 hopCheckpoint45Tick(2);
 auto& item=addItem(991,graph.points[2].x+4,graph.points[2].z,botcore::CecilItemKind::Weapon);
 item.item.weapon=4;item.pl.pl_PositionVector(2)=graph.points[2].y;
 s.goalEntity=991;s.goalSince=0;s.goalDeadline=12;s.scanTick=3;
 bool retained=true;
 for(int tick=3;tick<=150;++tick){
  player.pl.pl_PositionVector=FLOAT3D(graph.points[2].x,graph.points[2].y,graph.points[2].z+float(((tick-3)/20)%3));
  hopCheckpoint45Tick(tick);retained&=s.goalEntity==991;
 }
 check(hopCheckpointEvents==0&&retained,
  "actual original-radius arrival and live final item connector are not a stuck directed edge");
}
void groundedReplanFixture(){
 setup(4);auto& g=BotSupplyGraph();
 const float p[4][3]={{71,1,63},{63,1,63},{63.0233955f,38.367321f,63.126381f},{67.5f,36.5f,63.25f}};
 for(int i=0;i<4;++i){g.points[i].x=p[i][0];g.points[i].y=p[i][1];g.points[i].z=p[i][2];g.points[i].radius=i==0?3:(i==1?4:1);g.points[i].links.clear();}
 g.points[0].links={1};g.points[1].links={2};g.points[2].links={3};g.points[3].links={2};
 auto& item=addItem(311,67.5f,63,botcore::CecilItemKind::Weapon);item.item.weapon=14;item.pl.pl_PositionVector(2)=36.001f;
 auto& s=BotSupplyState(0);s.goal=3;s.goalEntity=311;s.goalSince=0;s.goalDeadline=12;s.scanTick=99999;s.anchor=2;
 player.pl.pl_PositionVector=FLOAT3D(p[2][0],p[2][1],p[2][2]);player.m_pstState=PST_FALL;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 player.pl.pl_PositionVector=FLOAT3D(67.431f,.378f,63.419f);player.m_pstState=PST_STAND;
 floorEntity.en_ulID=1;floorEntity.type=CEntity::RT_BRUSH;floorEntity.cls.name="Classes/WorldBase.ecl";
 player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 s.anchor=0;s.RejectItem(999,.05);s.worldLock[1]=0;
}
SCecilMove groundedReplanHold(int budget=16){
 SCecilMove move;for(int tick=2;tick<=43;++tick){_botRayBudget=budget;move=BotSupplyTick(&player,0,tick,1000);}return move;
}
void groundedReplanGuards(){
 groundedReplanFixture();auto& s=BotSupplyState(0);const auto move=groundedReplanHold();
 check(s.goalEntity==311&&endEvents==0&&groundReplanEvents==1&&!s.ItemRejected(311,2.15),"measured grounded Cannon landing retains the real attempt instead of unreachable_hold failure");
 check(move.active&&s.hop==0&&std::hypot(move.forward,move.strafe)>0,"fresh floor hint outside its original radius is approached after failed air edge reset");
 check(s.goalSince==0&&s.goalDeadline==12&&!s.goalRelocationBudgeted&&s.ItemRejected(999,2.15)&&s.worldLock[1]==0,
   "grounded route reacquisition preserves deadline rejection and lock state without relocation extension");
 for(int i=0;i<3;++i){const auto& point=BotSupplyGraph().points[i];player.pl.pl_PositionVector=FLOAT3D(point.x,point.y,point.z);s.anchor=i;_botRayBudget=16;
   const auto next=BotSupplyTick(&player,0,44+i,1000);check(next.active&&s.hop==i+1,"only original radius arrival advances floor launcher and high source route");}
 groundedReplanFixture();player.pl.pl_PositionVector=FLOAT3D(67.512f,.378f,64.154f);player.m_pstState=PST_CROUCH;
 groundedReplanHold();check(BotSupplyState(0).goalEntity==311&&BotSupplyState(0).hop==0,"second native Cannon landing also reacquires while crouched");
 for(int n=0;n<32;++n){
  groundedReplanFixture();auto& state=BotSupplyState(0);
  if(n==0)player.m_pstState=PST_FALL;
  if(n==1)player.m_pstState=PST_SWIM;
  if(n==2)player.en_penReference=nullptr;
  if(n==3)floorEntity.flags=ENF_DELETED;
  if(n==4)floorEntity.type=CEntity::RT_MODEL;
  if(n==5)floorEntity.cls.name="Classes/MovingBrush.ecl";
  if(n==6)player.world.wo_cenEntities.erase(player.world.wo_cenEntities.end()-1);
  if(n==7)player.en_vCurrentTranslationAbsolute(1)=NAN;
  if(n==8)player.en_vCurrentTranslationAbsolute(3)=.101f;
  if(n==9)state.importantGoal=true;
  if(n==10)BotSupplyGraph().points[2].flags=botcore::CECIL_UNREACHABLE;
  if(n==11)BotSupplyGraph().points[2].flags=botcore::CECIL_TELEPORT;
  if(n==12)BotSupplyGraph().points[0].flags=botcore::CECIL_UNREACHABLE;
  if(n==13)BotSupplyGraph().points[2].y=1; // A legitimate ground launch source is not a failed air edge.
  if(n==14)BotSupplyGraph().points[0].links.clear();
  if(n==15)wallMode=2;
  if(n==16)state.useReleaseTick=10000;
  if(n==17){state.avoidNode=0;state.avoidUntil=100;}
  if(n==18)state.anchor=2;
  if(n==19)player.en_vCurrentTranslationAbsolute=FLOAT3D(.08f,.08f,0);
  if(n==20)floorEntity.cls.name="Classes/WorldBaseFake.ecl";
  if(n==21){player.hasWorld=false;botcore::CecilMotion denied;denied.active=true;denied.hop=3;
   check(!BotCecilGroundedReplan(&player,state,denied,0,42),"grounded helper rejects missing world before any lookup");continue;}
  if(n==22)BotSupplyGraph().points[2].flags=botcore::CECIL_IMPORTANT;
  if(n==23)BotSupplyGraph().points[3].flags=botcore::CECIL_TELEPORT;
  if(n==24)BotSupplyGraph().points[3].y=4;
  if(n==25)BotSupplyGraph().points[0].y=5;
  if(n==26){state.avoidNode=3;state.avoidUntil=100;}
  if(n==27)state.interactionPoint=2;
  if(n==28)state.navigator.Reset();
  if(n==29)state.goal=2;
  if(n==30){BotSupplyGraph().points[3].flags=botcore::CECIL_UNREACHABLE;
   player.pl.pl_PositionVector=FLOAT3D(63.0233955f,.378f,63.126381f);state.anchor=1;BotSupplyGraph().points[1].radius=.1f;}
  if(n==31)player.en_plViewpoint.pl_OrientationAngle(1)=NAN;
  groundedReplanHold();check(groundReplanEvents==0,"unknown moving liquid invalid special disconnected or stale anchor context cannot rebase high edge");
 }
 groundedReplanFixture();groundedReplanHold(2);check(BotSupplyState(0).goalEntity!=311||BotSupplyState(0).hop!=0,"missing shared connector budget never authorizes grounded rebase");
 groundedReplanFixture();bool bounded=true;for(int tick=2;tick<=43;++tick){_botRayBudget=16;const int before=rayCount;BotSupplyTick(&player,0,tick,1000);bounded&=rayCount-before<=16&&_botRayBudget>=2;}
 check(bounded,"grounded acquisition uses shared ray budget and preserves final two safety probes");
 groundedReplanFixture();SCecilMove reset;
 for(int tick=2;tick<=42;++tick){_botRayBudget=16;reset=BotSupplyTick(&player,0,tick,1000);}
 check(groundReplanEvents==1&&owns(reset,0)&&!reset.active&&reset.forward==0&&reset.strafe==0&&reset.up==0&&
   BotSupplyState(0).hop==-1&&BotSupplyState(0).currentNavTime<0&&BotSupplyState(0).currentNavGoal==-1&&BotSupplyState(0).heldNode==-1,
   "rebase occurs at unchanged two second boundary with owned neutral and no stale current-point exemption");
 double f=.5,st=0,u=0;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),2.1,f,st,u,0,1,true)==0&&f==0&&st==0&&u==0,
   "final floor veto still applies immediately after grounded navigator reset");
 groundedReplanFixture();groundedReplanHold();_botRayBudget=16;BotSupplyTick(&player,0,241,1000);
 check(endEvents==1&&std::strcmp(lastEnd,"timeout")==0,"original item lifetime still expires after grounded rebase without renewal");
 groundedReplanFixture();allocations=0;measuring=true;groundedReplanHold();measuring=false;
 check(allocations==0,"grounded rebase performs no per-tick heap allocation");
 groundedReplanFixture();player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 for(auto& point:BotSupplyGraph().points)point.y=-point.y;
 player.pl.pl_PositionVector(2)=-player.pl.pl_PositionVector(2);items[0].pl.pl_PositionVector(2)=-items[0].pl.pl_PositionVector(2);
 groundedReplanHold();check(groundReplanEvents==1&&BotSupplyState(0).goalEntity==311,"both high-point tests use actual gravity rather than world Y");
 groundedReplanFixture();BotSupplyReset(0);check(BotSupplyState(0).navigator.SourceSlot(3)==-1&&groundReplanEvents==0,
   "life or map reset discards the old committed source before another generation");
 groundedReplanFixture();player.health=0;_botRayBudget=16;BotSupplyTick(&player,0,42,1000);
 check(groundReplanEvents==0&&BotSupplyState(0).goalEntity==0,"death cannot preserve or reacquire an old airborne goal");
}

// Real040diag no-candidate bubble: the nearest ORIGINAL point lies ~55m away.
void farHintFixture(){
 setup(296);auto& graph=BotSupplyGraph();auto& state=BotSupplyState(0);
 for(int i=0;i<296;++i){auto& point=graph.points[i];point.x=-200.f-i;point.y=-29.5f;point.z=-200;point.radius=1;point.links.clear();}
 graph.points[236].x=122;graph.points[236].z=80;graph.points[236].radius=8;
 graph.points[237].x=95;graph.points[237].z=80;
 player.pl.pl_PositionVector=FLOAT3D(149.522f,-29.998f,127.651f);player.en_ulID=1847;
 floorEntity.en_ulID=1;floorEntity.type=CEntity::RT_BRUSH;player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 floorMode=2;state.anchor=-1;state.scanTick=99999;state.generation=8;BotCecilSettings().bAvoidPits=0;_botRayBudget=16;
}
void farHintTests(){
 farHintFixture();auto& state=BotSupplyState(0);const auto move=BotSupplyTick(&player,0,1,1000);
 check(move.active&&owns(move,0)&&state.reacquireNode==236&&state.reacquiring&&state.anchor<0&&state.hop<0,
   "genuine proved ground no-local-point case selects nearest original55m hint without anchor or graph edge");
 check(rayCount==1&&_botRayBudget==15&&std::hypot(move.forward,move.strafe)<=.300001,
   "far hint uses existing single LOS budget and bounded proposal");
 double f=move.forward,st=move.strafe,u=move.up;
 check(BotCecilSafeMotion(&player,state,.05,f,st,u,move.yaw_delta,1)==1&&std::hypot(f,st)>.05&&std::hypot(f,st)<=.300001&&state.anchor<0,
   "far hint action must pass actual final wall and mandatory floor before bounded movement");
 const double fixedSince=state.reacquireSince;_botRayBudget=16;BotSupplyTick(&player,0,21,1000);
 check(state.reacquireNode==236&&state.reacquireSince==fixedSince,"held far hint preserves original six-second deadline");
 _botRayBudget=2;const auto postponed=BotSupplyTick(&player,0,22,1000);
 check(!postponed.active&&state.reacquireNode==236&&state.reacquireSince==fixedSince,
   "budget-deferred far hint preserves attempt rather than rejecting or renewing it");
 const auto original=BotSupplyGraph().points[236];botcore::CecilNavigator nav;nav.Prepare(296);
 botcore::CecilMotionInput in;in.alive=true;in.anchor=in.goal=236;in.x=149.522;in.y=-29.998;in.z=127.651;
 check(!nav.Update(BotSupplyGraph(),state.blocked.data(),state.blocked.size(),in).arrived,
   "far hint does not change original arrival into distant reached state");
 in.x=original.x;in.y=original.y;in.z=original.z+8.01;in.now=.05;
 check(!nav.Update(BotSupplyGraph(),state.blocked.data(),state.blocked.size(),in).arrived,
   "originalradius8 still rejects a physically outside far-hint arrival");
 in.z=original.z+7.99;in.now=.1;
 check(nav.Update(BotSupplyGraph(),state.blocked.data(),state.blocked.size(),in).arrived,
   "far hint arrival occurs only after physical pose enters unchanged originalradius");
}
void farHintGuards(){
 auto localPoint=[](float distance=20){auto& p=BotSupplyGraph().points[0];p.x=player.pl.pl_PositionVector(1)+distance;p.y=player.pl.pl_PositionVector(2);p.z=player.pl.pl_PositionVector(3);};
 for(int unavailable=0;unavailable<3;++unavailable){
  farHintFixture();localPoint();auto& state=BotSupplyState(0);
  if(unavailable==0)wallMode=2;
  else{
   state.reacquireScanTime=0;
   for(int axis=0;axis<3;++axis){state.reacquireScanPosition[axis]=player.pl.pl_PositionVector(axis+1);state.reacquireScanGravity[axis]=player.en_vGravityDir(axis+1);}
   if(unavailable==1)state.reacquireTried[0]=1;
   else{state.reacquireRejected=0;state.reacquireRetryAfter=10;}
  }
  bool noFar=true,bounded=true;
  for(int tick=1;tick<=3;++tick){const int casts=rayCount;_botRayBudget=16;const auto m=BotSupplyTick(&player,0,tick,1000);
   noFar&=m.active?state.reacquireNode==0:state.reacquireNode<0;bounded&=rayCount-casts<=1;}
  check(noFar&&bounded,"local geometry prevents FAR even when its LOS fails, tried bit is set or retry is deferred");
 }
 for(float distance:{32.f,32.01f}){
  farHintFixture();localPoint(distance);const auto m=BotSupplyTick(&player,0,1,1000);
  check(m.active&&BotSupplyState(0).reacquireNode==0&&rayCount==1,
    "inclusive32m local boundary and first farther point retain nearest original ranking");
 }
 for(float height:{8.f,8.01f}){
  farHintFixture();localPoint(1);BotSupplyGraph().points[0].y+=height;const auto m=BotSupplyTick(&player,0,1,1000);
  check(m.active&&BotSupplyState(0).reacquireNode==(height==8?0:236),
    "FAR geometric absence uses unchanged inclusive gravity-relative8m height bound");
 }
 // A cached far target yields immediately to local geometry, even if that local
 // target cannot currently pass LOS. Its old world escape must not survive.
 farHintFixture();BotSupplyTick(&player,0,1,1000);auto& switched=BotSupplyState(0);
 switched.escapeUntil=1;switched.escapeWorld[0]=.3;localPoint();wallMode=2;_botRayBudget=16;
 const auto localBlocked=BotSupplyTick(&player,0,2,1000);
 check(!localBlocked.active&&switched.reacquireNode<0&&switched.escapeUntil==0,
   "new local geometry invalidates cached far mode and its held escape despite blocked local LOS");
 farHintFixture();BotSupplyTick(&player,0,1,1000);localPoint();_botRayBudget=16;
 check(BotSupplyTick(&player,0,2,1000).active&&BotSupplyState(0).reacquireNode==0,
   "new visible local geometry switches a cached far target back to the existing near path");
 farHintFixture();BotSupplyTick(&player,0,1,1000);const double initial=BotSupplyState(0).reacquireSince;
 _botRayBudget=16;BotSupplyTick(&player,0,101,1000);
 check(BotSupplyState(0).reacquireNode==236&&BotSupplyState(0).reacquireSince==initial,
   "repeated FAR revalidation never renews the six-second attempt");
 _botRayBudget=16;BotSupplyTick(&player,0,122,1000);
 check(BotSupplyState(0).reacquireNode==237&&BotSupplyState(0).reacquireRejected==236&&
   near(BotSupplyState(0).reacquireRetryAfter,12.1),"FAR target expires into unchanged six-second backoff and nearest alternative");
 _botRayBudget=16;BotSupplyTick(&player,0,244,1000);
 check(BotSupplyState(0).reacquireNode==236,"FAR target becomes eligible again after existing bounded retry");
 for(int budget:{0,1,2,3,4,5,16}){
  farHintFixture();_botRayBudget=budget;const auto m=BotSupplyTick(&player,0,1,1000);
  check(m.active==(budget>2)&&rayCount==(budget>2?1:0)&&_botRayBudget==budget-(budget>2?1:0),
    "FAR LOS cannot consume the last two shared safety rays at any initial budget");
 }
 farHintFixture();wallMode=2;_botRayBudget=5;const auto blocked=BotSupplyTick(&player,0,1,1000);
 check(!blocked.active&&rayCount==3&&_botRayBudget==2,"FAR blocked batch remains at most three LOS rays with two reserved");
 wallMode=0;_botRayBudget=16;const auto continued=BotSupplyTick(&player,0,2,1000);
 check(continued.active&&BotSupplyState(0).reacquireNode!=236,
   "FAR uses the existing bounded failed-LOS sweep rather than retrying nearest forever");
 farHintFixture();player.en_penReference=nullptr;_botRayBudget=16;
 check(!BotSupplyTick(&player,0,1,1000).active&&rayCount==1&&BotSupplyState(0).reacquireNode<0,
   "unknown NULL support cannot authorize a FAR hint");
 farHintFixture();player.en_penReference=nullptr;nearFootMode=2;_botRayBudget=4;
 check(BotSupplyTick(&player,0,1,1000).active&&BotSupplyState(0).reacquireNode==236&&nearFootRays==1&&rayCount==2&&_botRayBudget==2,
   "existing strictly verified NULL near-foot support may authorize FAR while retaining final safety reserve");
 for(int budget:{0,1,2,3}){
  farHintFixture();player.en_penReference=nullptr;nearFootMode=2;_botRayBudget=budget;
  check(!BotSupplyTick(&player,0,1,1000).active&&rayCount==0,
    "deferred NULL current-support budget never authorizes FAR from passive observation");
 }
 for(int invalid=0;invalid<13;++invalid){
  farHintFixture();
  if(invalid==0)player.m_pstState=PST_FALL;
  if(invalid==1)player.m_pstState=PST_DIVE;
  if(invalid==2)floorEntity.flags=ENF_DELETED;
  if(invalid==3)floorEntity.type=CEntity::RT_MODEL;
  if(invalid==4)player.world.wo_cenEntities.clear();
  if(invalid==5)player.en_vCurrentTranslationAbsolute(1)=NAN;
  if(invalid==6)player.en_vGravityDir=FLOAT3D(0,-2,0);
  if(invalid==7)player.body.m[0][0]=0;
  if(invalid==8)BotSupplyGraph().points[10].x=NAN;
  if(invalid==9)BotSupplyGraph().points[10].radius=0;
  if(invalid==10)BotSupplyState(0).blocked.pop_back();
  if(invalid==11)player.health=0;
  if(invalid==12)player.hasWorld=false;
  const auto m=BotSupplyTick(&player,0,1,1000);
  check(!m.active&&rayCount==0,"FAR refuses invalid graph/frame/lifecycle/medium/support instead of widening existing authority");
 }
 farHintFixture();player.m_pstState=PST_CROUCH;
 check(BotSupplyTick(&player,0,1,1000).active,"native proved CROUCH can select FAR under unchanged ground policy");
 farHintFixture();player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 check(BotSupplyTick(&player,0,1,1000).active,"FAR height and bounded proposal remain valid under actual inverted gravity frame");
 farHintFixture();CEntity lock;lock.en_ulID=990;player.world.wo_cenEntities.push_back(&lock);
 BotSupplyGraph().points[236].lock_entity=990;lock.pl.pl_PositionVector(1)=1;
 check(BotSupplyTick(&player,0,1,1000).active&&BotSupplyState(0).reacquireNode==237,
   "actual moved physical lock excludes closest FAR point without unlocking or fabricating arrival");
 farHintFixture();for(auto& point:BotSupplyGraph().points)point.lock_entity=991;
 check(!BotSupplyTick(&player,0,1,1000).active&&rayCount==0,"all physically missing locked FAR points remain blocked");
 farHintFixture();BotSupplyTick(&player,0,1,1000);auto& finalState=BotSupplyState(0);
 _botRayBudget=16;const auto current=BotSupplyTick(&player,0,2,1000);double f=current.forward,st=current.strafe,u=current.up;
 floorMode=0;const int veto=BotCecilSafeMotion(&player,finalState,.1,f,st,u,current.yaw_delta,1);
 check(veto==0&&f==0&&st==0&&u==0,"selected FAR hint cannot bypass the final actual floor veto");
 farHintFixture();bool bounded=true;allocations=0;measuring=true;
 for(int tick=1;tick<=270;++tick){const int before=rayCount;_botRayBudget=16;const auto m=BotSupplyTick(&player,0,tick,1000);
  bounded&=rayCount-before<=3&&_botRayBudget>=2&&std::hypot(m.forward,m.strafe)<=.300001;}
 measuring=false;check(bounded&&allocations==0,"FAR metadata and fixed three-cast batches allocate nothing across repeated lifecycle deadlines");
 setup(4096);auto& full=BotSupplyGraph();auto& sweep=BotSupplyState(0);
 sweep.anchor=-1;sweep.scanTick=99999;player.pl.pl_PositionVector=FLOAT3D(149,-30,127);
 floorEntity.en_ulID=1;floorEntity.type=CEntity::RT_BRUSH;player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 for(auto& point:full.points){point.x=189;point.y=-30;point.z=127;point.links.clear();}
 full.points[4095].x=220;blockedItems=200;bool fullBound=true;SCecilMove tail;allocations=0;measuring=true;
 for(int tick=1;tick<=1366;++tick){const int before=rayCount;_botRayBudget=16;tail=BotSupplyTick(&player,0,tick,1000);
  fullBound&=rayCount-before<=3&&_botRayBudget>=13;}
 measuring=false;
 check(tail.active&&sweep.reacquireNode==4095&&fullBound&&allocations==0,
   "FAR full4096-node failed-LOS prefix reaches final original point with fixed memory and at most3 rays");
 setup(4097);BotSupplyState(0).anchor=-1;BotSupplyState(0).scanTick=99999;
 floorEntity.en_ulID=1;floorEntity.type=CEntity::RT_BRUSH;player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 check(!BotSupplyTick(&player,0,1,1000).active&&rayCount==0,"FAR never admits a graph beyond4096 original points");
}
void groundProgressFixture(bool neutral=false){
 setup(1);auto& state=BotSupplyState(0);state.anchor=-1;state.scanTick=99999;
 BotSupplyGraph().points[0].z=neutral?-50:-20;
 // A neutral fixture needs no height-eligible hint, including the far fallback.
 if(neutral)BotSupplyGraph().points[0].y=20;
 player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_ulID=100;
 floorEntity.en_ulID=77;floorEntity.type=CEntity::RT_BRUSH;
 player.world.wo_cenEntities.push_back(&floorEntity);player.en_penReference=&floorEntity;
 floorMode=2;BotCecilSettings().bAvoidPits=1;
}
double groundF=0,groundSt=0,groundU=0;
int groundProgressTick(int tick,bool accepted=true,double maxStrafe=1,int budget=16){
 _botRayBudget=budget;const auto move=BotSupplyTick(&player,0,tick,1000);
 double f=move.forward,st=move.strafe,u=move.up;
 const int status=BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,move.yaw_delta,maxStrafe,accepted);
 groundF=f;groundSt=st;groundU=u;return status;
}

void airRecovery44Fixture(){
 setup(2);auto& state=BotSupplyState(0);state.anchor=-1;state.scanTick=99999;
 BotCecilSettings().bAvoidPits=0;player.en_ulID=100;player.en_penReference=nullptr;
 player.m_pstState=PST_FALL;player.pl.pl_PositionVector=FLOAT3D(0,-4.5f,0);
 player.en_vCurrentTranslationAbsolute=FLOAT3D(0,40,0);
 auto& graph=BotSupplyGraph();graph.points[0].x=20;graph.points[0].z=0;
 graph.points[1].x=30;graph.points[1].z=0;
 floorMode=0;
}
void airRecovery44(){
 airRecovery44Fixture();_botRayBudget=16;
 const auto move=BotSupplyTick(&player,0,1,1000);auto& state=BotSupplyState(0);
 check(move.active&&move.ownsMovement&&state.reacquireNode==0&&state.anchor<0&&state.goal<0&&state.hop<0,
  "NORMAL44 actual airborne Tick selects original directed-node hint without fabricating a NAV anchor");
 double f=move.forward,st=move.strafe,u=move.up;
 const int status=BotCecilSafeMotion(&player,state,.05,f,st,u,move.yaw_delta,1,true);
 check(status==1&&std::hypot(f,st)>.05&&std::hypot(f,st)<=.300001&&u==0&&state.probe.wallRays==1&&state.probe.floorRays==0,
  "NORMAL44 selected air hint becomes actual accepted wall-checked horizontal input without a ground-stall or floor claim");
 bool moving=true;const double since=state.reacquireSince;
 for(int tick=2;tick<=20;++tick){player.pl.pl_PositionVector(2)=-4.5f+.02f*tick;
  _botRayBudget=16;const auto m=BotSupplyTick(&player,0,tick,1000);f=m.forward;st=m.strafe;u=m.up;
  moving&=m.active&&BotCecilSafeMotion(&player,state,tick*.05,f,st,u,m.yaw_delta,1,true)==1&&std::hypot(f,st)>.05;
 }
 check(moving&&near(state.reacquireSince,since)&&!state.groundStalled&&state.groundRecoveryTime<0&&state.anchor<0,
  "NORMAL44 changing altitude receives current original-hint steering before two seconds without renewing attempt or entering ground watchdog");
 // Controlled fixture arrival tests acquisition, not unimplemented engine flight.
 player.pl.pl_PositionVector=FLOAT3D(19.5f,0,0);player.m_pstState=PST_STAND;
 state.scanTick=0;_botRayBudget=16;const auto routed=BotSupplyTick(&player,0,21,1000);
 check(state.anchor==0&&state.goal==1&&state.hop==1&&routed.active,
  "NORMAL44 later physical fixture arrival uses ordinary original directed NAV acquisition independently of the air proposal");
}

int airSafety44(const SCecilMove& m,int tick,bool accepted=true,double maxStrafe=1){
 groundF=m.forward;groundSt=m.strafe;groundU=m.up;
 return BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,groundF,groundSt,groundU,m.yaw_delta,maxStrafe,accepted);
}
void airRecovery44Guards(){
 for(int bad=0;bad<15;++bad){
  airRecovery44Fixture();auto& s=BotSupplyState(0);
  if(bad==0)BotCecilSettings().bAvoidPits=1;
  if(bad==1)player.m_pstState=PST_STAND;
  if(bad==2)player.m_pstState=PST_SWIM;
  if(bad==3)player.m_pstState=PST_DIVE;
  if(bad==4)player.health=0;
  if(bad==5)player.hasWorld=false;
  if(bad==6)player.en_vCurrentTranslationAbsolute(2)=NAN;
  if(bad==7)player.body.m[0][0]=0;
  if(bad==8)BotSupplyGraph().points[0].x=NAN;
  if(bad==9)s.blocked.clear();
  if(bad==10)s.useReleaseTick=10000;
  if(bad==11){for(auto& p:BotSupplyGraph().points)p.y=9;}
  if(bad==12){for(auto& p:BotSupplyGraph().points)p.x=40;}
  if(bad==13){for(auto& p:BotSupplyGraph().points)p.lock_entity=999;}
  if(bad==14)blockedItems=30;
  _botRayBudget=16;const auto m=BotSupplyTick(&player,0,1,1000);
  check(s.airMovementTime<0,"NORMAL44 opt-in otherstate USE death malformed graph/frame/velocity range locks and blocked LOS never stamp air authority");
  // Liquid has its own unchanged controller; it must not be called air motion.
  if(bad!=2&&bad!=3){airSafety44(m,1);check(groundF==0&&groundSt==0&&groundU==0,
    "NORMAL44 absent eligible original air hint emits neutral rather than borrowing a legacy escape");}
 }
 airRecovery44Fixture();auto& budget=BotSupplyState(0);budget.escapeUntil=9;budget.escapeWorld[0]=.3;
 _botRayBudget=2;auto m=BotSupplyTick(&player,0,1,1000);const int before=rayCount;
 check(!m.active&&airSafety44(m,1)==0&&rayCount==before&&budget.escapeUntil==0,
  "NORMAL44 insufficient original-hint LOS reserve cannot emit a stale legacy held direction");
 airRecovery44Fixture();_botRayBudget=3;m=BotSupplyTick(&player,0,1,1000);
 check(m.active&&_botRayBudget==2&&airSafety44(m,1)==1&&_botRayBudget==1,
  "NORMAL44 original LOS reserves two safety rays and final exact air request spends only one wall ray");
 airRecovery44Fixture();_botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);_botRayBudget=0;
 check(airSafety44(m,1)==0&&BotSupplyState(0).probe.lastReason==SCecilProbe::reasonBudget&&groundF==0&&groundSt==0,
  "NORMAL44 exhausted final shared budget defers movement without an unchecked air input");
 airRecovery44Fixture();_botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);wallMode=2;
 auto& wall=BotSupplyState(0);wall.escapeUntil=9;wall.escapeWorld[0]=.3;
 check(airSafety44(m,1)==0&&wall.probe.wallRays==1&&wall.probe.floorRays==0&&wall.escapeUntil==0,
  "NORMAL44 selected hint LOS cannot substitute for a blocked actual movement wall and no alternative hold is attempted");
 for(int change=0;change<10;++change){
  airRecovery44Fixture();_botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);auto& s=BotSupplyState(0);
  if(change==0)BotCecilSettings().bAvoidPits=1;
  if(change==1)player.m_pstState=PST_STAND;
  if(change==2)++player.en_ulID;
  if(change==3)++s.generation;
  if(change==4)player.health=0;
  if(change==5)s.blocked[0]=1;
  if(change==6)s.reacquireNode=1;
  if(change==7)player.en_vCurrentTranslationAbsolute(1)=INFINITY;
  if(change==8)player.hasWorld=false;
  if(change==9)m.up=1;
  const int rays=rayCount;
  check(airSafety44(m,1)==0&&groundF==0&&groundSt==0&&groundU==0&&rayCount==rays,
   "NORMAL44 setting state entity generation death lock hint velocity world or vertical-request change invalidates exact air proposal before query");
 }
 airRecovery44Fixture();_botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);auto& stale=BotSupplyState(0);
 check(airSafety44(m,2)==0&&groundF==0&&groundSt==0&&stale.airMovementTime<0,
  "NORMAL44 previous-tick air authority cannot survive without another original-hint LOS proposal");
 airRecovery44Fixture();_botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);m.forward=.64;m.strafe=0;
 check(airSafety44(m,1,false)==1&&near(groundF,.64)&&BotSupplyState(0).airMovementTime<0,
  "NORMAL44 rejected Supply proposal cannot cap or replace Human-owned input and clears its air token");
 airRecovery44Fixture();_botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);
 player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 check(airSafety44(m,1)==0&&groundF==0&&groundSt==0,
  "NORMAL44 changed gravity cannot reuse the previously proposed air direction");
 airRecovery44Fixture();player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 _botRayBudget=16;m=BotSupplyTick(&player,0,1,1000);
 check(m.active&&airSafety44(m,1)==1&&groundU==0&&BotSupplyState(0).probe.floorRays==0,
  "NORMAL44 newly proposed matched inverted-gravity air motion remains bounded and has no up/floor authority");
 // A valid committed airborne route retains its ordinary controller and speed.
 setup(3);auto& route=BotSupplyState(0);route.goal=2;route.scanTick=99999;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);player.m_pstState=PST_FALL;
 player.pl.pl_PositionVector=FLOAT3D(0,5,-3);route.scanTick=0;
 _botRayBudget=16;m=BotSupplyTick(&player,0,2,1000);
 check(route.navigator.HasCommittedEdge(2)&&route.anchor==0&&route.airMovementTime<0&&m.active,
  "NORMAL44 valid committed airborne route remains independent of offgraph air hints");
 airRecovery44Fixture();auto& timed=BotSupplyState(0);double first=-1;bool deadline=true,bounded=true;
 allocations=0;measuring=true;
 for(int tick=1;tick<=160;++tick){const int rays=rayCount;_botRayBudget=16;m=BotSupplyTick(&player,0,tick,1000);
  if(tick==1)first=timed.reacquireSince;
  if(tick<=120)deadline&=near(timed.reacquireSince,first);
  airSafety44(m,tick,true,.1);bounded&=rayCount-rays<=16&&_botRayBudget>=0&&std::hypot(groundF,groundSt)<=.300001&&std::fabs(groundSt)<=.100001&&groundU==0;
 }
 measuring=false;check(deadline&&timed.reacquireRejected==0&&timed.reacquireNode==1,
  "NORMAL44 repeated original air proposals keep the fixed six-second target deadline and genuine next-target backoff");
 check(bounded&&allocations==0,"NORMAL44 changing air hint attempts preserve sixteen shared rays motion caps and zero per-tick allocations");
}

// NORMAL042 A0 reaches an original isolated UNREACHABLE point, then has no
// directed goal. A2 is stationary on a sidewall with current NULL/near-foot NOHIT.
// Default Cecil pit policy permits bounded movement, not a claim of ground.
void neutralRecovery43(){
 groundProgressFixture(true);auto& orphan=BotSupplyState(0);
 orphan.anchor=0;BotSupplyGraph().points[0].flags=botcore::CECIL_UNREACHABLE;
 BotSupplyGraph().points[0].links.clear();BotCecilSettings().bAvoidPits=0;
 bool escaped=false;for(int tick=1;tick<=80;++tick)escaped|=groundProgressTick(tick)==2;
 check(escaped&&orphan.anchor==0&&orphan.goal<0&&orphan.hop<0,
  "NORMAL43 isolated anchored no-goal accepted owner observes real no-progress without altering original NAV");
 groundProgressFixture(true);player.en_penReference=nullptr;floorMode=0;
 player.en_vCurrentTranslationAbsolute=FLOAT3D(-4.95f,.001f,0);BotCecilSettings().bAvoidPits=0;
 escaped=false;bool bounded=true;for(int tick=1;tick<=80;++tick){const int before=rayCount;
  const int status=groundProgressTick(tick);escaped|=status==2;
  bounded&=rayCount-before<=16&&std::hypot(groundF,groundSt)<=.300001&&groundU==0;
 }
 check(escaped&&bounded&&BotSupplyState(0).groundRecoveryTime<0,
  "NORMAL43 actual frozen NULL support with finite nonzero velocity permits default-policy wall-tested movement without ground proof");
 for(int invalid=0;invalid<4;++invalid){
  groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;
  if(invalid==0)floorEntity.flags=ENF_DELETED;
  if(invalid==1)player.world.wo_cenEntities.clear();
  if(invalid==2)floorEntity.type=CEntity::RT_MODEL;
  if(invalid==3){player.en_penReference=nullptr;player.physicsFlags=0;}
  bool denied=true;for(int tick=1;tick<=70;++tick)denied&=groundProgressTick(tick)!=2;
  check(denied,"NORMAL43 default movement refuses deleted foreign nonphysical or gravity-disabled current context");
 }
}

void neutralRecovery43Guards(){
 // Both current policy and current context must authorize every emitted hold.
 groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;player.en_penReference=nullptr;floorMode=0;
 for(int tick=1;tick<=41;++tick)groundProgressTick(tick);
 auto& held=BotSupplyState(0);const double until=held.escapeUntil;
 check(held.groundEscapeActive&&held.probe.wallRays==1&&held.probe.floorRays==0&&held.groundRecoveryTime<0,
  "NORMAL43 default NULL recovery consumes a completed wall ray and never manufactures support or floor evidence");
 player.pl.pl_PositionVector(1)+=.26f;
 check(groundProgressTick(42)==2&&!held.groundStalled&&near(held.escapeUntil,until),
  "NORMAL43 real progress resets watchdog while current default policy finishes the original bounded hold");
 BotCecilSettings().bAvoidPits=1;
 check(groundProgressTick(43)==0&&groundF==0&&groundSt==0&&near(held.escapeUntil,until),
  "NORMAL43 changing to opt-in pits immediately suspends a NULL hold even after watchdog progress reset");
 BotCecilSettings().bAvoidPits=0;
 check(groundProgressTick(44)==2&&held.probe.floorRays==0&&near(held.escapeUntil,until),
  "NORMAL43 restoring default policy revalidates the wall without renewing the original world hold");
 const int rays=rayCount;double f=0,st=0,u=0;
 check(BotCecilSafeMotion(&player,held,2.25,f,st,u,0,1)!=2&&f==0&&st==0&&!held.groundEscapeActive&&rayCount==rays,
  "NORMAL43 an old movement-context timestamp cannot authorize a later tick held escape");
 for(int mode=0;mode<3;++mode){
  groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;
  for(int tick=1;tick<=41;++tick)groundProgressTick(tick);
  auto& state=BotSupplyState(0);state.anchor=0;state.goal=0;
  if(mode==1)BotSupplyGraph().points[0].flags=botcore::CECIL_UNREACHABLE;
  if(mode==2){BotSupplyGraph().points[0].lock_entity=999;state.blocked[0]=1;}
  groundProgressTick(42);
  check(!state.groundStalled&&!state.groundEscapeActive&&state.groundObservationTime<0,
   "NORMAL43 valid ordinary unreachable or locked goal context cancels no-goal watchdog authority");
 }
 for(int bad=0;bad<12;++bad){
  groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;player.en_penReference=nullptr;floorMode=0;
  for(int tick=1;tick<=41;++tick)groundProgressTick(tick);
  auto& state=BotSupplyState(0);
  if(bad==0)state.useReleaseTick=10000;
  if(bad==1)player.health=0;
  if(bad==2)player.m_pstState=PST_FALL;
  if(bad==3)player.m_pstState=PST_SWIM;
  if(bad==4)player.en_vCurrentTranslationAbsolute(1)=NAN;
  if(bad==5)BotSupplyGraph().points[0].x=NAN;
  if(bad==6)state.blocked.clear();
  if(bad==7)player.body.m[0][0]=0;
  if(bad==8)player.hasWorld=false;
  if(bad==9)++state.generation;
  if(bad==10)++player.en_ulID;
  const int status=groundProgressTick(42,bad!=11);
  check(status!=2&&!state.groundEscapeActive&&!state.groundStalled,
   "NORMAL43 USE death air liquid invalid graph/frame/physics life generation and owner loss cancel inherited recovery");
 }
 groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;player.en_penReference=nullptr;floorMode=0;wallMode=2;
 bool blocked=true;for(int tick=1;tick<=100;++tick)blocked&=groundProgressTick(tick)!=2;
 check(blocked&&wallCount>0&&BotSupplyState(0).probe.floorRays==0&&BotSupplyState(0).reacquireTried[0]==0,
  "NORMAL43 default policy never bypasses a physical wall or turns missing support into NoFloor NAV rejection");
 groundProgressFixture();BotCecilSettings().bAvoidPits=0;floorMode=0;bool unstalled=true;
 for(int tick=1;tick<=39;++tick)unstalled&=groundProgressTick(tick)!=2&&groundF==0&&groundSt==0;
 check(unstalled&&BotSupplyState(0).probe.floorRays>0,
  "NORMAL43 unstalled original Reacquire proposals keep the previous mandatory floor policy");
 groundProgressFixture(true);BotCecilSettings().bAvoidPits=1;player.en_penReference=nullptr;floorMode=0;bool optIn=true;
 for(int tick=1;tick<=100;++tick)optIn&=groundProgressTick(tick)!=2&&groundF==0&&groundSt==0;
 check(optIn,"NORMAL43 opt-in pit policy still denies NULL-nohit movement throughout a genuine stall");
 groundProgressFixture(true);BotSupplyState(0).anchor=0;BotCecilSettings().bAvoidPits=1;floorMode=0;bool orphanPit=true;
 for(int tick=1;tick<=90;++tick)orphanPit&=groundProgressTick(tick)!=2;
 check(orphanPit&&wallCount>0,"NORMAL43 anchored no-goal recovery with opt-in pits still requires a completed floor hit");
 groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;player.en_penReference=nullptr;floorMode=0;
 bool progressed=true;for(int tick=1;tick<=90;++tick){player.pl.pl_PositionVector(1)+=.02f;progressed&=groundProgressTick(tick)!=2;}
 check(progressed,"NORMAL43 meaningful actual position progress prevents default-policy false recovery");
 groundProgressFixture(true);BotCecilSettings().bAvoidPits=0;player.en_penReference=nullptr;floorMode=0;
 bool bounded=true;allocations=0;measuring=true;
 for(int tick=1;tick<=300;++tick){const int before=rayCount;groundProgressTick(tick,true,0);
  bounded&=rayCount-before<=16&&_botRayBudget>=0&&std::hypot(groundF,groundSt)<=.300001&&groundSt==0&&groundU==0;}
 measuring=false;check(bounded&&allocations==0,"NORMAL43 repeated NULL sweeps preserve disabled strafe sixteen rays and zero allocations");
}

// Normal041 actual frozen pose exhausted all five approved directions for over
// 200s. A complete bounded pass must include forward and be repeatable, not
// convert another finite set of approved rays into a permanent neutral latch.
void groundSweep42(){
 groundProgressFixture(true);wallMode=4;bool forwardExit=false;
 for(int tick=1;tick<=60;++tick)if(groundProgressTick(tick)==2)forwardExit|=groundF>0&&std::fabs(groundSt)<1e-6;
 check(forwardExit,"NORMAL42 neutral stalled recovery tests the missing physically clear forward half-plane");
 groundProgressFixture(true);int starts=0;double until=0;std::vector<std::pair<double,double>> dirs;
 for(int tick=1;tick<=410;++tick){
  const int status=groundProgressTick(tick);auto& state=BotSupplyState(0);
  if(status==2&&state.escapeUntil>until+.01){dirs.push_back({groundF,groundSt});until=state.escapeUntil;++starts;}
 }
 check(starts>=10,"NORMAL42 exhausted physical stationary sweep repeats after cooldown without fake progress");
 bool complete=dirs.size()>=8;
 for(size_t i=0;i<dirs.size()&&i<8;++i)for(size_t j=0;j<i;++j)
  complete&=std::hypot(dirs[i].first-dirs[j].first,dirs[i].second-dirs[j].second)>.1;
 check(complete,"NORMAL42 first stationary pass covers eight distinct cardinal and diagonal directions");
 check(BotSupplyState(0).anchor<0&&BotSupplyState(0).hop<0&&BotSupplyState(0).groundProgress.StationarySeconds()>19,
  "NORMAL42 sweep wrap does not reset measured stationary time or invent NAV arrival");
 groundProgressFixture(true);wallMode=2;captureWalls=true;
 for(int tick=1;tick<=80&&capturedWalls<8;++tick)groundProgressTick(tick,true,1,2);
 bool fair=capturedWalls>=8;
 for(int i=0;i<capturedWalls&&i<8;++i)for(int j=0;j<i;++j)
  fair&=std::hypot(capturedWorld[i][0]-capturedWorld[j][0],capturedWorld[i][1]-capturedWorld[j][1])>.1;
 check(fair,"NORMAL42 definite blocked probes advance a persistent cursor despite only one completed wall check per frame");
 groundProgressFixture(true);double groundUntil=0;bool yawStable=true;int sectors=0;
 for(int tick=1;tick<=300;++tick){
  _botRayBudget=16;BotSupplyTick(&player,0,tick,1000);double f=0,st=0,u=0;
  const double yaw=tick<60?0:90;const int status=BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,yaw,1);
  if(status==2&&BotSupplyState(0).escapeUntil>groundUntil+.01){
   const double a=yaw*3.141592653589793/180;
   const double x=-std::sin(a)*f+std::cos(a)*st,z=-std::cos(a)*f-std::sin(a)*st;
   const double expected=sectors*3.141592653589793/4;
   if(sectors<8)yawStable&=std::hypot(x-.3*std::sin(expected),z+.3*std::cos(expected))<1e-5;
   ++sectors;groundUntil=BotSupplyState(0).escapeUntil;
  }
 }
 check(yawStable&&sectors>=8,"NORMAL42 sector identity remains fixed in world space while final body yaw changes");
}

int groundSweepYawTick(int tick,double yaw,double maxStrafe=1,int budget=16){
 _botRayBudget=budget;BotSupplyTick(&player,0,tick,1000);groundF=groundSt=groundU=0;
 return BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,groundF,groundSt,groundU,yaw,maxStrafe);
}
void groundSweep42Guards(){
 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundSweepYawTick(tick,45);
 const double until=BotSupplyState(0).escapeUntil;
 check(groundSweepYawTick(42,0,.1)==2&&near(groundF,-groundSt)&&near(std::fabs(groundSt),.1)&&
  near(BotSupplyState(0).escapeUntil,until),
  "NORMAL42 held world direction scales uniformly at reduced strafe limit instead of independently clipping its heading");
 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundProgressTick(tick);
 const unsigned cursor=BotSupplyState(0).groundEscapeCursor,bits=BotSupplyState(0).groundEscapeTried;
 const double expiry=BotSupplyState(0).escapeUntil;
 player.en_penReference=nullptr;
 check(groundProgressTick(42)==0&&groundF==0&&groundSt==0&&BotSupplyState(0).groundEscapeCursor==cursor&&
  BotSupplyState(0).groundEscapeTried==bits&&near(BotSupplyState(0).escapeUntil,expiry),
  "NORMAL42 unknown NULL cannot advance sectors or renew a paused original held expiry");
 player.en_penReference=&floorEntity;
 check(groundProgressTick(43)==2&&near(BotSupplyState(0).escapeUntil,expiry),
  "NORMAL42 world hold resumes only with current support and fresh wall/floor tests");
 groundProgressFixture(true);for(int tick=1;tick<=40;++tick)groundProgressTick(tick);
 invalidHitDistance=true;const unsigned before=BotSupplyState(0).groundEscapeCursor;
 check(groundProgressTick(41)==0&&BotSupplyState(0).groundEscapeCursor==before&&BotSupplyState(0).groundEscapeTried==0,
  "NORMAL42 invalid physical query defers the same sector without consuming a tried bit");
 invalidHitDistance=false;
 check(groundProgressTick(42)==2&&groundF>0&&BotSupplyState(0).groundEscapeCursor==1,
  "NORMAL42 deferred invalid sector is retried rather than silently skipped");
 groundProgressFixture(true);for(int tick=1;tick<=40;++tick)groundProgressTick(tick);
 check(groundProgressTick(41,true,1,1)==0&&BotSupplyState(0).groundEscapeCursor==0&&BotSupplyState(0).groundEscapeTried==0,
  "NORMAL42 missing current safety budget cannot consume the initial forward sector");
 check(groundProgressTick(42)==2&&groundF>0,"NORMAL42 restored budget starts the original deferred forward sector");
 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundSweepYawTick(tick,0,0);
 const double cooldown=BotSupplyState(0).groundEscapeAfter;
 check(groundSweepYawTick(42,90,0)==0&&groundF==0&&groundSt==0&&near(BotSupplyState(0).groundEscapeAfter,cooldown),
  "NORMAL42 body-only heading change cancels unrepresentable held world motion without bypassing cooldown");
 bool bodyOnly=true;int bodyStarts=0;double bodyUntil=0;
 for(int tick=43;tick<=160;++tick){const int status=groundSweepYawTick(tick,90,0);
  bodyOnly&=groundSt==0&&groundU==0;
  if(status==2&&BotSupplyState(0).escapeUntil>bodyUntil+.01){++bodyStarts;bodyUntil=BotSupplyState(0).escapeUntil;}
 }
 check(bodyOnly&&bodyStarts>=3&&BotSupplyState(0).groundEscapeCursor<=2,
  "NORMAL42 disabled strafe repeats only the two current body-forward/back alternatives, never claims eight world sectors");

 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundSweepYawTick(tick,0,0);
 groundSweepYawTick(42,.01,0);bool tinyBodyRebound=false;
 for(int tick=43;tick<=110;++tick)tinyBodyRebound|=groundSweepYawTick(tick,.01,0)==2;
 check(tinyBodyRebound,"NORMAL42 even a small actual body heading change cannot strand both zero-strafe alternatives in an old world basis");
 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundSweepYawTick(tick,0);
 check(groundSweepYawTick(42,90,0)==0&&!BotSupplyState(0).groundEscapeActive,
  "NORMAL42 switching to body-only cannot inherit a sideways world hold");
 bool reenabled=false;
 for(int tick=43;tick<=90;++tick)reenabled|=groundSweepYawTick(tick,90,1)==2;
 check(reenabled&&BotSupplyState(0).groundSweepReady&&!BotSupplyState(0).groundSweepBodyOnly,
  "NORMAL42 switching back to strafe-enabled starts a coherent newly bound world sweep after cooldown");
 groundProgressFixture(true);wallMode=2;for(int tick=1;tick<=41;++tick)groundProgressTick(tick);
 auto& exhausted=BotSupplyState(0);const double passAfter=exhausted.groundEscapeAfter;const int rays=rayCount;
 for(int tick=42;tick<=60;++tick)groundProgressTick(tick);
 check(exhausted.groundEscapeCursor==8&&exhausted.groundEscapeTried==255&&rayCount==rays&&passAfter>3.5,
  "NORMAL42 a fully blocked pass waits its existing cooldown instead of replaying all eight every frame");
 wallMode=0;bool repeated=false;for(int tick=61;tick<=90;++tick)repeated|=groundProgressTick(tick)==2;
 check(repeated&&exhausted.groundProgress.StationarySeconds()>4,
  "NORMAL42 a later clear physical sector can recover after a blocked pass without resetting real stationary time");
 groundProgressFixture(true);player.en_vGravityDir=FLOAT3D(.6f,-.8f,0);
 floorPlane.bpl_plAbsolute=FLOAT3D(-.6f,.8f,0);bool tangent=true;
 for(int tick=1;tick<=200;++tick){const int status=groundSweepYawTick(tick,0);
  if(status==2)tangent&=std::fabs(.6*groundSt)<1e-6;
 }
 check(tangent,"NORMAL42 gravity-relative world sectors cannot silently acquire a vertical component from an unmatched body plane");


 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundSweepYawTick(tick,0);
 const double tiny=.0001,ct=std::cos(tiny),sn=std::sin(tiny);
 player.en_vGravityDir=FLOAT3D(0,float(-ct),float(-sn));
 player.body.m[1][1]=ct;player.body.m[1][2]=-sn;player.body.m[2][1]=sn;player.body.m[2][2]=ct;
 floorPlane.bpl_plAbsolute=FLOAT3D(0,float(ct),float(sn));bool gravityRebound=false;
 const double priorCooldown=BotSupplyState(0).groundEscapeAfter;
 groundSweepYawTick(42,0);
 check(near(BotSupplyState(0).groundEscapeAfter,priorCooldown),
  "NORMAL42 a small current gravity turn must not bypass the previous physical-attempt cooldown");
 for(int tick=43;tick<=130;++tick)gravityRebound|=groundSweepYawTick(tick,0)==2;
 check(gravityRebound,"NORMAL42 a small stable gravity/body turn cannot leave all captured world sectors permanently unrepresentable");

 // Other rotation axis: old forward remains representable, but the next old
 // diagonal would be permanently Invalid without rebinding the sweep normal.
 groundProgressFixture(true);for(int tick=1;tick<=41;++tick)groundSweepYawTick(tick,0);
 const double oldExpiry=BotSupplyState(0).escapeUntil;
 player.en_vGravityDir=FLOAT3D(float(sn),float(-ct),0);
 player.body.m[0][0]=ct;player.body.m[0][1]=-sn;player.body.m[1][0]=sn;player.body.m[1][1]=ct;
 floorPlane.bpl_plAbsolute=FLOAT3D(float(-sn),float(ct),0);
 check(groundSweepYawTick(42,0)==0&&!BotSupplyState(0).groundEscapeActive,
  "NORMAL42 a changed gravity normal cancels a previously held context even when its first axis still happens to fit");
 bool secondAxis=false;
 for(int tick=43;tick<=150;++tick){const int status=groundSweepYawTick(tick,0);
  secondAxis|=status==2&&BotSupplyState(0).escapeUntil>oldExpiry+.01&&groundSt>0;
 }
 check(secondAxis,"NORMAL42 a small second-axis gravity turn reaches the newly rebound diagonal instead of permanent Invalid");
 groundProgressFixture(true);bool bounded=true;allocations=0;measuring=true;
 for(int tick=1;tick<=900;++tick){const int beforeRays=rayCount;groundSweepYawTick(tick,(tick*7)%360,.1);
  bounded&=rayCount-beforeRays<=16&&_botRayBudget>=0&&std::hypot(groundF,groundSt)<=.300001&&std::fabs(groundSt)<=.100001&&groundU==0;}
 measuring=false;check(bounded&&allocations==0,"NORMAL42 repeated world sweeps and rotating yaw retain sixteen shared rays, uniform caps and zero allocation");
}

// Native039diag3b freezes: actual accepted offgraph pose is unchanged while
// valid native brush support alternates with current NULL / physical NOHIT.
void groundObservationFlicker(){
 for(bool neutral:{false,true})for(int period:{20,2}){
  groundProgressFixture(neutral);bool escaped=false,unknownNeutral=true,bounded=true;allocations=0;measuring=true;
  unsigned priorTried=0;double priorCooldown=0;
  for(int tick=1;tick<=110;++tick){
   const bool supported=tick%period!=0;player.en_penReference=supported?&floorEntity:nullptr;
   const int before=rayCount;const int status=groundProgressTick(tick);auto& state=BotSupplyState(0);
   if(supported)escaped|=status==2;
   else unknownNeutral&=status!=2&&groundF==0&&groundSt==0&&groundU==0&&
      state.probe.reasonMask==0&&state.reacquireTried[0]==0&&
      state.groundEscapeTried==priorTried&&near(state.groundEscapeAfter,priorCooldown);
   bounded&=rayCount-before<=16&&_botRayBudget>=0&&std::hypot(groundF,groundSt)<=.300001&&groundU==0;
   priorTried=state.groundEscapeTried;priorCooldown=state.groundEscapeAfter;
  }
  measuring=false;
  check(escaped,"frozen native brush NULL flicker preserves observation until a currently supported verified escape");
  check(unknownNeutral,"current unknown support emits neutral without rays NoFloor blacklist or resetting stationary-episode history");
  check(bounded&&allocations==0,"flicker recovery preserves physical probe budget motion cap and allocation bound");
 }
 groundProgressFixture(true);player.en_penReference=nullptr;bool unknown=true;
 for(int tick=1;tick<=60;++tick){unknown&=groundProgressTick(tick)!=2&&groundF==0&&groundSt==0;}
 player.en_penReference=&floorEntity;
 check(unknown&&groundProgressTick(61)==2,"three seconds of passive unknown-support observation cannot act until fresh support then recovers immediately");
 groundProgressFixture(true);for(int tick=1;tick<=60;++tick)groundProgressTick(tick,true,1,1);
 check(groundProgressTick(61)==2,"deferred safety budget preserves passive position time but cannot authorize before fresh probe budget");
 groundProgressFixture();bool escaped=false;
 for(int tick=1;tick<=110;++tick){player.en_penReference=(tick&1)?&floorEntity:nullptr;player.pl.pl_PositionVector(3)-=.02f;escaped|=groundProgressTick(tick)==2;}
 check(!escaped,"real physical progress across support flicker still prevents a false watchdog escape");
 groundProgressFixture(true);player.en_penReference=nullptr;for(int tick=1;tick<=60;++tick)groundProgressTick(tick);
 double f=.3,st=0,u=0;const int before=rayCount;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),3,f,st,u,0,1,true)==0&&f==0&&st==0&&u==0&&rayCount==before,
  "observed stall with no current support cannot test or emit a stale positive request");
}

void groundObservationHoldGuards(){
 groundProgressFixture(true);for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 auto& state=BotSupplyState(0);const double until=state.escapeUntil,cooldown=state.groundEscapeAfter;const unsigned tried=state.groundEscapeTried;
 player.en_penReference=nullptr;const int before=rayCount;
 check(groundProgressTick(44)==0&&groundF==0&&groundSt==0&&groundU==0&&state.probe.reasonMask==0&&
   near(state.escapeUntil,until)&&near(state.groundEscapeAfter,cooldown)&&state.groundEscapeTried==tried&&rayCount-before==1,
   "unknown current support pauses held recovery after its sole support query without expiry renewal or episode reset");
 player.en_penReference=&floorEntity;
 check(groundProgressTick(45)==2&&groundF>0&&near(state.escapeUntil,until)&&state.probe.wallRays==1&&state.probe.floorRays==1,
   "freshly supported held direction resumes only after actual wall and floor revalidation with original expiry");
 groundProgressFixture(true);for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 const double progressUntil=BotSupplyState(0).escapeUntil;player.pl.pl_PositionVector(1)+=.26f;
 groundProgressTick(44);player.en_penReference=nullptr;
 check(groundProgressTick(45)==0&&groundF==0&&groundSt==0&&!BotSupplyState(0).groundStalled&&near(BotSupplyState(0).escapeUntil,progressUntil),
   "support loss also pauses a still-held successful escape after real progress reset the watchdog");
 player.en_penReference=&floorEntity;
 check(groundProgressTick(46)==2&&near(BotSupplyState(0).escapeUntil,progressUntil),
   "successful held recovery can resume with current proof and no renewed deadline");
 groundProgressFixture(true);for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 const double expired=BotSupplyState(0).escapeUntil;player.en_penReference=nullptr;
 for(int tick=44;tick<=60;++tick)groundProgressTick(tick);
 check(near(BotSupplyState(0).escapeUntil,expired),"a suspended hold never renews its original elapsed expiry");
 player.en_penReference=&floorEntity;
 check(groundProgressTick(61)!=2&&BotSupplyState(0).escapeUntil==0,
   "restored support after hold expiry cannot resurrect an expired world direction or bypass cooldown");
 for(int loss=0;loss<6;++loss){
  groundProgressFixture(true);player.en_penReference=nullptr;for(int tick=1;tick<=59;++tick)groundProgressTick(tick);
  if(loss==0)groundProgressTick(60,false);
  if(loss==1){player.m_pstState=PST_FALL;groundProgressTick(60);player.m_pstState=PST_STAND;}
  if(loss==2){BotSupplyGraph().points[0].x=NAN;groundProgressTick(60);BotSupplyGraph().points[0].x=0;}
  if(loss==3){player.en_vCurrentTranslationAbsolute(1)=NAN;groundProgressTick(60);player.en_vCurrentTranslationAbsolute(1)=0;}
  if(loss==4){player.body.m[0][0]=0;groundProgressTick(60);player.body.m[0][0]=1;}
  if(loss==5){++BotSupplyState(0).generation;groundProgressTick(60);}
  player.en_penReference=&floorEntity;
  check(groundProgressTick(61)!=2&&!BotSupplyState(0).groundStalled,
    "passive unknown-support history cannot cross owner air graph velocity frame or generation context loss");
 }
 groundProgressFixture(true);player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);bool escaped=false,neutral=true;
 for(int tick=1;tick<=100;++tick){player.en_penReference=(tick&1)?&floorEntity:nullptr;int status=groundProgressTick(tick);
  if(tick&1)escaped|=status==2;else neutral&=groundF==0&&groundSt==0&&groundU==0;}
 check(escaped&&neutral,"dense support flicker retains current-proof action gating under rotated gravity");
}

void originalDiagonalRecovery(){
 // Original BotMovement.cpp580..589: NoPosChange chooses side+back together.
 // A corner with only diagonal exits cannot be escaped by three cardinal rays.
 groundProgressFixture(true);wallMode=3;bool diagonal=false,bounded=true;allocations=0;measuring=true;
 for(int tick=1;tick<=120;++tick){const int before=rayCount;const int status=groundProgressTick(tick);
  if(status==2){diagonal|=groundF<-.05&&std::fabs(groundSt)>.05;
   bounded&=tick>=40&&groundU==0&&std::hypot(groundF,groundSt)<=.300001;}
  bounded&=rayCount-before<=16&&_botRayBudget>=0;
 }
 measuring=false;
 check(diagonal,"original Cecil side-plus-back recovery can use a physically verified diagonal corner exit");
 check(bounded&&allocations==0,"diagonal recovery retains actual stall delay normal cap shared sixteen rays and no allocation");
 for(int negative=0;negative<5;++negative){
  groundProgressFixture(true);wallMode=3;bool escaped=false;
  if(negative==0)floorMode=0;
  if(negative==1)player.en_penReference=nullptr;
  if(negative==2)player.m_pstState=PST_FALL;
  for(int tick=1;tick<=120;++tick)escaped|=groundProgressTick(tick,negative!=3,negative==4?0:1)==2;
  check(!escaped,"diagonal exit never bypasses floor current support ground movement owner or disabled strafe");
 }
 groundProgressFixture(true);wallMode=3;
 for(int tick=1;tick<=40;++tick)groundProgressTick(tick);
 check(groundProgressTick(41,true,1,2)==0&&_botRayBudget==1,
  "a diagonal cannot borrow missing wall-plus-floor budget after the first blocked forward direction");
 check(groundProgressTick(42,true,1,2)==2&&_botRayBudget==0,
  "a deferred diagonal may use exactly two fresh safety rays on the next frame");
}

void offgraphProgressGuards(){
 // A held ray-clear escape with no physical motion must progress through fair
 // world directions, rather than relabeling the same side after escapeSide flips.
 groundProgressFixture(true);double heldUntil=0;std::vector<std::pair<double,double>> directions;
 for(int tick=1;tick<=220;++tick){
  const int status=groundProgressTick(tick);auto& state=BotSupplyState(0);
  if(status==2&&state.escapeUntil>heldUntil+.01){directions.push_back({groundF,groundSt});heldUntil=state.escapeUntil;}
 }
 check(directions.size()>=5&&directions[0].first>0&&near(directions[0].second,0)&&
   directions[1].first>0&&directions[1].second>0&&directions[2].second>0&&
   directions[3].first<0&&directions[3].second>0&&directions[4].first<0,
  "stationary world sweep starts forward and continues fairly through both forward and backward half-planes");


 groundProgressFixture(true);for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 const double successfulHold=BotSupplyState(0).escapeUntil;
 player.pl.pl_PositionVector(1)+=.26f;
 const int progressedHold=groundProgressTick(44);
 check(progressedHold==2&&groundF>0&&!BotSupplyState(0).groundStalled&&
   near(BotSupplyState(0).escapeUntil,successfulHold),
  "actual progress resets watchdog but preserves the remaining verified world-direction hold");

 groundProgressFixture(true);for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);
 check(groundProgressTick(44)==1&&groundSt==0&&!BotSupplyState(0).groundEscapeActive,
  "gravity change cancels an old held escape rather than treating reset as successful movement");

 groundProgressFixture(true);for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 check(groundProgressTick(49)==1&&groundSt==0&&!BotSupplyState(0).groundEscapeActive,
  "missing accepted-frame interval cancels old held escape before its nominal end");

 groundProgressFixture();for(int tick=1;tick<=43;++tick)groundProgressTick(tick);
 player.body.m[0][0]=0;_botRayBudget=16;BotSupplyTick(&player,0,44,1000); // Driver may skip invalid final action.
 player.body.m[0][0]=1;
 check(groundProgressTick(45)==1&&groundSt==0&&!BotSupplyState(0).groundEscapeActive,
  "invalid planner-frame reset cannot leave an orphan ground hold for later valid positive movement");
 groundProgressFixture(true);for(int tick=1;tick<=45;++tick)groundProgressTick(tick);
 BotSupplyState(0).ClearEscape();
 check(groundProgressTick(46)==0,"planner ClearEscape cannot bypass stationary-episode direction cooldown");
 groundProgressFixture(true);BotCecilSettings().bStrafe=0;bool backstep=false;bool bounded=true;
 for(int tick=1;tick<=120;++tick){const int status=groundProgressTick(tick,true,0);
  backstep|=status==2&&groundF<0;bounded=bounded&&groundSt==0&&groundU==0&&std::hypot(groundF,groundSt)<=.300001;}
 check(backstep&&bounded,"neutral strafe-disabled recovery uses only verified bounded body forward/back alternatives");
 groundProgressFixture(true);floorMode=0;bool escaped=false;
 for(int tick=1;tick<=110;++tick)escaped|=groundProgressTick(tick)==2;
 check(!escaped&&groundF==0&&groundSt==0&&BotSupplyState(0).reacquireTried[0]==0,
  "synthetic neutral recovery still requires actual floor and cannot reject a NAV target as original NoFloor");

 groundProgressFixture();floorPattern=5;bool retainedOriginal=true;
 for(int tick=1;tick<=100;++tick){groundProgressTick(tick);retainedOriginal&=BotSupplyState(0).reacquireTried[0]==0;}
 check(retainedOriginal,"ray-clear original followed by failed escape floors is never original NoFloor NAV feedback");
 for(int negative=0;negative<10;++negative){
  groundProgressFixture(true);
  if(negative==0)player.en_penReference=nullptr;
  if(negative==1)floorEntity.flags=ENF_DELETED;
  if(negative==2)player.world.wo_cenEntities.clear();
  if(negative==3)player.m_pstState=PST_FALL;
  if(negative==4)player.m_pstState=PST_SWIM;
  if(negative==5)player.en_vCurrentTranslationAbsolute(1)=NAN;
  if(negative==6)BotSupplyState(0).blocked.clear();
  if(negative==7)BotSupplyGraph().points[0].x=NAN;
  if(negative==8)BotSupplyState(0).useReleaseTick=10000;
  if(negative==9)player.body.m[0][0]=0;
  escaped=false;for(int tick=1;tick<=100;++tick)escaped|=groundProgressTick(tick)==2;
  check(!escaped,"unknown support air liquid invalid velocity graph USE and frame never authorize neutral recovery");
 }
 groundProgressFixture(true);escaped=false;
 for(int tick=1;tick<=100;++tick)escaped|=groundProgressTick(tick,true,1,1)==2;
 check(!escaped,"missing shared safety-probe budget cannot authorize neutral escape");
 groundProgressFixture(true);escaped=false;
 for(int tick=1;tick<=100;++tick)escaped|=groundProgressTick(tick,false)==2;
 check(!escaped,"Human-owned movement cannot accrue or activate offgraph watchdog");
 groundProgressFixture();escaped=false;
 for(int tick=1;tick<=100;++tick){player.pl.pl_PositionVector(3)-=.02f;escaped|=groundProgressTick(tick)==2;}
 check(!escaped,"meaningful actual physical progress prevents false recovery despite clear movement requests");
 groundProgressFixture();escaped=false;
 for(int tick=1;tick<=100;++tick){player.pl.pl_PositionVector(1)=(tick&1)?.01f:0;escaped|=groundProgressTick(tick)==2;}
 check(escaped,"small physical jitter cannot renew stationary watchdog");
 groundProgressFixture(true);player.en_penReference=nullptr;nearFootMode=2;escaped=false;
 for(int tick=1;tick<=110;++tick)escaped|=groundProgressTick(tick)==2;
 check(escaped&&nearFootRays>0,"physically verified near-foot NULL support authorizes neutral recovery");
 groundProgressFixture(true);player.en_vGravityDir=FLOAT3D(0,1,0);player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);escaped=false;
 for(int tick=1;tick<=110;++tick)escaped|=groundProgressTick(tick)==2;
 check(escaped&&std::hypot(groundF,groundSt)<=.300001,"ground recovery follows rotated gravity and body axes with unchanged norm bound");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 check(BotSupplyState(0).groundStalled,"owner-reset fixture has a real physical stall");
 groundProgressTick(51,false);groundProgressTick(52);
 check(!BotSupplyState(0).groundStalled,"owner loss removes inherited physical stall and held escape immediately");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 player.en_ulID=101;groundProgressTick(51);
 check(!BotSupplyState(0).groundStalled,"entity replacement cannot inherit physical watchdog");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 ++BotSupplyState(0).generation;groundProgressTick(51);
 check(!BotSupplyState(0).groundStalled,"next generation cannot inherit physical watchdog");

 groundProgressFixture(true);bool rayBounded=true;bool normBounded=true;allocations=0;measuring=true;
 for(int tick=1;tick<=270;++tick){const int before=rayCount;groundProgressTick(tick,true,.1);
  rayBounded&=rayCount-before<=16&&_botRayBudget>=0;normBounded&=std::hypot(groundF,groundSt)<=.300001&&std::fabs(groundSt)<=.100001&&groundU==0;}
 measuring=false;check(rayBounded&&normBounded&&allocations==0,"all recovery directions retain shared sixteen-ray budget exact caps and no per-tick allocation");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 player.health=0;_botRayBudget=16;BotSupplyTick(&player,0,51,1000);
 check(!BotSupplyState(0).groundStalled&&BotSupplyState(0).groundRecoveryTime<0,
  "death clears watchdog even when Driver correctly skips final live safety");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 BotSupplyState(0).Reset();check(!BotSupplyState(0).groundStalled&&BotSupplyState(0).groundEscapeTried==0,
  "map/reset lifecycle removes physical recovery direction history");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 BotSupplyState(0).anchor=0;BotSupplyState(0).goal=0;groundProgressTick(51);
 check(!BotSupplyState(0).groundStalled&&!BotSupplyState(0).groundEscapeActive,
  "ordinary graph reacquisition immediately relinquishes local offgraph recovery");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 double f=0,st=0,u=0;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),2.6,f,st,u,0,1,true)==1&&f==0&&st==0&&!BotSupplyState(0).groundStalled,
  "stale eligibility cannot authorize a later-tick neutral escape");
 groundProgressFixture(true);for(int tick=1;tick<=50;++tick)groundProgressTick(tick);
 groundProgressTick(1);check(!BotSupplyState(0).groundStalled&&!BotSupplyState(0).groundEscapeActive,"clock rewind removes inherited stall and held escape");
}

void offgraphProgressBridge(){
 groundProgressFixture();int escapes=0;for(int tick=1;tick<=110;++tick)escapes+=groundProgressTick(tick)==2;
 check(escapes>0,"clear rays plus frozen actual pose trigger a physically verified bounded escape");
 groundProgressFixture(true);escapes=0;for(int tick=1;tick<=110;++tick)escapes+=groundProgressTick(tick)==2;
 check(escapes>0&&BotSupplyState(0).anchor<0&&BotSupplyState(0).hop<0,
  "eligible no-candidate neutral recovery can escape without fabricating graph context");
 groundProgressFixture();escapes=0;for(int tick=1;tick<=270;++tick)escapes+=groundProgressTick(tick)==2;
 check(escapes>0,"watchdog persists across fixed six-second target and six-second backoff cycles");
}

// Actual040diag A3: native StandOn and existing rejected floor hit are the
// same static brush polygon, up=.3976075, distance2.4784, stepDn1.5.
void nativeContactFixture(){
 groundProgressFixture();floorEntity.cls.name="Classes/WorldBase.ecl";floorEntity.en_pwoWorld=&player.world;
 static CBrush3D brush;static CBrushMip mip;static CBrushSector sector;
 brush.br_penEntity=&floorEntity;mip.bm_pbrBrush=&brush;sector.bsc_pbmBrushMip=&mip;floorPolygon.bpo_pbscSector=&sector;
 player.en_pbpoStandOn=&floorPolygon;player.en_fStepUpHeight=1;player.en_fStepDnHeight=1.5f;
 floorPlane.bpl_plAbsolute=FLOAT3D(float(std::sqrt(1-.3976075*.3976075)),.3976075f,0);floorHitDistance=2.4784336f;
}
template<class P>auto contactFloor(P* p,bool allow,int)->decltype(BotCecilFloor(p,.3,0,0,0,nullptr,allow)){
 return BotCecilFloor(p,.3,0,0,0,nullptr,allow);
}
template<class P>bool contactFloor(P* p,bool,long){return BotCecilFloor(p,.3,0,0,0);}
template<class P>auto nativeProof(P* p,const CCastRay& ray,double length,int)->decltype(BotCecilNativeContactFloor(p,ray,length)){
 return BotCecilNativeContactFloor(p,ray,length);
}
template<class P>bool nativeProof(P*,const CCastRay&,double,long){return false;}
void nativeContactRecovery(){
 nativeContactFixture();check(!BotCecilFloor(&player,.3,0,0,0),"same native steep polygon never widens ordinary floor normal policy");
 check(contactFloor(&player,true,0),"explicit current recovery can use native contacted slope within actual stepDn");
 nativeContactFixture();bool escaped=false,preStall=false,bounded=true;allocations=0;measuring=true;
 for(int tick=1;tick<=70;++tick){const int result=groundProgressTick(tick);if(tick<40)preStall|=result!=0;
  escaped|=result==2;bounded&=rayCount<=tick*16&&std::hypot(groundF,groundSt)<=.300001;}
 measuring=false;check(escaped&&!preStall,"actual frozen current-supported offgraph owner escapes contacted native slope only after watchdog stall");
 check(bounded&&allocations==0,"native-contact recovery preserves16ray bound .3norm and zero tick allocations");
 for(int control=0;control<29;++control){
  nativeContactFixture();CBrushPolygon different=floorPolygon;CWorld foreign;CEntity owner;
  switch(control){
   case 0:floorHitPolygon=&different;break;
   case 1:floorPolygon.bpo_pbscSector->bsc_pbmBrushMip->bm_pbrBrush->br_penEntity=&owner;break;
   case 2:player.en_penReference=&owner;break;
   case 3:floorEntity.flags=ENF_DELETED;break;
   case 4:floorEntity.cls.name="Classes/MovingBrush.ecl";break;
   case 5:floorEntity.entityPhysicsFlags=EPF_MOVABLE;break;
   case 6:player.en_penReference=nullptr;break;
   case 7:player.m_pstState=PST_FALL;break;
   case 8:player.health=0;break;
   case 9:floorEntity.en_pwoWorld=&foreign;break;
   case 10:floorPolygon.bpo_ulFlags=BPOF_PASSABLE;forcePassableHit=true;break;
   case 11:floorPolygon.bpo_pbplPlane=nullptr;break;
   case 12:floorPlane.bpl_plAbsolute(1)=NAN;break;
   case 13:floorPlane.bpl_plAbsolute=FLOAT3D(0,0,1);break;
   case 14:floorPlane.bpl_plAbsolute(2)=-.3976075f;break;
   case 15:floorPlane.bpl_plAbsolute=FLOAT3D(0,.3976075f,0);break;
   case 16:floorHitDistance=2.5001f;break;
   case 17:floorHitDistance=.4f;player.en_fStepUpHeight=.5f;break;
   case 18:player.en_fStepDnHeight=NAN;break;
   case 19:player.en_fStepUpHeight=INFINITY;break;
   case 20:player.en_fStepDnHeight=0;break;
   case 21:floorHitDistance=5.0001f;player.en_fStepDnHeight=10;break;
   case 22:floorHitDistance=NAN;break;
   case 23:floorPolygon.bpo_pbscSector=nullptr;break;
   case 24:floorEntity.type=CEntity::RT_MODEL;break;
   case 25:floorPolygon.bpo_pbscSector->bsc_pbmBrushMip=nullptr;break;
   case 26:floorPolygon.bpo_pbscSector->bsc_pbmBrushMip->bm_pbrBrush=nullptr;break;
   case 27:floorPlane.bpl_plAbsolute.pl_distance=NAN;break;
   case 28:floorPlane.bpl_plAbsolute.pl_distance=INFINITY;break;
  }
  _botRayBudget=16;check(!contactFloor(&player,true,0),"native-contact exception fails closed for foreign missing deleted moving air liquid badnormal invalidsteps and outside-segment contacts");
 }
 nativeContactFixture();const int lookups=worldLookups;_botRayBudget=16;
 check(contactFloor(&player,true,0)&&worldLookups==lookups&&rayCount==1&&_botRayBudget==15,
   "native-contact exception reads cached identity only and consumes exactly existing single floor ray");
 nativeContactFixture();player.m_pstState=PST_SWIM;
 CCastRay liquidRay(&player,FLOAT3D(0,1,0),FLOAT3D(0,-4,0));liquidRay.cr_penHit=&floorEntity;liquidRay.cr_pbpoBrushPolygon=&floorPolygon;liquidRay.cr_fHitDistance=floorHitDistance;
 check(!nativeProof(&player,liquidRay,5,0),"liquid cannot authorize native contacted ground exception");
 check(BotCecilFloor(&player,.3,0,0,0),"ordinary confirmed-liquid floor exemption remains unchanged");
 nativeContactFixture();player.m_pstState=PST_CROUCH;check(contactFloor(&player,true,0),"actual crouched native static contact uses identical bounded rule");
 nativeContactFixture();player.en_fStepDnHeight=1.4783f;check(!contactFloor(&player,true,0),"actual stepDn narrower than measured1.4784 drop cannot be guessed upward");
 nativeContactFixture();floorHitDistance=2.5f;check(contactFloor(&player,true,0),"exact finite native stepDn boundary accepted without skin tolerance");
 nativeContactFixture();floorHitDistance=.5f;player.en_fStepUpHeight=.5f;check(contactFloor(&player,true,0),"exact finite native stepUp boundary accepted without widening");
 nativeContactFixture();bool humanEscape=false;BotCecilSettings().bAvoidPits=1;
 for(int tick=1;tick<=70;++tick)humanEscape|=groundProgressTick(tick,false)!=0;
 check(!humanEscape,"rejected Supply proposal never lends current-contact exception to Human-owned pit avoidance");
 nativeContactFixture();_botRayBudget=0;const int priorRays=rayCount;
 check(!contactFloor(&player,true,0)&&rayCount==priorRays,"same-contact metadata never substitutes for missing floor probe budget");
 nativeContactFixture();BotCecilSettings().bAvoidPits=1;bool held=false;double deadline=0;int tick=1;
 for(;tick<=80;++tick)if(groundProgressTick(tick)==2){held=true;deadline=BotSupplyState(0).escapeUntil;break;}
 check(held,"native-contact fixture starts a genuinely verified world-held ground escape");
 if(held){
  player.pl.pl_PositionVector(1)+=.26f;const int resumed=groundProgressTick(++tick);
  check(resumed==2&&!BotSupplyState(0).groundStalled&&near(BotSupplyState(0).escapeUntil,deadline),
    "current-proof active ground hold keeps native-contact allowance after actual progress without renewing deadline");
  player.en_penReference=nullptr;const int paused=groundProgressTick(++tick);
  check(paused==0&&groundF==0&&groundSt==0&&near(BotSupplyState(0).escapeUntil,deadline),
    "held same-contact movement pauses immediately under unknown NULL without renewing its deadline");
 }
 nativeContactFixture();player.body.m[0][0]=-1;player.body.m[1][1]=-1;player.en_vGravityDir=FLOAT3D(0,1,0);
 floorPlane.bpl_plAbsolute(2)=-.3976075f;
 check(contactFloor(&player,true,0)&&lastTo(2)>lastFrom(2),"same-contact height and support follow real rotated gravity rather than world Y");
}

// Synthetic topology reuses the existing historical fixture; no new original NAV data.
void importantTransit48(){
 for(int kind=0;kind<3;++kind)for(bool fall:{false,true}){
  const bool entity=kind!=0;hopCheckpoint45Fixture();auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
  g.points[2].flags=kind==2?(botcore::CECIL_JUMP|botcore::CECIL_OVERRIDE):(entity?0:botcore::CECIL_IMPORTANT);g.points[2].important_entity=entity?777:-1;s.scanTick=2;
  bool observed=false,bounded=true,airDenied=true;int first=-1;
  for(int tick=2;tick<=142;++tick){
   hopCheckpoint45Wiggle(tick);player.m_pstState=fall&&tick%40==0?PST_FALL:PST_STAND;
   const int before=rayCount;hopCheckpoint45Tick(tick);observed|=s.hopCheckpointSince>=0;
   if(player.m_pstState==PST_FALL)airDenied&=hopCheckpointEvents==0;
   bounded&=rayCount-before<=16&&_botRayBudget>=0;
   if(hopCheckpointEvents){first=tick;break;}
  }
  check(s.importantGoal&&first>=102&&first<=122&&observed,
    "ordinary intermediate edge toward remote important endpoint receives unchanged five-second checkpoint");
  check(s.goal==2&&s.goalEntity==0&&s.goalSince==7&&s.goalDeadline==47&&s.interactionPoint<0&&s.useReleaseTick<0,
    "important transit checkpoint retains same endpoint identity and lifetime without interaction or item relocation");
  check(bounded&&airDenied,"important transit observation never lends air authority or extra ray budget");
 }
 // Terminal/special protection is about the actual edge, not remote intent.
 for(int invalid=0;invalid<24;++invalid){
  hopCheckpoint45Fixture();auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
  g.points[2].flags=0;g.points[2].important_entity=777;s.scanTick=2;
  const unsigned flags[]={botcore::CECIL_WALK,botcore::CECIL_CROUCH,botcore::CECIL_OVERRIDE,
    botcore::CECIL_UNREACHABLE,botcore::CECIL_TELEPORT,botcore::CECIL_IMPORTANT,botcore::CECIL_JUMP};
  for(int tick=2;tick<=145;++tick){
   hopCheckpoint45Wiggle(tick);
   if(invalid<14)g.points[invalid/7].flags=flags[invalid%7];
   if(invalid==14)g.points[0].important_entity=777;
   if(invalid==15)g.points[1].important_entity=777;
   if(invalid==16)g.points[0].lock_entity=777;
   if(invalid==17)g.points[1].lock_entity=777;
   if(invalid==18)s.interactionPoint=1;
   if(invalid==19)s.useReleaseTick=999;
   if(invalid==20)player.m_pstState=PST_FALL;
   if(invalid==21)player.en_penReference=nullptr;
   if(invalid==22)floorEntity.entityPhysicsFlags=EPF_MOVABLE;
   hopCheckpoint45Tick(tick,invalid!=23);
  }
  check(hopCheckpointEvents==0,
    "remote important goal cannot override terminal flags entity locks interaction USE current-ground contact or owner guards");
 }
}
void importantPatrol48Fixture(bool entity){
 patrolAlternate46Fixture(5);auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
 g.points[4].x=50;g.points[4].y=10;g.points[4].z=0;
 g.points[4].flags=entity?0:botcore::CECIL_IMPORTANT;g.points[4].important_entity=entity?777:-1;g.points[1].links={4};
 s.ClearGoal();s.goal=4;s.goalSince=7;s.anchor=0;s.scanTick=2;
 player.pl.pl_PositionVector=FLOAT3D();hopCheckpoint45Tick(1);
}
void itemTransit49Fixture(){
 importantPatrol48Fixture(true);auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
 auto& item=addItem(991,g.points[4].x,g.points[4].z,botcore::CecilItemKind::Weapon);
 item.item.weapon=4;item.pl.pl_PositionVector(2)=g.points[4].y;g.points[4].important_entity=991;
 s.goalEntity=991;s.goalSince=0;s.goalDeadline=45;s.mappedWeaponGoal=true;
}
void itemTransit49(){
 for(int rebase=0;rebase<2;++rebase){
  itemTransit49Fixture();auto& s=BotSupplyState(0);if(!rebase)s.scanTick=99999;
  int ended=-1;SCecilMove last;
  for(int tick=2;tick<=350;++tick){
   patrolAlternate46Pose(tick);last=hopCheckpoint45Tick(tick);
   if(s.goalEntity!=991){ended=tick;break;}
  }
  check(ended>=202&&ended<=242&&s.ItemRejected(991,ended*.05)&&!s.patrolAlternate,
   "extended item cycle ends within ten seconds of no new hop gain with or without checkpoint rebases");
  check(last.forward==0&&last.strafe==0&&last.up==0&&s.goalSince==0&&!s.goalRelocationBudgeted,
   "failed item transit emits neutral without extending original attempt or granting recovery movement");
  if(ended<0)continue;
  auto& alternate=addItem(992,0,-16,botcore::CecilItemKind::Weapon);alternate.item.weapon=7;
  BotSupplyGraph().points[2].important_entity=992;BotSupplyGraph().points[0].links.push_back(2);
  player.pl.pl_PositionVector=FLOAT3D();_botRayBudget=16;
  BotSupplyTick(&player,0,ended+1,1000);
  check(s.goalEntity==992&&!s.ItemRejected(992,ended*.05)&&s.goalSince==(ended+1)*.05,
   "next normal typed item scan chooses a different eligible ranged weapon after bounded failed attempt");
 }
 itemTransit49Fixture();auto& s=BotSupplyState(0);s.scanTick=99999;
 for(int tick=2;tick<=300;++tick){player.pl.pl_PositionVector=FLOAT3D(float((tick-2)*.02),0,0);hopCheckpoint45Tick(tick);}
 check(s.goalEntity==991&&s.goalSince==0&&s.goalDeadline==45,
  "new best hop distance gain retains a slow valid extended item approach without renewing its deadline");
}
void itemTransit49Guards(){
 for(int guard=0;guard<17;++guard){
  itemTransit49Fixture();auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
  player.pl.pl_PositionVector=FLOAT3D(5,0,0);bool accepted=true,current=true;
  if(guard==0)g.points[1].flags=botcore::CECIL_JUMP;
  if(guard==1)g.points[1].flags=botcore::CECIL_TELEPORT;
  if(guard==2)g.points[1].flags=botcore::CECIL_UNREACHABLE;
  if(guard==3)g.points[1].flags=botcore::CECIL_CROUCH;
  if(guard==4)g.points[1].important_entity=991;
  if(guard==5)g.points[1].lock_entity=777;
  if(guard==6)s.blocked[1]=1;
  if(guard==7)s.followEntity=777;
  if(guard==8)s.interactionPoint=1;
  if(guard==9)s.useReleaseTick=9999;
  if(guard==10)accepted=false;
  if(guard==11)current=false;
  if(guard==12)player.m_pstState=PST_SWIM;
  if(guard==13)s.mappedWeaponGoal=false;
  if(guard==14){g.points[1].x=5;g.points[1].z=0;}
  if(guard==15)player.health=0;
  if(guard==16)player.pl.pl_PositionVector(1)=NAN;
  bool failed=false;
  for(int tick=2;tick<=300;++tick)failed|=BotCecilItemTransitFailed(&player,s,tick*.05,accepted,current);
  check(!failed&&s.goalEntity==991&&!s.ItemRejected(991,15),
   "passive item bound excludes special terminal locked liquid follow USE invalid and unowned contexts");
 }
 for(int change=0;change<11;++change){
  itemTransit49Fixture();auto& s=BotSupplyState(0);player.pl.pl_PositionVector=FLOAT3D(5,0,0);
  for(int tick=2;tick<180;++tick)BotCecilItemTransitFailed(&player,s,tick*.05,true,true);
  CWorld other;bool accepted=true;
  if(change==0)++s.generation;
  if(change==1)++player.en_ulID;
  if(change==2)++_botSupplyMapSerial;
  if(change==3)player.worldOverride=&other;
  if(change==4)++s.goalEntity;
  if(change==5)s.goalSince=1;
  if(change==6)s.goalDeadline=40;
  if(change==7)player.en_vGravityDir=FLOAT3D(0,1,0);
  if(change==8)accepted=false;
  if(change==9)s.ClearGoal();
  const double now=change==10?9.5:9;
  BotCecilItemTransitFailed(&player,s,now,accepted,true);
  bool failed=false;
  for(int step=1;step<=40;++step)failed|=BotCecilItemTransitFailed(&player,s,now+step*.05,true,true);
  check(!failed&&!s.ItemRejected(991,12),
   "life entity map world goal attempt deadline gravity ownership reset and observation gaps erase item clock");
 }
 itemTransit49Fixture();auto& air=BotSupplyState(0);player.pl.pl_PositionVector=FLOAT3D(5,0,0);
 for(int tick=2;tick<180;++tick)BotCecilItemTransitFailed(&player,air,tick*.05,true,true);
 air.airMovementTime=9;double f=.3,st=0,up=0;
 BotCecilSafeMotion(&player,air,9,f,st,up,0,1,true);
 bool carried=false;
 for(int tick=181;tick<=225;++tick)carried|=BotCecilItemTransitFailed(&player,air,tick*.05,true,true);
 check(!carried&&!air.ItemRejected(991,12),"early air-safety return erases unrelated ground item progress history");
 itemTransit49Fixture();auto& s=BotSupplyState(0);player.pl.pl_PositionVector=FLOAT3D(5,0,0);
 for(int tick=2;tick<202;++tick)BotCecilItemTransitFailed(&player,s,tick*.05,true,true);
 const int rays=rayCount,lookups=worldLookups;allocations=0;measuring=true;
 const bool ended=BotCecilItemTransitFailed(&player,s,10.1,true,true);measuring=false;
 check(ended&&rayCount==rays&&worldLookups==lookups&&allocations==0&&s.ItemRejected(991,40)&&!s.ItemRejected(991,40.1),
  "bounded failure adds no geometry scans allocations or movement and uses exact existing thirty second backoff");
}
int importantPatrol48Enter(bool entity){
 importantPatrol48Fixture(entity);auto& s=BotSupplyState(0);
 for(int tick=2;tick<=300;++tick){patrolAlternate46Pose(tick);hopCheckpoint45Tick(tick);if(s.patrolAlternate)return tick;}
 return -1;
}
void importantPatrol48(){
 for(bool entity:{false,true}){
  const int entered=importantPatrol48Enter(entity);auto& s=BotSupplyState(0);
  check(entered>=202&&hopCheckpointEvents>=2&&s.patrolAlternate,
    "two real failed checkpoints allow existing alternate ordinary transit toward SAME important endpoint");
  if(entered<0)continue;
  const double since=s.patrolSince;check(s.importantGoal&&s.goal==4&&s.goalSince==7&&s.goalEntity==0,
    "alternate recovery preserves important goal and original goal time");
  player.m_pstState=PST_FALL;const auto air=hopCheckpoint45Tick(entered+1);
  check(air.forward==0&&air.strafe==0&&air.up==0&&s.goal==4&&s.patrolSince==since,
    "important alternate remains neutral in air without renewing six-second lifetime");
  player.m_pstState=PST_STAND;const int casts=rayCount;const auto deferred=hopCheckpoint45Tick(entered+2,true,2);
  check(deferred.forward==0&&deferred.strafe==0&&s.goal==4&&s.patrolSince==since&&rayCount==casts,
    "important alternate budget deferral retains SAME goal and fixed deadline without an unverified step");
  const auto move=hopCheckpoint45Tick(entered+3);
  check(move.active&&std::hypot(move.forward,move.strafe)<=.300001&&move.up==0&&
    (move.buttons&EXPECTED_NATIVE_USE)==0&&s.interactionPoint<0&&s.useReleaseTick<0&&s.goal==4,
    "important alternate uses only existing bounded verified hint movement and never synthesizes endpoint USE or completion");
  for(int tick=entered+4;tick<entered+120;++tick)hopCheckpoint45Tick(tick,true,2);
  const auto expired=hopCheckpoint45Tick(entered+120);
  check(!s.patrolAlternate&&s.goal<0&&!expired.active&&expired.buttons==0&&endEvents==0,
    "fixed six-second exhausted important alternate explicitly abandons rather than pretending endpoint arrival or interaction");
 }
}


SCecilMove liquidProjection48Fixture(double sign=1){
 setup(2);auto& g=BotSupplyGraph();g.points[0].x=g.points[0].y=g.points[0].z=0;g.points[0].radius=.5;
 g.points[1].x=0;g.points[1].y=float(sign);g.points[1].z=-12;g.points[1].radius=.25;
 auto& s=BotSupplyState(0);s.goal=1;s.anchor=0;s.scanTick=99999;
 player.m_pstState=PST_DIVE;BotCecilSettings().bAvoidPits=0;_botRayBudget=16;
 return BotSupplyTick(&player,0,1,1000);
}
int liquidProjection48Safety(SCecilMove& move,double now=.05,bool owner=true){
 return BotCecilSafeMotion(&player,BotSupplyState(0),now,move.forward,move.strafe,move.up,0,1,owner);
}
void liquidProjection48(){
 for(double sign:{-1,1}){
  auto move=liquidProjection48Fixture(sign);const auto request=move;auto& s=BotSupplyState(0);wallMode=5;
  const int rays=rayCount,lookups=worldLookups;allocations=0;measuring=true;
  const int result=liquidProjection48Safety(move);measuring=false;
  check(result==1&&move.forward==0&&move.strafe==0&&move.up==request.up&&std::fabs(move.up)>.05,
    "blocked diagonal liquid NAV preserves exact already-selected signed vertical component only after its own fresh physical cast");
  check(rayCount-rays==2&&liquidAxisQueries==1&&_botRayBudget==14&&s.probe.wallRays==2&&s.probe.floorRays==0&&
    lastModels==CCastRay::TT_COLLISIONBOX&&lastMask==BPOF_PASSABLE&&lastPhysical&&!lastOverHit&&worldLookups==lookups&&allocations==0,
    "liquid projection uses exactly one extra existing physical cast within shared sixteen budget without floor authority lookup or allocation");
  check(s.goal==1&&s.anchor==0&&s.goalSince==0&&s.goalDeadline==0&&s.escapeUntil==0,
    "verified projection creates no target arrival goal deadline or persistent escape hold");
 }
 auto clear=liquidProjection48Fixture();const auto wanted=clear;const int rays=rayCount;
 check(liquidProjection48Safety(clear)==1&&clear.forward==wanted.forward&&clear.strafe==wanted.strafe&&clear.up==wanted.up&&
   rayCount-rays==1&&liquidAxisQueries==0,"unobstructed diagonal remains bit-for-bit unchanged with no projection query");
 for(int denied=0;denied<24;++denied){
  auto move=liquidProjection48Fixture();auto& s=BotSupplyState(0);wallMode=5;bool owner=true;
  if(denied==0)owner=false;
  if(denied==1)player.m_pstState=PST_STAND;
  if(denied==2)s.currentNavTime=-1;
  if(denied==3)s.currentNavTravel=false;
  if(denied==4)s.interactionPoint=0;
  if(denied==5)s.useReleaseTick=999;
  if(denied==6)s.followEntity=777;
  if(denied==7)move.up=0;
  if(denied==8)_botRayBudget=3;
  if(denied==9)s.escapeAfter=.2;
  if(denied==10)player.health=0;
  if(denied==11)player.m_penWeapons=nullptr;
  if(denied==12)++player.en_ulID;
  if(denied==13)s.playable=false;
  if(denied==14)player.flags=ENF_DELETED;
  if(denied==15)move.up=NAN;
  if(denied==16)move.up=.04999;
  if(denied==17)_botRayBudget=0;
  if(denied==18)player.en_vCurrentTranslationAbsolute(2)=NAN;
  if(denied==19){move.forward=.04;move.strafe=0;}
  if(denied==20)s.currentNavGoal=-1;
  if(denied==21)s.hop=-1;
  if(denied==22)s.blocked[s.hop]=1;
  if(denied==23)move.forward=NAN;
  const auto request=move;liquidProjection48Safety(move,.05,owner);
  check(liquidAxisQueries==0&&!(move.forward==0&&move.strafe==0&&std::isfinite(request.up)&&std::fabs(request.up)>=.05&&move.up==request.up),
    "Human ground stale nontravel interaction USE follow zero-up budget cooldown dead identity invalid or subthreshold intent cannot acquire liquid projection");
 }
 for(int blocked=0;blocked<4;++blocked){
  auto move=liquidProjection48Fixture();wallMode=5;liquidAxisBlocked=blocked!=3;liquidAxisInvalid=blocked==3;CWorld foreign;
  obstruction.type=CEntity::RT_BRUSH;obstruction.entityPhysicsFlags=blocked==0?EPF_MOVABLE:0;
  obstruction.en_pwoWorld=blocked==1?&foreign:player.GetWorld();obstruction.flags=blocked==2?ENF_DELETED:0;
  const int result=liquidProjection48Safety(move);
  check(liquidAxisQueries==1&&move.up==0&&result==2&&std::fabs(move.strafe)>.05,
    "vertical HIT or invalid query never emits vertical input and retains independently checked legacy horizontal escape");
 }
 auto reserve=liquidProjection48Fixture();wallMode=5;_botRayBudget=4;
 check(liquidProjection48Safety(reserve)==1&&liquidAxisQueries==1&&_botRayBudget==2&&reserve.forward==0&&reserve.up>.05,
   "projection reserves two final shared rays at its exact four-before-primary budget boundary");
 auto held=liquidProjection48Fixture();wallMode=5;
 check(liquidProjection48Safety(held,.05,false)==2&&held.up==0,"existing Human-owned fixture establishes legacy horizontal hold");
 auto& s=BotSupplyState(0);const double until=s.escapeUntil;
 _botRayBudget=16;auto pending=BotSupplyTick(&player,0,2,1000);const int axis=liquidAxisQueries;
 check(liquidProjection48Safety(pending,.1,true)==2&&pending.up==0&&s.escapeUntil==until&&liquidAxisQueries==axis,
   "new projection never overrides or extends an already verified legacy point-six-second hold");
 for(int tick=3;tick<=34;++tick){_botRayBudget=16;pending=BotSupplyTick(&player,0,tick,1000);liquidProjection48Safety(pending,tick*.05,true);}
 check(pending.forward==0&&pending.strafe==0&&pending.up>.05&&liquidAxisQueries>axis,
   "fresh diagonal after original hold and unchanged no-progress cooldown can use verified existing vertical intent");
}

void supplyDiagnosticsBoundsAndReasons(){
 setup(25);bot_bDiagnostics=true;supplyDiagLines=0;supplyDiagText.clear();
 for(int i=1;i<25;++i){addItem(1000+i,0,float(-10*i),botcore::CecilItemKind::Weapon);BotSupplyGraph().points[i].important_entity=1000+i;}
 auto& s=BotSupplyState(0);s.goals.Run(BotSupplyGraph(),0,s.blocked.data(),s.blocked.size());
 auto input=BotCecilItemInput(&player,s,1000);_botRayBudget=16;
 BotCecilChooseMappedWeapon(&player,s,input,0,1,.05);
 check(supplyDiagLines==18&&supplyDiagText.find("eligible=24 emitted=16")!=std::string::npos,
   "selection bounds sixteen candidates plus one selection and its existing connector cast");
 const int lines=supplyDiagLines;s.ClearGoal();_botRayBudget=16;BotCecilChooseMappedWeapon(&player,s,input,0,2,.10);
 check(supplyDiagLines==lines,"selection cooldown survives ClearGoal and cannot spam repeated decisions");
 s.ClearGoal();_botRayBudget=16;BotCecilChooseMappedWeapon(&player,s,input,0,21,1.05);
 check(supplyDiagLines==lines+18,"selection diagnostic resumes at one second without changing admission");
 check(s.goals.Parent(-1)==-1&&s.goals.Parent(25)==-1&&s.goals.Parent(0)==-1&&s.goals.Parent(24)==23,
   "diagnostic parent accessor handles absent root out-of-range and actual selected parent");
 BotSupplyGraph().points[5].flags=botcore::CECIL_TELEPORT;
 BotSupplyGraph().points[6].flags=botcore::CECIL_OVERRIDE;
 BotSupplyGraph().points[20].flags=botcore::CECIL_JUMP;
 s.goals.Run(BotSupplyGraph(),0,s.blocked.data(),s.blocked.size());int from,to;unsigned flags;
 BotCecilSupplyDiagPath(s,24,from,to,flags);
 check(from==4&&to==5&&(flags&botcore::CECIL_TELEPORT),"first special edge is from actual selected path including teleport endpoints before override");
 BotCecilSupplyDiagPath(s,999,from,to,flags);check(from==-1&&to==-1&&flags==0,"invalid diagnostic path is absent");
 CWeaponItem weapon;weapon.cls.name="Classes/WeaponItem.ecl";weapon.en_ulID=991;weapon.m_ulPickedMask=1u<<4;
 weapon.m_bPickupOnce=1;weapon.m_bDropped=0;weapon.m_bRespawn=1;weapon.m_EwitType=10;
 s.goalEntity=991;supplyDiagText.clear();supplyDiagLines=0;
 BotCecilSupplyDiagUnavailable(&player,s,&weapon,0,22,1.1,"hidden",input);
 check(supplyDiagText.find("reason=hidden")!=std::string::npos&&supplyDiagText.find("player_index=5 picked_mask=16 picked_for_player=0 pickup_once=1 dropped=0 respawn=1 raw_weapon_type=10 weapons_stay=1")!=std::string::npos,
   "unavailable diagnostic distinguishes another player's picked bit from visibility rejection and exact item settings");
 BotCecilSupplyDiagUnavailable(&player,s,&weapon,0,23,1.15,"hidden",input);
 check(supplyDiagLines==1,"unavailable diagnostic is independently cooldown bounded");
 check(supplyDiagText.find("weapon_metadata_valid=1")!=std::string::npos,"real weapon metadata is explicitly valid");
 CEntity notWeapon;CWeaponItem deletedWeapon;deletedWeapon.cls.name="Classes/WeaponItem.ecl";deletedWeapon.flags=ENF_DELETED;
 for(CEntity* absent:{static_cast<CEntity*>(nullptr),static_cast<CEntity*>(&deletedWeapon),&notWeapon}){
  s.diagUnavailableLast=-1;supplyDiagText.clear();
  BotCecilSupplyDiagUnavailable(&player,s,absent,0,24,1.2,"unavailable",input);
  check(supplyDiagText.find("weapon_metadata_valid=0")!=std::string::npos&&supplyDiagText.find("picked_for_player=-1")!=std::string::npos,
    "missing deleted and nonweapon objects never claim a known false pickup bit");
 }

 s.Reset();check(s.diagSelectionLast==-1&&s.diagUnavailableLast==-1&&s.diagTerminalLast==-1,"lifecycle reset clears only diagnostic clocks as well as normal reset");
 bot_bDiagnostics=false;
 double last=-1;check(!BotCecilSupplyDiagDue(1,last)&&last==-1,"disabled diagnostics do not update telemetry clocks");
 bot_bDiagnostics=true;check(!BotCecilSupplyDiagDue(NAN,last)&&!BotCecilSupplyDiagDue(-1,last)&&last==-1,"invalid diagnostic time never emits");
 bot_bDiagnostics=false;
}
void supplyDiagnosticsRetentionAndTerminal(){
 SCecilMove before[2],after[2];double starts[2],deadlines[2],f[2],st[2],up[2];int codes[2],rays[2];
 for(int mode=0;mode<2;++mode){
  setup(3);bot_bDiagnostics=mode;auto& weapon=addItem(991,0,-22,botcore::CecilItemKind::Weapon);
  BotSupplyGraph().points[2].important_entity=991;_botRayBudget=16;BotSupplyTick(&player,0,1,1000);
  auto& s=BotSupplyState(0);starts[mode]=s.goalSince;deadlines[mode]=s.goalDeadline;
  player.pl.pl_PositionVector=FLOAT3D(0,0,-10);s.anchor=1;_botRayBudget=16;before[mode]=BotSupplyTick(&player,0,2,1000);
  supplyDiagLines=0;supplyDiagText.clear();player.en_vCurrentTranslationAbsolute=FLOAT3D(1,2,3);
  f[mode]=before[mode].forward;st[mode]=before[mode].strafe;up[mode]=before[mode].up;
  codes[mode]=BotCecilSafeMotion(&player,s,.10,f[mode],st[mode],up[mode],0,1,true);rays[mode]=rayCount;
  if(mode){
   check(supplyDiagLines==1&&supplyDiagText.find("[CecilSupplyDiagTerminal]")!=std::string::npos&&
     supplyDiagText.find("support=0 support_render=-1")!=std::string::npos&&supplyDiagText.find("velocity=(1.000,2.000,3.000)")!=std::string::npos,
     "terminal diagnostic reports actual absent support and motion without claiming grounded authority");
   BotCecilSupplyDiagTerminal(&player,s,.15,true,true);check(supplyDiagLines==1,"terminal diagnostic has independent one-second bound");
  }else check(supplyDiagLines==0,"disabled terminal telemetry emits no output");
  _botRayBudget=16;after[mode]=BotSupplyTick(&player,0,3,7.9);
  check(s.goalEntity==991&&s.goalSince==starts[mode]&&s.goalDeadline==deadlines[mode]&&!after[mode].ownsMovement,
    "telemetry preserves retained goal and original deadline through close-combat action yield");
  weapon.pickable=false;supplyDiagLines=0;supplyDiagText.clear();_botRayBudget=16;
  BotSupplyTick(&player,0,4,7.9);
  check(s.goalEntity==0&&std::strcmp(lastEnd,"unavailable")==0,"telemetry preserves real unavailable ending");
  if(mode)check(supplyDiagText.find("reason=stub_unpickable")!=std::string::npos,"unavailable ending uses the actual read-filter rejection reason");
 }
 check(f[0]==f[1]&&st[0]==st[1]&&up[0]==up[1]&&codes[0]==codes[1]&&rays[0]==rays[1]&&
  starts[0]==starts[1]&&deadlines[0]==deadlines[1],"terminal telemetry leaves final safety commands rays and lifetime pins unchanged");
 bot_bDiagnostics=false;
}
void boundedSupplySegment(){
 // Real006 Minigun connector: floor at1.309612, requested target at1.258371.
 for(float distance:{.5f,1.258371f,1.309612f}){
  setup();wallMode=2;physicalHitDistanceOverride=distance;_botRayBudget=16;
  bool valid=false;SCecilSupplyCastDetail detail;const int before=rayCount;
  const bool clear=BotSupplyClear(&player,FLOAT3D(0,0,0),FLOAT3D(0,0,-1.258371f),nullptr,&valid,&detail);
  check(valid&&detail.valid&&rayCount-before==1&&_botRayBudget==15,
    "bounded connector still uses exactly one valid original physical query");
  check(clear==(distance>1.258371f)&&detail.clear==clear,
    "physical blocker beyond connector endpoint cannot reject the segment, inside or endpoint hits still block");
  check(detail.distance==distance&&detail.hit==obstruction.en_ulID,
    "segment clipping preserves actual hit metadata including beyond-end floor evidence");
 }
 setup();wallMode=2;physicalHitDistanceOverride=1.309612f;invalidHitDistance=true;bool valid=false;
 check(!BotSupplyClear(&player,FLOAT3D(),FLOAT3D(0,0,-1.258371f),nullptr,&valid)&&!valid,
   "invalid physical distance cannot authorize connector clearance");
 setup();wallMode=2;physicalHitDistanceOverride=1.309612f;_botRayBudget=2;valid=true;const int before=rayCount;
 check(!BotSupplyClear(&player,FLOAT3D(),FLOAT3D(0,0,-1.258371f),nullptr,&valid)&&!valid&&rayCount==before,
   "bounded segment never borrows the final reserved safety rays");
}
void supplyConnectorDiagnostics(){
 int rays[2],lookups[2];unsigned random[2];bool rejected[2];
 for(int mode=0;mode<2;++mode){
  setup(3);bot_bDiagnostics=mode;supplyDiagLines=0;supplyDiagText.clear();
  addItem(991,0,-22,botcore::CecilItemKind::Weapon);BotSupplyGraph().points[2].important_entity=991;
  auto& s=BotSupplyState(0);s.goals.Run(BotSupplyGraph(),0,s.blocked.data(),s.blocked.size());
  wallMode=2;obstruction.en_ulID=77;obstruction.type=CEntity::RT_BRUSH;obstruction.entityPhysicsFlags=512;
  const auto input=BotCecilItemInput(&player,s,1000);_botRayBudget=16;worldLookups=0;
  BotCecilChooseMappedWeapon(&player,s,input,0,1,.05);
  rays[mode]=rayCount;lookups[mode]=worldLookups;random[mode]=s.rng;rejected[mode]=s.ItemRejected(991,.05,false);
  check(s.goalEntity==0&&rejected[mode],"blocked mapped weapon remains rejected with diagnostics on or off");
  if(mode)check(supplyDiagText.find("[CecilSupplyDiagConnector]")!=std::string::npos&&
    supplyDiagText.find("entity=991 anchor=2 valid=1 clear=0 hit=77 render=4 physics=512")!=std::string::npos,
    "mapped rejection identifies the actual existing physical cast blocker rather than inferring LOS failure");
  else check(supplyDiagLines==0,"disabled connector diagnostics produce no lines");
  const int lines=supplyDiagLines;s.ClearRejections();_botRayBudget=16;
  BotCecilChooseMappedWeapon(&player,s,input,0,2,.10);
  check(supplyDiagLines==lines,"connector rows share the one-second bounded selection batch");
 }
 check(rays[0]==1&&rays[0]==rays[1]&&lookups[0]==lookups[1]&&random[0]==random[1]&&rejected[0]==rejected[1],
   "connector observation changes no ray lookup RNG or rejection decision");
 bot_bDiagnostics=false;
}
void approachArrivalGeometry(){
 setup(35);auto& g=BotSupplyGraph();for(auto& p:g.points)p.links.clear();
 g.points[8].x=-37.783684f;g.points[8].y=24.503325f;g.points[8].z=63.127693f;g.points[8].radius=2;g.points[8].links={12};
 g.points[12].x=-51;g.points[12].y=24.5;g.points[12].z=63;g.points[12].radius=4;g.points[12].flags=42;g.points[12].links={34};
 g.points[34].x=63.094364f;g.points[34].y=49.254681f;g.points[34].z=-63.054783f;
 botcore::CecilMotionInput in;in.alive=true;in.anchor=8;in.goal=34;
 in.x=g.points[8].x;in.y=g.points[8].y;in.z=g.points[8].z;
 auto& n=BotSupplyState(0).navigator;auto first=n.Update(g,nullptr,0,in);
 check(first.hop==12&&first.flags==42&&first.up==1,"authored target override requests jump on initial8-to12 action");
 in.now=.05;in.x=-49.036;in.y=29.482;in.z=63.019;
 auto next=n.Update(g,nullptr,0,in);
 check(n.SourceSlot(34)==12&&next.hop==34,"recorded high airborne position satisfies existing shifted-radius arrival without contact input");
 // This is current mathematical behavior, not a native proof of which action
 // caused the miss or authorization to change the authored flags/radius.
}
void bouncer009Fixture(int run=0){
 setup(193);auto& g=BotSupplyGraph();for(auto& p:g.points)p.links.clear();
 g.points[7].x=2.802741289138794f;g.points[7].y=18.485923767089844f;g.points[7].z=63.08060073852539f;g.points[7].radius=2;g.points[7].links={8};
 g.points[8].x=-37.78368377685547f;g.points[8].y=24.503324508666992f;g.points[8].z=63.12769317626953f;g.points[8].radius=2;g.points[8].links={7,13,12,187,83,94};
 g.points[11].x=-50.95821762084961f;g.points[11].y=24.501291275024414f;g.points[11].z=55.24614334106445f;g.points[11].radius=2;g.points[11].links={10,13,12,89,189,94};
 g.points[12].x=-51;g.points[12].y=24.5;g.points[12].z=63;g.points[12].radius=4;g.points[12].flags=42;g.points[12].links={34};
 g.points[34].x=63.094364166259766f;g.points[34].y=49.25468063354492f;g.points[34].z=-63.05478286743164f;g.points[34].radius=2;g.points[34].important_entity=243;
 auto& item=addItem(243,g.points[34].x,g.points[34].z,botcore::CecilItemKind::Weapon);item.pl.pl_PositionVector(2)=g.points[34].y;
 player.en_ulID=567;player.w.usable=3;
 auto& s=BotSupplyState(0);s.entity=567;s.goal=34;s.goalEntity=243;s.goalSince=0;s.goalDeadline=999;s.scanTick=99999;s.anchor=7;s.hop=8;
 botcore::CecilMotionInput in;in.alive=true;in.anchor=7;in.goal=34;in.x=g.points[7].x;in.y=g.points[7].y;in.z=g.points[7].z;s.navigator.Update(g,nullptr,0,in);
 player.pl.pl_PositionVector=run?FLOAT3D(-36.412056f,23.959534f,63.125698f):FLOAT3D(-35.983700f,23.894304f,63.126614f);
 player.en_vCurrentTranslationAbsolute=FLOAT3D(-17.15173f,2.613636f,.01f);
 floorEntity.en_ulID=54;floorEntity.flags=0;floorEntity.entityPhysicsFlags=0;floorEntity.type=CEntity::RT_BRUSH;floorEntity.en_pwoWorld=player.GetWorld();player.en_penReference=&floorEntity;
 bot_bEnabled=bot_bSupplyNavigation=true;_botSupplyMapReady=1;
 BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,7);
}


void bouncer011Native010Replay(){
 // Actual010 local2/gen7 ticks1025..1035. Recorded trajectory is input only;
 // this checks native decision outputs, not an Engine physics simulation.
 const float rows[][7]={{-50.962830f,23.929928f,54.148029f,0.075359f,2.280761f,17.248251f,194},
 {-50.962795f,24.771252f,55.103348f,0.000654f,16.826462f,19.106359f,0},
 {-50.966557f,25.537575f,55.983761f,-0.075227f,15.326462f,17.608280f,0},
 {-50.970715f,26.228897f,56.861252f,-0.083168f,13.826462f,17.549805f,0},
 {-50.974899f,26.845221f,57.738743f,-0.083686f,12.326462f,17.549801f,0},
 {-50.979084f,27.386543f,58.616234f,-0.083722f,10.826463f,17.549801f,0},
 {-50.983269f,27.852867f,59.493725f,-0.083727f,9.326463f,17.549801f,0},
 {-50.972725f,28.244190f,60.297676f,0.210848f,7.826463f,16.079010f,0},
 {-50.949173f,28.560513f,61.027763f,0.471027f,6.326463f,14.601747f,0},
 {-50.913452f,28.801836f,61.683846f,0.714389f,4.826463f,13.121620f,0},
 {-50.865177f,28.968159f,62.265984f,0.965476f,3.326463f,11.642785f,0}};
 for(int diagnostics=0;diagnostics<2;++diagnostics){
  bouncer009Fixture();bot_bDiagnostics=diagnostics;auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
  s.navigator.Reset();s.anchor=10;s.hop=11;s.goalDeadline=73.943733;
  g.points[10].x=g.points[11].x;g.points[10].y=g.points[11].y;g.points[10].z=40;g.points[10].links={11};
  botcore::CecilMotionInput in;in.alive=true;in.anchor=10;in.goal=34;
  in.x=g.points[10].x;in.y=g.points[10].y;in.z=g.points[10].z;
  s.navigator.Update(g,nullptr,0,in);auto baseline=s.navigator;
  const auto rng=s.rng;const auto generation=s.generation;
  const int rays=rayCount,lookups=worldLookups;
  for(int i=0;i<11;++i){
   player.pl.pl_PositionVector=FLOAT3D(rows[i][0],rows[i][1],rows[i][2]);
   player.en_vCurrentTranslationAbsolute=FLOAT3D(rows[i][3],rows[i][4],rows[i][5]);
   floorEntity.en_ulID=(int)rows[i][6];player.en_penReference=rows[i][6]?&floorEntity:nullptr;
   in.x=rows[i][0];in.y=rows[i][1];in.z=rows[i][2];in.now=static_cast<float>((1025+i)*.05f);
   const int source=s.navigator.SourceSlot(34),hop=s.hop;const bool reached=BotCecilAtNode(&player,hop);
   auto move=s.navigator.Update(g,s.blocked.data(),s.blocked.size(),in);s.hop=move.hop;
   const auto original=baseline.Update(g,nullptr,0,in);auto* reference=player.en_penReference;
   const auto velocity=player.en_vCurrentTranslationAbsolute;
   BotCecilApproachCapture(s,1025+i,in.now,source,hop,reached,move);
   BotCecilBouncerApproach(&player,s,move);
   if(i==0||i==4){
    check(original.up==1&&move.up==0,"011 actual010 supported initial and nullref repeated11-to12 pulses suppressed");
    if(diagnostics)check(s.approach.move.up==1,"011 raw11 diagnostic retains original UP before suppression");
   }else check(move.up==original.up,"011 zero pulses and later12-to34 UP stay original");
   check(move.forward==original.forward&&move.strafe==original.strafe&&move.yaw_delta==original.yaw_delta&&
     move.flags==original.flags&&move.hop==original.hop&&s.navigator.SourceSlot(34)==baseline.SourceSlot(34),
     "011 preserves original route radius flags motion and navigator clock transitions");
   check(s.goalEntity==243&&s.goal==34&&s.goalDeadline==73.943733&&s.rng==rng&&s.generation==generation&&
     rayCount==rays&&worldLookups==lookups&&player.en_penReference==reference&&
     player.en_vCurrentTranslationAbsolute(1)==velocity(1)&&player.en_vCurrentTranslationAbsolute(2)==velocity(2)&&player.en_vCurrentTranslationAbsolute(3)==velocity(3),
     "011 does not modify entity physics life goal deadline RNG or add queries");
  }
  check(s.navigator.SourceSlot(34)==12&&s.hop==34,"011 does not change recorded later arrival or flight edge");
 }
 bot_bDiagnostics=false;
 for(int bad=0;bad<18;++bad){
  bouncer009Fixture();auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();s.navigator.Reset();
  botcore::CecilMotionInput in;in.alive=true;in.anchor=11;in.goal=34;
  in.x=g.points[11].x;in.y=g.points[11].y;in.z=g.points[11].z;
  auto move=s.navigator.Update(g,nullptr,0,in);s.hop=move.hop;
  check(move.up==1,"011 invalid-context fixture begins with real11-to12 jump");
  if(bad==0)g.points[11].x+=1;
  if(bad==1)g.points[11].radius=3;
  if(bad==2)g.points[11].flags=2;
  if(bad==3)g.points[11].links.pop_back();
  if(bad==4)std::swap(g.points[11].links[0],g.points[11].links[1]);
  if(bad==5)g.points[11].important_entity=99;
  if(bad==6)g.points[11].next_slot=12;
  if(bad==7)g.points[11].lock_entity=99;
  if(bad==8)s.blocked[11]=1;
  if(bad==9)s.blocked[12]=1;
  if(bad==10){player.en_penReference=nullptr;player.m_pstState=PST_FALL;}
  if(bad==11){player.en_penReference=nullptr;player.m_pstState=PST_SWIM;}
  if(bad==12){player.en_penReference=nullptr;player.m_pstState=PST_DIVE;}
  if(bad==13)floorEntity.entityPhysicsFlags=EPF_MOVABLE;
  if(bad==14)floorEntity.en_pwoWorld=nullptr;
  if(bad==15)++_botSupplyMapSerial;
  if(bad==16)_botSupplyMapReady=0;
  if(bad==17)g.points[11].id=99;
  BotCecilBouncerApproach(&player,s,move);
  check(move.up==1,"011 wrong11 metadata blocked source/destination or invalid context preserves original jump");
 }
 for(int crouch=0;crouch<2;++crouch){
  bouncer009Fixture();auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();s.navigator.Reset();player.en_penReference=nullptr;
  player.m_pstState=crouch?PST_CROUCH:PST_STAND;
  botcore::CecilMotionInput in;in.alive=true;in.anchor=11;in.goal=34;in.x=g.points[11].x;in.y=g.points[11].y;in.z=g.points[11].z;
  auto move=s.navigator.Update(g,nullptr,0,in);s.hop=move.hop;s.blocked[8]=1;
  BotCecilBouncerApproach(&player,s,move);
  check(move.up==0,"011 valid11-to12 stand/crouch uses current source block, not unrelated8 block");
 }

 bouncer009Fixture();auto& integrated=BotSupplyState(0);auto& graph=BotSupplyGraph();integrated.navigator.Reset();
 integrated.mappedWeaponGoal=true;integrated.goalSince=43.05;integrated.goalDeadline=73.943733;items.back().item.weapon=7;
 graph.points[10].x=graph.points[11].x;graph.points[10].y=graph.points[11].y;graph.points[10].z=40;graph.points[10].links={11};
 botcore::CecilMotionInput input;input.alive=true;input.anchor=10;input.goal=34;
 input.x=graph.points[10].x;input.y=graph.points[10].y;input.z=graph.points[10].z;
 integrated.navigator.Update(graph,nullptr,0,input);integrated.anchor=10;integrated.hop=11;
 player.pl.pl_PositionVector=FLOAT3D(rows[0][0],rows[0][1],rows[0][2]);
 player.en_vCurrentTranslationAbsolute=FLOAT3D(rows[0][3],rows[0][4],rows[0][5]);
 floorEntity.en_ulID=194;player.en_penReference=&floorEntity;_botRayBudget=40;
 const auto nativeMove=BotSupplyTick(&player,0,1025,1000);
 check(nativeMove.active&&nativeMove.up==0&&integrated.navigator.SourceSlot(34)==11&&integrated.hop==12&&integrated.goalEntity==243,
   "011 real BotSupplyTick arrival11 returns suppressed UP on exact active approach");
 bouncer009Fixture();auto& unrelated=BotSupplyState(0);auto& otherGraph=BotSupplyGraph();unrelated.navigator.Reset();otherGraph.points[13].links={12};
 botcore::CecilMotionInput other;other.alive=true;other.anchor=13;other.goal=34;
 other.x=otherGraph.points[13].x;other.y=otherGraph.points[13].y;other.z=otherGraph.points[13].z;
 auto unchanged=unrelated.navigator.Update(otherGraph,nullptr,0,other);unrelated.hop=unchanged.hop;
 check(unchanged.up==1&&unchanged.hop==12&&unrelated.navigator.SourceSlot(34)==13,"011 unrelated directed13-to12 has real UP request");
 BotCecilBouncerApproach(&player,unrelated,unchanged);
 check(unchanged.up==1,"011 unrelated13-to12 remains original even with same flagged destination");
 bouncer009Fixture();auto& g=BotSupplyGraph();g.points[11].links[0]=1;
 BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,7);
 check(!BotCecilBouncerBindingValid(),"011 loader cannot publish binding with changed original11 links");
}

void bouncer010Native009Replay(){
 // Actual completed009 local2/gen5 samples, ticks1368..1382. Recorded states
 // are inputs, not a portable simulation or a predicted native010 trajectory.
 const float rows[][7]={
 {-36.148930f,23.919989f,63.126144f,-17.151726f,2.613640f,.017174f,54},
 {-37.006516f,24.050671f,63.126995f,-17.151726f,2.613640f,.016988f,54},
 {-37.864067f,24.181347f,63.123688f,-17.151031f,2.613535f,-.066152f,0},
 {-38.721619f,24.237024f,63.120380f,-17.151031f,1.113535f,-.066152f,0},
 {-39.579170f,24.217701f,63.117073f,-17.151031f,-.386465f,-.066152f,0},
 {-40.436722f,24.123377f,63.113766f,-17.151031f,-1.886465f,-.066152f,0},
 {-41.281776f,24.007467f,63.110508f,-16.901091f,-2.318191f,-.065188f,193},
 {-42.159225f,24.722467f,63.101089f,-17.548983f,14.299999f,-.188361f,0},
 {-43.036667f,25.362467f,63.091148f,-17.548862f,12.799999f,-.198826f,0},
 {-43.914108f,25.927467f,63.080879f,-17.548796f,11.300000f,-.205382f,0},
 {-44.791550f,26.417467f,63.070812f,-17.548845f,9.800000f,-.201315f,0},
 {-45.668991f,26.832468f,63.060780f,-17.548853f,8.300000f,-.200686f,0},
 {-46.546432f,27.172468f,63.050781f,-17.548862f,6.800001f,-.199954f,0},
 {-47.423874f,27.437468f,63.040779f,-17.548862f,5.300001f,-.200043f,0},
 {-48.301315f,27.627468f,63.030777f,-17.548861f,3.800001f,-.200042f,0}};
 for(int diagnostics=0;diagnostics<2;++diagnostics){
  bouncer009Fixture();bot_bDiagnostics=diagnostics;auto& s=BotSupplyState(0);
  const auto rng=s.rng;auto originalNavigator=s.navigator;
  for(int i=0;i<15;++i){
   player.pl.pl_PositionVector=FLOAT3D(rows[i][0],rows[i][1],rows[i][2]);
   player.en_vCurrentTranslationAbsolute=FLOAT3D(rows[i][3],rows[i][4],rows[i][5]);
   player.en_penReference=rows[i][6]?&floorEntity:nullptr;floorEntity.en_ulID=(int)rows[i][6];
   botcore::CecilMotionInput in;in.alive=true;in.anchor=7;in.goal=34;
   in.x=rows[i][0];in.y=rows[i][1];in.z=rows[i][2];in.now=static_cast<float>((1368+i)*.05f); // Retail TickQuantum and multiplication are FLOAT.
   const auto original=originalNavigator.Update(BotSupplyGraph(),nullptr,0,in);
   const int previousSource=s.navigator.SourceSlot(s.goal),previousHop=s.hop;
   const bool reached=BotCecilAtNode(&player,previousHop);
   auto actual=s.navigator.Update(BotSupplyGraph(),s.blocked.data(),s.blocked.size(),in);s.hop=actual.hop;
   BotCecilApproachCapture(s,1368+i,in.now,previousSource,previousHop,reached,actual);
   BotCecilBouncerApproach(&player,s,actual);
   check(actual.active&&s.goalEntity==243&&s.goalDeadline==999&&s.rng==rng,
     "010 actual009 multistep replay retains goal deadline life and RNG");
   check(s.hop==original.hop&&actual.flags==original.flags&&s.navigator.SourceSlot(34)==originalNavigator.SourceSlot(34),
     "010 actual009 multistep replay preserves graph transition and flags");
   if(i==0||i==5||i==10){
    check(original.up==1&&actual.up==0,
      "010 actual009 grounded and unsupported repeat pulses are suppressed on source8 hop12");
    if(diagnostics)check(s.approach.move.up==1,"010 raw diagnostics retain unsupported requested up before suppression");
   }else check(actual.up==original.up,"010 zero and other-edge up remain unchanged");
  }
  check(s.navigator.SourceSlot(34)==12&&s.hop==34,
    "010 replay does not alter original high radius arrival or later flight");
 }
 bot_bDiagnostics=false;
 // Non-STAND airborne state is still excluded even without support. This rule
 // does not promote FALL, SWIM or DIVE to standing/contact authority.
 for(int state=0;state<3;++state){
  bouncer009Fixture();auto& s=BotSupplyState(0);player.en_penReference=nullptr;
  player.m_pstState=state==0?PST_FALL:(state==1?PST_SWIM:PST_DIVE);
  botcore::CecilMotionInput in;in.alive=true;in.anchor=8;in.goal=34;
  in.x=player.pl.pl_PositionVector(1);in.y=player.pl.pl_PositionVector(2);in.z=player.pl.pl_PositionVector(3);in.now=.05;
  auto move=s.navigator.Update(BotSupplyGraph(),nullptr,0,in);s.hop=move.hop;
  check(move.up==1,"010 state counterexample starts with real jump pulse");
  BotCecilBouncerApproach(&player,s,move);check(move.up==1,"010 unsupported FALL/liquid state retains original jump");
 }
 bouncer009Fixture();auto& s=BotSupplyState(0);s.navigator.Reset();player.en_penReference=nullptr;
 botcore::CecilMotionInput in;in.alive=true;in.anchor=8;in.goal=34;in.x=player.pl.pl_PositionVector(1);in.y=player.pl.pl_PositionVector(2);in.z=player.pl.pl_PositionVector(3);in.now=.05;
 auto move=s.navigator.Update(BotSupplyGraph(),nullptr,0,in);s.hop=move.hop;
 check(move.up==1&&s.navigator.SourceSlot(34)==8,"010 passive output fixture has the real bound edge and positive pulse");
 const auto original=move;const auto rng=s.rng;const int rays=rayCount,lookups=worldLookups;
 BotCecilBouncerApproach(&player,s,move);
 check(original.up==1&&move.up==0&&move.forward==original.forward&&move.strafe==original.strafe&&move.yaw_delta==original.yaw_delta&&
   rays==rayCount&&lookups==worldLookups&&rng==s.rng&&player.en_penReference==nullptr,
   "010 unsupported policy only removes positive up without support mutation casts lookups or RNG");
}

void bouncer009Transitions(){
 for(int run=0;run<2;++run){
  bouncer009Fixture(run);bot_bDiagnostics=true;supplyDiagText.clear();const auto before=BotSupplyState(0).rng;
  const auto m=BotSupplyTick(&player,0,1,1000);auto& s=BotSupplyState(0);
  check(m.active&&m.up==0&&m.flags==42&&s.navigator.SourceSlot(34)==8&&s.hop==12,
    "009 both native first approach transitions remove only ordinary up on the actual8-to12 edge");
  check(s.approach.move.up==1&&s.goalEntity==243&&s.goalDeadline==999&&s.rng==before&&BotSupplyGraph().points[12].radius==4,
    "009 raw requested jump flags radius target deadline and RNG remain original");
 }
 bot_bDiagnostics=false;
 for(int bad=0;bad<25;++bad){
  bouncer009Fixture();auto& s=BotSupplyState(0);
  if(bad==0)player.en_vGravityDir=FLOAT3D(0,1,0);
  if(bad==1)floorEntity.flags=ENF_DELETED;
  if(bad==2)floorEntity.entityPhysicsFlags=EPF_MOVABLE;
  if(bad==3)floorEntity.en_pwoWorld=nullptr;
  if(bad==4)floorEntity.type=CEntity::RT_MODEL;
  if(bad==5)player.m_pstState=PST_FALL;
  if(bad==6)player.m_pstState=PST_SWIM;
  if(bad==7)player.health=0;
  if(bad==8)player.flags=ENF_DELETED;
  if(bad==9)player.en_vCurrentTranslationAbsolute(1)=NAN;
  if(bad==10)++_botSupplyMapSerial;
  if(bad==11)_botSupplyMapReady=0;
  if(bad==12)bot_bEnabled=false;
  if(bad==13)bot_bSupplyNavigation=false;
  if(bad==14)player.m_penWeapons=nullptr;
  if(bad==15)player.body.m[0][0]=2;
  if(bad==16)BotSupplyGraph().points[12].radius=3;
  if(bad==17)BotSupplyGraph().points[8].links.pop_back();
  if(bad==18)s.entity++;
  if(bad==19)s.playable=false;
  if(bad==20)player.health=NAN;
  if(bad==21)player.health=INFINITY;
  if(bad==22)s.blocked[8]=1;
  if(bad==23)s.blocked[12]=1;
  if(bad==24)s.blocked.resize(12);
  botcore::CecilMotionInput in;in.alive=true;in.anchor=8;in.goal=34;in.x=player.pl.pl_PositionVector(1);in.y=player.pl.pl_PositionVector(2);in.z=player.pl.pl_PositionVector(3);in.now=.05;
  auto move=s.navigator.Update(BotSupplyGraph(),nullptr,0,in);s.hop=move.hop;const auto original=move;
  check(original.up==1,"009 rejection fixture has a real ordinary jump to preserve");
  const int rays=rayCount,lookups=worldLookups;BotCecilBouncerApproach(&player,s,move);
  check(move.up==original.up&&move.flags==original.flags&&move.forward==original.forward&&rayCount==rays&&worldLookups==lookups,
    "009 invalid context cannot modify ordinary jump or add rays/lookups");
 }
 for(int bad=0;bad<8;++bad){
  bouncer009Fixture();
  if(bad==0)BotCecilBouncerPublish(false,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,7);
  if(bad==1)BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\Other.wld",0xff3776e0u,0xe4571656u,7);
  if(bad==2)BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0,0xe4571656u,7);
  if(bad==3)BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0,7);
  if(bad==4)BotCecilBouncerPublish(true,nullptr,0xff3776e0u,0xe4571656u,7);
  if(bad==5){BotSupplyGraph().points.resize(12);BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,7);}
  if(bad==6){BotSupplyGraph().points[8].x+=1;BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,7);}
  if(bad==7)BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,6);
  check(!BotCecilBouncerBindingValid(),"009 failed loading/path/CRC/metadata/serial clears or revokes binding");
 }
 for(int source:{11,12}){
  bouncer009Fixture();auto& s=BotSupplyState(0);s.navigator.Reset();
  const auto& p=BotSupplyGraph().points[source];botcore::CecilMotionInput in;
  in.alive=true;in.anchor=source;in.goal=34;in.x=p.x;in.y=p.y;in.z=p.z;
  auto m=s.navigator.Update(BotSupplyGraph(),nullptr,0,in);s.hop=m.hop;const auto before=m;
  BotCecilBouncerApproach(&player,s,m);
  check(before.up==1&&m.up==(source==11?0:1)&&m.flags==before.flags&&s.navigator.SourceSlot(34)==source,
    "011 bound11-to12 suppresses UP while12-to34 retains original jump request");
 }
 bouncer009Fixture();auto& s=BotSupplyState(0);botcore::CecilMotionInput in;
 in.alive=true;in.anchor=8;in.goal=34;in.x=player.pl.pl_PositionVector(1);in.y=player.pl.pl_PositionVector(2);in.z=player.pl.pl_PositionVector(3);in.now=.05;
 auto original=s.navigator.Update(BotSupplyGraph(),nullptr,0,in);s.hop=original.hop;
 auto baseline=s.navigator;auto changed=original;BotCecilBouncerApproach(&player,s,changed);
 check(changed.up==0&&original.up==1&&changed.forward==original.forward&&changed.strafe==original.strafe&&
   changed.yaw_delta==original.yaw_delta&&changed.flags==original.flags&&changed.hop==original.hop,
   "009 changes only copied positive up and no other motion component");
 for(int i=2;i<9;++i){in.now=i*.05;const auto a=s.navigator.Update(BotSupplyGraph(),nullptr,0,in),b=baseline.Update(BotSupplyGraph(),nullptr,0,in);
  check(a.up==b.up&&a.hop==b.hop&&a.flags==b.flags,"009 output suppression leaves original navigator jump cooldown bit-for-bit unchanged");}
 for(int mode=0;mode<2;++mode){
  bouncer009Fixture();bot_bDiagnostics=mode;const auto& s=BotSupplyState(0);
  const auto move=BotSupplyTick(&player,0,1,1000);
  check(move.up==0&&move.flags==42&&s.goalDeadline==999,"009 diagnostics toggle cannot change supported approach policy");
 }
 for(int which=0;which<7;++which){
  bouncer009Fixture();auto& s=BotSupplyState(0);botcore::CecilMotionInput in;
  in.alive=true;in.anchor=8;in.goal=34;in.x=player.pl.pl_PositionVector(1);in.y=player.pl.pl_PositionVector(2);in.z=player.pl.pl_PositionVector(3);in.now=.05;
  auto move=s.navigator.Update(BotSupplyGraph(),nullptr,0,in);s.hop=move.hop;
  if(which==0)move.active=false;
  if(which==1)move.stuck=true;
  if(which==2)move.relocated=true;
  if(which==3)move.arrived=true;
  if(which==4)move.up=0;
  if(which==5)move.up=-1;
  if(which==6)move.flags=2;
  const auto before=move;BotCecilBouncerApproach(&player,s,move);
  check(move.up==before.up&&move.flags==before.flags,"009 nontravel/negative/ordinary-unrelated jump outputs stay unchanged");
 }
 bouncer009Fixture();BotCecilBouncerPublish(false,"",0,0,7);check(!BotCecilBouncerBindingValid(),"009 disable publication clears previous map binding");
 bot_bDiagnostics=false;
}
void approach008Transitions(){
 // Actual Build008 per-action positions translated by node12's origin. This
 // replays navigation mathematics only, never engine dynamics or a proposed fix.
 const double samples[2][3][3]={
  {{15.016300,-.605696,.126614},{3.511040,4.749033,.030994},{2.633575,4.635935,.023247}},
  {{14.587944,-.540466,.125698},{3.082676,4.814253,.027962},{2.205212,4.701155,.020004}}
 };
 for(int run=0;run<2;++run){
  setup(35);auto& g=BotSupplyGraph();for(auto& p:g.points)p.links.clear();
  g.points[7].x=53.802741f;g.points[7].y=-6.014077f;g.points[7].z=.080601f;g.points[7].radius=2;g.points[7].links={8};
  g.points[8].x=13.216316f;g.points[8].y=.003325f;g.points[8].z=.127693f;g.points[8].radius=2;g.points[8].links={12};
  g.points[12].x=0;g.points[12].y=0;g.points[12].z=0;g.points[12].radius=4;g.points[12].flags=42;g.points[12].links={34};
  g.points[34].x=114.094364f;g.points[34].y=24.754681f;g.points[34].z=-126.054783f;
  auto& n=BotSupplyState(0).navigator;botcore::CecilMotionInput in;in.alive=true;in.goal=34;in.anchor=7;
  in.x=g.points[7].x;in.y=g.points[7].y;in.z=g.points[7].z;in.yaw=90;n.Update(g,nullptr,0,in);
  in.now=.05;in.x=samples[run][0][0];in.y=samples[run][0][1];in.z=samples[run][0][2];
  const auto first=n.Update(g,nullptr,0,in);
  check(n.SourceSlot(34)==8&&first.hop==12&&first.flags==42&&first.up==1,
    "008 exact first transition inherits Override42 and requests normal jump toward12");
  in.anchor=8;in.now=.70;in.x=samples[run][1][0];in.y=samples[run][1][1];in.z=samples[run][1][2];
  const auto prior=n.Update(g,nullptr,0,in);
  check(n.SourceSlot(34)==8&&prior.hop==12,"008 action immediately before observed reachedHop remains8-to12");
  in.now=.75;in.x=samples[run][2][0];in.y=samples[run][2][1];in.z=samples[run][2][2];
  const auto arrival=n.Update(g,nullptr,0,in);
  check(n.SourceSlot(34)==12&&arrival.hop==34&&arrival.forward<0,
    "008 observed airborne reachedHop switches to34 and reverses requested forward direction");
  check(in.x*in.x+in.y*in.y+in.z*in.z>16&&in.x*in.x+(in.y-2)*(in.y-2)+in.z*in.z<16,
    "008 both airborne arrivals require shifted sphere; neither is within original centered radius");
 }
}
void approachElevenDiagnostics(){
 for(int mode=0;mode<2;++mode){
  bouncer009Fixture();bot_bDiagnostics=mode;supplyDiagText.clear();supplyDiagLines=0;
  auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();s.navigator.Reset();s.approach=SCecilApproachDiagnostic();
  g.points[10].x=g.points[11].x;g.points[10].y=g.points[11].y;g.points[10].z=40;g.points[10].links={11};
  botcore::CecilMotionInput in;in.alive=true;in.anchor=10;in.goal=34;in.x=g.points[10].x;in.y=g.points[10].y;in.z=g.points[10].z;
  auto first=s.navigator.Update(g,nullptr,0,in);s.hop=first.hop;
  check(first.hop==11&&s.navigator.SourceSlot(34)==10,"11 diagnostic fixture actually approaches distant11 from10");
  BotCecilApproachCapture(s,0,0,-1,10,false,first);
  in.now=.05;auto far=s.navigator.Update(g,nullptr,0,in);
  BotCecilApproachCapture(s,1,.05,10,11,false,far);
  check(s.approach.start<0,"distant selected hop11 cannot arm11-to12 diagnostic");
  in.now=.1;in.x=g.points[11].x;in.y=g.points[11].y;in.z=g.points[11].z;
  auto move=s.navigator.Update(g,nullptr,0,in);s.hop=move.hop;
  check(move.hop==12&&move.up==1&&s.navigator.SourceSlot(34)==11,"actual arrival11 produces first ordinary UP on11-to12");
  const auto original=move;const auto rng=s.rng;const int rays=rayCount,lookups=worldLookups;
  BotCecilApproachCapture(s,2,.1,10,11,true,move);
  BotCecilBouncerApproach(&player,s,move);
  BotCecilApproachFinal(&player,s,0,2,.1,true,1,false,FLOAT3D(0,float(move.up*11),0),FLOAT3D(),0);
  check(original.up==1&&move.up==0&&move.flags==original.flags&&move.forward==original.forward,
    "011 bound11-to12 suppression is identical with diagnostics on or off");
  check(s.rng==rng&&rayCount==rays&&worldLookups==lookups&&s.goal==34&&s.goalEntity==243&&s.goalDeadline==999,
    "11 diagnostic adds no casts lookups RNG or gameplay goal/deadline writes");
  if(mode)check(s.approach.start==.1&&s.approach.move.up==1&&supplyDiagLines==1&&supplyDiagText.find("prev_source=10 prev_hop=11 reached=1 update=1")!=std::string::npos&&
      supplyDiagText.find("requested=(")!=std::string::npos&&supplyDiagText.find("action=(0.000000,0.000000,0.000000)")!=std::string::npos,
      "011 actual arrival captures raw UP1 and suppressed final UP0 in same bounded episode");
  else check(s.approach.start<0&&supplyDiagLines==0,"11 trigger remains default off");
  // Start an observer at an already committed11-to12 edge, independent of the
  // first-arrival trigger. Navigator and gameplay state remain untouched.
  s.approach=SCecilApproachDiagnostic();supplyDiagLines=0;
  in.now=.15;in.z=g.points[11].z+.2;auto ongoing=s.navigator.Update(g,nullptr,0,in);
  BotCecilApproachCapture(s,3,.15,11,12,false,ongoing);
  check(mode?s.approach.start==.15:s.approach.start<0,"11 committed ongoing edge can arm only when diagnostics enabled");
  for(int i=3;i<150;++i)BotCecilApproachFinal(&player,s,0,i,.15+(i-3)*.01,true,1,false,FLOAT3D(),FLOAT3D(),0);
  check(supplyDiagLines==(mode?120:0),"11 diagnostic keeps existing120-row cap");
  s.approach=SCecilApproachDiagnostic();supplyDiagLines=0;
  BotCecilApproachCapture(s,3,.15,11,12,false,ongoing);
  BotCecilApproachFinal(&player,s,0,130,6.15,true,1,false,FLOAT3D(),FLOAT3D(),0);
  check(supplyDiagLines==0,"11 diagnostic keeps existing exclusive6-second cap");
  s.Reset();check(s.approach.start<0&&s.approach.rows==0,"11 life/map reset clears diagnostic bounds");
 }
 for(int bad=0;bad<7;++bad){
  bouncer009Fixture();bot_bDiagnostics=true;auto& s=BotSupplyState(0);s.navigator.Reset();
  auto& g=BotSupplyGraph();botcore::CecilMotionInput in;in.alive=true;in.anchor=11;in.goal=34;
  in.x=g.points[11].x;in.y=g.points[11].y;in.z=g.points[11].z;
  auto move=s.navigator.Update(g,nullptr,0,in);s.hop=move.hop;
  if(bad==0)move.hop=11;
  if(bad==1)move.active=false;
  if(bad==2)move.arrived=true;
  if(bad==3)move.relocated=true;
  if(bad==4)move.stuck=true;
  if(bad==5)s.navigator.Reset();
  if(bad==6)g.points[12].radius=3;
  BotCecilApproachCapture(s,1,.05,10,11,true,move);
  check(s.approach.start<0,"11 unrelated inactive relocated stale or invalid geometry cannot arm new trigger");
 }
 bot_bDiagnostics=false;
}

void approachDiagnostics(){
 for(int mode=0;mode<2;++mode){
  setup(35);bot_bDiagnostics=mode;supplyDiagText.clear();supplyDiagLines=0;
  auto& s=BotSupplyState(0);auto& node=BotSupplyGraph().points[12];
  node.x=-51;node.y=24.5;node.z=63;node.radius=4;node.flags=42;
  s.goal=34;s.goalEntity=243;s.goalDeadline=99;s.entity=player.en_ulID;s.playable=true;
  botcore::CecilMotion move;move.active=true;move.hop=12;move.flags=42;move.forward=1;move.up=1;
  const auto rng=s.rng;const int rays=rayCount,lookups=worldLookups;
  BotCecilApproachCapture(s,100,5,8,12,false,move);
  BotCecilApproachFinal(&player,s,0,100,5,true,1,true,FLOAT3D(1,2,3),FLOAT3D(4,5,6),7);
  if(mode)check(supplyDiagText.find("prev_source=8 prev_hop=12 reached=0 update=1")!=std::string::npos&&
    supplyDiagText.find("requested=(1.000000,0.000000,1.000000)")!=std::string::npos&&supplyDiagText.find("action=(1.000000,2.000000,3.000000)")!=std::string::npos,
    "approach telemetry keeps original Update and composed action separate");
  else check(supplyDiagLines==0&&s.approach.start<0,"disabled approach diagnostics do not arm or log");
  BotCecilApproachFinal(&player,s,0,101,5.05,false,0,true,FLOAT3D(),FLOAT3D(),0);
  if(mode)check(supplyDiagText.find("prev_source=-1 prev_hop=-1 reached=0 update=0")!=std::string::npos,
    "combat yield records absent Update without carrying previous planned movement");
  const int beforeDuplicate=supplyDiagLines;
  BotCecilApproachFinal(&player,s,0,101,5.05,false,0,true,FLOAT3D(),FLOAT3D(),0);
  BotCecilApproachFinal(&player,s,0,102,NAN,false,0,true,FLOAT3D(),FLOAT3D(),0);
  BotCecilApproachFinal(&player,s,0,102,4.99,false,0,true,FLOAT3D(),FLOAT3D(),0);
  check(supplyDiagLines==beforeDuplicate,"duplicate backward and nonfinite clock cannot add action evidence");
  for(int i=102;i<250;++i)BotCecilApproachFinal(&player,s,0,i,5+(i-100)*.01,true,1,false,FLOAT3D(),FLOAT3D(),0);
  check(supplyDiagLines==(mode?120:0),"approach episode hard bounds total action rows to120");
  check(s.goal==34&&s.goalEntity==243&&s.goalDeadline==99&&s.rng==rng&&rayCount==rays&&worldLookups==lookups,
    "approach observer changes no goal deadline RNG rays or world lookups");
  s.Reset();check(s.approach.start<0&&s.approach.rows==0,"life/map reset clears diagnostic episode");
 }
 setup(35);bot_bDiagnostics=true;auto& s=BotSupplyState(0);botcore::CecilMotion move;move.hop=12;
 BotCecilApproachCapture(s,1,.05,8,12,false,move);check(s.approach.start<0,"unrelated map geometry cannot arm node-specific observer");
 auto& p=BotSupplyGraph().points[12];p.x=-51;p.y=24.5;p.z=63;p.radius=4;p.flags=42;
 BotCecilApproachCapture(s,1,.05,1,2,false,move);check(s.approach.start<0,"unrelated edge cannot arm observer");
 BotCecilApproachCapture(s,2,.1,7,8,true,move);
 check(s.approach.start==.1&&s.approach.previousHop==8,"arrival at8 captures first newly requested jump toward12 in same action");
 supplyDiagLines=0;BotCecilApproachFinal(&player,s,0,3,6.1,true,1,false,FLOAT3D(),FLOAT3D(),0);
 check(supplyDiagLines==0,"six second episode boundary is exclusive");
 BotCecilApproachCapture(s,200,10,8,12,false,move);check(s.approach.start==.1,"expired episode never re-arms within life");
 bot_bDiagnostics=false;
}
void approachDeathRespawnDiagnostics(){
 setup(35);bot_bDiagnostics=true;supplyDiagText.clear();supplyDiagLines=0;
 auto& s=BotSupplyState(0);auto& p=BotSupplyGraph().points[12];
 p.x=-51;p.y=24.5;p.z=63;p.radius=4;p.flags=42;
 s.playable=true;s.entity=player.en_ulID;const auto entity=player.en_ulID,generation=s.generation;
 botcore::CecilMotion move;move.hop=12;
 BotCecilApproachCapture(s,10,.5,8,12,false,move);
 BotCecilApproachFinal(&player,s,0,10,.5,true,1,false,FLOAT3D(),FLOAT3D(),0);
 check(s.approach.rows==1,"lifecycle fixture starts a genuine live approach episode");
 player.health=0;BotSupplyTick(&player,0,11,1000);
 check(!s.playable&&s.approach.start<0&&s.approach.rows==0,"actual death Tick discards previous life diagnostic episode");
 const int lines=supplyDiagLines;
 BotCecilApproachFinal(&player,s,0,11,.55,false,0,false,FLOAT3D(),FLOAT3D(),0);
 check(supplyDiagLines==lines,"death action cannot emit the old approach episode");
 // A diagnostic remnant must also be cleared by the real !playable spawn path,
 // independently of whether a dead Tick was observed by this observer.
 s.approach.start=.5;s.approach.rows=120;
 player.health=100;_botRayBudget=40;BotSupplyTick(&player,0,12,1000);
 check(player.en_ulID==entity&&s.generation==generation+1&&s.playable&&s.approach.start<0&&s.approach.rows==0,
   "same entity respawn increments generation and discards exhausted diagnostic state without Reset");
 BotCecilApproachCapture(s,13,.65,8,12,false,move);
 BotCecilApproachFinal(&player,s,0,13,.65,true,1,false,FLOAT3D(),FLOAT3D(),0);
 check(s.approach.start==.65&&s.approach.rows==1,"next life on same entity can arm a fresh bounded episode");
 bot_bDiagnostics=false;
}
void supplyDiagnosticsParity(){
 SCecilMove outputs[2];int goals[2],rays[2],lookups[2];unsigned random[2];double deadlines[2];
 for(int mode=0;mode<2;++mode){
  setup(3);bot_bDiagnostics=mode;supplyDiagLines=0;supplyDiagText.clear();player.w.usable=3;
  addItem(991,0,-22,botcore::CecilItemKind::Weapon);BotSupplyGraph().points[2].important_entity=991;
  _botRayBudget=16;worldLookups=0;outputs[mode]=BotSupplyTick(&player,0,1,1000);
  auto& s=BotSupplyState(0);goals[mode]=s.goal;deadlines[mode]=s.goalDeadline;random[mode]=s.rng;
  rays[mode]=rayCount;lookups[mode]=worldLookups;
  check(mode?supplyDiagLines>0:supplyDiagLines==0,"supply telemetry is opt-in and emits selected mapped candidate evidence");
  if(mode)check(supplyDiagText.find("entity=991")!=std::string::npos&&supplyDiagText.find("path_distance=")!=std::string::npos,
    "mapped diagnostic carries actual candidate identity and path score inputs");
 }
 const auto& a=outputs[0];const auto& b=outputs[1];
 check(a.active==b.active&&a.ownsMovement==b.ownsMovement&&a.itemGoal==b.itemGoal&&a.urgent==b.urgent&&
 a.forward==b.forward&&a.strafe==b.strafe&&a.up==b.up&&a.yaw_delta==b.yaw_delta&&a.pitch_delta==b.pitch_delta&&a.buttons==b.buttons&&a.flags==b.flags&&
 goals[0]==goals[1]&&deadlines[0]==deadlines[1]&&random[0]==random[1]&&rays[0]==rays[1]&&lookups[0]==lookups[1],
 "diagnostics change neither command nor goal deadline RNG casts or world lookup count");
 bot_bDiagnostics=false;
}

int flightSafetyResult=0;
SCecilMove flightLossTick(int tick,bool accepted=true){
 _botRayBudget=40;auto m=BotSupplyTick(&player,0,tick,100);double f=m.forward,st=m.strafe,u=m.up;
 flightSafetyResult=BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,m.yaw_delta,1,accepted);
 m.forward=f;m.strafe=st;m.up=u;return m;
}
void flightLossFixture(bool special=true,double deadline=20.4,bool escape=false,bool advance=true){
 setup(3);auto& g=BotSupplyGraph();
 g.points[0].y=.5;g.points[0].z=12;g.points[0].radius=4;
 g.points[0].flags=special?(botcore::CECIL_JUMP|botcore::CECIL_OVERRIDE):0;
 g.points[1].y=38;g.points[1].z=12;
 g.points[2].x=-4.5;g.points[2].y=37.25;g.points[2].z=12;
 auto& item=addItem(267,-4.5,12,botcore::CecilItemKind::Weapon);item.pl.pl_PositionVector(2)=37.25;
 g.points[2].important_entity=267;
 auto& s=BotSupplyState(0);s.goal=2;s.goalEntity=267;s.mappedWeaponGoal=true;
 s.goalSince=0;s.goalDeadline=deadline;s.scanTick=999;s.searchAfter=999;
 player.m_pstState=PST_FALL;player.en_penReference=nullptr;
 player.pl.pl_PositionVector=FLOAT3D(0,.5,12);flightLossTick(98);
 if(!advance){check(s.navigator.SourceSlot(2)==0&&s.hop==1,"launch fixture commits original84 to86 before loss");return;}
 player.pl.pl_PositionVector=FLOAT3D(0,37,12);flightLossTick(99);
 player.pl.pl_PositionVector=FLOAT3D(.049,38.184,12.185);if(escape)wallMode=6;flightLossTick(100);
 if(escape)check(flightSafetyResult==2,"native004 tick100 uses an existing safety-approved alternative");
 wallMode=0;
 check(s.navigator.SourceSlot(2)==1&&s.hop==2,"native004 fixture reaches ordinary successor of jump edge before item loss");
}
void flightLossRegression(){
 flightLossFixture();auto& s=BotSupplyState(0);items[0].pickable=false;player.pl.pl_PositionVector(2)=40.0;
 const auto m=flightLossTick(101);
 check(s.goal==2&&s.navigator.SourceSlot(2)==1&&s.hop==2&&s.goalEntity==0,
  "unavailable item retains only already committed airborne special-route successor");
 check(s.goalSince==0&&near(s.goalDeadline,20.4)&&!m.itemGoal&&endEvents==1,
  "flight finish ends item ownership once without changing original bounded deadline");
 player.pl.pl_PositionVector=FLOAT3D(-4.5,37.25,12);const auto arrived=flightLossTick(102);
 check(s.goal==-1&&arrived.forward==0&&arrived.strafe==0&&arrived.up==0,
  "flight finish ends neutral at original radius without important interaction or new edge");
 flightLossFixture(false);items[0].pickable=false;player.pl.pl_PositionVector(2)=40.0;flightLossTick(101);
 check(BotSupplyState(0).goalEntity==0&&BotSupplyState(0).navigator.SourceSlot(2)==-1,
  "ordinary airborne item disappearance retains original clear-goal behavior");
}

void flightLossGuards(){
 for(bool held:{false,true}){
  flightLossFixture(true,20.4,true);auto& s=BotSupplyState(0);
  int lossTick=101;
  if(held){flightLossTick(101);check(flightSafetyResult==2,"existing accepted escape hold renews only real route provenance");lossTick=102;}
  items[0].pickable=false;player.pl.pl_PositionVector(2)=40;flightLossTick(lossTick);
  check(s.flightFinishing&&s.navigator.SourceSlot(2)==1&&s.hop==2&&near(s.goalDeadline,20.4),
    "actual return2 alternative immediately before loss retains bounded original committed flight");
 }
 for(int guard=0;guard<19;++guard){
  flightLossFixture();auto& s=BotSupplyState(0);items[0].pickable=false;
  player.pl.pl_PositionVector(2)=40;int tick=101;CWorld other;
  if(guard==0)++s.generation;
  if(guard==1)++player.en_ulID;
  if(guard==2)++_botSupplyMapSerial;
  if(guard==3)player.worldOverride=&other;
  if(guard==4)player.en_vGravityDir=FLOAT3D(0,1,0);
  if(guard==5)s.goalSince=1;
  if(guard==6)s.goalDeadline=30;
  if(guard==7)tick=106;
  if(guard==8)tick=99;
  if(guard==9)player.m_pstState=PST_STAND;
  if(guard==10)player.health=0;
  if(guard==11)s.navigator.Reset();
  if(guard==12)s.blocked[2]=1;
  if(guard==13)s.blocked[1]=1;
  if(guard==14){double f=0,st=0,u=0;BotCecilSafeMotion(&player,s,5,f,st,u,0,1,false);}
  if(guard==15)s.ClearGoal();
  if(guard==16)++s.goalEntity;
  if(guard==17)s.goal=1;
  if(guard==18)s.importantGoal=true;
  flightLossTick(tick);
  check(!s.flightFinishing,"map world entity generation gravity attempt deadline stale rewind ground death edge lock ownership reset deny flight continuation");
 }
 for(int denial=0;denial<3;++denial){
  flightLossFixture(true,20.4,true);auto& s=BotSupplyState(0);
  if(denial==0)flightLossTick(101,false);
  else{
    auto m=BotSupplyTick(&player,0,101,100);double f=m.forward,st=m.strafe,u=m.up;
    if(denial==1)wallMode=2;else _botRayBudget=0;
    check(BotCecilSafeMotion(&player,s,5.05,f,st,u,m.yaw_delta,1,true)==0,
      "failed or budget-deferred held escape is not accepted flight evidence");
  }
  items[0].pickable=false;player.pl.pl_PositionVector(2)=40;wallMode=0;flightLossTick(102);
  check(!s.flightFinishing,"lost NAV ownership failed held escape and exhausted cast budget erase flight acceptance");
 }
 // Pending flight has a fixed physical destination and survives no stale identity.
 for(int guard=0;guard<12;++guard){
  flightLossFixture();auto& s=BotSupplyState(0);items[0].pickable=false;
  player.pl.pl_PositionVector(2)=40;flightLossTick(101);
  check(s.flightFinishing,"guard starts a real retained flight after item disappearance");
  int tick=102;CWorld other;
  if(guard==0)++s.generation;
  if(guard==1)++_botSupplyMapSerial;
  if(guard==2)player.worldOverride=&other;
  if(guard==3)++player.en_ulID;
  if(guard==4)player.en_vGravityDir=FLOAT3D(0,1,0);
  if(guard==5)player.m_pstState=PST_STAND;
  if(guard==6)player.health=0;
  if(guard==7)tick=107;
  if(guard==8)tick=100;
  if(guard==9)s.navigator.Reset();
  if(guard==10)BotSupplyGraph().points[2].links.clear(),BotSupplyGraph().points[1].links.clear();
  if(guard==11)BotSupplyGraph().points[2].lock_entity=777; // Fresh existing lock snapshot finds missing lock owner.
  const auto out=flightLossTick(tick);
  check(!s.flightFinishing&&!out.flightGoal&&!bridgeDriverOwns(true,out,&player,true)&&s.goal==-1&&out.forward==0&&out.strafe==0&&out.up==0,
    "pending flight identity grounding stale edge topology and newly refreshed lock abort neutral");
 }
 flightLossFixture();items[0].item.weapon=1;player.pl.pl_PositionVector(2)=40;
 flightLossTick(101);
 check(!BotSupplyState(0).flightFinishing,"live item rejected by typed need does not become a disappeared-item flight");
 flightLossFixture(true,5.1);auto& expiry=BotSupplyState(0);items[0].pickable=false;
 player.pl.pl_PositionVector(2)=40;flightLossTick(101);check(expiry.flightFinishing,"flight may start before original expiry");
 const auto ended=flightLossTick(102);
 check(!expiry.flightFinishing&&expiry.goal==-1&&ended.forward==0&&ended.strafe==0,
  "original item deadline expires pending flight exactly without extension");
 flightLossFixture();auto& s=BotSupplyState(0);items[0].pickable=false;player.pl.pl_PositionVector(2)=40;
 wallMode=2;flightLossTick(101);const auto denied=flightLossTick(102);
 check(!s.flightFinishing&&s.goal==-1&&denied.forward==0&&denied.strafe==0,
  "failed original final motion cannot authorize another pending flight tick");
 flightLossFixture();const int rays=rayCount,lookups=worldLookups;const uint32_t rng=s.rng;
 allocations=0;measuring=true;
 for(int n=0;n<100;++n){BotCecilFlightFresh(&player,s,5.05);BotCecilFlightEdge(s);BotCecilAtNode(&player,2);}
 measuring=false;
 check(rayCount==rays&&worldLookups==lookups&&s.rng==rng&&allocations==0&&near(s.goalDeadline,20.4),
  "flight observations add no casts entity lookups RNG allocations or deadline changes");
}

SCecilMove flightDriverTick(int tick,bool visible,double distance){
 _botRayBudget=40;auto move=BotSupplyTick(&player,0,tick,visible?distance:1000);
 const bool own=bridgeDriverOwns(true,move,&player,visible);
 double f=own?move.forward:-.6,st=own?move.strafe:.2,u=own?move.up:0;
 BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,move.yaw_delta,1,own);
 return move;
}
void flightVisibleOwnership(){
 for(bool launch:{false,true})for(double distance:{6.,15.}){
  flightLossFixture(true,20.4,false,!launch);auto& s=BotSupplyState(0);
  items[0].pickable=false;player.pl.pl_PositionVector=FLOAT3D(0,launch?20:40,12);
  flightDriverTick(101,false,1000);
  check(s.flightFinishing,"item disappearance starts actual bounded flight before visibility change");
  const auto visible=flightDriverTick(102,true,distance);
  check(visible.flightGoal&&bridgeDriverOwns(true,visible,&player,true)&&visible.active&&!visible.itemGoal&&!visible.urgent&&
        near(s.flightAccepted,5.1),"actual Driver preserves orphan flight ownership against newly visible close or distant enemy");
  const auto retained=flightDriverTick(103,true,distance);
  check(s.flightFinishing&&s.goal==2&&s.navigator.SourceSlot(2)==(launch?0:1)&&s.hop==(launch?1:2)&&
        near(s.goalDeadline,20.4)&&retained.active,"next tick preserves exact physical edge and original deadline after visible combat handoff");
  player.pl.pl_PositionVector=launch?FLOAT3D(0,38,12):FLOAT3D(-4.5,37.25,12);
  const auto ended=flightDriverTick(104,true,distance);
  check(!s.flightFinishing&&!bridgeDriverOwns(true,ended,&player,true)&&s.goal==-1,
    "arrival ends dedicated flight priority immediately and yields visible combat");
 }

 int rays[2],lookups[2];unsigned random[2];SCecilMove commands[2];
 for(int visible=0;visible<2;++visible){
  flightLossFixture(true,20.4,false,false);auto& s=BotSupplyState(0);
  items[0].pickable=false;player.pl.pl_PositionVector=FLOAT3D(0,20,12);
  rayCount=worldLookups=0;commands[visible]=flightDriverTick(101,visible!=0,6);
  rays[visible]=rayCount;lookups[visible]=worldLookups;random[visible]=s.rng;
  check(s.flightFinishing&&commands[visible].flightGoal,"visible-at-loss also owns validated original flight");
  SCecilFollowGoal follow;follow.valid=true;follow.entity=999;follow.generation=9;follow.expiresAt=99;follow.x=40;follow.z=30;
  auto& alternative=addItem(991,0,0,botcore::CecilItemKind::Weapon);alternative.pl.pl_PositionVector(2)=20;
  s.scanTick=0;_botRayBudget=40;
  const auto pending=BotSupplyTick(&player,0,102,6,&follow);
  check(pending.flightGoal&&s.goal==2&&s.goalEntity==0&&s.followEntity==0&&near(s.goalDeadline,20.4),
    "pending valid flight defers real fresh item and follow choices despite scheduled scan");
 }
 check(rays[0]==rays[1]&&lookups[0]==lookups[1]&&random[0]==random[1]&&
   near(commands[0].forward,commands[1].forward)&&near(commands[0].strafe,commands[1].strafe)&&
   near(commands[0].up,commands[1].up),"visible flight uses same existing NAV command rays lookups and RNG as unseen flight");
 flightLossFixture(true,5.1);items[0].pickable=false;player.pl.pl_PositionVector(2)=40;
 flightDriverTick(101,true,6);const auto expired=flightDriverTick(102,true,6);
 check(!expired.flightGoal&&!bridgeDriverOwns(true,expired,&player,true)&&BotSupplyState(0).goal==-1,
   "visible enemy never extends original flight deadline");
 setup(3);auto& s=BotSupplyState(0);player.health=60;
 auto& item=addItem(991,0,-20);s.goalEntity=991;s.goal=2;s.scanTick=999;s.searchAfter=999;
 const auto health=BotSupplyTick(&player,0,1,6);
 check(!bridgeDriverOwns(true,health,&player,true)&&s.goalEntity==item.en_ulID,
   "ordinary visible nonurgent health retains bounded target but yields combat");
 flightLossFixture(false);items[0].pickable=false;player.pl.pl_PositionVector(2)=40;
 const auto ordinary=flightDriverTick(101,true,6);
 check(!BotSupplyState(0).flightFinishing&&!bridgeDriverOwns(true,ordinary,&player,true),
   "ordinary FALL loss does not gain dedicated special-flight arbitration");
}
int main(){
 flightVisibleOwnership();flightLossRegression();flightLossGuards();
 boundedSupplySegment(); approachArrivalGeometry();approach008Transitions();bouncer009Transitions();bouncer010Native009Replay();bouncer011Native010Replay();approachElevenDiagnostics();approachDiagnostics();approachDeathRespawnDiagnostics();supplyConnectorDiagnostics(); supplyDiagnosticsParity();supplyDiagnosticsBoundsAndReasons();supplyDiagnosticsRetentionAndTerminal();
 itemTransit49();itemTransit49Guards();
 liquidProjection48();
 importantTransit48();importantPatrol48();
 nativeContactRecovery();farHintTests();farHintGuards();
 hopCheckpoint45();hopCheckpoint45Freshness();hopCheckpoint46Flicker();hopCheckpoint46Authority();hopCheckpoint46Resets();hopCheckpoint46ProgressAndProtection();patrolAlternate46Red();patrolAlternate46Gain();patrolAlternate46Safety();patrolAlternate46Lifecycle();patrolAlternate46Search();patrolAlternate46ExtraGuards();patrolAlternate46Metadata();patrolAlternate46Exit();hopCheckpoint47Passive();patrolAlternate47Passive();patrolObservation47Freshness();hopCheckpoint45Guards();hopCheckpoint45Deferral();hopCheckpoint45ItemDeadline();hopCheckpoint45Arrival();airRecovery44();airRecovery44Guards();neutralRecovery43();neutralRecovery43Guards();groundSweep42();groundSweep42Guards();offgraphProgressBridge();offgraphProgressGuards();originalDiagonalRecovery();groundObservationFlicker();groundObservationHoldGuards();groundedReplanGuards();
 liftOccupancyBridge();
 { // Reproduce Retail033's mask overwrite, including initialized-mask controls.
 for(bool physical:{false,true})for(ULONG initial:{0u,2048u}){
   setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorPolygon.bpo_ulFlags=274752625u;
   CCastRay ray(&player,FLOAT3D(0,1,0),FLOAT3D(0,-4,0));ray.cr_bPhysical=physical;
   ray.cr_ulPassablePolygons=initial;ray.Cast(player.GetWorld());
   check(ray.cr_ulPassablePolygons==(physical?2064u:1077936128u)&&ray.cr_penHit==nullptr,
     "Retail033 Cast control overwrites initialized masks and misses the observed nonpassable shoot-through floor");
 }
 setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorPolygon.bpo_ulFlags=274752625u;
 SCecilProbe probe;_botRayBudget=16;
 check(BotCecilFloor(&player,.3,0,0,0,&probe)&&rayCount==1&&lastMask==2048&&
   lastModels==CCastRay::TT_NONE&&lastPhysical&&!lastOverHit&&_botRayBudget==15,
   "physical floor query hits a nonpassable shoot-through brush with the original PASSABLE mask and unchanged budget/model mode");
 check(legacyCastCalls==0&&sectorAdds==1&&sectorTests==1,
   "physical floor uses original Cecil sector traversal rather than the mask-resetting Cast wrapper");
 setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorPolygon.bpo_ulFlags=BPOF_PASSABLE|BPOF_SHOOTTHRU;
 check(!BotCecilFloor(&player,.3,0,0,0,&probe)&&probe.primaryReason==SCecilProbe::reasonNoFloor,
   "a genuinely passable shoot-through floor remains unsupported under the movement mask");
 setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;
 check(BotCecilFloor(&player,.3,0,0,0)&&lastMask==2048,
   "an ordinary solid floor remains supported under the same physical movement policy");
 nullReferenceFixture();floorPolygon.bpo_ulFlags=BPOF_SHOOTTHRU;_botRayBudget=16;
 const auto supported=BotSupplyTick(&player,0,1,1000);
 check(supported.active&&nearFootRays==1&&nearFootPhysical&&!nearFootOverHit&&legacyCastCalls==0&&
   _botRayBudget==14,"NULL-reference recovery verifies shoot-through current-foot support and keeps the support/LOS budget reserve");
 setup();wallMode=2;wallPolygonFlags=BPOF_SHOOTTHRU;_botRayBudget=16;
 check(!BotSupplyClear(&player,FLOAT3D(),FLOAT3D(0,0,-2))&&rayCount==1&&lastMask==2048&&
   lastModels==CCastRay::TT_COLLISIONBOX&&lastPhysical&&!lastOverHit&&_botRayBudget==15,
   "navigation and item connectors treat a shoot-through physical wall as blocking");
 setup();wallMode=2;wallPolygonFlags=BPOF_SHOOTTHRU;_botRayBudget=16;probe=SCecilProbe();
 check(!BotCecilClearMotion(&player,.3,0,0,0,&probe,false)&&probe.primaryReason==SCecilProbe::reasonWallHit&&
   probe.wallRays==1&&probe.floorRays==0&&lastMask==2048&&lastModels==CCastRay::TT_COLLISIONBOX&&_botRayBudget==15,
   "final wall safety independently rejects a nonpassable shoot-through barrier without adding floor casts");
 setup();wallMode=2;wallPolygonFlags=BPOF_PASSABLE|BPOF_SHOOTTHRU;_botRayBudget=16;
 check(BotCecilClearMotion(&player,.3,0,0,0,nullptr,false)&&lastMask==2048&&rayCount==1,
   "physical wall safety continues through genuinely passable polygons");
 }
 { // Fresh and empty rays have defined results without inventing extra engine casts.
 setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorPolygon.bpo_ulFlags=BPOF_SHOOTTHRU;
 CCastRay world(nullptr,FLOAT3D(0,1,0),FLOAT3D(0,-4,0));world.cr_bPhysical=true;world.cr_bAllowOverHit=false;
 check(physicalCast(world,player.GetWorld(),0)&&world.cr_penHit==&floorEntity&&worldTests==1&&sectorAdds==0&&
   world.cr_ulPassablePolygons==2048&&near(world.cr_vHit(2),0),
   "original null-origin whole-world traversal preserves the physical mask and computes the finite hit position");
 setup();const FLOAT3D origin(1,2,3);CCastRay empty(&player,origin,origin);
 empty.cr_penHit=&obstruction;empty.cr_pbpoBrushPolygon=&floorPolygon;empty.cr_pbscBrushSector=(CBrushSector*)1;
 check(physicalCast(empty,player.GetWorld(),0)&&rayCount==0&&normalizeCalls==0&&empty.cr_penHit==nullptr&&
   empty.cr_pbpoBrushPolygon==nullptr&&empty.cr_pbscBrushSector==nullptr&&empty.cr_fHitDistance==0&&
   empty.cr_vHit(1)==1&&empty.cr_vHit(2)==2&&empty.cr_vHit(3)==3,
   "exactly zero segments clear stale hit metadata and return the origin without query or normalization");
 setup();_botRayBudget=16;
 check(BotSupplyClear(&player,origin,origin)&&rayCount==0&&rayConstructions==0&&_botRayBudget==15,
   "coincident navigation endpoints are clear without constructing or querying a zero-length native ray");
 for(int axis=1;axis<=3;++axis)for(float invalid:{NAN,INFINITY,-INFINITY}){
   setup();FLOAT3D from(0,1,0),to(0,-4,0);from(axis)=invalid;_botRayBudget=16;
   check(!BotSupplyClear(&player,from,to)&&rayCount==0&&rayConstructions==0&&normalizeCalls==0&&_botRayBudget==16,
     "nonfinite navigation endpoints fail closed before native ray construction or budget use");
   setup();player.pl.pl_PositionVector(axis)=invalid;SCecilProbe probe;_botRayBudget=16;
   check(!BotCecilClearMotion(&player,.3,0,0,0,&probe,false)&&probe.primaryReason==SCecilProbe::reasonInvalid&&
     rayCount==0&&rayConstructions==0&&_botRayBudget==16,
     "invalid final wall geometry records Invalid before any cast so recovery cannot mistake it for NoFloor");
 }
 setup();FLOAT3D bad(NAN,0,0);CCastRay invalid(&player,bad,FLOAT3D(0,-4,0));
 check(!physicalCast(invalid,player.GetWorld(),0)&&rayCount==0&&normalizeCalls==0,
   "direct physical helper rejects malformed endpoints without normalizing or querying");
 setup();player.hasWorld=false;_botRayBudget=16;
 check(!BotSupplyClear(&player,origin,origin)&&rayCount==0&&rayConstructions==0&&_botRayBudget==16,
   "empty navigation segment cannot grant clearance for an actor without a world");
 setup();CCastRay orphan(&player,FLOAT3D(0,1,0),FLOAT3D(0,-4,0));
 check(!physicalCast(orphan,nullptr,0)&&rayCount==0&&normalizeCalls==0,
   "direct physical helper fails closed when the world is missing");
 const FLOAT3D froms[]={{0,1,0},{std::numeric_limits<float>::max(),0,0},{1e30f,0,0},{std::numeric_limits<float>::denorm_min(),0,0}};
 const FLOAT3D tos[]={{0,INFINITY,0},{-std::numeric_limits<float>::max(),0,0},{0,0,0},{0,0,0}};
 for(int i=0;i<4;++i){setup();_botRayBudget=16;
   check(!BotSupplyClear(&player,froms[i],tos[i])&&rayCount==0&&rayConstructions==0&&normalizeCalls==0&&_botRayBudget==16,
     "nonfinite target or unrepresentable positive FLOAT segment fails before native construction and Normalize");
 }
 setup();player.pl.pl_PositionVector=FLOAT3D(1e30f,1e30f,1e30f);SCecilProbe collapsed;
 check(!BotCecilClearMotion(&player,.3,0,0,0,&collapsed,false)&&collapsed.primaryReason==SCecilProbe::reasonInvalid&&
   rayCount==0&&rayConstructions==0,"collapsed action geometry is Invalid rather than a false physical NoFloor observation");
 setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;invalidHitDistance=true;SCecilProbe uncertain;
 check(!BotCecilFloor(&player,.3,0,0,0,&uncertain)&&uncertain.primaryReason==SCecilProbe::reasonInvalid&&normalizeCalls==0,
   "malformed native hit distance fails closed without Normalize or a false physical floor approval");
 }
 { // Do not cycle targets while their real requested world direction is still turning.
 recoveryFloorFixture();auto& graph=BotSupplyGraph();graph.points[0].x=-4;graph.points[0].z=-4;
 graph.points[1].x=8;graph.points[1].z=-8;BotSupplyState(0).ClearAvoidance();
 BotCecilSettings().bStrafe=0;floorPattern=4;bool moved=false,keptTarget=true;
 int firstSafeTick=0;
 for(int tick=1;tick<=60;++tick){
   _botRayBudget=16;const auto move=BotSupplyTick(&player,0,tick,1000);auto& state=BotSupplyState(0);
   const double yaw=player.en_plViewpoint.pl_OrientationAngle(1)+move.yaw_delta;
   double f=move.forward,st=move.strafe,up=move.up;
   const int safe=BotCecilSafeMotion(&player,state,tick*.05,f,st,up,yaw,0,true);
   player.en_plViewpoint.pl_OrientationAngle(1)=(FLOAT)yaw;
   keptTarget=keptTarget&&state.reacquireNode==0;
   if(safe&&f!=0){moved=true;firstSafeTick=tick;break;}
 }
 check(moved&&firstSafeTick<=6&&keptTarget,"a strafe-disabled recovery turns toward its physically safe original target instead of cycling between opposite candidates");
 }
 { // Only an aligned, stationary native ground blockade supplies target feedback.
 for(double yaw:{.999,1.001}){
   auto move=recoveryFloorFixture();auto& state=BotSupplyState(0);move.forward=.3;move.strafe=0;move.yaw_delta=yaw;
   check(recoverySafety(move,.05)==0&&(yaw<1?state.reacquireNode==-1:state.reacquireNode==0),
     "floor feedback has a hard one-degree bound on the actual tested world direction");
 }
 for(bool sideways:{false,true}){
   auto move=recoveryFloorFixture();auto& state=BotSupplyState(0);
   move.forward=sideways?0:-.3;move.strafe=sideways?.3:0;move.yaw_delta=0;
   check(recoverySafety(move,.05)==0&&state.reacquireNode==0&&state.reacquireTried[0]==0,
     "matching view yaw cannot authorize floor feedback for backward or lateral motion away from the target");
 }
 const FLOAT3D velocities[]={{.11f,0,0},{0,.11f,0},{0,0,.11f},{.08f,.08f,0},
   {NAN,0,0},{0,NAN,0},{0,0,NAN},{INFINITY,0,0},{0,-INFINITY,0},{0,0,INFINITY}};
 for(const auto& velocity:velocities){
   const auto move=recoveryFloorFixture();auto& state=BotSupplyState(0);player.en_vCurrentTranslationAbsolute=velocity;
   check(recoverySafety(move,.05)==0&&state.reacquireNode==0&&state.reacquireTried[0]==0,
     "moving or nonfinite native velocity cannot reject a recovery target as a stationary ground blockade");
 }
 for(PlayerState ground:{PST_STAND,PST_CROUCH}){
   const auto move=recoveryFloorFixture();auto& state=BotSupplyState(0);player.m_pstState=ground;
   player.en_vCurrentTranslationAbsolute=FLOAT3D(.05f,0,0);
   check(recoverySafety(move,.05)==0&&state.reacquireNode==-1&&(state.reacquireTried[0]&1),
     "stationary stand and crouch retain physical floor feedback with small finite native drift");
 }
 const auto move=recoveryFloorFixture();auto& state=BotSupplyState(0);player.m_pstState=PST_FALL;
 check(recoverySafety(move,.05)==0&&state.reacquireNode==0&&state.reacquireTried[0]==0,
   "falling recovery with a retained reference cannot reject a target as a ground blockade");
 for(bool malformed:{false,true}){
   const auto uncertain=recoveryFloorFixture();auto& target=BotSupplyGraph().points[0];auto& held=BotSupplyState(0);
   target.x=malformed?NAN:0;target.z=0;
   check(recoverySafety(uncertain,.05)==0&&held.reacquireNode==0&&held.reacquireTried[0]==0,
     "nonfinite or zero horizontal target direction cannot authorize floor rejection");
 }
 const auto aligned=recoveryFloorFixture();recoverySafety(aligned,.05);player.pl.pl_PositionVector(1)=1;
 _botRayBudget=16;const auto movedOrigin=BotSupplyTick(&player,0,2,1000);
 check(movedOrigin.active&&BotSupplyState(0).reacquireNode==0&&(BotSupplyState(0).reacquireTried[0]&1)==0,
   "a moved pose invalidates final-floor rejection exactly like prior LOS rejections");
 setup(4096);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,0);player.en_penReference=&floorEntity;
 for(auto& point:BotSupplyGraph().points){point.x=0;point.z=1000;}
 BotSupplyGraph().points[4095].z=-4;_botRayBudget=16;const auto tail=BotSupplyTick(&player,0,1,1000);
 check(tail.active&&BotSupplyState(0).reacquireNode==4095&&recoverySafety(tail,.05)==0&&
   BotSupplyState(0).reacquireTried[511]==128&&BotSupplyState(0).reacquireNode==-1,
   "physical floor feedback safely marks the last original node in the fixed 4096-bit sweep");
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,0,-4.25f);player.en_vGravityDir=FLOAT3D(0,0,-1);
 player.body=FLOATmatrix3D{{{1,0,0},{0,0,-1},{0,1,0}}};player.en_penReference=&floorEntity;
 auto& tilted=BotSupplyGraph();tilted.points[0].x=0;tilted.points[0].y=4;tilted.points[0].z=0;
 tilted.points[1].x=8;tilted.points[1].y=8;tilted.points[1].z=0;_botRayBudget=16;
 const auto gravityRecovery=BotSupplyTick(&player,0,1,1000);
 check(gravityRecovery.active&&BotSupplyState(0).reacquireNode==0&&recoverySafety(gravityRecovery,.05)==0&&
   BotSupplyState(0).reacquireNode==-1&&(BotSupplyState(0).reacquireTried[0]&1),
   "floor feedback compares actual world movement with the target projected along native rotated gravity");
 }
 { // A LOS-clear target is not viable when its original motion and every escape lack floor.
 const auto first=recoveryFloorFixture();auto& state=BotSupplyState(0);
 state.reacquireTried[0]|=0x80;state.goalDeadline=12.05;state.reacquireRejected=99;state.reacquireRetryAfter=9;
 check(first.active&&state.reacquireNode==0,"floor-feedback fixture acquires the closest real original node");
 check(recoverySafety(first,.05)==0&&state.probe.primaryReason==SCecilProbe::reasonNoFloor&&
   state.probe.wallRays==4&&state.probe.floorRays==4,"original recovery and all three exact replacement motions physically fail floor");
 check(state.reacquireNode==-1&&state.reacquireSince==-1&&(state.reacquireTried[0]&0x81)==0x81&&
   state.reacquireRejected==99&&state.reacquireRetryAfter==9&&state.goalDeadline==12.05,
   "final physical floor rejection marks only the selected node in the existing pose sweep without renewing deadlines or backoff");
 const int casts=rayCount;_botRayBudget=16;const auto next=BotSupplyTick(&player,0,2,1000);
 check(next.active&&owns(next,0)&&state.reacquireNode==1&&near(state.reacquireSince,.1)&&rayCount-casts<=3,
   "next recovery tick selects another LOS-clear original direction without a six-second repeat");
 check(recoverySafety(next,.1)==1&&state.reacquireNode==1&&state.anchor<0&&state.hop<0&&
   !state.navigator.HasCommittedEdge(state.goal),"the next direction needs its own real floor approval without a fabricated anchor or edge");
 }
 { // A completely unsafe finite sweep reopens instead of permanently blacklisting the map.
 recoveryFloorFixture();floorMode=0;floorPattern=0;bool bounded=true,complete=false,reopened=false,retried=false;
 allocations=0;measuring=true;
 for(int tick=1;tick<=32;++tick){
   const int casts=rayCount;_botRayBudget=16;const auto move=BotSupplyTick(&player,0,tick,1000);
   bounded=bounded&&rayCount-casts<=3;
   if(complete&&!move.active&&BotSupplyState(0).reacquireTried[0]==0)reopened=true;
   if(reopened&&move.active&&BotSupplyState(0).reacquireNode==0)retried=true;
   if(move.active)bounded=bounded&&recoverySafety(move,tick*.05)==0;
   else check(move.forward==0&&move.strafe==0&&move.up==0,"fully swept recovery remains neutral while reopening its candidate scan");
   complete=complete||(BotSupplyState(0).reacquireTried[0]&3)==3;
 }
 measuring=false;check(bounded&&allocations==0,"floor-feedback sweeps keep the three-LOS cap and perform no per-tick allocation");
 check(complete,"all physically unsafe original candidates are remembered within one pose sweep");
 check(reopened,"a fully failed floor sweep clears for a bounded retry");
 check(retried,"a reopened floor sweep retries the original nearest node and still emits neutral for unsafe geometry");
 }
 { // Uncertainty, another movement owner, and a successful escape are not target failures.
 for(int budget:{0,1,2,3}){
   const auto move=recoveryFloorFixture();auto& state=BotSupplyState(0);const double since=state.reacquireSince;
   check(recoverySafety(move,.05,true,budget)==0&&state.reacquireNode==0&&state.reacquireSince==since&&
     state.reacquireTried[0]==0&&(state.probe.reasonMask&(1u<<SCecilProbe::reasonBudget)),
     "any original or fallback budget denial preserves the selected recovery target and sweep");
 }
 auto move=recoveryFloorFixture();auto* state=&BotSupplyState(0);
 check(recoverySafety(move,.05,false)==0&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "Human-owned physical floor rejection never rejects a planner recovery target");
 move=recoveryFloorFixture();state=&BotSupplyState(0);state->escapeUntil=1;state->escapeWorld[2]=-.3;
 check(recoverySafety(move,.05)==0&&state->probe.floorRays==1&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "held-escape-only floor rejection never claims that the original recovery request was tested");
 move=recoveryFloorFixture();state=&BotSupplyState(0);state->escapeAfter=1;
 check(recoverySafety(move,.05)==0&&state->probe.floorRays==1&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "deferred replacement attempts preserve a target until the existing escape cooldown permits full testing");
 move=recoveryFloorFixture();state=&BotSupplyState(0);wallMode=1;
 check(recoverySafety(move,.05)==0&&state->probe.primaryReason==SCecilProbe::reasonWallHit&&
   state->reacquireNode==0&&state->reacquireTried[0]==0,"an original wall rejection followed by floor failures is not original NoFloor feedback");
 move=recoveryFloorFixture();state=&BotSupplyState(0);floorPattern=0;floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);
 check(recoverySafety(move,.05)==0&&state->probe.primaryReason==SCecilProbe::reasonUnsupportedNormal&&
   state->reacquireNode==0&&state->reacquireTried[0]==0,"unsupported original surface normal preserves the target under the NoFloor-only policy");
 move=recoveryFloorFixture();state=&BotSupplyState(0);floorPattern=0;floorPolygon.bpo_ulFlags=BPOF_PASSABLE;forcePassableHit=true;
 check(recoverySafety(move,.05)==0&&state->probe.primaryReason==SCecilProbe::reasonPassable&&
   state->reacquireNode==0&&state->reacquireTried[0]==0,"passable original surface preserves the target under the NoFloor-only policy");
 move=recoveryFloorFixture();state=&BotSupplyState(0);invalidateAfterFloor=true;
 check(recoverySafety(move,.05)==0&&state->probe.primaryReason==SCecilProbe::reasonNoFloor&&
   (state->probe.reasonMask&(1u<<SCecilProbe::reasonInvalid))&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "invalid geometry during a replacement probe prevents physical target rejection after original NoFloor");
 move=recoveryFloorFixture();state=&BotSupplyState(0);move.forward=NAN;
 check(recoverySafety(move,.05)==0&&state->probe.wallRays==0&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "invalid original action cannot reject an untested recovery target");
 move=recoveryFloorFixture();state=&BotSupplyState(0);player.m_pstState=PST_SWIM;wallMode=2;
 check(recoverySafety(move,.05)==0&&state->probe.floorRays==0&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "liquid wall rejection never enters grounded NoFloor feedback");
 move=recoveryFloorFixture();state=&BotSupplyState(0);floorPattern=1;
 check(recoverySafety(move,.05)==2&&state->probe.primaryReason==SCecilProbe::reasonNoFloor&&
   state->reacquireNode==0&&state->reacquireTried[0]==0,"a physically approved replacement escape preserves the original recovery target");
 move=recoveryFloorFixture();state=&BotSupplyState(0);state->reacquiring=false;
 check(recoverySafety(move,.05)==0&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "a retained target alone never impersonates accepted recovery movement");
 move=recoveryFloorFixture();state=&BotSupplyState(0);state->reacquireNode=999;
 check(recoverySafety(move,.05)==0&&state->reacquireNode==999&&state->reacquireTried[0]==0,
   "out-of-range recovery target is never used as a sweep-mask index");
 move=recoveryFloorFixture();state=&BotSupplyState(0);state->blocked[0]=1;
 check(recoverySafety(move,.05)==0&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "a newly blocked target is left to normal lock invalidation rather than physical floor feedback");
 move=recoveryFloorFixture();state=&BotSupplyState(0);state->blocked.clear();
 check(recoverySafety(move,.05)==0&&state->reacquireNode==0&&state->reacquireTried[0]==0,
   "malformed lock snapshot cannot authorize a recovery feedback index");
 }
 { // A rejected recovery proposal must not impose recovery-only policy on Human movement.
 setup(2);BotCecilSettings().bAvoidPits=0;auto& proposal=BotSupplyState(0);proposal.reacquiring=true;
 proposal.anchor=-1;proposal.reacquireNode=1;proposal.reacquireSince=.25;proposal.reacquireRetryAfter=7;proposal.reacquireTried[0]=3;
 double f=.64,st=0,up=0;_botRayBudget=16;
 check(finalSafety(f,st,up,0,false,0)==1&&near(f,.64)&&st==0&&up==0&&rayCount==1&&proposal.probe.floorRays==0,
   "Human-owned motion keeps its requested speed and wall check when recovery was rejected and pit avoidance is disabled");
 check(proposal.reacquiring&&proposal.reacquireNode==1&&proposal.reacquireSince==.25&&
   proposal.reacquireRetryAfter==7&&proposal.reacquireTried[0]==3,
   "final movement ownership never clears or renews the planner recovery target deadline or failed-LOS sweep");
 setup(2);BotCecilSettings().bAvoidPits=1;BotSupplyState(0).reacquiring=true;f=.64;st=up=0;_botRayBudget=16;
 check(finalSafety(f,st,up,0,false,0)==0&&f==0&&st==0&&BotSupplyState(0).probe.floorRays>0,
   "Human-owned motion still obeys ordinary enabled pit avoidance without a current graph point");
 setup(2);BotCecilSettings().bAvoidPits=0;BotSupplyState(0).reacquiring=true;f=.64;st=up=0;_botRayBudget=16;
 check(finalSafety(f,st,up,0,true,0)==0&&f==0&&st==0&&BotSupplyState(0).probe.floorRays>0,
   "accepted recovery always requires real lookahead floor even when ordinary pit avoidance is disabled");
 setup(2);BotCecilSettings().bAvoidPits=0;BotSupplyState(0).reacquiring=true;floorMode=2;f=.64;st=.4;up=0;_botRayBudget=16;
 check(finalSafety(f,st,up,0,true,0)==1&&std::hypot(f,st)<=.300001,
   "accepted recovery keeps its horizontal norm cap before actual safety probes");
 setup(2);BotCecilSettings().bAvoidPits=0;BotSupplyState(0).reacquiring=true;player.m_pstState=PST_DIVE;
 f=.64;st=0;up=.1;_botRayBudget=16;
 check(finalSafety(f,st,up,0,false,0)==1&&near(f,.64)&&near(up,.1)&&rayCount==1&&BotSupplyState(0).probe.floorRays==0,
   "Human-owned liquid motion does not inherit a rejected recovery cap or any floor requirement");
 }
 { // Reproduce native accumulated FLOAT pitch, including composition and ApplyAction deltas.
 auto composePitch=[](const SCecilMove& motion,FLOAT& local){
   const FLOAT last=player.m_aLastRotation(2);
   const FLOAT requested=last+(FLOAT)motion.pitch_delta;
   const FLOAT axis=requested-local;local+=axis;
   const FLOAT applied=local-last;player.m_aLastRotation(2)=local;
   player.en_plViewpoint.pl_OrientationAngle(2)+=applied;
 };
 for(PlayerState state:{PST_SWIM,PST_DIVE}){
   setup(2);player.m_pstState=state;player.en_plViewpoint.pl_OrientationAngle(2)=-1.4e-6f;
   player.m_aLastRotation(2)=-33.84178161621094f;FLOAT local=player.m_aLastRotation(2);
   auto& s=BotSupplyState(0);s.goal=1;s.anchor=0;s.scanTick=999;s.levelSwimView=true;
   const FLOAT correction=(FLOAT)botcore::TestTurnDelta(player.en_plViewpoint.pl_OrientationAngle(2),0,9);
   check(FLOAT(local+correction)==local,"native tiny-pitch fixture reproduces FLOAT addition loss before the network packet");
   bool progresses=true;
   for(int tick=1;tick<=60;++tick){_botRayBudget=16;const auto motion=BotSupplyTick(&player,0,tick,1000);
     progresses=progresses&&motion.active&&motion.forward>0&&!s.levelSwimView;composePitch(motion,local);}
   check(progresses&&player.en_plViewpoint.pl_OrientationAngle(2)==-1.4e-6f,
     "unencodable native tiny pitch releases the latched swim or dive gate without mutating the view");
   wallMode=2;_botRayBudget=16;double f=1,st=0,u=0;
   check(BotCecilSafeMotion(&player,s,3.05,f,st,u,0,1)==0&&f==0&&st==0&&u==0,
     "tiny pitch release never bypasses the actual native movement wall veto");
   setup(2);player.m_pstState=state;player.en_plViewpoint.pl_OrientationAngle(2)=-1.4e-6f;local=0;
   auto& encoded=BotSupplyState(0);encoded.goal=1;encoded.anchor=0;encoded.scanTick=999;encoded.levelSwimView=true;
   _botRayBudget=16;const auto first=BotSupplyTick(&player,0,1,1000);
   check(first.forward==0&&first.pitch_delta>0&&encoded.levelSwimView,"tiny encodable correction must still level before forward swim motion");
   composePitch(first,local);_botRayBudget=16;const auto second=BotSupplyTick(&player,0,2,1000);
   check(second.forward>0&&!encoded.levelSwimView&&player.en_plViewpoint.pl_OrientationAngle(2)==0,
     "tiny encodable correction resumes movement only after the FLOAT composer reaches zero");
   for(FLOAT pitch:{.01f,-.01f,std::nextafter(.01f,1.f),-std::nextafter(.01f,1.f),1.f,-1.f}){
     setup(2);player.m_pstState=state;player.en_plViewpoint.pl_OrientationAngle(2)=pitch;player.m_aLastRotation(2)=1e8f;
     auto& bounded=BotSupplyState(0);bounded.goal=1;bounded.anchor=0;bounded.scanTick=999;bounded.levelSwimView=true;
     _botRayBudget=16;const auto motion=BotSupplyTick(&player,0,1,1000);
     check(std::fabs(double(pitch))<=.01?motion.forward>0&&!bounded.levelSwimView:motion.forward==0&&bounded.levelSwimView,
       "unencodable correction releases only inside the hard tiny-pitch bound even with huge accumulated angles");
   }
   setup(2);player.m_pstState=state;player.en_plViewpoint.pl_OrientationAngle(2)=state==PST_DIVE?90.f:-45.f;
   player.m_aLastRotation(2)=17.25f;local=17.25f;
   auto& full=BotSupplyState(0);full.goal=1;full.anchor=0;full.scanTick=999;full.levelSwimView=true;SCecilMove settled;
   for(int tick=1;tick<=11;++tick){_botRayBudget=16;settled=BotSupplyTick(&player,0,tick,1000);composePitch(settled,local);}
   check(settled.forward>0&&!full.levelSwimView&&player.en_plViewpoint.pl_OrientationAngle(2)==0,
     "large initial pitch still completes genuine leveling through the native FLOAT composer at a normal offset");
 }
 for(FLOAT bad:{std::numeric_limits<FLOAT>::quiet_NaN(),std::numeric_limits<FLOAT>::infinity(),-std::numeric_limits<FLOAT>::infinity()}){
   setup(2);player.m_pstState=PST_DIVE;player.m_aLastRotation(2)=bad;player.en_plViewpoint.pl_OrientationAngle(2)=-1.4e-6f;
   auto& s=BotSupplyState(0);s.goal=1;s.anchor=0;s.scanTick=999;s.levelSwimView=true;
   _botRayBudget=16;const auto motion=BotSupplyTick(&player,0,1,1000);
   check(!motion.active&&motion.forward==0&&motion.strafe==0&&motion.up==0&&motion.pitch_delta==0,
     "nonfinite accumulated native pitch fails closed before resolution-based swim release");
 }
 }
 { // The helper also rejects malformed clocks independently of its normal Tick caller.
 const double nan=std::numeric_limits<double>::quiet_NaN(),inf=std::numeric_limits<double>::infinity();
 const double clocks[][2]={{nan,0},{inf,0},{-inf,0},{-.1,0},{.1,nan},{.1,inf},{.1,-inf},{.1,-.1},{-.1,-1}};
 for(const auto& clock:clocks){
   relocationFixture();auto& s=BotSupplyState(0);s.anchor=2;s.goalSince=clock[1];s.goalDeadline=12;
   player.pl.pl_PositionVector=FLOAT3D(40,0,0);const auto input=BotCecilItemInput(&player,s,1000);
   botcore::CecilMotion event;event.active=event.relocated=true;const int before=rayCount;_botRayBudget=16;
   BotCecilRebudgetWeapon(&player,s,event,input,0,2,clock[0]);
   check(s.goal==5&&s.goalEntity==991&&s.goalDeadline==12&&!s.goalRelocationBudgeted&&rayCount==before&&_botRayBudget==16,
     "nonfinite or negative helper timestamps preserve the old weapon attempt without a grant or cast");
 }
 relocationFixture();auto& zero=BotSupplyState(0);zero.anchor=2;zero.goalSince=0;zero.goalDeadline=12;
 for(auto& point:BotSupplyGraph().points)point.x=point.y=point.z=0;
 items[0].pl.pl_PositionVector=player.pl.pl_PositionVector=FLOAT3D();
 const auto input=BotCecilItemInput(&player,zero,1000);botcore::CecilMotion event;event.active=event.relocated=true;
 const int before=rayCount;_botRayBudget=16;BotCecilRebudgetWeapon(&player,zero,event,input,0,200,10);
 check(zero.goalEntity==991&&zero.goalDeadline==12&&!zero.goalRelocationBudgeted&&rayCount==before,
   "zero remaining physical cost cannot earn a relocation extension from elapsed time alone");
 }
 { // Only a reached original-node relocation can increase a live ordinary weapon deadline.
 relocationFixture();relocateTo(2,2);const double deadline=BotSupplyState(0).goalDeadline;
 check(near(deadline,.1+(60+std::sqrt(3200.0))/6+5),"ordinary weapon relocation grants one fixed deadline from fresh directed remaining cost");
 BotSupplyState(0).scanTick=0;_botRayBudget=16;BotSupplyTick(&player,0,21,1000);
 check(BotSupplyState(0).goalDeadline==deadline,"ordinary acquisition scans cannot renew relocation budget");
 BotSupplyState(0).anchor=6;BotSupplyState(0).scanTick=999;_botRayBudget=16;BotSupplyTick(&player,0,22,1000);
 check(BotSupplyState(0).goalDeadline==deadline,"unreached anchor hint cannot extend an item deadline");
 relocateTo(6,23);
 check(BotSupplyState(0).goalDeadline==deadline,"second genuine relocation cannot extend the same weapon attempt again");
 _botRayBudget=16;BotSupplyTick(&player,0,250,1000);
 check(BotSupplyState(0).goalEntity==991,"valid once-rebudgeted weapon attempt survives its original twelve-second deadline");
 relocationFixture(true);relocateTo(2,2);
 check(near(BotSupplyState(0).goalDeadline,45),"long relocation route is capped at forty-five seconds since original admission");
 relocationFixture();relocateTo(2,240);
 check(BotSupplyState(0).goalEntity!=991,"already timed-out weapon attempt cannot revive on a relocation tick");
 relocationFixture();player.w.usable|=botcore::CecilWeaponMask(4);player.w.m_iAvailableWeapons=player.w.usable;relocateTo(2,2);
 check(BotSupplyState(0).goalEntity!=991,"gained goal weapon cancels before any relocation budget grant");
 relocationFixture();items[0].pickable=false;relocateTo(2,2);
 check(BotSupplyState(0).goalEntity!=991,"unavailable goal item cancels before any relocation budget grant");
 relocationFixture();BotSupplyState(0).mappedWeaponGoal=true;BotSupplyState(0).goalDeadline=20;relocateTo(2,2);
 check(BotSupplyState(0).goalDeadline==20,"mapped weapon deadline is untouched by ordinary relocation budgeting");
 relocationFixture();relocateTo(2,2);BotSupplyState(0).ClearGoal();
 auto& reset=BotSupplyState(0);reset.goal=5;reset.goalEntity=991;reset.goalSince=10;reset.anchor=0;reset.scanTick=999;
 player.pl.pl_PositionVector=FLOAT3D();_botRayBudget=16;BotSupplyTick(&player,0,201,1000);relocateTo(2,202);
 check(near(reset.goalDeadline,10.1+(60+std::sqrt(3200.0))/6+5),"clearing the item goal gives the next attempt its own single relocation budget");
 relocationFixture();relocateTo(2,2,2);
 check(BotSupplyState(0).goalDeadline==0&&_botRayBudget==2,"connector budget denial skips this relocation event without spending reserved rays");
 _botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(BotSupplyState(0).goalDeadline==0,"fresh budget on a later scan cannot fabricate the missed relocation event");
 relocateTo(6,4);
 check(BotSupplyState(0).goalDeadline>12,"a later genuine relocation can grant the still-unused extension after budget denial");
 relocationFixture();blockedItems=1;items[0].pl.pl_PositionVector(1)=1;const int before=rayCount;relocateTo(2,2);
 check(BotSupplyState(0).goalDeadline==0&&rayCount-before==1,"blocked live item connector prevents relocation budgeting with one bounded physical cast");
 relocationFixture();items[0].pl.pl_PositionVector(2)=4;relocateTo(2,2);
 check(BotSupplyState(0).goalDeadline==0,"wrong-floor live item connector prevents relocation budgeting");
 relocationFixture();BotSupplyGraph().points[2].links={5};BotSupplyGraph().points[2].x=10;relocateTo(2,2);
 check(BotSupplyState(0).goalDeadline==0,"short relocation route does not consume an extension when twelve seconds are sufficient");
 relocateTo(6,3);
 check(BotSupplyState(0).goalDeadline>12,"later costly relocation can use the option not consumed by a short route");
 relocationFixture();items[0].item.kind=botcore::CecilItemKind::Health;player.health=20;relocateTo(2,2);
 check(BotSupplyState(0).goalEntity==991&&BotSupplyState(0).goalDeadline==0,"ordinary nonweapon attempts keep their twelve-second lifetime after relocation");
 relocationFixture();BotSupplyGraph().points[2].links.clear();relocateTo(2,2);
 check(BotSupplyState(0).goalDeadline==0,"unreachable directed suffix cannot grant relocation budget");
 relocationFixture();CEntity lock;lock.en_ulID=1199;lock.pl.pl_PositionVector(1)=1;
 player.world.wo_cenEntities.push_back(&lock);BotSupplyGraph().points[2].lock_entity=1199;relocateTo(2,2);
 check(BotSupplyState(0).goalDeadline==0,"reached but physically locked relocation source cannot grant extra item lifetime");
 // Keep this a real nonzero connector; the empty-segment no-query case is tested separately.
 relocationFixture();items[0].pl.pl_PositionVector(1)=.5f;const int castsBefore=rayCount;relocateTo(2,2,3);
 check(BotSupplyState(0).goalDeadline>12&&rayCount-castsBefore==1&&_botRayBudget==2,
   "relocation connector spends exactly one cast while retaining the final two safety rays");
 _botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(rayCount-castsBefore==1,"ordinary ticks after relocation never repeat the connector budgeting cast");
 relocationFixture();items[0].pl.pl_PositionVector(1)=1;player.pl.pl_PositionVector=FLOAT3D(40.5f,0,0);
 BotSupplyState(0).anchor=2;_botRayBudget=16;BotSupplyTick(&player,0,2,1000);
 check(near(BotSupplyState(0).goalDeadline,.1+(.5+60+std::sqrt(3200.0)+1)/6+5),
   "relocation budget includes current approach to the reached node and the live item connector");
 relocationFixture();relocateTo(2,2);items[0].pickable=false;_botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(BotSupplyState(0).goalEntity==0&&BotSupplyState(0).goalDeadline==0,"extended attempt still clears immediately when its live item becomes unavailable");
 relocationFixture();relocateTo(2,2);player.health=0;_botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(BotSupplyState(0).goalEntity==0&&BotSupplyState(0).goalDeadline==0,"death clears the extended attempt and its budget state");
 relocationFixture(true);relocateTo(2,2);relocateTo(6,900);
 check(BotSupplyState(0).goalEntity!=991,"absolute forty-five-second lifetime expires even on another real relocation");
 }
 { // A missing reference can coexist with an actual brush immediately below the feet.
 nullReferenceFixture();BotCecilSettings().bAvoidPits=0;_botRayBudget=4;
 const auto supported=BotSupplyTick(&player,0,1,1000);
 check(supported.active&&owns(supported,0)&&BotSupplyState(0).reacquiring&&
   std::hypot(supported.forward,supported.strafe)<=.300001&&BotSupplyState(0).anchor<0,
   "near-foot physical brush support permits bounded NULL-reference recovery without fabricating an anchor");
 check(nearFootRays==1&&nearFootPhysical&&!nearFootOverHit&&near(nearFootFrom(2),-4)&&
   near(nearFootTo(2),-4.30)&&nearFootFrom(1)==0&&nearFootFrom(3)==2&&_botRayBudget==2,
   "NULL recovery spends one physical thirty-centimetre foot cast and retains two final safety rays");
 double f=supported.forward,st=supported.strafe,u=supported.up;floorMode=2;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),.05,f,st,u,0,1)==1&&_botRayBudget==0,
   "minimum NULL-support budget still permits the final wall and lookahead floor probes");
 const double selectedSince=BotSupplyState(0).reacquireSince;_botRayBudget=3;
 check(!BotSupplyTick(&player,0,2,1000).active&&BotSupplyState(0).reacquireNode==0&&
   BotSupplyState(0).reacquireSince==selectedSince&&nearFootRays==1,
   "deferred current-support check never renews or rejects a selected target deadline");
 nullReferenceFixture();_botRayBudget=16;auto edge=BotSupplyTick(&player,0,1,1000);
 f=edge.forward;st=edge.strafe;u=edge.up;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),.05,f,st,u,0,1)==0&&f==0&&st==0&&u==0,
   "current-foot support never bypasses the final unsupported lookahead-floor veto");
 nullReferenceFixture();player.m_pstState=PST_CROUCH;_botRayBudget=16;
 check(BotSupplyTick(&player,0,1,1000).active,"supported native crouch can use bounded NULL-reference recovery");
 nullReferenceFixture();player.en_vCurrentTranslationAbsolute=FLOAT3D(2,.099f,3);_botRayBudget=16;
 check(BotSupplyTick(&player,0,1,1000).active,"finite lateral motion with small vertical speed can retain actual foot support");
 nullReferenceFixture();auto& sweep=BotSupplyState(0);sweep.reacquireTried[0]=1;sweep.reacquireScanTime=0;
 for(int axis=0;axis<3;++axis){sweep.reacquireScanPosition[axis]=player.pl.pl_PositionVector(axis+1);sweep.reacquireScanGravity[axis]=player.en_vGravityDir(axis+1);}
 _botRayBudget=16;const auto continued=BotSupplyTick(&player,0,1,1000);
 check(continued.active&&sweep.reacquireTried[0]==1&&sweep.reacquireNode==1,
   "positive current support preserves the failed-LOS prefix and continues to the next node");
 nullReferenceFixture();player.pl.pl_PositionVector(2)=4.25f;player.body.m[0][0]=-1;player.body.m[1][1]=-1;
 player.en_vGravityDir=FLOAT3D(0,1,0);floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);_botRayBudget=16;
 check(BotSupplyTick(&player,0,1,1000).active&&near(nearFootFrom(2),4)&&near(nearFootTo(2),4.30),
   "near-foot support ray and upward normal follow actual inverted gravity");
 for(float distance:{.25f,.30f}){nullReferenceFixture();nearFootDistance=distance;_botRayBudget=16;
  check(BotSupplyTick(&player,0,1,1000).active,"near-foot support includes both native distance boundaries");}
 for(int budget:{0,1,2,3}){nullReferenceFixture();auto& state=BotSupplyState(0);state.reacquireTried[0]=1;state.reacquireScanTime=0;
  _botRayBudget=budget;const auto deferred=BotSupplyTick(&player,0,1,1000);
  check(!deferred.active&&owns(deferred,0)&&rayCount==0&&state.reacquireTried[0]==1,
    "insufficient support-plus-LOS-plus-safety budget defers without clearing failed-LOS evidence");}
 nullReferenceFixture();nearFootMode=0;auto& denied=BotSupplyState(0);denied.reacquireTried[0]=1;denied.reacquireScanTime=0;
 _botRayBudget=16;check(!BotSupplyTick(&player,0,1,1000).active&&denied.reacquireTried[0]==0,
   "actual missing current-foot support rejects recovery and resets its LOS sweep");
 for(PlayerState state:{PST_FALL}){nullReferenceFixture();player.m_pstState=state;_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"native falling state cannot use the NULL support fallback");}
 nullReferenceFixture();player.physicsFlags=0;_botRayBudget=16;
 check(!BotSupplyTick(&player,0,1,1000).active,"gravity-disabled entity cannot use the NULL support fallback");
 for(float speed:{-.1001f,.1001f,-20.f,20.f}){nullReferenceFixture();player.en_vCurrentTranslationAbsolute(2)=speed;_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"ascending or descending native velocity rejects NULL support fallback");}
 for(float bad:{std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()}){
  for(int axis=1;axis<=3;++axis){nullReferenceFixture();player.en_vCurrentTranslationAbsolute(axis)=bad;_botRayBudget=16;
   check(!BotSupplyTick(&player,0,1,1000).active,"nonfinite native velocity rejects NULL support fallback");}
  nullReferenceFixture();nearFootDistance=bad;_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"nonfinite physical hit distance rejects NULL support fallback");
  nullReferenceFixture();floorPlane.bpl_plAbsolute(1)=bad;_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"nonfinite native support normal rejects NULL support fallback");
 }
 for(float distance:{-.1f,.2499f,.3001f,1.f}){nullReferenceFixture();nearFootDistance=distance;_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"support above the feet or beyond five centimetres below is rejected");}
 for(int type:{CEntity::RT_MODEL,CEntity::RT_TERRAIN}){nullReferenceFixture();floorEntity.type=type;_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"model or terrain hits cannot substitute for native brush support");}
 nullReferenceFixture();nearFootMode=1;_botRayBudget=16;
 check(!BotSupplyTick(&player,0,1,1000).active,"a physical hit without a brush polygon is insufficient");
 nullReferenceFixture();floorPolygon.bpo_pbplPlane=nullptr;_botRayBudget=16;
 check(!BotSupplyTick(&player,0,1,1000).active,"a brush hit without its actual plane is insufficient");
 nullReferenceFixture();floorPolygon.bpo_ulFlags=BPOF_PASSABLE;_botRayBudget=16;
 check(!BotSupplyTick(&player,0,1,1000).active,"passable brush polygon cannot authorize recovery");
 for(float normal:{-1.f,0.f,.5f}){nullReferenceFixture();floorPlane.bpl_plAbsolute=FLOAT3D(0,normal,0);_botRayBudget=16;
  check(!BotSupplyTick(&player,0,1,1000).active,"wrong or insufficient upward normal rejects NULL support fallback");}
 nullReferenceFixture();floorEntity.flags=ENF_DELETED;_botRayBudget=16;
 check(!BotSupplyTick(&player,0,1,1000).active,"deleted brush hit cannot authorize recovery");
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 player.physicsFlags=0;player.en_vCurrentTranslationAbsolute(2)=20;_botRayBudget=16;
 check(BotSupplyTick(&player,0,1,1000).active&&nearFootRays==0,
   "existing non-NULL reference path remains unchanged by fallback restrictions");
 }
 { // A committed item attempt may briefly leave its acquisition radius on a route.
 setup(3);auto& flamer=addItem(991,0,-10,botcore::CecilItemKind::Weapon);flamer.item.weapon=11;
 player.w.m_iAvailableWeapons=259;player.w.usable=259;player.pl.pl_PositionVector(2)=6;
 auto& retained=BotSupplyState(0);retained.owned=259;retained.goal=1;retained.goalEntity=991;retained.goalSince=0;retained.scanTick=999;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(retained.goalEntity==991&&retained.goalSince==0&&endEvents==0,"ordinary retained flamer upgrade survives weighted acquisition-range crossing after grenade pickup");
 _botRayBudget=16;auto closeThreat=BotSupplyTick(&player,0,2,4);
 check(retained.goalEntity==991&&retained.goalSince==0&&!closeThreat.active&&!owns(closeThreat,0),"retained weapon attempt yields action ownership to close visible combat without renewing or dropping goal");
 player.w.m_iAvailableWeapons|=botcore::CecilWeaponMask(11);player.w.usable=player.w.m_iAvailableWeapons;
 _botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(retained.goalEntity!=991,"retained upgrade ends as soon as its native weapon becomes usable");
 }
 { // A ballistic edge can legitimately have no nearby same-floor acquisition node.
 setup(3);player.w.usable=3;
 BotSupplyGraph().points[1].y=38;BotSupplyGraph().points[2].y=38;
 auto& weapon=addItem(990,0,-22,botcore::CecilItemKind::Weapon);weapon.pl.pl_PositionVector(2)=38;
 BotSupplyGraph().points[2].important_entity=990;
 _botRayBudget=16;auto takeoff=BotSupplyTick(&player,0,1,1000);
 check(takeoff.active&&BotSupplyState(0).hop==1,"ballistic fixture commits directed ground to upper edge");
 player.pl.pl_PositionVector=FLOAT3D(0,31,-9);_botRayBudget=16;
 auto flying=BotSupplyTick(&player,0,21,1000);
 check(flying.active&&BotSupplyState(0).anchor==0&&BotSupplyState(0).hop==1,"airborne anchor gap retains existing edge and navigation heading ownership");
 setup(3);player.pl.pl_PositionVector(2)=31;_botRayBudget=16;
 auto noEdge=BotSupplyTick(&player,0,1,1000);
 check(!noEdge.active&&owns(noEdge,0)&&noEdge.forward==0&&noEdge.strafe==0&&noEdge.yaw_delta==0,"unanchored bot without commitment owns neutral movement rather than Human wandering");
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 BotCecilSettings().bAvoidPits=0;BotSupplyState(0).escapeUntil=9;BotSupplyState(0).escapeWorld[0]=1;_botRayBudget=16;
 auto recover=BotSupplyTick(&player,0,1,1000);
 check(recover.active&&owns(recover,0)&&recover.forward>0&&recover.forward<=.3&&BotSupplyState(0).anchor<0,"grounded offgraph bot uses bounded reacquisition without fabricating an anchor");
 check(BotSupplyState(0).escapeUntil==0,"entering a new reacquisition target clears stale normal-speed escape");
 double rf=recover.forward,rs=recover.strafe,ru=recover.up;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),.05,rf,rs,ru,0,1)==0&&rf==0&&rs==0,"offgraph recovery requires actual floor support even with original pit setting disabled");
 _botRayBudget=16;floorMode=2;recover=BotSupplyTick(&player,0,2,1000);rf=recover.forward;rs=recover.strafe;ru=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),.1,rf,rs,ru,0,1)==1&&rf>0,"supported clear reacquisition action proceeds through ordinary safe motion");
 BotSupplyState(0).escapeUntil=1;BotSupplyState(0).escapeWorld[2]=-.8;BotSupplyState(0).escapeWorld[0]=.4;
 _botRayBudget=16;rf=1;rs=ru=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),.2,rf,rs,ru,0,1)==2&&std::hypot(rf,rs)<=.300001,"held escape is capped before its exact offgraph floor and wall probes");
 const int acquiredNode=BotSupplyState(0).reacquireNode;const double acquiredSince=BotSupplyState(0).reacquireSince;
 _botRayBudget=16;BotSupplyTick(&player,0,21,1000);
 check(BotSupplyState(0).reacquireNode==acquiredNode&&BotSupplyState(0).reacquireSince==acquiredSince,"repeated acquisition scans preserve a fixed attempt deadline");
 _botRayBudget=16;BotSupplyTick(&player,0,141,1000);
 check(BotSupplyState(0).reacquireRejected==acquiredNode&&BotSupplyState(0).reacquireRetryAfter>7&&BotSupplyState(0).reacquireNode!=acquiredNode,"unsuccessful acquisition target expires into bounded backoff and another candidate");
 setup(2);player.m_pstState=PST_DIVE;player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,0);
 BotSupplyGraph().points[0].z=20;BotSupplyGraph().points[1].z=30;_botRayBudget=16;
 auto waterRecovery=BotSupplyTick(&player,0,1,1000);
 check(waterRecovery.active&&waterRecovery.up>0&&std::fabs(waterRecovery.forward)<=.3&&BotSupplyState(0).anchor<0,"water gap reacquires nearby three dimensional route with bounded native swim input");
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;_botRayBudget=2;
 auto deferred=BotSupplyTick(&player,0,1,1000);
 check(!deferred.active&&owns(deferred,0)&&deferred.forward==0,"reacquisition ray exhaustion stays owned neutral until next sample");
 }
 { // Failed nearest LOS candidates must not hide a clear fourth original node forever.
 setup(4);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<4;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 blockedItems=3;_botRayBudget=16;
 const auto firstBlocked=BotSupplyTick(&player,0,1,1000);const int firstCasts=rayCount;
 check(!firstBlocked.active&&owns(firstBlocked,0),"three physically blocked nearest recovery candidates initially stay owned neutral");
 _botRayBudget=16;const auto fourthClear=BotSupplyTick(&player,0,2,1000);
 check(firstCasts<=3&&rayCount-firstCasts<=3&&_botRayBudget>=13,"recovery candidate continuation keeps each tick within three LOS casts and the shared ray reserve");
 check(fourthClear.active&&owns(fourthClear,0)&&BotSupplyState(0).reacquireNode==3&&
   std::hypot(fourthClear.forward,fourthClear.strafe)<=.300001,
   "bounded recovery eventually reaches the clear fourth original node after three nearer LOS failures");
 check(BotSupplyState(0).anchor<0&&!BotSupplyState(0).navigator.HasCommittedEdge(BotSupplyState(0).goal),
   "recovery candidate continuation never fabricates an ordinary anchor or committed graph edge");
 const double selectedSince=BotSupplyState(0).reacquireSince;
 _botRayBudget=16;BotSupplyTick(&player,0,21,1000);
 check(BotSupplyState(0).reacquireNode==3&&BotSupplyState(0).reacquireSince==selectedSince,
   "LOS continuation preserves the selected target and its original attempt deadline");
 blockedItems=0;_botRayBudget=16;BotSupplyTick(&player,0,124,1000);
 check(BotSupplyState(0).reacquireNode==0&&BotSupplyState(0).reacquireRejected==3&&BotSupplyState(0).reacquireRetryAfter>12,
   "selected target timeout retains real backoff while another visible original node acquires a new deadline");
 }
 { // A failed LOS sweep is finite; budget denial is not a physical rejection.
 setup(4);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<4;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 blockedItems=4;
 for(int tick=1;tick<=2;++tick){_botRayBudget=16;BotSupplyTick(&player,0,tick,1000);}
 blockedItems=0;SCecilMove reopened;
 for(int tick=3;tick<=4;++tick){_botRayBudget=16;reopened=BotSupplyTick(&player,0,tick,1000);}
 check(reopened.active&&BotSupplyState(0).reacquireNode==0,"completed failed LOS sweep retries a newly clear nearest original node");
 setup(1);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 BotSupplyGraph().points[0].x=1;_botRayBudget=2;BotSupplyTick(&player,0,1,1000);
 _botRayBudget=16;const auto afterBudget=BotSupplyTick(&player,0,2,1000);
 check(afterBudget.active&&BotSupplyState(0).reacquireNode==0,"budget-deferred recovery candidate remains immediately eligible without rejection backoff");
 }
 { // An active recovery target still needs a fresh physical LOS every tick.
 setup(2);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<2;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);const double firstSince=BotSupplyState(0).reacquireSince;
 _botRayBudget=2;const auto postponed=BotSupplyTick(&player,0,2,1000);
 check(!postponed.active&&owns(postponed,0)&&BotSupplyState(0).reacquireNode==0&&BotSupplyState(0).reacquireSince==firstSince,
   "budget exhaustion neither rejects nor renews an already selected recovery target");
 blockedItems=1;_botRayBudget=16;const auto switched=BotSupplyTick(&player,0,3,1000);
 check(switched.active&&BotSupplyState(0).reacquireNode==1&&near(BotSupplyState(0).reacquireSince,.15),
   "new physical occlusion replaces a selected recovery target with a clear node and a fresh fixed deadline");
 }
 { // Changing the local geometry must discard previous LOS failures.
 setup(4);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<4;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 blockedItems=3;_botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 player.pl.pl_PositionVector(1)=1;blockedItems=0;_botRayBudget=16;
 const auto movedOrigin=BotSupplyTick(&player,0,2,1000);
 check(movedOrigin.active&&BotSupplyState(0).reacquireNode==0,"moving recovery origin invalidates cached LOS failures before selecting a farther candidate");
 setup(4);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<4;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 CEntity lock;lock.en_ulID=992;player.world.wo_cenEntities.push_back(&lock);BotSupplyGraph().points[0].lock_entity=992;
 blockedItems=3;_botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 lock.pl.pl_PositionVector(1)=1;blockedItems=0;_botRayBudget=16;
 const auto changedLock=BotSupplyTick(&player,0,2,1000);
 check(changedLock.active&&BotSupplyState(0).reacquireNode==1,"changed physical lock invalidates stale LOS failures while the newly blocked node stays excluded");
 setup(4);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<4;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 blockedItems=3;_botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 BotSupplyReset(0);blockedItems=0;_botRayBudget=16;
 const auto resetRecovery=BotSupplyTick(&player,0,2,1000);
 check(resetRecovery.active&&BotSupplyState(0).reacquireNode==0,"lifecycle reset discards all prior recovery LOS failures");
 setup(4);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(int i=0;i<4;++i){auto& point=BotSupplyGraph().points[i];point.x=float(i+1);point.y=point.z=0;}
 blockedItems=3;_botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 player.m_pstState=PST_DIVE;blockedItems=0;_botRayBudget=16;
 const auto changedMedium=BotSupplyTick(&player,0,2,1000);
 check(changedMedium.active&&BotSupplyState(0).reacquireNode==0,"switching to water invalidates grounded recovery LOS failures");
 }
 { // The hard graph limit must not turn a long blocked prefix into starvation.
 setup(4096);player.pl.pl_PositionVector=FLOAT3D(0,-4.25f,2);player.en_penReference=&floorEntity;
 for(auto& point:BotSupplyGraph().points){point.x=1;point.y=point.z=0;}
 BotSupplyGraph().points[4095].x=4;blockedItems=3;
 bool bounded=true;SCecilMove tail;allocations=0;measuring=true;
 for(int tick=1;tick<=1366;++tick){const int before=rayCount;_botRayBudget=16;tail=BotSupplyTick(&player,0,tick,1000);
   bounded=bounded&&rayCount-before<=3&&_botRayBudget>=13;}
 measuring=false;
 check(tail.active&&BotSupplyState(0).reacquireNode==4095,"recovery sweep reaches the final original node after a 4095-node blocked prefix");
 check(bounded&&allocations==0,"full-size recovery scan has fixed memory and at most three LOS casts per tick without heap allocation");
 }
 { // Original map knowledge supplies a directed acquisition route beyond local LOS search.
 setup(3);player.w.usable=3;BotSupplyGraph().points[0].links={1,2};
 BotSupplyGraph().points[1].y=70;BotSupplyGraph().points[1].z=-10;BotSupplyGraph().points[1].links.clear();
 BotSupplyGraph().points[2].z=-180;
 auto& high=addItem(988,0,-10,botcore::CecilItemKind::Weapon);high.pl.pl_PositionVector(2)=70;
 addItem(989,0,-180,botcore::CecilItemKind::Weapon);
 BotSupplyGraph().points[1].important_entity=988;BotSupplyGraph().points[2].important_entity=989;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==989,"unarmed acquisition retains Cecil vertical preference over a shorter high-platform route");
 check(near(BotSupplyState(0).goalDeadline,35.05),"mapped deadline uses physical route length rather than vertical ranking penalty");
 setup(3);player.w.usable=3;
 auto& weapon=addItem(991,0,-22,botcore::CecilItemKind::Weapon);
 BotSupplyGraph().points[2].important_entity=991;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==991&&BotSupplyState(0).goal==2,"unarmed bot acquires known reachable mapped weapon beyond ordinary sixteen metre search");
 _botRayBudget=16;BotSupplyTick(&player,0,250,1000);
 check(BotSupplyState(0).goalEntity==991,"mapped route has a fixed bounded lifetime beyond twelve seconds");
 const double deadline=BotSupplyState(0).goalDeadline;
 _botRayBudget=16;BotSupplyTick(&player,0,270,1000);
 check(BotSupplyState(0).goalDeadline==deadline,"repeated scans cannot renew mapped route deadline");
 player.w.usable=3|botcore::CecilWeaponMask(8);player.w.m_iAvailableWeapons=player.w.usable;
 _botRayBudget=16;BotSupplyTick(&player,0,271,1000);
 check(BotSupplyState(0).goalEntity==991&&BotSupplyState(0).goalDeadline==deadline,"incidental different usable gun does not discard a still-needed mapped weapon attempt");
 player.w.usable|=botcore::CecilWeaponMask(4);player.w.m_iAvailableWeapons=player.w.usable;
 _botRayBudget=16;BotSupplyTick(&player,0,272,1000);
 check(BotSupplyState(0).goalEntity==0,"selected mapped weapon becoming usable clears its attempt immediately");
 setup(3);player.w.usable=3|botcore::CecilWeaponMask(4);player.w.m_iAvailableWeapons=player.w.usable;
 addItem(992,0,-22,botcore::CecilItemKind::Weapon).item.weapon=8;BotSupplyGraph().points[2].important_entity=992;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==0,"loaded allowed ranged weapon forbids fallback without a visible enemy");
 setup(3);player.w.usable=3;addItem(993,0,-22,botcore::CecilItemKind::Weapon);
 BotSupplyGraph().points[2].important_entity=993;BotSupplyGraph().points[1].links.clear();
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==0,"mapped fallback never invents a reverse or unreachable arc");
 setup(3);player.w.usable=3;addItem(994,0,-22,botcore::CecilItemKind::Weapon).item.weapon=10;
 BotSupplyGraph().points[2].important_entity=994;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==0,"mapped fallback excludes chainsaw as useful ranged acquisition");
 setup(3);player.w.usable=3;addItem(995,0,-14,botcore::CecilItemKind::Weapon);
 BotSupplyGraph().points[2].important_entity=995;wallMode=1;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==995,"ordinary eye LOS rejection cannot poison a valid mapped node connector");
 _botRayBudget=16;BotSupplyTick(&player,0,2,4);
 check(BotSupplyState(0).goalEntity==995&&BotSupplyState(0).mappedWeaponGoal,"close threat pauses a still-needed mapped route instead of destroying its provenance");
 for(int finish=0;finish<2;++finish){
  setup(3);player.w.usable=3;addItem(998,0,-22,botcore::CecilItemKind::Weapon);
  BotSupplyGraph().points[2].important_entity=998;
  _botRayBudget=16;BotSupplyTick(&player,0,1,1000);auto& s=BotSupplyState(0);
  const double since=s.goalSince,limit=s.goalDeadline;const int starts=goalEvents;
  bool retained=true,yielded=true,resumed=true;
  for(int tick=2;tick<=100;++tick){
   const bool close=(tick%4)<2;_botRayBudget=16;
   const auto motion=BotSupplyTick(&player,0,tick,close?7.9:8.1);
   retained&=s.goalEntity==998&&s.mappedWeaponGoal&&s.goalSince==since&&s.goalDeadline==limit;
   if(close)yielded&=!motion.active&&!motion.ownsMovement&&motion.buttons==0;
   else resumed&=motion.active&&motion.itemGoal&&motion.urgent;
  }
  check(retained&&goalEvents==starts&&endEvents==0,
   "repeated close-fight threshold crossings retain one mapped item attempt and its original deadline");
  check(yielded&&resumed,"close combat owns its action while the same urgent mapped route resumes outside the threshold");
  if(finish==0){
   player.pl.pl_PositionVector=FLOAT3D(0,0,-22);
   player.w.m_iAvailableWeapons=player.w.usable=3|botcore::CecilWeaponMask(4);_botRayBudget=16;
   BotSupplyTick(&player,0,101,7.9);
   check(s.pickups==1&&s.goalEntity==0&&!s.mappedWeaponGoal&&!s.ItemRejected(998,5.05),
    "actual gained usable weapon ends retained mapped attempt normally even during a close fight");
  }else{
   const int expired=(int)std::ceil(limit/.05);_botRayBudget=16;
   BotSupplyTick(&player,0,expired,7.9);
   check(s.goalEntity==0&&s.ItemRejected(998,expired*.05)&&std::strcmp(lastEnd,"timeout")==0,
    "close-fight pause never extends mapped attempt and original deadline still rejects a failed item");
  }
 }
 setup(3);player.w.usable=3;addItem(996,3,-22,botcore::CecilItemKind::Weapon);
 BotSupplyGraph().points[2].important_entity=996;blockedItems=3;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==0&&BotSupplyState(0).ItemRejected(996,.05,false),"actual blocked mapped connector retains physical rejection backoff");
 setup(3);player.w.usable=3;addItem(997,0,-22,botcore::CecilItemKind::Weapon);
 BotSupplyGraph().points[2].important_entity=997;
 BotSupplyState(0).anchor=0;BotSupplyState(0).goals.Run(BotSupplyGraph(),0);
 _botRayBudget=2;BotCecilChooseMappedWeapon(&player,BotSupplyState(0),BotCecilItemInput(&player,BotSupplyState(0),1000),0,1,.05);
 check(!BotSupplyState(0).ItemRejected(997,.05)&&BotSupplyState(0).goalEntity==0,"mapped budget exhaustion defers without blacklisting");
 _botRayBudget=16;BotSupplyTick(&player,0,2,1000);items[0].pickable=false;
 _botRayBudget=16;BotSupplyTick(&player,0,3,1000);
 check(BotSupplyState(0).goalEntity==0,"disappearing mapped weapon clears route before stale movement");
 setup(3);player.w.usable=3;BotSupplyGraph().points[1].z=-12;BotSupplyGraph().points[2].z=-14;
 BotSupplyGraph().points[0].links={2};BotSupplyGraph().points[1].links.clear();
 addItem(998,0,-12,botcore::CecilItemKind::Weapon);BotSupplyGraph().points[2].important_entity=998;
 _botRayBudget=16;BotSupplyTick(&player,0,1,1000);
 check(BotSupplyState(0).goalEntity==998&&BotSupplyState(0).goal==2,"failed ordinary nearest anchor cannot poison a reachable original mapped anchor");
 (void)weapon;
 }
 { // Bounded snapshots must not let unsuitable prefix items starve a weapon.
 setup(2);player.health=100;player.w.usable=3;
 for(unsigned i=0;i<128;++i){auto& e=addItem(100+i,0,-2,botcore::CecilItemKind::Ammo);e.item.ammo_mask=botcore::CecilWeaponMask(8);}
 auto& useful=addItem(999,0,-2,botcore::CecilItemKind::Weapon);useful.item.weapon=4;
 for(int tick=1;tick<=40;++tick){_botRayBudget=16;BotSupplyTick(&player,0,tick,1000);}
 check(BotSupplyState(0).goalEntity==999&&goalEvents>0,"128 unsuitable ammo items cannot hide later useful weapon");
 // Even eligible but occluded prefixes must not monopolize every snapshot.
 setup(2);player.health=100;player.w.usable=3;
 for(unsigned i=0;i<128;++i){auto& e=addItem(100+i,0,-2,botcore::CecilItemKind::Weapon);e.item.weapon=4;}
 auto& later=addItem(999,0,-2,botcore::CecilItemKind::Weapon);later.item.weapon=4;
 auto& fair=BotSupplyState(0);bool foundLater=false;
 for(int scan=0;scan<3;++scan){fair.ClearGoal();_botRayBudget=40;BotCecilChooseGoal(&player,0,scan+1,1000,false);foundLater=foundLater||fair.goalEntity==999;}
 check(foundLater,"bounded candidate window rotates beyond 128 eligible prefix items");
 fair.Reset();check(fair.itemScanAfter==0,"lifecycle reset restarts item scan cursor");
 }
 { // Preset control: absence of support is not an unconditional movement veto.
 setup();BotCecilSettings()=botcore::CecilPreset(2);double pitF=1,pitS=0,pitU=0;
 check(BotCecilSettings().bAvoidPits==0,"original normal preset does not enable pit avoidance");
 _botRayBudget=1;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,pitF,pitS,pitU,0,1)==1&&pitF==1&&rayCount==1&&BotSupplyState(0).probe.floorRays==0,"default preset allows missing-floor motion after one verified wall ray");
 setup();BotCecilSettings().bAvoidPits=0;wallMode=2;pitF=1;pitS=pitU=0;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,pitF,pitS,pitU,0,1)==0&&pitF==0&&BotSupplyState(0).probe.primaryReason==SCecilProbe::reasonWallHit&&BotSupplyState(0).probe.floorRays==0,"disabled pit avoidance still rejects actual walls");
 setup();BotCecilSettings().bAvoidPits=0;pitF=1;pitS=pitU=0;_botRayBudget=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,pitF,pitS,pitU,0,1)==0&&pitF==0&&rayCount==0,"disabled pit avoidance cannot bypass wall-ray budget");
 setup();BotCecilSettings().bAvoidPits=0;player.en_plViewpoint.pl_OrientationAngle(1)=NAN;pitF=1;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,pitF,pitS,pitU,0,1)==0&&pitF==0&&rayCount==0,"disabled pit avoidance cannot bypass invalid view state");
 setup();auto& pathState=BotSupplyState(0);pathState.goal=2;pathState.scanTick=100;
 const auto pathMove=BotSupplyTick(&player,0,1,1000);_botRayBudget=16;rayCount=0;pitF=1;pitS=pitU=0;
 check(pathMove.active&&pathState.hop>=0,"fixture establishes a live directed navigation point");
 check(BotCecilSafeMotion(&player,pathState,.05,pitF,pitS,pitU,0,1)==1&&pitF==1&&pathState.probe.floorRays==0,"opt-in pit avoidance exempts an actual current NAV point");
 pathState.blocked[pathState.hop]=1;_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,pathState,.05,pitF,pitS,pitU,0,1)==0&&pathState.probe.floorRays>0,"blocked current NAV point restores off-graph support checks");
 pathState.blocked[pathState.hop]=0;_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,pathState,.1,pitF,pitS,pitU,0,1)==0&&pathState.probe.floorRays>0,"last-tick NAV context cannot exempt a caller that skipped navigation update");
 pathState.goal=1;_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,pathState,.05,pitF,pitS,pitU,0,1)==0&&pathState.probe.floorRays>0,"post-update goal change invalidates current point context");
 pathState.ClearGoal();_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,pathState,.15,pitF,pitS,pitU,0,1)==0&&pathState.probe.floorRays>0,"cleared goal cannot retain a stale floor exemption");
 setup();auto& stale=BotSupplyState(0);stale.goal=2;stale.hop=1;_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,stale,0,pitF,pitS,pitU,0,1)==0&&stale.probe.floorRays>0,"anchor goal and stale hop alone do not establish a current NAV point");
 setup();player.health=25;auto& connector=BotSupplyState(0);addItem(501,0,-2);connector.goal=connector.anchor=0;connector.goalEntity=501;connector.scanTick=100;
 const auto connectorMove=BotSupplyTick(&player,0,1,1000);_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(connectorMove.active&&connector.hop==0&&BotCecilSafeMotion(&player,connector,.05,pitF,pitS,pitU,0,1)==1&&connector.probe.floorRays==0,"arrived target retains NAV context for verified item connector");
 setup();auto& guarded=BotSupplyState(0);guarded.goal=2;guarded.scanTick=100;BotSupplyTick(&player,0,1,1000);
 BotSupplyTick(&player,0,2,1);_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,guarded,.1,pitF,pitS,pitU,0,1)==0&&guarded.probe.floorRays>0,"close-combat early return cannot retain preceding NAV context");
 setup();auto& failed=BotSupplyState(0);failed.goal=2;failed.scanTick=100;BotSupplyGraph().points[0].links.clear();
 BotSupplyTick(&player,0,1,1000);_botRayBudget=16;pitF=1;pitS=pitU=0;
 check(BotCecilSafeMotion(&player,failed,.05,pitF,pitS,pitU,0,1)==0&&failed.probe.floorRays>0,"unreachable directed goal remains off graph for pit avoidance");
 }
 setup();double probeF=1,probeS=0,probeU=0;wallMode=2;obstruction.en_ulID=77;_botRayBudget=16;
 auto& diagnostic=BotSupplyState(0);
 check(BotCecilSafeMotion(&player,diagnostic,0,probeF,probeS,probeU,0,1)==0&&diagnostic.probe.primaryReason==SCecilProbe::reasonWallHit&&diagnostic.probe.lastReason==SCecilProbe::reasonWallHit&&diagnostic.probe.hitEntity==77&&diagnostic.probe.wallRays==4&&diagnostic.probe.floorRays==0,"wall rejection records existing hit and exact ray counts");
 check(diagnostic.probe.inputForward==1&&diagnostic.probe.inputStrafe==0&&diagnostic.probe.finalYaw==0&&diagnostic.probe.to[2]>diagnostic.probe.from[2],"probe preserves original input and last rejected reverse geometry");
 setup();probeF=1;probeS=probeU=0;_botRayBudget=16;
 BotCecilSafeMotion(&player,BotSupplyState(0),0,probeF,probeS,probeU,0,1);
 const auto noSupport=BotSupplyState(0).probe;
 check(noSupport.primaryReason==SCecilProbe::reasonNoFloor&&noSupport.lastReason==SCecilProbe::reasonNoFloor&&noSupport.floorRays==4&&noSupport.wallRays==4&&noSupport.hitEntity==0&&noSupport.to[1]<noSupport.from[1],"missing support records floor rays and real downward geometry");
 setup();floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorEntity.en_ulID=55;floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);probeF=1;probeS=probeU=0;
 BotCecilSafeMotion(&player,BotSupplyState(0),0,probeF,probeS,probeU,0,1);
 check(BotSupplyState(0).probe.primaryReason==SCecilProbe::reasonUnsupportedNormal&&near(BotSupplyState(0).probe.support,-1)&&BotSupplyState(0).probe.normal[1]==-1&&BotSupplyState(0).probe.hitEntity==55,"unsupported normal records actual brush support dot and entity");
 setup();floorMode=2;floorPolygon.bpo_ulFlags=BPOF_PASSABLE;forcePassableHit=true;probeF=1;probeS=probeU=0;
 BotCecilSafeMotion(&player,BotSupplyState(0),0,probeF,probeS,probeU,0,1);
 check(BotSupplyState(0).probe.lastReason==SCecilProbe::reasonPassable,"passable brush has distinct rejection reason");
 setup();_botRayBudget=1;probeF=1;probeS=probeU=0;
 BotCecilSafeMotion(&player,BotSupplyState(0),0,probeF,probeS,probeU,0,1);
 check(BotSupplyState(0).probe.primaryReason==SCecilProbe::reasonBudget&&BotSupplyState(0).probe.reasonMask==(1u<<SCecilProbe::reasonBudget)&&rayCount==0,"budget rejection adds no diagnostic raycast");
 probeF=probeS=probeU=0;BotCecilSafeMotion(&player,BotSupplyState(0),.05,probeF,probeS,probeU,0,1);
 check(BotSupplyState(0).probe.primaryReason==0&&BotSupplyState(0).probe.lastReason==0&&BotSupplyState(0).probe.reasonMask==0&&BotSupplyState(0).probe.hitEntity==0,"each call resets stale probe diagnostics");
 setup();player.body.m[0][0]=2;probeF=1;
 BotCecilSafeMotion(&player,BotSupplyState(0),0,probeF,probeS,probeU,0,1);
 check(BotSupplyState(0).probe.primaryReason==SCecilProbe::reasonInvalid&&rayCount==0,"invalid input is distinct and adds no ray");
 setup();double tinyF=.04,tinyS=0,tinyU=0;_botRayBudget=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,tinyF,tinyS,tinyU,0,1)==1&&tinyF==0&&tinyS==0&&tinyU==0&&rayCount==0,"subthreshold motion becomes true neutral even without floor or budget");
 check(!BotCecilFloor(&player,.04,0,0,0)&&!BotCecilClearMotion(&player,.04,0,0,0),"direct probes never exempt small nonzero horizontal movement");
 tinyF=.04;tinyU=1;check(BotCecilSafeMotion(&player,BotSupplyState(0),0,tinyF,tinyS,tinyU,0,1)==0&&tinyF==0&&tinyU==0,"vertical input cannot hide small horizontal motion from floor checking");
 setup();auto& locks=BotSupplyState(0);auto& lockGraph=BotSupplyGraph();auto& lockEntity=addItem(99,0,0);lockGraph.points[1].lock_entity=99;
 BotCecilLocks(&player,locks,0);
 check(lockEvents==1&&lastLocked==0&&lastPresent==1&&!locks.blocked[1],"physical lock logs initial unlocked snapshot once");
 BotCecilLocks(&player,locks,.1);check(lockEvents==1,"unchanged physical lock produces no repeated event");
 locks.avoidNode=1;locks.avoidUntil=10;BotCecilLocks(&player,locks,.2);
 check(lockEvents==1&&locks.blocked[1],"temporary avoid node cannot create a physical lock event");
 lockEntity.pl.pl_PositionVector(1)=.2f;BotCecilLocks(&player,locks,.3);
 check(lockEvents==2&&lastLocked==1&&lastPresent==1,"physical lock displacement creates locked transition");
 lockEntity.flags=ENF_DELETED;BotCecilLocks(&player,locks,.4);
 check(lockEvents==3&&lastLocked==1&&lastPresent==0,"missing lock entity has distinct physical status");
 lockEntity.flags=0;lockEntity.pl.pl_PositionVector(1)=0;BotCecilLocks(&player,locks,.5);
 check(lockEvents==4&&lastLocked==0&&locks.blocked[1],"physical unlock logs independently of still active temporary avoid");
 locks.Reset();BotCecilLocks(&player,locks,.6);check(lockEvents==5&&lastLocked==0,"reset deterministically logs fresh physical lock snapshot");
 setup();_botRayBudget=2;check(!BotSupplyClear(&player,{0,0,0},{1,0,0})&&rayCount==0,"reserve final wall and floor rays");
 setup();check(!BotCecilFloor(&player,1,0,0,32),"teleport flags never excuse missing support");
 setup();floorMode=1;check(!BotCecilFloor(&player,1,0,0,0),"model is not floor support");
 floorMode=2;floorEntity.type=CEntity::RT_BRUSH;
 check(BotCecilFloor(&player,1,0,0,0),"brush upward polygon supports movement");
 floorPolygon.bpo_ulFlags=BPOF_PASSABLE;check(!BotCecilFloor(&player,1,0,0,0),"passable brush is not support");
 floorPolygon.bpo_ulFlags=0;floorPlane.bpl_plAbsolute=FLOAT3D(1,0,0);
 check(!BotCecilFloor(&player,1,0,0,0),"wall normal is not support");
 floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;
 check(BotCecilFloor(&player,1,0,0,90)&&near(lastFrom(1),-1.5)&&near(lastFrom(3),0),"terrain support and supplied final heading");
 setup(1);check(BotSupplyNearest(&player,{9,0,0},FALSE)==-1,"item connector beyond eight is rejected");
 setup(1);check(BotSupplyNearest(&player,{9,0,0},TRUE)==0,"player anchoring keeps twelve unit range");
 setup(1);player.health=25;addItem(10,0,-3);
 BotCecilChooseGoal(&player,0,0,1000);auto& s=BotSupplyState(0);double since=s.goalSince;
 _botRayBudget=40;BotCecilChooseGoal(&player,0,200,1000);
 check(goalEvents==1,"one goal event for one selection despite repeated scans");
 check(s.goalEntity==10&&s.goalSince==since,"same item does not renew twelve second lifetime");
 _botRayBudget=40;auto expired=BotSupplyTick(&player,0,260,1000);
 check(endEvents==1&&std::strcmp(lastEnd,"timeout")==0,"timeout goal end event");
 check(s.goalEntity!=10&&!expired.active,"expired item rejected before movement and selection");
 setup(1);player.health=25;for(int i=1;i<=7;++i)addItem(100+i,float(i),0);
 blockedItems=6;
 for(int tick=0;tick<140;tick+=20){_botRayBudget=7;BotCecilChooseGoal(&player,0,tick,1000);}
 check(BotSupplyState(0).goalEntity==107,"bounded rejection memory advances beyond occluded leaders");
 setup(1);player.health=25;addItem(10,0,-7);
 auto& connector=BotSupplyState(0);connector.goal=connector.anchor=0;connector.goalEntity=10;connector.goalSince=0;connector.scanTick=999;
 player.pl.pl_PositionVector=FLOAT3D(0,0,2);BotSupplyGraph().points[0].radius=3;
 auto disconnected=BotSupplyTick(&player,0,1,1000);
 check(endEvents==1&&std::strcmp(lastEnd,"connector")==0,"connector goal end event");
 check(connector.goalEntity==0&&!disconnected.active,"failed final connector immediately clears item");
 setup(3);auto& chain=BotSupplyState(0);chain.goal=0;chain.anchor=0;chain.scanTick=999;
 BotSupplyGraph().points[0].flags=botcore::CECIL_IMPORTANT;BotSupplyGraph().points[0].next_slot=2;
 BotSupplyGraph().points[0].links={1};BotSupplyGraph().points[1].flags=botcore::CECIL_UNREACHABLE;
 BotSupplyTick(&player,0,1,1000);_botRayBudget=40;
 auto chained=BotSupplyTick(&player,0,2,1000);
 check(chain.goal==2&&chained.active&&chained.forward>0,"important chain keeps context into untagged destination");
 setup(2);BotSupplyGraph().points[1].x=10;BotSupplyGraph().points[1].z=0;
 BotCecilSettings().bStrafe=0;auto& noStrafe=BotSupplyState(0);noStrafe.goal=1;noStrafe.anchor=0;noStrafe.scanTick=999;
 auto lateral=BotSupplyTick(&player,0,1,1000);check(lateral.strafe==0,"bStrafe disables native lateral motion");
 setup(2);auto& danger=BotSupplyState(0);danger.goal=1;danger.anchor=0;danger.scanTick=999;
 check(!BotSupplyTick(&player,0,1,5).active,"close threat prevents blind patrol navigation");
 setup(2);player.health=25;addItem(10,0,-10);auto& health=BotSupplyState(0);
 health.goal=1;health.anchor=0;health.goalEntity=10;health.scanTick=999;
 auto flee=BotSupplyTick(&player,0,1,5);
 check(flee.active&&owns(flee,0)&&typed(flee,0),"urgent health can navigate with a close threat and typed result");
 setup(2);player.health=70;addItem(10,0,-10);auto& mild=BotSupplyState(0);
 mild.goal=1;mild.anchor=0;mild.goalEntity=10;mild.scanTick=999;
 check(!BotSupplyTick(&player,0,1,5).active,"nonurgent health yields to close threat");
 setup(1);check(BotSupplyNearest(&player,{8,0,0},FALSE)==0,"eight unit item connector accepted");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;_botRayBudget=1;
 check(BotCecilFloor(&player,1,0,0,0)&&_botRayBudget==0,"floor uses the reserved last ray");
 setup();auto& reject=BotSupplyState(0);reject.RejectItem(42,10);
 check(reject.ItemRejected(42,39.9)&&!reject.ItemRejected(42,40),"rejection TTL expires exactly after thirty seconds");
 for(unsigned i=1;i<=300;++i)reject.RejectItem(1000+i,i);
 check(!reject.ItemRejected(1001,301)&&reject.ItemRejected(1300,301),"bounded rejection records replace oldest expiry");
 reject.Reset();check(!reject.ItemRejected(1300,301),"source reset clears rejection memory");
 setup(1);player.health=25;auto& hidden=addItem(10,0,-3);auto& gone=BotSupplyState(0);
 gone.goal=gone.anchor=0;gone.goalEntity=10;gone.scanTick=999;hidden.pickable=false;
 check(!BotSupplyTick(&player,0,1,1000).active&&gone.goalEntity==0,"unavailable item invalidated before movement");
 check(endEvents==1&&std::strcmp(lastEnd,"unavailable")==0,"unavailable goal end event");
 setup(1);player.health=25;addItem(10,1,0);auto& occluded=BotSupplyState(0);
 occluded.goal=occluded.anchor=0;occluded.goalEntity=10;occluded.scanTick=999;blockedItems=1;
 check(!BotSupplyTick(&player,0,1,1000).active&&occluded.goalEntity==0,"occluded final connector immediately rejected");
 botcore::CecilItem candidate;botcore::CecilItemInput need;
 candidate.kind=botcore::CecilItemKind::Ammo;candidate.ammo_mask=8;need.ammo_need_mask=8;need.owned=8;
 check(BotCecilUrgentItem(candidate,need),"needed ammo marked urgent");
 need.ammo_need_mask=0;check(!BotCecilUrgentItem(candidate,need),"unneeded ammo not urgent");
 candidate.kind=botcore::CecilItemKind::Weapon;need.usable=botcore::CecilWeaponMask(13);need.enemy_distance=20;
 check(BotCecilUrgentItem(candidate,need),"out of range collected weapon does not suppress supply urgency");
 need.enemy_distance=50;check(!BotCecilUrgentItem(candidate,need),"usable ranged weapon removes weapon supply urgency");
 setup(3);auto& stable=BotSupplyState(0);stable.goal=2;stable.anchor=0;stable.scanTick=99999;
 measuring=true;
 for(int tick=1;tick<=1000;++tick){_botRayBudget=20;BotSupplyTick(&player,0,tick,1000);}
 measuring=false;check(allocations==0,"prepared native timer path does not allocate");
 setup(3);BotCecilSettings().bItemSearch=0;
 SCecilFollowGoal follow;follow.valid=true;follow.x=0;follow.y=0;follow.z=-20;follow.entity=901;follow.generation=7;follow.expiresAt=5;
 auto chased=BotSupplyTick(&player,0,1,1000,&follow);
 check(chased.active&&chased.followGoal&&BotSupplyState(0).goal==2,"frozen target becomes directed NAV goal without target entity");
 _botRayBudget=40;follow.expiresAt=.1;
 auto timedOut=BotSupplyTick(&player,0,2,1000,&follow);
 check(!timedOut.followGoal&&BotSupplyState(0).followEntity==0,"expired follow snapshot clears owned goal");
 _botRayBudget=40;follow.expiresAt=5;BotSupplyTick(&player,0,3,1000,&follow);
 follow.entity=902;follow.generation=8;_botSupplyMapSerial=8;follow.z=-10;_botRayBudget=40;
 BotSupplyTick(&player,0,4,1000,&follow);
 check(BotSupplyState(0).goal==1&&BotSupplyState(0).followEntity==902&&BotSupplyState(0).followGeneration==8,"entity generation change replans immediately");
 follow.generation=9;_botSupplyMapSerial=9;follow.z=-20;_botRayBudget=40;BotSupplyTick(&player,0,5,1000,&follow);
 check(BotSupplyState(0).goal==2&&BotSupplyState(0).followGeneration==9,"same entity reused with new generation invalidates old route");
 _botRayBudget=40;auto missing=BotSupplyTick(&player,0,6,1000);
 check(!missing.followGoal&&BotSupplyState(0).followEntity==0,"missing snapshot clears follow context");
 follow.x=std::numeric_limits<double>::quiet_NaN();_botRayBudget=40;
 check(!BotSupplyTick(&player,0,7,1000,&follow).followGoal,"nonfinite frozen target is rejected");
 setup(3);follow.x=0;follow.entity=901;follow.generation=7;follow.z=-20;follow.expiresAt=5;
 BotSupplyTick(&player,0,1,1000,&follow);BotSupplyReset(0);
 check(BotSupplyState(0).followEntity==0&&BotSupplyState(0).goal==-1,"map or source reset clears frozen target route");
 setup(3);player.health=25;addItem(10,0,-10);auto& urgentState=BotSupplyState(0);
 urgentState.goal=1;urgentState.anchor=0;urgentState.goalEntity=10;urgentState.scanTick=999;
 auto supplyFirst=BotSupplyTick(&player,0,1,1000,&follow);
 check(supplyFirst.itemGoal&&supplyFirst.urgent&&!supplyFirst.followGoal&&urgentState.goalEntity==10,"urgent item retains priority over follow snapshot");
 setup(3);BotCecilSettings().bItemSearch=0;follow.z=-10;BotSupplyTick(&player,0,1,1000,&follow);
 player.pl.pl_PositionVector=FLOAT3D(0,0,-10);_botRayBudget=40;
 auto followArrived=BotSupplyTick(&player,0,2,1000,&follow);
 check(followArrived.followGoal&&!followArrived.active&&BotSupplyState(0).goal==1,"follow arrival waits at frozen node instead of taking important chain");
 measuring=true;
 for(int tick=3;tick<80;++tick){_botRayBudget=20;BotSupplyTick(&player,0,tick,1000,&follow);}
 measuring=false;check(allocations==0,"prepared follow updates do not allocate");
 setup(3);BotCecilSettings().bItemSearch=0;follow.entity=901;follow.generation=6;follow.z=-20;follow.expiresAt=5;
 check(!BotSupplyTick(&player,0,1,1000,&follow).followGoal,"snapshot from a different map generation is rejected");
 setup(3);BotCecilSettings().bItemSearch=0;follow.generation=7;follow.z=-10;follow.expiresAt=5;
 BotSupplyTick(&player,0,1,1000,&follow);follow.z=-20;_botRayBudget=40;
 BotSupplyTick(&player,0,2,1000,&follow);
 check(BotSupplyState(0).goal==1,"same identity snapshot refresh is throttled between replans");
 _botRayBudget=40;BotSupplyTick(&player,0,23,1000,&follow);
 check(BotSupplyState(0).goal==2,"updated frozen coordinates refresh the target after one second");
 setup(3);player.health=70;addItem(10,0,-10);auto& nonurgent=BotSupplyState(0);
 nonurgent.goal=1;nonurgent.anchor=0;nonurgent.goalEntity=10;nonurgent.scanTick=999;
 auto retained=BotSupplyTick(&player,0,1,1000,&follow);
 check(retained.itemGoal&&!retained.urgent&&!retained.followGoal&&nonurgent.goal==1,"existing nonurgent item may finish before chasing");
 setup(1);player.health=25;addItem(10,0,-3);auto& deferred=BotSupplyState(0);
 deferred.goal=deferred.anchor=0;deferred.goalEntity=10;deferred.scanTick=999;_botRayBudget=1;
 auto noBudget=BotSupplyTick(&player,0,1,1000);
 check(!noBudget.active&&deferred.goalEntity==10&&endEvents==0,"missing connector query budget waits without rejecting valid item");
 setup(4);BotCecilSettings().bItemSearch=0;BotSupplyGraph().points[0].links={1,3};
 BotSupplyGraph().points[1].flags=botcore::CECIL_UNREACHABLE;BotSupplyGraph().points[3].x=10;BotSupplyGraph().points[3].z=0;
 auto& hold=BotSupplyState(0);hold.goal=2;hold.anchor=0;hold.scanTick=999;
 auto stay=BotSupplyTick(&player,0,1,1000);check(stay.active&&stay.forward==0&&stay.strafe==0,"UNREACHABLE preserves original initial stay");
 for(int tick=2;tick<=41;++tick){_botRayBudget=40;BotSupplyTick(&player,0,tick,1000);}
 check(hold.goal==-1&&hold.avoidNode==1,"two second hold discards goal and avoids actual blocking hop");
 _botRayBudget=40;auto detour=BotSupplyTick(&player,0,43,1000);
 check(detour.active&&std::fabs(detour.forward)+std::fabs(detour.strafe)>0&&hold.goal==3,"roam resumes on alternate safe branch after bounded hold");
 BotSupplyGraph().points[2].lock_entity=777;BotCecilLocks(&player,hold,3);
 check(hold.blocked[1]&&hold.blocked[2],"temporary avoid is combined with actual dynamic lock");
 BotCecilLocks(&player,hold,13);check(!hold.blocked[1]&&hold.blocked[2],"avoid expires without removing actual dynamic lock");
 setup(3);BotSupplyGraph().points[1].flags=botcore::CECIL_UNREACHABLE;auto& important=BotSupplyState(0);
 important.goal=2;important.anchor=0;important.scanTick=999;important.importantGoal=true;important.avoidNode=1;important.avoidUntil=10;
 auto crossing=BotSupplyTick(&player,0,1,1000);
 check(crossing.active&&crossing.forward>0&&!important.blocked[1],"important context bypasses temporary avoidance and original stay");
 setup(2);BotSupplyGraph().points[1].y=6;BotSupplyGraph().points[1].z=0;
 auto& high=BotSupplyState(0);high.goal=1;high.anchor=0;high.scanTick=999;
 for(int tick=1;tick<=42;++tick){_botRayBudget=40;BotSupplyTick(&player,0,tick,1000);}
 check(high.goal==-1&&high.avoidNode==1,"too high stay is also bounded at two seconds");
 setup(4);BotCecilSettings().bItemSearch=0;BotSupplyGraph().points[0].links={1,3};
 BotSupplyGraph().points[1].flags=botcore::CECIL_UNREACHABLE;BotSupplyGraph().points[3].x=10;BotSupplyGraph().points[3].z=0;
 follow.valid=true;follow.entity=901;follow.generation=7;follow.x=follow.y=0;follow.z=-20;follow.expiresAt=100;
 SCecilMove followDetour;
 for(int tick=1;tick<=43;++tick){_botRayBudget=40;followDetour=BotSupplyTick(&player,0,tick,1000,&follow);}
 check(followDetour.active&&!followDetour.followGoal&&BotSupplyState(0).goal==3,"follow periodic refresh cannot reset hold deadline; alternate roam resumes");
 setup(3);player.pl.pl_PositionVector=FLOAT3D(100,0,100);
 auto unanchored=BotSupplyTick(&player,0,1,1000);
 check(!unanchored.active&&unanchored.forward==0&&unanchored.strafe==0&&unanchored.up==0,"missing safe anchor returns neutral movement");
 setup(2);BotSupplyGraph().points[1].y=6;BotSupplyGraph().points[1].z=0;player.m_pstState=PST_SWIM;
 auto& swimmer=BotSupplyState(0);swimmer.goal=1;swimmer.anchor=0;swimmer.scanTick=999;
 auto swimming=BotSupplyTick(&player,0,1,1000);
 check(swimming.active&&near(swimming.up,1)&&near(swimming.forward,0),"confirmed swim overrides too high stay with normalized vertical movement");
 check(player.m_pstState==PST_SWIM&&player.pl.pl_PositionVector.Length()==0&&player.flags==0,"swimming adapter does not mutate player snapshot");
 setup(2);BotSupplyGraph().points[1].y=-6;BotSupplyGraph().points[1].z=0;player.m_pstState=PST_DIVE;
 auto& diver=BotSupplyState(0);diver.goal=1;diver.anchor=0;diver.scanTick=999;
 check(near(BotSupplyTick(&player,0,1,1000).up,-1),"confirmed dive follows downward waypoint");
 setup(2);BotSupplyGraph().points[1].flags=botcore::CECIL_UNREACHABLE;player.m_pstState=PST_SWIM;
 auto& wet=BotSupplyState(0);wet.goal=1;wet.anchor=0;wet.scanTick=999;
 check(BotSupplyTick(&player,0,1,1000).forward>0,"liquid movement has original priority over UNREACHABLE stay");
 setup(1);player.m_pstState=PST_SWIM;player.health=25;auto& wetItem=addItem(10,0,-1);wetItem.pl.pl_PositionVector(2)=2;
 auto& wetGoal=BotSupplyState(0);wetGoal.goal=wetGoal.anchor=0;wetGoal.goalEntity=10;wetGoal.scanTick=999;
 auto wetConnector=BotSupplyTick(&player,0,1,1000);
 check(near(wetConnector.up,2/std::sqrt(5.0))&&near(wetConnector.forward,1/std::sqrt(5.0)),"liquid final item connector uses normalized three dimensional direction");
 setup();player.m_pstState=PST_SWIM;check(BotCecilFloor(&player,1,0,0,0)&&rayCount==0,"confirmed swim does not require a floor");
 player.m_pstState=PST_DIVE;check(BotCecilFloor(&player,1,0,0,0),"confirmed dive does not require a floor");
 player.m_pstState=PST_STAND;check(!BotCecilFloor(&player,1,0,0,0),"walking still requires floor support");
 setup(2);player.m_pstState=PST_SWIM;player.en_vGravityDir=FLOAT3D(1,0,0);auto& sideways=BotSupplyState(0);
 sideways.goal=1;sideways.anchor=0;sideways.scanTick=999;
 check(BotSupplyTick(&player,0,1,1000).active,"swim adapter accepts a valid transitional gravity basis");
 setup(3);BotCecilSettings().bItemSearch=0;CSwitch switchEntity;switchEntity.en_ulID=600;
 switchEntity.pl.pl_PositionVector=FLOAT3D(0,1,-1.5);player.world.wo_cenEntities.push_back(&switchEntity);
 BotSupplyGraph().points[0].important_entity=600;BotSupplyGraph().points[0].next_slot=1;
 auto& interaction=BotSupplyState(0);interaction.goal=interaction.anchor=0;interaction.importantGoal=true;interaction.scanTick=999;
 player.w.m_penRayHit=&switchEntity;player.w.m_fRayHitDistance=1.5;
 auto used=BotSupplyTick(&player,0,1,1000);
 check(used.buttons==EXPECTED_NATIVE_USE&&used.useControl&&interaction.goal==1,"native matching close usable switch yields one normal USE action and preserves chain");
 check(switchEntity.m_bUseable&&switchEntity.target==nullptr&&switchEntity.pl.pl_PositionVector(2)==1,"USE adapter leaves switch snapshot unchanged");
 _botRayBudget=40;auto release=BotSupplyTick(&player,0,2,1000);
 check(release.useControl&&release.buttons==0,"USE reserves following release tick against scope bits");
 _botRayBudget=40;check(!BotSupplyTick(&player,0,3,1000).useControl,"USE scope ownership ends after release tick");
 setup(1);switchEntity.en_ulID=600;player.world.wo_cenEntities.push_back(&switchEntity);BotSupplyGraph().points[0].important_entity=600;
 auto& wrongRay=BotSupplyState(0);wrongRay.goal=wrongRay.anchor=0;wrongRay.importantGoal=true;wrongRay.scanTick=999;
 player.w.m_penRayHit=&obstruction;player.w.m_fRayHitDistance=1;
 auto align=BotSupplyTick(&player,0,1,1000);
 check(align.buttons==0&&align.useControl&&align.pitch_delta>0&&align.forward>0,"wrong native hit cannot USE; bounded physical approach aims pitch");
 player.w.m_penRayHit=&switchEntity;player.w.m_fRayHitDistance=2;_botRayBudget=40;
 check(BotSupplyTick(&player,0,2,1000).buttons==0,"USE rejects exact two metre native hit distance");
 player.w.m_fRayHitDistance=-1;_botRayBudget=40;
 check(BotSupplyTick(&player,0,3,1000).buttons==0,"USE rejects invalid native hit distance");
 switchEntity.m_bUseable=false;player.w.m_fRayHitDistance=1;_botRayBudget=40;
 check(BotSupplyTick(&player,0,4,1000).buttons==0&&wrongRay.interactionPoint==-1,"unusable switch ends attempt without event or USE");
 switchEntity.m_bUseable=true;
 setup(3);CMovingBrush brush;brush.en_ulID=601;brush.m_penSwitch=&switchEntity;brush.pl.pl_PositionVector=FLOAT3D(0,1,-1.5);
 player.world.wo_cenEntities.push_back(&brush);player.world.wo_cenEntities.push_back(&switchEntity);
 BotSupplyGraph().points[0].important_entity=601;BotSupplyGraph().points[0].next_slot=1;
 auto& relay=BotSupplyState(0);relay.goal=relay.anchor=0;relay.importantGoal=true;relay.scanTick=999;
 player.w.m_penRayHit=&brush;player.w.m_fRayHitDistance=1;
 check(BotSupplyTick(&player,0,1,1000).buttons==EXPECTED_NATIVE_USE,"matching MovingBrush native ray relays USE to its usable switch");
 setup(3);CMarker marker;CEntity markerTarget;marker.en_ulID=700;markerTarget.en_ulID=701;
 marker.target=&markerTarget;markerTarget.pl.pl_PositionVector=FLOAT3D(0,0,-20);
 player.world.wo_cenEntities={&marker,&markerTarget};BotSupplyGraph().points[0].important_entity=700;BotSupplyGraph().points[0].next_slot=1;
 auto& markerRoute=BotSupplyState(0);markerRoute.goal=markerRoute.anchor=0;markerRoute.importantGoal=true;markerRoute.scanTick=999;
 auto redirected=BotSupplyTick(&player,0,1,1000);
 check(markerRoute.goal==2&&markerRoute.importantGoal&&redirected.buttons==0,"Marker GetTarget overrides next chain with reachable directed target anchor");
 setup(3);BotCecilSettings().bItemSearch=0;player.world.wo_cenEntities={&switchEntity};
 BotSupplyGraph().points[0].important_entity=600;BotSupplyGraph().points[0].next_slot=1;
 auto& timedInteraction=BotSupplyState(0);timedInteraction.goal=timedInteraction.anchor=0;timedInteraction.importantGoal=true;
 for(int tick=1;tick<=102;++tick){_botRayBudget=40;BotSupplyTick(&player,0,tick,1000);}
 check(timedInteraction.goal==1&&timedInteraction.interactionPoint==-1,"unmatched switch attempt ends after five seconds despite periodic scans");
 setup(1);player.world.wo_cenEntities={&switchEntity};BotSupplyGraph().points[0].important_entity=600;
 auto& finalUse=BotSupplyState(0);finalUse.goal=finalUse.anchor=0;finalUse.importantGoal=true;finalUse.scanTick=999;
 player.w.m_penRayHit=&switchEntity;player.w.m_fRayHitDistance=1;
 BotSupplyTick(&player,0,1,1000);_botRayBudget=40;auto idleRelease=BotSupplyTick(&player,0,2,1000);
 check(!idleRelease.active&&idleRelease.useControl&&idleRelease.ownsMovement&&idleRelease.buttons==0,"idle release tick reserves neutral movement and USE against scope");
 setup(1);player.world.wo_cenEntities={&switchEntity};BotSupplyGraph().points[0].important_entity=600;
 auto& threatened=BotSupplyState(0);threatened.goal=threatened.anchor=0;threatened.importantGoal=true;threatened.scanTick=999;
 player.w.m_penRayHit=&switchEntity;player.w.m_fRayHitDistance=1;
 auto closeCombat=BotSupplyTick(&player,0,1,5);
 check(!closeCombat.active&&closeCombat.buttons==0&&!closeCombat.useControl,"close threat prevents important approach and USE");
 setup(1);CSwitch otherSwitch;otherSwitch.en_ulID=602;CMovingBrush otherBrush;otherBrush.en_ulID=603;otherBrush.m_penSwitch=&otherSwitch;
 player.world.wo_cenEntities={&brush,&switchEntity,&otherBrush,&otherSwitch};BotSupplyGraph().points[0].important_entity=601;
 auto& wrongRelay=BotSupplyState(0);wrongRelay.goal=wrongRelay.anchor=0;wrongRelay.importantGoal=true;wrongRelay.scanTick=999;
 player.w.m_penRayHit=&otherBrush;player.w.m_fRayHitDistance=1;
 check(BotSupplyTick(&player,0,1,1000).buttons==0,"different MovingBrush switch identity cannot receive USE");
 brush.m_penSwitch=&brush;_botRayBudget=40;
 check(BotSupplyTick(&player,0,2,1000).buttons==0&&wrongRelay.interactionPoint==-1,"relay cycles are rejected without recursion");
 brush.m_penSwitch=&switchEntity;
 setup(3);BotCecilSettings().bItemSearch=0;marker.cls.name="Classes/MovingBrushMarker.ecl";
 player.world.wo_cenEntities={&marker,&markerTarget};BotSupplyGraph().points[0].important_entity=700;BotSupplyGraph().points[0].next_slot=1;
 BotSupplyGraph().points[1].links.clear();auto& unreachableMarker=BotSupplyState(0);
 unreachableMarker.goal=unreachableMarker.anchor=0;unreachableMarker.importantGoal=true;unreachableMarker.scanTick=999;
 BotSupplyTick(&player,0,1,1000);
 check(unreachableMarker.goal==0,"unreachable marker target cannot bypass directed topology");
 measuring=true;
 for(int tick=2;tick<=101;++tick){_botRayBudget=40;BotSupplyTick(&player,0,tick,1000);}
 measuring=false;
 check(unreachableMarker.goal==1&&unreachableMarker.interactionPoint==-1,"unreachable derived marker attempt expires and preserves next chain");
 check(allocations==0,"important interaction timer does not allocate");
 setup(1);player.world.wo_cenEntities={&switchEntity};BotSupplyGraph().points[0].important_entity=600;
 auto& cooled=BotSupplyState(0);cooled.goal=cooled.anchor=0;cooled.importantGoal=true;cooled.scanTick=999;
 player.w.m_penRayHit=&switchEntity;player.w.m_fRayHitDistance=1;BotSupplyTick(&player,0,1,1000);
 cooled.goal=0;cooled.importantGoal=true;cooled.scanTick=999;_botRayBudget=40;
 check(BotSupplyTick(&player,0,2,1000).buttons==0,"same switch cannot be rapidly retoggled within five second cooldown");
 setup(1);player.world.wo_cenEntities={&switchEntity};BotSupplyGraph().points[0].important_entity=600;
 auto& changingGravity=BotSupplyState(0);changingGravity.goal=changingGravity.anchor=0;changingGravity.importantGoal=true;changingGravity.scanTick=999;
 BotSupplyTick(&player,0,1,1000);player.en_vGravityDir=FLOAT3D(1,0,0);_botRayBudget=40;
 check(BotSupplyTick(&player,0,2,1000).active,"in-progress interaction supports valid gravity transitions");
 setup(1);switchEntity.pl.pl_PositionVector=FLOAT3D(30,0,0);player.world.wo_cenEntities={&switchEntity};BotSupplyGraph().points[0].important_entity=600;
 auto& remote=BotSupplyState(0);remote.goal=remote.anchor=0;remote.importantGoal=true;remote.scanTick=999;
 auto tooFar=BotSupplyTick(&player,0,1,1000);
 check(tooFar.buttons==0&&tooFar.forward==0&&remote.interactionPoint==-1,"remote switch cannot trigger blind interaction or distant connector");
 switchEntity.pl.pl_PositionVector=FLOAT3D(0,1,-1.5);
 setup(2);BotCecilSettings().bItemSearch=0;CSwitch firstSwitch,secondSwitch;
 firstSwitch.en_ulID=800;secondSwitch.en_ulID=801;
 firstSwitch.pl.pl_PositionVector=secondSwitch.pl.pl_PositionVector=FLOAT3D(0,1,-1);
 player.world.wo_cenEntities={&firstSwitch,&secondSwitch};
 BotSupplyGraph().points[0].important_entity=800;BotSupplyGraph().points[0].next_slot=1;
 BotSupplyGraph().points[1].important_entity=801;BotSupplyGraph().points[1].z=0;
 auto& sequence=BotSupplyState(0);sequence.goal=sequence.anchor=0;sequence.importantGoal=true;sequence.scanTick=999;
 player.w.m_penRayHit=&firstSwitch;player.w.m_fRayHitDistance=1;
 const auto firstPress=BotSupplyTick(&player,0,1,1000);
 player.w.m_penRayHit=&secondSwitch;_botRayBudget=40;
 const auto between=BotSupplyTick(&player,0,2,1000);
 _botRayBudget=40;const auto secondPress=BotSupplyTick(&player,0,3,1000);
 check(firstPress.buttons==EXPECTED_NATIVE_USE&&between.buttons==0&&between.useControl&&secondPress.buttons==EXPECTED_NATIVE_USE,
       "different chained switches require actual press release press edges");
 setup(2);player.body.m[0][0]=-1;player.body.m[1][1]=-1;player.en_vGravityDir=FLOAT3D(0,1,0);
 BotSupplyGraph().points[1].x=10;BotSupplyGraph().points[1].z=0;auto& inverted=BotSupplyState(0);
 inverted.goal=1;inverted.anchor=0;inverted.scanTick=999;
 auto upside=BotSupplyTick(&player,0,1,1000);
 check(upside.active&&near(upside.strafe,-1)&&near(upside.yaw_delta,9),"native inverted body projection emits correct lateral and yaw axes");
 inverted.navigator.Reset();player.en_plViewpoint.pl_OrientationAngle(1)=90;_botRayBudget=40;
 auto headTurn=BotSupplyTick(&player,0,2,1000);
 check(headTurn.active&&near(headTurn.forward,1)&&near(headTurn.strafe,0),"native inverted frame accounts for local head yaw");
 floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorPlane.bpl_plAbsolute=FLOAT3D(0,-1,0);_botRayBudget=40;
 check(BotCecilFloor(&player,1,0,0,0)&&lastTo(2)>lastFrom(2),"inverted floor ray follows real gravity and accepts upward-facing local support");
 floorPlane.bpl_plAbsolute=FLOAT3D(0,1,0);_botRayBudget=40;
 check(!BotCecilFloor(&player,1,0,0,0),"inverted support rejects wrong-facing world normal");
 setup(1);const double tilt=std::sqrt(.5);player.body.m[0][0]=tilt;player.body.m[0][1]=-tilt;player.body.m[1][0]=tilt;player.body.m[1][1]=tilt;
 player.en_vGravityDir=FLOAT3D(float(tilt),float(-tilt),0);BotSupplyGraph().points[0].x=float(7*tilt);BotSupplyGraph().points[0].y=float(7*tilt);
 check(BotSupplyNearest(&player,{0,0,0},FALSE)==0,"item anchoring tests height against actual tilted gravity instead of world Y");
 floorMode=2;floorEntity.type=CEntity::RT_BRUSH;floorPlane.bpl_plAbsolute=FLOAT3D(float(-tilt),float(tilt),0);_botRayBudget=40;
 check(BotCecilFloor(&player,1,0,0,0)&&lastTo(1)>lastFrom(1)&&lastTo(2)<lastFrom(2),"tilted floor ray and support-normal test use gravity vector");
 setup();player.body.m[0][0]=2;rayCount=0;double f=0,st=0,u=0;
 check(!BotCecilFloor(&player,0,0,0,0)&&BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==0&&rayCount==0,"invalid basis fails closed even for neutral input before any ray");
 setup();f=st=u=0;check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==1&&rayCount==0,"valid neutral motion consumes no floor query");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;floorPattern=1;f=1;st=u=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==2&&near(f,-.4)&&st==0&&u==0&&rayCount==8,"blocked primary motion recovers only after safe reverse ray");
 setup();f=1;st=u=0;check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==0&&f==0&&st==0&&u==0&&rayCount==8,"all unsafe alternatives result in neutral movement");
 setup();_botRayBudget=1;f=1;st=u=0;check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==0&&f==0&&rayCount==0,"recovery cannot exceed remaining ray budget");
 setup();_botRayBudget=0;f=1;st=u=0;check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==0&&f==0&&rayCount==0,"exhausted floor budget fails closed");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;floorPattern=2;player.pl.pl_PositionVector=FLOAT3D(0,0,1);
 for(int tick=0;tick<2000;++tick){f=1;st=u=0;_botRayBudget=16;BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,0,1);player.pl.pl_PositionVector(1)+=float(st*.5);player.pl.pl_PositionVector(3)-=float(f*.5);}
 check(player.pl.pl_PositionVector(1)>=2&&player.pl.pl_PositionVector(3)<-10,"2000 tick cliff detour makes net progress instead of reverse forward pendulum");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;floorPattern=1;player.pl.pl_PositionVector=FLOAT3D(0,0,2);
 bool budgetSafe=true;int reverseTicks=0;
 for(int tick=0;tick<2000;++tick){f=1;st=u=0;_botRayBudget=16;BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,0,1);player.pl.pl_PositionVector(1)+=float(st*10*1.35*.05);player.pl.pl_PositionVector(3)-=float(f*10*1.35*.05);budgetSafe=budgetSafe&&_botRayBudget>=0;reverseTicks+=f<0;}
 check(player.pl.pl_PositionVector(1)>10&&reverseTicks==0&&budgetSafe,"reviewer half-plane 2000 tick fixture gains lateral distance without reverse pendulum or ray overrun");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;floorPattern=1;player.pl.pl_PositionVector=FLOAT3D(0,0,2);reverseTicks=0;
 for(int tick=0;tick<2000;++tick){f=1;st=u=0;_botRayBudget=16;BotCecilSafeMotion(&player,BotSupplyState(0),tick*.05,f,st,u,0,0);player.pl.pl_PositionVector(3)-=float(f*10*1.35*.05);reverseTicks+=f<0;}
 check(reverseTicks>0&&reverseTicks<=12&&player.pl.pl_PositionVector(1)==0,"strafe disabled permits one bounded retreat then stops instead of repeating reverse forward cycles");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;wallMode=1;f=1;st=u=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==2&&f==0&&st>0,"wall collision selects safe lateral escape before reverse");
 auto& held=BotSupplyState(0);player.en_plViewpoint.pl_OrientationAngle(1)=90;f=1;st=u=0;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,held,.1,f,st,u,90,1)==2&&near(f,-.4)&&near(st,0),"held world escape survives changing head yaw");
 wallMode=2;f=1;st=u=0;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,held,.2,f,st,u,0,1)==0&&f==0&&st==0,"held escape is immediately stopped by new wall");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;wallMode=1;f=1;st=u=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,0)==2&&near(f,-.4)&&st==0,"strafe disabled permits only independently safe reverse");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;wallMode=1;f=1;st=u=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,.1)==2&&f==0&&near(st,.1)&&near(lastFrom(1),.15),"strafe cap is applied before floor support probe");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;player.body.m[0][0]=-1;player.body.m[1][1]=-1;player.en_vGravityDir=FLOAT3D(0,1,0);f=0;st=1;u=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==1&&wallFrom(2)<0&&wallTo(1)<wallFrom(1),"inverted wall probe uses body direction and gravity lift");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;wallMode=1;f=1;st=u=0;
 BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1);f=1;st=u=0;_botRayBudget=16;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),.6,f,st,u,0,1)==0&&BotSupplyState(0).escapeAfter>1,"zero net progress imposes cooldown rather than endless direction toggling");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;wallMode=2;f=1;st=u=0;_botRayBudget=3;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,f,st,u,0,1)==0&&rayCount==2&&_botRayBudget==1,"wall alternatives reserve floor query and never exceed shared budget");
 setup();auto& invalid=BotSupplyState(0);invalid.goal=1;invalid.anchor=0;invalid.scanTick=999;invalid.importantGoal=true;invalid.interactionPoint=1;
 player.en_plViewpoint.pl_OrientationAngle(1)=std::numeric_limits<float>::quiet_NaN();
 auto badYaw=BotSupplyTick(&player,0,1,1000);
 check(!badYaw.active&&badYaw.yaw_delta==0&&badYaw.buttons==0,"active Important rejects NaN local view yaw before interaction");
 player.en_plViewpoint.pl_OrientationAngle(1)=0;player.pl.pl_PositionVector(1)=std::numeric_limits<float>::quiet_NaN();
 auto badPosition=BotSupplyTick(&player,0,2,1000);
 check(!badPosition.active&&badPosition.yaw_delta==0&&badPosition.buttons==0,"active Important rejects NaN own position before interaction");
 setup(2);player.m_pstState=PST_DIVE;player.en_plViewpoint.pl_OrientationAngle(2)=60;auto& pitched=BotSupplyState(0);
 pitched.goal=1;pitched.anchor=0;pitched.scanTick=999;auto pitchedSwim=BotSupplyTick(&player,0,1,1000);
 const double back=-pitchedSwim.forward;const double appliedY=pitchedSwim.up-std::sin(60*3.141592653589793/180)*back;
 check(pitchedSwim.active&&std::fabs(appliedY)<1e-6&&pitchedSwim.forward==0&&pitchedSwim.pitch_delta<0,"dive levels pitched view before forward input without assuming native speed gains");
 pitched.navigator.Reset();player.en_plViewpoint.pl_OrientationAngle(2)=90;_botRayBudget=40;
 auto verticalLook=BotSupplyTick(&player,0,2,1000);
 check(verticalLook.active&&std::isfinite(verticalLook.forward)&&std::isfinite(verticalLook.up)&&std::fabs(verticalLook.forward)<=1&&std::fabs(verticalLook.up)<=1&&verticalLook.pitch_delta<0,"near vertical dive pitch uses bounded input and levels view for progress");
 setup();floorMode=1;floorEntity.type=CEntity::RT_TERRAIN;float nativeForward=1,nativeStrafe=0,nativeUp=0;
 check(BotCecilSafeMotion(&player,BotSupplyState(0),0,nativeForward,nativeStrafe,nativeUp,0,1)==1&&nativeForward==1,"safe motion accepts native FLOAT action references");
 setup(2);auto& malformed=BotSupplyState(0);malformed.goal=1;malformed.anchor=0;malformed.scanTick=999;player.body.m[2][2]=0;
 auto noFrame=BotSupplyTick(&player,0,1,1000);
 check(!noFrame.active&&noFrame.forward==0&&noFrame.strafe==0&&noFrame.buttons==0,"invalid native body frame suppresses navigation and interaction actions");
 setup(2);player.m_pstState=PST_DIVE;player.en_plViewpoint.pl_OrientationAngle(2)=90;auto& level=BotSupplyState(0);
 level.goal=1;level.anchor=0;level.scanTick=999;SCecilMove afterLevel;
 for(int tick=1;tick<=11;++tick){_botRayBudget=40;afterLevel=BotSupplyTick(&player,0,tick,1000);player.en_plViewpoint.pl_OrientationAngle(2)+=float(afterLevel.pitch_delta);}
 check(afterLevel.forward>0&&near(player.en_plViewpoint.pl_OrientationAngle(2),0),"vertical dive view levels and forward progress resumes within eleven ticks");
 setup(2);player.m_pstState=PST_SWIM;player.en_plViewpoint.pl_OrientationAngle(2)=-45;auto& swimLevel=BotSupplyState(0);
 swimLevel.goal=1;swimLevel.anchor=0;swimLevel.scanTick=999;
 for(int tick=1;tick<=7;++tick){_botRayBudget=40;afterLevel=BotSupplyTick(&player,0,tick,1000);player.en_plViewpoint.pl_OrientationAngle(2)+=float(afterLevel.pitch_delta);}
 check(afterLevel.forward>0&&near(player.en_plViewpoint.pl_OrientationAngle(2),0),"swim leveling continues through native minus thirty degree threshold until level");
 setup(2);player.m_pstState=PST_DIVE;player.en_plViewpoint.pl_OrientationAngle(2)=60;auto& deferredLevel=BotSupplyState(0);
 deferredLevel.goal=1;deferredLevel.anchor=0;deferredLevel.scanTick=999;
 for(int tick=1;tick<=60;++tick){_botRayBudget=40;afterLevel=BotSupplyTick(&player,0,tick,1000);}
 check(afterLevel.forward==0&&afterLevel.pitch_delta<0&&deferredLevel.goal==1,"unapplied leveling actions never allow blind forward or mark route unreachable");
 std::printf("native bridge: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
'''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--support-dir", type=Path)
    parser.add_argument("--sanitize", action="store_true")
    parser.add_argument("--sdk-player",type=Path,help="pinned Engine107 SDK Sources/EntitiesMP/Player.es button contract")
    args = parser.parse_args()
    use_mask=1<<5 # Pinned SDK fallback for portable fixtures.
    if args.sdk_player:
        native=args.sdk_player.read_text()
        def mask(name):
            match=re.search(r"^#define\s+"+name+r"\s+\(1L\s*<<\s*(\d+)\)",native,re.M)
            if not match:raise ValueError("SDK button declaration missing: "+name)
            return 1<<int(match[1])
        use_mask=mask("PLACT_USE")
        assert use_mask!=mask("PLACT_SNIPER_USE")
        print("SDK action contract",use_mask,mask("PLACT_SNIPER_USE"),hashlib.sha256(args.sdk_player.read_bytes()).hexdigest(),flush=True)
        sdk=args.sdk_player.resolve().parents[1]/"Includes"/"Engine107"/"Engine"
        brush=(sdk/"Brushes"/"Brush.h").read_text()
        def polygon_mask(name):
            match=re.search(r"^#define\s+"+name+r"\s+\(1UL\s*<<\s*(\d+)\)",brush,re.M)
            if not match:raise ValueError("SDK polygon declaration missing: "+name)
            return 1<<int(match[1])
        ray_header=sdk/"World"/"WorldRayCasting.h"
        kinds=re.search(r"enum TestType\s*\{(.*?)\};",ray_header.read_text(),re.S)
        if not kinds:raise ValueError("SDK ray model enumeration missing")
        model_types=re.findall(r"\bTT_[A-Z]+\b",kinds[1])
        assert polygon_mask("BPOF_PASSABLE")==2048 and polygon_mask("BPOF_SHOOTTHRU")==16
        assert model_types.index("TT_NONE")==0 and model_types.index("TT_COLLISIONBOX")==2
        print("SDK107 physical ray contract PASSABLE=2048 SHOOTTHRU=16 COLLISIONBOX=2",hashlib.sha256(ray_header.read_bytes()).hexdigest(),flush=True)
    here = Path(__file__).resolve().parent
    support = args.support_dir or here
    source = (here / "BotSupplyNative.h").read_text()
    # Keep actual function bodies; remove only the platform loader and includes.
    start = source.index("static void BotSupplyUpdateNavigation(")
    end = source.index("static botcore::CecilFrame BotCecilBodyFrame(", start)
    source = source[:start] + source[end:]
    source = "\n".join(line for line in source.splitlines() if not line.startswith("#"))
    driver=(here / "BotDriver.cpp").read_text()
    choice=re.search(r'if\((ready&&[\s\S]*?)\)\{\s*bs\.bs_aHeading=player->m_aLastRotation',driver)
    if not choice:raise ValueError("actual Driver supply arbitration missing")
    ownership="\nstatic bool bridgeDriverOwns(bool ready,const SCecilMove& supply,CPlayer* player,bool targetVisible){return "+choice[1]+";}\n"
    with tempfile.TemporaryDirectory(prefix="cecil-bridge-") as temp:
        cpp, exe = Path(temp) / "bridge.cpp", Path(temp) / "bridge"
        items_source = (support / "BotCecilItems.h").read_text()
        helper_start = items_source.index("inline bool BotCecilIsClass(")
        helper_end = items_source.index("inline uint32_t BotCecilAmmoNeed", helper_start)
        cpp.write_text("#define EXPECTED_NATIVE_USE "+str(use_mask)+"u\n"+STUBS + items_source[helper_start:helper_end] + source + ownership + TESTS)
        cmd = ["g++", "-std=c++14", "-O1", "-g", "-Wall", "-Wextra", "-Wno-unused-function",
               "-I", str(here), "-I", str(support), str(cpp), "-o", str(exe)]
        if args.sanitize:
            cmd += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        subprocess.run(cmd, check=True)
        subprocess.run([str(exe)], check=True)

if __name__ == "__main__":
    main()
