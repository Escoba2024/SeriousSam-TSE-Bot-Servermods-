# Spawn-zero Dev sync failure — read-only diagnosis

Status: root cause unproven. No runtime edits, hooks or process starts/stops were
performed by this analysis. The rollout owner is separately restoring Dev's prior
configuration. No runtime rollback success is asserted here.

## Observed evidence

Private logs were parsed without publishing addresses or player identities:

| Log window | Sync ticks represented | SYNCBAD | Confirmed bad-sync disconnects |
| --- | --- | ---: | ---: |
| Prior Dev session | 1.00–1759.54 | 1 | 0 |
| Spawn-zero session | 1.00–708.90 | 36 | 3 |

Baseline server-log SHA256:
`4b89a3e3b566459d76e3f722fbcc550dc70b12cba65e508d5a1fc4bfc7c02748`.
Failure server-log SHA256:
`8ff6128edd3dfeecf4a200e8b71d2feb2bed3731916b26423d5e7c054a6a6194`.
The windows have different participants/join timing and durations; they are not a
matched causal experiment.

Two external peers account for all failure-log BAD entries: peer A has 25 BAD and
two disconnects, peer B has 11 BAD and one disconnect. The preserved local botA
and botB logs contain no bad-sync disconnect. Peer A first reports BAD at tick
91.40/sequence 1839 and is OK at 92.40. The first continuous kick sequence ends
at tick 128.40. Both peers later report BAD together at 247.41/sequence 4961,
recover at 248.41, and finally share a continuous failure from tick 260.66/
sequence 5226 through tick 270.11/sequence 5415. Both are then disconnected.
This shared sequence/tick pattern warrants comparing simulated state; it does
not identify the differing field or prove a particular network/physics cause.
The original 17 October report remains applicable: the counter/kick mechanism is
known, but a BAD record alone does not expose the differing CRC inputs.

The baseline and failed server logs both report the same enabled power-up census:
one invisibility and one serious-damage entity before, two removed, neither after.
The failed session additionally has the spawn-zero startup witness. Equal census
counts do not prove equal entity state at subsequent client joins.

## Source trace and what it does not establish

- Cecil048 `Sources/Game/SessionProperties.cpp:223` copies the shell setting to
  `sp.sp_tmSpawnInvulnerability` when constructing multiplayer session properties.
- `overlay/Game.cpp:1150` passes the session pointer to `StartPeerToPeer_t`.
- `overlay/Game.cpp:1025` skips persistent-symbol loading on Dedicated; therefore a
  zero in PersistentSymbols.ini alone cannot override the source default of 3.
- Engine107 `Engine/Network/Network.h:20` defines a 2048-byte session-property
  buffer; its networking functions consume a pointer to that block.
- A portable layout probe using fixed 32-bit INDEX/BOOL/ULONG and float confirms
  offset 132 (0x84), structure size 156 and universal buffer size 2048 in both
  Cecil048's built SessionProperties.h and the pinned Engine107/GameV header.
  This is source-layout evidence, not a new Retail binary/serialization proof.
- The existing servermod manifest pins SessionProperties.cpp/header to the same
  source hashes as the client build. A1 changes configuration, not those binaries.
- The SDK/reference Player.es damage path at 3037 reads
  `GetSP()->sp_tmSpawnInvulnerability`; the spawn timestamp is assigned at 5306.
  It does not use the client-local shell `gam_tmSpawnInvulnerability` symbol.
  This reference is not asserted to be the original Retail Entities binary.

Consequently, changing each client's local `gam_` symbol is not an evidenced fix.
The actual session block received by each client must be measured. The available
headers do not reveal the complete Retail Engine transport or CRC implementation;
no serialization failure has been demonstrated.

## Existing selective power-up servermod

`tools/build_dev_powerup_gamemp.py` injects `DevFilterPowerups(dem_bPlay)` only in
CGame::NewGame, after StartPeerToPeer and before SetupLocalPlayers. The filter
requires authoritative server/non-demo mode and destroys only types 0 and 2.
It never reads spawn invulnerability and retains type 1 (invulnerability).
The deployed servermod DLL is `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0`;
the Cecil048 client is `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`.

The previous isolated original-client test was 120 seconds with one bot. The
separate eight-bot test was 180 seconds without the original client. Neither
establishes an active multi-client spawn-zero control beyond the newly observed
270-second failure point. The filter may be independent, interacting, or unrelated;
the current evidence does not decide. A matching before/after item count must not
be promoted to proof that its late-join snapshot/determinism is correct.

## Next discriminating isolated test

Use new private runtime/evidence paths, exclusive own-resource locks and an
isolated network namespace. The earlier private
`test-dev-powerups-r2-20261111.py` and `native048_safe.py` provide lifecycle examples,
but do not import/run the old harness unchanged: it executes at module scope and
owns fixed paths, services and display. Do not instrument external visitors.

1. First run the existing servermod with one controlled original 1.07 client and
   one unchanged Cecil048 opponent. Use the same Red Station files and input
   procedure twice, server spawn value 3 then 0. Record original component hashes,
   effective shell value, actual server and client session-field bytes at join and
   after respawn, and ordinary damage/death events. Source-predicted field offset
   is 0x84; obtain the actual session pointer through a verified native path rather
   than assuming an engine-object offset. Compare the known typed 156-byte region,
   not unidentified padding as semantic data.
2. Repeatedly apply ordinary valid hits immediately after respawn and after the
   former three-second protection interval. Observe at least beyond 270 seconds
   with comparable combat, preserving exact first BAD/OK tick/sequence and CRC
   evidence. Include an uninstrumented control to distinguish probe effects.
3. If spawn-zero reproduces, repeat 3/0 with original server GameMP (no filter),
   keeping the same controlled client/opponent and gameplay procedure. This forms
   a 2×2 server-binary/spawn-value test; a further servermod filter-off condition
   distinguishes the filter operation from unrelated servermod code.

Interpretation: unequal session spawn fields supports a configuration/transport/
layout investigation. Equal fields with divergence first at an early post-spawn
hit points to damage/action/state comparison at that first tick. Failure only with
servermod+zero supports an interaction investigation; failure with original server
+zero requires checking the unmodified simulation and client/action conditions.
A non-reproduction in these short isolated tests does not clear the public WAN
case. No kick-threshold suppression, live binary patches or speculative fixes.
