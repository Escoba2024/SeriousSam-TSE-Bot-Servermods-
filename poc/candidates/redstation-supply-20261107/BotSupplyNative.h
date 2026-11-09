// GPL-2.0-only. ssam.ai native read-only Cecil bridge, 2026-11-07.
// World access stays under ga_csNetwork; graph/config I/O stays on main thread.
#ifndef BOT_SUPPLY_NATIVE_H
#define BOT_SUPPLY_NATIVE_H
#include "cecil_nav_data.h"
#include "cecil_motion.h"
#include "cecil_rules.h"
#include "BotCecilItems.h"
#include <EntitiesV/Switch.h>
#include <EntitiesV/MovingBrush.h>
#include <EntitiesV/Marker.h>
#include <Engine/Base/Stream.h>
#include <Engine/Brushes/Brush.h>
#include <utility>
// Driver supplies a frozen perception snapshot; this bridge never resolves its entity.
struct SCecilFollowGoal {
  bool valid=false;
  double x=0,y=0,z=0;
  uint32_t entity=0,generation=0;
  double expiresAt=0;
};
struct SCecilProbe {
  // Stable telemetry values; reasonMask uses (1u << Reason).
  enum Reason {reasonNone=0,reasonWallHit=1,reasonNoFloor=2,reasonUnsupportedNormal=3,
               reasonPassable=4,reasonInvalid=5,reasonBudget=6};
  double inputForward=0,inputStrafe=0,inputUp=0,finalYaw=0;
  int primaryReason=reasonNone,lastReason=reasonNone,renderType=-1;
  unsigned reasonMask=0,wallRays=0,floorRays=0;
  ULONG hitEntity=0;
  double support=0,normal[3]={0,0,0},from[3]={0,0,0},to[3]={0,0,0};
};
struct SSupplyState {
  SCecilProbe probe;
  botcore::CecilNavigator navigator;
  botcore::CecilNavSearch goals;
  std::vector<unsigned char> blocked,worldLock; // 0 open, 1 moved, 2 missing, 3 unseen.
  uint32_t entity=0,generation=0,rng=1,goalEntity=0,owned=0,followEntity=0,followGeneration=0;
  double currentNavTime=-1;
  int currentNavGoal=-1; // Fresh navigator context; an anchor/old hop alone is not a current point.
  int goal=-1,anchor=-1,hop=-1,spawnTick=0,scanTick=0,itemScanAfter=0,avoidNode=-1,heldNode=-1;
  double searchAfter=0,goalSince=0,deadSince=-1,followAfter=0,avoidUntil=0,holdSince=-1;
  uint32_t avoidFollowEntity=0,lastUseEntity=0;
  int interactionPoint=-1,useReleaseTick=-1;
  double interactionSince=-1,useAfter=0;
  double escapeUntil=0,escapeAfter=0,escapeClock=-1,escapeWorld[3]={0,0,0},escapeOrigin[3]={0,0,0};
  int escapeSide=1;
  bool escapeReverseUsed=false;
  double escapeBlockPosition[3]={0,0,0},escapeRequest[3]={0,0,0};
  bool playable=false,hadUpgrade=false,importantGoal=false,levelSwimView=false;
  botcore::CecilItemKind goalKind=botcore::CecilItemKind::Weapon;
  // 256 fixed records cover eight rejects/second for the thirty-second TTL.
  struct Rejection {uint32_t id=0;double until=0;} rejected[256];
  unsigned deaths=0,respawns=0,pickups=0;
  bool ItemRejected(uint32_t id,double now)const{
    for(const auto& r:rejected)if(r.id==id&&now<r.until)return true;
    return false;
  }
  void RejectItem(uint32_t id,double now){
    if(!id)return;
    size_t victim=0;
    for(size_t i=0;i<256;++i){
      if(rejected[i].id==id){victim=i;break;}
      if(rejected[i].until<rejected[victim].until)victim=i;
    }
    rejected[victim].id=id;rejected[victim].until=now+30;
  }
  void ClearRejections(){for(auto& r:rejected)r=Rejection();}
  void ClearAvoidance(){avoidNode=heldNode=-1;avoidUntil=0;holdSince=-1;avoidFollowEntity=0;}
  void ClearGoal(){currentNavTime=-1;currentNavGoal=-1;interactionPoint=-1;interactionSince=-1;heldNode=-1;holdSince=-1;navigator.Reset();goal=-1;goalEntity=0;hop=-1;importantGoal=false;followEntity=followGeneration=0;followAfter=0;}
  void ClearEscape(){escapeUntil=escapeAfter=0;escapeClock=-1;escapeSide=1;escapeReverseUsed=false;}
  void ResetLockSnapshot(){for(auto& value:worldLock)value=3;}
  void Reset() {
    probe=SCecilProbe();ClearGoal();ClearRejections();ClearAvoidance();ClearEscape();ResetLockSnapshot();entity=owned=0;anchor=-1;
    itemScanAfter=scanTick=spawnTick=0;searchAfter=goalSince=0;deadSince=-1;
    playable=hadUpgrade=levelSwimView=false;useReleaseTick=-1;lastUseEntity=0;useAfter=0;++generation;
  }
};
struct SCecilMove {
  bool active=false,itemGoal=false,urgent=false,followGoal=false,useControl=false;
  botcore::CecilItemKind itemKind=botcore::CecilItemKind::Weapon;
  double forward=0,strafe=0,up=0,yaw_delta=0,pitch_delta=0;uint32_t flags=0,buttons=0;
};
static SSupplyState &BotSupplyState(INDEX slot){static SSupplyState states[4];return states[slot&3];}
static botcore::CecilNavGraph &BotSupplyGraph(){static botcore::CecilNavGraph graph;return graph;}
static botcore::CecilSettings &BotCecilSettings(){static botcore::CecilSettings settings=botcore::CecilPreset(2);return settings;}
static void BotSupplyReset(INDEX slot){BotSupplyState(slot).Reset();}
static unsigned BotCecilRandom(SSupplyState &s){s.rng^=s.rng<<13;s.rng^=s.rng>>17;s.rng^=s.rng<<5;return s.rng;}
static void BotSupplyUpdateNavigation(CGame *game){
  static CTString previousWorld="";static BOOL previousEnabled=FALSE;static LONG previousSerial=-1;
  const BOOL enabled=bot_bEnabled&&bot_bSupplyNavigation&&game!=NULL&&game->gm_bGameOn;
  const CTString world=enabled?CTString(_pNetwork->GetCurrentWorld()):CTString("");
  const LONG serial=InterlockedCompareExchange(&_botSupplyMapSerial,0,0);
  if(enabled==previousEnabled&&world==previousWorld&&serial==previousSerial)return;
  previousSerial=serial;previousEnabled=enabled;previousWorld=world;
  botcore::CecilNavGraph loaded;botcore::CecilSettings settings=botcore::CecilPreset(2);
  bool valid=false;unsigned mapCRC=0,navCRC=0;char navPath[256]={0};
  if(enabled){
    try {
      FILE *config=std::fopen("Scripts/Cecil/settings.txt","rb");
      char text[256]={0};
      if(config){size_t n=std::fread(text,1,sizeof(text)-1,config);bool ok=!std::ferror(config)&&std::feof(config);std::fclose(config);
        if(!ok||n==0||!botcore::CecilParseSettings(text,settings))throw "invalid Cecil settings";}
      else throw "missing Cecil settings";
      FILE *manifest=std::fopen("Scripts/Cecil/maps.txt","rb");
      if(!manifest)throw "missing Cecil map manifest";
      char line[1024],path[256],nav[256],extra;int version=0;
      bool header=std::fgets(line,sizeof(line),manifest)&&std::sscanf(line,"cecil-maps %d %c",&version,&extra)==1&&version==1;
      unsigned expectedMap=0,expectedNav=0;bool found=false;
      while(header&&std::fgets(line,sizeof(line),manifest)){
        if(std::sscanf(line,"%x %x %255s %255s %c",&expectedMap,&expectedNav,path,nav,&extra)!=4){header=false;break;}
        if(_stricmp(path,(const char*)world)==0){
          if(found){header=false;break;}
          found=true;mapCRC=expectedMap;navCRC=expectedNav;
          std::strncpy(navPath,nav,sizeof(navPath)-1);
        }
      }
      bool ioError=std::ferror(manifest)!=0;std::fclose(manifest);
      if(!header||!found||ioError||std::strncmp(navPath,"Scripts/Cecil/",14)!=0||std::strstr(navPath,".."))throw "invalid/missing map binding";
      if(GetFileCRC32_t(CTFileName(world))!=mapCRC)throw "map content CRC mismatch";
      if(GetFileCRC32_t(CTFileName(CTString(navPath)))!=navCRC)throw "NAV content CRC mismatch";
      FILE *file=std::fopen(navPath,"rb");if(!file)throw "NAV file missing";
      std::fseek(file,0,SEEK_END);long n=std::ftell(file);std::rewind(file);
      if(n<=0||n>(long)botcore::CecilNavGraph::kMaxBytes){std::fclose(file);throw "NAV size rejected";}
      std::vector<unsigned char> bytes((size_t)n);
      const bool read=std::fread(bytes.data(),1,bytes.size(),file)==bytes.size()&&!std::ferror(file);std::fclose(file);
      std::string error;if(!read||!loaded.Load(bytes.data(),bytes.size(),&error))throw "NAV parse rejected";
      valid=true;
    }catch(const char* error){BotLog("[CecilLoad] rejected=%s world=%s\n",error,(const char*)world);}
     catch(...){BotLog("[CecilLoad] rejected=exception world=%s\n",(const char*)world);}
  }
  SSupplyState prepared[4];
  for(int i=0;i<4;++i){
    prepared[i].navigator.Prepare(loaded.points.size());prepared[i].goals.Prepare(loaded.points.size());
    prepared[i].blocked.resize(loaded.points.size());prepared[i].worldLock.assign(loaded.points.size(),3);prepared[i].generation=(uint32_t)serial+1;
    prepared[i].rng=(uint32_t)bot_iProfileSeed^(0x9e3779b9u*(1+i+bot_iRosterOffset));
    if(!prepared[i].rng)prepared[i].rng=1;
  }
  CTSingleLock hooks(&_pTimer->tm_csHooks,TRUE);
  if(serial!=InterlockedCompareExchange(&_botSupplyMapSerial,0,0))return;
  BotSupplyGraph()=std::move(loaded);BotCecilSettings()=settings;
  for(int i=0;i<4;++i){BotSupplyState(i)=std::move(prepared[i]);BotHumanAttach(i);}
  InterlockedExchange(&_botSupplyMapReady,enabled&&valid);
  BotLog("[CecilLoad] policy=cecil-human-v1 schema=1 world=%s ready=%d nodes=%d map_crc=%08x nav_crc=%08x\n",
    (const char*)world,valid,(int)BotSupplyGraph().points.size(),mapCRC,navCRC);
}
static botcore::CecilFrame BotCecilBodyFrame(const CPlayer* player){
  botcore::CecilFrame frame;
  const FLOAT3D right=FLOAT3D(1,0,0)*player->GetRotationMatrix();
  const FLOAT3D up=FLOAT3D(0,1,0)*player->GetRotationMatrix();
  const FLOAT3D back=FLOAT3D(0,0,1)*player->GetRotationMatrix();
  for(int i=0;i<3;++i){frame.right[i]=right(i+1);frame.up[i]=up(i+1);frame.back[i]=back(i+1);}
  return frame;
}
static bool BotCecilFrameReady(const CPlayer* player){
  if(!player||!BotCecilBodyFrame(player).Valid())return false;
  for(int i=1;i<=3;++i)if(!std::isfinite(player->GetPlacement().pl_PositionVector(i))||
    !std::isfinite(player->en_plViewpoint.pl_OrientationAngle(i)))return false;
  double length=0;
  for(int i=1;i<=3;++i){const double g=player->en_vGravityDir(i);if(!std::isfinite(g))return false;length+=g*g;}
  return std::fabs(length-1)<1e-3;
}
static double BotCecilHeight(const CPlayer* player,const FLOAT3D& delta){
  return delta(1)*player->en_vGravityDir(1)+delta(2)*player->en_vGravityDir(2)+delta(3)*player->en_vGravityDir(3);
}
static BOOL BotSupplyClear(CPlayer *player,const FLOAT3D &from,const FLOAT3D &to,CEntity *item=NULL){
  // Reserve the final wall and floor probes for each action.
  if(_botRayBudget<=2)return FALSE;
  --_botRayBudget;
  CCastRay ray(player,from,to);ray.cr_bAllowOverHit=FALSE;ray.cr_bPhysical=TRUE;
  ray.cr_ttHitModels=CCastRay::TT_COLLISIONBOX;ray.Cast(player->GetWorld());
  return ray.cr_penHit==NULL||ray.cr_penHit==item;
}
static int BotSupplyNearest(CPlayer *player,const FLOAT3D &position,BOOL fromPlayer,CEntity *item=NULL){
  if(!BotCecilFrameReady(player)||!std::isfinite(position(1))||!std::isfinite(position(2))||!std::isfinite(position(3)))return -1;
  const auto& graph=BotSupplyGraph();int slots[3]={-1,-1,-1};
  const double limit=fromPlayer?144.0:64.0;double distances[3]={limit+1e-6,limit+1e-6,limit+1e-6};
  for(size_t i=0;i<graph.points.size();++i){
    const auto& p=graph.points[i];const FLOAT3D delta(p.x-position(1),p.y-position(2),p.z-position(3));
    const double height=BotCecilHeight(player,delta);if(std::fabs(height)>3)continue;
    const double distance=double(delta(1))*delta(1)+double(delta(2))*delta(2)+double(delta(3))*delta(3);
    const double d=fromPlayer?std::fmax(0,distance-height*height):distance;
    if(d>limit)continue;
    for(int k=0;k<3;++k)if(d<distances[k]){for(int j=2;j>k;--j){distances[j]=distances[j-1];slots[j]=slots[j-1];}slots[k]=(int)i;distances[k]=d;break;}
  }
  for(int k=0;k<3;++k)if(slots[k]>=0){
    const auto& p=graph.points[slots[k]];const FLOAT3D lift=player->en_vGravityDir*-.8f;
    FLOAT3D node=FLOAT3D(p.x,p.y,p.z)+lift,end=position+lift;
    if(BotSupplyClear(player,fromPlayer?end:node,fromPlayer?node:end,item))return slots[k];
  }
  return -1;
}
static void BotCecilLocks(CPlayer *player,SSupplyState& state,double now){
  const auto& graph=BotSupplyGraph();
  for(size_t i=0;i<graph.points.size();++i){
    const auto& p=graph.points[i];bool blocked=false;
    if(p.lock_entity>=0){
      CEntity *entity=player->GetWorld()->EntityFromID((ULONG)p.lock_entity);
      const bool present=entity&&(entity->GetFlags()&ENF_DELETED)==0;
      double d=0,a=0;
      if(present){
        const CPlacement3D &pl=entity->GetPlacement();
        for(int j=0;j<3;++j){double x=pl.pl_PositionVector(j+1)-p.lock_origin[j];double y=pl.pl_OrientationAngle(j+1)-p.lock_origin[j+3];d+=x*x;a+=y*y;}
      }
      blocked=!present||d>.01||a>.01;
      const unsigned char physical=present?(blocked?1:0):2;
      if(i<state.worldLock.size()&&state.worldLock[i]!=physical){
        state.worldLock[i]=physical;
        BotLog("[CecilLock] node=%d entity=%d locked=%d present=%d player=%lu generation=%lu time=%.3f distance=%.4f angle=%.4f\n",
          (int)i,p.lock_entity,blocked,present,(unsigned long)player->en_ulID,(unsigned long)state.generation,now,std::sqrt(d),std::sqrt(a));
      }
    }
    blocked=blocked||(!state.importantGoal&&(int)i==state.avoidNode&&now<state.avoidUntil);
    state.blocked[i]=blocked?1:0;
  }
}
static botcore::CecilItemInput BotCecilItemInput(CPlayer* player,const SSupplyState& state,double enemyDistance){
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  CPlayerWeapons* weapons=player->GetPlayerWeapons();
  const CSessionProperties *session=(const CSessionProperties*)_pNetwork->GetSessionProperties();
  botcore::CecilItemInput input;input.generation=state.generation;input.owned=weapons->m_iAvailableWeapons;
  input.usable=BotCecilUsableWeapons(weapons,session->sp_bInfiniteAmmo!=FALSE);
  input.ammo_need_mask=session->sp_bInfiniteAmmo?0:BotCecilAmmoNeed(weapons);
  input.x=position(1);input.y=position(2);input.z=position(3);input.health=player->GetHealth();input.armor=player->m_fArmor;
  input.enemy_distance=enemyDistance;input.settings=BotCecilSettings();return input;
}
static bool BotCecilUrgentItem(const botcore::CecilItem& item,const botcore::CecilItemInput& input){
  using botcore::CecilItemKind;
  if(item.kind==CecilItemKind::Health)return input.health<std::fmin(50.0,input.settings.fHealthSearch);
  if(item.kind==CecilItemKind::Ammo||item.kind==CecilItemKind::AmmoPack)
    return (item.ammo_mask&input.ammo_need_mask&input.owned)!=0;
  if(item.kind==CecilItemKind::Weapon){
    // Basic pistols and melee do not replace a usable collected ranged weapon.
    for(int id=4;id<=14;++id){
      const uint32_t mask=botcore::CecilWeaponMask(id);
      if(id!=10&&(input.usable&mask)&&(input.settings.iAllowedWeapons==-1||
         ((uint32_t)input.settings.iAllowedWeapons&mask))&&
         botcore::CecilFireRangeSafe(id,input.enemy_distance))return false;
    }
    return true;
  }
  return false;
}
static void BotCecilGoalEnd(INDEX slot,INDEX tick,const SSupplyState& state,const char* reason){
  if(state.goalEntity)BotLog("[CecilGoalEnd] local=%d tick=%d entity=%lu reason=%s\n",
    slot,tick,(unsigned long)state.goalEntity,reason);
}
static void BotCecilChooseGoal(CPlayer *player,INDEX slot,INDEX tick,double enemyDistance,bool allowPatrol=true){
  SSupplyState& s=BotSupplyState(slot);const auto& graph=BotSupplyGraph();
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;const double now=tick*_pTimer->TickQuantum;
  s.anchor=BotSupplyNearest(player,position,TRUE);
  if(s.anchor<0)return;
  BotCecilLocks(player,s,now);
  s.goals.Run(graph,s.anchor,s.blocked.data(),s.blocked.size());
  if(s.goal>=0&&(s.goal>=(int)graph.points.size()||!std::isfinite(s.goals.Distance(s.goal)))){
    BotCecilGoalEnd(slot,tick,s,"unreachable");s.RejectItem(s.goalEntity,now);s.ClearGoal();
  }
  const auto input=BotCecilItemInput(player,s,enemyDistance);const auto& settings=input.settings;
  // A retained item is one attempt with one lifetime, not a new goal every scan.
  if(!s.goalEntity&&now>=s.searchAfter&&settings.bItemSearch){
    botcore::CecilItem items[128];int count=0,scanned=0;
    // Rotate the bounded snapshot window. Unusable prefix items never occupy it,
    // and eligible prefixes cannot hide later candidates on every scan.
    const int skip=s.itemScanAfter;s.itemScanAfter=0;
    {FOREACHINDYNAMICCONTAINER(player->GetWorld()->wo_cenEntities,CEntity,iten){
      if(++scanned>8192)break;
      if(scanned<=skip)continue;
      botcore::CecilItem item;
      if(!BotCecilReadItem(player,&*iten,s.generation,input.owned,&item)||s.ItemRejected(item.id,now))continue;
      double d=std::fabs(item.x-input.x)+std::fabs(item.z-input.z)+3*std::fabs(item.y-input.y);
      if(d>128)continue;
      if(enemyDistance<8&&!(item.kind==botcore::CecilItemKind::Health&&BotCecilUrgentItem(item,input)))continue;
      item.visible=item.reachable=true;
      if(botcore::CecilChooseItem(&item,1,input)<0)continue;
      items[count++]=item;
      if(count==128){s.itemScanAfter=scanned;break;}
    }}
    for(int attempt=0;attempt<8&&_botRayBudget>3;++attempt){
      int index=botcore::CecilChooseItem(items,count,input);if(index<0)break;
      auto& item=items[index];CEntity* entity=player->GetWorld()->EntityFromID(item.id);
      if(!entity){item.reachable=false;s.RejectItem(item.id,now);continue;}
      const FLOAT3D target=FLOAT3D((FLOAT)item.x,(FLOAT)item.y,(FLOAT)item.z)-player->en_vGravityDir*.5f;
      if(settings.bItemVisibility&&!BotSupplyClear(player,BotCombatEye(player).pl_PositionVector,target,entity)){
        item.visible=false;s.RejectItem(item.id,now);continue;
      }
      int anchor=BotSupplyNearest(player,FLOAT3D((FLOAT)item.x,(FLOAT)item.y,(FLOAT)item.z),FALSE,entity);
      if(anchor<0&&_botRayBudget<=2)break;
      if(anchor<0||!std::isfinite(s.goals.Distance(anchor))){item.reachable=false;s.RejectItem(item.id,now);continue;}
      s.ClearGoal();s.goal=anchor;s.goalEntity=item.id;s.goalSince=now;s.searchAfter=now+settings.fItemSearchCD;
      s.importantGoal=false;s.goalKind=item.kind;s.navigator.Reset();
      BotLog("[CecilGoal] local=%d tick=%d entity=%lu kind=%d weapon=%d anchor=%d pos=(%.3f,%.3f,%.3f)\n",
        slot,tick,(unsigned long)item.id,(int)item.kind,item.weapon,anchor,item.x,item.y,item.z);break;
    }
  }
  if(s.goal<0&&allowPatrol){
    s.ClearGoal();
    const bool preferImportant=(BotCecilRandom(s)%1000)<(unsigned)(settings.fImportantChance*1000);
    unsigned start=BotCecilRandom(s)%(unsigned)graph.points.size();
    for(size_t j=0;j<graph.points.size();++j){
      int node=(int)((start+j)%graph.points.size());const auto& p=graph.points[node];
      if(node==s.anchor||!std::isfinite(s.goals.Distance(node)))continue;
      if(preferImportant&&p.important_entity<0&&!(p.flags&botcore::CECIL_IMPORTANT))continue;
      s.goal=node;break;
    }
    if(s.goal<0)for(size_t j=0;j<graph.points.size();++j)if((int)j!=s.anchor&&std::isfinite(s.goals.Distance((int)j))){s.goal=(int)j;break;}
    if(s.goal>=0){const auto& point=graph.points[s.goal];s.importantGoal=point.important_entity>=0||(point.flags&botcore::CECIL_IMPORTANT);}
    s.goalSince=now;s.navigator.Reset();
  }
}
static bool BotCecilFollowValid(const SCecilFollowGoal* follow,double now){
  return follow&&follow->valid&&follow->entity&&
    follow->generation==(uint32_t)InterlockedCompareExchange(&_botSupplyMapSerial,0,0)&&
    std::isfinite(follow->x)&&std::isfinite(follow->y)&&std::isfinite(follow->z)&&
    std::isfinite(follow->expiresAt)&&now<follow->expiresAt;
}
static void BotCecilFollow(CPlayer* player,SSupplyState& s,const SCecilFollowGoal& follow,double now){
  if(s.goalEntity)return;
  if(s.followEntity!=follow.entity||s.followGeneration!=follow.generation){
    s.ClearGoal();s.followEntity=follow.entity;s.followGeneration=follow.generation;
  }
  if(now<s.followAfter)return;
  s.followAfter=now+1;
  if(s.anchor<0||_botRayBudget<=2)return;
  const int goal=BotSupplyNearest(player,FLOAT3D((FLOAT)follow.x,(FLOAT)follow.y,(FLOAT)follow.z),FALSE);
  if(goal<0&&_botRayBudget<=2)return;
  BotCecilLocks(player,s,now);
  s.goals.Run(BotSupplyGraph(),s.anchor,s.blocked.data(),s.blocked.size());
  if(goal<0||!std::isfinite(s.goals.Distance(goal))){s.goal=-1;s.navigator.Reset();return;}
  if(s.goal!=goal){s.goal=goal;s.goalSince=now;s.navigator.Reset();}
  s.importantGoal=false;
}
static bool BotCecilLiquid(const CPlayer* player){
  return BotCecilFrameReady(player)&&(player->m_pstState==PST_SWIM||player->m_pstState==PST_DIVE);
}
static void BotCecilSwimMotion(CPlayer* player,const FLOAT3D& delta,double yaw,double dt,botcore::CecilMotion& move,bool& leveling){
  const double length=delta.Length();if(length<1e-6)return;
  const auto local=BotCecilBodyFrame(player).ToLocal(delta(1),delta(2),delta(3));
  const double angle=yaw*3.141592653589793/180;
  double back=(std::sin(angle)*local.x+std::cos(angle)*local.z)/length;
  double side=(std::cos(angle)*local.x-std::sin(angle)*local.z)/length,up=local.y/length;
  const double viewPitch=player->en_plViewpoint.pl_OrientationAngle(2);
  if(!std::isfinite(viewPitch)){move=botcore::CecilMotion();return;}
  if(player->m_pstState==PST_DIVE||viewPitch<=-30)leveling=true;
  if(std::fabs(viewPitch)<=1e-6)leveling=false;
  // Level before forward input instead of guessing private composer gains.
  // Nominally <=0.5s at 180deg/s; actual view pitch remains the gate if combat
  // arbitration postpones these actions. Once started, swimming levels fully.
  if(leveling&&std::fabs(back)>1e-6){
    back=0;move.pitch_delta=botcore::TestTurnDelta(viewPitch,0,180*dt);
  }
  const double scale=std::fmax(1,std::fmax(std::fabs(side),std::fmax(std::fabs(up),std::fabs(back))));
  move.active=true;move.forward=-back/scale;move.strafe=side/scale;move.up=up/scale;
  if(std::fabs(local.x)+std::fabs(local.z)>1e-6)
    move.yaw_delta=botcore::TestTurnDelta(yaw,std::atan2(-local.x,-local.z)*180/3.141592653589793,180*dt);
}
// The pure navigator reports its source when an UNREACHABLE next hop requests stay.
// Recover that concrete hop using the same prepared directed search, without allocation.
static int BotCecilTravelHop(SSupplyState& state,const botcore::CecilMotion& move,const FLOAT3D& position,const FLOAT3D& gravity){
  const auto& graph=BotSupplyGraph();int hop=move.hop;
  if(hop<0||hop>=(int)graph.points.size())return -1;
  if(!state.importantGoal&&move.forward==0&&move.strafe==0&&move.up==0){
    const auto& source=graph.points[hop];const double x=source.x-position(1),y=source.y-position(2),z=source.z-position(3),r=source.radius;
    const double ox=x-gravity(1)*r*.5,oy=y-gravity(2)*r*.5,oz=z-gravity(3)*r*.5;
    if(x*x+y*y+z*z<r*r||ox*ox+oy*oy+oz*oz<r*r){
      if(state.goals.Run(graph,hop,state.blocked.data(),state.blocked.size())){
        const int next=state.goals.NextHop(state.goal);
        if(next>=0&&next!=hop&&(graph.points[next].flags&botcore::CECIL_UNREACHABLE))hop=next;
      }
    }
  }
  return hop;
}
// Mirror only the read-side relay in original Player.es UsePressed.
// A normal PLACT_USE action performs the interaction; no entity events are sent here.
static CSwitch* BotCecilUsableSwitch(CEntity* entity){
  if(!entity||(entity->GetFlags()&ENF_DELETED))return nullptr;
  if(BotCecilIsClass(entity,"MovingBrush","Moving Brush")){
    entity=static_cast<CMovingBrush*>(entity)->m_penSwitch;
    if(!entity||(entity->GetFlags()&ENF_DELETED))return nullptr;
  }
  if(!BotCecilIsClass(entity,"Switch","Switch"))return nullptr;
  CSwitch* target=static_cast<CSwitch*>(entity);return target->m_bUseable?target:nullptr;
}
static void BotCecilFinishImportant(SSupplyState& state,INDEX slot,INDEX tick,double now,const char* reason){
  const int old=state.goal;
  const auto& point=BotSupplyGraph().points[old];const int next=point.next_slot;
  BotLog("[CecilInteraction] local=%d tick=%d node=%d entity=%d action=%s\n",slot,tick,old,point.important_entity,reason);
  state.ClearGoal();state.scanTick=0;
  if(next>=0&&next<(int)BotSupplyGraph().points.size()&&next!=old){
    state.goal=next;state.goalSince=now;state.importantGoal=true;
  }else{state.avoidNode=old;state.avoidUntil=now+10;}
}
static bool BotCecilImportant(CPlayer* player,SSupplyState& state,INDEX slot,INDEX tick,double now,
                              const botcore::CecilMotionInput& in,SCecilMove& out){
  const auto& point=BotSupplyGraph().points[state.goal];
  if(point.important_entity<0)return false;
  if(state.interactionPoint!=state.goal){state.interactionPoint=state.goal;state.interactionSince=now;}
  out.active=true;out.useControl=true;
  if(now<state.interactionSince||now-state.interactionSince+1e-9>=5){
    BotCecilFinishImportant(state,slot,tick,now,"timeout");return true;
  }
  if(!in.frame.Valid()||!BotCecilFrameReady(player)){
    out.active=false;return true;
  }
  CEntity* entity=player->GetWorld()->EntityFromID((ULONG)point.important_entity);
  if(!entity||(entity->GetFlags()&ENF_DELETED)){
    BotCecilFinishImportant(state,slot,tick,now,"unavailable");return true;
  }
  if(BotCecilIsClass(entity,"Marker","Marker")||entity->IsMarker()){
    CEntity* target=entity->GetTarget();
    if(!target||(target->GetFlags()&ENF_DELETED)){
      BotCecilFinishImportant(state,slot,tick,now,"marker_no_target");return true;
    }
    if(_botRayBudget<=2)return true;
    const int goal=BotSupplyNearest(player,target->GetPlacement().pl_PositionVector,FALSE,target);
    BotCecilLocks(player,state,now);
    state.goals.Run(BotSupplyGraph(),state.anchor,state.blocked.data(),state.blocked.size());
    if(goal>=0&&goal!=state.goal&&std::isfinite(state.goals.Distance(goal))){
      BotLog("[CecilInteraction] local=%d tick=%d node=%d entity=%d action=marker_target target=%d\n",
        slot,tick,state.goal,point.important_entity,goal);
      state.goal=goal;state.goalSince=now;state.importantGoal=true;state.navigator.Reset();
      state.interactionPoint=-1;state.interactionSince=-1;state.scanTick=tick+20;
    }
    // An unresolved or same-node marker is bounded by the attempt deadline.
    return true;
  }
  CSwitch* target=BotCecilUsableSwitch(entity);
  if(!target){BotCecilFinishImportant(state,slot,tick,now,"not_usable");return true;}
  if(state.lastUseEntity==target->en_ulID&&now<state.useAfter){
    BotCecilFinishImportant(state,slot,tick,now,"use_cooldown");return true;
  }
  CPlayerWeapons* weapons=player->GetPlayerWeapons();
  const double hitDistance=weapons->m_fRayHitDistance;
  if(BotCecilUsableSwitch(weapons->m_penRayHit)==target&&
     std::isfinite(hitDistance)&&hitDistance>=0&&hitDistance<2){
    out.buttons=1u<<5;state.useReleaseTick=tick+1; // Retail PLACT_USE, not sniper-only bit12.
    state.lastUseEntity=target->en_ulID;state.useAfter=now+5;
    BotCecilFinishImportant(state,slot,tick,now,"use_action");return true;
  }
  const FLOAT3D position=entity->GetPlacement().pl_PositionVector;
  const FLOAT3D delta=position-player->GetPlacement().pl_PositionVector;
  if(!std::isfinite(position(1))||!std::isfinite(position(2))||!std::isfinite(position(3))||delta.Length()>8){
    BotCecilFinishImportant(state,slot,tick,now,"out_of_range");return true;
  }
  const CPlacement3D eye=BotCombatEye(player);
  const FLOAT3D aimDelta=position-eye.pl_PositionVector;
  const auto localAim=in.frame.ToLocal(aimDelta(1),aimDelta(2),aimDelta(3));
  const auto aim=botcore::AimAt(localAim.x,localAim.y,localAim.z);
  out.yaw_delta=botcore::TestTurnDelta(in.yaw,aim.yaw_deg,180*in.dt);
  out.pitch_delta=botcore::TestTurnDelta(player->en_plViewpoint.pl_OrientationAngle(2),aim.pitch_deg,180*in.dt);
  if(delta.Length()>.75&&std::fabs(std::remainder(aim.yaw_deg-in.yaw,360.0))<50&&
     BotSupplyClear(player,eye.pl_PositionVector,position,entity)){
    out.forward=.5*BotCecilSettings().fSpeedMul;
    if(BotCecilLiquid(player)){
      botcore::CecilMotion swim;BotCecilSwimMotion(player,delta,in.yaw,in.dt,swim,state.levelSwimView);
      out.forward=swim.forward*.5*BotCecilSettings().fSpeedMul;
      out.strafe=BotCecilSettings().bStrafe?swim.strafe*.5*BotCecilSettings().fSpeedMul:0;out.up=swim.up*.5;
      if(swim.pitch_delta!=0)out.pitch_delta=swim.pitch_delta;
    }
  }
  return true;
}
static SCecilMove BotSupplyTick(CPlayer *player,INDEX slot,INDEX tick,double enemyDistance,const SCecilFollowGoal* follow=nullptr){
  SCecilMove result;SSupplyState &s=BotSupplyState(slot);s.currentNavTime=-1;s.currentNavGoal=-1;result.useControl=tick<=s.useReleaseTick;
  const double now=tick*_pTimer->TickQuantum;const bool alive=player&&player->GetHealth()>0&&player->m_penWeapons!=NULL;
  if(!alive){if(s.playable){BotCecilGoalEnd(slot,tick,s,"death");++s.deaths;s.deadSince=now;}s.playable=false;s.levelSwimView=false;s.ClearGoal();s.ClearEscape();return result;}
  if(!BotCecilFrameReady(player)||!std::isfinite(player->en_plViewpoint.pl_OrientationAngle(2)))return result;
  if(result.useControl)return result; // Preserve a released action even across chained switches.
  if(!s.playable){++s.respawns;s.spawnTick=tick;s.scanTick=0;s.ClearGoal();s.searchAfter=0;s.owned=0;s.ClearRejections();s.ClearAvoidance();s.ResetLockSnapshot();++s.generation;}
  s.playable=true;s.entity=player->en_ulID;
  if(!BotCecilLiquid(player))s.levelSwimView=false;
  CPlayerWeapons* weapons=player->GetPlayerWeapons();uint32_t owned=(uint32_t)weapons->m_iAvailableWeapons;
  if(s.owned&&(owned&~s.owned)){
    ++s.pickups;const FLOAT3D pos=player->GetPlacement().pl_PositionVector;
    const bool goalPicked=s.goalEntity&&BotCecilWeaponGoalPicked(player,player->GetWorld()->EntityFromID(s.goalEntity));
    BotLog("[CecilPickup] local=%d tick=%d old=%lu owned=%lu current=%d goal_entity=%lu goal_picked=%d pos=(%.3f,%.3f,%.3f)\n",
      slot,tick,(unsigned long)s.owned,(unsigned long)owned,weapons->m_iCurrentWeapon,(unsigned long)s.goalEntity,goalPicked,
      (double)pos(1),(double)pos(2),(double)pos(3));
  }
  s.owned=owned;
  const auto input=BotCecilItemInput(player,s,enemyDistance);
  const bool followValid=BotCecilFollowValid(follow,now)&&
    !(s.avoidFollowEntity==follow->entity&&now<s.avoidUntil);
  if(s.followEntity&&(!followValid||s.followEntity!=follow->entity||s.followGeneration!=follow->generation)){
    s.ClearGoal();s.scanTick=0;
  }
  bool urgent=false;
  if(s.goalEntity){
    CEntity* entity=player->GetWorld()->EntityFromID(s.goalEntity);botcore::CecilItem item;
    bool usable=entity&&BotCecilReadItem(player,entity,s.generation,owned,&item);
    if(usable){item.visible=item.reachable=true;usable=botcore::CecilChooseItem(&item,1,input)==0;}
    if(!usable||now<s.goalSince||now-s.goalSince>=12){
      BotCecilGoalEnd(slot,tick,s,usable?"timeout":"unavailable");
      if(usable)s.RejectItem(s.goalEntity,now);
      s.ClearGoal();s.searchAfter=now;s.scanTick=0;
    }else{s.goalKind=item.kind;urgent=BotCecilUrgentItem(item,input);}
  }
  if(tick>=s.scanTick){BotCecilChooseGoal(player,slot,tick,enemyDistance,!followValid);s.scanTick=tick+20;}
  if(followValid)BotCecilFollow(player,s,*follow,now);
  if(s.anchor<0||s.goal<0||s.goal>=(int)BotSupplyGraph().points.size())return result;
  // Refresh the typed result after a new selection in this tick.
  if(s.goalEntity){
    CEntity* entity=player->GetWorld()->EntityFromID(s.goalEntity);botcore::CecilItem item;
    if(!entity||!BotCecilReadItem(player,entity,s.generation,owned,&item)){BotCecilGoalEnd(slot,tick,s,"unavailable");s.ClearGoal();s.scanTick=0;return result;}
    s.goalKind=item.kind;urgent=BotCecilUrgentItem(item,input);
  }
  result.followGoal=s.followEntity!=0;result.itemGoal=s.goalEntity!=0;result.urgent=result.itemGoal&&urgent;result.itemKind=s.goalKind;
  if(enemyDistance<8&&!(result.urgent&&result.itemKind==botcore::CecilItemKind::Health))return result;
  BotCecilLocks(player,s,now);
  const FLOAT3D p=player->GetPlacement().pl_PositionVector;
  botcore::CecilMotionInput in;in.x=p(1);in.y=p(2);in.z=p(3);in.yaw=player->en_plViewpoint.pl_OrientationAngle(1);in.frame=BotCecilBodyFrame(player);
  for(int j=0;j<3;++j)in.gravity[j]=player->en_vGravityDir(j+1);
  in.now=now;in.dt=_pTimer->TickQuantum;in.anchor=s.anchor;in.goal=s.goal;in.slot=slot+bot_iRosterOffset;
  in.alive=true;in.allow_jump=BotCecilSettings().bJump!=0;
  const auto& point=BotSupplyGraph().points[s.goal];
  if(!s.goalEntity&&!s.followEntity&&(point.important_entity>=0||(point.flags&botcore::CECIL_IMPORTANT)))s.importantGoal=true;
  in.important_goal=s.importantGoal;
  auto move=s.navigator.Update(BotSupplyGraph(),s.blocked.data(),s.blocked.size(),in);s.hop=move.hop;
  if(move.active||move.arrived){s.currentNavGoal=s.goal;s.currentNavTime=now;}
  if(!s.goalEntity&&!s.followEntity&&s.importantGoal&&(move.arrived||s.interactionPoint>=0)&&
     BotCecilImportant(player,s,slot,tick,now,in,result))return result;
  if(move.active&&!move.arrived){
    const int travelHop=BotCecilTravelHop(s,move,p,player->en_vGravityDir);
    if(travelHop>=0&&BotCecilLiquid(player)){
      const auto& target=BotSupplyGraph().points[travelHop];
      BotCecilSwimMotion(player,FLOAT3D(target.x,target.y,target.z)-p,in.yaw,in.dt,move,s.levelSwimView);
      s.hop=travelHop;
    }
    if(travelHop>=0&&move.forward==0&&move.strafe==0&&move.up==0&&move.pitch_delta==0){
      if(s.heldNode!=travelHop||s.holdSince<0||now<s.holdSince){s.heldNode=travelHop;s.holdSince=now;}
      if(now-s.holdSince+1e-9>=2){
        BotCecilGoalEnd(slot,tick,s,"unreachable_hold");s.RejectItem(s.goalEntity,now);
        s.avoidNode=travelHop;s.avoidUntil=now+10;s.avoidFollowEntity=s.followEntity;
        s.ClearGoal();s.searchAfter=now;s.scanTick=0;result=SCecilMove();result.useControl=tick<=s.useReleaseTick;return result;
      }
    }else{s.heldNode=-1;s.holdSince=-1;}
  }else{s.heldNode=-1;s.holdSince=-1;}
  if(move.arrived){
    if(s.goalEntity){
      CEntity* item=player->GetWorld()->EntityFromID(s.goalEntity);
      // No query budget is not proof of a bad connector; wait without movement.
      if(_botRayBudget<=2)return result;
      const FLOAT3D delta=item?item->GetPlacement().pl_PositionVector-p:FLOAT3D(0,0,0);
      if(!item||std::fabs(BotCecilHeight(player,delta))>3||delta.Length()>8||
         !BotSupplyClear(player,BotCombatEye(player).pl_PositionVector,item->GetPlacement().pl_PositionVector-player->en_vGravityDir*.5f,item)){
        BotCecilGoalEnd(slot,tick,s,"connector");s.RejectItem(s.goalEntity,now);s.ClearGoal();s.searchAfter=now;s.scanTick=0;result=SCecilMove();result.useControl=tick<=s.useReleaseTick;return result;
      }
      const auto local=in.frame.ToLocal(delta(1),delta(2),delta(3));
      const double yaw=std::atan2(-local.x,-local.z)*180/3.141592653589793;
      move.active=true;move.yaw_delta=botcore::TestTurnDelta(in.yaw,yaw,180*in.dt);
      move.forward=std::fabs(std::remainder(yaw-in.yaw,360.0))<50?1:.1;
      if(BotCecilLiquid(player))BotCecilSwimMotion(player,delta,in.yaw,in.dt,move,s.levelSwimView);
    }else if(!s.followEntity){
      const int next=point.next_slot;
      if(next>=0&&next<(int)BotSupplyGraph().points.size()){
        s.goal=next;s.goalSince=now; // Keep original important-route context across untagged chain nodes.
      }else s.ClearGoal();
      s.scanTick=0;s.navigator.Reset();
    }
  }
  result.active=move.active;result.forward=move.forward*BotCecilSettings().fSpeedMul;
  result.strafe=BotCecilSettings().bStrafe?move.strafe*BotCecilSettings().fSpeedMul:0;
  result.up=move.up;result.yaw_delta=move.yaw_delta;result.pitch_delta=move.pitch_delta;result.flags=move.flags;
  return result;
}
// Record only results from existing casts. Metadata always describes the last
// rejection; primaryReason is the first rejected requested/held action this call.
static void BotCecilRejectedProbe(SCecilProbe* probe,int reason,const CPlayer* player,
    const CCastRay* ray=NULL,const FLOAT3D* from=NULL,const FLOAT3D* to=NULL){
  if(!probe)return;
  if(probe->primaryReason==SCecilProbe::reasonNone)probe->primaryReason=reason;
  probe->lastReason=reason;probe->reasonMask|=1u<<reason;
  probe->hitEntity=0;probe->renderType=-1;probe->support=0;
  for(int i=0;i<3;++i){probe->normal[i]=0;probe->from[i]=from?(*from)(i+1):0;probe->to[i]=to?(*to)(i+1):0;}
  if(!ray)return;
  if(ray->cr_penHit){probe->hitEntity=ray->cr_penHit->en_ulID;probe->renderType=(int)ray->cr_penHit->GetRenderType();}
  if(ray->cr_pbpoBrushPolygon&&ray->cr_pbpoBrushPolygon->bpo_pbplPlane){
    const auto& normal=ray->cr_pbpoBrushPolygon->bpo_pbplPlane->bpl_plAbsolute;
    for(int i=0;i<3;++i){probe->normal[i]=normal(i+1);probe->support-=normal(i+1)*player->en_vGravityDir(i+1);}
  }
}
// Explicit support probe. Original CheckPit uses WouldFallInNextPosition with
// step-down16; this read-only 5/10m ray remains a conservative off-graph adapter,
// not equivalent physics. SafeMotion applies the original bAvoidPits/current-point gate.
// finalBodyYaw is current local head yaw plus the emitted yaw delta, never world yaw.
static bool BotCecilFloor(CPlayer *player,double forward,double strafe,double up,double finalBodyYaw,SCecilProbe* probe=NULL){
  if(!BotCecilFrameReady(player)||!std::isfinite(forward)||!std::isfinite(strafe)||
     !std::isfinite(up)||!std::isfinite(finalBodyYaw)||std::fabs(forward)>1.000001||
     std::fabs(strafe)>1.000001||std::fabs(up)>1.000001){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  const FLOAT3D base=player->GetPlacement().pl_PositionVector;
  if(!std::isfinite(base(1))||!std::isfinite(base(2))||!std::isfinite(base(3))){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  if(BotCecilLiquid(player)||(forward==0&&strafe==0))return true;
  if(_botRayBudget<=0){BotCecilRejectedProbe(probe,SCecilProbe::reasonBudget,player);return false;}
  --_botRayBudget;if(probe)++probe->floorRays;
  const double yaw=finalBodyYaw*3.141592653589793/180;
  const auto offset=BotCecilBodyFrame(player).ToWorld(-std::sin(yaw)*forward+std::cos(yaw)*strafe,0,
    -std::cos(yaw)*forward-std::sin(yaw)*strafe);
  const FLOAT3D from=base+FLOAT3D((FLOAT)offset.x,(FLOAT)offset.y,(FLOAT)offset.z)*(up>0?3.0f:1.5f)-player->en_vGravityDir;
  const FLOAT3D to=from+player->en_vGravityDir*(up>0?10.0f:5.0f);
  CCastRay ray(player,from,to);
  ray.cr_bPhysical=TRUE;ray.cr_bAllowOverHit=FALSE;ray.cr_ttHitModels=CCastRay::TT_NONE;ray.Cast(player->GetWorld());
  if(!ray.cr_penHit){BotCecilRejectedProbe(probe,SCecilProbe::reasonNoFloor,player,&ray,&from,&to);return false;}
  if(ray.cr_penHit->GetRenderType()==CEntity::RT_TERRAIN)return true;
  const CBrushPolygon* polygon=ray.cr_pbpoBrushPolygon;
  if(!polygon||(polygon->bpo_ulFlags&BPOF_PASSABLE)||!polygon->bpo_pbplPlane){
    const int reason=polygon&&(polygon->bpo_ulFlags&BPOF_PASSABLE)?SCecilProbe::reasonPassable:SCecilProbe::reasonUnsupportedNormal;
    BotCecilRejectedProbe(probe,reason,player,&ray,&from,&to);return false;
  }
  const auto& normal=polygon->bpo_pbplPlane->bpl_plAbsolute;
  const double support=-(normal(1)*player->en_vGravityDir(1)+normal(2)*player->en_vGravityDir(2)+normal(3)*player->en_vGravityDir(3));
  if(!(support>.5))BotCecilRejectedProbe(probe,SCecilProbe::reasonUnsupportedNormal,player,&ray,&from,&to);
  return support>.5;
}
// Test the exact bounded action in the body/head frame before its floor probe.
static bool BotCecilClearMotion(CPlayer* player,double forward,double strafe,double up,double yaw,SCecilProbe* probe=NULL,bool requireFloor=true){
  const bool liquid=BotCecilLiquid(player);
  if(forward==0&&strafe==0&&(!liquid||up==0))
    return BotCecilFloor(player,forward,strafe,up,yaw,probe);
  if(_botRayBudget<((liquid||!requireFloor)?1:2)){BotCecilRejectedProbe(probe,SCecilProbe::reasonBudget,player);return false;}
  --_botRayBudget;if(probe)++probe->wallRays;
  const double angle=yaw*3.141592653589793/180;
  const auto world=BotCecilBodyFrame(player).ToWorld(-std::sin(angle)*forward+std::cos(angle)*strafe,
    liquid?up:0,-std::cos(angle)*forward-std::sin(angle)*strafe);
  const FLOAT3D from=player->GetPlacement().pl_PositionVector-player->en_vGravityDir*.8f;
  const FLOAT3D to=from+FLOAT3D((FLOAT)world.x,(FLOAT)world.y,(FLOAT)world.z)*1.5f;
  CCastRay ray(player,from,to);ray.cr_bPhysical=TRUE;ray.cr_bAllowOverHit=FALSE;
  ray.cr_ttHitModels=CCastRay::TT_COLLISIONBOX;ray.Cast(player->GetWorld());
  if(ray.cr_penHit){BotCecilRejectedProbe(probe,SCecilProbe::reasonWallHit,player,&ray,&from,&to);return false;}
  return !requireFloor||BotCecilFloor(player,forward,strafe,up,yaw,probe);
}
// 1 original, 2 verified escape, 0 neutral. Hold world direction for 0.6s so a
// one-tick reverse does not immediately undo itself. No progress earns a cooldown.
template<class T>
static int BotCecilSafeMotion(CPlayer* player,SSupplyState& state,double now,T& forward,T& strafe,T& up,
                             double finalBodyYaw,double maxStrafe){
  state.probe=SCecilProbe();state.probe.inputForward=forward;state.probe.inputStrafe=strafe;
  state.probe.inputUp=up;state.probe.finalYaw=finalBodyYaw;
  if(!BotCecilFrameReady(player)||!std::isfinite(now)||now<0||!std::isfinite(maxStrafe)||maxStrafe<0||maxStrafe>1||
     !std::isfinite(forward)||!std::isfinite(strafe)||!std::isfinite(up)||!std::isfinite(finalBodyYaw)||
     std::fabs(forward)>1.000001||std::fabs(strafe)>1.000001||std::fabs(up)>1.000001){
    BotCecilRejectedProbe(&state.probe,SCecilProbe::reasonInvalid,player);
    forward=strafe=up=0;state.ClearEscape();return 0;
  }
  // Cecil BotMovement.cpp517: pits are opt-in and checked only without a
  // current path point. Arrival still owns that point for the final item connector.
  // Clear/reset/failed updates and changed goals must never retain an exemption.
  const size_t nodes=BotSupplyGraph().points.size();
  const bool currentPoint=std::fabs(now-state.currentNavTime)<=1e-6&&state.currentNavGoal==state.goal&&state.goal>=0&&(size_t)state.goal<nodes&&
    state.hop>=0&&(size_t)state.hop<nodes&&state.blocked.size()==nodes&&!state.blocked[state.hop];
  const bool requireFloor=BotCecilSettings().bAvoidPits&&!BotCecilLiquid(player)&&!currentPoint;
  if(now<state.escapeClock)state.ClearEscape();
  state.escapeClock=now;
  strafe=(T)std::fmax(-maxStrafe,std::fmin(maxStrafe,(double)strafe));
  if(std::fabs(forward)+std::fabs(strafe)+std::fabs(up)<.05){
    state.escapeUntil=0;forward=strafe=up=0;return 1;
  }
  const auto frame=BotCecilBodyFrame(player);
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  const double angle=finalBodyYaw*3.141592653589793/180,si=std::sin(angle),co=std::cos(angle);
  const double requestedLength=std::hypot((double)forward,(double)strafe);
  const auto requested=frame.ToWorld(-si*forward+co*strafe,0,-co*forward-si*strafe);
  if(state.escapeReverseUsed&&requestedLength>.05){
    double progress=0;for(int i=0;i<3;++i)progress+=(position(i+1)-state.escapeBlockPosition[i])*state.escapeRequest[i];
    const double alignment=(requested.x*state.escapeRequest[0]+requested.y*state.escapeRequest[1]+requested.z*state.escapeRequest[2])/requestedLength;
    if(progress>2||alignment<.5)state.escapeReverseUsed=false;
  }
  if(state.escapeUntil>0){
    if(now+1e-9<state.escapeUntil){
      const auto local=frame.ToLocal(state.escapeWorld[0],state.escapeWorld[1],state.escapeWorld[2]);
      const double f=-si*local.x-co*local.z;
      const double st=std::fmax(-maxStrafe,std::fmin(maxStrafe,co*local.x-si*local.z));
      if(std::fabs(f)+std::fabs(st)>.05&&BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,requireFloor)){
        forward=(T)f;strafe=(T)st;up=0;return 2;
      }
      state.escapeUntil=0;state.escapeAfter=now+.3;
      forward=strafe=up=0;return 0;
    }
    double distance=0;
    for(int i=0;i<3;++i){const double d=position(i+1)-state.escapeOrigin[i];distance+=d*d;}
    state.escapeUntil=0;
    if(distance<.0225){state.escapeAfter=now+1;state.escapeSide=-state.escapeSide;}
  }
  if(BotCecilClearMotion(player,forward,strafe,up,finalBodyYaw,&state.probe,requireFloor))return 1;
  if(now<state.escapeAfter){forward=strafe=up=0;return 0;}
  const double length=std::hypot((double)forward,(double)strafe);
  const double side=std::fmin(.4,maxStrafe)*state.escapeSide;
  const double candidates[3][2]={{0,side},{0,-side},{length>.05?-.4*forward/length:0,length>.05?-.4*strafe/length:0}};
  for(int i=0;i<3;++i){
    if(i==2&&state.escapeReverseUsed)continue;
    const double f=candidates[i][0],st=std::fmax(-maxStrafe,std::fmin(maxStrafe,candidates[i][1]));
    if(std::fabs(f)+std::fabs(st)<.05)continue;
    if(BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,requireFloor)){
      // One retreat per blocked approach; retry only after forward progress or
      // a new world heading. Strafe-disabled bots cannot oscillate indefinitely.
      if(i==2){
        state.escapeReverseUsed=true;
        for(int j=0;j<3;++j)state.escapeBlockPosition[j]=position(j+1);
        state.escapeRequest[0]=requested.x/requestedLength;
        state.escapeRequest[1]=requested.y/requestedLength;state.escapeRequest[2]=requested.z/requestedLength;
      }
      const auto world=frame.ToWorld(-si*f+co*st,0,-co*f-si*st);
      state.escapeWorld[0]=world.x;state.escapeWorld[1]=world.y;state.escapeWorld[2]=world.z;
      for(int j=0;j<3;++j)state.escapeOrigin[j]=position(j+1);
      state.escapeUntil=now+.6;forward=(T)f;strafe=(T)st;up=0;return 2;
    }
  }
  state.escapeAfter=now+.3;forward=strafe=up=0;return 0;
}
#endif
