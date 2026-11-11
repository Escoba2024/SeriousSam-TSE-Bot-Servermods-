// SPDX-License-Identifier: GPL-2.0-only
#include "cecil_frame.h"
#include <cstdio>
#include <limits>
static int checks=0,failures=0;
static void check(bool yes,const char* name){++checks;if(!yes){++failures;std::printf("FAIL %s\n",name);}}
static bool near(double a,double b){return std::fabs(a-b)<1e-9;}
int main(){
  botcore::CecilFrame frame;
  check(frame.Valid(),"identity body frame valid");
  auto p=frame.ToLocal(1,2,3);check(near(p.x,1)&&near(p.y,2)&&near(p.z,3),"identity preserves world components");
  frame.right[0]=-1;frame.up[1]=-1;
  check(frame.Valid(),"inverted right handed body frame valid");
  p=frame.ToLocal(1,2,-3);check(near(p.x,-1)&&near(p.y,-2)&&near(p.z,-3),"inverted local components");
  auto w=frame.ToWorld(p.x,p.y,p.z);check(near(w.x,1)&&near(w.y,2)&&near(w.z,-3),"inverted round trip");
  const double c=std::sqrt(.5);frame=botcore::CecilFrame();
  frame.up[1]=c;frame.up[2]=c;frame.back[1]=-c;frame.back[2]=c;
  check(frame.Valid(),"tilted transition frame valid");
  p=frame.ToLocal(0,0,-1);check(near(p.x,0)&&near(p.y,-c)&&near(p.z,-c),"tilted body projection");
  for(int i=-3;i<=3;++i)for(int j=-3;j<=3;++j){
    p=frame.ToLocal(i,j,2.5);w=frame.ToWorld(p.x,p.y,p.z);
    check(near(w.x,i)&&near(w.y,j)&&near(w.z,2.5),"tilted round trip preserves vector");
  }
  frame=botcore::CecilFrame();frame.right[0]=2;check(!frame.Valid(),"scaled basis rejected");
  frame=botcore::CecilFrame();frame.right[1]=.1;check(!frame.Valid(),"skew basis rejected");
  frame=botcore::CecilFrame();frame.up[1]=-1;check(!frame.Valid(),"reflection rejected");
  frame=botcore::CecilFrame();frame.back[2]=0;check(!frame.Valid(),"degenerate basis rejected");
  frame=botcore::CecilFrame();frame.up[0]=std::numeric_limits<double>::quiet_NaN();check(!frame.Valid(),"NaN basis rejected");
  frame=botcore::CecilFrame();frame.back[1]=std::numeric_limits<double>::infinity();check(!frame.Valid(),"infinite basis rejected");
  frame=botcore::CecilFrame();frame.right[0]=1+1e-5;check(frame.Valid(),"native float rounding tolerated");
  std::printf("cecil frame: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
