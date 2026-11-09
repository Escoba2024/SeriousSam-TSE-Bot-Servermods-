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
template<class T>auto relocated(const T& m,int)->decltype(m.relocated){return m.relocated;}
template<class T>bool relocated(const T&,long){return false;}
template<class T>auto supportedLock(T& in,int node,int)->decltype(in.supported_lock_node=node,void()){in.supported_lock_node=node;}
template<class T>void supportedLock(T&,int,long){}
template<class T>auto lockStarted(const T& out,int)->decltype(out.supported_lock_started){return out.supported_lock_started;}
template<class T>bool lockStarted(const T&,long){return false;}
static CecilNavGraph liftGraph(){
  CecilNavGraph g;g.points.resize(6);
  const double p[6][3]={{-8,.5,0},{0,1.639451,0},{0,12.5,0},{10,12.5,0},{-5.5,1,0},{0,0,100}};
  for(int i=0;i<6;++i){g.points[i].id=i;g.points[i].radius=1;g.points[i].x=p[i][0];g.points[i].y=p[i][1];g.points[i].z=p[i][2];}
  g.points[0].links={1};g.points[1].links={2};g.points[2].links={3};g.points[4].links={0,5};g.points[5].links={3};return g;
}
static void liftOccupancy(){
  auto g=liftGraph();CecilNavigator nav;nav.Prepare(6);unsigned char locks[6]={};
  CecilMotionInput in;in.alive=true;in.anchor=0;in.goal=3;in.x=-8;in.y=.5;
  check(nav.Update(g,locks,6,in).hop==1,"lift fixture approaches original directed locked hop while open");
  in.now=.05;in.x=-1.584377;in.y=1.080671;in.z=.991288;in.anchor=4;locks[1]=1;supportedLock(in,1,0);
  auto out=nav.Update(g,locks,6,in);
  check(out.active&&out.hop==1,"actual supported 1.95m lock transition retains its existing edge instead of reversing to anchor");
  check(lockStarted(out,0),"fresh supported lock hold reports one bounded start event");
  check(!out.arrived&&!out.relocated&&locks[1]==1,"supported approach does not fabricate arrival relocation or global unlock");
  in.now=.1;out=nav.Update(g,locks,6,in);
  check(out.hop==1&&!lockStarted(out,0),"continuous current support preserves only the same edge without repeating start telemetry");
  in.now=.15;in.x=0;in.y=1.1;in.z=0;in.anchor=1;out=nav.Update(g,locks,6,in);
  check(out.hop==2&&!out.relocated&&!lockStarted(out,0),"only original radius arrival advances from occupied locked lift toward upper point");
  nav.Reset();std::fill(locks,locks+6,0);in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=3;in.x=-8;in.y=.5;nav.Update(g,locks,6,in);
  in.now=.05;in.x=-1.584377;in.y=1.080671;in.z=.991288;in.anchor=4;locks[1]=1;supportedLock(in,1,0);nav.Update(g,locks,6,in);
  in.now=.1;supportedLock(in,-1,0);out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"support loss immediately replans a closed approach before the one second timer");
  in.now=.15;supportedLock(in,1,0);out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"returning support cannot revive a dropped already-closed approach");
  auto prepare=[&](){g=liftGraph();nav.Prepare(6);std::fill(locks,locks+6,0);in=CecilMotionInput();
    in.alive=true;in.anchor=0;in.goal=3;in.x=-8;in.y=.5;nav.Update(g,locks,6,in);
    in.now=.05;in.x=-1.584377;in.y=1.080671;in.z=.991288;in.anchor=4;locks[1]=1;supportedLock(in,1,0);};
  prepare();supportedLock(in,4,0);out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"a different validated slot cannot claim the retained locked hop");
  prepare();supportedLock(in,-1,0);nav.Update(g,locks,6,in);supportedLock(in,1,0);in.now=.1;out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"already observed closed lock without initial support cannot start a later occupancy hold");
  prepare();g.points[0].links.clear();out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"support cannot preserve an edge absent from original directed adjacency");
  prepare();in.goal=5;out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"new goal cannot inherit a supported locked approach");
  prepare();nav.Reset();out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"reset cannot manufacture a fresh supported edge from closed acquisition hint");
  prepare();in.x=-5.5;in.y=1;in.z=0;out=nav.Update(g,locks,6,in);
  check(out.relocated&&out.hop==5&&!lockStarted(out,0),"genuine geometric relocation takes priority over an old supported hint");
  prepare();locks[3]=1;out=nav.Update(g,locks,6,in);
  check(!out.active&&!lockStarted(out,0),"supported hop with blocked goal suffix fails closed without start telemetry");
  prepare();nav.Update(g,locks,6,in);locks[5]=1;in.now=.1;out=nav.Update(g,locks,6,in);
  check(out.hop==1&&!lockStarted(out,0),"unrelated lock change preserves a continuously supported original edge");
  prepare();nav.Update(g,locks,6,in);in.now=2.06;out=nav.Update(g,locks,6,in);
  check(out.stuck&&!lockStarted(out,0),"supported stationary lift does not suppress existing two second stuck recovery");
  in.now=2.11;out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"recovery clears supported context and immediately returns to normal locked replan");
  prepare();nav.Update(g,locks,6,in);in.now=0;out=nav.Update(g,locks,6,in);
  check(out.hop==4&&!lockStarted(out,0),"clock rollback discards supported approach context");
  prepare();g.points[1].flags=CECIL_UNREACHABLE;out=nav.Update(g,locks,6,in);
  check(out.hop==0&&!lockStarted(out,0),"intentional UNREACHABLE source stay cannot log an effective supported edge hold");
  prepare();locks[1]=0;nav.Update(g,locks,6,in);locks[1]=1;in.now=2.06;out=nav.Update(g,locks,6,in);
  check(out.stuck&&!lockStarted(out,0),"fresh support observed only when stuck recovery starts cannot log an effective edge hold");
  prepare();allocations=0;measuring=true;out=nav.Update(g,locks,6,in);measuring=false;
  check(out.hop==1&&allocations==0,"supported lock transition allocates no per-tick memory");


}
static CecilNavGraph graph(){
  CecilNavGraph g;g.version=6;g.next_point_id=3;g.points.resize(3);
  for(int i=0;i<3;++i){g.points[i].id=i;g.points[i].radius=1;}
  g.points[1].z=-10;g.points[2].x=10;g.points[2].z=-10;
  g.points[0].links={1};g.points[1].links={2};return g;
}

