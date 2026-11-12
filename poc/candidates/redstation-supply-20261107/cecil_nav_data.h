// Copyright (c) 2018-2023 Dreamy Cecil; ssam.ai adaptations 2026.
// SPDX-License-Identifier: GPL-2.0-only
// Format: CecilBotMod 953b477, PathPoint/Navmesh.
// Original data is immutable after publication; load only outside the game timer.
#ifndef BOTCORE_CECIL_NAV_DATA_H
#define BOTCORE_CECIL_NAV_DATA_H
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <limits>
#include <new>
#include <string>
#include <utility>
#include <vector>
namespace botcore {
enum CecilNavFlag { CECIL_WALK=1,CECIL_JUMP=2,CECIL_CROUCH=4,CECIL_OVERRIDE=8,
  CECIL_UNREACHABLE=16,CECIL_TELEPORT=32,CECIL_IMPORTANT=64 };
struct CecilNavPoint {
  int id=0; float x=0,y=0,z=0,radius=1; uint32_t flags=0;
  int important_entity=-1,next_slot=-1,lock_entity=-1;
  float lock_origin[6]{};
  int polygon_kind=0; // 0 none, 1 PPO1, 2 PPO2
  std::vector<std::array<float,3>> polygon;
  std::vector<int> links; // Array slots, not stable IDs.
};
namespace cecil_nav_detail {
class Reader {
 public:
  Reader(const unsigned char* bytes,size_t size):bytes_(bytes),size_(size){}
  uint32_t Word() {
    Require(4);uint32_t v=0;
    for(int i=0;i<4;++i)v|=uint32_t(bytes_[pos_++])<<(8*i);
    return v;
  }
  int Integer(){const uint32_t u=Word();int32_t v;std::memcpy(&v,&u,4);return v;}
  float Real(){const uint32_t u=Word();float v;std::memcpy(&v,&u,4);
    if(!std::isfinite(v))throw "nonfinite NAV value";
    return v;
  }
  float Coordinate(){const float v=Real();if(std::fabs(v)>100000)throw "NAV coordinate out of range";return v;}
  unsigned char Byte(){Require(1);return bytes_[pos_++];}
  void Tag(const char* tag){Require(4);if(std::memcmp(bytes_+pos_,tag,4)!=0)throw "invalid NAV chunk";pos_+=4;}
  int PolygonTag(){Require(4);int k=0;
    if(std::memcmp(bytes_+pos_,"PPO1",4)==0)k=1;
    else if(std::memcmp(bytes_+pos_,"PPO2",4)==0)k=2;
    else throw "unsupported polygon";
    pos_+=4;return k;
  }
  bool End()const{return pos_==size_;}
 private:
  void Require(size_t n){if(n>size_-pos_)throw "truncated NAV";}
  const unsigned char* bytes_;size_t size_,pos_=0;
};
}
struct CecilNavGraph {
  static const size_t kMaxPoints=4096;
  static const size_t kMaxBytes=10*1024*1024;
  int version=0,next_point_id=0; bool generated=false;
  std::vector<CecilNavPoint> points;

