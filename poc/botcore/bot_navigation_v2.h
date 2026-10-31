// bot_navigation_v2.h - engine-free global navigation, item utility and pit
// avoidance for the vanilla bot client.
//
// SCOPE
//  - This layer is *optional*. The existing HumanBotPolicy keeps full ownership
//    of target selection, aiming and combat. NavigationV2 only proposes a
//    movement direction when the bot has no visible target, is retreating, or
//    explicitly wants to collect an item.
//  - All geometry knowledge is supplied by the caller (waypoint graph, floor
//    ray distances, item positions). No engine calls, no allocation, fully
//    deterministic.
//  - CecilBotMod concepts are used as inspiration only: explicit waypoints,
//    A* over edges, item desirability, pit probes. No Cecil code is copied.
//
// UNITS: metres, degrees, seconds, 20 Hz ticks.

#ifndef BOTCORE_BOT_NAVIGATION_V2_H
#define BOTCORE_BOT_NAVIGATION_V2_H

#include <cmath>
#include <cstdint>

#include "bot_profile.h"
#include "botcore_ai.h"

namespace botcore {

/* ------------------------------------------------------------------------ */
/* World snapshot supplied by the caller                                    */
/* ------------------------------------------------------------------------ */

struct NavWorld {
  double x = 0.0, y = 0.0, z = 0.0;  // eye position
  double yaw_deg = 0.0;              // current heading
  double health = 100.0;
  double max_health = 100.0;
  bool alive = false;
  bool has_target = false;  // if true, navigation should not fight for control
  double target_distance_m = 0.0;
};

struct NavCommand {
  bool active = false;          // true if navigation wants to override movement
  double yaw_delta_deg = 0.0;   // suggested heading change
  double forward = 0.0;         // -1..+1
  double strafe = 0.0;          // -1..+1
  int goal_waypoint = -1;       // current goal node, for telemetry
  int next_waypoint = -1;       // next hop node, for telemetry
  enum class Mode {
    kIdle = 0,
    kPathToWaypoint = 1,
    kFetchItem = 2,
    kRetreat = 3,
    kAvoidPit = 4
  } mode = Mode::kIdle;
};

/* ------------------------------------------------------------------------ */
/* A* pathfinding over the existing WaypointGraph                           */
/* ------------------------------------------------------------------------ */

class AStarPathfinder {
 public:
  // Returns true if a path from start to goal was found. `path` receives node
  // indices; path[0] == start, path[*len-1] == goal. `max_len` bounds writes.
  //
  // Implementation note: WaypointGraph's public API exposes NextHop (BFS)
  // but not a neighbour iterator. For the small graphs used in TSE bot
  // navigation we therefore run A* with a neighbour probe that scans all
  // nodes and asks NextHop(n,m)==m. This is O(n^2) but robust and keeps the
  // graph class unchanged.
  bool FindPath(const WaypointGraph& graph, int start, int goal,
                int* path, int* len, int max_len) const {
    if (len) *len = 0;
    if (path == nullptr || len == nullptr || max_len <= 0) return false;
    if (start == goal) {
      if (max_len > 0) { path[0] = start; *len = 1; }
      return true;
    }
    {
      double tx, ty, tz;
      if (!graph.NodePosition(start, &tx, &ty, &tz) ||
          !graph.NodePosition(goal, &tx, &ty, &tz)) {
        return false;
      }
    }

    const int n = graph.node_count();
    if (n <= 0 || n > WaypointGraph::kMaxNodes) return false;

    static const int kInf = 0x3f3f3f3f;
    int g_score[WaypointGraph::kMaxNodes];
    int f_score[WaypointGraph::kMaxNodes];
    int parent[WaypointGraph::kMaxNodes];
    bool visited[WaypointGraph::kMaxNodes];
    int heap[WaypointGraph::kMaxNodes];
    int heap_idx[WaypointGraph::kMaxNodes];
    int heap_size = 0;

    for (int i = 0; i < n; ++i) {
      g_score[i] = kInf;
      f_score[i] = kInf;
      parent[i] = -1;
      visited[i] = false;
      heap_idx[i] = -1;
    }

    g_score[start] = 0;
    f_score[start] = Heuristic(graph, start, goal);
    HeapPush(start, f_score[start], heap, heap_idx, heap_size);

    while (heap_size > 0) {
      int current = HeapPop(heap, heap_idx, heap_size, f_score);
      if (current < 0) break;
      if (visited[current]) continue;
      visited[current] = true;
      if (current == goal) {
        ReconstructPath(parent, start, goal, path, len, max_len);
        return *len > 0;
      }

      for (int next = 0; next < n; ++next) {
        if (visited[next] || next == current) continue;
        // NextHop returns `next` iff current and next are directly linked.
        if (graph.NextHop(current, next) != next) continue;

        const int edge_cost = EdgeCost(graph, current, next);
        const int tentative = g_score[current] + edge_cost;
        if (tentative < g_score[next]) {
          parent[next] = current;
          g_score[next] = tentative;
          f_score[next] = tentative + Heuristic(graph, next, goal);
          if (heap_idx[next] < 0) {
            HeapPush(next, f_score[next], heap, heap_idx, heap_size);
          } else {
            HeapifyUp(heap_idx[next], heap, heap_idx, f_score);
          }
        }
      }
    }
    return false;
  }

