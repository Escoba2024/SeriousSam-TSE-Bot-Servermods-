#include "bot_route.h"
#include "bot_human.h"
#include <cassert>
#include <cmath>
#include <cstdio>

static void RecoveryRespectsDamageWarning() {
  botcore::RouteMemory route;route.Configure(107);
  route.Observe(0,0,0,0,true,100,false);
  route.Observe(1,0,0,-8,true,100,false);
  route.Observe(2,0,12,-9,true,25,false);
  // Healing releases the injured hold but does not erase the learned warning.
  route.Observe(3,0,0,0,true,100,false);
  assert(!route.SafeMotion(0,0,0,0,1,0));
  route.NotifyRecovery(true);
  const auto into_warning=route.Travel(4,0,0,0,0,6);
  assert(into_warning.forward==0);
  const auto away=route.Travel(5,0,0,-9,0,6);
  assert(away.forward>0); // recovery may still move out of a warning area
}

static void InjuryTransitions() {
  botcore::RouteMemory route;route.Configure(107);
  route.Observe(0,0,0,0,true,100,false);
  route.Observe(1,0,12,0,true,25,false);
  assert(route.InjuryHold());
  route.NotifyRecovery(true);route.NotifyRecovery(false);
  // The warning's finite TTL is not permission to explore again while hurt.
  route.Observe(13000,0,0,0,true,25,false);
  assert(route.InjuryHold() && route.Travel(13000,0,0,0,0,6).forward==0);
  route.Observe(13001,0,0,0,true,50,false);
  assert(route.InjuryHold());
  route.Observe(13002,0,0,0,true,51,false);
  assert(!route.InjuryHold());
  route.Observe(13003,0,0,0,true,25,false);
  assert(route.InjuryHold());
  route.Observe(13004,NAN,0,0,false,-50,false);
  assert(!route.InjuryHold()); // absent/dead entity still ends the old life
  route.Observe(13005,20,0,0,true,25,false);
  assert(!route.InjuryHold());
  route.Observe(13006,20,0,0,true,100,false);
  route.Observe(13007,20,0,0,true,25,false);
  assert(route.InjuryHold());
  route.Configure(107);
  assert(!route.InjuryHold());

  route.Observe(0,0,0,0,true,100,false);
  route.Observe(1,0,0,0,true,25,true);
  assert(!route.InjuryHold() && route.SafeMotion(0,0,0,0,1,0));
  // The threshold follows the observed health scale, not a fixed50 HP.
  route.Configure(107);
  route.Observe(0,0,0,0,true,200,false,200);
  route.Observe(1,0,0,0,true,100,false,200);
  assert(route.InjuryHold());
  route.Observe(2,0,0,0,true,101,false,200);
  assert(!route.InjuryHold());
}

static void FinalMovementChecksActualAxes() {
  botcore::BotProfile profile;botcore::BuildProfile(3,0,107,"Final axes",&profile);
  botcore::HumanBotPolicy policy;policy.Configure(&profile,true);
  botcore::WorldView w;w.alive=true;w.health=100;
  policy.BeginTick(w);
  w.tick=1;w.pose.z=-8;policy.BeginTick(w);
  w.tick=2;w.pose.z=-9;w.pose.y=12;w.health=25;policy.BeginTick(w);
  policy.Step(w,nullptr,nullptr,0,.05);
  assert(policy.AllowFinalMovement(0,12,-9,0,0,0));
  assert(!policy.AllowFinalMovement(0,12,-9,0,0,.5)); // lateral override also held
  w.tick=3;w.pose={};w.health=100;policy.BeginTick(w);
  policy.NotifyNavigation(true);
  assert(!policy.AllowFinalMovement(0,0,0,0,.9,0)); // later recovery advance
  assert(!policy.AllowFinalMovement(0,0,0,90,0,.5)); // actual lateral axis toward warning
  assert(!policy.AllowFinalMovement(0,0,0,0,1,.5)); // combined scaled axes
  assert(policy.AllowFinalMovement(0,0,0,90,.9,0));
  assert(policy.AllowFinalMovement(0,20,0,0,.9,0)); // other floor remains unknown
  assert(!policy.AllowFinalMovement(0,0,0,NAN,0,0));
  policy.Reset();
  assert(policy.AllowFinalMovement(0,0,0,0,.9,0));
}

static void InjuredDefenceRetainsProfiles() {
  for(int tier=1;tier<=botcore::kSkillTierCount;++tier) {
    for(int persona=0;persona<botcore::kPersonalityCount;++persona) {
      botcore::BotProfile profile;
      botcore::BuildProfile(tier,persona,107,"Injured defence",&profile);
      botcore::HumanBotPolicy policy;policy.Configure(&profile,true);
      botcore::WorldView w;w.alive=true;w.health=100;w.current_weapon=2;
      w.usable_weapons=1u<<1;
      policy.BeginTick(w);policy.Step(w,nullptr,nullptr,0,.05);
      w.tick=1;w.health=25;w.pose.y=12;
      policy.BeginTick(w);policy.Step(w,nullptr,nullptr,0,.05);
      w.pose.y=0;
      botcore::SenseInput target{};target.index=1;target.alive=true;target.z=-18;
      bool los=true,seen=false,fired=false;
      for(int tick=2;tick<400;++tick) {
        w.tick=tick;policy.BeginTick(w);
        const auto command=policy.Step(w,&target,&los,1,.05);
        assert(command.travel && command.forward==0 && command.strafe==0);
        seen=seen || command.target_visible;fired=fired || command.fire;
        w.pose.yaw_deg+=command.yaw_delta_deg;
        w.pose.pitch_deg+=command.pitch_delta_deg;
      }
      assert(seen && fired);
      assert(policy.profile().tier==tier && policy.profile().persona==persona);
    }
  }
}

