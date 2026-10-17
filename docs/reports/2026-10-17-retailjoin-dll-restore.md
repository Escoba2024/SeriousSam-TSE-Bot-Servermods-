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
- An independent native Retail 1.07 test with an **isolated disposable BotClient installation** has **not** been run for this change. Release/native acceptance remains open until the restore is directly verified after a real candidate run and after a forced error.
- This does not fix `Too many bad syncs` or prove 24/7 / public masterserver behavior. It is a prerequisite safety improvement for future controlled differential tests.
- Temporary test evidence remains local, Git-ignored; never commit `.codex/` files, retail binaries or unredacted logs.
