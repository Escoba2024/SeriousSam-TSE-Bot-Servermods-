#include "bot_supply_navigation.h"
#include <cstdio>
#include <cmath>
#include <fstream>
#include <string>
int failures=0;
void check(bool yes,const char* name){if(!yes){++failures;std::printf("FAIL %s\n",name);}}
int main(int argc,char**argv){
 using namespace botcore;
 WaypointGraph g;g.AddNode(0,0,0);g.AddNode(0,0,-10);g.AddNode(10,0,-10);g.AddNode(10,0,0);g.Link(0,1);g.Link(1,2);g.Link(2,3);
 SupplySpot item;item.id=17;item.weapon=4;item.node=3;item.x=10;item.direct=false;
 SupplyInput in;in.alive=true;in.anchor=0;in.owned=7;in.tick=1;
 SupplyPlanner p;auto out=p.Update(g,&item,1,in);
 check(out.active && out.goal==17 && out.hop==1,"route uses connected waypoint around obstruction");
 check(out.active && std::fabs(out.yaw_delta)<.01 && out.forward>0,"route follows first hop rather than item through wall");
 in.owned|=1u<<3;out=p.Update(g,&item,1,in);check(!out.active,"collected weapon returns control to combat");
 in.owned=7;in.close_threat=true;out=p.Update(g,&item,1,in);check(!out.active,"immediate threat retains self defense");
 in.close_threat=false;in.alive=false;out=p.Update(g,&item,1,in);check(!out.active,"dead player receives no travel action");
 in.alive=true;in.tick=2;p.Reset();out=p.Update(g,nullptr,0,in);check(!out.active,"empty pickup feed fails safe");
 WaypointGraph disconnected;disconnected.AddNode(0,0,0);disconnected.AddNode(20,0,0);item.node=1;p.Reset();out=p.Update(disconnected,&item,1,in);check(!out.active,"disconnected item is not chased through walls");
 item.direct=true;item.node=-1;item.x=0;item.z=-10;p.Reset();out=p.Update(g,&item,1,in);check(out.active && out.hop==-1 && out.forward>0,"visible nearby weapon uses direct approach");
 p.Reset();item.direct=false;item.node=3;item.x=10;item.z=0;in.tick=1;p.Update(g,&item,1,in);in.tick=61;out=p.Update(g,&item,1,in);check(!out.active,"stalled goal is temporarily rejected");
 in.tick=62;out=p.Update(g,&item,1,in);check(!out.active,"stalled goal does not immediately restart");
 p.Reset();in.tick=1;p.Update(g,&item,1,in);in.tick=500;out=p.Update(g,&item,1,in);check(!out.active,"weapon rush has bounded duration");
 if(argc>1){WaypointGraph measured;std::ifstream f(argv[1]);std::string line;bool ok=true;while(std::getline(f,line))if(!measured.ParseLine(line.c_str())){ok=false;break;}check(ok && measured.node_count()==236,"existing measured Red Station graph parses completely");}
 p.Reset();in.tick=1;in.anchor=0;item.direct=true;item.node=-1;item.x=10;item.z=0;p.Update(g,&item,1,in);
 item.direct=false;item.node=3;in.tick=21;out=p.Update(g,&item,1,in);check(out.active&&out.hop==1,"lost direct connector replans through waypoint graph");
 p.Reset();in.tick=1;item.direct=true;item.node=-1;item.x=0;item.z=-10;in.x=0;in.z=0;
 SupplySpot alternatives[2]={item,item};alternatives[0].id=20;alternatives[0].z=-20;alternatives[1].id=21;alternatives[1].z=-5;
 out=p.Update(g,alternatives,2,in);check(out.goal==21,"nearest reachable useful weapon is preferred");
 in.x=std::nan("");out=p.Update(g,&item,1,in);check(!out.active,"invalid position cannot emit movement");in.x=0;
 p.Reset();in.tick=1;p.Update(g,&item,1,in);in.alive=false;in.tick=500;p.Update(g,&item,1,in);in.alive=true;in.tick=501;out=p.Update(g,&item,1,in);check(out.active,"respawn resets bounded rush timer");
 WaypointGraph malformed;check(!malformed.ParseLine("node nan 0 0"),"nonfinite map coordinate rejected");check(!malformed.ParseLine("edge 0 1"),"edge references require existing nodes");
 p.Reset();in.alive=true;in.owned=7;in.anchor=-1;in.tick=300;item.direct=false;item.node=-1;p.Update(g,&item,1,in);
 in.tick=1;item.direct=true;out=p.Update(g,&item,1,in);check(out.active,"new source tick restart cannot retain old retry deadline");
 CombatWeaponInput select;bool knife=false;for(int tick=1;tick<=25;++tick){const auto buttons=select.Poll(tick,ResolveSupplyWeapon(2,true),3,0);knife=knife||(buttons==(1u<<14));}
 check(knife,"final supply arbitration emits knife group instead of discarded Colt request");
 check(ResolveSupplyWeapon(5,false)==5,"combat weapon retained outside supply");
 std::printf("supply navigation failures=%d\n",failures);return failures?1:0;
}
