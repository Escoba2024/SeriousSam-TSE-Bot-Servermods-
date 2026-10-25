#include "bot_aim.h"
#include "bot_human.h"
#include <cassert>
#include <cmath>
#include <cstdio>

// The native own-player samples showed 106->31 / +13.39m and
// 100->25 / +11.48m, followed by retreat, fresh exploration and another
// world death. This engine-free trajectory keeps those health/launch values;
// it does not claim to reproduce the native damage source or physics.
static void InjuredSearchAfterRetreat(double before,double after,double launch,
                                      bool arrive_before_timeout) {
  botcore::BotProfile profile;
  botcore::BuildProfile(1,0,1135670155u,"Warning replay",&profile);
  botcore::HumanBotPolicy policy;policy.Configure(&profile,true);
  botcore::WorldView w;w.alive=true;w.health=before;w.current_weapon=2;
  w.usable_weapons=1u<<1;
  for(int tick=0;tick<120;++tick) {
    w.tick=tick;w.pose.y=.01;w.pose.z=-tick*.6075;
    policy.BeginTick(w);policy.Step(w,nullptr,nullptr,0,.05);
  }
  w.tick=120;w.health=after;w.pose.y=.01+launch;w.pose.z=-72.9;
  policy.BeginTick(w);
  auto command=policy.Step(w,nullptr,nullptr,0,.05);
  assert(command.escape && !command.fire);
  for(int tick=121;tick<220;++tick) {
    w.tick=tick;
    w.pose.y=tick<140 ? .01+launch*(140-tick)/20 : .01;
    if(arrive_before_timeout) {
      // Oldest position in the policy's 21-sample own history, at tick15.
      w.pose.z+=.7;if(w.pose.z>-9.1125)w.pose.z=-9.1125;
    }
    policy.BeginTick(w);command=policy.Step(w,nullptr,nullptr,0,.05);
    if(command.escape && command.forward>0) {
      assert(policy.AllowFinalMovement(w.pose.x,w.pose.y,w.pose.z,
                                       w.pose.yaw_deg+command.yaw_delta_deg,
                                       command.forward,0));
    }
    w.pose.yaw_deg+=command.yaw_delta_deg;
  }
  w.tick=220;policy.BeginTick(w);
  command=policy.Step(w,nullptr,nullptr,0,.05);
  assert(!command.escape); // arrival and the old100-tick deadline both end retreat
  int scanning=0,pauses=0;
  for(int tick=221;tick<850;++tick) {
    w.tick=tick;policy.BeginTick(w);
    command=policy.Step(w,nullptr,nullptr,0,.05);
    assert(command.travel && command.forward==0 && command.strafe==0);
    assert(command.target==-1 && !command.fire);
    assert(!policy.AllowFinalMovement(w.pose.x,w.pose.y,w.pose.z,w.pose.yaw_deg,.9,0));
    assert(std::fabs(command.yaw_delta_deg)<=profile.skill.search_rate_deg_s*.05+1e-9);
    if(command.yaw_delta_deg!=0)++scanning;else ++pauses;
    w.pose.yaw_deg+=command.yaw_delta_deg;
  }
  assert(scanning>0 && pauses>0); // bounded visual sweeps, not omnidirectional sensing
  w.health=100;
  bool moving=false;
  for(int tick=850;tick<950;++tick) {
    w.tick=tick;policy.BeginTick(w);
    command=policy.Step(w,nullptr,nullptr,0,.05);
    moving=moving || command.forward>0;
    w.pose.yaw_deg+=command.yaw_delta_deg;
  }
  assert(moving); // sufficient observed healing releases the injured hold
}

