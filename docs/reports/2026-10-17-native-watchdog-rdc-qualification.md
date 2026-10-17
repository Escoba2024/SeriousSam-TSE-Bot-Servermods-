# Native TSE Retail 1.07 watchdog checks via RDC (17.10.2026)

**Scope: PASS, LIMITED** – two native one-bot Windows scenarios on SHADOW-P9FLKL5K. These are **not** long-term sync, 24/7, public-browser or fleet-scale acceptance.

## Source and isolation

- Branch: `codex/portable-qa-watchdog-20261017`, implementation `17ec155`, portable QA `9f9398a`.
- Isolated complete **physical copies** of the Retail-1.07 Dedicated, BotClient and vanilla Observer installed in another private Shadow worktree (`rdc-retail-harness-restore-20261017/.codex/retail`). No junction to original or production game installations.
- Qualified unchanged BotClient `GameMP.dll` SHA-256 **`61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`** verified before/after. The original non-test installation also still matched this hash after both runs.
- The unmodified Dedicated and vanilla Observer ran on local UDP gameplay/query ports 25600/25601. A separate one-client fleet config used `Scripts/LocalBotRelease.ini`, localPlayers=1, target population=2 (one regular observer + one bot), two human slots reserved.
- Fresh controller/watchdog state for each run; no existing client adopted; no external bot/other agent processes terminated.

## Actual tests

| Scenario | Whole harness wall time | Independent observed facts | Result |
| --- | ---: | --- | --- |
| Guardian after controller **hard exit** | 35.633 s | Vanilla observer joined; watchdog launched `TSE_Bot_Client_1`, BotDriver in new client log, fresh UDP `numplayers=2`; controller identity validated (PID, start UTC, EXE, commandline and guardian parent), then deliberately killed; guardian confirmed `controllerExited=true`, `cleanupPassed=true`, controller exit -1; bot was gone, observer and Dedicated remained alive until own harness cleanup. | **PASS, native one-bot hard-exit boundary** |
| Fresh watchdog **restart on same client install**, normal `stop.request` | 33.537 s | New watchdog state/lock reuse succeeded, same actual native bot/observer join and UDP 2-player status; graceful supervisor stop requested; watchdog exited 0, `controllerExited=true`, `cleanupPassed=true`; bot gone and observer/Dedicated survived until independent cleanup. | **PASS, native one-bot normal stop/restart** |

Both tests had **0 isolated game processes left** and **unchanged qualified DLL SHA-256** after teardown. Watchdog's internal `nativeAcceptance=false` remains **correct**, as its completion receipt attests guardian cleanup and not a broad game-release qualification.

## Reproducible private evidence

Git-ignored local evidence directory: `.codex/evidence/rdc-native-watchdog-20261017/` in the watchdog worktree. Includes `Run-WatchdogNative.ps1`, `Run-WatchdogNativeNormal.ps1`, fleet config, `result.json`, `normal-result.json`, per-run `controller.json` / `group-0.json` / `completed.json`, query/lifecycle `events.jsonl` and local game logs. These raw files and Retail binaries must **not** be pushed to GitHub. The first normal-run attempt failed before starting a game because its private archive filename already existed; the script's evidence filenames were separated, then the full normal-run probe passed.

## Open gates

- No native launch/ack race injection during the actual Retail game join; corresponding **portable** races are separately tested, not upgraded to native PASS here.
- No Controller-stop vs human join/leave race, 4- or 8-bot watchdog scaling, map change, full AI combat hour, reconnect endurance, Wine/Linux deployment, public 333networks/Vanilla browser listing or 24/7 proof.
- No mitigation of `Too many bad syncs` proven. Never disable native sync kicks to reinterpret a failing test as stability.
- Guardian crash, machine failure, OS metadata failure and malicious same-user state changes remain documented fail-closed boundaries.

This bounded native evidence extends `2026-10-17-external-watchdog.md`; it does not supersede the prior portable suite report or qualify a new GameMP DLL.
