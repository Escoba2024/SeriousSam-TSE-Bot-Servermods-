// SPDX-License-Identifier: GPL-2.0-only
#pragma once
#include "DevPowerupPolicy.h"
#include <EntitiesV/PowerUpItem.h>

static INDEX dev_bRemoveDamageAndInvisibility = 0;

static void DevPowerupCensus(const char *phase) {
  INDEX counts[6] = {0,0,0,0,0,0};
  {FOREACHINDYNAMICCONTAINER(_pNetwork->ga_World.wo_cenEntities,CEntity,it) {
    CEntity *entity = it;
    if(!IsDerivedFromClass(entity,"PowerUp Item")) continue;
    const int type = (int)((CPowerUpItem*)entity)->m_puitType;
    ++counts[(type>=0 && type<5) ? type : 5];
  }}
  CPrintF("[DevPowerups] enabled=%d phase=%s invisibility=%d invulnerability=%d damage=%d speed=%d bomb=%d unknown=%d\n",
    dev_bRemoveDamageAndInvisibility,phase,counts[0],counts[1],counts[2],counts[3],counts[4],counts[5]);
}

static void DevFilterPowerups(BOOL demo) {
  if(demo || !_pNetwork->IsServer()) return;
  DevPowerupCensus("before");
  INDEX removed = 0;
  for(;;) {
    CEntity *selected = NULL;
    {FOREACHINDYNAMICCONTAINER(_pNetwork->ga_World.wo_cenEntities,CEntity,it) {
      CEntity *entity = it;
      if(!IsDerivedFromClass(entity,"PowerUp Item")) continue;
      const int type = (int)((CPowerUpItem*)entity)->m_puitType;
      if(DevRemovePowerup(dev_bRemoveDamageAndInvisibility!=0,true,false,true,type)) {
        selected = entity;
        break;
      }
    }} // release iterator/container lock before Destroy changes the container
    if(selected==NULL) break;
    selected->Destroy();
    ++removed;
  }
  CPrintF("[DevPowerups] removed=%d\n",removed);
  DevPowerupCensus("after");
}
