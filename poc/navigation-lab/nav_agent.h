// nav_agent.h - engine-free navigation agent for the Navigation 2.0
// prototype. One instance per bot; all instances may share ONE NavGraph
// (read-only) and still behave differently via per-bot seeds.
//
// STATE MACHINE (per 20 Hz tick):
//
//   PATROL      no combat target: pick a patrol destination (unvisited /
//               important / personality-weighted, dead-end averse), route
//               with the budgeted A*, follow it node by node.
//   PURSUE      combat target VISIBLE: hand movement to the combat layer;
//               the agent only steers toward the target position and keeps
//               its route state warm. (The existing HumanBotPolicy keeps
//               authority over aim/strafe/retreat.)
//   REPOSITION  combat target remembered but NOT visible: route to the
//               target's last known position, then SCAN on arrival.
//   SCAN        arrived at a last-known position without contact: hold and
//               look around for scan_ticks, then fall back to PATROL.
//   (RECOVER)   stuck detection does not implement its own avoidance; it
//               raises `stuck` so the CALLER can run the qualified
//               ObstacleRecovery, and it biases the next search away from
//               the node the agent failed to reach.
//
// OUTPUT CONTRACT: the agent returns intent only (desired yaw, rate-limited
// yaw delta, forward factor, mode, telemetry). Converting intent into a
// CPlayerAction stays in BotDriver - identical to the existing
// HumanBotPolicy/BotCommand boundary.
//
// DETERMINISM: every decision derives from the per-bot seed via a small LCG;
// there is no wall clock and no shared mutable state between agents.
//
// LICENSING NOTE: independent implementation. Behavioural ideas (patrol
// destinations ~ "important points", repath cooldown, stuck handling) are
// general game-AI patterns also present in CecilBotMod; no Cecil source was
// copied.

#ifndef NAVLAB_NAV_AGENT_H
#define NAVLAB_NAV_AGENT_H

#include <cmath>
#include <cstdint>

#include "nav_astar.h"
#include "nav_graph.h"

namespace navlab {

constexpr double kNavTickHz = 20.0;
constexpr double kNavPi = 3.14159265358979323846;

enum class NavMode : uint8_t {
  kIdle = 0,   // dead / disabled: no movement intent
  kPatrol,     // following a patrol route
  kPursue,     // visible target: combat layer leads, agent steers loosely
  kReposition, // routing to the target's last known position
  kScan,       // holding at a last-known position, looking around
};

/* ------------------------------------------------------------------------ */
/* Personality                                                               */
/* ------------------------------------------------------------------------ */

struct NavPersonality {
  float explore_bias;        // 0..1  weight of "unvisited" for patrol targets
  float important_bias;      // 0..1  weight of kNodeImportant
  float deadend_aversion;    // 0..1  penalty for leaf nodes
  float route_variance;      // 0..0.5 per-bot edge-cost jitter
  float walk_factor;         // 0.2..1 forward speed fraction
  float patrol_min_dist;     // [m] prefer patrol targets at least this far
  int   repath_cooldown;     // [ticks] minimum between replans to same goal
  int   stuck_window;        // [ticks] observation window (40 = 2 s)
  float stuck_min_dist;      // [m] required progress inside the window
  int   scan_ticks;          // [ticks] scan duration after repositioning
  float turn_rate_deg_s;     // [deg/s] yaw steering limit for route following
  float search_radius;       // [m] node arrival radius floor

