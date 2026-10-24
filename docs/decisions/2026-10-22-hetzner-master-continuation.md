# Hetzner-only continuation and qualification boundaries, 22 October 2026

The owner explicitly requested autonomous continuation, commits/pushes and qualified PR integration, with all development/runtime on `ubuntu-4gb-nbg1-2`. Hostname and public interface `91.99.75.33` were verified directly. No Windows/Shadow or connected desktop was used. Existing dirty PR46/49 worktrees remain untouched; a new worktree and unique source branch hold the continuation.

## Actual tool availability and publication

Local shell/Python/g++/Make/systemd and existing Wine/MSVC installations are present. The installed writing-plans/executing-plans, worktree, debugging, TDD, review and verification workflows are used with the owner's explicit continuous-execution instruction. One independent read-only reviewer ran on this same host; no additional runtime writer was delegated.

On this Hetzner executor `rea`, `ghidra`, `analyzeHeadless` and `frida` executables were not found; Python `frida`, `pyghidra` and `ghidra_bridge` modules were not found. This is an availability check, not a backend smoke test or a statement about other devices. No new tool installation or production hook was attempted. The previously proved Retail kick mechanism is unchanged; a reproducing remote client's matching state is still unavailable. Private passive `/proc` mapping reads confirm loaded original Engine/Entities and common Wine CRT hashes; they do not diagnose the remote CRC cause.

Public Git read/fetch works. Shell HTTPS push fails for missing configured credentials. The connected GitHub plugin can create Git trees/commits/refs and PRs: its published tree was compared to the local tested tree byte-for-byte. Local proof histories are retained, and the active isolated branch follows the published equivalent tree. No credential transfer, alternate desktop, force-push or foreign branch rewrite was used.

## Safety corrections and runtime scope

Reviewed changes are a Python operations follow-up to PR49/46, not a GameMP rebuild. Host-wide launch admissions require <=70% measured CPU busy and >=768MiB available RAM plus conservative forecast; the kernel flock spans complete startup. The forecasts (192MiB server,384MiB per grouped client,128MiB display) are admission policy, not memory measurements. Current/peak private memory and available host RAM are recorded separately.

Private game/query pairs receive exactly owned non-loopback IPv4 ingress drops and master-beacon suppression before launch. A lost/unverified rule holds further actions; only exact owned rules are removed after stop. A local namespace packet incremented the precise DROP rule and loopback queries still succeeded; this is not WAN visibility. The failed first comparison-query control is preserved and is not relabeled as passed. Temporary namespace/link objects were removed.

New source must pass its own >=3600s native test and safety/Originalclient gates before integration. Old PR49 hour evidence remains valid only for its old hashes; the failed outer duplicate-stop cleanup is recorded separately. The first new harness attempt failed before controller initialization and was cleaned up; corrected R2 is measuring with frozen source. Public eight bots, originals and rollback are retained.

## Production and capacity decisions

Only a read-only monitor migration is being prepared: immutable four-file bundle, checked pins/unit, saved original unit/source pins, and explicit restoration. The service command remains `monitor`; automatic production recovery is not enabled. A real host reboot,24/7 and second-public-server WAN/listing remain independent open gates.

PR47's eight-individual-client capacity failure remains real. Its existing four-client/color/identity evidence and fresh124 portable tests do not qualify eight normal sessions. Two grouped four-player processes have a different resource profile; the current public8+private8 hour measures that architecture only. A4-vCPU/8-GiB machine is a proposed future test envelope, not qualified capacity or an infrastructure order. No cost or new public instance was incurred.
