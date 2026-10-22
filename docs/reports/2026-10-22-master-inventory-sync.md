# Hetzner inventory and external sync investigation, 22 October 2026

Verified directly on `ubuntu-4gb-nbg1-2`, public IP `91.99.75.33`, starting 21:39 UTC. This continues PR46/49; it does not repeat their earlier implementation or alter the public fleet.

## Repository and process provenance

Main refreshed with a fast-forward to `fdfc46eae8ba5557af427c1b36fc91b0d95aec37` (PR45 merged). PR46 (`d6d2911`), PR47 (`b75f14d`) and PR49 (`5b0157f`, targeting PR46) remain draft; coordination PR48 (`57d0411`) is open. Review worktree `/srv/tse-master-20261022` is based on the published PR49 head. Existing reliability worktree contains four dirty artifacts, QA worktree an uncommitted native-result plan update: both preserved. The Codex app-server process is not evidence of an additional active implementation agent. A production read-only Python monitor remains active; no other native test controller or private game fleet was running in the process inventory.

Public processes remain Dedicated PID 124818, BotA 124882, BotB 124950, with recorded start ticks 28905984/28906785/28907286. A fresh connected GameSpy query at 21:40:47 UTC reports Retail1.07, Yodeller, 8/16, eight expected bots and no human at that instant. The old monitor reports BLOCKED: QUERY_UNCERTAIN, EXTERNAL_CLIENT_SYNC, LOG_LIMIT_MAINTENANCE_HOLD; its own SYNCBAD0/external105 are historical totals. Query freshness and monitor verdict must be evaluated separately.

At inventory: host 3819 MiB total, approximately 2274 MiB available, no swap; root approximately 15 GB free. These are snapshots, not a capacity qualification. No public restart, new DLL, process kill, service migration or second public server was performed.

## Backup and original-file verification

At 21:42 UTC all twelve active per-role binary pins match: original Dedicated/SeriousSam, Engine, Entities and server GameMP; bot GameMP is qualified Build04 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`. All 415 retained old-runtime files match the rollback manifest. All 415 archive member contents also match. Rollback tar SHA256 remains `d7b3650d55a21fc88614d5b969e126ac1cfcc52585262a1ef139eb0be1632b7d`. Production monitor's four `/etc` source pins pass. Additionally captured 455 configuration/profile/script files to a new private tar, plus process manifest and monitor-pin snapshot. Private data remains under `/srv/tse-master-evidence-20261022`, outside Git; no raw logs, GUIDs, player names or game payloads are published.

## P0: external SYNCBAD evidence

Streamed a fixed 17,210,980-byte prefix of the current server log, SHA256 `ad24e2aeadb13acb6618ebbc510f33c86a9fcb56117989f9c16491a9866d80c4`. This snapshot contains 105 external SYNCBAD, 0 owned SYNCBAD and nine explicit `Too many bad syncs` disconnect instructions. Five distinct external endpoint labels have bad checks; endpoint counts do not identify unique people. Other external endpoint labels have successful checks. Both successful and failed checks occur for some affected endpoint labels across sessions.

The first available bad check is Sequence290425/Tick14482.64, bad1; the latest in this captured prefix is Sequence2244462/Tick109968.69, bad10. These are simulation ticks, not independently timestamped wall-clock times. The log has no per-field server/client CRC dump, original remote binary hash, matched input trace, per-peer packet-loss capture or remote clock evidence. A counter starting at bad1 locates the first *reported mismatch* in a streak; it does not identify the first divergent simulation action.

What is narrowed: the unchanged Retail server accepts owned bot state while some external sessions diverge; external clients also sometimes synchronize successfully. This does not establish external-player fault, prove a Wine/NullRender defect, or establish latency/loss as the CRC cause. Packet delay and a mismatching checksum are separate observations. Existing original-client Build04 acceptance is useful control evidence for its exact environment, not proof about these remote sessions.

No SYNC check, threshold or production logging option was changed. No private client was joined to the live public party for diagnosis. Historical105 must be separated from subsequent appended bytes in follow-up monitoring. Root cause remains OPEN: an authorized reproducing remote Originalclient with its exact hashes and matched server/client state at the same tick is required to discriminate protocol/ABI/simulation/input causes. No such remote process is under this Hetzner-only session's control. Safe isolated reliability work can continue independently.

## Existing PR49 native result: recovered, not rerun

Private R2 qualifier finished at 10:27 UTC: 3600.00389663s elapsed, 648 samples, all eight active at median20Hz, zero owned sync errors and new throttles. Source hashes match the published PR49 files: supervisor `8c6c863aab2fc198012c9b39e4d65c917d3442eb555424164ca8c2c8b6f86893`, health `8752560b8aa49b6eb12d99804072f13c6dd8558a67db9c597e0da26bb8ce0c8f`. Double start, client/server recovery, adoption and boot-overlay replay passed. Host mean60.70%, P9564.82%; public identities unchanged. Boot replay is not a real reboot.

The outer orchestrator subsequently reported cleanup_error: a redundant second stop called `wineserver -w` after the prefix overlays were already unmounted. Independent post-run evidence recorded no own mounts, PIDs, ports26860/26861, display127 or active cgroup processes. Therefore the isolated qualifier hour is PASS for those exact files; the complete outer orchestration is FAIL and stop idempotence requires correction and fresh validation. PR46/49 integration and production recovery remain gated.