  NavPersonality()
      : explore_bias(0.5f), important_bias(0.35f), deadend_aversion(0.5f),
        route_variance(0.12f), walk_factor(1.0f), patrol_min_dist(10.0f),
        repath_cooldown(20), stuck_window(40), stuck_min_dist(1.0f),
        scan_ticks(60), turn_rate_deg_s(240.0f), search_radius(0.9f) {}
};

// Mapping helper for the later integration: derive a NavPersonality from the
// existing botcore PersonalityParams-like values WITHOUT including botcore
// (the seam test performs the actual bridge, keeping this lab standalone).
inline NavPersonality NavPersonalityFromTraits(float aggression, float caution,
                                               float speed_scale,
                                               float turn_rate_deg_s) {
  NavPersonality p;
  const float aggr = aggression < 0.0f ? 0.0f : (aggression > 1.0f ? 1.0f : aggression);
  const float caut = caution < 0.0f ? 0.0f : (caution > 1.0f ? 1.0f : caution);
  p.explore_bias = 0.30f + 0.40f * aggr;              // aggressive explores far
  p.important_bias = 0.25f + 0.30f * caut;            // cautious values objectives
  p.deadend_aversion = 0.25f + 0.60f * caut;          // cautious avoids leaves
  p.patrol_min_dist = 6.0f + 14.0f * aggr;            // aggressive roams wider
  p.walk_factor = speed_scale < 0.2f ? 0.2f : (speed_scale > 1.0f ? 1.0f : speed_scale);
  p.turn_rate_deg_s = turn_rate_deg_s > 30.0f ? turn_rate_deg_s : 30.0f;
  // Route variety is personality-independent by design (per-bot seed does it).
  return p;
}

/* ------------------------------------------------------------------------ */
/* I/O structs                                                               */
/* ------------------------------------------------------------------------ */

struct NavAgentInput {
  int tick;
  double x, y, z;         // current position (engine units = metres)
  double yaw_deg;         // current absolute heading (accumulated convention)
  bool alive;
  bool movement_requested;  // caller actually asked to move last tick (stuck)
  // Combat layer state (from HumanBotPolicy): -1 = no target at all.
  bool has_target;
  bool target_visible;
  double target_x, target_y, target_z;  // live or last-known position
};

struct NavCommand {
  bool active;               // agent wants to drive movement this tick
  double desired_yaw_deg;    // absolute heading the route wants
  double yaw_delta_deg;      // rate-limited delta to apply this tick
  double forward;            // 0..1 (navigation never moves backwards)
  NavMode mode;
  int dest_node;             // patrol destination (-1 when none)
  int route_hops_left;       // nodes remaining on the current route
  bool replanned;            // an A* search ran this tick (telemetry/CPU)
  bool stuck;                // caller should trigger ObstacleRecovery
  bool reached_destination;  // patrol destination reached this tick
  int expanded_last_search;  // A* expansions of the last search (telemetry)

  NavCommand()
      : active(false), desired_yaw_deg(0.0), yaw_delta_deg(0.0), forward(0.0),
        mode(NavMode::kIdle), dest_node(-1), route_hops_left(0),
        replanned(false), stuck(false), reached_destination(false),
        expanded_last_search(0) {}
};

/* ------------------------------------------------------------------------ */
/* The agent                                                                 */
/* ------------------------------------------------------------------------ */

class NavAgent {
 public:
  NavAgent() { Configure(NavPersonality(), 1u); }

  void Configure(const NavPersonality& personality, uint32_t seed) {
    p_ = personality;
    rng_state_ = seed ? seed : 1u;
    search_cfg_.max_expand = 256;
    search_cfg_.variance = p_.route_variance;
    search_cfg_.variance_seed = seed ? seed : 1u;
    Reset();
  }

  void Reset() {
    mode_ = NavMode::kIdle;
    dest_node_ = -1;
    route_len_ = 0;
    route_pos_ = 0;
    last_replan_tick_ = -1000000;
    searched_last_plan_ = false;
    force_replan_ = false;
    steer_err_ = 0.0;
    scan_until_tick_ = -1000000;
    avoid_node_ = -1;
    avoid_until_tick_ = -1000000;
    searches_total_ = 0;
    expansions_total_ = 0;
    stuck_events_ = 0;
    destinations_reached_ = 0;
    last_x_ = last_z_ = 0.0;
    stuck_ticks_ = 0;
    have_pos_ = false;
    last_target_x_ = last_target_z_ = 0.0;
    have_last_target_ = false;
    for (int i = 0; i < kNavMaxNodes; ++i) visits_[i] = 0;
  }

  /* --- telemetry -------------------------------------------------------- */
  int searches_total() const { return searches_total_; }
  int expansions_total() const { return expansions_total_; }
  int stuck_events() const { return stuck_events_; }
  int destinations_reached() const { return destinations_reached_; }
  NavMode mode() const { return mode_; }
  int dest_node() const { return dest_node_; }

