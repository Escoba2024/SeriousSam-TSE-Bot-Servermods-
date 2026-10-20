# Tactical Bot AI – CecilBotMod Reference (20.10.2026)

Status: Experimental; Linux C++ policy tests pass. Native GameMP/Wine tests and release NOT qualified.
Public Hetzner server and approved DLL stay unchanged.

Reference: https://github.com/DreamyCecil/CecilBotMod @ 953b477, GNU GPL-2.0.
Files used for design: BotFunctions.cpp, BotMovement.cpp, BotWeapons.cpp, BotSettings.h, Navmesh.cpp, PathPoint.cpp, PathPolygon.cpp.
New tactical policy is independently implemented, inspired by documented CecilBot behavior.

Features: sticky target selection; wounded-opponent weighting; weapon-specific ranges;
strafe/side switching per bot; low-health close-range retreat; three movement difficulties.
Only current visible replicated players are eligible targets. Native weapon readiness
and action transport remain handled by existing GameMP code.

BotDriver-tactics.patch is designed ONLY for a COPY of poc/release/gamemp/BotDriver.cpp.
Place bot_tactics.h beside the staged source, then apply patch with patch -p1.
New shell variables: bot_bTacticalAI (default FALSE) and bot_iTacticalDifficulty (0,1,2).
Do not change the protected release GameMP source or public bot-client binaries.

Offline tests from repository root:
  make -C poc/botcore test
  python3 -m unittest discover -s poc/experiments/tactical-ai -p 'test_*.py' -v

Isolated patch smoke (never on protected sources):
  mkdir -p /tmp/tactical-candidate-src
  cp poc/release/gamemp/* /tmp/tactical-candidate-src/
  cp poc/botcore/bot_tactics.h /tmp/tactical-candidate-src/
  sed -i "s/\r$//" /tmp/tactical-candidate-src/BotDriver.cpp
  patch --dry-run --batch -p1 -d /tmp/tactical-candidate-src < poc/experiments/tactical-ai/BotDriver-tactics.patch
  patch --batch -p1 -d /tmp/tactical-candidate-src < poc/experiments/tactical-ai/BotDriver-tactics.patch

Converted navmeshes: nine world-hash-tagged Cecil maps under maps/ (GPL-2.0 derived data).
Directional arc connectivity and binary parser are tested, but native path following
is NOT enabled. Dynamic door locks, jump/crouch/pit flags and world-hash validation must
be integrated and proven before enabling automated route following.

Next acceptance: isolated Windows GameMP compilation; native lateral action sign check;
Wine 1-bot control and 8-bot tests; real vanilla joins; sync logs/CRC and 60-minute run;
performance measurements; backup and rollback proof before deploying.