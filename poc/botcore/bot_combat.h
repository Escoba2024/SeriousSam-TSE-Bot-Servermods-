// Engine-free combat policy. The caller supplies only visible replicated players.
#ifndef BOT_COMBAT_H
#define BOT_COMBAT_H
#include "botcore.h"
#include "botcore_ai.h"
namespace botcore {
struct AmmoInfo { int bullets, shells, napalm, electricity, sniperBullets; };
inline uint32_t CombatUsableWeapons(uint32_t owned, const AmmoInfo& ammo) {
  if (ammo.shells < 1) owned &= ~(1u<<3);
  if (ammo.shells < 2) owned &= ~(1u<<4); // retail double shotgun consumes two shells
  if (ammo.bullets <= 0) owned &= ~((1u<<5)|(1u<<6));
  if (ammo.napalm <= 0) owned &= ~(1u<<10);
  if (ammo.electricity <= 0) owned &= ~(1u<<11);
  if (ammo.sniperBullets <= 0) owned &= ~(1u<<12);
  return owned; // Colt reloads without a finite reserve; a zero clip is usable.
}
struct CombatInput {
  TargetInfo self;
  double yaw, pitch, turnLimit, moveFactor;
  uint32_t usableWeapons;
  bool skipLocals;
  double stopDistance;
};
struct CombatDecision {
  int target, weapon;
  double yawDelta, pitchDelta, moveFactor;
  bool fireAllowed;
};
inline bool CombatValidPlayer(const TargetInfo& p) {
  return p.index >= 0 && p.index < 16 && std::isfinite(p.x) &&
         std::isfinite(p.y) && std::isfinite(p.z) && std::isfinite(p.health);
}
inline CombatDecision DecideCombat(const TargetInfo* players, int count,
                                   const CombatInput& in) {
  CombatDecision d = {-1, 1, 0, 0, 0, false};
  if (!CombatValidPlayer(in.self) || in.self.health <= 0 ||
      !std::isfinite(in.yaw) || !std::isfinite(in.pitch) ||
      !std::isfinite(in.turnLimit) || in.turnLimit < 0 ||
      !std::isfinite(in.moveFactor) || !std::isfinite(in.stopDistance)) return d;
  TargetInfo valid[16]; int n=0;
  if (players != nullptr) {
    for (int i=0; i<count && i<16; ++i)
      if (CombatValidPlayer(players[i])) valid[n++]=players[i];
  }
  d.target=SelectTarget(valid,n,in.self.index,in.self.x,in.self.y,in.self.z,in.skipLocals);
  if (d.target < 0) return d;
  const TargetInfo* target=nullptr;
  for (int i=0; i<n; ++i) if (valid[i].index==d.target) { target=&valid[i]; break; }
  if (!target) return d;
  const double dx=target->x-in.self.x, dy=target->y-in.self.y, dz=target->z-in.self.z;
  const double distance=std::sqrt(dx*dx+dy*dy+dz*dz);
  if (!std::isfinite(distance)) { d.target=-1; return d; }
  const AimAngles aim=AimAt(dx,dy,dz);
  d.yawDelta=TestTurnDelta(in.yaw,aim.yaw_deg,in.turnLimit);
  d.pitchDelta=TestTurnDelta(in.pitch,aim.pitch_deg,in.turnLimit);
  d.weapon=SelectWeapon(in.usableWeapons,distance);
  const bool aligned=std::fabs(TestTurnDelta(in.yaw,aim.yaw_deg,180.0))<3.0 &&
                     std::fabs(TestTurnDelta(in.pitch,aim.pitch_deg,180.0))<3.0;
  const bool melee=d.weapon==1 || d.weapon==10;
  d.fireAllowed=aligned && (!melee || distance<=2.0);
  const double stop=melee?1.5:in.stopDistance;
  if (aligned && distance>stop) d.moveFactor=in.moveFactor<0?0:(in.moveFactor>1?1:in.moveFactor);
  return d;
}
}
#endif
