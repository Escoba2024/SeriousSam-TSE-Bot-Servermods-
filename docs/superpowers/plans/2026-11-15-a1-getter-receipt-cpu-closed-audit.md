# A1 closed getter-receipt/CPU trace audit plan

> **For agentic workers:** Use superpowers:executing-plans; data audit only.

**Goal:** Audit exactly the closed093359 trace, retaining its CPU FAIL.
**Architecture:** One bounded deterministic private reader validates all13
wireframes against original journal byte ranges, then reuses the pinned pure
strict packet/TraceValidator on all28 packets and external38-region restore.
No runtime/controller import or test execution.
**Spec:** Root task after result d5064191…: first/all calls, epoch/tick/life,
fault/detail/order/drop/abort, F/denominator and actual CPU context; unknown
process CPU attribution must stay unknown.

## Scope and steps

- [x] Pin original result/raw/wires/frozen pure policy sources; bounded13 wires.
- [x] All capture serials1..F, exact original byte ranges/hashes and wireclosure.
- [x] Existing strict schema/TraceValidator; complete call/event/tick denominator,
 18kind census and every call's observed life context in private receipt.
- [x] Getter faults/details and TLS timing, independent38 original expectations.
- [x] Host interval/observation/worker command timings; no CPU-cause inference.
- [x] Private reproducible receipt and sanitized report commit; stop all jobs.

No source/harness fix, retries, package, native, Frida, tests or public raw IDs.
The normal host-stop in this case does not exercise the non-host fault-stop fix.

Ledger: one complete deterministic audit read, 13 wires/28 exact journalranges,
strict original validators accepted406events/203pairs; F28/S27, no getterfault,
all38regions equal before+expected. CPU77.50556793% aggregate interval remains
FAIL; missing per-process attribution UNKNOWN. No tests/native/sourcefix.
