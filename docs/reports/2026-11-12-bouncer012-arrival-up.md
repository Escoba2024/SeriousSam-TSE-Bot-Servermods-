# Bound approach arrival must retain UP suppression for its own Update

Native011's completed repeat exposed one remaining output boundary: a valid8/11→12 approach can reach the original node12 radius before physical pad contact. `CecilNavigator::Update` then advances its source to12 and hop to34 before the native approach helper runs. The011 helper sees the new edge and permits that invocation's ordinary positive UP. Candidate012 suppresses only that same invocation when the preceding approach was qualified. It does not suppress later12→34 ticks or change authored geometry.

## Observed controls and limits

Private window `arena011hook2-checked-swap1-trial-1-000025`:120.04123289394192seconds, final result `PASS_LIMITED_CONTROLLED_WINE_SESSION_FIELD_AND_POPULATION`, no result errors, all four roles normally closed. Root owns native execution. Physical candidate botA entities565..568 map to local0..3; this analysis matches actual entity IDs and action logs, not inventory group labels.

- Entity567/local2/generation5: actual8→12 UP pulses874/878/882 are suppressed. Tick887 reaches12, Update emits12→34 with rawUP1/finalUP11 while supported. Original-server Bouncer234 event1 sets vertical velocity to73.18436431884766. The corresponding action observation888 shows that launched state; observation889 has85.984360, an additional12.799996. It later rises above the intended platform and does not acquire the Minigun on this attempt. Bot action/state observations880 and900 identify current weapon1 (knife).
- Entity568/local3/generation6 is a successful control. The node12 arrival at1240 has raw/finalUP0, with the actual Bouncer launch already visible in that observation. Original-server event2 records vertical exit73.18109893798828. The next observation1241 has71.681099; Minigun acquisition is recorded at1329. Later positive UP requests are present and are deliberately unchanged by012.
- Entity566/local1/generation6 is the necessary counterexample. Corrected11→12 pulses1245/1249 are suppressed; arrival1253 still emitsUP11. Original event3 launches at72.3910140991211, but the next observation1255 has70.891014, without567's extra increase. The prior action/weapon observation identifies Colt/current2. Thus positive transition UP does **not** always cause an additional impulse, and this evidence does not establish a universal causal rule.

Client tick numbers above identify recorded action rows, not a general wall clock or an atomic action-processing timestamp. The Bouncer event is an original-server entry/leave observation; its sequence is matched to entity and trajectory. No per-tick `en_tmJumped`, jump-permission bit or last-ground timer was captured. Their actual values cannot be reconstructed as fact from these rows.

## Static original1.07 cross-check

The following was inspected read-only in the original files, independently rehashed. This is static disassembly, not a new Ghidra/Frida or native test:

- Original `EntitiesMP.dll` SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`, preferredVA603ffabb..603ffaf4, checks weapon1 and noncooperative play and multiplies all three input translation components by float6048c724 (`1.3`). SDK107 `Sources/EntitiesMP/Player.es:3954` corroborates the knife behavior. The observed567 increase is consistent with `11×1.3−1.5=12.8`, using the subsequent observed1.5 vertical decrement. This numerical agreement is a mechanism clue, not proof of the exact processing instruction.
- The same original's60400014..604000ab reads entity+17c and TickQuantum, tests the bounded recent-jump interval and null reference, then clears the jump-allowed flag. Earlier603ffbf9..603ffc37 handles reference/fall-time and rearming;6040031b..60400347 filters positive UP by that flag and calls SetDesiredTranslation. SDK Player.es3989–4030,4148–4155,4226–4231 corroborates these independent gates.
- Original `Engine.dll` SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, exported FakeJump RVA1584c0/preferredVA602184c0. Its602184cb..602184e7 writes entity+17c as CurrentTick minus entity+180 plus argument+20; it does not simply stamp CurrentTick. Its later body sets velocity and clears the reference. SDK107 `Bouncer.es:22` passes the Bouncer's control-time argument to FakeJump. Those actual per-pad timer values are not in the recorded events.
- Original PreMovingNew's6021e9ea..6021ea76 has its own requested-up/last-ground-time checks, adds the directional contribution and writes entity+17c. The matching older movement branch also exists; no runtime selection of a particular branch is claimed. Existing verified SetDesiredTranslation60217f60..60217fa6 copies all requested components without itself proving current support.

Bouncer launch and ordinary UP therefore pass through distinct original logic and time/state gates.012 removes a demonstrably unwanted ordinary request at the qualified boundary without rewriting those gates or trying to force their outcomes.

## Bounded change

`BotCecilBouncerContext` factors the unchanged011 context checks: exact world/NAV metadata binding, current enable/Ready/serial,193-point blocked array, live identity, valid frame/weapons, STAND/CROUCH, default gravity, finite velocity, and same-world undeleted static brush reference or null. `BotCecilBouncerApproaching` adds actual committed source8/11, hop12 and unblocked source/destination.

Immediately before the existing Update, a stack-local Boolean captures `reachedHop && qualifiedApproach`. Immediately after Update and the existing raw diagnostic capture, the output helper also accepts that Boolean **only** with a valid active/nonarrived/nonstuck/nonrelocated source12/hop34 result, flags42 and unblocked12/34. The only mutation is copied `move.up=0` for positive finite UP<=1. Both pre- and post-context must qualify. The Boolean is not stored across frames, lives or bots. Later12→34 calls have no qualifying preceding approach and preserve their authored pulses.

No entity/support/velocity/position, radius, flags, timer, jump cooldown, goal, deadline, generation or flight policy is changed. No casts, world entity lookups or RNG calls are added. This is no new ground/contact or airborne-control authority. Raw diagnostics retain the original navigator's UP before suppression.

## Portable verification

The first focused real `BotSupplyTick` regressions used the two actual arrival positions and diagnostics off/on. After correcting test-only argument order and establishing the prior diagnostic episode, unmodified011 produced **1928 checks /4 expected behavioral failures**. The focused implementation passed1928/0.

The final suite includes all prior1918 checks, twenty actual recorded state/action inputs for each of the three approaches, matching original FLOAT pulse timing, original navigator comparison, subsequent12→34 pulses,27 invalid pre/post contexts, valid STAND/CROUCH null-reference transitions, and expiry of the one-call qualification. These replays use recorded trajectories as inputs; they do not simulate new Engine trajectories or predict pickup success.

- `python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`: **2526 checks,0 failures**, SDK107+ASan/UBSan.
- `python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`: **PASS** actual Driver action guards.
- Root independently reviewed the gameplay diff with no Important/Critical finding before commit. Root will integrate, repeat tests, build and own native acceptance. This work performed no runtime or production changes;012's native efficacy remains unproven.

Private input hashes for reproducibility (raw data remains private):

| Artifact | SHA256 |
|---|---|
| result.json | `4e239cbdebcb30eddb3845f80faca1862e82c72dfd49dc8f9a2b204369b023d1` |
| botA.log | `55276bd952744ce7eb6bf0a4d5c0cfa487bd2533cd61a7da8699ad1194d72af8` |
| frida-bouncer.jsonl | `077bff26f05765b3595308888a2b8177ff1aba0b061c98812f39c5edff9e87fe` |
| inventory.jsonl | `8e99b558b59a76c44605ad5a6b3804cb75a275945c25c63ccc7943eb76c4072a` |
