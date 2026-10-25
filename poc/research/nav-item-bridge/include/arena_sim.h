// SPDX-License-Identifier: GPL-2.0-only
// arena_sim.h - deterministic 20 Hz engine-free Deathmatch arena simulator
// for validating `NavItemBridgeAgent` across single-bot and multi-bot
// scenarios (walls, LOS occlusion, feeler rays, pickups/respawn, damage,
// dynamic blockers).
//
// Zero heap allocations; fixed-capacity POD tables.

#ifndef NAV_ITEM_BRIDGE_ARENA_SIM_H
#define NAV_ITEM_BRIDGE_ARENA_SIM_H

#include <cmath>
#include <cstdint>

#include "nav_item_bridge.h"

namespace navbridge {

constexpr int kMaxSimBots = 8;
constexpr int kMaxSimItems = 64;
constexpr int kMaxSimWalls = 64;
constexpr double kSimPickupRadiusM = 1.5;
constexpr double kSimBotRadiusM = 0.45;
constexpr double kSimFeelerRangeM = 3.5;

struct SimWall {
  double ax = 0.0;
  double az = 0.0;
  double bx = 0.0;
  double bz = 0.0;
  double half_thick_m = 0.40;
  bool blocks_movement = true;
  bool blocks_los = true;
  bool enabled = true;
};

struct SimItem {
  int id = 0;
  itemai::ItemKind kind = itemai::ItemKind::kHealth;
  int weapon_index = 0;
  itemai::Vec3 pos{};
  double value = 25.0;
  int amount = 0;
  int respawn_ticks = 200;  // 10 s @ 20 Hz; <= 0 means one-shot
  int cooldown_left = 0;
  int picked_count = 0;
  int last_picker_slot = -1;
};

struct SimBot {
  bool active = false;
  bool dummy_actor = false;  // When true, bot does not run AI (scripted target)
  int slot = 0;
  double x = 0.0;
  double y = 0.0;
  double z = 0.0;
  double vx = 0.0;
  double vz = 0.0;
  double yaw_deg = 0.0;
  double pitch_deg = 0.0;
  double health = 100.0;
  double max_health = 100.0;
  double armor = 0.0;
  double max_armor = 100.0;
  bool alive = true;
  double move_speed_mps = 12.0;
  uint32_t owned_weapons = (1u << 0) | (1u << 1);  // Knife + Single Colt
  int current_weapon = 2;
  int ammo[itemai::kWeaponCount + 1] = {0};
  int fire_cooldown_ticks = 0;
  bool obstacle_avoidance_enabled = true;

  NavItemBridgeAgent agent;
  BridgeTickOutput last_output;

  // Telemetry counters
  int pickups = 0;
  int shots_fired = 0;
  double damage_dealt = 0.0;
  double damage_taken = 0.0;
  int combat_ticks = 0;
  int survival_retreat_ticks = 0;
  int item_nav_ticks = 0;
  int patrol_ticks = 0;
  int recovery_ticks = 0;
};

/* ------------------------------------------------------------------------ */
/* 2D Segment geometry (raycast & capsule push-out)                          */
/* ------------------------------------------------------------------------ */

inline double PointSegmentDistSqXZ(double px, double pz, double ax, double az,
                                   double bx, double bz, double* closest_x,
                                   double* closest_z) {
  const double vx = bx - ax;
  const double vz = bz - az;
  const double wx = px - ax;
  const double wz = pz - az;
  const double len2 = vx * vx + vz * vz;
  double t = 0.0;
  if (len2 > 1e-12) {
    t = (wx * vx + wz * vz) / len2;
    if (t < 0.0) t = 0.0;
    if (t > 1.0) t = 1.0;
  }
  const double cx = ax + t * vx;
  const double cz = az + t * vz;
  if (closest_x) *closest_x = cx;
  if (closest_z) *closest_z = cz;
  const double dx = px - cx;
  const double dz = pz - cz;
  return dx * dx + dz * dz;
}

inline double RaySegmentHitDistXZ(double ox, double oz, double dx, double dz,
                                  double max_t, const SimWall& w) {
  const double sx = w.bx - w.ax;
  const double sz = w.bz - w.az;
  const double denom = dx * sz - dz * sx;
  if (std::fabs(denom) > 1e-9) {
    const double qx = w.ax - ox;
    const double qz = w.az - oz;
    const double t = (qx * sz - qz * sx) / denom;
    const double u = (qx * dz - qz * dx) / denom;
    if (t >= 0.0 && u >= -0.02 && u <= 1.02) {
      const double hit = t > w.half_thick_m ? (t - w.half_thick_m) : 0.0;
      if (hit <= max_t) return hit;
    }
  }
  double cx = 0.0, cz = 0.0;
  const double end_d2 =
      PointSegmentDistSqXZ(ox, oz, w.ax, w.az, w.bx, w.bz, &cx, &cz);
  if (end_d2 <= w.half_thick_m * w.half_thick_m) return 0.0;
  return max_t + 1.0;
}

/* ------------------------------------------------------------------------ */
/* ArenaSim                                                                  */
/* ------------------------------------------------------------------------ */

class ArenaSim {
 public:
  ArenaSim() { Reset(); }