 private:
  static void SwapHeap(int a, int b, int* heap, int* idx) {
    int na = heap[a];
    int nb = heap[b];
    heap[a] = nb;
    heap[b] = na;
    idx[na] = b;
    idx[nb] = a;
  }

  static void HeapPush(int node, int f, int* heap, int* idx, int& size) {
    int pos = size++;
    heap[pos] = node;
    idx[node] = pos;
    HeapifyUp(pos, heap, idx, &f);
  }

  static void HeapifyUp(int pos, int* heap, int* idx, const int* f_score) {
    while (pos > 0) {
      int p = (pos - 1) / 2;
      if (f_score[heap[p]] <= f_score[heap[pos]]) break;
      SwapHeap(pos, p, heap, idx);
      pos = p;
    }
  }

  static void HeapifyDown(int pos, int* heap, int* idx, int size, const int* f_score) {
    while (true) {
      int l = 2 * pos + 1;
      int r = 2 * pos + 2;
      int smallest = pos;
      if (l < size && f_score[heap[l]] < f_score[heap[smallest]]) smallest = l;
      if (r < size && f_score[heap[r]] < f_score[heap[smallest]]) smallest = r;
      if (smallest == pos) break;
      SwapHeap(pos, smallest, heap, idx);
      pos = smallest;
    }
  }

  static int HeapPop(int* heap, int* idx, int& size, const int* f_score) {
    if (size == 0) return -1;
    int best = heap[0];
    idx[best] = -1;
    heap[0] = heap[--size];
    if (size > 0) {
      idx[heap[0]] = 0;
      HeapifyDown(0, heap, idx, size, f_score);
    }
    return best;
  }

  static int Heuristic(const WaypointGraph& graph, int a, int b) {
    double ax, ay, az, bx, by, bz;
    if (!graph.NodePosition(a, &ax, &ay, &az) ||
        !graph.NodePosition(b, &bx, &by, &bz)) {
      return 0;
    }
    const double dx = ax - bx, dy = ay - by, dz = az - bz;
    return static_cast<int>(std::sqrt(dx * dx + dy * dy + dz * dz) * 100.0 + 0.5);
  }

  static int EdgeCost(const WaypointGraph& graph, int a, int b) {
    double ax, ay, az, bx, by, bz;
    if (!graph.NodePosition(a, &ax, &ay, &az) ||
        !graph.NodePosition(b, &bx, &by, &bz)) {
      return 10000;
    }
    const double dx = ax - bx, dy = ay - by, dz = az - bz;
    return static_cast<int>(std::sqrt(dx * dx + dy * dy + dz * dz) * 100.0 + 0.5);
  }

  static void ReconstructPath(const int* parent, int start, int goal,
                              int* path, int* len, int max_len) {
    int tmp[WaypointGraph::kMaxNodes];
    int count = 0;
    int at = goal;
    while (count < WaypointGraph::kMaxNodes) {
      tmp[count++] = at;
      if (at == start || parent[at] < 0) break;
      at = parent[at];
    }
    if (count == 0 || tmp[count - 1] != start) {
      *len = 0;
      return;
    }
    int out = count < max_len ? count : max_len;
    for (int i = 0; i < out; ++i) path[i] = tmp[count - 1 - i];
    *len = out;
  }
};

/* ------------------------------------------------------------------------ */
/* Pit avoidance: caller supplies floor distances in a few probe directions */
/* ------------------------------------------------------------------------ */

struct FloorProbes {
  double front_m = 1.0e6;   // distance to floor straight ahead
  double left_m = 1.0e6;    // distance to floor 45 deg left
  double right_m = 1.0e6;   // distance to floor 45 deg right
  double step_m = 1.2;      // how far the bot would move in one tick
};

class PitAvoidance {
 public:
  // Returns a yaw delta to steer away from a detected pit, or 0 if the current
  // heading is safe. `threshold_m` is the minimum acceptable floor distance.
  double Avoid(const NavWorld& w, const FloorProbes& p, double threshold_m = 2.0) const {
    if (!w.alive) return 0.0;
    if (p.front_m >= threshold_m && p.left_m >= threshold_m && p.right_m >= threshold_m) {
      return 0.0;
    }
    // Front is unsafe: prefer the side with more floor. If both sides are bad,
    // turn back (180 deg) via the shortest rotation.
    bool front_bad = p.front_m < threshold_m;
    bool left_bad = p.left_m < threshold_m;
    bool right_bad = p.right_m < threshold_m;

    if (front_bad) {
      if (!left_bad && right_bad) return -45.0;  // steer left
      if (!right_bad && left_bad) return +45.0;  // steer right
      if (!left_bad && !right_bad) {
        return p.left_m >= p.right_m ? -45.0 : +45.0;
      }
      return 180.0;  // turn back
    }
    // Front is okay but one diagonal is not: nudge away from the drop.
    if (left_bad && !right_bad) return +22.5;
    if (right_bad && !left_bad) return -22.5;
    return 0.0;
  }

