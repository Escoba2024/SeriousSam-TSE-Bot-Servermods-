# Offline behavior-QA harness. Builds ONLY inside poc/research/behavior-qa.
# The botcore headers under ../../botcore are consumed strictly read-only.
CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

BOTCORE = ../../botcore
BIN = qa_sim

all: $(BIN)

$(BIN): qa_sim.cpp qa_world.h $(wildcard $(BOTCORE)/*.h)
	$(CXX) $(CXXFLAGS) -I $(BOTCORE) -o $(BIN) qa_sim.cpp

selftest: $(BIN)
	./$(BIN) --selftest

bench: $(BIN)
	./$(BIN) --perf --candidates 8 --ticks 20000

clean:
	rm -f $(BIN)

.PHONY: all selftest bench clean
