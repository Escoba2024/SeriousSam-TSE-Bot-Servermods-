# A4: readable round scripts and observed round order

## Result and scope

The previous A4 controller has a reproducible script-materialization defect. Under the actual root umask 0077, its existing `write_text` loop creates the four new round-2/3 files as mode 0600, root:root. An actual UID/GID-65534 process cannot read them. The new disabled private review package explicitly stages all seven files as mode 0644, UID/GID 65534, records their actual bytes and metadata, and requires a successful read by that identity before starting game processes.

The package also requires observed begin-script execution in the order 1, 2, 3 and captured session time limits 1, 1, 0. **113 offline tests pass. No corrected native run was performed by this worker.** The old native trial remains FAIL; this correction does not establish functional qualification or completed map reset.

Work was confined to branch `codex/20261112-a4-script-readability`, base `5a44b29374883d78d6da9b7f2e027dc615b2ff90`, and the new private directory `/srv/tse-a4-readability-completion-20261112`. The reviewed parent package is `/srv/tse-milestone-a-continuation-evidence-20261112/a4-build015-lowrender-wait-review`, manifest SHA-256 `1c558d9801b474a3fc6b05beef4f630572552e7e017ee87112dc5e637e654129`. All 79 parent files were preserved. Root owns independent review, freeze, native execution and integration. This repository commit contains only the plan and this sanitized report.

## Evidence for the permission defect

The offline reproduction executes the actual old controller staging statements extracted from its AST inside temporary directories. It uses umask 0077 and preexisting init/round-1 files with the observed ownership and mode. A separate read-only Python process runs with effective UID/GID 65534 and no supplementary groups.

| Files | Old actual mode and ownership | Actual UID-65534 read |
| --- | --- | --- |
| `init.ini`, `1_begin.ini`, `1_end.ini` | 0644, 65534:65534 | Exact bytes read successfully |
| `2_begin.ini`, `2_end.ini`, `3_begin.ini`, `3_end.ini` | 0600, 0:0 | EACCES, errno 13, for each file |

The failed native trial `a4-reset015-lowrender-20261112-082738` records `1_begin.ini` at server-log lines 83, 344 and 597, with no round-2/3 begin execution. All 12 archived peer/phase session snapshots decode to time limit 1. The result remains `FAIL` with `ValueError('unexpected round end/order')`; it records all four roles normally closed and exact restoration without errors.

The existing Original Retail DedicatedServer evidence documents the fallback to round 1 when the next begin file is unavailable. Its pinned `DedicatedServer.exe` SHA-256 is `9596f53c260c6fe5f6b7b6666fdf210bcac9952e4eec4b2ee2ee82f37153052d`; the fallback is at VA 0x40288A, with round-end increment at 0x402A0E–0x402A16. Official 1.10 source corroborates the same pattern but is not treated as proof of Retail 1.07 ABI identity.

These observations establish the offline materialization defect and a concrete explanation consistent with the native log. The old trial did not capture a native file-open errno, so the exact native cause and the corrected runtime outcome still require the new controlled run.

Preserved old evidence hashes:

- `result.json`: `f30046aaca81ce199c8d888fb3c332ac9d55f1db76a801d72d74fee5ec3917c2`.
- `server-closed.log`: `fbaf786e777e9245504d50fca9ed6e995399015581209581a6425db397e67b1a`.

## Small, strict correction

`round_script_io.materialize` accepts exactly the seven intended script filenames and validates paths and payloads before writing. It rejects aliases, symlinks, nonregular files and hardlinks. After the existing full transaction snapshot/seal, each file is opened with no symlink following; file-descriptor ownership and mode are set to 65534:65534 and 0644. The original intended script content is unchanged.

The helper reads back the actual file bytes and metadata, then runs a bounded isolated Python child as UID/GID 65534 with no supplementary groups. The child must read exactly those bytes from all seven paths. A root-only parent directory fails this real read check even when the files themselves have correct permission bits. Receipts retain actual bytes, hashes, modes, owners, reader identity and errors. The controller saves the receipt in a `finally` block before any game launch. Existing transaction restoration still restores preexisting bytes and metadata and removes newly created files.

