// SPDX-License-Identifier: GPL-2.0-only
// nav_goal_sink.h - concrete `itemai::NavigationSink` backed by Navigation 2.0
// (`navlab::NavGraph` + budgeted A* + local stuck-edge avoidance).
//
// RESPONSIBILITIES (Navigation side of the hard seam)
//  - Translates `itemai::NavGoal` into budgeted A* routes over `NavGraph`.
//  - Reports honest status (`kAccepted`, `kInProgress`, `kArrived`,
//    `kUnreachable`, `kStalled`, `kExpired`, `kAborted`, `kRejected`).
//  - Distinguishes provable graph unreachability (`kUnreachable`) from per-tick
//    search budget limits (`kBudgetExhausted` -> incremental partial routes).
//  - Couples stuck / wall-blockage events with per-agent blocked-edge memory
//    so alternative corridors are found without mutating `const NavGraph`.
//  - Never chooses items, never scores utility, never fires or changes weapons.

#ifndef NAV_ITEM_BRIDGE_NAV_GOAL_SINK_H
#define NAV_ITEM_BRIDGE_NAV_GOAL_SINK_H

#include <cmath>
#include <cstdint>

#include "nav_cost_cache.h"

namespace navbridge {

struct GoalMoveCommand {
  bool active;
  double desired_yaw_deg;
  double yaw_delta_deg;
  double forward;
  bool jump_hint;
  bool stuck;
  bool replanned;
  int goal_id;
  int dest_node;
  int next_node;
  int route_hops_left;
  double path_remaining_m;
  int expanded_last_search;

  GoalMoveCommand()
      : active(false),
        desired_yaw_deg(0.0),
        yaw_delta_deg(0.0),
        forward(0.0),
        jump_hint(false),
        stuck(false),
        replanned(false),
        goal_id(-1),
        dest_node(-1),
        next_node(-1),
        route_hops_left(0),
        path_remaining_m(-1.0),
        expanded_last_search(0) {}
};

class NavGraphSink : public itemai::NavigationSink {
 public:
  NavGraphSink() {
    Configure(BridgeBudgetConfig(), navlab::NavPersonality(), 1u);
  }

  void Configure(const BridgeBudgetConfig& budget_cfg,
                 const navlab::NavPersonality& nav_persona, uint32_t seed) {
    cfg_ = budget_cfg;
    persona_ = nav_persona;
    seed_ = seed ? seed : 1u;
    Reset();
  }

  void Reset() {
    graph_ = nullptr;
    graph_epoch_ = 1u;
    tick_ = 0;
    bot_pos_ = MakeVec3(0.0, 0.0, 0.0);
    bot_yaw_deg_ = 0.0;
    true_items_ = nullptr;
    tick_budget_ = nullptr;
    local_blocked_ = nullptr;

    active_ = false;
    goal_ = itemai::NavGoal();
    true_pos_ = MakeVec3(0.0, 0.0, 0.0);
    status_ = itemai::NavStatus::kIdle;
    last_terminal_id_ = -1;
    last_terminal_status_ = itemai::NavStatus::kIdle;

    goal_node_ = -1;
    route_len_ = 0;
    route_pos_ = 0;
    partial_route_ = false;
    planned_epoch_ = 0;
    last_search_expanded_ = 0;

    best_remaining_m_ = 1e30;
    no_progress_ticks_ = 0;
    stuck_ticks_ = 0;
    stuck_ref_x_ = 0.0;
    stuck_ref_z_ = 0.0;
    last_bot_x_ = 0.0;
    last_bot_z_ = 0.0;
    have_last_bot_pos_ = false;
    pending_stall_ = false;

    submits_ = 0;
    cancels_ = 0;
    polls_ = 0;
    arrivals_ = 0;
    unreachable_aborts_ = 0;
    expirations_ = 0;
    stall_reports_ = 0;
    reroutes_ = 0;
    stuck_events_ = 0;
    searches_total_ = 0;
    expansions_total_ = 0;
    goal_stall_strikes_ = 0;
    last_stalled_u_ = -1;
    last_stalled_v_ = -1;
  }