  // True if the bot should not move forward at all this tick.
  bool BlockForward(const NavWorld& w, const FloorProbes& p, double threshold_m = 2.0) const {
    (void)w;
    return p.front_m < p.step_m || p.front_m < threshold_m * 0.5;
  }
};

/* ------------------------------------------------------------------------ */
/* Item utility: choose pickups based on need, distance and danger          */
/* ------------------------------------------------------------------------ */

enum class ItemType { kHealth = 0, kArmor = 1, kWeapon = 2, kAmmo = 3, kPowerup = 4 };

struct ItemInfo {
  int index = -1;
  double x = 0.0, y = 0.0, z = 0.0;
  ItemType type = ItemType::kAmmo;
  double value = 0.0;       // e.g. health points, ammo count
  double max_value = 1.0;   // for normalising need
  bool reachable = true;    // caller can mark items behind walls/closed doors
};

class ItemUtility {
 public:
  void Configure(const BotProfile* profile) { profile_ = profile; }

  double ScoreItem(const ItemInfo& item, const NavWorld& w) const {
    if (!item.reachable || item.value <= 0.0 || !std::isfinite(item.value)) return 0.0;
    const double dx = item.x - w.x;
    const double dy = item.y - w.y;
    const double dz = item.z - w.z;
    const double dist = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (!(dist > 0.0)) return 0.0;

    double need = NeedFor(item, w);
    if (need <= 0.0) return 0.0;

    // Critical health makes medkits dramatically more attractive.
    const double health_frac = w.max_health > 0.0 ? w.health / w.max_health : 1.0;
    if (item.type == ItemType::kHealth && health_frac < 0.5) {
      need *= 1.0 + 2.0 * (0.5 - health_frac);  // up to 2x at zero health
    }

    double score = need * 100.0 / (dist + 5.0);
    // Personality modifiers.
    if (profile_) {
      if (item.type == ItemType::kHealth && profile_->personality.caution > 0.5) {
        score *= 1.25;
      }
      if (item.type == ItemType::kWeapon && profile_->personality.aggression > 0.7) {
        score *= 1.15;
      }
      if (item.type == ItemType::kAmmo && profile_->personality.range_preference > 0.3) {
        score *= 1.1;
      }
    }
    return score;
  }

  int SelectBestItem(const ItemInfo* items, int count, const NavWorld& w) const {
    int best = -1;
    double best_score = 0.0;
    for (int i = 0; i < count; ++i) {
      const double s = ScoreItem(items[i], w);
      if (s > best_score) {
        best_score = s;
        best = i;
      }
    }
    return best;
  }

 private:
  static double NeedFor(const ItemInfo& item, const NavWorld& w) {
    switch (item.type) {
      case ItemType::kHealth:
        if (w.max_health <= 0.0) return 0.0;
        return 1.0 - (w.health / w.max_health);
      case ItemType::kArmor:
        return 0.6;  // always useful if available
      case ItemType::kWeapon:
        return 0.8;
      case ItemType::kAmmo:
        return 0.5;
      case ItemType::kPowerup:
        return 0.9;
    }
    return 0.0;
  }

  const BotProfile* profile_ = nullptr;
};

/* ------------------------------------------------------------------------ */
/* Navigation planner: combines pathfinding, pit avoidance and item utility */
/* ------------------------------------------------------------------------ */

class NavigationPlanner {
 public:
  void Configure(const BotProfile* profile, const WaypointGraph* graph) {
    profile_ = profile;
    graph_ = graph;
    item_utility_.Configure(profile);
    current_path_len_ = 0;
    path_index_ = 0;
    stuck_.Reset();
    last_x_ = last_z_ = 0.0;
    have_last_ = false;
    mode_ = NavCommand::Mode::kIdle;
    cooldown_ticks_ = 0;
  }

