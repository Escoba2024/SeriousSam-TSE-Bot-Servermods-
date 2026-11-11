# Native supply qualification and retained item diagnosis, 9 November 2026

Status: **NOT QUALIFIED**. These observations do not authorize production release.

Build016 is published source `c6662dac40a4d344667222f7cb6abd0b8eb5341c`, tree `f264127e4d26883cc94021b5dadd759a85b5dff5`, DLL `ea1b9d3b19424aa7a5c4d5fe06864afd51084d0d63d73486788ecc00a2d5c47f`. Fifteen native Win32 translation units and linking succeeded. The ordinary search limits and original directed navigation data were preserved.

Ten predeclared 60-second single-bot windows completed under original Retail 1.07 Dedicated/Engine/Entities in a private loopback-only Wine namespace. Each fresh BotClient was closed normally, its slot drained, then the dedicated closed normally. No enemy, cheat, authoritative entity write or forced process termination was used. Full startup-to-exit logs and process/map/hash-pinned epochs remain private.

The first useful weapon ownership gain after the exact native spawn event occurred after 8.40, 3.35, 3.45, 3.30, 3.90, 3.90, 2.60, 2.60, 2.60 and 3.80 seconds. Median3.40s and nearest-rank P95 8.40s meet the frozen latency bounds. This does not close the separate weapon-goal requirement: only **3 of the first10 actual weapon selections** have corresponding ownership gains, below the required9. Unavailable, failed and repeated selections remain in chronological order; none were replaced. Inventory gains near the selected item corroborate acquisitions; no exact ReceiveItem hook was installed. No native errors were detected in the complete audit inputs.

The source also applied acquisition distance/ranking to every retained ordinary item. A separate diagnostic-only flat overlay of Build016 added rejection-stage logging, with no eligibility, movement or action changes. It built DLL `b43833876c2ff6927ecd827ed056ab3b86940ade194728b81385807ae441123b`. The manifest records the base published tree and the actual overlay/source hashes; the diagnostic DLL is **not an unmodified build of that tree** and is not a release candidate.

One diagnostic 60-second native window reproduced a cannon goal selected at tick1019 and rejected at tick1026. The typed snapshot still succeeded; the item was not picked, usable/owned masks were unchanged, no close enemy existed, and weighted acquisition distance was16.3763m against16m. The logged failure stage was retention_policy. This establishes an actual acquisition-distance cancellation. It does not prove that both earlier flamer cancellations had this cause; those historical rows lack rejection-stage evidence. The same diagnostic window actually collected its flamer goal.

Next: share strict typed/item-needed rules while separating acquisition radius, visibility admission and ranking from retained-goal continuation. Preserve real item availability, generation, allowed/usable weapon checks, close-threat arbitration and the existing attempt deadline. Add portable and actual bridge regressions, build a new hash, then repeat all final native gates. No Build016 duration, resource, recovery or fleet qualification is claimed.

Build016 also passed limited eight-bot Hole300s (36 deaths; maximum unexplained stationary interval4.021s) and Trouble300s (68 deaths;2.019s), without detected sync/runtime errors. These are short functional observations, not the required duration gates. All five production instances retain their prior DLLs; the public development instance remains on Build013 pending qualification.

Private audit artifact SHA256: `c3a8d4aab6257029947d274abedb137084af5447e35c1a3523afacd08048290a`.
Predeclared protocol SHA256: `aa3861f660cd8c06fd1ff30a5c391c3c0569cee3ba54112c896558703b467247`.
Diagnostic complete log SHA256: `0009fd2994cbb77ccb5f7c4b50dab0cd93a44c80d699b5c2ac2645edbcd3976f`.

Implementation update: shared `CecilRetainItem` now keeps strict item-needed rules, with initial acquisition policy unchanged. A close non-health threat explicitly yields action ownership to Human combat without renewing the item deadline. Both concrete regressions first failed and then passed;187 actual bridge checks with ASan/UBSan and pinned SDK USE32, all Cecil C++ suites, Driver guards and166 tool tests pass. Focused independent review reports no remaining blocker. Native Build018 qualification has not yet started.
