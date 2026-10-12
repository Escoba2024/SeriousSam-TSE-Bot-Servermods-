/* SeriousSam TSE Bot Project: GameMP-only bot-client integration.
 * Modified 2026-10-08 through 2026-10-11; publication notice 2026-10-12.
 * Original captured source and published hashes: docs/reports/2026-10-12-source-verification.json.
 * GPL-2.0-only; existing upstream copyright notices are retained. */
/* Copyright (c) 2002-2012 Croteam Ltd. 
This program is free software; you can redistribute it and/or modify
it under the terms of version 2 of the GNU General Public License as published by
the Free Software Foundation


This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. */

#include <Engine/Engine.h>
#include "Game.h"
#include "SEColors.h"

// [Cecil] Include common header for Entities
#if SE1_GAME == SS_TSE
  #include <EntitiesTSE/EntitiesAPI.h>
  #include <EntitiesV/Player.h>
#else
  #include <EntitiesTFE/EntitiesAPI.h>
  #include <EntitiesTFE/Players/Player.h>
#endif

