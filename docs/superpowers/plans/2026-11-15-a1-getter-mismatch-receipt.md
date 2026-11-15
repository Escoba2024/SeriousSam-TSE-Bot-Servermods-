# A1 first getter mismatch receipt implementation plan

> **For agentic workers:** Use superpowers:executing-plans and test-driven-development.

**Goal:** Retain actual/expected bytes from the existing single getter read
when any of the three current getter guards fails.

**Architecture:** New exact SHA-pinned reversible source transform inserts one
shared getter comparison and replaces exactly three current guard expressions.
It uses unchanged `rebased` HIGHLOW logic; only a false comparison constructs
diagnostic detail for the existing `need` → `fail` → `e.raw.detail` path.

**Spec:** Root task after all own method controls failed to reproduce the native
outer-callback mismatch. Actual first mismatching bytes are required before a
getter protection change. No inference that generic deferred flush is causal.

## Global constraints / review focus

- Body206a232e and compiled7108529a are the only accepted disabled parents.
- Pass performs one existing22B read; failure reuses those same bytes.
- Exactly three callsites; existing compare, failure text and rebasing retained.
- Whole body/compiled inverse and G-prefix byte equality mandatory.
- Old guards, gates,18hooks/38regions/11imports, timing/counters/schema unchanged.
- Fault detail only: actual/expectedRebased hex, RVA/length, getter map/callback
  and TLS binding state. No native calls, memory writes, timers or second read.

## Task

- [x] Actual old guard behavioral RED: mismatch exists but emitted raw.detail
  lacks the bytes; no missing import counted as RED.
- [x] Minimal pure transform; new shared routine single-read on PASS and FAIL.
- [x] Actual compiled-source VM checks all22 mutations, HIGHLOW relocation,
  three fault paths and same-read proof when backing memory changes after read.
- [x] Exact inverses/adversarial changes/disabled boundaries; focused inherited
  VM regressions, private receipts/logs, report and commit. No package/native.

Pre-flight: source helper/test files new and separate from Root source writers.
Only current test fixtures are composed privately; no Retail bytes published.

Ledger: actual old-guard RED five VM failures/one explicit skipped inverse,
no imports failed. GREEN seven tests0.571s; final eight tests1.074s including
nine inherited scenarios on the transformed compiled source. Self-review:
only one existing memory read/rebased compare, fault detail from that array;
all three exact substitutions and complete body/G inverse proved. Independent
Root source review remains pending. No package/native qualification.
