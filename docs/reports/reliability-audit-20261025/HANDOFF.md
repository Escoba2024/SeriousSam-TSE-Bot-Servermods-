# C1 Reliability: offline audit, 25 October 2026

Five additional defects are reproducible against the actual imported PR50
supervisor/health modules. The isolated integration patch passes all 11 audit
tests and the inherited Python suite (91 PASS, 1 deliberately skipped). This
is an offline regression result, **not native Retail/Wine qualification**.

Branch: `agent/c1/20261025-reliability-audit`; worktree:
`/srv/tse-c1-reliability-20261025`; source baseline: PR50 `b5dafb8`, after
PR46 `d6d2911` and PR49 `5b0157f`. The baseline supervisor exactly matches the
read-only reference `/srv/tse-live-reliability-20261024`; the later reference
branch head does not imply a different supervisor source.

Only `poc/research/reliability-audit-20261025/**` and this report directory were
changed. No production source was edited, no push/merge/deployment performed,
and no Retail game, service, cgroup, Wine command, firewall, mount or public
port was manipulated. Tests use synthetic files, a pidfd for their own Python
process, and inherited local fixture processes/ephemeral loopback sockets.
The externally reported Build06 Dedicated399158/Bots399232/399305 and
real/unknown foreign slots were not contacted or acted upon.

## Reproduced defects and patch behavior

| Finding | Reproduction against unmodified code | Isolated correction |
|---|---|---|
| State read precedes controller lock | Previous controller publishes a new result generation immediately before this controller acquires its lock; the new controller consumes the old generation. | Read `result.json` after acquiring the instance lock. |
| Unregistered native role can survive an exec/save crash | An unregistered `SeriousSam.exe` in the instance cgroup passes `ownership()`; a missing saved role is still eligible for launch. | Reject unregistered Dedicated/SeriousSam/Xvfb processes found in that cgroup. Do not silently adopt or kill them. |
| Path-based writer scan misses hardlinks | Keep an append handle open through a different hardlink to the source inode; `archive_closed()` unlinks the source anyway. | Match open descriptors using device/inode identity, retaining read-only-handle support. |
| Archive manifest bypasses archive budget | Long synthetic source/archive paths make the manifest exceed a small declared budget although raw bytes plus the old fixed allowance fit. | Check compressed output plus projected manifest and existing archive files before source removal; publish manifest before unlinking source. |
| Unterminated SYNCBAD line appears fully scanned | A file ends with an owned `SYNCBAD` record without its newline; scanner reports `complete=true`, owned count 0. | Keep the scan incomplete while a partial record remains; after newline, retain the owned count and complete the scan. |

These are five demonstrated boundary failures, not a claim that they caused
the historical production incident. The orphan test simulates the exact
post-exec/pre-save state at dependency boundaries; it does not crash a real
Wine controller or demonstrate a native duplicate game process.

Additional existing-behavior checks exercise the actual imported code for
PID-reuse pidfd closure, controller lock contention, unknown/stale/malformed/
duplicate/human rosters, action-time roster validation, owned-sync and
incomplete-scan holds, OOM/throttle/resource/disk holds, and CPU/RAM boundary
admission. Six tests pass on both baseline and candidate.

## Reproduce

From the original C1/PR50 worktree (contains the pinned stacked operations modules):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 poc/research/reliability-audit-20261025/run_audit.py --report-dir docs/reports/reliability-audit-20261025
```

The runner pins both baseline modules, observes the five expected RED failures,
copies source into an automatically removed directory under the research scope,
applies the patch there with zero fuzz, then imports those real patched modules
for both the audit and inherited suite. It verifies the original module hashes
remain unchanged. Exit 0 means the expected RED set and both GREEN runs were
confirmed; RED alone intentionally exits 1:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 poc/research/reliability-audit-20261025/test_reliability_audit.py
```

For an already integrated source tree, select it directly without the baseline
pin requirement:

```sh
TSE_AUDIT_SOURCE=/path/to/reviewed/tree PYTHONDONTWRITEBYTECODE=1 python3 poc/research/reliability-audit-20261025/test_reliability_audit.py
```

