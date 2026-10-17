# Retail 1.07 Test-RetailJoin – reversible DLL installation (17.10.2026)

## Problem

The previous `poc/scripts/Test-RetailJoin.ps1` backed up
`TSE-BotClient/Bin/GameMP.dll` into the private evidence directory as
`GameMP-before.dll`, but never restored the installed original.
This left the candidate DLL active even after an unsuccessful or successful test.

## Isolated change

- Record the original SHA-256 and validate the private backup before attempting candidate installation.
- Copy the candidate only **inside** the main `try`, so its `finally` is reached even on a failed copy.
- After stopping only the processes started by this test and restoring any capture INI files, copy the backup back to the BotClient installation and verify the destination SHA-256.
- Treat failed backup integrity, copy, or post-restore verification as a **failure**, never as a successful native result.
- Add a pure offline fixture test under `Test-RetailJoinState.Tests.ps1`: original file recovered; corrupted backup rejected before changing active file.

No original Retail game binaries or user installations were modified by developing this change. The Git worktree is separate from `main`.

## Test and acceptance boundaries

- Offline fixture test: `poc/scripts/Test-RetailJoinState.Tests.ps1`, PASSED on Shadow Windows PowerShell 5.1.
- The publication test runner now uses `Start-Process` to capture Python stdout and stderr as separate files and checks Python's actual exit code; this avoids Windows PowerShell 5.1 treating a successful `unittest` progress message on stderr as an execution failure. No native game fixtures are run by this runner.
- **Native isolated test now completed** on Shadow using private full file copies of Retail server, BotClient and vanilla observer (no junctions or shared game profiles):
  - **Different Retail GameMP.dll candidate**, SHA-256 `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208`: 25.255 s client/observer joined and CRC accepted 2 times, but test gate FAILED (no bot driver; old module detection/name assertions). After the failed run the qualified DLL SHA-256 `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` was **restored and verified**; 0 test processes remained. This is real evidence that the restore works after a candidate with **different file bytes**, not a runtime qualification of that original DLL as a bot.
  - **Qualified bot candidate**, same `61DC27E0...` SHA-256: initial harness incorrectly said FAIL despite CRC and join. Diagnosed two independent evidence bugs: old hard-coded observer name and x64 PowerShell enumerating only WOW64 wrapper modules for the x86 client.
  - **Corrected harness**, same qualified candidate: 25.019 s, `GameMP.dll` loaded=true via 32-bit PowerShell, client/server/vanilla observer joined=true, observer saw configured name `TSE_Bot_Client_1`, CRC accepted twice, `testPassed=true`, restore SHA-256 verified, 0 remaining own processes. No launcher flags or bot DLL changed.
  - New fixture verifies x86 module discovery against an owned 32-bit PowerShell process and rejects a nonexistent module; `-ExpectedBotName` is explicit and regex-escaped (default retains legacy `TSE_Bot_PoC`).
- `Test-NativeJoined` now rejects a previously successful join when a **later** explicit disconnect, timeout or session stop was logged. It accepts a genuinely later successful rejoin. This closes a false-positive gate where `Disconnected: Too many bad syncs` could otherwise be hidden by historical `joined`. Merely observing an isolated `SYNCBAD` warning is not automatically classified as a permanent disconnect; native sync-kick auditing remains separate.
- Private test evidence only: `.codex/evidence/rdc-native-restore-20261017/`; logs and copied Retail binaries were not staged or published.
- **Scope limit:** the short tests do not establish long-term sync stability, bot AI movement/weapon quality, 333networks listing, external Vanilla-Browser join or 24/7 acceptance. The harness has not been tested against a deliberately corrupted candidate/forced crash after DLL loading; the different-binary failed-gate restore was verified.
- This does not fix `Too many bad syncs` or prove 24/7 / public masterserver behavior. It is a prerequisite safety improvement for future controlled differential tests.
- Temporary test evidence remains local, Git-ignored; never commit `.codex/` files, retail binaries or unredacted logs.

## A05 source-only follow-up: exact observer bot identity (17.10.2026)

