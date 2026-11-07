// SPDX-License-Identifier: GPL-2.0-only
// ssam.ai body-frame projections, 2026-11-07. No engine objects or allocations.
#ifndef BOTCORE_CECIL_FRAME_H
#define BOTCORE_CECIL_FRAME_H
#include <cmath>
namespace botcore {
struct CecilVec {double x,y,z;};
struct CecilFrame {
  // World-space native body axes: local X(right), Y(up), Z(back).
  double right[3]={1,0,0},up[3]={0,1,0},back[3]={0,0,1};
  bool Valid()const{
    const double* axes[3]={right,up,back};
    for(int i=0;i<3;++i){
      double length=0;
      for(int k=0;k<3;++k){if(!std::isfinite(axes[i][k]))return false;length+=axes[i][k]*axes[i][k];}
      if(std::fabs(length-1)>1e-3)return false;
      for(int j=0;j<i;++j){
        double dot=0;for(int k=0;k<3;++k)dot+=axes[i][k]*axes[j][k];
        if(std::fabs(dot)>1e-3)return false;
      }
    }
    const double determinant=(right[1]*up[2]-right[2]*up[1])*back[0]+
      (right[2]*up[0]-right[0]*up[2])*back[1]+(right[0]*up[1]-right[1]*up[0])*back[2];
    return std::fabs(determinant-1)<=3e-3;
  }
  // Callers validate snapshots before emitting actions. Projections never normalize
  // or silently repair an invalid basis, and remembered positions remain world-space.
  CecilVec ToLocal(double dx,double dy,double dz)const{
    return {dx*right[0]+dy*right[1]+dz*right[2],
            dx*up[0]+dy*up[1]+dz*up[2],
            dx*back[0]+dy*back[1]+dz*back[2]};
  }
  CecilVec ToWorld(double x,double y,double z)const{
    return {x*right[0]+y*up[0]+z*back[0],
            x*right[1]+y*up[1]+z*back[1],
            x*right[2]+y*up[2]+z*back[2]};
  }
};
}
#endif
