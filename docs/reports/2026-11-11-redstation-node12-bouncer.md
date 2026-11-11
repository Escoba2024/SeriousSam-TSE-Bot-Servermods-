# Red Station node12→34: Bouncer, not a demonstrated Teleport entity

Read-only follow-up to the [006 acquisition diagnosis](2026-11-11-arena006-acquisition-diagnosis.md). No process access, hooks, runtime changes or gameplay implementation. Static analysis used the legal private fixture's original `RedStation.wld`, original Retail1.07 Engine/Entities DLLs and the SDK's `EntitiesMP` sources. Ghidra/Frida tools were unavailable in this session; the binary counterchecks below used `objdump` and bounded Python decoding of static files. This does not claim Ghidra qualification or native acceptance.

**The authored node12 corresponds to Bouncer234. Node34 is the Minigun destination, not a proven teleport exit.** The actual world contains20 class filenames including Bouncer, TouchField, Trigger and Marker, but no Teleport or PlayerActionMarker class. Its `Models\Editor\Teleport.mdl` resource does not establish a Teleport entity. The static association is recorded without absolute world coordinates in the [evidence JSON](2026-11-11-redstation-node12-bouncer.json).

The original world SHA256 is `66e1309ee6eeeda8c564574df65df87a8406f4079b78ad508e77c82d19971111`, member `Levels/LevelsMP/Deathmatch/RedStation.wld` in the private `SE1_00_Levels.gro`. `ENs2` at0x7956a contains443 unique entity records; the32-byte records terminate exactly at first `ENT4`. Entity234 resolves to Bouncer, with the same horizontal origin as node12 and origin0.6875 below it. Its `ENT4` at0xab4c9 binds brush8. Nine typed `PRPS` properties decode speed118, direction317.5°/35°/0, control5 s, max exit speed200, normal multiplier1 and parallel multiplier0. Entity243 is the WeaponItem at node34; WorldBase373 is the floor there, consistent with the previously observed connector collider373.

Brush8 begins0x4acf1 and contains16 double-precision vertices (`VTXs` at0x4ad29, followed exactly by `PLNs`). Its local bounds are x/z−3..3 and y−0.1875..0.375. The top is therefore0.3125 below node12. These are geometry bounds, **not a complete collision/ETouch volume**: player collision shape, contacting polygon and support still matter. Nav radius4 exceeds the pad's horizontal half-width3, so satisfying nav arrival alone does not establish contact with this Bouncer.

## Source behavior and original binary counterchecks

SDK `Sources/EntitiesMP/Teleport.es:77–105` initializes an immaterial touch model, stretches width/height, and handles `EPass`: an active instance with a target teleports the entrant to target placement; optional players-only and force-stop checks apply. It requires no USE action or facing test in that handler. This is source behavior; no such class instance was found in this world. `Player.es:6116–6119` is a separate automatic-marker teleport path and does not explain this authored Bouncer route.

The relevant path is `Player.es:6691–6700`: `ETouch` with class Bouncer calls `JumpFromBouncer`. `Bouncer.es:8–24` checks model/movable state and non-null physical reference, derives direction from the Bouncer and calls `FakeJump`; `:49–53` initializes a fixed brush. There is no USE button or player-facing requirement in this path. Ordinary physical contact and valid support are required; artificial arrival or entity teleportation is not equivalent.

Counterchecked against original Entities SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`:

- Exported `JumpFromBouncer` at0x6035e870 checks render3, movable0x200 and non-null reference at0x6035e87a–890; 0x6035e899 reads direction and 0x6035e8df calls the imported FakeJump path. This confirms the source's critical support guard without assuming1.10 layout.
- Player handler class check at0x6040ad65–0x6040ad79 reaches the direct `JumpFromBouncer` call at0x6040ad84. This agrees with the SDK touch handler; it is static control-flow evidence, not an observed contact event.

Counterchecked against original Engine SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`:

- `CWorld::ReadState_new_t` at0x60179730: entity creation reads serialized ID and filename/placement at0x60179ae6–b46, then restores ID at0x60179b65.
- `CEntity::Read_t`0x601c1590 handles the ENT4 header; the brush branch0x601c18c4–18de resolves the serialized index through the world's brush archive.
- `ReadProperties_t`0x601c71a0 separates low-byte type and property identifier shifted8 at0x601c71f8–7217. Bouncer property IDs match the SDK generated Engine107 tables.
- `CBrushSector::Read_t`0x601cd1e0 copies24 serialized bytes per vertex at0x601cd3bf–3f1, consistent with three doubles and the next chunk boundary. No guessed process-memory reads were used.

Original Cecil reference953b477e uses TELEPORT32 solely for zero outgoing path cost (`PathFinding/Navmesh.cpp:689–692`), not an event invocation. Destination OVERRIDE takes priority, otherwise source flags (`Logic/BotMovement.cpp:200`); thus both8→12 and12→34 use42. The current flag propagation agrees. For this world, calling12→34 a physically instantaneous teleport is unsupported; its Bouncer association explains why the authored graph can connect distant points without a walkable corridor.

## Native limit and smallest next observation

006 botB local1/gen7 shows tick960 approaching8→12 with Jump requested and support0; tick980 has advanced12→34, still support0 and beyond the pad; tick1000 remains on that edge with support0 (log lines924,930,953). No sampled state/terminal row in that window identifies support234. These roughly one-second samples can miss contact or a short launch. They support investigating approach/arrival/contact, **not concluding that jump pulses, radius4 or any single code path caused the failure**.

Proposed diagnostics only, not implemented:

1. Under the existing native world lock, emit bounded map-once metadata from existing entities: class/ID/generation, Bouncer placement/direction/speed/control, brush bounds, and the associated source/destination nodes. Use already validated class/property APIs or explicitly verified Engine107 types. No new ray, RNG, event dispatch, target change or engine-state write. Any diagnostic lookup/cache must remain separate from decision state and invalidate on map change.
2. For one bounded approach/attempt per local player, sample each action tick near8→12 and12→34: simulation tick, entity/life identity, source/hop before and after update, node-distance/arrival result, current and intended translation, support entity/class, movement state, requested/final jump and final movement owner. Reuse values already read/calculated by production decisions; do not call navigation, SafeMotion or item-selection a second time. End on death/context change/deadline or a fixed short sample limit; never prolong an attempt for logging.
3. Compare native motion before/after contact against the configured launch direction and velocity. A state trace can distinguish premature route advance, physical overshoot and a real launch followed by bad steering; it cannot by itself prove the ETouch call occurred. If exact event attribution remains necessary, use a separately authorized minimal passive hook on the verified original function, with uninstrumented control and cost measurement. Do not substitute a synthetic jump/teleport call.

Before a gameplay change, obtain the actual failing decision transition and reproduce it portably. Preserve normal contact, support and physical-movement permissions; do not blanket-remove JUMP/TELEPORT flags or shrink source radii from this static finding alone.
