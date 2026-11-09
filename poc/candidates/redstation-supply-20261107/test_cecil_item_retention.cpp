// SPDX-License-Identifier: GPL-2.0-only
#include "cecil_rules.h"
#include <cassert>
#include <cstdio>
#include <limits>
using namespace botcore;

static CecilItemInput input() {
  CecilItemInput in;in.generation=7;
  in.owned=in.usable=CecilWeaponMask(1)|CecilWeaponMask(2)|CecilWeaponMask(9);
  return in;
}
static CecilItem item(CecilItemKind kind=CecilItemKind::Weapon) {
  CecilItem it;it.id=248;it.generation=7;it.kind=kind;it.weapon=11;
  it.pickable=it.visible=it.reachable=true;it.x=1;return it;
}
static void retained_upgrade_and_acquisition() {
  CecilItemInput in=input();CecilItem it=item();
  it.x=0;it.y=5;assert(CecilChooseItem(&it,1,in)==0);
  it.y=6; // A live flamer moves from weighted 15 m to 18 m after grenade acquisition.
  assert(CecilRetainItem(it,in));
  assert(CecilChooseItem(&it,1,in)==-1);
  it.y=0;it.x=2;in.enemy_distance=1;
  assert(CecilRetainItem(it,in));
  assert(CecilChooseItem(&it,1,in)==-1);
  in.enemy_distance=100;it.visible=false;it.reachable=false;
  assert(CecilRetainItem(it,in)); // Native typed reads and path validation are separate.
  assert(CecilChooseItem(&it,1,in)==-1);
  it.reachable=true;assert(CecilChooseItem(&it,1,in)==-1);
  in.settings.bItemVisibility=0;assert(CecilChooseItem(&it,1,in)==0);
  it.visible=true;in.settings.bItemVisibility=1;in.enemy_distance=2;
  assert(CecilChooseItem(&it,1,in)==-1); // Strict enemy-distance boundary is unchanged.
  in.enemy_distance=100;it.x=16;assert(CecilChooseItem(&it,1,in)==-1);
  it.x=15.999;assert(CecilChooseItem(&it,1,in)==0);
  in.usable|=CecilWeaponMask(11);assert(!CecilRetainItem(it,in));
  in.owned|=CecilWeaponMask(11);in.usable&=~CecilWeaponMask(11);
  assert(CecilRetainItem(it,in)); // Owned empty weapon still needs its pickup.
  in.settings.iAllowedWeapons=CecilWeaponMask(9);assert(!CecilRetainItem(it,in));
  in.settings.iAllowedWeapons=CecilWeaponMask(11);assert(CecilRetainItem(it,in));
  in.settings.iAllowedWeapons=-1;
  for(int weapon:{-1,0,1,15}){it.weapon=weapon;assert(!CecilRetainItem(it,in));}
  it.weapon=2;in.usable&=~CecilWeaponMask(2);assert(CecilRetainItem(it,in));
}
static void typed_need() {
  CecilItemInput in=input();CecilItem it=item(CecilItemKind::Health);
  struct Band {double value,needed,full;};
  const Band health[]={{5,74,75},{20,84,85},{100,149,150}};
  in.settings.fHealthSearch=200;
  for(const Band& b:health){
    it.value=b.value;in.health=b.needed;assert(CecilRetainItem(it,in));
    in.health=b.full;assert(!CecilRetainItem(it,in));
  }
  in.health=50;it.value=20;in.settings.fHealthSearch=50;
  assert(!CecilRetainItem(it,in));
  in.settings.fHealthSearch=100;
  for(double value:{0.,51.,99.}){it.value=value;assert(!CecilRetainItem(it,in));}
  it.kind=CecilItemKind::Armor;
  const Band armor[]={{5,74,75},{20,84,85},{100,99,100}};
  for(const Band& b:armor){
    it.value=b.value;in.armor=b.needed;assert(CecilRetainItem(it,in));
    in.armor=b.full;assert(!CecilRetainItem(it,in));
  }
  in.armor=0;
  for(double value:{0.,51.,99.}){it.value=value;assert(!CecilRetainItem(it,in));}
  for(CecilItemKind kind:{CecilItemKind::Ammo,CecilItemKind::AmmoPack}){
    it=item(kind);it.ammo_mask=CecilWeaponMask(9);in.ammo_need_mask=it.ammo_mask;
    assert(CecilRetainItem(it,in));
    in.ammo_need_mask=CecilWeaponMask(8);assert(!CecilRetainItem(it,in));
    in.ammo_need_mask=it.ammo_mask;in.owned&=~it.ammo_mask;
    assert(!CecilRetainItem(it,in));in.owned|=it.ammo_mask;
    it.ammo_mask=0;assert(!CecilRetainItem(it,in));
  }
  it=item(CecilItemKind::Powerup);it.x=1000;it.visible=it.reachable=false;
  assert(CecilRetainItem(it,in));assert(CecilChooseItem(&it,1,in)==-1);
  // Every kind keeps the acquisition radius as a separate strict boundary.
  in=input();in.health=20;in.ammo_need_mask=CecilWeaponMask(9);
  for(CecilItemKind kind:{CecilItemKind::Weapon,CecilItemKind::Health,CecilItemKind::Powerup,
                         CecilItemKind::Armor,CecilItemKind::AmmoPack,CecilItemKind::Ammo}){
    it=item(kind);it.value=100;it.ammo_mask=CecilWeaponMask(9);
    assert(CecilChooseItem(&it,1,in)==0);
    switch(kind){
      case CecilItemKind::Weapon:case CecilItemKind::Powerup:it.x=in.settings.fWeaponDist;break;
      case CecilItemKind::Health:it.x=in.settings.fHealthDist;break;
      case CecilItemKind::Armor:it.x=in.settings.fArmorDist;break;
      case CecilItemKind::AmmoPack:case CecilItemKind::Ammo:it.x=in.settings.fAmmoDist;break;
    }
    assert(CecilRetainItem(it,in));assert(CecilChooseItem(&it,1,in)==-1);
  }
}
static void invalid_data() {
  const CecilItem good=item();const CecilItemInput valid=input();
  CecilItem it=good;CecilItemInput in=valid;
  it.pickable=false;assert(!CecilRetainItem(it,in));
  it=good;it.generation=8;assert(!CecilRetainItem(it,in));
  for(int kind:{-1,6}){it=good;it.kind=static_cast<CecilItemKind>(kind);assert(!CecilRetainItem(it,in));}
  for(double bad:{std::numeric_limits<double>::quiet_NaN(),
                  std::numeric_limits<double>::infinity(),
                  -std::numeric_limits<double>::infinity()}){
    for(double CecilItem::* field:{&CecilItem::x,&CecilItem::y,&CecilItem::z,&CecilItem::value}){
      it=good;it.*field=bad;assert(!CecilRetainItem(it,valid));
      assert(CecilChooseItem(&it,1,valid)==-1);
    }
    for(double CecilItemInput::* field:{&CecilItemInput::x,&CecilItemInput::y,&CecilItemInput::z,
        &CecilItemInput::health,&CecilItemInput::armor,&CecilItemInput::enemy_distance}){
      in=valid;in.*field=bad;assert(!CecilRetainItem(good,in));
      assert(CecilChooseItem(&good,1,in)==-1);
    }
  }
  it=good;it.value=-1;assert(!CecilRetainItem(it,valid));
  for(double CecilItemInput::* field:{&CecilItemInput::health,&CecilItemInput::armor,
                                     &CecilItemInput::enemy_distance}){
    in=valid;in.*field=-1;assert(!CecilRetainItem(good,in));
  }
  in=valid;in.settings.schema_version=0;assert(!CecilRetainItem(good,in));
  in=valid;in.settings.bItemSearch=0;assert(!CecilRetainItem(good,in));
}
int main(){
  retained_upgrade_and_acquisition();typed_need();invalid_data();
  std::puts("Cecil item retention: upgrade/typed need/strict validation PASS");
}
