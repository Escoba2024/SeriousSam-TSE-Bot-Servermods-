// SPDX-License-Identifier: GPL-2.0-only
// item_planner.h - the goal state machine of the item layer.
//
// WHAT IT DOES
//   Every tick it (a) evaluates all known items with item_scoring.h,
//   (b) decides whether the current goal survives, (c) switches goals only
//   past a documented commit margin and dwell time, and (d) hands exactly one
//   goal to the navigation seam (navigation_interface.h).
//
// HYSTERESIS, COOLDOWNS, TIME LIMITS
//   * Start threshold vs. continue threshold: a *new* goal must clear
//     tuning.min_utility; a *running* goal only has to keep a non-zero need.
//     Without that asymmetry every small fluctuation would cancel a trip.
//   * Commit margin: a competitor must beat the running goal by
//     (1 + tuning.commit_margin) to replace it.
//   * Dwell: no voluntary switch inside tuning.min_commit_s.
//   * Global search cooldown after a trouble abort (damage, threat, stall,
//     timeout, unreachable) - not after a successful pickup, because the next
//     need must stay reachable.
//   * Per-item cooldown after a trouble abort and a longer blacklist after a
//     pickup or an "unreachable" verdict. Both are tick based and bounded.
//   * Per-goal time limit tuning.max_search_time_s, enforced against the
//     caller's tick; plus a hard travel estimate cutoff for new goals.
//
// THREAT / DAMAGE / ABORT
//   * kThreatOverride: a visible enemy inside tuning.enemy_abort_radius_m while
//     health is below tuning.health_abort_frac, unless the bot is already
//     within tuning.close_finish_radius_m of the pickup (finishing a medkit two
//     steps away is safer than turning around).
//   * kDamageAbort: more than tuning.abort_damage_frac of max health lost
//     inside tuning.damage_window_s.
//   * kCombatLock: a committed fight (combat_priority above
//     tuning.combat_lock_priority) starts no resource trip at all unless the
//     bot is critically hurt.
//
// ENGINE-FREE: no allocation, no I/O, no engine types, no global state. All
// state lives in the planner instance, so two planners never interfere.

#ifndef ITEMAI_ITEM_PLANNER_H
#define ITEMAI_ITEM_PLANNER_H

#include <cstdio>
#include <cstring>

#include "item_profile.h"
#include "item_scoring.h"
#include "item_snapshot.h"
#include "item_types.h"
#include "navigation_interface.h"

namespace itemai {

constexpr int kTimerSlots = 32;
constexpr int kStallAbortReports = 2;
constexpr int kExplainCap = 120;

/* ------------------------------------------------------------------------ */
/* Bounded tick-based timer table (no allocation, no hashing)                */
/* ------------------------------------------------------------------------ */

struct TimerTable {
  int id[kTimerSlots];
  int until[kTimerSlots];

  void Clear() {
    for (int i = 0; i < kTimerSlots; ++i) {
      id[i] = -1;
      until[i] = 0;
    }
  }
  TimerTable() { Clear(); }

  void Set(int item_id, int until_tick) {
    if (item_id < 0) return;
    int free_slot = -1;
    int oldest = 0;
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) {
        if (until_tick > until[i]) until[i] = until_tick;
        return;
      }
      if (id[i] < 0 && free_slot < 0) free_slot = i;
      if (until[i] < until[oldest]) oldest = i;
    }
    const int slot = free_slot >= 0 ? free_slot : oldest;
    id[slot] = item_id;
    until[slot] = until_tick;
  }

  bool Active(int item_id, int tick) const {
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) return tick < until[i];
    }
    return false;
  }

  int Remaining(int item_id, int tick) const {
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) {
        const int r = until[i] - tick;
        return r > 0 ? r : 0;
      }
    }
    return 0;
  }

  void ClearEntry(int item_id) {
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) {
        id[i] = -1;
        until[i] = 0;
      }
    }
  }
};

/* ------------------------------------------------------------------------ */
/* Decision result                                                           */
/* ------------------------------------------------------------------------ */

