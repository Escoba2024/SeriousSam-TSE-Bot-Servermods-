# Original keyboard qualification — offline preparation

This is an isolated, disabled diagnostic fork. No new Original session, X server,
Frida attachment, XTest event or game process has been started by its author.
The historical mouse calibration failures remain failures. A pure policy replay
is not evidence that a real Original client received a key or acknowledged it.

The parent is the complete `/srv/tse-a1-xres-lifecycle-root-frozen-20261115`
package, manifest SHA256
`e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`.
The derivative retains the existing Original binaries, native readers, process
and life guards, normal closes and sealed transaction. The four qualified Core
files are copied byte for byte. This case does not arm Frida or RECORD and makes
no wire observation claim.

The only input program is six ordinary 0.1-second actions: yaw left, Forward,
yaw right, Forward, pitch up and pitch down. J/L/I/K replace exactly the four
original profile Key1 assignments; W remains the existing Forward key. The two
Forward actions are the historical body-alignment operations. They are required
before comparing body yaw with native action/view acknowledgements. No mouse,
route, pickup, weapon selection or fire operation belongs to this case.

Existing limits stay unchanged: ACK 2 seconds, EPS 0.001, input through release
0.35 seconds, shared preparation 85 seconds, runner 90 seconds, 48 actions and
96 native attempts. The real test may fail because ordinary keyboard rotation
is too coarse to return to the existing geometry limits; no pixel gain is
inferred from a key duration.

## Offline implementation checkpoint

Task 1 is commit `1b81c4d`: the narrow profile/key adapter and six portable tests.
Task 2 is commit `8e993ab`: the six-action native-angle policy and six pure replay
tests. Both tasks first failed because their new module did not exist, then
passed their targeted tests. These tests use fake C functions or synthetic
native frames and confer no runtime qualification.

Task 3 first produced two missing-builder failures. Its two structural builder
checks are now green. During Root's exclusive Trouble window only source/test
text was edited; execution resumed after Root's explicit CLOSED and restore
receipt. The final targeted run passed 20 tests in 1.210 seconds, without skips.

Root's static release finding was reproduced as three RED subcases: metadata
rejection after native keyup withheld XSync; first-counter and reservation errors
withheld native keyup. The own release path now invokes the original C keyup
exactly once, flushes it, and checks the actual keymap even if metadata fails.
All failures remain sticky; the original shared proxy and Down path are
unchanged. Successful and failed releases retain native-return, flush and bitmap
receipts. These control-flow tests use a fake C function which buffers state
until XSync, so an immediate fake state change cannot substitute for a flush.

A separately observed RED covered the misleading completed-action count. The
policy now distinguishes admissions, invoked step attempts, verified releases
and native acknowledgements. Failed admitted inputs cannot count as a completed
program. Commit `cd2d7ec` contains this correction and the release correction.

Further observed REDs covered missing persisted native/keymap evidence,
malformed direction types, reversed request counters and a failed XQueryKeymap
return. The completion auditor requires all twelve accepted native key calls,
their real bounded intervals, exact Down/Up bitmaps and other-key neutrality,
six native acknowledgements and normal closes/restoration. These are diagnostic
completion conditions, not A1 acceptance. A first synthetic receipt incorrectly
hard-coded `.11` rather than the actual floating-point `finished-start`; that
fixture failure is retained, and the fixture was corrected without changing any
production tolerance.

The recorder-free path also required the public XNextRequest ABI declaration
which the old `controller_gc()` supplied. A missing-declaration RED preceded
the explicit `void*` argument and unsigned-long return declaration. Declaring it
makes no native call. Commit `348b744` contains these evidence and ABI additions.

Private 0600 logs are in `/srv/tse-a1-keyboard-evidence-20261115`:

| Log | SHA256 |
| --- | --- |
| red-task1-missing-keyboard-input.log | 6bcb1479d537d262f13b49fc057396f3bdd1d845cd2e189438394ad7cb89df0f |
| green-task1-first.log | cacd0c9f949ef911867de392fb7c2f2e64e1e6723013dbbf2bdc147987b2f433 |
| red-task2-keyboard-geometry.log | 6a84c66267cc124e1b71882682d1b15aa619a9da0aca6f0c81cea20a918cc0b2 |
| green-task2-first.log | 256610a61808607d4ddd4d06b0c40510954136fdf91f2736fbf66d88cdd15f37 |
| red-task3-disabled-builder.log | fe4e9bcb9fff18808ad4a5e81ef30a92a2465e60750b8f7960f6d83f79c1ffca |

Root then found a real disabled-status metadata error: the copied collector
manifest retained `runtime_reviewed=True` although its code gate was False.
The new regression failed on that exact field, then both builder cases passed
after setting only the collector manifest field to False. No collector was
executed. The original package and receipt remain unchanged as the superseded
checkpoint; their limitation is explicitly recorded in the new receipt.

Final corrected private disabled package:
`/srv/tse-a1-keyboard-qualification-gates-disabled-20261115`.

| Artifact | SHA256 |
| --- | --- |
| source-manifest.json | a14749e6a55f7001899f2a961fab3c15ff6c4fb7032ee121603d31e0972f3951 |
| run_dual.py | c8e6855e63509c84244c1d6c70bd3b8f6816cec0ee5429c23398d4c1e020fdae |
| a1_keyboard_input.py | b8f1ec83ea86a50c57dd66bbca8b18bc4c3ddab9a9b32f239a4bceb5fc34f514 |
| a1_keyboard_geometry.py | 48a9c444c298f6070461951ad88a9e7899e0131751ffb22837caac364d62adf7 |
| prepare_a1_keyboard_qualification.py | ff709256468900f6eee31ca9c0eb23d472fa47abd408b7a09a15f2244c721e35 |
| green-keyboard-20-focused.log | c4c401db15ed76323b4953317d4c281281f566ea8035334158c58cb33bd58229 |
| completion-proof-first-followup.log (retained fixture failure) | 67dd088638e03be9ae6e62a322f164a842536a54a75e5bf36328382638bf0ee2 |
| red-disabled-collector-manifest.log | 521c2485d4a2c7634c1cbdd6fa916134ee9838f42af44593879f0cce3b788c42 |
| green-disabled-collector-manifest.log | 0c07c36c72b96f836be347acce9ab7670d83bfaaf666ec394c2b59c880ab32d3 |
| offline-preparation-gates-final.json | 4f87e820860eef86bbd091746e75cdd571c85fd3d69a56f6a46e752abba4d205 |

All 107 runtime, 90 diagnostic-source and 14 collector pins were freshly checked.
All twelve selected inherited input/identity/close/restore functions have equal
ASTs, and all four qualified Core files remain byte-identical. Runtime gates are
disabled, including both main and collector manifest fields. The complete
private offline receipt lists every retained RED/GREEN
log, its SHA256 and 0600 mode; no output was retroactively changed into a pass.

Reproduce offline from the worktree's `tools` directory with:

```
python3 -m unittest -v test_a1_keyboard_input.KeyboardInput test_a1_keyboard_geometry.KeyboardGeometry test_prepare_a1_keyboard_qualification.KeyboardPackage
```

The builder requires a fresh path:

```
python3 tools/prepare_a1_keyboard_qualification.py --destination /srv/NEW-OWN-DISABLED-KEYBOARD-PACKAGE
```

Root alone reviews, integrates, freezes and decides the single native case.
No keyboard delivery, real ACK, native precision or damage gate is yet passed.
