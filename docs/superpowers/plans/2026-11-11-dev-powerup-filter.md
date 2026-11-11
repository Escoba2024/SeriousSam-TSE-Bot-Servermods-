# Development power-up filter implementation plan

> **For agentic workers:** Use superpowers:executing-plans in this session.

**Goal:** Remove only Invisibility (type 0) and Serious Damage (type 2) on the Development Red Station server.

**Architecture:** A default-off GameMP server hook removes selected existing entities after authoritative world creation, before players join. The original 1.07 Engine and Entities remain unchanged; existing Cecil048 clients and map/NAV bytes remain unchanged. The user explicitly approved preparing and isolated-testing this Dev exception on 11 November.

**Tech Stack:** Existing Retail-1.07 SDK headers, MSVC x86 under Wine, portable C++ policy test, private Wine network namespace.

**Spec:** User's Dev-only request, approved servermod exception, and docs/decisions/2026-11-11-development-names-and-powerups.md.

## Global constraints

Five production servers, saved rollout, original qualified DLL and live Cecil048 clients are protected. No sync/CRC bypass. No removal of external players. No public Retail assets/raw logs. Wine tests are limited evidence, not native Windows or duration qualification.

## Review focus

Default disabled; type 1/3/4/unknown retained; demos and clients do not mutate; deletion iteration must remain valid; a late Retail join and subsequent server restart must preserve the filtered snapshot.

### Task 1: Server candidate

- [ ] Add a portable policy regression for disabled/server/client/demo/all known and unknown types; observe RED.
- [ ] Add policy header and guarded NewGame hook with before/after census. Destroy one entity after releasing the container iterator, then rescan.
- [ ] Run policy and existing portable suites, commit source, build into a new private directory with actual source hashes; inspect imports against original Entities.

### Task 2: Isolated Retail verification

- [ ] Copy private runtimes/prefixes to a new root, preflight identities/files/resources/ports, namespace isolation and lock.
- [ ] Observe default-off census, then enabled census (0/2 absent, other types preserved).
- [ ] Join unchanged Cecil048 and original Retail, verify queries, actual modules and logs with active bot combat; normal client/server cleanup.

### Task 3: Dev rollout if verification succeeds

- [ ] Fresh all-six inventory and exclusive fleet/runtime locks; no external Dev player removal.
- [ ] Preserve original server DLL/config in a new private rollback delta; stop only Dev normally; install tested server candidate and explicit toggle.
- [ ] Verify eight original Cecil048 profiles/names, filtered census and limited live observation; production identity/pins unchanged. Save evidence and report exact limits.
