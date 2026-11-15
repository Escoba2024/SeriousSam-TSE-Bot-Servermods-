# FirstState: bounded autonomous method-only drain

Status: SOURCE_AND_TEMPORARY_PACKAGE_TESTS_GREEN_ROOT_REVIEW_PENDING. Root
accepted the design. Protocol/worker/session/window/builder have run offline.
The fixed disabled review package awaits Root source review; no native
readiness or runtime qualification follows from these components.

## Ownership and boundaries

The writer owns only new autonomous-drain tools/tests and this plan in this worktree.
Preserve checkpoint 49dcfbb and every existing transport, observer session, strict
validator, compiled JavaScript, Retail binding and frozen package. Root alone
integrates, freezes, qualifies and runs. No additional agent or runtime process.

Reuse the accepted scheduler design in
`../specs/2026-11-15-first-state-worker-drain-scheduler-design.md`.
The existing monitor package is a disabled parent, not a runnable scheduler.

## Fixed contract

- One fresh exec worker owns Frida. No parent import of Frida or Xlib, no thread,
  fork, input, NativeFunction, memory write, extra hook or extra game read.
- Preserve the actual packets and strict Trace.consume, including all counters,
  ordering, limits, identity, TTL, I1/I2 and 38-region checks.
- Preserve 64 records, 8192 calls, 16384 events, 1024 damage records, 256 binding
  calls, binding 2000 ms, TTL 15000 ms, parent-start +85 s and 90 s admission
  scope. Setup consumes the original absolute budget.
- Drain target 20 ms is not a real-time guarantee. Capture duration and service
  interval must each remain at most the existing 100 ms bound; missing/unknown
  timing, overruns and every error remain sticky failures. No catch-up burst or
  deadline reset.
- Raw Frida values are privately archived before validation, under the existing
  512 MiB journal budget. Index at most 1024 captures. Per payload at most 2 MiB;
  fixed framing/metadata at most 16 KiB. A valid full-sized payload must fit
  without truncation, filtering, parsing/re-encoding or a new smaller limit.
- Every capture gets one immutable serial and archived byte range/hash. No
  duplicate, reverse, gap, fabricated, conflicting or silently missing serial.
- A bounded nonblocking select loop services partial command/reply sockets and
  captures. Never block on readline/sendall while admission is active.
- Worker procfs ownership and NativeContext identity before/after each capture;
  existing JavaScript guards per event. Parent full guards before/after every
  batch, rather than falsely claiming the old per-capture parent guard frequency.
- Stop immediately closes admission. Immutable S denotes the last completed
  active capture before closure; never wait for parent backlog validation while
  admitting events. Preserve and validate all cleanup-tail packets through F.
  Repeated barriers cannot move S or F.
- On parent or packet failure, attempt validation of the entire archived serial
  sequence 1..F, retain every error/raw packet and report incomplete work as FAIL.
  No offline success can repair a failed native run.
- Preserve bounded admission-only stop, callback idle, finishstop outside
  callbacks, unload/detach and full original-region comparison. Worker reaping
  follows proven normal closure of all three game roles and units.

## Steps after Root explicitly resumes

1. Read only the narrowly needed base proxy lifecycle, NativePorts archive,
   strict session/Trace interface and method-window helper. Record hashes and
   check the accepted API assumptions. Report an interface blocker before any
   wider redesign.
2. Execute the new protocol tests with the implementation absent: retain actual
   import/contract RED. Implement the smallest new protocol/index module, then
   run those tests GREEN. No new message/result semantic schema.
3. Add fake fresh-exec/socket tests before a new worker implementation: partial
   input frame, blocked output, slow parent, command oversize, wrong owner/start,
   capture failure, raw write failure, timing gap, TTL, archive/index limits,
   stop during active callbacks and post-stop tail. Run RED, implement, GREEN.
4. Add new method-only Ports/Session adapter tests: exact old Trace.consume once
   per original packet; full guards around each batch; continue attempting later
   serials after malformed packets; immutable cutoff/tail, stop on exception,
   final-drain failure, unload/detach failure and roles-first worker reap. Keep
   the old session/API code byte-identical.
5. Add a narrow derivative builder: same monitor conditions and new required
   matched control, all gates false. Exact inverses for intended new helper
   deltas and exact expected hash VALUES for all unchanged parent/API sources.
   Reject self-repinned body/policy/JS, missing/changed pins and altered limits.
6. Run only focused new tests and justified inherited regressions once. Inspect
   every result, record actual RED/GREEN commands/logs, fresh source/payload pins,
   disabled package and limitations. No native or retail compiler.
7. Request Root review and report every child/session ended. No native-ready,
   queue safety or ABI claim until later Root evidence qualifies the actual path.

## Required adversarial evidence

