# M1 – paired Retail 1.07 exported-function snapshots

Status: DIAGNOSTIC_PROGRESS, not root-cause or release acceptance.

Original Engine SHA256: b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f. Original Engine107 SDK declarations plus original PE exports and disassembly were read on Hetzner. The native producer hooks only conventional function entries (SessionState::ChecksumForSync and base/player entity checksum functions); no CMP/interior hooks and no state writes or altered sync checks. Frida temporarily changes process code memory and may perturb timing; all instrumented runs remain diagnostics.

## Source validation
- Export RVA e5b10 is SessionState::ChecksumForSync; prologue 55 8b ec 6a ff.
- Original MakeSynchronisationCheck RVA e7eb0 calls it, then complements the returned CRC and emits the 16-byte tick/sequence/CRC/level block.
- Original checksum disassembly reads session sequence +0x20, level +0x1c, pause/state word +0xa8 and optionally further state. Player target table has stride 0x88; two action objects at +0x10/+0x40; only the first 40 bytes enter CPlayerAction checksum (timestamp excluded).
- Tick bits at session +0x4c are independently confirmed by original MakeSynchronisationCheck disassembly. This is not an assumed 1.10 layout.
- All raw traces, process records, player data and runtime files remain private on Hetzner. Public code refuses public namespaces, other roots/cgroups/generations, modified DLLs and unreviewed entry addresses.

## New tests and native observations
- 16 focused test methods: RED with 17 failed assertions/subtests, then GREEN. Covers mismatched/absent ticks, sequence, altered action bytes/CRC, conflicting duplicates, malformed input, namespace/generation/cgroup/hash and unsafe entry rejection. No fixture is a native runtime proof.
- Fresh integrated tools suite: 147 tests, 146 passed, one native Wine process test deliberately skipped.
- Fresh onebot uninstrumented control: 157.02 s, PASS_LIMITED_SESSION_LIFECYCLE, peak one, drained cleanly.
- Onebot instrumented run: 186.87 s, PASS_LIMITED_SESSION_LIFECYCLE, source-pinned same Cecil-P1 DLL, original Retail control.
- Three concurrent 30-second capture jobs: server 29 snapshots, original client 29, botclient 23; all jobs detached without capture errors.
- Exact shared tick+sequence comparisons: server/original 29 and server/bot 23; all captured actions, layer CRC transitions and raw final CRC matched.

This validates a bounded paired producer. It does not reproduce the historic fourbot failure, establish root cause, prove all engine fields or satisfy 60/60/120-minute stability/restart gates.

Next: collect fourbot paired evidence around the earlier failing tick. Keep public runtime disabled and the 8 GiB free-space reserve.

## Fourbot diagnostic checkpoint
- Isolated instrumented fourbot run completed: 359.64 s including orderly drain; PASS_LIMITED_SESSION_LIFECYCLE, peak four.
- All six 150-second capture jobs finished without capture errors: server 147 snapshots, original control 148, four botclients 151/153/154/155.
- Exact server/client paired comparisons: original 147; bots 137,118,99,79; all captured CRCs, actions and player layer transitions matched.
- Historic five-SYNCBAD case not reproduced in this bounded run. No root-cause fix inferred.

## Independent review and duration gate hardening
Read-only independent review found three Important duration acceptance weaknesses: unbound bot identities, count-only cleanup and missing host time coverage. Concrete negative reproductions failed RED; each was fixed GREEN.
- Exact telemetry identities must equal sample process roles and healthy decision IDs.
- Cleanup role/mount sets must be unique and exact; runtime evaluator independently verifies empty cgroup, absence of live processes using the private root and absence of expected mounts.
- Host samples must cover native elapsed/UTC through final cleanup with monotonic bounded gaps and final reserve data. These are host-wide resource observations; native producer/source and private artifact paths are separately pinned. No nonexistent child identity fields are manufactured.
- Duration evaluator: 22 test methods. Short real control remains REJECTED for insufficient full-population/telemetry duration; no release status inferred.

## Further M1 acceptance/recovery safeguards
- Native JSON truncate/write race reproduced and handled by bounded retry with no fallback success state (5 regression tests).
- Fourbot/3600 and eightbot/7200 boundary cases and native source-inventory drift covered.
- Recovery command construction, exact three-stage admission, default/import side effects and identity-bound direct-child cleanup tested. An independent reviewer found three concrete recovery-driver issues; all were corrected before native fault work.
- 39/39 build-source files plus candidate DLL hash reverified; running onebot original Engine kick threshold independently read as 10 through read-only procfs.
- Public server remains off. Long native duration and fault outcomes still require actual receipts.
