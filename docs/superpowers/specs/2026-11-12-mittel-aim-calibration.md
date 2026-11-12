# MITTEL aim calibration within milestone A3

The original user request delegates routine implementation choices and requires competent MITTEL combat, stronger STARK/DEMON and unchanged valid damage/aim constraints.

Native diagnostic014 (closed30.075024s window arena014aim-dense-checked-swap0-trial-1-043831) demonstrates that intentional correlated drift plus target offset can exceed MITTEL's unchanged1.5degree trigger tolerance even when the motor follows its biased target. In383 visible, stable non-Sniper observations after10 same-target ticks,235 residuals exceed tolerance;86 have the biased residual within tolerance. Laser local0/generation6 ticks548–551 provide a stationary-target example. This is separate from the already-corrected original sniper zoom residual and the unreproduced013 Colt excursion.

## Approach chosen by the implementer

Reduce only MITTEL ArenaSkill aim_sigma_deg from0.9 to0.6; keep STARK0.45, DEMON0.15, all turn/reaction/settle/fire-tolerance/loadout/navigation parameters and original action transport. This reduces a demonstrated self-blocking cause without adding perfect aim. Raising turn limits is unsupported (no observed saturation); widening fire tolerance would permit less accurate shots and does not address deliberate drift.

A deterministic closed-loop real-policy regression uses visible slowly moving targets at0.2deg/s, matching the negligible target motion seen in the native example, across three existing seeds and Minigun/Laser. After100 warmup ticks MITTEL must emit aligned FIRE on at least75% of1100 observations. This threshold is an implementation acceptance floor for the controlled stationary-like case, not a promised native hit rate. The pre-change measured range was454–730/1100; the bounded0.6 exploratory configuration produced887–1025/1100. All permitted shots retain the original1.5degree gate and turn bounds.

Native crossed comparisons on the new pinned candidate remain required. No native improvement, map acceptance or rollout is claimed by this regression.
