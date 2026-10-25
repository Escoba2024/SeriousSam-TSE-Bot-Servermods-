# Standalone build for the item-utility research prototype.
#
# This directory is intentionally independent of poc/botcore: the prototype must
# be buildable and testable without the GameMP tree, without Windows and without
# Retail. The integration adapter is a header-only bridge that *consumes*
# botcore and is therefore not part of this build (see botcore_adapter.h and
# docs/research/item-utility/… integration plan).
#
#   make test    unit + acceptance tests (decision semantics, determinism, CPU)
#   make bench   CPU benchmarks (prints a table, exits non-zero on budget miss)
#   make all     test + bench
#   make clean

CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic
INCLUDES = -Iinclude

TESTS = test_item_utility test_scoring_terms test_botcore_adapter
HEADERS = $(wildcard include/*.h)

all: test bench

test_item_utility: tests/test_item_utility.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $<

test_scoring_terms: tests/test_scoring_terms.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $<

# Integration bridge: reads poc/botcore headers (read-only) to prove that the
# stand-in weapon table equals botcore::ScoreWeapon and that the mask/personality
# conventions match. Nothing under poc/botcore is modified.
test_botcore_adapter: tests/test_botcore_adapter.cpp $(HEADERS) ../../botcore/bot_loadout.h ../../botcore/bot_profile.h
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $<

bench_item_utility: benches/bench_item_utility.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $<

test: $(TESTS)
	@set -e; for t in $(TESTS); do echo "--- $$t"; ./$$t; done
	@echo "ALL ITEM-UTILITY OFFLINE TESTS PASSED"

bench: bench_item_utility
	@./bench_item_utility

clean:
	rm -f $(TESTS) bench_item_utility

.PHONY: all test bench clean
