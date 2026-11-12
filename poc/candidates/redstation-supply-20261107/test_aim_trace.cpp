#include "bot_human.h"
#include <cassert>
#include <cmath>
#include <cstdio>
using namespace botcore;
static void same(const BotCommand&a,const BotCommand&b){
 assert(a.target==b.target&&a.target_visible==b.target_visible&&a.fire==b.fire&&a.weapon==b.weapon);
 assert(a.yaw_delta_deg==b.yaw_delta_deg&&a.pitch_delta_deg==b.pitch_delta_deg&&a.aim_error_deg==b.aim_error_deg);
 assert(a.forward==b.forward&&a.strafe==b.strafe&&a.distance_m==b.distance_m&&a.preferred_range_m==b.preferred_range_m);
}
int main(){
 AimController plain,traced;plain.Configure(ArenaSkill(1),123);traced.Configure(ArenaSkill(1),123);
 for(int i=0;i<4000;++i){
  AimPose pose;pose.yaw_deg=i%2?70:0;pose.pitch_deg=std::sin(i*.03)*3;
  AimPoint p;p.valid=i%17!=0;p.target_key=(i/71)%3;p.visible_now=i%7!=0;p.x=std::sin(i*.02)*20;p.y=2;p.z=-30;
  AimTrace trace;auto a=plain.Step(pose,p,.05),b=traced.Step(pose,p,.05,&trace);
  assert(a.yaw_delta_deg==b.yaw_delta_deg&&a.pitch_delta_deg==b.pitch_delta_deg&&a.residual_error_deg==b.residual_error_deg&&a.fire_allowed==b.fire_allowed);
  assert(trace.valid==p.valid);
  if(trace.valid){assert(trace.pose.yaw_deg==pose.yaw_deg&&trace.point.x==p.x);assert(trace.rate_after[0]*.05==b.yaw_delta_deg);
   double ry=AimController::WrapDeg(trace.desired[0]-(pose.yaw_deg+b.yaw_delta_deg)),rp=trace.desired[1]-(pose.pitch_deg+b.pitch_delta_deg);
   assert(ry==trace.residual[0]&&rp==trace.residual[1]);assert(std::sqrt(ry*ry+rp*rp)==b.residual_error_deg);
   assert(trace.error[0]==AimController::WrapDeg(trace.desired[0]+trace.bias[0]+trace.offset[0]-pose.yaw_deg));
  }
 }
 AimTrace reused;AimPose good;AimPoint target;target.valid=true;target.z=-10;
 traced.Step(good,target,.05,&reused);assert(reused.valid);
 traced.Step(good,AimPoint(),.05,&reused);assert(!reused.valid&&reused.dt==0);
 good.yaw_deg=std::nan("");traced.Step(good,target,.05,&reused);assert(!reused.valid);
 traced.Step(AimPose(),target,0,&reused);assert(!reused.valid);
 HumanBotPolicy a,b;BotProfile profile;assert(BuildProfile(1,2,2026110750,"MITTEL",&profile));profile.arena=true;profile.skill=ArenaSkill(1);CecilSettings settings=CecilPreset(2);a.Configure(&profile,&settings);b.Configure(&profile,&settings);
 int valid=0;
 for(int tick=1;tick<=4000;++tick){
  WorldView w;w.cecil=tick%2==0;w.tick=tick;w.alive=tick%503>3;w.health=100;w.current_weapon=tick%61<5?2:14;w.usable_weapons=(1u<<1)|(1u<<13);w.pose.yaw_deg=tick%2?70:0;
  SenseInput s[2];bool los[2]={tick%11!=0,tick%13!=0};
  for(int i=0;i<2;++i){s[i].index=i;s[i].entity_id=100+i;s[i].generation=1;s[i].alive=true;s[i].enemy=true;s[i].health=100;s[i].x=std::sin(tick*.01+i)*10;s[i].y=2;s[i].z=-20-i*10;s[i].vx=2;}
  a.BeginTick(w);b.BeginTick(w);bool qa[2],qb[2];a.PlanLosQueries(s,2,qa);b.PlanLosQueries(s,2,qb);assert(qa[0]==qb[0]&&qa[1]==qb[1]);
  HumanAimTrace tr;auto ca=a.Step(w,s,los,2,.05),cb=b.Step(w,s,los,2,.05,&tr);same(ca,cb);
  assert(a.aim().yaw_rate()==b.aim().yaw_rate()&&a.aim().bias_yaw_deg()==b.aim().bias_yaw_deg()&&a.target_switches()==b.target_switches());
  if(tr.aim.valid){++valid;assert(tr.aim.point.target_key==cb.target&&tr.track.index==cb.target);assert(tr.settled_after>=-1);}
 }
 assert(valid>100);
 std::puts("AIM TRACE 8000 multi-tick parity/geometry checks PASS");
}
