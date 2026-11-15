# Mapped220 circulation: SDK reproduction plan

> **For agentic workers:** Use superpowers:executing-plans, systematic-debugging and test-driven-development. Root alone decides any gameplay fix after this RED-only task.

**Goal:** Test whether a legitimately reached neighboring acquisition node can repeatedly restart the existing per-edge transit budget while the same mapped first-weapon attempt makes no sustained route progress.

**Architecture:** Extend only the actual SDK107 bridge fixture, keeping BotSupplyNative.h/cecil_motion.h unchanged. Execute real BotSupplyTick→ChooseGoal/Nearest→Navigator.Update→SafeMotion→HopCheckpoint/ItemTransit. Scripted external positions isolate the mechanism; they do not simulate native physics or explain the first blocked ray.

**Tech Stack:** Existing C++14 extracted production bodies, Windows `far` macro, pinned SDK107 Player.es contracts, serial nice15 portable compiler; ephemeral executable in tmpfs to preserve disk reserve.

**Spec:** Root ruling following the derived-only Weapon220 investigation, 2026-11-15. Native Source A0/g39 attempt10489–10889 had Goal27 and fixed20s lifetime; source states repeatedly showed60→59 and62→60. Source/Native clocks remain separate.

## Constraints and review focus

- No production, limits, radius, height, flags, locks, floor, deadline, CD or RNG changes. No Native/MSVC/buildDLL/Frida/live activity or Raw replay.
- Original authored local point positions/radii/flags/important/locks; induced directed subgraph27/59/60/61/62 only. Omitted routes make this a bounded mechanism fixture, not the complete native graph/lock state.
- Anchor may be initialized once to an actually occupied source60; subsequent hints come only from real ChooseGoal/Nearest. Never assign anchor62/hop59 during the loop.
- Every interpolation/velocity/support/cast is explicitly synthetic. Physical cause behind the native approach failure remains UNKNOWN. Support187's type/motion is not established by its ID.
- Relocation must pass the original two strict arrival spheres; target27/edge59 must not be reached. All original per-frame guards and fixed20s lifetime stay active.
- A falsifying positive control must be capable of actually reaching59 and progressing to27. This task must not reinterpret a legitimate completed route as failure.

## Task1: source-backed diagnosis and bounded fixture

- [x] Inspect only existing032 derived outputs and relevant production bodies; verify goal220 deadline and terminal/pickup limits.
- [x] Add fixture to `poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py`, original local metadata, real fresh Nearest/committed transitions, scripted3s loop below59.
- [x] Assert admissible relocations, repeated60→59, fixed attempt/deadline, finite bounded query use, unchanged inventory, nonstationary external movement and no target arrival. Track first global target best versus revisited-edge clock resets.
- [x] Run actual SDK fixture normally:4181 checks/one desired behavioral failure, old4175 checks and five new controls pass. Complete log preserved; no production changes. Two adjacent fixture `if`s subsequently split into separate lines only to remove compiler indentation warning; this whitespace-only delta is separately disclosed.
- [x] Report smallest supported fix *design* and countercases to Root, without implementation. Any episode tracking must preserve all existing safety/lifecycle/ownership guards and deadline.

## Native evidence boundary

Twenty sparse source states do not prove uninterrupted accepted movement, exact relocation callback time, item-transit timer state or primary collision. `floor=2` means verified escape, not rejection; `rays` logs16−remaining budget; `liquid` logs PlayerState, not a Boolean water flag. MotionProbe is emitted only when final safety is0, so an accepted escape can conceal its primary rejected direction. A diagnostic proposal/Submit is never a native movement/pickup ACK.

Private evidence `.codex/evidence/mapped220-circulation/diagnosis-receipt.json` SHA82833097ae5d56773039c4705bb8e76fc5717df3b1f81df14605ded34a48d472; full SDK log `sdk-red.log` alongside. Compiler/executable naturally ended, ephemeral tmpfs directory removed by existing harness. No remaining jobs or Raw handles. Await Root gameplay ruling.
