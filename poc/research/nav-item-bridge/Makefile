CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror
UPSTREAM_FLAGS ?=
INCLUDES = $(UPSTREAM_FLAGS) -Iinclude -I../../botcore
BUILD = build

TEST_BINS = \
	$(BUILD)/test_seams_and_contracts \
	$(BUILD)/test_scenarios_matrix \
	$(BUILD)/test_multibot_competition

BENCH_BIN = $(BUILD)/bench_nav_item_bridge

HEADERS = \
	include/upstream_seams.h \
	include/nav_cost_cache.h \
	include/nav_goal_sink.h \
	include/bridge_arbitrator.h \
	include/nav_item_bridge.h \
	include/arena_sim.h \
	include/upstream/navlab_mirror.h \
	include/upstream/itemai_mirror.h

.PHONY: all test smoke bench compat check-noalloc clean

all: $(TEST_BINS) $(BENCH_BIN)

$(BUILD):
	@mkdir -p $(BUILD)

$(BUILD)/test_seams_and_contracts: tests/test_seams_and_contracts.cpp $(HEADERS) | $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $@

$(BUILD)/test_scenarios_matrix: tests/test_scenarios_matrix.cpp $(HEADERS) | $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $@

$(BUILD)/test_multibot_competition: tests/test_multibot_competition.cpp $(HEADERS) | $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $@

$(BENCH_BIN): benches/bench_nav_item_bridge.cpp $(HEADERS) | $(BUILD)
	$(CXX) $(CXXFLAGS) -O3 -DNDEBUG $(INCLUDES) $< -o $@

test: $(TEST_BINS)
	@./$(BUILD)/test_seams_and_contracts
	@./$(BUILD)/test_scenarios_matrix
	@./$(BUILD)/test_multibot_competition

smoke: $(BUILD)/test_scenarios_matrix $(BUILD)/test_multibot_competition
	@./$(BUILD)/test_scenarios_matrix --summary
	@./$(BUILD)/test_multibot_competition --summary

bench: $(BENCH_BIN)
	@./$(BENCH_BIN)

compat: tests/compat_tu.cpp $(HEADERS) | $(BUILD)
	$(CXX) -std=c++14 -Wall -Wextra -Werror $(INCLUDES) -fsyntax-only tests/compat_tu.cpp
	$(CXX) -std=c++17 -Wall -Wextra -Werror $(INCLUDES) -fsyntax-only tests/compat_tu.cpp
	$(CXX) -std=c++20 -Wall -Wextra -Werror $(INCLUDES) -fsyntax-only tests/compat_tu.cpp
	@echo "[PASS] compat: C++14, C++17, C++20 clean"

check-noalloc:
	@python3 -c 'import pathlib, re, sys; bad = re.compile(r"\b(new|delete|malloc|calloc|realloc|free|vector|unordered_map|shared_ptr|unique_ptr)\b"); files = sorted(pathlib.Path("include").rglob("*.h")); errs = [f"{p}:{i}: forbidden token {m.group(1)!r}" for p in files for i, ln in enumerate(re.sub(r"\"(?:\\.|[^\"\\])*\"", "\"\"", re.sub(r"/\*.*?\*/", "", re.sub(r"//.*", "", p.read_text()), flags=re.S)).splitlines(), 1) if not ln.lstrip().startswith("#") for m in [bad.search(ln)] if m]; print("\n".join(errs) if errs else f"[PASS] check-noalloc: {len(files)} headers clean (zero dynamic allocation / STL heap tokens)"); sys.exit(1 if errs else 0)'

clean:
	rm -rf $(BUILD)
