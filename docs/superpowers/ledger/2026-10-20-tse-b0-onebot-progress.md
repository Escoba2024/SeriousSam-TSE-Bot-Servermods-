# B0 ledger — plan: docs/superpowers/plans/2026-10-20-tse-b0-onebot.md

2026-10-20T03:30Z: Initialized isolated own branch agent/TSE-main/20261020-b0-onebot from d8fba75 in /srv/tse-main-agent-20261019. The old tmux Codex CLI was idle at goal prompt; no parallel agent/dispatcher started. Shadow via RDC online, no observed SeriousSam or DedicatedServer process. Existing private Retail original paired V1-20261019T233521Z known matched from previous validated host evidence, not evidence under bot load. B0 pending native execution.

Preflight: No shared interfaces beyond retained 2026-10-19 plan/ledger and private source paths. Safety: source GameMP never altered; every new process owned; only private test files changed and restored. No new success asserted.

## Native B0.2 — 20.10.2026, 03:38:55–03:40:55 UTC
Shadow native Retail x86; exclusively owned localhost processes: 1 original Dedicated Server, 1 original unmodified Vanilla observer, 1 BotClient with qualified GameMP.dll SHA256 61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9. Separate bot clone and zero-movement/zero-yaw/zero-fire profile SHA256 6068F2A9C01A44C1D9E9BEE390DD394D094B84DD6B66F3C44829FE28F59FBBC6. Source DLL unmodified.

Run ID B0-20261020T033855Z; archived privately on Shadow at .codex/evidence/p0-pair-20261019-main/B0-20261020T033855Z. Independently observed host runner result: process exit 0; after bot join, observed 90.5 seconds; dedicated reports 2 successful joins and 2 CRC checks; Vanilla client sees bot joining; BotDriver identifies player as bot-driven, 90 action log entries. Observed stationary positions/heading and fire=0. Server+Vanilla+Bot native logs: SYNCBAD=0, unexpected exits=0. Bot/Vanilla closed normally, owned Dedicated required FORCE_FALLBACK, both modified clone configs hash-restored; result reports no cleanup errors, local test port closed. This is B0.2 short native RUN PASS, not a continuous snapshot or 60-minute pass.

## Fresh Hetzner offline regression (20.10.2026)
make -C poc/botcore test: 6 C++ suites exit 0. Portable Python tests: 25 + 9 + 10 passed, each exit 0. Offline pair validator: 30/30 passed exit 0. Source provenance: 13 hashes passed exit 0. No retail engine DLL changed. Targeted scripts only; private combat fixture not discovered.

## Native B0.3
Dedicated + Vanilla + Bot capture variant prepared in new independent isolated Server/Client clones .codex/retail/P0-B0-CAP-20261020. Bot qualified clone retained. Original native V1 x86 guarded flag procedure copied to private, adapted to require both joins, two CRCs, bot driver evidence and owned cleanup. Test-file PowerShell ParseFile: syntax PASS 3304 tokens; no source DLL/engine modification. Capture RUN and independent comparator outcome pending.

### Capture Attempt 1 (under Bot load)
B0CAP-20261020T034418Z, Shadow x64 launcher: verified bot join but ended early with Server:ENGINE_MODULE_COUNT before any flag write. Process cleanup Bot/Vanilla/Server: normal, error is x64 PowerShell WOW64 module introspection and not native sync evidence. No engine/game binary changes.

### Capture Attempt 2 (under Bot load)
B0CAP-20261020T034508Z, Shadow SysWOW64 x86 PowerShell: validated bot join; guarded server/client original Engine.dll dump flag writes separated by 0.791 ms. Two genuine raw native dumps (1833/1831 bytes) archived, SHA256 server 6E4A875C69CB9CCD95734E262F9700C6687A2226563CD29AE389905E05F5D7E4; client 5182746EFA00F622B22F73C334158596BF848270A4BBAFC8398B191A26FEFFE9. Comparator from separate pinned PR#21 source reports UNALIGNED: server Level 1 / Sequence 336 / Tick 16.65 / CRC CBC1099F; client Level 1 / Sequence 337 / Tick 16.7 / CRC 35A5F32E. No valid state-line compare; CRC mismatch between different ticks is NOT a native sync defect proof. All three owned processes closed normally, no script errors. This attempt cannot pass native sync pairing.

Original archived files hash-matched against owned-clone duplicated dumps before those duplicates alone were cleared; archive preserved. One further bounded capture attempt initiated without changing application code. Preserve no invented alignment.