// The incomplete-type fallback exposes the old missing watchdog as behavior RED.
namespace botcore {class CecilGroundProgress;}
template<class T,class=void>struct GroundFixture {
 bool Update(double,const CecilVec&,const CecilVec&,bool){return false;}
 void Reset(){}
};
template<class T>struct GroundFixture<T,decltype(void(sizeof(T)))> {
 T value;bool Update(double n,const CecilVec& p,const CecilVec& g,bool e){return value.Update(n,p,g,e);}
 void Reset(){value.Reset();}
};
static void offgraphProgress(){
 GroundFixture<CecilGroundProgress> watch;CecilVec p{0,0,0},g{0,-1,0};bool stalled=false;
 for(int i=0;i<=41;++i)stalled=watch.Update(i*.05,p,g,true);
 check(stalled,"actual frozen world position triggers offgraph watchdog after two seconds");
 p.x=.01;check(watch.Update(2.1,p,g,true),"substantial stall survives position jitter");
 p.x=.26;check(!watch.Update(2.15,p,g,true),"actual quarter-meter displacement resets watchdog");
 watch.Reset();for(int i=0;i<=250;++i)stalled=watch.Update(i*.05,{0,0,0},g,true);
 check(stalled,"six-second candidate and cooldown epochs cannot renew physical progress");
 check(!watch.Update(12.55,p,g,false),"loss of accepted eligibility resets physical watchdog");
 check(!watch.Update(12.6,p,g,true),"a new eligible epoch has no inherited stall");
 for(int i=0;i<42;++i)watch.Update(13+i*.05,p,g,true);
 check(!watch.Update(15.1,p,{0,1,0},true),"gravity change resets physical watchdog");
 check(!watch.Update(1,p,g,true),"clock rewind resets physical watchdog");
 check(!watch.Update(NAN,p,g,true),"nonfinite clock cannot authorize escape");
 check(!watch.Update(2,{NAN,0,0},g,true),"nonfinite position cannot authorize escape");
 watch.Reset();for(int i=0;i<=41;++i)watch.Update(i*.05,p,g,true);
 check(!watch.Update(2.4,p,g,true),"a gap in accepted updates cannot accrue unobserved stall time");
 watch.Reset();for(int i=0;i<=41;++i)watch.Update(i*.05,p,g,true);
 check(!watch.Update(2.1,p,{0,0,0},true),"invalid gravity cannot authorize physical recovery");
 watch.Reset();for(int i=0;i<=41;++i)watch.Update(i*.05,p,g,true);
 p.y+=.26;check(!watch.Update(2.1,p,g,true),"vertical world displacement also resets physical progress detector");
}

