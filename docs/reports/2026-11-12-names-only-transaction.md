# Names-only transaction completion — 12 November 2026

## Scope

This change finishes the prepared A2 controller. It does not deploy a DLL, stop a
Dedicated server, authorize a native run, or establish milestone-A acceptance.
The existing pool and assignments are retained. The generic backend has no CLI
entry point and performs no runtime work on import.

The exact write set is 48 active PLC4 name fields, the two Red Station launchers,
and the Red Station roster JSON. PLC4 tails, GUIDs and sidecars are preserved.
The staged payloads are independently regenerated through the byte planner;
a correct payload hash alone cannot authorize a non-name change.

## Files

- `tools/fleet_names_apply_policy.py`: 48-slot identity/query checks and ordered
  apply/rollback orchestration, including journal-failure handling.
- `tools/names_staging.py`: existing offline PLC4, launcher and roster byte planner.
- `tools/fleet_names_transaction.py`: canonical file IO, exact locks and manifest
  closure, staged payload validation, guarded backend and journal recovery.
- The corresponding three test modules exercise the planner, policy and backend.
  Existing pool, native-log, query and identity-wait tests remain applicable.

The runtime-specific entry, original stop helper, dependency manifest, native
paths, service names, GUIDs and raw evidence remain private.

## Safety and recovery contract

The caller must acquire the existing fleet-install lock, deployment lock, Red
identity-rotation lock, and both runtime/rollout locks for each of the six
instances, in that order. Lock aliases and replaced lock inodes reject. The
private entry passes the held-lock guard into the backend.

Preflight verifies six original GameSpy responses, all 48 actual local
attachments and profile GUIDs, and each Dedicated process generation and pinned
inputs. Extra players are preserved. Query name multiplicity is retained.
A current native process must hold a writable FD for its corresponding log;
old unattached log bytes are insufficient. Source drift rejects before shutdown.

Before each shutdown, the exact own native PID/start, service invocation,
root and pinned modules/config are checked. Only the reviewed normal-close
adapter is available. Its exact acknowledgement is required before a closed log
is archived. No force-stop or server-stop callback is added.

Before each start, the saved stop policy and normalized systemd ExecStart /
ExecStartPre configuration must match. ExecStart must invoke the reviewed Bash
launcher; pre-start commands are limited to configured sleep commands. Volatile
systemd PID/timestamp fields are excluded from that comparison.

Start intent and service invocation are journaled before native identification.
An interrupted native-identification wait can recover only the same durable
systemd invocation, matching root/pins, current host boot and a process birth at
or after the recorded start intent. A replaced invocation or PID is rejected.

**Deliberate limitation:** a controller death after the start command but before
the invocation receipt is durable leaves an identity blocker. Recovery does not
adopt a new PID merely because it appears in the expected service. The main
operator must retain the evidence and independently review that ambiguous
generation. This controller provides no override that bypasses this boundary.

Rollback closes only recorded/recovered own generations. It validates complete
backup scope and every backup blob before restoring mutable inputs, including
saved ownership/mode. Binaries and server files are never restored through this
writer. Red startup rotation is temporarily bypassed while old names rejoin.
Only after all old actual/query identities are verified are the original
launchers restored. The final full backup byte/metadata comparison must pass.

A failed candidate's closed log can contain sync/crash/join-failure markers:
those bytes are retained during rollback without preventing a valid old-state
restore. IO failure to retain the log still blocks completion. Retried archival
uses a fresh destination instead of overwriting an earlier receipt.

A transient failure to journal the apply exception does not skip a subsequently
journalable rollback. Every actual recovery phase still needs a durable intent.
If journaling remains unavailable, mutation stops and both the operation and
recovery errors survive. A first close-intent failure does not stop healthy
clients. Incomplete recovery and failed final journaling are never success.

## Offline evidence

The initial regressions reproduced unsafe symlink replacement, missing service
invocation validation, loss of the apply error after a journal failure, inability
to recover an identified interrupted start, backup-path escape, and refusal to
restore after retaining a failed candidate log. Each received a targeted
RED-to-GREEN check.

Real temporary-file tests cover full 51-file application, all saved bytes after
rollback, 48 loaded names, untouched server generations and extra players,
metadata restore, exact write boundaries, late foreign-name collisions,
interrupted invocation recovery, archival retry and manifest/lock boundaries.
The Red launchers execute actual harmless Python scripts through Bash in these
fixtures; rotation would create an observable marker, which remains absent on
apply and rollback startup.

