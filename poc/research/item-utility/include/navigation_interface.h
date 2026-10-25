// SPDX-License-Identifier: GPL-2.0-only
// navigation_interface.h - the ONLY seam between the item layer and the
// navigation agent.
//
// DIVISION OF LABOUR (hard boundary, from the task assignment)
//   item layer        : WHICH item, WHY, and WHEN to give up.
//   navigation agent  : WaypointGraph, A*, path following, obstacle recovery,
//                       pit avoidance, jump/crouch flags.
// The item layer therefore
//   * never stores a path, a waypoint index or a heading,
//   * never casts a ray and never reads an entity,
//   * never walks geometry: the travel estimate in item_scoring.h is a
//     straight-line / speed estimate used ONLY for utility, never for control,
//   * emits exactly one active goal plus a validity window and reads back a
//     coarse status.
//
// CONTRACT FOR THE NAVIGATION AGENT
//   1. Submit() is called once when a goal is committed and again after a
//      switch. The same goal_id must not be submitted twice in a row with a
//      different position: commit a new goal instead.
//   2. The item layer expects no progress callback at all. It only reads
//      Poll() at its own 20 Hz tick, so the navigation agent may run at a
//      different rate, may budget its A* freely and may be a stub.
//   3. A goal carries an absolute `expires_tick`. Once reached, navigation must
//      report kExpired; the item layer treats it as a plain miss.
//   4. `arrive_radius_m` is a *pickup* tolerance, not a path tolerance: the
//      server grants the item on touch. A radius below ~1 m is not useful.
//   5. Report kUnreachable rather than faking progress. The item layer
//      blacklists that item; a false "unreachable" costs a real pickup.
//   6. Report kStalled when the bot has not decreased the path remainder for a
//      meaningful interval. Two consecutive kStalled aborts the goal.
//   7. Navigation must never decide *which* item to go for, and must never call
//      back into the planner except through the documented Notify* entry
//      points.
//
// The interface is abstract so the offline prototype can be driven by
// RecordingNavigationSink (tests) and the integration can bind a thin adapter
// over the existing botcore navigation/ObstacleRecovery code without changing
// the planner at all.

#ifndef ITEMAI_NAVIGATION_INTERFACE_H
#define ITEMAI_NAVIGATION_INTERFACE_H

#include <cstring>

#include "item_types.h"

namespace itemai {

/* ------------------------------------------------------------------------ */
/* Goal / status vocabulary                                                  */
/* ------------------------------------------------------------------------ */

enum class NavPriority : uint8_t {
  kSoft = 0,     // opportunistic detour, yields to anything else
  kNormal = 1,   // default resource trip
  kUrgent = 2,   // bot is in trouble, movement should prefer this
  kCritical = 3  // survival: the combat layer should yield
};

enum class NavStatus : uint8_t {
  kIdle = 0,       // no such goal known
  kAccepted = 1,   // queued, not yet planned
  kInProgress = 2, // a path exists and the bot is following it
  kArrived = 3,    // inside the arrival radius
  kUnreachable = 4,// no path exists
  kStalled = 5,    // path exists but no progress
  kAborted = 6,    // cancelled by either side
  kExpired = 7,    // validity window elapsed
  kRejected = 8    // navigation refused the goal outright
};

inline const char* NavStatusName(NavStatus s) {
  switch (s) {
    case NavStatus::kIdle: return "idle";
    case NavStatus::kAccepted: return "accepted";
    case NavStatus::kInProgress: return "in-progress";
    case NavStatus::kArrived: return "arrived";
    case NavStatus::kUnreachable: return "unreachable";
    case NavStatus::kStalled: return "stalled";
    case NavStatus::kAborted: return "aborted";
    case NavStatus::kExpired: return "expired";
    case NavStatus::kRejected: return "rejected";
    default: return "?";
  }
}

inline bool NavIsTerminal(NavStatus s) {
  return s == NavStatus::kArrived || s == NavStatus::kUnreachable ||
         s == NavStatus::kStalled || s == NavStatus::kAborted ||
         s == NavStatus::kExpired || s == NavStatus::kRejected;
}

/* ------------------------------------------------------------------------ */
/* Goal                                                                      */
/* ------------------------------------------------------------------------ */

struct NavGoal {
  int goal_id = -1;               // item id from the snapshot, stable
  Vec3 pos{};                     // item position (pickup centre)
  double arrive_radius_m = kArrivalRadiusM;
  NavPriority priority = NavPriority::kNormal;
  double max_speed_frac = 1.0;    // 0..1, lets a cautious bot walk
  bool allow_jump = true;         // navigation decides, this is a hint only
  bool yield_to_combat = true;    // set false only for survival pickups
  int issued_tick = 0;
  int expires_tick = 0;