  void Reset() {
    graph_.Clear();
    graph_epoch_ = 1;
    tick_ = 0;
    bot_count_ = 0;
    item_count_ = 0;
    wall_count_ = 0;
    combat_damage_enabled_ = false;
    for (int i = 0; i < kMaxSimBots; ++i) bots_[i] = SimBot{};
    for (int i = 0; i < kMaxSimItems; ++i) items_[i] = SimItem{};
    for (int i = 0; i < kMaxSimWalls; ++i) walls_[i] = SimWall{};
  }

  navlab::NavGraph& mutable_graph() { return graph_; }
  const navlab::NavGraph& graph() const { return graph_; }
  uint32_t graph_epoch() const { return graph_epoch_; }
  void BumpGraphEpoch() { ++graph_epoch_; }

  void set_combat_damage_enabled(bool enabled) {
    combat_damage_enabled_ = enabled;
  }

  int AddBot(const BridgeProfileBundle& bundle, double x, double z,
             double yaw_deg = 0.0,
             const BridgeBudgetConfig& budget = BridgeBudgetConfig()) {
    if (bot_count_ >= kMaxSimBots) return -1;
    const int idx = bot_count_++;
    SimBot& b = bots_[idx];
    b = SimBot{};
    b.active = true;
    b.dummy_actor = false;
    b.slot = idx;
    b.x = x;
    b.y = 0.0;
    b.z = z;
    b.yaw_deg = yaw_deg;
    b.ammo[2] = 50;  // Default Single Colt bullets
    b.agent.Configure(bundle, budget, idx);
    return idx;
  }

  int AddDummyEnemy(double x, double z, double yaw_deg = 0.0,
                    double health = 100.0) {
    if (bot_count_ >= kMaxSimBots) return -1;
    const int idx = bot_count_++;
    SimBot& b = bots_[idx];
    b = SimBot{};
    b.active = true;
    b.dummy_actor = true;
    b.slot = idx;
    b.x = x;
    b.y = 0.0;
    b.z = z;
    b.yaw_deg = yaw_deg;
    b.health = health;
    b.alive = health > 0.0;
    return idx;
  }

  int AddItem(int id, itemai::ItemKind kind, double x, double z,
              double value = 25.0, int weapon_index = 0, int amount = 0,
              int respawn_ticks = 200) {
    if (item_count_ >= kMaxSimItems) return -1;
    const int idx = item_count_++;
    SimItem& it = items_[idx];
    it.id = id;
    it.kind = kind;
    it.weapon_index = weapon_index;
    it.pos = MakeVec3(x, 0.0, z);
    it.value = value;
    it.amount = amount;
    it.respawn_ticks = respawn_ticks;
    it.cooldown_left = 0;
    it.picked_count = 0;
    it.last_picker_slot = -1;
    return idx;
  }

  int AddWall(double ax, double az, double bx, double bz,
              double half_thick_m = 0.40, bool blocks_movement = true,
              bool blocks_los = true) {
    if (wall_count_ >= kMaxSimWalls) return -1;
    const int idx = wall_count_++;
    SimWall& w = walls_[idx];
    w.ax = ax;
    w.az = az;
    w.bx = bx;
    w.bz = bz;
    w.half_thick_m = half_thick_m;
    w.blocks_movement = blocks_movement;
    w.blocks_los = blocks_los;
    w.enabled = true;
    return idx;
  }

  void SetWallEnabled(int wall_idx, bool enabled) {
    if (wall_idx >= 0 && wall_idx < wall_count_) {
      walls_[wall_idx].enabled = enabled;
    }
  }

  void InjectDamage(int bot_idx, double dmg) {
    if (bot_idx < 0 || bot_idx >= bot_count_ || dmg <= 0.0) return;
    SimBot& b = bots_[bot_idx];
    if (!b.alive) return;
    const double armor_absorb =
        b.armor > 0.0 ? std::fmin(b.armor, dmg * 0.5) : 0.0;
    b.armor -= armor_absorb;
    b.health -= (dmg - armor_absorb);
    b.damage_taken += dmg;
    if (b.health <= 0.0) {
      b.health = 0.0;
      b.alive = false;
    }
  }

