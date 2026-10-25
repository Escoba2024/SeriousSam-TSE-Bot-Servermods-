// compat_tu.cpp - compile-only translation unit for `make compat`.
// Instantiates every lab header under -std=c++11/c++14/c++17 to prove the
// headers stay toolchain-compatible for the mod tree.
#include "nav_graph.h"
#include "nav_astar.h"
#include "nav_agent.h"
#include "nav_maps.h"

namespace navlab {

// Force instantiation of every inline surface (no runtime, link never used;
// external linkage keeps -Wall -Wextra quiet about "unused function").
inline void CompatInstantiate() {
  NavGraph g;
  maps::MakeGrid(g, 3, 3);
  g.ComputeDegrees();
  g.ParseLine("block 0 1 1");
  NavAStar s;
  NavSearchConfig cfg;
  NavPath p = s.Find(g, 0, 8, cfg);
  (void)p.status;
  NavAgent a;
  NavPersonality np = NavPersonalityFromTraits(0.5f, 0.5f, 1.0f, 240.0f);
  a.Configure(np, 1u);
  NavAgentInput in;
  in.tick = 0;
  in.x = 0.0;
  in.y = 0.0;
  in.z = 0.0;
  in.yaw_deg = 0.0;
  in.alive = true;
  in.movement_requested = false;
  in.has_target = false;
  in.target_visible = false;
  in.target_x = 0.0;
  in.target_y = 0.0;
  in.target_z = 0.0;
  NavCommand c = a.Step(g, in);
  (void)c.mode;
}

}  // namespace navlab
