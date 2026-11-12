# Preselected RedStation flight exit after item loss

Status: portable regression and source review only; new candidate native effect remains untested. This change addresses one observed item-loss lifecycle boundary, not every Laser terminal miss or repeated contact.

## Observed failure

Completed private window `arena012brush3p-i1-swap1-trial-1-010721` had full retained original-function coverage, clean detach/body restoration, four normal closes and accepted post-close logs. Candidate local2/entity567/generation8 lost Laser item267 at driver tick2445 while committed84→86. Bounded finishing ended at2474 with `arrived`; tick2475 selected Minigun243, followed by uncommitted reacquisition of86 and another original `JumpFromBouncer` call with known Brush argument136.

Native inventory brackets the arrival with upward velocity38.276 then35.276 and null support. Arrival at geometric node86 was therefore during ongoing physical flight. The precise2474 callback position was not sampled. Two136 calls already occurred before this endpoint; the change does not explain or claim to repair those earlier contacts.

## Change and limits

A read-only observer walks the already computed, bounded navigator parent chain. Its search origin must be the current source with the current edge on the selected path, or the current hop from an existing suffix refresh. Bounds, locks and original directed links are checked. It performs no new search, allocation, ray, entity lookup or RNG operation.

Only the verified original RedStation world path/content CRC `ff3776e0`, NAV content CRC `e4571656`, and exact84/86/176 metadata admit the new behavior. World-path hash `5af1a276` is a separate identifier. Node86 and176 have ordinary flags0; the prior special edge84→86 supplies provenance. Slot176 has stable ID178 and important entity267. After item loss it is only the preselected geometric exit, never a new item/USE/important interaction.

While item267 is still valid, an accepted same-action flight plan may seal one selected successor176. On real arrival at86 during pending finishing, all existing world/map/entity/life/gravity/goal/attempt/deadline, fresh accepted motion and FALL checks still apply. The ordinary existing navigator Update must produce exactly86→176 without relocation, stuck or arrival. Its existing arrival replan is not an authority source: any other output ends neutral. The seal is consumed once. There is no resealing or arbitrary successor chain after item loss, new deadline, radius/flag/topology change, synthetic launch, support permission or entity write.

Death, goal/life/map resets and FlightEnd clear the seal. Existing final movement safety remains authoritative. The diagnostic-only single `CecilFlightFinish action=continue` event identifies the consumed transition for the next native experiment; normal per-tick logging is not added.

## Verification

The initial regression retained the existing2526 checks and added the native loss/arrival boundary with both existing cache-origin forms:2534 checks,4 expected failures before implementation. The first implementation passed2536 checks. Expanded SDK107 bridge verification under ASan/UBSan passed2687 checks with zero failures, retaining the actual Driver arbitration and native item helper bodies.

The existing NAV suite passed287 checks and motion suite101 checks under ASan/UBSan. Independent read-only source review found no important or critical issue; the stale current-edge-only comment was corrected.

Coverage includes stale/unrelated/absent cached paths, invalid indices/counts/locks, changed metadata/world binding/serial, entity/generation/world/gravity/attempt/deadline changes, missing or stale accepted motion, ground state, death and same-entity respawn, actual normal navigator stuck/relocation, one-time consumption, terminal arrival, valid live-item behavior and visible close-combat ownership. Pure observer tests verify unchanged RNG/ray/lookup counts, no heap allocation and unchanged deadline/search output. All earlier ordinary/unavailable, unrelated special-edge and movement-safety cases remain in the full suite.

The lifecycle regression uses retained pre-loss positions and observed loss/arrival ticks. Missing intermediate positions are explicitly synthetic inputs; the reached-node fixture uses the original node center. It does not simulate native physics or claim the modified commands reproduce the old trajectory.

Reproduction:

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Native gates remain open: actual sealed continuation exercise, final safety acceptance, retained original deadline, no premature new item selection, physical landing/acquisition, repeated contact behavior, whole-life acquisition and matched public comparisons. No A3 or A4 acceptance follows from these portable tests.
