# Lift lock transition: native commitment loss and bounded correction

Status: **native mechanism reproduced; next normal candidate038 acceptance pending**.

Candidate036 source `2f216fe5b93297456fea2c2736b946752029ea90`, DLL `d3889413432b4eccbe8e375c2f1e5cf6d06c7af0edbb5908da1cf8225ca26a39`, fails the fixed supply P95 gate at31.60s. Its case4 follows a long detour after a moving-platform lock closes before the lift entry's original arrival radius is reached. See [complete036 results](2026-11-09-candidate036-native-results.md).

## Native same-tick context

Diagnostic037b adds only existing lock-change-event context to the normal036 overlay. DLL SHA256 `19c4e47cc912c1b1efc66dff039c1de03f789fcf887a3b91f22b006866069252`; overlay Bsup SHA256 `42b66c8b7b6c4e13b6ee955853e4c0454348729a5c3f606cb4572ca6aab7b394`. No extra raycasts, planner decisions or movement changes. Four separate60-second single-bot joins encounter other spawn situations and do not reproduce the lift event. They are retained as non-reproductions, not successes or counterevidence against036.

A separate four-bot RedStation observation completes600.004097s with596 samples and zero recognized errors, then bots and server close normally. Two actual supported entry episodes independently reproduce the problematic transition:

| Native time | Slot/entity | Actual state/reference | Retained hop/goal before lock | Original hop distance/radius | Following action |
|---|---|---|---|---|---|
|69.950005s|local1/entity560|STAND, live MovingBrush9|hop2/goal96|1.950676m/1m|hop180, backward motion|
|361.649994s|local3/entity562|STAND, live MovingBrush9|hop2/goal138|1.992399m/1m|hop180, backward motion|

The native class reference identifies Entity9 as MovingBrush. Each event observes the lock changing from open to closed while the bot has a current matching physical reference and a committed directed approach. Neither the original hop nor the alternative anchor satisfies the unchanged Reached predicate. Subsequent states preserve goal and life identity, show no final floor veto and reverse toward the alternative anchor. Distant bots with no reference or world-brush reference provide same-event controls. Another supported event at4.139m is outside the proposed scoped proximity window; no general moving-platform repair is claimed.

The source path drops commitment specifically when `locks_[hop_]` becomes true, sets its source to the acquisition hint and follows the long alternative. Ordinary timer expiry, actual teleport relocation and false NoFloor are distinct mechanisms. Independent review confirms both repetitions against preserved raw logs and source. This establishes the cause of these commitment losses, not every historical slow pickup.

## Correction contract for testing

Preserve only an already committed original directed edge when the navigator newly observes its hop changing from open to closed and the native adapter currently confirms live, identity-matched MovingBrush support, STAND/CROUCH, valid frame/finite velocity and a distance no greater than the smaller of twice the original point radius and2m. That proximity bound authorizes retention only; it does not enlarge the arrival radius. Keep the exact original hop until normal Reached advances it. Global blocked flags, topology, final safety probes, action arbitration, item deadlines and actual relocation semantics remain unchanged.

Every navigation update must revalidate current contact. Loss of contact, type, range or validity immediately forces ordinary path reconsideration, including before the usual one-second replan timer. No implicit NULL-reference grace is permitted. Goal/reset/recovery/actual relocation also end retention. A bounded start event records real retained approaches without adding queries. Freshness and contact continuity are observed at navigator updates; Human-owned combat intervals are not claimed as continuously sampled contact or exact native transition timing.

A portable regression initially reproduces the loss and separately catches an unintended one-second stale-support grace in the first implementation. The corrected source passes 518 merged bridge checks under ASan/UBSan with pinned SDK107 contracts and87 motion checks; all nine C++ suites, Driver, typed item/ammo and original export tests also pass. Independent review is CLEAR. The cap regression is independently mutation-checked by removing only the private-copy2m cap and observing its expected failure. New native observation remains required. Whether strict current-reference retention avoids the actual lift detour remains unproven until the normal candidate runs. Do not infer success from source, stubs, diagnostic joins or the completed diagnostic600s.

Diagnostic037's first build fails because SDK107 GetRenderType lacks a const overload and is never installed. The qualifier-corrected unique037b build is the diagnostic used above. Normal candidate038 still needs the complete prospective supply gate, five maps, full3600/3600/7200-second windows, resources, original Retail gameplay, weapons/special actions, respawn and recovery before any production rollout.