struct GoalDecision {
  ItemAction action = ItemAction::kNone;
  ItemReason reason = ItemReason::kNone;

  bool has_goal = false;
  int goal_id = -1;
  ItemKind goal_kind = ItemKind::kNone;
  int goal_weapon_index = 0;
  Vec3 goal_pos{};

  double utility = 0.0;
  double need = 0.0;
  double travel_s = 0.0;
  double distance_m = 0.0;

  // True when the combat layer should yield movement to this pickup
  // (survival-critical health/armor trip).
  bool suppress_combat = false;
  // True when the goal was committed/changed in this tick.
  bool changed = false;

  int candidates = 0;
  int eligible = 0;
  char explain[kExplainCap] = {0};
};

/* ------------------------------------------------------------------------ */
/* Planner                                                                   */
/* ------------------------------------------------------------------------ */

class ItemPlanner {
 public:
  ItemPlanner() {
    ItemProfile p;
    BuildItemProfile(3, 0, 0x1234567u, &p);
    Configure(p);
  }

  void Configure(const ItemProfile& p) {
    profile_ = p;
    Reset();
  }

  void Reset() {
    has_goal_ = false;
    goal_ = GoalState();
    cooldown_.Clear();
    blacklist_.Clear();
    global_cooldown_until_ = 0;
    damage_window_tick_ = -1;
    damage_window_health_ = 0.0;
    eval_count_ = 0;
    ticks_processed_ = 0;
    selections_ = 0;
    switches_ = 0;
    aborts_ = 0;
    reached_ = 0;
    timeouts_ = 0;
    cooldown_blocks_ = 0;
    combat_lock_blocks_ = 0;
    evaluations_ = 0;
    slot_ = 0;
  }

  const ItemProfile& profile() const { return profile_; }
  void set_slot(int slot) { slot_ = slot; }

  bool has_goal() const { return has_goal_; }
  int goal_id() const { return has_goal_ ? goal_.item_id : -1; }
  ItemKind goal_kind() const { return has_goal_ ? goal_.kind : ItemKind::kNone; }
  int goal_started_tick() const { return has_goal_ ? goal_.started_tick : -1; }
  double goal_utility() const { return has_goal_ ? goal_.utility : 0.0; }
  int last_tick() const { return last_tick_; }

  // Planning counters (telemetry / tests). Never used for control.
  int selections() const { return selections_; }
  int switches() const { return switches_; }
  int aborts() const { return aborts_; }
  int reached() const { return reached_; }
  int timeouts() const { return timeouts_; }
  int cooldown_blocks() const { return cooldown_blocks_; }
  int combat_lock_blocks() const { return combat_lock_blocks_; }
  int ticks_processed() const { return ticks_processed_; }
  long long evaluations() const { return evaluations_; }

  // Evaluations of the most recent Step(), best-first order is *not* applied:
  // the array keeps snapshot order so callers can index it by item.
  const ItemEvaluation* last_evaluations(int* count) const {
    if (count != nullptr) *count = eval_count_;
    return evals_;
  }

  // External pickup notification (the world says the item vanished). Does not
  // need navigation feedback; keeps the blacklist in sync.
  void NotifyItemPicked(int item_id, int tick) {
    if (item_id < 0) return;
    blacklist_.Set(item_id, tick + TickFromSeconds(profile_.tuning.consumable_blacklist_s));
    if (has_goal_ && goal_.item_id == item_id) {
      ++reached_;
      CloseGoal(ItemReason::kReached);
    }
  }

  /* ---------------------------------------------------------------------- */
  /* Main tick                                                               */
  /* ---------------------------------------------------------------------- */

