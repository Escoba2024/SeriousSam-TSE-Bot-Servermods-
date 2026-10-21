#!/usr/bin/env bash
# Materialise the unqualified P0 candidate source tree.
#
#   poc/candidates/p0-nullrender-20261022/apply.sh <target-dir> [--force]
#
# The qualified release source in poc/release/gamemp/ is never modified. This
# script copies it, verifies the exact source hashes it was tested against,
# and then overwrites the three candidate files. Every other file in the
# target directory is byte-identical to the verified release source.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
SRC="$REPO/poc/release/gamemp"

TARGET="${1:-}"
FORCE="${2:-}"
if [ -z "$TARGET" ] || { [ "$FORCE" != "" ] && [ "$FORCE" != "--force" ]; }; then
  echo "usage: $0 <target-dir> [--force]" >&2
  exit 2
fi

# Source this candidate was authored against (the 61DC... release source).
declare -A EXPECT=(
  [Game.cpp]="01dfa59857df4953d3a89096cd8049b9ba022f81e388c0dfc52b4826909474b6"
  [BotDriver.cpp]="b5d3290391b2504cce96529155b4072361fed0319a80ad1695707e36a9165c64"
  [BotDriver.h]="82c8282d1426177031cdaa3f140fd084c2ddcf51cb74bfd694e49af90e8d0a3d"
)

for name in "${!EXPECT[@]}"; do
  actual="$(sha256sum "$SRC/$name" | cut -d' ' -f1)"
  if [ "$actual" != "${EXPECT[$name]}" ]; then
    echo "PROVENANCE FAILURE: $SRC/$name is $actual, expected ${EXPECT[$name]}" >&2
    exit 3
  fi
done

if [ -e "$TARGET" ]; then
  if [ "$FORCE" != "--force" ]; then
    echo "target exists: $TARGET (use --force to overwrite candidate files)" >&2
    exit 4
  fi
  rm -rf "$TARGET"
fi
mkdir -p "$TARGET"
cp -a "$SRC"/. "$TARGET"/

cp "$HERE/BotDriver.cpp" "$TARGET/BotDriver.cpp"
cp "$HERE/Game.cpp" "$TARGET/Game.cpp"
cp "$HERE/BotTelemetry.h" "$TARGET/BotTelemetry.h"

# Fail loudly if the overlay is incomplete or a stale file slipped in.
for marker in "BotTelemetry.h" "bot_bNullRender" "bot_iTelemetry"; do
  grep -q "$marker" "$TARGET/Game.cpp" "$TARGET/BotDriver.cpp" || {
    echo "verification failed: marker '$marker' missing" >&2
    exit 5
  }
done

echo "candidate source: $TARGET"
echo "next:"
echo "  msbuild '$TARGET/Game.vcxproj' /p:Configuration=Release_TSE107 /p:Platform=Win32"
echo "  sha256sum '$TARGET/../Bin/GameMP.dll'   # new hash, never deploy unqualified"
