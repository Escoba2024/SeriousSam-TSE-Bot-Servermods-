#035 Yodeller options v2 correction

Owner a4_diagnosis, same isolated WT/new branch `codex/20261115-build035-yodeller-options-v2`; writer claim only existing pure builder/tests and own docs. No oldD/F, Root, gameplay, build or runtime writes.

Cause is now reproduced: actual Fv2 Runner CLI emits Yodeller600/diag0; extracted actual adapter.options accepts it, but actual a4_hard_map_policy.options throws `Hard map: fixed300s diagnostic window`. The first7tests never called this second production policy; their two-file inverse guaranteed preservation of the wrong old window. Root's failed start/owner/ended/host files and old packages remain unchanged; no engine/window acceptance is inferred.

- [x] Execute actual paired production functions with emitted CLI: behavior RED1/1 with fixed300s ValueError, no import error.
- [x] Keep actual035Trouble parent and all current fixes; add `a4_hard_map_policy.py` as third changed Source. Only options literals change: fixed Yodeller still in current catalog,600duration,diag0. Startup-count, Hard validation/registry/reader/clock/config/safety code byte-identical.
- [x] Create fresh `/srv/tse-nav20-035-yodeller600-diag0-disabled-v2-20261115`, explicit three full inverses. Do not overwrite oldD623b4920 or oldFv2.
- [x] Paired actual adapter/hardmap functions + final Runner CLI GREEN; reject other map/duration/diagnostic/types and missingcatalog. All oldSource/provenance/asset/safety tests remain. Check full pin values and141→140other unchanged parent files.
- [x] Small failure/correction report, complete private pins/inverses and commit. Root independently reviews/freezes/backups and alone decides a fresh start. No guard/resource/sampling changes or NativeReady claim.

Actual behavior RED0.017s retained; final10tests PASS0.130s. FreshD-v2 manifest9b2b2fac…/Runner9ca11ad3…,160/147/79pins,81sameBuildpins, three full inverses,140other Parent files byte-equal. All jobs ended at handoff; no gameplay/compiler/Native action.