  bool HasLineOfSightXZ(double ax, double az, double bx, double bz) const {
    const double vx = bx - ax;
    const double vz = bz - az;
    const double dist = std::sqrt(vx * vx + vz * vz);
    if (dist <= 1e-6) return true;
    const double dx = vx / dist;
    const double dz = vz / dist;
    for (int i = 0; i < wall_count_; ++i) {
      const SimWall& w = walls_[i];
      if (!w.enabled || !w.blocks_los) continue;
      const double hit = RaySegmentHitDistXZ(ax, az, dx, dz, dist, w);
      if (hit < dist - 1e-3) return false;
    }
    return true;
  }

  double CastFeelerRay(double ox, double oz, double yaw_deg,
                       double max_range = kSimFeelerRangeM) const {
    const double rad = yaw_deg * (navlab::kNavPi / 180.0);
    const double dx = -std::sin(rad);
    const double dz = -std::cos(rad);
    double best = max_range;
    for (int i = 0; i < wall_count_; ++i) {
      const SimWall& w = walls_[i];
      if (!w.enabled || !w.blocks_movement) continue;
      const double hit = RaySegmentHitDistXZ(ox, oz, dx, dz, best, w);
      if (hit < best) best = hit;
    }
    return best;
  }

  void StepTick() {
    ++tick_;

    // 1. Tick item respawn timers and build snapshot array.
    itemai::ItemSnapshot snaps[kMaxSimItems];
    for (int i = 0; i < item_count_; ++i) {
      SimItem& it = items_[i];
      if (it.cooldown_left > 0 && it.respawn_ticks > 0) {
        --it.cooldown_left;
      }
      itemai::ItemSnapshot& s = snaps[i];
      s.id = it.id;
      s.kind = it.kind;
      s.weapon_index = it.weapon_index;
      s.pos = it.pos;
      s.value = it.value;
      s.amount = it.amount;
      const bool ready = (it.cooldown_left == 0);
      s.respawn_s =
          ready ? 0.0
                : (it.respawn_ticks > 0
                       ? it.cooldown_left * botcore::kTickQuantum
                       : 999.0);
      s.visible = ready;
      s.reachable = true;
      s.staleness_s = 0.0;
    }

    // 2. Step all AI bots on the frozen start-of-tick world snapshot.
    BotDriverIntent intents[kMaxSimBots];
    for (int bi = 0; bi < bot_count_; ++bi) {
      SimBot& b = bots_[bi];
      if (!b.active || b.dummy_actor) continue;
      if (b.fire_cooldown_ticks > 0) --b.fire_cooldown_ticks;

      botcore::SenseInput sensed[kMaxSimBots];
      bool los[kMaxSimBots] = {false};
      bool needs_ray[kMaxSimBots] = {false};
      int sc = 0;
      for (int oi = 0; oi < bot_count_; ++oi) {
        if (oi == bi || !bots_[oi].active) continue;
        const SimBot& o = bots_[oi];
        botcore::SenseInput& si = sensed[sc];
        si.index = o.slot;
        si.x = o.x;
        si.y = o.y + 1.6;
        si.z = o.z;
        si.vx = o.vx;
        si.vy = 0.0;
        si.vz = o.vz;
        si.health = o.health;
        si.alive = o.alive;
        si.local = false;
        ++sc;
      }

      BridgeTickInput in;
      in.world.tick = tick_;
      in.world.pose.x = b.x;
      in.world.pose.y = b.y + 1.6;
      in.world.pose.z = b.z;
      in.world.pose.yaw_deg = b.yaw_deg;
      in.world.pose.pitch_deg = b.pitch_deg;
      in.world.health = b.health;
      in.world.max_health = b.max_health;
      in.world.alive = b.alive;
      in.world.deathmatch = true;
      in.world.current_weapon = b.current_weapon;

      in.armor = b.armor;
      in.max_armor = b.max_armor;
      in.owned_weapons = b.owned_weapons;
      for (int w = 0; w <= itemai::kWeaponCount; ++w) in.ammo[w] = b.ammo[w];
      in.move_speed_mps = b.move_speed_mps;

      // Two-pass LOS budget identical to BotDriver.cpp.
      b.agent.PlanLosQueries(in.world, sensed, sc, needs_ray);
      for (int k = 0; k < sc; ++k) {
        if (needs_ray[k]) {
          los[k] = HasLineOfSightXZ(b.x, b.z, sensed[k].x, sensed[k].z);
        }
      }

      // Per-bot item visibility: line-of-sight sets `visible = true` when ready.
      itemai::ItemSnapshot bot_snaps[kMaxSimItems];
      for (int ii = 0; ii < item_count_; ++ii) {
        bot_snaps[ii] = snaps[ii];
        if (bot_snaps[ii].respawn_s <= 0.0) {
          bot_snaps[ii].visible =
              HasLineOfSightXZ(b.x, b.z, snaps[ii].pos.x, snaps[ii].pos.z);
        } else {
          bot_snaps[ii].visible = false;
        }
      }

      in.sensed_players = sensed;
      in.player_los = los;
      in.sensed_count = sc;
      in.items = bot_snaps;
      in.item_count = item_count_;
      in.obstacle_avoidance_enabled = b.obstacle_avoidance_enabled;
      in.obstacle_front_m = CastFeelerRay(b.x, b.z, b.yaw_deg);
      in.obstacle_left_m = CastFeelerRay(b.x, b.z, b.yaw_deg + 60.0);
      in.obstacle_right_m = CastFeelerRay(b.x, b.z, b.yaw_deg - 60.0);
      in.preferred_recovery_dir = (b.slot & 1) ? -1 : 1;
      in.dt = botcore::kTickQuantum;

      b.last_output = b.agent.Step(graph_, graph_epoch_, in);
      intents[bi] = b.last_output.intent;

      switch (b.last_output.trace.owner) {
        case ControllerOwner::kCombat:
          ++b.combat_ticks;
          break;
        case ControllerOwner::kSurvivalRetreat:
          ++b.survival_retreat_ticks;
          break;
        case ControllerOwner::kItemNavigation:
          ++b.item_nav_ticks;
          break;
        case ControllerOwner::kPatrolNavigation:
          ++b.patrol_ticks;
          break;
        case ControllerOwner::kObstacleRecovery:
          ++b.recovery_ticks;
          break;
        default:
          break;
      }
    }

    // 3. Integrate kinematics & wall collision for each active AI bot.
    for (int bi = 0; bi < bot_count_; ++bi) {
      SimBot& b = bots_[bi];
      if (!b.active || b.dummy_actor || !b.alive) continue;
      const BotDriverIntent& act = intents[bi];

      b.yaw_deg += act.yaw_delta_deg;
      b.pitch_deg =
          act.pitch_delta_deg + b.pitch_deg < -85.0
              ? -85.0
              : (act.pitch_delta_deg + b.pitch_deg > 85.0
                     ? 85.0
                     : act.pitch_delta_deg + b.pitch_deg);
      if (act.weapon >= 1 && act.weapon <= itemai::kWeaponCount &&
          itemai::WeaponOwned(b.owned_weapons, act.weapon)) {
        b.current_weapon = act.weapon;
      }

      const double rad = b.yaw_deg * (navlab::kNavPi / 180.0);
      const double fwd_x = -std::sin(rad);
      const double fwd_z = -std::cos(rad);
      const double right_x = std::cos(rad);
      const double right_z = -std::sin(rad);

      double dir_x = fwd_x * act.forward + right_x * act.strafe;
      double dir_z = fwd_z * act.forward + right_z * act.strafe;
      const double mag = std::sqrt(dir_x * dir_x + dir_z * dir_z);
      if (mag > 1.0) {
        dir_x /= mag;
        dir_z /= mag;
      }
      b.vx = dir_x * b.move_speed_mps;
      b.vz = dir_z * b.move_speed_mps;
      double nx = b.x + b.vx * botcore::kTickQuantum;
      double nz = b.z + b.vz * botcore::kTickQuantum;

      for (int pass = 0; pass < 2; ++pass) {
        for (int wi = 0; wi < wall_count_; ++wi) {
          const SimWall& w = walls_[wi];
          if (!w.enabled || !w.blocks_movement) continue;
          double cx = 0.0, cz = 0.0;
          const double d2 =
              PointSegmentDistSqXZ(nx, nz, w.ax, w.az, w.bx, w.bz, &cx, &cz);
          const double min_r = kSimBotRadiusM + w.half_thick_m;
          if (d2 < min_r * min_r) {
            const double d = std::sqrt(d2);
            if (d > 1e-6) {
              const double push = (min_r - d);
              nx += ((nx - cx) / d) * push;
              nz += ((nz - cz) / d) * push;
            } else {
              nx = b.x;
              nz = b.z;
            }
          }
        }
      }
      b.x = nx;
      b.z = nz;

      if (act.fire && b.fire_cooldown_ticks == 0) {
        ++b.shots_fired;
        b.fire_cooldown_ticks = 8;
        if (itemai::WeaponNeedsAmmo(b.current_weapon) &&
            b.ammo[b.current_weapon] > 0) {
          --b.ammo[b.current_weapon];
        }
        if (combat_damage_enabled_) {
          const int tgt = b.last_output.combat_cmd.target;
          if (tgt >= 0 && tgt < bot_count_ && bots_[tgt].alive &&
              HasLineOfSightXZ(b.x, b.z, bots_[tgt].x, bots_[tgt].z)) {
            InjectDamage(tgt, 12.0);
            b.damage_dealt += 12.0;
          }
        }
      }
    }

    // 4. Resolve item pickups deterministically (closest bot inside pickup
    //    sphere wins; ties broken by lower slot index).
    for (int ii = 0; ii < item_count_; ++ii) {
      SimItem& it = items_[ii];
      if (it.cooldown_left != 0) continue;

      int best_bot = -1;
      double best_d2 = kSimPickupRadiusM * kSimPickupRadiusM;
      for (int bi = 0; bi < bot_count_; ++bi) {
        const SimBot& b = bots_[bi];
        if (!b.active || b.dummy_actor || !b.alive) continue;
        const double dx = b.x - it.pos.x;
        const double dz = b.z - it.pos.z;
        const double d2 = dx * dx + dz * dz;
        if (d2 <= best_d2) {
          if (best_bot < 0 || d2 < best_d2 - 1e-9) {
            best_d2 = d2;
            best_bot = bi;
          }
        }
      }
      if (best_bot >= 0) {
        ApplyPickup(&bots_[best_bot], &it);
      }
    }
  }

