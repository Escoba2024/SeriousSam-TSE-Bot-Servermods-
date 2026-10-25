// SPDX-License-Identifier: GPL-2.0-only
// upstream_seams.h - read-only include resolver for poc/botcore, PR #54
// (poc/navigation-lab) and PR #55 (poc/research/item-utility).
//
// BEHAVIOUR
//  1. `poc/botcore/*.h` is already on `main` and is always included read-only
//     from `../../../botcore/`.
//  2. When PR #54 (`poc/navigation-lab/`) is merged or supplied on `-I`, its
//     exact headers are included directly (`NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB=1`).
//     Otherwise, the guard-compatible mirror in `upstream/navlab_mirror.h` is
//     used so a standalone checkout of this branch builds out of the box.
//  3. Likewise for PR #55 (`poc/research/item-utility/include/`): included
//     directly when present (`NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI=1`), otherwise
//     resolved via `upstream/itemai_mirror.h`.
//  4. Defining `-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM` turns any fallback into a
//     hard `#error`, proving at compile time that both upstream PR trees were
//     resolved directly.

#ifndef NAV_ITEM_BRIDGE_UPSTREAM_SEAMS_H
#define NAV_ITEM_BRIDGE_UPSTREAM_SEAMS_H

// --- 1. Existing botcore headers (read-only) -----------------------------
#include "../../../botcore/botcore.h"
#include "../../../botcore/botcore_ai.h"
#include "../../../botcore/bot_profile.h"
#include "../../../botcore/bot_perception.h"
#include "../../../botcore/bot_aim.h"
#include "../../../botcore/bot_loadout.h"
#include "../../../botcore/bot_human.h"
#include "../../../botcore/bot_navigation.h"
#include "../../../botcore/bot_combat.h"
#include "../../../botcore/bot_weapon_input.h"

// --- 2. Navigation 2.0 (PR #54: poc/navigation-lab) ----------------------
#if defined(NAVLAB_NAV_AGENT_H)
#define NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB 1
#elif defined(__has_include) && __has_include("../../../navigation-lab/nav_agent.h")
#include "../../../navigation-lab/nav_graph.h"
#include "../../../navigation-lab/nav_astar.h"
#include "../../../navigation-lab/nav_agent.h"
#include "../../../navigation-lab/nav_maps.h"
#define NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB 1
#elif defined(__has_include) && __has_include("nav_agent.h")
#include "nav_graph.h"
#include "nav_astar.h"
#include "nav_agent.h"
#include "nav_maps.h"
#define NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB 1
#else
#if defined(NAV_ITEM_BRIDGE_REQUIRE_UPSTREAM)
#error "Upstream poc/navigation-lab headers required by NAV_ITEM_BRIDGE_REQUIRE_UPSTREAM"
#endif
#include "upstream/navlab_mirror.h"
#define NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB 0
#endif

// --- 3. Item-Utility (PR #55: poc/research/item-utility) -----------------
#if defined(ITEMAI_BOTCORE_ADAPTER_H)
#define NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI 1
#elif defined(__has_include) && __has_include("../../item-utility/include/botcore_adapter.h")
#include "../../item-utility/include/item_types.h"
#include "../../item-utility/include/item_weapons.h"
#include "../../item-utility/include/item_snapshot.h"
#include "../../item-utility/include/item_profile.h"
#include "../../item-utility/include/item_scoring.h"
#include "../../item-utility/include/navigation_interface.h"
#include "../../item-utility/include/item_planner.h"
#include "../../item-utility/include/botcore_adapter.h"
#define NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI 1
#elif defined(__has_include) && __has_include("botcore_adapter.h")
#include "item_types.h"
#include "item_weapons.h"
#include "item_snapshot.h"
#include "item_profile.h"
#include "item_scoring.h"
#include "navigation_interface.h"
#include "item_planner.h"
#include "botcore_adapter.h"
#define NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI 1
#else
#if defined(NAV_ITEM_BRIDGE_REQUIRE_UPSTREAM)
#error "Upstream poc/research/item-utility headers required by NAV_ITEM_BRIDGE_REQUIRE_UPSTREAM"
#endif
#include "upstream/itemai_mirror.h"
#define NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI 0
#endif

#endif  // NAV_ITEM_BRIDGE_UPSTREAM_SEAMS_H
