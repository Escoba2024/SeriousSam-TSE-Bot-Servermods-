/* SeriousSam TSE Bot Project: GameMP-only bot-client integration.
 * Modified 2026-10-08 through 2026-10-11; publication notice 2026-10-12.
 * Original captured source and published hashes: docs/reports/2026-10-12-source-verification.json.
 * GPL-2.0-only; existing upstream copyright notices are retained. */
/* A "Pfad D" proof-of-concept bot driver for Serious Sam: TSE.
 * (sample code for the vanilla-compatible bot client; see VERIFIKATION.md)
 *
 * Behavior (PoC, no AI): every local player walks forward at full speed,
 * slowly rotates its heading and fires in periodic pulses. All state that
 * the server and other clients see is produced exclusively through the
 * regular action pipeline:
 *
 *   CPlayerSource::SetAction()  ->  WriteActionPacket()  ->  (network)
 *   ->  CPlayerBuffer / MSG_SEQ_ALLACTIONS  ->  CPlayerTarget::ApplyActionPacket()
 *   ->  CPlayerEntity::ApplyAction()
 *
 * Conventions replicated from the vanilla code (see Player.es):
 *  - pa_vTranslation is a VELOCITY: full forward = -plr_fSpeedForward (z<0!)
 *  - pa_aRotation / pa_aViewRotation are ABSOLUTE accumulated angles
 *    (relative to the spawn orientation) - they must NOT wrap, because
 *    CPlayerEntity::ApplyAction() computes deltas against the last action.
 *  - pa_ulButtons uses the PLACT_* flags of Player.es (bit 0 = fire).
 *  - pa_llCreated is stamped by CPlayerSource::SetAction() itself.
 */

#include "StdAfx.h"
#include <Engine/Network/Network.h>
#include <Engine/Entities/Entity.h>
#include "Game.h"
#include "BotDriver.h"
#include "botcore.h"
#include "bot_reconnect.h"
#include "bot_combat.h"
#include "bot_weapon_input.h"
#include "bot_navigation.h"
#include <Engine/World/WorldRayCasting.h>
#include "SessionProperties.h"
#include <cstdarg>
#include <cstdio>
#include <EntitiesV/PlayerWeapons.h>

// Engine CTString::VPrintF shares a static buffer with the renderer. Timer
// diagnostics must format locally, then use the synchronized console writer.
static void BotLog(const char *format, ...) {
  char text[2048];
  va_list args;
  va_start(args, format);
  std::vsnprintf(text, sizeof(text), format, args);
  va_end(args);
  CPutString(text);
}

/* ------------------------------------------------------------------------ */
/* Console symbols                                                            */
/* ------------------------------------------------------------------------ */

static INDEX bot_bEnabled    = FALSE;   // master switch
static FLOAT bot_fYawSpeed   = 45.0f;   // [deg/s] heading change rate (0 = straight)
static FLOAT bot_fMoveFactor = 1.0f;    // [0..1] fraction of plr_fSpeedForward
static FLOAT bot_fFirePeriod = 1.0f;    // [s] fire pulse period (0 = never fire)
static INDEX bot_iFireTicks  = 3;       // fire pulse length in ticks (20 ticks = 1 s)
static INDEX bot_iLogEvery   = 40;      // status log every N ticks (0 = off)
static INDEX bot_bDiagnostics = FALSE; // read-only player snapshots for Phase 1
static INDEX bot_iTestTarget = -1;     // fixed player index, -1 = original PoC
static INDEX bot_bTestThirdPerson = FALSE; // native view action for spectator QA
static INDEX bot_bAutoCombat = FALSE; // optional deathmatch decisions
static INDEX bot_bCombatSkipLocals = TRUE; // siblings share one bot client
static INDEX bot_bObstacleAvoidance = FALSE; // optional reactive movement recovery

static botcore::Reconnect _botReconnect;
static CTString _strBotReconnectAddress;
static volatile LONG _botNavigationResetRequested=FALSE;

void BotDriver_StopGame(void)
{
  // StopGame can run on the main thread while the timer owns slot state.
  // Publish only the request; consume it before the next bot action.
  InterlockedExchange(&_botNavigationResetRequested,TRUE);
  // JoinGame itself calls StopGame: preserve only that in-flight recovery.
  // An explicit stop between attempts cancels pending retries.
  _botReconnect.OnStop();
}

