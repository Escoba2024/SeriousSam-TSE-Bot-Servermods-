// GPL-2.0-only. Passive source-submission receipt; no Engine calls or authority.
#ifndef SSAM_DRIVER_FINAL_DECISION_H
#define SSAM_DRIVER_FINAL_DECISION_H
#include <cstdint>
#include <cstdio>

namespace botcore {
struct CecilDriverFinal {
  bool admitted=false,actualCurrentMapKnown=false;
  int local=0,tick=0,baselineMapPin=-1;
  uint32_t actor=0,entryGeneration=0,exitGeneration=0,exitActor=0;
  bool supplyBlockEntered=false,ready=false,supplyCalled=false,proposalValid=false,weaponsEvaluated=false,weaponsPresent=false;
  uint32_t proposalBits=0,proposalFlags=0,proposalButtons=0;
  int proposalKind=0;
  double proposal[5]={0,0,0,0,0};
  uint32_t preSupplyModeBits=0,modeBits=0,arbitrationFlags=0;
  int cachedTargetIndex=-1;
  double arbitration[5]={0,0,0,0,0};
  bool weaponPolled=false,travelKnife=false,firePolled=false;
  int preWeapon=0,finalWeapon=0,pollWanted=0,fireCurrent=0,fireWanted=0;
  uint32_t pollLastButtons=0,combatSelect=0,cecilButtons=0;
  bool safeCalled=false,safeReacquire=false,safeCombat=false;
  int safeStatus=-1;
  double safeArgs[6]={0,0,0,0,0,0},safeAfter[3]={0,0,0};
  bool submitted=false;
  double translation[3]={0,0,0},rotation[3]={0,0,0},view[3]={0,0,0};
  uint32_t buttons=0;
  bool SameLife()const {
    return admitted&&submitted&&actor!=0&&actor==exitActor&&entryGeneration==exitGeneration;
  }
};
inline bool CecilDriverFinalDue(bool diagnostics,bool supply,bool player,int tick){
  return diagnostics&&supply&&player&&tick%20==0;
}
inline void CecilDriverFinalBegin(CecilDriverFinal& d,bool admitted,int local,int tick,
    uint32_t actor,uint32_t generation,int baselineMapPin){
  if(!admitted)return;
  d.admitted=true;d.local=local;d.tick=tick;d.actor=actor;
  d.entryGeneration=generation;d.baselineMapPin=baselineMapPin;
}
template<class Move>inline void CecilDriverFinalSupply(CecilDriverFinal& d,bool called,
    const Move& m,uint32_t generation,uint32_t actor){
  if(!d.admitted)return;
  d.supplyBlockEntered=true;d.ready=called;
  d.supplyCalled=called;d.exitGeneration=generation;d.exitActor=actor;
  if(!called)return;
  d.proposalValid=true;
  d.proposalBits=(unsigned)m.active|((unsigned)m.ownsMovement<<1)|((unsigned)m.itemGoal<<2)|
    ((unsigned)m.urgent<<3)|((unsigned)m.followGoal<<4)|((unsigned)m.useControl<<5)|
    ((unsigned)m.flightGoal<<6)|((unsigned)m.activeFlight<<7);
  d.proposalKind=(int)m.itemKind;d.proposalFlags=m.flags;d.proposalButtons=m.buttons;
  d.proposal[0]=m.forward;d.proposal[1]=m.strafe;d.proposal[2]=m.up;
  d.proposal[3]=m.yaw_delta;d.proposal[4]=m.pitch_delta;
}
// Pass-through at the OLD short-circuit pointer read: never adds a read.
inline bool CecilDriverFinalPresence(CecilDriverFinal& d,bool present){
  if(d.admitted){d.weaponsEvaluated=true;d.weaponsPresent=present;}
  return present;
}
template<class T,class Field>inline T CecilDriverFinalValue(CecilDriverFinal& d,Field& field,T value){
  if(d.admitted)field=value;
  return value;
}
template<class Action>inline void CecilDriverFinalSubmit(CecilDriverFinal& d,const Action& a,
    uint32_t generation,uint32_t actor){
  if(!d.admitted)return;
  d.submitted=true;d.exitGeneration=generation;d.exitActor=actor;
  for(int i=0;i<3;++i){d.translation[i]=a.pa_vTranslation(i+1);
    d.rotation[i]=a.pa_aRotation(i+1);d.view[i]=a.pa_aViewRotation(i+1);}
  d.buttons=a.pa_ulButtons;
}
inline int CecilDriverFinalFormat(char* out,size_t capacity,const CecilDriverFinal& d){
  if(!d.admitted||!d.submitted)return 0;
  // life_link=0 means UNKNOWN; map_known is ALWAYS false, not an equality test.
  return std::snprintf(out,capacity,
    "[CecilDriverFinalV1] local=%d tick=%d actor=%u gen=(%u,%u) exit_actor=%u baseline_map_pin=%d map_known=0 life_link=%d "
    "pre_supply=(%u,%d) supply=(%d,%d,%d,%d,%u,%d,%u,%u,%.17g,%.17g,%.17g,%.17g,%.17g) wp=(%d,%d) post_mode=%u arb=(%.17g,%.17g,%.17g,%.17g,%.17g,%u) "
    "weapon=(%d,%d,%d,%d,%d,%d,%d,%d,%u,%u,%u) safe=(%d,%d,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g) "
    "submitted=1 action=(%.17g,%.17g,%.17g) rot=(%.17g,%.17g,%.17g) view=(%.17g,%.17g,%.17g) buttons=%u\n",
    d.local,d.tick,d.actor,d.entryGeneration,d.exitGeneration,d.exitActor,d.baselineMapPin,(int)d.SameLife(),
    d.preSupplyModeBits,d.cachedTargetIndex,(int)d.supplyBlockEntered,(int)d.ready,
    (int)d.supplyCalled,(int)d.proposalValid,d.proposalBits,d.proposalKind,d.proposalFlags,d.proposalButtons,
    d.proposal[0],d.proposal[1],d.proposal[2],d.proposal[3],d.proposal[4],
    (int)d.weaponsEvaluated,(int)d.weaponsPresent,d.modeBits,
    d.arbitration[0],d.arbitration[1],d.arbitration[2],d.arbitration[3],d.arbitration[4],d.arbitrationFlags,
    (int)d.weaponPolled,(int)d.travelKnife,d.preWeapon,d.finalWeapon,d.pollWanted,(int)d.firePolled,
    d.fireCurrent,d.fireWanted,d.pollLastButtons,d.combatSelect,d.cecilButtons,
    (int)d.safeCalled,(int)d.safeReacquire,(int)d.safeCombat,d.safeStatus,
    d.safeArgs[0],d.safeArgs[1],d.safeArgs[2],d.safeArgs[3],d.safeArgs[4],d.safeArgs[5],
    d.safeAfter[0],d.safeAfter[1],d.safeAfter[2],d.translation[0],d.translation[1],d.translation[2],
    d.rotation[0],d.rotation[1],d.rotation[2],d.view[0],d.view[1],d.view[2],d.buttons);
}
} // namespace botcore
#endif