  /* --- main step --------------------------------------------------------- */
  NavCommand Step(const NavGraph& graph, const NavAgentInput& in) {
    NavCommand cmd;
    if (!in.alive || graph.node_count() <= 0) {
      mode_ = NavMode::kIdle;
      have_pos_ = false;
      return cmd;
    }

    UpdateStuck(in, cmd);

    // Teleports / map changes: position jumped -> drop route state.
    if (have_pos_) {
      const double dx = in.x - last_x_, dz = in.z - last_z_;
      if (dx * dx + dz * dz > 64.0) {  // > 8 m per tick is not walking
        route_len_ = 0;
        route_pos_ = 0;
        dest_node_ = -1;
        have_pos_ = false;
      }
    }
    last_x_ = in.x;
    last_z_ = in.z;
    have_pos_ = true;

    // Expire the temporary "avoid" bias.
    if (in.tick > avoid_until_tick_) avoid_node_ = -1;

    // ---- mode arbitration ------------------------------------------------
    if (in.has_target && in.target_visible) {
      // PURSUE: the combat layer owns fine movement; we only keep a coarse
      // heading toward the live target so long chases still make progress.
      mode_ = NavMode::kPursue;
      last_target_x_ = in.target_x;
      last_target_z_ = in.target_z;
      have_last_target_ = true;
      SteerTowards(cmd, in, in.target_x, in.target_z);
      cmd.active = true;
      cmd.forward = (steer_err_ > 90.0) ? 0.0 : p_.walk_factor * 0.5;
      cmd.mode = mode_;
      cmd.dest_node = dest_node_;
      cmd.route_hops_left = route_len_ - route_pos_;
      return cmd;
    }

    if (in.has_target && !in.target_visible) {
      // REPOSITION toward the last known position.
      last_target_x_ = in.target_x;
      last_target_z_ = in.target_z;
      have_last_target_ = true;
      const int goal = graph.NearestNode(last_target_x_, last_target_z_);
      if (graph.Valid(goal) && (dest_node_ != goal || force_replan_)) {
        Plan(graph, in, goal);  // may fail; route stays empty
        cmd.replanned = searched_last_plan_;
      }
      if (route_len_ > route_pos_) {
        mode_ = NavMode::kReposition;
        FollowRoute(graph, in, cmd);
        if (route_len_ == 0) {
          // Route consumed this tick: start scanning on the next one.
          mode_ = NavMode::kScan;
          scan_until_tick_ = in.tick + ScanTicks();
        }
      } else if (mode_ == NavMode::kReposition && Arrived(graph, in)) {
        mode_ = NavMode::kScan;
        scan_until_tick_ = in.tick + ScanTicks();
        ScanStep(in, cmd);
      } else {
        // No route available (or already scanning): hold and look around.
        mode_ = NavMode::kScan;
        if (in.tick >= scan_until_tick_) scan_until_tick_ = in.tick + ScanTicks();
        ScanStep(in, cmd);
      }
      cmd.mode = mode_;
      cmd.dest_node = dest_node_;
      cmd.route_hops_left = route_len_ - route_pos_;
      cmd.expanded_last_search = last_search_expanded_;
      return cmd;
    }

    // No combat target.
    if (mode_ == NavMode::kScan && in.tick < scan_until_tick_) {
      ScanStep(in, cmd);
      cmd.mode = mode_;
      return cmd;
    }

    // PATROL.
    mode_ = NavMode::kPatrol;
    if (route_len_ == 0 || route_pos_ >= route_len_) {
      const int goal = ChoosePatrolDestination(graph, in);
      if (goal < 0) {
        cmd.mode = mode_;
        return cmd;  // empty/degenerate graph
      }
      if (!Plan(graph, in, goal)) {
        cmd.replanned = searched_last_plan_;
        cmd.mode = mode_;
        return cmd;
      }
      cmd.replanned = searched_last_plan_;
      cmd.expanded_last_search = last_search_expanded_;
    }
    const bool arrived = FollowRoute(graph, in, cmd);
    if (arrived) ++destinations_reached_;
    cmd.reached_destination = arrived;
    cmd.mode = mode_;
    cmd.dest_node = dest_node_;
    cmd.route_hops_left = route_len_ - route_pos_;
    return cmd;
  }

 private:
  /* --- planning ---------------------------------------------------------- */