**Authorization:** A00 granted the A05 claim in GitHub Issue #18 (source-only, expires 2026-10-17T06:30:00+02:00). Writable scope: this report, `poc/scripts/Test-RetailJoin.ps1`, and `poc/scripts/Test-RetailJoinState.Tests.ps1`. `SHADOW_RETAIL` and `SHADOW_GAME_FILES` remain **BLOCKED**. No native process or retail installation was used or changed in this follow-up; no UDP-parser or `tools/Test-Publication.ps1` source change.

### Reproduction and fix

- Read-only original Retail 1.07 observer evidence contained a formatted event `^oTSE_Bot_Client_1^r joined`. Previous `observerSawBotJoin` used an unanchored substring around `ExpectedBotName`: an unrelated player named `ImpostorTSE_Bot_Client_1_Else` could cause a false PASS. An empty expected name could match any join.
- New `Test-ObserverSawExactBotJoin` extracts complete `joined` lines, removes only recognized TSE presentation codes (`^cRRGGBB`, `^fN`, `^o`, `^i`, `^r`), and compares the resulting *whole visible name* to the configured expected name using ordinal string equality. Empty/whitespace names are rejected; the script parameter also rejects null/empty.
- Regression exercises the *actual observer result expression* from the script AST: real colored join, plain exact join, multiple formatting codes (positive); impostor substring, appended name, unrelated join (negative); and an empty-name rejection. Historical native joined/disconnect, 32-bit module-enumeration, SHA256 backup-restore fixtures remain intact.
- RED before fix: Windows PowerShell fixture exited with `Observer exact-identity gate wrong for impostor substring`. This first interactive RED invocation was not independently transcript-logged; its reproduction is directly encoded in the committed fixture.
- GREEN after fix: Windows PowerShell 5.1.22621.4249 on Shadow (Windows NT 10.0.22621.0), `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File poc\scripts\Test-RetailJoinState.Tests.ps1`, exit 0. Private transcript: `.codex/evidence/a05-observer-exact-name-20261017/targeted-test-transcript.log` (timestamp 2026-10-17T01:27:43Z). No retail binary touched, no shared game PID stopped.
- Full offline runner initially attempted with `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\Test-Publication.ps1 -Evidence .codex/evidence/a05-observer-exact-name-20261017/full-publication`; **FAILED_ENV**, because the RDC shell resolved only the Windows Store alias `python.exe` (exit 9009). This was an interpreter resolution problem, not an assertion failure. Logs: `.codex/evidence/a05-observer-exact-name-20261017/full-publication/`. Python 3.12.10 was found at `C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe`; rerun with explicit `-Python` path documented separately below.

### Additional reproducible offline evidence

| Version / environment | Command | Result | Private log |
|---|---|---|---|
| Retail 1.07 observer capture, Shadow Windows PowerShell 5.1.22621.4249 | `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .codex/evidence/a05-observer-exact-name-20261017/run-archived-observer-replay.ps1` | **PASS**, exit 0: target `TSE_Bot_Client_1` true; unrelated impostor false; original observer logfile SHA256 `9FCA038A33F2AF67E5FE6E21844B7CD8580FAAFFC444F80E926D1CB220E46392` | `.codex/evidence/a05-observer-exact-name-20261017/archived-retail-observer-replay.log` |
| Shadow Windows PowerShell 5.1.22621.4249 + Python 3.12.10, **offline only** | `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools/Test-Publication.ps1 -Evidence .codex/evidence/a05-observer-exact-name-20261017/full-publication-python312 -Python C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe` | **PASS**, exit 0: 19 PowerShell suites, 44 Python fixture tests, 13 source hashes, `nativeRuntimeStarted=false` | `.codex/evidence/a05-observer-exact-name-20261017/full-publication-python312/result.json` and suite-specific logs |

The archived observer log contains original native Retail 1.07 evidence but was only **read**, not used to launch a new game process. All private evidence stays ignored and uncommitted.

**Acceptance boundary:** The exact visible name in observer text is verified by fixture; a server/player identity key is not established by name equality alone. Previous ~25-second native Retail join/restore evidence remains historical, not a new native pass. Long-running SYNCBAD, gameplay action capture, public browser listing and 24/7 remain outside this patch.
