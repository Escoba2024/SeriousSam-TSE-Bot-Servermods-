// botcore_ai.h - standalone, engine-free decision logic for Phases 2 and 4-6
// of the vanilla bot client ("Pfad D"). Companion to botcore.h; consumed by
// poc/patch/gamemp/BotDriver.cpp and verified in isolation by
// test_botcore_ai.cpp.
//
// HARD SCOPE RULES (same as the Phase-1 PoC):
//  - pure decision logic only: no entity writes, no engine calls, no I/O;
//  - everything is deterministic (seeded LCG for presence/chat cadence);
//  - all world knowledge comes from read-only replicated player snapshots
//    that the caller provides (positions/health as already logged by
//    [BotSnapshot] in Phase 1);
//  - NO line-of-sight or collision model exists here. Target pursuit is
//    straight-line; the waypoint graph is only a hand-authored fallback for
//    stuck situations. This is NOT CecilBot navigation.
//
// Conventions replicated from the vanilla sources:
//  - weapon selection bits: pa_ulButtons |= (weapon_index << 14), exactly the
//    "2L<<14 == Colt" convention already used by the Phase-1 combat test
//    (EntitiesMP/Player.es PLACT_SELECT_WEAPON_SHIFT = 14);
//  - weapon indices: EntitiesMP/PlayerWeapons.es WeaponType enum for TSE
//    (1 knife, 2 colt, 3 double colt, 4 single shotgun, 5 double shotgun,
//     6 tommygun, 7 minigun, 8 rocket launcher, 9 grenade launcher,
//     10 chainsaw, 11 flamer, 12 laser, 13 sniper, 14 cannon);
//  - the available-weapons bitmask uses bit (index-1), mirroring
//    CPlayerWeapons::m_iAvailableWeapons ("1 << (WEAPON_* - 1)").

