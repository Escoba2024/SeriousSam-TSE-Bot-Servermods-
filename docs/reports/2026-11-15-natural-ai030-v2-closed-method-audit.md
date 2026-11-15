# NaturalAI030 V2: control limitedPASS, trace remains queue-coverage FAIL

The closed uninstrumented control completed its10s input-free observation. The corresponding trace failed at the unchanged64-record observer queue. This is an actual coverage failure, with no retry, threshold change, event exclusion or first-state acceptance.

Conditions are the new Build030 AI shooter and Original victim/server, exactly two game actors/three OS roles. Frozen manifest: `882b578a17af082332d7aecfbcf541ac3ca0f8e1aea4772e2027172039d3ff6b`. Control result SHA `1f69abbc7e18d908dfdfe811dc32dc7457987c8ebac14c4feb567d2a12a67a6a`; trace `6a1c82996277870b4c33a45287a3b7578bbbf99dad6b3cf27a24335e4da4e0ba`.

## First failure and complete denominator

The bounded reader decodes all49 exact IPC frames and all183 journal-linked captures, verifies wire hashes/archive offsets, and replays the unchanged pinned strict validator. Captures1–175 are accepted. Capture176 first raises `TraceRejected('sticky observer/coverage failure')`;176–183 remain rejected. S=181,F=183; all indexed tails are present. The final validator still fails. Packet176 has valid schema/identity but a real drop, so valid shape is not successful coverage.

Accepted prefix:2478 events, exactly177 complete game ticks with14 events each. The next native tick, ordinal178, begins at event2479 / process_game_tick call1240. Its64 archived events span13ms on the observer's JS wall clock:

| Raw event kind | Enter | Leave |
|---|---:|---:|
| process_game_tick |1|0|
| apply_action |2|2|
| post_moving |2|2|
| inflict_direct_damage, unregistered |2|2|
| cast_ray, unregistered |26|25|

The65th attempted event of that tick is terminal sequence2543: cast_ray leave for call1272, directly nested under the same GameTick1240. Its native tick is18.10000991821289; scope is `unregistered`, reason `cast outside observed Colt launch`. The cast entry2542 exists, its return is only the terminal record. The GameTick return is absent from the event stream too. Final counters report1272 entered/completed calls,2543 attempted events,2542 enqueued/drained, dropped1 and aborted_leaves1. Completed-call counters therefore do not prove complete archived return pairs. The actual remainder of tick178 is censored;64 is the queued-record limit, not its true event total.

Previous/failed drain starts are54.601ms apart. The host-monotonic gap from prior finish to next start is20.539ms; failed drain duration40.831ms. All capture start intervals remain below100ms (maximum66.835ms), and every IPC operation completes inside its existing budget. No host deadline violation or service-gap cause is demonstrated. The observed single-tick burst exceeds the queue; why that world/cast burst occurred is not established. Host monotonic, JS wall and native game clocks are kept separate.

## Callback, ownership and damage boundaries

The complete raw stream contains five of18 kinds:178 GameTick entries/177 returns,356 ApplyAction pairs,356 PostMoving pairs,380 CastRay entries/379 returns and two InflictDirectDamage pairs. All casts and both direct-damage calls are explicitly unregistered. The accepted prefix contains only the original four observed kinds; the two direct-damage pairs occur inside rejected tick178. The recorded acceptance cutoff is2478.

Zero Initialize/connection/death/ReceiveDamage/Colt/PrepareBullet/FireOneBullet/LaunchBullet callbacks are observed. The two direct-damage calls have empty payload and `damage outside observed Colt launch`; they do not identify an applied victim hit, damage amount/type, weapon, projectile owner or normal/fatal result. No other weapon is identified by this trace. An initial pre-Arm inventory has Colt selected with Knife wanted for the AI, but this cannot be interpolated to the later burst. There is only one initial inventory snapshot per arm and no inventory sequence covering the observer interval.

Both fresh Source custody prefixes match the closed bot log byte-for-byte and reproduce their original raw hashes. GameV012 confirms exactly local0; Source player-index/entity observations match the exclusive two-actor mapping. The trace worker's archived per-role module pins and the full ownership policy replay match Build030 AI, Original victim/server and exact Engine/Entities hashes; Root/worker identities are consistent. The control has Source/GMS/staging/join custody and strict executed runtime guards, but no independently archived full bot-module mapping receipt was found; that limit is retained.