Fresh results and complete synthetic diagnostics are recorded in
[results.json](results.json), [red-tests.txt](red-tests.txt),
[audit-tests.txt](audit-tests.txt), and [inherited-tests.txt](inherited-tests.txt).
The inherited suite discovers 92 tests: 91 PASS and
`test_native_absent_server_wait_with_remaining_process` SKIP, explicitly because
the C1 assignment excludes real Wine CLI operations. Existing negative CLI
fixtures intentionally print errors; the suite has zero failures/errors.

## Exact versions and integration

Integration artifact:
[`0001-close-controller-archive-and-sync-gaps.patch`](../../../poc/research/reliability-audit-20261025/0001-close-controller-archive-and-sync-gaps.patch).
It changes only `tools/operations/fleet_supervisor.py` and
`tools/operations/fleet_health.py` when deliberately applied by the integrator.
The current worktree's files at those paths remain unchanged.

| Artifact | SHA256 |
|---|---|
| Baseline supervisor | `83d2bec6507d9de87fa7c42a97af69501f8f77b4608122a6f954dbfae20c1242` |
| Baseline health | `152d2b71865d0649f977016701267ed17a086eb15a506c4113173a28f45e1800` |
| Patched supervisor | `c0c1a99853f373ff052f33252ccab12f436537a3f96be85c1fccfbea62a3f87b` |
| Patched health | `ef99e37d4754c60ad3acf0eb484a529e56b80115c6734ba21252c68c1f4fd030` |
| Integration patch | `9268f2a11bc4cd52589061af4094376a673d688cd9952278345b49e51ef31ba4` |

Integration starts with `git apply --check` of that artifact against the
intended branch, review, and direct imported-code tests. Preserve this audit
alongside the patch so the baseline RED proof remains reproducible. Rebase or
merge conflicts require fresh verification rather than accepting the old SHAs.

## Remaining limits and blockers

The historical completed hour qualifies supervisor SHA
`d83a81e3a26d08a2f718e6b6c3fddaf8e3d650e3784707c90b56fba60ee00c28`,
not the inherited `83d2...` correction and not this `c0c1...` proposal. Both
later versions still require their own native ownership/helper/Xvfb recovery,
duplicate-start, full human/unknown protection, closed-generation archive and
circuit tests, Originalclient/GameSpy evidence, and final-source >=3600 s run.
No native or 24/7 PASS is claimed. Current foreign runtime occupancy and the
offline assignment prevent those checks; old CPU-pressure observations are not
presented as a fresh resource measurement.

Writer and cgroup inventories remain point-in-time observations. This patch
does not provide a transaction against a foreign actor reopening/replacing a
file between final inspection and unlink, nor automatic adoption of an orphan.
Exclusive ownership and closing all role/prefix writers remain mandatory.
Unknown helpers that do not identify as the three native executable names are
left to the existing cgroup/prefix/ownership guards. Inode-based `/proc` scans
add metadata reads; their native overhead is unmeasured.

Archive admission now bounds the committed archive files plus the projected
manifest. Atomic manifest replacement can transiently retain old and new
manifest bytes; it is not a strict bound on instantaneous filesystem use or
crash durability (`fsync` was not added). A failed archive step can leave a
compressed artifact with the original source intact, preserving evidence for
manual reconciliation. No eviction of old evidence is introduced.

A permanently truncated final line now intentionally holds recovery until the
closed generation is examined. This trades recovery availability for accurate
scanner completeness; no synthetic newline is appended to evidence.

Review performed here is an author self-review. Independent integration review
and all native checks remain outstanding. Required project policy and current
coordination files were read. No Ghidra/Frida, remote MCP or GitHub write was
needed for these source-level findings; the optional managed-environment status
tool was absent from the actual tool registry.

Integration note: main does not yet contain the stacked PR50 runtime modules. From the master integration branch, reproduce with `python3 poc/research/reliability-audit-20261025/run_audit.py --source-root /srv/tse-c1-reliability-20261025`. The runner now discovers inherited tests from that selected source snapshot; no dependency on unmerged runtime files in main is implied.
