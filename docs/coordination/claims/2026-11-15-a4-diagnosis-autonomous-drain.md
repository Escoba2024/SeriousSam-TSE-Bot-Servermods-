# Autonomous method-only drain — isolated writer claim

Owner: `/root/a4_diagnosis`; worktree
`/srv/tse-build026-skulls-closed-audit-20261115`.

Exclusive scope: new `tools/first_state_autodrain_*`, their new tests, a new
disabled derivative builder, and this task's new plan/report/claim. Parent owns
integration and all runtime. No additional agents.

Existing monitor checkpoint 49dcfbb, old transport/session/JavaScript/validators,
Retail bindings, root worktree, frozen packages and C++ sources are outside this
claim. No runtime, Frida, display, build or network operation is authorized here.

Root accepted length-prefixed metadata (at most16KiB) followed by exact archived
raw JSON bytes (at most2MiB), without quoting/base64/parent reserialization.
Frida returns Python values: their first journal encoding is the byte origin;
these are not original Frida wire bytes. NaN/malformed input stays raw and FAIL.