  GoalDecision Step(const ItemWorld& w, NavigationSink* nav = nullptr) {
    GoalDecision d;
    nav_ = nav;
    last_tick_ = w.combat.tick;
    const int tick = w.combat.tick;

    const ValidationError ve = ValidateWorld(w);
    if (ve != ValidationError::kOk) {
      // Fail closed: never chase a goal derived from a corrupt snapshot.
      if (has_goal_) {
        CloseGoal(ItemReason::kInvalidWorld);
        d.action = ItemAction::kAbort;
      }
      d.reason = ItemReason::kInvalidWorld;
      d.changed = true;
      std::snprintf(d.explain, sizeof(d.explain), "invalid-world:%s",
                    ValidationErrorName(ve));
      return d;
    }

    ctx_ = MakeContext(profile_, w, slot_);
    ++ticks_processed_;
    UpdateDamageWindow(w);
    EvaluateAll(w);
    d.candidates = w.count;

    // ---- navigation feedback for the running goal ----------------------
    if (has_goal_ && nav_ != nullptr && goal_.nav_submitted) {
      NavFeedback fb{};
      const NavStatus st = nav_->Poll(goal_.item_id, &fb);
      switch (st) {
        case NavStatus::kArrived:
          if (FinishGoal(d, ItemReason::kReached)) return d;
          break;
        case NavStatus::kUnreachable:
        case NavStatus::kRejected:
          if (FinishGoal(d, ItemReason::kUnreachable)) return d;
          break;
        case NavStatus::kExpired:
          ++timeouts_;
          if (FinishGoal(d, ItemReason::kTimeout)) return d;
          break;
        case NavStatus::kStalled:
          if (++goal_.stall_reports >= kStallAbortReports) {
            if (FinishGoal(d, ItemReason::kStalled)) return d;
          }
          break;
        case NavStatus::kAborted:
          if (FinishGoal(d, ItemReason::kItemGone)) return d;
          break;
        default:
          break;
      }
    }

    // ---- keep, abort or switch the running goal ------------------------
    if (has_goal_) {
      const int idx = IndexOfItem(w, goal_.item_id);
      if (idx < 0) {
        if (FinishGoal(d, ItemReason::kItemGone)) return d;
      } else {
        const ItemEvaluation& cur = evals_[idx];
        const double dist = Distance(w.self.eye, cur.pos);
        if (dist <= kArrivalRadiusM) {
          if (FinishGoal(d, ItemReason::kReached)) return d;
        } else if (cur.reject == ItemReason::kUnreachable) {
          if (FinishGoal(d, ItemReason::kUnreachable)) return d;
        } else if (cur.reject == ItemReason::kItemGone) {
          if (FinishGoal(d, ItemReason::kItemGone)) return d;
        } else if (cur.reject == ItemReason::kOutOfRange) {
          if (FinishGoal(d, ItemReason::kOutOfRange)) return d;
        } else if (cur.terms.base <= kNeedEpsilon) {
          if (FinishGoal(d, ItemReason::kNeedSatisfied)) return d;
        } else if (ThreatAbort(w, dist)) {
          if (FinishGoal(d, ItemReason::kThreatOverride)) return d;
        } else if (DamageAbort(w)) {
          if (FinishGoal(d, ItemReason::kDamageAbort)) return d;
        } else if (TimedOut(tick)) {
          ++timeouts_;
          if (FinishGoal(d, ItemReason::kTimeout)) return d;
        } else if (CombatLock(w)) {
          ++combat_lock_blocks_;
          if (FinishGoal(d, ItemReason::kCombatLock)) return d;
        } else {
          // Survives: keep, or switch past the commit margin.
          const ItemEvaluation* best = PickBest(ItemKind::kNone, goal_.item_id);
          const bool dwell_ok =
              (tick - goal_.started_tick) >= TickFromSeconds(profile_.tuning.min_commit_s);
          if (best != nullptr && dwell_ok &&
              best->terms.utility >
                  cur.terms.utility * (1.0 + profile_.tuning.commit_margin)) {
            if (CommitGoal(*best, tick, ItemReason::kSwitched)) {
              ++switches_;
              FillDecision(d, ItemAction::kSwitch, ItemReason::kSwitched, true);
              return d;
            }
            // Navigation refused the alternative: stay on the current trip.
          }
          goal_.last_update_tick = tick;
          goal_.utility = cur.terms.utility;
          goal_.need = cur.terms.need;
          FillDecision(d, ItemAction::kKeep,
                       dwell_ok ? ItemReason::kKept : ItemReason::kHysteresisHold,
                       false);
          return d;
        }
      }
    }

    // ---- no goal: may we start one? ------------------------------------
    if (tick < global_cooldown_until_) {
      ++cooldown_blocks_;
      d.reason = ItemReason::kCooldown;
      std::snprintf(d.explain, sizeof(d.explain), "cooldown:%dt",
                    global_cooldown_until_ - tick);
      return d;
    }
    if (CombatLock(w)) {
      ++combat_lock_blocks_;
      d.reason = ItemReason::kCombatLock;
      std::snprintf(d.explain, sizeof(d.explain), "combat-lock:%.2f/%.2f",
                    w.combat.combat_priority, profile_.tuning.combat_lock_priority);
      return d;
    }

    const ItemEvaluation* best = PickBest(ItemKind::kNone, -1);
    if (best == nullptr) {
      d.reason = ExplainNoCandidate();
      std::snprintf(d.explain, sizeof(d.explain), "no-candidate:%s",
                    ItemReasonName(d.reason));
      return d;
    }
    if (!CommitGoal(*best, tick, ItemReason::kSelected)) {
      d.reason = ItemReason::kUnreachable;
      std::snprintf(d.explain, sizeof(d.explain), "nav-refused:%d", best->item_id);
      return d;
    }
    ++selections_;
    FillDecision(d, ItemAction::kSelect, ItemReason::kSelected, true);
    return d;
  }

