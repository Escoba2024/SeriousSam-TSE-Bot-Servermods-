// Reactive obstacle recovery, not a navmesh or global path planner.
#ifndef BOT_NAVIGATION_H
#define BOT_NAVIGATION_H
#include "botcore.h"
#include "botcore_ai.h"
namespace botcore {
enum class NavigationPhase { Idle=0, Turn=1, Advance=2 };
enum class NavigationReason { None=0, Blocked=1, Stuck=2 };
struct NavigationInput {
  double x,z,yaw,turnLimit,forward,front,left,right;
  bool alive,holdPosition;
  int preferredDirection;
  double moveScale=1.0;
};
struct NavigationDecision {
  bool overrideInput,active,began,finished;
  NavigationPhase phase;
  NavigationReason reason;
  double yawDelta,forward;
};
class ObstacleRecovery {
 public:
  ObstacleRecovery() : stuck_(40,1.0) { Reset(); }
  void Reset() {
    stuck_.Reset(); phase_=NavigationPhase::Idle; reason_=NavigationReason::None;
    desiredYaw_=0; remaining_=0; attemptRemaining_=0; cooldown_=0;
    havePosition_=false;
  }
  NavigationDecision Update(const NavigationInput& in) {
    NavigationDecision d={false,false,false,false,NavigationPhase::Idle,
                          NavigationReason::None,0,0};
    if (!std::isfinite(in.x) || !std::isfinite(in.z) || !std::isfinite(in.yaw) ||
        !std::isfinite(in.turnLimit) || in.turnLimit<0 || !std::isfinite(in.forward) ||
        !std::isfinite(in.front) || !std::isfinite(in.left) || !std::isfinite(in.right) ||
        in.front<0 || in.left<0 || in.right<0 || !std::isfinite(in.moveScale)) {
      Reset(); d.overrideInput=true; return d;
    }
    if (!in.alive || in.holdPosition || in.moveScale<=0) { Reset(); return d; }
    // Teleports/map changes are not progress along a previous recovery heading.
    if (havePosition_ && (in.x-lastX_)*(in.x-lastX_)+(in.z-lastZ_)*(in.z-lastZ_)>64.0)
      Reset();
    havePosition_=true; lastX_=in.x; lastZ_=in.z;
    if (cooldown_>0) { --cooldown_; return d; }
    const double limit=in.turnLimit>9.0?9.0:in.turnLimit;
    const bool moving=in.forward>0;
    const bool blocked=in.front<1.2;
    bool trigger=false;
    NavigationReason cause=NavigationReason::None;
    if (phase_==NavigationPhase::Idle) {
      const bool stuck=stuck_.Update(in.x,in.z,moving);
      if (moving && (blocked || stuck)) {
        trigger=true; cause=blocked?NavigationReason::Blocked:NavigationReason::Stuck;
      }
    } else if (blocked && (phase_==NavigationPhase::Advance ||
               std::fabs(TestTurnDelta(in.yaw,desiredYaw_,180.0))<3.0)) {
      trigger=true; cause=NavigationReason::Blocked;
    }
    if (trigger) {
      if (limit==0) { Reset(); d.overrideInput=true; return d; }
      if (phase_==NavigationPhase::Idle) attemptRemaining_=240;
      int direction=in.left>in.right?1:in.right>in.left?-1:
                    (in.preferredDirection<0?-1:1);
      const double angle=(in.left<1.2 && in.right<1.2)?180.0:90.0;
      desiredYaw_=in.yaw+direction*angle;
      phase_=NavigationPhase::Turn; reason_=cause; remaining_=160;
      stuck_.Reset(); d.began=true;
    }
    if (phase_==NavigationPhase::Idle) return d;
    if (limit==0) { Reset(); d.overrideInput=true; return d; }
    d.overrideInput=true; d.active=true; d.reason=reason_;
    // Replanning at another wall must not extend the overall attempt forever.
    if (--attemptRemaining_<=0) {
      d.phase=phase_; Reset(); cooldown_=40;
      d.active=false; d.finished=true; return d;
    }
    if (phase_==NavigationPhase::Turn) {
      const double error=TestTurnDelta(in.yaw,desiredYaw_,180.0);
      if (std::fabs(error)<3.0) {
        phase_=NavigationPhase::Advance; remaining_=40;
      } else {
        d.phase=phase_; d.yawDelta=TestTurnDelta(in.yaw,desiredYaw_,limit);
        if (--remaining_<=0) { Reset(); cooldown_=40; d.active=false; d.finished=true; }
        return d;
      }
    }
    d.phase=NavigationPhase::Advance;
    d.yawDelta=TestTurnDelta(in.yaw,desiredYaw_,limit);
    d.forward=in.moveScale>1.0?1.0:in.moveScale;
    if (--remaining_<=0) { Reset(); d.finished=true; }
    return d;
  }
 private:
  StuckDetector stuck_;
  NavigationPhase phase_;
  NavigationReason reason_;
  double desiredYaw_;
  int remaining_;
  int attemptRemaining_,cooldown_;
  bool havePosition_;
  double lastX_,lastZ_;
};
}
#endif
