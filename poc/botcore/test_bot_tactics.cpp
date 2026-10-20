// Portable tactical AI regressions. Full Retail/Wine sync tests are separate.
#include "bot_tactics.h"
#include <cmath>
#include <cstdio>
#include <limits>
using namespace botcore;
static int fails=0;
#define CHECK(x,msg) do { if(!(x)) { std::printf("FAIL: %s @%d\n",msg,__LINE__); ++fails; } } while(0)
int main() {
  CombatInput in={{0,0,0,0,100,true},0,0,4.5,1.0,3u,true,8.0};
  TargetInfo p[]={{1,0,0,-12,100,false},{2,0,0,-14,10,false},
                  {3,0,0,-3,100,true},{4,0,0,-2,0,false}};
  TacticalState state;
  TacticalDecision d=DecideTacticalCombat(p,4,in,state,1,0,1);
  CHECK(d.combat.target==2,"wounded opponent selected when similarly reachable");
  CHECK(d.combat.fireAllowed,"visible aligned target is still fire-eligible");
  CHECK(d.strafeFactor>0 && d.combat.moveFactor==0,"strafe near ideal Colt range");
  TargetInfo p2[]={{1,0,0,-11,100,false},{2,0,0,-15,100,false}};
  d=DecideTacticalCombat(p2,2,in,state,2,0,1);
  CHECK(d.combat.target==2,"target stickiness prevents rapid retarget");
  d=DecideTacticalCombat(p2,2,in,state,80,0,1);
  CHECK(d.strafeFactor<0,"direction alternates by period");
  TacticalState sibling;
  TacticalDecision siblingD=DecideTacticalCombat(p2,2,in,sibling,1,1,1);
  CHECK(siblingD.strafeFactor<0 && state.target==2,"bot slots have separate movement and state");
  d=DecideTacticalCombat(p2,1,in,state,81,0,1);
  CHECK(d.combat.target==1,"missing target switches immediately");
  d=DecideTacticalCombat(nullptr,0,in,state,82,0,1);
  CHECK(d.combat.target==-1 && d.strafeFactor==0,"no phantom target or strafing");
  TargetInfo local[]={{3,0,0,-7,100,true}};
  d=DecideTacticalCombat(local,1,in,state,83,0,1);
  CHECK(d.combat.target==-1,"local sibling not attacked");
  in.self.health=35;
  TargetInfo near[]={{1,0,0,-4,100,false}};
  d=DecideTacticalCombat(near,1,in,state,84,0,1);
  CHECK(d.combat.moveFactor<0,"low-health close-range retreat");
  in.self.health=100;
  d=DecideTacticalCombat(near,1,in,state,85,0,1);
  CHECK(d.combat.moveFactor==0,"healthy player does not reverse blindly");
  TargetInfo far[]={{1,0,0,-45,100,false}};
  d=DecideTacticalCombat(far,1,in,state,86,0,1);
  CHECK(d.combat.moveFactor>0,"distant opponent is pursued");
  in.yaw=179;
  d=DecideTacticalCombat(far,1,in,state,87,0,1);
  CHECK(d.combat.moveFactor==0 && d.strafeFactor==0,"no movement facing backwards");
  in.yaw=0;
  in.self.health=0;
  d=DecideTacticalCombat(near,1,in,state,88,0,1);
  CHECK(d.combat.target==-1 && !d.combat.fireAllowed,"dead bot has no combat decision");
  in.self.health=100;
  TargetInfo invalid[]={{5,std::numeric_limits<double>::quiet_NaN(),0,0,100,false}};
  d=DecideTacticalCombat(invalid,1,in,state,89,0,1);
  CHECK(d.combat.target==-1,"reject malformed world snapshots");
  TacticalState reset;
  d=DecideTacticalCombat(near,1,in,reset,1,0,0);
  const double easyStrafe=std::fabs(d.strafeFactor);
  reset.Reset();
  d=DecideTacticalCombat(near,1,in,reset,1,0,2);
  CHECK(std::fabs(d.strafeFactor)>easyStrafe,"hard bot strafes faster than easy bot");
  reset.target=1;
  d=DecideTacticalCombat(p,4,in,reset,0,0,1);
  CHECK(d.combat.target>=0,"state can restart after tick reset");
  std::printf("TACTICAL POLICY %s (%d failures)\n",fails?"FAIL":"PASS",fails);
  return fails?1:0;
}
