# A1 fault-stop final denominator implementation plan

> **For agentic workers:** Use superpowers:executing-plans and test-driven-development.

**Goal:** Preserve the original observer fault as FAIL while recording one
authentic final drain/F after verified idle and successful detach.

**Architecture:** Reuse the actual JournalCollector, CaptureJournal and
DrainPump with synthetic RPC exports, without importing Frida. After exact
status/finishstop consistency checks, latch a non-host reason without raising
past the existing final capture and index.finish. No getter change.

**Spec:** Root ruling after closed trace 085939: original fault reason remains
FAIL; final capture/F must still preserve the denominator, not repeat cleanup
until the deadline. No TTL/queue/2s/schema relaxation.

## Review focus and global constraints

- Non-host fault/TTL/queue reasons remain sticky and unchanged in raw packets.
- Stopped false, wrong shape or changed reason never permits final F.
- Actual raw/final capture failure still fails; no fabricated evidence.
- S remains immutable and F covers all active/tail captures.
- Missing idle continues to veto detach and F; original deadline unchanged.
- Separate primary getter failure from cleanup follow-on, with unknown offset.

## Task

- [x] Actual production collector/pump RED: authentic non-host stopped ACK
  otherwise leaves F unset and loops after every status interval.
- [x] Minimum exact consistent ACK correction; record non-host FAIL and still
  execute original final capture/index.finish.
- [x] Targeted GREEN plus existing focused autodrain regressions, no broad suite.
- [x] Deterministic first-fault/private receipt, sanitized report, commit.

Pre-flight: new focused test consumes actual worker module, already separate
from Root C++/runtime claims. No new transport or JS architecture.

Ledger: first fixture run failed at missing loaded/expected fields; kept as a
setup-error log, not a behavioral RED. Corrected actual-owner RED: five failures
including changed idle/finishstop reason accepted by old code. Four new tests
GREEN 0.060 s; all 61 focused tests GREEN 4.275 s. Self-review: exact consistency
guard precedes non-host sticky FAIL and original finalcapture/F path; active
callbacks, bad ACK and original timeout still veto. No getter cause/fix claim.
Root independent source review remains required.
