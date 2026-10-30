#include "bot_human.h"
#include <cstdio>
using FLOAT=float;using INDEX=int;using BOOL=int;using ULONG=unsigned long;
#define TRUE 1
#define FALSE 0
static botcore::HumanBotPolicy policy;
static botcore::HumanBotPolicy& BotHumanPolicy(INDEX){return policy;}
struct Action {ULONG pa_ulButtons=0;};
struct Source {int calls=0;Action last;void SetAction(const Action& a){last=a;++calls;}};
struct Player {FLOAT health=100;FLOAT GetHealth(){return health;}};
struct State {int bs_iTick=0;};
struct Weapons {int m_iCurrentWeapon=13,m_iWantedWeapon=13;};
static constexpr ULONG BOT_PLACT_FIRE=1;
static int checks=0,failures=0;
#define CHECK(c) do{++checks;if(!(c)){++failures;std::printf("FAIL %d %s\n",__LINE__,#c);}}while(0)
static bool emit(int tick,bool proposal,int current,int wanted,bool recovery,bool respawn){
  INDEX iLP=0,combatWeapon=13;BOOL automatic=TRUE,bot_bHumanAI=TRUE;
  INDEX ctPeriodTicks=20,ctFireTicks=3;BOOL humanFire=proposal,testAimReady=proposal;
  Player actor;actor.health=respawn?0:100;Player* player=&actor;
  State bs;bs.bs_iTick=tick;Weapons weapon{current,wanted};Weapons* weapons=&weapon;
#include "weapon_gate.inc"
  if(recovery)testAimReady=FALSE; // the separately extracted real recovery block sets this
#include "fire_decision.inc"
  Action pa;
#include "fire_button.inc"
  Source source;Source* ppls=&source;
#include "emission.inc"
  CHECK(source.calls==1);return (source.last.pa_ulButtons&BOT_PLACT_FIRE)!=0;
}
static botcore::WorldView w;
static botcore::BotCommand step(){
  botcore::SenseInput s{};s.index=1;s.z=-40;s.alive=true;s.health=100;bool los=true;
  policy.BeginTick(w);return policy.Step(w,&s,&los,1,.05);
}
static void reset(){
  botcore::BotProfile p{};botcore::BuildProfile(5,2,333u,"emit-fixture",&p);
  p.skill.aim_sigma_deg=0;p.skill.settle_s=.05;p.skill.reaction_s=.05;
#ifdef M2_AI2_AVAILABLE
  policy.Configure(&p,false,true,true,false,false,true);
#else
  policy.Configure(&p,false,true,true,false,false);
#endif
  w=botcore::WorldView{};w.alive=true;w.health=100;w.usable_weapons=1u<<12;w.current_weapon=13;
  for(;w.tick<20;++w.tick)step();
}
int main(){
  reset();auto c=step();CHECK(c.fire);
  CHECK(!emit(w.tick,c.fire,2,13,false,false));++w.tick;c=step();CHECK(c.fire);
  CHECK(!emit(w.tick,c.fire,13,2,false,false));++w.tick;c=step();CHECK(c.fire);
  CHECK(!emit(w.tick,c.fire,13,13,true,false));++w.tick;c=step();CHECK(c.fire);
#ifdef M2_AI2_AVAILABLE
  policy.NotifyFireEmitted(w.tick-1,13);policy.NotifyFireEmitted(w.tick,8);
#endif
  ++w.tick;c=step();CHECK(c.fire);
  CHECK(emit(w.tick,c.fire,13,13,false,false));const int committed=w.tick;
  w.tick=committed+1;CHECK(!step().fire); // assert the actual adapter committed first
#ifdef M2_AI2_AVAILABLE
  policy.NotifyFireEmitted(committed,13);policy.NotifyFireEmitted(committed+7,13);
#endif
  for(w.tick=committed+2;w.tick<committed+26;++w.tick)CHECK(!step().fire);
  CHECK(step().fire); // invalid/duplicate acknowledgements must not extend cooldown
  reset();c=step();CHECK(c.fire);
  CHECK(emit(w.tick,c.fire,13,13,false,true));++w.tick;CHECK(step().fire);
  std::printf("M2 FINAL ACTION: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
