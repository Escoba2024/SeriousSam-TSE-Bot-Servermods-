# Bounded extended item attempts and retained048 map evidence

The completed048 native windows contain real route failures. Missing verdict files are not the reason to withhold functional acceptance. This review read the retained raw logs, graph bindings, bounded monitor windows and feature indexes. It did not start or change a runtime or issue a native certificate.

The evidence belongs only to source `4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`, tree `127451e9b340af751cdd7fd6544d378b7425a429`, DLL `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`. The code change below creates a new candidate requiring new native tests.

| Retained window | Proven observations | Functional problem |
|---|---|---|
| Hole048 | 600.007804s, 595 monitor samples, eight bots, full coverage, positive score changes for every bot; 81 health-correlated death/respawn pairs, no unresolved subsequent activity; max unexplained stationary interval 2.023139s | BotA local2, generation11, ticks9240–10120: one item goal for44s, same anchor throughout, same hop in43/45 samples; 139.66m summed movement inside a6.70×2.84×7.73m extent. No added shots. Six repeated checkpoints at469.05–504.05s do not resolve the edge. Item ends at tick10121 with `timeout`. |
| Skulls048 | 600.005876s, 595 monitor samples, eight bots, full coverage, positive score changes for every bot; 71 health-correlated pairs, no unresolved subsequent activity; max unexplained stationary interval 5.046478s | BotA local0, generation9: same item transit hop for25s at ticks10620–11120, no shots, closest sampled distance11.69m from original hop; item ends at tick11132 with `timeout`. No checkpoint for this failed life: the safe rebase prerequisites were not satisfied. Similar failed approaches recur in other lives. |

Private reproduction references: `/srv/tse-cecil-gate8-20261109/evidence/candidate048-{hole,skulls}-preserved/{botA,botB}.log`, matching `048-*-functional/{report,analysis,timeseries}.json*`, and `/srv/tse-cecil-full-20261107/.codex/evidence/source048/{hole,skulls}-main/`. Hole BotA relevant lines6403–7021; Skulls BotA lines7520–7957. Preserve the complete files and their existing index SHA256 bindings. No NAV coordinate payload or raw logs are included here.

The152 health-correlated pairs are actual048 observations across distinct processes and lives. They are useful retained evidence, not new-candidate credit. The sampled nonpositive-health corroboration does not determine an earlier exact physical health-death instant. Existing activity indexes show subsequent activity within1.1s at worst; no new respawn policy or acceptance is inferred.

Additional feature review remains bounded. Hole has six sampled Jump-input candidates and actual changes in height, including one same-life sequence with rise and later fall. Other candidates descend into water; Jump input alone is not a completed intended jump route. Hole has345 lock snapshots with real lock changes, but snapshot counts alone do not prove traversal. Skulls has143 teleport-flag samples and many fast displacements; inspection finds long airborne arcs as well, so those heuristics cannot establish a teleport event. Neither map has sampled USE intent/output or completed crouch physical evidence. Skulls has one brief native inverted-gravity interval, not a demonstrated completed traversal. Each log has one loaded map: these fixed-map windows do not test map reset. Liquid/hazard escape, endpoint-matched teleport and successful intended traversal remain open. Red Station's ten retained initial Supply lives meet the numerical acquisition criteria (10/10, median5.075s, P9517.65s), but do not substitute for the missing full Red Station functional window or the final-candidate weapon/animation review.

## Change

The existing repeated-checkpoint patrol recovery deliberately excludes item-backed goals. Extending its movement permissions would be a larger safety change. Extended mapped/relocated item attempts now have a separate passive ordinary-edge progress bound. Ten seconds without at least0.75m of new best-distance gain ends the failed attempt, records `CecilItemTransitEnd`, applies the existing30s item rejection TTL and requests the ordinary item scan on the next tick. The existing selector still checks type, need, weapon permissions, reachability and connector geometry.

The observation is pinned to world/map serial, player entity/generation, item, goal, attempt start/deadline, gravity and original edge. Original-source reapproach after a checkpoint retains the clock. Real best-distance gain resets it. Ownership loss, missing samples, changed identity, explicit goal reset, invalid input and off-graph air handling erase it. Special, locked and terminal item edges, liquid, follow and interaction/USE contexts retain their existing policies. Ordinary12s item attempts keep their original timeout. No extra casts, world entity scans, allocation, teleport, synthetic arrival, longer item deadline or new movement permission is added. Ending an unsuccessful goal does not require the static-support authority that would be necessary to command a recovery move.

## Portable verification

Behavioral tests compile the real native bridge against deterministic SDK-contract stubs. The initial regression failed four assertions on the old implementation. A second regression exposed one early-air-return history leak, then passed after clearing that history. Tests cover repeated checkpoint and no-checkpoint cycles, neutral failure, selection of a different eligible ranged item, slow genuine progress, seventeen excluded contexts, eleven identity/freshness/reset cases, the original rejection TTL and absence of new casts/scans/allocation.

Commands:

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
python3 -m unittest discover -s tools
```

Results: 1372 native-bridge checks passed both normally and with SDK107 contracts plus ASan/UBSan. All nine C++ fixture executables, native action/item/export checks and182 Python tooling tests passed. Expected negative-fixture messages from query/parser tests are not runtime failures. These are portable behavioral/contract checks, not Retail runtime qualification. The new bounded rejection may abandon an achievable but temporarily obstructed item; the existing30s retry expiry limits that tradeoff. Native tests must show both faster departure from the failed edge and subsequent acquisition/combat, not just a new rejection log.

## Safe native next steps owned by Main

The retained `/srv/tse-cecil-gate8-20261109/native048_safe.py` is a reusable lifecycle pattern, pinned to old048. It checks build/source/tree/DLL, original server DLL, root quiescence, empty service cgroups, private namespace, exact population and map identity. It takes two nonblocking root locks, owns PID/start identities, closes its own windows normally, preserves complete logs and cleanup, and refuses existing evidence paths. These guards must remain.

For a new candidate, copy/rebind the harness, helper source/hash, manifest, installed isolated bot DLLs, root and unique evidence/service names together. Do not overwrite retained048 outputs or merely replace a top-level DLL constant. Run Hole and Skulls600s first, then Little Trouble/Yodeller/Red Station600s with the same hash. Review the old failure shapes using same-life original-hop distance, the new rejection event and the next actual pickup/fire sequence. Retain failed attempts and dead/censored lives. Continue the existing numerical activity/sync checks, but never treat bounded spatial cycles as functional progress.

The old command `python3 /srv/tse-cecil-gate8-20261109/qualify048-safe.py trouble yodeller redstation` applies only to the old048 root/hash and unused output paths; it is not a command for the new candidate. Existing Hole/Skulls output names intentionally cannot be rerun. Formal1/4-bot3600s and8-bot7200s entry points additionally require correctly pinned independent Supply and Hole/Skulls native verdicts; the retained failures do not justify creating PASS verdicts. Final map-reset/recovery, native special actions, original Retail gameplay, resource thresholds and fleet gates remain separate.
