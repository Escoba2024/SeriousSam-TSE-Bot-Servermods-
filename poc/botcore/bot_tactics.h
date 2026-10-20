// Tactical client-only policy inspired by CecilBotMod's documented behavior.
// Independent implementation; no world writes, ABI changes, or network protocol changes.
// Reference: DreamyCecil/CecilBotMod @ 953b477 (GPL-2.0).
// All inputs are caller-supplied, visible retail player snapshots.
#ifndef BOT_TACTICS_H
#define BOT_TACTICS_H
#include "bot_combat.h"
#include <cmath>

namespace botcore {

struct TacticalState {
  int target;
  int lastTick;
  TacticalState() : target(-1), lastTick(-1) {}
  void Reset() { target=-1; lastTick=-1; }
};

struct TacticalDecision {
  CombatDecision combat;
  double strafeFactor; // signed normalized lateral movement, [-1,+1]
  double targetDistance;
};

// Difficulty 0=easy, 1=normal, 2=hard; affects movement only.
// Kill decisions still require vanilla ray visibility and native weapon readiness.
inline TacticalDecision DecideTacticalCombat(const TargetInfo* players, int count,
                                              const CombatInput& input,
                                              TacticalState& state, int tick,
                                              int localSlot, int difficulty) {
  TacticalDecision out={{-1,1,0,0,0,false},0.0,0.0};
  if (tick < 0 || (state.lastTick >= 0 && tick < state.lastTick)) state.Reset();
  state.lastTick=tick;
  if (!CombatValidPlayer(input.self) || input.self.health<=0 ||
      !std::isfinite(input.yaw) || !std::isfinite(input.pitch) ||
      !std::isfinite(input.turnLimit) || input.turnLimit<0 ||
      !std::isfinite(input.moveFactor) || input.moveFactor<0 ||
      !std::isfinite(input.stopDistance)) {
    state.target=-1;
    return out;
  }

  // Choose among already visible opponents only. The current target gets a
  // hysteresis bonus to avoid changing opponents every 50-ms network tick.
  int chosen=-1;
  double best=0.0;
  TargetInfo selected={-1,0,0,0,0,false};
  for (int i=0; players!=nullptr && i<count && i<16; ++i) {
    const TargetInfo& p=players[i];
    if (!CombatValidPlayer(p) || p.health<=0 || p.index==input.self.index ||
        (input.skipLocals && p.local)) continue;
    const double dx=p.x-input.self.x, dy=p.y-input.self.y, dz=p.z-input.self.z;
    const double distance=std::sqrt(dx*dx+dy*dy+dz*dz);
    if (!std::isfinite(distance)) continue;
    double hp=p.health<0?0:(p.health>100?100:p.health);
    double score=distance + hp*0.03; // reachable low-health rivals are attractive
    if (p.index==state.target) score*=0.72; // stick until a materially better target
    if (chosen<0 || score<best || (score==best && p.index<chosen)) {
      chosen=p.index; best=score; selected=p;
    }
  }
  state.target=chosen;
  if (chosen<0) return out;

  out.combat=DecideCombat(&selected,1,input);
  const double dx=selected.x-input.self.x;
  const double dy=selected.y-input.self.y;
  const double dz=selected.z-input.self.z;
  const double dist=std::sqrt(dx*dx+dy*dy+dz*dz);
  out.targetDistance=dist;

  // Different weapon types favor different ranges. Avoid explosives until
  // ammo, splash damage, and nearby geometry can all be assessed safely.
  const int weapon=out.combat.weapon;
  double ideal=14.0; // Colt, Tommygun
  if (weapon==1 || weapon==10) ideal=1.5;
  else if (weapon==4 || weapon==5) ideal=7.0;
  else if (weapon==13) ideal=32.0;
  else if (weapon==7 || weapon==12) ideal=19.0;

  const AimAngles aim=AimAt(dx,dy,dz);
  const double yawError=std::fabs(std::remainder(aim.yaw_deg-input.yaw,360.0));
  const double pitchError=std::fabs(std::remainder(aim.pitch_deg-input.pitch,360.0));
  const double speed=input.moveFactor>1.0?1.0:input.moveFactor;

  // Chase while turning only if facing approximately the target. Back off
  // solely as a low-health defense, and only at close range: long retreat
  // without a rearward floor probe is unsafe.
  if (yawError>65.0 || pitchError>55.0) out.combat.moveFactor=0.0;
  else if (dist>ideal+2.0) out.combat.moveFactor=speed;
  else if (weapon!=1 && weapon!=10 && input.self.health<45 &&
           dist<6.0 && dist<ideal-2.0) out.combat.moveFactor=-0.30*speed;
  else out.combat.moveFactor=0.0;

  // Cecil-style lateral combat motion. Timed direction changes remove the
  // static "stand and shoot" behavior; slot offsets prevent synchronized bots.
  int level=difficulty<0?0:(difficulty>2?2:difficulty);
  const int phaseTicks=level==0?110:(level==2?45:70);
  const double strafeSpeed=level==0?0.25:(level==2?0.70:0.48);
  if (weapon!=1 && weapon!=10 && dist>=3.0 && dist<50.0 &&
      yawError<22.0 && pitchError<18.0 && speed>0.0) {
    out.strafeFactor=(((tick/phaseTicks)+(localSlot&1))&1 ? -1.0:1.0)
                     *strafeSpeed*speed;
  }
  return out;
}
} // namespace botcore
#endif
