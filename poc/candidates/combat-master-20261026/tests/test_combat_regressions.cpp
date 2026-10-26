// Real policy + real ObstacleRecovery; kinematics provide only observed poses.
#include "bot_human.h"
#include "bot_navigation.h"
#include <cmath>
#include <cstdio>
using namespace botcore;
static int checks=0,failures=0;
#define CHECK(c) do {++checks;if(!(c)){++failures;std::printf("FAIL line%d: %s\n",__LINE__,#c);}}while(0)
static BotProfile Profile(int tier=4){BotProfile p;BuildProfile(tier,0,0x5702u,"regression",&p);return p;}
static WorldView World(int tick){WorldView w;w.tick=tick;w.alive=true;w.health=100;w.pose.y=1.6;w.usable_weapons=1u<<5;w.current_weapon=6;return w;}
static SenseInput Enemy(double d=30){SenseInput e{};e.index=1;e.alive=true;e.y=1.6;e.z=-d;e.health=100;return e;}
static BotCommand Tick(HumanBotPolicy& h,const WorldView& w,const SenseInput* e=nullptr,bool visible=false){
 h.BeginTick(w);bool ray[1]={false};h.PlanLosQueries(e,e?1:0,ray);bool los[1]={visible&&ray[0]};return h.Step(w,e,los,e?1:0,.05);
}
static void CombatDetourKeepsIntent(bool exploratory,bool visible){
 auto p=Profile();HumanBotPolicy h;h.Configure(&p,exploratory);auto e=Enemy(80);BotCommand c;
 for(int t=0;t<60;++t)c=Tick(h,World(t),&e,true);
 h.NotifyNavigation(true);
 auto w=World(60);w.pose.yaw_deg=visible?50:80;c=Tick(h,w,&e,visible);
 CHECK(c.target>=0);CHECK(c.target_visible==visible);CHECK(c.forward>0);CHECK(!c.travel);
}
static void RecoveryResetRestoresExploratoryHold(){
 auto p=Profile();HumanBotPolicy h;h.Configure(&p,true);auto e=Enemy(80);BotCommand c;
 h.NotifyNavigation(true);h.Reset();
 for(int t=0;t<60;++t){auto w=World(t);w.pose.yaw_deg=50;c=Tick(h,w,&e,true);}
 CHECK(c.target>=0);CHECK(c.forward==0);CHECK(c.travel);
 h.NotifyNavigation(true);auto w=World(60);w.pose.yaw_deg=50;c=Tick(h,w,&e,true);CHECK(c.forward>0);
 h.NotifyNavigation(false);w.tick=61;c=Tick(h,w,&e,true);CHECK(c.forward==0);
}
static void BlindEscape(bool exploratory,int visible_from,bool occluded,bool outside_fov=false){
 auto p=Profile();HumanBotPolicy h;h.Configure(&p,exploratory,true);auto e=Enemy(12);BotCommand c;
 // Populate own history. No hidden actor positions are exposed before ambush.
 for(int t=0;t<=20;++t){auto w=World(t);w.pose.z=-t*.2;c=Tick(h,w);}
 int escaped=0,shots=0,first_target=-1;bool cancellation_seen=false;
 for(int t=21;t<121;++t){auto w=World(t);w.pose.z=-4.2;w.health=70;
  if(outside_fov)w.pose.yaw_deg=180;
  const bool expose=t>=visible_from;c=Tick(h,w,expose?&e:nullptr,expose&&!occluded);
  if(c.escape)++escaped;
  if(c.fire)++shots;
  if(c.target>=0&&first_target<0)first_target=t;
  if(expose&&!occluded&&!outside_fov&&!c.escape)cancellation_seen=true;
  if(expose&&!occluded&&!outside_fov)CHECK(!c.escape);
  if(c.fire){CHECK(c.target_visible);CHECK(!c.escape);}
 }
 if(occluded||outside_fov){CHECK(escaped==100);CHECK(shots==0);CHECK(first_target<0);}
 else{CHECK(cancellation_seen);CHECK(first_target>=visible_from+p.skill.reaction_s*kProfileTickHz-1);CHECK(first_target<visible_from+20);CHECK(shots>=5);CHECK(escaped<=visible_from-21);}
 std::printf("AMBUSH exploratory=%d visible_from=%d occluded=%d outside_fov=%d escaped=%d shots=%d first_target=%d\n",exploratory,visible_from,occluded,outside_fov,escaped,shots,first_target);
}
static void WallChase(bool exploratory){
 auto p=Profile(3);HumanBotPolicy h;h.Configure(&p,exploratory);ObstacleRecovery recovery;
 double x=0,z=0,yaw=0,pitch=0,max_x=0;bool bypass=false,active=false;int resets=0;
 auto e=Enemy(25);
 for(int t=1;t<=240;++t){auto w=World(t);w.pose={x,1.6,z,yaw,pitch};const bool visible=t<=8||std::fabs(x)>2.05;
  auto c=Tick(h,w,&e,visible);
  // Same reset criterion as the actual adapter; no rewritten policy command.
  if((c.escape||c.travel)&&c.forward==0){if(active)++resets;recovery.Reset();}
  auto ray=[&](double angle){const double r=angle*kDegToRad,dx=-std::sin(r),dz=-std::cos(r);if(std::fabs(dz)<1e-6)return 3.;const double d=(-1.5-z)/dz;return d>0&&d<3&&std::fabs(x+dx*d)<=2?d:3.;};
  const double requested_forward=c.target>=0||c.escape||c.travel?c.forward:1.0;
  const bool hold=c.target>=0&&c.distance_m<=((c.weapon==1||c.weapon==10)?1.5:8.0);
  NavigationInput in={x,z,yaw,9,requested_forward,ray(yaw),ray(yaw+60),ray(yaw-60),true,hold,1,1};
  auto n=recovery.Update(in);active=n.active;h.NotifyNavigation(n.overrideInput);
  double forward=requested_forward,strafe=c.strafe;
  if(n.overrideInput){yaw=AimController::WrapDeg(yaw+n.yawDelta);forward=n.forward;strafe=0;}else{yaw=AimController::WrapDeg(yaw+c.yaw_delta_deg);pitch+=c.pitch_delta_deg;}
  if(!h.AllowFinalMovement(x,1.6,z,yaw,forward,strafe))forward=strafe=0;
  const double r=yaw*kDegToRad,nx=x+(-std::sin(r)*forward+std::cos(r)*strafe)*.375,nz=z+(-std::cos(r)*forward-std::sin(r)*strafe)*.375;
  const bool wall=z>-1.4&&nz<=-1.4&&std::fabs(nx)<=2;x=nx;if(!wall)z=nz;max_x=std::fmax(max_x,std::fabs(x));
  if(z<-2){bypass=true;break;}
 }
 // After its observed target memory expires, exploratory travel may choose a
 // different route; require clearing the pillar, not pursuit of expired data.
 CHECK(max_x>2.05);if(!exploratory)CHECK(bypass);CHECK(resets<=1);std::printf("WALL exploratory=%d bypass=%d resets=%d max_x=%.2f\n",exploratory,bypass,resets,max_x);
}
static void ExploratoryTurnsResumeTravel(){
 for(unsigned seed=1;seed<=40;++seed){auto p=Profile(3);p.seed=seed;HumanBotPolicy h;h.Configure(&p,true);
  double yaw=0;int moving=0,stopped=0,max_stop=0;
  for(int t=0;t<240;++t){auto w=World(t);w.pose.yaw_deg=yaw;auto c=Tick(h,w);yaw=AimController::WrapDeg(yaw+c.yaw_delta_deg);
   CHECK(c.target<0);CHECK(!c.fire);CHECK(!c.escape);
   if(c.forward>.5){++moving;stopped=0;}else{++stopped;max_stop=stopped>max_stop?stopped:max_stop;}
  }
  CHECK(moving>120);CHECK(max_stop<30);
 }
}
int main(){CombatDetourKeepsIntent(false,false);CombatDetourKeepsIntent(true,false);CombatDetourKeepsIntent(false,true);CombatDetourKeepsIntent(true,true);RecoveryResetRestoresExploratoryHold();BlindEscape(false,21,false);BlindEscape(true,21,false);BlindEscape(false,26,false);BlindEscape(false,21,true);BlindEscape(false,21,false,true);WallChase(false);WallChase(true);ExploratoryTurnsResumeTravel();std::printf("COMBAT REGRESSIONS: %d checks, %d failures\n",checks,failures);return failures?1:0;}
