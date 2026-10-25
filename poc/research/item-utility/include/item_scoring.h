// SPDX-License-Identifier: GPL-2.0-only
// item_scoring.h - the utility-scoring system of the item layer.
//
// MODEL (multiplicative "need x supply x opportunity" gating)
//
//   base      = need * scarcity * capability
//   utility   = base * threat * priority * time * distance * freshness
//               * personality * skill_planning
//
// Every factor is bounded and documented; the product stays in [0, ~1.6] and
// is comparable across item kinds, which is the whole point: a bot must be
// able to compare "20 health" against "ammo for my only working gun".
//
// * need        how badly the bot lacks this resource *right now* (0..1).
//               Health is a convex deficit (critical health is worth much more
//               than the same nominal points at 90 %), armor a linear deficit
//               with a lower ceiling, ammo depends on whether the refilled
//               weapon is the bot's actual capability, weapons on the relative
//               capability gain, powerups/strategic on caller-supplied value.
// * scarcity    how rare that resource is (bounded 0.5..1.5); ammo gets more
//               scarce the more the bot depends on it.
// * capability  how much of the need this *specific* item can actually cover
//               (yield vs. remaining deficit). A +1 health pickup is worth
//               almost nothing at 40/100 hp, a +50 is worth a lot. This is the
//               term that stops "collect every health item always".
// * threat      1 - risk_awareness * caution-scaled exposure. Walking into a
//               visible enemy's face is discounted; with no visible enemy the
//               factor is exactly 1.
// * priority    1 - combat_lock * combat_priority. A committed fight suppresses
//               resource detours. Health below the critical threshold is
//               exempt (the planner then asks the combat layer to yield).
// * time        1 - time_weight * min(1, travel / planning_horizon). Uses the
//               caller's speed, not a hard-coded one.
// * distance    0.65..1.0 smooth "nearer is better, but not overridingly so".
//               Kept separate because the task asks for it explicitly and it
//               also keeps the score continuous at the travel cutoff.
// * freshness   1 - 0.45 * min(1, staleness / memory_horizon) for items the
//               caller has not confirmed visible.
//
// Deterministic tie-break: only when two utilities are exactly equal, a
// per-bot/per-item hash (seed) decides. It is never a success chance.

#ifndef ITEMAI_ITEM_SCORING_H
#define ITEMAI_ITEM_SCORING_H

#include <cmath>

#include "item_profile.h"
#include "item_snapshot.h"
#include "item_types.h"

namespace itemai {

constexpr double kUrgentHealthFrac = 0.35;  // below this health, need is convex
constexpr double kFullHealthFrac = 0.98;    // at/above this, health is useless

/* ------------------------------------------------------------------------ */
/* Pre-computed per-tick context                                             */
/* ------------------------------------------------------------------------ */

struct ScoreContext {
  SelfAssessment self;
  ItemSkillBlock skill;
  ItemPersonalityBlock persona;
  ItemTuning tuning;
  uint32_t seed = 1u;
  int slot = 0;
  int tick = 0;

