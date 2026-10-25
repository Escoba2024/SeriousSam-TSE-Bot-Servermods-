# C2 – Native sync capture/compare preparation, 25.10.2026

Result: an implemented **offline** capture-bundle validator and comparison tool,
37 synthetic regressions, and independent review of PR58 at
`df7108ba04cafb120c6a035503fa2f9732a83b0f`. **Retail runtime: NOT_TESTED. Root
cause remains open.** No native hook or capture producer is implemented here.

Worktree `/srv/tse-c2-sync-20261025`, branch
`agent/c2/20261025-native-sync-gates`, base `ab0c740`. Write scope is restricted
to `poc/research/native-sync-gates/**` and `docs/reports/native-sync-gates/**`.
Existing worktrees and process names were inventoried read-only. Existing Wine/
SeriousSam processes were observed and left alone. No server query, game process
start/stop, DLL replacement, MCP attachment, network instrumentation or live
configuration change was performed. No private logs/binaries were copied into Git.

## Evidence read and conclusions retained

- [Mandatory tool policy](../../decisions/2026-10-17-tse-ai-tools-mcp-policy.md)
  and repository `AGENTS.md`: offline tests cannot replace Retail acceptance;
  unknown shared processes, public players and qualified DLLs remain protected.
- [Retail investigation, 17.10.](../2026-10-17-retail107-sync-check-investigation.md):
  the Retail kick/counter path and threshold 10 are established; actual checksum
  divergence cause is not. Historical failures do not invalidate separately
  qualified candidate hashes. The handler RVA is not a proven action/state
  capture function or a license to hook a running process.
- [Integrated acceptance](../2026-10-21-human-cpu-final.md),
  [runtime ledger](../2026-10-21-integration-runtime-ledger.md), and
  [tick diagnosis](../2026-10-22-p0-bot-tick-diagnosis.md): preserve the exact
  candidate/environment/duration scope. Bot tick telemetry and UDP continuity
  cannot independently locate the first divergent engine state.
- PR58 tools and report were read through `git show`, not checked out. The
  separate `/srv/tse-bot-ai2-20261025` tree was searched read-only for capture/
  Frida/sync tools; the visible versioned matches were the historical report and
  `tools/analyze_sync_log.py`. This is not a negative claim about private tools
  elsewhere, and is not a new Frida qualification.

## Independent PR58 review

Reproducer: `python3 -B poc/research/native-sync-gates/review_pr58.py`. Python
3.12.3/Linux: upstream **29/29 tests PASS**, then all seven independent findings
below reproduced using synthetic data. No runtime input or copyrighted content.

| Severity | Pinned path/function | Reproduced behavior | Consequence |
|---|---|---|---|
| High | `tools/sync_crc_diff.py:compare_snapshot` | Removing CRC still yields `COMPARABLE`, `crc_equal=None` | Missing mandatory evidence can exit successfully |
| High | Same function / common parser | Appending an unparsed line still yields `COMPARABLE` | Parser errors are not a closed gate |
| High | `compare_series` | One aligned pair plus an unmatched server snapshot yields `COMPARABLE` | Intersection is mistaken for complete window |
| High | `compare_series` maps | Two server snapshots with the same key; later equal one overwrites earlier divergent one | Genuine fixture difference disappears |
| High | `sync_incomplete_detector.py:detect_incomplete` | No inputs yields `complete=true` | Absence of evidence becomes success |
| Medium | `check_telemetry` | Header plus nonnumeric data row has no issues | Claimed numeric validation is absent |
| Medium | `sync_forensics_common.py:parse_server_log_events` | Tick `1.2.3` matches regex and raises `ValueError` | Malformed input crashes instead of structured blocked result |

Paths in this table are under the pinned PR58
`poc/research/sync-forensics/` tree. The original suite passing does not cover
these cases. The C2 change leaves PR58 files unchanged; it supplies an independent
strict gate and reproducible review. Integration should not treat PR58 exit 0 or
`COMPARABLE`/`complete=true` as native acceptance.

The PR58 report also goes beyond its evidence in places:

1. Ground-Lookahead failure is a useful candidate-specific hypothesis. It is not
   established as the explanation of all historical generations. No aligned
   action/state evidence or historical ground-code identity was shown.
2. Deterministic RNG/AI does not exclude incorrect action construction, tick
   assignment, ABI differences or deterministic simulation divergence.
