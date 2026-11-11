# Observe the actual11→12 approach transition

The completed009 run also showed approaches from10 through11 before12→34, but the existing diagnostic episode started too late to retain their first requested UP. This separate change extends only the existing diagnostic trigger. It adds no gameplay rule for11→12.

The new trigger requires an active, non-arrived, unstuck, unrelocated output with hop12 and the navigator's actual committed source11. It accepts either a reached previous hop11 in that same Update, or the already committed source11/hop12. Merely selecting a distant hop11 does not start an episode. Existing node12 metadata checks, default-off diagnostics, one episode per life, six-second/120-row bounds, raw-before-adjustment capture and final-action reporting stay unchanged. The existing death and same-entity respawn reset remains covered. SourceSlot is a const field query; no ray, lookup, selector or RNG is introduced.

Tests execute actual navigator arrival11→12 and its continuing edge, assert that ordinary UP remains1, compare diagnostics off/on without gameplay changes, reject distant11/stale navigator/inactive/arrived/stuck/relocated/wrong-geometry cases, and retain the bounds/reset checks. RED before the trigger addition:1806 checks, three expected failures. GREEN with `python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`:1806 checks, zero failures under ASan/UBSan. Independent read-only review found no Important/Critical issue.

This expands the next native observation only. It does not establish the cause of the11→12 misses or qualify any new native behavior.