  double health_deficit_pts = 0.0;
  double armor_deficit_pts = 0.0;
  double health_frac = 1.0;
  double armor_frac = 0.0;
  double ammo_pressure = 0.0;       // 0..1, how much the bot needs ammo
  double ammo_pressure_frac = 0.0;  // 0..1, mood-adjusted
  double mood = 1.0;                // deterministic personality modulation
  double combat_priority = 0.0;
  bool engaged = false;
  int visible_enemies = 0;
  double nearest_enemy_m = -1.0;
  bool under_fire = false;
};

// Deterministic mood: only the "flaky" personality oscillates, and it does so
// from its own seed, not from a global RNG. Everything else returns 1.0.
inline double ItemMood(const ItemProfile& p, int tick) {
  if (p.persona_index != 5) return 1.0;
  const double t = SecondsFromTicks(tick);
  const double phase = static_cast<double>(p.seed % 997u) * 0.0063;
  return 1.0 + 0.18 * std::sin(0.35 * t + phase);
}

inline ScoreContext MakeContext(const ItemProfile& p, const ItemWorld& w,
                                int slot = 0) {
  ScoreContext c;
  c.self = AssessSelf(w, p.persona.weapon_appetite >= 1.0 ? 0.15 : 0.0);
  c.skill = p.skill;
  c.persona = p.persona;
  c.tuning = p.tuning;
  c.seed = p.seed;
  c.slot = slot;
  c.tick = w.combat.tick;
  c.health_frac = c.self.health_frac;
  c.armor_frac = c.self.armor_frac;
  c.health_deficit_pts = w.self.max_health - w.self.health;
  c.armor_deficit_pts = w.self.max_armor - w.self.armor;
  c.combat_priority = w.combat.combat_priority;
  c.engaged = w.combat.engaged;
  c.visible_enemies = w.threat.visible_enemies;
  c.nearest_enemy_m = w.threat.nearest_enemy_m;
  c.under_fire = w.threat.under_fire;

  // Ammo pressure: how much of the bot's ranged capability is actually
  // available. Starvation (owned ranged weapons, none loaded) is maximal.
  if (c.self.ammunition_starved) {
    c.ammo_pressure = 1.0;
  } else if (c.self.best_weapon > 1) {
    const int cap = WeaponAmmoCap(c.self.best_weapon);
    const double fill = cap > 0
        ? Clamp01(static_cast<double>(w.self.ammo[c.self.best_weapon]) / cap)
        : 1.0;
    c.ammo_pressure = fill < 0.35 ? 0.60 : (fill < 0.65 ? 0.35 : 0.20);
  } else {
    c.ammo_pressure = 0.85;  // melee only
  }

  c.mood = ItemMood(p, w.combat.tick);
  c.ammo_pressure_frac = Clamp01(c.ammo_pressure);
  return c;
}

/* ------------------------------------------------------------------------ */
/* Individual scoring terms                                                  */
/* ------------------------------------------------------------------------ */

// Convex health need: recovering from 10 % is worth far more than topping off
// from 90 %. At/above kFullHealthFrac the need is exactly zero.
inline double HealthNeed(const ScoreContext& c) {
  const double hf = Clamp01(c.health_frac);
  if (hf >= kFullHealthFrac) return 0.0;
  const double linear = 1.0 - hf;
  if (hf >= kUrgentHealthFrac) return linear * 0.75;
  const double urgent = 0.55 + 0.45 * (1.0 - hf / kUrgentHealthFrac);
  const double v = linear * 0.75 > urgent ? linear * 0.75 : urgent;
  return Clamp01(v);
}

inline double ArmorNeed(const ScoreContext& c) {
  const double af = Clamp01(c.armor_frac);
  if (af >= kFullHealthFrac) return 0.0;
  return Clamp01((1.0 - af) * 0.82);
}

// Ammo need for one weapon index. Ammo the bot cannot use (weapon not owned)
// is worthless; ammo for a weapon it does not load is discounted.
inline double AmmoNeed(const ScoreContext& c, const ItemWorld& w, int weapon_index) {
  if (weapon_index < 1 || weapon_index > kWeaponCount) return 0.0;
  if (!WeaponOwned(w.self.owned_weapons, weapon_index)) return 0.0;
  const int cap = WeaponAmmoCap(weapon_index);
  if (cap <= 0) return 0.0;  // melee: no ammo exists
  const double current = static_cast<double>(w.self.ammo[weapon_index]);
  const double fill = Clamp01(current / cap);
  if (fill >= kFullHealthFrac) return 0.0;

  // How much of the bot's capability this weapon represents at the reference
  // distance. A near-best weapon's ammo matters; a leftover pistol's does not.
  const double ref = c.self.reference_distance_m;
  const double score = StandInWeaponScore(weapon_index, ref, 0.0);
  const double best = c.self.best_weapon_score > 1e-6 ? c.self.best_weapon_score : 1e-6;
  const double rel = Clamp01(score / best);

  const double deficit = 1.0 - fill;
  const double pressure = 0.35 + 0.65 * c.ammo_pressure_frac;
  const double weapon_relevance = 0.30 + 0.70 * rel;
  double need = deficit * pressure * weapon_relevance;
  // An empty weapon that is the bot's main capability is an emergency.
  if (current <= 0.5 && rel > 0.75) need = need > 0.75 ? need : 0.75;
  return Clamp01(need);
}

// Weapon need: capability gain over the best weapon already held. Holding the
// weapon already means the pickup is just ammo.
inline double WeaponNeed(const ScoreContext& c, const ItemWorld& w, int weapon_index) {
  if (weapon_index < 1 || weapon_index > kWeaponCount) return 0.0;
  const double ref = c.self.reference_distance_m;
  const double candidate =
      StandInWeaponScore(weapon_index, ref, 0.0);
  const double best = c.self.best_weapon_score;

  if (WeaponOwned(w.self.owned_weapons, weapon_index)) {
    // Duplicate pickup = ammo. Modest, but real when the weapon is in use.
    return Clamp01(0.45 * AmmoNeed(c, w, weapon_index));
  }
  if (best <= 1e-6) return 1.0;  // nothing usable at all
  const double gain = (candidate - best) / best;
  if (gain <= 0.0) {
    // A weapon worse than what the bot holds is still worth having (it is a
    // spare), but only barely - and never while ammunition is plentiful.
    return Clamp01(0.10 * (1.0 - c.ammo_pressure_frac));
  }
  return Clamp01(gain);
}

// How much of the outstanding deficit this specific item covers.
inline double Capability(const ScoreContext& c, const ItemWorld& w,
                         const ItemSnapshot& it) {
  switch (it.kind) {
    case ItemKind::kHealth: {
      if (it.value <= 0.0) return 1.0;
      const double deficit = c.health_deficit_pts > 1.0 ? c.health_deficit_pts : 1.0;
      const double useful = it.value < deficit ? it.value : deficit;
      return Clamp01(useful / deficit);
    }
    case ItemKind::kArmor: {
      if (it.value <= 0.0) return 1.0;
      const double deficit = c.armor_deficit_pts > 1.0 ? c.armor_deficit_pts : 1.0;
      const double useful = it.value < deficit ? it.value : deficit;
      return Clamp01(useful / deficit);
    }
    case ItemKind::kAmmo: {
      const int cap = WeaponAmmoCap(it.weapon_index);
      if (cap <= 0) return 0.0;
      const double have = static_cast<double>(w.self.ammo[it.weapon_index]);
      const double missing = cap - have > 1.0 ? cap - have : 1.0;
      const double amount = it.amount > 0 ? static_cast<double>(it.amount) : it.value;
      const double useful = amount < missing ? amount : missing;
      return Clamp01(useful / missing);
    }
    case ItemKind::kWeapon:
      return 1.0;
    case ItemKind::kPowerup:
    case ItemKind::kStrategic:
      return Clamp01(it.value > 0.0 ? it.value : 0.5);
    default:
      return 0.0;
  }
}

inline double Scarcity(const ScoreContext& c, const ItemSnapshot& it) {
  double r = 0.6;
  switch (it.kind) {
    case ItemKind::kHealth: r = 0.75; break;
    case ItemKind::kArmor: r = 0.80; break;
    case ItemKind::kAmmo: r = 0.45 + 0.85 * c.ammo_pressure_frac; break;
    case ItemKind::kWeapon: r = 0.95; break;
    case ItemKind::kPowerup: r = 1.05; break;
    case ItemKind::kStrategic: r = 0.55; break;
    default: return 1.0;
  }
  const double v = 0.75 + 0.5 * r;
  return Clamp(v, 0.5, 1.5);
}

// 0..1 exposure of the bot to a visible threat at the given distance.
inline double Exposure(const ScoreContext& c) {
  if (c.visible_enemies <= 0 || c.nearest_enemy_m < 0.0) return 0.0;
  const double proximity = Clamp01(1.0 - c.nearest_enemy_m / 25.0);
  const double fire = c.under_fire ? 1.0 : 0.55;
  return proximity * fire;
}

inline double ThreatFactor(const ScoreContext& c) {
  // Risk is priced *correctly* only as far as the skill's risk_awareness goes;
  // a beginner underrates danger, an expert does not.
  const double discount = c.tuning.threat_weight * c.skill.risk_awareness * Exposure(c);
  return Clamp(1.0 - discount, 0.30, 1.0);
}

inline double PriorityFactor(const ScoreContext& c, const ItemSnapshot& it) {
  if (!c.engaged || c.combat_priority <= 0.0) return 1.0;
  double priority = c.combat_priority;
  // A dying bot must be allowed to disengage even mid-fight.
  if ((it.kind == ItemKind::kHealth || it.kind == ItemKind::kArmor) &&
      c.health_frac < kUrgentHealthFrac) {
    priority *= 0.25;
  }
  const double f = 1.0 - c.tuning.combat_lock_priority * priority;
  return Clamp(f, 0.05, 1.0);
}

inline double TravelSeconds(const ItemWorld& w, const ItemSnapshot& it) {
  const double d = Distance(w.self.eye, it.pos);
  const double speed = w.self.move_speed_mps > 0.1 ? w.self.move_speed_mps : 0.1;
  return d / speed + 0.35;  // + a short, documented pickup/handling overhead
}

inline double TimeFactor(const ScoreContext& c, double travel_s) {
  const double horizon = c.tuning.memory_horizon_s > 0.5 ? c.tuning.memory_horizon_s : 0.5;
  const double ratio = Clamp01(travel_s / horizon);
  return Clamp(1.0 - c.tuning.time_weight * ratio, 0.10, 1.0);
}

inline double DistanceFactor(const ItemWorld& w, const ItemSnapshot& it) {
  const double d = Distance(w.self.eye, it.pos);
  return 0.65 + 0.35 * Clamp01(1.0 - d / 40.0);
}

inline double FreshnessFactor(const ScoreContext& c, const ItemSnapshot& it) {
  if (it.visible) return 1.0;
  const double horizon = c.tuning.memory_horizon_s > 0.5 ? c.tuning.memory_horizon_s : 0.5;
  const double age = Clamp01(it.staleness_s / horizon);
  return Clamp(1.0 - 0.45 * age, 0.40, 1.0);
}

inline double AppetiteFor(const ScoreContext& c, ItemKind kind) {
  switch (kind) {
    case ItemKind::kHealth: return c.persona.health_appetite;
    case ItemKind::kArmor: return c.persona.armor_appetite;
    case ItemKind::kAmmo: return c.persona.ammo_appetite;
    case ItemKind::kWeapon: return c.persona.weapon_appetite;
    case ItemKind::kPowerup: return c.persona.powerup_appetite;
    case ItemKind::kStrategic: return c.persona.strategic_appetite;
    default: return 1.0;
  }
}

// Skill scaling: a better planner discounts far-away pickups more strongly
// (because it values its own time) and wastes fewer trips.
inline double SkillFactor(const ScoreContext& c, double travel_s) {
  const double horizon = c.skill.planning_horizon_s > 0.5 ? c.skill.planning_horizon_s : 0.5;
  const double far = Clamp01(travel_s / (horizon * 2.0));
  return Clamp(1.0 - 0.35 * c.skill.risk_awareness * far * far, 0.45, 1.0);
}

/* ------------------------------------------------------------------------ */
/* One evaluation                                                            */
/* ------------------------------------------------------------------------ */

struct ScoreTerms {
  double need = 0.0;
  double scarcity = 1.0;
  double capability = 0.0;
  double base = 0.0;
  double threat = 1.0;
  double priority = 1.0;
  double time = 1.0;
  double distance = 1.0;
  double freshness = 1.0;
  double appetite = 1.0;
  double skill = 1.0;
  double travel_s = 0.0;
  double utility = 0.0;
  double tiebreak = 0.0;
};

struct ItemEvaluation {
  int item_index = -1;   // index into ItemWorld::items
  int item_id = -1;
  ItemKind kind = ItemKind::kNone;
  int weapon_index = 0;
  Vec3 pos{};
  double distance_m = 0.0;
  ScoreTerms terms;
  bool eligible = false;
  ItemReason reject = ItemReason::kNone;
  bool selected = false;
};

// Full evaluation of one item. `intent` is the item the bot is currently
// travelling to (or -1); it only affects the documented "close finish" rule.
inline ItemEvaluation EvaluateItem(const ScoreContext& c, const ItemWorld& w,
                                   int item_index) {
  ItemEvaluation e;
  e.item_index = item_index;
  const ItemSnapshot& it = w.items[item_index];
  e.item_id = it.id;
  e.kind = it.kind;
  e.weapon_index = it.weapon_index;
  e.pos = it.pos;
  e.distance_m = Distance(w.self.eye, it.pos);

  ScoreTerms& t = e.terms;
  t.travel_s = TravelSeconds(w, it);

  // --- need ------------------------------------------------------------
  switch (it.kind) {
    case ItemKind::kHealth: t.need = HealthNeed(c); break;
    case ItemKind::kArmor: t.need = ArmorNeed(c); break;
    case ItemKind::kAmmo: t.need = AmmoNeed(c, w, it.weapon_index); break;
    case ItemKind::kWeapon: t.need = WeaponNeed(c, w, it.weapon_index); break;
    case ItemKind::kPowerup:
      t.need = Clamp01(it.value) * (c.engaged ? 1.0 : 0.55);
      break;
    case ItemKind::kStrategic:
      // Strategic resources are worth *more* when there is no fight to win.
      t.need = Clamp01(it.value) * (c.engaged ? 0.35 : 1.0);
      break;
    default:
      t.need = 0.0;
      break;
  }
  t.appetite = Clamp(AppetiteFor(c, it.kind), 0.0, 2.0);
  t.need = Clamp01(t.need * t.appetite * (it.kind == ItemKind::kPowerup ||
                                         it.kind == ItemKind::kStrategic
                                             ? 1.0
                                             : c.mood));

  t.scarcity = Scarcity(c, it);
  t.capability = Capability(c, w, it);
  t.base = t.need * t.scarcity * t.capability;

  t.threat = ThreatFactor(c);
  t.priority = PriorityFactor(c, it);
  t.time = TimeFactor(c, t.travel_s);
  t.distance = DistanceFactor(w, it);
  t.freshness = FreshnessFactor(c, it);
  t.skill = SkillFactor(c, t.travel_s);
  t.utility = t.base * t.threat * t.priority * t.time * t.distance *
              t.freshness * t.skill;
  t.tiebreak = TieBreakUnit(c.seed, it.id, c.slot);

  // --- eligibility (hard, explainable rejects) -------------------------
  e.eligible = true;
  if (!it.reachable) {
    e.eligible = false;
    e.reject = ItemReason::kUnreachable;
  } else if (it.respawn_s > 0.0) {
    e.eligible = false;
    e.reject = ItemReason::kItemGone;
  } else if (t.travel_s > c.tuning.max_search_time_s) {
    e.eligible = false;
    e.reject = ItemReason::kOutOfRange;
  } else if (t.base <= kNeedEpsilon) {
    // No need at all: this is the "full health does not chase health" gate.
    e.eligible = false;
    e.reject = ItemReason::kNeedSatisfied;
  } else if (t.utility < c.tuning.min_utility) {
    e.eligible = false;
    e.reject = ItemReason::kNoCandidate;
  } else if (c.engaged && c.combat_priority > c.tuning.combat_lock_priority &&
             !(it.kind == ItemKind::kHealth && c.health_frac < kUrgentHealthFrac)) {
    e.eligible = false;
    e.reject = ItemReason::kCombatLock;
  }
  return e;
}

// Strict "better than": utility first, then deterministic tie-break, then the
// lower item id (so the result never depends on the caller's array order).
inline bool BetterEvaluation(const ItemEvaluation& a, const ItemEvaluation& b) {
  if (a.terms.utility > b.terms.utility + 1e-12) return true;
  if (b.terms.utility > a.terms.utility + 1e-12) return false;
  if (a.terms.tiebreak > b.terms.tiebreak + 1e-12) return true;
  if (b.terms.tiebreak > a.terms.tiebreak + 1e-12) return false;
  return a.item_id < b.item_id;
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_SCORING_H
