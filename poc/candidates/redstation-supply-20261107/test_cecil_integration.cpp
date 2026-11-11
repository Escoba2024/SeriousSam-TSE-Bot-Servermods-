#include "bot_human.h"
#include <cassert>
#include <cstdio>
#include <initializer_list>
using namespace botcore;
int main() {
  assert(!CecilTravelKnife(2,0,true,false));
  assert(CecilTravelKnife(2.05,0,true,false));
  assert(!CecilTravelKnife(20,0,true,true));
  assert(!CecilTravelKnife(20,0,false,false));

  BotProfile profile; assert(BuildProfile(3,0,123,"test",&profile));
  WeaponSelector weapons; weapons.Configure(profile.skill);
  weapons.ForceWeapon(8);
  LoadoutInput travel; travel.usable_mask=3;
  assert(weapons.Update(travel,1)!=8); // Lost weapon cannot remain selected while travelling.
  HumanBotPolicy human; human.Configure(&profile);
  WorldView world;world.tick=1;world.alive=true;world.health=100;
  world.current_weapon=8;world.usable_weapons=(1u<<7)|3u;
  human.BeginTick(world);
  SenseInput enemy{};enemy.index=1;enemy.x=0;enemy.y=0;enemy.z=-30;
  enemy.health=100;enemy.alive=true;bool los=true;
  for(int tick=1;tick<100;++tick){world.tick=tick;human.BeginTick(world);human.Step(world,&enemy,&los,1,.05);}
  assert(human.weapons().current()!=0);
  world.alive=false;world.tick=100;human.BeginTick(world);
  assert(human.weapons().current()==0); // Death resets weapon hold state with target memory.
  Perception perception;perception.Configure(profile.skill,123);
  enemy.entity_id=11;enemy.generation=1;
  perception.BeginTick(1,0,0,0,0,0);perception.Observe(enemy,true);
  assert(perception.Track(1)!=nullptr);
  enemy.entity_id=12;
  perception.BeginTick(2,0,0,0,0,0);perception.Observe(enemy,false);
  assert(perception.Track(1)==nullptr);
  enemy.enemy=true;perception.BeginTick(3,0,0,0,0,0);perception.Observe(enemy,true);
  assert(perception.Track(1)!=nullptr);
  enemy.enemy=false;perception.BeginTick(4,0,0,0,0,0);perception.Observe(enemy,true);
  assert(!perception.NeedsLineOfSight(enemy)&&perception.Track(1)==nullptr);
  for(int weapon : {3,8,9,11,14}) {
    WeaponSelector choice;choice.Configure(profile.skill);
    LoadoutInput fight;fight.cecil=true;fight.has_target=true;
    fight.usable_mask=3u|(1u<<(weapon-1));fight.distance_m=weapon==11?8:24;
    assert(choice.Update(fight,100)==weapon);
  }
  WeaponSelector upgrade;upgrade.Configure(profile.skill);upgrade.ForceWeapon(2);
  LoadoutInput doublecolt;doublecolt.cecil=true;doublecolt.has_target=true;
  doublecolt.usable_mask=7;doublecolt.distance_m=24;
  assert(upgrade.Update(doublecolt,100)==3);
  LoadoutInput distant;distant.cecil=true;distant.has_target=true;
  distant.distance_m=100;distant.usable_mask=(1u<<12)|(1u<<13);
  WeaponSelector original;original.Configure(profile.skill);
  assert(original.Update(distant,100)==14); // Cecil ratings: Cannon165 > Sniper150 at100.
  LoadoutInput near;near.cecil=true;near.has_target=true;near.distance_m=3;
  near.usable_mask=3u|(1u<<7)|(1u<<8)|(1u<<13);
  WeaponSelector safe;safe.Configure(profile.skill);assert(safe.Update(near,100)==2);
  puts("Cecil native policy integration contracts PASS");
}