int main(){
  offgraphProgress();
  liftOccupancy();
  auto g=graph();CecilNavigator nav;nav.Prepare(3);unsigned char locked[3]={0,0,0};
  CecilMotionInput in;in.alive=true;in.anchor=0;in.goal=2;
  auto out=nav.Update(g,locked,3,in);
  check(out.active&&out.hop==1&&near(out.forward,1)&&near(out.yaw_delta,0),"route begins on directed next hop");
  check(nav.HasCommittedEdge(2)&&!nav.HasCommittedEdge(1),"route commitment is bound to its exact goal");
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
  // A completed source stays completed while traversing a long directed edge.
  g=graph();g.points[1].x=20;g.points[1].z=0;g.points[2].x=40;g.points[2].z=0;
  g.points[1].flags=CECIL_CROUCH;g.points[2].flags=CECIL_JUMP;
  nav.Prepare(3);in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=2;
  out=nav.Update(g,locked,3,in);check(out.hop==1,"long-edge fixture begins toward first waypoint");
  in.x=6;in.now=1.1;out=nav.Update(g,locked,3,in);
  check(out.hop==1&&out.strafe>0,"first long edge retains completed initial source at timer expiry");
  in.now=1.2;
  in.x=20;in.anchor=1;out=nav.Update(g,locked,3,in);
  check(out.hop==2&&out.flags==CECIL_CROUCH,"arrival commits next edge with reached-source flags");
  in.x=26;in.now=1.6;out=nav.Update(g,locked,3,in);
  check(out.hop==2&&out.strafe>0&&out.flags==CECIL_CROUCH,"periodic replan cannot return to completed nearest source or apply destination flags early");
  bool forward_progress=true;
  for(int tick=0;tick<8;++tick){in.x=27+tick;in.now=2.7+tick;out=nav.Update(g,locked,3,in);forward_progress=forward_progress&&out.hop==2&&out.strafe>0&&!out.stuck;}
  check(forward_progress,"slow long-edge travel keeps its committed directed successor across repeated replans");
  locked[2]=1;in.now+=.1;out=nav.Update(g,locked,3,in);
  check(!out.active,"newly locked destination still invalidates committed edge immediately");locked[2]=0;
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=2;in.x=10;
  out=nav.Update(g,locked,3,in);in.x=9;in.now=1.1;out=nav.Update(g,locked,3,in);
  check(out.hop==0,"unreached approach source cannot be skipped by edge commitment");
  check(!nav.HasCommittedEdge(2),"acquisition approach is not a committed traversed edge");
  nav.Reset();check(!nav.HasCommittedEdge(2),"lifecycle reset removes route commitment");
  // A real relocation onto another known node must re-anchor immediately.
  g.points.resize(4);g.points[2].x=120;g.points[2].radius=1;g.points[2].links={3};
  g.points[3].id=3;g.points[3].x=140;g.points[3].radius=1;g.points[1].flags=CECIL_TELEPORT;
  nav.Prepare(4);unsigned char open4[4]={0,0,0,0};in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=3;
  nav.Update(g,open4,4,in);in.x=17;in.now=.4;nav.Update(g,open4,4,in);
  in.x=120;in.anchor=2;in.now=.45;out=nav.Update(g,open4,4,in);
  check(out.hop==3&&out.strafe>0,"native teleport onto a reached exit point reanchors without backtracking to its entry");
  check(relocated(out,0),"actual reached relocation is exposed to the native caller");
  in.now=.5;out=nav.Update(g,open4,4,in);
  check(!relocated(out,0),"repeated scans at the relocated source do not repeat the relocation event");
  in.x=126;in.anchor=0;in.now=.55;out=nav.Update(g,open4,4,in);
  check(!relocated(out,0),"an unreached anchor hint cannot report relocation");
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=3;
  nav.Update(g,open4,4,in);in.x=6;in.now=.5;open4[2]=1;
  out=nav.Update(g,open4,4,in);
  check(!out.active,"locked suffix with no alternative invalidates travel before entering a dead end");
  open4[2]=0;g.points[2].links.clear();g.points[1].links={3};
  nav.Reset();in.x=0;in.now=0;nav.Update(g,open4,4,in);
  in.x=6;in.now=.5;open4[2]=1;out=nav.Update(g,open4,4,in);
  check(out.hop==1&&out.strafe>0,"unrelated lock cannot undo a completed source on an active edge");
  open4[2]=0;g.points[1].flags=CECIL_CROUCH|CECIL_OVERRIDE;
  in.now=1.6;out=nav.Update(g,open4,4,in);
  check(out.hop==1&&out.up==-1,"destination override survives periodic validation and unrelated unlock");
  in.goal=0;in.now=1.7;out=nav.Update(g,open4,4,in);
  check(out.hop==0&&out.strafe<0,"new goal immediately clears the old forward commitment");
  nav.Reset();in=CecilMotionInput();in.alive=true;in.anchor=0;in.goal=3;
  nav.Update(g,open4,4,in);in.x=14;in.anchor=1;in.now=.5;open4[1]=1;
  out=nav.Update(g,open4,4,in);
  check(!out.active,"unreached locked nearest anchor cannot be approached as an allowed search origin");
  in.x=20;in.now=.6;out=nav.Update(g,open4,4,in);
  check(out.active&&out.hop==3,"a bot already inside a newly locked source may still exit it");
  std::printf("CECIL MOTION checks=%d failures=%d\n",checks,failures);return failures?1:0;
}