These facts qualify neither a first valid post-Initialize state nor bullet ownership or damage. Earlier Init is left-censored, no observed respawn supplies the missing boundary, and the Bot-victim class remains open. No input was emitted in either arm.

## Cleanup, runtime and resources

The actual cold metadata RPC reports QJS, the bound server PID, ia32 and pointer size4. Main-thread TLS is bound19ms after Arm; getter callback count1, non-main0. Faults/errors_lost/detach_failures/non-main counters are0. The failure is queue/drop coverage, not a demonstrated TLS or module-identity fault.

All38 external Original regions match the before/after byte receipts; process identity is equal and unload/detach are true. The legacy external-restore validation step remains failed because the observer error is sticky, despite actual restored bytes. Stop/drain/unload/detach cleanup completes; own worker is intentionally SIGTERM-reaped after normal role closure (return−15), not mislabelled exit0 or a Frida crash. Worker proxy `sticky_failure=False` does not erase the observer's failed coverage.

Root independently verified664 files/nanosecond timestamps,9 absences and3 normal closed logs for each arm, both timestamp domains and own units/PIDs/displays/locks. Native status remains control limitedPASS / traceFAIL.

CPU companions have49 control/51 trace samples, no binding errors, exact PID/start and cgroup device/inode checks, raw-counter reconstruction and unchanged interval calculations. UNKNOWN domains, startup/end intervals and unused botB remain explicit; overlapping process/cgroup domains are not added. Host measured CPU peaks46.981%/63.679%; memory minima2843410432/2743267328B and disk minima9248845824/9202888704B. Startup gaps25.763/26.250s leave `budget_pass_claim=False`; no general resource or instrumentation-cost improvement is claimed.

## One next recommendation, no implementation

Review a **new registered first-state/damage-chain measurement contract** rather than retrying or weakening FULL18. Preserve the existing guards/bounds and every relevant registered actor Init/connection/death/first-valid GameTick/ReceiveDamage fact, together with actual registered Colt/Bullet-owner/Cast ancestry. Under that separately specified denominator only, avoid enqueueing full world CastRay rows when no registered Colt/Bullet ancestry exists; retain exact excluded-call counters and explicit UNKNOWN owner outcomes. This is a candidate scope to prove with adversarial completeness tests, not an already qualified observer or a way to relabel this failure.

The existing A3 ReceiveDamage collector demonstrates a smaller registered-victim before/after payload with an `inflictor_known_player` field, but it does not supply Initialize/first-processed-state or guaranteed projectile ownership. It is a source comparison only. Unknown other-weapon ownership or absent normal/fatal and Original/Bot victim examples must remain INCOMPLETE. Root reviews the new contract before any code/native work.

## Reproduction and retained evidence

`tools/audit_natural_ai030_v2_closed.py` performs one bounded new full replay; `--supplement <full-receipt>` reads only small custody/inventory/source witnesses, never the observer wire/journal again. Its two pure tests first failed on omitted failed-packet events/terminal and invalid serial acceptance, then passed. An initial syntax typo stopped the first GREEN invocation before case reads; that log remains. No runtime/helper/observer/fixture source was modified.

Private directory: `/srv/tse-natural-ai030-v2-closed-audit-evidence-20261115`.

- Full receipt `full-receipt.json`: `af2a856603a5e3549e37e1be63c1d85fe9431471d52f4f153c4b89855f5ccdc4`,921035B; full-reader source reads7313267B.
- Small custody supplement `custody-supplement.json`: `2bc226ca33c4bd36360f835b715b06a92168c79eb5ae000480596bd1c1848eb0`,10601B; reads1321770B including the derived receipt.
- `executed-full-reader.py` exactly matches its recorded SHA `af10592854c38d6ece7df5a29a193067c6f3fd06a3d4df7590121db69e36dfd9`; executed supplement source and all actual RED/GREEN/error logs are retained.

All reads use explicit resolution plus O_NOATIME/NOFOLLOW. Outputs remain below5MiB and no large archive/old-case replay was needed. The audit is complete; A1 remains incomplete and the trace remains FAIL.