### Capture Attempt 3 — first proven aligned native Bot-load pair (20.10.2026)
Run ID B0CAP-20261020T034700Z, x86 PowerShell; instrumented *original registered* Engine dump-flag on owned isolated Retail 1.07 Dedicated+Vanilla after bot join, no patch to any on-disk Engine/GameMP. Process IDs private in run archive. Trigger gap 0.760 ms. Server and client native original raw dump each 1831 bytes, each SHA256 9FD6F7F75F84860CF7EDD84C10217494363A5A283A2A75D8550F568918566C3A, archived privately in this run directory.

Pinned PR#21 comparator executed again freshly via Shadow Python 3.12, EXIT 0, MATCHING_SNAPSHOT / can_compare true: Level 1, Sequence 338, Game Tick 16.75, CRC 5279EC1D on BOTH server and vanilla client, 48 state lines on EACH, 0 differences. This is the first confirmed **matched observation under one live Bot**; exactly one paired observed sample, no continuous tick coverage and no first divergent tick determination, no proof of general error-free synchronization.

Independent private after-test verifier Exit 0: native server joins=2; server CRC check OK=2; BotDriver action tick log messages=15; count SYNCBAD/Too many bad syncs across the three archived native logs =0. Three own processes all ClosedMainWindow normally (bot/vanilla/dedicated), remaining game processes=0, test UDP ports occupied=0, eight original Server/Client module SHA256 all as expected, original BotClient SHA256 pinned 61DC27E0... remains unchanged, capture runner error count=0. Do not publish original player details, raw logs or the Retail DLLs. The raw script generic status V1_TWO_NATIVE_DUMPS_CREATED_UNALIGNED_UNCHECKED is only a dump-created status **before** the separately executed comparator; definitive paired comparison was MATCHING_SNAPSHOT exit 0.

Final B0.3 assessment: B0.3 ALIGNED_SINGLE_BOT_SNAPSHOT_PASS (narrow sampled observation), no reproduced sync defect and no justified code patch. Previous single bot no-dump 90.5s run B0.2 PASS. B0.4 remains OPEN: no new 2/4/8 bot duration test, no >=60min 8bot test, no 60min fresh sustained one-bot verification. Existing historical ~61min 8-bot report is not interchangeable with this isolated qualifying build/profile and captures. No 24/7/WAN release decision.

No isolated game processes remain active. No new Git source or qualified DLL changes. Two authored plan/ledger files only; author self-review, not an independent audit.

## B0.4 2-Bot short native control — 20.10.2026, 03:53:52–03:55:51 UTC
Private Shadow run B2-20261020T035352Z: original Retail Dedicated and Vanilla observer with two stationary 61DC-qualified BotClient copies, each native player0 GUID independently verified *different* by SHA256 (GUID contents remain private). Runner Exit 0 / status B0_TWOBOT_SHORT_LOG_CONTROL_PASS. After second bot joined, observed 90.5 seconds; native server logs show 3 joins / 3 CRC check OK, Vanilla log observed both bot joins; no unexpected game exits. Independently read archived four native logs: each bot had **91** BotDriver action ticks, overall 0 SYNCBAD/Too many bad syncs. Two Bot clients and Vanilla normal CloseMainWindow; Dedicated FORCE_FALLBACK after graceful close attempt; modified test clone configs restored, no runtime remains and ports 25640/25641 free, result errors=0. Original BotClient/GameMP sources never edited. Independent Verify-B0-TwoBots.ps1 reports same measurements, separate from generic runner counters.

Private test harness quality issue caught during audit: combined botTickLogs in original runner counted first bot's fresh samples plus only a stale pre-observation second-bot sample, because bt2 was not refreshed during the monitoring loop. This did not change native runtime nor the saved logs; independently verified both full logs postrun. Private harness now fixes bt2 refresh and explicit sum parentheses and passes PowerShell parser. A short additional regression run to validate this harness correction is distinct from the prior B2 native result.

Scope of B0.4 PASS: **2 Bots / 90.5 seconds**, without native paired snapshot. 4- and 8-bot scaling, >=60min soak, persistent 24/7 and join/leave stability gates are OPEN, not PASS. No valid claim of 60-minute stability is made here.

### 2-Bot harness repeat failure — native transport join, not sync (20.10.2026 03:57:54 UTC)
B2-20261020T035754Z was a 20s attempted regression after a local harness counter fix; it **FAILED BEFORE** the observation window: only 2 of 3 expected regular joins, 2 CRC OK. The second BotClient native log explicitly reports **"Cannot join game: Client: Timeout receiving UDP port"**; no third server CRC or bot-joined event. This is a real B0.4 **REPRODUCIBILITY FAILURE** (not a CRC mismatch or simulation divergence). All owned processes closed and test configs restored; no running game processes assumed. Prior B2 90.5s success remains a discrete valid observation, NOT a reliable repeated pass.