  bool Expired(int tick) const { return tick >= expires_tick; }
  bool Valid() const {
    return goal_id >= 0 && Finite(pos.x) && Finite(pos.y) && Finite(pos.z) &&
           arrive_radius_m > 0.0 && Finite(arrive_radius_m) &&
           max_speed_frac > 0.0 && max_speed_frac <= 1.0 && expires_tick > issued_tick;
  }
};

struct NavFeedback {
  int goal_id = -1;
  NavStatus status = NavStatus::kIdle;
  Vec3 bot_pos{};              // optional, for progress accounting
  double path_remaining_m = -1.0;  // -1 = unknown
  bool line_of_sight = false;  // navigation may report this; item layer ignores it
  int tick = 0;
};

/* ------------------------------------------------------------------------ */
/* Abstract sink                                                             */
/* ------------------------------------------------------------------------ */

class NavigationSink {
 public:
  virtual ~NavigationSink() = default;

  // Commit a goal. Returns kAccepted normally, kRejected if navigation cannot
  // handle it at all. Must be idempotent for an unchanged goal_id.
  virtual NavStatus Submit(const NavGoal& goal) = 0;

  // Drop a goal. After this the item layer will not poll it again.
  virtual void Cancel(int goal_id) = 0;

  // Latest status. kIdle = unknown goal.
  virtual NavStatus Poll(int goal_id, NavFeedback* out) = 0;

  // Diagnostic label for logs; may be static storage.
  virtual const char* Name() const = 0;
};

/* ------------------------------------------------------------------------ */
/* Test double                                                               */
/* ------------------------------------------------------------------------ */

// Deterministic, scriptable sink for the offline tests and benchmarks. It
// implements no pathfinding on purpose; it models *reported behaviour* only.
class RecordingNavigationSink : public NavigationSink {
 public:
  static constexpr int kSlots = 16;

  void Reset() {
    for (int i = 0; i < kSlots; ++i) slots_[i] = Slot();
    submits_ = 0;
    cancels_ = 0;
    polls_ = 0;
    rejected_all_ = false;
    arrive_after_ticks_ = 0;   // 0 = never arrive
    stall_after_ticks_ = -1;   // <0 = never stall
    unreachable_ids_[0] = -1;
    unreachable_count_ = 0;
  }

  RecordingNavigationSink() { Reset(); }

  // --- scripting -------------------------------------------------------
  void RejectEverything(bool v) { rejected_all_ = v; }
  // "Arrive" once the goal has been polled this many times (0 = never).
  void SetArriveAfterPolls(int polls) { arrive_after_ticks_ = polls; }
  void SetStallAfterPolls(int polls) { stall_after_ticks_ = polls; }
  void MarkUnreachable(int goal_id) {
    for (int i = 0; i < 8; ++i) {
      if (unreachable_ids_[i] == goal_id) return;
    }
    for (int i = 0; i < 8; ++i) {
      if (unreachable_ids_[i] < 0) {
        unreachable_ids_[i] = goal_id;
        ++unreachable_count_;
        return;
      }
    }
  }

  // --- NavigationSink --------------------------------------------------
  NavStatus Submit(const NavGoal& goal) override {
    ++submits_;
    last_goal_ = goal;
    const int s = FindSlot(goal.goal_id, true);
    if (s < 0) return NavStatus::kRejected;
    Slot& sl = slots_[s];
    if (sl.goal_id == goal.goal_id && sl.status == NavStatus::kInProgress) {
      return sl.status;  // idempotent
    }
    sl.goal_id = goal.goal_id;
    sl.pos = goal.pos;
    sl.goal = goal;
    sl.polls = 0;
    sl.status = rejected_all_ || IsUnreachable(goal.goal_id) ? NavStatus::kUnreachable
                                                            : NavStatus::kAccepted;
    return sl.status;
  }

  void Cancel(int goal_id) override {
    ++cancels_;
    const int s = FindSlot(goal_id, false);
    if (s < 0) return;
    slots_[s].status = NavStatus::kAborted;
  }

