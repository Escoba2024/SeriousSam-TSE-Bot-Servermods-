# Fail-closed UDP query framing in external Vanilla preflight

Date: 2026-10-17. Scope: `tools/Test-TSEExternalVanillaPreflight.ps1` and its disposable fixture tests. This is an independent, isolated review; no native Retail installation or running Dedicated/Vanilla/Bot process was changed.

## Reproduced pre-fix defect

The original GameSpy status parser iterated over available backslash-separated pairs and silently ignored malformed framing. It did not require a `final` marker, did not reject duplicate keys, and could accept an unexpected `player_2` alongside `numplayers=1` and the expected `player_0`. Thus a syntactically invalid or inconsistent status response could produce `oneBotOnly=true` and, with valid local hashes and a live query, could reach the `READY_AT_CHECK_TIME` decision. This is a **potential unsafe authorization path**, not evidence that a real production server sent such a response.

Before modifying the parser, added a negative offline fixture and ran the test file on Shadow: **RED**, `FAIL: missing final blocked`, exit code 1.

## Fix

- Require leading separator and complete key/value pairs; reject dangling/unpaired fields.
- Reject empty or duplicate field keys and require a single empty-valued `final` marker, with only optional `queryid` afterward.
- Reject player fields outside exactly `player_0`, and unexpected `frags_*` or `ping_*` indices, even if `numplayers` claims 1.
- Require GameSpy `gamename=serioussamse` in addition to the existing Retail version, port, dedicated flag and expected bot name.
- Preserve strict fixture-mode `canStart=false` and all original hash/process checks.

## Verification and limits

- Offline PowerShell fixture tests: **21 PASS** on Shadow (initial eight plus thirteen new cases, including optional-queryid and realistic per-player fields), after patch.
- Independent read-only audit of **365 archived real GameSpy query samples**: **730/730** complete `status`/`statusAfter` responses validate against the stricter structural conditions. All include `final`, `queryid`, `frags_0` and `ping_0`; 0 structural exceptions. No private raw responses committed.
- Actual patched PowerShell preflight replayed **6/6** archived real datagrams (first, middle, last; before/after status) using disposable synthetic Retail binaries with matching temporary fixture hashes. All returned `FIXTURE_MATCH_ONLY`, four hashes verified, `canStart=false`, `live=false`. This is not a new live or native join.
- Independently executed Python suites: **44 PASS** (25 fleet, 9 obstacle, 10 release smoke). Source provenance: **13 hashes PASS**.
- The combined legacy `Test-Publication.ps1` finished exit 1 at its Python runner because PowerShell 5.1 treats unittest progress printed on stderr as an error with its `$ErrorActionPreference='Stop'`. This pre-existing runner defect is addressed separately in draft PR #15; the same Python tests all return exit 0 when run independently. Do not claim a combined Publication PASS on this branch.
- `git diff --check`: clean.
- No live UDP query, live process scan, native Vanilla client join, Linux/Wine test, masterserver listing or release acceptance performed by this change.
- Historical genuine server responses were checked, but **no fresh live response** was fetched by this PR and there is no operational runtime acceptance. Current server occupancy must still be checked immediately before any permitted start. On a rejected/malformed response, fail closed and investigate; do not relax the gate merely to start a test.
- Regression fixtures are synthetic; additionally, private genuine status captures were analyzed locally read-only. No raw captures, Retail binaries or player data are published.

The patch does not overlap the Retail DLL restoration work or the cloud fleet-auditor PRs.
