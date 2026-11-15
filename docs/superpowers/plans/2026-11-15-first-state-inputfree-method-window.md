# FirstState input-free method window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein deaktivierter reproduzierbarer control|trace-Zweier-Original-Methodencontroller auf dem bestehenden PitchRoot.
**Architecture:** Exact-anchor Sourcepatch + byteinverse; kleiner Methodenhelper mit lazy Trace-API; beide privaten Eltern bleiben unverändert. Kein neuer Launcher und keine Eingabeimplementierung.
**Tech Stack:** Python standard library, fokussierte FakeContext/Clock/Worker-Fixturen, AST/inverse/Closureprüfungen.
**Spec:** docs/superpowers/specs/2026-11-15-first-state-inputfree-method-window.md

## Global Constraints

Genau2Originalclients/serverOriginal. 10s nachJoin,85s inneres/90s äußeres Budget; parent_started bei main-Eintritt. Keine Input-/Pointer-/Fokusaufrufe/AI/Runtime/Delegation. Authorgates false;72Methodenpins/38Regionen/11Imports/18Hooks/Registry2 unverändert. AbsoluteDeadline min(parent_started+85,armnow+15), feste IPC3/.1/2. Alte 6Input-/Collector-Gates/BaseCLI/FirstStateRunner false. Control ohne Worker-/Fridaimporte. Alte Generic-/Restore-/Hostgates bleiben.

## Review Focus

Startfehler vor Handlerzuweisung; Workerreap vor normalen3Rolecloses; control mit transitivem Workerimport; unvollständige Tick-/TLS-/38Restore-Evidenz; Setup-/Bind-/Observationskosten überschreiten unveränderte Deadline.

### Task1: pure methodscope/finalizer and lifecycle helper

Create tools/first_state_inputfree_method.py +tools/test_first_state_inputfree_method.py. Interface MethodWindow(mode,api_root,arena,evidence,parent_started,frame,records,pins,own_identity,unit,periodic,save,clock,sleep). run/finish_before_roles/finish_after_roles_closed; pure candidate_status(report,window) returns no promotion onFAIL.
- [x] RED control noimports/noinputs, exact10s/budgets/tracecfg, failures retain handles, requiredTLS/TickPair/38Restore, stickyFAIL and normalclose-before-reap.
- [x] Minimal helper reusing API; GREEN and commit.

### Task2: exact narrow PitchRoot retarget and disabled package

Create tools/prepare_first_state_inputfree_method.py +tools/test_prepare_first_state_inputfree_method.py. Compose private method-api folder from exact72pins; retain legacy false runner/unusedCLI. Patch run_dual anchored replacements and save exact inverse diff/closure receipt.
- [x] RED exact mainCallgraph/noInput/noWorkercontrol/oldFunctionsunchanged/falsegates/strictmodes/72closure/worker-finally-order.
- [x] Build fresh /srv/tse-a1-first-state-inputfree-method-disabled-20261115. Run only focused source/helper/package cases. Report/pins/commits/alljobsended.

## Ledger

Task1→Task2: method object assigned before run; finally calls finish_before_roles, geerbte cleanup_chain, freshquiescent+all3closed, finish_after_roles_closed. No helper can trigger a separate runtime start. Rootexplicitpairdecision supersedes older single-window assumption. Control imports only standardlib helper; trace API is lazy. No further approvalround required; Root alone freeze/start.

Task1: RED10/10 missinghelper; GREEN10/10 focused0.021s. Per-window privatefixture directory corrected after O_EXCL correctly rejected accidental fixture reuse; no production loosening. Control has no API import; Traceonlylazyload; object retains proxy/session across arm failure and requires allrolesclosed before reap.

Rootruling:90s Admission/Observation, keinHardwatchdog; unveränderteStartupFail-/Cleanupbounds bleiben, parent_started amMaineintritt+85/15TTL. ExpiredContext RED→GREEN vorWorker/Arm; NonmainTickpair RED→GREEN. Task2 complete:21/21focusedPASS5.113s. RootreviewR1 expectedHashValues:5adversarialeREDs→GREEN, kompletterWertevergleich+nestedmapping+fixedHelperSHA. Finalfresh51e1bc45/151pins72Methods; altesf2cae1f7bytegleichbewahrt. Author self-review completed; Root independent final review pending. NoRuntime/Native/inputs, allownjobsended.
