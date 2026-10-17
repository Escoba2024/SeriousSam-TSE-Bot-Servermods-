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


## A03 independent reproduction after A00 authorization (2026-10-17)

A00 granted **SOURCE-ONLY** ownership of the three PR #17 paths in coordination Issue #18 (comment `6227932628`, expiry 06:30 CEST); no game, runtime, port, server, or binary lease was granted. The dedicated Shadow worktree was clean before this audit at `e0cb57252654a2fb96b99c536f79953c5e406c6f`.

### Private evidence provenance

Evidence remains uncommitted on Shadow in
`.codex/evidence/hetzner-lowrender-external-20261017-rdc-requalify/` relative to the main TSE checkout. This is a previously completed **archived** lowrender network poll, **not a fresh live query**. The following SHA256 values were independently recalculated on 2026-10-17 and match the prior `audit-rdc-20261017.md`:

| File | Verified SHA256 |
| --- | --- |
| `query.jsonl` | `655CA6594158FA2FC0E1F44409495CDCB09E48CBBA0E8CC1F37D769F054CA4BE` |
| `summary.json` | `3FB2FC06E59FC6FA18044CA3A84AA4A319AD67A108E75B8476C0AEE2C74A0515` |

The independent **read-only PowerShell 5.1** audit parsed all **365 JSONL rows**; each row had `confirmed=true` and an empty error. Both `status` and `statusAfter` were parsed per row (**730 UDP status response strings**). Each response passed leading separator, complete key/value pairs, duplicate/empty-key rejection, empty-valued `final`, no unexpected post-`final` key, expected `gamename`, Retail `gamever=1.07`, exactly one expected bot, dedicated-server flag, and no out-of-range `player_*`, `frags_*`, or `ping_*` keys. All 730 included `frags_0`, `ping_0`, and `queryid`. Results: **365/365 row confirmations; 730/730 structurally valid status responses; zero observed protocol violations**. An initial *audit-command-only* comparison treated JSON empty-string `error` as unequal to `$null`, incorrectly labeling rows unconfirmed; after changing the check to `[string]::IsNullOrEmpty([string]$record.error)`, 365/365 passed. This was not a preflight-parser error or a change to the archive.

Repeat the provenance and standalone fixture gates on the authorized Shadow machine:

```powershell
$repo = 'C:\Users\Shadow\Documents\SeriousSam-TSE-Bot-Servermods-'
$archiveDir = Join-Path $repo '.codex\evidence\hetzner-lowrender-external-20261017-rdc-requalify'
Get-FileHash -LiteralPath (Join-Path $archiveDir 'query.jsonl') -Algorithm SHA256
Get-FileHash -LiteralPath (Join-Path $archiveDir 'summary.json') -Algorithm SHA256
(Get-Content -LiteralPath (Join-Path $archiveDir 'query.jsonl') | Measure-Object -Line).Lines
$worktree = 'C:\Users\Shadow\Documents\SeriousSam-TSE-Worktrees\chatgpt-vanilla-preflight-framing-20261017'
$fixtureTests = Join-Path $worktree 'tools\Test-TSEExternalVanillaPreflight.Tests.ps1'
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $fixtureTests
git -C $worktree diff --check
```

The full 730-response structural check can be re-run read-only using the same `$archiveDir` from above. It reproduces the response framing/field gate without starting clients, sending UDP packets, or exporting private packets:

```powershell
$rows = 0; $responses = 0
foreach ($line in [IO.File]::ReadLines((Join-Path $archiveDir 'query.jsonl'))) {
  $rows++
  $entry = ConvertFrom-Json -InputObject $line
  if ($entry.confirmed -ne $true -or -not [string]::IsNullOrEmpty([string]$entry.error)) {
    throw "Unconfirmed archived row $rows"
  }
  foreach ($field in @('status','statusAfter')) {
    $parts = ([string]$entry.$field).Split([char]92)
    if ($parts.Count -lt 5 -or $parts[0] -cne '' -or (($parts.Count-1) % 2) -ne 0) {
      throw "Malformed $field on row $rows"
    }
    $fields = @{}; $sawFinal = $false
    for ($i=1; $i -lt $parts.Count; $i+=2) {
      $k = $parts[$i]; $v = $parts[$i+1]
      if ([string]::IsNullOrEmpty($k) -or $fields.ContainsKey($k)) { throw "Duplicate/empty key on row $rows" }
      if ($sawFinal -and $k -cne 'queryid') { throw "Post-final field on row $rows" }
      if ($k -ceq 'final') {
        if ($v -cne '') { throw "Nonempty final on row $rows" }
        $sawFinal = $true
      }
      $fields[$k] = $v
    }
    if (-not $sawFinal -or $fields['gamename'] -cne 'serioussamse' -or
        $fields['gamever'] -ne '1.07' -or $fields['numplayers'] -ne '1' -or
        $fields['player_0'] -cne 'TSE_Wine_Low1' -or $fields['dedicatedserver'] -ne 'yes') {
      throw "Status identity/final mismatch on row $rows"
    }
    foreach ($k in $fields.Keys) {
      if (($k -like 'player_*' -and $k -cne 'player_0') -or
          ($k -match '^(frags|ping)_' -and $k -cnotmatch '^(frags|ping)_0$')) {
        throw "Unexpected player index on row $rows"
      }
    }
    foreach ($k in @('frags_0','ping_0','queryid')) {
      if (-not $fields.ContainsKey($k)) { throw "Missing $k on row $rows" }
    }
    $responses++
  }
}
if ($rows -ne 365 -or $responses -ne 730) { throw 'Archive count mismatch' }
"PASS: $rows archived queries, $responses status responses"
```

This structural audit is **independent of**, not a substitute for, exercising the actual PowerShell preflight script.

**Re-executed actual script fixtures:** Windows PowerShell 5.1 `Test-TSEExternalVanillaPreflight.Tests.ps1` → **21 PASS**, exit 0 (2026-10-17). Separately, first/middle/last archived JSONL rows (zero-based indices 0, 182, 364), both `status` and `statusAfter`, were each written to a unique disposable ASCII status fixture and supplied to the **actual patched** `Test-TSEExternalVanillaPreflight.ps1` with four benign mock files, their matching temporary SHA256 manifest, expected bot `TSE_Wine_Low1`, game port `25630`, and query port `25631`. **6/6 PASS**: `FIXTURE_MATCH_ONLY`, `filesVerified=4`, `oneBotOnly=true`, `live=false`, `canStart=false`; exit 0, temporary fixture directory removed. Other 724 archive responses were structurally inspected but **not** individually executed through child PowerShell preflight processes.

**Decision:** No new parser defect reproduced; therefore no speculative source or test changes. Only this report was refreshed. PR #17 remains subject to normal A00 review/merge coordination; **no** new live UDP, native Retail/Vanilla join, CRC/Sync, current server occupancy or release acceptance is claimed. PR #15's Retail harness and DLL work are explicitly outside this A03 handoff.
