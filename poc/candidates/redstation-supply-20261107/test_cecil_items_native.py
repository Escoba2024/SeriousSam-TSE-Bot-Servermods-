#!/usr/bin/env python3
"""Exercise the real native adapter with field-only Engine107 SDK stand-ins."""
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
STUB = r"""
#include <cstdint>
#include <cstring>
#include <cmath>
#include <cassert>
#include <limits>
using INDEX=int;using ULONG=uint32_t;
constexpr int ENF_DELETED=1,ENF_HIDDEN=2;
struct FLOAT3D{float v[3]={1,2,3};float operator()(int i)const{return v[i-1];}};
struct Placement{FLOAT3D pl_PositionVector;};
struct EntityClass{const char* name=nullptr;const char* GetName(){return name;}};
struct CEntity{
  enum{RT_MODEL=1,RT_SKAMODEL=2};
  virtual ~CEntity()=default;
  uint32_t en_ulID=42,flags=0;int render=RT_MODEL;EntityClass klass;Placement placement;
  uint32_t GetFlags(){return flags;}int GetRenderType(){return render;}
  EntityClass* GetClass(){return &klass;}const Placement& GetPlacement(){return placement;}
};
inline bool IsDerivedFromClass(CEntity* e,const char* n){return e->klass.name&&std::strcmp(e->klass.name,n)==0;}
struct CPlayer:CEntity{int index=1,m_iSeriousBombCount=0;float health=80,m_fArmor=20,m_fMaxHealth=100;
  int GetMyPlayerIndex(){return index;}float GetHealth(){return health;}};
struct CItem:CEntity{float m_fValue=10;int m_ulPickedMask=0;};
struct CWeaponItem:CItem{int m_EwitType=1;};
struct CHealthItem:CItem{bool m_bOverTopHealth=false;};
struct CArmorItem:CItem{bool m_bOverTopArmor=false;};
struct CAmmoItem:CItem{int m_EaitType=1;};
struct CAmmoPack:CItem{int m_iShells=0,m_iBullets=0,m_iRockets=0,m_iGrenades=0,
  m_iNapalm=0,m_iElectricity=0,m_iIronBalls=0,m_iSniperBullets=0;};
struct CPowerUpItem:CItem{int m_puitType=0;};
struct CPlayerWeapons{
  int m_iAvailableWeapons=16383,m_iBullets=0,m_iShells=0,m_iRockets=0,m_iGrenades=0,
  m_iNapalm=0,m_iElectricity=0,m_iIronBalls=0,m_iSniperBullets=0;
  int m_iMaxBullets=10,m_iMaxShells=10,m_iMaxRockets=10,m_iMaxGrenades=10,
  m_iMaxNapalm=10,m_iMaxElectricity=10,m_iMaxIronBalls=10,m_iMaxSniperBullets=10;};
#include "BotCecilItems.h"
static uint32_t bit(int n){return 1u<<(n-1);}
int main(){
  CPlayer p;CWeaponItem weapon;weapon.klass.name="Classes\\WeaponItem.ecl";
  assert(!BotCecilWeaponGoalPicked(nullptr,&weapon));
  assert(!BotCecilWeaponGoalPicked(&p,nullptr));
  CEntity wrong;wrong.klass.name="Health Item";
  assert(!BotCecilWeaponGoalPicked(&p,&wrong));
  weapon.m_ulPickedMask=0;assert(!BotCecilWeaponGoalPicked(&p,&weapon));
  weapon.m_ulPickedMask=2;assert(BotCecilWeaponGoalPicked(&p,&weapon));
  weapon.flags=ENF_HIDDEN;assert(BotCecilWeaponGoalPicked(&p,&weapon));
  weapon.flags=ENF_DELETED;assert(!BotCecilWeaponGoalPicked(&p,&weapon));weapon.flags=0;
  p.index=-1;assert(!BotCecilWeaponGoalPicked(&p,&weapon));
  p.index=16;assert(!BotCecilWeaponGoalPicked(&p,&weapon));
  p.index=15;weapon.m_ulPickedMask=1<<15;assert(BotCecilWeaponGoalPicked(&p,&weapon));
  p.index=0;assert(!BotCecilWeaponGoalPicked(&p,&weapon));
  weapon.m_ulPickedMask=1;assert(BotCecilWeaponGoalPicked(&p,&weapon));
  p.index=1;weapon.m_ulPickedMask=0;
  botcore::CecilItem out;
  assert(BotCecilReadItem(&p,&weapon,7,bit(2),&out));
  assert(out.weapon==3&&out.id==42&&out.generation==7&&out.x==1&&out.y==2&&out.z==3);
  assert(out.pickable&&!out.visible&&!out.reachable);
  assert(BotCecilReadItem(&p,&weapon,7,0,&out)&&out.weapon==2);
  weapon.m_EwitType=6;assert(BotCecilReadItem(&p,&weapon,7,0,&out)&&out.weapon==8);
  weapon.m_EwitType=13;assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  weapon.m_EwitType=6;weapon.m_ulPickedMask=bit(2);
  assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  weapon.m_ulPickedMask=1;assert(BotCecilReadItem(&p,&weapon,7,0,&out));
  p.index=-1;assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  p.index=16;assert(!BotCecilReadItem(&p,&weapon,7,0,&out));p.index=1;
  weapon.flags=ENF_DELETED;assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  weapon.flags=ENF_HIDDEN;assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  weapon.flags=0;weapon.render=0;assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  weapon.render=1;weapon.placement.pl_PositionVector.v[0]=std::numeric_limits<float>::quiet_NaN();
  assert(!BotCecilReadItem(&p,&weapon,7,0,&out));
  weapon.placement.pl_PositionVector.v[0]=1;weapon.klass.name="Weapon Item";
  assert(BotCecilReadItem(&p,&weapon,7,0,&out));
  CHealthItem health;health.klass.name="Health Item";p.health=100;
  assert(!BotCecilReadItem(&p,&health,7,0,&out));
  health.m_bOverTopHealth=true;assert(BotCecilReadItem(&p,&health,7,0,&out));
  p.health=200;assert(!BotCecilReadItem(&p,&health,7,0,&out));
  p.m_fMaxHealth=200;assert(BotCecilReadItem(&p,&health,7,0,&out));p.health=80;
  p.m_fMaxHealth=100;health.m_fValue=0;assert(!BotCecilReadItem(&p,&health,7,0,&out));
  CArmorItem armor;armor.klass.name="Armor Item";p.m_fArmor=100;
  assert(!BotCecilReadItem(&p,&armor,7,0,&out));
  armor.m_bOverTopArmor=true;assert(BotCecilReadItem(&p,&armor,7,0,&out));
  CAmmoPack pack;pack.klass.name="Ammo Pack";pack.m_iRockets=1;pack.m_iShells=1;
  pack.m_iSniperBullets=0;pack.m_iNapalm=-1;
  assert(BotCecilReadItem(&p,&pack,7,0,&out));
  assert(out.ammo_mask==(bit(4)|bit(5)|bit(8)));
  CAmmoItem ammo;ammo.klass.name="Ammo Item";ammo.m_EaitType=10;
  assert(BotCecilReadItem(&p,&ammo,7,0,&out)&&out.ammo_mask==bit(11));
  ammo.m_EaitType=6;assert(!BotCecilReadItem(&p,&ammo,7,0,&out));
  CPowerUpItem power;power.klass.name="PowerUp Item";
  assert(BotCecilReadItem(&p,&power,7,0,&out)&&out.kind==botcore::CecilItemKind::Powerup);
  power.m_puitType=4;p.m_iSeriousBombCount=3;
  assert(!BotCecilReadItem(&p,&power,7,0,&out));
  p.m_iSeriousBombCount=2;assert(BotCecilReadItem(&p,&power,7,0,&out));
  power.m_puitType=5;assert(!BotCecilReadItem(&p,&power,7,0,&out));
  CEntity other;other.klass.name="MovingBrush";assert(!BotCecilReadItem(&p,&other,7,0,&out));
  assert(!BotCecilReadItem(nullptr,&other,7,0,&out));
  assert(!BotCecilReadItem(&p,nullptr,7,0,&out));
  assert(!BotCecilReadItem(&p,&other,7,0,nullptr));
  CPlayerWeapons w;
  const uint32_t starters=bit(1)|bit(2)|bit(3)|bit(10);
  assert(BotCecilUsableWeapons(&w,false)==starters);
  assert(BotCecilUsableWeapons(&w,true)==16383);
  w.m_iShells=1;assert((BotCecilUsableWeapons(&w,false)&(bit(4)|bit(5)))==bit(4));
  w.m_iShells=2;assert((BotCecilUsableWeapons(&w,false)&(bit(4)|bit(5)))==(bit(4)|bit(5)));
  assert((BotCecilAmmoNeed(&w)&(bit(4)|bit(5)))==(bit(4)|bit(5)));
  w.m_iShells=10;assert((BotCecilAmmoNeed(&w)&(bit(4)|bit(5)))==0);
  w.m_iMaxBullets=0;assert((BotCecilAmmoNeed(&w)&(bit(6)|bit(7)))==0);
  w.m_iRockets=-1;assert(!(BotCecilUsableWeapons(&w,false)&bit(8)));
  assert(BotCecilUsableWeapons(nullptr,false)==0&&BotCecilAmmoNeed(nullptr)==0);
}
"""


def main():
    if not (HERE / "BotCecilItems.h").exists():
        raise AssertionError("native Cecil item adapter not implemented")
    with tempfile.TemporaryDirectory(prefix="cecil-native-contract-") as tmp:
        tmp = Path(tmp)
        sdk = tmp / "EntitiesV"
        sdk.mkdir()
        for name in ("Player", "PlayerWeapons", "WeaponItem", "HealthItem", "ArmorItem",
                     "AmmoItem", "AmmoPack", "PowerUpItem", "Item"):
            (sdk / (name + ".h")).write_text("// field-only contract fixture\n")
        (tmp / "test.cpp").write_text(STUB)
        binary = tmp / "test"
        subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                        "-fsanitize=address,undefined", "-g", "-I", str(tmp), "-I", str(HERE),
                        str(tmp / "test.cpp"), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print("PASS: native item/ammo snapshot contracts (fake SDK, not ABI/runtime proof)")


if __name__ == "__main__":
    main()
