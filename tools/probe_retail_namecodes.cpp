// Read-only native CTString probe, linked against the pinned Retail Engine.lib.
// Run only in a fresh private Wine directory with original Engine.dll and deps.
// This tests the ORIGINAL exported decoder, not a Python reimplementation.
#include "StdAfx.h"  // from the materialized, pinned Retail GameMP build
#include <cstdio>
#include <cstring>
#include <cstddef>
#include <EntitiesV/Player.h>
#include <EntitiesV/Bullet.h>
#include <EntitiesV/Projectile.h>

static void hex(const char *s) {
  for (const unsigned char *p=(const unsigned char*)s; *p; ++p)
    std::printf("%02x", (unsigned)*p);
}

int main(int argc, char **argv) {
  if (argc < 2) return 2;
  if (std::strcmp(argv[1],"--layout")==0) {
    std::printf("{\"entity_id\":%u,\"health\":%u,\"armor\":%u,\"bullet_owner\":%u,\"projectile_owner\":%u,\"player_name\":%u}\n",
      (unsigned)offsetof(CEntity,en_ulID),(unsigned)offsetof(CLiveEntity,en_fHealth),
      (unsigned)offsetof(CPlayer,m_fArmor),(unsigned)offsetof(CBullet,m_penOwner),
      (unsigned)offsetof(CProjectile,m_penLauncher),
      (unsigned)(offsetof(CPlayerEntity,en_pcCharacter)+offsetof(CPlayerCharacter,pc_strName)));
    return 0;
  }
  for (int i=1; i<argc; ++i) {
    CTString source(argv[i]);
    CTString decoded=source.Undecorated();
    std::printf("NAME,"); hex(argv[i]); std::printf(","); hex((const char*)decoded);
    std::printf(",%ld\n", (long)source.LengthNaked());
  }
  return 0;
}