  // Bound at the start of every 20 Hz tick before `ItemPlanner::Step`.
  void BindTickContext(const navlab::NavGraph* graph, uint32_t graph_epoch,
                       int tick, const itemai::Vec3& bot_pos,
                       double bot_yaw_deg, const TrueItemTable* true_items,
                       ConstrainedNavSearch* search,
                       TickExpansionBudget* tick_budget,
                       LocalBlockedEdgeTable* local_blocked) {
    graph_ = graph;
    graph_epoch_ = graph_epoch;
    tick_ = tick;
    bot_pos_ = bot_pos;
    bot_yaw_deg_ = bot_yaw_deg;
    true_items_ = true_items;
    search_ = search;
    tick_budget_ = tick_budget;
    local_blocked_ = local_blocked;

    if (active_ && true_items_ != nullptr) {
      const TrueItemEntry* te = true_items_->Find(goal_.goal_id);
      if (te != nullptr) true_pos_ = te->true_pos;
    }
  }

  /* --- itemai::NavigationSink interface ---------------------------------- */

  itemai::NavStatus Submit(const itemai::NavGoal& goal) override {
    ++submits_;
    if (!goal.Valid() || graph_ == nullptr) {
      return itemai::NavStatus::kRejected;
    }

    const itemai::Vec3 target_pos = ResolveTruePos(goal.goal_id, goal.pos);

    // Idempotent update when same goal_id and unchanged pickup position.
    if (active_ && goal_.goal_id == goal.goal_id &&
        PlanarDistXZ(true_pos_.x, true_pos_.z, target_pos.x, target_pos.z) <
            0.05 &&
        (status_ == itemai::NavStatus::kAccepted ||
         status_ == itemai::NavStatus::kInProgress)) {
      goal_ = goal;
      true_pos_ = target_pos;
      return status_;
    }

    // Immediate pickup radius: already standing on the item.
    if (itemai::Distance(bot_pos_, target_pos) <= goal.arrive_radius_m) {
      ActivateGoal(goal, target_pos, -1);
      route_len_ = 0;
      route_pos_ = 0;
      partial_route_ = false;
      return itemai::NavStatus::kAccepted;
    }

    if (graph_->node_count() <= 0) {
      return itemai::NavStatus::kUnreachable;
    }

    const int start_node = graph_->NearestNode(bot_pos_.x, bot_pos_.z,
                                               cfg_.max_anchor_dist_m);
    const int goal_node = graph_->NearestNode(target_pos.x, target_pos.z,
                                              cfg_.max_anchor_dist_m);
    if (start_node < 0 || goal_node < 0) {
      ++unreachable_aborts_;
      return itemai::NavStatus::kUnreachable;
    }

    const navlab::NavPath path = RunGoalSearch(start_node, goal_node);
    if (path.status == navlab::NavSearchStatus::kUnreachable ||
        path.status == navlab::NavSearchStatus::kInvalidArgs) {
      ++unreachable_aborts_;
      return itemai::NavStatus::kUnreachable;
    }

    ActivateGoal(goal, target_pos, goal_node);
    InstallPath(path);
    best_remaining_m_ = ComputeRemainingMeters();
    return itemai::NavStatus::kAccepted;
  }

  void Cancel(int goal_id) override {
    ++cancels_;
    if (active_ && goal_.goal_id == goal_id) {
      if (goal_stall_strikes_ >= 2 && local_blocked_ != nullptr &&
          last_stalled_u_ >= 0 && last_stalled_v_ >= 0) {
        local_blocked_->BlockLink(last_stalled_u_, last_stalled_v_,
                                  tick_ + cfg_.blocked_edge_ttl_ticks);
      }
      active_ = false;
      status_ = itemai::NavStatus::kAborted;
      last_terminal_id_ = goal_id;
      last_terminal_status_ = itemai::NavStatus::kAborted;
      route_len_ = 0;
      route_pos_ = 0;
      pending_stall_ = false;
      goal_stall_strikes_ = 0;
      last_stalled_u_ = -1;
      last_stalled_v_ = -1;
    }
  }

