CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror
ROOT := .build/upstream/poc
BRIDGE := $(ROOT)/research/nav-item-bridge
INCLUDES := -I. -I$(BRIDGE)/include
DEFINES := -DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM
.PHONY: prepare test upstream-tests candidate-tests compat sanitize bench bench-upstream bench-candidate clean
prepare:
	python3 prepare.py

test: prepare
	$(MAKE) -j1 upstream-tests candidate-tests compat

upstream-tests:
	$(MAKE) -j1 -C $(ROOT)/navigation-lab test compat check-noalloc
	$(MAKE) -j1 -C $(ROOT)/research/item-utility test
	$(MAKE) -j1 -C $(BRIDGE) test compat check-noalloc UPSTREAM_FLAGS=$(DEFINES)
	$(MAKE) -j1 -C $(ROOT)/botcore test

candidate-tests:
	$(CXX) $(CXXFLAGS) $(DEFINES) $(INCLUDES) tests/test_completion.cpp -o .build/test_completion
	./.build/test_completion
	$(CXX) $(CXXFLAGS) $(DEFINES) $(INCLUDES) tests/test_regressions.cpp -o .build/test_regressions
	./.build/test_regressions
	$(CXX) $(CXXFLAGS) $(DEFINES) $(INCLUDES) tests/test_controller.cpp -o .build/test_controller
	./.build/test_controller

compat:
	$(CXX) -std=c++14 -Wall -Wextra -Wpedantic -Werror $(DEFINES) $(INCLUDES) -fsyntax-only tests/test_completion.cpp
	$(CXX) -std=c++20 -Wall -Wextra -Wpedantic -Werror $(DEFINES) $(INCLUDES) -fsyntax-only tests/test_completion.cpp
	$(CXX) -std=c++14 -Wall -Wextra -Wpedantic -Werror $(DEFINES) $(INCLUDES) -fsyntax-only tests/test_controller.cpp
	$(CXX) -std=c++20 -Wall -Wextra -Wpedantic -Werror $(DEFINES) $(INCLUDES) -fsyntax-only tests/test_controller.cpp

sanitize:
	$(CXX) -std=c++17 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer $(DEFINES) $(INCLUDES) tests/test_completion.cpp -o .build/test_completion_san
	ASAN_OPTIONS=detect_leaks=1 ./.build/test_completion_san
	$(CXX) -std=c++17 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer $(DEFINES) $(INCLUDES) tests/test_regressions.cpp -o .build/test_regressions_san
	ASAN_OPTIONS=detect_leaks=1 ./.build/test_regressions_san
	$(CXX) -std=c++17 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer $(DEFINES) $(INCLUDES) tests/test_controller.cpp -o .build/test_controller_san
	ASAN_OPTIONS=detect_leaks=1 ./.build/test_controller_san

bench: bench-upstream bench-candidate

bench-upstream:
	$(MAKE) -j1 -C $(ROOT)/navigation-lab bench
	$(MAKE) -j1 -C $(ROOT)/research/item-utility bench
	$(MAKE) -j1 -C $(BRIDGE) bench UPSTREAM_FLAGS=$(DEFINES)

bench-candidate:
	$(CXX) $(CXXFLAGS) $(DEFINES) $(INCLUDES) bench_controller.cpp -o .build/bench_controller
	./.build/bench_controller

clean:
	python3 -c 'import pathlib,shutil; p=pathlib.Path(".build"); assert not p.is_symlink(); shutil.rmtree(p,ignore_errors=True)'
