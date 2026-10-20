CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

TESTS = test_botcore test_botcore_ai test_bot_reconnect test_bot_combat test_bot_weapon_input test_bot_navigation test_bot_tactics test_bot_nav_graph
HEADERS = $(wildcard *.h)

all: $(TESTS)

$(TESTS): %: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ $<

test: $(TESTS)
	@set -e; for test in $(TESTS); do ./$$test; done

clean:
	rm -f $(TESTS) test_output.txt test_ai_output.txt

.PHONY: all test clean
