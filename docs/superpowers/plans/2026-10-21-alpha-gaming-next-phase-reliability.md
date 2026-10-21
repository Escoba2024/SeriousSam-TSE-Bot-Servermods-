# Alpha-Gaming TSE 1.07 – Next Phase Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the qualified eight-bot public fleet safe, recover disk headroom, qualify guarded unattended restarts, then validate a second server instance without regressing native Retail 1.07.

**Architecture:** Existing Build04 + overlays remain untouched. Operational tooling must be owner/PID/start-time/CWD/cgroup aware and fail closed on foreign players/processes. No simultaneous publication or rollout before isolated gates.

**Tech Stack:** Ubuntu 24.x, Wine 9, original Retail 1.07, Python 3, systemd if qualified, 2 vCPU / 3.8 GiB Hetzner.

**Spec:** `docs/reports/2026-10-21-human-cpu-final.md`, `docs/reports/2026-10-21-hetzner-operations.md`, `docs/reports/2026-10-21-hetzner-capacity.md`, `AGENTS.md`.

## Global Constraints
- Hetzner only; no Shadow reliance or new paid resources.
- Public `91.99.75.33:25600` / GameSpy UDP `25601` stays online, currently 8/16, Build04 SHA256 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
- Original game files and protected 61DC reference DLL untouched; private logs/binaries never committed.
- Do not disturb active players, the running public fleet, shared runtime or another agent's worktree.
- Never assume a reboot service is qualified just because a service file exists; test isolated lifecycle and fail-closed reconciliation first.
- Do not infer 16-, 24/7-, multi-map-, or GPU-player-PC acceptance from eight-bot Wine tests.
- Each stage has explicit recovery and fresh evidence. No unattended destructive cleanup; preserve all protected backups and raw evidence until independently verified.

## Review Focus
1. PID reuse: ownership must include Linux start ticks and working directory.
2. Stale `CURRENT_PUBLIC.json`: reconcile to live PIDs, ports, query, DLL SHA rather than trusting age or filename.
3. Wine/overlay replay: do not unmount mounts belonging to an active process or another owner.
4. Saturation and cgroup throttling under additional server instances: require real independent measurement.
5. Disk cleanup: no deletion based on filename/date alone; active overlay dependencies and backup retention are mandatory.

## Baseline – independent read-only check, 2026-10-21 ca. 14:06–14:09 UTC
- PR #45 merged to `main` at `fdfc46eae8ba5557af427c1b36fc91b0d95aec37`.
- Live Linux PIDs: original DedicatedServer `124818`, BotA `124882`, BotB `124950`, all attached to `/srv/tse-integration-public-20261021/eight-115115-z44oq5ua`; public UDP 25600/25601 listen.
- Two current native GameSpy queries returned 8/16, eight expected bot names, map Yodeller and no reported parser problems. Query alone does not prove continuous humanlike combat; 60-minute proof is in the merged report.
- Host: 2 vCPU, 3819 MiB RAM (approx. 2472 MiB available), 38 GB root, 34 GB used, 1.8 GB free, 96% use.
- `/srv/tse-wine-runtime-20261020` takes about 20 GB, including historical full private Wine/game copies; `/srv/tse-msvc-20261021` 2.9 GB; historical `yodeller-20261020-0925/bot/SeriousSam.log` about 0.5 GiB. These are inventory facts, not permission to delete.
- No `tse`/Wine/SeriousSam systemd service listed. A reboot-safe automated restart is **not** established.
- No active Codex/lmarena or measured benchmark controller process found in the bounded process scan.
- Current public cgroup CPU `nr_throttled=0` at snapshot, not a long-term saturation guarantee.