#ifndef BOTCORE_AI_H
#define BOTCORE_AI_H

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace botcore {

/* ------------------------------------------------------------------------ */
/* Deterministic PRNG (presence / chat cadence only - never gameplay state)  */
/* ------------------------------------------------------------------------ */

class Lcg {
 public:
  explicit Lcg(uint32_t seed) : state_(seed ? seed : 1u) {}
  uint32_t Next() {
    state_ = state_ * 1664525u + 1013904223u;  // Numerical Recipes LCG
    return state_;
  }
  // Uniform-ish integer in [lo, hi] (inclusive); lo <= hi required.
  int NextRange(int lo, int hi) {
    const uint32_t span = static_cast<uint32_t>(hi - lo) + 1u;
    return lo + static_cast<int>((Next() >> 8) % span);
  }

 private:
  uint32_t state_;
};

/* ------------------------------------------------------------------------ */
/* Phase 2 - deterministic per-bot variation                                 */
/* ------------------------------------------------------------------------ */

// Distinct, reproducible behavior per local player slot (iLP 0..3) so four
// bots in one process never move in lockstep. The heading offset is applied
// once at (re)join; the yaw scale multiplies bot_fYawSpeed.
struct BotVariant {
  double heading_offset_deg;
  double yaw_speed_scale;
};

inline BotVariant VariantFor(int bot_index) {
  static const BotVariant kVariants[4] = {
      {0.0, 1.00}, {90.0, 0.85}, {180.0, 1.15}, {270.0, 0.70}};
  return kVariants[bot_index & 3];
}

/* ------------------------------------------------------------------------ */
/* Phase 4 - target selection                                                */
/* ------------------------------------------------------------------------ */

struct TargetInfo {
  int index;      // replicated player index 0..15
  double x, y, z; // en_plPlacement position
  double health;  // replicated health (<=0 means dead/respawning)
  bool local;     // true if this player belongs to our own bot process
};

// Nearest living player that is neither ourselves nor (optionally) another
// local bot. Returns the replicated player index, or -1 if no target exists.
inline int SelectTarget(const TargetInfo* players, int count, int self_index,
                        double self_x, double self_y, double self_z,
                        bool skip_locals) {
  int best = -1;
  double best_d2 = 0.0;
  for (int i = 0; i < count; ++i) {
    const TargetInfo& t = players[i];
    if (t.index == self_index || t.health <= 0.0) continue;
    if (skip_locals && t.local) continue;
    const double dx = t.x - self_x, dy = t.y - self_y, dz = t.z - self_z;
    const double d2 = dx * dx + dy * dy + dz * dz;
    if (best < 0 || d2 < best_d2) {
      best = t.index;
      best_d2 = d2;
    }
  }
  return best;
}

/* ------------------------------------------------------------------------ */
/* Phase 4 - weapon selection                                                */
/* ------------------------------------------------------------------------ */

constexpr int kPlactSelectWeaponShift = 14;  // Player.es PLACT_SELECT_WEAPON_SHIFT

inline uint32_t WeaponSelectButtons(int weapon_index) {
  return static_cast<uint32_t>(weapon_index) << kPlactSelectWeaponShift;
}

// m_iAvailableWeapons-style mask helper: bit (index-1) set = weapon owned.
inline bool WeaponAvailable(uint32_t available_mask, int weapon_index) {
  return weapon_index >= 1 &&
         (available_mask & (1u << (weapon_index - 1))) != 0u;
}

// Simple deterministic range-band preference. This is a heuristic of this
// PoC, NOT a vanilla constant: explosives are excluded to avoid self-damage,
// the knife is the guaranteed fallback (always owned in deathmatch spawns).
inline int SelectWeapon(uint32_t available_mask, double distance_m) {
  static const int kClose[] = {5, 4, 6, 2, 10, 1};   // < 10 m
  static const int kMid[]   = {7, 6, 5, 12, 2, 1};   // 10..30 m
  static const int kFar[]   = {13, 12, 7, 6, 2, 1};  // > 30 m
  const int* order = distance_m < 10.0 ? kClose
                     : distance_m <= 30.0 ? kMid
                                          : kFar;
  const int count = 6;
  for (int i = 0; i < count; ++i) {
    if (WeaponAvailable(available_mask, order[i])) return order[i];
  }
  return 1;  // knife
}

/* ------------------------------------------------------------------------ */
/* Phase 4 - hand-authored waypoint graph (stuck fallback, no pathfinding    */
/* against world geometry; BFS over explicit edges only)                     */
/* ------------------------------------------------------------------------ */

class WaypointGraph {
 public:
  static const int kMaxNodes = 256;
  static const int kMaxEdgesPerNode = 8;

  WaypointGraph() : node_count_(0) { std::memset(edge_count_, 0, sizeof(edge_count_)); }

  int node_count() const { return node_count_; }

  int AddNode(double x, double y, double z) {
    if (node_count_ >= kMaxNodes) return -1;
    nodes_[node_count_][0] = x;
    nodes_[node_count_][1] = y;
    nodes_[node_count_][2] = z;
    edge_count_[node_count_] = 0;
    return node_count_++;
  }

  bool Link(int a, int b) {  // bidirectional
    if (!Valid(a) || !Valid(b) || a == b) return false;
    return AddEdge(a, b) && AddEdge(b, a);
  }

  bool NodePosition(int i, double* x, double* y, double* z) const {
    if (!Valid(i)) return false;
    *x = nodes_[i][0];
    *y = nodes_[i][1];
    *z = nodes_[i][2];
    return true;
  }

  int NearestNode(double x, double y, double z) const {
    int best = -1;
    double best_d2 = 0.0;
    for (int i = 0; i < node_count_; ++i) {
      const double dx = nodes_[i][0] - x, dy = nodes_[i][1] - y,
                   dz = nodes_[i][2] - z;
      const double d2 = dx * dx + dy * dy + dz * dz;
      if (best < 0 || d2 < best_d2) {
        best = i;
        best_d2 = d2;
      }
    }
    return best;
  }

  // First hop of the shortest (fewest-edges) path from `from` to `to`.
  // Returns `to` when adjacent or equal, -1 when unreachable.
  int NextHop(int from, int to) const {
    if (!Valid(from) || !Valid(to)) return -1;
    if (from == to) return to;
    int parent[kMaxNodes];
    int queue[kMaxNodes];
    for (int i = 0; i < node_count_; ++i) parent[i] = -1;
    int head = 0, tail = 0;
    queue[tail++] = from;
    parent[from] = from;
    while (head < tail) {
      const int n = queue[head++];
      for (int e = 0; e < edge_count_[n]; ++e) {
        const int m = edges_[n][e];
        if (parent[m] >= 0) continue;
        parent[m] = n;
        if (m == to) {
          int hop = to;  // walk back to the node right after `from`
          while (parent[hop] != from) hop = parent[hop];
          return hop;
        }
        queue[tail++] = m;
      }
    }
    return -1;
  }

  // Line format for Scripts waypoint files (parsed by BotDriver):
  //   "node <x> <y> <z>"   and   "edge <a> <b>"
  // '#' or "//" starts a comment; blank lines are ignored.
  // Returns false on malformed input (caller should log and disable nav).
  bool ParseLine(const char* line) {
    while (*line == ' ' || *line == '\t') ++line;
    if (*line == '\0' || *line == '#' || *line == '\r' || *line == '\n' ||
        (line[0] == '/' && line[1] == '/')) {
      return true;  // comment / blank
    }
    double x, y, z;
    int a, b;
    if (std::sscanf(line, "node %lf %lf %lf", &x, &y, &z) == 3) {
      return AddNode(x, y, z) >= 0;
    }
    if (std::sscanf(line, "edge %d %d", &a, &b) == 2) {
      return Link(a, b);
    }
    return false;
  }

 private:
  bool Valid(int i) const { return i >= 0 && i < node_count_; }
  bool AddEdge(int from, int to) {
    for (int e = 0; e < edge_count_[from]; ++e) {
      if (edges_[from][e] == to) return true;  // idempotent
    }
    if (edge_count_[from] >= kMaxEdgesPerNode) return false;
    edges_[from][edge_count_[from]++] = to;
    return true;
  }

  double nodes_[kMaxNodes][3];
  int edges_[kMaxNodes][kMaxEdgesPerNode];
  int edge_count_[kMaxNodes];
  int node_count_;
};

/* ------------------------------------------------------------------------ */
/* Phase 4 - stuck detection (replaces nothing; triggers waypoint fallback   */
/* and the native jump pulse)                                                */
/* ------------------------------------------------------------------------ */

class StuckDetector {
 public:
  // stuck = moved less than `min_distance` meters within `window` ticks
  // while a forward move was requested. 40 ticks = 2 s at 20 Hz.
  explicit StuckDetector(int window_ticks = 40, double min_distance = 1.0)
      : window_(window_ticks), min_d2_(min_distance * min_distance) {}

  void Reset() { ticks_ = 0; }

  bool Update(double x, double z, bool moving_requested) {
    if (!moving_requested) {
      ticks_ = 0;
      return false;
    }
    if (ticks_ == 0) {
      ref_x_ = x;
      ref_z_ = z;
    }
    ++ticks_;
    if (ticks_ < window_) return false;
    const double dx = x - ref_x_, dz = z - ref_z_;
    const bool stuck = (dx * dx + dz * dz) < min_d2_;
    ticks_ = 0;  // start the next window either way
    return stuck;
  }

 private:
  int window_;
  double min_d2_;
  int ticks_ = 0;
  double ref_x_ = 0.0, ref_z_ = 0.0;
};

/* ------------------------------------------------------------------------ */
/* Phase 5 - population controller (pure decision step)                      */
/* ------------------------------------------------------------------------ */

struct PopulationInput {
  int max_players;           // gam_ctMaxPlayers of the instance (<= 16)
  int humans;                // currently connected human players
  int bots;                  // currently connected bot players
  int target_population;     // desired total players (humans + bots)
  int reserved_human_slots;  // slots always kept free for humans
};

enum class PopulationAction { kNone, kStartBot, kStopBot };

// Desired bot count: fill up to target_population, but never occupy the
// reserved human slots and never exceed capacity. Humans always win: when a
// human joins and capacity is tight, the controller answers kStopBot.
// One action per step -> the caller applies join/leave pacing (Phase 6).
inline int DesiredBots(const PopulationInput& in) {
  int desired = in.target_population - in.humans;
  const int capacity = in.max_players - in.humans - in.reserved_human_slots;
  if (desired > capacity) desired = capacity;
  if (desired < 0) desired = 0;
  return desired;
}

inline PopulationAction PopulationStep(const PopulationInput& in) {
  const int desired = DesiredBots(in);
  if (in.bots > desired) return PopulationAction::kStopBot;
  if (in.bots < desired &&
      in.humans + in.bots < in.max_players - in.reserved_human_slots) {
    return PopulationAction::kStartBot;
  }
  return PopulationAction::kNone;
}

/* ------------------------------------------------------------------------ */
/* Phase 6 - presence / chat cadence (deterministic, low frequency)          */
/* ------------------------------------------------------------------------ */

class PresenceSchedule {
 public:
  // Seed is mixed with the bot index so no two bots share a pattern.
  PresenceSchedule(uint32_t seed, int bot_index)
      : rng_(seed * 2654435761u + static_cast<uint32_t>(bot_index) * 40503u + 1u) {}

  // Seconds to wait before joining / after leaving (anti-lockstep).
  int JoinDelaySeconds(int min_s = 5, int max_s = 90) {
    return rng_.NextRange(min_s, max_s);
  }
  int LeaveDelaySeconds(int min_s = 2, int max_s = 30) {
    return rng_.NextRange(min_s, max_s);
  }

  // Ticks (20 Hz) until the next chat line; period is jittered +/-50% so the
  // cadence never repeats exactly. base_period_s <= 0 disables chat.
  int NextChatDelayTicks(double base_period_s) {
    if (base_period_s <= 0.0) return -1;
    const int base = static_cast<int>(base_period_s * 20.0 + 0.5);
    const int lo = base / 2 < 1 ? 1 : base / 2;
    const int hi = base + base / 2;
    return rng_.NextRange(lo, hi);
  }

  // Pick a chat line index; avoids immediately repeating the previous line.
  int NextChatLine(int line_count) {
    if (line_count <= 0) return -1;
    if (line_count == 1) return 0;
    int pick = rng_.NextRange(0, line_count - 1);
    if (pick == last_line_) pick = (pick + 1) % line_count;
    last_line_ = pick;
    return pick;
  }

 private:
  Lcg rng_;
  int last_line_ = -1;
};

}  // namespace botcore

#endif  // BOTCORE_AI_H
