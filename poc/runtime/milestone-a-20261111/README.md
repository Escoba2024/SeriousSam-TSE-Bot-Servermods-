# A1 session-boundary configuration

These six `1_begin.ini` files are staged copies of the actual six server scripts on 2026-11-11. `manifest.json` pins their source and proposed bytes. They preserve map, unlimited ammo, game difficulty, flower blood/no-gibs and Dev's separately authorized selective powerup flag. They explicitly set `gam_tmSpawnInvulnerability=0` immediately before session creation and emit a conditional shell-value witness. They are not a Cecil-map whitelist or complete milestone-A release.

The inspected Dev source (`Game.cpp` in server build001, lines1025–1028) loads PersistentSymbols only when `!_bDedicatedServer`. Thus the zero in `Scripts/PersistentSymbols.ini` did not set the dedicated server variable. Read-only process memory at the matching linker-map RVA `0x5b120`, pinned server DLL `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0`, was **3.0** before correction. No memory was written. This identifies the Dev cause; do not treat the SDK source alone as proof of an original Retail implementation.

Startup logs show Game startup, Dedicated startup, `BotTest/init.ini`, then `BotTest/1_begin.ini`. Current `1_end.ini` has no map rotation. Every future rotation's corresponding `*_begin.ini` must preserve this last assignment. Keep the persistent zero as well, but never rely on that client-oriented file as the server acceptance check.

Runtime application is recorded separately in the progress report and private rollout receipt, not inferred from these files. The conditional startup marker and live variable read prove the shell setting. Immediate post-respawn damage/death, bot/Vanilla behavior and map-switch checks are separate gates and remain open until explicitly reported.
