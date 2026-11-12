// Real policy feedback using original Retail zoom scaling; no native simulation claim.
#include "bot_human.h"
#include <cassert>
#include <cmath>
#include <cstdio>
#include <limits>
using namespace botcore;
// Allows this same regression to execute against the pre-fix WorldView: the
// old policy has no damping input and must fail the behavioral assertion.
template<class T> auto Damping(T& w,double value,int)->decltype(w.rotation_damping=value,void()){w.rotation_damping=value;}
template<class T> void Damping(T&,double,long){}
static double Expected(const HumanAimTrace& trace,const BotCommand& cmd,double scale){
  const double yaw=AimController::WrapDeg(trace.aim.desired[0]-trace.aim.pose.yaw_deg-cmd.yaw_delta_deg*scale);
  const double pitch=trace.aim.desired[1]-trace.aim.pose.pitch_deg-cmd.pitch_delta_deg*scale;
  return std::sqrt(yaw*yaw+pitch*pitch);
}
static BotCommand Tick(HumanBotPolicy& h,WorldView&w,SenseInput&e,int tick,HumanAimTrace*trace){
  w.tick=tick;h.BeginTick(w);const bool los=true;return h.Step(w,&e,&los,1,.05,trace);
}
static void NativeResidualFixtures(){
  struct Row {double poseYaw,posePitch,desiredYaw,desiredPitch,yaw,pitch,oldError,newError;};
  // Actual014 local3/gen5 Sniper13 FIRE ticks572/576/577. Geometry is the
  // same stored point at decision time, not a fabricated native hit result.
  const Row rows[]={
    {0,1.25059104,-.558354275,-.832914861,-.501141529,-.898870477,1.18601618,1.84820508},
    {0,.567957342,-1.1075563,-.918703495,.0829847461,-.603866834,1.48213131,1.72377336},
    {0,.380087733,-1.38474018,-.943024087,-.409201847,-.479042122,1.29001112,1.72034683}
  };
  for(int frame=0;frame<3;++frame)for(const auto&r:rows){
    AimPose pose;pose.yaw_deg=r.poseYaw;pose.pitch_deg=r.posePitch;
    if(frame==1){pose.frame.up[1]=-1;pose.frame.back[2]=-1;}
    if(frame==2){pose.frame.right[0]=.5;pose.frame.right[1]=std::sqrt(.75);pose.frame.up[0]=-std::sqrt(.75);pose.frame.up[1]=.5;}
    const double y=r.desiredYaw*kDegToRad,p=r.desiredPitch*kDegToRad;
    const auto v=pose.frame.ToWorld(-50*std::sin(y)*std::cos(p),50*std::sin(p),-50*std::cos(y)*std::cos(p));
    AimPoint point;point.valid=true;point.x=v.x;point.y=v.y;point.z=v.z;
    const auto old=ArenaRotationResidual(pose,point,r.yaw,r.pitch,1);
    const auto actual=ArenaRotationResidual(pose,point,r.yaw,r.pitch,double(float(28)/float(90)));
    assert(std::fabs(old-r.oldError)<1e-6&&old<1.5);
    assert(std::fabs(actual-r.newError)<1e-6&&actual>1.5);
  }
}
static bool SameIntent(const BotCommand&a,const BotCommand&b){
  return a.target==b.target&&a.target_visible==b.target_visible&&a.yaw_delta_deg==b.yaw_delta_deg&&
    a.pitch_delta_deg==b.pitch_delta_deg&&a.forward==b.forward&&a.strafe==b.strafe&&a.weapon==b.weapon&&
    a.preferred_range_m==b.preferred_range_m&&a.distance_m==b.distance_m;
}
static void DefaultsLegacyAndInvalid(){
  int compared=0;
  for(int arena=0;arena<2;++arena)for(int cecil=0;cecil<2;++cecil){
    BotProfile p;assert(arena?BuildRosterProfile(0,0,123,&p,1):BuildProfile(3,0,123,"legacy",&p));
    auto settings=CecilPreset(2);HumanBotPolicy a,b;a.Configure(&p,cecil?&settings:nullptr);b.Configure(&p,cecil?&settings:nullptr);
    WorldView x;x.cecil=cecil;x.alive=true;x.health=100;x.current_weapon=13;x.usable_weapons=CecilWeaponMask(13);
    WorldView y=x;
    SenseInput e{};e.index=2;e.entity_id=3;e.alive=true;e.health=100;e.z=-40;
    for(int tick=0;tick<400;++tick){
      // All new-scale values must be inert in legacy/Cecil-only profiles.
      y.rotation_damping=arena?1:tick%2?.3:std::numeric_limits<double>::quiet_NaN();
      e.x=2*std::sin(tick*.03);e.y=std::sin(tick*.02);
      if(tick==130)e.entity_id=4;
      x.alive=y.alive=tick!=200;
      HumanAimTrace ta,tb;auto ca=Tick(a,x,e,tick,&ta);auto cb=Tick(b,y,e,tick,&tb);
      assert(SameIntent(ca,cb)&&ca.fire==cb.fire&&ca.aim_error_deg==cb.aim_error_deg);
      assert(ta.aim.rate_after[0]==tb.aim.rate_after[0]&&ta.aim.bias[0]==tb.aim.bias[0]);
      x.pose.yaw_deg+=ca.yaw_delta_deg;x.pose.pitch_deg+=ca.pitch_delta_deg;y.pose=x.pose;++compared;
    }
  }
  BotProfile p;assert(BuildRosterProfile(0,0,123,&p,1));p.skill.reaction_s=0;p.skill.aim_sigma_deg=0;
  HumanBotPolicy h;auto settings=CecilPreset(2);h.Configure(&p,&settings);
  WorldView w;w.cecil=true;w.alive=true;w.health=100;w.current_weapon=13;w.usable_weapons=CecilWeaponMask(13);
  SenseInput e{};e.index=2;e.entity_id=3;e.alive=true;e.health=100;e.z=-40;
  int tick=0;HumanAimTrace trace;BotCommand cmd;
  for(;tick<20;++tick)cmd=Tick(h,w,e,tick,&trace);
  assert(cmd.fire);
  const double invalid[]={0,-1,1.01,INFINITY,-INFINITY,NAN};
  for(double scale:invalid){
    w.rotation_damping=scale;cmd=Tick(h,w,e,tick++,&trace);
    assert(!cmd.fire&&!trace.arena_aligned&&trace.settled_after==-1&&std::isfinite(cmd.aim_error_deg));
    w.rotation_damping=.3;
    for(int n=0;n<3;++n){cmd=Tick(h,w,e,tick++,&trace);assert(cmd.fire==(n==2));}
  }
  // Damping updates never alter raw rotation, targeting, movement, or RNG.
  HumanBotPolicy raw,scaled;raw.Configure(&p,&settings);scaled.Configure(&p,&settings);
  WorldView u=w,v=w;u.rotation_damping=1;v.rotation_damping=28./90.;e.x=-8;e.y=3;
  for(int t=0;t<100;++t){HumanAimTrace a,b;auto ca=Tick(raw,u,e,t,&a),cb=Tick(scaled,v,e,t,&b);assert(SameIntent(ca,cb));
    assert(a.aim.bias[0]==b.aim.bias[0]&&a.aim.rate_after[0]==b.aim.rate_after[0]);}
  std::printf("default/legacy parity %d ticks; invalid-scale settle and intent/RNG invariance passed\n",compared);
}
int main(){
  NativeResidualFixtures();DefaultsLegacyAndInvalid();
  BotProfile p;assert(BuildRosterProfile(0,0,2026110750u,&p,1));
  const CecilSettings c=CecilPreset(2);HumanBotPolicy h;h.Configure(&p,&c);
  WorldView w;w.cecil=true;w.alive=true;w.health=100;w.current_weapon=13;w.usable_weapons=CecilWeaponMask(13);
  const double scale=double(float(28)/float(90));Damping(w,scale,0);
  SenseInput e{};e.index=2;e.entity_id=572;e.generation=5;e.alive=true;e.health=100;e.x=-5;e.y=2;e.z=-40;
  int checked=0,fired=0;
  for(int tick=0;tick<400;++tick){
    HumanAimTrace trace;const auto cmd=Tick(h,w,e,tick,&trace);
    if(trace.aim.valid){
      const double expected=Expected(trace,cmd,scale);
      if(std::fabs(expected-cmd.aim_error_deg)>1e-9){
        std::printf("RED actual policy tick=%d raw=%.9f expected_damped=%.9f\n",tick,cmd.aim_error_deg,expected);return 1;
      }
      assert(!cmd.fire||expected<=p.skill.fire_tol_deg);++checked;fired+=cmd.fire;
    }
    w.pose.yaw_deg+=cmd.yaw_delta_deg*scale;w.pose.pitch_deg+=cmd.pitch_delta_deg*scale;
  }
  assert(checked>300&&fired>0);
  std::printf("rotation residual policy %d checks, %d permitted aligned ticks\n",checked,fired);
}
