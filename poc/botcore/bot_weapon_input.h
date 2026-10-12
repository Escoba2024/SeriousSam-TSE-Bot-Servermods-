// Retail action protocol: select-number groups are 1..8, not WeaponType IDs.
#ifndef BOT_WEAPON_INPUT_H
#define BOT_WEAPON_INPUT_H
#include <cstdint>
namespace botcore {
inline int CombatWeaponGroup(int weapon) {
  static const int groups[15]={0,1,2,2,3,3,4,4,5,5,1,6,7,6,8};
  return weapon>=1 && weapon<=14?groups[weapon]:0;
}
class CombatWeaponInput {
 public:
  CombatWeaponInput() { Reset(); }
  void Reset() { pending_=false; sentTick_=0; beforeWanted_=0; }
  uint32_t Poll(int tick,int desired,int wanted,uint32_t nativeButtons) {
    const int group=CombatWeaponGroup(desired);
    if (!group || wanted==desired) { pending_=false; return 0; }
    // Player.es interprets the bitwise rising edge as a complete group number.
    // Wait for acknowledgement AND release before another pulse/alternate flip.
    if (nativeButtons & (31u<<14)) return 0;
    if (pending_ && wanted==beforeWanted_ && tick>=sentTick_ && tick-sentTick_<10)
      return 0;
    pending_=true; sentTick_=tick; beforeWanted_=wanted;
    return static_cast<uint32_t>(group)<<14;
  }
 private:
  bool pending_;
  int sentTick_,beforeWanted_;
};
}
#endif
