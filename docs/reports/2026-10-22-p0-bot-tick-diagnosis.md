# P0: why four joined Hetzner bots produced no BotDriver evidence

**Date:** 2026-10-22 · **Status:** code-level diagnosis + instrumented candidate.
**Runtime:** **NOT RUN**. This report contains no measurement and no acceptance
result. The environment that produced it had no Wine, no MSVC and no route to
the Hetzner host.

> **Kurzfassung.** Der bisherige Test konnte „Bots laufen nicht" nicht von
> „Bots laufen, aber die Beweisquelle fehlt" unterscheiden. Im ausgelieferten
> Quellstand ist der Bot-Treiber im inaktiven Zustand **vollständig stumm**,
> und die einzige unkonditionale Logzeile erscheint erst, wenn ein lokaler
> Spieler eine Entity besitzt. Zusätzlich setzt das PR-#40-Profil
> `bot_bNullRender`, aber **nicht** `bot_bEnabled`; wird es als Startskript
> verwendet, entstehen vier Joins ohne einen einzigen Bot-Tick. Der neue
> Kandidat schreibt jede Sekunde einen timerunabhängigen Datensatz und nennt
> den Grund, wenn er nicht arbeitet.

## 0. Scope and limits

The working checkout is a Linux sandbox with `gcc` but without Wine, without
the MSVC/v143 toolset, without the 1.07 SDK and without network access to
`91.99.75.33` (a TCP test to a TEST-NET address also "succeeds", so a
successful `connect()` here proves nothing). Therefore:

- **not done:** native build of the candidate, any Wine run, any Hetzner
  measurement, any vanilla join.
- **done:** source-level root-cause analysis, an instrumented candidate whose
  source overlay is hash-pinned to the qualified release tree, three analysers
  with 60+ unit tests, and a measurement harness that *refuses* to qualify a
  throttled or bot-less window.

Everything marked "hypothesis" stays a hypothesis until the corresponding
evidence exists on Hetzner.

## 1. Verified facts from the current source

| # | Fact | Evidence |
| --- | --- | --- |
| F1 | The 20 Hz game timer calls `BotDriver_HandleTimer()` first; if it returns TRUE the vanilla input path is skipped. | `Game.cpp:745-755`; `BotDriver.cpp:259` |
| F2 | The inactive path is **silent**: `if (!bot_bEnabled \|\| pgame==NULL \|\| !pgame->gm_bGameOn) { BotResetNavigation(); return FALSE; }` logs nothing and counts nothing. | `BotDriver.cpp:262-266` |
| F3 | The only unconditional BotDriver line appears when a local player source gets its *first* action; it requires a valid local player entity and appears even with `bot_iLogEvery=0`. | `BotDriver.cpp:309-310` |
| F4 | Periodic evidence (`[BotDriver] botN tick=...`) is gated by `bot_iLogEvery>0` inside the per-player action path. | `BotDriver.cpp:481` |
| F5 | `BotLog()` formats locally and calls `CPutString()`, i.e. it writes to the console/standard output. Whether a harness captured that stream is a property of the harness, not of the driver. | `BotDriver.cpp:44-51` |
| F6 | The number of local players is stored by the launcher in `Data\SeriousSam.gms` (`localPlayers-1` at offset +24) and the names/GUIDs in `Players\PlayerN.plr`; the bot driver does not create players. Four players therefore join even when `bot_bEnabled=0`. | `LocalBotReleaseCore.ps1:23,36-46` |
| F7 | Clients are started as `+connect <server> +quickjoin +script <startupScript>`; the named file **is** the startup script executed by `CGame::InitInternal`, not an include chain. | `PopulationCore.ps1:153`; `Game.cpp:1022` |
| F8 | The PR #40 profile `poc/profiles/HetznerNullRender.ini` contains only `bot_bNullRender` and FPS keys; its comment says it must be *included at the end of the fleet script*. Passed directly to `+script`, `bot_bEnabled` is never set. | PR #40, `poc/profiles/HetznerNullRender.ini` |
| F9 | The timer handler is registered in `CGame::InitInternal` (line 908), `BotDriver_Init()` declares the symbols at 1015, and the startup script runs at 1022. | `Game.cpp:908,1015,1022` |
| F10 | The renderer bypass of PR #40 returns before `CTSingleLock slBotRender(&_pTimer->tm_csHooks, TRUE)`, so it cannot be the reason for a *timer* stall. | `Game.cpp:2091-2111` (PR #40) |
| F11 | `sam_iMaxFPSActive` is **not** declared anywhere in GameMP; the FPS limiter lives in the (not published) EXE. Its behaviour under a skipping render callback is therefore unknown, not merely unverified. | `grep` over `poc/release/gamemp/Game.cpp` |

## 2. Ranked hypotheses and the evidence that decides them

