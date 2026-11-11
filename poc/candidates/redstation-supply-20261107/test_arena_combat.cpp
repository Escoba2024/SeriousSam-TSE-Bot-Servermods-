// Portable policy contracts; does not establish native damage or difficulty.
#include "bot_human.h"
#include <cassert>
#include <cstdio>
using namespace botcore;
static BotProfile Roster(int index) {
  BotProfile p{};assert(BuildRosterProfile(index,index%4,77123,&p));return p;
}
static void MigrationAndConfiguration() {
  const int tiers[]={1,1,1,1,1,1,2,3};
  for(int i=0;i<8;++i){auto p=Roster(i);assert(p.tier==tiers[i]);
    assert(ValidateProfile(p)==ProfileError::kOk);
    assert(p.persona==2); // one shared arena tactical policy, no mood roulette
    auto again=Roster(i);assert(p.seed==again.seed);
  }
  assert(Roster(0).seed!=Roster(1).seed);
  BotProfile chosen{};
  for(int tier=1;tier<=3;++tier){assert(BuildRosterProfile(0,0,77123,&chosen,tier));assert(chosen.tier==tier);}
  assert(!BuildRosterProfile(0,0,77123,&chosen,4));
  assert(!BuildRosterProfile(0,0,77123,&chosen,-1));
  assert(!BuildRosterProfile(0,0,77123,nullptr));
  for(int preset=0;preset<4;++preset){
    const auto settings=CecilPreset(preset);
    HumanBotPolicy medium,strong,demon;
    auto a=Roster(0),b=Roster(6),c=Roster(7);
    medium.Configure(&a,&settings);strong.Configure(&b,&settings);demon.Configure(&c,&settings);
    const auto& x=medium.profile().skill;const auto& y=strong.profile().skill;const auto& z=demon.profile().skill;
    assert(x.reaction_s>y.reaction_s&&y.reaction_s>z.reaction_s);
    assert(x.aim_sigma_deg>y.aim_sigma_deg&&y.aim_sigma_deg>z.aim_sigma_deg);
    assert(x.turn_rate_deg_s<y.turn_rate_deg_s&&y.turn_rate_deg_s<z.turn_rate_deg_s);
    assert(x.tracking_gain_s<y.tracking_gain_s&&y.tracking_gain_s<z.tracking_gain_s);
    assert(x.max_los_per_tick==z.max_los_per_tick&&x.sight_range_m==z.sight_range_m);
    assert(x.weapon_dwell_s==a.skill.weapon_dwell_s);
  }
  for(int tier=1;tier<=5;++tier)assert(SkillFor(tier).tracking_gain_s==10);
  auto invalid=Roster(7);invalid.skill.tracking_gain_s=21;
  assert(ValidateProfile(invalid)==ProfileError::kTrackingGainOutOfRange);
  invalid.skill.tracking_gain_s=NAN;assert(ValidateProfile(invalid)==ProfileError::kNonFinite);
}
static BotCommand Run(HumanBotPolicy& policy,WorldView& w,SenseInput* enemies,bool* los,int tick,int count=2){
  w.tick=tick;policy.BeginTick(w);return policy.Step(w,enemies,los,count,.05);
}
static void ShortColtsAndOwnership() {
  auto p=Roster(7);HumanBotPolicy h;auto settings=CecilPreset(2);h.Configure(&p,&settings);
  WorldView w;w.cecil=true;w.alive=true;w.health=100;w.current_weapon=3;
  w.usable_weapons=CecilWeaponMask(1)|CecilWeaponMask(3);
  SenseInput e[2]{};bool los[2]={true,true};
  for(int i=0;i<2;++i){e[i].index=i+1;e[i].entity_id=i+10;e[i].alive=true;e[i].health=100;}
  e[0].z=-50;e[0].health=10;e[1].z=-10;
  BotCommand cmd;
  for(int t=0;t<80;++t)cmd=Run(h,w,e,los,t);
  assert(cmd.target==2&&cmd.weapon==3); // nearby fight beats distant low-HP bait
  e[1].alive=false;
  for(int t=80;t<140;++t){cmd=Run(h,w,e,los,t);assert(!cmd.fire&&cmd.target==-1&&cmd.forward==0);}
  w.usable_weapons|=CecilWeaponMask(6);w.current_weapon=6;
  bool fired=false;
  for(int t=140;t<240;++t){cmd=Run(h,w,e,los,t);fired|=cmd.fire;}
  assert(cmd.target==1&&cmd.weapon==6&&fired);
  los[0]=false;
  for(int t=240;t<260;++t)assert(!Run(h,w,e,los,t).fire);
  // A disallowed long-range gun must not bypass the Colt gate.
  settings.iAllowedWeapons=CecilWeaponMask(1)|CecilWeaponMask(3);h.Configure(&p,&settings);
  los[0]=true;
  for(int t=0;t<80;++t){cmd=Run(h,w,e,los,t);assert(!cmd.fire&&cmd.target==-1);}
  // Reference data stays the original Cecil table; our arena policy is separate.
  assert(CecilWeaponScore(3,100)>0);
}
static void ReactionIsolationAndLifetime() {
  auto settings=CecilPreset(2);
  HumanBotPolicy bots[3];WorldView worlds[3];
  SenseInput e{};e.index=1;e.entity_id=10;e.alive=true;e.health=100;e.z=-10;e.local=true;
  bool los=true;const int roster[]={0,6,7},expected[]={4,2,1};
  for(int i=0;i<3;++i){auto p=Roster(roster[i]);bots[i].Configure(&p,&settings);
    worlds[i].cecil=true;worlds[i].alive=true;worlds[i].health=100;worlds[i].usable_weapons=CecilWeaponMask(6);worlds[i].current_weapon=6;}
  for(int tick=0;tick<12;++tick)for(int i=0;i<3;++i){
    auto cmd=Run(bots[i],worlds[i],&e,&los,tick,1);
    assert((cmd.target>=0)==(tick>=expected[i])); // no shared reaction state; sibling is an enemy
  }
  worlds[0].alive=false;Run(bots[0],worlds[0],&e,&los,12,1);
  assert(bots[0].target()==-1&&bots[0].weapons().current()==0);
  assert(Run(bots[1],worlds[1],&e,&los,12,1).target==1);
  e.alive=false;
  for(int i=0;i<3;++i){auto cmd=Run(bots[i],worlds[i],&e,&los,13,1);assert(cmd.target==-1&&!cmd.fire);}
  e.alive=true;e.entity_id=11;
  assert(Run(bots[2],worlds[2],&e,&los,14,1).target==-1);
  assert(Run(bots[2],worlds[2],&e,&los,15,1).target==1); // no special spawn grace
  settings.bShooting=0;auto p=Roster(7);bots[2].Configure(&p,&settings);
  for(int t=0;t<40;++t)assert(!Run(bots[2],worlds[2],&e,&los,t,1).fire);
  settings.bShooting=1;bots[2].Configure(&p,&settings);worlds[2].deathmatch=false;
  for(int t=0;t<40;++t)assert(!Run(bots[2],worlds[2],&e,&los,t,1).fire);
}
static void HumanOnlyArenaLoadout() {
  // HumanAI without SupplyNavigation must use the same feasible weapon set.
  auto profile=Roster(7);WeaponSelector selector;selector.Configure(profile.skill);
  LoadoutInput in;in.arena=true;in.has_target=true;in.distance_m=90;
  in.usable_mask=CecilWeaponMask(1)|CecilWeaponMask(6);
  assert(selector.Update(in,0)==6); // no fallback knife at a valid ranged target
}
static void TrackingAndBounds() {
  const int roster[]={0,6,7};
  for(int rotation=0;rotation<3;++rotation){
    for(int i=0;i<3;++i){
      auto p=Roster(roster[i]);auto settings=CecilPreset(2);HumanBotPolicy h;h.Configure(&p,&settings);
      WorldView w;w.cecil=true;w.alive=true;w.health=100;w.current_weapon=6;w.usable_weapons=CecilWeaponMask(6);
      if(rotation==1){w.pose.frame.up[1]=-1;w.pose.frame.back[2]=-1;}
      if(rotation==2){w.pose.frame.right[0]=.5;w.pose.frame.right[1]=std::sqrt(.75);w.pose.frame.up[0]=-std::sqrt(.75);w.pose.frame.up[1]=.5;}
      SenseInput e{};e.index=1;e.entity_id=10;e.alive=true;e.health=100;bool los=true;int fired=0;
      for(int tick=0;tick<600;++tick){
        auto point=w.pose.frame.ToWorld(3*std::sin(tick*.04),1,-20);
        e.x=point.x;e.y=point.y;e.z=point.z;
        auto cmd=Run(h,w,&e,&los,tick,1);
        assert(std::fabs(cmd.yaw_delta_deg)<=p.skill.turn_rate_deg_s*.05+1e-9);
        assert(std::fabs(cmd.pitch_delta_deg)<=p.skill.turn_rate_deg_s*.05+1e-9);
        w.pose.yaw_deg+=cmd.yaw_delta_deg;w.pose.pitch_deg+=cmd.pitch_delta_deg;
        if(tick>100&&cmd.fire)++fired;
      }
      assert(fired>100); // all tiers can track/fire; no stronger native-tier claim
      std::printf("arena frame=%d tier=%d tracking fire_ticks=%d\n",rotation,i+1,fired);
    }
  }
}
static void MovingTargetFire() {
  // Same seed/start/target for each tier. This 20 deg/s crossing exposed the
  // pre-turn trigger bug: DEMON tracked within tolerance but fired 7/699 ticks.
  for(double speed:{20.,40.,60.}){
  int totals[3]={};double errors[3]={};
  for(unsigned seed:{123u,77123u,20261111u})for(int tier=1;tier<=3;++tier){
    BotProfile p;assert(BuildRosterProfile(0,0,seed,&p,tier));
    auto settings=CecilPreset(2);HumanBotPolicy h;h.Configure(&p,&settings);
    WorldView w;w.cecil=true;w.alive=true;w.health=100;
    w.current_weapon=6;w.usable_weapons=CecilWeaponMask(6);
    SenseInput e{};e.index=1;e.entity_id=1;e.health=100;e.alive=true;bool los=true;
    int fired=0,aligned=0;double previous_yaw=0,previous_pitch=0;
    for(int t=0;t<800;++t){
      const double angle=std::asin(std::sin(t*.05*speed*kDegToRad));
      e.x=-30*std::sin(angle);e.z=-30*std::cos(angle);
      auto cmd=Run(h,w,&e,&los,t,1);
      assert(!cmd.fire||cmd.aim_error_deg<=p.skill.fire_tol_deg);
      if(cmd.target>=0&&t>10){
        assert(std::fabs(cmd.yaw_delta_deg-previous_yaw)<=p.skill.turn_accel_deg_s2*.05*.05+1e-9);
        assert(std::fabs(cmd.pitch_delta_deg-previous_pitch)<=p.skill.turn_accel_deg_s2*.05*.05+1e-9);
      }
      previous_yaw=cmd.yaw_delta_deg;previous_pitch=cmd.pitch_delta_deg;
      w.pose.yaw_deg+=cmd.yaw_delta_deg;w.pose.pitch_deg+=cmd.pitch_delta_deg;
      if(t>100){fired+=cmd.fire;aligned+=cmd.aim_error_deg<=p.skill.fire_tol_deg;
        errors[tier-1]+=cmd.aim_error_deg;}
    }
    if(tier==3)assert(fired>600); // sustained aligned tracking must not starve trigger
    totals[tier-1]+=fired;
    std::printf("arena crossing speed=%.0f seed=%u tier=%d fire=%d aligned=%d\n",speed,seed,tier,fired,aligned);
  }
  assert(totals[0]<totals[1]&&totals[1]<totals[2]);
  assert(errors[0]>errors[1]&&errors[1]>errors[2]);
  std::printf("arena aggregate speed=%.0f fire=%d/%d/%d mean_error=%.3f/%.3f/%.3f\n",
    speed,totals[0],totals[1],totals[2],errors[0]/2097,errors[1]/2097,errors[2]/2097);
  }
}
static void TriggerLifetime() {
  auto settings=CecilPreset(2);
  for(int tier=1;tier<=3;++tier){
    BotProfile p;assert(BuildRosterProfile(0,0,123,&p,tier));
    // Remove motor noise to measure settle duration separately from tracking.
    p.skill.aim_sigma_deg=0;p.skill.reaction_s=0;
    HumanBotPolicy h;h.Configure(&p,&settings);
    WorldView w;w.cecil=true;w.alive=true;w.health=100;
    w.current_weapon=6;w.usable_weapons=CecilWeaponMask(6);
    SenseInput e{};e.index=1;e.entity_id=1;e.health=100;e.alive=true;e.z=-20;
    bool los=true;int tick=0;
    for(;tick<10;++tick)Run(h,w,&e,&los,tick,1);
    assert(Run(h,w,&e,&los,tick++,1).fire);
    los=false;assert(!Run(h,w,&e,&los,tick++,1).fire);los=true;
    assert(Run(h,w,&e,&los,tick++,1).target==-1); // minimum one-tick reacquisition
    for(int consecutive=0;consecutive<3;++consecutive)
      assert(Run(h,w,&e,&los,tick++,1).fire==(consecutive>=3-tier));
    // A rejected frame cannot leave an old settle window armed.
    w.pose.x=NAN;assert(!Run(h,w,&e,&los,tick++,1).fire);w.pose.x=0;
    assert(Run(h,w,&e,&los,tick++,1).target==-1);
    for(int consecutive=0;consecutive<3;++consecutive)
      assert(Run(h,w,&e,&los,tick++,1).fire==(consecutive>=3-tier));
    for(double invalid:{INFINITY,NAN}){
      w.tick=tick++;h.BeginTick(w);assert(!h.Step(w,&e,&los,1,invalid).fire);
    }
    // No trigger while the engine still holds the previous weapon.
    w.current_weapon=1;assert(!Run(h,w,&e,&los,tick++,1).fire);
    w.current_weapon=6;
    for(int consecutive=0;consecutive<3;++consecutive)
      assert(Run(h,w,&e,&los,tick++,1).fire==(consecutive>=3-tier));
  }
}
static void TriggerIsolation() {
  BotProfile profile;assert(BuildRosterProfile(0,0,123,&profile,1));profile.skill.aim_sigma_deg=0;
  auto settings=CecilPreset(2);HumanBotPolicy policies[2];WorldView worlds[2];
  for(int i=0;i<2;++i){policies[i].Configure(&profile,&settings);worlds[i].cecil=true;
    worlds[i].alive=true;worlds[i].health=100;worlds[i].current_weapon=6;worlds[i].usable_weapons=CecilWeaponMask(6);}
  SenseInput e{};e.index=1;e.entity_id=1;e.alive=true;e.health=100;e.z=-20;
  for(int tick=0;tick<30;++tick)for(int i=0;i<2;++i){
    bool los=i==1||tick<20;
    if(i==0&&tick==25)worlds[i].alive=false;
    auto cmd=Run(policies[i],worlds[i],&e,&los,tick,1);
    if(tick>=10)assert(cmd.fire==(i==1||tick<20));
  }
}
int main(){MigrationAndConfiguration();ShortColtsAndOwnership();ReactionIsolationAndLifetime();HumanOnlyArenaLoadout();TrackingAndBounds();MovingTargetFire();TriggerLifetime();TriggerIsolation();puts("Arena migration, tier and short-Colt contracts PASS");}
