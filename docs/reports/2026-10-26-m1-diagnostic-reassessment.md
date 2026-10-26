# M1: corrected diagnostic validation and retained eight-bot evidence

Date: 26 October 2026. Scope: isolated development, no public deployment.

## Result
The retained eight-bot log-prefilter diagnostic now passes a separate read-only retrospective evaluation: `DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE`. The original controller receipt remains unchanged `BLOCKED` with `DIAGNOSTIC_MAX_LOG_CONFIG_INVALID`. M1 remains incomplete.

The controller supplied raw configuration to its final validator. The pinned producer normalizes omitted `max_log_mib` to 32 and requires exact integer 1..128; the final validator incorrectly required an explicit field and omitted the upper bound. Fixing this contract does not modify game behavior, reduce resource reserves or disable sync checks.

## Native evidence revalidated
- Original native measurement: 1,500 seconds, peak eight bots plus original stationary Retail observer.
- Continuous population-nine window with all eight healthy bot roles and unchanged process generations: **1,331.624 seconds**.
- All eight bot telemetry streams valid `ACTIVE_OK`, approximately 20 Hz; ten complete preserved game/server logs independently scanned with zero SYNCBAD / Too many bad syncs / CRC check failed markers.
- Host guard FINISHED, exit 0; zero new CPU throttle periods; orderly drain, 20 successful unmounts; independently fresh process/cgroup/mount census clean.
- Five producer and eleven extra input pins, config, manifest, candidate and original protected runner checked through the unchanged original controller bootstrap. Historical receipts, source inventory and policy hashes identical before/after reassessment.
- Candidate GameMP SHA256 `7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf` unchanged.
- Corrected read-only validator SHA256 `4fe00d4f83a774545977183d6d6e0a21bfbcab41aac77e68db6d7c21840c3005`.
- Private derived receipt: `/root/ssam-ai-backups/m1-diagnostic-reassessment-20261026/reassessment.json`. No raw logs, profiles or retail data published.

## Resource findings
Across 1,464 bound CPU-attribution samples spanning 1,556.163 seconds, the test cgroup consumed **1.341 logical CPU cores on average**; mean host busy was **70.20%**. Aggregated SeriousSam processes consumed 0.986 cores, DedicatedServer 0.109, wineserver 0.102, inner Python 0.097 and Xvfb 0.036. These are summed process groups, including the original observer; they are not per-bot capacity measurements.

Minimum guard reserves: **1,081.70 MiB available RAM**, **8.306 GiB disk free**. Maximum single host CPU sample: **89.84%**; no three-consecutive-sample overload trip. Means over successive five-minute windows were 59.65%, 73.38%, 72.57%, 73.75%, and 68.09% for the final partial window. This limited run does not prove two-hour stability.

## Verification
- Regressions first reproduced missing-default rejection and invalid-129 acceptance (RED).
- Corrected performance suite: **69 PASS** normal and **69 PASS** with `python -O`.
- Full tools suite: **220 run, 219 PASS, one documented native Wine test skipped** because no owned runtime belongs to this read-only repair.
- Independent read-only reviewer: no Critical, Important or Minor findings; focused 18 tests independently passed normal and optimized.
- `git diff --check` clean.

## Next gates
The historic one/four-bot duration receipts remain accepted under their original harness. Their source inventory must never be relabeled as the prefilter harness. A new source-pinned full 1/4/8 duration matrix under the optimized producer is still needed, followed by candidate-bound client/server fault qualification and M1 review. Historical sync root cause remains unestablished. M2/M3/M4 native promotion and public rollout remain gated.