  itemai::NavStatus Poll(int goal_id, itemai::NavFeedback* out) override {
    ++polls_;
    if (out != nullptr) *out = itemai::NavFeedback();

    if (!active_) {
      const itemai::NavStatus st = (last_terminal_id_ == goal_id)
                                       ? last_terminal_status_
                                       : itemai::NavStatus::kIdle;
      FillFeedback(goal_id, st, -1.0, out);
      return st;
    }
    if (goal_.goal_id != goal_id) {
      FillFeedback(goal_id, itemai::NavStatus::kIdle, -1.0, out);
      return itemai::NavStatus::kIdle;
    }

    // Teleport guard (> 8 m jump in a single tick): invalidate route and replan.
    if (have_last_bot_pos_) {
      const double dx = bot_pos_.x - last_bot_x_;
      const double dz = bot_pos_.z - last_bot_z_;
      if (dx * dx + dz * dz > 64.0) {
        planned_epoch_ = 0;  // triggers replan below
      }
    }

    // 1. Arrival check against authoritative 3D item coordinates.
    if (itemai::Distance(bot_pos_, true_pos_) <= goal_.arrive_radius_m) {
      active_ = false;
      status_ = itemai::NavStatus::kArrived;
      last_terminal_id_ = goal_id;
      last_terminal_status_ = itemai::NavStatus::kArrived;
      ++arrivals_;
      FillFeedback(goal_id, itemai::NavStatus::kArrived, 0.0, out);
      return itemai::NavStatus::kArrived;
    }

    // 2. Hard expiration window check.
    if (goal_.Expired(tick_)) {
      active_ = false;
      status_ = itemai::NavStatus::kExpired;
      last_terminal_id_ = goal_id;
      last_terminal_status_ = itemai::NavStatus::kExpired;
      ++expirations_;
      FillFeedback(goal_id, itemai::NavStatus::kExpired,
                   ComputeRemainingMeters(), out);
      return itemai::NavStatus::kExpired;
    }

    // 3. Topology / blocker epoch change -> immediate replan.
    if (graph_ != nullptr && graph_->node_count() > 0 &&
        CombinedEpoch() != planned_epoch_) {
      if (!ReplanCurrentGoal()) {
        active_ = false;
        status_ = itemai::NavStatus::kUnreachable;
        last_terminal_id_ = goal_id;
        last_terminal_status_ = itemai::NavStatus::kUnreachable;
        ++unreachable_aborts_;
        FillFeedback(goal_id, itemai::NavStatus::kUnreachable, -1.0, out);
        return itemai::NavStatus::kUnreachable;
      }
    }

    // 4. Incremental continuation for budget-capped partial routes.
    if (partial_route_ && route_pos_ >= route_len_ && graph_ != nullptr &&
        graph_->node_count() > 0) {
      if (!ReplanCurrentGoal()) {
        active_ = false;
        status_ = itemai::NavStatus::kUnreachable;
        last_terminal_id_ = goal_id;
        last_terminal_status_ = itemai::NavStatus::kUnreachable;
        ++unreachable_aborts_;
        FillFeedback(goal_id, itemai::NavStatus::kUnreachable, -1.0, out);
        return itemai::NavStatus::kUnreachable;
      }
    }

    // 5. Stall feedback: emit once per stalled window while keeping the goal
    //    alive so `ItemPlanner` can enforce its 2-strike abort rule.
    if (pending_stall_) {
      pending_stall_ = false;
      ++stall_reports_;
      ++goal_stall_strikes_;
      status_ = itemai::NavStatus::kInProgress;
      FillFeedback(goal_id, itemai::NavStatus::kStalled,
                   ComputeRemainingMeters(), out);
      return itemai::NavStatus::kStalled;
    }

    status_ = itemai::NavStatus::kInProgress;
    FillFeedback(goal_id, status_, ComputeRemainingMeters(), out);
    return status_;
  }

  const char* Name() const override { return "navlab-astar-sink"; }

  /* --- Movement execution for the active item goal ----------------------- */

