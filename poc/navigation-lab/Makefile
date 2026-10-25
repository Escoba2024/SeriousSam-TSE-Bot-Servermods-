CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

TESTS = test_nav_graph test_nav_astar test_nav_agent test_nav_seam
HEADERS = nav_graph.h nav_astar.h nav_agent.h nav_maps.h

all: $(TESTS) bench_nav

$(TESTS): %: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ $<

bench_nav: bench_nav.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o bench_nav bench_nav.cpp

test: $(TESTS)
	@set -e; for test in $(TESTS); do ./$$test; done

# Quick sanity run (graph + search only; agent/seam come with `make test`).
smoke: test_nav_graph test_nav_astar
	./test_nav_graph
	./test_nav_astar

# Measured CPU/RAM benchmark (1/4/8/16 bots, real timings, no estimates).
bench: bench_nav
	./bench_nav

# The lab is allocation-free by design: no heap primitives in any header.
# Comments are stripped by the preprocessor first (so prose like
# "allocation-free" cannot trip the gate). The bench additionally traps
# operator new at runtime.
check-noalloc:
	@set -e; for h in $(HEADERS); do \
	  if $(CXX) -std=c++17 -fpreprocessed -dD -E $$h | \
	     grep -nE '\b(new|malloc|calloc|realloc|free|delete)\b'; then \
	    echo "HEAP PRIMITIVE FOUND IN $$h"; exit 1; \
	  fi; \
	done
	@echo "check-noalloc OK"

# Header compatibility with the older toolchains the mod tree must support.
compat: compat_tu.cpp $(HEADERS)
	$(CXX) -std=c++11 -O2 -Wall -Wextra -c compat_tu.cpp -o /dev/null
	$(CXX) -std=c++14 -O2 -Wall -Wextra -c compat_tu.cpp -o /dev/null
	$(CXX) -std=c++17 -O2 -Wall -Wextra -c compat_tu.cpp -o /dev/null
	@echo "compat OK (c++11/c++14/c++17)"

clean:
	rm -f $(TESTS) bench_nav

.PHONY: all test smoke bench check-noalloc compat clean
