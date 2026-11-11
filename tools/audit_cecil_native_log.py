#!/usr/bin/env python3
"""Offline evidence from a complete fresh Cecil native log; never full qualification.

--epoch is private JSON with pid, start_ticks, dll_sha256, world, map_crc32.
These are caller-supplied process/map pins, not independently verified runtime
identity. Whole-file hashes bind the report to its inputs. No launches, network,
process inspection, file changes, raw coordinates or player names in output.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

FIELDS = re.compile(r"(\w+)=([^\s]+)")
TAG = re.compile(r"\[(CecilState|CecilSpawn|CecilDeath|CecilGoal|CecilGoalEnd|CecilPickup)\]\s+(.*)")
LOAD = re.compile(r"\[CecilLoad\].*?world=(.*?)\s+ready=([01])\s+nodes=\d+\s+map_crc=([0-9a-fA-F]{8})")
BAD = re.compile(r"SYNCBAD|Too many bad syncs|CRC check failed|Access violation|Fatal Error|\[CecilLoad\] rejected=|\[CecilInvalidAction\]", re.I)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def percentile(values):
    return sorted(values)[math.ceil(.95 * len(values)) - 1]


def position(value):
    result = tuple(map(float, value.strip("()").split(",")))
    require(len(result) == 3 and all(map(math.isfinite, result)), "invalid native position")
    return result


def parse(lines, local_slot):
    records, loads, issues, slots = [], [], [], set()
    last_tick = -1
    seen = set()
    for line_number, line in enumerate(lines, 1):
        if BAD.search(line):
            issues.append(f"native error at line {line_number}")
        load = LOAD.search(line)
        if load and load[2] == "1":
            loads.append((load[1], load[3].lower()))
        match = TAG.search(line)
        if not match:
            continue
        # Never mix a second map/load epoch into a prospective first-ten cohort.
        if len(loads) > 1:
            continue
        try:
            pairs = FIELDS.findall(match[2]); fields = dict(pairs)
            require(len(pairs) == len(fields), "duplicate native fields")
            fields["local"], fields["tick"] = int(fields["local"]), int(fields["tick"])
            slots.add(fields["local"])
            if fields["local"] != local_slot:
                continue
            require(fields["tick"] >= 0 and fields["tick"] >= last_tick, "native tick decreased")
            last_tick = fields["tick"]
            tag = match[1]
            if tag != "CecilGoalEnd":
                require((tag, fields["tick"]) not in seen, "duplicate native record")
                seen.add((tag, fields["tick"]))
            required = {"CecilState": ("generation", "entity", "alive", "owned", "shots", "vis", "deaths", "respawns"),
                        "CecilSpawn": ("entity", "generation", "respawns"),
                        "CecilDeath": ("entity", "generation", "deaths"),
                        "CecilGoal": ("entity", "kind", "weapon"),
                        "CecilPickup": ("old", "owned", "current", "goal_entity", "goal_picked"),
                        "CecilGoalEnd": ("entity",)}[tag]
            for key in required:
                fields[key] = int(fields[key]); require(fields[key] >= 0, "negative native field")
            if tag in ("CecilState", "CecilSpawn", "CecilGoal", "CecilPickup"):
                fields["pos"] = position(fields["pos"])
            if tag == "CecilGoalEnd":
                require(bool(fields["reason"]), "missing goal-end reason")
            if tag == "CecilState":
                require(fields["alive"] in (0, 1), "invalid alive flag")
            if tag == "CecilGoal" and fields["kind"] == 0:
                require(1 <= fields["weapon"] <= 14 and fields["entity"] > 0, "invalid native weapon goal")
            if tag == "CecilGoal":
                if "mapped" in fields:
                    fields["mapped"] = int(fields["mapped"]); require(fields["mapped"] in (0, 1), "invalid mapped flag")
                if "deadline" in fields:
                    fields["deadline"] = float(fields["deadline"])
                    require(math.isfinite(fields["deadline"]) and fields["deadline"] >= 0, "invalid goal deadline")
            if tag in ("CecilSpawn", "CecilDeath"):
                require(fields["respawns" if tag == "CecilSpawn" else "deaths"] > 0, "invalid lifecycle counter")
            if tag == "CecilPickup":
                require(fields["goal_picked"] in (0, 1) and max(fields["old"], fields["owned"]) <= 0xffffffff,
                        "invalid native pickup mask")
            records.append((tag, fields))
        except (ValueError, KeyError, TypeError):
            issues.append(f"malformed or nonmonotonic native row at line {line_number}")
    return records, loads, issues, slots


def weapon_goals(records):
    goals, active = [], None
    previous_state = None
    for tag, row in records:
        if tag in ("CecilSpawn", "CecilDeath"):
            if active and active["end_reason"] is None:
                active["end_reason"] = "observed_death" if tag == "CecilDeath" else "spawn_or_generation_boundary"
            if tag == "CecilSpawn": previous_state = row
        elif tag == "CecilState":
            if active and active["end_reason"] is None:
                if previous_state and (row["generation"] != previous_state["generation"] or row["respawns"] != previous_state["respawns"]):
                    active["end_reason"] = "spawn_or_generation_boundary"
                elif not row["alive"]:
                    active["end_reason"] = "observed_death"
            previous_state = row
        elif tag == "CecilGoal":
            if active and active["end_reason"] is None:
                active["end_reason"] = "superseded"
            active = None
            if row["kind"] != 0:
                continue
            active = dict(tick=row["tick"], entity=row["entity"], weapon=row["weapon"],
                          acquisition="NO_MATCHING_ACQUISITION", end_reason=None,
                          picked_mask_observed=False, ownership_gain_observed=False,
                          distance_from_selected_item_m=None, _pos=row["pos"])
            for key in ("mapped", "deadline"):
                if key in row: active[key] = row[key]
            goals.append(active)
        elif tag == "CecilPickup" and active and active["end_reason"] is None:
            if row["goal_entity"] != active["entity"]:
                continue
            mask = 1 << (active["weapon"] - 1) if 1 <= active["weapon"] <= 30 else 0
            gained = bool((row["owned"] & ~row["old"]) & mask)
            picked = row["goal_picked"] == 1
            active["picked_mask_observed"] |= picked
            active["ownership_gain_observed"] |= gained
            if gained:
                active["acquisition"] = "OWNERSHIP_GAIN_MATCHING_GOAL_AND_MASK" if picked else "OWNERSHIP_GAIN_MATCHING_GOAL"
                active["distance_from_selected_item_m"] = math.dist(active["_pos"], row["pos"])
                active["acquisition_tick"] = row["tick"]
            elif picked and not active["ownership_gain_observed"]:
                active["acquisition"] = "MASK_ONLY"
        elif tag == "CecilGoalEnd" and active and row["entity"] == active["entity"] and active["end_reason"] is None:
            active["end_reason"] = row["reason"]
    for goal in goals:
        goal.pop("_pos")
        goal["censored_at_end"] = goal["end_reason"] is None
    first = goals[:10]
    corroborated = sum(goal["ownership_gain_observed"] for goal in first)
    return dict(first_ten=first, observed_weapon_selections=len(goals), corroborated_goal_count=corroborated,
                confirmed_native_receipts=0,
                gate="OWNERSHIP_CORROBORATION_MET_REVIEW_REQUIRED" if len(first) == 10 and corroborated >= 9 else "INCONCLUSIVE",
                limitation="Typed native planner selection supports initial pickability. Matching ownership gain and proximity are acquisition corroboration; masks alone and unavailable endings are not receipt proof. Native review must assess collision/source semantics; no fixed proximity radius is assumed.")


def exact_lives(records, states, quantum):
    """Optional lifecycle events must cover the first spawn and agree with states."""
    episodes, bounds, issues = [], [], []
    active, dead_tick = None, None
    last_spawn_count = last_death_count = 0
    for tag, row in records:
        if tag == "CecilSpawn":
            if row["respawns"] != last_spawn_count + 1:
                issues.append("exact spawn counter discontinuity or missing cohort start")
            last_spawn_count = row["respawns"]
            if not episodes and any(s["alive"] and s["tick"] < row["tick"] for s in states):
                issues.append("earlier alive state precedes first exact spawn")
            if active and active["end_upper_tick"] is None:
                active["end_upper_tick"] = row["tick"]
                active["end_lower_tick"] = max((s["tick"] for s in states if s["alive"] and
                                                 active["_lower"] <= s["tick"] < row["tick"]), default=active["_lower"])
            if dead_tick is not None:
                delay = (row["tick"] - dead_tick) * quantum
                bounds.append([delay, delay]); dead_tick = None
            active = dict(spawn_bounds_s=[row["tick"] * quantum] * 2, spawn_observation="EXACT_NATIVE_SPAWN_EVENT",
                          respawn_counter=row["respawns"], generation=row["generation"],
                          pickup_observation="RIGHT_CENSORED_NO_PICKUP", pickup_latency_bounds_s=None,
                          _lower=row["tick"], _upper=row["tick"], end_upper_tick=None, end_lower_tick=None)
            episodes.append(active)
        elif tag == "CecilDeath":
            if row["deaths"] != last_death_count + 1:
                issues.append("exact death counter discontinuity")
            last_death_count = row["deaths"]
            if active is None or active["generation"] != row["generation"] or active["end_upper_tick"] is not None:
                issues.append("exact death lacks matching live generation")
            else:
                active["end_lower_tick"] = active["end_upper_tick"] = dead_tick = row["tick"]
    for state in states:
        if state["alive"] and not any(e["_lower"] <= state["tick"] and
                                      (e["end_upper_tick"] is None or state["tick"] < e["end_upper_tick"]) and
                                      state["generation"] == e["generation"] and state["respawns"] == e["respawn_counter"]
                                      for e in episodes):
            issues.append("alive state is not covered by matching exact spawn epoch")
            break
    return episodes, bounds, issues, dead_tick is not None


def spawn_pickups(records, fresh, useful_mask, quantum, respawn_delay):
    states = [row for tag, row in records if tag == "CecilState"]
    episodes, previous, active = [], None, None
    dead_first = dead_last = alive_before_dead = None
    death_bounds, counter_issues = [], []
    unobserved = 0
    for row in states:
        tick = row["tick"]
        if previous:
            for key in ("deaths", "respawns"):
                if row[key] < previous[key]: counter_issues.append("native counter decreased: " + key)
            unobserved += max(0, row["respawns"] - previous["respawns"] - 1)
        else:
            unobserved += max(0, row["respawns"] - 1)
        if not row["alive"]:
            # A life that ended before the first 1s sample still belongs to the
            # prospective cohort; never replace it with a later successful life.
            if previous is None and row["respawns"] > 0:
                lower = 0 if fresh and row["respawns"] == 1 else None
                active = dict(spawn_bounds_s=[lower, tick * quantum],
                              spawn_observation="INITIAL_SPAWN_ALREADY_DEAD_AT_FIRST_SAMPLE",
                              respawn_counter=row["respawns"], generation=row["generation"],
                              pickup_observation="RIGHT_CENSORED_NO_PICKUP", pickup_latency_bounds_s=None,
                              _lower=lower, _upper=tick, end_upper_tick=None, end_lower_tick=None)
                episodes.append(active)
            if dead_first is None and active is not None:
                dead_first = tick
                alive_before_dead = previous["tick"] if previous and previous["alive"] else None
                if active:
                    active["end_upper_tick"] = tick
                    active["end_lower_tick"] = alive_before_dead
            dead_last = tick
        else:
            spawned = active is None or (previous and (not previous["alive"] or row["respawns"] > previous["respawns"]))
            if spawned:
                lower = dead_last if dead_last is not None else (previous["tick"] if previous else 0 if fresh and row["respawns"] == 1 else None)
                if active and active["end_upper_tick"] is None:
                    active["end_upper_tick"] = tick
                    active["end_lower_tick"] = previous["tick"] if previous else None
                active = dict(spawn_bounds_s=[None if lower is None else lower * quantum, tick * quantum],
                              spawn_observation="BRACKETED_RESPAWN" if dead_last is not None else "INITIAL_SPAWN_BOUNDED_FROM_FRESH_TICK_ORIGIN" if not previous and lower == 0 else "UNCERTAIN_SPAWN_EDGE",
                              respawn_counter=row["respawns"], generation=row["generation"],
                              pickup_observation="RIGHT_CENSORED_NO_PICKUP", pickup_latency_bounds_s=None,
                              _lower=lower, _upper=tick, end_upper_tick=None, end_lower_tick=None)
                episodes.append(active)
                if dead_first is not None:
                    death_bounds.append([max(0, dead_last - dead_first) * quantum,
                                         None if alive_before_dead is None else (tick - alive_before_dead) * quantum])
                dead_first = dead_last = alive_before_dead = None
        previous = row
    exact_spawn_count = sum(tag == "CecilSpawn" for tag, _ in records)
    exact_death_count = sum(tag == "CecilDeath" for tag, _ in records)
    exact_open_dead = None
    if exact_spawn_count:
        episodes, death_bounds, exact_issues, exact_open_dead = exact_lives(records, states, quantum)
        counter_issues.extend(exact_issues)
    elif exact_death_count:
        counter_issues.append("exact death events lack initial exact spawn coverage")
    last_tick = max((row["tick"] for tag, row in records if tag in ("CecilState", "CecilSpawn", "CecilDeath")), default=0)
    ambiguous_pickups = 0
    for tag, row in records:
        if tag != "CecilPickup" or not ((row["owned"] & ~row["old"]) & useful_mask):
            continue
        candidates = [e for e in episodes if (e["_lower"] is None or row["tick"] >= e["_lower"])
                      and (e["end_upper_tick"] is None or row["tick"] < e["end_upper_tick"])]
        if len(candidates) != 1:
            ambiguous_pickups += 1; continue
        episode = candidates[0]
        if episode["pickup_observation"] == "OBSERVED_NEW_USEFUL_WEAPON_BIT":
            continue
        episode["pickup_observation"] = "OBSERVED_NEW_USEFUL_WEAPON_BIT"
        episode["pickup_tick"] = row["tick"]
        episode["pickup_latency_bounds_s"] = [max(0, row["tick"] - episode["_upper"]) * quantum,
                                               None if episode["_lower"] is None else (row["tick"] - episode["_lower"]) * quantum]
    for episode in episodes:
        if episode["pickup_latency_bounds_s"] is None:
            end = (episode["end_lower_tick"] if episode["end_lower_tick"] is not None else episode["_upper"]) if episode["end_upper_tick"] is not None else last_tick
            episode["pickup_latency_bounds_s"] = [max(0, end - episode["_upper"]) * quantum, None]
            if episode["end_upper_tick"] is not None: episode["pickup_observation"] = "NO_PICKUP_BEFORE_OBSERVED_DEATH_OR_RESET"
        episode.pop("_lower"); episode.pop("_upper"); episode.pop("end_upper_tick"); episode.pop("end_lower_tick")
    first = episodes[:10]
    lows = [e["pickup_latency_bounds_s"][0] for e in first]
    highs = [e["pickup_latency_bounds_s"][1] for e in first]
    med = [statistics.median(lows), statistics.median(highs) if all(v is not None for v in highs) else None] if first else [None, None]
    p95 = [percentile(lows), percentile(highs) if all(v is not None for v in highs) else None] if first else [None, None]
    gate = "INCONCLUSIVE"
    if len(first) == 10 and fresh and not counter_issues and not unobserved and not ambiguous_pickups:
        if med[1] is not None and med[1] <= 15 and p95[1] <= 30:
            gate = "UPPER_BOUNDS_WITHIN_FROZEN_LIMITS_REVIEW_REQUIRED"
        elif med[0] > 15 or p95[0] > 30:
            gate = "LOWER_BOUNDS_EXCEED_FROZEN_LIMITS"
    summary = dict(first_ten=first, cohort_size=len(first), observed_spawn_episodes=len(episodes), unobserved_respawns=unobserved,
                   ambiguous_pickups=ambiguous_pickups, useful_weapon_mask=useful_mask,
                   median_latency_bounds_s=med, p95_latency_bounds_s=p95, percentile_method="nearest-rank P95", gate=gate,
                   limitation="Useful means a new weapon bit in the explicit caller mask; ammunition usability needs native review. Initial [0,first-state] bound assumes the caller-pinned fresh process and zero initial respawns. Tick time does not prove wall-clock network timing. Failed/censored first-ten episodes are never replaced.")
    deaths = states[-1]["deaths"] - states[0]["deaths"] if states and not counter_issues else None
    respawns = states[-1]["respawns"] - states[0]["respawns"] if states and not counter_issues else None
    death_summary = dict(death_counter_delta=deaths, respawn_counter_delta=respawns,
                        count_gate="COUNT_ONLY_MET" if deaths is not None and deaths >= 100 else "NOT_MET",
                        observed_dead_episodes=len(death_bounds) + int(exact_open_dead if exact_open_dead is not None else dead_first is not None),
                        respawn_delay_bounds_s=death_bounds, open_dead_interval=exact_open_dead if exact_open_dead is not None else dead_first is not None,
                        exact_spawn_events=exact_spawn_count, exact_death_events=exact_death_count,
                        allowed_respawn_delay_s=respawn_delay + 5,
                        limitation="Counters alone do not prove 100 health deaths; null weapons also make supply state unplayable. Cross-check health/death events and preserve process/map epochs when aggregating.")
    return summary, death_summary, counter_issues


def audit(lines, epoch, *, useful_weapon_mask, tick_quantum_s=.05, respawn_delay_s=1, local_slot=0):
    require(isinstance(epoch, dict), "explicit epoch object required")
    require(type(epoch.get("pid")) is int and epoch["pid"] > 1, "invalid process PID pin")
    require(type(epoch.get("start_ticks")) is int and epoch["start_ticks"] > 0, "invalid process start pin")
    require(re.fullmatch(r"[a-f0-9]{64}", epoch.get("dll_sha256", "")), "invalid DLL SHA256 pin")
    require(re.fullmatch(r"[a-fA-F0-9]{8}", epoch.get("map_crc32", "")) and bool(epoch.get("world")), "invalid map pin")
    require(0 < tick_quantum_s <= 1 and math.isfinite(tick_quantum_s), "invalid native tick quantum")
    require(math.isfinite(respawn_delay_s) and respawn_delay_s >= 0, "invalid preset respawn delay")
    require(type(useful_weapon_mask) is int and 0 < useful_weapon_mask <= 0x3fff, "explicit native useful weapon mask required")
    require(local_slot in range(4), "invalid local slot")
    records, loads, issues, slots = parse(lines, local_slot)
    states = [row for tag, row in records if tag == "CecilState"]
    fresh = (loads == [(epoch["world"], epoch["map_crc32"].lower())] and bool(states)
             and states[0]["tick"] <= 20 and slots == {local_slot} and not issues)
    if not fresh: issues.append("fresh single-bot process/map prefix not established")
    weapons = weapon_goals(records)
    spawns, deaths, counters = spawn_pickups(records, fresh, useful_weapon_mask, tick_quantum_s, respawn_delay_s)
    issues.extend(counters)
    if issues:
        weapons["gate"] = spawns["gate"] = "INCONCLUSIVE"
    return dict(schema_version=1, qualified=False, status="INCONCLUSIVE" if issues else "EVIDENCE_ONLY",
                epoch=dict(epoch), epoch_pin_limit="Caller-supplied identity pins; no live identity verification",
                epoch_evidence="CONSISTENT_FRESH_PREFIX" if fresh else "NOT_ESTABLISHED", issues=issues,
                state_samples=len(states), tick_quantum_s=tick_quantum_s,
                weapon_scenario=weapons, spawn_pickups=spawns, death_respawn=deaths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--epoch", type=Path, required=True)
    parser.add_argument("--useful-weapon-mask", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--tick-quantum-s", type=float, default=.05)
    parser.add_argument("--respawn-delay-s", type=float, default=1)
    parser.add_argument("--local-slot", type=int, default=0)
    args = parser.parse_args()
    try:
        raw, epoch_raw = args.log.read_bytes(), args.epoch.read_bytes()
        result = audit(raw.decode("latin1").splitlines(), json.loads(epoch_raw), useful_weapon_mask=args.useful_weapon_mask,
                       tick_quantum_s=args.tick_quantum_s, respawn_delay_s=args.respawn_delay_s, local_slot=args.local_slot)
        result["input_sha256"] = dict(log=hashlib.sha256(raw).hexdigest(), epoch=hashlib.sha256(epoch_raw).hexdigest())
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, "Evidence error: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
