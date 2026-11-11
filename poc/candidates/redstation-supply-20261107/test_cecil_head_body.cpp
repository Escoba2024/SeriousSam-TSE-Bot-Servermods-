// SPDX-License-Identifier: GPL-2.0-only
// Portable feedback model of Engine107 Player.es:4234-4266, HEADING_MAX=45.
// Models head/body angle transfer, not native physics, collision or ABI.
#include "bot_human.h"
#include <cassert>
#include <cmath>
#include <cstdio>
using namespace botcore;

static void CheckHeadBody(bool alternateMovement,int rotation) {
  BotProfile profile;
  assert(BuildProfile(3,0,123,"head-body",&profile));
  profile.skill.reaction_s=.05;
  profile.skill.aim_sigma_deg=0;
  profile.skill.fov_half_deg=90;
  profile.skill.sight_range_m=200;
  CecilSettings settings=CecilPreset(2);
  settings.fAccuracyAngle=0;settings.fTargetCD=1;
  HumanBotPolicy human;human.Configure(&profile,&settings);
  WorldView world;
  world.cecil=true;world.alive=true;world.health=100;world.current_weapon=6;
  world.usable_weapons=CecilWeaponMask(6);
  SenseInput enemy;
  enemy.index=1;enemy.entity_id=11;enemy.generation=1;
  enemy.alive=true;enemy.health=100;
  CecilFrame base;
  if(rotation==1){base.up[1]=-1;base.back[2]=-1;}
  if(rotation==2){
    base.right[0]=.5;base.right[1]=std::sqrt(.75);
    base.up[0]=-std::sqrt(.75);base.up[1]=.5;
  }
  assert(base.Valid());world.pose.frame=base;
  int shots=0;bool los=true;
  for(int tick=0;tick<2000;++tick) {
    const auto point=base.ToWorld(-80+3*std::sin(tick*.005),4,-20);
    const auto speed=base.ToWorld(.3*std::cos(tick*.005),0,0);
    enemy.x=point.x;enemy.y=point.y;enemy.z=point.z;
    enemy.vx=speed.x;enemy.vy=speed.y;enemy.vz=speed.z;
    world.tick=tick;human.BeginTick(world);
    const auto command=human.Step(world,&enemy,&los,1,.05);
    assert(std::isfinite(command.yaw_delta_deg)&&std::isfinite(command.pitch_delta_deg));
    world.pose.yaw_deg+=command.yaw_delta_deg;
    world.pose.pitch_deg+=command.pitch_delta_deg;
    // A blocked/stationary player keeps head yaw until the +/-45 degree limit.
    // Translation transfers all remaining head yaw to the body, then zeros it.
    const bool translating=alternateMovement&&tick%100>=50;
    const double bodyTurn=translating?world.pose.yaw_deg:
      std::fmax(0.,world.pose.yaw_deg-45)+std::fmin(0.,world.pose.yaw_deg+45);
    world.pose.yaw_deg-=bodyTurn;
    const double angle=bodyTurn*std::acos(-1.)/180.;
    const auto old=world.pose.frame;
    for(int k=0;k<3;++k) {
      world.pose.frame.right[k]=std::cos(angle)*old.right[k]-std::sin(angle)*old.back[k];
      world.pose.frame.back[k]=std::sin(angle)*old.right[k]+std::cos(angle)*old.back[k];
    }
    assert(world.pose.frame.Valid());
    assert(std::fabs(world.pose.yaw_deg)<=45+1e-9);
    if(tick>100&&command.fire)++shots;
  }
  assert(shots>1500);
  const auto* observed=human.perception().Track(1);
  assert(observed&&observed->x==enemy.x&&observed->y==enemy.y&&observed->z==enemy.z);
  const auto before=*observed;
  // Changing the local frame while an enemy moves unseen must not rotate,
  // refresh or extrapolate the remembered world-space position.
  los=false;enemy.x=10000;world.pose.frame=CecilFrame();
  world.tick=2000;human.BeginTick(world);
  const auto hidden=human.Step(world,&enemy,&los,1,.05);
  const auto* after=human.perception().Track(1);
  assert(after&&after->x==before.x&&after->y==before.y&&after->z==before.z);
  assert(after->vx==0&&after->vy==0&&after->vz==0&&!hidden.fire);
  std::printf("head/body movement=%d frame=%d fire_ticks=%d memory=world-frozen\n",
              alternateMovement,rotation,shots);
}

int main() {
  for(int movement=0;movement<2;++movement)
    for(int rotation=0;rotation<3;++rotation)CheckHeadBody(movement!=0,rotation);
}
