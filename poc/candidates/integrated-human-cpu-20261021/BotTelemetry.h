/* SeriousSam TSE Bot Project: GameMP-only bot-client integration.
 * P0 evidence instrumentation (candidate, NOT qualified). GPL-2.0-only.
 *
 * Why this exists
 * ---------------
 * The 2026-10-21 Hetzner A/B reported four joined players but no BotDriver
 * tick evidence. Reading the release source shows why that observation cannot
 * be interpreted: when `bot_bEnabled`/`gm_bGameOn` is false the timer handler
 * returns before any log line, and the per-tick log is gated by
 * `bot_iLogEvery`. Silence therefore means "no log line", not "no problem".
 *
 * This module writes an independent CSV from a watchdog thread: one data row
 * per second plus `#` manifest/state lines. The thread never calls engine code,
 * never waits for an engine lock and never decides bot behaviour. If the game
 * timer blocks, the file keeps growing while `ticks` stays at zero - which
 * separates a deadlock from a disabled driver for the first time.
 *
 * All entry points are cheap, lock-free counters plus at most one line per
 * second. Set `bot_iTelemetry = 0` to keep the build quiet.
 *
 * CSV layout (fixed; tools/bot_telemetry.py rejects anything else):
 *   #bot-telemetry,rev=1
 *   #build,tag=...,built=...
 *   #exe,...
 *   #columns,t_ms,ticks,actions,frames,renderskip,renderdraw,lp,gameon,
 *            enabled,disabled,gameoff,nolocal,noentity,lock_ms_max,
 *            lock_ms_last,tick_ms_max,tick_ms_avg,cpu_user_ms,
 *            cpu_kernel_ms,stall_s,reason
 *   <data rows>
 *
 * `ticks` counts every timer invocation (active and inactive). `actions`
 * counts CPlayerSource::SetAction() calls. `stall_s` grows while the driver is
 * enabled and in game but no timer invocation arrives.
 */

#ifndef SE_INCL_BOTTELEMETRY_H
#define SE_INCL_BOTTELEMETRY_H

#ifdef PRAGMA_ONCE
  #pragma once
#endif

/* Reason of the last timer invocation. Mirrored in the CSV `reason` column. */
#define BOT_TM_REASON_ACTIVE   0   /* driver enabled, game on                 */
#define BOT_TM_REASON_DISABLED 1   /* bot_bEnabled == 0                       */
#define BOT_TM_REASON_GAMEOFF  2   /* gm_bGameOn == 0 (menu/loading/ended)    */
#define BOT_TM_REASON_NOLOCAL  3   /* no local player source                  */
#define BOT_TM_REASON_NOENTITY 4   /* player source present, entity missing   */

/* Opens BotTelemetry.csv (next to the executable, or $TSE_BOT_TELEMETRY),
 * writes the manifest and starts the watchdog thread. Idempotent. Called from
 * BotDriver_Init(). */
void BotTelemetry_Start(void);

/* Records the switches that the startup script actually produced. Called by
 * CGame::InitInternal after the script has run, so a forgotten switch is
 * visible instead of being inferred from silence. */
void BotTelemetry_Config(int iNullRender, int iNullRenderFps, int iDedicatedServer);

/* Free-form `#note` line (thread safe). */
void BotTelemetry_Note(const char *strText);
void BotTelemetry_NoteF(const char *strFormat, ...);

/* One timer invocation. Called exactly once per CGame::GameHandleTimer(),
 * before any early-out; increments `ticks` and the tick-interval statistics. */
void BotTelemetry_Tick(int iEnabled, int iGameOn, int iLocalPlayers);

/* Publishes the verdict for this invocation: 0 when at least one SetAction()
 * happened, otherwise DISABLED/GAMEOFF/NOLOCAL/NOENTITY. Increments the
 * matching skip counter and logs a #state line when the reason changes. */
void BotTelemetry_Reason(int iReason, int iEnabled, int iGameOn, int iLocalPlayers);

/* One CPlayerSource::SetAction() call for local slot 0..3. */
void BotTelemetry_Action(int iSlot);

/* A local player source exists but has no entity yet (join/loading window). */
void BotTelemetry_NoEntity(void);

/* Blocking time on ga_csNetwork; Begin/End wrap the CTSingleLock. */
void BotTelemetry_LockWaitBegin(void);
void BotTelemetry_LockWaitEnd(void);

/* One CGame::GameMainLoop() iteration. */
void BotTelemetry_Frame(void);

/* One CGame::GameRedrawView() call: iSkipped != 0 means the null-render
 * early-out was taken. */
void BotTelemetry_Render(int iSkipped);

/* Opt-in frame pacing for the null-render path. iFps <= 0 disables it.
 * Sleeps only on the render/timer thread and never holds an engine lock. */
void BotTelemetry_PaceFrame(int iFps);

#endif  /* SE_INCL_BOTTELEMETRY_H */
