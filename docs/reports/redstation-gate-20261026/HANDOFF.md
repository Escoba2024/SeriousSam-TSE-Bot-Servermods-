# 2026-10-26 ssam.ai Red Station runtime release gate – corrected encoding

**Scope:** isolated, read-only QA worktree based on PR #63. Public processes/players, binaries, scripts and other agent worktrees unchanged.

## Critical source-level discovery and corrected conclusion

The first version of this gate **incorrectly** treated GameSpy `infiniteammo=0` as "disabled". A later source audit disproved that inference:

- `Sources/Game/SessionProperties.cpp:213` in the separately checked-out Serious Engine SDK copies `gam_bInfiniteAmmo` to `sp.sp_bInfiniteAmmo` when creating a multiplayer session.
- `Sources/Game/SessionProperties.cpp:348` emits **`\\infiniteammo\\%d` with `sp.sp_bInfiniteAmmo ? 0 : 1`**, reversing the conventional numeric reading. Similar inversions exist for `ammostays`, `friendlyfire` and other GameSpy booleans.
- At 2026-10-25 23:40 UTC active server configuration contained `gam_bInfiniteAmmo=(INDEX)1` in `PersistentSymbols.ini` and `gam_bInfiniteAmmo=1` in `Scripts/Dedicated/BotTest/1_begin.ini`. Both native GameSpy `\\status\\` and `\\rules\\` responded `infiniteammo=0`, consistent with **enabled** under the inspected SDK wire encoding.

**Evidence limitation:** the inspected open-source SDK is NOT proof of byte-identical Retail 1.07 GameMP binary behavior. An original Retail 1.07 client must confirm ammunition is not consumed and Sync remains healthy. This gate passes only the **configuration snapshot**, never full gameplay, 300-second chat, MOTD HUD or vanilla-release acceptance.

## New read-only validator

`tools/release_gates/redstation_gate.py` queries native GameSpy `status` and `rules`; it rejects incomplete replies, wrong name/mode/version/map, wrong difficulty, cross-response discrepancies and invalid infinite-ammo wire encoding. It returns exit `8` on config mismatch and `0` on matching snapshot. The output always has `release_qualified=false`, and offline fixture output is always `SYNTHETIC_FIXTURE`.

Live read-only command:

`python3 tools/release_gates/redstation_gate.py --address 127.0.0.1:25601`

No production process signals, changes or game-client captures are performed.

## Test evidence

- Initial red/green implementation: 5 new tests PASS; inherited `test_redstation_preset` + `test_gamespy_query` 18 PASS.
- After discovering inverted encoding, **2 tests failed (RED)** before correcting the validator; following code correction all 5 new tests PASS.
- Current GameSpy configuration snapshot: `infiniteammo=0` is treated as **0=enabled** per inspected SDK, while gameplay still `NOT_TESTED_RETAIL`.

## Remaining native acceptance

1. Validate the actual Retail 1.07 GameSpy encoder or capture original-client ammo consumption during a controlled isolated match.
2. Confirm the dedicated session options are applied on entry and at respawn and confirm correct damage/hits and sync.
3. Verify MOTD is shown to human players and 300-second chat sends exactly once, including on match restart; powerup removal still unsupported pending vanilla-compatible proof.
4. Integrate only through PR #63/PR #70 dependency after native gates, preserving protected builds and backups.
