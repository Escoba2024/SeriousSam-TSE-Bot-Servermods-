// SPDX-License-Identifier: GPL-2.0-only
#include "cecil_motion.h"
#include <cstdio>
#include <cstdlib>
#include <new>
static bool measuring=false;static size_t allocations=0;
void* operator new(size_t n){if(measuring)++allocations;void* p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();return p;}
void operator delete(void* p)noexcept{std::free(p);}
void operator delete(void* p,size_t)noexcept{std::free(p);}
using namespace botcore;
static int checks=0,failures=0;
static void check(bool yes,const char* s){++checks;if(!yes){++failures;std::fprintf(stderr,"FAIL %s\n",s);}}
static bool near(double a,double b){return std::fabs(a-b)<1e-8;}
static CecilNavGraph graph(){
  CecilNavGraph g;g.version=6;g.next_point_id=3;g.points.resize(3);
  for(int i=0;i<3;++i){g.points[i].id=i;g.points[i].radius=1;}
  g.points[1].z=-10;g.points[2].x=10;g.points[2].z=-10;
  g.points[0].links={1};g.points[1].links={2};return g;
}
int main(){
  auto g=graph();CecilNavigator nav;nav.Prepare(3);unsigned char locked[3]={0,0,0};
  CecilMotionInput in;in.alive=true;in.anchor=0;in.goal=2;
  auto out=nav.Update(g,locked,3,in);
  check(out.active&&out.hop==1&&near(out.forward,1)&&near(out.yaw_delta,0),"route begins on directed next hop");
  in.anchor=2;in.now=.5;out=nav.Update(g,locked,3,in);
  check(out.hop==1,"retain current hop between replans despite nearest-anchor change");
  in.anchor=1;in.z=-10;in.now=.6;out=nav.Update(g,locked,3,in);
  check(out.hop==2&&near(out.strafe,1)&&near(out.forward,0)&&near(out.yaw_delta,-9),"arrival advances directed path with normalized lateral motion");
  in.x=10;in.anchor=2;in.now=.7;out=nav.Update(g,locked,3,in);
  check(out.arrived&&!out.active&&near(out.forward,0)&&near(out.strafe,0),"goal arrival stops travel");
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=2;g.points[0].flags=CECIL_WALK;
  out=nav.Update(g,locked,3,in);check(near(out.forward,.5),"source WALK halves normalized horizontal motion");
  g.points[0].flags=CECIL_JUMP;nav.Reset();out=nav.Update(g,locked,3,in);check(near(out.up,1),"source JUMP starts pulse");
  in.now=.05;out=nav.Update(g,locked,3,in);check(out.up==0,"jump releases between pulses");
  in.now=.2;out=nav.Update(g,locked,3,in);check(out.up==1,"jump repeats at 0.2 second cooldown");
  in.now=.4;in.allow_jump=false;out=nav.Update(g,locked,3,in);check(out.up==0,"native jump permission veto respected");
  in.allow_jump=true;g.points[1].flags=CECIL_CROUCH|CECIL_OVERRIDE;nav.Reset();out=nav.Update(g,locked,3,in);
  check(out.up==-1&&out.flags==(CECIL_CROUCH|CECIL_OVERRIDE),"destination OVERRIDE crouches before arrival instead of source jump");
  in.now=.45;out=nav.Update(g,locked,3,in);check(out.up==-1,"crouch held continuously");
  g.points[0].flags=0;g.points[1].flags=CECIL_CROUCH;nav.Reset();out=nav.Update(g,locked,3,in);
  check(out.up==0,"destination without OVERRIDE does not apply early");
  g.points[1].flags=CECIL_UNREACHABLE;nav.Reset();out=nav.Update(g,locked,3,in);
  check(out.active&&out.forward==0&&out.strafe==0&&out.hop==0,"non-important UNREACHABLE stays at source without deleting arc");
  in.now=3;out=nav.Update(g,locked,3,in);check(!out.stuck,"intentional unreachable stay does not trigger recovery");
  in.important_goal=true;nav.Reset();out=nav.Update(g,locked,3,in);check(out.hop==1&&out.forward>0,"important route may approach UNREACHABLE point");
  g.points[1].flags=0;locked[1]=1;out=nav.Update(g,locked,3,in);
  check(!out.active,"changed lock snapshot immediately invalidates path");
  locked[1]=0;in.now=3.05;out=nav.Update(g,locked,3,in);check(out.active&&out.hop==1,"unlock replans without map rebuild");
  in.goal=0;in.now=3.1;out=nav.Update(g,locked,3,in);check(out.arrived,"changed goal immediately replaces old route");
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=1;in.goal=1;in.y=1.3;in.z=-10;
  out=nav.Update(g,locked,3,in);check(out.arrived,"second gravity-offset sphere accepts correct point radius");
  nav.Reset();in.y=3;out=nav.Update(g,locked,3,in);check(!out.arrived,"same XZ on another floor is not arrival");
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=2;nav.Update(g,locked,3,in);
  in.now=2.01;out=nav.Update(g,locked,3,in);check(out.stuck&&out.forward<0&&out.strafe>0,"two seconds without progress starts bounded recovery");
  in.now=2.3;out=nav.Update(g,locked,3,in);check(out.stuck,"recovery holds within half-second window");
  in.now=2.6;out=nav.Update(g,locked,3,in);check(!out.stuck&&out.active,"recovery ends and replans");
  nav.Reset();in.now=0;in.slot=1;nav.Update(g,locked,3,in);in.now=2.01;out=nav.Update(g,locked,3,in);
  check(out.stuck&&out.strafe<0,"recovery side deterministic per slot");
  in.alive=false;out=nav.Update(g,locked,3,in);check(!out.active&&!out.stuck,"death clears navigation");
  in.alive=true;in.now=2.02;out=nav.Update(g,locked,3,in);check(out.active&&!out.stuck,"respawn resets progress clock");
  in.now=0;out=nav.Update(g,locked,3,in);check(out.active&&!out.stuck,"clock rollback resets transient state");
  in.gravity[0]=1;out=nav.Update(g,locked,3,in);check(!out.active,"nonunit gravity is rejected");
  in.gravity[0]=0;in.x=std::numeric_limits<double>::quiet_NaN();check(!nav.Update(g,locked,3,in).active,"nonfinite position emits no action");
  in.x=0;in.dt=0;check(!nav.Update(g,locked,3,in).active,"zero tick interval emits no action");
  in.dt=.05;in.anchor=-1;check(!nav.Update(g,locked,3,in).active,"missing native anchor emits no action");
  in.anchor=0;check(!nav.Update(g,locked,2,in).active,"wrong lock generation size emits no action");
  nav.Prepare(2);check(!nav.Update(g,locked,3,in).active,"unprepared map size emits no action");
  nav.Prepare(3);allocations=0;measuring=true;out=nav.Update(g,locked,3,in);nav.Reset();out=nav.Update(g,locked,3,in);measuring=false;
  check(out.active&&allocations==0,"Update and Reset allocate no memory");
  g.points[0].flags=CECIL_TELEPORT;nav.Reset();out=nav.Update(g,locked,3,in);
  check(out.active&&out.hop==1&&g.points[0].x==0&&g.points[1].z==-10,"teleport remains ordinary motion on unchanged graph");
  nav.Reset();in.dt=.1;in.yaw=90;out=nav.Update(g,locked,3,in);check(near(out.yaw_delta,-18),"rotation bound scales with seconds not tick count");
  g=graph();nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=1;
  in.frame.right[0]=-1;in.frame.up[1]=-1;in.gravity[1]=1;
  out=nav.Update(g,locked,3,in);check(out.active&&near(out.forward,1),"inverted body travels forward in its local frame");
  g.points[1].x=10;g.points[1].z=0;nav.Reset();out=nav.Update(g,locked,3,in);
  check(out.active&&near(out.strafe,-1)&&near(out.yaw_delta,9),"inverted body reverses world lateral and yaw handedness correctly");
  g.points[0].flags=CECIL_WALK|CECIL_JUMP;nav.Reset();out=nav.Update(g,locked,3,in);
  check(near(out.strafe,-.5)&&out.up==1,"Cecil walk and jump flags survive inverted projection");
  g=graph();nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=1;
  const double c=std::sqrt(.5);in.frame.right[0]=c;in.frame.right[1]=c;in.frame.up[0]=-c;in.frame.up[1]=c;
  in.gravity[0]=c;in.gravity[1]=-c;g.points[1].x=float(10*c);g.points[1].y=float(10*c);g.points[1].z=0;
  out=nav.Update(g,locked,3,in);check(out.active&&near(out.strafe,1),"tilted frame treats movement tangent to actual gravity as horizontal");
  nav.Reset();in.frame=CecilFrame();out=nav.Update(g,locked,3,in);
  check(out.active&&out.strafe>0,"transition body frame may differ from gravity alignment");
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=0;in.gravity[1]=1;in.frame.right[0]=-1;in.frame.up[1]=-1;in.y=-1.3;
  check(nav.Update(g,locked,3,in).arrived,"arrival second sphere uses actual inverted gravity");
  in.goal=1;in.y=0;in.frame.right[0]=1;nav.Reset();check(!nav.Update(g,locked,3,in).active,"reflected body basis fails closed");
  in.frame=CecilFrame();in.gravity[1]=0;check(!nav.Update(g,locked,3,in).active,"zero gravity vector fails closed");
  g=graph();nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=1;
  in.gravity[1]=1;in.frame.right[0]=-1;in.frame.up[1]=-1;in.yaw=90;g.points[1].x=10;g.points[1].z=0;
  out=nav.Update(g,locked,3,in);check(out.active&&near(out.forward,1)&&near(out.strafe,0)&&near(out.yaw_delta,0),"inverted body and ninety degree local head yaw compose correctly");
  std::printf("CECIL MOTION checks=%d failures=%d\n",checks,failures);return failures?1:0;
}
