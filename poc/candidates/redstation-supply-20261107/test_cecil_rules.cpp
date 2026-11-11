#include <cassert>
#include <cmath>
#include <cstdio>
#include <limits>
#if !__has_include("cecil_rules.h")
int main() { std::fputs("FAIL: Cecil rules not implemented\n", stderr); return 1; }
#else
#include "cecil_rules.h"
using namespace botcore;
static uint32_t bit(int w) { return 1u << (w-1); }
static void weapons() {
  assert(CecilWeaponAt(0)==nullptr && CecilWeaponAt(-1)==nullptr && CecilWeaponAt(15)==nullptr);
  assert(CecilWeaponScore(0,10)==0 && CecilWeaponScore(32,10)==0);
  assert(CecilWeaponScore(8,std::numeric_limits<double>::quiet_NaN())==0);
  assert(CecilWeaponScore(8,-1)==0 && CecilWeaponScore(8,11.999)==0);
  assert(CecilWeaponScore(8,12)==70 && CecilWeaponScore(8,96)>13.999);
  assert(CecilWeaponScore(8,96.001)==0);
  assert(CecilBestWeapon(0,20)==0);
  assert(CecilBestWeapon(bit(8)|bit(2),20)==8);
  assert(CecilBestWeapon(bit(8)|bit(2),3)==2);
  assert(CecilBestWeapon(bit(9)|bit(2),20)==9);
  assert(CecilBestWeapon(bit(14)|bit(2),20)==14);
  assert(CecilBestWeapon(bit(11)|bit(2),5)==11);
  assert(CecilBestWeapon(bit(3),30)==3);
  assert(CecilBestWeapon(bit(8),20,false,0)==0);
  assert(CecilBestWeapon(bit(8)|bit(9),20,false,bit(8))==8);
  assert(CecilBestWeapon(0xffffffffu,20)==14);
  assert(CecilBestWeapon(bit(6)|bit(2),20)==6); // exact score tie, original row order
  assert(!CecilFireRangeSafe(14,15) && CecilFireRangeSafe(14,16));
  assert(!CecilFireRangeSafe(1,3) && CecilFireRangeSafe(1,2));
  for(int coop=0;coop<2;++coop) for(int w=1;w<=14;++w) {
    const CecilWeapon* row=CecilWeaponAt(w,coop);
    assert(row && row->id==w && row->max_distance>row->min_distance);
    assert(CecilBestWeapon(bit(w),row->min_distance,coop)==w);
  }
}
static void presets() {
  assert(CecilPreset(-1).schema_version==0 && CecilPreset(4).schema_version==0);
  for(int p=0;p<4;++p) {
    CecilSettings s;
    char text[64];std::snprintf(text,sizeof(text),"cecil-settings 1\npreset %d\n",p);
    assert(CecilParseSettings(text,s) && s.schema_version==1);
    assert(s.b3rdPerson && s.iCrosshair==-1 && !s.bAvoidPits);
    assert(s.fItemSearchCD==5 && s.fShootAngle==15);
  }
  CecilSettings s=CecilPreset(2); const double old=s.fHealthSearch;
  assert(!CecilParseSettings("cecil-settings 2\npreset 2",s) && s.fHealthSearch==old);
  assert(!CecilParseSettings("cecil-settings 1\npreset 4",s));
  assert(!CecilParseSettings("cecil-settings 1\npreset 2\njunk",s));
  assert(!CecilParseSettings("cecil-settings 1\npreset 2\npreset 1",s));
  assert(!CecilParseSettings(nullptr,s));
  assert(!CecilPreset(0).bShooting && !CecilPreset(1).bStrafe);
  assert(CecilPreset(1).fWeaponCD==5 && CecilPreset(3).fPrediction==.5);
}
static CecilItem item(CecilItemKind kind,int id,double x,double value=0) {
  CecilItem it;it.kind=kind;it.id=id;it.generation=7;it.x=x;it.value=value;
  it.pickable=it.visible=it.reachable=true;return it;
}
static void items() {
  CecilItemInput in;in.generation=7;in.settings=CecilPreset(3);in.health=80;
  in.owned=bit(1)|bit(2);in.usable=in.owned;
  CecilItem a[]={item(CecilItemKind::Health,1,1,5),item(CecilItemKind::Health,2,2,20)};
  assert(CecilChooseItem(a,2,in)==1); // unsuitable nearest health cannot mask second
  in.health=74;assert(CecilChooseItem(a,2,in)==0);
  in.health=85;assert(CecilChooseItem(a,2,in)==-1);
  a[1].value=100;in.health=90;assert(CecilChooseItem(a,2,in)==1);
  a[1].generation=8;assert(CecilChooseItem(a,2,in)==-1);
  a[1].generation=7;a[1].reachable=false;assert(CecilChooseItem(a,2,in)==-1);
  a[1].reachable=true;a[1].visible=false;assert(CecilChooseItem(a,2,in)==-1);
  in.settings.bItemVisibility=false;assert(CecilChooseItem(a,2,in)==1);
  a[1].pickable=false;assert(CecilChooseItem(a,2,in)==-1);
  in=CecilItemInput();in.generation=7;in.settings=CecilPreset(2);
  in.ammo_need_mask=bit(8);in.owned=bit(8);
  CecilItem ammo[]={item(CecilItemKind::AmmoPack,3,30),item(CecilItemKind::Ammo,4,2)};
  ammo[0].ammo_mask=ammo[1].ammo_mask=bit(8);
  assert(CecilChooseItem(ammo,2,in)==1); // remote pack cannot suppress nearby ammo
  ammo[0].x=3;assert(CecilChooseItem(ammo,2,in)==0);
  ammo[0].ammo_mask=bit(6);assert(CecilChooseItem(ammo,2,in)==1);
  in.ammo_need_mask=0;assert(CecilChooseItem(ammo,2,in)==-1);
  in.owned=bit(1)|bit(2);in.usable=in.owned;in.enemy_distance=100;
  CecilItem guns[]={item(CecilItemKind::Weapon,5,4),item(CecilItemKind::Health,6,1,100)};
  guns[0].weapon=8;in.health=20;assert(CecilChooseItem(guns,2,in)==0);
  in.owned|=bit(8);in.usable|=bit(8);assert(CecilChooseItem(guns,2,in)==1);
  in.usable&=~bit(8);assert(CecilChooseItem(guns,2,in)==0); // owned but empty pickup refills
  in.enemy_distance=3;assert(CecilChooseItem(guns,2,in)==1);
  guns[0].weapon=3;in.enemy_distance=100;assert(CecilChooseItem(guns,2,in)==0);
  guns[0].weapon=0;assert(CecilChooseItem(guns,2,in)==1);
  guns[1].y=20;assert(CecilChooseItem(guns,2,in)==-1); // weighted vertical distance
  CecilItem armor[]={item(CecilItemKind::Armor,8,1,5),item(CecilItemKind::Armor,9,2,20)};
  in.armor=80;assert(CecilChooseItem(armor,2,in)==1);
  in.armor=100;assert(CecilChooseItem(armor,2,in)==-1);
  assert(CecilChooseItem(nullptr,1,in)==-1 && CecilChooseItem(armor,-1,in)==-1);
  in.health=std::numeric_limits<double>::quiet_NaN();assert(CecilChooseItem(armor,2,in)==-1);
  assert(CecilAmmoWeaponMask(1)==(bit(4)|bit(5)));
  assert(CecilAmmoWeaponMask(2)==(bit(6)|bit(7)));
  assert(CecilAmmoWeaponMask(3)==bit(8) && CecilAmmoWeaponMask(4)==bit(9));
  assert(CecilAmmoWeaponMask(5)==bit(12) && CecilAmmoWeaponMask(7)==bit(14));
  assert(CecilAmmoWeaponMask(10)==bit(11) && CecilAmmoWeaponMask(11)==bit(13));
  assert(CecilAmmoWeaponMask(0)==0 && CecilAmmoWeaponMask(6)==0 && CecilAmmoWeaponMask(9)==0);
}
static void fire() {
  const CecilSettings s=CecilPreset(2);
  CecilFireState f;
  assert(!f.Poll(0,8,9,9,true,true,true,20,s));
  assert(!f.Poll(0,9,8,9,true,true,true,20,s));
  assert(!f.Poll(0,0,0,0,true,true,true,20,s));
  assert(f.Poll(0,9,9,9,true,true,true,20,s));
  assert(f.Poll(.99,9,9,9,true,true,true,20,s));
  assert(!f.Poll(1,9,9,9,true,true,true,20,s));
  assert(!f.Poll(1,9,9,9,true,true,true,20,s)); // duplicate timestamp stays released
  assert(f.Poll(1.025,9,9,9,true,true,true,20,s));
  assert(!f.Poll(1.1,9,9,9,true,false,true,20,s));
  assert(f.Poll(1.2,9,9,9,true,true,true,20,s)); // sight regain starts new hold
  assert(!f.Poll(1.3,9,9,9,true,true,false,20,s));
  assert(f.Poll(1.4,9,9,9,true,true,true,20,s));
  assert(!f.Poll(1.5,9,9,9,true,true,true,3,s));
  assert(!f.Poll(1.6,9,9,9,true,true,true,20,CecilPreset(0)));
  assert(!f.Poll(std::numeric_limits<double>::quiet_NaN(),9,9,9,true,true,true,20,s));
  assert(f.Poll(2,8,8,8,true,true,true,20,s));
  assert(f.Poll(3,8,8,8,true,true,true,20,s));
  f.Reset();
  assert(f.ScopeButtons(0,13,false,true,s)==((1u<<12)|(1u<<10)));
  assert(f.ScopeButtons(.1,13,false,true,s)==0);
  assert(f.ScopeButtons(.2,13,true,false,s)==(1u<<12));
  assert(f.ScopeButtons(.4,8,false,true,s)==0);
  assert(f.ScopeButtons(.5,13,false,true,CecilPreset(0))==0);
}
int main(){weapons();presets();items();fire();std::puts("Cecil rules: weapons/presets/items/fire PASS");}
#endif
