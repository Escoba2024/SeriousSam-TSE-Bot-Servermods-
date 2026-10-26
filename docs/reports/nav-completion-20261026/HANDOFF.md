# Navigation and item completion handoff

Status: OFFLINE_CANDIDATE; NOT_TESTED_RETAIL. No BotDriver, binary, public fleet, port or foreign worktree was modified. Parent owns native integration and qualification.

## Provenance and design

Base main ab0c7400353a108f8461bb82280c539fdfe81499. Imported the uncommitted C2 candidate read-only from /srv/tse-c2-nav-20261026; import-inventory.json records every imported source SHA256 before modifications. That source was not assumed accepted. Only source files were copied; generated .build, executables and pycache were excluded.

pins.json fixes exact commits and tree IDs: PR54 3f2ba8dbf0df341b35cb157efd152fa93d1d7fd7 navigation; PR55 72d464ff501d90ec4b69c2a131a50a06323e1909 item utility; PR69 d0c181c638c6e82fd0187c3a29ad5fc8bf6d1869 bridge; botcore baseline ab0c740. These three research objects were fetched from the local /srv/tse-main-agent-20261019 Git store into the own repository. prepare.py verifies trees, extracts source-only copies into this candidate's ignored .build/upstream, applies integration.patch without fuzz, removes fallback mirror headers, and records every generated source SHA256 in .build/manifest.json.

Read AGENTS.md/tool policy, PR72 QA03/04/07 and integration handoff at 7df2867e1ad7a6101b95a54031d7583265977f72, and PR54/55/69 native limitations. Research flags and caller declarations are evidence contracts, not native proof.

## Changes

- QA03: Bridge enrichment and NavGraphSink anchor with explicit NearestNode3D. A 2m vertical tolerance prevents snapping through ceilings; waypoint advancement also checks height. Final arrival remains actual 3D distance. Same-ID goal changes in height reanchor; live item movement invalidates the route epoch. Controller patrol uses the same sink rather than the upstream duplicated patrol router.
- QA04: Legal finite health and armor above normal top no longer invalidate an entire snapshot. Explicit per-item pickup_limit supports caller-verified super health/armor limits; zero means normal top. No item classification is inferred from amount/appearance.
- QA04: Knife, Colt, dual Colt, chainsaw have no reserve requirement. Double shotgun requires at least two shells. Shell slots4/5 and bullet slots6/7 share canonical storage. SetAmmo updates aliases; readers use canonical slots. SelfState.infinite_ammo keeps owned weapons usable and removes ammo-resupply need. Starvation now means no usable ranged weapon, rather than any depleted backup.
- QA07: Uncached/unprobed/partial-path items are pending and unavailable to utility selection until a complete graph path is certified. They cannot win with optimistic air distance. Found routes restore eligibility; cached known paths avoid starving later candidates. Unknown is not cached as permanently unreachable.
- Retained reviewed original C2 fixes: bounded routes return source-anchored prefixes, zero search caps expand nothing, graph-epoch replacement reanchors goals, and recovery clears stale jump hints.

Updated research fixtures document actual rule changes: ammo/cooldown tests use finite-ammo Tommyguns rather than impossible empty Colt reserves; the island fixture sets the actual item's Y to6, matching its graph node. S05 finite-ammo pickup has sufficient synthetic yield to preserve the test's damage-abort purpose. No production behavior was altered to satisfy obsolete assertions.

## Exact integration seam for parent

Candidate is header-only: poc/candidates/nav-master-20261026/nav_item_controller.h. Use generated real headers from .build/upstream/poc; include bridge include path and NAV_ITEM_BRIDGE_REQUIRE_UPSTREAM. Configure one persistent c2nav::Controller per bot with BridgeProfileBundle and Options. Options default disabled.

Produce combat exactly once in parent, populate Frame.combat, and preserve caller-owned recovery. Set combat_movement_reserved for hold/escape/travel; compatible C1 commands also expose escape/travel automatically. Only copy movement/yaw from Result.intent if override_movement is true. Combat owns weapon/fire; bridge may inhibit firing while navigating/recovering. jump_hint is always false in this unqualified adapter.

Frame.world and Frame.items must describe the same tick, health, normal maximum and 3D origin. Contract requires exact map and waypoint SHA256, nonzero world_instance and graph_epoch, snapshot_tick, anchors_3d_verified, and item_entities_verified for item goals. Stable item IDs are scoped to a world instance. Every topology/coordinate/ID-index mutation requires an epoch change. Death and world replacement reset planning.

Populate eight ammo pools as canonical weapon slots: shells4, bullets6, rockets8, grenades9, napalm11, electricity12, sniper13, iron balls14. Use SetAmmo or write canonical slots; twin slots5/7 are aliases, never independent reserves. Populate actual session infinite_ammo explicitly. Existing fallback ammo capacities are research hypotheses and must be replaced or injected from verified native quantities before active qualification.

For health/armor pass normal top in max_health/max_armor and actual current values (including legal overtop). Set pickup_limit to actual verified recipient cap for an overtop pickup; leave0 for normal items. Unobserved native facts must not be fabricated.

The adapter deliberately returns kNativeNotQualified when offline_fixture=false. Do not relabel native snapshots as fixtures. Parent needs a separately reviewed native capability/provenance adapter and genuine Retail gates before removing this restriction.

## Native and performance blockers

Native Windows/MSVC/Wine builds, actual item/entity field offsets and stable identity extraction, exact origin/feet/eye-height conventions, verified map graphs and stair/lift/jump/ground contracts, active 1/4/8-bot Retail + unchanged Vanilla sync/CRC qualification remain NOT_TESTED_RETAIL here. Do not infer those from portable tests.

The 2m height tolerance is a synthetic routing policy, not a measured Retail step limit. Unsupported pure vertical movement requires real lift/stair/ground handling; this adapter supplies planar steering only. Legacy navlab::NavAgent's planar API remains for existing research callers; only this adapter's sink/enrichment/patrol path is 3D guarded.

Budget exhaustion conservatively defers unknown items. A path requiring more expansions than a complete cost probe may remain pending until budget/configuration changes; no incremental cost-search certificate was invented. Static item-anchor caching and native LOS-ray budgets remain parent integration work. No rays are cast here.

PR69 legacy M02 uses a vacuous even-XOR hash; it is retained as historical research output and is not claimed as determinism evidence. This controller's tests compare decision fields per tick; the controller benchmark uses a streaming non-XOR digest and allocation trap.

SDK reference only: /srv/tse-sdk-20261021 HEAD aa7869c2c2c4db0562281814d0ac3784e6b9d6f0. PlayerWeapons.es SHA256 4dd36ef1c300804d1fe8e6607299d42ca0ded4078fa97e5fe4c876c93d54cbd4 (shared GetAmmo/HasAmmo rules), Player.es 85c92933fa5b0cc726be7b42a3bc82d4c95b255507ec8b1fffe2666fcf3888af (separate normal/over-top recipients), HealthItem.es 5d8c813a6f52cbbd62ccd91177e052d21de598276fe5992b751d40fc09df2ae6, ArmorItem.es adc07ce2c30c50f1251ad77f883ac274d320c119df455519771cf4f746c2b07d. These are SDK/reference source hypotheses; original Retail1.07 source/ABI identity was not established. No proprietary source or binary was copied into this commit.
