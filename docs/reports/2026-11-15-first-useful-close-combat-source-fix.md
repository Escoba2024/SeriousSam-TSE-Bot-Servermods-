# First-useful Weapon close-combat priority: SDK Source correction

The existing Source disagreed with itself: `BotCecilUrgentItem` marks the first ranged Weapon urgent, and the Driver explicitly grants urgent item proposals priority. `BotSupplyTick` nevertheless yielded to any enemy<8m except urgent Health or accepted special flight. The actual SDK bridge reproduced this for retained mapped Weapon goals with owned masks3 and7:4239 checks, two new priority failures, with the original4231 checks passing.

The correction keeps the legacy closeCombat Boolean, its early `ownsMovement=false`, and the late accepted-flight verification. A fresh typed useful-Weapon target with no useful owned OR usable weapon may plan only as an ordinary candidate: STAND/CROUCH self-state, no retained flight/finishing/important/follow/patrol/interaction context. The existing0x3df8 mask is unchanged. The new final gate grants ownership only after the real Navigator/connector path produces an active, unstuck, unrelocated, unflagged move, no flight context exists and pre-navigation Actor/generation/item/goal/GoalSince/deadline remain identical. Driver final SafeMotion is byte-identical and mandatory. Self-state and proposals are not floors, ACKs or successful pickups.

No Engine getter, physical cast, clock, world lookup, RNG or Driver call site was added. The new logic only copies existing fields and does pure mask comparisons. Newly admitted ordinary-first-Weapon contexts execute existing planning calls that the previous early veto skipped; this is an intentional policy change, not a claim of globally identical dynamic query counts. No radius, fixed deadline, rejection cooldown, mask, lock rule, navigation algorithm, physical permission, CPlayer ABI field or new history/state structure changes.

## Observed REDs and guard preservation

- Reproducer commit `76b5fed` runs the real extracted BotSupplyTick and Navigator: far admission→same retained goal with4m enemy. Owned3/7 remain the only newly failing assertions; Source urgency and deadline continuity already pass.
- A naive four-line exception made closeCombat false. The actual full SDK run failed4253/26, including Flight/FALL/arrival/lock and invalid-context guards. Its patch, Source pins and log are retained as a rejected WIP. No passing claim was made.
- The refined gate restored every old flight/special guard. Its4253/2 result exposed that the old threshold fixture held the player stationary for5s, legitimately triggering Navigator's two-second no-progress recovery. Production was not relaxed: the priority/deadline control now supplies explicit0.04m/tick synthetic SDK progress, remaining before the original first hop. A separate fixed-position case verifies that actual stuck recovery receives no ordinary-first-Weapon priority.
- Explicitly revised old assertions are the close/far first-Weapon priority control, its two DIAG-mode telemetry instances, and the grounded ordinary-tail subcase. FALL still yields; the grounded positive never gains activeFlight or floor proof. All17 invalid-flight guards, arrival/no-ray, special replanning, locks, deadlines, pickup, reset and other safety assertions remain. These deliberate policy updates are not hidden as unchanged regressions.
- Added adversaries cover already owned or usable useful weapons, empty-ammo ownership, unsafe-range Grenade inventory, basic/melee target types, Armor/Ammo targets, invalid weapons context, actual unavailable item and expired deadline. A real final SafeMotion wall rejection still zeros the newly planned movement. Existing urgent/nonurgent Health and other physical/air/teleporter controls remain in the complete harness.

Final full SDK107 normal and one ASan/UBSan run both report **4257 checks,0 failures, Exit0**, serial `nice15`. Both use the real SDK action/physical-ray declarations and the Windows empty `far` macro around actual production Source. No Retail DLL build, Native, live deployment or Raw replay was performed.

```sh
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

## Exact evidence and limits

Current Header SHA `a2cf922bdd05058e50b633282a4ebb21be6f25ef01e1482c5dd56b710a8c88d9`; three exact inverse regions restore whole Parent `652bb66d266d2e52bf961a3b6141112a7fe8abce4c8501032e2c1e3c3e0264dd`. Mutation of the new goal capture,8m threshold or old12s deadline is rejected. Static whole-header member-call and selected global Engine/helper call-site counters are equal. These are Source inverse/call-site checks, not runtime cost qualification.

Private evidence remains under the isolated worktree `.codex/evidence/first-useful-close-combat/`: Parent RED, rejected26-failure diff/receipt, refined two-failure fixture result, final normal/sanitizer logs, exact inverse regions and final source/log pins. Whole inverse receipt SHA `da651b38cfe3dae4f9a3de232507d2d08fe4c43c71ff53471f873db76c96211e`; rejected naive patch SHA `9166776152731fbe43b9a8e2fffc8f8527b736279e6ac25d029c88dcd8636878`.

The034 ownership brackets motivated the Source contradiction test; they do not prove the primary physical pickup failure, exact unsampled arbitration tick or causal Native improvement. Native effectiveness, continuous eight-bot supply, actual useful pickups and regression cost remain unqualified. Root alone reviews, integrates and creates a new DLL/candidate before deciding any Native window.
