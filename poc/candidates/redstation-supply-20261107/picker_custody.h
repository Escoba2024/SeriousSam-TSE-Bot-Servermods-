// GPL-2.0-only. Fixed passive custody; never authority or an Engine query.
#ifndef SSAM_PICKER_CUSTODY_H
#define SSAM_PICKER_CUSTODY_H
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
namespace botcore {
// Probe codes: 0 uncalled,1 input unknown,2 budget,3 empty/no cast,
// 4 invalid physical result,5 valid blocked,6 valid clear.
struct CecilPickerProbe {int code=0,before=0,after=0;bool lengthKnown=false;double length=0;};
struct CecilPickerNearest {
  const char* end="uncalled";bool geometry=false;int result=-1;
  int slot[3]={-1,-1,-1};double distance2[3]={0,0,0};CecilPickerProbe probe[3];
};
struct CecilPickerAttempt {
  int index=-1,kind=-1,weapon=0,before=0,after=0;uint32_t item=0,itemGeneration=0;
  double x=0,y=0,z=0,value=0;
  const char* end="unattempted";CecilPickerProbe visibility;CecilPickerNearest nearest;
  bool pathKnown=false;double path=0;
  bool Finite(double value){pathKnown=true;path=value;return std::isfinite(value);}
};
inline unsigned CecilPickerReadReason(const char* value){
  const char* const names[]={"ok","null_output","null_player","missing_entity","player_not_alive","deleted","hidden","render_type","player_index","position","weapon_type","health_armor_no_gain_or_invalid","empty_ammo_pack","ammo_kind_or_value","powerup_type_or_capacity","item_class","picked_for_player","item_value","typed_need"};
  if(value)for(unsigned i=0;i<sizeof(names)/sizeof(names[0]);++i)if(!std::strcmp(value,names[i]))return i;
  return 31; // Explicit unknown (also deterministic fixture-only reasons).
}
struct CecilPickerCustody {
  bool active=false;double last=-1;
  int local=-1,tick=-1;uint32_t actor=0,generation=0;
  const char* reason="entered";unsigned known=0,truth=0,mappedKnown=0,mappedTruth=0;
  int anchorBefore=-1,anchorAfter=-1,goalBefore=-1,goalAfter=-1;
  uint32_t itemBefore=0,itemAfter=0;double searchAfter=0,sinceBefore=0,deadlineBefore=0,sinceAfter=0,deadlineAfter=0;
  int budgetBefore=0,budgetAfter=0,scanned=0,count=0,reads=0,readFailed=0,rejected=0,farItems=0,closeItems=0,filtered=0;
  unsigned readReasons=0;bool windowFull=false,inputKnown=false;
  uint32_t owned=0,usable=0;int allowed=0;bool search=false,visibility=false;
  double health=0,armor=0,enemy=0,weaponRadius=0,healthRadius=0,armorRadius=0,ammoRadius=0,x=0,y=0,z=0;
  CecilPickerNearest origin;CecilPickerAttempt attempt[8];int attempts=0;bool overflow=false;
  unsigned refreshReason=0;bool refreshKnown=false;
  void Begin(bool diagnostics,int l,int t,double now,uint32_t a,uint32_t g){
    active=false;
    if(!diagnostics||!std::isfinite(now)||now<0)return;
    if(last>=0&&(now<last||now-last<1))return;
    *this=CecilPickerCustody();active=true;last=now;actor=a;generation=g;local=l;tick=t;
  }
  bool Gate(unsigned bit,bool value){if(active){known|=1u<<bit;if(value)truth|=1u<<bit;}return value;}
  bool Mapped(unsigned bit,bool value){if(active){mappedKnown|=1u<<bit;if(value)mappedTruth|=1u<<bit;}return value;}
  bool Read(bool value,const char* const& why){if(active){++reads;if(!value){++readFailed;readReasons|=1u<<CecilPickerReadReason(why);}}return value;}
  bool Rejected(bool value){if(active&&value)++rejected;return value;}
  int Single(int value){if(active&&value<0)++filtered;return value;}
  template<class InputType>void Input(const InputType& in){if(!active)return;
    inputKnown=true;owned=in.owned;usable=in.usable;health=in.health;armor=in.armor;enemy=in.enemy_distance;
    x=in.x;y=in.y;z=in.z;
    const auto& s=in.settings;allowed=s.iAllowedWeapons;search=s.bItemSearch;visibility=s.bItemVisibility;
    weaponRadius=s.fWeaponDist;healthRadius=s.fHealthDist;armorRadius=s.fArmorDist;ammoRadius=s.fAmmoDist;
  }
  CecilPickerAttempt* Next(int index,int budget){
    if(!active)return NULL;
    if(attempts>=8){overflow=true;return NULL;}
    auto& a=attempt[attempts++];a.index=index;a.before=budget;return &a;
  }
  bool Matches(bool diagnostics,int t,uint32_t a,uint32_t g)const{
    return diagnostics&&active&&local>=0&&t>=0&&actor!=0&&generation!=0&&tick==t&&actor==a&&generation==g;
  }
};
inline int CecilPickerFormat(char* out,size_t capacity,const CecilPickerCustody& d){
  const int n=std::snprintf(out,capacity,
    "[CecilPickerDecision] local=%d tick=%d actor=%u generation=%u time=%.17g reason=%s gates=(%u,%u) mapped=(%u,%u) anchor=(%d,%d) goal=(%d,%d) item=(%u,%u) search_after=%.17g attempt=(%.17g,%.17g) deadline=(%.17g,%.17g) budget=(%d,%d) origin=(%s,%d,%d) scan=(%d,%d,%d,%d,%d,%d,%d,%d,%d,%u) input=(%d,%u,%u,%.17g,%.17g,%.17g,%d,%d,%d,%.17g,%.17g,%.17g,%.17g) source_position=(%.17g,%.17g,%.17g) attempts=%d overflow=%d refresh=(%d,%u)\n",
    d.local,d.tick,d.actor,d.generation,d.last,d.reason,d.known,d.truth,d.mappedKnown,d.mappedTruth,
    d.anchorBefore,d.anchorAfter,d.goalBefore,d.goalAfter,d.itemBefore,d.itemAfter,d.searchAfter,
    d.sinceBefore,d.sinceAfter,d.deadlineBefore,d.deadlineAfter,d.budgetBefore,d.budgetAfter,
    d.origin.end,d.origin.result,(int)d.origin.geometry,d.scanned,d.count,d.reads,d.readFailed,d.rejected,d.farItems,d.closeItems,d.filtered,(int)d.windowFull,d.readReasons,
    (int)d.inputKnown,d.owned,d.usable,d.health,d.armor,d.enemy,d.allowed,(int)d.search,(int)d.visibility,
    d.weaponRadius,d.healthRadius,d.armorRadius,d.ammoRadius,d.x,d.y,d.z,d.attempts,(int)d.overflow,(int)d.refreshKnown,d.refreshReason);
  return n>=0&&(size_t)n<capacity?n:-1;
}
inline int CecilPickerAttemptFormat(char* out,size_t capacity,const CecilPickerCustody& d,int index){
  if(index<0||index>=d.attempts||index>=8)return -1;
  const auto& a=d.attempt[index];const auto& n=a.nearest;const auto& v=a.visibility;
  const int length=std::snprintf(out,capacity,
    "[CecilPickerAttempt] local=%d tick=%d actor=%u generation=%u attempt=%d index=%d item=%u kind=%d weapon=%d snapshot=(%u,%.17g,%.17g,%.17g,%.17g) end=%s budget=(%d,%d) visibility=(%d,%d,%d,%d,%.17g) nearest=(%s,%d,%d) path=(%d,%.17g) h0=(%d,%.17g,%d,%d,%d,%d,%.17g) h1=(%d,%.17g,%d,%d,%d,%d,%.17g) h2=(%d,%.17g,%d,%d,%d,%d,%.17g)\n",
    d.local,d.tick,d.actor,d.generation,index,a.index,a.item,a.kind,a.weapon,a.itemGeneration,a.value,a.x,a.y,a.z,a.end,a.before,a.after,
    v.code,v.before,v.after,(int)v.lengthKnown,v.length,n.end,n.result,(int)n.geometry,(int)a.pathKnown,a.path,
    n.slot[0],n.distance2[0],n.probe[0].code,n.probe[0].before,n.probe[0].after,(int)n.probe[0].lengthKnown,n.probe[0].length,
    n.slot[1],n.distance2[1],n.probe[1].code,n.probe[1].before,n.probe[1].after,(int)n.probe[1].lengthKnown,n.probe[1].length,
    n.slot[2],n.distance2[2],n.probe[2].code,n.probe[2].before,n.probe[2].after,(int)n.probe[2].lengthKnown,n.probe[2].length);
  return length>=0&&(size_t)length<capacity?length:-1;
}
inline int CecilPickerOriginFormat(char* out,size_t capacity,const CecilPickerCustody& d){
  const auto& n=d.origin;
  const int length=std::snprintf(out,capacity,
    "[CecilPickerOrigin] local=%d tick=%d actor=%u generation=%u nearest=(%s,%d,%d) h0=(%d,%.17g,%d,%d,%d,%d,%.17g) h1=(%d,%.17g,%d,%d,%d,%d,%.17g) h2=(%d,%.17g,%d,%d,%d,%d,%.17g)\n",
    d.local,d.tick,d.actor,d.generation,n.end,n.result,(int)n.geometry,
    n.slot[0],n.distance2[0],n.probe[0].code,n.probe[0].before,n.probe[0].after,(int)n.probe[0].lengthKnown,n.probe[0].length,
    n.slot[1],n.distance2[1],n.probe[1].code,n.probe[1].before,n.probe[1].after,(int)n.probe[1].lengthKnown,n.probe[1].length,
    n.slot[2],n.distance2[2],n.probe[2].code,n.probe[2].before,n.probe[2].after,(int)n.probe[2].lengthKnown,n.probe[2].length);
  return length>=0&&(size_t)length<capacity?length:-1;
}
// Kept outside old DriverFinal schema/admission. All Gate calls pass through
// the one original short-circuited expression, not a reconstructed decision.
struct CecilPickerArbitration {
  bool enabled=false,taken=false,proposalKnown=false;unsigned known=0,truth=0,bits=0;
  double proposal[3]={0,0,0};
  explicit CecilPickerArbitration(bool diagnostics):enabled(diagnostics){}
  bool Gate(unsigned bit,bool value){if(enabled){known|=1u<<bit;if(value)truth|=1u<<bit;}return value;}
  template<class Move>void Supply(bool called,const Move& m){if(!enabled||!called)return;proposalKnown=true;
    bits=(unsigned)m.active|((unsigned)m.ownsMovement<<1)|((unsigned)m.itemGoal<<2)|((unsigned)m.urgent<<3)|
      ((unsigned)m.flightGoal<<4)|((unsigned)m.activeFlight<<5)|((unsigned)m.useControl<<6);
    proposal[0]=m.forward;proposal[1]=m.strafe;proposal[2]=m.up;
  }
};
template<class Action>inline int CecilPickerArbitrationFormat(char* out,size_t capacity,const CecilPickerCustody& d,
    const CecilPickerArbitration& a,const Action& action){
  const int n=std::snprintf(out,capacity,
    "[CecilPickerArbitration] local=%d tick=%d actor=%u generation=%u proposal=(%d,%u,%.17g,%.17g,%.17g) gates=(%u,%u) taken=%d submitted=1 action=(%.17g,%.17g,%.17g) rotation=(%.17g,%.17g,%.17g) buttons=%u refresh=(%d,%u)\n",
    d.local,d.tick,d.actor,d.generation,(int)a.proposalKnown,a.bits,a.proposal[0],a.proposal[1],a.proposal[2],a.known,a.truth,(int)a.taken,
    (double)action.pa_vTranslation(1),(double)action.pa_vTranslation(2),(double)action.pa_vTranslation(3),
    (double)action.pa_aRotation(1),(double)action.pa_aRotation(2),(double)action.pa_aRotation(3),(unsigned)action.pa_ulButtons,
    (int)d.refreshKnown,d.refreshReason);
  return n>=0&&(size_t)n<capacity?n:-1;
}
} // namespace botcore
#endif
