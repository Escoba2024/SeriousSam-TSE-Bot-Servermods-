#include "bot_human.h"
#include "bot_navigation.h"
#include <cstring>
#include <cstdio>
using INDEX=int;using FLOAT=float;using BOOL=int;
#define FALSE 0
struct Player{};struct State {void* bs_ppls=nullptr;botcore::ObstacleRecovery bs_navigation;Player* bs_navPlayer=nullptr;Player* bs_apObservedPlayers[16]{};FLOAT bs_lastHealth=0;};
static State _absBots[4];
static INDEX slots[4]={0,1,2,3};static INDEX* _apiProfileSlot[4]={slots,slots+1,slots+2,slots+3};
static INDEX bot_iRosterOffset=0,bot_iProfileSeed=20261020;
static INDEX bot_iSkillTier=-1,bot_iPersonality=-1;
static BOOL bot_bExploratorySearch=FALSE,bot_bCecilP1=FALSE,bot_bCombatWeapon2=FALSE,bot_bCombatLead2=FALSE,bot_bCombatStrafe2=FALSE;
static botcore::HumanBotPolicy& BotHumanPolicy(INDEX slot){static botcore::HumanBotPolicy p[4];return p[slot];}
static botcore::BotProfile& BotHumanProfile(INDEX slot){static botcore::BotProfile p[4];return p[slot];}
static void BotLog(const char*,...){}
#include "attach.inc"
#include "session_reset.inc"
int main(){
  BotHumanAttach(0);const auto original=BotHumanProfile(0);int failed=0,checks=0;
  for(int tier=1;tier<=5;++tier)for(int persona=0;persona<6;++persona){
    bot_iSkillTier=tier;bot_iPersonality=persona;BotHumanAttach(0);auto p=BotHumanProfile(0);++checks;
    if(p.tier!=tier||p.persona!=persona||std::strcmp(p.name,original.name)){++failed;}
  }
  // Invalid overrides retain known safe roster defaults.
  bot_iSkillTier=6;bot_iPersonality=6;BotHumanAttach(0);++checks;
  if(BotHumanProfile(0).tier!=original.tier||BotHumanProfile(0).persona!=original.persona)++failed;
  int same_source=7;
  for(auto& state:_absBots)state.bs_ppls=&same_source;
  BotResetNavigation();
  for(auto& state:_absBots){++checks;if(state.bs_ppls==&same_source)++failed;}
  std::printf("M2 NATIVE PROFILE ATTACH: %d checks, %d failures\n",checks,failed);return failed?1:0;
}
