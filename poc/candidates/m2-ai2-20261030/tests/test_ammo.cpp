// Exercise the actual native logging statement, including pools formerly absent.
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <iostream>
struct Weapons {
  int m_iCurrentWeapon=8,m_iWantedWeapon=8,m_iAvailableWeapons=139;
  int m_iColtBullets=6,m_iBullets=11,m_iShells=12,m_iRockets=13;
  int m_iGrenades=14,m_iNapalm=15,m_iElectricity=16;
  int m_iSniperBullets=17,m_iIronBalls=18;
};
static char output[1024];
static void BotLog(const char* format,...) {
  va_list arguments;va_start(arguments,format);
  std::vsnprintf(output,sizeof(output),format,arguments);va_end(arguments);
}
int main() {
  Weapons state;Weapons* weapons=&state;const Weapons original=state;
  const int iLP=0;struct { int bs_iTick=42; } bs;
  // Empty baseline include remains compilable, but cannot satisfy observation.
  (void)weapons;(void)iLP;(void)bs;(void)&BotLog;
  #include "ammo.inc"
  int failures=0;
  const char* expected="[BotAmmo] tick=42 local=0 current=8 wanted=8 available=139 colt=6 bullets=11 shells=12 rockets=13 grenades=14 napalm=15 cells=16 sniper=17 cannon=18\n";
  if (std::strcmp(output,expected)!=0) ++failures;
  if (std::memcmp(&original,&state,sizeof(state))!=0) ++failures;
  state.m_iRockets=0;state.m_iGrenades=0;state.m_iIronBalls=0;
  #include "ammo.inc"
  if (!std::strstr(output,"rockets=0 grenades=0") || !std::strstr(output,"cannon=0\n")) ++failures;
  std::cout<<"M2 NATIVE AMMO OBSERVATION: 3 checks, "<<failures<<" failures\n";
  return failures ? 1 : 0;
}
