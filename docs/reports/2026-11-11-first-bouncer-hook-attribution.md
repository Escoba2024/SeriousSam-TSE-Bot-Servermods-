# First Bouncer hook: successful old-bot route, not a candidate failure reproduction

Read-only attribution of completed `arena007hook-checked-swap0-trial-1-221254`. Raw evidence remains private; the companion JSON records source hashes, identity mapping and line references without player names, addresses, process pointers or absolute world positions. No runtime or gameplay changes were made for this analysis.

**The sole hooked player565 is old048 botA/local0, global slot0. Its Bouncer234 launch is followed by acquisition of the target Minigun243.** It is not the Vanilla observer. `botA.log:208–211` identifies locals0–3 as565–568; native inventory binds them to global slots0/2/3/4. `botB.log:208–211` identifies569–572 at slots5–8. The remaining original observer is563/slot1. These assignments persist throughout the inventory file.

The harness names `physicalA` for slots1–4 and `observer` for0–3 are sampling groups, not reliable cohort identities. My initial informal slot0=observer attribution was wrong and withdrawn. The existing full240-second007 report already joins actual BotCombat/self identities and native slots0/2/3/4; independent inspection found no established cohort-value error in that report. The same identity mapping occurs in both trials.

## The observed chain

Old botA/local0 generation8 spawns at native34.899754. It selects Minigun243 at Cecil tick878 (`botA.log:758`). Its route progresses through63→68→6→7→8→12; tick1080 still has source8/hop12 and flags42. At tick1089 it acquires Grenade ownership first:3→259 (`:936`), while retaining the Minigun goal.

The original function event at Unix1794435265891ms has before support entity234 and velocity approximately(−13.37,−6.19,−0.12), then after support null and velocity(59.78,63.71,−80.10). The player identity, world and position remain unchanged through the call. This is actual native launch execution, not an inferred jump from sparse positions. Server inventory brackets it between native45.499592 and45.599590 (`inventory.jsonl:920,923`); session-health samples313–314 independently bracket the same global slot and motion across peers. The player is in the same life, about10.65 seconds after spawn.

Cecil ticks1100/1120/1140/1160 retain source12/hop34 and goal243 during flight. Tick1165 records ownership259→323, adding Minigun bit64 (`botA.log:987`); the adjacent native weapon observation reports time49.249535 and owned323 (`:990`). At tick1180, anchor34/source34 and the next goal556 replace the completed approach (`:997`). Health remains100 in these observations. The weapon's disappearance is logged as goal-unavailable at tick1165; ownership gain and destination arrival establish success despite `goal_picked=0` in that diagnostic.

Inventory polling has a gap from native48.899540 to52.449486, so it does not independently time the Minigun acquisition to49.25. The first subsequent inventory sample (`:1003`) corroborates owned323, the unchanged spawn clock,100HP and non-null support. Do not substitute that later sampled acquisition time for the Cecil/native weapon-event time. Different clients' Cecil action ticks also have different offsets; raw tick numbers cannot be aligned between processes without native clocks or event brackets.

## What this resolves and what remains open

This successfully executed ordinary contact→native launch→flight→destination pickup rules out a universally broken Bouncer234 or an intrinsically impossible12→34 route. The authored TELEPORT flag does not require an artificial teleport call. The actual old bot succeeds with the existing flags42 and normal engine physics.

It does **not** establish why candidate006 missed/repeated this route. In this60-second007 hook window the candidate has no sampled source12 state and no Minigun243 goal; it supplies no failing candidate approach to compare with the old success. The earlier006 trace still demonstrates premature-looking route progression without a sampled launch, but its coarse states cannot identify a missing touch, failed support guard, physical overshoot or post-launch steering as the exact cause. An approach-speed difference alone would also not prove causality.

The narrow next observation is a bounded candidate attempt on8→12→34, tied to the same local/entity/life, recording each action's approach/arrival transition, actual and intended velocity, support identity, final movement ownership and jump input alongside the original event hook. A missing call while the path advances would separate contact/arrival failure from a call rejected by native guards; a successful call followed by a miss would instead focus the flight. Preserve ordinary physics and permissions; this evidence does not justify changing radii, deleting jump flags or synthesizing a launch.

The completed window reports60.050696 seconds, one matched event, zero dropped records/faults, no observed SYNCBAD/disconnects across four roles and all own roles closed. Original hook bytes were reported restored. This is a limited native diagnostic success, not long-duration sync, candidate route acceptance or proof of zero instrumentation cost; an uninstrumented007 control exists but is not a matched frame-time comparison here.
