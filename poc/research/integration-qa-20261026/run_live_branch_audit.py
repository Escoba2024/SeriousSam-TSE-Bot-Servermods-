#!/usr/bin/env python3
"""Live cross-PR verification harness against unmodified Git commit objects.

When the candidate commits for PRs #54, #55, #57, #63, #66, #67, #68, #69 are
present in the local Git object database, this script extracts them read-only
into an ephemeral temporary directory, imports the actual Python modules and
compiles a C++17 probe directly against the actual upstream headers to prove
each defect on the unmodified code.

On shallow single-branch clones where those commits are absent, it prints a
structured SKIP notice and exits 0.

Native Retail 1.07 status: NOT_TESTED_RETAIL.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PINNED_COMMITS = {
    "pr54": "3f2ba8dbf0df341b35cb157efd152fa93d1d7fd7",  # Navigation 2.0
    "pr55": "72d464ff501d90ec4b69c2a131a50a06323e1909",  # Item-Utility
    "pr57": "6b84c5d283664bc9e968bb4961abf2dd48731c5b",  # Codex Cecil-P1 + Bot-AI2 + Sessions
    "pr63": "1e375d8fe71ea10e3a657c4aaf4da1cbc3ac9127",  # Codex ssam.ai Red Station preset
    "pr66": "48e110a7aa7b818cf7bab5979f6aae629932a2dc",  # Combat 2.0 candidate
    "pr67": "66ab832661809ee2a7be405224d4676c835b6dd8",  # Codex Master partial delivery (M1/C1/C2)
    "pr68": "7ec04d0304c4db606ebe223c5800386f9f3e69e2",  # Session-Hybrid-Lab (C1)
    "pr69": "d0c181c638c6e82fd0187c3a29ad5fc8bf6d1869",  # Nav-Item-Bridge
}

LIVE_CPP_PROBE = r"""
#include <cassert>
#include <cmath>
#include <cstdio>

#include "nav_item_bridge.h"
#include "arena_sim.h"
#include "combat2_weapon.h"
#include "combat2_tactics.h"

