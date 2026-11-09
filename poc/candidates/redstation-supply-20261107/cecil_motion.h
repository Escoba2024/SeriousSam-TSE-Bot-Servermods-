// Copyright (c) 2018-2023 Dreamy Cecil; ssam.ai adaptations 2026.
// SPDX-License-Identifier: GPL-2.0-only
// BotMovement.cpp / BotPathFinding at CecilBotMod 953b477.
// Native caller owns collision/floor vetoes, entity generations and map resets.
#ifndef BOTCORE_CECIL_MOTION_H
#define BOTCORE_CECIL_MOTION_H
#include "cecil_nav_data.h"
#include "botcore.h"
#include "cecil_frame.h"
namespace botcore {
// Original Cecil NoPosChange also applies away from a graph edge. This detector
// measures world displacement, never a ray approval, requested action or NAV scan.
class CecilGroundProgress {
 public:
  void Reset(){last_=since_=-1;displacement_=0;continuous_=false;}
  bool Continuous()const{return continuous_;}
  double StationarySeconds()const{return since_>=0?last_-since_:0;}
  double Displacement()const{return displacement_;}
  bool Update(double now,const CecilVec& p,const CecilVec& g,bool eligible){
    const double gravity=g.x*g.x+g.y*g.y+g.z*g.z;
    if(!eligible||!std::isfinite(now)||now<0||!Finite(p)||!Finite(g)||
       !std::isfinite(gravity)||std::fabs(gravity-1)>1e-3){Reset();return false;}
    const double changed=(g.x-gravity_.x)*(g.x-gravity_.x)+(g.y-gravity_.y)*(g.y-gravity_.y)+(g.z-gravity_.z)*(g.z-gravity_.z);
    const double moved=(p.x-position_.x)*(p.x-position_.x)+(p.y-position_.y)*(p.y-position_.y)+(p.z-position_.z)*(p.z-position_.z);
    displacement_=std::sqrt(moved);
    // Missing accepted frames must not accrue unobserved control time.
    continuous_=last_>=0&&now>=last_&&now-last_<=.25&&changed<=1e-6;
    if(!continuous_||moved>=.25*.25){
      since_=now;position_=p;gravity_=g;displacement_=0;
    }
    last_=now;return now-since_+1e-9>=2;
  }
 private:
  static bool Finite(const CecilVec& v){return std::isfinite(v.x)&&std::isfinite(v.y)&&std::isfinite(v.z);}
  bool continuous_=false;double last_=-1,since_=-1,displacement_=0;CecilVec position_{0,0,0},gravity_{0,0,0};
};
struct CecilMotionInput {
  CecilFrame frame; // identity preserves legacy world-yaw callers; native supplies body axes and local head yaw.
  double x=0,y=0,z=0,yaw=0,gravity[3]={0,-1,0};
  double now=0,dt=.05,turn_speed_deg=180;
  int anchor=-1,goal=-1,slot=0;
  int supported_lock_node=-1; // Native validates current grounded contact; never an anchor/arrival hint.
  bool alive=false,allow_jump=true,important_goal=false;
};
struct CecilMotion {
  bool active=false,arrived=false,stuck=false,relocated=false,supported_lock_started=false;
  int hop=-1;double forward=0,strafe=0,up=0,yaw_delta=0,pitch_delta=0;uint32_t flags=0;
};
class CecilNavigator {
 public:
  void Prepare(size_t nodes) {
    if(nodes>CecilNavGraph::kMaxPoints)nodes=0;
    search_.Prepare(nodes);locks_.assign(nodes,0);Reset();
  }
  void Reset() {
    source_=hop_=goal_=supported_lock_hop_=-1;last_time_=-1;next_replan_=next_jump_=0;
    recovery_until_=-1;have_progress_=false;progress_time_=px_=py_=pz_=0;
    std::fill(locks_.begin(),locks_.end(),0);
  }
  bool HasCommittedEdge(int goal)const {
    return goal>=0&&goal_==goal&&source_>=0&&hop_>=0&&source_!=hop_&&
      (size_t)source_<locks_.size()&&(size_t)hop_<locks_.size();
  }
  CecilMotion Update(const CecilNavGraph& g,const unsigned char* blocked,size_t count,const CecilMotionInput& in) {
    CecilMotion out;const size_t n=g.points.size();
    if(!in.alive||n==0||n!=locks_.size()||in.anchor<0||(size_t)in.anchor>=n||
       in.goal<0||(size_t)in.goal>=n||(blocked?count!=n:count!=0)||!Valid(in)) {Reset();return out;}
    if(last_time_>=0&&in.now<last_time_)Reset();
    last_time_=in.now;
    const bool was_hop_locked=hop_>=0&&(size_t)hop_<n&&locks_[hop_];
    bool lock_change=false;
    for(size_t i=0;i<n;++i){const unsigned char value=blocked&&blocked[i]?1:0;
      lock_change|=locks_[i]!=value;locks_[i]=value;}
    const bool new_goal=goal_!=in.goal;
    if(new_goal){goal_=in.goal;hop_=-1;recovery_until_=-1;have_progress_=false;}
    if(!have_progress_||Distance2(in.x-px_,in.y-py_,in.z-pz_)>=.75*.75)Progress(in);
    if(Reached(g.points[in.goal],in)) {
      supported_lock_hop_=-1;out.arrived=true;out.hop=in.goal;hop_=in.goal;Progress(in);recovery_until_=-1;return out;
    }
    bool recovered=false;
    if(recovery_until_>=0&&in.now>=recovery_until_) {
      recovered=true;recovery_until_=-1;next_replan_=in.now;Progress(in);
    }
    const bool at_hop=hop_>=0&&(size_t)hop_<n&&Reached(g.points[hop_],in);
    // Nearest anchors acquire a route; timer expiry must not undo a source
    // already reached while the bot is still traversing its directed edge.
    // A real relocation onto another reached node (for example a teleport exit)
    // is independent evidence to acquire a route from the actual new location.
    const bool relocated=source_>=0&&!at_hop&&in.anchor!=source_&&in.anchor!=hop_&&
      Reached(g.points[in.anchor],in);
    out.relocated=relocated;
    // A supported approach at an observed open-to-closed lift transition is the
    // same edge. Keep its exact hop until the original radius is reached; do
    // not synthesize arrival, relocation, a source or an unlocked destination.
    const bool supported=!new_goal&&!recovered&&!relocated&&!at_hop&&recovery_until_<0&&
      source_>=0&&(size_t)source_<n&&hop_>=0&&(size_t)hop_<n&&source_!=hop_&&
      in.supported_lock_node==hop_&&locks_[hop_]&&
      (!was_hop_locked||supported_lock_hop_==hop_)&&
      std::find(g.points[source_].links.begin(),g.points[source_].links.end(),hop_)!=g.points[source_].links.end();
    const bool support_ended=supported_lock_hop_>=0&&!supported;
    const bool supported_started=supported&&supported_lock_hop_!=hop_;
    supported_lock_hop_=supported?hop_:-1;
    if(new_goal||lock_change||recovered||relocated||support_ended||hop_<0||in.now>=next_replan_||at_hop) {
      const bool committed=!new_goal&&!recovered&&!relocated&&!at_hop&&
        source_>=0&&hop_>=0&&hop_!=source_&&(!locks_[hop_]||supported);
      if(!committed)source_=at_hop&&!new_goal&&!recovered&&!relocated?hop_:in.anchor;
      // Search allows an occupied blocked origin to exit. An acquisition anchor
      // outside its arrival radius is still a destination and must respect locks.
      if(!committed&&locks_[source_]&&!Reached(g.points[source_],in)){hop_=-1;return out;}
      // Validate the remaining suffix from the committed destination. Even an
      // unrelated lock change must not replace the active edge or its flags.
      if(!search_.Run(g,committed?hop_:source_,locks_.data(),n)){hop_=supported_lock_hop_=-1;return out;}
      const int next=search_.NextHop(in.goal);
      if(next<0){hop_=supported_lock_hop_=-1;return out;}
      if(!committed)hop_=Reached(g.points[source_],in)?next:source_;
      next_replan_=in.now+1.0;
    }
    if(hop_<0||(size_t)hop_>=n)return out;
    out.supported_lock_started=supported_started;
    const CecilNavPoint& target=g.points[hop_];
    out.active=true;out.hop=hop_;
    out.flags=(target.flags&CECIL_OVERRIDE)?target.flags:g.points[source_].flags;
    // UNREACHABLE is a stay instruction, not a topology filter.
    if(hop_!=source_&&(target.flags&CECIL_UNREACHABLE)&&!in.important_goal) {
      out.supported_lock_started=false;out.hop=source_;Progress(in);recovery_until_=-1;return out;
    }
    const double dx=double(target.x)-in.x,dy=double(target.y)-in.y,dz=double(target.z)-in.z;
    if(!std::isfinite(dx)||!std::isfinite(dy)||!std::isfinite(dz)){Reset();return CecilMotion();}
    const double vertical=dx*in.gravity[0]+dy*in.gravity[1]+dz*in.gravity[2];
    const double hx=dx-in.gravity[0]*vertical,hy=dy-in.gravity[1]*vertical,hz=dz-in.gravity[2]*vertical;
    const CecilVec local=in.frame.ToLocal(hx,hy,hz);
    // Original stay-on-point rule uses the actual gravity plane, including transitions.
    if(hx*hx+hy*hy+hz*hz<1&&std::fabs(vertical)>4){Progress(in);return out;}
    if(recovery_until_<0&&in.now-progress_time_>=2.0) {
      out.supported_lock_started=false;supported_lock_hop_=-1;recovery_until_=in.now+.5;next_replan_=in.now;Progress(in);
    }
    if(in.now<recovery_until_) {
      out.stuck=true;out.forward=-.4;out.strafe=(in.slot&1)?-.8:.8;
    } else if(local.x*local.x+local.z*local.z>1e-12) {
      const AimAngles aim=AimAt(local.x,0,local.z);
      const double error=std::remainder(aim.yaw_deg-in.yaw,360.0);
      const double radians=error*std::acos(-1.0)/180.0;
      out.forward=std::cos(radians);out.strafe=-std::sin(radians);
      out.yaw_delta=TestTurnDelta(in.yaw,aim.yaw_deg,in.turn_speed_deg*in.dt);
    }
    if(out.flags&CECIL_WALK){out.forward*=.5;out.strafe*=.5;}
    if(out.flags&CECIL_CROUCH)out.up=-1;
    else if((out.flags&CECIL_JUMP)&&in.allow_jump&&in.now+1e-9>=next_jump_) {
      out.up=1;next_jump_=in.now+.2;
    }
    return out;
  }
 private:
  static double Distance2(double x,double y,double z){return x*x+y*y+z*z;}
  static bool Valid(const CecilMotionInput& in) {
    if(!std::isfinite(in.x)||!std::isfinite(in.y)||!std::isfinite(in.z)||
       !std::isfinite(in.yaw)||!std::isfinite(in.now)||in.now<0||
       !std::isfinite(in.dt)||in.dt<=0||in.dt>1||
       !std::isfinite(in.turn_speed_deg)||in.turn_speed_deg<0||in.turn_speed_deg>720)return false;
    if(!in.frame.Valid())return false;
    double gravityLength=0;
    for(int i=0;i<3;++i){if(!std::isfinite(in.gravity[i]))return false;gravityLength+=in.gravity[i]*in.gravity[i];}
    return std::fabs(gravityLength-1)<1e-3;
  }
  static bool Reached(const CecilNavPoint& p,const CecilMotionInput& in) {
    const double x=double(p.x)-in.x,y=double(p.y)-in.y,z=double(p.z)-in.z,r=p.radius;
    if(!std::isfinite(r)||r<=0)return false;
    return Distance2(x,y,z)<r*r||
      Distance2(x-in.gravity[0]*r*.5,y-in.gravity[1]*r*.5,z-in.gravity[2]*r*.5)<r*r;
  }
  void Progress(const CecilMotionInput& in) {
    have_progress_=true;progress_time_=in.now;px_=in.x;py_=in.y;pz_=in.z;
  }
  CecilNavSearch search_;
  std::vector<unsigned char> locks_;
  int source_=-1,hop_=-1,goal_=-1,supported_lock_hop_=-1;
  double last_time_=-1,next_replan_=0,next_jump_=0,recovery_until_=-1;
  bool have_progress_=false;
  double progress_time_=0,px_=0,py_=0,pz_=0;
};
}
#endif
