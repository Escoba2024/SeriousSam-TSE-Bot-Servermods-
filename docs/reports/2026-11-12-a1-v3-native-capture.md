# A1 V3 native rotation capture and remaining acceptance

Recorded UTC: 2026-11-12T09:16:31.484057+00:00

## Observed result

The single root-owned V3 run `a1-input-diagnostics-completion-v3-20261112-090901` completed with `PASS_LIMITED_ROTATION_CAPTURE_REVIEW_REQUIRED`, no controller errors and `completed_diagnostic_pair=true`. All three native roles and both displays closed normally. All 673 tracked fixture files were restored; the retained closed logs passed their error checks. This is a short diagnostic result, not A1 release acceptance.

The four ordinary input phases were exactly look-right, forward, look-left, forward. Both received cumulative yaw gains were -0.25 degrees/pixel. The actual body gains were -0.25000635782877606 and -0.2499974568684896 degrees/pixel; the return error was 0.0001068115234375 degrees. Fresh local/server cumulative responses and relative-view transfer were observed. Of 38 paired read attempts, three explicit consistency failures were retained and discarded within the reviewed bounded reacquisition policy. No input was repeated. These sparse observations do not prove exactly-once engine input consumption.

The observed diagnostic lasted 3.3817317851353437 seconds. Maximum sampled aggregate CPU was 66.25%, minimum available RAM was 2465660928 bytes and minimum disk free was 17528061952 bytes. A 24.920849333982915-second host sampling gap covers setup; `budget_pass_claim=false` and no complete-window stability claim is made. No route, control shot, foreign hit or first processed post-respawn damage was attempted. All such qualification flags remain false.

## Provenance

- Reviewed disabled V3 manifest: `0f15a0cb6e82ebfe8694ddf8cc007c74a5318f42bae2fc984138ffb460029e26`.
- Root frozen manifest: `3ec2f6c80d68c064a1543122cf1c3c4b0de73276932258ac11044961e7a0774d`.
- Root frozen controller: `2f268d074069f8157743d9b3579ed5543dad26078d348b9c3205d9096c72b77d`.
- Author docs commit: `0e12f645cee518aeb249043b67d09f971ce7c34e`.
- Integrated root commit before this report: `3b202b4708301f2686ed206e0504d7972fc2f825`.

The old V2 consistency-read failure and original asymmetric-body endpoint failure remain unchanged. V3 explains that a complete acknowledged pair can be captured under the unchanged bounds; it does not retrospectively turn an earlier failed run into a pass.

## Next work

Use the captured acknowledgement/settling boundaries when preparing bounded ordinary movement and firing. Review any added route or shot phase separately and retain actual native evidence. A1 requires repeated valid damage from the first processed post-respawn state for bot and available Original client, including restart/map transition; that acceptance remains open. Existing screening of 17 passive damage windows found zero eligible same-spawn-tick health decreases among 1886 recorded events, so those windows cannot close A1.
