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
#include <EntitiesV/PlayerWeapons.h>

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
}

/* ------------------------------------------------------------------------ */
/* Per-local-player bot state                                                 */
/* ------------------------------------------------------------------------ */

struct SBotState {
  CPlayerSource *bs_ppls;     // player source this state belongs to
  ANGLE  bs_aHeading;         // accumulated heading (relative to spawn direction)
  INDEX  bs_iTick;            // ticks since (re)join
  ANGLE  bs_aPitch;
};

static SBotState _absBots[4] = {
  {NULL, 0.0f, 0}, {NULL, 0.0f, 0}, {NULL, 0.0f, 0}, {NULL, 0.0f, 0},
};

/* ------------------------------------------------------------------------ */
/* The bot driver tick                                                        */
/* ------------------------------------------------------------------------ */

BOOL BotDriver_HandleTimer(CGame *pgame)
{
  if (!bot_bEnabled || pgame==NULL || !pgame->gm_bGameOn) {
    return FALSE;
  }

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
    CLocalPlayer &lp = pgame->gm_lpLocalPlayers[iLP];
    CPlayerSource *ppls = lp.lp_pplsPlayerSource;

    // if this local player exists
    if (ppls==NULL) {
      continue;
    }
    CPlayer *localInput = (CPlayer *)CEntity::GetPlayerEntity(ppls->pls_Index);
    if (localInput==NULL) continue;

    SBotState &bs = _absBots[iLP];

    // reset state when a new player source appears (join / rejoin / map change)
    if (bs.bs_ppls != ppls) {
      bs.bs_ppls     = ppls;
      bs.bs_aHeading = 0.0f;
      bs.bs_iTick    = 0;
      bs.bs_aPitch   = 0.0f;
      CPrintF("[BotDriver] local player %d (player index %d) is now bot-driven: %s\n",
        iLP, ppls->pls_Index, ppls->pls_pcCharacter.GetNameForPrinting());
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
    if (player!=NULL && target!=NULL && player!=target && target->GetHealth()>0) {
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

    // 2) periodic fire pulse (with a small per-bot phase offset)
    BOOL bFire = FALSE;
    if (ctPeriodTicks>0 && ctFireTicks>0) {
      const INDEX iPhase = (bs.bs_iTick + iLP*ctPeriodTicks/4) % ctPeriodTicks;
      bFire = (iPhase < ctFireTicks);
    }
    bFire = bFire && testAimReady;

    // 3) compose the action
    CPlayerAction pa;
    pa.Clear();
    pa.pa_vTranslation(3) = -moveFactor; // normalized forward axis for native composer
    if (target!=NULL && botcore::TestJump(bs.bs_iTick)) {
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
    ctl_ComposeActionPacket(ppls->pls_pcCharacter, pa, FALSE);
    memcpy(ctl_pvPlayerControls, controls, ctl_slPlayerControlsSize);
    if (bFire) {
      pa.pa_ulButtons |= BOT_PLACT_FIRE;
    }
    if (bot_iTestTarget>=0 && bot_iTestTarget<16) pa.pa_ulButtons |= 2L<<14; // Colt

    // 4) hand it to the network player source (stamps pa_llCreated internally)
    ppls->SetAction(pa);

    // 5) periodic status log (position read from our own player entity)
    if (bot_iLogEvery>0 && (bs.bs_iTick%bot_iLogEvery)==0) {
      if (bot_bDiagnostics) CPrintF("[BotInput] tick=%d forward=%.2f up=%.2f\n",
        bs.bs_iTick, pa.pa_vTranslation(3), pa.pa_vTranslation(2));
      CEntity *pen = _pNetwork->GetLocalPlayerEntity(ppls);
      if (pen!=NULL) {
        const FLOAT3D &vPos = pen->en_plPlacement.pl_PositionVector;
        CPrintF("[BotDriver] bot%d tick=%d pos=(%.1f,%.1f,%.1f) heading=%.1f fire=%d\n",
          iLP, bs.bs_iTick, vPos(1), vPos(2), vPos(3), bs.bs_aHeading, bFire);
      } else {
        CPrintF("[BotDriver] bot%d tick=%d (no entity yet) heading=%.1f fire=%d\n",
          iLP, bs.bs_iTick, bs.bs_aHeading, bFire);
      }
      if (bot_bDiagnostics && iLP==0) {
        if (player!=NULL && player->m_penWeapons!=NULL) {
          CPlayerWeapons *weapons = player->GetPlayerWeapons();
          CPlacement3D eye = player->en_plViewpoint;
          eye.RelativeToAbsolute(player->en_plPlacement);
          CPrintF("[BotWeapon] tick=%d eye=(%.2f,%.2f,%.2f) yaw=%.2f pitch=%.2f weapon=%d wanted=%d available=%d ammo=%d firing=%d rayDistance=%.2f\n",
            bs.bs_iTick, eye.pl_PositionVector(1), eye.pl_PositionVector(2),
            eye.pl_PositionVector(3), eye.pl_OrientationAngle(1), eye.pl_OrientationAngle(2),
            weapons->m_iCurrentWeapon, weapons->m_iWantedWeapon, weapons->m_iAvailableWeapons,
            weapons->m_iColtBullets, weapons->m_bFireWeapon, weapons->m_fRayHitDistance);
        }
        for (INDEX iPlayer=0; iPlayer<16; iPlayer++) {
          CPlayer *player = (CPlayer *)CEntity::GetPlayerEntity(iPlayer);
          if (player==NULL) continue;
          CTString info;
          player->GetGameSpyPlayerInfo(iPlayer, info);
          const CPlacement3D &placement = player->en_plPlacement;
          CPrintF("[BotSnapshot] tick=%d player=%d pos=(%.2f,%.2f,%.2f) yaw=%.2f health=%.1f buttons=%lu %s\n",
            bs.bs_iTick, iPlayer, placement.pl_PositionVector(1),
            placement.pl_PositionVector(2), placement.pl_PositionVector(3),
            placement.pl_OrientationAngle(1), player->GetHealth(),
            (unsigned long)player->m_ulLastButtons, (const char *)info);
        }
      }
    }
  }

  // the bot driver owns action generation now - skip vanilla input handling
  return TRUE;
}
