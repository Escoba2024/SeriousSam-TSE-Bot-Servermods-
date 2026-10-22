# Reliability continuation: reviewed corrections and qualification ledger

Host: `ubuntu-4gb-nbg1-2`, Hetzner-only, 22 October 2026. Follow-up [PR50](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/50) targets PR49, which targets PR46. Public GameMP Build04 and original binaries are unchanged.

## Reproduced defects and corrections

1. Repeated native stop entered already-unmounted Wine prefixes. Stop now closes a prefix only when its exact expected overlay is still present. Existing process/mount/cgroup ownership and actual command failures remain enforced. Regression failed before correction and passes after it; first new harness attempt also independently completed two final stops.
2. Confirmed server exit used a recovery branch that bypassed OOM/throttle, owned sync and incomplete-log-scan holds. That branch now permits only the expected absent-server observations and informational historical alerts; every other safety hold blocks it. Unknown future safety codes also block. Five adverse subcases reproduced before correction.
3. Independent review found missing CPU/RAM admission. Startup and individual role launches now require a measured one-second host sample with <=70% busy, and >=768 MiB protected available RAM plus forecast (server192 MiB, client384 MiB, fleet includes128 MiB display allowance). A root-owned host-wide flock serializes controllers through startup. Health includes current/peak private cgroup memory and host available RAM; memory below768 MiB holds recovery. These conservative admission estimates are policies to validate, not measured per-role memory claims.
4. Private master announcement suppression did not isolate its wildcard query listener. Own game/query port pair now also has a tagged non-loopback INPUT drop, installed before launch, verified throughout ownership checks and removed only after shutdown. An absent/unverified rule holds adoption and further actions. Only private26800–26999 ports are accepted; production25600/25601 are outside this interface. Actual IPv4 rule and listeners are checked in native qualification. No assertion about a second public server's WAN visibility follows from this firewall check.
5. Direct action guard accepted duplicated bot nicknames, unknown mod or wrong capacity that health rejected. Health and direct action guards now share complete Retail query-roster validation. Fresh action revalidation also rejects a query changing after reconciliation. Unit regressions first reproduced all four failures; normal external players remain protected by a human hold.

Independent review evaluated the original combined PR46/49 implementation and first correction. Three Important findings (reserve, ingress, roster) were accepted and corrected in one test-driven pass. No Critical or Minor finding was established. Runtime/reboot/WAN/CRC cause were explicitly not established by that read-only review; deliberate root compromise was outside its threat model. The author's final corrective pass is covered by failing-then-passing regressions and the complete suite, not a claim of a second independent review.

## Verification before native source freeze

- 85 root Python tests PASS, 59 benchmark-tool tests PASS.
- C++ `make -C poc/botcore test smoke` PASS, including555 Human-AI checks and the real extracted integration block. Existing unused-function compiler warning in the integration smoke remains; no new DLL was built.
- `git diff --check` PASS. PR47's isolated read-only source snapshot separately passes124 root Python tests; no PR47 runtime test repeated or code merged.
- Local proof commits `5460602`, `bf2573a`, `ef8b0f4` retained. Published equivalent-tree commit `b5a6cba184d881c41014d601c139db00d4ea1ec5`, tree `8293f2e4f6837b1995a0e8b7593f511f1b8b1ae8`, exactly matches the tested local tree. Shell HTTPS lacks credentials; publication used the authorized connected GitHub Git-object tools, without any desktop or credential transfer.
- Frozen native source SHA256: supervisor `d83a81e3a26d08a2f718e6b6c3fddaf8e3d650e3784707c90b56fba60ee00c28`; health `152d2b71865d0649f977016701267ed17a086eb15a506c4113173a28f45e1800`.

## Monitor false uncertainty: reproduced resource interaction

An independent six-collection read-only probe used the existing service's CPUQuota5% and MemoryMax128M. Old source returned QUERY_UNCERTAIN6/6 times: total8.70–12.10s, query age5.89–9.29s. The same old source outside this cap collected in0.268s with query age0.198s and correctly returned ALERT. Thus this observed monitor warning can be produced by its own quota plus repeated log processing; it does not demonstrate missing UDP responses or multiplayer packet loss.

The incremental candidate initially holds while scanning historical evidence. Under the same quota, its first four collections were incomplete; after catching up it preserved all105 external faults, with two warm collections of5.60/5.70s total and query age3.10/2.90s, returning ALERT. A separate service-shaped candidate probe runs against the immutable deployment bundle and separate output. These are monitoring tests, not game sync acceptance. `query_fresh` now uses the same age rule as the verdict and exposes the age.

## Native execution: pending

First new harness attempt read `result.cgroup` before the resource-guarded controller initialized it. Failed before gameplay qualification, retained privately; repeated stop and public identity checks passed. Corrected R2 waits for actual initialization. It runs on private26880/26881, display128 with exclusive own native/session locks. Double-start, actual owned bot loss/recovery and controller adoption have passed at the current checkpoint. Final >=3600s, server recovery, cleanup and original-client checks remain PENDING until their actual results are appended.

Public monitor migration is staged as an immutable four-file bundle with checked hashes, a verified systemd unit and explicit restore instructions. The original source/unit/pins remain available. No production game restart or automatic recovery is enabled. A real host reboot and24/7 remain NOT_TESTED.