int main() {
  InjuredSearchAfterRetreat(106,31,13.39,true);
  InjuredSearchAfterRetreat(100,25,11.48,false);
  // Independent analytic cases: 30m away, 30m/s projectile.
  assert(std::fabs(botcore::InterceptTime(30,0,0,0,0,0,30)-1)<1e-9);
  assert(std::fabs(botcore::InterceptTime(30,0,0,-10,0,0,30)-0.75)<1e-9);
  assert(std::fabs(botcore::InterceptTime(30,0,0,10,0,0,30)-1.5)<1e-9);
  assert(std::fabs(botcore::InterceptTime(30,0,0,0,10,0,30)-std::sqrt(1.125))<1e-9);
  assert(botcore::InterceptTime(30,0,0,40,0,0,30)==0);
  assert(botcore::InterceptTime(30,0,0,0,0,0,0)==0);
  assert(botcore::InterceptTime(300,0,0,0,0,0,30)==0); // >2s speculation refused
  assert(botcore::InterceptTime(NAN,0,0,0,0,0,30)==0);
  botcore::BotProfile p;
  botcore::BuildProfile(5, 0, 107, "Danger", &p);
  botcore::HumanBotPolicy policy; policy.Configure(&p);
  botcore::WorldView w; w.alive=true; w.health=100; w.current_weapon=8;
  w.usable_weapons=1u<<7;
  botcore::SenseInput target{}; target.index=1; target.z=-2; target.alive=true;
  bool los=true;
  for (int tick=0; tick<200; ++tick) {
    w.tick=tick; policy.BeginTick(w);
    const auto cmd=policy.Step(w,&target,&los,1,0.05);
    w.pose.yaw_deg+=cmd.yaw_delta_deg; w.pose.pitch_deg+=cmd.pitch_delta_deg;
    assert(!cmd.fire); // even when the only loaded weapon is an explosive
  }
  policy.Reset(); w.pose={}; target.z=-policy.PreferredRange(2); w.current_weapon=2;
  w.usable_weapons=1u<<1;
  int last_sign=0, last_flip=-1, flips=0, previous_gap=-1; bool varied=false;
  for (int tick=0; tick<1600; ++tick) {
    w.tick=tick; policy.BeginTick(w);
    const auto cmd=policy.Step(w,&target,&los,1,0.05);
    w.pose.yaw_deg+=cmd.yaw_delta_deg; w.pose.pitch_deg+=cmd.pitch_delta_deg;
    const int sign=cmd.strafe>0?1:(cmd.strafe<0?-1:0);
    if (sign && last_sign && sign!=last_sign) {
      if (last_flip>=0) {
        const int gap=tick-last_flip;
        if (previous_gap>=0 && gap!=previous_gap) varied=true;
        previous_gap=gap;
      }
      last_flip=tick; ++flips;
    }
    if (sign) last_sign=sign;
  }
  assert(flips>4 && varied); // no fixed-period left/right metronome
  botcore::HumanBotPolicy conservative; conservative.Configure(&p);
  for (int tick=0;tick<600;++tick) {
    w.tick=tick;conservative.BeginTick(w);
    auto c=conservative.Step(w,nullptr,nullptr,0,0.05);
    assert(c.yaw_delta_deg==p.skill.search_rate_deg_s*0.05);
  }
  policy.Configure(&p,true); w.pose={};
  for (int tick=0; tick<600; ++tick) {
    w.tick=tick;policy.BeginTick(w);
    const auto cmd=policy.Step(w,nullptr,nullptr,0,0.05);
    assert(!cmd.fire && cmd.target==-1 && cmd.travel);
    w.pose.yaw_deg+=cmd.yaw_delta_deg;
    w.pose.x-=std::sin(w.pose.yaw_deg*botcore::kDegToRad)*cmd.forward*.5;
    w.pose.z-=std::cos(w.pose.yaw_deg*botcore::kDegToRad)*cmd.forward*.5;
  }
  assert(std::hypot(w.pose.x,w.pose.z)>35); // actual progress between bounded goals
  policy.Configure(&p,true); w.pose={}; w.health=100;
  for (int tick=0; tick<120; ++tick) {
    w.tick=tick;w.pose.z=-tick*0.1;policy.BeginTick(w);
    policy.Step(w,nullptr,nullptr,0,0.05);
  }
  w.tick=120;w.health=25;w.pose.z=-12;policy.BeginTick(w);
  auto flee=policy.Step(w,nullptr,nullptr,0,0.05);
  assert(flee.escape && !flee.fire && flee.forward==0 && flee.yaw_delta_deg!=0);
  // Return to the old, own observed position; no knowledge of hidden damage entity.
  for(int tick=121;tick<230;++tick){
    w.tick=tick;policy.BeginTick(w);flee=policy.Step(w,nullptr,nullptr,0,0.05);
    w.pose.yaw_deg+=flee.yaw_delta_deg;
  }
  assert(!flee.escape); // bounded attempt, never a permanent retreat loop
  std::puts("INTERCEPT PASS");
}
