// Bounded travel memory built solely from this player's own observations.
// Unknown space is NOT asserted to be safe. Existing retail collision recovery
// remains authoritative; no ground rays, map objects or engine layouts here.
#ifndef BOTCORE_BOT_ROUTE_H
#define BOTCORE_BOT_ROUTE_H
#include <cmath>
#include "bot_aim.h"

namespace botcore {
struct TravelIntent { double yaw_delta_deg=0, forward=0; };

class RouteMemory {
 public:
  void Configure(uint32_t seed) {
    rng_=Lcg(seed ? seed : 1u);
    cells_=hazards_=0;last_cell_=-1;have_previous_=have_goal_=recovering_=false;
    injured_=false;
    next_goal_=progress_tick_=0;
  }

  void Observe(int tick,double x,double y,double z,bool alive,double health,bool visible_threat,
               double max_health=100.0) {
    if (!alive) injured_=false;
    if (!Finite(x,y,z) || !std::isfinite(health)) {have_previous_=false;return;}
    const double healthy_above=std::isfinite(max_health) && max_health>0 ? max_health*.5 : 50;
    if (health>healthy_above) injured_=false;
    if (have_previous_ && previous_alive_ && health<previous_health_-24.99 && !visible_threat) {
      // A damage impulse may already have launched the player vertically.
      // Associate the warning with the previous observation, not an upper floor.
      if (Squared(x-previous_x_,z-previous_z_)<64) {
        MarkHazard(tick,previous_x_,previous_y_,previous_z_);
        if (std::fabs(y-previous_y_)<3) MarkHazard(tick,x,y,z);
      }
      // This is an unattributed damage warning, not proof of a terrain type.
      // Finishing the bounded retreat must not restart novelty while injured.
      if (alive && health<=healthy_above) injured_=true;
    }
    if (!alive || (have_previous_ && Squared(x-previous_x_,z-previous_z_)>256)) {
      have_goal_=false;last_cell_=-1;
    }
    if (alive && tick%5==0) Visit(tick,x,y,z);
    previous_x_=x;previous_y_=y;previous_z_=z;previous_health_=health;
    previous_alive_=alive;have_previous_=true;tick_=tick;
  }

  void NotifyRecovery(bool active) {
    recovering_=active;
    if (active) have_goal_=false;
  }

  bool InjuryHold() const { return injured_; }

  bool SafeMotion(double x,double y,double z,double yaw,double forward,double strafe) const {
    if (!Finite(x,y,z) || !std::isfinite(yaw) || !std::isfinite(forward) || !std::isfinite(strafe)) return false;
    if (std::fabs(forward)+std::fabs(strafe)<1e-6) return true;
    // Retail forward = (-sin(yaw), -cos(yaw)), right = (cos(yaw), -sin(yaw)).
    const double a=yaw*kDegToRad;
    double dx=-std::sin(a)*forward+std::cos(a)*strafe;
    double dz=-std::cos(a)*forward-std::sin(a)*strafe;
    const double length=std::hypot(dx,dz);
    if (length<1e-6) return true;
    dx*=6/length;dz*=6/length;
    return HazardCost(x,y,z,x+dx,z+dz)==0;
  }