The observation: four named players joined, CRC passed, and an 18 s sample
contained **no** BotDriver line in either variant. From F2/F3/F5/F6/F7/F8 only
five mechanisms can produce that:

| # | Hypothesis | What it would mean | Decisive evidence |
| --- | --- | --- | --- |
| H1 | The isolated client ran with `bot_bEnabled=0` (profile used as startup script, include missing, or script error before that line). | The players were vanilla split-screen clients with empty actions: joined, idle, no BotDriver output. CPU compared "idle client rendering" with "idle client not rendering". | `#config,bot_enabled=0` and `reason=1` in `BotTelemetry.csv`; the startup script itself |
| H2 | Driver active, but output not captured (stdout/console not redirected, `bot_iLogEvery=0`, capture started after the attach lines). | Bots may have acted; the CPU number still came from a saturated cgroup. | CSV shows ticks/actions > 0 while the console log has no `[BotDriver]` lines; `#build` tag present |
| H3 | The timer stopped or blocked (`ga_csNetwork`, Wine scheduling, `tm_csHooks` order). | The client appeared connected but stopped simulating/acking. | Watchdog rows continue while `ticks=0` and `stall_s` grows; `lock_ms_max` rises |
| H4 | `gm_bGameOn` stayed false during the sample (menu/loading/waiting). | No actions by design; an 18 s window after join on llvmpipe is short. | `reason=2` and `gameoff` counter dominate the CSV |
| H5 | A different `GameMP.dll` was in the prefix (copy step failed). | The null-render flag could not have any effect; the A/B compared identical binaries. | Missing/old `#build` tag, no CSV at all, DLL hash mismatch |

H1 is the most plausible because of F7+F8, but it is **not proven**: the raw
logs of that run are private to the Hetzner staging directory. Likewise, the
A/B report itself notes that the FPS flags were "not independently verified at
runtime". The instrumentation now makes H1–H5 distinguishable in a single
60 s run.

## 3. Why the 2026-10-21 A/B could not measure a saving

This is arithmetic, not opinion. Test cgroup `45000/100000 µs`, i.e. **45 % of
one core shared by the dedicated server and the client**, with
`nr_throttled=2528` of `nr_periods=3146` (80.3 %).

- The dedicated server alone needs ~8–10 % of a core (baseline report), leaving
  ~35–37 % for the client.
- Measured: 35.56 % in **both** variants. That is the cap being handed out,
  not the renderer's cost.
- With 80 % of periods throttled the process is frozen for most of the wall
  time; timer lateness and action rate are meaningless in that window.

`tools/benchmarks/tse_cpu_profile.py` now rejects exactly this: a throttled
period ratio > 1 % or a throttled-time ratio > 2 % marks the repetition
`INVALID` with the measured numbers (a unit test reproduces 2528/3146).

## 4. What the candidate records

`poc/candidates/p0-nullrender-20261022/` (source overlay + `apply.sh` +
profiles). One CSV row per second from a watchdog thread that never calls
engine code and never takes an engine lock:

| Column group | Meaning |
| --- | --- |
| `ticks` | `CGame::GameHandleTimer()` invocations in the last second, active and inactive |
| `actions` | `CPlayerSource::SetAction()` calls in the last second |
| `disabled`, `gameoff`, `nolocal` | why an invocation did not act |
| `noentity` | local player source exists but has no player entity yet |
| `frames` | `CGame::GameMainLoop()` iterations |
| `renderskip`, `renderdraw` | proof that the null-render switch is live |
| `lp`, `gameon`, `enabled` | state as seen by the last invocation |
| `lock_ms_max`, `lock_ms_last` | blocking time for `ga_csNetwork` |
| `tick_ms_max`, `tick_ms_avg` | interval between timer invocations (quantum 50 ms) |
| `cpu_user_ms`, `cpu_kernel_ms` | whole-process CPU from `GetProcessTimes` |
| `stall_s` | consecutive seconds with enabled+in-game but zero invocations |
| `reason` | 0 active, 1 disabled, 2 game off, 3 no local players |

Manifest lines (`#build` with a compile-time tag, `#exe`, `#config`) prove
*which* binary and which effective switches produced the data. The config line
is written **after** the startup script, so a forgotten `bot_bEnabled=1` is
visible instead of being inferred from silence.

Mapping to the P0 questions:

| Question | Answered by |
| --- | --- |
| 1. `bot_bEnabled` really set? | `#config,bot_enabled` + `disabled` counter |
| 2. start script fully executed? | `#config` line exists (written after `_pShell->Execute(startup)`) |
| 3. is the new DLL loaded? | `#build` tag + the file appearing at all |
| 4. `BotDriver_HandleTimer` calls? | `ticks` |
| 5. actions for all four bots? | `actions`, `actions/ticks/lp`, existing per-bot console log |
| 6. actions reach the server? | server-side population/score polling in the same window (`gamespy_query.py`) |
| 7. movement/aim/fire/obstacle avoidance? | existing `[BotDriver] pos=`, `[BotCombat]`, `[BotNavigation]` lines + server-side score progression |
| 8. deadlock/timer blockade? | rows continue, `ticks=0`, `stall_s` grows, `lock_ms_max` rises |
| 9. render locking blocks 20 Hz? | `lock_ms_max` distribution; `renderskip/renderdraw` |
| 10. throttling delays ticks? | `tick_ms_max` vs 50 ms, plus the external cgroup sampler |
| 11. reconnect works? | existing `[BotReconnect]` lines + `reason` transitions |
| 12. CRC/sync still correct? | unchanged server gates; `tools/analyze_sync_log.py` |

## 5. Decision tree for the next Hetzner run

Run `profiles/p0-diagnostic.ini` (rendering untouched, console summary on) on
one isolated client with four bots, 60 s after the join:

1. **No `BotTelemetry.csv` at all** → the candidate DLL is not loaded (H5).
   Check the prefix copy and the DLL hash; nothing else can be concluded.
2. **File exists, `bot_enabled=0`** → H1. Fix the startup script. The script is
   the only file passed via `+script`.
3. **`bot_enabled=1`, `lp=0`, `nolocal` grows** → the client joined but has no
   local player sources: check `.gms` `localPlayers=4` and the `.plr` profiles.
4. **`reason=1` despite `bot_bEnabled=1` in the script** → the script ran
   before the symbol existed or was overwritten later; check `BotDriver_Init`
   order and `PersistentSymbols.ini`.
5. **`ticks` ≈ 0 and `reason=2`** → the game was not on (menu/loading). Extend
   the warmup until `gameon=1` before judging (H4).
6. **`ticks` ≈ 20 but `actions` = 0, `noentity` grows** → the player source
   exists but the entity is not replicated yet; check the join/CRC state.
7. **`ticks` = 0 while rows continue, `stall_s` rises** → H3. Inspect
   `lock_ms_max`; if it rises too, take a Wine thread backtrace
   (`winedbg --auto`, `gdb`) before changing any lock.
8. **`ticks` ≈ 20 and `actions` ≈ 4×20, `renderskip=0` in the null variant** →
   the switch did not take effect (profile not applied, or `_fnmThumb` set).
9. **`ticks` ≈ 20, `actions` ≈ 80, `renderskip≈frames` in the null variant** →
   only now may CPU be measured.

## 6. Exact next procedure on Hetzner (not executed here)

```bash
# 1. build (new hash; never overwrite 61DC...)
poc/candidates/p0-nullrender-20261022/apply.sh /srv/tse-cpu-opt-candidates-20261022/gamemp-p0
msbuild /srv/tse-cpu-opt-candidates-20261022/gamemp-p0/Game.vcxproj \
    /p:Configuration=Release_TSE107 /p:Platform=Win32
sha256sum .../Bin/GameMP.dll

# 2. read-only preflight, then P0 diagnostic run (render native, telemetry on)
tools/benchmarks/hetzner_preflight.sh --runtime <isolated-client> --dll <...>/GameMP.dll \
    --port 26860 --server <isolated-server>:26860
tools/benchmarks/measure_window.sh --label p0-diag --out /srv/.../evidence/p0-diag \
    --pid <client>:client --pid <server>:server --duration 120 --warmup 30 \
    --telemetry <client>/Bin/BotTelemetry.csv --expect-bots 4 \
    --require-cwd /srv/tse-cpu-opt-candidates-20261022
```

Only a `QUALIFIED_WINDOW` with `verdict: ACTIVE_OK` allows the A/B
(`docs/reports/2026-10-22-cpu-measurement-protocol.md`).

## 7. Acceptance status

| Item | Status |
| --- | --- |
| Root cause proven | **NO** – five hypotheses, one leading (H1), instrumentation ready |
| Candidate built natively | **NO** |
| Bot activity proven on Hetzner | **NO** |
| CPU saving measured without throttling | **NO** |
| Vanilla join / CRC / 60 min / reconnect | **NOT TESTED for this candidate** |
| Production change | **NONE** (`poc/release/gamemp/` and `61DC...` untouched) |

## 8. Handoff

- Branch: `arena/89ecfb03-serioussam-tse-bot-servermods`.
- Candidate: `poc/candidates/p0-nullrender-20261022/` (overlay, profiles,
  `apply.sh`, README).
- Tooling: `tools/bot_telemetry.py`, `tools/benchmarks/tse_cpu_profile.py`,
  `tools/gamespy_query.py`, `tools/benchmarks/hetzner_preflight.sh`,
  `tools/benchmarks/measure_window.sh` (+ unit tests).
- Blocking external requirement: access to the Hetzner host and an MSVC/v143
  x86 build environment. No further conclusion is possible without them.
- Do not merge or deploy; PR #40 stays a draft and the production fleet stays
  on `61DC...`.