  // Run the budgeted A* toward `goal`; honours the repath cooldown unless
  // this is a brand-new destination. Returns false when no route exists.
  bool Plan(const NavGraph& graph, const NavAgentInput& in, int goal) {
    searched_last_plan_ = false;
    if (!graph.Valid(goal)) return false;
    const int start = graph.NearestNode(in.x, in.z);
    if (start < 0) return false;

    const bool same_goal = (goal == dest_node_);
    if (same_goal && !force_replan_ &&
        in.tick - last_replan_tick_ < p_.repath_cooldown) {
      // Cooldown: keep walking the existing route if we still have one.
      return route_len_ > route_pos_;
    }

    const int avoid = avoid_node_;
    NavPath path = RunSearch(graph, start, goal, avoid);
    searched_last_plan_ = true;  // search ran even when it failed
    force_replan_ = false;
    if (path.count <= 0) return false;

    for (int i = 0; i < path.count && i < kNavMaxPathNodes; ++i) {
      route_[i] = path.nodes[i];
    }
    route_len_ = path.count;
    route_pos_ = 0;
    dest_node_ = goal;
    last_replan_tick_ = in.tick;
    last_search_expanded_ = path.expanded;
    ++searches_total_;
    expansions_total_ += path.expanded;
    MarkVisited(route_[route_len_ - 1]);
    return true;
  }

  NavPath RunSearch(const NavGraph& graph, int start, int goal, int avoid) {
    if (avoid >= 0 && avoid != goal) {
      // Penalise edges entering the avoid node by running the search with a
      // temporary cost override: we cannot mutate the shared graph, so we
      // perform the search and, if the resulting first hop is the avoid node,
      // retry with the avoid node's edges conceptually removed via a higher
      // variance-free deterministic tie push (lower budget keeps it cheap).
      NavPath first = search_.Find(graph, start, goal, search_cfg_);
      if (first.count >= 2 && first.nodes[1] == avoid) {
        // Deterministic reroute: search from start but forbid the first hop
        // by seeding a per-search variance that keeps costs stable while we
        // temporarily mark the edge blocked in a local edge-mask search.
        NavPath alt = SearchAvoiding(graph, start, goal, avoid);
        if (alt.count >= 2 && alt.nodes[1] != avoid) return alt;
      }
      return first;
    }
    return search_.Find(graph, start, goal, search_cfg_);
  }

  // Second-chance search that skips the first hop into `avoid`. Implemented
  // without touching the shared graph: try A* from each other neighbour of
  // start and prepend that neighbour. Deterministic (neighbours in index
  // order, budgeted).
  NavPath SearchAvoiding(const NavGraph& graph, int start, int goal,
                         int avoid) {
    NavPath best;
    best.status = NavSearchStatus::kInvalidArgs;
    best.count = 0;
    best.cost = 0.0f;
    best.expanded = 0;
    const int count = graph.edge_count(start);
    for (int e = 0; e < count; ++e) {
      const NavEdge& edge = graph.edge(start, e);
      if (edge.flags & kEdgeBlocked) continue;
      const int next = edge.to;
      if (next == avoid || !graph.Valid(next)) continue;
      NavPath sub = search_.Find(graph, next, goal, search_cfg_);
      if (sub.count <= 0) continue;
      if (best.count == 0 || sub.cost < best.cost) {
        best = sub;
        // Prepend the start node (shift right, keep within capacity).
        if (best.count < kNavMaxPathNodes) {
          for (int i = best.count; i > 0; --i) best.nodes[i] = best.nodes[i - 1];
          best.nodes[0] = static_cast<int16_t>(start);
          ++best.count;
        }
      }
    }
    return best;
  }

  /* --- patrol destination choice ----------------------------------------- */

