// SPDX-License-Identifier: GPL-2.0-only
// Copyright (c) 2018-2023 Dreamy Cecil; adapted for ssam.ai 2026-11-07.
// Original tables/settings and rules: CecilBotMod 953b477e53fdc5a5d84c8ae8d759c84fdf6c973c,
// Sources/Bots/Logic/{BotWeapons,BotSettings,BotItems}.cpp and BotStructure.cpp.
// Damage is an AI rating, not DPS. No engine objects, network packets or entity writes.
#ifndef BOTCORE_CECIL_RULES_H
#define BOTCORE_CECIL_RULES_H
#include <cmath>
#include <cstdint>
#include <sstream>
#include <string>
namespace botcore {
struct CecilWeapon {
  int id;
  double min_distance,max_distance,damage_rating,accuracy,strafe,special,shot_frequency;
};
inline const CecilWeapon* CecilWeapons(bool coop=false) {
  static const CecilWeapon dm[15]={
    {13,32.0,300.0,150.0,1.0,0.3,0.0,-1.0},
    {5,0.0,32.0,100.0,0.6,0.5,0.0,-1.0},
    {7,0.0,300.0,30.0,0.85,0.25,0.0,-1.0},
    {4,0.0,24.0,70.0,0.7,0.25,0.0,-1.0},
    {6,0.0,500.0,20.0,0.9,0.1,0.0,-1.0},
    {12,0.0,128.0,40.0,0.6,0.2,0.0,-1.0},
    {14,16.0,128.0,300.0,0.4,0.2,0.0,-1.0},
    {9,12.0,128.0,100.0,0.3,0.2,0.0,1.0},
    {8,12.0,96.0,70.0,0.2,0.2,0.0,-1.0},
    {11,0.0,24.0,30.0,0.8,0.5,0.0,-1.0},
    {10,0.0,10.0,50.0,1.0,0.0,0.0,-1.0},
    {1,0.0,8.0,50.0,1.0,0.0,0.0,-1.0},
    {3,0.0,500.0,10.0,0.9,0.0,0.0,-1.0},
    {2,0.0,500.0,20.0,0.9,0.0,0.0,-1.0},
    {0,0.0,0.0,0.0,0.0,0.0,0.0,-1.0},
  };
  static const CecilWeapon cooperative[15]={
    {14,24.0,128.0,200.0,0.4,0.2,0.0,-1.0},
    {7,0.0,500.0,200.0,0.85,0.25,0.0,-1.0},
    {13,32.0,500.0,100.0,1.0,0.3,0.0,-1.0},
    {12,0.0,256.0,100.0,0.6,0.2,0.0,-1.0},
    {9,12.0,128.0,150.0,0.4,0.2,0.0,1.0},
    {8,12.0,96.0,100.0,0.2,0.2,0.0,-1.0},
    {11,0.0,24.0,60.0,0.8,0.5,0.0,-1.0},
    {6,0.0,500.0,100.0,0.9,0.1,0.0,-1.0},
    {5,0.0,32.0,70.0,0.6,0.5,0.0,-1.0},
    {4,0.0,24.0,40.0,0.7,0.25,0.0,-1.0},
    {10,0.0,10.0,100.0,1.0,0.0,0.0,-1.0},
    {1,0.0,8.0,50.0,1.0,0.0,0.0,-1.0},
    {3,0.0,500.0,10.0,0.9,0.0,0.0,-1.0},
    {2,0.0,500.0,10.0,0.9,0.0,0.0,-1.0},
    {0,0.0,0.0,0.0,0.0,0.0,0.0,-1.0},
  };
  return coop?cooperative:dm;
}
inline uint32_t CecilWeaponMask(int id) { return id>=1&&id<=14 ? (1u<<(id-1)) : 0u; }
inline const CecilWeapon* CecilWeaponAt(int id,bool coop=false) {
  if(!CecilWeaponMask(id))return nullptr;
  const CecilWeapon* rows=CecilWeapons(coop);
  for(int i=0;i<15;++i)if(rows[i].id==id)return rows+i;
  return nullptr;
}
inline double CecilWeaponScore(int id,double distance,bool coop=false) {
  const CecilWeapon* w=CecilWeaponAt(id,coop);
  if(!w||!std::isfinite(distance)||distance<w->min_distance||distance>w->max_distance)return 0;
  const double t=(distance-w->min_distance)/(w->max_distance-w->min_distance);
  return w->damage_rating*(w->accuracy+(1-w->accuracy)*(1-t));
}
inline int CecilBestWeapon(uint32_t usable,double distance,bool coop=false,int allowed=-1) {
  int best=0;double score=0;
  const CecilWeapon* rows=CecilWeapons(coop);
  for(int i=0;i<15;++i){
    const uint32_t mask=CecilWeaponMask(rows[i].id);
    if(!(usable&mask)||(allowed!=-1&&!(static_cast<uint32_t>(allowed)&mask)))continue;
    const double candidate=CecilWeaponScore(rows[i].id,distance,coop);
    if(candidate>score){best=rows[i].id;score=candidate;}
  }
  return best;
}
inline bool CecilFireRangeSafe(int id,double distance,bool coop=false) {
  // Keep ssam's proven melee reach; Cecil's 8/10-unit rating is not hit geometry.
  return CecilWeaponScore(id,distance,coop)>0&&((id!=1&&id!=10)||distance<=2);
}
struct CecilSettings {
  int schema_version=0;
  int b3rdPerson=0;
  int iCrosshair=0;
  double fRespawnDelay=0;
  int bSniperZoom=0;
  int bShooting=0;
  double fShootAngle=0;
  double fAccuracyAngle=0;
  double fRotSpeedDist=0;
  double fRotSpeedMin=0;
  double fRotSpeedMax=0;
  double fRotSpeedLimit=0;
  double fWeaponCD=0;
  double fTargetCD=0;
  int iFollowPlayers=0;
  double fSpeedMul=0;
  int bStrafe=0;
  int bJump=0;
  int bAvoidPits=0;
  double fPrediction=0;
  double fPredictRnd=0;
  int iAllowedWeapons=0;
  int iTargetType=0;
  int bTargetSearch=0;
  double fImportantChance=0;
  int bItemSearch=0;
  double fItemSearchCD=0;
  int bItemVisibility=0;
  double fWeaponDist=0;
  double fHealthSearch=0;
  double fHealthDist=0;
  double fArmorDist=0;
  double fAmmoDist=0;
};
inline CecilSettings CecilPreset(int preset) {
  CecilSettings s;
  if(preset<0||preset>3)return s;
  s.schema_version=1;s.b3rdPerson=1;s.iCrosshair=-1;s.bAvoidPits=0;
  switch(preset){
    case 0: // Dummy
      s.fRespawnDelay=0.0;
      s.bSniperZoom=0;
      s.bShooting=0;
      s.fShootAngle=15.0;
      s.fAccuracyAngle=5.0;
      s.fRotSpeedDist=400.0;
      s.fRotSpeedMin=0.05;
      s.fRotSpeedMax=0.2;
      s.fRotSpeedLimit=30.0;
      s.fWeaponCD=3.0;
      s.fTargetCD=1.0;
      s.iFollowPlayers=0;
      s.fSpeedMul=1.0;
      s.bStrafe=1;
      s.bJump=1;
      s.fPrediction=0.1;
      s.fPredictRnd=0.1;
      s.iAllowedWeapons=-1;
      s.iTargetType=-1;
      s.bTargetSearch=1;
      s.fImportantChance=0.2;
      s.bItemSearch=1;
      s.fItemSearchCD=5.0;
      s.bItemVisibility=1;
      s.fWeaponDist=16.0;
      s.fHealthSearch=100.0;
      s.fHealthDist=0.0;
      s.fArmorDist=0.0;
      s.fAmmoDist=0.0;
      break;
    case 1: // Easy
      s.fRespawnDelay=3.0;
      s.bSniperZoom=1;
      s.bShooting=1;
      s.fShootAngle=15.0;
      s.fAccuracyAngle=10.0;
      s.fRotSpeedDist=400.0;
      s.fRotSpeedMin=0.1;
      s.fRotSpeedMax=0.5;
      s.fRotSpeedLimit=20.0;
      s.fWeaponCD=5.0;
      s.fTargetCD=3.0;
      s.iFollowPlayers=1;
      s.fSpeedMul=1.0;
      s.bStrafe=0;
      s.bJump=1;
      s.fPrediction=0.2;
      s.fPredictRnd=0.5;
      s.iAllowedWeapons=-1;
      s.iTargetType=-1;
      s.bTargetSearch=1;
      s.fImportantChance=0.1;
      s.bItemSearch=1;
      s.fItemSearchCD=5.0;
      s.bItemVisibility=1;
      s.fWeaponDist=16.0;
      s.fHealthSearch=50.0;
      s.fHealthDist=32.0;
      s.fArmorDist=16.0;
      s.fAmmoDist=16.0;
      break;
    case 2: // Normal
      s.fRespawnDelay=1.0;
      s.bSniperZoom=1;
      s.bShooting=1;
      s.fShootAngle=15.0;
      s.fAccuracyAngle=5.0;
      s.fRotSpeedDist=400.0;
      s.fRotSpeedMin=0.05;
      s.fRotSpeedMax=0.2;
      s.fRotSpeedLimit=30.0;
      s.fWeaponCD=3.0;
      s.fTargetCD=1.0;
      s.iFollowPlayers=1;
      s.fSpeedMul=1.0;
      s.bStrafe=1;
      s.bJump=1;
      s.fPrediction=0.1;
      s.fPredictRnd=0.1;
      s.iAllowedWeapons=-1;
      s.iTargetType=-1;
      s.bTargetSearch=1;
      s.fImportantChance=0.2;
      s.bItemSearch=1;
      s.fItemSearchCD=5.0;
      s.bItemVisibility=1;
      s.fWeaponDist=16.0;
      s.fHealthSearch=80.0;
      s.fHealthDist=32.0;
      s.fArmorDist=16.0;
      s.fAmmoDist=16.0;
      break;
    case 3: // Hard
      s.fRespawnDelay=0.0;
      s.bSniperZoom=1;
      s.bShooting=1;
      s.fShootAngle=15.0;
      s.fAccuracyAngle=2.0;
      s.fRotSpeedDist=50.0;
      s.fRotSpeedMin=0.05;
      s.fRotSpeedMax=0.1;
      s.fRotSpeedLimit=30.0;
      s.fWeaponCD=3.0;
      s.fTargetCD=1.0;
      s.iFollowPlayers=2;
      s.fSpeedMul=1.0;
      s.bStrafe=1;
      s.bJump=1;
      s.fPrediction=0.5;
      s.fPredictRnd=0.0;
      s.iAllowedWeapons=-1;
      s.iTargetType=-1;
      s.bTargetSearch=1;
      s.fImportantChance=0.4;
      s.bItemSearch=1;
      s.fItemSearchCD=5.0;
      s.bItemVisibility=1;
      s.fWeaponDist=16.0;
      s.fHealthSearch=100.0;
      s.fHealthDist=32.0;
      s.fArmorDist=16.0;
      s.fAmmoDist=16.0;
      break;
  }
  return s;
}
// Text configuration is versioned; parse on the loader thread, never in a timer.
inline bool CecilParseSettings(const char* text,CecilSettings& out) {
  if(!text)return false;
  std::istringstream input(text);std::string magic,key,extra;int version,preset;
  if(!(input>>magic>>version>>key>>preset)||magic!="cecil-settings"||version!=1||
     key!="preset"||preset<0||preset>3||(input>>extra))return false;
  out=CecilPreset(preset);return true;
}
// AmmoItemType values from the pinned SDK Engine107/EntitiesV/AmmoItem.h.
// Pack entities supply their real nonzero reserve fields; no invented pack contents.
inline uint32_t CecilAmmoWeaponMask(int kind) {
  switch(kind){
    case 1:return CecilWeaponMask(4)|CecilWeaponMask(5);
    case 2:return CecilWeaponMask(6)|CecilWeaponMask(7);
    case 3:return CecilWeaponMask(8);
    case 4:return CecilWeaponMask(9);
    case 5:return CecilWeaponMask(12);
    case 7:return CecilWeaponMask(14);
    case 10:return CecilWeaponMask(11);
    case 11:return CecilWeaponMask(13);
    default:return 0;
  }
}
enum class CecilItemKind { Weapon,Health,Powerup,Armor,AmmoPack,Ammo };
struct CecilItem {
  uint32_t id=0,generation=0;
  CecilItemKind kind=CecilItemKind::Weapon;
  double x=0,y=0,z=0,value=0;
  int weapon=0;
  uint32_t ammo_mask=0;
  bool pickable=false,visible=false,reachable=false;
};
struct CecilItemInput {
  uint32_t generation=0,owned=0,usable=0,ammo_need_mask=0;
  double x=0,y=0,z=0,health=100,armor=0,enemy_distance=1000;
  CecilSettings settings=CecilPreset(2);
};
inline int CecilChooseItem(const CecilItem* items,int count,const CecilItemInput& in) {
  const CecilSettings& s=in.settings;
  if(!items||count<0||count>1024||s.schema_version!=1||!s.bItemSearch||
     !std::isfinite(in.x)||!std::isfinite(in.y)||!std::isfinite(in.z)||
     !std::isfinite(in.health)||in.health<0||!std::isfinite(in.armor)||in.armor<0||
     !std::isfinite(in.enemy_distance)||in.enemy_distance<0)return -1;
  int best=-1,best_kind=6;double best_distance=0;
  for(int i=0;i<count;++i){
    const CecilItem& it=items[i];const int kind=static_cast<int>(it.kind);
    if(kind<0||kind>5||!it.pickable||!it.reachable||it.generation!=in.generation||
       (s.bItemVisibility&&!it.visible)||!std::isfinite(it.x)||!std::isfinite(it.y)||
       !std::isfinite(it.z)||!std::isfinite(it.value)||it.value<0)continue;
    const double dx=it.x-in.x,dy=3*(it.y-in.y),dz=it.z-in.z;
    const double distance=std::sqrt(dx*dx+dy*dy+dz*dz);
    double limit=0;bool needed=false;
    switch(it.kind){
      case CecilItemKind::Weapon:{
        limit=s.fWeaponDist;const uint32_t mask=CecilWeaponMask(it.weapon);
        // An empty owned gun can use its pickup; a usable owned gun is not an upgrade.
        needed=mask&&(it.weapon>=2)&&!(in.usable&mask)&&distance<in.enemy_distance&&
          (s.iAllowedWeapons==-1||(static_cast<uint32_t>(s.iAllowedWeapons)&mask));break;
      }
      case CecilItemKind::Health:
        limit=s.fHealthDist;
        // Corrected disjoint bands; filter every candidate before nearest selection.
        needed=in.health<s.fHealthSearch&&((it.value>0&&it.value<=10&&in.health<75)||
          (it.value>10&&it.value<=50&&in.health<85)||(it.value>=100&&in.health<150));break;
      case CecilItemKind::Powerup:limit=s.fWeaponDist;needed=true;break;
      case CecilItemKind::Armor:
        limit=s.fArmorDist;needed=in.armor<100&&((it.value>0&&it.value<=10&&in.armor<75)||
          (it.value>10&&it.value<=50&&in.armor<85)||it.value>=100);break;
      case CecilItemKind::AmmoPack:case CecilItemKind::Ammo:
        limit=s.fAmmoDist;needed=(it.ammo_mask&in.ammo_need_mask&in.owned)!=0;break;
    }
    // A rejected/far pack cannot hide eligible ammo. Native LOS is item-specific.
    if(!needed||!std::isfinite(limit)||limit<=0||!std::isfinite(distance)||distance>=limit)continue;
    if(kind<best_kind||(kind==best_kind&&(best<0||distance<best_distance))){
      best=i;best_kind=kind;best_distance=distance;
    }
  }
  return best;
}
// Original travel knife delay; a navigation override is not itself a travel phase.
inline bool CecilTravelKnife(double now,double last_seen,bool navigating,bool visible) {
  return navigating&&!visible&&std::isfinite(now)&&std::isfinite(last_seen)&&now-last_seen>2.0;
}
class CecilFireState {
 public:
  void Reset(){weapon_=0;hold_until_=-1;release_time_=-1;last_time_=-1;next_scope_=0;scope_time_=-1;}
  bool Poll(double now,int current,int wanted,int desired,bool aim,bool visible,bool alive,
            double distance,const CecilSettings& s,bool coop=false) {
    if(!std::isfinite(now)||now<0){Reset();return false;}
    if(now<last_time_)Reset();
    last_time_=now;
    const uint32_t mask=CecilWeaponMask(current);
    const bool allowed=s.iAllowedWeapons==-1||(static_cast<uint32_t>(s.iAllowedWeapons)&mask);
    if(!alive||s.schema_version!=1||!s.bShooting||!aim||!visible||!mask||!allowed||
       current!=wanted||current!=desired||!CecilFireRangeSafe(current,distance,coop)){
      weapon_=0;hold_until_=-1;release_time_=-1;return false;
    }
    if(current!=weapon_){weapon_=current;hold_until_=-1;release_time_=-1;}
    const double period=CecilWeaponAt(current,coop)->shot_frequency;
    if(period<=0)return true;
    // Deliberate correction: at least one released action even if timer skips a tick.
    if(release_time_>=0){
      if(now<=release_time_)return false;
      release_time_=-1;hold_until_=now+period;return true;
    }
    if(hold_until_<0)hold_until_=now+period;
    if(now>=hold_until_){release_time_=now;return false;}
    return true;
  }
  uint32_t ScopeButtons(double now,int current,bool sniping,bool visible,const CecilSettings& s) {
    if(!std::isfinite(now)||now<0||s.schema_version!=1||!s.bSniperZoom||current!=13)return 0;
    if(now<scope_time_)next_scope_=0;
    scope_time_=now;
    if(now<next_scope_||sniping==visible)return 0;
    next_scope_=now+.2;
    return (1u<<12)|(visible?(1u<<10):0u);
  }
 private:
  int weapon_=0;
  double hold_until_=-1,release_time_=-1,last_time_=-1,next_scope_=0,scope_time_=-1;
};
} // namespace botcore
#endif