3. A static `cli_bDumpSync` symbol does not establish a usable per-tick server and
   client capture interface or the proposed text parser's actual Retail grammar.
   First qualify output, phase, overwrite behavior, cadence and completeness.
4. Counter jumps can reflect missed lines, interleaved clients or observation
   scope; field-name categories based on 1.10 are hypotheses, not Retail ABI proof.

## Implemented gate design

The [tool contract](../../../poc/research/native-sync-gates/README.md) uses a
single sealed manifest and independent server/client JSONL artifacts. Identity
is session + connection epoch + level epoch + sequence + exact engine tick;
layout/phase, all selected player actions and every required state field are
mandatory. Full action/state byte lengths prevent truncated snapshots from
being treated as differences. Binaries, map, config, producer, binding evidence
and both captures are read and SHA256-verified before any pair comparison.

Both sides must cover the whole declared window in order. Missing/extra/duplicate
records, shared gaps, wrong epochs, non-integer ticks, unknown fields, missing
CRC, incomplete producer declarations, drops and invalid tails produce `BLOCKED`
without a difference result. Native labels require a producer-attested
`verified-retail107` binding, but even then output says `NOT_TESTED`: file hashes
and attestation cannot authenticate a live module or a true native observation.

This tool intentionally does not parse guessed Retail dump text or derive engine
ticks from BotDriver counters. A future native exporter must supply a defensible
raw-to-record mapping; otherwise the gate remains blocked. Its limited schema is
an interchange proposal, not an ABI discovery.

The output is `MATCHED_WINDOW`, `DIFFERENT_WINDOW`, or `BLOCKED`, exits 0/3/2.
The first observed difference includes sequence, tick, domain(s), JSONL line and
whether a preceding captured pair matched. It never says first divergent
simulation tick, first cause, or native PASS. Every artifact hash and the
manifest hash bind the comparison to the local inputs. Keep verifier commit/
source hash with the private execution record.

## Native capture gates – all pending

These gates are evidence requirements for the responsible runtime owner, **not
manual A00 authorization stages**. C2 did not execute them. The public experimental
Build06 generation with other players must not be used as the diagnostic target.

| Gate | Required evidence before proceeding | Current status |
|---|---|---|
| N0 Isolation | Private cloned installs/prefixes, own ports/PIDs, ownership and exclusive lock, no foreign players; inventory and restore plan | NOT_TESTED |
| N1 Exact identity | On-disk and loaded module hashes/base/RVA for executable/Engine/GameMP/Entities; map/config/OS/Wine/CPU/build/tool versions; unique run/join/map epochs | NOT_TESTED |
| N2 Retail binding | Independently verified 1.07 function/ABI, source bytes and lengths, applied-action timing, native sequence/tick mapping, state coverage and raw capture offsets | NOT_TESTED |
| N3 Capture qualification | Owned disposable-process smoke, then isolated TSE qualification; passive hooks only; records/drop counters, cadence and rollover verified, server/client independently sealed | NOT_TESTED |
| N4 Perturbation | Matched uninstrumented/instrumented controls: elapsed duration, CPU and tick cadence, log volume, hook timing distribution; predetermined overhead/continuity budget and regular detach/cleanup | NOT_TESTED |
| N5 First-window compare | Baseline matching samples, then whole declared window around initial SYNCBAD; exhaustive action/state/CRC pairs, no ignored lines/gaps and no slot/epoch ambiguity | NOT_TESTED |
| N6 Cause experiment | Change one hypothesized cause in isolated candidate, repeat original reproduction and control, compare same provenance and phases | NOT_TESTED |
| N7 Acceptance | New DLL SHA, full native one/four/eight-player regression and hour gate, active Vanilla combat/respawn/map/reconnect; browser/24h assessed separately | NOT_TESTED |

For any external Vanilla start, the existing
`tools/Test-TSEExternalVanillaPreflight.ps1` remains mandatory where applicable;
freshness and exclusive occupancy must be checked again at actual start. Its
fixture result never authorizes runtime. Unknown/foreign players are left alone.
Do not lower/disable `ser_iKickOnSyncBad`. Do not reuse the non-restoring
`Test-RetailJoin.ps1` wrapper to replace a protected DLL. A new build is a new
candidate; historical qualified `61DC...` and `7FC9...` copies remain protected.