 private:
  struct GoalState {
    int item_id = -1;
    ItemKind kind = ItemKind::kNone;
    int weapon_index = 0;
    Vec3 pos{};
    int started_tick = 0;
    int last_update_tick = 0;
    double utility = 0.0;
    double need = 0.0;
    int stall_reports = 0;
    bool survival = false;
    bool nav_submitted = false;
  };

  /* --- evaluation ------------------------------------------------------ */

  void EvaluateAll(const ItemWorld& w) {
    eval_count_ = w.count;
    for (int i = 0; i < w.count; ++i) {
      evals_[i] = EvaluateItem(ctx_, w, i);
    }
    evaluations_ += w.count;
  }

  int IndexOfItem(const ItemWorld& w, int item_id) const {
    for (int i = 0; i < w.count; ++i) {
      if (w.items[i].id == item_id) return i;
    }
    return -1;
  }

  const ItemEvaluation* PickBest(ItemKind /*preferred*/, int exclude_id) {
    const ItemEvaluation* best = nullptr;
    for (int i = 0; i < eval_count_; ++i) {
      const ItemEvaluation& e = evals_[i];
      if (!e.eligible) continue;
      if (e.item_id == exclude_id) continue;
      if (cooldown_.Active(e.item_id, last_tick_)) continue;
      if (blacklist_.Active(e.item_id, last_tick_)) continue;
      if (best == nullptr || BetterEvaluation(e, *best)) best = &e;
    }
    return best;
  }

  ItemReason ExplainNoCandidate() const {
    // Report the most informative blocking reason instead of a generic miss.
    bool out_of_range = false;
    bool combat_lock = false;
    bool cooldown = false;
    bool unreachable = false;
    bool resupply_candidate = false;
    for (int i = 0; i < eval_count_; ++i) {
      const ItemEvaluation& e = evals_[i];
      if (e.kind == ItemKind::kAmmo || e.kind == ItemKind::kWeapon) {
        resupply_candidate = true;
      }
      if (e.reject == ItemReason::kOutOfRange) out_of_range = true;
      if (e.reject == ItemReason::kCombatLock) combat_lock = true;
      if (e.reject == ItemReason::kUnreachable) unreachable = true;
      if (cooldown_.Active(e.item_id, last_tick_) ||
          blacklist_.Active(e.item_id, last_tick_)) {
        cooldown = true;
      }
    }
    // A starved bot with nothing to resupply it cannot fix the problem by
    // walking: the combat layer has to switch to a working weapon instead.
    if (ctx_.self.ammunition_starved && !resupply_candidate) {
      return ItemReason::kAmmoStarved;
    }
    if (unreachable) return ItemReason::kUnreachable;
    if (combat_lock) return ItemReason::kCombatLock;
    if (out_of_range) return ItemReason::kOutOfRange;
    if (cooldown) return ItemReason::kCooldown;
    return ItemReason::kNoCandidate;
  }

