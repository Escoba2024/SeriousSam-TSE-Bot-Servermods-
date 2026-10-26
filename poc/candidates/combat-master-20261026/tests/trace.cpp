// Same seeded inputs compiled separately against pristine PR57 and candidate.
#include "bot_human.h"
#include <cstdio>
using namespace botcore;
int main(){
 for(int tier=1;tier<=5;++tier)for(int persona=0;persona<6;++persona)for(int cecil=0;cecil<2;++cecil){
 BotProfile p;BuildProfile(tier,persona,20261026u,"trace",&p);HumanBotPolicy h;h.Configure(&p,false,cecil!=0);
 for(int t=0;t<360;++t){WorldView w;w.tick=t;w.alive=t<220 || t>=270;w.health=w.alive?(t<150?100:35):0;w.current_weapon=6;w.usable_weapons=t<100?0x3fffu:(1u<<5);w.pose.x=(t%29)*.05;w.pose.yaw_deg=(t%13)-6;
 SenseInput e[2]{};e[0].index=1;e[0].alive=true;e[0].x=(t%47)*.07;e[0].z=-18;e[0].vx=1.4;e[0].health=80;e[0].facing_known=true;e[0].yaw_deg=180;
 e[1]=e[0];e[1].index=2;e[1].z=-25;e[1].health=15;bool los[2]={t%50<40,t%60<45};h.BeginTick(w);bool rays[2];h.PlanLosQueries(e,2,rays);auto c=h.Step(w,e,los,2,.05);
 std::printf("%d %d %d %d %d %d %.17g %.17g %.17g %.17g %d %d %.17g %.17g %.17g %d %d %d\n",tier,persona,cecil,t,c.target,c.target_visible,c.yaw_delta_deg,c.pitch_delta_deg,c.forward,c.strafe,c.fire,c.weapon,c.aim_error_deg,c.preferred_range_m,c.distance_m,c.escape,c.travel,h.ShouldRespawnPulse(t));}
 }
}
