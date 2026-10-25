// nav_maps.h - SYNTHETIC map builders for the Navigation 2.0 offline tests
// and benchmarks. Everything here is generated procedurally; no data from
// retail maps is stored in or loaded by this repository.
//
// Coordinate convention matches the engine: y is up, routing happens in the
// x/z plane. Node spacing is in metres.

#ifndef NAVLAB_NAV_MAPS_H
#define NAVLAB_NAV_MAPS_H

#include <cstdint>

#include "nav_graph.h"

namespace navlab {
namespace maps {

// Straight corridor along +x: nodes 0..count-1, spacing metres apart.
inline void MakeCorridor(NavGraph& g, int count, double spacing = 4.0,
                         uint32_t flags = kNodeNone) {
  for (int i = 0; i < count; ++i) {
    g.AddNode(i * spacing, 0.0, 0.0, flags);
    if (i > 0) g.Link(i - 1, i);
  }
  g.ComputeDegrees();
}

// Open grid, 4-connected. `is_wall(y, x)` removes a cell (and its edges).
// Node index = y * width + x for non-wall cells... NOTE: to keep indexing
// simple, wall cells still CONSUME an index but are not added; use the
// returned mapping via NodeAt(width, x, y) = y*width+x only when the cell
// exists. Tests below only use wall-free or fully-checked layouts.
inline void MakeGrid(NavGraph& g, int width, int height, double spacing = 4.0,
                     bool (*is_wall)(int y, int x, void* ctx) = nullptr,
                     void* ctx = nullptr) {
  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      if (is_wall && is_wall(y, x, ctx)) {
        g.AddNode(x * spacing, 0.0, y * spacing, kNodeNone, 1.0);
        // Node exists (keeps index mapping) but gets NO edges below.
        continue;
      }
      g.AddNode(x * spacing, 0.0, y * spacing);
    }
  }
  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      const int i = y * width + x;
      if (is_wall && is_wall(y, x, ctx)) continue;
      if (x + 1 < width && !(is_wall && is_wall(y, x + 1, ctx))) g.Link(i, i + 1);
      if (y + 1 < height && !(is_wall && is_wall(y + 1, x, ctx))) {
        g.Link(i, i + width);
      }
    }
  }
  g.ComputeDegrees();
}

// Ring of `count` nodes on a circle of `radius`; pure cycle, two equal ways
// around - the canonical alternative-route test map.
inline void MakeRing(NavGraph& g, int count, double radius = 20.0) {
  const double pi = 3.14159265358979323846;
  for (int i = 0; i < count; ++i) {
    const double a = 2.0 * pi * i / count;
    g.AddNode(radius * std::sin(a), 0.0, radius * std::cos(a));
  }
  for (int i = 0; i < count; ++i) {
    g.Link(i, (i + 1) % count);
  }
  g.ComputeDegrees();
}

// Corridor with dead-end side branches: main line 0..main-1 along +x; from
// every `branch_every`-th node a leaf hangs at -z. Leaves get no flag so
// dead-end aversion can be measured.
inline void MakeDeadEndMap(NavGraph& g, int main_count, int branch_every,
                           double spacing = 4.0) {
  for (int i = 0; i < main_count; ++i) {
    g.AddNode(i * spacing, 0.0, 0.0);
    if (i > 0) g.Link(i - 1, i);
  }
  for (int i = 0; i < main_count; ++i) {
    if (branch_every > 0 && (i % branch_every) == 0 && i > 0 &&
        i < main_count - 1) {
      const int leaf = g.AddNode(i * spacing, 0.0, -spacing);
      g.Link(i, leaf);
    }
  }
  g.ComputeDegrees();
}

// Two separate grids side by side with NO connection: unreachable-goal tests.
inline void MakeDisconnected(NavGraph& g, int side, double spacing = 4.0,
                             double gap = 100.0) {
  const int base = g.node_count();
  MakeGrid(g, side, side, spacing);
  // Second component, offset far along +x; indices shifted by the first grid.
  for (int y = 0; y < side; ++y) {
    for (int x = 0; x < side; ++x) {
      g.AddNode(gap + x * spacing, 0.0, y * spacing);
    }
  }
  for (int y = 0; y < side; ++y) {
    for (int x = 0; x < side; ++x) {
      const int i = base + side * side + y * side + x;
      if (x + 1 < side) g.Link(i, i + 1);
      if (y + 1 < side) g.Link(i, i + side);
    }
  }
  g.ComputeDegrees();
}

// Inward spiral corridor: the unique path from the outside to the centre is
// long, which makes budget limits observable. Cells are laid out on a
// width*height grid; only the spiral corridor gets edges.
inline void MakeSpiral(NavGraph& g, int side, double spacing = 4.0) {
  // Allocate all cells as nodes (index = y*side+x) so index math stays easy.
  for (int y = 0; y < side; ++y) {
    for (int x = 0; x < side; ++x) {
      g.AddNode(x * spacing, 0.0, y * spacing);
    }
  }
  // Walk the spiral and link consecutive cells.
  int x0 = 0, y0 = 0, x1 = side - 1, y1 = side - 1;
  int prev = -1;
  while (x0 <= x1 && y0 <= y1) {
    for (int x = x0; x <= x1; ++x) {
      const int i = y0 * side + x;
      if (prev >= 0) g.Link(prev, i);
      prev = i;
    }
    ++y0;
    for (int y = y0; y <= y1; ++y) {
      const int i = y * side + x1;
      if (prev >= 0) g.Link(prev, i);
      prev = i;
    }
    --x1;
    if (y0 <= y1) {
      for (int x = x1; x >= x0; --x) {
        const int i = y1 * side + x;
        if (prev >= 0) g.Link(prev, i);
        prev = i;
      }
      --y1;
    }
    if (x0 <= x1) {
      for (int y = y1; y >= y0; --y) {
        const int i = y * side + x0;
        if (prev >= 0) g.Link(prev, i);
        prev = i;
      }
      ++x0;
    }
  }
  g.ComputeDegrees();
}

}  // namespace maps
}  // namespace navlab

#endif  // NAVLAB_NAV_MAPS_H