  /* --- goal lifecycle -------------------------------------------------- */

  // Returns false when the navigation seam refused the goal; the running goal
  // (if any) is then left untouched, so a refused switch never loses the
  // current trip.
  bool CommitGoal(const ItemEvaluation& e, int tick, ItemReason reason) {
    GoalState next;
    next.item_id = e.item_id;
    next.kind = e.kind;
    next.weapon_index = e.weapon_index;
    next.pos = e.pos;
    next.started_tick = tick;
    next.last_update_tick = tick;
    next.utility = e.terms.utility;
    next.need = e.terms.need;
    next.survival = (e.kind == ItemKind::kHealth || e.kind == ItemKind::kArmor) &&
                    ctx_.health_frac < kUrgentHealthFrac;

    if (nav_ != nullptr) {
      GoalTranslationInput ti;
      ti.goal_id = e.item_id;
      ti.pos = e.pos;
      ti.survival = next.survival;
      // "Urgent" is reserved for the bot's actual capability: no loaded ranged
      // weapon, or health already below half. It is not a shortcut for size.
      ti.urgent = ctx_.self.ammunition_starved || ctx_.health_frac < 0.50;
      ti.combat_engaged = ctx_.engaged;
      ti.utility = e.terms.utility;
      ti.issued_tick = tick;
      ti.max_duration_ticks = TickFromSeconds(profile_.tuning.max_search_time_s) + 20;
      ti.caution = profile_.persona.caution;
      const NavGoal g = MakeNavGoal(ti);
      const NavStatus st = nav_->Submit(g);
      if (st != NavStatus::kAccepted && st != NavStatus::kInProgress) {
        // Navigation cannot handle this goal: blacklist and keep going. The
        // previous goal is deliberately NOT cancelled before this point.
        blacklist_.Set(e.item_id, tick + 300 * static_cast<int>(kTickHz));
        return false;
      }
      next.nav_submitted = true;
    }
    if (has_goal_ && nav_ != nullptr && goal_.nav_submitted) {
      nav_->Cancel(goal_.item_id);
    }
    goal_ = next;
    has_goal_ = true;
    (void)reason;
    return true;
  }

  bool FinishGoal(GoalDecision& d, ItemReason reason) {
    if (!has_goal_) return false;
    const int id = goal_.item_id;
    const ItemKind kind = goal_.kind;
    const Vec3 pos = goal_.pos;
    const double utility = goal_.utility;
    const int tick = last_tick_;

    switch (reason) {
      case ItemReason::kReached:
        ++reached_;
        blacklist_.Set(id,
                       tick + TickFromSeconds(profile_.tuning.consumable_blacklist_s));
        break;
      case ItemReason::kUnreachable:
        blacklist_.Set(id, tick + TickFromSeconds(profile_.tuning.consumable_blacklist_s) +
                               600);
        break;
      case ItemReason::kNeedSatisfied:
      case ItemReason::kItemGone:
        break;  // no penalty, the world changed
      default:
        // Trouble abort: back off from this item *and* pause searching.
        cooldown_.Set(id, tick + TickFromSeconds(profile_.tuning.abort_cooldown_s));
        global_cooldown_until_ =
            tick + TickFromSeconds(profile_.tuning.search_cooldown_s);
        ++aborts_;
        break;
    }

    CloseGoal(reason);
    d.action = reason == ItemReason::kReached ? ItemAction::kReached
                                              : ItemAction::kAbort;
    d.reason = reason;
    d.changed = true;
    d.has_goal = false;
    d.goal_id = id;
    d.goal_kind = kind;
    d.goal_pos = pos;
    d.utility = utility;
    std::snprintf(d.explain, sizeof(d.explain), "%s:%s(%d)", ItemActionName(d.action),
                  ItemReasonName(reason), id);
    return true;
  }

