# Cecil four-bot A/B native admission: generation-safe public guard

Goal: close unsafe preflight paths before any same-DLL off/on Retail 1.07 A/B attempt. Current Build06 public result does not contain expected_names; old public health file has no generation binding and was last updated at 2026-10-25T11:33:40Z, while current MCP health is LIMITED with HEALTH_SOURCE_STALE, HEALTH_GENERATION_UNVERIFIED and SYNC_HISTORY_UNVERIFIED.

Approach: perform read-only, fail-closed checks on fresh public runtime metadata and pinned health provenance *before* creating a private test root or launching any native process. Refuse absence of a complete eight-name manifest, process generation mapping, explicit fresh healthy state, generation-bound sync-history coverage, foreign or additional game slots, and any stale data. Keep old protected live processes untouched. Store all test evidence without private raw logs or player identifiers. Future admission depends on a trustworthy current-generation producer, not silently reusing yesterday's old health file.

Choice: reject the current unsafe resource/admission preflight (rather than approximating roster from a game query or assuming old healthy snapshots remain valid). Only after monitors produce authoritative generation-bound data and guard tests pass may an isolated one-client control then a controlled four-bot same-DLL Cecil OFF/ON comparison be admitted.

Out of scope: production restart, gameplay/CRC patch, P1 feature deployment, source changes to the protected public runtime, disabling sync checks, virtual player spoofing and claiming stable release acceptance.
