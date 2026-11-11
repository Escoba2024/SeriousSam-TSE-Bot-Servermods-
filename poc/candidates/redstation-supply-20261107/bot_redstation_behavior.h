// bot_redstation_behavior.h — pure, deterministic Red Station policies.
#ifndef BOTCORE_BOT_REDSTATION_BEHAVIOR_H
#define BOTCORE_BOT_REDSTATION_BEHAVIOR_H
#include <cstdint>
#include <cmath>
namespace botcore {
// Retail PlayerWeapons bits are (WeaponType - 1); 1 knife, 2/3 colts.
inline bool HasCollectedWeapon(uint32_t owned) {
  const uint32_t starter=(1u<<0)|(1u<<1)|(1u<<2);
  const uint32_t possible=(1u<<14)-1;
  return (owned & possible & ~starter)!=0;
}
inline bool BeginWeaponRush(bool was_playable, bool now_playable,uint32_t owned) {
  return !was_playable && now_playable && !HasCollectedWeapon(owned);
}
inline bool WeaponRushOngoing(bool rushing, int ticks_since_spawn, uint32_t owned) {
  // Fail-safe exit: no permanent helpless knife run if a spot is unreachable.
  return rushing && !HasCollectedWeapon(owned) &&
         ticks_since_spawn >= 0 && ticks_since_spawn < 20*22;
}
inline int PickupWeaponType(int item_kind) {
  switch(item_kind) {
    case 1: return 2;   // colt, ignored by pickup planner
    case 2: return 4;   // single shotgun
    case 3: return 5;   // double shotgun
    case 4: return 6;   // tommy gun
    case 5: return 7;   // minigun
    case 6: return 8;   // rocket launcher
    case 7: return 9;   // grenade launcher
    case 8: return 13;  // sniper
    case 9: return 11;  // flamer
    case 10:return 12;  // laser
    case 11:return 10;  // chainsaw
    case 12:return 14;  // cannon
    default:return 0;
  }
}
inline bool WantWeaponPickup(int item_kind,uint32_t owned) {
  const int w=PickupWeaponType(item_kind);
  return w>=4 && w<=14 && (owned & (1u<<(w-1)))==0;
}
inline bool RedStationJumpPulse(int tick,int slot,double forward,bool safe_floor) {
  if (tick<0 || slot<0 || slot>7 || !safe_floor ||
      !(forward>0.55) || !std::isfinite(forward)) return false;
  // Every ~7–12 s per bot, with naturally desynchronised offsets, 3-tick press.
  const int period=143+slot*13;
  const int phase=(tick+slot*41)%period;
  return phase>=0 && phase<3;
}
inline bool IsOwnBotCharacter(const unsigned char guid[16],
                             const unsigned char known[8][16],
                             bool complete_roster) {
  if (!complete_roster || guid==nullptr || known==nullptr) return false;
  for(int i=0;i<8;++i) {
    bool equal=true;
    for(int j=0;j<16;++j) if(guid[j]!=known[i][j]) {equal=false;break;}
    if(equal) return true;
  }
  return false;
}
} // namespace botcore
#endif
