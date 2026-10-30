# M2 native combat QA continuation

The full M2 mandate remains unchanged. The previous goal turn made progress:
reviewed implementation/build/tests and draft PR81 are authoritative. Full native
combat acceptance is still unproven; this continuation closes that evidence gap.

Reinspection of retained native logs shows more than the former input summary:
the 240s RedStation run sampled Colt magazine values0..6, original actor health
100→70→40→10→-20 and one bot's replicated kill counter0→1. The original actor's
pose also moved after its PID-bound W input. The outer143 quarantine remains;
these observations alone do not accept that run or establish all weapon behavior.

## Approach

Prefer normal unmodified-client controls and existing original maps before adding
GameMP probes or authoring custom levels. Use one M2 bot and one own original
Retail test opponent on the bundled Little Trouble deathmatch map; finite ammo.
Bind the existing Turn/Look actions to arrow keys only in the private original
opponent's copied control file. Keep canonical engine/server/binaries untouched.
Normal PID/window-bound X11 input may position, aim and fire the test opponent;
it must not modify game memory or grant the M2 policy hidden information.

The alternative of modifying replicated world/inventory state from a bot client
is rejected: it would not be an authoritative server-side scenario and risks
invalid sync evidence. No engine hooks, teleports, assumed1.10 APIs, public action,
M3 implementation or guard changes. Existing native serialization, identity,
original-hash, network namespace and resource safeguards remain mandatory.

## Evidence needed

Native inputs accepted by the engine (poses/rotation/fire/clip) must be checked
separately from X11 dispatch. Link health loss, native kill counters and subsequent
respawn within the private actor roster. Observe actual weapon/current/wanted/
finite-ammo state, and separate sampled evidence/lower bounds from exact shot
counts. Retain failures and unknown causes; no completion by logging alone.
A new test helper must refuse stale/foreign process/window/runtime targets.

One native campaign at a time, max one/two bots, each <=300s, CPU/RAM/disk and
original guards unchanged. No compiler or broad offline suite during campaigns.
All raw native data/control files/screenshots remain private. Publish only source,
reproducible checks and sanitized aggregate evidence in the existing draft.
