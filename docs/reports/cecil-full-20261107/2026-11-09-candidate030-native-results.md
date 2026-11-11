# Candidate030 native results and remaining floor-recovery failure

Status: **NOT QUALIFIED; no production rollout**. Source `c7197856cf18f60836f06a0884ff865570db5ae8`, tree `d4f81e8d5d247a46ffbd6c91e4e1e52e1ef33cfc`, DLL `4ad49476ee65ff93edb9949e772169626ebb25a9856ea4d75e32813427086688`.

## Completed supply cohort

All ten consecutive fresh60-second single-bot RedStation observations completed with normal shutdown, ten distinct native epochs and matching raw-log hashes.580/580 recorded queries show exactly one expected bot and RedStation. The fixed first ten actual weapon goals occur as3+4+3 in cases1–3: nine have matching selected entity, typed weapon and newly gained ownership bit with native pickup proximity. Case3 laser267 ends `unreachable_hold` and remains a failure. No replacement or missing observation.

First useful pickup latencies are9.10,10.15,20.40,2.60,9.55,3.95,3.95,3.95,4.85,3.15seconds: median4.40/P95 nearest-rank20.40. Main and independent complete-log review agree. Later incidental shotgun gains count toward useful spawn pickup timing, not toward the unrelated active flamer goal. A limited `SUPPLY_GATE_PASS_NATIVE_REVIEW` certificate explicitly sets qualified=false and SINGLE_SUPPLY_ONLY. Acquisition is inventory-correlated, not an exact ReceiveItem-ID receipt. All earlier failed cohorts remain unchanged.

## Completed eight-bot short observations

Hole:600.007871seconds, complete coverage, no recognized native/monitor errors, all eight bots show positive score changes, maximum unexplained stillness4.026312seconds.92 native health deaths each have a following spawn, native delay1.50..1.95seconds; sampled post-respawn activity maximum1.019570seconds. Four accepted jump actions and a corresponding vertical trajectory are observed. Doppel-Colt, rocket, grenade and cannon have ownership, selection, current-weapon and fire-action evidence. Hole supplies no flamer, USE, crouch, teleport or inverted-gravity evidence.

Little Trouble:600seconds, complete monitor observation with147 reported deaths and maximum unexplained stillness4.031603seconds; detailed feature/death review remains separate. Both owned runtimes close normally and logs are preserved. The following Yodeller observation is explicitly interrupted when the separate four-bot failure invalidates candidate qualification; it is a partial observation, not a completed map gate.

## Original Retail gameplay

An unchanged original Retail client under Wine joins the owned isolated single-bot RedStation server after fresh four-component hash, occupancy and exact one-bot UDP preflights.115 valid two-player queries cover a120-second observation, with no recognized native errors. PID-bound ordinary keyboard/mouse inputs produce visible movement and turning; HUD coordinates change from(102,14,97) to(50,2,46), then(60,13,37). Fire input is recorded; no hit claim is made. Window close succeeds, the server returns to exactly one bot, original file hashes remain unchanged and all own runtime/display resources close normally. Result is PASS_LIMITED_RETAIL_WINE_GAMEPLAY, not native Windows or independent WAN acceptance.

## Failed four-bot duration attempt

The final-hash one- and four-bot3600-second gates start only after the genuine supply and Hole results. In the four-bot run, slot0 has10.072208seconds unexplained stillness at observation21.173011..31.245220seconds. Eleven native samples show an unchanged grounded pose, actual accepted recovery `nav=1`, no visible target, a valid sampled reference and repeated real `NoFloor` results. Requested movement is neutralized; there is no budget or wall failure. Recovery target95 is held until its six-second limit, then118 is chosen with a similar direction and also fails floor checking.

These are neither the corrected Human-ownership branch nor the null-reference branch. Final floor vetoes are not returned to target selection: failed-LOS scan state only records LOS failures or unusable horizontal targets. Thus the existing six-second per-target timeout does not guarantee the unchanged ten-second stillness bound. This establishes repeated failed attempts, not a safe alternative route or a false floor result.

Both duration monitors are explicitly interrupted and own bots/servers closed normally with cgroups drained. One-bot elapsed269.957seconds/four-bot268.383seconds are partial observations, not accepted duration gates. No completed3600/3600/7200 gate exists for030. Preserve floor checks; diagnose current collision/foot/stand-polygon geometry and alternative physically checked directions. Any behavior correction requires a new published normal build and repeated affected gates. Public DLLs remain unchanged.