Root-cause hypothesis: starting both clients near-simultaneously races the Retail localhost handshake/UDP port negotiation. No evidence yet of which network substage or code path caused it. Separate harness fix introduced strict staged joins: second bot launched only after first server/Vanilla CRC+join and BotDriver recognition, plus a short spacing; on every loop the second bot log is now freshly read, and counters are independently combined. Private script parser PASS, native follow-up result pending. No GameMP/Engine patch or CRC suppression.

### B0.4 serial-join harness regression after transport timeout — 20.10.2026 04:00:39 UTC
Run B2-20261020T040039Z: 20s controlled test with first bot's native server/Vanilla joined state and BotDriver confirmed **before** initiating second BotClient. Sequential launch established BOT1_SEQUENTIAL_JOIN_UTC 04:01:07Z, second joined 04:01:19Z. Result Exit 0 / B0_TWOBOT_SHORT_LOG_CONTROL_PASS, 21.1s observation. Independent read-only archived native verifier Exit 0: 3 server joins, 3 CRC checks, Vanilla saw 3 player joins, bot1 35 and bot2 21 BotDriver tick messages, SYNCBAD 0, no unexpected exit, 0 own game processes remaining, ports 25640/25641 free. All owned clients closed normally, Dedicated documented FORCE_FALLBACK, clone config restores done. This is evidence that staged joins can avoid one observed UDP timeout, NOT a proven network root cause or a long-term reliability acceptance. A second short staged repetition is being checked separately.

### Second consecutive staged control — 20.10.2026 04:02:16 UTC
B2-20261020T040216Z: staged local Retail Dedicated + original Vanilla + 2 distinct stationary bots, 21.1s observation. Native runner Exit 0, private independent Verify-B0-TwoBots.ps1: 3 joins/3 CRC, Vanilla sees both bot joins, Bot1 36 action ticks, Bot2 21, SYNCBAD 0, all owned processes closed and configs restored, no test UDP port occupied, verifier Exit 0. After first near-simultaneous run PASS and a simultaneous-repeat FAIL (UDP port timeout), **both sequential retests passed**. This supports staggering as a mitigation for the specific observed join race, but it does not establish full root cause or guarantee under WAN/extended play.

### B0 final scope at end of this host session
- B0.1 historical original Vanilla control: PASS 120s (2026-10-19), not freshly extended.
- B0.2 current original Vanilla + 1 true Bot: PASS 90.5s, 2 CRC and joins, SYNCBAD 0.
- B0.3 current original native server/client original-tick Bot-load state pairing: PASS for exactly one Level 1 / Sequence 338 / Tick 16.75 aligned observation, CRC 5279EC1D both, 48 lines each, 0 diffs, comparator exit 0. Continuous coverage not assessed.
- B0.4: 2 Bot / 90.5s PASS in isolated single observation; one simultaneous repeat FAIL (UDP port timeout); two serial-join follow-up runs 21.1s each PASS. 4 and 8 Bot tests OPEN, 60min 8-bot soak OPEN, Human Join/Leave cycling OPEN, ≥60min 1 Bot soak OPEN. No universal B0 release gate approval.
- Git code changes: None. Only plan and outcome ledger, no private binaries/dumps/logs committed. The dedicated server sometimes requires bounded forced shutdown after normal close attempt; owned process hash/identity verified; no other processes affected.

### Reproduce private native test (on authorized Shadow, no concurrent game sessions)
The following scripts already exist on Shadow in the private ignored .codex/evidence/p0-pair-20261019-main folder and are NOT checked into the public repo:
- Run-B0-OneBot.ps1 -Seconds 90 (Dedicated+Vanilla+stationary qualified single bot)
- Run-B0-TwoBots.ps1 -Seconds 20 (staggered first-joined guard before launching second bot, 2-Bot isolated profile)
- Verify-B0-TwoBots.ps1 -RunId B2-20261020T040216Z (read-only independent archived run audit)
- Run-B0-Capture-x86.ps1 -ControlSeconds 45 (must launch via C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe, x86, original registered Engine native dump flag, owned processes only)
- Pinned comparator: SeriousSam-TSE-Worktrees/chatgpt-syncdump-compare-20261017/tools/compare_sync_dumps.py --server <private run>/server-native-syncdump.txt --client <private run>/client-native-syncdump.txt
Run preflight hash/port/process check before each attempt; never use old raw dump files from unmatched runs as new evidence.
