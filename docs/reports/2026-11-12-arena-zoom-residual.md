# Original zoom scaling in the Arena fire gate

Closed diagnostic window `arena014aim-dense-checked-swap0-trial-1-043831` completed30.075024s, with four normal closes, accepted retained logs and no reported errors. This is a diagnostic observation, not an A3/release qualification. The private active botB log contains2298 complete Aim/Transport pairs. In838 valid, non-NAV, consecutive same-life aim actions, `requested - LastRotation - intent` differs by at most0.000016degrees, consistent with FLOAT rounding. The former013 roughly70degree alternating body excursion was not reproduced and remains unexplained.

A separate concrete defect is proven: Arena settling evaluates the unscaled intended rotation, although original sniper zoom scales the applied rotation. Original EntitiesMP SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`, ApplyAction603fe980 tests player flag bit10;603fe9ee/603fe9f4 divide weapon FOV+124 by MaxFOV+334;603fe9fa–603fea27 multiply the rotation components before unscaled LastRotation is stored at603fea2f/603fea38. SDK107 Player.es3589 agrees. Existing SafeMotion already accounts for this factor.

Among116 eligible consecutive Sniper observations (valid non-NAV aim, same life, next row available, absolute yaw intent>=0.05degrees),107 observed next-body yaw changes match28/90 within0.001. The ratio is an observed corroboration, not a hardcoded bot setting. Three positive false permits occur for candidate local3/generation5/current and wanted weapon13:

| Tick | Active log Aim/Transport lines | Prior residual | Residual with original damping | Human/final FIRE |
|---|---|---:|---:|---|
|572|19850/19851|1.186016°|1.848205°|1/1|
|576|19994/19995|1.482131°|1.723773°|1/1|
|577|20027/20028|1.290011°|1.720347°|1/1|

MITTEL tolerance remains1.5degrees. These residual comparisons use the same decision-time eye, local body frame and saved aimpoint. They do not claim next-tick target geometry, a landed shot, or shooter damage attribution. For tick572, subsequent observed yaw/pitch changes were−0.155883/−0.279649degrees against intended−0.501142/−0.898870degrees, independently corroborating the original scaling.

The correction reads the pre-action flag/FOV from the already available player/weapon objects into `WorldView.rotation_damping`, default1. Arena final residual and consecutive settling use the scaled command in the existing body frame. Invalid, nonfinite, nonpositive or greater-than-one factors prevent firing and reset settling. The default1 branch retains the old calculation exactly. Raw action angles, turn rate/acceleration, RNG, noise, tolerances, targeting, movement, legacy/Cecil-only behavior and SafeMotion are unchanged. There is no compensating angle amplification, new Engine call, ray or entity write. The existing raw AimTrace residual remains the undamped motor-model value; `BotHuman err` and Arena alignment use the corrected final residual.

## Verification

The actual unchanged Human policy first failed the behavioral regression at tick4: reported residual2.075686183 versus damped residual3.357525066. This was a running behavior RED, not merely a missing-field compilation failure.

After the change, ASan/UBSan passed `test_arena_rotation`, `test_arena_combat`, `test_cecil_human`, and `test_aim_trace`. The new suite includes396 real-policy zoom feedback checks,1600 default/legacy parity ticks, intent/RNG invariance, invalid-factor settling reset/rebuild, and the three native numeric fixtures in normal, inverted and tilted local frames. The actual extracted Driver action guards and the passive trace block also passed. Independent read-only review found no important or critical issue. All compilers finished before the next native window.

Reproduction from repository root:

```sh
B=poc/candidates/redstation-supply-20261107
for t in test_arena_rotation test_arena_combat test_cecil_human test_aim_trace; do
  g++ -std=c++14 -O1 -fsanitize=address,undefined -fno-omit-frame-pointer -I "$B" "$B/$t.cpp" -o "/tmp/$t"
  "/tmp/$t"
done
python3 "$B/test_cecil_action_native.py" --sdk-player /path/to/verified/SDK107/Player.es
python3 "$B/test_aim_trace_native.py"
```

No new Windows build or native effectiveness/cost qualification is implied. This correction addresses zoom residual permits; it does not resolve the separate013 transport excursion, overall MITTEL performance or map traversal failures.