  void CloseGoal(ItemReason reason) {
    if (!has_goal_) return;
    if (nav_ != nullptr && goal_.nav_submitted) nav_->Cancel(goal_.item_id);
    has_goal_ = false;
    goal_ = GoalState();
    (void)reason;
  }

  void FillDecision(GoalDecision& d, ItemAction action, ItemReason reason, bool changed) {
    d.action = action;
    d.reason = reason;
    d.changed = changed;
    d.has_goal = has_goal_;
    if (!has_goal_) return;
    d.goal_id = goal_.item_id;
    d.goal_kind = goal_.kind;
    d.goal_weapon_index = goal_.weapon_index;
    d.goal_pos = goal_.pos;
    d.utility = goal_.utility;
    d.need = goal_.need;
    d.suppress_combat = goal_.survival;
    for (int i = 0; i < eval_count_; ++i) {
      if (evals_[i].item_id == goal_.item_id) {
        d.travel_s = evals_[i].terms.travel_s;
        d.distance_m = evals_[i].distance_m;
        break;
      }
    }
    std::snprintf(d.explain, sizeof(d.explain), "%s %s id=%d need=%.2f u=%.2f t=%.1fs",
                  ItemActionName(action), ItemKindName(goal_.kind), goal_.item_id,
                  goal_.need, goal_.utility, d.travel_s);
  }

  /* --- abort predicates ------------------------------------------------ */

  bool ThreatAbort(const ItemWorld& w, double distance_to_goal_m) const {
    const ThreatState& t = w.threat;
    if (t.visible_enemies <= 0 || t.nearest_enemy_m < 0.0) return false;
    if (distance_to_goal_m <= profile_.tuning.close_finish_radius_m) return false;
    if (ctx_.health_frac >= profile_.tuning.health_abort_frac) return false;
    return t.nearest_enemy_m <= profile_.tuning.enemy_abort_radius_m;
  }

  bool DamageAbort(const ItemWorld& w) const {
    if (damage_window_tick_ < 0) return false;
    const double lost = damage_window_health_ - w.self.health;
    if (lost <= 0.0) return false;
    const double frac = lost / (w.self.max_health > 0.0 ? w.self.max_health : 100.0);
    return frac > profile_.tuning.abort_damage_frac;
  }

  bool TimedOut(int tick) const {
    const int limit = TickFromSeconds(profile_.tuning.max_search_time_s);
    return (tick - goal_.started_tick) > (limit > 0 ? limit : 1);
  }

  bool CombatLock(const ItemWorld& w) const {
    if (!w.combat.engaged) return false;
    if (w.combat.combat_priority <= profile_.tuning.combat_lock_priority) return false;
    return ctx_.health_frac >= kUrgentHealthFrac;
  }

  void UpdateDamageWindow(const ItemWorld& w) {
    const int window = TickFromSeconds(profile_.tuning.damage_window_s);
    const int tick = w.combat.tick;
    if (damage_window_tick_ < 0 || (tick - damage_window_tick_) >= (window > 0 ? window : 1) ||
        w.self.health > damage_window_health_) {
      damage_window_tick_ = tick;
      damage_window_health_ = w.self.health;
    }
  }

  /* --- state ----------------------------------------------------------- */
  ItemProfile profile_{};
  ScoreContext ctx_{};
  GoalState goal_{};
  bool has_goal_ = false;
  NavigationSink* nav_ = nullptr;
  TimerTable cooldown_;
  TimerTable blacklist_;
  int global_cooldown_until_ = 0;
  int damage_window_tick_ = -1;
  double damage_window_health_ = 0.0;
  int eval_count_ = 0;
  ItemEvaluation evals_[kMaxItems];
  int last_tick_ = 0;
  int slot_ = 0;

  // counters
  int ticks_processed_ = 0;
  int selections_ = 0;
  int switches_ = 0;
  int aborts_ = 0;
  int reached_ = 0;
  int timeouts_ = 0;
  int cooldown_blocks_ = 0;
  int combat_lock_blocks_ = 0;
  long long evaluations_ = 0;
};

}  // namespace itemai

#endif  // ITEMAI_ITEM_PLANNER_H
