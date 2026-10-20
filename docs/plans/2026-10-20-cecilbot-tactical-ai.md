# Alpha-Gaming CecilBot tactical AI – persistent plan and test ledger
Date: 2026-10-20; branch agent/bot-ai-cecil-20261020
Workspace: /srv/tse-bot-ai-20261020; Cecil reference: /srv/tse-cecilbot-reference-20261020 @ 953b477
Protected public runtime: /srv/tse-wine-runtime-20261020/public-eight-20261020-2140
Other active Codex workspace /srv/tse-main-agent-20261019 (PID 60355) intentionally unchanged.

Done:
[x] Audited available BotDriver, BotCore, CecilBot source and running service.
[x] Client-only tactical AI: target stickiness, health weighting, weapon ranges, strafing, low-HP retreat.
[x] Opt-in BotDriver integration patch; applies to isolated copy. Default disabled.
[x] Strict Cecil BNMV-v6 importer; nine maps converted to directional waypoints.
[x] Graph capacity to 512 nodes/16 arcs and complete map import regression.
[x] 8 portable C++ test executables PASS; 5 Python format tests PASS.
[x] New C++ tactical test warnings-as-errors, ASan and UBSan PASS.

Next required evidence:
[ ] New isolated Windows Retail GameMP compilation and DLL SHA256.
[ ] One-bot native movement sign/timer/action validation and control comparison.
[ ] Wine one-bot and eight-bot native gameplay tests isolated from live server.
[ ] Verified vanilla join, 60-minute sync/CRC + CPU/RAM and graceful exit checks.
[ ] Door locks, jump/crouch flags and drop/pit navigation policy before enabling map routes.
[ ] Backup/rollback plus explicit release gate before any public deployment.

Limits: pure C++ and topology tests do not establish native gameplay correctness.
All nine map conversions are GPL-2.0-derived, world hash must match target map.
Never confuse this branch with the historically qualified public GameMP binary.