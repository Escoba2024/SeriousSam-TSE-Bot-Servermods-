// Optional, bounded weapon-acquisition policy. No engine/world mutation.
#ifndef BOT_SUPPLY_NAVIGATION_H
#define BOT_SUPPLY_NAVIGATION_H
#include "botcore.h"
#include "bot_weapon_input.h"
#include "botcore_ai.h"
#include "bot_redstation_behavior.h"
namespace botcore {
struct SupplySpot {int id=0,weapon=0,node=-1;double x=0,y=0,z=0;bool direct=false;};
struct SupplyInput {int tick=0,anchor=-1;double x=0,y=0,z=0,yaw=0,turn_limit=9;uint32_t owned=0;bool alive=false,close_threat=false;};
struct SupplyMove {bool active=false;double yaw_delta=0,forward=0;int goal=-1,hop=-1;};
inline int ResolveSupplyWeapon(int combat,bool supply){return supply?1:combat;}
class SupplyPlanner {
 public:
  void Reset(){*this=SupplyPlanner();}
  SupplyMove Update(const WaypointGraph& g,const SupplySpot* spots,int count,const SupplyInput& in){
    SupplyMove out;
    if(!in.alive){Reset();return out;}
    if(!Finite(in.x,in.y,in.z)||!std::isfinite(in.yaw)||!std::isfinite(in.turn_limit)||in.turn_limit<=0||in.tick<0)return out;
    if(was_alive_&&in.tick<last_tick_)Reset();
    last_tick_=in.tick;
    if(!was_alive_){was_alive_=true;spawn_tick_=in.tick;}
    if(HasCollectedWeapon(in.owned)){goal_=-1;return out;}
    if(in.tick-spawn_tick_>=440 || in.close_threat)return out;
    if(spots==nullptr||count<=0){goal_=-1;return out;}
    if(count>32)count=32;
    int chosen=-1;
    for(int i=0;i<count;++i)if(spots[i].id==goal_&&Valid(spots[i],in.owned)){chosen=i;break;}
    if(chosen>=0 && (spots[chosen].direct!=planned_direct_ || spots[chosen].node!=planned_node_)){chosen=-1;}
    if(chosen>=0 && in.tick-progress_tick_>=60){
      const double d2=Distance2(in.x,in.z,progress_x_,progress_z_);
      progress_tick_=in.tick;progress_x_=in.x;progress_z_=in.z;
      if(d2<2.25){blocked_id_=goal_;blocked_until_=in.tick+100;goal_=-1;retry_tick_=in.tick+20;return out;}
    }
    if(chosen<0){
      goal_=-1;
      if(in.tick<retry_tick_)return out;
      retry_tick_=in.tick+20;
      double dist[WaypointGraph::kMaxNodes];int parent[WaypointGraph::kMaxNodes];
      BuildDistances(g,in.anchor,dist,parent);
      double best=1e30;
      for(int i=0;i<count;++i){
        const SupplySpot& spot=spots[i];
        if(!Valid(spot,in.owned)||(spot.id==blocked_id_&&in.tick<blocked_until_))continue;
        double score=1e30;
        if(spot.direct)score=std::sqrt(Distance2(in.x,in.z,spot.x,spot.z));
        else if(in.anchor>=0&&spot.node>=0&&spot.node<g.node_count()&&dist[spot.node]<1e29){
          double x,y,z;g.NodePosition(in.anchor,&x,&y,&z);
          const double entry=std::sqrt(Distance2(in.x,in.z,x,z));
          g.NodePosition(spot.node,&x,&y,&z);
          score=entry+dist[spot.node]+std::sqrt(Distance2(x,z,spot.x,spot.z));
        }
        // Travel cost dominates: get any missing firearm instead of wandering
        // past a nearby useful weapon to chase a distant "best" weapon.
        if(score<best){best=score;chosen=i;}
      }
      if(chosen<0)return out;
      const SupplySpot& spot=spots[chosen];goal_=spot.id;path_len_=path_pos_=0;
      planned_direct_=spot.direct;planned_node_=spot.node;
      if(!spot.direct){
        int reverse[WaypointGraph::kMaxNodes],n=0,at=spot.node;
        while(at>=0&&n<WaypointGraph::kMaxNodes){reverse[n++]=at;if(at==in.anchor)break;at=parent[at];}
        if(n==0||reverse[n-1]!=in.anchor){goal_=-1;return out;}
        for(int i=n-1;i>=0;--i)path_[path_len_++]=reverse[i];
      }
      progress_tick_=in.tick;progress_x_=in.x;progress_z_=in.z;
    }
    const SupplySpot& spot=spots[chosen];double tx=spot.x,ty=spot.y,tz=spot.z;
    while(path_pos_<path_len_){
      g.NodePosition(path_[path_pos_],&tx,&ty,&tz);
      if(Distance2(in.x,in.z,tx,tz)>2.25||std::fabs(in.y-ty)>3.5)break;
      ++path_pos_;
    }
    if(path_pos_>=path_len_){tx=spot.x;ty=spot.y;tz=spot.z;}
    if(!Finite(tx,ty,tz))return out;
    const AimAngles aim=AimAt(tx-in.x,0,tz-in.z);
    const double error=TestTurnDelta(in.yaw,aim.yaw_deg,180);
    out.active=true;out.goal=goal_;out.hop=path_pos_<path_len_?path_[path_pos_]:-1;
    out.yaw_delta=TestTurnDelta(in.yaw,aim.yaw_deg,in.turn_limit);
    out.forward=std::fabs(error)<35?1.0:(std::fabs(error)<75?.3:0);
    return out;
  }
 private:
  static bool Finite(double x,double y,double z){return std::isfinite(x)&&std::isfinite(y)&&std::isfinite(z);}
  static double Distance2(double x,double z,double a,double b){return (x-a)*(x-a)+(z-b)*(z-b);}
  static bool Valid(const SupplySpot& s,uint32_t owned){return s.weapon>=4&&s.weapon<=14&&(owned&(1u<<(s.weapon-1)))==0&&Finite(s.x,s.y,s.z);}
  static void BuildDistances(const WaypointGraph& g,int start,double* dist,int* parent){
    bool used[WaypointGraph::kMaxNodes]{};const int n=g.node_count();
    for(int i=0;i<WaypointGraph::kMaxNodes;++i){dist[i]=1e30;parent[i]=-1;}
    if(start<0||start>=n)return;
    dist[start]=0;
    for(int round=0;round<n;++round){
      int a=-1;for(int i=0;i<n;++i)if(!used[i]&&(a<0||dist[i]<dist[a]))a=i;
      if(a<0||dist[a]>=1e29)break;
      used[a]=true;
      double ax,ay,az;g.NodePosition(a,&ax,&ay,&az);
      for(int b=0;b<n;++b){
        if(used[b]||!g.IsAdjacent(a,b))continue;
        double bx,by,bz;g.NodePosition(b,&bx,&by,&bz);
        const double cost=std::sqrt((ax-bx)*(ax-bx)+(ay-by)*(ay-by)+(az-bz)*(az-bz));
        if(dist[a]+cost<dist[b]){dist[b]=dist[a]+cost;parent[b]=a;}
      }
    }
  }
  bool was_alive_=false,planned_direct_=false;int planned_node_=-1,last_tick_=0;int spawn_tick_=0,goal_=-1,retry_tick_=0,blocked_id_=-1,blocked_until_=0;
  int progress_tick_=0,path_[WaypointGraph::kMaxNodes]{},path_len_=0,path_pos_=0;
  double progress_x_=0,progress_z_=0;
};
}
#endif
