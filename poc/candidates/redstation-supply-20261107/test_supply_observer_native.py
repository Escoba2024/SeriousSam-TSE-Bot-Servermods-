#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the real native bridge and final diagnostic hook; no Retail runtime proof.

The existing harness supplies only SDK-shaped world/physics stubs. These cases
execute production BotSupplyTick, SafeMotion and the Driver's existing final hook.
"""
import test_cecil_native_bridge as bridge

if "int main(){" not in bridge.TESTS:
    raise ValueError("existing bridge main boundary changed")
bridge.TESTS = bridge.TESTS.replace("int main(){", "int legacyBridgeMain(){", 1) + r'''
static unsigned supplyRows(const std::string& text,const char* needle="[CecilSupplyDiagWindow]"){
 unsigned n=0;size_t at=0;while((at=text.find(needle,at))!=std::string::npos){++n;at+=std::strlen(needle);}return n;
}
static bool supplyVector(const std::string& text,const char* key,const FLOAT3D& wanted){
 const auto at=text.find(key);if(at==std::string::npos)return false;
 double a,b,c;if(std::sscanf(text.c_str()+at+std::strlen(key),"%lf,%lf,%lf)",&a,&b,&c)!=3)return false;
 return std::fabs(a-wanted(1))<1e-6&&std::fabs(b-wanted(2))<1e-6&&std::fabs(c-wanted(3))<1e-6;
}
static void supplyObserverFixture(int kind,long map,int slot=0,bool diagnostics=true){
 bouncer009Fixture();timer.TickQuantum=.05;bot_bDiagnostics=diagnostics;BotCecilSettings().bAvoidPits=0;
 auto& g=BotSupplyGraph();
 // Deliberately synthetic route coordinates; only the authored slot classes
 // and the already pinned loader binding identify which decision is observed.
 g.points[68].x=0;g.points[68].y=0;g.points[68].z=0;g.points[68].radius=1;g.points[68].links={6};
 g.points[6].x=0;g.points[6].y=0;g.points[6].z=-10;g.points[6].radius=1;g.points[6].links={34};
 g.points[87].x=0;g.points[87].y=0;g.points[87].z=-10;g.points[87].radius=1;g.points[87].flags=2;g.points[87].links={34};
 auto& s=BotSupplyState(slot);if(slot)s=BotSupplyState(0);
 s.navigator.Reset();s.goal=34;s.goalEntity=243;s.goalKind=botcore::CecilItemKind::Weapon;
 s.goalSince=0;s.goalDeadline=1000;s.mappedWeaponGoal=true;s.scanTick=99999;s.hop=-1;
 s.anchor=kind?87:68;s.playable=true;s.owned=3;s.entity=567+slot;s.generation=5;
 player.en_ulID=s.entity;player.pl.pl_PositionVector=FLOAT3D(0,0,0);
 player.en_vCurrentTranslationAbsolute=FLOAT3D(1,2,3);player.m_aLastRotation=FLOAT3D(13,17,0);
 player.en_plViewpoint.pl_OrientationAngle=FLOAT3D(0,19,0);
 _botSupplyMapSerial=map;BotCecilBouncerPublish(true,"Levels\\LevelsMP\\Deathmatch\\RedStation.wld",0xff3776e0u,0xe4571656u,map);
 supplyDiagLines=0;supplyDiagText.clear();
}
struct SupplyObservedAction {SCecilMove move;FLOAT3D action,rotation;int safety,rays,lookups;unsigned rng;};
static SupplyObservedAction supplyObserverAction(int tick,int slot=0){
 auto& s=BotSupplyState(slot);_botRayBudget=40;
 const auto move=BotSupplyTick(&player,slot,tick,1000);
 double f=move.forward,st=move.strafe,up=move.up;
 const double now=tick*timer.TickQuantum;
 const int safety=BotCecilSafeMotion(&player,s,now,f,st,up,move.yaw_delta,.5,true);
 const FLOAT3D action(float(st*5),float(up*11),float(-f*10)),rotation(float(13+move.yaw_delta),float(17+move.pitch_delta),0);
 BotCecilApproachFinal(&player,s,slot,tick,now,true,safety,false,action,rotation,0);
 return {move,action,rotation,safety,rayCount,worldLookups,s.rng};
}
static bool sameSupplyObservedAction(const SupplyObservedAction& a,const SupplyObservedAction& b){
 return a.move.active==b.move.active&&a.move.ownsMovement==b.move.ownsMovement&&
  a.move.itemGoal==b.move.itemGoal&&a.move.urgent==b.move.urgent&&a.move.flags==b.move.flags&&
  a.move.followGoal==b.move.followGoal&&a.move.useControl==b.move.useControl&&a.move.flightGoal==b.move.flightGoal&&
  a.move.itemKind==b.move.itemKind&&a.move.buttons==b.move.buttons&&
  a.move.forward==b.move.forward&&a.move.strafe==b.move.strafe&&a.move.up==b.move.up&&
  a.move.yaw_delta==b.move.yaw_delta&&a.move.pitch_delta==b.move.pitch_delta&&
  a.safety==b.safety&&a.rays==b.rays&&a.lookups==b.lookups&&a.rng==b.rng&&
  a.action(1)==b.action(1)&&a.action(2)==b.action(2)&&a.action(3)==b.action(3)&&
  a.rotation(1)==b.rotation(1)&&a.rotation(2)==b.rotation(2)&&a.rotation(3)==b.rotation(3);
}
static void supplyObserverActivation(){
 for(int kind=0;kind<2;++kind){
  supplyObserverFixture(kind,100+kind*2,0,false);const auto off=supplyObserverAction(20);
  check(supplyRows(supplyDiagText)==0,"supply window remains silent without the existing opt-in");
  supplyObserverFixture(kind,101+kind*2);const auto on=supplyObserverAction(20);
  check(supplyRows(supplyDiagText)==1,kind?
   "actual source87 acquisition action emits exactly one passive receipt":
   "actual north68->6 action emits exactly one passive receipt");
  check(sameSupplyObservedAction(off,on),"observer opt-in preserves actual planner safety action queries and RNG");
 }
}

static void supplyObserverPayload(){
 supplyObserverFixture(0,200);supplyObserverAction(20);
 check(supplyDiagText.find("class=north68_6")!=std::string::npos&&
  supplyDiagText.find("owned=3 usable=3")!=std::string::npos&&supplyDiagText.find("source=68 out_hop=6")!=std::string::npos,
  "receipt identifies the actual unarmed directed route and ownership snapshot");
 check(supplyVector(supplyDiagText,"action=(",FLOAT3D(0,0,-10))&&
  supplyVector(supplyDiagText,"rotation=(",FLOAT3D(13,17,0))&&
  supplyVector(supplyDiagText,"velocity=(",FLOAT3D(1,2,3)),
  "receipt retains final action and current native velocity without synthesizing a new decision");
 supplyObserverFixture(1,201);supplyObserverAction(20);
 check(supplyDiagText.find("class=source87")!=std::string::npos&&supplyDiagText.find("source=-1 out_hop=87")!=std::string::npos,
  "receipt distinguishes acquisition approach from a committed edge to87");
}
static void supplyObserverAdmission(){
 for(int bad=0;bad<9;++bad){
  supplyObserverFixture(bad==1?1:0,210+bad);auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();
  if(bad==0){g.points[68].links={7};g.points[7].links={34};}
  if(bad==1){s.anchor=83;g.points[83].x=g.points[83].y=g.points[83].z=0;g.points[83].links={87};}
  if(bad==2)player.w.m_iAvailableWeapons=player.w.usable=67;
  if(bad==3){player.w.m_iAvailableWeapons=67;player.w.usable=3;}
  if(bad==4)s.mappedWeaponGoal=false;
  if(bad==5)_botSupplyMapReady=0;
  if(bad==6)BotCecilBouncerBindingSerial()=-1;
  if(bad==7){player.health=0;}
  if(bad==8)bot_bEnabled=false;
  supplyObserverAction(20);
  check(supplyRows(supplyDiagText)==0,"unrelated route owned gun nonmapped goal invalid map and dead player cannot open a supply window");
 }
}
static void supplyObserverLimits(){
 for(int kind=0;kind<2;++kind){
  const long map=230+kind;supplyObserverFixture(kind,map);
  for(int tick=20;tick<260;++tick)supplyObserverAction(tick);
  check(supplyRows(supplyDiagText)==200,"one class emits at most200 distinct actual action receipts");
  supplyObserverFixture(kind,map);for(int tick=300;tick<320;++tick)supplyObserverAction(tick);
  check(supplyRows(supplyDiagText)==0,"ClearGoal or complete supply state replacement cannot renew a spent map budget");
  bot_bDiagnostics=false;supplyObserverAction(321);bot_bDiagnostics=true;supplyObserverAction(322);
  check(supplyRows(supplyDiagText)==0,"opt-in toggling cannot reopen the same map budget");
 }
 supplyObserverFixture(0,240);supplyObserverAction(20);supplyObserverAction(200);
 check(supplyRows(supplyDiagText)==2,"sparse fresh actions within the fixed window remain distinguishable samples");
 supplyObserverAction(220);supplyObserverAction(21);
 check(supplyRows(supplyDiagText)==2,"the10s deadline rejects an otherwise valid late action and a later clock rewind");
}
static void supplyObserverFreshFinal(){
 for(int bad=0;bad<10;++bad){
  supplyObserverFixture(0,250+bad);auto& s=BotSupplyState(0);_botRayBudget=40;BotSupplyTick(&player,0,20,1000);
  CPlayer copy=player;copy.worldOverride=player.GetWorld();CPlayer* observed=&player;
  int slot=0,tick=20;double now=1;CWorld otherWorld=*player.GetWorld();
  FLOAT3D action(1,2,3),rotation(4,5,6);
  if(bad==0)tick=21;
  if(bad==1)now=1.05;
  if(bad==2){s.generation+=1;}
  if(bad==3){player.en_ulID+=1;}
  if(bad==4){observed=&copy;}
  if(bad==5){player.hasWorld=false;}
  if(bad==6){_botSupplyMapReady=0;}
  if(bad==7){player.worldOverride=&otherWorld;}
  if(bad==8)action(2)=std::numeric_limits<float>::infinity();
  if(bad==9)rotation(1)=std::numeric_limits<float>::quiet_NaN();
  BotCecilApproachFinal(observed,s,slot,tick,now,true,1,false,action,rotation,7);
  check(supplyRows(supplyDiagText)==0,"final receipt rejects missing tick time life entity pointer world or ready identity");
 }
 supplyObserverFixture(0,260);supplyObserverAction(20);auto& s=BotSupplyState(0);
 BotCecilApproachFinal(&player,s,0,20,1,true,1,false,FLOAT3D(),FLOAT3D(),0);
 check(supplyRows(supplyDiagText)==1,"duplicate final callbacks cannot duplicate an actual action receipt");
 supplyObserverFixture(0,261);_botRayBudget=40;BotSupplyTick(&player,0,20,1000);
 BotCecilApproachFinal(&player,BotSupplyState(0),4,20,1,true,1,false,FLOAT3D(),FLOAT3D(),0);
 check(supplyRows(supplyDiagText)==0,"an invalid local slot cannot alias a different player's observer budget");
}
static void supplyObserverLifeAndMap(){
 supplyObserverFixture(0,270);supplyObserverAction(20);player.health=0;supplyObserverAction(21);
 player.health=100;auto& s=BotSupplyState(0);s.playable=true;s.generation+=1;s.navigator.Reset();s.anchor=68;s.goal=34;
 s.goalEntity=243;s.goalKind=botcore::CecilItemKind::Weapon;s.mappedWeaponGoal=true;s.goalSince=0;s.goalDeadline=1000;
 s.scanTick=99999;supplyObserverAction(22);
 check(supplyRows(supplyDiagText)==1,"a new life never renews or continues the previous life observation");
 supplyObserverFixture(0,271);supplyObserverAction(20);
 check(supplyRows(supplyDiagText)==1,"a freshly published new map epoch gets its own bounded observation");
 supplyObserverFixture(0,270);supplyObserverAction(20);
 check(supplyRows(supplyDiagText)==0,"a stale map serial cannot reopen an older observation epoch");
 supplyObserverFixture(0,280);supplyObserverAction(20);auto& t=BotSupplyState(0);BotSupplyReset(0);
 t.playable=true;t.entity=player.en_ulID;t.anchor=68;t.goal=34;t.goalEntity=243;
 t.goalKind=botcore::CecilItemKind::Weapon;t.mappedWeaponGoal=true;t.goalDeadline=1000;t.scanTick=99999;
 supplyObserverAction(21);
 check(supplyRows(supplyDiagText)==1,"the public supply Reset helper cannot grant a fresh same-map budget");
}
static void supplyObserverIndependentClassesAndSlots(){
 unsigned total=0;
 for(int slot=0;slot<4;++slot)for(int kind=0;kind<2;++kind){
  supplyObserverFixture(kind,300,slot);for(int tick=20;tick<250;++tick)supplyObserverAction(tick,slot);
  const unsigned rows=supplyRows(supplyDiagText);total+=rows;
  check(rows==200,"each actual class and local slot has one independent capped map budget");
 }
 check(total==1600,"a four-player map epoch cannot exceed1600 new supply action lines");
}
static void supplyObserverRouteExit(){
 supplyObserverFixture(0,310);supplyObserverAction(20);auto& g=BotSupplyGraph();
 player.pl.pl_PositionVector=FLOAT3D(g.points[6].x,g.points[6].y,g.points[6].z);
 supplyObserverAction(21);
 check(supplyRows(supplyDiagText)==2&&supplyDiagText.find("prev_source=68 prev_hop=6 reached=1")!=std::string::npos,
  "the genuine reached transition is retained in its final action receipt");
 supplyObserverAction(22);
 check(supplyRows(supplyDiagText)==2,"unrelated successor movement does not extend a closed class window");
}

static void supplyObserverWorldAndGoal(){
 supplyObserverFixture(0,320);supplyObserverAction(20);
 CWorld other=*player.GetWorld();player.worldOverride=&other;supplyObserverAction(21);
 player.worldOverride=nullptr;supplyObserverAction(22);
 check(supplyRows(supplyDiagText)==1,"a changed world at unchanged map serial closes the old window without rebinding");
 for(int kind=0;kind<2;++kind){
  supplyObserverFixture(kind,330+kind);supplyObserverAction(20);
  auto& s=BotSupplyState(0);auto& g=BotSupplyGraph();s.ClearGoal();
  g.points[35].x=2;g.points[35].y=0;g.points[35].z=-20;g.points[35].important_entity=267;
  g.points[kind?87:6].links={35};addItem(267,2,-20,botcore::CecilItemKind::Weapon);
  s.goal=35;s.goalEntity=267;s.goalKind=botcore::CecilItemKind::Weapon;s.mappedWeaponGoal=true;
  s.goalSince=5;s.goalDeadline=1000;s.anchor=kind?87:68;s.scanTick=99999;
  supplyObserverAction(100);supplyObserverAction(219);supplyObserverAction(220);
  check(supplyRows(supplyDiagText)==3&&supplyDiagText.find("goal_entity=267 goal=35")!=std::string::npos,
   "a real replacement goal on the same approach retains its original quota and10s deadline");
 }
 supplyObserverFixture(0,340);_botRayBudget=40;BotSupplyTick(&player,0,20,1000);auto& s=BotSupplyState(0);
 s.ClearGoal();BotCecilApproachFinal(&player,s,0,20,1,false,0,false,FLOAT3D(),FLOAT3D(),0);
 check(supplyRows(supplyDiagText)==1&&supplyDiagText.find("final_goal_entity=0 final_goal=-1")!=std::string::npos&&
  supplyDiagText.find("ending=1")!=std::string::npos,
  "a goal invalidated after navigation retains the actual neutral final action with its changed context");
 supplyObserverFixture(0,350);supplyObserverAction(20);_botRayBudget=40;BotSupplyTick(&player,0,219,1000);
 BotCecilApproachFinal(&player,BotSupplyState(0),0,219,11,true,1,false,FLOAT3D(0,0,-10),FLOAT3D(),0);
 check(supplyRows(supplyDiagText)==1,"a final callback after the fixed deadline cannot publish its previously valid capture");
}
static void supplyObserverProbeAndFraming(){
 supplyObserverFixture(0,360);wallMode=2;obstruction.en_ulID=777;
 const auto blocked=supplyObserverAction(20);const auto& p=BotSupplyState(0).probe;
 check(supplyRows(supplyDiagText)==1&&supplyDiagText.find("ending=0\n")!=std::string::npos,
  "one accepted observation is a complete newline-terminated existing logger record");
 check(supplyDiagText.find("probe_rays=(")!=std::string::npos&&supplyDiagText.find("probe_hit=")!=std::string::npos&&
  supplyVector(supplyDiagText,"probe_from=(",FLOAT3D(p.from[0],p.from[1],p.from[2]))&&
  supplyVector(supplyDiagText,"probe_to=(",FLOAT3D(p.to[0],p.to[1],p.to[2]))&&
  supplyVector(supplyDiagText,"probe_normal=(",FLOAT3D(p.normal[0],p.normal[1],p.normal[2])),
  "the existing safety decision's ray endpoints and contact outcome survive in the passive receipt");
 check(blocked.safety==0&&blocked.action(1)==0&&blocked.action(2)==0&&blocked.action(3)==0,
  "observation never overrides a neutral native safety decision");
 supplyObserverFixture(0,361);_botRayBudget=40;BotSupplyTick(&player,0,20,1000);
 const float f=-std::numeric_limits<float>::max();const double d=-std::numeric_limits<double>::max();
 player.pl.pl_PositionVector=player.pl.pl_OrientationAngle=player.en_plViewpoint.pl_OrientationAngle=
  player.en_vCurrentTranslationAbsolute=player.en_vGravityDir=player.m_aLastRotation=FLOAT3D(f,f,f);
 auto& s=BotSupplyState(0);s.probe.inputForward=s.probe.inputStrafe=s.probe.inputUp=s.probe.finalYaw=s.probe.support=d;
 for(int i=0;i<3;++i)s.probe.from[i]=s.probe.to[i]=s.probe.normal[i]=d;
 BotCecilApproachFinal(&player,s,0,20,1,true,1,false,FLOAT3D(f,f,f),FLOAT3D(f,f,f),0);
 check(supplyRows(supplyDiagText)==1&&supplyDiagText.size()<2048&&supplyDiagText.find("ending=0\n")!=std::string::npos,
  "even large finite observed fields cannot truncate the one-line receipt in the existing2048-byte logger");
}
static void supplyObserverClockRewind(){
 supplyObserverFixture(0,380);supplyObserverAction(20);supplyObserverAction(100);
 timer.TickQuantum=.03;supplyObserverAction(101);
 check(supplyRows(supplyDiagText)==2,"a newer tick with a backwards capture clock cannot extend the fixed observation interval");
 timer.TickQuantum=.05;supplyObserverAction(102);
 check(supplyRows(supplyDiagText)==2,"restoring the clock cannot reopen the rejected same-map observation");
}
static void supplyObserverSequenceParity(){
 for(int kind=0;kind<2;++kind)for(int blocked=0;blocked<2;++blocked){
  std::vector<SupplyObservedAction> baseline;
  supplyObserverFixture(kind,400+kind*4+blocked*2,0,false);wallMode=blocked?2:0;
  for(int tick=20;tick<260;++tick)baseline.push_back(supplyObserverAction(tick));
  supplyObserverFixture(kind,401+kind*4+blocked*2);wallMode=blocked?2:0;
  bool unchanged=true;for(int tick=20;tick<260;++tick)
   unchanged=unchanged&&sameSupplyObservedAction(baseline[tick-20],supplyObserverAction(tick));
  check(unchanged,"a full active/expired observer sequence preserves all requested movement action safety RNG and query results");
 }
}

int main(){
 checks=failures=0;supplyObserverActivation();supplyObserverPayload();supplyObserverAdmission();
 supplyObserverLimits();supplyObserverFreshFinal();supplyObserverLifeAndMap();supplyObserverIndependentClassesAndSlots();supplyObserverRouteExit();
 supplyObserverWorldAndGoal();supplyObserverProbeAndFraming();supplyObserverClockRewind();supplyObserverSequenceParity();
 std::printf("supply observer actual bridge: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
'''

if __name__ == "__main__":
    bridge.main()