static void VisibleCombatDoesNotCreateHold() {
  botcore::BotProfile profile;botcore::BuildProfile(5,0,107,"Visible damage",&profile);
  botcore::HumanBotPolicy policy;policy.Configure(&profile,true);
  botcore::WorldView w;w.alive=true;w.health=100;w.current_weapon=2;w.usable_weapons=2;
  botcore::SenseInput target{};target.index=1;target.alive=true;target.z=-18;
  bool los=true;
  for(int tick=0;tick<60;++tick) {
    w.tick=tick;policy.BeginTick(w);
    const auto command=policy.Step(w,&target,&los,1,.05);
    w.pose.yaw_deg+=command.yaw_delta_deg;w.pose.pitch_deg+=command.pitch_delta_deg;
  }
  w.tick=60;w.health=25;policy.BeginTick(w);
  const auto command=policy.Step(w,&target,&los,1,.05);
  assert(command.target_visible && (command.forward!=0 || command.strafe!=0));
  assert(policy.AllowFinalMovement(0,0,0,0,1,0));
}

int main() {
  RecoveryRespectsDamageWarning();
  InjuryTransitions();
  FinalMovementChecksActualAxes();
  InjuredDefenceRetainsProfiles();
  VisibleCombatDoesNotCreateHold();
  // Search must traverse an open area instead of continuously drawing circles.
  botcore::RouteMemory route;
  route.Configure(107);
  double x=0,z=0,yaw=0;
  for(int tick=0;tick<120;++tick) {
    route.Observe(tick,x,0,z,true,100,false);
    const auto move=route.Travel(tick,x,0,z,yaw,6);
    yaw+=move.yaw_delta_deg;
    x-=std::sin(yaw*botcore::kDegToRad)*move.forward*.5;
    z-=std::cos(yaw*botcore::kDegToRad)*move.forward*.5;
  }
  assert(std::hypot(x,z)>35); // at least 35m net in six simulated seconds

  route.Configure(107);
  route.Observe(0,0,0,0,true,100,false);
  route.Observe(1,0,0,-8,true,100,false);
  // Native acid can throw the bot upward. Learn the last contact position,
  // rather than incorrectly placing the hazard on the upper floor.
  route.Observe(2,0,12,-9,true,25,false);
  assert(!route.SafeMotion(0,0,0,0,1,0));
  assert(route.SafeMotion(0,20,0,0,1,0));
  assert(route.SafeMotion(0,0,-9,0,1,0)); // moving away from the contact
  assert(!route.SafeMotion(0,0,-16,180,1,0)); // approaching from the other side
  route.Observe(3,0,0,-9,false,-50,false);
  route.Observe(4,0,0,0,true,100,false);
  assert(!route.SafeMotion(0,0,0,0,1,0)); // own learned hazard survives respawn
  const auto avoid=route.Travel(4,0,0,0,0,6);
  assert(avoid.yaw_delta_deg!=0 && avoid.forward==0);
  route.Configure(107);
  assert(route.SafeMotion(0,0,0,0,1,0)); // a new map/session clears old memory

  route.Observe(0,0,0,0,true,100,false);
  route.Observe(1,0,0,-8,true,100,false);
  route.Observe(2,0,0,-9,true,25,true);
  assert(route.SafeMotion(0,0,0,0,1,0)); // visible combat loss is no terrain proof
  route.Observe(3,NAN,0,0,true,0,false);
  assert(route.Travel(3,NAN,0,0,0,6).forward==0);

  // A successful obstacle turn becomes the next travel heading; the high-level
  // goal must not immediately steer back into the wall it just escaped.
  route.Configure(107);
  route.Observe(0,0,0,0,true,100,false);
  route.Travel(0,0,0,0,0,6);
  route.NotifyRecovery(true);
  auto moving=route.Travel(1,0,0,0,90,6);
  assert(moving.yaw_delta_deg==0);
  route.NotifyRecovery(false);
  moving=route.Travel(2,0,0,0,90,6);
  assert(std::fabs(moving.yaw_delta_deg)<1e-6 && moving.forward>0);

  botcore::BotProfile p;botcore::BuildProfile(5,0,107,"Tracker",&p);
  botcore::HumanBotPolicy policy;policy.Configure(&p,true);
  botcore::WorldView w;w.alive=true;w.health=100;w.usable_weapons=2;w.current_weapon=2;
  botcore::SenseInput target{};target.index=1;target.alive=true;
  target.x=-30;target.z=-10;bool los=true;bool acquired=false;
  for(int tick=0;tick<60 && !acquired;++tick) {
    w.tick=tick;policy.BeginTick(w);
    auto c=policy.Step(w,&target,&los,1,.05);
    if(c.target==1) {acquired=true;assert(c.forward==0);}
  }
  assert(acquired); // face an off-axis opponent before chasing through terrain

  policy.Configure(&p,true);w.pose={};w.health=100;
  w.tick=0;policy.BeginTick(w);
  w.tick=1;w.pose.z=-8;policy.BeginTick(w);
  w.tick=2;w.pose.y=12;w.pose.z=-9;w.health=25;policy.BeginTick(w);
  w.tick=3;w.alive=false;w.health=-50;policy.BeginTick(w);
  w.alive=true;w.health=100;w.pose={};target.x=0;target.z=-30;acquired=false;
  for(int tick=4;tick<60;++tick) {
    w.tick=tick;policy.BeginTick(w);
    const auto c=policy.Step(w,&target,&los,1,.05);
    if(c.target==1) {acquired=true;assert(c.forward==0 && c.strafe==0 && c.travel);}
  }
  assert(acquired); // a visible opponent must not lure the bot back into a known warning
  std::puts("ROUTE MEMORY PASS");
}