  GoalMoveCommand StepGoalMove(bool driving_allowed,
                               bool movement_requested_last_tick,
                               double front_obstacle_m) {
    GoalMoveCommand cmd;
    last_bot_x_ = bot_pos_.x;
    last_bot_z_ = bot_pos_.z;
    have_last_bot_pos_ = true;

    if (!active_ || graph_ == nullptr) return cmd;
    cmd.goal_id = goal_.goal_id;
    cmd.dest_node = goal_node_;

    // When Combat temporarily owns movement (`yield_to_combat`), pause stuck
    // and stall timers so combat strafing is never misdiagnosed as a nav stall.
    if (!driving_allowed) {
      stuck_ticks_ = 0;
      return cmd;
    }

    // Advance along intermediate waypoints (segment projection prevents orbit).
    AdvanceWaypoints();

    // If a partial route just reached its frontier node, extend it if budget
    // remains this tick; otherwise wait for next tick's budget.
    if (partial_route_ && route_pos_ >= route_len_) {
      if (tick_budget_ == nullptr || tick_budget_->Remaining() >= 8) {
        if (!ReplanCurrentGoal()) {
          active_ = false;
          status_ = itemai::NavStatus::kUnreachable;
          last_terminal_id_ = goal_.goal_id;
          last_terminal_status_ = itemai::NavStatus::kUnreachable;
          ++unreachable_aborts_;
          return cmd;
        }
        cmd.replanned = true;
        cmd.expanded_last_search = last_search_expanded_;
        AdvanceWaypoints();
      }
    }

    // Progress & physical stuck monitoring coupled with local edge avoidance.
    const double rem_now = ComputeRemainingMeters();
    if (rem_now < best_remaining_m_ - 0.75) {
      best_remaining_m_ = rem_now;
      no_progress_ticks_ = 0;
    } else if (movement_requested_last_tick) {
      ++no_progress_ticks_;
    }

    bool physical_stuck = false;
    if (movement_requested_last_tick) {
      if (stuck_ticks_ == 0) {
        stuck_ref_x_ = bot_pos_.x;
        stuck_ref_z_ = bot_pos_.z;
      }
      ++stuck_ticks_;
      const int win = persona_.stuck_window > 4 ? persona_.stuck_window : 40;
      if (stuck_ticks_ >= win) {
        const double d =
            PlanarDistXZ(bot_pos_.x, bot_pos_.z, stuck_ref_x_, stuck_ref_z_);
        const double min_d =
            persona_.stuck_min_dist > 0.2f ? persona_.stuck_min_dist : 1.0f;
        physical_stuck = (d < min_d);
        stuck_ticks_ = 0;
      }
    } else {
      stuck_ticks_ = 0;
    }

    const int stall_win =
        (persona_.stuck_window > 4 ? persona_.stuck_window : 40) + 5;
    const bool progress_stalled = (no_progress_ticks_ >= stall_win);
    const bool wall_blocked_now =
        (front_obstacle_m >= 0.0 && front_obstacle_m < 1.2 &&
         no_progress_ticks_ >= 12);

    if (physical_stuck || progress_stalled || wall_blocked_now) {
      ++stuck_events_;
      cmd.stuck = true;
      no_progress_ticks_ = 0;
      stuck_ticks_ = 0;

      const int prev_first_hop = CurrentTargetNode();
      int u1 = -1, v1 = -1, u2 = -1, v2 = -1;
      BlockCurrentSegment(&u1, &v1, &u2, &v2);

      if (ReplanCurrentGoal()) {
        cmd.replanned = true;
        cmd.expanded_last_search = last_search_expanded_;
        const int next_first_hop = CurrentTargetNode();
        if (next_first_hop >= 0 && next_first_hop != prev_first_hop &&
            !partial_route_) {
          ++reroutes_;
          best_remaining_m_ = ComputeRemainingMeters();
        } else {
          pending_stall_ = true;
        }
      } else {
        // Blocking the obstructed segment left NO alternative graph path at
        // all: roll back the tentative edge block during active retry so
        // `WorldPathEnricher` and `Poll` do not misclassify a physical stall
        // as `kUnreachable`. `ItemPlanner` retries once after ObstacleRecovery
        // and aborts cleanly via `ItemReason::kStalled` on the 2nd strike
        // (at which point `Cancel` commits the corridor block).
        if (local_blocked_ != nullptr) {
          if (u1 >= 0 && v1 >= 0) local_blocked_->UnblockLink(u1, v1);
          if (u2 >= 0 && v2 >= 0) local_blocked_->UnblockLink(u2, v2);
        }
        last_stalled_u_ = u1 >= 0 ? u1 : u2;
        last_stalled_v_ = u1 >= 0 ? v1 : v2;
        planned_epoch_ = CombinedEpoch();
        pending_stall_ = true;
      }
    }

    // Choose immediate steering point: intermediate waypoint, or final 3D item
    // coordinates once on the terminal leg so arrival inside `arrive_radius_m`
    // is geometrically guaranteed.
    double target_x = true_pos_.x;
    double target_z = true_pos_.z;
    bool jump_edge = false;

    if (route_pos_ < route_len_ && graph_->Valid(route_[route_pos_])) {
      const int wp_idx = route_[route_pos_];
      const bool is_last_wp = (route_pos_ == route_len_ - 1) && !partial_route_;
      const double dist_to_item =
          PlanarDistXZ(bot_pos_.x, bot_pos_.z, true_pos_.x, true_pos_.z);
      if (!is_last_wp || dist_to_item > goal_.arrive_radius_m * 2.2) {
        const navlab::NavNode& wp = graph_->node(wp_idx);
        target_x = wp.x;
        target_z = wp.z;
        cmd.next_node = wp_idx;
      }
      if (route_pos_ > 0 && goal_.allow_jump) {
        jump_edge = HasJumpFlag(route_[route_pos_ - 1], wp_idx);
      }
    }

    SteerTowards(target_x, target_z, cmd);
    cmd.active = true;
    cmd.jump_hint = jump_edge;
    cmd.route_hops_left =
        route_pos_ < route_len_ ? (route_len_ - route_pos_) : 0;
    cmd.path_remaining_m = ComputeRemainingMeters();
    return cmd;
  }