  NavStatus Poll(int goal_id, NavFeedback* out) override {
    ++polls_;
    const int s = FindSlot(goal_id, false);
    if (s < 0) {
      if (out != nullptr) *out = NavFeedback();
      return NavStatus::kIdle;
    }
    Slot& sl = slots_[s];
    const int polls = ++sl.polls;

    if (sl.status == NavStatus::kAccepted) sl.status = NavStatus::kInProgress;
    if (arrive_after_ticks_ > 0 && polls >= arrive_after_ticks_) {
      sl.status = NavStatus::kArrived;
    } else if (stall_after_ticks_ >= 0 && polls >= stall_after_ticks_ &&
               sl.status == NavStatus::kInProgress) {
      sl.status = NavStatus::kStalled;
    } else if (sl.goal.expires_tick > 0 && sl.goal.Expired(sl.goal.issued_tick + polls)) {
      sl.status = NavStatus::kExpired;
    }

    if (out != nullptr) {
      out->goal_id = goal_id;
      out->status = sl.status;
      out->bot_pos = sl.pos;
      out->path_remaining_m = -1.0;
      out->line_of_sight = false;
      out->tick = sl.goal.issued_tick + polls;
    }
    return sl.status;
  }

  const char* Name() const override { return "recording"; }

  // --- inspection ------------------------------------------------------
  int submits() const { return submits_; }
  int cancels() const { return cancels_; }
  int polls() const { return polls_; }
  const NavGoal& last_goal() const { return last_goal_; }
  NavStatus StatusOf(int goal_id) {
    const int s = FindSlot(goal_id, false);
    return s < 0 ? NavStatus::kIdle : slots_[s].status;
  }

 private:
  struct Slot {
    int goal_id = -1;
    NavStatus status = NavStatus::kIdle;
    Vec3 pos{};
    NavGoal goal{};
    int polls = 0;
  };

  int FindSlot(int goal_id, bool create) {
    if (goal_id < 0) return -1;
    for (int i = 0; i < kSlots; ++i) {
      if (slots_[i].goal_id == goal_id) return i;
    }
    if (!create) return -1;
    for (int i = 0; i < kSlots; ++i) {
      if (slots_[i].goal_id < 0) return i;
    }
    // Reuse the oldest terminal slot.
    for (int i = 0; i < kSlots; ++i) {
      if (NavIsTerminal(slots_[i].status)) return i;
    }
    return -1;
  }

  bool IsUnreachable(int goal_id) const {
    for (int i = 0; i < 8; ++i) {
      if (unreachable_ids_[i] == goal_id) return true;
    }
    return false;
  }

  Slot slots_[kSlots];
  NavGoal last_goal_{};
  int submits_ = 0;
  int cancels_ = 0;
  int polls_ = 0;
  bool rejected_all_ = false;
  int arrive_after_ticks_ = 0;
  int stall_after_ticks_ = -1;
  int unreachable_ids_[8] = {-1, -1, -1, -1, -1, -1, -1, -1};
  int unreachable_count_ = 0;
};

/* ------------------------------------------------------------------------ */
/* Goal translation                                                          */
/* ------------------------------------------------------------------------ */

// Maps a planner decision onto a navigation goal. Priority and the
// "yield to combat" flag are derived from need, not from the item kind alone,
// so a full-health armor trip stays a soft detour while a 12 %-health medkit is
// survival-critical.
struct GoalTranslationInput {
  int goal_id = -1;
  Vec3 pos{};
  bool survival = false;      // health/armor need while critically low
  bool urgent = false;        // ammunition starvation or visibly low health
  bool combat_engaged = false;
  double utility = 0.0;
  int issued_tick = 0;
  int max_duration_ticks = 160;
  double caution = 0.5;
};

inline NavGoal MakeNavGoal(const GoalTranslationInput& in) {
  NavGoal g;
  g.goal_id = in.goal_id;
  g.pos = in.pos;
  g.arrive_radius_m = kArrivalRadiusM;
  g.issued_tick = in.issued_tick;
  g.expires_tick = in.issued_tick + (in.max_duration_ticks > 0 ? in.max_duration_ticks : 1);
  g.priority = in.survival   ? NavPriority::kCritical
               : in.urgent   ? NavPriority::kUrgent
               : in.utility > 0.55 ? NavPriority::kNormal
                                   : NavPriority::kSoft;
  g.yield_to_combat = !in.survival;
  // A cautious bot walks (0.8), an aggressive one sprints (1.0). Never below
  // 0.6: a resource trip slower than that is not worth the trip at all.
  g.max_speed_frac = Clamp(1.0 - 0.35 * in.caution, 0.6, 1.0);
  g.allow_jump = true;
  return g;
}

}  // namespace itemai

#endif  // ITEMAI_NAVIGATION_INTERFACE_H