void BotDriver_CancelReconnect(void)
{
  _botReconnect.Reset();
}

static BOOL BotDriver_ReconnectAbortRequested(void)
{
  if (GetAsyncKeyState(VK_ESCAPE)&0x8001) { return TRUE; }
  MSG msg;
  if (PeekMessage(&msg, NULL, WM_QUIT, WM_QUIT, PM_NOREMOVE) ||
      PeekMessage(&msg, NULL, WM_CLOSE, WM_CLOSE, PM_NOREMOVE)) {
    return TRUE; // leave close/quit for the native outer message loop
  }
  // Consume and dispatch earlier system commands so they cannot hide SC_CLOSE.
  while (PeekMessage(&msg, NULL, WM_SYSCOMMAND, WM_SYSCOMMAND, PM_REMOVE)) {
    // WM_QUIT bypasses PeekMessage's filter, including a quit posted while
    // dispatching an earlier system command. Preserve its original exit code.
    if (msg.message==WM_QUIT) {
      PostQuitMessage((int)msg.wParam);
      return TRUE;
    }
    if ((msg.wParam&0xFFF0)==SC_CLOSE) {
      PostMessage(msg.hwnd, msg.message, msg.wParam, msg.lParam);
      return TRUE;
    }
    TranslateMessage(&msg);
    DispatchMessage(&msg);
  }
  return FALSE;
}

BOOL BotDriver_HandleReconnect(CGame *pgame)
{
  if (!bot_bEnabled || pgame==NULL) {
    _botReconnect.Reset();
    return FALSE; // retain the original SDK path when bot mode is disabled
  }
  if (_strBotReconnectAddress!=pgame->gam_strJoinAddress) {
    _botReconnect.Reset();
    _strBotReconnectAddress=pgame->gam_strJoinAddress;
  }
  const BOOL gameOn=pgame->gm_bGameOn;
  if (!_botReconnect.Poll(_pTimer->GetHighPrecisionTimer().GetSeconds(),
      TRUE, gameOn, gameOn && _pNetwork->IsServer(),
      gameOn && _pNetwork->IsGameFinished(),
      gameOn && _pNetwork->IsDisconnected(), _strBotReconnectAddress.Length()>0)) {
    return TRUE;
  }
  do {
    BotLog("[BotReconnect] attempt address=%s\n", (const char *)_strBotReconnectAddress);
    BOOL joined=FALSE;
    try {
      joined=pgame->JoinGame(CNetworkSession(_strBotReconnectAddress));
    } catch (...) {
      _botReconnect.Reset();
      throw; // preserve the failure; never leave a permanently in-flight retry
    }
    _botReconnect.OnResult(_pTimer->GetHighPrecisionTimer().GetSeconds(), joined!=FALSE);
    BotLog("[BotReconnect] result=%s\n", joined ? "joined" : "failed");
    if (joined) { return TRUE; }
    // Returning with gameOn=false makes the retail EXE stop GameMainLoop.
    // Keep recovery on its existing main-thread stack, never on the timer.
    while (_botReconnect.HasPending()) {
      if (!bot_bEnabled || _strBotReconnectAddress!=pgame->gam_strJoinAddress ||
          BotDriver_ReconnectAbortRequested()) {
        _botReconnect.Reset();
        return TRUE;
      }
      // PeekMessage may synchronously deliver a StopGame cancellation.
      if (!_botReconnect.HasPending()) { return TRUE; }
      if (_botReconnect.Poll(_pTimer->GetHighPrecisionTimer().GetSeconds(),
          TRUE, FALSE, FALSE, FALSE, FALSE, TRUE)) { break; }
      Sleep(50);
    }
  } while (_botReconnect.HasPending());
  return TRUE;
}