  void Reset() {
    current_path_len_ = 0;
    path_index_ = 0;
    stuck_.Reset();
    have_last_ = false;
    mode_ = NavCommand::Mode::kIdle;
    cooldown_ticks_ = 0;
  }

  // Main entry. `items` may be nullptr if none are known.
  NavCommand Update(const NavWorld& w, const ItemInfo* items, int item_count,
                    const FloorProbes& probes, bool retreat_requested) {
    NavCommand cmd;
    if (!w.alive) { Reset(); return cmd; }

    if (cooldown_ticks_ > 0) --cooldown_ticks_;

    // Combat always wins unless we are retreating or have no target.
    if (w.has_target && !retreat_requested) {
      Reset();
      return cmd;
    }

    UpdateStuck(w);

    // 1. Retreat mode: move to the safest known waypoint away from danger.
    if (retreat_requested) {
      cmd = FollowPathOrSearch(w, probes, /*away_from_target*/ true,
                               NavCommand::Mode::kRetreat);
      return cmd;
    }

    // 2. Item fetch: only if health/ammo need is high and an item is known.
    if (items != nullptr && item_count > 0 && ShouldFetchItem(w)) {
      const int best_item = item_utility_.SelectBestItem(items, item_count, w);
      if (best_item >= 0) {
        cmd = NavigateToPoint(w, items[best_item].x, items[best_item].y, items[best_item].z,
                              NavCommand::Mode::kFetchItem);
        if (cmd.active) return ApplyPitAvoidance(cmd, w, probes);
      }
    }

    // 3. Patrolling / area control: move toward a semi-random waypoint.
    cmd = FollowPathOrSearch(w, probes, /*away_from_target*/ false,
                             NavCommand::Mode::kPathToWaypoint);
    return cmd;
  }

 private:
  void UpdateStuck(const NavWorld& w) {
    if (have_last_) {
      const double dx = w.x - last_x_;
      const double dz = w.z - last_z_;
      const double d2 = dx * dx + dz * dz;
      if (d2 > 64.0) {  // teleport / respawn
        stuck_.Reset();
        current_path_len_ = 0;
      }
    }
    last_x_ = w.x;
    last_z_ = w.z;
    have_last_ = true;
  }

  bool ShouldFetchItem(const NavWorld& w) const {
    if (profile_ == nullptr) return false;
    const double health_frac = w.max_health > 0.0 ? w.health / w.max_health : 1.0;
    if (health_frac < 0.55) return true;
    if (profile_->personality.aggression < 0.35 && health_frac < 0.75) return true;
    return false;
  }

  NavCommand FollowPathOrSearch(const NavWorld& w, const FloorProbes& probes,
                                bool away_from_target,
                                NavCommand::Mode explicit_mode = NavCommand::Mode::kPathToWaypoint) {
    NavCommand cmd;
    if (graph_ == nullptr || graph_->node_count() <= 0) {
      // No graph: scan in place, do not walk blindly.
      cmd.active = false;
      return cmd;
    }

    mode_ = explicit_mode;

    // Replan if path empty or stuck.
    bool replan = (current_path_len_ == 0 || path_index_ >= current_path_len_ ||
                   stuck_.Update(w.x, w.z, true));
    if (replan) {
      int start = graph_->NearestNode(w.x, w.y, w.z);
      int goal = PickGoal(w, away_from_target);
      if (start >= 0 && goal >= 0 && start != goal) {
        AStarPathfinder pf;
        if (pf.FindPath(*graph_, start, goal, current_path_, &current_path_len_,
                        kMaxPath)) {
          path_index_ = 0;
        } else {
          current_path_len_ = 0;
        }
      }
      stuck_.Reset();
    }

    // Skip waypoints we are already on top of (including the start node).
    while (path_index_ < current_path_len_) {
      double nx, ny, nz;
      if (!graph_->NodePosition(current_path_[path_index_], &nx, &ny, &nz)) break;
      const double dx = nx - w.x;
      const double dz = nz - w.z;
      if (std::sqrt(dx * dx + dz * dz) > 2.0) break;
      ++path_index_;
    }

    if (current_path_len_ > 0 && path_index_ < current_path_len_) {
      const int next = current_path_[path_index_];
      double nx, ny, nz;
      if (graph_->NodePosition(next, &nx, &ny, &nz)) {
        cmd = SteerTo(w, nx, ny, nz, mode_);
        cmd.goal_waypoint = current_path_[current_path_len_ - 1];
        cmd.next_waypoint = next;
      }
    }
    return ApplyPitAvoidance(cmd, w, probes);
  }

