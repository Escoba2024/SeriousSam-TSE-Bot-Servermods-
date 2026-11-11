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
  // Diagnostic clocks are not consulted by any decision or movement gate.
  double diagSelectionLast=-1,diagUnavailableLast=-1,diagTerminalLast=-1;
  botcore::CecilNavigator navigator;
  botcore::CecilGroundProgress groundProgress;
  // Observation and default-policy movement context never substitute for the
  // separate current-support stamp used by opt-in floor/contact authorization.
  double groundRecoveryTime=-1,groundObservationTime=-1,recoveryMovementTime=-1,groundEscapeAfter=0;
  uint32_t groundProgressEntity=0,groundProgressGeneration=0;
  double airMovementTime=-1,airMovementGravity[3]={0,0,0};
  uint32_t airMovementEntity=0,airMovementGeneration=0;
  int airMovementNode=-1; // Original hint only; never an anchor or support stamp.
  unsigned groundEscapeTried=0;
  unsigned groundEscapeCursor=0;
  bool groundSweepReady=false,groundSweepBodyOnly=false;
  double groundSweepForward[3]={0,0,0},groundSweepRight[3]={0,0,0};
  bool groundStalled=false,groundEscapeActive=false;
  botcore::CecilNavSearch goals;
  botcore::CecilNavSearch patrolSearch; // Prepared separately: ordinary goal scans overwrite goals.
  CWorld* patrolWorld=NULL;
  long patrolMap=-1;
  uint32_t patrolEntity=0,patrolGeneration=0;
  int patrolGoal=-1,patrolSource=-1,patrolHop=-1,patrolHint=-1;
  double patrolLast=-1,patrolBest=0,patrolGainBase=0,patrolGravity[3]={0,0,0};
  double patrolSince=-1,patrolProposalTime=-1;
  unsigned patrolStrikes=0;bool patrolAlternate=false;
  uint64_t patrolLocks=0;
  unsigned char patrolTried[(botcore::CecilNavGraph::kMaxPoints+7)/8]={0};
  std::vector<unsigned char> blocked,worldLock; // 0 open, 1 moved, 2 missing, 3 unseen.
  uint32_t entity=0,generation=0,rng=1,goalEntity=0,owned=0,followEntity=0,followGeneration=0;
  // Passive edge progress survives ground-reference flicker. A checkpoint
  // still needs a currently authorized static-ground acquisition below.
  double acquiredAnchorTime=-1;int acquiredAnchor=-1; // Same-tick ordinary nearest LOS, not support.
  double hopCheckpointLast=-1,hopCheckpointSince=-1,hopCheckpointBest=0,hopCheckpointGainBase=0;
  double hopCheckpointGravity[3]={0,0,0};
  int hopCheckpointGoal=-1,hopCheckpointSource=-1,hopCheckpointHop=-1;
  uint32_t hopCheckpointEntity=0,hopCheckpointGeneration=0;
  CWorld* hopCheckpointWorld=NULL;
  // Passive extended-item attempt bound. Never authorizes movement or rebases NAV.
  CWorld* itemTransitWorld=NULL;
  long itemTransitMap=-1;
  uint32_t itemTransitEntity=0,itemTransitGeneration=0,itemTransitItem=0;
  int itemTransitGoal=-1,itemTransitSource=-1,itemTransitHop=-1;
  double itemTransitLast=-1,itemTransitSince=-1,itemTransitBest=0,itemTransitGainBase=0;
  double itemTransitAttempt=0,itemTransitDeadline=0,itemTransitGravity[3]={0,0,0};
  bool currentNavTravel=false; // Active edge, not arrival connector or intentional recovery.
  double currentNavTime=-1;
  int currentNavGoal=-1; // Fresh navigator context; an anchor/old hop alone is not a current point.
  int goal=-1,anchor=-1,hop=-1,spawnTick=0,scanTick=0,itemScanAfter=0,avoidNode=-1,heldNode=-1;
  double searchAfter=0,goalSince=0,goalDeadline=0,deadSince=-1,followAfter=0,avoidUntil=0,holdSince=-1;
  uint32_t avoidFollowEntity=0,lastUseEntity=0;
  int interactionPoint=-1,useReleaseTick=-1;
  int reacquireNode=-1,reacquireRejected=-1;
  double reacquireSince=-1,reacquireRetryAfter=0;
  // One bit per original node keeps failed LOS/final-floor approaches from
  // monopolizing subsequent three-cast batches. Separate from target backoff.
  unsigned char reacquireTried[(botcore::CecilNavGraph::kMaxPoints+7)/8]={0};
  double reacquireScanTime=-1,reacquireScanPosition[3]={0,0,0},reacquireScanGravity[3]={0,0,0};
  bool reacquireScanLiquid=false;
  double interactionSince=-1,useAfter=0;
  double escapeUntil=0,escapeAfter=0,escapeClock=-1,escapeWorld[3]={0,0,0},escapeOrigin[3]={0,0,0};
  int escapeSide=1;
  bool escapeReverseUsed=false;
  double escapeBlockPosition[3]={0,0,0},escapeRequest[3]={0,0,0};
  bool playable=false,hadUpgrade=false,importantGoal=false,levelSwimView=false,mappedWeaponGoal=false,reacquiring=false,goalRelocationBudgeted=false;
  botcore::CecilItemKind goalKind=botcore::CecilItemKind::Weapon;
  // 256 fixed records cover eight rejects/second for the thirty-second TTL.
  struct Rejection {uint32_t id=0;double until=0;bool localOnly=false;} rejected[256];
  unsigned deaths=0,respawns=0,pickups=0;
  bool ItemRejected(uint32_t id,double now,bool includeLocal=true)const{
    for(const auto& r:rejected)if(r.id==id&&now<r.until&&(includeLocal||!r.localOnly))return true;
    return false;
  }
  void RejectItem(uint32_t id,double now,bool localOnly=false){
    if(!id)return;
    size_t victim=0;
    for(size_t i=0;i<256;++i){
      if(rejected[i].id==id){victim=i;break;}
      if(rejected[i].until<rejected[victim].until)victim=i;
    }
    rejected[victim].id=id;rejected[victim].until=now+30;rejected[victim].localOnly=localOnly;
  }
  void ClearRejections(){for(auto& r:rejected)r=Rejection();}
  void ClearReacquireScan(){std::fill(reacquireTried,reacquireTried+sizeof(reacquireTried),0);reacquireScanTime=-1;}
  void ClearAvoidance(){avoidNode=heldNode=reacquireNode=reacquireRejected=-1;avoidUntil=reacquireRetryAfter=0;holdSince=reacquireSince=-1;avoidFollowEntity=0;ClearReacquireScan();}
  void ClearHopCheckpoint(){hopCheckpointLast=hopCheckpointSince=-1;hopCheckpointGoal=hopCheckpointSource=hopCheckpointHop=-1;hopCheckpointEntity=hopCheckpointGeneration=0;hopCheckpointWorld=NULL;}
  void ClearItemTransit(){itemTransitWorld=NULL;itemTransitMap=-1;itemTransitEntity=itemTransitGeneration=itemTransitItem=0;
    itemTransitGoal=itemTransitSource=itemTransitHop=-1;itemTransitLast=itemTransitSince=-1;}
  void ClearPatrolEpisode(){patrolWorld=NULL;patrolMap=-1;patrolEntity=patrolGeneration=0;patrolGoal=patrolSource=patrolHop=patrolHint=-1;
    patrolLast=patrolSince=patrolProposalTime=-1;patrolStrikes=0;patrolAlternate=false;patrolLocks=0;
    std::fill(patrolTried,patrolTried+sizeof(patrolTried),0);}
  void ClearGoal(){acquiredAnchorTime=-1;acquiredAnchor=-1;ClearHopCheckpoint();ClearItemTransit();ClearPatrolEpisode();currentNavTime=-1;currentNavGoal=-1;currentNavTravel=false;interactionPoint=-1;interactionSince=-1;heldNode=-1;holdSince=-1;navigator.Reset();goal=-1;goalEntity=0;hop=-1;importantGoal=mappedWeaponGoal=goalRelocationBudgeted=false;goalDeadline=0;followEntity=followGeneration=0;followAfter=0;}
  void ClearEscape(){escapeUntil=escapeAfter=0;escapeClock=-1;escapeSide=1;escapeReverseUsed=false;}
  void ClearAirMovement(){airMovementTime=-1;airMovementEntity=airMovementGeneration=0;airMovementNode=-1;}
  void ClearGroundSweep(){groundEscapeTried=groundEscapeCursor=0;groundSweepReady=false;}
  void ClearGroundProgress(){if(groundEscapeActive)ClearEscape();groundProgress.Reset();groundRecoveryTime=groundObservationTime=recoveryMovementTime=-1;ClearGroundSweep();groundEscapeAfter=0;groundStalled=groundEscapeActive=false;groundProgressEntity=groundProgressGeneration=0;}
  void ResetLockSnapshot(){for(auto& value:worldLock)value=3;}
  void Reset() {
    diagSelectionLast=diagUnavailableLast=diagTerminalLast=-1;
    ClearAirMovement();ClearGroundProgress();probe=SCecilProbe();ClearGoal();ClearRejections();ClearAvoidance();ClearEscape();ResetLockSnapshot();entity=owned=0;anchor=-1;
    itemScanAfter=scanTick=spawnTick=0;searchAfter=goalSince=0;deadSince=-1;
    playable=hadUpgrade=levelSwimView=reacquiring=false;useReleaseTick=-1;lastUseEntity=0;useAfter=0;++generation;
  }
};
struct SCecilMove {
  bool active=false,ownsMovement=false,itemGoal=false,urgent=false,followGoal=false,useControl=false;
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
    prepared[i].navigator.Prepare(loaded.points.size());prepared[i].goals.Prepare(loaded.points.size());prepared[i].patrolSearch.Prepare(loaded.points.size());
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
// A matching current physics reference proves only occupancy of this approach,
// not arrival at the NAV point. The navigator validates its retained edge and
// newly observed lock transition; this helper never changes an anchor, lock or deadline.
static int BotCecilSupportedLockNode(CPlayer* player,const SSupplyState& state){
  if(!BotCecilFrameReady(player)||!player->GetWorld()||
     (player->m_pstState!=PST_STAND&&player->m_pstState!=PST_CROUCH)||
     !state.navigator.HasCommittedEdge(state.goal)||state.hop<0)return -1;
  const auto& graph=BotSupplyGraph();const size_t hop=(size_t)state.hop;
  if(hop>=graph.points.size()||hop>=state.worldLock.size()||state.worldLock[hop]!=1)return -1;
  const auto& point=graph.points[hop];
  if(point.lock_entity<0||!std::isfinite(point.radius)||point.radius<=0)return -1;
  CEntity* entity=player->GetWorld()->EntityFromID((ULONG)point.lock_entity);
  if(!entity||entity!=player->en_penReference||(entity->GetFlags()&ENF_DELETED)||
     entity->GetRenderType()!=CEntity::RT_BRUSH||!BotCecilIsClass(entity,"MovingBrush","Moving Brush"))return -1;
  const auto& position=player->GetPlacement().pl_PositionVector;
  const auto& placement=entity->GetPlacement();double distance2=0;
  for(int i=0;i<3;++i){
    if(!std::isfinite(player->en_vCurrentTranslationAbsolute(i+1))||
       !std::isfinite(placement.pl_PositionVector(i+1))||!std::isfinite(placement.pl_OrientationAngle(i+1)))return -1;
    const double coordinate=i==0?point.x:(i==1?point.y:point.z);
    const double delta=coordinate-position(i+1);distance2+=delta*delta;
  }
  const double limit=std::fmin(2.0,2.0*point.radius);
  return std::isfinite(distance2)&&distance2<=limit*limit?state.hop:-1;
}
static bool BotCecilRayLength(const FLOAT3D& from,const FLOAT3D& to,double& length){
  length=0;bool same=true;
  for(int i=1;i<=3;++i){
    if(!std::isfinite(from(i))||!std::isfinite(to(i)))return false;
    same=same&&from(i)==to(i);
  }
  if(same)return true;
  const FLOAT3D delta=to-from;
  for(int i=1;i<=3;++i)if(!std::isfinite(delta(i)))return false;
  length=delta.Length();return std::isfinite(length)&&length>0;
}
// Adapted from Dreamy Cecil, Copyright (c) 2018-2025, GPL-2.0-only:
// CecilBotMod 953b477e53fdc5a5d84c8ae8d759c84fdf6c973c,
// Sources/Bots/SandboxCommon.cpp:173-206, CastRayFlags.
// Retail107 Cast() overwrites a physical mask with PASSABLE|SHOOTTHRU.
// Movement must stop at nonpassable shoot-through geometry, including floors.
static bool BotCecilPhysicalCast(CCastRay& ray,CWorld* world){
  ray.cr_pbpoBrushPolygon=NULL;ray.cr_pbscBrushSector=NULL;ray.cr_penHit=NULL;
  ray.cr_ulPassablePolygons=BPOF_PASSABLE;ray.cr_bPhysical=TRUE;
  ray.cr_vHit=ray.cr_vOrigin;
  double length=0;
  if(!world||!BotCecilRayLength(ray.cr_vOrigin,ray.cr_vTarget,length))return false;
  if(length==0){ray.cr_fHitDistance=0;return true;} // Defined empty segment: no native query or Normalize.
  if(ray.cr_penOrigin!=NULL){ray.AddSectorsAroundEntity(ray.cr_penOrigin);ray.TestThroughSectors();}
  else ray.TestWholeWorld(world);
  if(!std::isfinite(ray.cr_fHitDistance)||ray.cr_fHitDistance<0)return false;
  ray.cr_vHit=ray.cr_vOrigin+(ray.cr_vTarget-ray.cr_vOrigin).Normalize()*ray.cr_fHitDistance;
  return true;
}
static BOOL BotSupplyClear(CPlayer *player,const FLOAT3D &from,const FLOAT3D &to,CEntity *item=NULL,bool* validProbe=NULL){
  if(validProbe)*validProbe=false;
  double length=0;
  if(!player||!player->GetWorld()||!BotCecilRayLength(from,to,length))return FALSE;
  // Reserve the final wall and floor probes for each action.
  if(_botRayBudget<=2)return FALSE;
  --_botRayBudget;
  if(length==0){if(validProbe)*validProbe=true;return TRUE;}
  CCastRay ray(player,from,to);ray.cr_bAllowOverHit=FALSE;ray.cr_bPhysical=TRUE;
  ray.cr_ttHitModels=CCastRay::TT_COLLISIONBOX;
  if(!BotCecilPhysicalCast(ray,player->GetWorld()))return FALSE;
  if(validProbe)*validProbe=true;
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
        state.ClearReacquireScan();
        BotLog("[CecilLock] node=%d entity=%d locked=%d present=%d player=%lu generation=%lu time=%.3f distance=%.4f angle=%.4f\n",
          (int)i,p.lock_entity,blocked,present,(unsigned long)player->en_ulID,(unsigned long)state.generation,now,std::sqrt(d),std::sqrt(a));
      }
    }
    blocked=blocked||(!state.importantGoal&&(int)i==state.avoidNode&&now<state.avoidUntil);
    if(state.blocked[i]!=(blocked?1:0))state.ClearReacquireScan();
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
// At most one selection batch, one unavailable row and one terminal row per
// second per local bot. No rays, entity lookups, search, heap allocation or RNG.
static bool BotCecilSupplyDiagDue(double now,double& last){
  if(!bot_bDiagnostics||!std::isfinite(now)||now<0)return false;
  if(last>=0&&now>=last&&now-last<1)return false;
  last=now;return true;
}
static void BotCecilSupplyDiagPath(const SSupplyState& s,int goal,int& firstFrom,int& firstTo,unsigned& flags){
  const auto& graph=BotSupplyGraph();firstFrom=firstTo=-1;flags=0;
  int child=goal;
  for(size_t step=0;step<graph.points.size()&&step<botcore::CecilNavGraph::kMaxPoints;++step){
    if(child<0||(size_t)child>=graph.points.size())return;
    const int parent=s.goals.Parent(child);
    if(parent<0||(size_t)parent>=graph.points.size())return;
    const auto& a=graph.points[parent];const auto& b=graph.points[child];
    // Union describes special path endpoints, not the effective movement flags.
    const unsigned endpointFlags=a.flags|b.flags;
    if((endpointFlags&(botcore::CECIL_JUMP|botcore::CECIL_CROUCH|botcore::CECIL_UNREACHABLE|botcore::CECIL_TELEPORT|botcore::CECIL_IMPORTANT))||
       a.lock_entity>=0||b.lock_entity>=0){firstFrom=parent;firstTo=child;flags=endpointFlags;}
    child=parent;
  }
}
static void BotCecilSupplyDiagUnavailable(CPlayer* player,SSupplyState& s,CEntity* entity,
    INDEX slot,INDEX tick,double now,const char* reason,const botcore::CecilItemInput& input){
  if(!BotCecilSupplyDiagDue(now,s.diagUnavailableLast))return;
  const int index=player->GetMyPlayerIndex();
  const bool weapon=entity&&!(entity->GetFlags()&ENF_DELETED)&&BotCecilIsClass(entity,"WeaponItem","Weapon Item");
  const CWeaponItem* item=weapon?static_cast<CWeaponItem*>(entity):nullptr;
  const unsigned mask=item?(unsigned)item->m_ulPickedMask:0;
  BotLog("[CecilSupplyDiagUnavailable] local=%d tick=%d generation=%lu entity=%lu reason=%s flags=%lu render=%d weapon_metadata_valid=%d player_index=%d picked_mask=%lu picked_for_player=%d pickup_once=%d dropped=%d respawn=%d raw_weapon_type=%d weapons_stay=%d current=%d owned=%lu usable=%lu mapped=%d since=%.3f deadline=%.3f\n",
    slot,tick,(unsigned long)s.generation,(unsigned long)s.goalEntity,reason,
    entity?(unsigned long)entity->GetFlags():0ul,entity?(int)entity->GetRenderType():-1,item?1:0,index,(unsigned long)mask,
    item&&index>=0&&index<16?(mask&(1u<<index))!=0:-1,item?(int)item->m_bPickupOnce:-1,item?(int)item->m_bDropped:-1,
    item?(int)item->m_bRespawn:-1,item?(int)item->m_EwitType:-1,
    (int)static_cast<const CSessionProperties*>(_pNetwork->GetSessionProperties())->sp_bWeaponsStay,player->GetPlayerWeapons()->m_iCurrentWeapon,
    (unsigned long)input.owned,(unsigned long)input.usable,(int)s.mappedWeaponGoal,s.goalSince,s.goalDeadline);
}
static void BotCecilSupplyDiagTerminal(CPlayer* player,SSupplyState& s,double now,bool accepted,bool currentPoint){
  const auto& graph=BotSupplyGraph();const int source=s.navigator.SourceSlot(s.goal),hop=s.hop;
  if(!bot_bDiagnostics||!s.goalEntity||hop!=s.goal||source<0||hop<0||
     (size_t)source>=graph.points.size()||(size_t)hop>=graph.points.size()||
     !BotCecilSupplyDiagDue(now,s.diagTerminalLast))return;
  const auto& a=graph.points[source];const auto& b=graph.points[hop];
  const auto& p=player->GetPlacement().pl_PositionVector;const auto& v=player->en_vCurrentTranslationAbsolute;
  const FLOAT3D delta(b.x-p(1),b.y-p(2),b.z-p(3));CEntity* ref=player->en_penReference;
  BotLog("[CecilSupplyDiagTerminal] entity=%lu generation=%lu time=%.3f goal_entity=%lu goal=%d source=%d hop=%d anchor=%d source_flags=%lu hop_flags=%lu accepted=%d current_point=%d nav_travel=%d state=%d support=%lu support_render=%d support_physics=%lu distance=%.6f height=%.6f velocity=(%.3f,%.3f,%.3f) gravity=(%.3f,%.3f,%.3f) acquired_time=%.3f use_point=%d use_release=%d since=%.3f deadline=%.3f\n",
    (unsigned long)player->en_ulID,(unsigned long)s.generation,now,(unsigned long)s.goalEntity,s.goal,source,hop,s.anchor,
    (unsigned long)a.flags,(unsigned long)b.flags,(int)accepted,(int)currentPoint,(int)s.currentNavTravel,(int)player->m_pstState,
    ref?(unsigned long)ref->en_ulID:0ul,ref?(int)ref->GetRenderType():-1,ref?(unsigned long)ref->GetPhysicsFlags():0ul,
    (double)delta.Length(),BotCecilHeight(player,delta),(double)v(1),(double)v(2),(double)v(3),
    (double)player->en_vGravityDir(1),(double)player->en_vGravityDir(2),(double)player->en_vGravityDir(3),
    s.acquiredAnchorTime,s.interactionPoint,s.useReleaseTick,s.goalSince,s.goalDeadline);
}
static bool BotCecilHasRanged(const botcore::CecilItemInput& input){
  const uint32_t ranged=0x3df8u; // IDs4..14, excluding melee10; independent of enemy range.
  const uint32_t allowed=input.settings.iAllowedWeapons==-1?0x3fffu:(uint32_t)input.settings.iAllowedWeapons;
  return (input.usable&allowed&ranged)!=0;
}
static bool BotCecilMappedWeaponNeeded(const botcore::CecilItem& item,const botcore::CecilItemInput& input){
  return item.kind==botcore::CecilItemKind::Weapon&&
    (botcore::CecilWeaponMask(item.weapon)&0x3df8u)&&botcore::CecilRetainItem(item,input);
}
static bool BotCecilMappedWeaponEligible(const botcore::CecilItem& item,const botcore::CecilItemInput& input){
  return !BotCecilHasRanged(input)&&BotCecilMappedWeaponNeeded(item,input);
}
static void BotCecilChooseMappedWeapon(CPlayer* player,SSupplyState& s,const botcore::CecilItemInput& input,
    INDEX slot,INDEX tick,double now){
  if(s.goalEntity||now<s.searchAfter||!std::isfinite(input.enemy_distance)||input.enemy_distance<8||
     !input.settings.bItemSearch||BotCecilHasRanged(input))return;
  const auto& graph=BotSupplyGraph();
  const bool diagnostics=BotCecilSupplyDiagDue(now,s.diagSelectionLast);
  // Only original mapped WeaponItem references supply remote item knowledge.
  // No enemy visibility or ordinary preset search distance is changed.
  for(int attempt=0;attempt<8&&_botRayBudget>2;++attempt){
    unsigned eligible=0,emitted=0;
    int best=-1;double bestScore=std::numeric_limits<double>::infinity(),bestCost=0;botcore::CecilItem chosen;
    for(size_t i=0;i<graph.points.size();++i){
      const auto& point=graph.points[i];if(point.important_entity<0||s.blocked[i]||!std::isfinite(s.goals.Distance((int)i)))continue;
      CEntity* entity=player->GetWorld()->EntityFromID((ULONG)point.important_entity);botcore::CecilItem item;
      if(!BotCecilReadItem(player,entity,s.generation,input.owned,&item)||s.ItemRejected(item.id,now,false)||
         !BotCecilMappedWeaponEligible(item,input))continue;
      const FLOAT3D connector((FLOAT)item.x-point.x,(FLOAT)item.y-point.y,(FLOAT)item.z-point.z);
      const double length=connector.Length();
      if(length>8||std::fabs(BotCecilHeight(player,connector))>3)continue;
      const double dx=graph.points[s.anchor].x-input.x,dy=graph.points[s.anchor].y-input.y,dz=graph.points[s.anchor].z-input.z;
      const double cost=std::sqrt(dx*dx+dy*dy+dz*dz)+s.goals.Distance((int)i)+length;
      // Preserve Cecil's preference for small height differences while equipping:
      // a short launch route need not be the quickest first useful pickup.
      // This ranks items only; graph costs/topology and physical deadlines stay unchanged.
      const FLOAT3D displacement((FLOAT)(item.x-input.x),(FLOAT)(item.y-input.y),(FLOAT)(item.z-input.z));
      const double score=cost+3*std::fabs(BotCecilHeight(player,displacement));
      if(diagnostics){
        ++eligible;
        if(attempt==0&&emitted<16){
          int from,to;unsigned flags;BotCecilSupplyDiagPath(s,(int)i,from,to,flags);++emitted;
          BotLog("[CecilSupplyDiagCandidate] local=%d tick=%d generation=%lu entity=%lu weapon=%d anchor=%d path_distance=%.6f connector=%.6f vertical=%.6f total=%.6f special_from=%d special_to=%d special_flags=%lu\n",
            slot,tick,(unsigned long)s.generation,(unsigned long)item.id,item.weapon,(int)i,s.goals.Distance((int)i),length,
            std::fabs(BotCecilHeight(player,displacement)),score,from,to,(unsigned long)flags);
        }
      }
      if(score<bestScore){best=(int)i;bestScore=score;bestCost=cost;chosen=item;}
    }
    if(diagnostics){
      int from,to;unsigned flags;BotCecilSupplyDiagPath(s,best,from,to,flags);
      BotLog("[CecilSupplyDiagSelection] local=%d tick=%d attempt=%d eligible=%u emitted=%u chosen=%lu weapon=%d anchor=%d path_distance=%.6f cost=%.6f score=%.6f special_from=%d special_to=%d special_flags=%lu\n",
        slot,tick,attempt,eligible,emitted,(unsigned long)(best<0?0:chosen.id),best<0?0:chosen.weapon,best,s.goals.Distance(best),bestCost,bestScore,from,to,(unsigned long)flags);
    }
    if(best<0)return;
    CEntity* entity=player->GetWorld()->EntityFromID(chosen.id);const auto& point=graph.points[best];
    const FLOAT3D lift=player->en_vGravityDir*-.8f;
    if(!BotSupplyClear(player,FLOAT3D(point.x,point.y,point.z)+lift,
         FLOAT3D((FLOAT)chosen.x,(FLOAT)chosen.y,(FLOAT)chosen.z)+lift,entity)){
      s.RejectItem(chosen.id,now);continue;
    }
    s.ClearGoal();s.goal=best;s.goalEntity=chosen.id;s.goalKind=chosen.kind;s.goalSince=now;
    s.mappedWeaponGoal=true;s.goalDeadline=now+std::fmin(45.0,std::fmax(20.0,bestCost/6.0+5.0));
    s.searchAfter=now+input.settings.fItemSearchCD;
    BotLog("[CecilGoal] local=%d tick=%d entity=%lu kind=%d weapon=%d anchor=%d pos=(%.3f,%.3f,%.3f) mapped=1 deadline=%.3f\n",
      slot,tick,(unsigned long)chosen.id,(int)chosen.kind,chosen.weapon,best,chosen.x,chosen.y,chosen.z,s.goalDeadline);
    return;
  }
}
static void BotCecilChooseGoal(CPlayer *player,INDEX slot,INDEX tick,double enemyDistance,bool allowPatrol=true){
  SSupplyState& s=BotSupplyState(slot);const auto& graph=BotSupplyGraph();
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;const double now=tick*_pTimer->TickQuantum;
  const int acquired=BotSupplyNearest(player,position,TRUE);
  if(acquired>=0){s.anchor=acquired;s.acquiredAnchor=acquired;s.acquiredAnchorTime=now;}
  // Acquisition nodes are hints, not a requirement to fly through a valid edge.
  // Map/death/rejoin resets and goal identity invalidate this navigator context.
  else if(!s.patrolAlternate&&!s.navigator.HasCommittedEdge(s.goal))s.anchor=-1;
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
        item.visible=false;s.RejectItem(item.id,now,true);continue;
      }
      int anchor=BotSupplyNearest(player,FLOAT3D((FLOAT)item.x,(FLOAT)item.y,(FLOAT)item.z),FALSE,entity);
      if(anchor<0&&_botRayBudget<=2)break;
      if(anchor<0||!std::isfinite(s.goals.Distance(anchor))){item.reachable=false;s.RejectItem(item.id,now,true);continue;}
      s.ClearGoal();s.goal=anchor;s.goalEntity=item.id;s.goalSince=now;s.searchAfter=now+settings.fItemSearchCD;
      s.importantGoal=false;s.goalKind=item.kind;s.navigator.Reset();
      BotLog("[CecilGoal] local=%d tick=%d entity=%lu kind=%d weapon=%d anchor=%d pos=(%.3f,%.3f,%.3f)\n",
        slot,tick,(unsigned long)item.id,(int)item.kind,item.weapon,anchor,item.x,item.y,item.z);break;
    }
  }
  BotCecilChooseMappedWeapon(player,s,input,slot,tick,now);
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
  const FLOAT lastPitch=player->m_aLastRotation(2);
  if(!std::isfinite(viewPitch)||!std::isfinite(lastPitch)){move=botcore::CecilMotion();return;}
  if(player->m_pstState==PST_DIVE||viewPitch<=-30)leveling=true;
  if(std::fabs(viewPitch)<=1e-6)leveling=false;
  const double correction=botcore::TestTurnDelta(viewPitch,0,180*dt);
  const FLOAT correctedPitch=lastPitch+(FLOAT)correction; // Same FLOAT accumulation as Driver bs_aPitch.
  if(!std::isfinite(correction)||!std::isfinite(correctedPitch)){move=botcore::CecilMotion();return;}
  // Native residuals can exceed the exact-zero gate while their correction is
  // lost in accumulated FLOAT pitch. Release only an already tiny, unencodable
  // correction; a large accumulated angle must never waive meaningful leveling.
  if(leveling&&std::fabs(viewPitch)<=.01&&correctedPitch==lastPitch)leveling=false;
  // Level before forward input instead of guessing private composer gains.
  // Nominally <=0.5s at 180deg/s; actual view pitch remains the gate if combat
  // arbitration postpones these actions. Only the tiny FLOAT residual above
  // may release the gate before exact zero.
  if(leveling&&std::fabs(back)>1e-6){
    back=0;move.pitch_delta=correction;
  }
  const double scale=std::fmax(1,std::fmax(std::fabs(side),std::fmax(std::fabs(up),std::fabs(back))));
  move.active=true;move.forward=-back/scale;move.strafe=side/scale;move.up=up/scale;
  if(std::fabs(local.x)+std::fabs(local.z)>1e-6)
    move.yaw_delta=botcore::TestTurnDelta(yaw,std::atan2(-local.x,-local.z)*180/3.141592653589793,180*dt);
}
// The pure navigator reports its source when an UNREACHABLE next hop requests stay.
// Recover that concrete hop using the same prepared directed search, without allocation.
static void BotCecilReacquire(CPlayer* player,SSupplyState& state,double now,SCecilMove& out,bool contextOnly=false){
  const bool liquid=BotCecilLiquid(player);
  bool groundEligible=BotCecilFrameReady(player)&&player->GetWorld()&&!liquid&&
    (player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH)&&
    std::isfinite(now)&&now>=0;
  for(int i=1;groundEligible&&i<=3;++i)groundEligible=std::isfinite(player->en_vCurrentTranslationAbsolute(i));
  const auto& graph=BotSupplyGraph();
  const bool graphShapeValid=!graph.points.empty()&&graph.points.size()<=botcore::CecilNavGraph::kMaxPoints&&state.blocked.size()==graph.points.size();
  bool graphMetadataValid=graphShapeValid;
  if(graphShapeValid)for(const auto& point:graph.points)graphMetadataValid=graphMetadataValid&&std::isfinite(point.x)&&
    std::isfinite(point.y)&&std::isfinite(point.z)&&std::isfinite(point.radius)&&point.radius>0;
  bool airContext=!contextOnly&&state.anchor<0&&!state.navigator.HasCommittedEdge(state.goal)&&
    player->m_pstState==PST_FALL&&!liquid&&!BotCecilSettings().bAvoidPits&&
    BotCecilFrameReady(player)&&player->GetWorld()&&player->GetHealth()>0&&player->m_penWeapons&&
    std::isfinite(now)&&now>=0&&graphMetadataValid;
  for(int i=1;airContext&&i<=3;++i)airContext=std::isfinite(player->en_vCurrentTranslationAbsolute(i));
  // Observing an accepted frozen ground pose does not prove current support.
  // Reference flicker or a deferred query cannot erase passive position time.
  if(groundEligible&&graphMetadataValid)state.groundObservationTime=now;
  if(player->en_penReference){
    CEntity* ref=player->en_penReference;
    groundEligible=groundEligible&&!(ref->GetFlags()&ENF_DELETED)&&
      (ref->GetRenderType()==CEntity::RT_BRUSH||ref->GetRenderType()==CEntity::RT_TERRAIN)&&
      player->GetWorld()->EntityFromID(ref->en_ulID)==ref;
    if(groundEligible&&graphMetadataValid)state.recoveryMovementTime=now;
  }
  // A NULL reference can coexist with native brush contact. Only a near-foot
  // hit substitutes for support authority; default-policy stalled movement is
  // separate and still requires its own current wall validation.
  if(!airContext&&!liquid&&player->en_penReference==NULL){
    const bool trace=((int)std::floor(now*20+.5))%20==0;
    if(trace)BotLog("[CecilReacquireSupport] entity=%lu generation=%lu time=%.3f stage=begin state=%d physics=%lu velocity=(%.5f,%.5f,%.5f) budget=%d\n",(unsigned long)player->en_ulID,(unsigned long)state.generation,now,(int)player->m_pstState,(unsigned long)player->GetPhysicsFlags(),player->en_vCurrentTranslationAbsolute(1),player->en_vCurrentTranslationAbsolute(2),player->en_vCurrentTranslationAbsolute(3),_botRayBudget);
    // One support cast, at least one LOS cast and the final two safety probes.
    if(_botRayBudget<4)return; // Unknown support must not erase a deferred LOS sweep.
    const FLOAT3D& velocity=player->en_vCurrentTranslationAbsolute;
    bool valid=(player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH)&&
      (player->GetPhysicsFlags()&EPF_TRANSLATEDBYGRAVITY);
    double verticalSpeed=0;
    for(int i=1;i<=3;++i){valid=valid&&std::isfinite(velocity(i));verticalSpeed+=double(velocity(i))*player->en_vGravityDir(i);}
    if(!valid||!std::isfinite(verticalSpeed)||std::fabs(verticalSpeed)>.1){state.ClearReacquireScan();return;}
    if(groundEligible&&graphMetadataValid)state.recoveryMovementTime=now; // Movement context, never a support proof.
    const FLOAT3D foot=player->GetPlacement().pl_PositionVector;
    const FLOAT3D from=foot-player->en_vGravityDir*.25f,to=foot+player->en_vGravityDir*.05f;
    double length=0;
    if(!BotCecilRayLength(from,to,length)||length==0){state.ClearReacquireScan();return;}
    CCastRay supportRay(player,from,to);
    --_botRayBudget;supportRay.cr_bPhysical=TRUE;supportRay.cr_bAllowOverHit=FALSE;
    supportRay.cr_ttHitModels=CCastRay::TT_NONE;
    if(!BotCecilPhysicalCast(supportRay,player->GetWorld())){state.ClearReacquireScan();return;}
    const CBrushPolygon* polygon=supportRay.cr_pbpoBrushPolygon;
    if(!supportRay.cr_penHit||(supportRay.cr_penHit->GetFlags()&ENF_DELETED)||
       supportRay.cr_penHit->GetRenderType()!=CEntity::RT_BRUSH||!polygon||
       (polygon->bpo_ulFlags&BPOF_PASSABLE)||!polygon->bpo_pbplPlane||
       !std::isfinite(supportRay.cr_fHitDistance)||supportRay.cr_fHitDistance<.25f||supportRay.cr_fHitDistance>.30f){
      if(trace)BotLog("[CecilReacquireSupport] entity=%lu generation=%lu time=%.3f stage=geometry_rejected hit=%lu type=%d distance=%.7f polygon=%d passable=%d budget=%d\n",(unsigned long)player->en_ulID,(unsigned long)state.generation,now,supportRay.cr_penHit?(unsigned long)supportRay.cr_penHit->en_ulID:0,supportRay.cr_penHit?(int)supportRay.cr_penHit->GetRenderType():-1,supportRay.cr_fHitDistance,polygon!=NULL,polygon&&(polygon->bpo_ulFlags&BPOF_PASSABLE),_botRayBudget);
      state.ClearReacquireScan();return;
    }
    const auto& normal=polygon->bpo_pbplPlane->bpl_plAbsolute;
    const double support=-(double(normal(1))*player->en_vGravityDir(1)+double(normal(2))*player->en_vGravityDir(2)+double(normal(3))*player->en_vGravityDir(3));
    if(!std::isfinite(support)||support<=.5){
      if(trace)BotLog("[CecilReacquireSupport] entity=%lu generation=%lu time=%.3f stage=normal_rejected distance=%.7f support=%.7f budget=%d\n",(unsigned long)player->en_ulID,(unsigned long)state.generation,now,supportRay.cr_fHitDistance,support,_botRayBudget);
      state.ClearReacquireScan();return;
    }
    if(trace)BotLog("[CecilReacquireSupport] entity=%lu generation=%lu time=%.3f stage=verified distance=%.7f support=%.7f budget=%d\n",(unsigned long)player->en_ulID,(unsigned long)state.generation,now,supportRay.cr_fHitDistance,support,_botRayBudget);
  }
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  if(!graphShapeValid)return;
  // This remains a separate same-update support authorization. Unknown support
  // and deferred queries may never authorize opt-in floor/contact recovery.
  groundEligible=groundEligible&&graphMetadataValid;
  if(groundEligible&&_botRayBudget>=2)state.groundRecoveryTime=now;
  if(contextOnly)return; // Observe/support-check neutral ownership without inventing a NAV target.
  BotCecilLocks(player,state,now);
  if(state.reacquireNode>=0&&(now<state.reacquireSince||now-state.reacquireSince>=6)){
    state.reacquireRejected=state.reacquireNode;state.reacquireRetryAfter=now+6;
    state.reacquireNode=-1;state.reacquireSince=-1;state.ClearEscape();state.ClearReacquireScan();
  }
  double moved=0,turnedGravity=0;
  for(int i=0;i<3;++i){const double p=position(i+1)-state.reacquireScanPosition[i],g=player->en_vGravityDir(i+1)-state.reacquireScanGravity[i];moved+=p*p;turnedGravity+=g*g;}
  if(state.reacquireScanTime<0||now<state.reacquireScanTime||moved>=.75*.75||turnedGravity>1e-6||liquid!=state.reacquireScanLiquid){
    state.ClearReacquireScan();
    for(int i=0;i<3;++i){state.reacquireScanPosition[i]=position(i+1);state.reacquireScanGravity[i]=player->en_vGravityDir(i+1);}
    state.reacquireScanLiquid=liquid;
  }
  state.reacquireScanTime=now;
  // Only a geometrically absent local graph permits a farther original hint.
  // LOS failures, tried bits and target backoff must never manufacture absence.
  bool localPoint=false;
  if(groundEligible)for(size_t i=0;i<graph.points.size();++i){
    if(state.blocked[i])continue;
    const auto& point=graph.points[i];const FLOAT3D delta(point.x-position(1),point.y-position(2),point.z-position(3));
    const double height=BotCecilHeight(player,delta);
    const double d=double(delta(1))*delta(1)+double(delta(2))*delta(2)+double(delta(3))*delta(3);
    if(std::isfinite(height)&&std::fabs(height)<=8&&d<=1024){localPoint=true;break;}
  }
  // Mode validation is metadata-only; a deferred ray budget must not erase or
  // renew an existing attempt. The unchanged LOS loop reserves two safety rays.
  const bool farHint=groundEligible&&!liquid&&!localPoint;
  const double limit=farHint?std::numeric_limits<double>::infinity():1024.000001;
  int slots[3]={-1,-1,-1};double distance[3]={limit,limit,limit};
  if(state.reacquireNode>=0&&(size_t)state.reacquireNode<graph.points.size()){
    const auto& point=graph.points[state.reacquireNode];const FLOAT3D delta(point.x-position(1),point.y-position(2),point.z-position(3));
    const double d=double(delta(1))*delta(1)+double(delta(2))*delta(2)+double(delta(3))*delta(3);
    if(!state.blocked[state.reacquireNode]&&std::isfinite(d)&&(farHint?d>1024:d<=1024)&&
       (liquid||std::fabs(BotCecilHeight(player,delta))<=8)){slots[0]=state.reacquireNode;distance[0]=-1;}
    else if(d>1024){state.reacquireNode=-1;state.reacquireSince=-1;state.ClearEscape();}
  }
  for(size_t i=0;i<graph.points.size();++i){
    if(state.blocked[i]||(int)i==slots[0]||(state.reacquireTried[i/8]&(1u<<(i%8)))||
       ((int)i==state.reacquireRejected&&now<state.reacquireRetryAfter))continue;
    const auto& point=graph.points[i];const FLOAT3D delta(point.x-position(1),point.y-position(2),point.z-position(3));
    if(!liquid&&std::fabs(BotCecilHeight(player,delta))>8)continue;
    const double d=double(delta(1))*delta(1)+double(delta(2))*delta(2)+double(delta(3))*delta(3);
    if(!std::isfinite(d)||(farHint?d<=1024:d>1024))continue;
    for(int k=0;k<3;++k)if(d<distance[k]){for(int j=2;j>k;--j){slots[j]=slots[j-1];distance[j]=distance[j-1];}slots[k]=(int)i;distance[k]=d;break;}
  }
  // A complete failed sweep is retried, so changing physical LOS is never a
  // permanent blacklist. Ordinary scanTick expiry does not restart the sweep.
  if(slots[0]<0){state.ClearReacquireScan();return;}
  for(int k=0;k<3&&_botRayBudget>2;++k){
    if(slots[k]<0)continue;
    const auto& point=graph.points[slots[k]];const FLOAT3D target(point.x,point.y,point.z),lift=player->en_vGravityDir*-.8f;
    const bool clear=BotSupplyClear(player,position+lift,target+lift)!=FALSE;
    if(!clear){
      state.reacquireTried[slots[k]/8]|=(unsigned char)(1u<<(slots[k]%8));
      if(state.reacquireNode==slots[k]){state.reacquireNode=-1;state.reacquireSince=-1;state.ClearEscape();}
      continue;
    }
    const FLOAT3D delta=target-position;const double height=BotCecilHeight(player,delta);
    const auto local=BotCecilBodyFrame(player).ToLocal(delta(1)+player->en_vGravityDir(1)*-height,
      delta(2)+player->en_vGravityDir(2)*-height,delta(3)+player->en_vGravityDir(3)*-height);
    if(!liquid&&local.x*local.x+local.z*local.z<.25){state.reacquireTried[slots[k]/8]|=(unsigned char)(1u<<(slots[k]%8));continue;}
    const auto aim=botcore::AimAt(local.x,0,local.z);const double yaw=player->en_plViewpoint.pl_OrientationAngle(1);
    const double error=std::remainder(aim.yaw_deg-yaw,360.0)*3.141592653589793/180;
    out.forward=.3*std::cos(error);out.strafe=BotCecilSettings().bStrafe?-.3*std::sin(error):0;
    out.yaw_delta=botcore::TestTurnDelta(yaw,aim.yaw_deg,180*_pTimer->TickQuantum);
    if(liquid){botcore::CecilMotion motion;BotCecilSwimMotion(player,delta,yaw,_pTimer->TickQuantum,motion,state.levelSwimView);
      out.forward=.3*motion.forward;out.strafe=BotCecilSettings().bStrafe?.3*motion.strafe:0;out.up=.3*motion.up;out.pitch_delta=motion.pitch_delta;}
    if(state.reacquireNode!=slots[k]){state.reacquireNode=slots[k];state.reacquireSince=now;state.ClearEscape();}
    out.active=true;state.reacquiring=true;
    if(airContext){state.airMovementTime=now;state.airMovementEntity=player->en_ulID;
      state.airMovementGeneration=state.generation;state.airMovementNode=slots[k];
      for(int i=0;i<3;++i)state.airMovementGravity[i]=player->en_vGravityDir(i+1);}
    return;
  }
}
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
// A native launch/relocation can replace a short ordinary weapon route with a
// much longer directed return. Only the navigator's existing reached-node event
// permits one fixed extension; scans and ordinary progress never renew it.
static void BotCecilRebudgetWeapon(CPlayer* player,SSupplyState& s,const botcore::CecilMotion& move,
    const botcore::CecilItemInput& input,INDEX slot,INDEX tick,double now){
  if(!std::isfinite(now)||!std::isfinite(s.goalSince)||now<0||s.goalSince<0||
     !move.relocated||!move.active||move.arrived||!s.goalEntity||s.mappedWeaponGoal||s.goalRelocationBudgeted||
     now<s.goalSince||now-s.goalSince>=12)return;
  const auto& graph=BotSupplyGraph();const size_t nodes=graph.points.size();
  if(s.anchor<0||s.goal<0||(size_t)s.anchor>=nodes||(size_t)s.goal>=nodes||s.blocked.size()!=nodes||
     s.blocked[s.anchor]||s.blocked[s.goal])return;
  CEntity* entity=player->GetWorld()->EntityFromID(s.goalEntity);botcore::CecilItem item;
  if(!entity||!BotCecilReadItem(player,entity,s.generation,input.owned,&item)||
     item.kind!=botcore::CecilItemKind::Weapon||!botcore::CecilRetainItem(item,input))return;
  if(!s.goals.Run(graph,s.anchor,s.blocked.data(),nodes))return;
  const double remaining=s.goals.Distance(s.goal);if(!std::isfinite(remaining))return;
  const auto& origin=graph.points[s.anchor];const auto& target=graph.points[s.goal];
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  const FLOAT3D approach=FLOAT3D(origin.x,origin.y,origin.z)-position;
  const FLOAT3D connector((FLOAT)item.x-target.x,(FLOAT)item.y-target.y,(FLOAT)item.z-target.z);
  const double length=connector.Length();
  if(length>8||std::fabs(BotCecilHeight(player,connector))>3)return;
  const double cost=approach.Length()+remaining+length,oldDeadline=s.goalSince+12;
  if(!std::isfinite(cost)||cost<=0)return;
  const double deadline=std::fmin(s.goalSince+45,std::fmax(oldDeadline,now+cost/6+5));
  if(!std::isfinite(deadline)||deadline<=oldDeadline||_botRayBudget<=2)return;
  const FLOAT3D lift=player->en_vGravityDir*-.8f;
  if(!BotSupplyClear(player,FLOAT3D(target.x,target.y,target.z)+lift,
      FLOAT3D((FLOAT)item.x,(FLOAT)item.y,(FLOAT)item.z)+lift,entity))return;
  s.goalDeadline=deadline;s.goalRelocationBudgeted=true;
  BotLog("[CecilGoalBudget] local=%d tick=%d entity=%lu source=%d goal=%d cost=%.3f old=%.3f deadline=%.3f reason=relocation\n",
    slot,tick,(unsigned long)s.goalEntity,s.anchor,s.goal,cost,oldDeadline,deadline);
}
// A missed airborne edge can leave both committed points on another floor.
// Reacquire only a fresh existing ground hint; it must still be approached and
// reached at its original radius. This is not a relocation or a new item attempt.
static bool BotCecilGroundedReplan(CPlayer* player,SSupplyState& s,const botcore::CecilMotion& move,INDEX slot,INDEX tick){
  const auto& graph=BotSupplyGraph();const int source=s.navigator.SourceSlot(s.goal),hop=move.hop;
  if(source<0||hop<0||hop==source||(size_t)source>=graph.points.size()||(size_t)hop>=graph.points.size()||
     s.blocked.size()!=graph.points.size()||s.blocked[source]||s.blocked[hop]||
     s.importantGoal||s.interactionPoint>=0||tick<=s.useReleaseTick||!move.active||move.arrived||move.stuck||
     !BotCecilFrameReady(player)||!player->GetWorld()||BotCecilLiquid(player)||
     (player->m_pstState!=PST_STAND&&player->m_pstState!=PST_CROUCH))return false;
  CEntity* ref=player->en_penReference;
  if(!ref||(ref->GetFlags()&ENF_DELETED)||ref->GetRenderType()!=CEntity::RT_BRUSH||
     !BotCecilIsClass(ref,"WorldBase","World Base")||player->GetWorld()->EntityFromID(ref->en_ulID)!=ref)return false;
  double speed2=0;
  for(int i=1;i<=3;++i){const double v=player->en_vCurrentTranslationAbsolute(i);if(!std::isfinite(v))return false;speed2+=v*v;}
  if(!std::isfinite(speed2)||speed2>.01)return false;
  const auto& a=graph.points[source];const auto& b=graph.points[hop];
  const uint32_t special=botcore::CECIL_UNREACHABLE|botcore::CECIL_TELEPORT|botcore::CECIL_IMPORTANT;
  if((a.flags|b.flags)&special)return false;
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  const FLOAT3D da=FLOAT3D(a.x,a.y,a.z)-position,db=FLOAT3D(b.x,b.y,b.z)-position;
  const double sourceHeight=-BotCecilHeight(player,da),hopHeight=-BotCecilHeight(player,db);
  double horizontal2=0;
  for(int i=1;i<=3;++i){const double h=db(i)+player->en_vGravityDir(i)*hopHeight;horizontal2+=h*h;}
  if(!std::isfinite(sourceHeight)||!std::isfinite(hopHeight)||!std::isfinite(horizontal2)||
     sourceHeight<=4||hopHeight<=4||horizontal2>=1)return false;
  const int candidate=BotSupplyNearest(player,position,TRUE);
  if(candidate<0||candidate!=s.anchor||candidate==source||candidate==hop||s.blocked[candidate]||
     (graph.points[candidate].flags&special)||!s.goals.Run(graph,candidate,s.blocked.data(),s.blocked.size())||
     !std::isfinite(s.goals.Distance(s.goal)))return false;
  BotLog("[CecilGroundReplan] local=%d tick=%d entity=%lu reason=landed_below_committed_edge source=%d hop=%d anchor=%d source_height=%.6f hop_height=%.6f goal=%d goal_entity=%lu\n",
    slot,tick,(unsigned long)player->en_ulID,source,hop,candidate,sourceHeight,hopHeight,s.goal,(unsigned long)s.goalEntity);
  s.navigator.Reset();s.hop=s.heldNode=-1;s.holdSince=-1;s.currentNavTime=-1;s.currentNavGoal=-1;s.currentNavTravel=false;
  return true;
}
// Two accepted checkpoints can prove repeated same-source rebasing ineffective.
// Observe the fixed failed hop across real source reapproach; this history is
// never static-contact authority, a new anchor, or a renewed patrol deadline.
static bool BotCecilPatrolContext(CPlayer* player,const SSupplyState& s,double now){
  const auto& graph=BotSupplyGraph();
  if(!BotCecilFrameReady(player)||!std::isfinite(now)||now<0||!s.playable||player->GetHealth()<=0||
     !player->m_penWeapons||!player->GetWorld()||(player->GetFlags()&ENF_DELETED)||BotCecilLiquid(player)||
     (player->m_pstState!=PST_STAND&&player->m_pstState!=PST_CROUCH&&player->m_pstState!=PST_FALL)||s.goalEntity||s.followEntity||
     s.interactionPoint>=0||(s.useReleaseTick>=0&&now<=s.useReleaseTick*_pTimer->TickQuantum)||
     s.patrolGoal!=s.goal||s.patrolWorld!=player->GetWorld()||s.patrolEntity!=player->en_ulID||s.patrolGeneration!=s.generation||
     s.patrolMap!=InterlockedCompareExchange(&_botSupplyMapSerial,0,0)||
     s.patrolLast<0||now<s.patrolLast||now-s.patrolLast>.25||graph.points.empty()||graph.points.size()>botcore::CecilNavGraph::kMaxPoints||
     s.blocked.size()!=graph.points.size()||s.goal<0||(size_t)s.goal>=graph.points.size()||s.patrolSource<0||s.patrolHop<0||
     (size_t)s.patrolSource>=graph.points.size()||(size_t)s.patrolHop>=graph.points.size())return false;
  const auto& a=graph.points[s.patrolSource];const auto& b=graph.points[s.patrolHop];
  if(a.flags||b.flags||a.important_entity>=0||b.important_entity>=0||a.lock_entity>=0||b.lock_entity>=0||
     s.blocked[s.patrolSource]||s.blocked[s.patrolHop]||
     std::find(a.links.begin(),a.links.end(),s.patrolHop)==a.links.end())return false;
  for(int i=1;i<=3;++i)if(!std::isfinite(player->en_vCurrentTranslationAbsolute(i))||
    s.patrolGravity[i-1]!=player->en_vGravityDir(i))return false;
  CEntity* ref=player->en_penReference;
  return !ref||(!(ref->GetFlags()&ENF_DELETED)&&ref->en_pwoWorld==player->GetWorld()&&ref->GetRenderType()==CEntity::RT_BRUSH);
}
static bool BotCecilPatrolStatic(CPlayer* player){
  CEntity* ref=player->en_penReference;
  // Passive FALL history is not current standing/contact authority.
  return (player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH)&&
    ref&&!(ref->GetFlags()&ENF_DELETED)&&ref->GetRenderType()==CEntity::RT_BRUSH&&
    !(ref->GetPhysicsFlags()&EPF_MOVABLE)&&ref->en_pwoWorld==player->GetWorld()&&BotCecilIsClass(ref,"WorldBase","World Base");
}
static bool BotCecilPatrolAtHop(CPlayer* player,const SSupplyState& s){
  const auto& point=BotSupplyGraph().points[s.patrolHop];const auto& p=player->GetPlacement().pl_PositionVector;
  const double radius=point.radius;if(!std::isfinite(radius)||radius<=0)return false;
  double first=0,second=0;
  for(int i=1;i<=3;++i){const double d=(i==1?point.x:(i==2?point.y:point.z))-p(i);
    first+=d*d;const double shifted=d-player->en_vGravityDir(i)*radius*.5;second+=shifted*shifted;}
  return first<radius*radius||second<radius*radius; // Unchanged CecilNavigator::Reached geometry.
}
static void BotCecilPatrolObserve(CPlayer* player,SSupplyState& s,double now,bool accepted){
  if(s.patrolSource<0)return;
  const int source=s.navigator.SourceSlot(s.goal);
  // SourceSlot deliberately reports only a committed edge. After a checkpoint
  // the navigator first approaches the original source (source_ == hop_).
  const bool sourceApproach=s.hop==s.patrolSource&&s.anchor==s.patrolSource&&
    s.currentNavGoal==s.goal&&std::fabs(now-s.currentNavTime)<=1e-6;
  if(!accepted||!BotCecilPatrolContext(player,s,now)||(!s.patrolAlternate&&
     (s.currentNavGoal!=s.goal||!(std::fabs(now-s.currentNavTime)<=1e-6)||
      (source!=s.patrolSource&&!sourceApproach)||
      (s.hop!=s.patrolSource&&s.hop!=s.patrolHop)))){s.ClearPatrolEpisode();return;}
  if(BotCecilPatrolAtHop(player,s)){
    if(s.patrolAlternate)BotLog("[CecilPatrolRecovery] entity=%lu generation=%lu time=%.3f action=original_hop_arrival source=%d hop=%d goal=%d\n",
      (unsigned long)player->en_ulID,(unsigned long)s.generation,now,s.patrolSource,s.patrolHop,s.goal);
    s.ClearPatrolEpisode();return;
  }
  const auto& point=BotSupplyGraph().points[s.patrolHop];const auto& p=player->GetPlacement().pl_PositionVector;
  const double dx=point.x-p(1),dy=point.y-p(2),dz=point.z-p(3),distance=std::sqrt(dx*dx+dy*dy+dz*dz);
  const double vertical=dx*player->en_vGravityDir(1)+dy*player->en_vGravityDir(2)+dz*player->en_vGravityDir(3);
  if(!std::isfinite(distance)||(distance*distance-vertical*vertical<1&&std::fabs(vertical)>4)){s.ClearPatrolEpisode();return;}
  s.patrolLast=now;s.patrolBest=std::fmin(s.patrolBest,distance);
  if(s.patrolGainBase-s.patrolBest>=.75){s.patrolGainBase=s.patrolBest;s.patrolStrikes=0;}
}
static void BotCecilPatrolStrike(CPlayer* player,SSupplyState& s,double now,int source,int hop,double best){
  const auto& a=BotSupplyGraph().points[source];const auto& b=BotSupplyGraph().points[hop];
  if(s.goalEntity||s.followEntity||a.flags||b.flags||a.important_entity>=0||b.important_entity>=0||
     a.lock_entity>=0||b.lock_entity>=0)return;
  if(s.patrolSource!=source||s.patrolHop!=hop||!BotCecilPatrolContext(player,s,now)){
    s.ClearPatrolEpisode();s.patrolWorld=player->GetWorld();s.patrolEntity=player->en_ulID;s.patrolGeneration=s.generation;
    s.patrolMap=InterlockedCompareExchange(&_botSupplyMapSerial,0,0);
    s.patrolGoal=s.goal;s.patrolSource=source;s.patrolHop=hop;s.patrolLast=now;s.patrolBest=s.patrolGainBase=best;
    for(int i=0;i<3;++i)s.patrolGravity[i]=player->en_vGravityDir(i+1);
  }
  if(++s.patrolStrikes<2)return;
  s.patrolAlternate=true;s.patrolSince=now;s.patrolHint=-1;s.patrolProposalTime=-1;
  std::fill(s.patrolTried,s.patrolTried+sizeof(s.patrolTried),0);s.ClearGroundProgress();
  BotLog("[CecilPatrolRecovery] entity=%lu generation=%lu time=%.3f action=enter source=%d hop=%d goal=%d deadline=%.3f best_distance=%.6f\n",
    (unsigned long)player->en_ulID,(unsigned long)s.generation,now,source,hop,s.goal,now+6,s.patrolBest);
}
static void BotCecilPatrolFail(CPlayer* player,SSupplyState& s,double now,const char* reason){
  BotLog("[CecilPatrolRecovery] entity=%lu generation=%lu time=%.3f action=failed source=%d hop=%d goal=%d reason=%s\n",
    (unsigned long)player->en_ulID,(unsigned long)s.generation,now,s.patrolSource,s.patrolHop,s.goal,reason);
  s.ClearGoal();s.ClearEscape();s.searchAfter=now;s.scanTick=0;
}
static void BotCecilPatrolPlan(CPlayer* player,SSupplyState& s,double now,SCecilMove& out){
  if(now-s.patrolSince>=6){BotCecilPatrolFail(player,s,now,"deadline");return;}
  if(!BotCecilPatrolStatic(player)||_botRayBudget<=2)return;
  BotCecilLocks(player,s,now);const auto& graph=BotSupplyGraph();uint64_t locks=1469598103934665603ULL;
  for(unsigned char value:s.blocked){locks^=value;locks*=1099511628211ULL;}
  if(locks!=s.patrolLocks){s.patrolHint=-1;s.patrolLocks=locks;}
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  auto candidate=[&](int node){
    if(node<0||(size_t)node>=graph.points.size()||node==s.patrolSource||node==s.patrolHop||s.blocked[node]||
       ((s.patrolTried[node/8]|s.reacquireTried[node/8])&(1u<<(node%8)))||
       (node==s.reacquireRejected&&now<s.reacquireRetryAfter))return false;
    const auto& p=graph.points[node];const FLOAT3D d(p.x-position(1),p.y-position(2),p.z-position(3));
    const double height=BotCecilHeight(player,d),length2=double(d(1))*d(1)+double(d(2))*d(2)+double(d(3))*d(3);
    return !p.flags&&p.important_entity<0&&p.lock_entity<0&&std::isfinite(p.radius)&&p.radius>0&&
      std::isfinite(length2)&&std::isfinite(height)&&length2<=1024&&std::fabs(height)<=8&&length2-height*height>=.25;
  };
  if(s.patrolHint>=0&&(!candidate(s.patrolHint)||
     !s.patrolSearch.PathAvoidsEdge(graph,s.goal,s.patrolSource,s.patrolHop,s.blocked.data(),s.blocked.size())))s.patrolHint=-1;
  int slots[3]={-1,-1,-1};double distances[3]={1024.000001,1024.000001,1024.000001};
  if(s.patrolHint>=0){slots[0]=s.patrolHint;distances[0]=-1;}
  for(size_t i=0;i<graph.points.size();++i)if((int)i!=slots[0]&&candidate((int)i)){
    const auto& p=graph.points[i];const double d=double(p.x-position(1))*(p.x-position(1))+
      double(p.y-position(2))*(p.y-position(2))+double(p.z-position(3))*(p.z-position(3));
    for(int k=0;k<3;++k)if(d<distances[k]){for(int j=2;j>k;--j){slots[j]=slots[j-1];distances[j]=distances[j-1];}slots[k]=(int)i;distances[k]=d;break;}
  }
  if(slots[0]<0){BotCecilPatrolFail(player,s,now,"exhausted_candidates");return;}
  for(int k=0;k<3&&_botRayBudget>2;++k){
    const int node=slots[k];if(node<0)continue;const auto& p=graph.points[node];
    const FLOAT3D target(p.x,p.y,p.z),lift=player->en_vGravityDir*-.8f;bool valid=false;
    if(!BotSupplyClear(player,position+lift,target+lift,NULL,&valid)){
      if(!valid)return;
      s.patrolTried[node/8]|=(unsigned char)(1u<<(node%8));if(s.patrolHint==node)s.patrolHint=-1;continue;
    }
    if(s.patrolHint!=node){
      if(!s.patrolSearch.Run(graph,node,s.blocked.data(),s.blocked.size())||
         !s.patrolSearch.PathAvoidsEdge(graph,s.goal,s.patrolSource,s.patrolHop,s.blocked.data(),s.blocked.size())){
        s.patrolTried[node/8]|=(unsigned char)(1u<<(node%8));return; // One new prepared search per update.
      }
      s.patrolHint=node;
      BotLog("[CecilPatrolRecovery] entity=%lu generation=%lu time=%.3f action=hint source=%d hop=%d goal=%d hint=%d deadline=%.3f\n",
        (unsigned long)player->en_ulID,(unsigned long)s.generation,now,s.patrolSource,s.patrolHop,s.goal,node,s.patrolSince+6);
    }
    const FLOAT3D delta=target-position;const double height=BotCecilHeight(player,delta);
    const auto local=BotCecilBodyFrame(player).ToLocal(delta(1)-player->en_vGravityDir(1)*height,
      delta(2)-player->en_vGravityDir(2)*height,delta(3)-player->en_vGravityDir(3)*height);
    const double yaw=player->en_plViewpoint.pl_OrientationAngle(1);const auto aim=botcore::AimAt(local.x,0,local.z);
    const double error=std::remainder(aim.yaw_deg-yaw,360.0)*3.141592653589793/180;
    out.forward=.3*std::cos(error);out.strafe=BotCecilSettings().bStrafe?-.3*std::sin(error):0;
    out.yaw_delta=botcore::TestTurnDelta(yaw,aim.yaw_deg,180*_pTimer->TickQuantum);out.up=0;
    out.active=true;s.patrolProposalTime=now;return;
  }
}
static SCecilMove BotSupplyTick(CPlayer *player,INDEX slot,INDEX tick,double enemyDistance,const SCecilFollowGoal* follow=nullptr){
  SCecilMove result;SSupplyState &s=BotSupplyState(slot);s.acquiredAnchorTime=-1;s.acquiredAnchor=-1;s.currentNavTime=-1;s.currentNavGoal=-1;s.currentNavTravel=false;s.reacquiring=false;s.ClearAirMovement();s.groundRecoveryTime=s.groundObservationTime=s.recoveryMovementTime=-1;result.useControl=tick<=s.useReleaseTick;
  s.patrolProposalTime=-1;
  const double now=tick*_pTimer->TickQuantum;const bool alive=player&&player->GetHealth()>0&&player->m_penWeapons!=NULL;
  if(!alive){if(s.playable){BotCecilGoalEnd(slot,tick,s,"death");++s.deaths;s.deadSince=now;
    BotLog("[CecilDeath] local=%d tick=%d entity=%lu generation=%lu deaths=%u\n",slot,tick,(unsigned long)s.entity,(unsigned long)s.generation,s.deaths);
    }s.ClearGroundProgress();s.playable=false;s.levelSwimView=false;s.ClearGoal();s.ClearEscape();s.ClearReacquireScan();return result;}
  if(!BotCecilFrameReady(player)||!std::isfinite(player->en_plViewpoint.pl_OrientationAngle(2))){s.ClearGroundProgress();return result;}
  // Inactive/neutral navigation must not hand an unanchored bot to blind Human
  // travel. The Driver still retains visible-target combat arbitration.
  result.ownsMovement=true;
  if(result.useControl)return result; // Preserve a released action even across chained switches.
  if(!s.playable){s.ClearGroundProgress();++s.respawns;s.spawnTick=tick;s.scanTick=0;s.ClearGoal();s.searchAfter=0;s.owned=0;s.ClearRejections();s.ClearAvoidance();s.ResetLockSnapshot();++s.generation;
    const FLOAT3D position=player->GetPlacement().pl_PositionVector;
    BotLog("[CecilSpawn] local=%d tick=%d entity=%lu generation=%lu respawns=%u pos=(%.3f,%.3f,%.3f)\n",slot,tick,(unsigned long)player->en_ulID,(unsigned long)s.generation,s.respawns,(double)position(1),(double)position(2),(double)position(3));}
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
    const char* readReason="missing_entity";
    bool usable=entity&&BotCecilReadItem(player,entity,s.generation,owned,&item,bot_bDiagnostics?&readReason:nullptr);
    if(usable){
      // Close combat pauses movement below; it does not make a live needed
      // weapon unavailable. Keep the same attempt and fixed deadline through
      // that interruption instead of repeatedly discarding its directed route.
      if(s.mappedWeaponGoal)usable=BotCecilMappedWeaponNeeded(item,input);
      // Radius/visibility/ranking admit a new goal. A retained attempt uses its
      // live typed need and directed path. Ordinary attempts start at twelve
      // seconds; one reached-node relocation may grant a bounded fixed extension.
      else usable=botcore::CecilRetainItem(item,input);
      if(!usable)readReason="typed_need";
    }
    if(!usable||now<s.goalSince||((s.mappedWeaponGoal||s.goalRelocationBudgeted)?now>=s.goalDeadline:now-s.goalSince>=12)){
      if(!usable)BotCecilSupplyDiagUnavailable(player,s,entity,slot,tick,now,readReason,input);
      BotCecilGoalEnd(slot,tick,s,usable?"timeout":"unavailable");
      if(usable)s.RejectItem(s.goalEntity,now);
      s.ClearGoal();s.searchAfter=now;s.scanTick=0;
    }else{s.goalKind=item.kind;urgent=BotCecilUrgentItem(item,input);}
  }
  if(tick>=s.scanTick){BotCecilChooseGoal(player,slot,tick,enemyDistance,!followValid);s.scanTick=tick+20;}
  if(followValid)BotCecilFollow(player,s,*follow,now);
  if(s.patrolAlternate){
    if(!BotCecilPatrolContext(player,s,now)){s.ClearPatrolEpisode();return result;}
    else if(s.acquiredAnchor>=0&&s.acquiredAnchor!=s.patrolSource&&std::fabs(now-s.acquiredAnchorTime)<=1e-6){
      BotLog("[CecilPatrolRecovery] entity=%lu generation=%lu time=%.3f action=ordinary_acquisition node=%d goal=%d\n",
        (unsigned long)player->en_ulID,(unsigned long)s.generation,now,s.acquiredAnchor,s.goal);
      s.ClearPatrolEpisode();s.navigator.Reset();
    }
  }
  if(s.patrolAlternate){
    if(enemyDistance<8){result.ownsMovement=false;return result;}
    BotCecilPatrolPlan(player,s,now,result);return result;
  }
  if(s.anchor<0){BotCecilReacquire(player,s,now,result);return result;}
  s.ClearReacquireScan();
  if(s.reacquireNode>=0){s.reacquireNode=-1;s.reacquireSince=-1;s.ClearEscape();}
  if(s.goal<0){BotCecilReacquire(player,s,now,result,true);return result;}
  if(s.goal>=(int)BotSupplyGraph().points.size())return result;
  // Refresh the typed result after a new selection in this tick.
  if(s.goalEntity){
    CEntity* entity=player->GetWorld()->EntityFromID(s.goalEntity);botcore::CecilItem item;
    if(!entity||!BotCecilReadItem(player,entity,s.generation,owned,&item)){BotCecilGoalEnd(slot,tick,s,"unavailable");s.ClearGoal();s.scanTick=0;return result;}
    s.goalKind=item.kind;urgent=BotCecilUrgentItem(item,input);
  }
  result.followGoal=s.followEntity!=0;result.itemGoal=s.goalEntity!=0;result.urgent=result.itemGoal&&urgent;result.itemKind=s.goalKind;
  if(enemyDistance<8&&!(result.urgent&&result.itemKind==botcore::CecilItemKind::Health)){
    // Keep the bounded attempt, but let visible-target combat own this action.
    // Inactive owned urgent-weapon output would otherwise suppress Human fire.
    result.ownsMovement=false;return result;
  }
  BotCecilLocks(player,s,now);
  const FLOAT3D p=player->GetPlacement().pl_PositionVector;
  botcore::CecilMotionInput in;in.x=p(1);in.y=p(2);in.z=p(3);in.yaw=player->en_plViewpoint.pl_OrientationAngle(1);in.frame=BotCecilBodyFrame(player);
  for(int j=0;j<3;++j)in.gravity[j]=player->en_vGravityDir(j+1);
  in.now=now;in.dt=_pTimer->TickQuantum;in.anchor=s.anchor;in.goal=s.goal;in.slot=slot+bot_iRosterOffset;
  in.supported_lock_node=BotCecilSupportedLockNode(player,s);
  in.alive=true;in.allow_jump=BotCecilSettings().bJump!=0;
  const auto& point=BotSupplyGraph().points[s.goal];
  if(!s.goalEntity&&!s.followEntity&&(point.important_entity>=0||(point.flags&botcore::CECIL_IMPORTANT)))s.importantGoal=true;
  in.important_goal=s.importantGoal;
  auto move=s.navigator.Update(BotSupplyGraph(),s.blocked.data(),s.blocked.size(),in);s.hop=move.hop;
  if(move.supported_lock_started){
    const auto& held=BotSupplyGraph().points[move.hop];
    const FLOAT3D delta=FLOAT3D(held.x,held.y,held.z)-p;
    BotLog("[CecilLockApproach] local=%d tick=%d player=%lu ref=%lu node=%d radius=%.6f distance=%.6f goal=%d hop=%d\n",
      slot,tick,(unsigned long)player->en_ulID,(unsigned long)(player->en_penReference?player->en_penReference->en_ulID:0),move.hop,(double)held.radius,(double)delta.Length(),s.goal,s.hop);
  }
  BotCecilRebudgetWeapon(player,s,move,input,slot,tick,now);
  if(move.active||move.arrived){s.currentNavGoal=s.goal;s.currentNavTime=now;s.currentNavTravel=move.active&&!move.arrived&&!move.stuck;}
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
        if(BotCecilGroundedReplan(player,s,move,slot,tick)){
          result=SCecilMove();result.ownsMovement=true;return result;
        }
        BotCecilGoalEnd(slot,tick,s,"unreachable_hold");s.RejectItem(s.goalEntity,now);
        s.avoidNode=travelHop;s.avoidUntil=now+10;s.avoidFollowEntity=s.followEntity;
        s.ClearGoal();s.searchAfter=now;s.scanTick=0;result=SCecilMove();result.ownsMovement=true;result.useControl=tick<=s.useReleaseTick;return result;
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
        BotCecilGoalEnd(slot,tick,s,"connector");s.RejectItem(s.goalEntity,now);s.ClearGoal();s.searchAfter=now;s.scanTick=0;result=SCecilMove();result.ownsMovement=true;result.useControl=tick<=s.useReleaseTick;return result;
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
// A current native contact can include a positive-up slope below the ordinary
// floor-normal cutoff. Reuse only that exact static-world polygon, within the
// player's actual step bounds and the existing tested segment; never infer a
// floor from proximity, a NULL reference, a different face or a missing cast.
static bool BotCecilNativeContactFloor(CPlayer* player,const CCastRay& ray,double segmentLength){
  if(!BotCecilFrameReady(player)||!player->GetWorld()||
     !std::isfinite(player->GetHealth())||player->GetHealth()<=0||
     (player->m_pstState!=PST_STAND&&player->m_pstState!=PST_CROUCH))return false;
  CEntity* ref=player->en_penReference;
  const CBrushPolygon* polygon=ray.cr_pbpoBrushPolygon;
  if(!ref||ref!=ray.cr_penHit||(ref->GetFlags()&ENF_DELETED)||
     ref->GetRenderType()!=CEntity::RT_BRUSH||(ref->GetPhysicsFlags()&EPF_MOVABLE)||
     ref->en_pwoWorld!=player->GetWorld()||!BotCecilIsClass(ref,"WorldBase","WorldBase")||
     !polygon||polygon!=player->en_pbpoStandOn||(polygon->bpo_ulFlags&BPOF_PASSABLE)||
     !polygon->bpo_pbplPlane)return false;
  const CBrushSector* sector=polygon->bpo_pbscSector;
  const CBrushMip* mip=sector?sector->bsc_pbmBrushMip:NULL;
  const CBrush3D* brush=mip?mip->bm_pbrBrush:NULL;
  if(!brush||brush->br_penEntity!=ref)return false;
  const auto& normal=polygon->bpo_pbplPlane->bpl_plAbsolute;
  if(!std::isfinite(normal.pl_distance))return false;
  double norm2=0,support=0;
  for(int i=1;i<=3;++i){
    const double n=normal(i);
    if(!std::isfinite(n)||!std::isfinite(player->en_vCurrentTranslationAbsolute(i)))return false;
    norm2+=n*n;support-=n*player->en_vGravityDir(i);
  }
  if(!std::isfinite(norm2)||std::fabs(norm2-1)>1e-3||!std::isfinite(support)||support<=0)return false;
  const double stepDown=player->en_fStepDnHeight,stepUp=player->en_fStepUpHeight,
    distance=ray.cr_fHitDistance;
  if(!std::isfinite(stepDown)||stepDown<=0||!std::isfinite(stepUp)||stepUp<=0||
     !std::isfinite(segmentLength)||segmentLength<=0||!std::isfinite(distance)||distance<0||distance>segmentLength)return false;
  // Existing floor segments begin one gravity-unit above the requested foot.
  const double height=1-distance;
  return height>=-stepDown&&height<=stepUp;
}
// Explicit support probe. Original CheckPit uses WouldFallInNextPosition with
// step-down16; this read-only 5/10m ray remains a conservative off-graph adapter,
// not equivalent physics. SafeMotion applies the original bAvoidPits/current-point gate.
// finalBodyYaw is current local head yaw plus the emitted yaw delta, never world yaw.
static bool BotCecilFloor(CPlayer *player,double forward,double strafe,double up,double finalBodyYaw,SCecilProbe* probe=NULL,bool allowCurrentContact=false){
  if(!BotCecilFrameReady(player)||!std::isfinite(forward)||!std::isfinite(strafe)||
     !std::isfinite(up)||!std::isfinite(finalBodyYaw)||std::fabs(forward)>1.000001||
     std::fabs(strafe)>1.000001||std::fabs(up)>1.000001){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  const FLOAT3D base=player->GetPlacement().pl_PositionVector;
  if(!std::isfinite(base(1))||!std::isfinite(base(2))||!std::isfinite(base(3))){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  if(BotCecilLiquid(player)||(forward==0&&strafe==0))return true;
  if(_botRayBudget<=0){BotCecilRejectedProbe(probe,SCecilProbe::reasonBudget,player);return false;}
  const double yaw=finalBodyYaw*3.141592653589793/180;
  const auto offset=BotCecilBodyFrame(player).ToWorld(-std::sin(yaw)*forward+std::cos(yaw)*strafe,0,
    -std::cos(yaw)*forward-std::sin(yaw)*strafe);
  const FLOAT3D from=base+FLOAT3D((FLOAT)offset.x,(FLOAT)offset.y,(FLOAT)offset.z)*(up>0?3.0f:1.5f)-player->en_vGravityDir;
  const FLOAT3D to=from+player->en_vGravityDir*(up>0?10.0f:5.0f);
  double length=0;
  // A collapsed floor segment cannot establish a physical NoFloor rejection.
  if(!BotCecilRayLength(from,to,length)||length==0){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  --_botRayBudget;if(probe)++probe->floorRays;
  CCastRay ray(player,from,to);
  ray.cr_bPhysical=TRUE;ray.cr_bAllowOverHit=FALSE;ray.cr_ttHitModels=CCastRay::TT_NONE;
  if(!BotCecilPhysicalCast(ray,player->GetWorld())){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  if(!ray.cr_penHit){BotCecilRejectedProbe(probe,SCecilProbe::reasonNoFloor,player,&ray,&from,&to);return false;}
  if(ray.cr_penHit->GetRenderType()==CEntity::RT_TERRAIN)return true;
  const CBrushPolygon* polygon=ray.cr_pbpoBrushPolygon;
  if(!polygon||(polygon->bpo_ulFlags&BPOF_PASSABLE)||!polygon->bpo_pbplPlane){
    const int reason=polygon&&(polygon->bpo_ulFlags&BPOF_PASSABLE)?SCecilProbe::reasonPassable:SCecilProbe::reasonUnsupportedNormal;
    BotCecilRejectedProbe(probe,reason,player,&ray,&from,&to);return false;
  }
  const auto& normal=polygon->bpo_pbplPlane->bpl_plAbsolute;
  const double support=-(normal(1)*player->en_vGravityDir(1)+normal(2)*player->en_vGravityDir(2)+normal(3)*player->en_vGravityDir(3));
  if(!(support>.5)&&allowCurrentContact&&BotCecilNativeContactFloor(player,ray,length))return true;
  if(!(support>.5))BotCecilRejectedProbe(probe,SCecilProbe::reasonUnsupportedNormal,player,&ray,&from,&to);
  return support>.5;
}
// Test the exact bounded action in the body/head frame before its floor probe.
static bool BotCecilClearMotion(CPlayer* player,double forward,double strafe,double up,double yaw,SCecilProbe* probe=NULL,bool requireFloor=true,bool allowCurrentContact=false){
  if(!BotCecilFrameReady(player)||!std::isfinite(forward)||!std::isfinite(strafe)||!std::isfinite(up)||
     !std::isfinite(yaw)||std::fabs(forward)>1.000001||std::fabs(strafe)>1.000001||std::fabs(up)>1.000001){
    BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;
  }
  const bool liquid=BotCecilLiquid(player);
  if(forward==0&&strafe==0&&(!liquid||up==0))
    return BotCecilFloor(player,forward,strafe,up,yaw,probe,allowCurrentContact);
  if(_botRayBudget<((liquid||!requireFloor)?1:2)){BotCecilRejectedProbe(probe,SCecilProbe::reasonBudget,player);return false;}
  const double angle=yaw*3.141592653589793/180;
  const auto world=BotCecilBodyFrame(player).ToWorld(-std::sin(angle)*forward+std::cos(angle)*strafe,
    liquid?up:0,-std::cos(angle)*forward-std::sin(angle)*strafe);
  const FLOAT3D from=player->GetPlacement().pl_PositionVector-player->en_vGravityDir*.8f;
  const FLOAT3D to=from+FLOAT3D((FLOAT)world.x,(FLOAT)world.y,(FLOAT)world.z)*1.5f;
  double length=0;
  if(!BotCecilRayLength(from,to,length)||length==0){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  --_botRayBudget;if(probe)++probe->wallRays;
  CCastRay ray(player,from,to);ray.cr_bPhysical=TRUE;ray.cr_bAllowOverHit=FALSE;
  ray.cr_ttHitModels=CCastRay::TT_COLLISIONBOX;
  if(!BotCecilPhysicalCast(ray,player->GetWorld())){BotCecilRejectedProbe(probe,SCecilProbe::reasonInvalid,player);return false;}
  if(ray.cr_penHit){BotCecilRejectedProbe(probe,SCecilProbe::reasonWallHit,player,&ray,&from,&to);return false;}
  return !requireFloor||BotCecilFloor(player,forward,strafe,up,yaw,probe,allowCurrentContact);
}
// Extended item attempts must not spend their full deadline circling one edge.
// This passive bound only rejects the item; the existing selector chooses the
// next typed/needed/allowed target and all subsequent movement keeps its guards.
static bool BotCecilItemTransitFailed(CPlayer* player,SSupplyState& s,double now,bool accepted,bool currentPoint){
  const auto& graph=BotSupplyGraph();
  int source=s.navigator.SourceSlot(s.goal),hop=s.hop;
  // A checkpoint only reapproaches the same original source. It must not give
  // an unsuccessful item a fresh no-progress clock every five seconds.
  const bool sourceApproach=source<0&&hop==s.itemTransitSource&&s.anchor==s.itemTransitSource;
  if(sourceApproach){source=s.itemTransitSource;hop=s.itemTransitHop;}
  bool eligible=accepted&&currentPoint&&s.playable&&s.goalEntity&&
    (s.mappedWeaponGoal||s.goalRelocationBudgeted)&&!s.followEntity&&s.interactionPoint<0&&
    (s.useReleaseTick<0||now>s.useReleaseTick*_pTimer->TickQuantum)&&
    player->GetWorld()&&player->GetHealth()>0&&player->m_penWeapons&&!(player->GetFlags()&ENF_DELETED)&&
    !BotCecilLiquid(player)&&(player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH||player->m_pstState==PST_FALL)&&
    std::isfinite(now)&&std::isfinite(s.goalSince)&&std::isfinite(s.goalDeadline)&&now>=s.goalSince&&now<s.goalDeadline&&
    source>=0&&hop>=0&&source!=hop&&(size_t)source<graph.points.size()&&(size_t)hop<graph.points.size()&&
    s.blocked.size()==graph.points.size()&&!s.blocked[source]&&!s.blocked[hop];
  double distance2=0,vertical=0,gravity2=0;
  if(eligible){
    const auto& a=graph.points[source];const auto& b=graph.points[hop];
    eligible=!a.flags&&!b.flags&&a.important_entity<0&&b.important_entity<0&&a.lock_entity<0&&b.lock_entity<0&&
      std::find(a.links.begin(),a.links.end(),hop)!=a.links.end();
    for(int i=1;i<=3;++i){
      const double d=(i==1?b.x:(i==2?b.y:b.z))-player->GetPlacement().pl_PositionVector(i),g=player->en_vGravityDir(i);
      eligible=eligible&&std::isfinite(d)&&std::isfinite(g)&&std::isfinite(player->en_vCurrentTranslationAbsolute(i));
      distance2+=d*d;vertical+=d*g;gravity2+=g*g;
    }
  }
  // Intentional vertical waits and special/terminal item actions keep their
  // existing policy. This watchdog only ends an ordinary intermediate attempt.
  eligible=eligible&&std::isfinite(distance2)&&std::isfinite(vertical)&&std::fabs(gravity2-1)<1e-3&&
    !(distance2-vertical*vertical<1&&std::fabs(vertical)>4);
  if(!eligible){s.ClearItemTransit();return false;}
  const double distance=std::sqrt(distance2);const long map=InterlockedCompareExchange(&_botSupplyMapSerial,0,0);
  bool same=s.itemTransitLast>=0&&now>=s.itemTransitLast&&now-s.itemTransitLast<=.25&&
    s.itemTransitWorld==player->GetWorld()&&s.itemTransitMap==map&&s.itemTransitEntity==player->en_ulID&&
    s.itemTransitGeneration==s.generation&&s.itemTransitItem==s.goalEntity&&s.itemTransitGoal==s.goal&&
    s.itemTransitSource==source&&s.itemTransitHop==hop&&s.itemTransitAttempt==s.goalSince&&s.itemTransitDeadline==s.goalDeadline;
  for(int i=0;i<3;++i)same=same&&s.itemTransitGravity[i]==player->en_vGravityDir(i+1);
  if(!same){
    s.itemTransitWorld=player->GetWorld();s.itemTransitMap=map;s.itemTransitEntity=player->en_ulID;
    s.itemTransitGeneration=s.generation;s.itemTransitItem=s.goalEntity;s.itemTransitGoal=s.goal;
    s.itemTransitSource=source;s.itemTransitHop=hop;s.itemTransitAttempt=s.goalSince;s.itemTransitDeadline=s.goalDeadline;
    s.itemTransitSince=now;s.itemTransitBest=s.itemTransitGainBase=distance;
    for(int i=0;i<3;++i)s.itemTransitGravity[i]=player->en_vGravityDir(i+1);
  }
  s.itemTransitLast=now;s.itemTransitBest=std::fmin(s.itemTransitBest,distance);
  if(s.itemTransitGainBase-s.itemTransitBest>=.75){s.itemTransitSince=now;s.itemTransitGainBase=s.itemTransitBest;}
  if(now-s.itemTransitSince+1e-9<10)return false;
  BotLog("[CecilItemTransitEnd] entity=%lu generation=%lu time=%.3f goal_entity=%lu goal=%d source=%d hop=%d since=%.3f best_distance=%.6f reason=no_hop_progress\n",
    (unsigned long)player->en_ulID,(unsigned long)s.generation,now,(unsigned long)s.goalEntity,s.goal,source,hop,s.itemTransitSince,s.itemTransitBest);
  s.RejectItem(s.goalEntity,now);s.ClearGoal();s.ClearEscape();s.searchAfter=now;s.scanTick=0;
  return true;
}
// Original BotMovement.cpp129..224 reacquires its nearest point every five
// seconds. Passive observation never authorizes movement: the checkpoint still
// needs current static ground and fresh nearest LOS. World wiggle is not gain.
static bool BotCecilHopCheckpoint(CPlayer* player,SSupplyState& s,double now,bool accepted,bool currentPoint){
  BotCecilSupplyDiagTerminal(player,s,now,accepted,currentPoint);
  if(BotCecilItemTransitFailed(player,s,now,accepted,currentPoint))return true;
  BotCecilPatrolObserve(player,s,now,accepted);
  const auto& graph=BotSupplyGraph();const int source=s.navigator.SourceSlot(s.goal),hop=s.hop;
  bool observeEligible=accepted&&currentPoint&&s.playable&&source>=0&&hop>=0&&source!=hop&&
    (size_t)source<graph.points.size()&&(size_t)hop<graph.points.size()&&
    graph.points.size()<=botcore::CecilNavGraph::kMaxPoints&&s.blocked.size()==graph.points.size()&&
    !s.blocked[source]&&!s.blocked[hop]&&!s.followEntity&&s.interactionPoint<0&&
    (s.useReleaseTick<0||now>s.useReleaseTick*_pTimer->TickQuantum)&&
    player->GetHealth()>0&&player->m_penWeapons&&player->GetWorld()&&!BotCecilLiquid(player)&&
    (player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH||player->m_pstState==PST_FALL);
  CEntity* ref=player->en_penReference;CWorld* world=player->GetWorld();
  observeEligible=observeEligible&&(!ref||(!(ref->GetFlags()&ENF_DELETED)&&
    ref->GetRenderType()==CEntity::RT_BRUSH&&ref->en_pwoWorld==world));
  double distance2=0,vertical=0,gravity2=0;
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  if(observeEligible){
    const auto& a=graph.points[source];const auto& b=graph.points[hop];
    const uint32_t special=botcore::CECIL_UNREACHABLE|botcore::CECIL_TELEPORT|botcore::CECIL_IMPORTANT|botcore::CECIL_JUMP;
    // An important destination does not exempt an ordinary intermediate edge.
    // Keep its terminal/special edge excluded; ordinary-goal flag policy is unchanged.
    observeEligible=(!s.importantGoal||!(a.flags|b.flags))&&
      !((a.flags|b.flags)&special)&&a.important_entity<0&&b.important_entity<0&&
      a.lock_entity<0&&b.lock_entity<0&&
      std::find(a.links.begin(),a.links.end(),hop)!=a.links.end();
    for(int i=1;i<=3;++i){
      const double d=(i==1?b.x:(i==2?b.y:b.z))-position(i),g=player->en_vGravityDir(i);
      observeEligible=observeEligible&&std::isfinite(d)&&std::isfinite(g)&&std::isfinite(player->en_vCurrentTranslationAbsolute(i));
      distance2+=d*d;vertical+=d*g;gravity2+=g*g;
    }
  }
  // The original vertical stay is intentional, not an ineffective approach.
  observeEligible=observeEligible&&std::isfinite(distance2)&&std::isfinite(vertical)&&std::isfinite(gravity2)&&
    std::fabs(gravity2-1)<1e-3&&!(distance2-vertical*vertical<1&&std::fabs(vertical)>4);
  if(!observeEligible){s.ClearHopCheckpoint();if(!accepted){s.acquiredAnchorTime=-1;s.acquiredAnchor=-1;}return false;}
  const double distance=std::sqrt(distance2);
  bool continuous=s.hopCheckpointLast>=0&&now>=s.hopCheckpointLast&&now-s.hopCheckpointLast<=.25&&
    s.hopCheckpointGoal==s.goal&&s.hopCheckpointSource==source&&s.hopCheckpointHop==hop&&
    s.hopCheckpointEntity==player->en_ulID&&s.hopCheckpointGeneration==s.generation&&s.hopCheckpointWorld==world;
  for(int i=0;i<3;++i)continuous=continuous&&s.hopCheckpointGravity[i]==player->en_vGravityDir(i+1);
  if(!continuous){
    s.hopCheckpointSince=now;s.hopCheckpointBest=s.hopCheckpointGainBase=distance;
    s.hopCheckpointGoal=s.goal;s.hopCheckpointSource=source;s.hopCheckpointHop=hop;
    s.hopCheckpointEntity=player->en_ulID;s.hopCheckpointGeneration=s.generation;s.hopCheckpointWorld=world;
    for(int i=0;i<3;++i)s.hopCheckpointGravity[i]=player->en_vGravityDir(i+1);
  }
  s.hopCheckpointLast=now;s.hopCheckpointBest=std::fmin(s.hopCheckpointBest,distance);
  if(s.hopCheckpointGainBase-s.hopCheckpointBest>=.75){s.hopCheckpointSince=now;s.hopCheckpointGainBase=s.hopCheckpointBest;}
  if(now-s.hopCheckpointSince+1e-9<5)return false;
  // FALL and the navigator's bounded STUCK action are observations only.
  // An expired clock still needs current normal ground travel before rebasing.
  if(!s.currentNavTravel||(player->m_pstState!=PST_STAND&&player->m_pstState!=PST_CROUCH))return false;
  // NULL/moving support can preserve observations, never supply authority.
  if(!ref||(ref->GetPhysicsFlags()&EPF_MOVABLE)||!BotCecilIsClass(ref,"WorldBase","World Base"))return false;
  // Wait for same-tick successful ordinary nearest LOS. Never force an extra
  // scan or treat a cached, merely nearby anchor as a fresh acquisition.
  const int anchor=s.anchor;
  if(s.acquiredAnchor!=anchor||std::fabs(now-s.acquiredAnchorTime)>1e-6)return false;
  if(anchor<0||(size_t)anchor>=graph.points.size()||s.blocked[anchor])return false;
  const auto& a=graph.points[anchor];const FLOAT3D delta(a.x-position(1),a.y-position(2),a.z-position(3));
  const double height=BotCecilHeight(player,delta),d2=double(delta(1))*delta(1)+double(delta(2))*delta(2)+double(delta(3))*delta(3);
  if(!std::isfinite(height)||!std::isfinite(d2)||std::fabs(height)>3||d2-height*height>144)return false;
  BotLog("[CecilHopCheckpoint] entity=%lu generation=%lu time=%.3f source=%d hop=%d goal=%d anchor=%d since=%.3f best_distance=%.6f current_distance=%.6f reset_reason=no_hop_progress\n",
    (unsigned long)player->en_ulID,(unsigned long)s.generation,now,source,hop,s.goal,anchor,
    s.hopCheckpointSince,s.hopCheckpointBest,distance);
  BotCecilPatrolStrike(player,s,now,source,hop,s.hopCheckpointBest);
  s.navigator.Reset();s.hop=s.heldNode=-1;s.holdSince=-1;s.currentNavTime=-1;s.currentNavGoal=-1;s.currentNavTravel=false;
  s.ClearEscape();s.ClearHopCheckpoint();return true;
}
// 1 original, 2 verified escape, 0 neutral. Hold world direction for 0.6s so a
// one-tick reverse does not immediately undo itself. No progress earns a cooldown.
template<class T>
static int BotCecilSafeMotion(CPlayer* player,SSupplyState& state,double now,T& forward,T& strafe,T& up,
                             double finalBodyYaw,double maxStrafe,bool useReacquire=true){
  state.probe=SCecilProbe();state.probe.inputForward=forward;state.probe.inputStrafe=strafe;
  state.probe.inputUp=up;state.probe.finalYaw=finalBodyYaw;
  if(!BotCecilFrameReady(player)||!std::isfinite(now)||now<0||!std::isfinite(maxStrafe)||maxStrafe<0||maxStrafe>1||
     !std::isfinite(forward)||!std::isfinite(strafe)||!std::isfinite(up)||!std::isfinite(finalBodyYaw)||
     std::fabs(forward)>1.000001||std::fabs(strafe)>1.000001||std::fabs(up)>1.000001){
    BotCecilRejectedProbe(&state.probe,SCecilProbe::reasonInvalid,player);
    forward=strafe=up=0;state.ClearEscape();state.ClearAirMovement();state.ClearGroundProgress();state.ClearHopCheckpoint();state.ClearItemTransit();state.ClearPatrolEpisode();state.acquiredAnchorTime=-1;state.acquiredAnchor=-1;return 0;
  }
  if(!useReacquire){state.ClearPatrolEpisode();state.ClearItemTransit();}
  if(state.patrolAlternate){
    BotCecilPatrolObserve(player,state,now,true);
    if(!state.patrolAlternate){forward=strafe=up=0;return 0;}
    if(now-state.patrolSince>=6){BotCecilPatrolFail(player,state,now,"deadline");forward=strafe=up=0;return 0;}
    const bool current=std::fabs(now-state.patrolProposalTime)<=1e-6&&BotCecilPatrolStatic(player)&&
      _botRayBudget>=2&&up==0&&state.patrolHint>=0;
    if(!current){forward=strafe=up=0;return 0;}
    double f=std::fmax(-.3,std::fmin(.3,(double)forward));
    double st=BotCecilSettings().bStrafe?std::fmax(-std::fmin(.3,maxStrafe),std::fmin(std::fmin(.3,maxStrafe),(double)strafe)):0;
    const double norm=std::hypot(f,st);if(norm>.3){f*=.3/norm;st*=.3/norm;}
    if(norm<.05||!BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,true,false)){forward=strafe=up=0;return 0;}
    forward=(T)f;strafe=(T)st;up=0;return 1;
  }
  // Cecil BotMovement.cpp517: pits are opt-in and checked only without a
  // current path point. Arrival still owns that point for the final item connector.
  // Clear/reset/failed updates and changed goals must never retain an exemption.
  const size_t nodes=BotSupplyGraph().points.size();
  if(!useReacquire)state.ClearAirMovement();
  const bool offgraphAir=state.anchor<0&&player->m_pstState==PST_FALL&&
    !state.navigator.HasCommittedEdge(state.goal)&&!BotCecilSettings().bAvoidPits;
  if(useReacquire&&(offgraphAir||state.airMovementTime>=0)){
    // Original follow/path motion also steers in air. This is a single fresh
    // hint proposal, never a ground proof, watchdog escape or remembered hold.
    const int node=state.airMovementNode;
    bool current=offgraphAir&&std::fabs(now-state.airMovementTime)<=1e-6&&
      state.airMovementEntity==player->en_ulID&&state.airMovementGeneration==state.generation&&
      state.reacquiring&&state.reacquireNode==node&&node>=0&&(size_t)node<nodes&&
      nodes<=botcore::CecilNavGraph::kMaxPoints&&state.blocked.size()==nodes&&!state.blocked[node]&&
      player->GetWorld()&&player->GetHealth()>0&&player->m_penWeapons&&!BotCecilLiquid(player)&&up==0;
    for(int i=1;current&&i<=3;++i)current=std::isfinite(player->en_vCurrentTranslationAbsolute(i))&&
      state.airMovementGravity[i-1]==player->en_vGravityDir(i);
    if(current){
      const auto& point=BotSupplyGraph().points[node];const auto& pos=player->GetPlacement().pl_PositionVector;
      const FLOAT3D delta(point.x-pos(1),point.y-pos(2),point.z-pos(3));
      const double d=double(delta(1))*delta(1)+double(delta(2))*delta(2)+double(delta(3))*delta(3);
      current=std::isfinite(point.radius)&&point.radius>0&&std::isfinite(d)&&d<=1024&&
        std::fabs(BotCecilHeight(player,delta))<=8;
    }
    state.ClearGroundProgress();state.ClearEscape();state.ClearHopCheckpoint();state.ClearItemTransit(); // Accepted air owns no legacy escape direction.
    if(!current){forward=strafe=up=0;state.ClearAirMovement();return 0;}
    double f=std::fmax(-.3,std::fmin(.3,(double)forward)),st=BotCecilSettings().bStrafe?
      std::fmax(-std::fmin(.3,maxStrafe),std::fmin(std::fmin(.3,maxStrafe),(double)strafe)):0;
    const double length=std::hypot(f,st);if(length>.3){f*=.3/length;st*=.3/length;}
    if(std::hypot(f,st)<.05||!BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,false,false)){
      forward=strafe=up=0;return 0;
    }
    forward=(T)f;strafe=(T)st;up=0;
    if(((int)std::floor(now*20+.5))%20==0)
      BotLog("[CecilAirRecovery] entity=%lu generation=%lu time=%.3f action=steer hint=%d since=%.3f support_authorized=0 pit_avoidance=0 floor_required=0 forward=%.3f strafe=%.3f\n",
        (unsigned long)player->en_ulID,(unsigned long)state.generation,now,node,state.reacquireSince,f,st);
    return 1;
  }
  const bool currentPoint=std::fabs(now-state.currentNavTime)<=1e-6&&state.currentNavGoal==state.goal&&state.goal>=0&&(size_t)state.goal<nodes&&
    state.hop>=0&&(size_t)state.hop<nodes&&state.blocked.size()==nodes&&!state.blocked[state.hop];
  if(BotCecilHopCheckpoint(player,state,now,useReacquire,currentPoint)){forward=strafe=up=0;return 0;}
  // The planner can propose recovery while visible combat owns the final input.
  // Recovery-only limits belong to accepted movement, not the retained proposal.
  const bool recoveryContext=state.anchor<0||(state.anchor<(int)nodes&&state.goal<0);
  const bool groundEligible=useReacquire&&recoveryContext&&std::fabs(now-state.groundRecoveryTime)<=1e-6&&
    _botRayBudget>=2&&player->GetHealth()>0&&player->m_penWeapons&&
    (player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH);
  const bool groundObserved=useReacquire&&recoveryContext&&std::fabs(now-state.groundObservationTime)<=1e-6&&
    player->GetHealth()>0&&player->m_penWeapons&&
    (player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH);
  if(state.groundProgressEntity!=player->en_ulID||state.groundProgressGeneration!=state.generation){
    state.groundProgress.Reset();state.ClearGroundSweep();state.groundEscapeAfter=0;state.groundStalled=false;
    if(state.groundEscapeActive)state.ClearEscape();
    state.groundEscapeActive=false;
    state.groundProgressEntity=player->en_ulID;state.groundProgressGeneration=state.generation;
  }
  const auto& groundPosition=player->GetPlacement().pl_PositionVector;
  const bool observedStalled=state.groundProgress.Update(now,{groundPosition(1),groundPosition(2),groundPosition(3)},
    {player->en_vGravityDir(1),player->en_vGravityDir(2),player->en_vGravityDir(3)},groundObserved);
  // Original NoPosChange is not restricted to missing NAV anchors. With Cecil's
  // default pit policy a current accepted stationary pose may move without a
  // floor claim; opt-in avoidance still needs fresh support and final floor.
  const bool defaultMovement=groundObserved&&std::fabs(now-state.recoveryMovementTime)<=1e-6&&
    !BotCecilSettings().bAvoidPits&&_botRayBudget>=1;
  const bool recoveryEligible=groundEligible||defaultMovement;
  const bool stalled=observedStalled&&recoveryEligible;
  if(!observedStalled){
    state.ClearGroundSweep();state.groundEscapeAfter=0;
    // Real progress resets the detector, but a verified, still-owned escape
    // finishes its original world-direction hold rather than undoing the step.
    if(state.groundEscapeActive&&(!groundObserved||!state.groundProgress.Continuous()||now>=state.escapeUntil)){
      state.ClearEscape();state.groundEscapeActive=false;
    }
  }else if(!state.groundStalled){
    BotLog("[CecilGroundRecovery] entity=%lu generation=%lu time=%.3f action=stall eligible=%d support_authorized=%d pit_avoidance=%d reason=no_position_progress node=%d stationary=%.3f displacement=%.4f\n",
      (unsigned long)player->en_ulID,(unsigned long)state.generation,now,recoveryEligible,groundEligible,BotCecilSettings().bAvoidPits,state.reacquireNode,state.groundProgress.StationarySeconds(),state.groundProgress.Displacement());
  }
  state.groundStalled=observedStalled;
  if(!recoveryEligible&&(observedStalled||state.groundEscapeActive)){
    // Pause only the emitted action. The verified world hold keeps its original
    // expiry and must pass current movement policy plus fresh physical checks.
    forward=strafe=up=0;return 0;
  }
  const bool actualReacquire=useReacquire&&(state.reacquiring||stalled||(recoveryEligible&&state.groundEscapeActive));
  const bool allowCurrentContact=groundEligible&&(stalled||state.groundEscapeActive);
  const bool defaultRecovery=defaultMovement&&(stalled||state.groundEscapeActive);
  const bool requireFloor=!BotCecilLiquid(player)&&((actualReacquire&&!defaultRecovery)||(BotCecilSettings().bAvoidPits&&!currentPoint));
  const double maxForward=actualReacquire?.3:1;
  if(actualReacquire)maxStrafe=std::fmin(maxStrafe,.3);
  auto capMotion=[&](double& f,double& st){
    f=std::fmax(-maxForward,std::fmin(maxForward,f));st=std::fmax(-maxStrafe,std::fmin(maxStrafe,st));
    const double length=std::hypot(f,st);
    if(actualReacquire&&length>.3){f*=.3/length;st*=.3/length;}
  };
  if(now<state.escapeClock)state.ClearEscape();
  state.escapeClock=now;
  double requestedForward=forward,requestedStrafe=strafe;capMotion(requestedForward,requestedStrafe);
  forward=(T)requestedForward;strafe=(T)requestedStrafe;
  const bool neutralRequest=std::fabs(forward)+std::fabs(strafe)+std::fabs(up)<.05;
  if(neutralRequest&&!stalled&&!(recoveryEligible&&state.groundEscapeActive&&now<state.escapeUntil)){
    state.escapeUntil=0;forward=strafe=up=0;return 1;
  }
  const auto frame=BotCecilBodyFrame(player);
  const FLOAT3D position=player->GetPlacement().pl_PositionVector;
  const double angle=finalBodyYaw*3.141592653589793/180,si=std::sin(angle),co=std::cos(angle);
  // Ground sweeps name fixed WORLD sectors, not indices relative to a changing
  // planner request/yaw. Disabled strafe instead permits only current body +/-F.
  const bool bodyOnly=maxStrafe==0;
  const auto bodyHeading=frame.ToWorld(-si,0,-co);
  const double gravityNorm=std::sqrt(double(player->en_vGravityDir(1))*player->en_vGravityDir(1)+
    double(player->en_vGravityDir(2))*player->en_vGravityDir(2)+double(player->en_vGravityDir(3))*player->en_vGravityDir(3));
  const botcore::CecilVec gravity{player->en_vGravityDir(1)/gravityNorm,player->en_vGravityDir(2)/gravityNorm,player->en_vGravityDir(3)/gravityNorm};
  const double vertical=bodyHeading.x*gravity.x+bodyHeading.y*gravity.y+bodyHeading.z*gravity.z;
  botcore::CecilVec heading{bodyHeading.x-vertical*gravity.x,bodyHeading.y-vertical*gravity.y,bodyHeading.z-vertical*gravity.z};
  const double headingNorm=std::sqrt(heading.x*heading.x+heading.y*heading.y+heading.z*heading.z);
  if((stalled||state.groundEscapeActive)&&(!std::isfinite(headingNorm)||headingNorm<1e-6)){
    BotCecilRejectedProbe(&state.probe,SCecilProbe::reasonInvalid,player);forward=strafe=up=0;return 0;
  }
  if(headingNorm>0){heading.x/=headingNorm;heading.y/=headingNorm;heading.z/=headingNorm;}
  if((stalled||state.groundEscapeActive)&&(state.groundSweepReady||state.groundEscapeActive)){
    const double dx=heading.x-state.groundSweepForward[0],dy=heading.y-state.groundSweepForward[1],dz=heading.z-state.groundSweepForward[2];
    // Recover the captured gravity normal from its two tangent basis axes. Even
    // a turn below the position-clock tolerance changes world-sector identity.
    const double gx=state.groundSweepForward[1]*state.groundSweepRight[2]-state.groundSweepForward[2]*state.groundSweepRight[1]-gravity.x,
      gy=state.groundSweepForward[2]*state.groundSweepRight[0]-state.groundSweepForward[0]*state.groundSweepRight[2]-gravity.y,
      gz=state.groundSweepForward[0]*state.groundSweepRight[1]-state.groundSweepForward[1]*state.groundSweepRight[0]-gravity.z;
    // Body-only axes must rebind even after a small turn: no strafe is available
    // to represent the previous world axis. Preserve the existing cooldown.
    if(bodyOnly!=state.groundSweepBodyOnly||gx*gx+gy*gy+gz*gz>1e-24||(bodyOnly&&dx*dx+dy*dy+dz*dz>1e-24)){
      if(state.groundEscapeActive)state.ClearEscape();
      state.groundEscapeActive=false;state.ClearGroundSweep();
    }
  }
  if(stalled&&!state.groundSweepReady){
    const botcore::CecilVec right{gravity.y*heading.z-gravity.z*heading.y,
      gravity.z*heading.x-gravity.x*heading.z,gravity.x*heading.y-gravity.y*heading.x};
    state.groundSweepForward[0]=heading.x;state.groundSweepForward[1]=heading.y;state.groundSweepForward[2]=heading.z;
    state.groundSweepRight[0]=right.x;state.groundSweepRight[1]=right.y;state.groundSweepRight[2]=right.z;
    state.groundSweepReady=true;state.groundSweepBodyOnly=bodyOnly;
  }
  auto capGround=[&](double& f,double& st){
    // Roundoff on an exactly body-aligned direction is not a strafe request.
    if(std::fabs(st)<1e-12)st=0;
    double scale=1;const double norm=std::hypot(f,st);
    if(norm>.3)scale=.3/norm;
    if(std::fabs(st)>maxStrafe)scale=std::fmin(scale,maxStrafe/std::fabs(st));
    f*=scale;st*=scale;
    return std::isfinite(f)&&std::isfinite(st)&&std::hypot(f,st)>0;
  };
  auto groundLocal=[&](double x,double y,double z,double& f,double& st){
    const double norm=std::sqrt(x*x+y*y+z*z);const auto local=frame.ToLocal(x,y,z);
    // A transient body/gravity mismatch must not project a remembered sector
    // into a different world heading or add vertical motion with up=0.
    if(!std::isfinite(norm)||norm<=0||std::fabs(x*gravity.x+y*gravity.y+z*gravity.z)>norm*1e-6||
       std::fabs(local.y)>norm*1e-6)return false;
    f=-si*local.x-co*local.z;st=co*local.x-si*local.z;return capGround(f,st);
  };
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
      double f=-si*local.x-co*local.z,st=co*local.x-si*local.z;
      const bool held=state.groundEscapeActive?groundLocal(state.escapeWorld[0],state.escapeWorld[1],state.escapeWorld[2],f,st):
        (capMotion(f,st),std::fabs(f)+std::fabs(st)>.05);
      if(held&&BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,requireFloor,allowCurrentContact)){
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
  const bool originalClear=!neutralRequest&&BotCecilClearMotion(player,forward,strafe,up,finalBodyYaw,&state.probe,requireFloor,allowCurrentContact);
  if(originalClear&&!stalled)return 1;
  const bool originalNoFloor=!neutralRequest&&!originalClear&&state.probe.primaryReason==SCecilProbe::reasonNoFloor;
  if(stalled&&now+1e-9<state.groundEscapeAfter){forward=strafe=up=0;return 0;}
  if(now<state.escapeAfter){forward=strafe=up=0;return 0;}
  // A blocked diagonal need not block its already selected liquid vertical axis.
  // This is a fresh component query, never extra intent or ground authority.
  const unsigned liquidUncertain=(1u<<SCecilProbe::reasonBudget)|(1u<<SCecilProbe::reasonInvalid);
  if(useReacquire&&currentPoint&&state.currentNavTravel&&BotCecilLiquid(player)&&
     state.playable&&state.entity==player->en_ulID&&player->GetWorld()&&
     !(player->GetFlags()&ENF_DELETED)&&std::isfinite(player->GetHealth())&&player->GetHealth()>0&&player->m_penWeapons&&
     !state.followEntity&&state.interactionPoint<0&&
     (state.useReleaseTick<0||now>state.useReleaseTick*_pTimer->TickQuantum)&&
     std::isfinite(player->en_vCurrentTranslationAbsolute(1))&&std::isfinite(player->en_vCurrentTranslationAbsolute(2))&&
     std::isfinite(player->en_vCurrentTranslationAbsolute(3))&&requestedLength>.05&&std::fabs(up)>=.05&&
     !originalClear&&state.probe.primaryReason==SCecilProbe::reasonWallHit&&
     !(state.probe.reasonMask&liquidUncertain)&&_botRayBudget>2&&
     BotCecilClearMotion(player,0,0,up,finalBodyYaw,&state.probe,false,false)){
    forward=strafe=0;state.ClearEscape();return 1;
  }
  // Only this branch tested the original request. Held-escape failures return
  // above; deferred/uncertain probes or an approved escape preserve its target.
  auto rejectOriginal=[&](){
    const unsigned uncertain=(1u<<SCecilProbe::reasonBudget)|(1u<<SCecilProbe::reasonInvalid);
    const int node=state.reacquireNode;
    if(originalNoFloor&&actualReacquire&&(player->m_pstState==PST_STAND||player->m_pstState==PST_CROUCH)&&
       state.probe.primaryReason==SCecilProbe::reasonNoFloor&&
       !(state.probe.reasonMask&uncertain)&&nodes<=botcore::CecilNavGraph::kMaxPoints&&
       node>=0&&(size_t)node<nodes&&state.blocked.size()==nodes&&!state.blocked[node]){
      double speed2=0;bool stationary=true;
      for(int i=1;i<=3;++i){const double v=player->en_vCurrentTranslationAbsolute(i);
        stationary=stationary&&std::isfinite(v);speed2+=v*v;}
      const auto& point=BotSupplyGraph().points[node];
      const FLOAT3D delta(point.x-position(1),point.y-position(2),point.z-position(3));
      const double height=BotCecilHeight(player,delta);
      const double x=delta(1)-player->en_vGravityDir(1)*height,
        y=delta(2)-player->en_vGravityDir(2)*height,z=delta(3)-player->en_vGravityDir(3)*height;
      const double targetNorm=std::sqrt(x*x+y*y+z*z),
        requestNorm=std::sqrt(requested.x*requested.x+requested.y*requested.y+requested.z*requested.z);
      bool aligned=false;
      if(std::isfinite(targetNorm)&&targetNorm>0&&std::isfinite(requestNorm)&&requestNorm>0){
        const double alignment=(requested.x*x+requested.y*y+requested.z*z)/(requestNorm*targetNorm);
        aligned=std::isfinite(alignment)&&alignment>=.9998476951563913;
      }
      // A turning/projected action is not evidence against the eventual target
      // direction. Only a stationary, aligned (<=1 degree) approach may reject it.
      if(stationary&&std::isfinite(speed2)&&speed2<=.01&&aligned){
        state.reacquireTried[node/8]|=(unsigned char)(1u<<(node%8));
        state.reacquireNode=-1;state.reacquireSince=-1;state.ClearEscape();
        BotLog("[CecilReacquireReject] entity=%lu generation=%lu time=%.3f node=%d reason=no_floor\n",
          (unsigned long)state.entity,(unsigned long)state.generation,now,node);
      }
    }
    forward=strafe=up=0;return 0;
  };
  if(stalled){
    // Original NoPosChange repeats; permanently exhausting a finite tried mask
    // is an adapter liveness bug. Eight bounded world sectors form one pass.
    // A new pass retains the same pose clock/basis and all NAV/goal deadlines.
    const unsigned count=bodyOnly?2:8;
    if(state.groundEscapeCursor>=count){state.groundEscapeCursor=0;state.groundEscapeTried=0;}
    const double directions[8][2]={{1,0},{1,1},{0,1},{-1,1},{-1,0},{-1,-1},{0,-1},{1,-1}};
    for(unsigned n=0;n<count&&state.groundEscapeCursor<count;++n){
      const unsigned i=state.groundEscapeCursor;
      const double a=bodyOnly?(i==0?.3:-.3):.3*directions[i][0]/std::hypot(directions[i][0],directions[i][1]);
      const double b=bodyOnly?0:.3*directions[i][1]/std::hypot(directions[i][0],directions[i][1]);
      double f=0,st=0;
      if(!groundLocal(a*state.groundSweepForward[0]+b*state.groundSweepRight[0],
          a*state.groundSweepForward[1]+b*state.groundSweepRight[1],a*state.groundSweepForward[2]+b*state.groundSweepRight[2],f,st)){
        BotCecilRejectedProbe(&state.probe,SCecilProbe::reasonInvalid,player);return rejectOriginal();
      }
      const bool clear=BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,requireFloor,allowCurrentContact);
      if(!clear&&(state.probe.lastReason==SCecilProbe::reasonBudget||state.probe.lastReason==SCecilProbe::reasonInvalid))return rejectOriginal();
      // A definite wall/floor rejection is an observed sector too. Retaining
      // the cursor across budget deferral prevents early blocked rays starving
      // the remaining sectors. No bit is consumed by an uncertain query.
      state.groundEscapeTried|=1u<<i;++state.groundEscapeCursor;
      if(clear){
        const auto world=frame.ToWorld(-si*f+co*st,0,-co*f-si*st);
        state.escapeWorld[0]=world.x;state.escapeWorld[1]=world.y;state.escapeWorld[2]=world.z;
        for(int j=0;j<3;++j)state.escapeOrigin[j]=position(j+1);
        state.groundEscapeActive=true;state.groundEscapeAfter=now+1.6;
        state.escapeUntil=now+.6;forward=(T)f;strafe=(T)st;up=0;
        BotLog("[CecilGroundRecovery] entity=%lu generation=%lu time=%.3f action=escape eligible=1 support_authorized=%d pit_avoidance=%d floor_required=%d reason=no_position_progress dir=%u forward=%.3f strafe=%.3f stationary=%.3f displacement=%.4f\n",
          (unsigned long)player->en_ulID,(unsigned long)state.generation,now,groundEligible,BotCecilSettings().bAvoidPits,requireFloor,i,f,st,state.groundProgress.StationarySeconds(),state.groundProgress.Displacement());
        return 2;
      }
    }
    if(state.groundEscapeCursor>=count)state.groundEscapeAfter=now+1.6;
    state.escapeAfter=now+.3;return rejectOriginal();
  }
  const double length=std::hypot((double)forward,(double)strafe);
  const double side=std::fmin(.4,maxStrafe)*(stalled?1:state.escapeSide);
  // Legacy non-stalled escape path retained unchanged. Ground stalls returned
  // through the complete world sweep above; the old stalled clauses are inert.
  const double candidates[5][2]={{0,side},{0,-side},{length>.05?-.4*forward/length:(stalled?-.3:0),length>.05?-.4*strafe/length:0},
    {-.3,side},{-.3,-side}};
  for(int i=0;i<5;++i){
    if(i>=3&&(!stalled||std::fabs(side)<1e-9))continue;
    // Each approved direction is tried once per physical stationary episode,
    // even when the planner's six-second target cycle clears its escape hold.
    if(stalled&&(state.groundEscapeTried&(1u<<i)))continue;
    if(i==2&&state.escapeReverseUsed)continue;
    double f=candidates[i][0],st=candidates[i][1];capMotion(f,st);
    if(std::fabs(f)+std::fabs(st)<.05)continue;
    if(BotCecilClearMotion(player,f,st,0,finalBodyYaw,&state.probe,requireFloor,allowCurrentContact)){
      // Record backward motion for the ordinary straight-retreat guard. Each
      // stalled diagonal has its own once-per-episode tried bit above.
      if(i>=2){
        state.escapeReverseUsed=true;
        for(int j=0;j<3;++j)state.escapeBlockPosition[j]=position(j+1);
        const auto direction=requestedLength>.05?botcore::CecilVec{requested.x/requestedLength,requested.y/requestedLength,requested.z/requestedLength}:
          frame.ToWorld(-si,0,-co); // Explicit body-forward seed for a neutral backstep.
        state.escapeRequest[0]=direction.x;state.escapeRequest[1]=direction.y;state.escapeRequest[2]=direction.z;
      }
      if(stalled){
        state.groundEscapeTried|=1u<<i;state.groundEscapeActive=true;state.groundEscapeAfter=now+1.6;
        BotLog("[CecilGroundRecovery] entity=%lu generation=%lu time=%.3f action=escape eligible=1 support_authorized=%d pit_avoidance=%d floor_required=%d reason=no_position_progress dir=%d forward=%.3f strafe=%.3f stationary=%.3f displacement=%.4f\n",
          (unsigned long)player->en_ulID,(unsigned long)state.generation,now,groundEligible,BotCecilSettings().bAvoidPits,requireFloor,i,f,st,state.groundProgress.StationarySeconds(),state.groundProgress.Displacement());
      }
      const auto world=frame.ToWorld(-si*f+co*st,0,-co*f-si*st);
      state.escapeWorld[0]=world.x;state.escapeWorld[1]=world.y;state.escapeWorld[2]=world.z;
      for(int j=0;j<3;++j)state.escapeOrigin[j]=position(j+1);
      state.escapeUntil=now+.6;forward=(T)f;strafe=(T)st;up=0;return 2;
    }
  }
  state.escapeAfter=now+.3;return rejectOriginal();
}
#endif
