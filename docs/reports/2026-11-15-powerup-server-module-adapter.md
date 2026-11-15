# Strict server module adapter for the powerup contrast

Two fresh OFF0/ON1 v2 packages are prepared and disabled. No native run, new
DLL, live change, tolerance relaxation or causal sync finding occurred.

The actual OFF061540 case remains FAIL. Its first Reader.sample returned
successfully, but canonical binding called V2.check_sample, which required
original GameMP1c41 despite the deliberately staged and loaded fe4 Dedicated.
InventoryReader already pinned fe4 correctly. The successful read1 metadata
was journaled; `inventory.jsonl` is0B, so its full raw sample is unavailable.
Portable reproduction uses the pinned reader return contract and real own
server PID/start; it is not described as replay of a saved native sample.

The complete downstream path was checked:

- Paused smoke and gameplay: orderedV3.bind_sample -> canonical.bind_sample ->
  V2.bind_sample -> V2.check_sample.
- Full final V3 validation, including excluded overlap: canonical.validate_all
  -> V2.check_sample before any evidence selection.
- Direct V2.evidence/apply also call that same sample check.
- Source/life/Decimal/FIRE/pickup auditors do not contain a second GameMP hash
  assumption. Physical role modules remain guarded by the original backend;
  original Engine/Entities fingerprints and the external reader are unchanged.

The original `a4_fire_observer_v2.py` stays byte identical. A separate
`powerup_server_native_fire.py` is generated from it by exactly two invertible
substitutions: one policy import and delegation of the one module-hash check.
The new pure policy accepts only role `server`, matching PID/start, original
Engine/Entities and exact fe4 GameMP. Original/bot/unknown GameMP, wrong role,
wrong PID/start, missing/extra/changed hashes fail. No union of accepted DLLs
and no rewriting of native sample hashes is used. All other V2 code, consistency,
epoch and evidence rules remain identical. Runner and canonical groups explicitly
import the new server copy; V3 and both auditors remain byte identical.

Root additionally ruled preservation of only the first successful unbound read
(global serial1, paused_smoke). The runner archives the complete untouched sample
BEFORE its existing presence/binding checks, with already available role, PID/
start, group, phase, serial and read interval. The new sidecar is0600,
O_EXCL/O_APPEND, one record≤65536bytes. No extra clock/native query is made.
Wrong-hash/PID and later consistency rejection leave this record intact.
Duplicate/overwrite/symlink attempts and oversized/bad-provenance records fail.
This adds one bounded paused-startup write, subject to the unchanged resource
and startup limits. Later prebind failures can still lack full raw data; this
is not a complete all-read archival claim. Existing inventory/journal schemas
and queues are unchanged.

The two modified existing files (runner and canonical-group import) invert to
their parents exactly. The generated server copy inverts to the original V2
exactly.67 other parent files, complete finally/finalizer, source config/Nav,
profiles, candidate closure, counters/attempts, sampling and all gameplay,
clock/life/host guards remain unchanged. Both arms still use fe4 Dedicated,
048 Expert-Rifle bots, original observer20FPS, Hard2/Red600/diagnostics0.

| Fresh disabled package | Manifest SHA256 | Controller SHA256 |
|---|---|---|
| `/srv/tse-powerup-off0-048-red600-module-v2-disabled-20261115` | `3f21c95ea2f2e364c12e0815a976edcab77a70afdab3c565eb2797821eb7b2dd` | `7227d9bccc830f0ab97b94d1cd43da6de631df49d0a0825bf57670f0662c5b7c` |
| `/srv/tse-powerup-on1-048-red600-module-v2-disabled-20261115` | `f24c74d9f6f8052190f8e753b9968480ef764c2d1cfab70020fd990aa4fbdc8e` | `b4f7eb739d85e553e190eda989789e05752b6201bf310b0bf5c6b7affdf29902` |

Both have223 runtime/75source/48Python pins, including81fe4 build targets.
Their server-copy SHA256 is
`8dedf75c8c3f7b4664e7d5e172122bc415ffc7c9ad648469fa9bb013cb49de3b`.
All gates/qualification fields remain false. Old disabled/frozen packages and
the closed FAIL were not changed.

Reproduce the12 unique focused portable tests:

```sh
cd tools
python3 -m unittest test_powerup_server_module_policy test_prepare_powerup_server_modules -v
```

Result12PASS/0skips in0.458s. This includes both independently imported pure
package graphs: paused binding, nine raw V3 observations/six canonical samples,
all-eight-slot direct V2 evidence, overlap hash rejection, identity/consistency
rejection, and execution of only the exact source-derived archival hook followed
by a deliberately failing binding. No native controller was imported. Synthetic
fixtures explicitly select fe4 when constructing model samples; this is not a
rewrite of native observations. The historical Original-only fixture files are
unchanged, and their general Original contract remains strict.

Actual missing-adapter RED was retained (initial fixture layout collected13
cases/18failures including duplicate inherited cases; four duplicates were
removed before the final9unique policy/archival cases). The separate builder
RED had3missing-builder failures. No error log was discarded or turned into
native evidence. The final graph tests use real pure helpers, not a simulated
controller/native PASS.

Private author verification and logs:
`/srv/tse-powerup-server-hash-v2-evidence-20261115/package-verification.json`,
SHA256 `861b5626a7e813f4e59ce1cb11454b3183c98daf7ac8b274d4e33a77c6d3b6a9`.
The colocated `audit-packages.py --output NEW_PRIVATE_PATH` reproduces the pin/
byte checks without a raw replay or native import. This is author verification,
not independent review. Root alone integrates, reviews, freezes, backs up and
decides a revised native case; there is no automatic retry or ON/OFF sequence.