  // Score every node once; pick the best deterministically. O(N) per
  // destination choice (not per tick) - negligible at 20 Hz.
  int ChoosePatrolDestination(const NavGraph& graph, const NavAgentInput& in) {
    int best = -1;
    double best_score = -1e30;
    const int n = graph.node_count();
    uint8_t max_visits = 1;
    for (int i = 0; i < n; ++i) {
      if (visits_[i] > max_visits) max_visits = visits_[i];
    }
    for (int i = 0; i < n; ++i) {
      const NavNode& node = graph.node(i);
      if (node.degree == 0 && !(node.flags & kNodeImportant)) continue;
      const double dx = node.x - in.x, dz = node.z - in.z;
      const double dist = std::sqrt(dx * dx + dz * dz);
      if (dist < 2.0) continue;  // never target the node we stand on

      double score = 0.0;
      // Unvisited / rarely visited first.
      const double freshness =
          1.0 - static_cast<double>(visits_[i]) / static_cast<double>(max_visits);
      score += p_.explore_bias * freshness;
      // Important nodes.
      if (node.flags & kNodeImportant) score += p_.important_bias;
      // Distance: reward patrol_min_dist, saturate beyond 3x.
      const double d_norm = dist / (p_.patrol_min_dist > 1.0 ? p_.patrol_min_dist : 1.0);
      score += 0.35 * (d_norm < 3.0 ? d_norm / 3.0 : 1.0);
      // Dead ends are disliked (unless they are important).
      if ((node.flags & kNodeDeadEnd) && !(node.flags & kNodeImportant)) {
        score -= p_.deadend_aversion;
      }
      // Spawn points are boring patrol targets.
      if (node.flags & kNodeSpawn) score -= 0.15;
      // Deterministic tie-break: lower index wins (strict >).
      if (score > best_score) {
        best_score = score;
        best = i;
      }
    }
    return best;
  }

  /* --- route following ---------------------------------------------------- */

  // Advance along the current route; returns true when the FINAL destination
  // was reached this tick.
  bool FollowRoute(const NavGraph& graph, const NavAgentInput& in,
                   NavCommand& cmd) {
    if (route_len_ == 0 || route_pos_ >= route_len_) return false;

    // Advance past nodes we have reached (or overshot). "Passed" is tested
    // geometrically: projection of the bot onto the route segment
    // prev->current beyond the current node (t > 1). Facing-based rules
    // misfire here twice: a fresh route may start opposite to the current
    // heading (everything reads "behind"), and with a turn radius larger
    // than the arrival circle a distance-only test lets the agent orbit a
    // waypoint forever.
    bool reached_final = false;
    while (route_pos_ < route_len_) {
      const NavNode& node = graph.node(route_[route_pos_]);
      const double dx = node.x - in.x, dz = node.z - in.z;
      const double reach = node.radius > p_.search_radius ? node.radius
                                                           : p_.search_radius;
      const double d2 = dx * dx + dz * dz;
      bool passed = false;
      if (route_pos_ > 0) {
        const NavNode& prev = graph.node(route_[route_pos_ - 1]);
        const double sx = node.x - prev.x, sz = node.z - prev.z;
        const double bx = in.x - prev.x, bz = in.z - prev.z;
        const double seg2 = sx * sx + sz * sz;
        if (seg2 > 1e-9) passed = ((bx * sx + bz * sz) / seg2) > 1.0;
      }
      if (d2 <= reach * reach || passed) {
        MarkVisited(route_[route_pos_]);
        ++route_pos_;
        if (route_pos_ >= route_len_) {
          reached_final = true;
          break;
        }
      } else {
        break;
      }
    }
    if (route_pos_ >= route_len_) {
      route_len_ = 0;
      route_pos_ = 0;
      cmd.forward = 0.0;
      return reached_final;
    }

    const NavNode& next = graph.node(route_[route_pos_]);
    SteerTowards(cmd, in, next.x, next.z);
    cmd.active = true;
    // Turn in place while the heading error is large: walking through big
    // turns arcs the bot off the corridor (and can capture it in an orbit
    // when the turn radius exceeds the waypoint arrival radius).
    cmd.forward = (steer_err_ > 60.0) ? 0.0 : p_.walk_factor;
    return reached_final;
  }

  // Rate-limited yaw steering toward a planar point (absolute-angle
  // convention identical to botcore: yaw = atan2(-dx, -dz)).
  void SteerTowards(NavCommand& cmd, const NavAgentInput& in, double tx,
                    double tz) {
    const double dx = tx - in.x, dz = tz - in.z;
    const double desired = std::atan2(-dx, -dz) * (180.0 / kNavPi);
    cmd.desired_yaw_deg = desired;
    double delta = desired - in.yaw_deg;
    while (delta > 180.0) delta -= 360.0;
    while (delta < -180.0) delta += 360.0;
    steer_err_ = delta < 0.0 ? -delta : delta;
    const double limit = p_.turn_rate_deg_s / kNavTickHz;
    cmd.yaw_delta_deg = delta < -limit ? -limit : (delta > limit ? limit : delta);
    cmd.desired_yaw_deg = in.yaw_deg + cmd.yaw_delta_deg;
  }