The first test draft addresses framing/index invariants only. It does not prove
the worker scheduler or callback behavior. The implementation must additionally
exercise real old strict validation through a private fixture, fresh-exec OS
ownership/cleanup with fake children, actual partial sockets, and every failure
listed above. Fakes cannot establish a native scheduler latency guarantee.

## Open implementation checks

Unexpected NativePorts message callbacks must not make journal/index byte ranges
ambiguous; retain raw and fail closed if exact capture provenance cannot be
proved. Admission-closed in-flight waiting must archive cleanup tails without
recursively pumping status/drain. A hung Frida synchronous RPC remains bounded
only at the parent IPC boundary; normal role cleanup must remain independent.

## Execution ledger

2026-11-15: actual initial RED: `python3 -m unittest
tools.test_first_state_autodrain_protocol` failed because the new protocol module
did not exist (ImportError retained in private protocol-red.log). New module
then passed11 focused cases in0.027s. No worker/Frida/runtime was executed.

Ruling: Root accepted a fixed binary length prefix plus bounded JSON metadata
and exact concatenated archived JSON payload bytes. This avoids JSON quoting or
base64 expansion and admits a full2MiB payload with at most16KiB envelope.
The first JSON encoding of a Frida Python return value defines the journal bytes;
there is no claim these are original Frida transport bytes. Parent must never
parse/re-encode them as a substitute for byte provenance. Malformed/NaN raw stays
archived and causes strict semantic failure; it is never sanitized.

Ruling: focused tests only, per Root's explicit shared-host resource constraint;
do not run broad unchanged test discovery prescribed by the generic TDD skill.
Root performs the independent full source review and alone decides native use.

2026-11-15 component ledger: missing Worker module RED; real single-loop
assertion RED2; binary proxy RED4; passive native-adapter RED4; method-only Session
RED8 (11subtest failures). After the corresponding new implementation,
42focused cases passed in0.153s. No Frida or game was loaded. Session includes the
unchanged private actual TraceValidator plus retained actual callback fixture
and full38-region restoration contract. Generic packet fakes do not qualify ABI.

Root review correction: one-buffer/index-denominator RED2 preceded direct
journal-preadv wire construction and finalF=actualattempted, including overflow.
Expiry RED showed repeated error journaling2436vs116bytes; a latched expired
state now records failure once and retains a positive select wait without more
capture/status operations. Final observer cleanup can still FAIL without F;
that missing proof is never relabelled as complete.

Memory boundary: production batch transport builds one bytearray via preadv and
memoryviews, without a list of full payloads or a second payload accumulator.
The2MiB fixture's traced encoder peak is below2MiB+16KiB+512KiB. This is not a
whole-Python-heap claim: incoming Frida Python values, JSONEncoder text/encoding,
and strict Parent JSON interpretation require additional bounded transient
objects. Raw journal data is streamed and never retained as a512MiB RAM list.

Observed implementation-stage errors retained privately: an incorrectly placed
patch caused one IndentationError before correction; a fake integer event list
was corrected to dictionary-shaped event fixtures required by the actual
validator interface. The actual original strict callback fixture stayed intact.

Root review correction: STOP-before-slow-Parentguard RED1 showed the expensive
guard before admission close. Stop now uses the own PID/start-bound proxy first,
then full Parent identity; ordinary batches retain full before/after guards.
This special Stop ordering is explicit, not a claimed before-guard equivalence.
Additional RED2 showed a reused worker-start snapshot still allowed IPC and a
second Stop already buffered in the socket reader could wait indefinitely for
new fd readiness. Fresh PID/start/liveness before every command and processing
already-complete buffered commands correct those paths. Focused suite45/45
passed in0.158s. Root's native admission and whole-source review remain pending.

2026-11-15 final source checkpoint: actual production JournalCollector cleanup
raw-failure RED3 (stop/status/finishstop) corrected with a latched Pumpfailure,
without withholding authentic safe cleanup acknowledgements. Windowtransform
RED4, typed-result RED1, additional Native/control alias RED3 and BuilderRED4
preceded implementation. Final focused run55/55 PASS4.275s. Four temporary
disabled builder cases proved154/75 expected hash values,90 unchanged parent
files and whole helper/runner inverses. The fixed OUTPUT package has not yet
been generated; Root's independent source review precedes that delivery.

Review correction after ff205d7: peer receipt638b200d identified last-batch
deadline bypass. OwnerRED4 proved both exact absolute deadline and2s limits
could be crossed during final validation or metadata archive with COMPLETE.
Post-processing absolute check plus budget checks before early collect return
now retain stickyFAIL and safe cleanup; positive1.999s control stays COMPLETE.
Targeted Session11/11 PASS0.017s; focused full57/57 PASS4.154s. No other refactor,
limit change, fixed package, runtime or Root integration in this correction.
