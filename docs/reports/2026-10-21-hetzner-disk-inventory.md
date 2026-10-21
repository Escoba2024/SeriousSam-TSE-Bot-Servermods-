# Hetzner disk retention and verified recovery — 2026-10-21

## Result
PASS at 2026-10-21T16:41:10.749042+00:00: 10387 individually SHA256-matched duplicate payload files removed from four inactive historical test copies. 14369226752 bytes reclaimed (13.382 GiB); free space increased from 1806262272 to 16175489024 bytes (15.065 GiB). No shared parent, game Bin directory, log, profile, configuration, screenshot, source, raw measurement or protected backup deleted.

## Dependency inventory and exclusions
Only live overlays were the six production mounts under `eight-115115-z44oq5ua`. All lower directories point into `public-eight-20261020-2140`; BotB prefix deliberately uses the retained prefix-botA lower. All upper/work directories remain under the production run. Actual /proc CWD, executable, maps, command line and open FD references were scanned before reclamation; no candidate tree was mounted or referenced. No Codex agent or benchmark controller was active. RDC node and unrelated GMX/nginx/SSH/system services were identified and left alone. Existing integration/review/main worktrees were inventoried and preserved; own execution worktree is `/srv/tse-reliability-20261021`, branch `agent/ops/20261021-reliability-execution`, based on PR46 `48151a8a1823a72f5b8233eab2345cc0def2259b`.

Protected: complete active production root/layers, complete `public-eight` lower template, `install/vanilla`, immutable 61DC DLL, Build04 output/manifest, protected release sources, public rollback tar/manifest/restore verification, hosts.before and legacy-master metadata, toolchain and all worktrees. No originals were modified to reclaim space; no hard links or aliases were introduced.

## Bounded duplicate sets
| Historical copy | Matched allocated bytes |
|---|---:|
| onebot-20261020-0905 | 3316015104 |
| fortress-20261020-0920 | 3316023296 |
| yodeller-20261020-0925 | 3316015104 |
| scale-staging-20261020 | 4421353472 |

Files qualified by SHA256 against still-retained regular files in `install/vanilla` or `public-eight`. Filename/date/inactivity alone never authorized removal. Every candidate's inode/device/size/mtime/content was revalidated immediately before unlink. References were independently rehashed; dependencies re-scanned before mutations. Symlinks were never followed during traversal; Wine z: cannot escape into the host filesystem. Historical run directories remain with all their distinct evidence and every game Bin file, but are now archival partial copies and MUST be restored before reuse.

## Restore and protected invariants
Private compressed manifest: `/srv/tse-reliability-evidence-20261021/restore-manifest.json.gz`, SHA256 `2a6845e992131c0dc86a38a7d40adeb0ca76f4afa87fbce85fa5688d225385b6`. It records each exact destination, retained reference, content SHA, mode, UID/GID and nanosecond mtime. The alternative reference pool is retained in full; the manifest is a local deduplicated recovery representation, not an off-host disaster backup.

Before deletion: independently copied/restored 13 files totaling 272250658 bytes, verified exact SHA and nanosecond mtime, tested compressed-manifest round-trip. Only that disposable fixture was then removed. The protected rollback tar SHA `d7b3650d55a21fc88614d5b969e126ac1cfcc52585262a1ef139eb0be1632b7d` and all 415 protected source entries were checked before AND after reclamation. Immutable reference DLL remained 61DC. Whole retained source files remain available; no protected backup was consumed or replaced.

Restoration must target one archived historical tree at a time into missing paths only, verify reference SHA before copy, restore metadata and verify destination SHA, while retaining >=8 GiB free. Never restore across live mounts or over existing files. Total payload restoration would consume the reclaimed budget; full simultaneous restoration is not an operational requirement.

## Fresh production verification
After cleanup: original server PID124818/start28905984 and clients PID124882/start28906785, PID124950/start28907286 still match CWD and cgroup; original server binary and both Build04 DLL hashes verified. Native GameSpy 1.07 returned the complete eight-bot roster, first 8/16 and later 9/16 after a real human joined. Human presence is allowed, never removed to force an exact-eight assertion. Both bot clients retained fresh 20-Hz/action telemetry, zero render draws, no owned-client SYNCBAD. Private `post-disk-health.json` records the live snapshot.

New operational finding: server history contained 21 SYNCBAD entries and two native bad-sync kicks for an external client, with zero entries/disconnects for the owned bots. Raw peer identity and logs remain private. This is an alert and a human-client compatibility investigation, not permission to disable the original kick threshold or restart production. Previous one-hour/public-smoke zero-error evidence remains scoped to its earlier windows.
