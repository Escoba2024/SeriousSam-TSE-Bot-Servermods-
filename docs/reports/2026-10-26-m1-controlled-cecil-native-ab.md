# SSAM.AI – Controlled Cecil P1 Native Retail 1.07 A/B (2026-10-26)

Scope: Private NetNS under existing Hetzner; public game server user-disabled. This is a short native compatibility observation, NOT M1 acceptance.

Exact pinned source: PR73 guarded harness, Git tree 4ef97be3700deb19b9e536bfd3ac30a2c713d1f4.
DLL: 7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf
Input config SHA256 (same local source file for both runs, unchanged before/after): 13f2ddeeb372cc4ef03cf8a7f5454b3a7c2a8bd6e206ffa4cdea6052dd3c297f
Shared run arguments: preset redstation, port 27382, display :162, --duration 125, same build-manifest and original Retail observer.
Harness: five individually SHA256-pinned source files; hashes match across both receipts.
User explicitly authorized public server shutdown; private guards required status DISABLED_BY_USER and absence of host public processes/ports.

| Run | P1 flag | Native harness status | Elapsed s | Peak bots | Server SYNCBAD count | Outer guard |
|---|---|---|---:|---:|---:|---|
| master-four-off-20261026 | false | PASS_LIMITED_SESSION_LIFECYCLE | 152.38 | 4 | 0 | FINISHED |
| master-four-on-20261026 | true | PASS_LIMITED_SESSION_LIFECYCLE | 152.43 | 4 | 0 | FINISHED |

Important: Different host load and session start time cannot be eliminated by matching the script/config/DLL alone. Run outcome is not CRC-causation proof.
Historic Cecil P1 four-bot Retail run on 2026-10-25 failed with five SYNCBAD despite same DLL family. Root cause is still unresolved; cannot mark M1 COMPLETE.
No final one-hour/four-hour/eight-bot acceptance, no independent original Windows client, no sealed server/client action/state/CRC capture.
Raw game logs, player identities, Wine paths and private receipts remain on the authorized Hetzner host, not in Git.

Next: qualify a truly paired native applied-action/CRC/state producer tied to owner, game generation, engine tick and source DLL. Then reproduce under controlled variables, red-green fix and duration gates.
