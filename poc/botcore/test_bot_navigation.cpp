#include <cstdio>
#if !__has_include("bot_navigation.h")
int main() { std::puts("FAIL: obstacle recovery policy is missing"); return 1; }
#else
#include "bot_navigation.h"
#include <limits>
using namespace botcore;
static int failures=0;
#define CHECK(c,m) do { if (!(c)) { std::printf("FAIL: %s at %d\n",m,__LINE__); ++failures; } } while(0)
int main() {
  NavigationInput in{0,0,0,4.5,1,3,3,3,true,false,1};
  ObstacleRecovery nav;
  NavigationDecision d=nav.Update(in);
  CHECK(!d.active && !d.overrideInput,"clear direction leaves existing action intact");
  in.front=0.4; in.right=0.5;
  d=nav.Update(in);
  CHECK(d.began && d.active && d.reason==NavigationReason::Blocked,"short native forward ray starts recovery");
  CHECK(d.forward==0 && d.yawDelta==4.5,"turn in place bounded toward clear left side");
  in.yaw=90; in.front=3;
  d=nav.Update(in);
  CHECK(d.phase==NavigationPhase::Advance && d.forward==1,"aligned escape heading advances");
  for(int i=0;i<45;++i) { in.z-=0.4; d=nav.Update(in); }
  CHECK(!d.active,"escape attempt ends after a bounded advance");
  nav.Reset(); in={0,0,0,4.5,1,3,3,3,true,false,-1};
  for(int i=0;i<39;++i) { d=nav.Update(in); CHECK(!d.active,"stuck detector waits for full window"); }
  d=nav.Update(in);
  CHECK(d.began && d.reason==NavigationReason::Stuck && d.yawDelta<0,"existing stuck detector and per-slot tie direction");
  in.forward=0; // aiming pause does not cancel an already selected escape
  in.yaw=-45; d=nav.Update(in);
  CHECK(d.active && d.yawDelta<0,"aim pause during recovery does not restart or cancel the turn");
  in.holdPosition=true; d=nav.Update(in);
  CHECK(!d.active && !d.overrideInput,"intentional close-range hold cancels recovery without altering aim");
  nav.Reset(); in={0,0,0,4.5,1,3,3,3,true,false,1};
  for(int i=0;i<80;++i) { in.z-=0.2; d=nav.Update(in); CHECK(!d.active,"real progress is not stuck"); }
  nav.Reset(); in.forward=0; in.front=0.1;
  for(int i=0;i<80;++i) { d=nav.Update(in); CHECK(!d.active,"intentional no movement never starts avoidance"); }
  in.forward=1; in.front=0.2; in.left=0.2; in.right=0.3; in.yaw=170;
  d=nav.Update(in);
  CHECK(d.active && d.yawDelta==-4.5,"blocked corner turns back via shortest bounded angle");
  in.alive=false; d=nav.Update(in);
  CHECK(!d.active && d.forward==0,"death resets recovery");
  in.alive=true; in.holdPosition=false; in.front=3; in.left=3; in.right=3; in.yaw=0;
  d=nav.Update(in);
  CHECK(!d.active,"respawn has no stale escape heading");
  in.x=std::numeric_limits<double>::quiet_NaN(); d=nav.Update(in);
  CHECK(d.overrideInput && d.forward==0 && d.yawDelta==0,"malformed movement snapshot fails closed");
  in.x=0; in.front=0.2; in.left=3; in.right=0.2; in.turnLimit=0;
  d=nav.Update(in);
  CHECK(d.overrideInput && d.forward==0 && !d.active,"zero turn speed stops at obstacle without infinite turning");
  nav.Reset(); in.turnLimit=4.5; d=nav.Update(in);
  in.yaw=90; in.front=3; d=nav.Update(in);
  in.front=0.2; in.left=0.1; in.right=3; d=nav.Update(in);
  CHECK(d.began && d.phase==NavigationPhase::Turn && d.forward==0 && d.yawDelta<0,"new obstacle aborts advance and chooses fresh direction");
  nav.Reset(); in={0,0,0,4.5,1,0.2,3,0.2,true,false,1};
  d=nav.Update(in); in.yaw=90; in.front=3; in.moveScale=0.2; d=nav.Update(in);
  CHECK(d.forward==0.2,"recovery respects configured movement speed");
  in.moveScale=0; d=nav.Update(in);
  CHECK(!d.active && d.forward==0,"zero movement scale cancels recovery");
  nav.Reset(); in={0,0,0,4.5,1,0.2,3,0.2,true,false,1}; d=nav.Update(in);
  in.x=100; in.front=3; d=nav.Update(in);
  CHECK(!d.active,"teleport discards stale recovery heading");
  nav.Reset(); in={0,0,0,4.5,1,0.2,3,0.2,true,false,1}; d=nav.Update(in);
  in.yaw=90; d=nav.Update(in);
  CHECK(d.began && d.phase==NavigationPhase::Turn && d.forward==0,
        "aligned turn still blocked must replan without a forward tick");
  nav.Reset(); in={0,0,0,4.5,1,0.2,3,0.2,true,false,1};
  int ended=0;
  for(int i=0;i<260;++i) {
    d=nav.Update(in); in.yaw+=d.yawDelta;
    if(d.finished && !d.active) { ended=i+1; break; }
  }
  CHECK(ended>0 && ended<=240,"repeated obstacles have a total recovery budget");
  if(ended) for(int i=0;i<20;++i) {
    d=nav.Update(in); CHECK(!d.active,"exhausted recovery has a retry cooldown");
  }
  std::printf("OBSTACLE RECOVERY %s (%d failures)\n",failures?"FAIL":"PASS",failures);
  return failures?1:0;
}
#endif