Verification history:

- The policy/backend batch passed 30 tests before the last two collision/start
  regressions; those two then passed independently.
- A broader seven-module run completed 79 tests with one **test-fixture** error:
  a styled example omitted the required explicit bold terminator. The validator
  correctly rejected it. The fixture was corrected; production formatting rules
  were unchanged.
- The final low-IO batch passed **64 tests in 2.251 s**, including that corrected
  planner fixture, all policy and file/lock/manifest boundary tests, and the
  existing name-pool, closed-log, query and native-identity-wait suites.
- The last service-launch-command regression passed separately after its fix.
  Fifteen full filesystem/backend scenarios passed in the broader run before
  that final command-binding guard.
- The complete current 80-test seven-module command was not repeated during the
  main agent's initial native resource-sensitive comparison. The bounded review
  corrections are verified in the subsequent full focused run recorded below. No compile, live transaction or native launch was performed
  by this implementation worker.

Reproduction command (from the repository root):

```bash
cd tools
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest   test_gaming_names test_names_staging test_fleet_names_apply_policy   test_fleet_names_transaction test_native_closed_log_evidence   test_gamespy_query test_native_identity_wait -v
```

This is a focused Python suite, not the entire project's C++/native acceptance.

**Post-review final run: 89/89 tests passed in 125.552 seconds, exit 0.**
This complete current run includes all seven new backend regressions and both
byte-boundary scanner regressions. The separate private bootstrap regression
also passed: omitting the transitive graceful-close helper rejects before native
imports. The refreshed seven-source/six-dependency package validated offline;
the runtime gate remains false.

## Bounded independent-review corrections

The first independent review identified three additional runtime boundaries.
They are corrected without changing the name-only write set or the existing
normal-close acceptance rules:

- Both final verification methods bind every observed and freshly rechecked
  native target exactly to the durable started record, including PID/start,
  invocation and pins. Identical names on a replacement process do not pass.
- Full new client-generation log snapshots are scanned for the same sync,
  disconnect, CRC, crash, invalid-action and join-failure classes used by the
  closed-log gate. An error before success enters the existing rollback path.
  This also applies to the new generations started during rollback.
- Each still-running Dedicated server gets a private durable preflight prefix
  with length, SHA256, source device/inode and exact server generation. Historical
  events remain explicit baseline evidence. Preflight and final apply checks
  require the original prefix to remain intact and reject any new SYNCBAD or
  sync-disconnect match. Truncation, rotation and same-size rewrites reject.
  A match spanning the baseline boundary is new, even when the boundary falls
  inside a word or a line with an earlier historical match.

The shared error scanner preserves the closed-log marker classes. No blanket
sync tolerance and no additional old-client-prefix system were introduced.
Journal schema 3 requires the six durable Dedicated baselines; older incomplete
prepared journals cannot silently acquire invented baseline evidence.

Rollback retains the failed attempt's server events; those historical events
cannot be undone by restoring names. Its success still means verified restoration
of old bytes/metadata and exact own new client generations, not server stability
or DLL qualification.

The private source closure now includes the original graceful-close helper behind
the wrapper. Its expected path and the wrapper's ORIGINAL_SHA are checked before
native imports or the first stop; a missing transitive dependency is rejected by
the offline bootstrap.

## Remaining root-owned work

1. Independently review the whole change and rerun the current focused suite.
2. Capture fresh live source/profile/launcher data under the existing locks;
   compare the current complete mutable inventory with the prior capture.
3. Rebuild the stage from the same 48 stable assignments and fresh original
   bytes. Preserve all current DLL/config/Nav baselines; do not promote a combat
   candidate as a side effect of name deployment.
4. Review the current public-query collision/ownership picture and service
   launch commands, current log-FD proof, normal-close helper and disk reserve.
5. Freeze the entire private import/data closure. Keep every used package and
   stage immutable for recovery; a later restage uses a new package/run.
6. Only the main agent may enable the private runtime gate and invoke the
   reviewed transaction. Preserve exact evidence, refresh name-dependent
   monitoring after verification, and perform separate native health and
   independent external/browser checks. Host-to-public-IP queries do not prove
   an independent WAN/browser vantage.
