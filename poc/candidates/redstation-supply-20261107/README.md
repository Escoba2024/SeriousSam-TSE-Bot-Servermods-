# Cecil/Human Retail-1.07 candidate

Experimental source overlay for the existing vanilla-network-player BotClient. Native qualification is pending. No Dedicated, Engine, Entities, human-client, packet-format or sync-check changes are part of this candidate.

## Source provenance

CecilBotMod `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c` supplies the GPL-2.0 weapon/settings/item/navigation rules. Attribution is retained in the adapted files. Existing ssam.ai Human policy, driver and Retail allocator are integrated in this flat overlay. The source-only packaging reproduces all 47 source inputs of diagnostic build009 before the explicit pit-preset correction; no binary equivalence or runtime acceptance follows from this check.

Pinned build SDK: `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`; Includes: `94ff8cd0e63941f8601294350b616472f772ed51`. The builder archives the SDK and overlays this directory, excluding tests. It records the repository revision, all source hashes, compiler options and resulting PE32 x86 DLL hash. It never installs the DLL. Use an existing authorized MSVC/Wine toolchain:

```sh
python3 tools/build_supply_gamemp.py --sdk /path/to/sdk --toolchain /path/to/msvc --prefix /path/to/build-wine-prefix --output /path/to/new-build-directory
```

Original Retail binaries, raw captures/logs, private deployment profiles and NAV coordinate payloads are not distributed here. Supply the nine authorized Cecil v6 NAV assets privately, with the runtime map-CRC bindings and preset configuration. Missing/invalid assets fail closed. The graph parser and fixtures are portable; actual collision, item acquisition, special map actions and network stability require native tests.

## Portable checks

From the repository root, compile and execute each `test_*.cpp` here with `g++ -std=c++14 -O2`. Run `test_cecil_native_bridge.py` both normally and with `--sanitize`, plus `test_cecil_action_native.py --sdk-player /path/to/sdk/Sources/EntitiesMP/Player.es`, `test_cecil_items_native.py` and `test_cecil_rules_exports.py poc/candidates/redstation-supply-20261107/fixtures/cecil-953b477`. The supplied weapon/settings fixtures are source-derived GPL-2.0 Cecil tables, pinned to the revision above; they contain no NAV coordinates. Python tooling tests use `python3 -m unittest discover -s tools -p 'test_NAME.py'` for build_supply_gamemp, parse_cecil_navmesh, qualify_cecil_live, analyze_cecil_qualification and analyze_retail_sync_pcap.

## Acceptance boundary

The pit check now respects Cecil's opt-in `bAvoidPits` and fresh current-path-point condition. Its remaining read-only off-graph support ray is conservative and is not equivalent to Cecil's temporary-entity `WouldFallInNextPosition` physics. No entity mutation is used to emulate that behavior.

A build or portable test does not qualify deployment. Final native gates require the same DLL hash for 1 bot/3600s, 4 bots/3600s, 8 bots/7200s and recovery, plus actual behavior on all five operated maps and an original Retail gameplay client. The live observer reports measurements and keeps behavior review explicitly pending; sampled packet CRC equality is only diagnostic evidence.

License: adapted Cecil code and source-derived fixtures retain Dreamy Cecil attribution under GPL-2.0; see the repository [GPL text](../../release/LICENSE).