## Task 1 – P0: Disk safety, inventory, retention and recovery budget
**Files:** New `docs/reports/2026-10-21-hetzner-disk-inventory.md`, later optional `tools/operations/...` under own worktree only.
**Interfaces:** Existing runtime result/manifest, `CURRENT_PUBLIC.json`, `/proc/<pid>`, `findmnt`, `df`.
- [x] Observe free bytes/inodes and identify largest trees read-only.
- [ ] Map all live overlay lower/upper/work dependencies, mounted source paths and PID/CWD references. Explicitly exempt current production tree, protected 61DC files, public rollback tar and master-DNS backup.
- [ ] Identify inactive copies with provenance and verified alternative backup/checksums; quantify recoverable bytes without mutations.
- [ ] Rehearse archiving/checksum validation and exact restore on a small disposable test fixture.
- [ ] Only after independent retention/restore validation, execute a bounded candidate cleanup; never recursively erase a shared parent or live mount.
- [ ] After cleanup, require `df -B1 /` free >= 8 GiB, protected hash invariant, live 8/16 query, correct PID/start/CWD, and successful read-only telemetry/sync check. If target unreachable without unsafe cleanup, mark BLOCKED_NEEDS_STORAGE rather than improvising.

## Task 2 – P0: Restart and monitoring safeguards (new subsystem; separate design approval before changing runtime)
**Files:** Own `tools/operations/` module/tests and `docs/reports/` smoke evidence; no writes to integrated production tool in this stage.
**Interfaces:** Consume existing `qualify_integrated_wine.py`, `stop_integrated_public_wine.py`, `CURRENT_PUBLIC.json` and immutable manifest without bypassing gates.
- [ ] Design idempotent read-only live-health assessment: expected port, exactly owned fleet, DLL SHA, GameSpy eight bot names, fresh telemetric ticks/actions, no SYNCBAD/disconnects and disk/cgroup alerts.
- [ ] TDD (RED/GREEN): fixtures for absent/stale PID, PID reuse, wrong CWD, port owned by somebody else, invalid manifest, disk threshold, extra human player, stale GameSpy query and missing master DNS.
- [ ] Isolated supervisor/startup dry-run using own port and overlay; preserve existing public server and all humans. Compare before/after lower-file hashes.
- [ ] Test induced self-owned process failures and recovery, no double-start, boot simulation and safe stop with own PID.
- [ ] Only after fresh clean acceptance evaluate systemd installation/activation and reversible rollback. No production reboot just to demonstrate a unit works.
- [ ] Require 60 minutes active bots, native browser/WAN validation, real error handling, boot acceptance (only when safely schedulable), plus operational alert/rollback documentation.

## Task 3 – P1: Capacity 16 bots on TWO servers after Task 1
**Files:** Isolated scale worktree/runbook and capacity measurements; no edits to Build04.
- [ ] Confirm CPU >30% reserve, RAM, disk >8 GiB free, available unique ports and exclusive own runtime/cgroups.
- [ ] Two isolated instances with eight bots each; 16-slot server limits preserved, leaving human slots. No sixteen-bot fill of one server.
- [ ] Prove native action frequency, real movement/fire, CRC and SYNC for 1/4/8 per instance, representative human joins, 600s smoke followed by 3600s stability.
- [ ] Three valid CPU/cgroup samples with no meaningful throttling/steal; calculate conservative upper bound and record 95th percentile (if available), RSS/PSS and write volume.
- [ ] Rollback own test-only runtime; do not publish both servers until thresholds, visibility and restore gates are met. If limits fail, stay at eight bots.

## Task 4 – P2: Human-AI gameplay quality across maps, only after reliable ops
- [ ] Observe controlled Rookie/Casual/Average/Veteran/Expert behavior versus human-like metrics: aim error, target reacquisition, reactions, stuck time, death/respawn and actual map navigation.
- [ ] Separate present 555 deterministic unit checks from real skill ranking; gather objective gameplay samples on Yodeller plus other supported maps.
- [ ] Propose minimal navigation/anti-stuck improvement; any new GameMP.dll receives its own MSVC build, checksum, Retail sync/gameplay acceptance and rollback.

## Handoff and Current State
**Completed:** Current merge/live read-only cross-check and high-level storage/process inventories.
**Next:** Task 1 live-mount/dependency/backup inventory and small disposable restore fixture. No deletion requested or performed at plan creation.
**Blocker:** Free space 1.8 GiB (96% used) means additional full-copy scale tests are not safe yet.
**Evidence:** `docs/reports/2026-10-21-human-cpu-final.md`, `docs/reports/2026-10-21-hetzner-operations.md`, actual GameSpy query and RDC read-only inventory on 21.10.
