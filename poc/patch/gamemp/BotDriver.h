/* A "Pfad D" proof-of-concept bot driver for Serious Sam: TSE.
 * (sample code for the vanilla-compatible bot client; see VERIFIKATION.md)
 *
 * This is NOT a Croteam file. It is a new, self-contained GameMP module that
 * generates synthetic CPlayerActions for all local players, bypassing the
 * normal controls/input path.
 */

#ifndef SE_INCL_BOTDRIVER_H
#define SE_INCL_BOTDRIVER_H

#ifdef PRAGMA_ONCE
  #pragma once
#endif

/*
 * Button flags for CPlayerAction::pa_ulButtons.
 * These MUST match the PLACT_* defines in Sources/EntitiesMP/Player.es!
 * (kept in sync manually - do not change one without the other)
 */
#define BOT_PLACT_FIRE (1L<<0)

/* Declare bot console symbols. Call once from CGame::InitInternal(),
 * BEFORE persistent symbols and Scripts/Game_startup.ini are executed,
 * so those scripts can set the bot variables.
 */
void BotDriver_Init(void);

/* Phase 2: called at the head of CGame::JoinGame(). When the bot driver is
 * enabled and bot_ctLocalPlayers >= 2, this overrides the split-screen join
 * configuration (gm_StartSplitScreenCfg, gm_aiStartLocalPlayers) so one bot
 * client process joins with 2..4 local players - through the exact same
 * native join path the split-screen menu uses. Distinct player profiles
 * (bot_iProfileBase..+n-1) must exist in the bot client beforehand; their
 * per-character GUIDs provide the required uniqueness.
 * Does nothing when disabled, so the vanilla observer path stays untouched.
 */
void BotDriver_ConfigureJoin(class CGame *pgame);

/* Called at the start of CGame::GameHandleTimer() (every timer tick, 20 Hz).
 * If the bot driver is enabled, it generates one synthetic CPlayerAction per
 * active local player and hands it to CPlayerSource::SetAction() - exactly
 * like the vanilla input path does - and returns TRUE so that the caller
 * skips normal input handling.
 */
BOOL BotDriver_HandleTimer(class CGame *pgame);

#endif  /* SE_INCL_BOTDRIVER_H */
