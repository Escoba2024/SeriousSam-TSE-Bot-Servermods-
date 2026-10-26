# SSAM.AI – M1 native Retail sync handler instrumentation (26 October 2026)

**Classification: PARTIAL_DIAGNOSTIC_SUCCESS / UNSAFE_COMPARISON_HOOK_FAILED / NO_ROOT_CAUSE / NO_RELEASE.**

## Scope and source pins

Hetzner `ubuntu-4gb-nbg1-2`; public gameserver intentionally stopped by user
throughout. Only isolated, single-owned, netns/Wine Retail 1.07 copies were
used. Existing PR73 fail-closed private native runner, a pinned Cecil P1 DLL
(SHA256 `7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf`)
and unmodified Retail `Engine.dll` (SHA256
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`).
Engine image base was derived from the *exact* private `/proc/PID/maps`
hash-matching file and verified executable PE RVA. Original files were not
modified. Frida Interceptor hooks modify *process code memory temporarily*;
do not describe them as non-instrumenting/read-only native execution.

## New code

- `tools/native_sync_handler_probe.py`: exclusive private-process, netns,
  cgroup, epoch, UID and original-engine-SHA guard. Bounded Frida handler
  reachability at pinned RVA `0x000e2d10`, capped duration and private,
  sanitized result. Does not record player names, IPs, raw packets, CRC bytes
  or network identifiers.
- `tools/test_native_sync_handler_probe.py`: TDD red/green regressions for
  ownership, pinned RVA mapping, real non-contiguous Wine PE maps, stale
  process state, source SHA, result class and prevention of dangerous
  comparator hooks.
- The attempted interior comparison interception at original binary
  `0x601a34b2` (`cmp ecx,eax`) and `0x601a34ca`
  (`cmp edx,eax`) **caused an unsafe result**. It is explicitly
  *disabled and absent as executable native hook code* in the published
  probe; `--comparisons` fails closed before any attach. Offline operand
  summary helpers remain unqualified consumer logic only.

## Native receipts and independent counterexample

| Run | Native status | Duration | Evidence |
|---|---|---:|---|
| Single-bot control, initial probe | PASS_LIMITED_SESSION_LIFECYCLE | 117.31 s | Zero observed server SYNCBAD. Original initial Frida module lookup failed safely; no qualified handler sample. |
| Single-bot control, PE-map corrected, count-only | PASS_LIMITED_SESSION_LIFECYCLE | 116.78 s | 1,272 server handler entries in 20.39 s, 0 Frida errors; 0 observed server SYNCBAD. No native CRC input comparison. |
| Single-bot comparison-instruction experiment | **FAIL** | 19.31 s (native receipt) | Server query unavailable beyond 15 s, Wine unhandled page fault writing to `0x3bffffef` at `0x601a2d57`; instrumented target exited. Probe status `PROBE_FAILED`, errors FileNotFoundError and UNLOAD_FAILED. |

In the failed interior-hook attempt the private trace emitted **one** level
operand and **one** CRC operand pair before the failure; those observations
are **NOT qualified** as stable CRC captures, have no authenticated
server/client phase mapping, and are not used to infer correctness/cause.
Raw private traces, PIDs, session records and full crash logs are retained
**only on Hetzner**, under `/srv/tse-session-qualification-master-*`
and private backup controller logs. They must not enter public Git.

The first handler-count-only native qualification is an instrumentation
reachability observation, not M1 completeness. The historic 2026-10-25
Cecil P1 four-bot five-SYNCBAD failure remains unresolved.

## Safety ruling and next step

**Ruling:** stop native CMP-site Frida interception; a bounded read-only
preflight and successful handler-entry hook do not guarantee safe
instrumentation at interior branch/cmp instructions. One failing run
is sufficient to suspend that approach. A later alternative requires an
isolated *non-instrumented* 1.07 baseline, instruction relocation review
and its own explicit controlled approval gates. Never repeat unsafe hook
merely to collect more CRCs.

Prefer statically qualified Retail binary/ABI disassembly and a safe producer
that obtains applied actions + CRC/state on both original server and
client without changing game semantics. Engine aggregate log/timer counters,
a single server-side operand snapshot and offline PR58/65 synthetic
comparisons are insufficient. Build a connection-epoch, exact applied-action
phase and tick mapping before diagnosing the first divergent state.

**M1:** IN_PROGRESS. **M2/M3/M4:** not natively integrated or accepted in a
single release candidate. Public gameserver remains offline.

## Tests and release limitations

Fresh `python3 -m unittest discover -s tools -p 'test_*.py'`: 81 PASS,
including 25 handler probe tests. All source compile/syntax tests passed.
No 60/60/120-minute gates, no paired CRC producer, no fixes to the underlying
native sync issue, no M1–M4 shared DLL and no release deployed.
