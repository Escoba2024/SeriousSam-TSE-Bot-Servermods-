# Completion checkpoint: native startup guards, 2026-11-12

This checkpoint is progress, not milestone-A acceptance. Milestone B remains unstarted.

## Names

Reviewed names source was integrated at 9b7181e. Fresh stage v2 contains 2,011 captured inputs, 1,426 recursively added mutable inputs, exactly 51 intended changes, and 48 profiles. No prior source drift was found. Package c87374a9e163d9225e88335970de008cae427f22e8fad601431b27446fe73b1a passed its 7-source/6-dependency/2,063-data closure check. Native read-only preflight failed before any client stop or file change because five existing server-readiness helpers were not yet represented in the command allowlist. The original systemctl parser also loses repeated ExecStartPre entries. Both are being corrected with exact helper pins and complete command parsing; no guard is bypassed. All existing live clients remain running.

## A4 startup trial and exact recovery

Build015 reduced-render trial a4-reset015-lowrender-20261112-082028 failed before observation because the renderer mode log was checked before the renderer initialized. The initial archived Vanilla log has no mode line; the subsequently closed log contains exactly `320x240xdesktop (window)`. The original cleanup's early window message did not close the loading Vanilla client; the original FAIL report and its incomplete-cleanup errors are retained. Root separately verified the recorded PID/start and issued a second normal window close after startup, verified own process/helper quiescence, closed the exact display invocation, and restored/rehashed all 648 recorded files with metadata. The independent recovery receipt has no errors. No force kill, production change or retrospective trial acceptance occurred.

A separate gate-false correction now waits up to 25 seconds within the existing transition deadline, validates the same native identity before and after each read, and still rejects wrong or repeated completed mode lines. Six meaningful late-start/generation/timeout regressions failed before the fix; all 100 offline tests then passed. Native re-run awaits review.

## A1 diagnostics

Optional read-only reader commit a69ab11 was integrated exactly as ddd65b7; five source/report files match author blobs. Independent review confirms the bounded diagnostic scope and test evidence, with two remaining private-package fixes: explicit transitive normal-close dependency precheck and strict success-side two-second acknowledgement/settling deadlines. No native A1 diagnostic has run.

## Open acceptance

A1 first processed post-respawn hit evidence, complete final-build difficulty comparisons, supported map/reset evidence, still-valid stability gates, final Dev/public deployment and verified complete private runtime backup remain open. Build015 remains unqualified; B must not start.
