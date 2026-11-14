# A1 NoSmooth: local doubled yaw, cause still open

Status: **FAIL before fire**. Read-only analysis; no new native attempt or observer installed. This report contains sanitized facts, not private raw records.

## Actual observation

Private window: `/srv/tse-milestone-a-evidence-20261111/a1-colt-preparation-20261114-084241`.

- Both calibrated axis gains were −0.25 degrees/pixel. Nine subsequent horizontal +12-pixel requests each produced the expected −3-degree local/received delta. The tenth (action index 15) produced **−6 degrees**.
- Its receipt records exactly one confirmed +12-pixel XTest request. That proves one controller request, not a measured twelve-pixel displacement at the Original input boundary.
- Last baseline: local/server/received yaw −27 degrees. `rotation-pairs.jsonl` line 150, 50.627 ms after request completion: Original local cumulative yaw already −33, while server/received yaw remains −27. Line 151, 291.803 ms after completion: all three values −33. Lines 153–156 retain −33 across 0.149998 native seconds. The settled excess is therefore exactly **factor two**; waiting for settled ACK did not remove it.
- All 156 accepted pairs read effective AllowMouseAcceleration=0, MouseSensitivity=0.25 and AllowPrescan=0. The single pre-calibration passive controls sample succeeded: local/profile 0, global smoothing 0, X/Y axis smoothing 0, effective smoothing 0, relative axes, influence 1. The smoothing flags were **not** resampled at the failed impulse.
- The long post-request hold (0.305 seconds) contains no repeated mouse emission. An earlier successful impulse also had a 0.310-second hold. Hold length alone is not a demonstrated cause.
- No fire, damage or A1 completion is proved. The failure remains genuine. Main separately verified restoration/absence/original preflight; this analysis does not replace that proof.

Pins: `result.json` SHA256 `664e6328163f4e6e44418028082d27650cd40531fb1921398e1cf9bbd1b07d40`; `rotation-pairs.jsonl` `375056e468bfe050191819d100fade4be877a071156809b07a28ef18843fd03a`; `controls-effective.json` `49a0c0afea21a7b5743634a1032522e274ab8f42e4a8c1015a31246b04e4708e`.

## Original static path and smallest decisive observation

The existing static evidence is `/srv/tse-a1-colt-pitch-analysis-20261112/evidence/Engine-GetInput.asm.txt` and `Game-Controls.asm.txt`, with timer/prescan call excerpts in that directory. No new disassembler or runtime tool was used.

| Original module SHA256 | Preferred VA / RVA | Required passive observation |
| --- | --- | --- |
| Engine.dll `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f` | GetInput 600CD200 / D200 | Entry thread, invocation ID, bool prescan and CInput identity; return engine X/Y readings at this+24/+38 |
| same Engine | GetCursorPos call 600CD2AC / D2AC | Actual success/result and cursor minus original center this+17A4/+17A8; retain invocation ID |
| same Engine | SetCursorPos call 600CD56A / D56A | Original recenter arguments and API success, attached to the same invocation |
| GameMP.dll `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208` | CreateAction 60850470 / 10470, compose call 608504FE / 104FE | Character/action arguments, actual thread, correlated input ID; raw action before compose and cumulative action afterwards; separate Entity accumulator/received/viewpoint observations |

These are **preferred-file addresses**, never literal live addresses: loaded base + RVA, matching module identity/hash, relocated instruction guards and ownership checks are mandatory. Engine preferred base is 600C0000, Game preferred base 60840000. An initial RVA transcription error was caught by static PE verification before any attach and corrected; the generator now derives RVAs from the archived preferred VAs and verifies exact instruction bytes.

At CreateAction entry, x86 this is ECX; stack arguments are **CPlayerCharacter reference** at ESP+4, action at ESP+8, prescan at ESP+C. Original timer instructions 608512F0–608512F8 bind the character to Game+114 for required profile 0. The inner IAT 60861404 at 608504FE calls `ctl_ComposeActionPacket`, not an assumed CPlayer member function. The frozen CP reader maps +CC4 to Entity local cumulative input yaw, +CA0 to received cumulative yaw and +344 to relative viewpoint yaw. Its Original Entities fingerprint E3CED contains `fld [edi+CC4]`, `fadd [action+0C]` and the subsequent store through `lea [edi+CC4]`; Player.es475/509 corroborates this accumulation inside compose. The collector records these levels separately and also records raw action yaw immediately before compose, rather than treating a viewpoint field as consumed input.

No PID=TID assumption remains. The first actual thread is bound only after matching Original input this, prescan flag and timer return 60851241. Action return 608512FB, controls/character arguments and the same actually observed thread must match. SDK107 Timer.h97–99 explicitly notes thread-local clocks; it does not establish main-thread execution. Cursor/recenter observers sit at Original instruction boundaries (D2B2, D56A, D570), with no USER32 export hooks or Wine structure assumptions.

This **one correlated input-consumption trace** is the decisive next observation: one raw displacement 24, two sampled displacements 12, one Engine axis consumed twice, or a changed transformation between those boundaries become distinguishable. It is not a request for another parameter combination or a tolerated larger error. Precision/filter and effective controls globals should be copied into the same bounded record so a changed transform is not inferred solely from a configuration file. Existing samples do not establish their values at the failed invocation.

Prescan is disabled in every accepted pair and the Original rendering branch skips its GetInput(TRUE)/CreateAction(TRUE) path when that global is zero. The trace must nevertheless retain actual invocation mode; configuration is not a call-count observation. The current evidence does not prove which unresolved input-boundary mechanism caused the doubled local delta. A doubled server application is unsupported because the local excess precedes server adoption.