  TravelIntent Travel(int tick,double x,double y,double z,double yaw,double limit) {
    TravelIntent out;
    if (!Finite(x,y,z) || !std::isfinite(yaw) || !std::isfinite(limit) || limit<=0) return out;
    if (injured_) return out;
    if (recovering_) {
      out.forward=SafeMotion(x,y,z,yaw,1,0) ? .9 : 0;
      return out;
    }
    bool stuck=false;
    if (have_goal_ && tick-progress_tick_>=40) {
      stuck=Squared(x-progress_x_,z-progress_z_)<1;
      progress_tick_=tick;progress_x_=x;progress_z_=z;
    }
    if (!have_goal_ || tick>=next_goal_ || stuck || !SafeMotion(x,y,z,desired_yaw_,1,0)) {
      static const double offsets[]={0,45,-45,90,-90,135,-135,180};
      double best=1e30;
      for (double offset:offsets) {
        const double heading=yaw+offset,a=heading*kDegToRad;
        const double end_x=x-12*std::sin(a),end_z=z-12*std::cos(a);
        double score=HazardCost(x,y,z,end_x,end_z)*1000+std::fabs(offset)/180;
        if (stuck && std::fabs(offset)<60) score+=4;
        for (int step=1;step<=3;++step) {
          const double px=x-6*step*std::sin(a),pz=z-6*step*std::cos(a);
          for (int i=0;i<cells_;++i)
            if (std::fabs(y-cell_[i].y)<4 && Squared(px-cell_[i].x,pz-cell_[i].z)<25)
              score+=1+cell_[i].visits*.25;
        }
        score+=(rng_.Next()%1000)*.00001; // deterministic tie variation per identity
        if (score<best) {best=score;desired_yaw_=heading;}
      }
      have_goal_=true;next_goal_=tick+80+static_cast<int>(rng_.Next()%81);
      progress_tick_=tick;progress_x_=x;progress_z_=z;
    }
    const double error=AimController::WrapDeg(desired_yaw_-yaw);
    out.yaw_delta_deg=error < -limit ? -limit : (error > limit ? limit : error);
    out.forward=std::fabs(error)<35 && SafeMotion(x,y,z,yaw,1,0) ? .9 : 0;
    return out;
  }

 private:
  struct Cell {double x,y,z;int visits,tick;};
  struct Hazard {double x,y,z;int tick;};
  static bool Finite(double x,double y,double z) {
    return std::isfinite(x)&&std::isfinite(y)&&std::isfinite(z);
  }
  static double Squared(double x,double z) {return x*x+z*z;}
  void Visit(int tick,double x,double y,double z) {
    int found=-1;
    for (int i=0;i<cells_;++i)
      if (std::fabs(y-cell_[i].y)<4 && Squared(x-cell_[i].x,z-cell_[i].z)<16) {found=i;break;}
    if (found<0) {
      if (cells_<96) found=cells_++;
      else {
        found=0;for(int i=1;i<96;++i)if(cell_[i].tick<cell_[found].tick)found=i;
      }
      cell_[found]={x,y,z,0,tick};
    }
    Cell& c=cell_[found];c.tick=tick;
    if(found!=last_cell_ && c.visits<1000)++c.visits;
    last_cell_=found;
  }
  void MarkHazard(int tick,double x,double y,double z) {
    for (int i=0;i<hazards_;++i)
      if (std::fabs(y-hazard_[i].y)<4 && Squared(x-hazard_[i].x,z-hazard_[i].z)<16) {
        hazard_[i].tick=tick;return;
      }
    int i=hazards_<16 ? hazards_++ : 0;
    if (hazards_==16)for(int j=1;j<16;++j)if(hazard_[j].tick<hazard_[i].tick)i=j;
    hazard_[i]={x,y,z,tick};have_goal_=false;
  }
  double HazardCost(double x,double y,double z,double end_x,double end_z) const {
    double cost=0;const double dx=end_x-x,dz=end_z-z,len2=Squared(dx,dz);
    for (int i=0;i<hazards_;++i) {
      const Hazard& h=hazard_[i];
      if (tick_-h.tick>12000 || std::fabs(y-h.y)>=4)continue;
      const double start2=Squared(x-h.x,z-h.z),end2=Squared(end_x-h.x,end_z-h.z);
      // Allow escape out of a warning area instead of trapping the player in it.
      if (start2<25 && end2>start2+4)continue;
      double t=len2>1e-9?((h.x-x)*dx+(h.z-z)*dz)/len2:0;
      if(t<0)t=0;
      if(t>1)t=1;
      const double nearest2=Squared(x+t*dx-h.x,z+t*dz-h.z);
      if(nearest2<25)cost+=25-nearest2;
    }
    return cost;
  }
  Cell cell_[96]{};Hazard hazard_[16]{};int cells_=0,hazards_=0,last_cell_=-1,tick_=0;
  Lcg rng_{1};bool have_previous_=false,previous_alive_=false,have_goal_=false,recovering_=false;
  bool injured_=false;
  double previous_x_=0,previous_y_=0,previous_z_=0,previous_health_=0;
  double desired_yaw_=0,progress_x_=0,progress_z_=0;int next_goal_=0,progress_tick_=0;
};
}
#endif
