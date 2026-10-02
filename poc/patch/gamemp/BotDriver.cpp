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
 *
 * Phase-2/4/6 extensions (all OFF by default; Phase-1 defaults unchanged):
 *  - bot_ctLocalPlayers 2..4 joins with multiple local players through the
 *    native split-screen configuration (BotDriver_ConfigureJoin);
 *  - bot_bVariants gives each local slot a distinct deterministic heading
 *    offset and yaw scale (botcore::VariantFor);
 *  - bot_iAiMode 1 selects the nearest living target from the read-only
 *    replicated player snapshots and picks a weapon by range band
 *    (botcore::SelectTarget / SelectWeapon); still no entity writes;
 *  - bot_strWaypoints loads a hand-authored waypoint graph used only as a
 *    stuck fallback (botcore::WaypointGraph / StuckDetector); there is NO
 *    line-of-sight or collision model - this is not CecilBot navigation;
 *  - bot_fChatPeriod > 0 sends low-frequency jittered chat lines from
 *    bot_strChatFile via the regular CNetwork::SendChat() client path.
 */

#include "StdAfx.h"
#include <Engine/Network/Network.h>
#include <Engine/Entities/Entity.h>
#include "Game.h"
#include "BotDriver.h"
#include "botcore.h"
#include "botcore_ai.h"
#include "SessionProperties.h"
#include <cstdarg>
#include <cstdio>
#include <cstring>
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

// Phase 2 - multiple local players per bot client process
static INDEX bot_ctLocalPlayers = 1;   // 1..4 local players at join time
static INDEX bot_iProfileBase   = 0;   // first player profile index (0..7)
static INDEX bot_bVariants      = FALSE; // per-slot heading offset / yaw scale

// Phase 4 - minimal AI (still read-only world access, actions only)
static INDEX bot_iAiMode        = 0;   // 0 = Phase-1 PoC, 1 = auto target + weapon
static INDEX bot_bTargetLocals  = FALSE; // allow targeting sibling local bots
static CTString bot_strWaypoints = "";  // Scripts\...txt ("node x y z"/"edge a b")

// Phase 6 - presence/chat (low frequency, jittered, deterministic)
static FLOAT bot_fChatPeriod    = 0.0f; // [s] base chat period (0 = off)
static CTString bot_strChatFile = "";   // plain text, one chat line per line
static INDEX bot_iChatSeed      = 1;    // seed for the per-bot cadence

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
  _pShell->DeclareSymbol("user INDEX bot_ctLocalPlayers;", &bot_ctLocalPlayers);
  _pShell->DeclareSymbol("user INDEX bot_iProfileBase;",   &bot_iProfileBase);
  _pShell->DeclareSymbol("user INDEX bot_bVariants;",      &bot_bVariants);
  _pShell->DeclareSymbol("user INDEX bot_iAiMode;",        &bot_iAiMode);
  _pShell->DeclareSymbol("user INDEX bot_bTargetLocals;",  &bot_bTargetLocals);
  _pShell->DeclareSymbol("user CTString bot_strWaypoints;", &bot_strWaypoints);
  _pShell->DeclareSymbol("user FLOAT bot_fChatPeriod;",    &bot_fChatPeriod);
  _pShell->DeclareSymbol("user CTString bot_strChatFile;", &bot_strChatFile);
  _pShell->DeclareSymbol("user INDEX bot_iChatSeed;",      &bot_iChatSeed);
}

/* ------------------------------------------------------------------------ */
/* Phase 2: native multi-local-player join configuration                      */
/* ------------------------------------------------------------------------ */

