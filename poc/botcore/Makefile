CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

TESTS = test_botcore test_botcore_ai test_bot_reconnect test_bot_combat test_bot_weapon_input test_bot_navigation test_bot_human_ai
HEADERS = $(wildcard *.h)

# Patched driver used by the integration-block smoke test. Point BOTDRIVER at
# your integrated tree, e.g.
#   make smoke BOTDRIVER=/path/to/tree/poc/release/gamemp/BotDriver.cpp
BOTDRIVER ?= ../ai-integration/gamemp/BotDriver.cpp

all: $(TESTS)

$(TESTS): %: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o $@ $<

test: $(TESTS)
	@set -e; for test in $(TESTS); do ./$$test; done

# Compiles the real `if (bot_bHumanAI) { ... }` integration block out of an
# already patched BotDriver.cpp against stubbed engine types. Skips cleanly
# when the patched driver is not available.
smoke: test_botdriver_block.cpp extract_block.py
	@if [ ! -f "$(BOTDRIVER)" ]; then \
	  echo "SKIP integration-block smoke: $(BOTDRIVER) not present"; \
	else \
	  python3 extract_block.py "$(BOTDRIVER)" > block.inc && \
	  $(CXX) $(CXXFLAGS) -o test_botdriver_block test_botdriver_block.cpp && \
	  ./test_botdriver_block; \
	fi

bench: bench_bot_human.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o bench_bot_human bench_bot_human.cpp
	./bench_bot_human

clean:
	rm -f $(TESTS) test_botdriver_block bench_bot_human block.inc test_output.txt test_ai_output.txt

.PHONY: all test smoke bench clean