  // A rejected file clears the old graph: never route on stale map data.
  bool Load(const unsigned char* bytes,size_t size,std::string* error=nullptr) {
    version=next_point_id=0;generated=false;points.clear();
    if(error)error->clear();
    try {
      if(bytes==nullptr||size>kMaxBytes)throw "invalid NAV input size";
      cecil_nav_detail::Reader r(bytes,size);r.Tag("BNMV");
      const int v=r.Integer(),gen=r.Integer(),next=r.Integer(),count=r.Integer();
      if(v!=6||(gen!=0&&gen!=1)||count<1||count>(int)kMaxPoints)throw "unsupported NAV header";
      if(next<count||next>1000000)throw "invalid next point ID";
      std::vector<CecilNavPoint> loaded;loaded.reserve((size_t)count);
      for(int slot=0;slot<count;++slot) {
        r.Tag("BPPH");CecilNavPoint p;p.id=r.Integer();
        p.x=r.Coordinate();p.y=r.Coordinate();p.z=r.Coordinate();p.radius=r.Real();p.flags=r.Word();
        p.important_entity=r.Integer();p.next_slot=r.Integer();p.lock_entity=r.Integer();
        if(p.id<0||p.id>=next||p.radius<=0||p.radius>1000||(p.flags&~127u))throw "invalid point metadata";
        for(const auto& prior:loaded)if(prior.id==p.id)throw "duplicate point ID";
        if(p.important_entity< -1||p.lock_entity< -1||p.next_slot< -1||p.next_slot>=count)throw "invalid entity or next slot";
        if(p.lock_entity!=-1)for(float& f:p.lock_origin)f=r.Real();
        const int links=r.Integer();if(links<0||links>count)throw "invalid link count";
        p.links.reserve((size_t)links);
        for(int j=0;j<links;++j) {
          const int target=r.Integer();
          if(target<0||target>=count||target==slot||std::find(p.links.begin(),p.links.end(),target)!=p.links.end())
            throw "invalid directed link";
          p.links.push_back(target);
        }
        const unsigned char polygon=r.Byte();if(polygon>1)throw "invalid polygon marker";
        if(polygon) {
          p.polygon_kind=r.PolygonTag();
          const int vertices=p.polygon_kind==1?3:r.Integer();
          if(vertices<3||vertices>1024)throw "invalid polygon vertex count";
          p.polygon.reserve((size_t)vertices);
          for(int j=0;j<vertices;++j) {
            const float x=r.Coordinate(),y=r.Coordinate(),z=r.Coordinate();
            p.polygon.push_back({{x,y,z}});
          }
        }
        loaded.push_back(std::move(p));
      }
      if(!r.End())throw "trailing NAV bytes";
      points.swap(loaded);version=v;generated=gen!=0;next_point_id=next;return true;
    } catch(const char* message) {if(error)*error=message;}
      catch(const std::bad_alloc&) {if(error)*error="NAV allocation failed";}
    return false;
  }
};
// Read only an already prepared parent chain. Edge absence alone is not proof:
// every original arc must be valid and the bounded chain must reach its start.
inline bool CecilNavPathAvoidsEdge(const CecilNavGraph& graph,const int* parents,size_t size,
    int start,int goal,int from,int to,const unsigned char* blocked=nullptr,size_t count=0){
  const size_t n=graph.points.size();
  if(!parents||n==0||n>CecilNavGraph::kMaxPoints||size!=n||start<0||goal<0||from<0||to<0||
     (size_t)start>=n||(size_t)goal>=n||(size_t)from>=n||(size_t)to>=n||
     (blocked?count!=n:count!=0))return false;
  int at=goal;
  for(size_t step=0;step<n;++step){
    if(at<0||(size_t)at>=n||(blocked&&blocked[at]))return false;
    if(at==start)return true;
    const int parent=parents[at];
    if(parent<0||(size_t)parent>=n||(parent==from&&at==to)||
       std::find(graph.points[parent].links.begin(),graph.points[parent].links.end(),at)==graph.points[parent].links.end())return false;
    at=parent;
  }
  return false;
}
class CecilNavSearch {
 public:
  // Allocate once per map, before publishing this per-bot search context.
  void Prepare(size_t nodes) {
    if(nodes>CecilNavGraph::kMaxPoints)nodes=0;
    distances_.assign(nodes,Infinity());parents_.assign(nodes,-1);used_.assign(nodes,0);start_=-1;
  }
  // h=0 deliberately corrects Cecil's non-admissible teleport A* heuristic.
  // Blocked destinations represent a snapshot of locks; an origin may exit.
  bool Run(const CecilNavGraph& graph,int start,const unsigned char* blocked=nullptr,size_t count=0) {
    start_=-1;
    std::fill(distances_.begin(),distances_.end(),Infinity());
    std::fill(parents_.begin(),parents_.end(),-1);
    std::fill(used_.begin(),used_.end(),0);
    const size_t n=graph.points.size();
    if(n==0||n>CecilNavGraph::kMaxPoints||distances_.size()!=n||start<0||(size_t)start>=n)return false;
    if(blocked?count!=n:count!=0)return false;
    // Public snapshot fields are validated before indexing, even for synthetic callers.
    for(const auto& p:graph.points) {
      if(!std::isfinite(p.x)||!std::isfinite(p.y)||!std::isfinite(p.z)||(p.flags&~127u))return false;
      for(int target:p.links)if(target<0||(size_t)target>=n)return false;
    }
    start_=start;distances_[start]=0;
    for(size_t round=0;round<n;++round) {
      int best=-1;
      for(size_t i=0;i<n;++i)if(!used_[i]&&(best<0||distances_[i]<distances_[best]))best=(int)i;
      if(best<0||!std::isfinite(distances_[best]))break;
      used_[best]=1;const CecilNavPoint& p=graph.points[best];
      for(int target:p.links) {
        if(used_[target]||(blocked&&blocked[target]))continue;
        const CecilNavPoint& q=graph.points[target];
        const double x=double(p.x)-q.x,y=double(p.y)-q.y,z=double(p.z)-q.z;
        const double cost=(p.flags&CECIL_TELEPORT)?0:std::sqrt(x*x+y*y+z*z);
        const double distance=distances_[best]+cost;
        if(distance<distances_[target]){distances_[target]=distance;parents_[target]=best;}
      }
    }
    return true;
  }
  // Read-only selected-path observation; no search or allocation.
  int Parent(int slot) const {
    return start_>=0&&slot>=0&&(size_t)slot<parents_.size()?parents_[slot]:-1;
  }
  // Observe only this existing search tree. The root may be the committed
  // source (initial search) or its hop (suffix refresh); never search here.
  int SelectedSuccessor(const CecilNavGraph& graph,int goal,int source,int hop,
      const unsigned char* blocked,size_t count) const {
    const size_t n=parents_.size();
    if(n==0||n!=graph.points.size()||!blocked||count!=n||
       source<0||hop<0||source==hop||(size_t)source>=n||(size_t)hop>=n||
       (start_!=source&&start_!=hop)||!std::isfinite(Distance(goal))||
       blocked[source]||blocked[hop]||
       (start_==source&&Parent(hop)!=source))return -1;
    int at=goal,successor=-1;
    for(size_t steps=0;steps<n;++steps){
      if(at<0||(size_t)at>=n||blocked[at])return -1;
      if(at==start_)return successor;
      const int parent=parents_[at];
      if(parent<0||(size_t)parent>=n||parent==at)return -1;
      const auto& links=graph.points[parent].links;
      if(std::find(links.begin(),links.end(),at)==links.end())return -1;
      if(parent==hop)successor=at;
      at=parent;
    }
    return -1;
  }
  int NextHop(int goal) const {
    if(!std::isfinite(Distance(goal)))return -1;
    if(goal==start_)return start_;
    int at=goal;
    for(size_t step=0;step<parents_.size();++step) {
      const int parent=parents_[at];
      if(parent==start_)return at;
      if(parent<0||(size_t)parent>=parents_.size())return -1;
      at=parent;
    }
    return -1;
  }
  double Distance(int goal) const {
    return start_>=0&&goal>=0&&(size_t)goal<distances_.size()?distances_[goal]:Infinity();
  }
  bool PathAvoidsEdge(const CecilNavGraph& graph,int goal,int from,int to,
      const unsigned char* blocked=nullptr,size_t count=0)const{
    return std::isfinite(Distance(goal))&&
      CecilNavPathAvoidsEdge(graph,parents_.data(),parents_.size(),start_,goal,from,to,blocked,count);
  }
 private:
  static double Infinity(){return std::numeric_limits<double>::infinity();}
  std::vector<double> distances_;
  std::vector<int> parents_;
  std::vector<unsigned char> used_;
  int start_=-1;
};
}
#endif
