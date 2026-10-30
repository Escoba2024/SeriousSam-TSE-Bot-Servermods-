# M2 native combat measurement — 30 October 2026

## Decision and scope

Continue PR81's existing policy and guarded private Retail1.07/Wine harness on
Hetzner. M1's eight-bot/120-minute campaign remains deferred. Native sessions
are serial, at most two bots and300 measured seconds per case, with the existing
8GiB/CPU/RAM/sync/original-file/ownership gates unchanged. Original game/server
binaries and the qualified61DC DLL remain protected; only owned test copies use
ordinary finite-ammo session settings.

Use normal keyboard/button input exclusively on the owned original opponent,
bound to PID/start time/UID/CWD/netns/cgroup, display and unique window. Revalidate
fresh runtime/resource receipts before every dispatch. Verify later replicated
positions, health and counters separately: a successful dispatch is not an
engine-effect, shot or hit proof. Private steering scripts are test actors, not
another production Bot AI. Stop steering on stale evidence or repeated blocked
movement; retain failed attempts. No memory writes, teleports, inventory cheats,
server hooks or resource-guard bypasses.

## Additional observation

Existing `BotWeapon.ammo` measures the Colt magazine even when another weapon
is selected. It cannot prove rocket/shell/etc. exhaustion. Add a single bounded
`BotAmmo` diagnostic under the existing debug/local-player/null-pointer/world-lock
and periodic-log guards. Read fields already used by the native ammo adapter;
explicit integer varargs, no writes or policy/action/packet changes. Extract the
actual patched statement for a compiling regression and sanitizer validation.
This creates a new unqualified candidate: build03 DLL
`a62a19e75251f69207966bb8965c019d8c7e76458099e6eb86bfddc4cb1ee5dd`.
Build02's `860ae6d7…` gameplay evidence remains attached to build02.

No new unknown Retail binary/ABI behavior requires REA/Ghidra/Frida for these
source-level diagnostic reads. No Ghidra service, GUI8080 entry or runtime hook
is invoked. Successful MSVC build, tool smoke, portable policy tests, Wine native
gameplay, original-client compatibility, long-term sync and public release remain
distinct evidence levels. New errors require the tool-policy routing rules.

## Evidence interpretation

- Colt/other reserve decreases are sampled observations, not exact shot counts.
  Death/reset/pickup and different local slots must be separated before attributing
  exhaustion. A zero pool alone does not establish usable-weapon fallback.
- Projectile witnesses deduplicate engine entity IDs. Type0 is `PRT_ROCKET` in
  this build's pinned Engine107 header; no assumption from Engine1.10.
- Same-entity health loss plus attributable frag/death/roster/session continuity
  supports scoped combat. Concurrent rockets prevent attributing every observed
  health change specifically to shotgun pellets.
- Five-tier/six-persona axes are a native matrix, not30 native Cartesian cases.
  All30 generated configurations and paired policy distinctions are tested offline.
- Sparse true residual aim errors do not measure the policy's perceived error or
  seven consecutive valid trigger ticks. Tier1's observed plateau is a calibration
  limitation until a reproducing cause supports a code change.

Raw licensed data, identities, profiles, screenshots, controllers and logs stay
private. Versioned reports contain sanitized summaries, source/build/DLL hashes,
commands and explicit open qualification gates. No runtime or release permission
is inferred from this measurement decision.
