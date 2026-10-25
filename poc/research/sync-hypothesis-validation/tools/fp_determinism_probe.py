#!/usr/bin/env python3
"""Float-model determinism probe for the client-side player state.

Hypothesis (H3 in hypothesis_registry.py)
----------------------------------------
The sync CRC is compared bit-exactly between the client's session state and the
server's session state. Entity state is a set of 32-bit floats. Two builds of
the *same* source can still produce different float bits if they were compiled
with different floating-point models:

* 32-bit MSVC defaults to the x87 FPU (80-bit intermediates, 32-bit stores),
  while ``/arch:SSE2`` uses native single precision - classic double rounding;
* ``/fp:fast`` may algebraically simplify expressions that ``/fp:precise``
  evaluates step by step. The bot's own composer interaction is a textbook
  case: it asks the vanilla composer to accumulate ``target - accumulator``
  into ``accumulator``. A strict build computes
  ``round32(round32(acc + round32(target - acc)))``, which is *not* exactly
  ``round32(target)`` for all inputs; a simplifying build may fold it to
  ``round32(target)``.

Both produce a *bit-level* state difference with no gameplay bug at all. This
probe quantifies the consequence offline: from which tick a difference is
visible in the serialised state, and how a 1-ulp input difference propagates.
That tells the native test whether "FP model mismatch" is a plausible
explanation for a SYNCBAD window starting at tick T - it does not prove it.

What the model does
-------------------
* 20 Hz ticks (``TickQuantum = 1/20 s``), one composed action per tick.
* Heading accumulator follows the documented composer round-trip.
* Position integrates the action velocity (``pa_vTranslation`` is a velocity,
  forward is -Z, see the CRC addendum).
* Four arithmetic models: ``f32_strict`` (per-operation binary32 rounding),
  ``f32_extended`` (double intermediates, binary32 store - x87-like),
  ``f32_simplified`` (algebraic simplification of the round-trip - /fp:fast
  like), ``f64_ideal`` (no 32-bit rounding at all).
* Plus a 1-ulp perturbation run to measure error propagation speed.

Everything is Python ``struct``-based, deterministic and platform independent.

Exit codes
----------
0  DETERMINISTIC_ACROSS_MODELS
3  MODEL_DIVERGENCE
2  usage error
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EXIT_DIVERGENCE, EXIT_OK, EXIT_USAGE, TICK_QUANTUM_S,
    SyncValError, base_payload, bits_hex, emit, f32, f32_bits, observation, require,
)

TOOL = "fp_determinism_probe"
MODES = ("f32_strict", "f32_extended", "f32_simplified", "f64_ideal")


def _round(mode: str, value: float) -> float:
    return f32(value) if mode != "f64_ideal" else float(value)


def _step(mode: str, target: float, acc: float,
          pos: Tuple[float, float, float], speed: float,
          yaw_rate_deg: float, dt: float
          ) -> Tuple[float, float, Tuple[float, float, float]]:
    """One tick of the modelled driver -> composer -> integration chain."""
    # 1) driver-side target accumulation (real code: bs_aHeading += yaw*fTick
    #    or re-based on the entity rotation; both are float32 accumulations).
    increment = _round(mode, yaw_rate_deg * dt)
    if mode == "f32_extended":
        target_new = _round(mode, target + yaw_rate_deg * dt)
    else:
        target_new = _round(mode, target + increment)

    # 2) composer round-trip: the bot passes target-minus-accumulator and the
    #    vanilla composer adds it back into its accumulator.
    delta = _round(mode, target_new - acc)
    if mode == "f32_simplified":
        # /fp:fast style algebraic simplification: acc + (target - acc) -> target
        acc_new = _round(mode, target_new)
    elif mode == "f32_extended":
        acc_new = _round(mode, acc + delta)          # double add, then store
    else:
        acc_new = _round(mode, _round(mode, acc) + delta)

    # 3) integrate velocity. pa_vTranslation is a velocity; forward is -Z.
    yaw_rad = math.radians(acc_new)
    sin_yaw = math.sin(yaw_rad)
    cos_yaw = math.cos(yaw_rad)
    v = _round(mode, speed)
    step = _round(mode, v * dt)
    dx = _round(mode, _round(mode, sin_yaw * step))
    dz = _round(mode, -_round(mode, cos_yaw * step))
    new_pos = (
        _round(mode, pos[0] + dx),
        pos[1],
        _round(mode, pos[2] + dz),
    )
    return target_new, acc_new, new_pos


State = Tuple[float, float, Tuple[float, float, float]]


def simulate(mode: str, ticks: int, speed: float = 1.0,
             yaw_rate_deg: float = 45.7, speed_forward: float = 15.0,
             acc_perturbation_ulp: int = 0,
             velocity_perturbation_ulp: int = 0) -> List[State]:
    """Deterministic state series; index 0 is the initial state."""
    dt = TICK_QUANTUM_S
    acc = 0.0
    if acc_perturbation_ulp:
        acc = _ulp_nudge(acc, acc_perturbation_ulp)
    pos = (0.0, 0.0, 0.0)
    target = 0.0
    units_per_s = speed_forward * speed
    if velocity_perturbation_ulp:
        units_per_s = _ulp_nudge(units_per_s, velocity_perturbation_ulp)
    series: List[State] = [(target, acc, pos)]
    for _ in range(ticks):
        target, acc, pos = _step(mode, target, acc, pos, units_per_s, yaw_rate_deg, dt)
        series.append((target, acc, pos))
    return series


def _ulp_nudge(value: float, ulps: int) -> float:
    """Return value nudged by ulps, derived from its binary32 bit pattern."""
    import struct
    bits = (f32_bits(value) + ulps) & 0xFFFFFFFF
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def _bits_state(state: State) -> Tuple[int, int, int, int, int]:
    target, acc, pos = state
    return (f32_bits(target), f32_bits(acc), f32_bits(pos[0]),
            f32_bits(pos[1]), f32_bits(pos[2]))


def _bits_action_like(state: State) -> Tuple[int, int]:
    """What the client writes into the action packet: rotation value and
    heading; both are 32-bit floats in the action image."""
    target, acc, _pos = state
    return (f32_bits(f32(target - acc)), f32_bits(acc))


def _first_divergence(a: List[State], b: List[State],
                      key=_bits_state) -> Optional[int]:
    for tick, (left, right) in enumerate(zip(a, b)):
        if key(left) != key(right):
            return tick
    return None


def _max_axis_drift(a: List[State], b: List[State]) -> Dict[str, float]:
    heading_drift = 0.0
    angle_drift = 0.0
    pos_drift = 0.0
    for (ta, aa, pa), (tb, ab, pb) in zip(a, b):
        heading_drift = max(heading_drift, abs(ta - tb))
        angle_drift = max(angle_drift, abs(aa - ab))
        for i in range(3):
            pos_drift = max(pos_drift, abs(pa[i] - pb[i]))
    return {"max_abs_heading_drift_deg": round(heading_drift, 9),
            "max_abs_entity_angle_drift_deg": round(angle_drift, 9),
            "max_abs_position_drift_units": round(pos_drift, 9)}


def analyse(ticks: int, speed: float, yaw_rate_deg: float,
            speed_forward: float) -> Dict[str, object]:
    series = {mode: simulate(mode, ticks, speed, yaw_rate_deg, speed_forward)
              for mode in MODES}

    pairs: List[Dict[str, object]] = []
    earliest: Optional[int] = None
    earliest_action: Optional[int] = None
    for i, left in enumerate(MODES):
        for right in MODES[i + 1:]:
            first = _first_divergence(series[left], series[right])
            first_action = _first_divergence(series[left], series[right],
                                             key=_bits_action_like)
            entry = {
                "left": left,
                "right": right,
                "first_divergent_tick": first,
                "first_divergent_action_tick": first_action,
                "final_state_equal": _bits_state(series[left][-1]) == _bits_state(series[right][-1]),
            }
            entry.update(_max_axis_drift(series[left], series[right]))
            pairs.append(entry)
            if first is not None and (earliest is None or first < earliest):
                earliest = first
            if first_action is not None and (earliest_action is None
                                             or first_action < earliest_action):
                earliest_action = first_action

    # Two one-ulp perturbations: the composer accumulator (re-targeted every
    # tick, so it can be absorbed) and the velocity input (integrated, so it
    # should persist). The difference is the whole point of the experiment.
    acc_perturbed = simulate("f32_strict", ticks, speed, yaw_rate_deg,
                             speed_forward, acc_perturbation_ulp=1)
    vel_perturbed = simulate("f32_strict", ticks, speed, yaw_rate_deg,
                             speed_forward, velocity_perturbation_ulp=1)
    reference = series["f32_strict"]

    def _propagation_onset(perturbed: List[State], key=_bits_state) -> Optional[int]:
        # Skip tick 0: that is the injected perturbation itself, not propagation.
        first = _first_divergence(reference[1:], perturbed[1:], key=key)
        return None if first is None else first + 1

    def _perturbation_report(perturbed: List[State]) -> Dict[str, object]:
        first_state = _propagation_onset(perturbed)
        first_action = _propagation_onset(perturbed, key=_bits_action_like)
        drift = _max_axis_drift(reference, perturbed)
        absorbed = (first_state is None
                    and drift["max_abs_position_drift_units"] == 0.0
                    and drift["max_abs_entity_angle_drift_deg"] == 0.0)
        return {
            "first_propagated_tick": first_state,
            "first_propagated_action_tick": first_action,
            "absorbed": absorbed,
            "propagation": drift,
        }

    ulp_report = {
        "perturbation_ulps": 1,
        "accumulator": _perturbation_report(acc_perturbed),
        "velocity": _perturbation_report(vel_perturbed),
        "note": ("The composer accumulator is re-targeted every tick, so a one-ulp "
                 "error can be absorbed (Sterbenz-style exactness of target-acc plus "
                 "acc+delta). The velocity is integrated, so a one-ulp error persists "
                 "and grows into the serialised position. This is why 'the bot looks "
                 "identical' is not evidence that the state bits are identical."),
    }

    finals = {}
    for mode in MODES:
        target, acc, pos = series[mode][-1]
        finals[mode] = {
            "target_heading_deg": target,
            "target_heading_bits": bits_hex(target),
            "entity_angle_deg": acc,
            "entity_angle_bits": bits_hex(acc),
            "acc_minus_target_deg": f32(acc - target),
            "pos_x": pos[0],
            "pos_x_bits": bits_hex(pos[0]),
            "pos_z": pos[2],
            "pos_z_bits": bits_hex(pos[2]),
        }

    payload = base_payload(TOOL, "model")
    payload.update({
        "scenario": {
            "ticks": ticks,
            "tick_hz": 20,
            "tick_quantum_s": TICK_QUANTUM_S,
            "yaw_rate_deg_per_s": yaw_rate_deg,
            "speed_forward_units_per_s": speed_forward,
            "speed_factor": speed,
            "note": ("speed_forward is a model input, not a claim about the retail "
                     "plr_fSpeedForward value; the driver's target accumulation is "
                     "modelled from BotDriver.cpp (bs_aHeading += yaw*fTick / "
                     "re-based on the entity rotation)"),
        },
        "modes": list(MODES),
        "pairwise": pairs,
        "earliest_divergence_tick": earliest,
        "earliest_divergence_action_tick": earliest_action,
        "final_states": finals,
        "ulp_sensitivity": ulp_report,
        "interpretation": (
            "If two builds of the same source use different FP models, the entity "
            "state can diverge bit-exactly within the first ticks of motion while "
            "the gameplay behaviour looks identical. This makes an FP-model "
            "mismatch a candidate explanation for an *early* SYNCBAD window. The "
            "model cannot show which model the retail 1.07 BotClient build used; "
            "that requires the recorded compiler/linker flags and a native A/B run. "
            "Note the self-healing result for exactly representable headings: a "
            "re-targeting composer can absorb small accumulator errors, so a "
            "negative result here is a real falsifier for the composer path."
        ),
    })
    payload["observations"] = [
        observation("fp.earliest_divergence_tick", earliest, "model", TOOL),
        observation("fp.earliest_divergence_action_tick", earliest_action, "model", TOOL),
        observation("fp.accumulator_perturbation_absorbed",
                    ulp_report["accumulator"]["absorbed"], "model", TOOL),
        observation("fp.velocity_perturbation_propagated_tick",
                    ulp_report["velocity"]["first_propagated_tick"], "model", TOOL),
    ]
    payload["verdict"] = ("MODEL_DIVERGENCE" if earliest is not None
                          else "DETERMINISTIC_ACROSS_MODELS")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ticks", type=int, default=400)
    parser.add_argument("--speed-factor", type=float, default=1.0)
    parser.add_argument("--yaw-rate", type=float, default=45.7, help="deg/s")
    parser.add_argument("--speed-forward", type=float, default=15.0, help="units/s")
    parser.add_argument("--out")
    args = parser.parse_args()

    require(1 <= args.ticks <= 20000, "--ticks must be within 1..20000")
    require(args.speed_factor >= 0.0, "--speed-factor must not be negative")

    payload = analyse(args.ticks, args.speed_factor, args.yaw_rate, args.speed_forward)
    emit(payload, args.out)
    return EXIT_DIVERGENCE if payload["verdict"] == "MODEL_DIVERGENCE" else EXIT_OK


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
