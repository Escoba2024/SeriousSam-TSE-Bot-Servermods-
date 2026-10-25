# ssam.ai Red Station player-facing server settings — 25 October 2026

## Prepared change (isolated branch, not yet a qualified live runtime)

- Dedicated session: `ssam.ai | Red Station | Human Bots`, original map `RedStation.wld`.
- Join message via retail `ser_strMOTD`: `Welcome to ssam.ai | TSE Classic 1.07 | RED STATION | #SamIsBack | Play fair and have fun!`.
- Five-minute chat via retail `cmd_cmdOnTick` and `Say()`: `[ssam.ai] RED STATION - classic 1.07 deathmatch. Respect other players. #SamIsBack`.
- Message scheduling uses a dedicated server-only guard using built-in `tmp_ai[9]` scratch integer, 300-second buckets, reset near tick zero; protects from repeated broadcasts on adjacent 100-FPS simulation ticks. Initial native retail private smoke detected `Only external declarations are supported` on an attempted custom `user INDEX` guard; it was replaced by the original engine-provided scratch integer `tmp_ai[9]`, which is unused by other current server scripts. The corrected generated shell line MUST be proven by a native private 1.07 run, not by Python syntax tests alone. The initial private run with the original declaration failed to reach population readiness (120-second join timeout); its server log confirmed the incorrect declaration. The runtime has been cleaned up by the runner. Do not treat this as validation of the corrected timer.
- Inherited Red Station properties unchanged: hard, unlimited ammo, flower blood, no gibs, 16 slots.
- No edits to runtime process, vanilla world `.wld`, .gro archives, retail binaries, qualified candidate DLLs or active agent worktrees. Changes are only injected into fresh server overlay files by `redstation_preset.configure_overlay`.

## Power-up exclusion/invisibility investigation

Original `SE1_00_Levels.gro` contains `Levels/LevelsMP/Deathmatch/RedStation.wld` (901,715 bytes), with multiple power-up item references including Invisibility. Vanilla `EntitiesMP/PowerUpItem.es` declares `PUIT_INVISIB`, `PUIT_INVULNER`, `PUIT_DAMAGE`, `PUIT_SPEED`, `PUIT_BOMB`; the original Retail-1.07 dedicated server binary + default persistent symbol list yielded **no verified global disable-power-ups/invisibility switch**.

Changing `RedStation.wld` or `EntitiesMP.dll` unilaterally would be a separately testable map/Entity modification and could break joins by untouched Retail-1.07 clients (world/class CRC). No undocumented cvar or simple text edit is sufficient evidence that pickups disappear. **Power-ups and invisibility remain active unless an independently verified compatible removal path is implemented.**

The correct follow-up is an isolated player-join test using original 1.07 client after a targeted server-side entity filter or map modification, with checks that: (a) invisible/power-up items cannot be picked; (b) game map matches client expectations; (c) GameSpy 1.07 no active mod; (d) no SYNCBAD; and (e) original hashes are preserved and rollback exists. Do not activate a guessed map edit in public.

## Verification and release boundary

- Existing Red Station preset `unittest` suite: 9/9 before change, 12/12 after new tests.
- No current live game processes/listening port `25600/25601` at inspection.
- `ser_strMOTD`, `cmd_cmdOnTick`, `cmd_tmTick` found in original Retail engine symbols; `Say(CTString)` found in game SDK. However `user INDEX` declaration and chat rendering/timing are **not yet verified in an actual 1.07 game process**.
- Existing public 8-bot attempt on 25 October returned `RuntimeError: server runtime failure SYNCBAD` in its launcher log; its report is not a green public-acceptance certificate. Do not start an eight-bot public fleet without a safe acceptance gate.

### Second native parser finding

The corrected existing-variable guard launched a private retail server and GameSpy session under `ssam.ai | Red Station | Human Bots`, but its OnTick parser printed `<command>(1): Type mismatch` on every game tick. The test was interrupted and cleaned up; no public update occurred. Third candidate uses explicit `(FLOAT)` / `(INDEX)` casts for strict Retail-1.07 shell typechecking. Native retest remains required.

### Third native 1.07 startup parser check — partial pass

A third private overlay on 27054/27055 loaded the corrected type casts. The original unmodified DedicatedServer.exe reported `Starting session: 'ssam.ai | Red Station | Human Bots'` and loaded original RedStation.wld. Its `Dedicated_BotTest.log` had **no** `Type mismatch`, `<command>(1)` parser failure or `Only external declarations` during observed startup. After sampling the console the private run was intentionally SIGINT-interrupted; the runner's cleanup returned and no TSE test processes / ports 27054–27055 persisted. **Not equivalent to proving a successful 300-second announcement**: the native test was short and did not complete its observer population gate, and MOTD visibility in an actual player HUD was not captured. The launch contains pre-existing unrelated errors for `sam_strTechTestLevel` and `net_strMasterServerOverride`; these also occur in the prior unmodified configuration.
