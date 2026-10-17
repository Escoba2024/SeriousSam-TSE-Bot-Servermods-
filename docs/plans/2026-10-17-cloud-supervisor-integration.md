# Cloud integration qualification — 2026-10-17

Scope: isolated candidate combining PR #10 (`9d77adf99bb13fb3bf0ec981e3bf3288a3104680`) and PR #11 (`c7bb2cc407524ada82310540331707c092df8969`, including PR #8). No main merge, runtime access, game launches, or release/DLL changes. Remote branches and PR heads freshly fetched; main `39662e3757154540c1220fef0ebfcba67f5291eb`.

1. Combine the two exact heads locally without committing; inspect shared supervisor hunks.
2. Run the existing Publication runner unchanged. Preserve actual FAIL/exit evidence and compare known platform boundaries.
3. If proven necessary, update only explicit platform classification for added Windows integration suites; preserve full Windows execution and all assertions. Do not relax ownership/time guards or claim full mailbox coverage under Linux.
4. Re-run positive Publication and failure propagation checks. Commit reviewed combined code and runner change; validate that exact commit in a separate fresh checkout.
5. Independent reviewer checks semantic integration and new platform classifications. Address actionable findings before publication.
6. Publish a separate draft integration PR against PR #10 with sanitized SHA-bound matrix and concrete Windows/native handoff. Keep all source PRs open; do not merge remotely.

Expected safety checks: readiness recovered after deadline, malformed UDP, four-player capacity/readiness transitions, no direct launch/stop with guardian, owner/pinned-handle cleanup, live-controller hold, explicit skips. Windows/PS5.1 mailbox/hard-exit integration and native game qualification remain outside this host.
