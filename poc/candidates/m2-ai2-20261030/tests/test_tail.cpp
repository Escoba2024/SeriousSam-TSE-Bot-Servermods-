#include "bot_human.h"
#include "bot_navigation.h"
#include <cstdio>
#include <vector>
using namespace botcore;
using FLOAT=float;using INDEX=int;using BOOL=int;
#define FALSE 0
#define TRUE 1
static int failed=0,checks=0;
#define CHECK(c) do{++checks;if(!(c)){++failed;std::printf("FAIL %d %s\n",__LINE__,#c);}}while(0)
static FLOAT Clamp(FLOAT v,FLOAT lo,FLOAT hi){return v<lo?lo:(v>hi?hi:v);}
struct Player { FLOAT m_aLastRotation(int)const{return 0;} };
struct State {FLOAT bs_aHeading=0,bs_aPitch=0;};
static std::vector<FLOAT> bearings;
static FLOAT clearance=3;
static FLOAT BotObstacleDistance(Player*,FLOAT yaw){bearings.push_back(yaw);return clearance;}
static bool hold(FLOAT moveFactor,FLOAT humanStrafe,FLOAT distance){
  BOOL bot_bHumanAI=TRUE,combatHold=FALSE;FLOAT bot_fStrafeScale=.5f;int combatWeapon=6;
#include "hold.inc"
  return combatHold;
}
static void recovery(const NavigationDecision& navigation,FLOAT& moveFactor,FLOAT& humanStrafe,BOOL& testAimReady){
  State bs;Player actor;Player* player=&actor;
#include "recovery.inc"
  (void)bs;(void)humanStrafe;
}
static void motion(FLOAT& moveFactor,FLOAT& humanStrafe,FLOAT yaw,FLOAT requestedYaw){
  Player actor;Player* player=&actor;BOOL bot_bObstacleAvoidance=TRUE;FLOAT bot_fStrafeScale=.5f;
  const FLOAT lateral=Clamp(humanStrafe*bot_fStrafeScale,-1.0f,1.0f);
#include "clearance.inc"
  (void)moveFactor;(void)player;(void)bot_bObstacleAvoidance;(void)yaw;(void)requestedYaw;(void)lateral;(void)BotObstacleDistance;
}
int main(){
  CHECK(!hold(-.85f,.6f,6));CHECK(!hold(.8f,0,6));CHECK(!hold(0,.6f,6));CHECK(hold(0,0,12));
  for(auto phase:{NavigationPhase::Turn,NavigationPhase::Advance}){
    NavigationDecision n{};n.overrideInput=true;n.forward=phase==NavigationPhase::Turn?0:.8;n.yawDelta=9;
    FLOAT forward=-.85f,strafe=.8f;BOOL ready=TRUE;recovery(n,forward,strafe,ready);
    CHECK(forward==static_cast<FLOAT>(n.forward));CHECK(strafe==0);CHECK(!ready);
  }
  for(FLOAT yaw:{0.f,90.f,-90.f})for(FLOAT forward:{-.85f,0.f}){
    FLOAT f=forward,s=.8;clearance=.2;bearings.clear();motion(f,s,yaw,yaw+5);
    CHECK(f==0&&s==0);CHECK(bearings.size()==2);
  }
  FLOAT f=-.85,s=0;clearance=3;bearings.clear();motion(f,s,0,0);
  CHECK(f==-.85f&&s==0);CHECK(bearings.size()==1);CHECK(!bearings.empty() && std::fabs(std::fabs(bearings[0])-180)<.01);
  f=0;s=1;bearings.clear();motion(f,s,0,0);CHECK(bearings.size()==1);CHECK(!bearings.empty() && std::fabs(bearings[0]+90)<.01);
  f=.8;s=0;clearance=.2;bearings.clear();motion(f,s,0,0);CHECK(f==.8f);CHECK(bearings.empty());
  std::printf("M2 ADAPTER TAIL: %d checks, %d failures\n",checks,failed);return failed?1:0;
}
