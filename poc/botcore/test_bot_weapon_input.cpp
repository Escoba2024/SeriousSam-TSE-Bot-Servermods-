#include <cstdio>
#if !__has_include("bot_weapon_input.h")
int main() { std::puts("FAIL: native weapon group/pulse policy is missing"); return 1; }
#else
#include "bot_weapon_input.h"
using namespace botcore;
static int failures=0;
#define CHECK(c,m) do { if (!(c)) { std::printf("FAIL: %s at %d\n",m,__LINE__); ++failures; } } while(0)
int main() {
  const int groups[]={0,1,2,2,3,3,4,4,5,5,1,6,7,6,8};
  for(int i=0;i<15;++i) CHECK(CombatWeaponGroup(i)==groups[i],"retail group mapping");
  CHECK(CombatWeaponGroup(-1)==0 && CombatWeaponGroup(15)==0,"invalid weapon does not select");
  CombatWeaponInput input;
  CHECK(input.Poll(1,7,2,0)==(4u<<14),"minigun selects group 4");
  CHECK(input.Poll(2,7,2,0)==0,"do not duplicate a pulse before native acknowledgement");
  CHECK(input.Poll(3,7,7,4u<<14)==0,"release all selection bits");
  CHECK(input.Poll(4,7,7,0)==0,"matching native wanted weapon stays selected");
  CHECK(input.Poll(5,13,7,0)==(6u<<14),"sniper selects group 6");
  CHECK(input.Poll(6,13,11,6u<<14)==0,"first pulse may select stronger flamer, then release");
  CHECK(input.Poll(7,13,11,0)==(6u<<14),"acknowledged release allows group flip to sniper");
  CHECK(input.Poll(8,13,13,6u<<14)==0,"acknowledged sniper is not flipped back");
  CHECK(input.Poll(9,4,13,0)==(3u<<14),"single shotgun selects group 3");
  CHECK(input.Poll(10,5,13,0)==0,"target weapon changes still wait for previous native request");
  CHECK(input.Poll(19,5,13,0)==(3u<<14),"bounded retry if pulse was not applied");
  CHECK(input.Poll(20,5,4,3u<<14)==0,"retry pulse receives full release");
  CHECK(input.Poll(21,5,4,0)==(3u<<14),"observed alternate requires a fresh complete group pulse");
  CHECK(input.Poll(22,0,4,3u<<14)==0,"lost target emits no stale weapon request");
  input.Reset();
  CHECK(input.Poll(1,12,2,16u<<14)==0,"wait for all five native selection bits to release");
  CHECK(input.Poll(1,12,2,0)==(7u<<14),"reset/respawn and laser group 7");
  std::printf("NATIVE WEAPON INPUT %s (%d failures)\n",failures?"FAIL":"PASS",failures);
  return failures?1:0;
}
#endif
