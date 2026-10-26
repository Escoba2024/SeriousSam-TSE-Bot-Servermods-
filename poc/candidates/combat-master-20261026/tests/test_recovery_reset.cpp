// Executes the actual generated native adapter reset branch with real policies.
#include "bot_human.h"
#include "bot_navigation.h"
#include <cstddef>
#include <cstdio>
static botcore::HumanBotPolicy human;
[[maybe_unused]] static botcore::HumanBotPolicy& BotHumanPolicy(int){return human;}
int main(){
 botcore::BotProfile p;botcore::BuildProfile(4,0,0x5702u,"reset",&p);human.Configure(&p,true);
 botcore::WorldView w;w.alive=true;w.health=100;w.usable_weapons=1u<<5;w.current_weapon=6;w.pose.yaw_deg=50;
 botcore::SenseInput enemy{};enemy.index=1;enemy.alive=true;enemy.z=-80;enemy.health=100;bool los=true;
 botcore::BotCommand c;
 for(int t=0;t<60;++t){w.tick=t;human.BeginTick(w);c=human.Step(w,&enemy,&los,1,.05);}
 if(c.target!=1||c.forward!=0)return 1;
 human.NotifyNavigation(true);w.tick=60;human.BeginTick(w);c=human.Step(w,&enemy,&los,1,.05);if(c.forward<=0)return 2;
 struct State{botcore::ObstacleRecovery bs_navigation;void* bs_navPlayer;};State bs;bs.bs_navPlayer=&bs;
 [[maybe_unused]] const bool bot_bHumanAI=true;[[maybe_unused]] const int iLP=0;
 #include "driver_reset.inc"
 w.tick=61;human.BeginTick(w);c=human.Step(w,&enemy,&los,1,.05);
 if(bs.bs_navPlayer!=nullptr||c.forward!=0){std::puts("RECOVERY RESET FAIL: disabled adapter retained override");return 3;}
 std::puts("NATIVE RECOVERY RESET BRANCH PASS");return 0;
}