The added observation validator accepts only complete, anchored server execution lines for `Scripts\Dedicated\BotTest\N_begin.ini`. The observed names must form the exact prefix of 1, 2, 3; each phase admission/completion requires the corresponding count. Duplicate 1/1/1, skipped numbers, extra rounds, malformed identifiers and embedded text fail. Partial trailing log lines are not counted. Rejected observations and their offsets remain in the report.

The added time-limit validator checks the existing raw 156-byte session hex against its SHA before decoding signed int32 minutes at offset 0x30. It requires 1, 1, 0 for phases 0, 1, 2. It runs at the paused barrier, matching persistent-peer readiness, all-peer transition readiness, round-end capture and active sampling. These checks consume already captured state; raw evidence is saved before rejection.

## Direct Original evidence for offset 0x30

This offset is not inferred solely from the SDK field list. The pinned Original `EntitiesMP.dll`, SHA-256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`, exports `CPlayer::CheckGameEnd` at RVA 0xEE850. Its bounded disassembly loads the session field at RVA 0xEE86A with bytes `8b4030`, corresponding to `[eax+0x30]`. The verified PE import at IAT 0x6048B2F8 is `CNetworkLibrary::GetSessionProperties`; the original routine skips nonpositive values and compares the timer after multiplying this signed field by the PE's actual 60.0 constant. The SDK `sp_iTimeLimit` layout and `CheckGameEnd` source independently corroborate minutes at this offset.

The existing passive reader and its Engine guards remain unchanged. It captures the 156-byte session block from the guarded session-properties address; the new validator only interprets that captured block. Private `evidence/time-limit-layout-receipt.json`, bounded disassembly and PE export/import receipts preserve the derivation.

## Verification and preserved limits

The complete private suite passed **113 tests in 0.523 seconds**. The first permission regression was RED on actual UID-65534 reads; the new sequence/time tests were RED before their implementation. The final suite includes the original 100 tests, three permission/receipt/restore tests, nine observed-order/time-layout tests, and one additional phase-finish rejection test.

The inherited phase-finish fixture was updated to provide actual valid begin records and the real new validator, replacing its previously incomplete placeholder namespace. No prior assertion was removed. Tests execute actual extracted staging, log-reader and phase-finish controller boundaries. They reject the archived 1/1/1 server log and actual old phase-3 time-limit snapshots, and verify restoration of a preexisting binary round-2 file with different ownership/mode.

Normalized comparison confirms 23 controller functions remain AST-identical; only `main`, `logs_now` and `finish_phase` change. The original reset policy is an exact byte prefix of the extended file. Observer, adapter, backend, transaction, host-budget and reference-policy files remain byte-identical. The 300-second cap, 19-second observer-close cap, 50-second transition cap, final 60 wall/native seconds, lock, resource guards, identity checks, normal closure and exact restoration remain unchanged. Own evidence/unit labels identify this new variant.

Build015 remains pinned to source commit `b6b776ddbc761ee96049e6626edd5af4895cb3af`, build-manifest SHA-256 `a90685f99bd40deb48fc39db57e77a65902df6c5c16077b623a3f069fbd88323`, and candidate DLL SHA-256 `10015f213c05b2faefc312e11a310dae63d64eda1c7173601c6ffd4386a70313`. No build or native test was run for this change. Both review gates and `runtime_performed` remain false in the private handoff package.

## Root continuation

Review the new materializer, actual UID read, receipt persistence, log sequence and time-limit evidence, then verify the final package manifest and normalized delta receipt. Create a separate Root-owned frozen copy with only reviewed gate/path/pin changes. After other native windows end, use the existing exclusive lock and fresh quiescence/resource checks; the invocation remains the fixed `main('redstation',300,1)`.

Before the first game launch, require the persisted seven-file readability receipt. In the bounded native run, require actual observed begin execution 1/2/3, each peer's captured time limits 1/1/0, and every preexisting acceptance guard. Evaluate normal-close, post-close log and exact restoration receipts. Preserve all previous failed trials as FAIL. The new disabled package alone is not evidence of completed map reset, automatic Original rejoin, first processed state or functional qualification.