  /* --- Inspection / telemetry -------------------------------------------- */
  bool has_active_goal() const { return active_; }
  int active_goal_id() const { return active_ ? goal_.goal_id : -1; }
  const itemai::NavGoal& active_goal() const { return goal_; }
  const itemai::Vec3& active_true_pos() const { return true_pos_; }
  itemai::NavStatus status() const { return status_; }
  int submits() const { return submits_; }
  int cancels() const { return cancels_; }
  int polls() const { return polls_; }
  int arrivals() const { return arrivals_; }
  int unreachable_aborts() const { return unreachable_aborts_; }
  int expirations() const { return expirations_; }
  int stall_reports() const { return stall_reports_; }
  int reroutes() const { return reroutes_; }
  int stuck_events() const { return stuck_events_; }
  int searches_total() const { return searches_total_; }
  int expansions_total() const { return expansions_total_; }

 private:
  uint32_t CombinedEpoch() const {
    const uint32_t le =
        local_blocked_ != nullptr ? local_blocked_->epoch() : 0u;
    return MixEpoch(graph_epoch_, le);
  }

  itemai::Vec3 ResolveTruePos(int goal_id,
                              const itemai::Vec3& fallback) const {
    if (true_items_ != nullptr) {
      const TrueItemEntry* te = true_items_->Find(goal_id);
      if (te != nullptr) return te->true_pos;
    }
    return fallback;
  }

  void ActivateGoal(const itemai::NavGoal& goal, const itemai::Vec3& true_pos,
                    int goal_node) {
    active_ = true;
    goal_ = goal;
    true_pos_ = true_pos;
    goal_node_ = goal_node;
    status_ = itemai::NavStatus::kAccepted;
    planned_epoch_ = CombinedEpoch();
    no_progress_ticks_ = 0;
    stuck_ticks_ = 0;
    pending_stall_ = false;
    goal_stall_strikes_ = 0;
    last_stalled_u_ = -1;
    last_stalled_v_ = -1;
  }

  navlab::NavPath RunGoalSearch(int start_node, int goal_node) {
    if (search_ == nullptr) {
      navlab::NavPath bad;
      bad.status = navlab::NavSearchStatus::kInvalidArgs;
      return bad;
    }
    const navlab::NavPath path = search_->Search(
        *graph_, start_node, goal_node, cfg_.max_expand_goal_search,
        cfg_.route_variance, seed_, local_blocked_, tick_,
        cfg_.avoid_danger_edges, tick_budget_);
    last_search_expanded_ = path.expanded;
    if (path.expanded > 0 || path.status == navlab::NavSearchStatus::kFound) {
      ++searches_total_;
      expansions_total_ += path.expanded;
    }
    return path;
  }

  void InstallPath(const navlab::NavPath& path) {
    route_len_ = 0;
    for (int i = 0; i < path.count && i < navlab::kNavMaxPathNodes; ++i) {
      route_[route_len_++] = path.nodes[i];
    }
    route_pos_ = 0;
    partial_route_ =
        (path.status == navlab::NavSearchStatus::kBudgetExhausted);
    planned_epoch_ = CombinedEpoch();
  }

