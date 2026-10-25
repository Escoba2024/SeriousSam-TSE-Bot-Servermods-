# 2026-10-26 ssam.ai Red Station runtime release gate

**Scope:** isolated read-only QA worktree, based on PR #63 (not `main`), no production writes.

## Grounded discrepancy

Active eight-player Red Station server at `127.0.0.1:25601` (Hetzner loopback, 2026-10-25 23:40 UTC):

- Existing mounted server `Scripts/PersistentSymbols.ini` explicitly declares `gam_bInfiniteAmmo=(INDEX)1`.
- Existing mounted `Scripts/Dedicated/BotTest/1_begin.ini` specifies `gam_bInfiniteAmmo=1`.
- Native GameSpy `\\status\\` reported `mapname=Red Station`, `gamever=1.07`, `difficulty=Hard`, `infiniteammo=0`.
- Independent native GameSpy `\\rules\\` also reported `infiniteammo=0`.
- Root cause **NOT ESTABLISHED**: perhaps mode/session initialization overwrites it; requires separate isolated native tests. Neither a script assignment nor offline unit tests are proof of gameplay behavior.

## New evidence gate

`tools/release_gates/redstation_gate.py` validates both read-only query replies and rejects missing final markers, wrong hostname/game version/mode/map, wrong difficulty, inconsistent rule status and missing/wrong ammo setting. It exits `8` for unexpected or incomplete runtime state and `0` only for a matching configuration snapshot. It never reports a full release PASS.

Usage with the existing read-only query port (not a game process operation):

`python3 tools/release_gates/redstation_gate.py --address 127.0.0.1:25601`

For offline fixtures use both `--status-json /path/to/status.json --rules-json /path/to/rules.json`. Such output explicitly reads `SYNTHETIC_FIXTURE` and `release_qualified=false`.

## Reproduction

- Five newly written tests failed before the new CLI existed (8 checks across subtests, exit `2` vs expected `8` or `0`).
- After implementation `python3 -m unittest discover -s tools/release_gates -p 'test_*.py' -v`: **5/5 PASS**.
- Existing `python3 -m unittest test_redstation_preset test_gamespy_query -q` from `tools/`: **18/18 PASS**.
- Read-only live query: **exit 8, CONFIG_BLOCKED**, `status.infiniteammo='0' expected '1'` and `rules.infiniteammo='0' expected '1'`.

## Next work for Codex lead

1. Identify runtime initialization and the actual owned `gam_bInfiniteAmmo` setting path on an **isolated native Retail 1.07** instance; reproduce GameSpy `0` with controlled flags and find the smallest change.
2. Add negative regression covering the corrected runtime state and test ammunition behavior in an original Retail 1.07 client, then re-run Sync/WAN/multiplayer gates.
3. Keep PR #63 separate and draft until native MOTD/300-second chat/UI verification. Do not adjust protected `.wld`, original DLLs, current public sessions or fail-open this configuration gate.