void BotDriver_ConfigureJoin(CGame *pgame)
{
  if (!bot_bEnabled || pgame==NULL) {
    return;
  }
  const INDEX ctPlayers = Clamp(bot_ctLocalPlayers, (INDEX)1, (INDEX)4);
  if (ctPlayers<=1) {
    return; // Phase-1 single-player join stays exactly as before
  }
  // profiles bot_iProfileBase..+ctPlayers-1 must exist (8 profile slots);
  // their distinct per-character GUIDs are the required uniqueness proof
  const INDEX iBase = Clamp(bot_iProfileBase, (INDEX)0, (INDEX)(8-ctPlayers));
  pgame->gm_StartSplitScreenCfg =
    (enum CGame::SplitScreenCfg)(CGame::SSC_PLAY1 + ctPlayers - 1);
  for (INDEX i=0; i<4; i++) {
    pgame->gm_aiStartLocalPlayers[i] = (i<ctPlayers) ? (iBase+i) : -1;
  }
  BotLog("[BotDriver] join configured for %d local players (profiles %d..%d)\n",
    ctPlayers, iBase, iBase+ctPlayers-1);
}

/* ------------------------------------------------------------------------ */
/* Per-local-player bot state                                                 */
/* ------------------------------------------------------------------------ */

struct SBotState {
  CPlayerSource *bs_ppls = NULL; // player source this state belongs to
  ANGLE  bs_aHeading = 0.0f;     // accumulated heading (relative to spawn direction)
  INDEX  bs_iTick = 0;           // ticks since (re)join
  ANGLE  bs_aPitch = 0.0f;
  botcore::StuckDetector bs_stuck;   // Phase 4: forward-progress watchdog
  INDEX  bs_iWaypointHold = 0;       // ticks left steering along the graph
  INDEX  bs_iChatCountdown = -1;     // ticks until next chat line (-1 = unarmed)
};

static SBotState _absBots[4];

/* ------------------------------------------------------------------------ */
/* Phase 4/6 shared assets (waypoints, chat lines, presence schedules)        */
/* ------------------------------------------------------------------------ */

static botcore::WaypointGraph _wpGraph;
static CTString _strLoadedWaypoints = "";
static BOOL _bWaypointsBroken = FALSE;

static char _achChatLines[64][256];
static INDEX _ctChatLines = 0;
static CTString _strLoadedChatFile = "";
static BOOL _bChatBroken = FALSE;
static botcore::PresenceSchedule *_apsChat[4] = {NULL, NULL, NULL, NULL};

// Plain text files from the Scripts directory (on disk, not inside a GRO).
// Any parse error logs loudly and disables the feature (fail closed).
static void BotLoadWaypoints(void)
{
  if (_strLoadedWaypoints==bot_strWaypoints) return;
  _strLoadedWaypoints = bot_strWaypoints;
  _wpGraph = botcore::WaypointGraph();
  _bWaypointsBroken = FALSE;
  if (bot_strWaypoints=="") return;
  FILE *file = std::fopen((const char *)bot_strWaypoints, "r");
  if (file==NULL) {
    BotLog("[BotDriver] waypoint file '%s' not readable - navigation disabled\n",
      (const char *)bot_strWaypoints);
    _bWaypointsBroken = TRUE;
    return;
  }
  char line[512];
  INDEX iLine = 0;
  while (std::fgets(line, sizeof(line), file)!=NULL) {
    iLine++;
    if (!_wpGraph.ParseLine(line)) {
      BotLog("[BotDriver] waypoint file '%s' line %d invalid - navigation disabled\n",
        (const char *)bot_strWaypoints, iLine);
      _wpGraph = botcore::WaypointGraph();
      _bWaypointsBroken = TRUE;
      break;
    }
  }
  std::fclose(file);
  if (!_bWaypointsBroken) {
    BotLog("[BotDriver] waypoint graph loaded: %d nodes from '%s'\n",
      _wpGraph.node_count(), (const char *)bot_strWaypoints);
  }
}

