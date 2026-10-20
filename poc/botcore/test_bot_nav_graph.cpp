// Text waypoint import/graph capacity regression, including converted Cecil maps.
#include "botcore_ai.h"
#include <cstdio>
using namespace botcore;
static int failures=0;
#define CHECK(expr,msg) do { if(!(expr)){std::printf("FAIL: %s @ %d\n",msg,__LINE__); ++failures;} }while(0)
int main() {
  WaypointGraph graph;
  CHECK(graph.ParseLine("node 0 0 0"),"node 0");
  CHECK(graph.ParseLine("node 1 0 0"),"node 1");
  CHECK(graph.ParseLine("node 2 0 0"),"node 2");
  CHECK(graph.ParseLine("arc 0 1"),"arc 0 to 1");
  CHECK(graph.ParseLine("arc 1 2"),"arc 1 to 2");
  CHECK(graph.NextHop(0,2)==1,"directed multihop path");
  CHECK(graph.NextHop(2,0)==-1,"no invented reverse arc");
  CHECK(graph.ParseLine("# comment"),"comments");
  CHECK(!graph.ParseLine("arc 0 999"),"invalid link rejected");
  CHECK(!graph.ParseLine("node nan 0 0"),"nonfinite nodes rejected");

  struct Map { const char* name; int nodes; } maps[]={
    {"DesertTemple_E6B24B0F",282},{"DM_LittleTrouble_6C64BF87",110},
    {"DM_TheLostTomb_AACB1C67",111},{"Fortress_5652374B",158},
    {"Hole_1AD627D0",139},{"KuntaKinte_AFD9424F",335},
    {"RedStation_5AF1A276",193},{"WeGotSkullsNBonesToo_9B573405",296},
    {"Yodeller_FC72665B",111}
  };
  for (const Map& map: maps) {
    char filename[300];
    std::snprintf(filename,sizeof(filename),
      "../experiments/tactical-ai/maps/%s.waypoints",map.name);
    FILE* f=std::fopen(filename,"rb");
    CHECK(f!=nullptr,"converted map exists");
    if (!f) continue;
    WaypointGraph imported;
    char line[512];
    int arcs=0;
    bool valid=true;
    while (std::fgets(line,sizeof(line),f)) {
      if (line[0]=='a' && line[1]=='r' && line[2]=='c') ++arcs;
      if (!imported.ParseLine(line)) { valid=false; break; }
    }
    std::fclose(f);
    CHECK(valid,"all map lines parse");
    CHECK(imported.node_count()==map.nodes,"all expected map nodes retained");
    CHECK(arcs>200,"nontrivial map connectivity retained");
  }
  WaypointGraph capped;
  for (int i=0;i<WaypointGraph::kMaxNodes;i++)
    CHECK(capped.AddNode(i,0,0)==i,"all graph capacity nodes accepted");
  CHECK(capped.AddNode(513,0,0)==-1,"capacity boundary enforced");
  std::printf("WAYPOINT IMPORT %s (%d failures)\n",failures?"FAIL":"PASS",failures);
  return failures?1:0;
}
