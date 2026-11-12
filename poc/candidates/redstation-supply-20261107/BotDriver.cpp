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
#include "BotTelemetry.h"
#include "botcore.h"
#include "bot_reconnect.h"
#include "bot_combat.h"
#include "bot_weapon_input.h"
#include "bot_navigation.h"
#include "bot_supply_navigation.h"
#include "bot_human.h"
#include "cecil_rules.h"
#include "BotCecilItems.h"
#include <Engine/World/WorldRayCasting.h>
#include "SessionProperties.h"
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <EntitiesV/PlayerWeapons.h>
#include <EntitiesV/WeaponItem.h>

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
static INDEX bot_iTelemetry = 1;         // 0 = keep the build silent
static INDEX bot_bTelemetryConsole = 0;  // 1 = console summary every 5 s
static INDEX bot_bSupplyNavigation = FALSE; // development-only optional weapon goals
static volatile LONG _botSupplyMapReady=FALSE;
static volatile LONG _botSupplyMapSerial=0;
static void BotSupplyUpdateNavigation(CGame *game);
static void BotSupplyReset(INDEX slot);
static botcore::CecilSettings &BotCecilSettings();
static int _botRayBudget=16;
static INDEX bot_bHumanAI      = FALSE; // profile-driven perception/aim/loadout (new path)
static INDEX bot_iArenaTier = 0; // 0 = migrate roster; 1 MITTEL, 2 STARK, 3 DEMON
static INDEX bot_iRosterOffset = 0;     // 0 or 4: which half of the 8-bot roster this client uses
static INDEX bot_iProfile0     = -1;    // explicit roster index per local slot (-1 = offset+iLP)
static INDEX bot_iProfile1     = -1;
static INDEX bot_iProfile2     = -1;
static INDEX bot_iProfile3     = -1;
static INDEX bot_iProfileSeed  = 20261020; // per-client seed; slots/tiers are mixed in
static FLOAT bot_fStrafeScale  = 0.0f;  // 0 = strafe disabled; see the migration notes
static INDEX bot_bDiag = FALSE;        // P0: timer/config heartbeat (opt-in)
static INDEX bot_iDiagEvery = 100;     // P0: heartbeat every N timer calls (100 = 5 s)
static INDEX bot_iDiagTicks = 0;       // P0: observed GameHandleTimer calls
static BOOL _botDiagLoggedFirst = FALSE;
static INDEX bot_iScanInterval = 1;     // full target scan every N ticks (1 = every tick)
static FLOAT bot_fTargetRange  = 0.0f;  // max combat target distance in m (0 = unlimited)
static INDEX bot_iMaxLosRays   = 0;     // max LOS raycasts per bot and full scan (0 = unlimited)
static INDEX bot_iObstacleInterval = 1; // side obstacle rays every N ticks (1 = every tick)

static botcore::Reconnect _botReconnect;
static CTString _strBotReconnectAddress;
static volatile LONG _botNavigationResetRequested=FALSE;

/* ------------------------------------------------------------------------ */
/* P0 evidence telemetry (diagnostic candidate, not for production)          */
/* ------------------------------------------------------------------------ */

#define BT_LINE_MAX 1024

static HANDLE _btHandle = INVALID_HANDLE_VALUE;
static char _btPath[1024] = {0};
static CRITICAL_SECTION _btCs;
static BOOL _btCsReady = FALSE;
static BOOL _btStarted = FALSE;

static volatile LONG _btTicks = 0, _btActions = 0, _btFrames = 0;
static volatile LONG _btRenderSkip = 0, _btRenderDraw = 0;
static volatile LONG _btDisabled = 0, _btGameOff = 0, _btNoLocal = 0, _btNoEntity = 0;
static volatile LONG _btActionBySlot[4] = {0, 0, 0, 0};
static volatile LONG _btLp = 0, _btGameOn = 0, _btEnabled = 0;
static volatile LONG _btReason = BOT_TM_REASON_ACTIVE;
static volatile LONG _btLockMaxUs = 0, _btLockLastUs = 0;
static volatile LONG _btTickMaxUs = 0, _btTickSumUs = 0, _btTickCount = 0;

static LONGLONG _btQpcFreq = 0;
static long long _btPrevTickUs = 0;      // timer thread only
static long long _btLockStartUs = 0;     // timer thread only
static int _btLastStateReason = -1;      // timer thread only

static long long BotTelemetry_NowUs(void)
{
  LARGE_INTEGER liCount;
  if (_btQpcFreq == 0) {
    LARGE_INTEGER liFreq;
    if (!QueryPerformanceFrequency(&liFreq) || liFreq.QuadPart == 0) { return 0; }
    _btQpcFreq = liFreq.QuadPart;
  }
  QueryPerformanceCounter(&liCount);
  return (long long)((double)liCount.QuadPart * 1000000.0 / (double)_btQpcFreq);
}

/* Raw Win32 writes instead of a CRT FILE*: during process shutdown the CRT
 * closes its streams, and a detached watchdog writing into a closed FILE*
 * could crash exactly when the accept test checks for a clean disconnect. */
static void BotTelemetry_WriteLine(const char *strFormat, ...)
{
  char achLine[BT_LINE_MAX];
  va_list ap;
  int iLength;
  DWORD dwWritten = 0;

  if (_btHandle == INVALID_HANDLE_VALUE) { return; }
  va_start(ap, strFormat);
  iLength = vsnprintf(achLine, sizeof(achLine) - 2, strFormat, ap);
  va_end(ap);
  if (iLength < 0) { return; }
  if (iLength > (int)sizeof(achLine) - 2) { iLength = (int)sizeof(achLine) - 2; }
  achLine[iLength] = '\n';
  achLine[iLength + 1] = 0;

  if (_btCsReady) { EnterCriticalSection(&_btCs); }
  WriteFile(_btHandle, achLine, (DWORD)(iLength + 1), &dwWritten, NULL);
  if (_btCsReady) { LeaveCriticalSection(&_btCs); }
}

static unsigned long long BotTelemetry_WallMs(void)
{
  FILETIME ft;
  ULARGE_INTEGER li;
  GetSystemTimeAsFileTime(&ft);
  li.LowPart = ft.dwLowDateTime;
  li.HighPart = ft.dwHighDateTime;
  return (li.QuadPart - 116444736000000000ULL) / 10000ULL;
}

static void BotTelemetry_CpuMs(unsigned long long *pullUser, unsigned long long *pullKernel)
{
  FILETIME ftCreate, ftExit, ftKernel, ftUser;
  ULARGE_INTEGER liKernel, liUser;
  if (!GetProcessTimes(GetCurrentProcess(), &ftCreate, &ftExit, &ftKernel, &ftUser)) {
    *pullUser = 0; *pullKernel = 0; return;
  }
  liKernel.LowPart = ftKernel.dwLowDateTime;
  liKernel.HighPart = ftKernel.dwHighDateTime;
  liUser.LowPart = ftUser.dwLowDateTime;
  liUser.HighPart = ftUser.dwHighDateTime;
  *pullKernel = liKernel.QuadPart / 10000ULL;
  *pullUser = liUser.QuadPart / 10000ULL;
}

/* Watchdog: never calls engine code and never takes an engine lock. If the
 * timer thread blocks, this thread keeps writing rows with ticks=0 - the only
 * way to distinguish a deadlock from a disabled driver afterwards. */
static DWORD WINAPI BotTelemetry_Watchdog(LPVOID)
{
  LONG lPrevTicks = 0, lPrevActions = 0, lPrevFrames = 0;
  LONG lPrevSkip = 0, lPrevDraw = 0;
  LONG lPrevDisabled = 0, lPrevGameOff = 0, lPrevNoLocal = 0, lPrevNoEntity = 0;
  unsigned long long ullPrevUser = 0, ullPrevKernel = 0;
  int iStall = 0;

  SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_LOWEST);
  for (;;) {
    LONG lTicks, lActions, lFrames, lSkip, lDraw;
    LONG lDisabled, lGameOff, lNoLocal, lNoEntity;
    LONG lLockMax, lLockLast, lTickMax, lTickSum, lTickCount;
    LONG lEnabled, lGameOn;
    unsigned long long ullUser = 0, ullKernel = 0;

    Sleep(1000);
    lTicks = InterlockedExchangeAdd(&_btTicks, 0);
    lActions = InterlockedExchangeAdd(&_btActions, 0);
    lFrames = InterlockedExchangeAdd(&_btFrames, 0);
    lSkip = InterlockedExchangeAdd(&_btRenderSkip, 0);
    lDraw = InterlockedExchangeAdd(&_btRenderDraw, 0);
    lDisabled = InterlockedExchangeAdd(&_btDisabled, 0);
    lGameOff = InterlockedExchangeAdd(&_btGameOff, 0);
    lNoLocal = InterlockedExchangeAdd(&_btNoLocal, 0);
    lNoEntity = InterlockedExchangeAdd(&_btNoEntity, 0);
    lEnabled = InterlockedExchangeAdd(&_btEnabled, 0);
    lGameOn = InterlockedExchangeAdd(&_btGameOn, 0);
    lLockMax = InterlockedExchange(&_btLockMaxUs, 0);
    lLockLast = InterlockedExchange(&_btLockLastUs, 0);
    lTickMax = InterlockedExchange(&_btTickMaxUs, 0);
    lTickSum = InterlockedExchange(&_btTickSumUs, 0);
    lTickCount = InterlockedExchange(&_btTickCount, 0);
    BotTelemetry_CpuMs(&ullUser, &ullKernel);

    if (lEnabled != 0 && lGameOn != 0 && (lTicks - lPrevTicks) <= 0) { ++iStall; }
    else { iStall = 0; }

    if (bot_iTelemetry != 0) {
      BotTelemetry_WriteLine(
        "%llu,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld,%.3f,%.3f,%.3f,%.3f,%llu,%llu,%d,%ld",
        BotTelemetry_WallMs(),
        lTicks - lPrevTicks, lActions - lPrevActions, lFrames - lPrevFrames,
        lSkip - lPrevSkip, lDraw - lPrevDraw,
        (LONG)InterlockedExchangeAdd(&_btLp, 0), lGameOn, lEnabled,
        lDisabled - lPrevDisabled, lGameOff - lPrevGameOff,
        lNoLocal - lPrevNoLocal, lNoEntity - lPrevNoEntity,
        (double)lLockMax / 1000.0, (double)lLockLast / 1000.0,
        (double)lTickMax / 1000.0,
        (lTickCount > 0 ? (double)lTickSum / (double)lTickCount / 1000.0 : 0.0),
        ullUser - ullPrevUser, ullKernel - ullPrevKernel,
        iStall, (LONG)InterlockedExchangeAdd(&_btReason, 0));
    }

    lPrevTicks = lTicks; lPrevActions = lActions; lPrevFrames = lFrames;
    lPrevSkip = lSkip; lPrevDraw = lDraw;
    lPrevDisabled = lDisabled; lPrevGameOff = lGameOff;
    lPrevNoLocal = lNoLocal; lPrevNoEntity = lNoEntity;
    ullPrevUser = ullUser; ullPrevKernel = ullKernel;
  }
  return 0;
}

