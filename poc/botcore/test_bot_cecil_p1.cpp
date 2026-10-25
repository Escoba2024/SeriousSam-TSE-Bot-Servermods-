// RED/GREEN CecilBotMod-inspired P1 transfer tests. No engine or Cecil source.
#include "bot_human.h"
#include <cstdio>
#include <cmath>
#include <cstring>

using namespace botcore;
static int failures=0, checks=0;
#define REQUIRE(x) do { ++checks; if (!(x)) { ++failures; std::printf("FAIL %s:%d %s\n",__FILE__,__LINE__,#x); } } while (0)

static WorldView World(int tick,bool alive=true) {
  WorldView w{};
  w.tick=tick;
  w.alive=alive;
  w.pose.x=0;w.pose.y=0;w.pose.z=0;
  w.pose.yaw_deg=0;w.pose.pitch_deg=0;
  w.health=alive?100:0;w.max_health=100;
  w.deathmatch=true;
  w.current_weapon=9;
  w.usable_weapons=1u<<8;
  return w;
}
static SenseInput Enemy(int idx,double dist,double health,double yaw,bool known) {
  SenseInput s{};
  s.index=idx;
  s.z=-dist;
  s.health=health;s.alive=true;
  s.yaw_deg=yaw;s.facing_known=known;
  return s;
}
static int Target(const BotProfile& profile,bool feature) {
  HumanBotPolicy p;
  p.Configure(&profile,false,feature);
  SenseInput e[2]={Enemy(1,17.0,100.0,0.0,true),
                   Enemy(2,25.0,15.0,180.0,true)};
  bool los[2]={true,true};
  int target=-1;
  for(int t=0;t<45;++t){
    const WorldView w=World(t);
    p.BeginTick(w);
    const BotCommand c=p.Step(w,e,los,2,0.05);
    target=c.target;
  }
  return target;
}
static void TestTargetThreatAndHealth() {
  BotProfile p{};
  REQUIRE(BuildProfile(3,2,11u,"probe",&p));
  REQUIRE(Target(p,false)==1); // strictly preserve legacy nearest choice
  REQUIRE(Target(p,true)==2); // threat + low-health beats distance
  REQUIRE(AimsAtMe(0.0,0.0,0.0,-25.0,180.0,25.0));
  REQUIRE(!AimsAtMe(0.0,0.0,0.0,-25.0,0.0,25.0));
}

static void TestCadenceAndDeterminism(){
  BotProfile profile{};
  REQUIRE(BuildProfile(5,4,919u,"cadence",&profile));
  HumanBotPolicy a,b;
  a.Configure(&profile,false,true);b.Configure(&profile,false,true);
  SenseInput s=Enemy(3,33.0,100.0,180.0,true);
  bool los=true;
  int shots=0,last=-1000;
  for(int tick=0;tick<220;++tick) {
    WorldView w=World(tick);
    a.BeginTick(w);b.BeginTick(w);
    BotCommand x=a.Step(w,&s,&los,1,0.05),y=b.Step(w,&s,&los,1,0.05);
    REQUIRE(x.fire==y.fire && x.weapon==y.weapon && x.target==y.target);
    if(x.fire) {
      REQUIRE(tick-last>=18); // grenade minimum 0.9 s
      ++shots;last=tick;
    }
  }
  REQUIRE(shots>=1);
  REQUIRE(WeaponAt(6).shot_period_s==0.0); // controlled continuous fire
  REQUIRE(WeaponAt(7).shot_period_s==0.0);
  REQUIRE(WeaponAt(8).shot_period_s>0.0);
  REQUIRE(WeaponAt(9).shot_period_s>=0.9);
  REQUIRE(WeaponAt(13).shot_period_s>0.0);
  REQUIRE(WeaponAt(14).shot_period_s>0.0);
}
static void TestRespawnGate() {
  BotProfile beginner{},expert{};
  REQUIRE(BuildProfile(1,0,13u,"beginner",&beginner));
  REQUIRE(BuildProfile(5,0,13u,"expert",&expert));
  REQUIRE(beginner.skill.respawn_delay_s>expert.skill.respawn_delay_s);
  HumanBotPolicy slow,fast,legacy;
  slow.Configure(&beginner,false,true);
  fast.Configure(&expert,false,true);
  legacy.Configure(&beginner,false,false);
  const int start=70;
  for(int tick=0;tick<start+60;++tick){
    WorldView w=World(tick,tick<start);
    slow.BeginTick(w);fast.BeginTick(w);legacy.BeginTick(w);
    if(tick>=start && tick<start+5) REQUIRE(!slow.ShouldRespawnPulse(tick));
  }
  REQUIRE(slow.ShouldRespawnPulse(start+40)); // beginner 2.0s
  REQUIRE(fast.ShouldRespawnPulse(start+5)); // expert 0.25s
  REQUIRE(legacy.ShouldRespawnPulse(start+2)==(((start+2)&4)==0));
  slow.BeginTick(World(start+61,true));
  REQUIRE(!slow.ShouldRespawnPulse(start+61)); // revived life clears pending pulse
}
int main(){
  TestTargetThreatAndHealth();
  TestCadenceAndDeterminism();
  TestRespawnGate();
  std::printf("CECIL P1 %s: %d checks, %d failures\n",failures?"FAIL":"PASS",checks,failures);
  return failures?1:0;
}