  bool Arrived(const NavGraph& graph, const NavAgentInput& in) {
    if (route_len_ == 0) {
      // Direct check against the destination node (post-plan arrival).
      if (!graph.Valid(dest_node_)) return false;
      const NavNode& node = graph.node(dest_node_);
      const double dx = node.x - in.x, dz = node.z - in.z;
      const double reach = node.radius > p_.search_radius ? node.radius
                                                           : p_.search_radius;
      return dx * dx + dz * dz <= reach * reach;
    }
    return false;
  }

  void ScanStep(const NavAgentInput& in, NavCommand& cmd) {
    // Slow deterministic scan rotation; no forward movement.
    cmd.active = true;
    cmd.forward = 0.0;
    cmd.yaw_delta_deg = 3.0;  // 60 deg/s scan
    cmd.desired_yaw_deg = in.yaw_deg + cmd.yaw_delta_deg;
  }

  int ScanTicks() const { return p_.scan_ticks > 0 ? p_.scan_ticks : 20; }

  /* --- stuck detection (same semantics as botcore StuckDetector) --------- */

  void UpdateStuck(const NavAgentInput& in, NavCommand& cmd) {
    if (!in.movement_requested) {
      stuck_ticks_ = 0;
      return;
    }
    if (stuck_ticks_ == 0) {
      stuck_ref_x_ = in.x;
      stuck_ref_z_ = in.z;
    }
    ++stuck_ticks_;
    const int window = p_.stuck_window > 1 ? p_.stuck_window : 2;
    if (stuck_ticks_ < window) return;
    const double dx = in.x - stuck_ref_x_, dz = in.z - stuck_ref_z_;
    const double min_d = p_.stuck_min_dist > 0.0f ? p_.stuck_min_dist : 0.5f;
    const bool stuck = (dx * dx + dz * dz) < min_d * min_d;
    stuck_ticks_ = 0;
    if (!stuck) return;

    // Stuck: raise the flag, bias the next plan away from the node ahead,
    // and force a replan as soon as the caller's recovery finished.
    ++stuck_events_;
    cmd.stuck = true;
    if (route_pos_ < route_len_) {
      avoid_node_ = route_[route_pos_];
      avoid_until_tick_ = in.tick + 5 * static_cast<int>(kNavTickHz);
    }
    last_replan_tick_ = -1000000;  // allow an immediate replan
    force_replan_ = true;
    route_len_ = 0;
    route_pos_ = 0;
  }

  void MarkVisited(int node) {
    if (node >= 0 && node < kNavMaxNodes && visits_[node] < 250) ++visits_[node];
  }

  /* --- state -------------------------------------------------------------- */
  NavPersonality p_;
  NavAStar search_;
  NavSearchConfig search_cfg_;
  uint32_t rng_state_;  // reserved for future jittered patrol sampling

  NavMode mode_;
  int dest_node_;
  int16_t route_[kNavMaxPathNodes];
  int route_len_;
  int route_pos_;
  int last_replan_tick_;
  bool searched_last_plan_;  // telemetry: a search really ran
  bool force_replan_;        // set by stuck handler: bypass goal memo+cooldown
  double steer_err_;         // [deg] absolute heading error of the last steer
  int scan_until_tick_;
  int avoid_node_;
  int avoid_until_tick_;
  int last_search_expanded_;

  // Stuck detector state.
  int stuck_ticks_;
  double stuck_ref_x_, stuck_ref_z_;
  double last_x_, last_z_;
  bool have_pos_;
  double last_target_x_, last_target_z_;
  bool have_last_target_;

  uint8_t visits_[kNavMaxNodes];

  // Telemetry.
  int searches_total_;
  int expansions_total_;
  int stuck_events_;
  int destinations_reached_;
};

}  // namespace navlab

#endif  // NAVLAB_NAV_AGENT_H
