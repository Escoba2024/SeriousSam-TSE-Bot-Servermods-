#include "bot_human.h"
#include <cassert>
#include <cmath>
#include <cstdio>
#include <initializer_list>
using namespace botcore;
struct Fixture {
  BotProfile profile; CecilSettings settings=CecilPreset(2); HumanBotPolicy human;
  WorldView world;SenseInput enemies[2]{};bool los[2]={true,true};
  Fixture(){
    assert(BuildProfile(3,0,123,"cecil-test",&profile));
    profile.skill.reaction_s=.05;profile.skill.aim_sigma_deg=0;
    profile.skill.fov_half_deg=90;profile.skill.sight_range_m=200;
    settings.fAccuracyAngle=0;settings.fTargetCD=1;
    world.cecil=true;world.alive=true;world.health=100;world.current_weapon=6;
    world.usable_weapons=CecilWeaponMask(6);
    for(int i=0;i<2;++i){auto& e=enemies[i];e.index=i+1;e.entity_id=11+i;
      e.generation=1;e.alive=true;e.health=100;e.z=-30;}
    Configure();
  }
  void Configure(){human.Configure(&profile,&settings);}
  BotCommand Tick(int t){world.tick=t;human.BeginTick(world);return human.Step(world,enemies,los,2,.05);}
};
static int FeedbackFire(bool moving) {
  Fixture f;f.enemies[1].alive=false;f.enemies[0].x=10;f.enemies[0].z=-40;
  int shots=0;
  for(int tick=0;tick<2000;++tick) {
    if(moving){f.enemies[0].x=10+3*std::sin(tick*.05*.1);
      f.enemies[0].vx=.3*std::cos(tick*.05*.1);}
    BotCommand cmd=f.Tick(tick);
    f.world.pose.yaw_deg+=cmd.yaw_delta_deg;
    f.world.pose.pitch_deg+=cmd.pitch_delta_deg;
    if(tick>100&&cmd.fire) {
      ++shots;assert(cmd.aim_error_deg<=f.human.profile().skill.fire_tol_deg);
    }
  }
  std::printf("feedback %s: %d fire ticks after warmup\n",moving?"slow":"stationary",shots);
  return shots;
}
static void BodyFrameFeedback() {
  for(int rotation=0;rotation<3;++rotation) {
    Fixture f;f.enemies[1].alive=false;
    CecilFrame base;
    if(rotation==1){base.up[1]=-1;base.back[2]=-1;}
    if(rotation==2){base.right[0]=.5;base.right[1]=std::sqrt(.75);base.up[0]=-std::sqrt(.75);base.up[1]=.5;}
    assert(base.Valid());f.world.pose.frame=base;
    int shots=0;
    for(int tick=0;tick<2000;++tick) {
      const auto target=base.ToWorld(10+3*std::sin(tick*.005),4,-40);
      const auto speed=base.ToWorld(.3*std::cos(tick*.005),0,0);
      auto& enemy=f.enemies[0];enemy.x=target.x;enemy.y=target.y;enemy.z=target.z;
      enemy.vx=speed.x;enemy.vy=speed.y;enemy.vz=speed.z;
      BotCommand cmd=f.Tick(tick);
      const double angle=cmd.yaw_delta_deg*std::acos(-1.0)/180;
      const auto old=f.world.pose.frame;
      for(int k=0;k<3;++k){
        f.world.pose.frame.right[k]=std::cos(angle)*old.right[k]-std::sin(angle)*old.back[k];
        f.world.pose.frame.back[k]=std::sin(angle)*old.right[k]+std::cos(angle)*old.back[k];
      }
      f.world.pose.pitch_deg+=cmd.pitch_delta_deg;
      // Native stationary head yaw can be transferred to body orientation.
      if(tick%100==50){
        f.world.pose.yaw_deg=20;
        const auto b=f.world.pose.frame;const double a=-20*std::acos(-1.0)/180;
        for(int k=0;k<3;++k){f.world.pose.frame.right[k]=std::cos(a)*b.right[k]-std::sin(a)*b.back[k];f.world.pose.frame.back[k]=std::sin(a)*b.right[k]+std::cos(a)*b.back[k];}
      }
      if(tick%100==51){
        const auto b=f.world.pose.frame;const double a=f.world.pose.yaw_deg*std::acos(-1.0)/180;
        for(int k=0;k<3;++k){f.world.pose.frame.right[k]=std::cos(a)*b.right[k]-std::sin(a)*b.back[k];f.world.pose.frame.back[k]=std::sin(a)*b.right[k]+std::cos(a)*b.back[k];}
        f.world.pose.yaw_deg=0;
      }
      if(tick>100&&cmd.fire)++shots;
    }
    assert(shots>1000);
    const auto* track=f.human.perception().Track(1);
    assert(track&&std::fabs(track->x-f.enemies[0].x)<1e-10&&std::fabs(track->y-f.enemies[0].y)<1e-10);
    const double rememberedX=track->x;
    f.world.pose.frame.right[0]=NAN;
    const auto invalid=f.Tick(2001);
    assert(!invalid.fire&&invalid.forward==0&&invalid.strafe==0&&invalid.yaw_delta_deg==0&&invalid.pitch_delta_deg==0&&std::isfinite(invalid.aim_error_deg));
    assert(f.human.perception().Track(1)->x==rememberedX);
    f.world.pose.frame=base;f.world.pose.x=NAN;
    const auto invalidPose=f.Tick(2002);assert(!invalidPose.fire&&invalidPose.forward==0&&invalidPose.yaw_delta_deg==0);
    std::printf("body frame %d: %d fire ticks after warmup\n",rotation,shots);
  }
}
int main(){
  BodyFrameFeedback();
  const int stationary=FeedbackFire(false),moving=FeedbackFire(true);
  assert(stationary>0&&moving>0);

  CecilSettings turn=CecilPreset(2);
  assert(CecilTurnLimit(turn,40,20,.05)==10); // .1 s rotation time
  assert(CecilTurnLimit(turn,400,20,.05)==5); // max .2 s
  assert(CecilTurnLimit(turn,0,90,.05)==30);  // min .05 s, 30 degree error cap
  turn.fRotSpeedDist=800;assert(CecilTurnLimit(turn,40,20,.05)==20);
  turn.fRotSpeedMax=.4;assert(CecilTurnLimit(turn,800,20,.05)==2.5);
  assert(CecilTurnLimit(turn,800,20,.1)==5); // degrees/sec -> per-action delta
  turn.fRotSpeedLimit=-1;assert(CecilTurnLimit(turn,0,90,.05)==90);
  assert(CecilTurnLimit(turn,0,20,0)==0);

  // Original candidate voting: the closer but healthier player does not beat
  // a candidate that met visibility+health+distance; enumeration is stable slots.
  Fixture f;f.enemies[1].health=200;f.enemies[1].z=-10;
  assert(f.Tick(0).target==-1);assert(f.Tick(1).target==1);
  // A newly superior candidate waits the full preset cooldown, not reaction_s.
  f.enemies[1].health=20;
  for(int t=2;t<=20;++t)assert(f.Tick(t).target==1);
  assert(f.Tick(21).target==2);
  // Death invalidates a lock immediately; replacement identity needs reaction.
  f.enemies[1].alive=false;assert(f.Tick(22).target==1);
  f.enemies[0].entity_id=99;assert(f.Tick(23).target==-1);
  assert(f.Tick(24).target==1);
  // Losing LOS preserves only the frozen Human observation and never fires.
  f.los[0]=false;f.enemies[0].x=100;f.enemies[0].health=1;
  BotCommand hidden=f.Tick(25);assert(hidden.target==1&&!hidden.fire&&!hidden.target_visible);
  const TrackState* remembered=f.human.perception().Track(1);
  assert(remembered&&remembered->x==0&&remembered->health==100);
  // A fresh, reacted visible candidate wins over remembered state before CD.
  f.enemies[1].alive=true;assert(f.Tick(26).target==1);
  assert(f.Tick(27).target==2);
  // Settings disable combat acquisition without disturbing the Human profile.
  Fixture disabled;disabled.settings.bTargetSearch=0;disabled.Configure();
  for(int t=0;t<30;++t)assert(disabled.Tick(t).target==-1);
  disabled.settings.bTargetSearch=1;disabled.settings.iTargetType=1;disabled.Configure();
  for(int t=0;t<30;++t)assert(disabled.Tick(t).target==-1); // monster-only in DM
  for(int preset=0;preset<4;++preset){
    Fixture p;p.settings=CecilPreset(preset);p.Configure();
    assert(p.human.profile().skill.weapon_dwell_s==p.settings.fWeaponCD);
    assert(std::fabs(p.human.profile().skill.aim_sigma_deg-p.settings.fAccuracyAngle/std::sqrt(12.0))<1e-12);
    assert(p.human.profile().skill.reaction_s==p.profile.skill.reaction_s);
    assert(p.human.profile().skill.turn_accel_deg_s2==p.profile.skill.turn_accel_deg_s2);
    assert(p.human.profile().skill.fire_tol_deg<=p.settings.fShootAngle);
    if(!p.settings.bStrafe)assert(p.human.profile().personality.strafe_bias==0);
    for(int t=0;t<40;++t){BotCommand cmd=p.Tick(t);if(!p.settings.bShooting)assert(!cmd.fire);}
  }
  // Cecil speed/strafe gates apply after the Human retreat decision.
  Fixture retreat;retreat.world.health=1;retreat.settings.fSpeedMul=.5;
  retreat.settings.bStrafe=0;retreat.Configure();retreat.Tick(0);
  BotCommand escape=retreat.Tick(1);assert(escape.forward<0&&escape.forward>=-.5&&escape.strafe==0);
  // Weapon restrictions reach loadout as well as the final native fire gate.
  Fixture restricted;restricted.world.usable_weapons|=CecilWeaponMask(8);
  restricted.settings.iAllowedWeapons=CecilWeaponMask(6);restricted.Configure();
  restricted.Tick(0);assert(restricted.Tick(1).weapon==6);
  // Original fixed-time prediction is deterministic and remains visible-only.
  Fixture noLead,lead,repeat;noLead.settings.fPrediction=0;noLead.settings.fPredictRnd=0;
  lead.settings.fPrediction=.5;lead.settings.fPredictRnd=.1;repeat.settings=lead.settings;
  noLead.Configure();lead.Configure();repeat.Configure();
  for(auto* p:{&noLead,&lead,&repeat}){p->enemies[0].vx=10;p->enemies[1].alive=false;}
  BotCommand a,b,c;
  for(int t=0;t<30;++t){a=noLead.Tick(t);b=lead.Tick(t);c=repeat.Tick(t);assert(b.yaw_delta_deg==c.yaw_delta_deg);}
  assert(std::fabs(b.yaw_delta_deg-a.yaw_delta_deg)>1e-6);
  Fixture limited;limited.settings.fRotSpeedDist=10;limited.settings.fRotSpeedMax=2;
  limited.settings.fRotSpeedMin=.1;limited.enemies[0].x=10;limited.enemies[1].alive=false;
  limited.Configure();limited.Tick(0);
  const double error=std::atan2(10.0,30.0)*kRadToDeg;
  const double cap=CecilTurnLimit(limited.settings,std::sqrt(1000.0),error,.05);
  for(int t=1;t<10;++t){BotCommand cmd=limited.Tick(t);
    assert(std::fabs(cmd.yaw_delta_deg)<=cap+1e-12&&!cmd.fire);
    assert(std::fabs(cmd.aim_error_deg-(error-std::fabs(cmd.yaw_delta_deg)))<1e-10);
  }
  Fixture ceiling;ceiling.settings.fRotSpeedLimit=1;ceiling.settings.fRotSpeedMin=.1;
  ceiling.Configure();assert(ceiling.human.profile().skill.turn_rate_deg_s==10);
  assert(ceiling.human.profile().skill.turn_accel_deg_s2==ceiling.profile.skill.turn_accel_deg_s2);
  // No settings argument leaves the existing Human profile byte-for-field behavior.
  HumanBotPolicy legacy;legacy.Configure(&f.profile);
  assert(legacy.profile().skill.aim_sigma_deg==f.profile.skill.aim_sigma_deg);
  assert(legacy.profile().skill.weapon_dwell_s==f.profile.skill.weapon_dwell_s);
  puts("Cecil Human target/preset contracts PASS");
}
