# Qualified contention diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task.

**Goal:** Existing Candidate/Selection diagnostics expose the actual qualified
local owner and preference that ranked a higher-score weapon, without changing gameplay.

**Architecture:** Scalar receipt copied only at the existing successful
NearerLocalSupply return; optional output parameter, no second lookup or clock.
Candidate and winner retain that exact snapshot on the stack; existing admitted
rows print it. No persistent state or Driver/final-action changes in this slice.

**Tech Stack:** C++14 Retail adapter and existing portable native bridge harness.

**Spec:** MilestoneA4 and private reviewed supply-final-action-design.md (Delta073).

## Global Constraints

Original .250001 common-clock freshness,5s owner-local progress, cost+1,
8attempts/sharedraybudget, item filtering/connector/goal deadlines unchanged.
Diagnostics defaultoff, same selection cadence/candidate cap/row count.
No additional ray/RNG/lookup/native time/world/entity dereference or allocation.
No pointers escape. Invalid/unevaluated owner = UNKNOWN with cleared scalars.
Exact full selection+owner source inverse to027; Driver byteequal.
Rows includingNUL <2048; separate noCecilparity/nativeimprovement claim.

## Task1 — tests and passive source

- [x] Add actual Candidate/Selection log-contract behavioral checks; run baseline RED.
- [x] Add optional scalar receipt at existing admitted owner, print compactCandidate
      and fullwinner fields including observed common time vs own local clocks.
- [x] Add stale/world/map/entity/generation/item/goal/attempt/deadline/dead/armed
      negatives, winner replacement and no-preference fallback; verify no stale receipt.
- [x] Exact sourceinverse plus deliberate gameplaymutation rejection; printf bounds.
- [x] Run relevant actual bridge once GREEN and inspect all results, diffcheck.
- [x] Commit reviewed source/tests/claim/report. New DLL/runtime qualification remains separate.

## Review Focus

Unqueried owner must not appear unoccupied. Candidate cost excludes connector,
score includesheight. Preserve first qualifyingowner rather than invent cheapest.
Selection snapshot must follow actual winner even when later candidates replace it.
No pure diagnostic receipt may influence policy or admit movement.
