// Real engine-free combat policy checks; retail acceptance is separate.
#include <cstdio>
#if !__has_include("bot_combat.h")
int main() { std::puts("FAIL: automatic combat decision policy is missing"); return 1; }
#else
#include "bot_combat.h"
#include <limits>
#include <cmath>
using namespace botcore;
static int failures=0;
#define CHECK(c,m) do { if (!(c)) { std::printf("FAIL: %s at %d\n",m,__LINE__); ++failures; } } while(0)
int main() {
    CombatInput in{{0,0,0,0,100,true},0,0,4.5,1.0,3u,true,8.0};
    TargetInfo players[]={{0,0,0,0,100,true},{1,0,0,-20,100,false},
                         {2,0,0,-5,100,true},{3,0,0,-2,0,false}};
    CombatDecision d=DecideCombat(players,4,in);
    CHECK(d.target==1 && d.weapon==2,"nearest living remote target; local and dead excluded");
    CHECK(d.fireAllowed && d.moveFactor==1.0,"aligned valid distant target allows fire and pursuit");
    in.skipLocals=false;
    d=DecideCombat(players,4,in);
    CHECK(d.target==2 && d.moveFactor==0.0,"explicit local opponents allowed; close target stops pursuit");
    in.skipLocals=true; in.yaw=90;
    d=DecideCombat(players,4,in);
    CHECK(d.yawDelta==-4.5 && !d.fireAllowed && d.moveFactor==0.0,"bounded turn and no firing/movement while unaligned");
    in.yaw=179;
    TargetInfo behind[]={{1,0.0,0.0,20.0,100,false}};
    d=DecideCombat(behind,1,in);
    CHECK(std::fabs(d.yawDelta-1.0)<0.001 && d.fireAllowed,"shortest turn across yaw wrap");
    in.yaw=0; in.self.health=0;
    d=DecideCombat(players,4,in);
    CHECK(d.target==-1 && !d.fireAllowed && d.moveFactor==0.0,"dead self cannot attack or pursue");
    in.self.health=100;
    d=DecideCombat(nullptr,0,in);
    CHECK(d.target==-1 && !d.fireAllowed,"no stale target when opponent disappears");
    TargetInfo invalid[]={{-1,0,0,-1,100,false},{16,0,0,-1,100,false},
                         {1,std::numeric_limits<double>::quiet_NaN(),0,0,100,false},
                         {2,0,0,-3,std::numeric_limits<double>::infinity(),false},
                         {3,0,0,-10,100,false}};
    d=DecideCombat(invalid,5,in);
    CHECK(d.target==3,"invalid snapshot indices, coordinates and health are excluded");
    in.usableWeapons=1u;
    d=DecideCombat(players,4,in);
    CHECK(d.weapon==1 && !d.fireAllowed,"knife cannot fire at distant target");
    const uint32_t owned=(1u<<0)|(1u<<1)|(1u<<4)|(1u<<6)|(1u<<11)|(1u<<12);
    AmmoInfo empty{0,0,0,0,0};
    CHECK(SelectWeapon(CombatUsableWeapons(owned,empty),20)==2,"empty ammo weapons fall back to reloadable Colt");
    AmmoInfo loaded{100,10,0,20,5};
    AmmoInfo oneShell{0,1,0,0,0};
    const uint32_t shotguns=(1u<<0)|(1u<<1)|(1u<<3)|(1u<<4);
    CHECK(SelectWeapon(CombatUsableWeapons(shotguns,oneShell),5)==4,"one shell can fire single shotgun but not double shotgun");
    CHECK(SelectWeapon(CombatUsableWeapons(owned,loaded),20)==7,"available minigun with bullets at mid range");
    CHECK(SelectWeapon(CombatUsableWeapons(owned,loaded),50)==13,"loaded sniper at long range");
    in.self.health=100; in.usableWeapons=3u; in.yaw=0;
    d=DecideCombat(players,4,in);
    CHECK(d.target==1 && d.fireAllowed,"fresh decision after respawn reacquires valid target");
    std::printf("COMBAT POLICY %s (%d failures)\n",failures?"FAIL":"PASS",failures);
    return failures?1:0;
}
#endif