The static sync handler address identifies the bad-sync handling path, not every
capture site. A native specialist must separately verify checksum-generation and
action-application hooks in the exact loaded x86 image. Never apply 1.10 offsets
or serialize C++ objects using an assumed Retail layout.

## Hypotheses and controlled matrix

All hypotheses remain **OPEN**. No row is a claim that failure will occur.

| Hypothesis | Same-window observation to obtain | Discriminating experiment |
|---|---|---|
| Action serialization/composition | Raw full action bytes plus checksum-relevant subset at verified phase, lengths, timestamp fields and slots | One owned bot; baseline action mode, then single controlled movement/fire change; compare producer vs applied streams separately |
| Sequence/tick assignment | Action receive/apply identity, session/join/level epochs, message sequence and true engine tick | Same actions with controlled local scheduling/latency variation on isolated ports; never infer mismatch from latency alone |
| Simulation/state difference | Matching applied actions but first different verified state field/CRC | Same exact map/seed/config, short matching prelude, then one candidate feature; compare per-tick state before root-cause attribution |
| ABI/float/RNG state | Binary/toolchain identity, exact typed bytes, RNG/float fields only after Retail layout proof | Identical Engine/Entities and controlled candidate pair; deterministic AI is not an exclusion proof |
| Missing CRC coverage | Different CRC but equal selected state/action fields, or vice versa | Expand verified field coverage without changing simulation; requalify exporter and overhead |
| Observation artifact | Gaps/duplicates, parser errors, hook cadence or CPU effect | Native no-hook control and passive-hook control with sealed raw logs; invalid/incomplete data remain blocked |

Minimum matrix: Vanilla↔Vanilla uninstrumented/instrumented; one exact qualified
bot idle/movement/combat; one experimental candidate with one feature toggled;
only after a clean one-client baseline progress to four/eight owned bots. Hold
map, seed, inputs, duration, config and environment constant within each pair.
Capture a short fully covered window around reproduction before long captures;
long-term acceptance is a separate subsequent run. Map changes/rejoins split
bundles, never pool them by map filename, IP or similar wall-clock timestamps.

## Verification and RED/GREEN

Executed on 25.10.2026 with Python 3.12.3/Linux, all synthetic:

- Initial test-first gate contract ran against an unimplemented stub and failed;
  helper errors were corrected before the implementation was verified.
- Explicit behavioral RED: `test_truncated_action_and_state_bytes` initially
  failed (`DIFFERENT_WINDOW` instead of required `BLOCKED`). Adding declared
  per-action/per-state byte sizes made it GREEN.
- Example generator RED: missing executable made its CLI regression fail.
  Generator implementation made it GREEN and refuses existing destinations.
- Final `python3 -B -m unittest discover -s poc/research/native-sync-gates/tests -v`:
  **37/37 PASS**. Includes CLI exits, per-execution input immutability, symlink
  escape, duplicate JSON keys, non-finite input, provenance tampering, late invalid
  records, synthetic/native-label boundary, state differences despite equal CRC,
  independent gaps on both sides, and a candidate GameMP differing from Vanilla.
- `python3 -B poc/research/native-sync-gates/review_pr58.py`: original **29/29
  PASS**, **7/7 findings reproduced**, exit 0.
- `git diff --check`: PASS after final scoped changes.

No Windows build, Frida-MCP/TSE-hook qualification, native capture, native Retail
acceptance, runtime root-cause fix, production stability or long-term gate was
performed. Native action/state data needed to resolve the cause remain absent.

## Handoff

```text
HANDOFF
slot: C2 Multiplayer Sync
ticket_or_pr: independent review PR58 df7108b
branch: agent/c2/20261025-native-sync-gates
base_sha: ab0c740
head_sha: resolve final scoped commit with git log -1 --format=%H
paths_changed: poc/research/native-sync-gates/**; docs/reports/native-sync-gates/**
tests: Python3.12.3 Linux; 37 synthetic gate tests PASS; upstream29 PASS; seven findings reproduced
retail_runtime: NOT_TESTED
resource_cleanup: temporary PR58 extraction removed automatically; no game resources acquired
known_issues: native producer/binding/aligned captures absent; root cause OPEN; PR58 strict-gate findings unresolved upstream
pr_url: no PR created or push performed by C2
status: REVIEW
```