## Collector implementation: disabled, native validation pending

The initial System-Python import check was incomplete: the existing qualified A3 path is `/srv/tse-frida-probe-20261111/lib/python3.12/site-packages`, with Frida17.26.2. The implementation reuses exact hash-pinned A3 `host_binding.py`, `controller_guard.py`, `damage_policy.py` and the frozen NoSmooth controls decoder. It imports no Frida at module import, starts no process and remains `RUNTIME_REVIEWED=False`. Existing tools are reused; no dependency/service/subscription is added. A disposable-method control and matched uninstrumented control still precede any new Retail measurement; historical A3 success does not qualify these different hook sites.

The library has six instruction listeners for those four boundaries, a 256-record queue, 4096-call cap, 90-second TTL timer, no synchronous host I/O inside callbacks, no callback waits, and no call/result replacement or gameplay writes. Full Original GetInput/CreateAction/axis/caller ranges are checked before arm and after detach. Private guard metadata SHA256 is `319cf4889bc3290ecfc84cc0a65b6015f330e7c99ad99b87d95e984bde67ed46`; protected Retail bytes remain outside Git. Wrong bindings/flags, losses, API failures, journal/message errors and timeouts remain sticky failures.

ARM may land between a legitimate GetInput and CreateAction. Such warmup observations are excluded; no controller input is allowed until an actual complete bound pair has been observed (at most one-second startup wait). Stop disarms new captures, retains admitted callback pairs until their leaves, and only then detaches/unloads/verifies Original bytes. A one-second quiescence timeout retains script/session and raises, so the outer controller must still perform its normal owned-role cleanup. Message/journal errors cannot skip otherwise safe quiescent cleanup. An RPC transport hang itself is not proven bounded by the Python polling deadline; this is part of the pending method/control check and existing outer-controller supervision.

Use an isolated Original client only, after main independently rechecks preflight/ownership. Main alone freezes gates and starts any measurement. Instrumented outcomes cannot qualify A1 or establish absence of observer effects. A separate disabled controller copy is required: retain the existing CP/RD comparison, including exactly two historical bounded forward body-alignment impulses, and end unconditionally before CP's fire branch. Root explicitly retained these two inherited impulses to preserve the control conditions; no new route/pickup/fire input is permitted. Library `before_input` alone is not sufficient integration. No run is running or scheduled by this branch.

## Offline deliverable and verification limits

`tools/analyze_original_input_trace.py` accounts for a compact, reviewed projection of that future full ordered trace. Its shape labels are diagnostic examples, never runtime qualification or causal proof. It has no process, mouse, network, subprocess or hook access. Twelve unittest methods exercise ordinary gain, doubled/repeated raw displacement, active input reuse, idle events, altered transformations and incomplete observations. The projection maps `entity_local_accumulator_before/after` to analyzer `local_yaw_before/after`; it does not conflate the action packet with received/viewpoint ACK levels. Full raw chronology remains private; this projection does not authenticate a collector or replace chronology review.

Analyzer RED: initially 9 methods/19 failures (missing implementation); later three actual idle/missing-consumer regressions RED→GREEN. Latest targeted checks after resource release: analyzer **12/12**, host/cleanup/Original-file tests **11/11**, synthetic JavaScript callback model **21/21**. These are portable/model/static checks only. No Frida import, attach, method smoke, compiler or native attempt was executed by this agent. The exact native collector and hard no-fire controller integration remain pending main's review and qualification.

An earlier broad `python3 -m unittest discover -s tools -p 'test_*.py'` was mistakenly launched during the exclusive A4 lab window. It used substantial CPU and compromised that resource observation. It was **ABORTED**, not passed: own PID 1344797 received SIGINT (no effect), then SIGTERM; a fresh process check found it absent, with no children observed before termination. Main has been notified. No further tests/compilers/runtime will run until main explicitly releases resources. This mistake must not be used to qualify or reject Build019 gameplay.

Targeted commands: `python3 -m unittest discover -s tools -p test_analyze_original_input_trace.py`; `TSE_A1_INPUT_PRIVATE=/srv/tse-a1-input-trace-controller-20261114 python3 -m unittest discover -s tools -p test_a1_original_input_collector.py`; `node tools/test_a1_input_trace_callbacks.js`. The private package contains Original guards and disabled source copies/manifests. No broader discovery is authorized as part of this subtask.

Private library package `/srv/tse-a1-input-trace-controller-20261114`: source manifest SHA256 `d509b72c3f1c6fbb7c22d9f61caa53f225c8f7f98dfa65531ef9f40245fa47dc`, 15 source/external pins, `runtime_reviewed=false`. No live registry or launcher is provided by the library. Main must separately verify its frozen parent controller's inherited manifest/lock/population constraints; the explicit ownership callback is not itself proof of exclusivity.

Observer-window correction: the initial 20s/1024-call observer could expire inside the unchanged85s CP/90s runner. A targeted synthetic budget regression failed then passed after aligning only the observer to90s/4096calls; queue256 and all CP inputs/deadlines/ACK/gain rules remain unchanged. This is observation coverage, not an extended gameplay test or a native pass.

The separate disabled no-fire runner and bounded worker supervision are now implemented; see `2026-11-14-a1-input-trace-controller-handoff.md`. This resolves the source-level unbounded-RPC exposure in the owning parent without claiming that a Frida RPC itself has a deadline. Original methods, observer overhead, independent controllerreview and any native trace remain separate open gates.
