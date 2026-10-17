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