  bool ReplanCurrentGoal() {
    if (graph_ == nullptr || graph_->node_count() <= 0 || goal_node_ < 0) {
      return false;
    }
    const int start_node = graph_->NearestNode(bot_pos_.x, bot_pos_.z,
                                               cfg_.max_anchor_dist_m);
    if (start_node < 0) return false;
    const navlab::NavPath path = RunGoalSearch(start_node, goal_node_);
    if (path.status == navlab::NavSearchStatus::kUnreachable ||
        path.status == navlab::NavSearchStatus::kInvalidArgs) {
      return false;
    }
    InstallPath(path);
    return true;
  }

  int CurrentTargetNode() const {
    if (route_pos_ < route_len_) return route_[route_pos_];
    return -1;
  }

  void BlockCurrentSegment(int* out_u1, int* out_v1, int* out_u2, int* out_v2) {
    if (out_u1) *out_u1 = -1;
    if (out_v1) *out_v1 = -1;
    if (out_u2) *out_u2 = -1;
    if (out_v2) *out_v2 = -1;
    if (local_blocked_ == nullptr || graph_ == nullptr || route_len_ <= 0) {
      return;
    }
    const int until = tick_ + cfg_.blocked_edge_ttl_ticks;
    const int near_node =
        graph_->NearestNode(bot_pos_.x, bot_pos_.z, cfg_.max_anchor_dist_m);
    if (route_pos_ > 0 && route_pos_ < route_len_) {
      const int u = route_[route_pos_ - 1];
      const int v = route_[route_pos_];
      local_blocked_->BlockLink(u, v, until);
      if (out_u1) *out_u1 = u;
      if (out_v1) *out_v1 = v;
    } else if (route_pos_ == 0 && route_len_ >= 2) {
      const int u = route_[0];
      const int v = route_[1];
      local_blocked_->BlockLink(u, v, until);
      if (out_u1) *out_u1 = u;
      if (out_v1) *out_v1 = v;
    }
    if (near_node >= 0 && route_pos_ < route_len_ &&
        near_node != route_[route_pos_]) {
      const int v = route_[route_pos_];
      local_blocked_->BlockLink(near_node, v, until);
      if (out_u2) *out_u2 = near_node;
      if (out_v2) *out_v2 = v;
    }
  }

  void AdvanceWaypoints() {
    if (graph_ == nullptr) return;
    while (route_pos_ < route_len_) {
      const int idx = route_[route_pos_];
      if (!graph_->Valid(idx)) {
        ++route_pos_;
        continue;
      }
      const navlab::NavNode& node = graph_->node(idx);
      const double dx = node.x - bot_pos_.x;
      const double dz = node.z - bot_pos_.z;
      const double reach = node.radius > persona_.search_radius
                               ? node.radius
                               : persona_.search_radius;
      const double d2 = dx * dx + dz * dz;
      bool passed = false;
      if (route_pos_ > 0 && graph_->Valid(route_[route_pos_ - 1])) {
        const navlab::NavNode& prev = graph_->node(route_[route_pos_ - 1]);
        const double sx = node.x - prev.x;
        const double sz = node.z - prev.z;
        const double bx = bot_pos_.x - prev.x;
        const double bz = bot_pos_.z - prev.z;
        const double seg2 = sx * sx + sz * sz;
        if (seg2 > 1e-9) passed = ((bx * sx + bz * sz) / seg2) > 1.0;
      }
      if (d2 <= reach * reach || passed) {
        ++route_pos_;
      } else {
        break;
      }
    }
  }

  bool HasJumpFlag(int from, int to) const {
    if (graph_ == nullptr || !graph_->Valid(from)) return false;
    const int n = graph_->edge_count(from);
    for (int e = 0; e < n; ++e) {
      const navlab::NavEdge& ed = graph_->edge(from, e);
      if (ed.to == static_cast<int16_t>(to)) {
        return (ed.flags & navlab::kEdgeJump) != 0u;
      }
    }
    return false;
  }

