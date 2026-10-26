# ssam.ai – M1 Cecil-P1 Retest: Repeatability and Evidence Limits

Date: 2026-10-26. All native raw logs are PRIVATE on the Hetzner host.
This is a review of measured native observations, **not a root-cause diagnosis**.

| Qualifier | Historic Cecil P1 (2026-10-25) | Controlled P1 ON (2026-10-26) |
|---|---|---|
| Four bot status | FAIL / SYNCBAD | PASS_LIMITED_SESSION_LIFECYCLE |
| Elapsed (seconds) | 97.928 | 152.434 |
| Peak simultaneous bots | 4 | 4 |
| Server SYNCBAD messages | 5 | 0 |
| Cecil P1 enabled | true | true |
| DLL SHA256 | 7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf | same |
| Original Retail observer | true | true |
| Red Station / low-memory renderer | true / true | true / true |
| Colors enabled / accelerated | false / false | false / false |
| Observer FPS cap | 5 | 5 |
| Qualifier script hash | different | different |

Comparison of saved five-file harness SHA256 inventories shows **only**
`qualify_bot_sessions.py` changed between the failed and newer P1 ON
run. Other four hashes match. New guard uses explicitly user-disabled
public-generation safety check. This does NOT establish the guard as the
cause of a missing/reappearing CRC mismatch.

The same newly pinned source and same four-identity configuration produced
a controlled 2026-10-26 P1 OFF run (152.380s, zero observed SYNCBAD).
The tool `tools/native_ab_comparability.py` reports only
`CONTROLLED_TOGGLE_RECEIPTS_ONLY`; it is not a native CRC comparator.

Historical other-candidate eight-bot observations:
- AI2 Build06: 8 peak, 465.69s PASS_LIMITED, 0 observed server SYNCBAD.
- Earlier AI2 eight-capacity candidate: peak 4, FAIL at 83.34s.
These runs used different GameMP DLL hashes from Cecil P1 and do not
qualify P1 eight-bot capacity or stability.

## Actual remaining acceptance blockers

1. Native authoritative applied-action, CRC input and engine-state producer
   must be demonstrated on original Retail 1.07, with source hash and
   session/player/connection epoch binding across client and server.
2. Reproduction of *first divergent simulation field* is not established.
   Five historical SYNCBAD messages alone cannot assign cause.
3. New combined M1–M4 native DLL/build does not exist.
4. M1 duration gates (1 bot >=3600s, 4 bots >=3600s,
   8 bots >=7200s), sync and unmodified external client, remain open.
5. M2/M3/M4 source prototypes and open PRs require careful integration
   after the qualified M1 baseline; no release claim is warranted.

## Non-destructive resume

- Public UDP 25600/25601 were verified closed; user explicitly shut
  public game server down. Do not restart automatically.
- Source-worktree and GitHub PR are aligned at commit
  `82a7973751ad0b3d54b2582e04fc6fa4dc21b8a8` before this report.
- Exact private test receipts remain under `/srv/tse-session-qualification-`
  with run IDs documented in the previous controlled A/B report.
- Continue from `docs/coordination/M1-M4-CONTINUATION.md`.
