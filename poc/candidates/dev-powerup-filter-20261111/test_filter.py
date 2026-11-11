#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise actual destructive filter with a mutation-checking world container.
Retail ABI, serialization and network compatibility require separate runtime tests.
"""
import pathlib, subprocess, tempfile
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=r'''
#include <cassert>
#include <vector>
#include <algorithm>
#include <cstdarg>
#include <cstdio>
using INDEX=int; using BOOL=int;
int locks=0;
struct CEntity { int type;bool powerup;explicit CEntity(int t,bool p=true):type(t),powerup(p){};void Destroy(); };
struct Container {std::vector<CEntity*> entities;};
struct Iterator {
 Container& c;size_t index=0;
 Iterator(Container& v):c(v){++locks;} ~Iterator(){--locks;}
 explicit operator bool()const{return index<c.entities.size();}
 operator CEntity*()const{return c.entities[index];}
 void operator++(){++index;}
};
#define FOREACHINDYNAMICCONTAINER(container,type,it) for(Iterator it(container);it;++it)
struct Network { bool server=true; struct {Container wo_cenEntities;}ga_World;bool IsServer(){return server;} }network;
Network* _pNetwork=&network;
void CEntity::Destroy(){assert(locks==0);auto& v=network.ga_World.wo_cenEntities.entities;v.erase(std::find(v.begin(),v.end(),this));}
bool IsDerivedFromClass(CEntity* e,const char*){return e->powerup;}
void CPrintF(const char* f,...){va_list v;va_start(v,f);vprintf(f,v);va_end(v);}
#include "DevPowerupFilter.h"
int main(){
 CPowerUpItem invis(0),damage(2),damage2(2),invuln(1),speed(3),bomb(4),unknown(9),other(0,false);
 auto& v=network.ga_World.wo_cenEntities.entities;
 v={&invis,&damage,&damage2,&invuln,&speed,&bomb,&unknown,&other};
 assert(dev_bRemoveDamageAndInvisibility==0);
 DevFilterPowerups(false);assert(v.size()==8);
 dev_bRemoveDamageAndInvisibility=1;
 network.server=false;DevFilterPowerups(false);assert(v.size()==8);
 network.server=true;DevFilterPowerups(true);assert(v.size()==8);
 DevFilterPowerups(false);assert((v==std::vector<CEntity*>{&invuln,&speed,&bomb,&unknown,&other}));
 DevFilterPowerups(false);assert(v.size()==5);
 v.clear();DevFilterPowerups(false);assert(v.empty());
}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=pathlib.Path(tmp);(p/'EntitiesV').mkdir();(p/'EntitiesV/PowerUpItem.h').write_text('struct CPowerUpItem:CEntity {int m_puitType;CPowerUpItem(int t,bool p=true):CEntity(t,p),m_puitType(t){} };\n')
 (p/'test.cpp').write_text(SOURCE)
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-I'+str(p),'-I'+str(ROOT),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('Actual filter: default-off, client/demo guard, selective destructive mutation, iterator release, idempotence and empty world PASS')