void BotTelemetry_Start(void)
{
  const char *strEnv;
  char achExe[1024] = {0};

  if (_btStarted) { return; }
  _btStarted = TRUE;
  if (!_btCsReady) {
    InitializeCriticalSection(&_btCs);
    _btCsReady = TRUE;
  }

  strEnv = getenv("TSE_BOT_TELEMETRY");
  if (strEnv != NULL && strEnv[0] != 0) {
    _snprintf(_btPath, sizeof(_btPath) - 1, "%s", strEnv);
  } else if (GetModuleFileNameA(NULL, achExe, sizeof(achExe)) > 0) {
    char *pSlash = strrchr(achExe, '\\');
    if (pSlash != NULL) { *(pSlash + 1) = 0; } else { achExe[0] = 0; }
    _snprintf(_btPath, sizeof(_btPath) - 1, "%sBotTelemetry.csv", achExe);
  } else {
    _snprintf(_btPath, sizeof(_btPath) - 1, "BotTelemetry.csv");
  }
  _btPath[sizeof(_btPath) - 1] = 0;

  _btHandle = CreateFileA(_btPath, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE,
    NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
  if (_btHandle == INVALID_HANDLE_VALUE) {
    BotLog("[BotP0] WARNING: cannot open telemetry file '%s'\n", _btPath);
    return;
  }
  BotTelemetry_WriteLine("#bot-telemetry,rev=1");
  BotTelemetry_WriteLine("#build,tag=p0-telemetry-20261022,built=%s %s", __DATE__, __TIME__);
  BotTelemetry_WriteLine("#exe,%s", achExe);
  BotTelemetry_WriteLine("#columns,t_ms,ticks,actions,frames,renderskip,renderdraw,lp,"
    "gameon,enabled,disabled,gameoff,nolocal,noentity,lock_ms_max,lock_ms_last,"
    "tick_ms_max,tick_ms_avg,cpu_user_ms,cpu_kernel_ms,stall_s,reason");
  CreateThread(NULL, 0, BotTelemetry_Watchdog, NULL, 0, NULL);
  BotLog("[BotP0] telemetry=%s\n", _btPath);
}

void BotTelemetry_Config(int iNullRender, int iNullRenderFps, int iDedicatedServer)
{
  // Startup scripts and command-line scripts run at different lifecycle points.
  // Emit the effective state after changes, without adding per-frame I/O.
  static int lastNull=-1, lastFps=-1, lastDedicated=-1;
  static int lastEnabled=-1, lastLog=-1, lastTelemetry=-1;
  if (lastNull==iNullRender && lastFps==iNullRenderFps &&
      lastDedicated==iDedicatedServer && lastEnabled==(int)bot_bEnabled &&
      lastLog==(int)bot_iLogEvery && lastTelemetry==(int)bot_iTelemetry) return;
  lastNull=iNullRender; lastFps=iNullRenderFps; lastDedicated=iDedicatedServer;
  lastEnabled=(int)bot_bEnabled; lastLog=(int)bot_iLogEvery;
  lastTelemetry=(int)bot_iTelemetry;
  double fTickMs = 0.0;
  if (_pTimer != NULL) { fTickMs = (double)_pTimer->TickQuantum * 1000.0; }
  BotTelemetry_WriteLine("#config,nullrender=%d,nullrender_fps=%d,dedicated=%d,"
    "bot_enabled=%d,bot_iLogEvery=%d,bot_iTelemetry=%d,tick_ms=%.3f",
    iNullRender, iNullRenderFps, iDedicatedServer, (int)bot_bEnabled,
    (int)bot_iLogEvery, (int)bot_iTelemetry, fTickMs);
  BotLog("[BotP0] config nullrender=%d nullrender_fps=%d bot_enabled=%d tick_ms=%.1f\n",
    iNullRender, iNullRenderFps, (int)bot_bEnabled, fTickMs);
  if (iNullRender != 0 && !bot_bEnabled) {
    BotLog("[BotP0] WARNING: bot_bNullRender=1 but bot_bEnabled=0 - this client"
      " renders nothing and produces no bot actions.\n");
  }
}

void BotTelemetry_Note(const char *strText)
{
  BotTelemetry_WriteLine("#note,%s", strText);
}

void BotTelemetry_NoteF(const char *strFormat, ...)
{
  char achLine[BT_LINE_MAX];
  va_list ap;
  int iLength;
  va_start(ap, strFormat);
  iLength = vsnprintf(achLine, sizeof(achLine) - 1, strFormat, ap);
  va_end(ap);
  if (iLength < 0) { return; }
  achLine[sizeof(achLine) - 1] = 0;
  BotTelemetry_Note(achLine);
}

void BotTelemetry_Tick(int iEnabled, int iGameOn, int iLocalPlayers)
{
  long long llNow = BotTelemetry_NowUs();
  InterlockedIncrement(&_btTicks);
  _btEnabled = iEnabled;
  _btGameOn = iGameOn;
  _btLp = iLocalPlayers;

  if (_btPrevTickUs != 0) {
    long long llDelta = llNow - _btPrevTickUs;
    LONG lDelta = (LONG)(llDelta > 2000000LL ? 2000000LL : (llDelta < 0 ? 0 : llDelta));
    if (lDelta > _btTickMaxUs) { _btTickMaxUs = lDelta; }
    _btTickSumUs += lDelta;
    ++_btTickCount;
  }
  _btPrevTickUs = llNow;

  if (bot_bTelemetryConsole != 0 && (InterlockedExchangeAdd(&_btTicks, 0) % 100) == 0) {
    BotLog("[BotP0] ticks=%ld actions=%ld lp=%ld gameon=%d reason=%ld\n",
      InterlockedExchangeAdd(&_btTicks, 0), InterlockedExchangeAdd(&_btActions, 0),
      InterlockedExchangeAdd(&_btLp, 0), (int)InterlockedExchangeAdd(&_btGameOn, 0),
      InterlockedExchangeAdd(&_btReason, 0));
  }
}

void BotTelemetry_Reason(int iReason, int iEnabled, int iGameOn, int iLocalPlayers)
{
  _btReason = iReason;
  _btEnabled = iEnabled;
  _btGameOn = iGameOn;
  _btLp = iLocalPlayers;
  if (iReason == BOT_TM_REASON_DISABLED) { InterlockedIncrement(&_btDisabled); }
  else if (iReason == BOT_TM_REASON_GAMEOFF) { InterlockedIncrement(&_btGameOff); }
  else if (iReason == BOT_TM_REASON_NOLOCAL) { InterlockedIncrement(&_btNoLocal); }
}

void BotTelemetry_Action(int iSlot)
{
  InterlockedIncrement(&_btActions);
  if (iSlot >= 0 && iSlot < 4) { InterlockedIncrement(&_btActionBySlot[iSlot]); }
}

void BotTelemetry_NoEntity(void)
{
  InterlockedIncrement(&_btNoEntity);
}

void BotTelemetry_LockWaitBegin(void)
{
  _btLockStartUs = BotTelemetry_NowUs();
}

void BotTelemetry_LockWaitEnd(void)
{
  long long llDelta;
  LONG lUs;
  if (_btLockStartUs == 0) { return; }
  llDelta = BotTelemetry_NowUs() - _btLockStartUs;
  _btLockStartUs = 0;
  lUs = (LONG)(llDelta < 0 ? 0 : (llDelta > 2000000LL ? 2000000LL : llDelta));
  _btLockLastUs = lUs;
  if (lUs > _btLockMaxUs) { _btLockMaxUs = lUs; }
}

void BotTelemetry_Frame(void)
{
  InterlockedIncrement(&_btFrames);
}

void BotTelemetry_Render(int iSkipped)
{
  if (iSkipped != 0) { InterlockedIncrement(&_btRenderSkip); }
  else { InterlockedIncrement(&_btRenderDraw); }
}

void BotTelemetry_PaceFrame(int iFps)
{
  static long long llNextUs = 0;
  long long llNow, llPeriod, llWait;
  if (iFps <= 0 || iFps > 1000) { return; }
  llNow = BotTelemetry_NowUs();
  llPeriod = 1000000LL / (long long)iFps;
  if (llNextUs == 0) { llNextUs = llNow + llPeriod; return; }
  llWait = llNextUs - llNow;
  if (llWait < -4 * llPeriod) { llNextUs = llNow + llPeriod; return; }
  if (llWait > 250000LL) { llWait = 250000LL; }
  if (llWait > 0) { Sleep((DWORD)((llWait + 999) / 1000)); }
  llNextUs += llPeriod;
  if (llNextUs < llNow) { llNextUs = llNow + llPeriod; }
}

/* ------------------------------------------------------------------------ */

void BotDriver_StopGame(void)
{
  // StopGame can run on the main thread while the timer owns slot state.
  // Publish only the request; consume it before the next bot action.
  InterlockedExchange(&_botNavigationResetRequested,TRUE);
  InterlockedExchange(&_botSupplyMapReady,FALSE);
  InterlockedIncrement(&_botSupplyMapSerial);
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
  BotSupplyUpdateNavigation(pgame);
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
  _pShell->DeclareSymbol("user INDEX bot_iTelemetry;", &bot_iTelemetry);
  _pShell->DeclareSymbol("user INDEX bot_bTelemetryConsole;", &bot_bTelemetryConsole);

  // Diagnostic candidate: start the independent evidence writer. It never
  // touches engine state and can be silenced with bot_iTelemetry=0.
  BotTelemetry_Start();
  _pShell->DeclareSymbol("user INDEX bot_bSupplyNavigation;", &bot_bSupplyNavigation);
  _pShell->DeclareSymbol("user INDEX bot_bHumanAI;",      &bot_bHumanAI);
  _pShell->DeclareSymbol("user INDEX bot_iArenaTier;", &bot_iArenaTier);
  _pShell->DeclareSymbol("user INDEX bot_iRosterOffset;", &bot_iRosterOffset);
  _pShell->DeclareSymbol("user INDEX bot_iProfile0;",     &bot_iProfile0);
  _pShell->DeclareSymbol("user INDEX bot_iProfile1;",     &bot_iProfile1);
  _pShell->DeclareSymbol("user INDEX bot_iProfile2;",     &bot_iProfile2);
  _pShell->DeclareSymbol("user INDEX bot_iProfile3;",     &bot_iProfile3);
  _pShell->DeclareSymbol("user INDEX bot_iProfileSeed;",  &bot_iProfileSeed);
  _pShell->DeclareSymbol("user FLOAT bot_fStrafeScale;",  &bot_fStrafeScale);
  _pShell->DeclareSymbol("user INDEX bot_bDiag;",      &bot_bDiag);
  _pShell->DeclareSymbol("user INDEX bot_iDiagEvery;", &bot_iDiagEvery);
  _pShell->DeclareSymbol("user INDEX bot_iScanInterval;", &bot_iScanInterval);
  _pShell->DeclareSymbol("user FLOAT bot_fTargetRange;",  &bot_fTargetRange);
  _pShell->DeclareSymbol("user INDEX bot_iMaxLosRays;",   &bot_iMaxLosRays);
  _pShell->DeclareSymbol("user INDEX bot_iObstacleInterval;", &bot_iObstacleInterval);
  // P0 diagnostics: proves that this exact GameMP build loaded and Init ran.
  BotLog("[BotDiag] init: bot symbols declared\n");
}


/* ------------------------------------------------------------------------ */
/* Per-local-player bot state                                                 */
/* ------------------------------------------------------------------------ */

// BEGIN CECIL PLAYER OBSERVER
// Existing one-second telemetry only. Observe a composed nonneutral action
// whose native player velocity is near zero; never repair native state here.
static void BotPlayerObserverTelemetry(const CPlayer* player,INDEX slot,INDEX tick,
    ULONG generation,const CPlayerAction& action) {
  if(slot<0||slot>=4||tick<0||!player||!_pNetwork||!player->en_pwoWorld||
     (player->GetFlags()&ENF_DELETED))return;
  double request2=0,speed2=0;
  for(int i=1;i<=3;++i){
    const double request=action.pa_vTranslation(i),speed=player->en_vCurrentTranslationAbsolute(i);
    if(!std::isfinite(request)||!std::isfinite(speed))return;
    request2+=request*request;speed2+=speed*speed;
  }
  if(request2<.0025||speed2>.01)return;
  const auto& stack=player->en_stslStateStack;const INDEX count=stack.sa_UsedCount;
  const bool valid=count>=0&&count<=16&&stack.sa_Count>=count&&stack.sa_Count<=4096&&
    (count==0||stack.sa_Array!=NULL);
  char states[145]={};size_t used=0;
  if(valid)for(INDEX n=0;n<count;++n)
    used+=(size_t)std::snprintf(states+used,sizeof(states)-used,"%s%08lx",n?",":"",
      (unsigned long)(uint32_t)stack.sa_Array[n]);
  const CEntity* camera=player->m_penCamera;const CEntity* marker=player->m_penActionMarker;
  const auto localEntity=[&](const CEntity* entity){return entity&&!(entity->GetFlags()&ENF_DELETED)&&
    entity->en_pwoWorld==player->en_pwoWorld;};
  const bool cameraValid=localEntity(camera),markerValid=localEntity(marker);
  BotLog("[CecilPlayerObserve] local=%d tick=%d entity=%lu generation=%lu native_time=%.9f player_flags=%lu camera_present=%d camera=%lu camera_valid=%d marker_present=%d marker=%lu marker_valid=%d states_valid=%d count=%d states=%s input=(%.4f,%.4f,%.4f) desired=(%.4f,%.4f,%.4f) velocity=(%.4f,%.4f,%.4f) action_rotation=(%.4f,%.4f,%.4f) last_buttons=%lu\n",
    slot,tick,(unsigned long)player->en_ulID,(unsigned long)generation,(double)_pNetwork->GetGameTime(),
    (unsigned long)player->m_ulFlags,camera!=NULL,cameraValid?(unsigned long)camera->en_ulID:0UL,cameraValid,
    marker!=NULL,markerValid?(unsigned long)marker->en_ulID:0UL,markerValid,valid,count,states,
    (double)action.pa_vTranslation(1),(double)action.pa_vTranslation(2),(double)action.pa_vTranslation(3),
    (double)player->en_vDesiredTranslationRelative(1),(double)player->en_vDesiredTranslationRelative(2),(double)player->en_vDesiredTranslationRelative(3),
    (double)player->en_vCurrentTranslationAbsolute(1),(double)player->en_vCurrentTranslationAbsolute(2),(double)player->en_vCurrentTranslationAbsolute(3),
    (double)action.pa_aRotation(1),(double)action.pa_aRotation(2),(double)action.pa_aRotation(3),(unsigned long)player->m_ulLastButtons);
}
// END CECIL PLAYER OBSERVER

// BEGIN CECIL WEAPON OBSERVER
// Read-only observation after SetAction, under the existing network/world lock.
// Retail107: current/wanted are NOT native BringUp-completion markers. Earlier
// policy opportunity/dwell remains unobserved; only actual final choice is timed.
struct SWeaponObservationModel {
  INDEX anim=0; double start=0; ULONG flags=0; bool valid=false;
};
struct SWeaponObservationFrame {
  size_t source=0,world=0,weapon=0; ULONG entity=0,generation=0,weaponEntity=0;
  INDEX tick=0,desired=0,current=0,wanted=0,previous=0,change=0,anim=0,count=0;
  ULONG owned=0,lastButtons=0,finalButtons=0,pulse=0; double time=0,timer=0,cd=0;
  long stack[16]={}; SWeaponObservationModel model[2]; bool valid=false,phase=false,ready=false;
};
struct SWeaponObservation {
  SWeaponObservationFrame last; bool known=false,active=false,sawPhase=false,sawPulse=false,sawWanted=false,left=false,censor=false;
  unsigned long long sequence=0,epoch=0,emittedEpoch=0; unsigned dropped=0,rateCount=0; INDEX emitted=-1;
  double rateSecond=-1;size_t rateWorld=0;
};
static SWeaponObservation _weaponObservations[4];
static void BotWeaponObserverReset(INDEX slot) {
  if(slot<0||slot>=4)return;
  auto& s=_weaponObservations[slot];s.censor=s.censor||s.active;
  if(s.known&&s.epoch!=(std::numeric_limits<unsigned long long>::max)())++s.epoch;
  s.rateSecond=-1;s.rateCount=0;s.rateWorld=0;
  s.known=false;s.active=false;s.sawPhase=false;
}
static SWeaponObservationModel BotWeaponObserverModel(const CModelObject& m) {
  SWeaponObservationModel out;out.anim=m.ao_iCurrentAnim;out.start=m.ao_tmAnimStart;out.flags=m.ao_ulFlags;
  out.valid=m.ao_AnimData&&m.ao_AnimData->ad_Anims&&out.anim>=0&&out.anim<m.ao_AnimData->ad_NumberOfAnims&&std::isfinite(out.start);
  return out;
}
static bool BotWeaponObserverModelChanged(const SWeaponObservationModel& a,const SWeaponObservationModel& b) {
  return a.anim!=b.anim||a.start!=b.start||a.flags!=b.flags||a.valid!=b.valid;
}
static void BotWeaponObserverAfterAction(CPlayer* player,CPlayerSource* source,INDEX slot,INDEX tick,
    ULONG generation,INDEX desired,ULONG finalButtons,ULONG pulse,bool enabled,double cd) {
  if(slot<0||slot>=4)return;
  auto& s=_weaponObservations[slot];SWeaponObservationFrame f;
  f.tick=tick;f.desired=desired;f.generation=generation;f.finalButtons=finalButtons&(31UL<<14);
  f.pulse=pulse&(31UL<<14);f.cd=cd;f.source=(size_t)source;
  CPlayerWeapons* w=NULL;
  if(enabled&&source&&player&&_pNetwork&&std::isfinite(player->GetHealth())&&player->GetHealth()>0&&
     !(player->GetFlags()&ENF_DELETED)&&player->GetWorld()&&player->m_penWeapons!=NULL){
    w=player->GetPlayerWeapons();
    if(w&&!(w->GetFlags()&ENF_DELETED)&&w->GetWorld()==player->GetWorld()&&(CEntity*)w->m_penPlayer==player){
      f.world=(size_t)player->GetWorld();f.weapon=(size_t)w;f.entity=player->en_ulID;f.weaponEntity=w->en_ulID;
      f.current=w->m_iCurrentWeapon;f.wanted=w->m_iWantedWeapon;f.previous=w->m_iPreviousWeapon;
      f.owned=(ULONG)w->m_iAvailableWeapons;f.change=w->m_bChangeWeapon;f.anim=w->m_iAnim;
      f.lastButtons=player->m_ulLastButtons;f.time=_pNetwork->GetGameTime();f.timer=w->en_timeTimer;
      const auto& stack=w->en_stslStateStack;f.count=stack.sa_UsedCount;
      f.valid=std::isfinite(f.time)&&std::isfinite(f.timer)&&std::isfinite(cd)&&cd>=0&&
        f.current>=0&&f.current<=14&&f.wanted>=0&&f.wanted<=14&&desired>=0&&desired<=14&&
        f.count>=0&&f.count<=16&&stack.sa_Count>=f.count&&stack.sa_Count<=4096&&
        (f.count==0||stack.sa_Array!=NULL);
      if(f.valid){
        for(INDEX n=0;n<f.count;++n){f.stack[n]=stack.sa_Array[n];
          f.phase=f.phase||(f.stack[n]>=0x01920007L&&f.stack[n]<=0x0192001cL);
          f.ready=f.ready||f.stack[n]==0x019200c9L||(f.stack[n]>=0x0192001dL&&f.stack[n]<=0x0192002dL);}
        f.model[0]=BotWeaponObserverModel(w->m_moWeapon);f.model[1]=BotWeaponObserverModel(w->m_moWeaponSecond);
      }
    }
  }
  const auto& old=s.last;
  const bool continuous=s.known&&old.valid&&f.valid&&f.tick==old.tick+1&&f.source==old.source&&
    f.world==old.world&&f.weapon==old.weapon&&f.weaponEntity==old.weaponEntity&&f.entity==old.entity&&f.generation==old.generation&&
    f.time>=old.time&&f.time-old.time<=.25&&f.cd==old.cd;
  bool censored=s.censor||(s.active&&!continuous);
  unsigned long long censorChain=censored?s.sequence:0;s.censor=false;
  if(!continuous){s.active=false;s.sawPhase=false;s.sawPulse=false;s.sawWanted=false;s.left=false;}
  const bool choice=f.valid&&(!continuous||f.desired!=old.desired);
  if(continuous&&choice&&s.active){censored=true;censorChain=s.sequence;s.active=false;s.sawPhase=false;}
  const bool wasActive=s.active;
  if(f.valid&&f.desired>0&&choice&&
      (f.current!=f.desired||f.wanted!=f.desired||f.pulse)){
    if(s.sequence!=(std::numeric_limits<unsigned long long>::max)())++s.sequence;
    else censored=true;
    s.active=true;s.sawPhase=false;s.sawPulse=false;s.sawWanted=false;s.left=f.phase||f.wanted==f.desired;
  }
  if(s.active&&f.pulse&&f.finalButtons==f.pulse&&
      f.pulse==((ULONG)botcore::CombatWeaponGroup(f.desired)<<14))s.sawPulse=true;
  if(s.active&&s.sawWanted&&f.wanted!=f.desired){censored=true;censorChain=s.sequence;s.left=true;s.active=false;}
  if(s.active&&f.wanted==f.desired)s.sawWanted=true;
  if(s.active&&f.phase&&f.wanted==f.desired)s.sawPhase=true;
  const bool modelGap=s.active&&(!f.model[0].valid||
    ((f.current==3||f.previous==3)&&!f.model[1].valid));
  if(modelGap&&!s.left){censored=true;censorChain=s.sequence;s.left=true;}
  // Original107 registry: Idle c9 or Fire/continuations1d..2d corroborate
  // exit; absence from the switch family alone (empty/unknown stack) is OPEN.
  const bool completed=s.active&&s.sawPulse&&s.sawPhase&&!s.left&&!f.phase&&f.ready&&f.valid&&
    f.current==f.desired&&f.wanted==f.desired;
  const bool unobservedExit=s.active&&(!s.sawPhase||!s.sawPulse||s.left||!f.ready)&&!f.phase&&f.valid&&
    f.current==f.desired&&f.wanted==f.desired;
  if(unobservedExit){censored=true;censorChain=s.sequence;}
  bool nativeChanged=f.valid!=old.valid||(f.valid&&(!continuous||f.current!=old.current||f.wanted!=old.wanted||f.owned!=old.owned));
  bool phaseChanged=!continuous||f.count!=old.count||f.phase!=old.phase;
  if(continuous)for(INDEX n=0;n<f.count;++n)phaseChanged=phaseChanged||f.stack[n]!=old.stack[n];
  const bool observing=s.active||wasActive||completed;
  const bool animChanged=BotWeaponObserverModelChanged(f.model[0],old.model[0])||
    BotWeaponObserverModelChanged(f.model[1],old.model[1]);
  const bool event=!s.known||choice||f.pulse||nativeChanged||censored||completed||s.dropped||
    (observing&&(f.phase||old.phase)&&(phaseChanged||animChanged));
  const double second=std::floor(f.valid?f.time:(s.known?old.time:s.rateSecond));
  if((f.valid&&f.world!=s.rateWorld)||second>s.rateSecond){s.rateSecond=second;s.rateWorld=f.world;s.rateCount=0;}
  if(event&&((s.emitted==tick&&s.emittedEpoch==s.epoch)||s.rateCount>=40)){
    if(s.dropped!=(std::numeric_limits<unsigned>::max)())++s.dropped;
    s.active=false;s.sawPhase=false;s.censor=true;
  }else if(event){
    double lengths[2]={-1,-1};bool called[2]={false,false};
    if(w&&f.valid&&(observing||!s.known)){
      if(f.model[0].valid){called[0]=true;lengths[0]=w->m_moWeapon.GetAnimLength(f.model[0].anim);}
      if(f.model[1].valid){called[1]=true;lengths[1]=w->m_moWeaponSecond.GetAnimLength(f.model[1].anim);}
    }
    bool lengthGap=false;for(int n=0;n<2;++n)lengthGap=lengthGap||
      (called[n]&&(!std::isfinite(lengths[n])||lengths[n]<0));
    if(lengthGap){censored=true;censorChain=s.sequence;s.left=true;}
    char states[16*9+1]={};size_t used=0;
    if(f.valid)for(INDEX n=0;n<f.count;++n){
      const int written=std::snprintf(states+used,sizeof(states)-used,"%08lx%s",(unsigned long)f.stack[n],n+1<f.count?",":"");
      if(written<0||(size_t)written>=sizeof(states)-used){censored=true;break;}used+=(size_t)written;
    }
    BotLog("[CecilWeaponObserve] local=%d tick=%d entity=%lu generation=%lu weapon_entity=%lu native_time=%.6f cd=%.3f desired=%d pulse=%lu final=%lu last=%lu current=%d wanted=%d previous=%d owned=%lu change=%d chain=%llu observer_epoch=%llu active=%d saw_pulse=%d saw_phase=%d censor_chain=%llu left_censored=%d completed=%d censored=%d valid=%d dropped=%u count=%d states=%s timer=%.6f native_anim=%d model_valid1=%d anim1=%d start1=%.6f flags1=%lu length1=%.6f model_valid2=%d anim2=%d start2=%.6f flags2=%lu length2=%.6f\n",
      slot,tick,(unsigned long)f.entity,(unsigned long)f.generation,(unsigned long)f.weaponEntity,f.time,cd,
      desired,(unsigned long)f.pulse,(unsigned long)f.finalButtons,(unsigned long)f.lastButtons,f.current,f.wanted,
      f.previous,(unsigned long)f.owned,f.change,s.sequence,s.epoch,(int)s.active,(int)s.sawPulse,(int)s.sawPhase,censorChain,(int)s.left,
      (int)(completed&&!censored&&!s.dropped),(int)censored,(int)f.valid,s.dropped,f.count,states,f.timer,f.anim,
      (int)f.model[0].valid,f.model[0].anim,f.model[0].start,(unsigned long)f.model[0].flags,lengths[0],
      (int)f.model[1].valid,f.model[1].anim,f.model[1].start,(unsigned long)f.model[1].flags,lengths[1]);
    s.emitted=tick;s.emittedEpoch=s.epoch;++s.rateCount;s.dropped=0;
  }
  if(completed||unobservedExit)s.active=false;
  s.last=f;s.known=true;
}
// END CECIL WEAPON OBSERVER


struct SBotState {
  CPlayerSource *bs_ppls;     // player source this state belongs to
  ANGLE  bs_aHeading;         // accumulated heading (relative to spawn direction)
  INDEX  bs_iTick;            // ticks since (re)join
  ANGLE  bs_aPitch;
  INDEX  bs_iCombatTarget;
  botcore::CombatWeaponInput bs_weaponInput;
  botcore::ObstacleRecovery bs_navigation;
  ULONG bs_navEntity;
  ULONG bs_supplyEntity;
  bool bs_gravityKnown=false;
  FLOAT bs_gravity[3]={0,0,0};
  FLOAT  bs_lastHealth;       // previous tick health, for the damage alert
  botcore::CecilFireState bs_cecilFire;
  double bs_deadSince=-1,bs_lastSeen=-1000;
  ULONG  bs_ulCombatFireActions; // cumulative emitted combat input, not respawn
  bool bs_rotationRebase=true;
  CPlayer* bs_rotationInput=NULL; // original local entity, not a transient predictor
  ULONG bs_rotationInputId=0;
  LONG bs_rotationMapSerial=-1;
};

static SBotState _absBots[4] = {
  {NULL, 0.0f, 0}, {NULL, 0.0f, 0}, {NULL, 0.0f, 0}, {NULL, 0.0f, 0},
};

// Adopt only our requested-angle baseline at an actual local/map boundary.
// Native cumulative input and last-received angles remain Engine-owned. In
// particular, an ordinary respawn may retain a nonzero cumulative baseline.
static bool BotAdoptRotationBaseline(SBotState& bs,CPlayer* player,CPlayer* localInput,INDEX slot) {
  const LONG serial=InterlockedCompareExchange(&_botSupplyMapSerial,0,0);
  if(!player||!localInput)return false;
  const bool changed=bs.bs_rotationRebase||bs.bs_rotationMapSerial!=serial||
    bs.bs_rotationInput!=localInput||bs.bs_rotationInputId!=localInput->en_ulID;
  if(!changed)return true;
  if(!player->en_ulID||player->en_ulID!=localInput->en_ulID||!player->GetWorld()||
     player->GetWorld()!=localInput->GetWorld())return false;
  const FLOAT heading=player->m_aLastRotation(1),pitch=player->m_aLastRotation(2);
  if(!std::isfinite(heading)||!std::isfinite(pitch))return false;
  if(bot_bDiagnostics) {
    BotLog("[BotRotationBaseline] local=%d tick=%d map_serial=%ld entity=%lu input_entity=%lu world=%p attach=%d prior_input=%p prior_entity=%lu prior_map=%ld requested_before=(%.9g,%.9g) native_last=(%.9g,%.9g) local_before=(%.9g,%.9g) view=(%.9g,%.9g) spawn_clock=%.9g\n",
      slot,bs.bs_iTick,(long)serial,(unsigned long)player->en_ulID,(unsigned long)localInput->en_ulID,
      (void*)player->GetWorld(),(int)bs.bs_rotationRebase,(void*)bs.bs_rotationInput,
      (unsigned long)bs.bs_rotationInputId,(long)bs.bs_rotationMapSerial,
      bs.bs_aHeading,bs.bs_aPitch,heading,pitch,localInput->m_aLocalRotation(1),localInput->m_aLocalRotation(2),
      player->en_plViewpoint.pl_OrientationAngle(1),player->en_plViewpoint.pl_OrientationAngle(2),player->m_tmSpawned);
  }
  bs.bs_aHeading=heading;bs.bs_aPitch=pitch;
  bs.bs_rotationInput=localInput;bs.bs_rotationInputId=localInput->en_ulID;
  bs.bs_rotationMapSerial=serial;bs.bs_rotationRebase=false;
  return true;
}

// Per-slot human-AI state. Function-local statics keep construction lazy, so
// no engine-side global constructor ordering is involved.
static botcore::HumanBotPolicy &BotHumanPolicy(INDEX iLP)
{
  static botcore::HumanBotPolicy s_policies[4];
  return s_policies[iLP & 3];
}

static botcore::BotProfile &BotHumanProfile(INDEX iLP)
{
  static botcore::BotProfile s_profiles[4];
  return s_profiles[iLP & 3];
}

static INDEX *const _apiProfileSlot[4] = {
  &bot_iProfile0, &bot_iProfile1, &bot_iProfile2, &bot_iProfile3
};

// Build (or rebuild) the profile for one local slot. Called on join, rejoin
// and map change, i.e. exactly where the action state is reset anyway.
static void BotHumanAttach(INDEX iLP)
{
  INDEX profile_index=*_apiProfileSlot[iLP];
  if (profile_index<0) profile_index=bot_iRosterOffset+iLP;
  botcore::BotProfile &profile=BotHumanProfile(iLP);
  profile=botcore::BotProfile();
  if (!botcore::BuildRosterProfile(profile_index,iLP,(uint32_t)bot_iProfileSeed,&profile,bot_iArenaTier)) {
    botcore::BuildRosterProfile(profile_index,iLP,(uint32_t)bot_iProfileSeed,&profile,1);
    BotLog("[BotHuman] local=%d arena tier %d rejected, MITTEL fallback\n",iLP,(int)bot_iArenaTier);
  }
  BotHumanPolicy(iLP).Configure(&profile,bot_bSupplyNavigation?&BotCecilSettings():NULL);
  _absBots[iLP].bs_cecilFire.Reset();
  _absBots[iLP].bs_lastSeen=-1000;
  _absBots[iLP].bs_lastHealth=0.0f;
  // Map publication may retain the same source, entity ID and allocation.
  // The timer reads the fresh native baseline later under the world lock.
  _absBots[iLP].bs_rotationRebase=true;
  BotLog("[BotHuman] local=%d profile=%s tier=%d persona=%s seed=%lu model=arena-v1\n",
    iLP,profile.name,profile.tier,botcore::PersonalityName(profile.persona),
    (unsigned long)profile.seed);
}

static void BotResetNavigation(void)
{
  for (INDEX slot=0; slot<4; ++slot) {
    BotWeaponObserverReset(slot);
    BotSupplyReset(slot);
    _absBots[slot].bs_navigation.Reset();
    _absBots[slot].bs_navEntity=0;
  }
}

static const char *BotDriver_ReasonName(int iReason)
{
  switch (iReason) {
    case BOT_TM_REASON_DISABLED: return "DISABLED";
    case BOT_TM_REASON_GAMEOFF:  return "GAMEOFF";
    case BOT_TM_REASON_NOLOCAL:  return "NOLOCAL";
    default:                     return "ACTIVE";
  }
}

/* Single place that turns a timer invocation into a reason counter and logs
 * the transition once. Keeps the hot path free of engine calls. */
static void BotDriver_NoteConfigOnce(void)
{
  static BOOL bConfigLogged = FALSE;
  if (bConfigLogged) { return; }
  bConfigLogged = TRUE;
  BotTelemetry_NoteF("CONFIG,bot_bEnabled=%d,bot_fYawSpeed=%.2f,"
    "bot_fMoveFactor=%.2f,bot_fFirePeriod=%.2f,bot_iFireTicks=%d,"
    "bot_iLogEvery=%d,bot_bDiagnostics=%d,bot_bAutoCombat=%d,"
    "bot_bObstacleAvoidance=%d,bot_iTelemetry=%d,bot_bTelemetryConsole=%d",
    (int)bot_bEnabled, (double)bot_fYawSpeed, (double)bot_fMoveFactor,
    (double)bot_fFirePeriod, (int)bot_iFireTicks, (int)bot_iLogEvery,
    (int)bot_bDiagnostics, (int)bot_bAutoCombat, (int)bot_bObstacleAvoidance,
    (int)bot_iTelemetry, (int)bot_bTelemetryConsole);
}

/* Called exactly once per timer invocation (after the player loop) and in
 * every early-out branch. Counters and the state line live here, not in the
 * per-player loop, so `ticks` stays at 20/s regardless of local player count. */
static void BotDriver_ReportState(int iReason, int iEnabled, int iGameOn, int iLocalPlayers)
{
  static int iLastReason = -1;
  static int iLastLocal = -1;

  BotTelemetry_Reason(iReason, iEnabled, iGameOn, iLocalPlayers);

  if (iReason != iLastReason || iLocalPlayers != iLastLocal) {
    iLastReason = iReason;
    iLastLocal = iLocalPlayers;
    BotLog("[BotP0] state=%s local_players=%d bot_bEnabled=%d game_on=%d\n",
      BotDriver_ReasonName(iReason), iLocalPlayers, iEnabled, iGameOn);
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

static uint32_t BotCombatUsableWeapons(CPlayerWeapons *weapons)
{
  const CSessionProperties* session=(const CSessionProperties*)_pNetwork->GetSessionProperties();
  return BotCecilUsableWeapons(weapons,session->sp_bInfiniteAmmo!=FALSE);
}

static BOOL BotCombatVisible(CPlayer *player, CPlayer *target)
{
  if(_botRayBudget<=0||!player||!target)return FALSE;--_botRayBudget;
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
  if(_botRayBudget<=0)return 0;--_botRayBudget;
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

#include "BotSupplyNative.h"
// Original7f595 ApplyAction603fe980..603fea27: bit10, FOV/MaxFOV.
// The Human gate observes this factor; it never rescales the action intent.
static double BotHumanRotationDamping(const CPlayer* player,const CPlayerWeapons* weapon){
  const double invalid=std::numeric_limits<double>::quiet_NaN();
  if(!player)return invalid;
  if(!(player->m_ulFlags&(1UL<<10)))return 1;
  if(!weapon||!std::isfinite(weapon->m_fSniperFOV)||!std::isfinite(weapon->m_fSniperMaxFOV)||
     weapon->m_fSniperFOV<=0||weapon->m_fSniperMaxFOV<=0)return invalid;
  return weapon->m_fSniperFOV/weapon->m_fSniperMaxFOV;
}
// Player.es ApplyAction damps rotations using the pre-action zoom flag/FOV.
static double BotCecilFinalBodyYaw(CPlayer* player,double actionDelta){
  const double invalid=std::numeric_limits<double>::quiet_NaN();
  if(!player||!std::isfinite(actionDelta))return invalid;
  const double head=player->en_plViewpoint.pl_OrientationAngle(1);
  if(!std::isfinite(head))return invalid;
  double damping=1;
  if(player->m_ulFlags&(1UL<<10)){ // Retail107 PLF_ISZOOMING, Player.es:240.
    if(!player->m_penWeapons)return invalid;
    const CPlayerWeapons* w=player->GetPlayerWeapons();
    if(!std::isfinite(w->m_fSniperFOV)||!std::isfinite(w->m_fSniperMaxFOV)||w->m_fSniperFOV<=0||w->m_fSniperMaxFOV<=0)return invalid;
    damping=w->m_fSniperFOV/w->m_fSniperMaxFOV;
  }
  const double result=head+actionDelta*damping;
  return std::isfinite(result)?result:invalid;
}
static bool BotCecilActionFinite(const CPlayerAction& action){
  for(int axis=1;axis<=3;++axis)
    if(!std::isfinite(action.pa_vTranslation(axis))||!std::isfinite(action.pa_aRotation(axis))||!std::isfinite(action.pa_aViewRotation(axis)))return false;
  return true;
}
// Invalid snapshots still replace the source action: skipping SetAction would
// keep a previous move/fire command alive. Retain only finite absolute view axes.
static void BotCecilNeutralAction(CPlayerSource* source){
  CPlayerAction neutral;
  {CTSingleLock actionLock(&source->pls_csAction,TRUE);neutral=source->pls_paAction;}
  neutral.pa_vTranslation=FLOAT3D(0,0,0);neutral.pa_ulButtons=0;
  if(!BotCecilActionFinite(neutral))neutral.Clear();
  source->SetAction(neutral);
}

// Called only from the action path while the native world mutex is held.
static void BotCecilLogReferences(CPlayer* player) {
  static LONG reported=-1;
  const LONG serial=InterlockedCompareExchange(&_botSupplyMapSerial,0,0);
  if(!player||reported==serial)return;
  reported=serial;
  const auto& graph=BotSupplyGraph();
  for(size_t slot=0;slot<graph.points.size();++slot){
    const auto& point=graph.points[slot];
    const int ids[2]={point.important_entity,point.lock_entity};
    for(int role=0;role<2;++role)if(ids[role]>=0){
      CEntity* entity=player->GetWorld()->EntityFromID((ULONG)ids[role]);
      const bool present=entity&&(entity->GetFlags()&ENF_DELETED)==0;
      const char* type=present&&entity->GetClass()?(const char*)entity->GetClass()->GetName():"missing";
      BotLog("[CecilReference] map_serial=%ld slot=%d id=%d role=%s entity=%d present=%d class=%s\n",
        (long)serial,(int)slot,point.id,role?"lock":"important",ids[role],present,type);
    }
  }
}


static int BotDriver_InactiveReason(CGame *pgame)
{
  if (!bot_bEnabled) { return BOT_TM_REASON_DISABLED; }
  if (pgame == NULL || !pgame->gm_bGameOn) { return BOT_TM_REASON_GAMEOFF; }
  return BOT_TM_REASON_ACTIVE;
}

BOOL BotDriver_HandleTimer(CGame *pgame)
{
  // P0 diagnostics: this heartbeat sits BEFORE every gate and proves that the
  // WinMM timer thread actually reaches GameHandleTimer (also in menus).
  // CShell::GetINDEX returns -666 for symbols missing from this binary
  // (release build); it never aborts, so the values are read defensively.
  if (bot_bDiag) {
    bot_iDiagTicks++;
    const BOOL bFirst = !_botDiagLoggedFirst;
    if (bFirst || (bot_iDiagEvery>0 && (bot_iDiagTicks%bot_iDiagEvery)==0)) {
      _botDiagLoggedFirst = TRUE;
      INDEX iMask = 0;
      if (pgame!=NULL) {
        for (INDEX iLP=0; iLP<4; ++iLP) {
          if (pgame->gm_lpLocalPlayers[iLP].lp_pplsPlayerSource!=NULL) iMask|=(1L<<iLP);
        }
      }
      const INDEX iFpsActive   = _pShell->GetINDEX("sam_iMaxFPSActive");
      const INDEX iFpsInactive = _pShell->GetINDEX("sam_iMaxFPSInactive");
      const INDEX iSndFormat   = _pShell->GetINDEX("snd_iFormat");
      BotLog("[BotDiag] call=%d gameon=%d enabled=%d locals=%d%d%d%d fpsActive=%d fpsInactive=%d snd=%d%s\n",
        bot_iDiagTicks, (pgame!=NULL && pgame->gm_bGameOn)?1:0, bot_bEnabled?1:0,
        (iMask&1)?1:0,(iMask&2)?1:0,(iMask&4)?1:0,(iMask&8)?1:0,
        iFpsActive,iFpsInactive,iSndFormat, bFirst?" firstcall":"");
    }
  }
  if (InterlockedExchange(&_botNavigationResetRequested,FALSE)) BotResetNavigation();

  // P0 evidence: count every timer invocation before any early-out. Only the
  // player-source pointer is read here - no world access, no engine lock.
  INDEX ctLocalPlayers = 0;
  for (INDEX iTelemetry = 0; iTelemetry < 4; ++iTelemetry) {
    if (pgame != NULL && pgame->gm_lpLocalPlayers[iTelemetry].lp_pplsPlayerSource != NULL) {
      ++ctLocalPlayers;
    }
  }

  BotTelemetry_Tick(bot_bEnabled != FALSE, pgame != NULL && pgame->gm_bGameOn != FALSE,
    ctLocalPlayers);

  if (!bot_bEnabled || pgame==NULL || !pgame->gm_bGameOn) {
    BotDriver_ReportState(BotDriver_InactiveReason(pgame), bot_bEnabled != FALSE,
      pgame != NULL && pgame->gm_bGameOn != FALSE, ctLocalPlayers);
    BotResetNavigation();
    return FALSE;
  }

  // Engine107 ray casting shares sector scratch data with world simulation.
  // Keep entities and every ray (including its destructor) under the native
  // world/network mutex. The timer already owns hooks: order 1000 -> 2000.
  // GetLocalPlayerEntity's internal lock ends before its pointer is returned.
  BotTelemetry_LockWaitBegin();
  CTSingleLock slBotWorld(&_pNetwork->ga_csNetwork, TRUE);
  BotTelemetry_LockWaitEnd();

  const FLOAT fTick     = _pTimer->TickQuantum;             // 1/20 s

  // fire pulse parameters (derived once per tick, fully deterministic)
  INDEX ctPeriodTicks = 0;
  INDEX ctFireTicks   = 0;
  if (bot_fFirePeriod >= fTick) {
    ctPeriodTicks = (INDEX)(bot_fFirePeriod/fTick + 0.5f);
    ctFireTicks   = Clamp<INDEX>(bot_iFireTicks, 0, ctPeriodTicks);
  }

  // for all possible local players (hard limit 4 - see NET_MAXLOCALPLAYERS)
  BOOL bActed = FALSE;
  for (INDEX iLP=0; iLP<4; iLP++) {
    if (ctLocalPlayers == 0) {
      // Enabled and in game, but no local player source at all.
      BotDriver_ReportState(BOT_TM_REASON_NOLOCAL, 1, 1, 0);
    }
    _botRayBudget=16;
    SBotState &bs = _absBots[iLP];
    CLocalPlayer &lp = pgame->gm_lpLocalPlayers[iLP];
    CPlayerSource *ppls = lp.lp_pplsPlayerSource;

    // if this local player exists
    if (ppls==NULL) {
      BotWeaponObserverReset(iLP);
      BotSupplyReset(iLP);bs.bs_supplyEntity=0;
      bs.bs_navigation.Reset(); bs.bs_navEntity=0;bs.bs_ppls=NULL;bs.bs_deadSince=-1;
      continue;
    }
    CPlayer *localInput = (CPlayer *)CEntity::GetPlayerEntity(ppls->pls_Index);
    if (localInput==NULL) {
      BotWeaponObserverReset(iLP);
      BotTelemetry_NoEntity();
      BotSupplyReset(iLP);bs.bs_supplyEntity=0;
      bs.bs_navigation.Reset(); bs.bs_navEntity=0;
      const CSessionProperties* session=(const CSessionProperties*)_pNetwork->GetSessionProperties();
      const bool dm=session->sp_gmGameMode==CSessionProperties::GM_FRAGMATCH||session->sp_gmGameMode==CSessionProperties::GM_SCOREMATCH;
      // Only a previously attached source may request a native respawn.
      if(bs.bs_ppls==ppls&&bot_bAutoCombat&&bot_iTestTarget<0&&dm){
        ++bs.bs_iTick;double now=bs.bs_iTick*fTick;
        if(bs.bs_deadSince<0)bs.bs_deadSince=now;
        CPlayerAction missing;
        {CTSingleLock actionLock(&ppls->pls_csAction,TRUE);missing=ppls->pls_paAction;}
        missing.pa_vTranslation=FLOAT3D(0,0,0);missing.pa_ulButtons=0;
        if(now-bs.bs_deadSince>=BotCecilSettings().fRespawnDelay&&(bs.bs_iTick&4)==0)missing.pa_ulButtons=BOT_PLACT_FIRE;
        ppls->SetAction(missing);BotTelemetry_Action(iLP);bActed=TRUE;
      }
      continue;
    }

    // reset state when a new player source appears (join / rejoin / map change)
    if (bs.bs_ppls != ppls) {
      BotSupplyReset(iLP);bs.bs_supplyEntity=0;
      bs.bs_ppls     = ppls;
      bs.bs_aHeading = 0.0f;
      bs.bs_iTick    = 0;
      bs.bs_deadSince=-1;
      bs.bs_ulCombatFireActions=0;bs.bs_gravityKnown=false;
      bs.bs_aPitch   = 0.0f;
      bs.bs_iCombatTarget = -1;
      bs.bs_weaponInput.Reset();
      bs.bs_navigation.Reset();
      bs.bs_navEntity=0;
      BotHumanAttach(iLP);
      BotLog("[BotDriver] local player %d (player index %d) is now bot-driven: %s\n",
        iLP, ppls->pls_Index, (const char *)ppls->pls_pcCharacter.pc_strName);
    }
    bs.bs_iTick++;

    // 1) accumulate heading (same convention as CPlayer::m_aLocalRotation:
    //    absolute accumulated angle relative to spawn orientation - never wrap!)
    CPlayer *player = (CPlayer *)_pNetwork->GetLocalPlayerEntity(ppls);
    const ULONG entityId=player?player->en_ulID:0;
    if(bs.bs_supplyEntity!=entityId){
      bs.bs_gravityKnown=false;bs.bs_rotationRebase=true;
      BotSupplyReset(iLP);bs.bs_supplyEntity=entityId;BotHumanPolicy(iLP).Reset();bs.bs_deadSince=-1;bs.bs_lastSeen=-1000;
      bs.bs_weaponInput.Reset();bs.bs_cecilFire.Reset();
    }
    if(player==NULL){
      bs.bs_rotationRebase=true;BotCecilNeutralAction(ppls);bActed=TRUE;
      continue;
    }
    if(!BotAdoptRotationBaseline(bs,player,localInput,iLP)){
      BotLog("[CecilInvalidAction] local=%d tick=%d rejected=rotation_baseline\n",iLP,bs.bs_iTick);
      BotCecilNeutralAction(ppls);bActed=TRUE;
      continue;
    }
    // ponytail: fixed-target action test; walls still need a suitable test arena.
    CPlayer *target = bot_iTestTarget>=0 && bot_iTestTarget<16
      ? (CPlayer *)CEntity::GetPlayerEntity(bot_iTestTarget) : NULL;
    FLOAT moveFactor = Clamp(bot_fMoveFactor, 0.0f, 1.0f);
    BOOL testAimReady = TRUE;
    const BOOL automatic=bot_bAutoCombat && bot_iTestTarget<0;
    const BOOL humanMode=bot_bHumanAI||bot_bSupplyNavigation;
    INDEX combatWeapon=0;
    BOOL supplyActive=FALSE;
    FLOAT cecilUp=0;ULONG cecilFlags=0,cecilButtons=0;INDEX cecilFloorStatus=-1;
    BOOL targetVisible=FALSE,cecilUseControl=FALSE;
    SCecilFollowGoal navFollow;
    ULONG combatSelect=0;
    BOOL combatDeathmatch=FALSE;
    BOOL combatHold=bot_fMoveFactor<=0;
    BOOL humanFire=FALSE;      // set only by the profile-driven path
    FLOAT humanStrafe=0.0f;    // -1..1, applied only when bot_fStrafeScale > 0
    FLOAT humanScanYaw=0.0f;   // scan delta while no opponent is perceived
    FLOAT humanTargetDistance=0.0f; // frozen last-seen distance from the policy
    // Existing diagnostics/cadence only; stack snapshots never feed decisions.
    const bool aimTraceEnabled=bot_bDiagnostics && bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0;
    botcore::HumanAimTrace aimTrace;
    botcore::BotCommand aimTraceCommand;
    bool aimTraceCaptured=false;
    INDEX aimCurrent=0,aimWanted=0;
    if (automatic) {
      testAimReady=FALSE;
      const CSessionProperties *session=(const CSessionProperties *)_pNetwork->GetSessionProperties();
      const BOOL deathmatch=session->sp_gmGameMode==CSessionProperties::GM_SCOREMATCH ||
        session->sp_gmGameMode==CSessionProperties::GM_FRAGMATCH;
      combatDeathmatch=deathmatch;
      botcore::CombatDecision decision={-1,1,0,0,0,false};
      INDEX visible=0;
      if (humanMode) {
        // ---------------------------------------------------------------
        // Profile-driven path: perception -> target -> aim -> loadout.
        // The policy only ever sees what this client can actually observe;
        // all ray casts are budgeted by PlanLosQueries().
        // ---------------------------------------------------------------
        botcore::HumanBotPolicy &human=BotHumanPolicy(iLP);
        CPlayerWeapons *hw=(player!=NULL && player->m_penWeapons!=NULL)
          ? player->GetPlayerWeapons() : NULL;
        if (player!=NULL && deathmatch && player->GetHealth()>0 && hw!=NULL) {
          const CPlacement3D eye=BotCombatEye(player);
          botcore::WorldView world;
          world.cecil=bot_bSupplyNavigation!=FALSE;
          world.tick=bs.bs_iTick;
          world.pose.x=eye.pl_PositionVector(1);
          world.pose.y=eye.pl_PositionVector(2);
          world.pose.z=eye.pl_PositionVector(3);
          world.pose.yaw_deg=eye.pl_OrientationAngle(1);
          world.pose.pitch_deg=eye.pl_OrientationAngle(2);
          if(bot_bSupplyNavigation){
            world.pose.frame=BotCecilBodyFrame(player);
            world.pose.yaw_deg=player->en_plViewpoint.pl_OrientationAngle(1);
            world.pose.pitch_deg=player->en_plViewpoint.pl_OrientationAngle(2);
          }
          world.alive=TRUE;
          world.health=player->GetHealth();
          world.max_health=player->m_fMaxHealth;
          world.deathmatch=deathmatch!=FALSE;
          world.usable_weapons=BotCombatUsableWeapons(hw);
          world.current_weapon=hw->m_iCurrentWeapon;
          world.rotation_damping=BotHumanRotationDamping(player,hw);

          if (bs.bs_lastHealth>0.0f && world.health<bs.bs_lastHealth) {
            human.NotifyDamage(bs.bs_lastHealth,world.health);
          }
          bs.bs_lastHealth=(FLOAT)world.health;

          human.BeginTick(world);

          botcore::SenseInput sensed[16];
          CPlayer *candidate[16];
          INDEX count=0;
          for (INDEX index=0; index<16; ++index) {
            CPlayer *other=(CPlayer *)CEntity::GetPlayerEntity(index);
            if (other==player) continue;
            const BOOL local=BotCombatIsLocal(pgame,index);
            if (local && bot_bCombatSkipLocals) continue;
            const CPlacement3D otherEye=other?BotCombatEye(other):eye;
            botcore::SenseInput &si=sensed[count];si=botcore::SenseInput();
            si.entity_id=other?other->en_ulID:0;si.generation=(uint32_t)_botSupplyMapSerial;
            si.index=index;
            si.x=otherEye.pl_PositionVector(1);
            si.y=otherEye.pl_PositionVector(2);
            si.z=otherEye.pl_PositionVector(3);
            si.vx=other?other->en_vCurrentTranslationAbsolute(1):0;
            si.vy=other?other->en_vCurrentTranslationAbsolute(2):0;
            si.vz=other?other->en_vCurrentTranslationAbsolute(3):0;
            si.health=other?other->GetHealth():0;
            si.alive=other&&other->GetHealth()>0&&(other->GetFlags()&ENF_DELETED)==0;
            si.local=local!=FALSE;
            si.enemy=other&&(player->en_pcCharacter.GetTeam()==""||
              player->en_pcCharacter.GetTeam()!=other->en_pcCharacter.GetTeam());
            candidate[count]=other;
            ++count;
          }

          bool needsLos[16];
          human.PlanLosQueries(sensed,count,needsLos);
          bool hasLos[16];
          for (INDEX i=0; i<count; ++i) {
            hasLos[i]=needsLos[i] && BotCombatVisible(player,candidate[i])!=FALSE;
            if (hasLos[i]) ++visible;
          }

          const botcore::BotCommand command=human.Step(world,sensed,hasLos,count,fTick,
            aimTraceEnabled?&aimTrace:NULL);
          if(aimTraceEnabled){aimTraceCommand=command;aimTraceCaptured=true;aimCurrent=hw->m_iCurrentWeapon;aimWanted=hw->m_iWantedWeapon;}

          decision.target=command.target;
          decision.weapon=command.weapon;
          decision.yawDelta=command.yaw_delta_deg;
          decision.pitchDelta=command.pitch_delta_deg;
          decision.moveFactor=command.forward;
          decision.fireAllowed=command.fire;
          humanFire=command.fire?TRUE:FALSE;
          humanStrafe=(FLOAT)command.strafe;
          humanScanYaw=(FLOAT)command.yaw_delta_deg;
          humanTargetDistance=(FLOAT)command.distance_m;
          targetVisible=command.target_visible;
          if(targetVisible)bs.bs_lastSeen=bs.bs_iTick*fTick;
          const botcore::TrackState* observed=human.perception().Track(command.target);
          if(observed&&observed->confidence>.5){
            navFollow.valid=true;navFollow.x=observed->x;navFollow.y=observed->y;navFollow.z=observed->z;
            navFollow.entity=observed->entity_id;navFollow.generation=observed->generation;
            navFollow.expiresAt=observed->last_seen_tick*fTick+human.profile().skill.memory_s;
          }

          if (bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0) {
            BotLog("[BotHuman] local=%d tick=%d profile=%s target=%d vis=%d fire=%d weapon=%d dist=%.1f pref=%.1f move=%.2f strafe=%.2f err=%.2f rays=%d skipped=%d switches=%d overshoots=%d\n",
              iLP,bs.bs_iTick,BotHumanProfile(iLP).label,command.target,
              command.target_visible?1:0,command.fire?1:0,command.weapon,
              command.distance_m,command.preferred_range_m,command.forward,
              command.strafe,command.aim_error_deg,human.los_queries_last_tick(),
              human.ray_budget_skips(),human.target_switches(),
              human.aim().overshoot_events());
          }
        } else {
          // Dead or unarmed: keep the policy clock in sync so it clears its
          // memory on the death transition, but move and shoot nothing.
          botcore::WorldView fallen;
          fallen.tick=bs.bs_iTick;
          fallen.alive=FALSE;
          human.BeginTick(fallen);
          moveFactor=0.0f;
          bs.bs_lastHealth=0.0f;
        }
      } else if (player!=NULL && deathmatch && player->GetHealth()>0 && player->m_penWeapons!=NULL) {
        botcore::TargetInfo candidates[16];
        const FLOAT3D selfPos=BotCombatEye(player).pl_PositionVector;
        // Full target scans may be throttled; between scans only the cached
        // target is re-verified (1 ray) while the 20 Hz aim keeps tracking it.
        const BOOL bFullScan=bot_iScanInterval<=1 || (bs.bs_iTick%bot_iScanInterval)==1;
        if (!bFullScan && bs.bs_iCombatTarget>=0 && bs.bs_iCombatTarget<16) {
          CPlayer *cached=(CPlayer *)CEntity::GetPlayerEntity(bs.bs_iCombatTarget);
          const BOOL local=BotCombatIsLocal(pgame,bs.bs_iCombatTarget);
          if (cached!=NULL && cached!=player && cached->GetHealth()>0 &&
              !(bot_bCombatSkipLocals && local) &&
              (bot_fTargetRange<=0 ||
               (BotCombatEye(cached).pl_PositionVector-selfPos).Length()<=bot_fTargetRange)) {
            const botcore::TargetInfo snapshot=BotCombatSnapshot(cached,bs.bs_iCombatTarget,local);
            if (botcore::CombatValidPlayer(snapshot) && BotCombatVisible(player,cached))
              candidates[visible++]=snapshot;
          }
        } else if (bFullScan) {
          // pass 1: distance-filtered collection, no rays yet
          struct ScanEntry { FLOAT fDist; INDEX index; BOOL local; };
          ScanEntry entries[16];
          INDEX ctEntries=0;
          for (INDEX index=0; index<16; ++index) {
            CPlayer *other=(CPlayer *)CEntity::GetPlayerEntity(index);
            const BOOL local=BotCombatIsLocal(pgame,index);
            if (other==NULL || other==player || other->GetHealth()<=0 ||
                (bot_bCombatSkipLocals && local)) continue;
            const FLOAT fDist=(BotCombatEye(other).pl_PositionVector-selfPos).Length();
            if (bot_fTargetRange>0 && fDist>bot_fTargetRange) continue;
            entries[ctEntries].fDist=fDist;
            entries[ctEntries].index=index;
            entries[ctEntries].local=local;
            ++ctEntries;
          }
          // deterministic nearest-first order (insertion sort, N<=16)
          for (INDEX i=1; i<ctEntries; ++i) {
            const ScanEntry se=entries[i];
            INDEX j=i;
            while (j>0 && entries[j-1].fDist>se.fDist) { entries[j]=entries[j-1]; --j; }
            entries[j]=se;
          }
          // pass 2: LOS verification nearest-first (optional ray budget)
          INDEX ctRays=0;
          for (INDEX i=0; i<ctEntries; ++i) {
            if (bot_iMaxLosRays>0 && ctRays>=bot_iMaxLosRays) break;
            ++ctRays;
            CPlayer *other=(CPlayer *)CEntity::GetPlayerEntity(entries[i].index);
            const botcore::TargetInfo snapshot=BotCombatSnapshot(other,entries[i].index,entries[i].local);
            if (botcore::CombatValidPlayer(snapshot) && BotCombatVisible(player,other))
              candidates[visible++]=snapshot;
          }
        }
        CPlayerWeapons *weapons=player->GetPlayerWeapons();
        const CPlacement3D eye=BotCombatEye(player);
        const botcore::CombatInput input={BotCombatSnapshot(player,ppls->pls_Index,TRUE),
          eye.pl_OrientationAngle(1),eye.pl_OrientationAngle(2),
          std::fabs(bot_fYawSpeed)*fTick,moveFactor,
          BotCombatUsableWeapons(weapons),
          bot_bCombatSkipLocals!=FALSE,8.0};
        decision=botcore::DecideCombat(candidates,visible,input);
      }
      if (decision.target>=0) {
        target=(CPlayer *)CEntity::GetPlayerEntity(decision.target);
        bs.bs_aHeading=player->m_aLastRotation(1)+(FLOAT)decision.yawDelta;
        bs.bs_aPitch=player->m_aLastRotation(2)+(FLOAT)decision.pitchDelta;
        moveFactor=(FLOAT)decision.moveFactor;
        testAimReady=decision.fireAllowed;
        if (target==NULL) testAimReady=FALSE; // a remembered player may have left
        combatWeapon=decision.weapon;
        // Human decisions use the frozen perceived position, never hidden live state.
        const FLOAT distance=humanMode ? humanTargetDistance
          : (target!=NULL ? (BotCombatEye(target).pl_PositionVector-
              BotCombatEye(player).pl_PositionVector).Length() : 0.0f);
        combatHold=combatHold || distance<=((combatWeapon==1 || combatWeapon==10)?1.5f:8.0f);
        CPlayerWeapons *weapons=player->GetPlayerWeapons();
        testAimReady=testAimReady && weapons->m_iCurrentWeapon==combatWeapon &&
          weapons->m_iWantedWeapon==combatWeapon;
        if (bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0) {
          BotLog("[BotCombatWeapon] local=%d tick=%d desired=%d current=%d wanted=%d group=%d buttons=%lu bullets=%d shells=%d napalm=%d cells=%d sniper=%d\n",
            iLP,bs.bs_iTick,combatWeapon,weapons->m_iCurrentWeapon,weapons->m_iWantedWeapon,
            botcore::CombatWeaponGroup(combatWeapon),(unsigned long)combatSelect,
            weapons->m_iBullets,weapons->m_iShells,weapons->m_iNapalm,
            weapons->m_iElectricity,weapons->m_iSniperBullets);
        }
      } else if (humanMode) {
        // Search with the configured travel input and existing obstacle recovery.
        // No opponent position is used; perception/aim/fire remain profile-driven.
        if (player!=NULL && player->GetHealth()>0 && deathmatch) {
          bs.bs_aHeading+=humanScanYaw;
        } else { moveFactor=0.0f; }
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

    if(bot_bSupplyNavigation&&automatic&&combatDeathmatch){
      const bool ready=InterlockedCompareExchange(&_botSupplyMapReady,0,0)!=0;
      SCecilMove supply;
      if(ready)BotCecilLogReferences(player);
      if(ready){
        supply=BotSupplyTick(player,iLP,bs.bs_iTick,targetVisible?humanTargetDistance:1000,&navFollow);
        cecilUseControl=supply.useControl;cecilButtons=supply.buttons;
      }
      // Keep a feasible visible fight unless an urgent item or traversal
      // control owns movement. Distance alone must not turn an ordinary pickup
      // into a reason to drop aim/fire. First ranged weapons remain urgent.
      if(ready&&(supply.active||supply.ownsMovement)&&player&&player->m_penWeapons&&
         (supply.flightGoal||supply.useControl||!targetVisible||(supply.itemGoal&&supply.urgent))){
        bs.bs_aHeading=player->m_aLastRotation(1)+(FLOAT)supply.yaw_delta;
        bs.bs_aPitch=player->m_aLastRotation(2)+(FLOAT)supply.pitch_delta;
        moveFactor=(FLOAT)supply.forward;humanStrafe=(FLOAT)supply.strafe;
        cecilUp=(FLOAT)supply.up;cecilFlags=supply.flags;
        combatHold=FALSE;testAimReady=FALSE;humanFire=FALSE;supplyActive=TRUE;
      }else if(!ready){moveFactor=0;humanStrafe=0;testAimReady=FALSE;}
    }

    // Stateful native selection is polled exactly once after arbitration.
    if(automatic&&player!=NULL&&player->m_penWeapons!=NULL){
      const bool travelKnife=botcore::CecilTravelKnife(bs.bs_iTick*fTick,bs.bs_lastSeen,supplyActive!=FALSE,targetVisible!=FALSE);
      const INDEX finalWeapon=botcore::ResolveSupplyWeapon(combatWeapon,travelKnife);
      combatWeapon=finalWeapon;
      combatSelect=bs.bs_weaponInput.Poll(bs.bs_iTick,finalWeapon,
        player->GetPlayerWeapons()->m_iWantedWeapon,player->m_ulLastButtons);
      if(supplyActive&&bs.bs_iTick%40==0)BotLog("[BotSupplyWeapon] local=%d tick=%d desired=%d current=%d wanted=%d buttons=%lu\n",iLP,bs.bs_iTick,finalWeapon,player->GetPlayerWeapons()->m_iCurrentWeapon,player->GetPlayerWeapons()->m_iWantedWeapon,(unsigned long)combatSelect);
    }

    if (bot_bObstacleAvoidance && !bot_bSupplyNavigation && automatic && combatDeathmatch && player!=NULL && !supplyActive) {
      if (bs.bs_navEntity!=entityId) { bs.bs_navigation.Reset(); bs.bs_navEntity=entityId; }
      const BOOL alive=player->GetHealth()>0;
      const FLOAT yaw=BotCombatEye(player).pl_OrientationAngle(1);
      FLOAT front=3,left=3,right=3;
      INDEX frontHitType=0;
      if (alive && !combatHold) {
        front=BotObstacleDistance(player,yaw,&frontHitType);
        if (bot_iObstacleInterval<=1 || (bs.bs_iTick%bot_iObstacleInterval)==0) {
          left=BotObstacleDistance(player,yaw+60.0f);
          right=BotObstacleDistance(player,yaw-60.0f);
        }
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
    } else { bs.bs_navigation.Reset(); bs.bs_navEntity=0; }

    // 2) fire decision
    // The legacy path uses a periodic pulse; the profile-driven path fires
    // exactly when its aim policy allows it (fresh line of sight, settled
    // crosshair) and never otherwise.
    BOOL bFire = FALSE;
    if (ctPeriodTicks>0 && ctFireTicks>0) {
      const INDEX iPhase = (bs.bs_iTick + iLP*ctPeriodTicks/4) % ctPeriodTicks;
      bFire = (iPhase < ctFireTicks);
    }
    // Retail deathmatch respawns on the native Fire press/release action.
    // The combat decision never attacks while dead; this pulse is respawn input.
    const BOOL respawnInput=automatic && player!=NULL && player->GetHealth()<=0;
    if (humanMode && automatic) {
      // A press/release cadence, so the native respawn edge really occurs.
      const BOOL respawnPulse=respawnInput && ((bs.bs_iTick&4)==0);
      bFire = (humanFire && testAimReady) || respawnPulse;
    } else {
      bFire = bFire && (testAimReady || respawnInput);
    }

    moveFactor=Clamp(moveFactor,-1.0f,1.0f);
    humanStrafe=(humanMode&&automatic&&bot_fStrafeScale>0.0f)
      ?Clamp(humanStrafe*bot_fStrafeScale,-1.0f,1.0f):0.0f;
    if(bot_bSupplyNavigation&&!BotCecilSettings().bStrafe)humanStrafe=0;

    if(bot_bSupplyNavigation&&automatic&&player){
      const double now=bs.bs_iTick*fTick;CPlayerWeapons* w=player->m_penWeapons?player->GetPlayerWeapons():NULL;
      const bool dead=player->GetHealth()<=0||w==NULL;
      if(dead){bs.bs_lastSeen=-1000;if(bs.bs_deadSince<0)bs.bs_deadSince=now;
        bFire=now-bs.bs_deadSince>=BotCecilSettings().fRespawnDelay&&(bs.bs_iTick&4)==0;
        bs.bs_cecilFire.Reset();
      }else{
        bs.bs_deadSince=-1;
        bFire=bs.bs_cecilFire.Poll(now,w->m_iCurrentWeapon,w->m_iWantedWeapon,combatWeapon,
          humanFire&&testAimReady&&!cecilUseControl,targetVisible,true,humanTargetDistance,BotCecilSettings());
        if(cecilUseControl)bFire=FALSE;
        if(!cecilUseControl&&w->m_iCurrentWeapon==combatWeapon&&w->m_iWantedWeapon==combatWeapon)
          cecilButtons=bs.bs_cecilFire.ScopeButtons(now,w->m_iCurrentWeapon,w->m_bSniping!=FALSE,targetVisible,BotCecilSettings());
        const double finalYaw=BotCecilFinalBodyYaw(player,bs.bs_aHeading-player->m_aLastRotation(1));
        if(!std::isfinite(finalYaw)){
          BotLog("[CecilInvalidAction] local=%d tick=%d rejected=rotation_state\n",iLP,bs.bs_iTick);
          BotCecilNeutralAction(ppls);bActed=TRUE;
          continue;
        }
        const double maxStrafe=BotCecilSettings().bStrafe?Clamp(bot_fStrafeScale,0.0f,1.0f):0;
        cecilFloorStatus=BotCecilSafeMotion(player,BotSupplyState(iLP),now,moveFactor,humanStrafe,cecilUp,finalYaw,maxStrafe,supplyActive!=FALSE);
      }
    }

    // 3) compose the action
    CPlayerAction pa;
    pa.Clear();
    pa.pa_vTranslation(3) = -moveFactor; // normalized forward axis for native composer
    // Lateral component is the same normalized [-1..1] convention as forward:
    // ctl_ComposeActionPacket multiplies it by plr_fSpeedSide. Disabled by
    // default because it is not native-verified yet (see the migration notes).
    if (humanMode && automatic && bot_fStrafeScale>0.0f) {
      pa.pa_vTranslation(1) = humanStrafe;
    }
    if(automatic&&bot_bSupplyNavigation)pa.pa_vTranslation(2)=cecilUp;
    if (!automatic && target!=NULL && botcore::TestJump(bs.bs_iTick)) {
      pa.pa_vTranslation(2) = 1.0f;
    }
    pa.pa_aRotation(1) = bs.bs_aHeading - localInput->m_aLocalRotation(1);
    pa.pa_aRotation(2) = bs.bs_aPitch - localInput->m_aLocalRotation(2);
    pa.pa_aViewRotation(1) = 0.0f;            // no freelook

    ANGLE3D aimInputBefore,aimPacketBefore;
    if(aimTraceCaptured){aimInputBefore=localInput->m_aLocalRotation;aimPacketBefore=pa.pa_aRotation;}

    // Use vanilla speed conversion and local input accumulation. Human buttons
    // must not leak into this synthetic action; preserve the shared control buffer.
    if(!BotCecilActionFinite(pa)){
      BotLog("[CecilInvalidAction] local=%d tick=%d rejected=nonfinite_input\n",iLP,bs.bs_iTick);
      BotCecilNeutralAction(ppls);bActed=TRUE;
      continue;
    }
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
    if (automatic) pa.pa_ulButtons |= combatSelect|cecilButtons;

    // Reject malformed local snapshots before they enter the normal network path.
    if(!BotCecilActionFinite(pa)){
      BotLog("[CecilInvalidAction] local=%d tick=%d rejected=nonfinite\n",iLP,bs.bs_iTick);
      BotCecilNeutralAction(ppls);bActed=TRUE;
      continue;
    }
    // 4) hand it to the network player source (stamps pa_llCreated internally)
    ppls->SetAction(pa);
    if(aimTraceCaptured && player){
      const botcore::AimTrace& a=aimTrace.aim;
      const botcore::TrackState& t=aimTrace.track;
      BotLog("[BotAimTrace] local=%d tick=%d entity=%lu generation=%lu valid=%d target=%d target_entity=%lu target_generation=%lu visible=%d changed=%d dt=%.9f eye=(%.9g,%.9g,%.9g) pose=(%.9g,%.9g) frame=(%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g) track=(%.9g,%.9g,%.9g) velocity=(%.9g,%.9g,%.9g) seen=(%d,%d) point=(%.9g,%.9g,%.9g) desired=(%.9g,%.9g) bias=(%.9g,%.9g) offset=(%.9g,%.9g) error=(%.9g,%.9g) rate_before=(%.9g,%.9g) rate_command=(%.9g,%.9g) rate_after=(%.9g,%.9g) intent=(%.9g,%.9g) residual=(%.9g,%.9g) aligned=%d settled=(%.9f,%.9f) human_fire=%d weapon=%d\n",
        iLP,bs.bs_iTick,(unsigned long)entityId,(unsigned long)BotSupplyState(iLP).generation,
        a.valid,aimTraceCommand.target,(unsigned long)t.entity_id,(unsigned long)t.generation,
        aimTraceCommand.target_visible,a.target_changed,a.dt,a.pose.x,a.pose.y,a.pose.z,a.pose.yaw_deg,a.pose.pitch_deg,
        a.pose.frame.right[0],a.pose.frame.right[1],a.pose.frame.right[2],a.pose.frame.up[0],a.pose.frame.up[1],a.pose.frame.up[2],a.pose.frame.back[0],a.pose.frame.back[1],a.pose.frame.back[2],
        t.x,t.y,t.z,t.vx,t.vy,t.vz,t.first_seen_tick,t.last_seen_tick,a.point.x,a.point.y,a.point.z,
        a.desired[0],a.desired[1],a.bias[0],a.bias[1],a.offset[0],a.offset[1],a.error[0],a.error[1],
        a.rate_before[0],a.rate_before[1],a.command_rate[0],a.command_rate[1],a.rate_after[0],a.rate_after[1],
        aimTraceCommand.yaw_delta_deg,aimTraceCommand.pitch_delta_deg,a.residual[0],a.residual[1],
        aimTrace.arena_aligned,aimTrace.settled_before,aimTrace.settled_after,aimTraceCommand.fire,aimTraceCommand.weapon);
      BotLog("[BotAimTransport] local=%d tick=%d entity=%lu input_entity=%lu same_entity=%d body=(%.9g,%.9g,%.9g) view=(%.9g,%.9g) input_body=(%.9g,%.9g,%.9g) input_view=(%.9g,%.9g) last=(%.9g,%.9g) input_last=(%.9g,%.9g) local_before=(%.9g,%.9g) requested=(%.9g,%.9g) precompose=(%.9g,%.9g) local_after=(%.9g,%.9g) composed=(%.9g,%.9g) nav=%d floor=%d human_fire=%d final_fire=%d current=%d wanted=%d\n",
        iLP,bs.bs_iTick,(unsigned long)entityId,(unsigned long)localInput->en_ulID,player==localInput,
        player->en_plPlacement.pl_OrientationAngle(1),player->en_plPlacement.pl_OrientationAngle(2),player->en_plPlacement.pl_OrientationAngle(3),
        player->en_plViewpoint.pl_OrientationAngle(1),player->en_plViewpoint.pl_OrientationAngle(2),
        localInput->en_plPlacement.pl_OrientationAngle(1),localInput->en_plPlacement.pl_OrientationAngle(2),localInput->en_plPlacement.pl_OrientationAngle(3),
        localInput->en_plViewpoint.pl_OrientationAngle(1),localInput->en_plViewpoint.pl_OrientationAngle(2),
        player->m_aLastRotation(1),player->m_aLastRotation(2),localInput->m_aLastRotation(1),localInput->m_aLastRotation(2),
        aimInputBefore(1),aimInputBefore(2),bs.bs_aHeading,bs.bs_aPitch,aimPacketBefore(1),aimPacketBefore(2),
        localInput->m_aLocalRotation(1),localInput->m_aLocalRotation(2),pa.pa_aRotation(1),pa.pa_aRotation(2),
        supplyActive,cecilFloorStatus,aimTraceCommand.fire,(pa.pa_ulButtons&BOT_PLACT_FIRE)!=0,aimCurrent,aimWanted);
    }
    if(bot_bDiagnostics&&bot_bSupplyNavigation&&player)
      BotCecilApproachFinal(player,BotSupplyState(iLP),iLP,bs.bs_iTick,bs.bs_iTick*fTick,
        supplyActive!=FALSE,cecilFloorStatus,targetVisible!=FALSE,pa.pa_vTranslation,pa.pa_aRotation,pa.pa_ulButtons);
    BotWeaponObserverAfterAction(player,ppls,iLP,bs.bs_iTick,BotSupplyState(iLP).generation,
      combatWeapon,pa.pa_ulButtons,combatSelect,automatic&&bot_bSupplyNavigation,BotCecilSettings().fWeaponCD);
    // Count emitted combat fire input independently of sampled status logs.
    if (bFire && automatic && !respawnInput) ++bs.bs_ulCombatFireActions;
    BotTelemetry_Action(iLP);
    BotDriver_NoteConfigOnce();
    bActed = TRUE;

    if(bot_bSupplyNavigation&&player){
      bool changed=!bs.bs_gravityKnown;
      for(int axis=0;axis<3;++axis)
        changed=changed||fabs(bs.bs_gravity[axis]-player->en_vGravityDir(axis+1))>.0001;
      if(changed){
        const FLOAT3D& p=player->GetPlacement().pl_PositionVector;
        BotLog("[CecilGravity] local=%d tick=%d entity=%lu generation=%lu gravity=(%.4f,%.4f,%.4f) pos=(%.3f,%.3f,%.3f) alive=%d\n",
          iLP,bs.bs_iTick,(unsigned long)entityId,(unsigned long)BotSupplyState(iLP).generation,
          player->en_vGravityDir(1),player->en_vGravityDir(2),player->en_vGravityDir(3),p(1),p(2),p(3),player->GetHealth()>0);
        for(int axis=0;axis<3;++axis)bs.bs_gravity[axis]=player->en_vGravityDir(axis+1);
        bs.bs_gravityKnown=true;
      }
    }

    if(bot_bSupplyNavigation&&player&&bs.bs_iTick%20==0){
      const auto& state=BotSupplyState(iLP);const FLOAT3D& p=player->GetPlacement().pl_PositionVector;
      CPlayerWeapons* w=player->m_penWeapons?player->GetPlayerWeapons():NULL;
      if(cecilFloorStatus==0){
        const auto& probe=state.probe;
        BotLog("[CecilMotionProbe] local=%d tick=%d requested=(%.4f,%.4f,%.4f) yaw=%.4f primary=%d last=%d mask=%u wall_rays=%u floor_rays=%u hit=%lu type=%d support=%.4f normal=(%.4f,%.4f,%.4f) from=(%.4f,%.4f,%.4f) to=(%.4f,%.4f,%.4f)\n",
          iLP,bs.bs_iTick,probe.inputForward,probe.inputStrafe,probe.inputUp,probe.finalYaw,
          (int)probe.primaryReason,(int)probe.lastReason,probe.reasonMask,probe.wallRays,probe.floorRays,
          (unsigned long)probe.hitEntity,probe.renderType,probe.support,probe.normal[0],probe.normal[1],probe.normal[2],
          probe.from[0],probe.from[1],probe.from[2],probe.to[0],probe.to[1],probe.to[2]);
      }
      BotLog("[CecilState] local=%d tick=%d policy=cecil-human-v1 ready=%ld entity=%lu generation=%lu alive=%d pos=(%.3f,%.3f,%.3f) health=%.1f owned=%lu current=%d wanted=%d target=%d vis=%d goal_entity=%lu goal=%d hop=%d nav=%d move=%.2f strafe=%.2f up=%.2f fire=%d shots=%lu pickups=%u deaths=%u respawns=%u rays=%d liquid=%d immersion=%.2f gravity=(%.1f,%.1f,%.1f) floor=%d flags=%lu buttons=%lu body=(%.2f,%.2f,%.2f) anchor=%d reacquire=%d support_ref=%lu level_swim=%d view_pitch=%.7f input_pitch=%.7f composed_pitch=%.7f last_pitch=%.7f important=%d nav_source=%d nav_travel=%d hop_clock=(%d,%d,%d,%.3f,%.3f)\n",
        iLP,bs.bs_iTick,(long)_botSupplyMapReady,(unsigned long)entityId,(unsigned long)state.generation,
        player->GetHealth()>0,p(1),p(2),p(3),player->GetHealth(),w?(unsigned long)w->m_iAvailableWeapons:0,
        w?w->m_iCurrentWeapon:0,w?w->m_iWantedWeapon:0,bs.bs_iCombatTarget,targetVisible,(unsigned long)state.goalEntity,state.goal,state.hop,supplyActive,moveFactor,humanStrafe,cecilUp,bFire,
        (unsigned long)bs.bs_ulCombatFireActions,state.pickups,state.deaths,state.respawns,16-_botRayBudget,(int)player->m_pstState,player->en_fImmersionFactor,
        player->en_vGravityDir(1),player->en_vGravityDir(2),player->en_vGravityDir(3),cecilFloorStatus,(unsigned long)cecilFlags,(unsigned long)pa.pa_ulButtons,
        player->GetPlacement().pl_OrientationAngle(1),player->GetPlacement().pl_OrientationAngle(2),player->GetPlacement().pl_OrientationAngle(3),state.anchor,state.reacquireNode,
        player->en_penReference?(unsigned long)player->en_penReference->en_ulID:0,state.levelSwimView,
        player->en_plViewpoint.pl_OrientationAngle(2),localInput->m_aLocalRotation(2),pa.pa_aRotation(2),player->m_aLastRotation(2),
        state.importantGoal,state.navigator.SourceSlot(state.goal),state.currentNavTravel,
        state.hopCheckpointGoal,state.hopCheckpointSource,state.hopCheckpointHop,state.hopCheckpointLast,state.hopCheckpointSince);
      BotPlayerObserverTelemetry(player,iLP,bs.bs_iTick,state.generation,pa);
    }

    // 5) periodic status log (position read from our own player entity)
    if (bot_iLogEvery>0 && (bs.bs_iTick%bot_iLogEvery)==0) {
      if (bot_bDiagnostics) BotLog("[BotInput] tick=%d forward=%.2f up=%.2f\n",
        bs.bs_iTick, pa.pa_vTranslation(3), pa.pa_vTranslation(2));
      CEntity *pen = _pNetwork->GetLocalPlayerEntity(ppls);
      if (pen!=NULL) {
        const FLOAT3D &vPos = pen->en_plPlacement.pl_PositionVector;
        BotLog("[BotDriver] bot%d tick=%d pos=(%.1f,%.1f,%.1f) heading=%.1f fire=%d combat_fire_actions=%lu\n",
          iLP, bs.bs_iTick, vPos(1), vPos(2), vPos(3), bs.bs_aHeading, bFire,
          (unsigned long)bs.bs_ulCombatFireActions);
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

  if (bActed) {
    BotDriver_ReportState(BOT_TM_REASON_ACTIVE, 1, 1, ctLocalPlayers);
  } else if (ctLocalPlayers > 0) {
    BotDriver_ReportState(BOT_TM_REASON_NOENTITY, 1, 1, ctLocalPlayers);
  }

  // the bot driver owns action generation now - skip vanilla input handling
  return TRUE;
}
