// SPDX-License-Identifier: GPL-2.0-only
#pragma once
// Retail-1.07 PowerUpItemType: invisibility=0, invulnerability=1,
// serious damage=2, speed=3, bomb=4. Unknown values are retained.
inline bool DevRemovePowerup(bool enabled, bool server, bool demo, bool powerup, int type) {
  return enabled && server && !demo && powerup && (type==0 || type==2);
}
