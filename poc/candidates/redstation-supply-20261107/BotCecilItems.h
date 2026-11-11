// SPDX-License-Identifier: GPL-2.0-only
// Read-only Engine107 snapshots, ssam.ai 2026-11-07.
// SDK pin 94ff8cd0e63941f8601294350b616472f772ed51. Caller holds world mutex.
// No rays, entity events, retained pointers, or changes to replicated state.
#ifndef BOT_CECIL_ITEMS_H
#define BOT_CECIL_ITEMS_H
#include "cecil_rules.h"
#include <cstring>
#include <EntitiesV/Player.h>
#include <EntitiesV/PlayerWeapons.h>
#include <EntitiesV/WeaponItem.h>
#include <EntitiesV/HealthItem.h>
#include <EntitiesV/ArmorItem.h>
#include <EntitiesV/AmmoItem.h>
#include <EntitiesV/AmmoPack.h>
#include <EntitiesV/PowerUpItem.h>

inline bool BotCecilIsClass(CEntity* entity,const char* name,const char* className) {
  if(IsDerivedFromClass(entity,className))return true;
  const char* path=entity->GetClass()?(const char*)entity->GetClass()->GetName():nullptr;
  if(!path)return false;
  const char* base=path;
  for(const char* p=path;*p;++p)if(*p=='\\'||*p=='/')base=p+1;
  const size_t len=std::strlen(name);
  return std::strncmp(base,name,len)==0&&std::strcmp(base+len,".ecl")==0;
}
inline uint32_t BotCecilAmmoNeed(CPlayerWeapons* w) {
  if(!w)return 0;
  const int ammo[]={w->m_iShells,w->m_iBullets,w->m_iRockets,w->m_iGrenades,
    w->m_iElectricity,w->m_iIronBalls,w->m_iNapalm,w->m_iSniperBullets};
  const int caps[]={w->m_iMaxShells,w->m_iMaxBullets,w->m_iMaxRockets,w->m_iMaxGrenades,
    w->m_iMaxElectricity,w->m_iMaxIronBalls,w->m_iMaxNapalm,w->m_iMaxSniperBullets};
  const int kinds[]={1,2,3,4,5,7,10,11};
  uint32_t needed=0;
  for(int i=0;i<8;++i)if(caps[i]>0&&ammo[i]<caps[i])needed|=botcore::CecilAmmoWeaponMask(kinds[i]);
  return needed&static_cast<uint32_t>(w->m_iAvailableWeapons);
}
inline uint32_t BotCecilUsableWeapons(CPlayerWeapons* w,bool infiniteAmmo) {
  if(!w)return 0;
  uint32_t usable=static_cast<uint32_t>(w->m_iAvailableWeapons)&0x3fffu;
  if(infiniteAmmo)return usable;
  // Colts reload without a finite reserve; double shotgun consumes two shells.
  const int shots[]={1,1,1,w->m_iShells,w->m_iShells/2,w->m_iBullets,w->m_iBullets,
    w->m_iRockets,w->m_iGrenades,1,w->m_iNapalm,w->m_iElectricity,w->m_iSniperBullets,w->m_iIronBalls};
  for(int i=0;i<14;++i)if(shots[i]<=0)usable&=~(1u<<i);
  return usable;
}
// WeaponItem.es:391-406 marks weapons-stay items before ReceiveItem. This is
// mask evidence only; a false value does not disprove a respawning-item pickup.
inline bool BotCecilWeaponGoalPicked(CPlayer* player,CEntity* entity) {
  if(!player||!entity||(entity->GetFlags()&ENF_DELETED))return false;
  const int index=player->GetMyPlayerIndex();
  if(index<0||index>=16||!BotCecilIsClass(entity,"WeaponItem","Weapon Item"))return false;
  // Hidden after pickup is expected; do not reuse the pickable-item filter.
  return (static_cast<uint32_t>(static_cast<CWeaponItem*>(entity)->m_ulPickedMask)&(1u<<index))!=0;
}
inline bool BotCecilReadItem(CPlayer* player,CEntity* entity,uint32_t generation,
                             uint32_t owned,botcore::CecilItem* out,const char** reason=nullptr) {
  auto reject=[&](const char* why){if(reason)*reason=why;return false;};
  if(reason)*reason="ok";
  if(!out)return reject("null_output");
  *out=botcore::CecilItem();
  if(!player)return reject("null_player");
  if(!entity)return reject("missing_entity");
  if(!std::isfinite(player->GetHealth())||player->GetHealth()<=0)return reject("player_not_alive");
  if(entity->GetFlags()&ENF_DELETED)return reject("deleted");
  if(entity->GetFlags()&ENF_HIDDEN)return reject("hidden");
  if(entity->GetRenderType()!=CEntity::RT_MODEL&&entity->GetRenderType()!=CEntity::RT_SKAMODEL)return reject("render_type");
  const int index=player->GetMyPlayerIndex();
  if(index<0||index>=16)return reject("player_index");
  botcore::CecilItem result;result.id=entity->en_ulID;result.generation=generation;
  const FLOAT3D& pos=entity->GetPlacement().pl_PositionVector;
  result.x=pos(1);result.y=pos(2);result.z=pos(3);
  if(!std::isfinite(result.x)||!std::isfinite(result.y)||!std::isfinite(result.z))return reject("position");
  CItem* item=nullptr;
  if(BotCecilIsClass(entity,"WeaponItem","Weapon Item")){
    CWeaponItem* weapon=static_cast<CWeaponItem*>(entity);item=weapon;
    static const int types[]={0,2,4,5,6,7,8,9,13,11,12,10,14};
    const int type=static_cast<int>(weapon->m_EwitType);
    if(type<1||type>12)return reject("weapon_type");
    result.weapon=types[type];
    if(result.weapon==2&&(owned&botcore::CecilWeaponMask(2)))result.weapon=3;
    result.kind=botcore::CecilItemKind::Weapon;
  }else if(BotCecilIsClass(entity,"HealthItem","Health Item")||BotCecilIsClass(entity,"ArmorItem","Armor Item")){
    const bool health=BotCecilIsClass(entity,"HealthItem","Health Item");
    item=static_cast<CItem*>(entity);
    const bool over=health?static_cast<CHealthItem*>(entity)->m_bOverTopHealth!=0:
                           static_cast<CArmorItem*>(entity)->m_bOverTopArmor!=0;
    const double old=health?player->GetHealth():player->m_fArmor;
    // Player.es:842-872,5276: spawn records TopHealth; TopArmor is identical,
    // and both OverTop maxima are Top+100. Match ReceiveItem's ceil comparison.
    const double top=player->m_fMaxHealth,cap=top+(over?100:0);
    if(!std::isfinite(top)||top<=0||!std::isfinite(old)||old<0||
       !std::isfinite(item->m_fValue)||item->m_fValue<=0||
       std::ceil(std::fmin(old+item->m_fValue,cap))<=std::ceil(old))return reject("health_armor_no_gain_or_invalid");
    result.kind=health?botcore::CecilItemKind::Health:botcore::CecilItemKind::Armor;
  }else if(BotCecilIsClass(entity,"AmmoPack","Ammo Pack")){
    CAmmoPack* pack=static_cast<CAmmoPack*>(entity);item=pack;
    result.kind=botcore::CecilItemKind::AmmoPack;
    const int amounts[]={pack->m_iShells,pack->m_iBullets,pack->m_iRockets,pack->m_iGrenades,
      pack->m_iElectricity,pack->m_iIronBalls,pack->m_iNapalm,pack->m_iSniperBullets};
    const int kinds[]={1,2,3,4,5,7,10,11};
    for(int i=0;i<8;++i)if(amounts[i]>0)result.ammo_mask|=botcore::CecilAmmoWeaponMask(kinds[i]);
    if(!result.ammo_mask)return reject("empty_ammo_pack");
  }else if(BotCecilIsClass(entity,"AmmoItem","Ammo Item")){
    CAmmoItem* ammo=static_cast<CAmmoItem*>(entity);item=ammo;
    result.kind=botcore::CecilItemKind::Ammo;
    // Legacy kinds 8/9 are explicitly "don't use" in AmmoItem.es; real packs
    // use CAmmoPack above. Nuke ammo (6) has no supported retail weapon.
    result.ammo_mask=botcore::CecilAmmoWeaponMask(static_cast<int>(ammo->m_EaitType));
    if(!result.ammo_mask||!std::isfinite(item->m_fValue)||item->m_fValue<=0)return reject("ammo_kind_or_value");
  }else if(BotCecilIsClass(entity,"PowerUpItem","PowerUp Item")){
    CPowerUpItem* power=static_cast<CPowerUpItem*>(entity);item=power;
    const int type=static_cast<int>(power->m_puitType);
    // PowerUpItem.es ItemCollected refuses a fourth Serious Bomb.
    if(type<0||type>4||(type==4&&player->m_iSeriousBombCount>=3))return reject("powerup_type_or_capacity");
    result.kind=botcore::CecilItemKind::Powerup;
  }else return reject("item_class");
  if(static_cast<uint32_t>(item->m_ulPickedMask)&(1u<<index))return reject("picked_for_player");
  if(!std::isfinite(item->m_fValue)||item->m_fValue<0)return reject("item_value");
  result.value=item->m_fValue;result.pickable=true;
  // Caller sets visible/reachable only after its budgeted item ray/path checks.
  *out=result;return true;
}
#endif
