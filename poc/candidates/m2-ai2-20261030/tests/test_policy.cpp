#include "bot_human.h"
#include <cstdio>
#include <set>
#include <utility>
using namespace botcore;
static int checks=0, failures=0;
#define CHECK(c) do{++checks;if(!(c)){++failures;std::printf("FAIL line %d: %s\n",__LINE__,#c);}}while(0)
static void setup(HumanBotPolicy& p,int tier=5,int persona=0,bool deferred=true) {
  BotProfile b{};BuildProfile(tier,persona,713u,"M2-test",&b);
#ifdef M2_AI2_AVAILABLE
  p.Configure(&b,false,true,true,true,true,deferred);
#else
  (void)deferred;p.Configure(&b,false,true,true,true,true);
#endif
}
static void emitted(HumanBotPolicy& p,int tick,int weapon) {
#ifdef M2_AI2_AVAILABLE
  p.NotifyFireEmitted(tick,weapon);
#else
  (void)p;(void)tick;(void)weapon;
#endif
}
static BotCommand step(HumanBotPolicy& p,WorldView& w, double distance=40,bool los=true) {
  SenseInput s{};s.index=1;s.z=-distance;s.alive=true;s.health=100;
  p.BeginTick(w);bool need=false;p.PlanLosQueries(&s,1,&need);
  bool seen=los && need;return p.Step(w,&s,&seen,1,.05);
}
static WorldView world(int weapon=13) {
  WorldView w{};w.alive=true;w.health=100;w.usable_weapons=1u<<(weapon-1);w.current_weapon=weapon;return w;
}
int main(){
  // Veto every proposed shot, then allow one: drawing/recovery cannot charge cadence.
  HumanBotPolicy p;setup(p);auto w=world();int proposals=0,first=-1;
  for(w.tick=0;w.tick<160;++w.tick){auto c=step(p,w);if(c.fire){++proposals;if(first<0)first=w.tick;}}
  std::printf("vetoed proposals=%d first=%d\n",proposals,first);CHECK(first>=0);CHECK(proposals>20);
  auto c=step(p,w);CHECK(c.fire);emitted(p,w.tick,c.weapon);
  int committed=w.tick;
  for(w.tick=committed+1;w.tick<committed+26;++w.tick)CHECK(!step(p,w).fire);
  // Keep crosshair steady: the first eligible post-cooldown proposal must arrive promptly.
  bool resumed=false;for(;w.tick<=committed+35;++w.tick)resumed|=step(p,w).fire;CHECK(resumed);
  // Empty usable mask must never emit combat fire even with a drawn weapon.
  setup(p);w=world();w.usable_weapons=0;int emptyfire=0;
  for(w.tick=0;w.tick<180;++w.tick){emptyfire+=step(p,w).fire;}CHECK(emptyfire==0);
  // Every profile closes with melee; no fictitious knife/chainsaw shots at 20m.
  for(int tier=1;tier<=5;++tier)for(int persona=0;persona<6;++persona)for(int weapon: {1,10}){
    setup(p,tier,persona);w=world(weapon);int acquired=0,farshots=0,closing=0;
    for(w.tick=0;w.tick<160;++w.tick){auto m=step(p,w,20);if(m.target>=0){++acquired;closing+=m.forward>0;}farshots+=m.fire;}
    CHECK(acquired>0);CHECK(closing==acquired);CHECK(farshots==0);
    setup(p,tier,persona);w=world(weapon);int nearshots=0;
    for(w.tick=0;w.tick<240;++w.tick){nearshots+=step(p,w,1.2).fire;}CHECK(nearshots>0);
  }
  // Pin the melee reach boundary independently of the preference tables.
  for(int tier=1;tier<=5;++tier)for(int persona=0;persona<6;++persona)
    for(int weapon:{1,10})for(double distance:{2.0,4.0,12.0}){
      setup(p,tier,persona);w=world(weapon);int shots=0,closing=0,targets=0;
      for(w.tick=0;w.tick<240;++w.tick){auto m=step(p,w,distance);shots+=m.fire;
        if(m.target>=0){++targets;closing+=m.forward>0;}}
      CHECK(targets>0&&closing==targets);CHECK(distance<=2.0?shots>0:shots==0);
    }
  // Skills differ in observable reaction, not only aim dispersion.
  int prior=10000;std::set<int> reactions;
  for(int tier=1;tier<=5;++tier){setup(p,tier);w=world(2);int firsttarget=-1;
    for(w.tick=0;w.tick<30;++w.tick){if(step(p,w,25).target>=0&&firsttarget<0)firsttarget=w.tick;}
    CHECK(firsttarget>=0&&firsttarget<prior);prior=firsttarget;reactions.insert(firsttarget);
  }CHECK(reactions.size()==5);
  // Persona decisions remain distinct at constant mechanical skill.
  std::set<long long> decisions;
  for(int persona=0;persona<6;++persona){setup(p,3,persona);w=world(6);long long fingerprint=0;
    for(w.tick=0;w.tick<300;++w.tick){auto m=step(p,w,25);fingerprint+=static_cast<long long>(m.forward*1000)+static_cast<long long>(m.strafe*100)*17+static_cast<long long>(m.preferred_range_m*100)*31;}
    decisions.insert(fingerprint);
  }CHECK(decisions.size()==6);
  // Expired target memory still has a per-target aiming bias. Slot reuse must
  // erase that identity even after target() already became -1.
  setup(p);w=world();for(w.tick=0;w.tick<70;++w.tick)step(p,w);
  for(;w.tick<200;++w.tick)step(p,w,40,false);
  CHECK(p.target()==-1);CHECK(std::fabs(p.aim().bias_yaw_deg())>1e-6);
  const double oldbias=p.aim().bias_yaw_deg();
#ifdef M2_AI2_AVAILABLE
  p.ForgetOpponent(2);CHECK(p.aim().bias_yaw_deg()==oldbias);
  p.ForgetOpponent(1);CHECK(p.aim().bias_yaw_deg()==0.0);
#else
  (void)oldbias;
#endif
  // Empty ammo fallback: when no ranged weapon is usable the bot switches to
  // knife and continues fighting in melee instead of staring or dry-firing.
  for(int tier=1;tier<=5;++tier)for(int persona=0;persona<6;++persona){
    setup(p,tier,persona);w=world(1); // knife from spawn
    int knifefire=0,holdingknife=0;
    for(w.tick=0;w.tick<240;++w.tick){auto c=step(p,w,1.2);knifefire+=c.fire;holdingknife+=(c.weapon==1);}
    CHECK(holdingknife>0);CHECK(knifefire>0);
  }
  // Mid-fight ammo depletion must be detected and the bot must not emit fire
  // with the now-empty weapon; it re-selects and falls back to melee.
  setup(p);w=world(2);
  for(w.tick=0;w.tick<40;++w.tick){auto c=step(p,w,10);CHECK(c.weapon==2);}
  w.usable_weapons=(1u<<0); // colt ammo exhausted, only knife remains
  int fallback_weapon=-1,fallback_fire=0;
  for(w.tick=40;w.tick<100;++w.tick){
    auto c=step(p,w,1.2);
    if(c.weapon==1)fallback_weapon=1;
    fallback_fire+=c.fire;
  }
  CHECK(fallback_weapon==1);CHECK(fallback_fire>0);

  // Weapon selection sanity for the Red-Station-relevant families.
  for(auto cas:{std::pair<int,double>{2,25.0},std::pair<int,double>{4,10.0},std::pair<int,double>{8,30.0}}){
    setup(p);w=world(cas.first);w.usable_weapons=(1u<<(cas.first-1));
    auto c=step(p,w,cas.second);CHECK(c.weapon==cas.first);
  }

  // Melee commitment: knife/chainsaw fire only inside the 2m reach boundary
  // and the policy does not emit dry ranged fire when only melee is usable.
  for(int weapon:{1,10}){
    setup(p);w=world(weapon);w.usable_weapons=(1u<<(weapon-1));
    int infire=0,outfire=0;
    for(w.tick=0;w.tick<120;++w.tick){infire+=step(p,w,1.2).fire;}
    setup(p);w=world(weapon);w.usable_weapons=(1u<<(weapon-1));
    for(w.tick=0;w.tick<120;++w.tick){outfire+=step(p,w,4.0).fire;}
    CHECK(infire>0);CHECK(outfire==0);
  }

  // Opponent replacement must reset acquisition and impose a fresh reaction
  // delay, even if the same slot index is reused by a new entity.
  setup(p);w=world();
  int acquired=1000;
  for(w.tick=0;w.tick<40;++w.tick)if(step(p,w).target>=0&&acquired>40)acquired=w.tick;
  CHECK(acquired<40);
  p.ForgetOpponent(1);
  int reacquired=1000;
  for(w.tick=40;w.tick<90;++w.tick)if(step(p,w).target>=0&&reacquired>90)reacquired=w.tick;
  CHECK(reacquired>acquired+2); // fresh reaction delay after identity reset

  // Occluded live position cannot drive new shots or hidden tracking.
  setup(p);w=world();for(w.tick=0;w.tick<70;++w.tick)step(p,w);
  for(;w.tick<170;++w.tick)CHECK(!step(p,w,400,false).fire);
  std::printf("M2 POLICY: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