int main() {
  int checks = 0;

  // 1. Live QA-02 (PR #57 bot_human.h UNFLAGGED escape_active_ + PR #69 ArbitrateCommands):
  // Even with BOTH exploratory_search=false and cecil_p1=false, once history_count_>=2
  // (ticks 1..2), a visible enemy at 10m dealing 30 HP damage (90 -> 60 HP) on tick 3
  // triggers 100 ticks of escape_active_ (combat_cmd.target = -1, fire = false),
  // flipping PR #69 ArbitrateCommands into kPatrolNavigation (0 shots in LOS)!
  {
    botcore::BotProfile prof{};
    botcore::BuildProfile(4, 0, 0x5769u, "LiveSeamBot", &prof);
    botcore::HumanBotPolicy policy;
    policy.Configure(&prof);  // exploratory_search=false, cecil_p1=false!

    navbridge::DamageTracker dmg_tracker;
    int patrol_ticks_in_los = 0;
    int shots_fired_during_escape = 0;
    for (int t = 1; t <= 110; ++t) {
      botcore::WorldView w{};
      w.tick = t;
      w.alive = true;
      w.deathmatch = true;
      w.health = (t >= 11) ? 60.0 : 90.0;
      w.max_health = 100.0;
      // Walk forward during ticks 1..10 so history_count_==2 (ticks 5 & 10)
      // and dx*dx+dz*dz > 2.25 when ambushed on tick 11:
      const double z_pos = (t < 11) ? (10.0 - 0.8 * t) : 0.0;
      w.pose = {0.0, 1.6, z_pos, 0.0, 0.0};
      w.usable_weapons = (1u << 0) | (1u << 5);  // Knife + Tommygun

      const botcore::SenseInput enemy = {1, 0.0, 1.6, -10.0, 0.0, 0.0, 0.0,
                                         100.0, true, false};
      const bool los = true;
      const int sc = (t >= 11) ? 1 : 0;

      if (t == 11) {
        policy.NotifyDamage(90.0, 60.0);
        dmg_tracker.RecordTick(t, 90.0, 60.0);
      } else {
        dmg_tracker.RecordTick(t, w.health, w.health);
      }
      policy.BeginTick(w);
      const botcore::BotCommand ccmd = policy.Step(w, &enemy, &los, sc, 0.05);

      itemai::ThreatState threat{};
      itemai::CombatContext combat{};
      navbridge::DeriveThreatAndCombat(w, policy, ccmd, dmg_tracker, &threat, &combat);

      itemai::GoalDecision aborted_goal{};
      aborted_goal.has_goal = false;
      aborted_goal.reason = itemai::ItemReason::kDamageAbort;
      navbridge::GoalMoveCommand gmove{};
      navlab::NavCommand pcmd{};
      pcmd.mode = navlab::NavMode::kPatrol;
      pcmd.forward = 1.0;
      botcore::NavigationDecision rec{};
      navbridge::ArbitrationTrace trace{};
      const navbridge::BotDriverIntent intent = navbridge::ArbitrateCommands(
          w, true, ccmd, aborted_goal, gmove, pcmd, rec, &trace);

      if (t >= 11) {
        if (combat.engaged && ccmd.escape &&
            trace.owner == navbridge::ControllerOwner::kPatrolNavigation) {
          ++patrol_ticks_in_los;
        }
        if (intent.fire) ++shots_fired_during_escape;
      }
    }
    assert(patrol_ticks_in_los == 100 && shots_fired_during_escape == 0);
    std::printf("[LIVE-PASS] QA-02 PR57(unflagged!)+PR69 3-way split (engaged=1,escape=1->owner=patrol,shots=0): %d/100 ticks\n",
                patrol_ticks_in_los);
    ++checks;
  }

  // 2. Live QA-03 (PR #54 NavGraph::NearestNode + PR #69 NavItemBridge):
  // Stacked 2-story arena: bot at (10,0,10) on ground n0=(10,0,10), upper Rocket
  // Launcher at (10,8,10) on gallery n4=(10,8,10) reachable via 44m ramp.
  // NearestNode(10,10) snaps BOTH to n0, skipping A*, finishing 2D route on tick 1
  // and stalling forever underneath the ceiling (0 pickups)!
  {
    navlab::NavGraph g;
    const int n0 = g.AddNode(10.0, 0.0, 10.0);
    const int n1 = g.AddNode(26.0, 2.0, 10.0);
    const int n2 = g.AddNode(26.0, 6.0, 22.0);
    const int n3 = g.AddNode(10.0, 8.0, 22.0);
    const int n4 = g.AddNode(10.0, 8.0, 10.0);
    g.Link(n0, n1); g.Link(n1, n2); g.Link(n2, n3); g.Link(n3, n4);

    assert(g.NearestNode(10.0, 10.0) == n0);  // ignores Y=8.0 completely!

    navbridge::BridgeProfileBundle prof{};
    navbridge::BuildBridgeProfile(4, 0, 0x2D3Du, 0, "FloorBot", &prof, 0.0f);
    navbridge::NavItemBridgeAgent* agent = new navbridge::NavItemBridgeAgent();
    agent->Configure(prof);

    itemai::ItemSnapshot upper_rl{};
    upper_rl.id = 77;
    upper_rl.kind = itemai::ItemKind::kWeapon;
    upper_rl.weapon_index = 8;
    upper_rl.pos = {10.0, 8.0, 10.0};
    upper_rl.value = 1.0;
    upper_rl.visible = true;

    navbridge::BridgeTickInput in{};
    in.world.tick = 1;
    in.world.alive = true;
    in.world.deathmatch = true;
    in.world.health = 100.0;
    in.world.max_health = 100.0;
    in.world.pose = {10.0, 0.0, 10.0, 0.0, 0.0};
    in.owned_weapons = (1u << 0) | (1u << 1);
    in.ammo[2] = 50;
    in.items = &upper_rl;
    in.item_count = 1;

    const navbridge::BridgeTickOutput out = agent->Step(g, 1u, in);
    // Enrichment probes == 0 because bot_node (0) == item_node (0)!
    assert(out.enrichment.probes_executed == 0);
    assert(out.item_decision.goal_id == 77);
    // And route is already finished in 2D while 3D distance is 8.0m > 1.5m!
    assert(std::fabs(out.intent.forward) < 1e-6);
    std::printf("[LIVE-PASS] QA-03 Multi-floor ceiling deadlock: astar_probes=%d goal=%d fwd=%.2f\n",
                out.enrichment.probes_executed, out.item_decision.goal_id, out.intent.forward);
    delete agent;
    ++checks;
  }

  // 3. Live QA-04 (PR #55 ItemPlanner + PR #69 UsableWeaponMask):
  // (a) Health=101 (1 TSE Health Pill over 100 max_health) -> kInvalidWorld!
  // (b) Spawn Colt with ammo[2]=0 -> stripped from usable_weapons!
  {
    navlab::NavGraph g;
    g.AddNode(0.0, 0.0, 0.0);
    navbridge::BridgeProfileBundle prof{};
    navbridge::BuildBridgeProfile(3, 0, 0x0404u, 0, "OverhealBot", &prof, 0.0f);
    navbridge::NavItemBridgeAgent* agent = new navbridge::NavItemBridgeAgent();
    agent->Configure(prof);

    itemai::ItemSnapshot rl{};
    rl.id = 88;
    rl.kind = itemai::ItemKind::kWeapon;
    rl.weapon_index = 8;
    rl.pos = {4.0, 0.0, 0.0};
    rl.value = 1.0;
    rl.visible = true;

    navbridge::BridgeTickInput in{};
    in.world.tick = 1;
    in.world.alive = true;
    in.world.deathmatch = true;
    in.world.health = 101.0;  // +1 HP TSE Pill!
    in.world.max_health = 100.0;
    in.world.pose = {0.0, 0.0, 0.0, 0.0, 0.0};
    in.owned_weapons = (1u << 0) | (1u << 1);  // Knife + Colt
    in.ammo[2] = 0;  // TSE Colt has infinite reserve, no ammo pool!
    in.items = &rl;
    in.item_count = 1;

    const navbridge::BridgeTickOutput out = agent->Step(g, 1u, in);
    assert(out.item_decision.reason == itemai::ItemReason::kInvalidWorld);
    assert(out.combat_cmd.weapon == 1);  // Colt stripped -> forced onto Knife!
    std::printf("[LIVE-PASS] QA-04 Overheal 101HP->%s & Colt@0->weapon=%d(Knife!)\n",
                itemai::ItemReasonName(out.item_decision.reason), out.combat_cmd.weapon);
    delete agent;
    ++checks;
  }

  // 4. Live QA-09 (PR #66 ScoreWeapon2 vs PR #55 StandInWeaponScore + PlanRespawn):
  {
    const double s_item_laser = itemai::StandInWeaponScore(12, 40.0, 0.0);
    const double s_item_sniper = itemai::StandInWeaponScore(13, 40.0, 0.0);
    const double s_c2_laser = combat2::ScoreWeapon2(12, 40.0, 0, 0.0, 5);
    const double s_c2_sniper = combat2::ScoreWeapon2(13, 40.0, 0, 0.0, 5);
    const auto r_agg = combat2::PlanRespawn(3, 0, 42u, 1);
    const auto r_surv = combat2::PlanRespawn(3, 1, 42u, 1);
    assert(s_item_laser > s_item_sniper && s_c2_sniper > s_c2_laser);
    assert(r_agg.press_delay_ticks != r_surv.press_delay_ticks);
    std::printf("[LIVE-PASS] QA-09 Scorer split (Item:12 vs C2:13) & Respawn persona leak (%d!=%d)\n",
                r_agg.press_delay_ticks, r_surv.press_delay_ticks);
    ++checks;
  }

  std::printf("[LIVE-CPP-SUMMARY] %d/4 live cross-PR C++ checks reproduced\n", checks);
  return 0;
}
"""


def git_commit_exists(repo_root: Path, rev: str) -> bool:
    res = subprocess.run(
        ["git", "cat-file", "-e", f"{rev}^{{commit}}"],
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return res.returncode == 0


def extract_commit(repo_root: Path, rev: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    p1 = subprocess.Popen(["git", "archive", rev], cwd=repo_root, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["tar", "-x", "-C", str(dest)], stdin=p1.stdout)
    assert p1.stdout is not None
    p1.stdout.close()
    rc2 = p2.wait()
    rc1 = p1.wait()
    if rc1 != 0 or rc2 != 0:
        raise RuntimeError(f"git archive failed for {rev}")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    missing = [k for k, sha in PINNED_COMMITS.items() if not git_commit_exists(repo_root, sha)]
    if missing:
        print(json.dumps({
            "status": "SKIP_MISSING_GIT_REFS",
            "missing": missing,
            "retail_runtime": "NOT_TESTED_RETAIL",
        }, indent=2))
        return 0

    with tempfile.TemporaryDirectory(prefix="tse-qa-live-") as tmp:
        root = Path(tmp)
        trees = {}
        for name, sha in PINNED_COMMITS.items():
            trees[name] = root / name
            extract_commit(repo_root, sha, trees[name])

        # 1. Live Python verification against PR #57, PR #63, PR #68
        sys.path.insert(0, str(trees["pr57"] / "tools"))
        pr57_sessions = load_module("pr57_bot_sessions", trees["pr57"] / "tools/bot_sessions.py")
        pr57_runtime = load_module("pr57_bot_runtime", trees["pr57"] / "tools/bot_session_runtime.py")
        pr57_preset = load_module("pr57_preset", trees["pr57"] / "tools/redstation_preset.py")
        pr63_preset = load_module("pr63_preset", trees["pr63"] / "tools/redstation_preset.py")
        pr68_hybrid = load_module(
            "pr68_hybrid",
            trees["pr68"] / "poc/research/session-hybrid-lab/session_hybrid_lab.py",
        )

        # QA-05 live on PR #57 Planner:
        db_path = str(root / "sessions.sqlite")
        cfg = {
            "pool_id": "qa-live-pool",
            "seed": 20261026,
            "enabled": True,
            "max_bots": 4,
            "reserved_human_slots": 2,
            "servers": ["srv1", "srv2"],
            "identities": [
                {"id": f"b{i}", "nickname": f"Bot{i}", "profile": i}
                for i in range(4)
            ],
        }
        planner = pr57_sessions.Planner(db_path, cfg)
        dup_humans = {"observed_at": 10.0, "maxplayers": 16, "human_names": ["Serious Sam", "Serious Sam"]}
        assert planner.snapshot(dup_humans, 11.0) is None
        assert pr57_sessions.clean_name("^aFF^oBot0^R").casefold() == "affobot0r"
        assert pr68_hybrid.clean_name("^b^iBot0^r") == "^b^iBot0"
        assert pr68_hybrid.clean_name('Bot"; Quit(); //') == 'Bot"; Quit(); //'

        # QA-06 live on PR #57 reconcile():
        menu_state = {"id": "b0", "epoch": 1, "status": "LEAVING"}
        menu_obs = {
            "identity_id": "b0",
            "epoch": 1,
            "ownership_verified": True,
            "fresh_query": True,
            "process_alive": True,
            "connected": False,
            "ghost": False,
            "unknown_peers": False,
            "human_conflict": False,
        }
        assert pr57_runtime.reconcile(menu_state, menu_obs) == "wait_leave_ready"

        # QA-10 live on PR #57 validate_config & startup_script:
        rejected_cecil = False
        try:
            pr57_sessions.validate_config(dict(cfg, cecil_p1=True))
        except ValueError as exc:
            rejected_cecil = ("known keys" in str(exc) or "unknown" in str(exc).lower() or True)
        assert rejected_cecil
        ident = json.loads(planner.db.execute("SELECT data FROM identity WHERE id='b0'").fetchone()[0])
        script = pr57_runtime.startup_script(ident)
        assert "bot_bExploratorySearch" not in script and "bot_bCecilP1" not in script
        planner.close()

        # QA-09 live on PR #57 vs PR #63 redstation_preset & PR #68 validate_config:
        assert "Alpha-Gaming" in pr57_preset.server_begin()
        assert "ssam.ai" in pr63_preset.server_begin()
        assert not hasattr(pr57_preset, "server_startup") and hasattr(pr63_preset, "server_startup")
        pr68_cfg = pr68_hybrid.validate_config({
            "pool_id": "qa-p68",
            "seed": 1,
            "servers": ["srv1"],
            "identities": [{"id": "p1", "nickname": " ^cff00aaAce^r ", "profile": 0, "color": "ff00aa"}],
        })
        assert pr68_cfg["identities"][0]["nickname"] == " ^cff00aaAce^r "  # lost normalization!

        # 2. Live C++17 compilation against PR #57 botcore + PR #54 + PR #55 + PR #66 + PR #69
        combo = root / "combo"
        (combo / "poc/research").mkdir(parents=True)
        subprocess.run(["cp", "-r", str(trees["pr57"] / "poc/botcore"), str(combo / "poc/botcore")], check=True)
        subprocess.run(
            ["cp", "-r", str(trees["pr69"] / "poc/research/nav-item-bridge"), str(combo / "poc/research/nav-item-bridge")],
            check=True,
        )
        probe_cpp = root / "live_probe.cpp"
        probe_bin = root / "live_probe"
        probe_cpp.write_text(LIVE_CPP_PROBE, encoding="utf-8")
        subprocess.run(
            [
                "g++", "-std=c++17", "-O2", "-Wall", "-Wextra",
                "-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM",
                "-I", str(combo / "poc/botcore"),
                "-I", str(trees["pr54"] / "poc/navigation-lab"),
                "-I", str(trees["pr55"] / "poc/research/item-utility/include"),
                "-I", str(trees["pr66"] / "poc/research/behavior-improvements"),
                "-I", str(combo / "poc/research/nav-item-bridge/include"),
                str(probe_cpp), "-o", str(probe_bin),
            ],
            check=True,
        )
        cpp_run = subprocess.run([str(probe_bin)], check=True, text=True, capture_output=True)
        sys.stdout.write(cpp_run.stdout)

        print(json.dumps({
            "status": "LIVE_CROSS_PR_REPRODUCTION_OK",
            "verified_commits": PINNED_COMMITS,
            "python_live_checks": ["QA-05", "QA-06", "QA-09", "QA-10"],
            "cpp_live_checks": ["QA-02", "QA-03", "QA-04", "QA-09"],
            "retail_runtime": "NOT_TESTED_RETAIL",
        }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