void BotDriver_Init(void)
{
  _pShell->DeclareSymbol("user INDEX bot_bEnabled;",    &bot_bEnabled);
  _pShell->DeclareSymbol("user FLOAT bot_fYawSpeed;",   &bot_fYawSpeed);
  _pShell->DeclareSymbol("user FLOAT bot_fMoveFactor;", &bot_fMoveFactor);
  _pShell->DeclareSymbol("user FLOAT bot_fFirePeriod;", &bot_fFirePeriod);
  _pShell->DeclareSymbol("user INDEX bot_iFireTicks;",  &bot_iFireTicks);
  _pShell->DeclareSymbol("user INDEX bot_iLogEvery;",   &bot_iLogEvery);
  _pShell->DeclareSymbol("user INDEX bot_bDiagnostics;", &bot_bDiagnostics);
  _pShell->DeclareSymbol("user INDEX bot_iTestTarget;", &bot_iTestTarget);
  _pShell->DeclareSymbol("user INDEX bot_bTestThirdPerson;", &bot_bTestThirdPerson);
  _pShell->DeclareSymbol("user INDEX bot_bAutoCombat;", &bot_bAutoCombat);
  _pShell->DeclareSymbol("user INDEX bot_bCombatSkipLocals;", &bot_bCombatSkipLocals);
  _pShell->DeclareSymbol("user INDEX bot_bObstacleAvoidance;", &bot_bObstacleAvoidance);
}

/* ------------------------------------------------------------------------ */
/* Per-local-player bot state                                                 */
/* ------------------------------------------------------------------------ */

struct SBotState {
  CPlayerSource *bs_ppls;     // player source this state belongs to
  ANGLE  bs_aHeading;         // accumulated heading (relative to spawn direction)
  INDEX  bs_iTick;            // ticks since (re)join
  ANGLE  bs_aPitch;
  INDEX  bs_iCombatTarget;
  botcore::CombatWeaponInput bs_weaponInput;
  botcore::ObstacleRecovery bs_navigation;
  CPlayer *bs_navPlayer;
};

static SBotState _absBots[4] = {
  {NULL, 0.0f, 0}, {NULL, 0.0f, 0}, {NULL, 0.0f, 0}, {NULL, 0.0f, 0},
};

static void BotResetNavigation(void)
{
  for (INDEX slot=0; slot<4; ++slot) {
    _absBots[slot].bs_navigation.Reset();
    _absBots[slot].bs_navPlayer=NULL;
  }
}

static CPlacement3D BotCombatEye(CPlayer *player)
{
  CPlacement3D eye=player->en_plViewpoint;
  eye.RelativeToAbsolute(player->en_plPlacement);
  return eye;
}

static BOOL BotCombatIsLocal(CGame *game, INDEX index)
{
  for (INDEX i=0; i<4; ++i) {
    CPlayerSource *source=game->gm_lpLocalPlayers[i].lp_pplsPlayerSource;
    if (source!=NULL && source->pls_Index==index) return TRUE;
  }
  return FALSE;
}

static botcore::TargetInfo BotCombatSnapshot(CPlayer *player, INDEX index, BOOL local)
{
  const FLOAT3D position=BotCombatEye(player).pl_PositionVector;
  const botcore::TargetInfo snapshot={index,position(1),position(2),position(3),
    player->GetHealth(),local!=FALSE};
  return snapshot;
}

static BOOL BotCombatVisible(CPlayer *player, CPlayer *target)
{
  const FLOAT3D origin=BotCombatEye(player).pl_PositionVector;
  const FLOAT3D destination=BotCombatEye(target).pl_PositionVector;
  CCastRay ray(player,origin,destination);
  ray.cr_bAllowOverHit=FALSE;
  ray.cr_ttHitModels=CCastRay::TT_COLLISIONBOX;
  ray.Cast(player->GetWorld());
  return ray.cr_penHit==NULL || ray.cr_penHit==target;
}

static FLOAT BotObstacleDistance(CPlayer *player, FLOAT yaw, INDEX *hitType=NULL)
{
  FLOAT3D origin=player->en_plPlacement.pl_PositionVector;
  origin(2)+=0.8f;
  const double radians=yaw*3.14159265358979323846/180.0;
  const FLOAT3D direction((FLOAT)-std::sin(radians),0,(FLOAT)-std::cos(radians));
  CCastRay ray(player,origin,origin+direction*3.0f);
  ray.cr_bAllowOverHit=FALSE;
  ray.cr_bPhysical=TRUE;
  ray.cr_ttHitModels=CCastRay::TT_COLLISIONBOX;
  ray.Cast(player->GetWorld());
  if (hitType!=NULL) *hitType=ray.cr_penHit==NULL?0:(INDEX)ray.cr_penHit->GetRenderType();
  return ray.cr_penHit==NULL?3.0f:Clamp(ray.cr_fHitDistance,0.0f,3.0f);
}

/* ------------------------------------------------------------------------ */
/* The bot driver tick                                                        */
/* ------------------------------------------------------------------------ */

