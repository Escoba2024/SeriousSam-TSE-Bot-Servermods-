# A1 passive input-consumption diagnosis implementation plan

> **For agentic workers:** Use superpowers:executing-plans. Main owns all integration and runtime. This branch prepares only an offline analyzer and a reviewable observation proposal.

**Goal:** Distinguish changed cursor displacement, repeated cursor sampling and repeated action consumption without changing input tolerances or game state.

**Architecture:** A bounded passive trace connects each original GetInput invocation to its cursor displacement, stored Engine axis and subsequent CreateAction/compose observations. The Python analyzer consumes a projection offline. The separately disabled collector reuses the existing hash-pinned A3 Frida/host/cleanup framework; the separate no-fire controller runs this observer in a bounded fresh IPC worker; no new dependency/service is introduced.

**Tech Stack:** Python standard library/unittest; proposed original Retail 1.07 address-bound observation only.

**Spec:** `docs/reports/2026-11-14-a1-nosmooth-input-cause.md`.

## Global constraints

- No game, DLL build, hook installation, attach, runtime edits or new native attempt.
- No tolerance, calibration, input-count, timeout, aim or fire-policy change.
- Synthetic results are offline diagnostic examples, never native qualification.
- No private raw player/process records or Retail binaries in Git.
- The A4 lab remains exclusively owned by main.

## Review focus

- Lost/truncated observations must prevent attribution: test rejected dropped/incomplete traces.
- An input request receipt is not an observed cursor displacement: test distinct request and raw totals.
- Multiple action consumers of one input must remain visible: test repeated input ID in actions.
- Prescan and multiple threads must not silently collapse into one timer path: retain invocation mode/thread; reject incompatible action linkage.
- Nonfinite values, duplicate IDs and unbound actions must prevent attribution: malformed trace tests.

## Task 1: Portable trace-accounting examples

**Files:** Create `tools/analyze_original_input_trace.py`, `tools/test_analyze_original_input_trace.py`.

**Interfaces:** `analyze(trace: dict) -> dict` consumes one completed, bounded, already ABI-reviewed trace with request, input and action records. Produces observed scalar totals and one conservative shape label; always `native_qualified=false`, `cause_proven=false`.

- [x] Write failing tests for ordinary gain, raw doubled, raw repeated, reused input, changed transformation and malformed/incomplete cases.
- [x] Run tests and record expected missing-analyzer failure (9 methods, 19 failures).
- [x] Implement strict offline accounting and conservative labels (not yet run).
- [x] Run focused suites: analyzer12/12, host/Original-file11/11, JS callback model21/21. Broad tools discovery ABORTED and not repeated; see report.
- [x] Commit initial proposal/analyzer for main review: 26cd1df0b8cc1655ddcebc3932e4587aa7fe72a8.

## Task 2: Disabled collector, implementation delivered for review

- [x] Resolve six Original instruction boundaries, exact character/action ABI and timer caller returns against pinned files. Generator derives RVAs from preferred VAs; full byte ranges remain private.
- [x] Implement bounded correlated observations, 256 records, 4096 calls, 90s TTL, real observed timer TID, startup-ready gate and disarm/quiescence/detach ordering. No input/call replacement/game-data writes.
- [x] Prepare and run targeted model/host/static tests, including callback/API/queue/life/flags faults, warmup, stop in flight, sticky message/journal errors, timeout retention and Original ranges. This is not native ABI or tool qualification.
- [ ] Verify the existing Frida tool/method on an own disposable process, overhead and matched uninstrumented control; no reliance on SDK1.10 or the stand-in model as native proof.
- [ ] Main reviews exact source/pins, performance budget and normal close/restore path before any separate future measurement. Existing uninstrumented NoSmooth run is a control, not proof of observer safety or identical execution.

## Task 3: Separate disabled no-fire runner (Root follow-up)

- [x] Copy the frozen NoSmooth controller; keep current RD/CP/ACK/gain policy and inherited startup/resources/restore logic.
- [x] Retain exactly the two bounded historical body-alignment forwards: Root explicitly retained these on 14 November to preserve comparison conditions. No new route/pickup controls.
- [x] Return TRACE_ONLY/NO_FIRE immediately before CP's fire branch; additionally reject fire/unknown controls in the controller allowlist regardless of gain outcome.
- [x] Bind collector before every inherited input, record request times, and close/detach/verify bytes before inherited reader/role/file cleanup.
- [x] Commit separately: add4ed4 + 2f6f700; final independent source review by candidate_audit found no remaining critical/important issues. Runtime gates remain disabled. Main alone freezes gates and launches any smoke/control/native measurement.

No native attempt is running or scheduled by this plan. Root's explicit follow-up authorized implementation; no new user approval round is requested.

Task3 adds fresh-exec worker supervision: real socket deadlines isolate blocking Frida calls from inherited normal role/file cleanup; own worker termination only after actual normal role closure and fresh quiescence. Targeted63 offline cases pass; native Original methods/control/overhead remain open; independent controllerreview has no remaining critical/important findings. Concrete package, pins and commands: `docs/reports/2026-11-14-a1-input-trace-controller-handoff.md`.

Root-review correction adds exactly two fixed diagnostic modes, instrumented by default, and an executable uninstrumented matched no-fire control. Start-constructor failure reaps only a provably unarmed child. Two regressions RED on add4ed4 then GREEN after explicit resource release; no broader/native checks.
