// Compile-and-run smoke test for the GameMP integration block itself.
//
// The offline policy tests in test_bot_human_ai.cpp never touch BotDriver.cpp.
// This file closes that gap without Windows, Visual Studio or the retail
// engine: it stubs the handful of engine types the integration touches and
// compiles the real `if (bot_bHumanAI) { ... }` block verbatim.
//
// It is NOT a build of GameMP.dll and proves no runtime gate. What it does
// prove:
//   - the integration code is syntactically valid C++ and type-correct
//     against the real botcore headers;
//   - a visible opponent is perceived, acquires a target after the profile's
//     reaction delay and produces a fire command;
//   - the block writes the values the surrounding driver expects.
//
// Usage:
//   python3 extract_block.py <path-to-BotDriver.cpp> > block.inc
//   g++ -std=c++17 -I. -o test_botdriver_block test_botdriver_block.cpp
//   ./test_botdriver_block
//
// The Makefile target `smoke` does this automatically and skips when the
// patched driver is not present.
#include <cstdint>
#include <cstdio>

#include "bot_combat.h"
#include "bot_human.h"

using botcore::BotProfile;
using botcore::HumanBotPolicy;

typedef float FLOAT;
typedef int INDEX;
typedef int BOOL;
#define TRUE 1
#define FALSE 0

static void BotLog(const char* fmt, ...) { (void)fmt; }
static FLOAT Clamp(FLOAT v, FLOAT lo, FLOAT hi) { return v < lo ? lo : (v > hi ? hi : v); }

// The engine's FLOAT3D uses 1-based component access: (1)=x, (2)=y, (3)=z.
struct FLOAT3D {
  FLOAT v[3];
  FLOAT operator()(int i) const { return v[i - 1]; }
  FLOAT& operator()(int i) { return v[i - 1]; }
};

struct CPlacement3D {
  FLOAT3D pl_PositionVector;
  FLOAT3D pl_OrientationAngle;
};

struct CPlayerWeapons {
  INDEX m_iBullets = 100;
  INDEX m_iShells = 20;
  INDEX m_iNapalm = 20;
  INDEX m_iElectricity = 20;
  INDEX m_iSniperBullets = 10;
  uint32_t m_iAvailableWeapons = 0x3FFFu;
  INDEX m_iCurrentWeapon = 2;
};

struct CEntity {
  static CEntity* GetPlayerEntity(INDEX i);
};

struct CPlayer : CEntity {
  CPlayerWeapons m_weapons;
  CPlayerWeapons* m_penWeapons = nullptr;
  CPlacement3D placement;
  FLOAT3D en_vCurrentTranslationAbsolute;
  FLOAT health = 100.0f;
  FLOAT GetHealth() const { return health; }
  CPlayerWeapons* GetPlayerWeapons() { return &m_weapons; }
};

static CPlayer g_players[16];

CEntity* CEntity::GetPlayerEntity(INDEX i) {
  if (i == 0 || i == 1) return &g_players[i];
  return nullptr;
}

static CPlacement3D BotCombatEye(CPlayer* p) { return p->placement; }
static BOOL BotCombatIsLocal(void*, INDEX) { return FALSE; }
static BOOL BotCombatVisible(CPlayer*, CPlayer*) { return TRUE; }

static HumanBotPolicy& BotHumanPolicy(INDEX iLP) {
  static HumanBotPolicy policies[4];
  return policies[iLP & 3];
}
static BotProfile& BotHumanProfile(INDEX iLP) {
  static BotProfile profiles[4];
  return profiles[iLP & 3];
}

struct SBotState {
  INDEX bs_iTick;
  FLOAT bs_lastHealth;
};

static INDEX bot_iLogEvery = 0;
static INDEX bot_bCombatSkipLocals = TRUE;
static INDEX bot_bHumanAI = TRUE;

// Mirrors the locals the surrounding BotDriver_HandleTimer scope provides.
static void HumanBlock(CPlayer* player, void* pgame, BOOL deathmatch, INDEX iLP,
                       SBotState& bs, FLOAT fTick, FLOAT& moveFactor,
                       botcore::CombatDecision& decision, INDEX& testAimReady,
                       FLOAT& outStrafe, BOOL& outFire) {
  INDEX visible = 0;
  BOOL humanFire = FALSE;
  FLOAT humanStrafe = 0.0f;
  FLOAT humanScanYaw = 0.0f;
  FLOAT humanTargetDistance = 0.0f;
  (void)testAimReady;

#include "block.inc"
  }  // closes the outer if (bot_bHumanAI) in the real driver

  outStrafe = humanStrafe;
  outFire = humanFire;
  (void)humanScanYaw;
  (void)humanTargetDistance;
  (void)visible;
}

int main() {
  g_players[0].m_penWeapons = &g_players[0].m_weapons;
  g_players[1].m_penWeapons = &g_players[1].m_weapons;
  g_players[1].placement.pl_PositionVector.v[2] = -20.0f;  // 20 m ahead (-z)

  BotProfile profile;
  botcore::BuildRosterProfile(7, 0, 20261020u, &profile);  // expert marksman
  BotHumanPolicy(0).Configure(&profile);

  SBotState bs;
  bs.bs_lastHealth = 0.0f;

  FLOAT move = 1.0f;
  int fires = 0;
  int first_target_tick = -1;
  botcore::CombatDecision last = {-1, 1, 0, 0, 0, false};
  FLOAT last_strafe = 0.0f;

  for (int t = 0; t < 40; ++t) {
    bs.bs_iTick = t;
    botcore::CombatDecision d = {-1, 1, 0, 0, 0, false};
    FLOAT strafe = 0.0f;
    BOOL fire = FALSE;
    INDEX ready = 0;
    HumanBlock(&g_players[0], nullptr, TRUE, 0, bs, 0.05f, move, d, ready, strafe, fire);
    if (fire) ++fires;
    if (d.target >= 0 && first_target_tick < 0) first_target_tick = t;
    last = d;
    last_strafe = strafe;
  }

  std::printf("integration block: target=%d first-acquire-tick=%d weapon=%d move=%.2f "
              "strafe=%.2f fires=%d/40\n",
              last.target, first_target_tick, last.weapon, (double)last.moveFactor,
              (double)last_strafe, fires);

  int failures = 0;
  if (last.target != 1) {
    std::printf("FAIL: the visible opponent was not targeted\n");
    ++failures;
  }
  if (first_target_tick < 0 || first_target_tick > 5) {
    std::printf("FAIL: reaction delay outside the expected 1..5 tick window\n");
    ++failures;
  }
  if (fires <= 0) {
    std::printf("FAIL: the policy never fired at a visible opponent\n");
    ++failures;
  }
  if (last.weapon < 1 || last.weapon > 14) {
    std::printf("FAIL: weapon number out of range\n");
    ++failures;
  }
  std::printf("%s\n", failures ? "INTEGRATION BLOCK FAIL" : "INTEGRATION BLOCK PASS");
  return failures ? 1 : 0;
}
