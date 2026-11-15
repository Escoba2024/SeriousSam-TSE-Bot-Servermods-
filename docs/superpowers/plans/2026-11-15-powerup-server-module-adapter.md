# Powerup Dedicated server module contract implementation plan

> Use superpowers:executing-plans and TDD inline; no delegation or native work.

Claim: only NEW powerup_server_module_policy.py, prepare_powerup_server_modules.py,
their two tests, this plan and a new report in the isolated writer worktree
`/srv/tse-powerup-server-hash-v2-20261115` (base16984204). Private evidence is
`/srv/tse-powerup-server-hash-v2-evidence-20261115`. Old packages remain immutable.

The first OFF case061540 is FAIL before census/release. Its successful read1
was not saved before bind rejected fe4 against the V2 OriginalGameMP constant.
The historical FAIL remains. A portable RED reproduces that exact hash-contract
conflict using the pinned reader output contract and real server PID/start;
it MUST NOT be described as replay of a saved native sample (inventory is0B).

1. [x] Pure policy RED then GREEN: accept only explicit server role, exact
   PID/start, original Engine/Entities and exact fe4 GameMP; reject wrong role,
   original/bot/unknown hash, missing/extra hash, PID/start and consistency.
   OriginalV2 remains byte identical. Generate a separate V2 copy with only
   an added policy import and its one hash check delegated to this strict policy.
2. [x] First-raw preservation RED then GREEN: Root ruled ONLY successful
   global read1/paused_smoke. Before bind, serialize the complete untouched
   sample plus existing serial/group/phase/PID/read-start/end provenance to
   a NEW0600/O_EXCL/O_APPEND sidecar (64KiB line bound). No new clock/native read.
   Negative bind leaves raw intact. No complete all-read preservation claim:
   later prebind failures can still lack complete raw data.
3. [x] Builder RED then GREEN: exact inverse of runner import/new namespaces/
   first-raw hook/archive-source list, canonical-groups import, generated server
   V2 copy; originals/V3/auditors/reader/guards/finalizer byte identical. Cover
   paused smoke, gameplay binding, all raw/overlap final validation and direct
   V2evidence. Generate TWO fresh DISABLED packages; verify all pins,81fe4
   closure, role staging, same flags0/1 and no gameplay/tolerance/schema change.
4. [x] Focused tests once, exact outputs/hashes/source report/commits; Root
   integrates/reviews/freezes/backs up and decides the next single native case.

Root accepted the separate exact-inverse server copy; no global monkeypatch,
union of accepted DLLs, changing sample hashes or weakening Original checks.
No Queue/reader/schema/life/time/threshold or cadence changes. Additional sidecar
I/O is one bounded first-sample write while paused, subject to unchanged host
limits and startup budget. It is not free or a native runtime qualification.

Stop all jobs when Root announces STATICONLY. No native/Frida/X/build/live work.

Completed offline:12 unique focused tests PASS0.458s/0skips; two fresh disabled
packages223runtime/75source/48Python pins each,81dedicated targets. Parent
core/reader/V3/auditors remain byte identical. Root review/native work remains.