  int tick() const { return tick_; }
  int bot_count() const { return bot_count_; }
  int item_count() const { return item_count_; }
  int wall_count() const { return wall_count_; }
  SimBot& bot(int idx) { return bots_[idx]; }
  const SimBot& bot(int idx) const { return bots_[idx]; }
  SimItem& item(int idx) { return items_[idx]; }
  const SimItem& item(int idx) const { return items_[idx]; }

 private:
  void ApplyPickup(SimBot* b, SimItem* it) {
    switch (it->kind) {
      case itemai::ItemKind::kHealth: {
        const double cap =
            it->value > 60.0 ? (b->max_health * 2.0) : b->max_health;
        b->health = std::fmin(cap, b->health + it->value);
        break;
      }
      case itemai::ItemKind::kArmor: {
        const double cap =
            it->value > 100.0 ? (b->max_armor * 2.0) : b->max_armor;
        b->armor = std::fmin(cap, b->armor + it->value);
        break;
      }
      case itemai::ItemKind::kWeapon: {
        const int w = it->weapon_index;
        if (w >= 1 && w <= itemai::kWeaponCount) {
          b->owned_weapons |= (1u << (w - 1));
          const int cap = itemai::WeaponAmmoCap(w);
          if (cap > 0) {
            const int bonus = it->amount > 0 ? it->amount : (cap / 4 > 5 ? cap / 4 : 5);
            b->ammo[w] = (b->ammo[w] + bonus > cap) ? cap : (b->ammo[w] + bonus);
          }
        }
        break;
      }
      case itemai::ItemKind::kAmmo: {
        const int w = it->weapon_index;
        if (w >= 1 && w <= itemai::kWeaponCount) {
          const int cap = itemai::WeaponAmmoCap(w);
          const int add = it->amount > 0 ? it->amount : (cap / 4 > 5 ? cap / 4 : 5);
          b->ammo[w] = (b->ammo[w] + add > cap) ? cap : (b->ammo[w] + add);
        }
        break;
      }
      default:
        break;
    }

    it->cooldown_left = it->respawn_ticks > 0 ? it->respawn_ticks : 999999;
    ++it->picked_count;
    it->last_picker_slot = b->slot;
    ++b->pickups;
    b->agent.NotifyItemPicked(it->id, tick_);
  }

  navlab::NavGraph graph_;
  uint32_t graph_epoch_ = 1;
  int tick_ = 0;
  int bot_count_ = 0;
  int item_count_ = 0;
  int wall_count_ = 0;
  bool combat_damage_enabled_ = false;

  SimBot bots_[kMaxSimBots];
  SimItem items_[kMaxSimItems];
  SimWall walls_[kMaxSimWalls];
};

}  // namespace navbridge

#endif  // NAV_ITEM_BRIDGE_ARENA_SIM_H
