# SSAM.AI – M1–M4 CONTINUATION
Updated: 2026-10-26. User explicitly requested shutdown and autonomous M1–M4 development.

## Resume priority
1. Read this file, docs/coordination/M1-M4-GOALS.md and docs/superpowers/plans/2026-10-26-m1-m4-master.md.
2. Verify actual host and active jobs BEFORE native tests: `ps -eo pid,ppid,args | grep -E 'SeriousSam|DedicatedServer|codex'`; `ss -lunp | grep -E '25600|25601'`; `free -h`; `df -h /`.
3. Check `git -C /srv/tse-m1-m4-integration-20261026 status -sb` and `git log -3 --oneline`.
4. Existing user shutdown receipt: /root/ssam-ai-backups/shutdown-20261026-0033/. Never revive public server without a deliberate choice.
5. Review PR71 integrated 90adf81 and PR73 guard source in `origin/pr-73`. PR73 requires dependent AI2/P1 history, not suitable for blind cherry-pick.
6. Next concrete action: design/verify privacy-preserving original config-pinning A/B receipts and private resource/preflight gate. Private guard has `--offline-public-marker` and `--build-manifest`. If healthy, do native Cecil OFF then ON on same P1 DLL, measuring 4 bots in isolated netns only. Test data stays private outside git.
7. Diagnose first divergent shared simulation tick from genuinely paired client/server action/CRC/state; log-only SYNCBAD cannot prove root cause.
8. No feature M2-M4 promotion until M1 native acceptance. Review existing C1–C4 isolated agent branches without modifying their worktrees.

## Known protected jobs/resources
- Existing Codex app-server on Hetzner remains running: DO NOT stop.
- Control plugin remains active; only game binaries stopped.
- Other working clones include /srv/tse-c1-combat-20261026, /srv/tse-c2-nav-20261026, /srv/tse-c3-sync-20261026, /srv/tse-c4-session-20261026 with uncommitted files. DO NOT overwrite.
- Preserve public runtime /srv/tse-experimental-public-20261025/runtime/eight-165601-zof3t2hr, 3.3 GiB.
- Available disk initially ~8.8 GiB, required floor 8.0 GiB; no unsafe deletion.
- Native private runner requirements: host ubuntu-4gb-nbg1-2, root, private /srv/tse-session-qualification-* path, unique 27000–27998 port, :130–:199 display; global /srv/tse-session-qualification.lock; no public process/port; preflight CPU/RAM/disk. Do not use source script without fully reviewing it and trusted build manifest.

## Known candidate findings
- Cecil P1 DLL: 7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf (from PR57; inspect manifest before use).
- PR57 private four-bot failed: 5 SYNCBAD at reported engine tick 99.40..103.40; root cause remains unknown. Read private /srv/tse-session-qualification-cecil-p1-four-20261025/results and C3 report before new tests.
- PR71 comparator is METADATA_ONLY; does not establish live CRC correctness.
- Current tests use `cd /srv/tse-m1-m4-integration-20261026 && python3 -m unittest discover -s tools -p 'test_*.py'`.
- Full release is NOT COMPLETE. No native build or new native tests in this integration worktree yet.

## Rollback and Git
- Branch derives cleanly from origin/main ab0c740. PR71 cherry-pick 90adf81.
- Revert only own integration worktree commits; don't reset main or external worktrees.
- Keep all private logs, raw identifiers, binary retail data out of public GitHub.
- Revalidate originals + backup manifests before any deployment. Production ports 25600/25601 are explicitly offline.

## Pending
Native Cecil OFF/ON controlled run, reliable native sync producer, 1/4/8 acceptance windows, integration of reliability/combat/navigation/sessions, source/build review, final acceptance report and GitHub push.

## Updated checkpoint (2026-10-26)
- Native onebot P1 OFF limited PASS (77.40s); fourbot same DLL OFF/ON results now pinned in docs/reports/2026-10-26-m1-controlled-cecil-native-ab.md.
- Verified 415/415 files in protected manifest SHA match original source + backup tar SHA matches manifest; no files deleted.
- Recheck public ports/generation, other ongoing processes and >8GiB free before next Retail run. Next source task: actual server/client native applied-action/CRC/state producer and first divergent tick; do not assume old SYNCBAD is fixed by one short control.
