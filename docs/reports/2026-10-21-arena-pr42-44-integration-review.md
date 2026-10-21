# Integration review: Arena PRs 42, 43 and 44 — 21.10.2026

## Verified upstream identity

GitHub connector metadata and fresh Hetzner fetch agree on these heads. Separate detached review worktrees were used; no upstream branch was edited and nothing was merged.

| PR | Head | State | Scope | Rechecked portable evidence |
|---|---|---|---|---|
| 42 | f3c938425515f021c6f6330fb62981ec09b3d7e4 | open, non-draft | independent CPU review, diagnostic patch 0008, optional scan/ray throttle patch 0009 | 9 static tests pass |
| 43 | b85df58d3854c51fa294a34d67d9bce928ff407b | open, draft | 23 files: diagnostic/null-render overlay, CSV telemetry, CPU sampler, UDP query, workflow | 26 tools + 39 benchmark tests pass, total 65 |
| 44 | 7d9e695eeaab133d7dc312d4af3b72e41fc5d311 | open, non-draft | 18 files: profile/perception/aim/loadout/human policy, integration patch/review copy | 7 C++ suites pass, including 555 human-AI checks; integration block PASS; patch verification PASS; 13-file provenance PASS |

PR44 integration smoke emits one unused-function warning for the stub Clamp helper. It does not fail the smoke, but the fresh Hetzner run is not warning-free. Offline performance figures in PR44 exclude engine raycasts, entity queries, simulation and Wine; they are not whole-client CPU results.

## Updated knowledge and decisions

1. **P0 cause is already resolved on Hetzner.** Original private A/B INI was root:root 0600, unreadable by the nobody runtime. That explains inactive bots and ineffective null-render settings. The old reports' timer/symbol hypotheses are historical, not the current blocker.
2. **Current native evidence predates all three new candidates.** Corrected 4F74146E smoke has four active slots, about 20Hz, motion/fire/kill markers, CRC OK and no observed short-run sync errors. The new Arena instrumentation and human-AI code have not been built or activated by this review.
3. **PR42 is a review source, not an execution authority.** Its Windows GitHub runner recommendation conflicts with the user's explicit Hetzner-only requirement. Continue on Hetzner. Minimized-window behavior, GAT_NONE and Dedicated-as-client remain hypotheses until Retail runtime proof; do not promote its CPU/capacity estimates to measured facts.
4. **PR43 has a confirmed CSV formatter defect before adoption.** In candidate BotDriver.cpp, BotTelemetry_Watchdog passes 21 values for 21 declared columns, but the format string contains 22 conversions. Conversion 14 is %ld although argument 14 is the double lock_ms_max value. Subsequent conversions are shifted; x86 variadic decoding is undefined and the strict parser cannot be trusted with emitted rows. The 65 tests do not exercise this real native formatter contract. Fix in an isolated integration candidate with a regression test before any telemetry-based acceptance.
5. **PR43 startup configuration evidence also needs review.** BotTelemetry_Config runs within CGame::InitInternal after Game_startup.ini, while command-line +script is applied by the EXE later. The parser treats #config bot_enabled=0 as inactive and checks nullrender against that snapshot. If the profile is supplied by +script, the snapshot can be stale even when later per-second rows show active bots. The separate #note CONFIG line is not parsed as #config. Validate this specific startup order in Retail or publish an effective runtime snapshot after profile application. The watchdog also has no explicit stop/join path; DLL unload/clean shutdown remains an acceptance gate.
6. **PR44 supplies a usable policy layer, not complete CecilBotMod.** Five skill levels and six independent personalities, reaction/aim error, target memory, weapon dwell and a mixed eight-bot roster are implemented offline. No Cecil source is copied; selected algorithms inspired the new policy. Server entity/network patches from Cecil are deliberately excluded. bot_bHumanAI defaults to 0; strafe scale defaults to 0. Navigation/pathfinding, MSVC target build, real hit/movement quality, vanilla observation and 60-minute sync still require proof.
7. **PR42 and PR44 cannot be stacked blindly.** Real git apply --check experiments on disposable copies: diagnostics then human fails at BotDriver.cpp:66; human then diagnostics also fails; diagnostics plus throttle applies, but adding human then fails. Preserve each original and integrate selected changes manually in an isolated build tree. PR43's full Game.cpp/BotDriver.cpp overlays also cannot simply overwrite the human-AI integration.

## First corrected long measurement on Hetzner

One render-on sample completed before installation: 180s post-readiness warmup, 600.0009s measurement, four slots each at 20Hz, each moved, CRC OK, zero observed sync error markers, zero new throttled periods, 65.855% whole-host busy and 0% steal. Client mean 115.79% of one core, median 116.951%, p95 122.954%; dedicated 9.517% of one core; whole test cgroup 129.678%.

This is one baseline repetition, not a before/after saving or capacity qualification. Remaining repetitions run in the isolated namespace; public fleet stays stopped. Installation was performed only after that completed window, with benchmark control paused between samples, then resumed.

## Toolchain authorization and verified state

User explicitly approved Microsoft license acceptance. Minimal x64-host/x86-target Visual Studio 2022 tools and Windows SDK 10.0.19041.0 are installed privately under /srv/tse-msvc-20261021. Upstream installer selected MSVC 14.44.35207. A generated PE32 x86 test program built and linked successfully, then executed under Wine with MSVC_X86_OK and exit 0. Proof SHA256: 7e3af3c0e9da45a648326ccf25fb52a757abac53c2b2c2e072dbbf4da2cd40e5.

The SDK remains pinned to aa7869c2c2c4db0562281814d0ac3784e6b9d6f0 and Includes 94ff8cd0e63941f8601294350b616472f772ed51. Shadow was not accessed.

First GameMP compile attempt reached Camera.cpp, then CompMessage.cpp failed C1083 on Game/SessionProperties.h despite the file being present: a build include-path problem, not a missing SDK. Retrying the same translation unit using relative -I. and -I.. succeeded. A complete GameMP link and runtime acceptance have not yet been claimed.

The unpack dependency installation stalled on a needrestart kernel notification. That notification was dismissed; no reboot or service restart was requested. Installed msitools and cabextract were verified.

## Next execution order

1. Keep the already running same-binary null-render comparison intact; no candidate replacement during it.
2. Complete and record a reproducible Hetzner GameMP build using the proven relative include paths; output is a new unqualified candidate.
3. Integrate PR43's selected measurement instrumentation only after fixing formatter and effective-config evidence, with explicit thread lifecycle checks.
4. Integrate PR44 human policy separately, defaults off, without silently stacking overlapping PR42 patches or applying generic AI throttles twice.
5. Run separate controls: original AI vs new AI, renderer on vs off, then minimized-window/headless candidates. Preserve 20Hz actions, unchanged Retail engine/entities/server, CRC, map transition/reconnect, observer join and 60-minute sync gates.
6. No main merge, production DLL replacement or capacity promise until those gates pass.