static void BotLoadChatLines(void)
{
  if (_strLoadedChatFile==bot_strChatFile) return;
  _strLoadedChatFile = bot_strChatFile;
  _ctChatLines = 0;
  _bChatBroken = FALSE;
  if (bot_strChatFile=="") return;
  FILE *file = std::fopen((const char *)bot_strChatFile, "r");
  if (file==NULL) {
    BotLog("[BotDriver] chat file '%s' not readable - chat disabled\n",
      (const char *)bot_strChatFile);
    _bChatBroken = TRUE;
    return;
  }
  char line[512];
  while (_ctChatLines<64 && std::fgets(line, sizeof(line), file)!=NULL) {
    // sanitize: strip newline plus characters that could break chat/console
    char *dst = _achChatLines[_ctChatLines];
    INDEX ct = 0;
    for (const char *src=line; *src!='\0' && ct<255; src++) {
      if (*src=='\r' || *src=='\n' || *src=='"' || *src=='\\' || *src==';') continue;
      dst[ct++] = *src;
    }
    dst[ct] = '\0';
    if (ct>0) _ctChatLines++;
  }
  std::fclose(file);
  BotLog("[BotDriver] %d chat lines loaded from '%s'\n",
    _ctChatLines, (const char *)bot_strChatFile);
}

/* ------------------------------------------------------------------------ */
/* The bot driver tick                                                        */
/* ------------------------------------------------------------------------ */

