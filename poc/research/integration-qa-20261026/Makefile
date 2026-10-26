CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Werror

CPP_TESTS = test_combat_nav_regressions test_item_multifloor_regressions
BOTCORE_HEADERS = $(wildcard ../../botcore/*.h)

all: $(CPP_TESTS)

$(CPP_TESTS): %: %.cpp $(BOTCORE_HEADERS)
	$(CXX) $(CXXFLAGS) -I ../../botcore -o $@ $<

test-cpp: $(CPP_TESTS)
	@set -e; for t in $(CPP_TESTS); do ./$$t; done

test-py:
	python3 -B -m unittest -v test_session_and_flags_regressions.py

test: test-cpp test-py

test-live: test
	python3 -B run_live_branch_audit.py

clean:
	rm -f $(CPP_TESTS) *.o

.PHONY: all test-cpp test-py test test-live clean
