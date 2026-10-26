// Exercises the actual, single PR57 policy, with selected PR66 modules wired in.
#include "bot_human.h"
#include <cmath>
#include <cstdio>
#include <limits>
using namespace botcore;
static int checks=0, failures=0;
#define CHECK(c) do { ++checks; if(!(c)) { ++failures; std::printf("FAIL line %d: %s\n",__LINE__,#c); } } while(0)
static void Configure(HumanBotPolicy& h,const BotProfile& p,bool weapon,bool lead,bool strafe) {
#ifdef COMBAT_MASTER_AVAILABLE
 h.Configure(&p,false,true,weapon,lead,strafe);
#else
 (void)weapon;(void)lead;(void)strafe;h.Configure(&p,false,true);
#endif
}
static WorldView World(int t,double d=10) {
 (void)d;WorldView w;w.tick=t;w.alive=true;w.health=100;w.usable_weapons=0x3fffu;w.current_weapon=2;return w;
}
static SenseInput Enemy(double d) {
 SenseInput s{};s.index=1;s.alive=true;s.z=-d;s.health=100;return s;
}
static BotCommand Tick(HumanBotPolicy& p,WorldView w,SenseInput e,bool los=true) {
 p.BeginTick(w);return p.Step(w,&e,&los,1,0.05);
}
static BotCommand Settle(HumanBotPolicy& p,double d,uint32_t mask=0x3fffu) {
 BotCommand c;for(int i=0;i<160;++i) {auto w=World(i);w.usable_weapons=mask;c=Tick(p,w,Enemy(d));}return c;
}
static void WeaponNichesAndAmmo() {
 BotProfile p;CHECK(BuildProfile(5,0,91,"probe",&p));HumanBotPolicy h;Configure(h,p,true,false,false);
 CHECK(Settle(h,5).weapon==5); // close aggressor: double shotgun, not laser
 CHECK(BuildProfile(5,4,91,"probe",&p));Configure(h,p,true,false,false);
 CHECK(Settle(h,55).weapon==13); // marksman at 55m: sniper
 auto w=World(161);w.usable_weapons=1u<<1;CHECK(Tick(h,w,Enemy(55)).weapon==2); // ammo loss bypasses dwell
 Configure(h,p,true,false,false);auto near=Settle(h,2,1u<<7);CHECK(!near.fire); // only rocket: blast gate wins
 CHECK(h.PreferredRange(5)<h.PreferredRange(13));
}
static void PersonaAndSkillPreserved() {
 int winners[6]={};for(int persona=0;persona<6;++persona) {
  BotProfile p;CHECK(BuildProfile(5,persona,91,"probe",&p));HumanBotPolicy h;Configure(h,p,true,true,true);
  CHECK(h.profile().skill.prediction_gain==p.skill.prediction_gain);
  CHECK(h.profile().skill.aim_sigma_deg==p.skill.aim_sigma_deg);
  CHECK(h.profile().personality.range_preference==p.personality.range_preference);
  winners[persona]=Settle(h,13).weapon;
 }
 bool distinct=false;for(int i=1;i<6;++i) distinct|=winners[i]!=winners[0];CHECK(distinct);
}
static void LeadAndLos() {
 BotProfile p;BuildProfile(5,2,77,"lead",&p);HumanBotPolicy h;Configure(h,p,false,true,false);
 auto w=World(0);w.usable_weapons=1u<<5;auto e=Enemy(20);e.vx=4;
#ifdef COMBAT_MASTER_AVAILABLE
 w.observation_age_s=0.1;
#endif
 HumanBotPolicy unled;Configure(unled,p,false,false,false);
 BotCommand c, original;for(int i=0;i<100;++i){w.tick=i;c=Tick(h,w,e);original=Tick(unled,w,e);}
#ifdef COMBAT_MASTER_AVAILABLE
 CHECK(std::fabs(c.yaw_delta_deg-original.yaw_delta_deg)>0.1); // lead reaches real aim controller
 CHECK(std::fabs(c.latency_lead_s-0.090)<1e-12); // measured age * expert gain
 w.tick++;w.observation_age_s=10;c=Tick(h,w,e);CHECK(std::fabs(c.latency_lead_s-0.225)<1e-12);
 w.tick++;w.observation_age_s=std::numeric_limits<double>::quiet_NaN();c=Tick(h,w,e);CHECK(c.latency_lead_s==0);
 w.tick++;w.observation_age_s=-1;c=Tick(h,w,e);CHECK(c.latency_lead_s==0);
 w.tick++;w.observation_age_s=.1;c=Tick(h,w,e,false);CHECK(c.latency_lead_s==0);CHECK(!c.fire);
#else
 CHECK(false); // missing measured-age lead in PR57
#endif
}
static void StrafeAndLifeReset() {
 BotProfile p;BuildProfile(3,2,99,"strafe",&p);HumanBotPolicy h;Configure(h,p,false,false,true);
 BotCommand c=Settle(h,80,1u<<5);CHECK(c.target_visible);CHECK(std::fabs(c.strafe)>0.05); // diagonal approach
#ifdef COMBAT_MASTER_AVAILABLE
 const double before=c.strafe;h.NotifyDamage(100,75);c=Tick(h,World(160),Enemy(80));CHECK(before*c.strafe<0);
#endif
 HumanBotPolicy a,b;Configure(a,p,true,true,true);Configure(b,p,true,true,true);
 for(int i=0;i<200;++i){auto x=Tick(a,World(i),Enemy(12)),y=Tick(b,World(i),Enemy(12));CHECK(x.strafe==y.strafe && x.weapon==y.weapon && x.fire==y.fire);}
 a.Reset();b.Reset();CHECK(Tick(a,World(0),Enemy(12)).strafe==Tick(b,World(0),Enemy(12)).strafe);
 // Target and respawn remain PR57-owned even with all new modules enabled.
 for(int tier=1;tier<=5;++tier){BuildProfile(tier,2,99,"life",&p);Configure(a,p,true,true,true);Configure(b,p,false,false,false);
  for(int i=0;i<100;++i){auto w=World(i);w.alive=i<10 || i>70;w.health=w.alive?100:0;
   auto x=Tick(a,w,Enemy(12)),y=Tick(b,w,Enemy(12));CHECK(x.target==y.target);CHECK(a.ShouldRespawnPulse(i)==b.ShouldRespawnPulse(i));}
 }
}
int main(){WeaponNichesAndAmmo();PersonaAndSkillPreserved();LeadAndLos();StrafeAndLifeReset();std::printf("COMBAT MASTER: %d checks, %d failures\n",checks,failures);return failures?1:0;}