BOOL BotDriver_HandleTimer(CGame *pgame)
{
  if (!bot_bEnabled || pgame==NULL || !pgame->gm_bGameOn) {
    return FALSE;
  }

  const FLOAT fTick     = _pTimer->TickQuantum;             // 1/20 s

  BotLoadWaypoints();
  BotLoadChatLines();

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
    const botcore::BotVariant variant = botcore::VariantFor(iLP);
    const FLOAT fYawSpeed = bot_bVariants
      ? bot_fYawSpeed*(FLOAT)variant.yaw_speed_scale : bot_fYawSpeed;

    // reset state when a new player source appears (join / rejoin / map change)
    if (bs.bs_ppls != ppls) {
      bs.bs_ppls     = ppls;
      bs.bs_aHeading = bot_bVariants ? (ANGLE)variant.heading_offset_deg : 0.0f;
      bs.bs_iTick    = 0;
      bs.bs_aPitch   = 0.0f;
      bs.bs_stuck.Reset();
      bs.bs_iWaypointHold = 0;
      bs.bs_iChatCountdown = -1;
      BotLog("[BotDriver] local player %d (player index %d) is now bot-driven: %s\n",
        iLP, ppls->pls_Index, (const char *)ppls->pls_pcCharacter.pc_strName);
    }
    bs.bs_iTick++;

    // 1) accumulate heading (same convention as CPlayer::m_aLocalRotation:
    //    absolute accumulated angle relative to spawn orientation - never wrap!)
    CPlayer *player = (CPlayer *)_pNetwork->GetLocalPlayerEntity(ppls);

    // target resolution: Phase-4 auto selection or the Phase-1 fixed index.
    // World access stays strictly read-only (replicated snapshots).
    CPlayer *target = NULL;
    if (bot_iAiMode==1 && player!=NULL) {
      botcore::TargetInfo aInfo[16];
      int ctInfo = 0;
      for (INDEX iPlayer=0; iPlayer<16; iPlayer++) {
        CPlayer *penScan = (CPlayer *)CEntity::GetPlayerEntity(iPlayer);
        if (penScan==NULL) continue;
        BOOL bLocal = FALSE;
        for (INDEX j=0; j<4; j++) {
          CPlayerSource *pplsOwn = pgame->gm_lpLocalPlayers[j].lp_pplsPlayerSource;
          if (pplsOwn!=NULL && CEntity::GetPlayerEntity(pplsOwn->pls_Index)==penScan) {
            bLocal = TRUE;
          }
        }
        const FLOAT3D &vScan = penScan->en_plPlacement.pl_PositionVector;
        botcore::TargetInfo &info = aInfo[ctInfo++];
        info.index = iPlayer;
        info.x = vScan(1); info.y = vScan(2); info.z = vScan(3);
        info.health = penScan->GetHealth();
        info.local = bLocal!=FALSE;
      }
      const FLOAT3D &vSelf = player->en_plPlacement.pl_PositionVector;
      const int iTarget = botcore::SelectTarget(aInfo, ctInfo, ppls->pls_Index,
        vSelf(1), vSelf(2), vSelf(3), !bot_bTargetLocals);
      if (iTarget>=0) {
        target = (CPlayer *)CEntity::GetPlayerEntity(iTarget);
      }
    } else if (bot_iTestTarget>=0 && bot_iTestTarget<16) {
      // ponytail: fixed-target action test; walls still need a suitable test arena.
      target = (CPlayer *)CEntity::GetPlayerEntity(bot_iTestTarget);
    }

    FLOAT moveFactor = Clamp(bot_fMoveFactor, 0.0f, 1.0f);
    BOOL testAimReady = TRUE;
    FLOAT fTargetDistance = -1.0f;
    if (player!=NULL && target!=NULL && player!=target && target->GetHealth()>0) {
      const FLOAT3D delta = target->en_plPlacement.pl_PositionVector
        - player->en_plPlacement.pl_PositionVector;
      fTargetDistance = delta.Length();
      const botcore::AimAngles aim = botcore::AimAt(delta(1), delta(2), delta(3));
      const FLOAT yaw = player->en_plPlacement.pl_OrientationAngle(1)
        + player->en_plViewpoint.pl_OrientationAngle(1);
      const FLOAT pitch = player->en_plViewpoint.pl_OrientationAngle(2);
      const FLOAT limit = (FLOAT)std::fabs(fYawSpeed)*fTick;
      bs.bs_aHeading = player->m_aLastRotation(1)
        + (FLOAT)botcore::TestTurnDelta(yaw, aim.yaw_deg, limit);
      bs.bs_aPitch = player->m_aLastRotation(2)
        + (FLOAT)botcore::TestTurnDelta(pitch, aim.pitch_deg, limit);
      testAimReady = std::fabs(std::remainder(aim.yaw_deg-yaw, 360.0))<3.0
        && std::fabs(aim.pitch_deg-pitch)<3.0;
      if (!testAimReady || delta.Length()<8.0f) moveFactor = 0.0f;
    } else {
      bs.bs_aHeading += fYawSpeed*fTick;
    }

    // Phase 4: forward-progress watchdog plus optional waypoint fallback.
    // Steering only - no engine collision or visibility queries are made.
    BOOL bStuckJump = FALSE;
    if (bot_iAiMode==1 && player!=NULL) {
      const FLOAT3D &vSelf = player->en_plPlacement.pl_PositionVector;
      if (bs.bs_stuck.Update(vSelf(1), vSelf(3), moveFactor>0.01f)) {
        bStuckJump = TRUE;
        if (_wpGraph.node_count()>0) {
          bs.bs_iWaypointHold = 60; // 3 s of graph steering after a stall
        }
        BotLog("[BotDriver] bot%d stuck at (%.1f,%.1f) - jump%s\n", iLP,
          vSelf(1), vSelf(3), _wpGraph.node_count()>0 ? " + waypoint detour" : "");
      }
      if (bs.bs_iWaypointHold>0 && _wpGraph.node_count()>0) {
        bs.bs_iWaypointHold--;
        const int iFrom = _wpGraph.NearestNode(vSelf(1), vSelf(2), vSelf(3));
        int iDest = iFrom;
        if (target!=NULL) {
          const FLOAT3D &vT = target->en_plPlacement.pl_PositionVector;
          iDest = _wpGraph.NearestNode(vT(1), vT(2), vT(3));
        } else if (_wpGraph.node_count()>1) {
          iDest = (iFrom+1)%_wpGraph.node_count();
        }
        const int iHop = _wpGraph.NextHop(iFrom, iDest);
        double fX, fY, fZ;
        if (iHop>=0 && _wpGraph.NodePosition(iHop, &fX, &fY, &fZ)) {
          const botcore::AimAngles steer = botcore::AimAt(
            fX-vSelf(1), fY-vSelf(2), fZ-vSelf(3));
          const FLOAT yaw = player->en_plPlacement.pl_OrientationAngle(1)
            + player->en_plViewpoint.pl_OrientationAngle(1);
          const FLOAT limit = (FLOAT)std::fabs(fYawSpeed)*fTick;
          bs.bs_aHeading = player->m_aLastRotation(1)
            + (FLOAT)botcore::TestTurnDelta(yaw, steer.yaw_deg, limit);
          moveFactor = Clamp(bot_fMoveFactor, 0.0f, 1.0f); // keep walking the detour
        }
      }
    }

    // 2) periodic fire pulse (with a small per-bot phase offset)
    BOOL bFire = FALSE;
    if (ctPeriodTicks>0 && ctFireTicks>0) {
      const INDEX iPhase = (bs.bs_iTick + iLP*ctPeriodTicks/4) % ctPeriodTicks;
      bFire = (iPhase < ctFireTicks);
    }
    bFire = bFire && testAimReady;
    if (bot_iAiMode==1 && target==NULL) {
      bFire = FALSE; // AI mode never fires blindly into empty rooms
    }

    // 3) compose the action
    CPlayerAction pa;
    pa.Clear();
    pa.pa_vTranslation(3) = -moveFactor; // normalized forward axis for native composer
    if ((target!=NULL && bot_iAiMode!=1 && botcore::TestJump(bs.bs_iTick)) || bStuckJump) {
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
    if (bot_iAiMode==1) {
      // Phase 4: deterministic range-band weapon choice (same button encoding
      // as the Phase-1 Colt test below: index << PLACT_SELECT_WEAPON_SHIFT)
      if (target!=NULL && fTargetDistance>=0.0f &&
          player!=NULL && player->m_penWeapons!=NULL) {
        CPlayerWeapons *weapons = player->GetPlayerWeapons();
        const int iWeapon = botcore::SelectWeapon(
          (uint32_t)weapons->m_iAvailableWeapons, fTargetDistance);
        if (weapons->m_iCurrentWeapon!=iWeapon && weapons->m_iWantedWeapon!=iWeapon) {
          pa.pa_ulButtons |= (ULONG)botcore::WeaponSelectButtons(iWeapon);
        }
      }
    } else if (bot_iTestTarget>=0 && bot_iTestTarget<16) {
      pa.pa_ulButtons |= 2L<<14; // Colt
    }

    // 4) hand it to the network player source (stamps pa_llCreated internally)
    ppls->SetAction(pa);

    // Phase 6: low-frequency jittered chat through the regular client chat
    // path (CNetwork::SendChat, same call the vanilla Say command uses).
    if (bot_fChatPeriod>0.0f && _ctChatLines>0 && !_bChatBroken) {
      if (_apsChat[iLP]==NULL) {
        _apsChat[iLP] = new botcore::PresenceSchedule((uint32_t)bot_iChatSeed, iLP);
      }
      if (bs.bs_iChatCountdown<0) {
        bs.bs_iChatCountdown = _apsChat[iLP]->NextChatDelayTicks(bot_fChatPeriod);
      } else if (bs.bs_iChatCountdown>0 && --bs.bs_iChatCountdown==0) {
        const int iLine = _apsChat[iLP]->NextChatLine((int)_ctChatLines);
        if (iLine>=0) {
          _pNetwork->SendChat(1UL<<ppls->pls_Index, (ULONG)-1,
            CTString(_achChatLines[iLine]));
          BotLog("[BotChat] bot%d tick=%d line=%d\n", iLP, bs.bs_iTick, iLine);
        }
        bs.bs_iChatCountdown = _apsChat[iLP]->NextChatDelayTicks(bot_fChatPeriod);
      }
    }

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