BOOL BotDriver_HandleTimer(CGame *pgame)
{
  if (InterlockedExchange(&_botNavigationResetRequested,FALSE)) BotResetNavigation();
  if (!bot_bEnabled || pgame==NULL || !pgame->gm_bGameOn) {
    BotResetNavigation();
    return FALSE;
  }

  // Engine107 ray casting shares sector scratch data with world simulation.
  // Keep entities and every ray (including its destructor) under the native
  // world/network mutex. The timer already owns hooks: order 1000 -> 2000.
  // GetLocalPlayerEntity's internal lock ends before its pointer is returned.
  CTSingleLock slBotWorld(&_pNetwork->ga_csNetwork, TRUE);

  const FLOAT fTick     = _pTimer->TickQuantum;             // 1/20 s

  // fire pulse parameters (derived once per tick, fully deterministic)
  INDEX ctPeriodTicks = 0;
  INDEX ctFireTicks   = 0;
  if (bot_fFirePeriod >= fTick) {
    ctPeriodTicks = (INDEX)(bot_fFirePeriod/fTick + 0.5f);
    ctFireTicks   = Clamp<INDEX>(bot_iFireTicks, 0, ctPeriodTicks);
  }

  // for all possible local players (hard limit 4 - see NET_MAXLOCALPLAYERS)
  for (INDEX iLP=0; iLP<4; iLP++) {
    SBotState &bs = _absBots[iLP];
    CLocalPlayer &lp = pgame->gm_lpLocalPlayers[iLP];
    CPlayerSource *ppls = lp.lp_pplsPlayerSource;

    // if this local player exists
    if (ppls==NULL) {
      bs.bs_navigation.Reset(); bs.bs_navPlayer=NULL;
      continue;
    }
    CPlayer *localInput = (CPlayer *)CEntity::GetPlayerEntity(ppls->pls_Index);
    if (localInput==NULL) {
      bs.bs_navigation.Reset(); bs.bs_navPlayer=NULL; continue;
    }

    // reset state when a new player source appears (join / rejoin / map change)
    if (bs.bs_ppls != ppls) {
      bs.bs_ppls     = ppls;
      bs.bs_aHeading = 0.0f;
      bs.bs_iTick    = 0;
      bs.bs_aPitch   = 0.0f;
      bs.bs_iCombatTarget = -1;
      bs.bs_weaponInput.Reset();
      bs.bs_navigation.Reset();
      bs.bs_navPlayer=NULL;
      BotLog("[BotDriver] local player %d (player index %d) is now bot-driven: %s\n",
        iLP, ppls->pls_Index, (const char *)ppls->pls_pcCharacter.pc_strName);
    }
    bs.bs_iTick++;

    // 1) accumulate heading (same convention as CPlayer::m_aLocalRotation:
    //    absolute accumulated angle relative to spawn orientation - never wrap!)
    CPlayer *player = (CPlayer *)_pNetwork->GetLocalPlayerEntity(ppls);
    // ponytail: fixed-target action test; walls still need a suitable test arena.
    CPlayer *target = bot_iTestTarget>=0 && bot_iTestTarget<16
      ? (CPlayer *)CEntity::GetPlayerEntity(bot_iTestTarget) : NULL;
    FLOAT moveFactor = Clamp(bot_fMoveFactor, 0.0f, 1.0f);
    BOOL testAimReady = TRUE;
    const BOOL automatic=bot_bAutoCombat && bot_iTestTarget<0;
    INDEX combatWeapon=0;
    ULONG combatSelect=0;
    BOOL combatDeathmatch=FALSE;
    BOOL combatHold=bot_fMoveFactor<=0;
    if (automatic) {
      testAimReady=FALSE;
      const CSessionProperties *session=(const CSessionProperties *)_pNetwork->GetSessionProperties();
      const BOOL deathmatch=session->sp_gmGameMode==CSessionProperties::GM_SCOREMATCH ||
        session->sp_gmGameMode==CSessionProperties::GM_FRAGMATCH;
      combatDeathmatch=deathmatch;
      botcore::CombatDecision decision={-1,1,0,0,0,false};
      INDEX visible=0;
      if (player!=NULL && deathmatch && player->GetHealth()>0 && player->m_penWeapons!=NULL) {
        botcore::TargetInfo candidates[16];
        for (INDEX index=0; index<16; ++index) {
          CPlayer *other=(CPlayer *)CEntity::GetPlayerEntity(index);
          const BOOL local=BotCombatIsLocal(pgame,index);
          if (other==NULL || other==player || other->GetHealth()<=0 ||
              (bot_bCombatSkipLocals && local)) continue;
          const botcore::TargetInfo snapshot=BotCombatSnapshot(other,index,local);
          if (botcore::CombatValidPlayer(snapshot) && BotCombatVisible(player,other))
            candidates[visible++]=snapshot;
        }
        CPlayerWeapons *weapons=player->GetPlayerWeapons();
        const botcore::AmmoInfo ammo={weapons->m_iBullets,weapons->m_iShells,
          weapons->m_iNapalm,weapons->m_iElectricity,weapons->m_iSniperBullets};
        const CPlacement3D eye=BotCombatEye(player);
        const botcore::CombatInput input={BotCombatSnapshot(player,ppls->pls_Index,TRUE),
          eye.pl_OrientationAngle(1),eye.pl_OrientationAngle(2),
          std::fabs(bot_fYawSpeed)*fTick,moveFactor,
          botcore::CombatUsableWeapons(weapons->m_iAvailableWeapons,ammo),
          bot_bCombatSkipLocals!=FALSE,8.0};
        decision=botcore::DecideCombat(candidates,visible,input);
      }
      if (decision.target>=0) {
        target=(CPlayer *)CEntity::GetPlayerEntity(decision.target);
        bs.bs_aHeading=player->m_aLastRotation(1)+(FLOAT)decision.yawDelta;
        bs.bs_aPitch=player->m_aLastRotation(2)+(FLOAT)decision.pitchDelta;
        moveFactor=(FLOAT)decision.moveFactor;
        testAimReady=decision.fireAllowed;
        combatWeapon=decision.weapon;
        const FLOAT distance=(BotCombatEye(target).pl_PositionVector-
          BotCombatEye(player).pl_PositionVector).Length();
        combatHold=combatHold || distance<=((combatWeapon==1 || combatWeapon==10)?1.5f:8.0f);
        CPlayerWeapons *weapons=player->GetPlayerWeapons();
        combatSelect=bs.bs_weaponInput.Poll(bs.bs_iTick,combatWeapon,
          weapons->m_iWantedWeapon,player->m_ulLastButtons);
        testAimReady=testAimReady && weapons->m_iCurrentWeapon==combatWeapon &&
          weapons->m_iWantedWeapon==combatWeapon;
        if (bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0) {
          BotLog("[BotCombatWeapon] local=%d tick=%d desired=%d current=%d wanted=%d group=%d buttons=%lu bullets=%d shells=%d napalm=%d cells=%d sniper=%d\n",
            iLP,bs.bs_iTick,combatWeapon,weapons->m_iCurrentWeapon,weapons->m_iWantedWeapon,
            botcore::CombatWeaponGroup(combatWeapon),(unsigned long)combatSelect,
            weapons->m_iBullets,weapons->m_iShells,weapons->m_iNapalm,
            weapons->m_iElectricity,weapons->m_iSniperBullets);
        }
      } else if (player!=NULL && player->GetHealth()>0 && deathmatch) {
        bs.bs_aHeading+=bot_fYawSpeed*fTick; // bounded search until a visible opponent exists
      } else { moveFactor=0; }
      if (bs.bs_iCombatTarget!=decision.target ||
          (bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0)) {
        BotLog("[BotCombat] local=%d tick=%d self=%d alive=%d dm=%d visible=%d target=%d weapon=%d ready=%d move=%.2f yawDelta=%.2f pitchDelta=%.2f\n",
          iLP,bs.bs_iTick,ppls->pls_Index,player!=NULL && player->GetHealth()>0,
          deathmatch,visible,decision.target,combatWeapon,testAimReady,moveFactor,
          decision.yawDelta,decision.pitchDelta);
      }
      bs.bs_iCombatTarget=decision.target;
    } else if (player!=NULL && target!=NULL && player!=target && target->GetHealth()>0) {
      const FLOAT3D delta = target->en_plPlacement.pl_PositionVector
        - player->en_plPlacement.pl_PositionVector;
      const botcore::AimAngles aim = botcore::AimAt(delta(1), delta(2), delta(3));
      const FLOAT yaw = player->en_plPlacement.pl_OrientationAngle(1)
        + player->en_plViewpoint.pl_OrientationAngle(1);
      const FLOAT pitch = player->en_plViewpoint.pl_OrientationAngle(2);
      const FLOAT limit = (FLOAT)std::fabs(bot_fYawSpeed)*fTick;
      bs.bs_aHeading = player->m_aLastRotation(1)
        + (FLOAT)botcore::TestTurnDelta(yaw, aim.yaw_deg, limit);
      bs.bs_aPitch = player->m_aLastRotation(2)
        + (FLOAT)botcore::TestTurnDelta(pitch, aim.pitch_deg, limit);
      testAimReady = std::fabs(std::remainder(aim.yaw_deg-yaw, 360.0))<3.0
        && std::fabs(aim.pitch_deg-pitch)<3.0;
      if (!testAimReady || delta.Length()<8.0f) moveFactor = 0.0f;
    } else {
      bs.bs_aHeading += bot_fYawSpeed*fTick;
    }

    if (bot_bObstacleAvoidance && automatic && combatDeathmatch && player!=NULL) {
      if (bs.bs_navPlayer!=player) { bs.bs_navigation.Reset(); bs.bs_navPlayer=player; }
      const BOOL alive=player->GetHealth()>0;
      const FLOAT yaw=BotCombatEye(player).pl_OrientationAngle(1);
      FLOAT front=3,left=3,right=3;
      INDEX frontHitType=0;
      if (alive && !combatHold) {
        front=BotObstacleDistance(player,yaw,&frontHitType);
        left=BotObstacleDistance(player,yaw+60.0f);
        right=BotObstacleDistance(player,yaw-60.0f);
      }
      const FLOAT3D &position=player->en_plPlacement.pl_PositionVector;
      const botcore::NavigationInput input={position(1),position(3),yaw,
        std::fabs(bot_fYawSpeed)*fTick,moveFactor,front,left,right,
        alive!=FALSE,combatHold!=FALSE,(iLP&1)?-1:1,
        Clamp(bot_fMoveFactor,0.0f,1.0f)};
      const botcore::NavigationDecision navigation=bs.bs_navigation.Update(input);
      if (navigation.overrideInput) {
        bs.bs_aHeading=player->m_aLastRotation(1)+(FLOAT)navigation.yawDelta;
        bs.bs_aPitch=player->m_aLastRotation(2);
        moveFactor=(FLOAT)navigation.forward;
        testAimReady=FALSE; // recovery heading is movement, not combat aim
      }
      if (navigation.began || navigation.finished ||
          (bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0)) {
        BotLog("[BotNavigation] local=%d tick=%d alive=%d hold=%d requested=%.2f front=%.2f hitType=%d left=%.2f right=%.2f active=%d phase=%d reason=%d began=%d finished=%d yaw=%.2f delta=%.2f forward=%.2f pos=(%.2f,%.2f,%.2f)\n",
          iLP,bs.bs_iTick,alive,combatHold,input.forward,front,frontHitType,left,right,navigation.active,
          (int)navigation.phase,(int)navigation.reason,navigation.began,navigation.finished,
          yaw,navigation.yawDelta,moveFactor,position(1),position(2),position(3));
      }
    } else { bs.bs_navigation.Reset(); bs.bs_navPlayer=NULL; }

    // 2) periodic fire pulse (with a small per-bot phase offset)
    BOOL bFire = FALSE;
    if (ctPeriodTicks>0 && ctFireTicks>0) {
      const INDEX iPhase = (bs.bs_iTick + iLP*ctPeriodTicks/4) % ctPeriodTicks;
      bFire = (iPhase < ctFireTicks);
    }
    // Retail deathmatch respawns on the native Fire press/release action.
    // The combat decision never attacks while dead; this pulse is respawn input.
    const BOOL respawnInput=automatic && player!=NULL && player->GetHealth()<=0;
    bFire = bFire && (testAimReady || respawnInput);

    // 3) compose the action
    CPlayerAction pa;
    pa.Clear();
    pa.pa_vTranslation(3) = -moveFactor; // normalized forward axis for native composer
    if (!automatic && target!=NULL && botcore::TestJump(bs.bs_iTick)) {
      pa.pa_vTranslation(2) = 1.0f;
    }
    pa.pa_aRotation(1) = bs.bs_aHeading - localInput->m_aLocalRotation(1);
    pa.pa_aRotation(2) = bs.bs_aPitch - localInput->m_aLocalRotation(2);
    pa.pa_aViewRotation(1) = 0.0f;            // no freelook

    // Use vanilla speed conversion and local input accumulation. Human buttons
    // must not leak into this synthetic action; preserve the shared control buffer.
    UBYTE controls[sizeof(lp.lp_ubPlayerControlsState)];
    memcpy(controls, ctl_pvPlayerControls, ctl_slPlayerControlsSize);
    memset(ctl_pvPlayerControls, 0, ctl_slPlayerControlsSize);
    _pShell->SetINDEX("ctl_b3rdPersonView", bot_bTestThirdPerson);
    ctl_ComposeActionPacket(ppls->pls_pcCharacter, pa, FALSE);
    memcpy(ctl_pvPlayerControls, controls, ctl_slPlayerControlsSize);
    if (bFire) {
      pa.pa_ulButtons |= BOT_PLACT_FIRE;
    }
    if (bot_iTestTarget>=0 && bot_iTestTarget<16) pa.pa_ulButtons |= 2L<<14; // Colt
    if (automatic) pa.pa_ulButtons |= combatSelect;

    // 4) hand it to the network player source (stamps pa_llCreated internally)
    ppls->SetAction(pa);

    // 5) periodic status log (position read from our own player entity)
    if (bot_iLogEvery>0 && (bs.bs_iTick%bot_iLogEvery)==0) {
      if (bot_bDiagnostics) BotLog("[BotInput] tick=%d forward=%.2f up=%.2f\n",
        bs.bs_iTick, pa.pa_vTranslation(3), pa.pa_vTranslation(2));
      CEntity *pen = _pNetwork->GetLocalPlayerEntity(ppls);
      if (pen!=NULL) {
        const FLOAT3D &vPos = pen->en_plPlacement.pl_PositionVector;
        BotLog("[BotDriver] bot%d tick=%d pos=(%.1f,%.1f,%.1f) heading=%.1f fire=%d\n",
          iLP, bs.bs_iTick, vPos(1), vPos(2), vPos(3), bs.bs_aHeading, bFire);
      } else {
        BotLog("[BotDriver] bot%d tick=%d (no entity yet) heading=%.1f fire=%d\n",
          iLP, bs.bs_iTick, bs.bs_aHeading, bFire);
      }
      if (bot_bDiagnostics && iLP==0) {
        if (player!=NULL && player->m_penWeapons!=NULL) {
          CPlayerWeapons *weapons = player->GetPlayerWeapons();
          CPlacement3D eye = player->en_plViewpoint;
          eye.RelativeToAbsolute(player->en_plPlacement);
          BotLog("[BotWeapon] tick=%d eye=(%.2f,%.2f,%.2f) yaw=%.2f pitch=%.2f weapon=%d wanted=%d available=%d ammo=%d firing=%d rayDistance=%.2f\n",
            bs.bs_iTick, eye.pl_PositionVector(1), eye.pl_PositionVector(2),
            eye.pl_PositionVector(3), eye.pl_OrientationAngle(1), eye.pl_OrientationAngle(2),
            weapons->m_iCurrentWeapon, weapons->m_iWantedWeapon, weapons->m_iAvailableWeapons,
            weapons->m_iColtBullets, weapons->m_bFireWeapon, weapons->m_fRayHitDistance);
        }
        for (INDEX iPlayer=0; iPlayer<16; iPlayer++) {
          CPlayer *player = (CPlayer *)CEntity::GetPlayerEntity(iPlayer);
          if (player==NULL) continue;
          const CSessionProperties *session = (const CSessionProperties *)_pNetwork->GetSessionProperties();
          const INDEX frags = session->sp_bUseFrags
            ? player->m_psLevelStats.ps_iKills : player->m_psLevelStats.ps_iScore;
          const CPlacement3D &placement = player->en_plPlacement;
          BotLog("[BotSnapshot] tick=%d player=%d pos=(%.2f,%.2f,%.2f) yaw=%.2f health=%.1f buttons=%lu \\frags_%d\\%d\n",
            bs.bs_iTick, iPlayer, placement.pl_PositionVector(1),
            placement.pl_PositionVector(2), placement.pl_PositionVector(3),
            placement.pl_OrientationAngle(1), player->GetHealth(),
            (unsigned long)player->m_ulLastButtons, iPlayer, frags);
        }
      }
    }
  }

  // the bot driver owns action generation now - skip vanilla input handling
  return TRUE;
}