  void SteerTowards(double tx, double tz, GoalMoveCommand& cmd) const {
    const double dx = tx - bot_pos_.x;
    const double dz = tz - bot_pos_.z;
    const double desired =
        std::atan2(-dx, -dz) * (180.0 / navlab::kNavPi);
    double delta = desired - bot_yaw_deg_;
    while (delta > 180.0) delta -= 360.0;
    while (delta < -180.0) delta += 360.0;
    const double abs_err = delta < 0.0 ? -delta : delta;
    const double max_step = persona_.turn_rate_deg_s / navlab::kNavTickHz;
    cmd.yaw_delta_deg =
        delta < -max_step ? -max_step : (delta > max_step ? max_step : delta);
    cmd.desired_yaw_deg = bot_yaw_deg_ + cmd.yaw_delta_deg;
    cmd.forward = (abs_err > 60.0) ? 0.0 : goal_.max_speed_frac;
  }

  double ComputeRemainingMeters() const {
    if (!active_) return -1.0;
    if (graph_ == nullptr || route_pos_ >= route_len_) {
      return itemai::Distance(bot_pos_, true_pos_);
    }
    double sum = 0.0;
    const int first_wp = route_[route_pos_];
    if (graph_->Valid(first_wp)) {
      const navlab::NavNode& n0 = graph_->node(first_wp);
      sum += PlanarDistXZ(bot_pos_.x, bot_pos_.z, n0.x, n0.z);
    }
    for (int i = route_pos_; i + 1 < route_len_; ++i) {
      if (graph_->Valid(route_[i]) && graph_->Valid(route_[i + 1])) {
        sum += graph_->PlanarDist(route_[i], route_[i + 1]);
      }
    }
    const int last_wp = route_[route_len_ - 1];
    if (graph_->Valid(last_wp)) {
      const navlab::NavNode& nl = graph_->node(last_wp);
      sum += PlanarDistXZ(nl.x, nl.z, true_pos_.x, true_pos_.z);
    }
    const double direct = itemai::Distance(bot_pos_, true_pos_);
    return sum > direct ? sum : direct;
  }

  void FillFeedback(int goal_id, itemai::NavStatus st, double rem_m,
                    itemai::NavFeedback* out) const {
    if (out == nullptr) return;
    out->goal_id = goal_id;
    out->status = st;
    out->bot_pos = bot_pos_;
    out->path_remaining_m = rem_m;
    out->line_of_sight = false;
    out->tick = tick_;
  }

  BridgeBudgetConfig cfg_;
  navlab::NavPersonality persona_;
  uint32_t seed_ = 1u;

  const navlab::NavGraph* graph_ = nullptr;
  uint32_t graph_epoch_ = 1u;
  int tick_ = 0;
  itemai::Vec3 bot_pos_{};
  double bot_yaw_deg_ = 0.0;
  const TrueItemTable* true_items_ = nullptr;
  ConstrainedNavSearch* search_ = nullptr;
  TickExpansionBudget* tick_budget_ = nullptr;
  LocalBlockedEdgeTable* local_blocked_ = nullptr;

  bool active_ = false;
  itemai::NavGoal goal_{};
  itemai::Vec3 true_pos_{};
  itemai::NavStatus status_ = itemai::NavStatus::kIdle;
  int last_terminal_id_ = -1;
  itemai::NavStatus last_terminal_status_ = itemai::NavStatus::kIdle;

  int goal_node_ = -1;
  int16_t route_[navlab::kNavMaxPathNodes] = {0};
  int route_len_ = 0;
  int route_pos_ = 0;
  bool partial_route_ = false;
  uint32_t planned_epoch_ = 0;
  int last_search_expanded_ = 0;

  double best_remaining_m_ = 1e30;
  int no_progress_ticks_ = 0;
  int stuck_ticks_ = 0;
  double stuck_ref_x_ = 0.0;
  double stuck_ref_z_ = 0.0;
  double last_bot_x_ = 0.0;
  double last_bot_z_ = 0.0;
  bool have_last_bot_pos_ = false;
  bool pending_stall_ = false;
  int goal_stall_strikes_ = 0;
  int last_stalled_u_ = -1;
  int last_stalled_v_ = -1;

  int submits_ = 0;
  int cancels_ = 0;
  int polls_ = 0;
  int arrivals_ = 0;
  int unreachable_aborts_ = 0;
  int expirations_ = 0;
  int stall_reports_ = 0;
  int reroutes_ = 0;
  int stuck_events_ = 0;
  int searches_total_ = 0;
  int expansions_total_ = 0;
};

}  // namespace navbridge

#endif  // NAV_ITEM_BRIDGE_NAV_GOAL_SINK_H