  int PickGoal(const NavWorld& w, bool away_from_target) const {
    if (graph_ == nullptr || graph_->node_count() <= 0) return -1;
    int best = -1;
    double best_score = -1.0e30;
    for (int i = 0; i < graph_->node_count(); ++i) {
      double ix, iy, iz;
      if (!graph_->NodePosition(i, &ix, &iy, &iz)) continue;
      const double dx = ix - w.x;
      const double dz = iz - w.z;
      const double d2 = dx * dx + dz * dz;
      if (d2 < 4.0) continue;  // already there
      double score = std::sqrt(d2);
      if (away_from_target && w.has_target && w.target_distance_m > 0.0) {
        // Prefer nodes that increase distance to the current threat.
        score += d2 / (w.target_distance_m + 1.0);
      }
      // Deterministic tie-breaker using seed.
      if (profile_ != nullptr) {
        score += static_cast<double>((profile_->seed + i) % 1000u) * 0.001;
      }
      if (score > best_score) {
        best_score = score;
        best = i;
      }
    }
    return best;
  }

  NavCommand NavigateToPoint(const NavWorld& w, double tx, double ty, double tz,
                             NavCommand::Mode mode) {
    NavCommand cmd;
    if (graph_ != nullptr && graph_->node_count() > 0) {
      int start = graph_->NearestNode(w.x, w.y, w.z);
      int goal = graph_->NearestNode(tx, ty, tz);
      if (start >= 0 && goal >= 0 && start != goal) {
        AStarPathfinder pf;
        if (pf.FindPath(*graph_, start, goal, current_path_, &current_path_len_, kMaxPath)) {
          path_index_ = 0;
          return FollowPathOrSearch(w, FloorProbes(), /*away*/ false, mode);
        }
      }
    }
    // Direct steering if no graph.
    cmd = SteerTo(w, tx, ty, tz, mode);
    return cmd;
  }

  static NavCommand SteerTo(const NavWorld& w, double tx, double /*ty*/, double tz,
                            NavCommand::Mode mode) {
    NavCommand cmd;
    const double dx = tx - w.x;
    const double dz = tz - w.z;
    const double horiz = std::sqrt(dx * dx + dz * dz);
    if (horiz < 0.5) return cmd;

    const double desired_yaw = std::atan2(-dx, -dz) * kRadToDeg;
    double yaw_err = desired_yaw - w.yaw_deg;
    while (yaw_err > 180.0) yaw_err -= 360.0;
    while (yaw_err < -180.0) yaw_err += 360.0;
    const double max_turn = 9.0;  // deg/tick
    cmd.yaw_delta_deg = yaw_err < -max_turn ? -max_turn
                        : yaw_err > max_turn ? max_turn
                                             : yaw_err;
    cmd.forward = std::fabs(yaw_err) < 20.0 ? 1.0 : 0.0;
    cmd.active = true;
    cmd.mode = mode;
    return cmd;
  }

  static NavCommand ApplyPitAvoidance(NavCommand cmd, const NavWorld& w,
                                      const FloorProbes& probes) {
    if (!cmd.active) return cmd;
    PitAvoidance pit;
    const double avoid = pit.Avoid(w, probes);
    if (avoid != 0.0) {
      cmd.yaw_delta_deg += avoid;
      while (cmd.yaw_delta_deg > 180.0) cmd.yaw_delta_deg -= 360.0;
      while (cmd.yaw_delta_deg < -180.0) cmd.yaw_delta_deg += 360.0;
      if (pit.BlockForward(w, probes)) cmd.forward = 0.0;
      cmd.mode = NavCommand::Mode::kAvoidPit;
    }
    return cmd;
  }

  static constexpr int kMaxPath = 256;

  const BotProfile* profile_ = nullptr;
  const WaypointGraph* graph_ = nullptr;
  ItemUtility item_utility_;
  StuckDetector stuck_{80, 0.75};  // 4 s window, 0.75 m min movement
  int current_path_[kMaxPath];
  int current_path_len_ = 0;
  int path_index_ = 0;
  double last_x_ = 0.0, last_z_ = 0.0;
  bool have_last_ = false;
  NavCommand::Mode mode_ = NavCommand::Mode::kIdle;
  int cooldown_ticks_ = 0;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_NAVIGATION_V2_H
