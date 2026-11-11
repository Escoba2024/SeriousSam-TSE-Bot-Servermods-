# Retail1.07 physical ray mask: native cause and source correction

Status: **cause demonstrated in measured segments; normal candidate qualification pending**.

Original Engine.dll SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`. Private diagnostic033 DLL `428a0882fdbe2f78bb0fdf59cdadf367dc4abc35b43177cad296ad01338fd460` uses normal030 behavior plus read-only post-SetAction observations and budgeted counterfactual queries. Its actual overlay is manifest-pinned; it is not an unmodified public-source build or performance evidence.

## Same-segment native controls

The full600.004699-second four-bot RedStation observation completes with596 samples and no recognized monitor/native errors. At three actual accepted-recovery NoFloor episodes, compare both the exact last rejected floor segment and the measured current-foot segment. Each of these six segments has identical endpoints, TT_NONE and radius0 across four explicitly initialized local query policies:

| Policy | Applied mask | Mask after query | Native result on every segment |
|---|---:|---:|---|
| Normal Cast, physical | 0 | 2064 | No hit |
| Normal Cast, physical, pre-set PASSABLE | 2048 | 2064 | No hit |
| Normal Cast, nonphysical, pre-set PASSABLE | 2048 | 1077936128 | No hit |
| Original Cecil explicit-sector path, physical | 2048 | 2048 | Actual upward nonpassable brush hit |

All six original-helper hits identify world brush1 at Y−0.75, upward normal/support1 and polygon flags274752625. The actual standing polygon has the same plane. Four measured model-space spheres have radius0.5 and transformed lower extent0; actual foot placement lies5–9mm above the plane. The rejected segments cross from1.005..1.009m above to3.991..3.995m below it. No larger radius or different origin is needed to explain these results.

The original mask2064 includes both PASSABLE2048 and SHOOTTHRU16. This floor is nonpassable but carries SHOOTTHRU; SDK107 explicitly distinguishes passage of physical raycasts from physical objects. Normal Cast also demonstrably overwrites a pre-set2048 mask. Switching physical off does not repair the query. These are measurements against the original Retail1.07 binary, not deductions from Open Source1.10 behavior. The observation demonstrates false NoFloor for these exact rejected recovery actions; it does not retrospectively establish every historical idle or sync cause.

## Original implementation and bounded adaptation

[Cecil953b477, SandboxCommon.cpp](https://github.com/DreamyCecil/CecilBotMod/blob/953b477e53fdc5a5d84c8ae8d759c84fdf6c973c/Sources/Bots/SandboxCommon.cpp) implements CastRayFlags by initializing hit fields, setting its explicit mask, adding origin sectors and testing through sectors, then deriving the hit point. It deliberately avoids normal Cast. BotFunctions.cpp physical navigation callers request PASSABLE alone. Retain Dreamy Cecil's copyright and GPL-2.0 attribution when adapting it. Retail exports for AddSectorsAroundEntity, TestThroughSectors, TestWholeWorld and ClearSectorList are present; diagnostic033 actually executes the origin-sector helper path and measures its result.

The integrated source shares this physical movement query path across navigation/item connectors, measured missing-reference support, final wall and final floor. It preserves each caller's model mode, over-hit setting, ray budget, geometry, normal/passability checks and final action arbitration. The separate combat visibility path remains unchanged. Finite endpoints and a positive representable segment are checked before normalization, exact zero navigation segments have a defined result, and invalid segments fail conservatively. The integrated helper and native bridge now model the observed normal-Cast mask overwrite and solid shoot-through versus genuinely passable surfaces. Exactly zero navigation segments avoid both the native constructor and query; invalid or collapsed movement segments fail conservatively before normalization. The merged source passes 486 bridge checks under ASan/UBSan against pinned SDK107 button, polygon and model-enumeration contracts; all nine C++ suites and actual Driver/item/export contracts also pass. Independent review of the complete source change and final null-world guard is CLEAR. These are portable checks, not candidate036 native acceptance.

A separate reviewed correction returns fully rejected stationary aligned recovery approaches to the existing bounded sweep. It requires actual accepted movement, STAND/CROUCH, finite total speed<=0.1m/s, requested world direction within1degree of the horizontal original-node direction, original NoFloor and no budget/invalid uncertainty. Held-only and successful escape actions do not reject a target. The initial unaligned variant reproduced a0↔9degree turn cycle and was corrected before integration.444 sanitized SDK bridge checks and independent counterexample review pass. Neither correction has normal final-hash native acceptance yet.

## Evidence limits and disposition

Diagnostic031 supplies earlier foot/plane/radius controls and closes normally after a partial observation.032 was built but never installed because its pre-Cast mask read could be indeterminate.034 was an unused unchanged033 build after a preparation assertion failed;035's broader pose sampler was built but never needed after033 produced the exact-segment evidence. Their manifests and unused dispositions remain private.033 closes bots and server normally and preserves all raw logs.

Next normal candidate036 requires a new published exact source/hash and all affected supply, five-map,3600/3600/7200-second, resource, original-Retail, weapon/special-action and recovery checks before serial six-instance rollout. Additional isolated fixtures may run these full windows concurrently under a protocol declared before launch; durations and pass thresholds do not change. No public binary has been changed by these diagnostics.
