CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -I../../botcore -I.
# research overlay; botcore is included READ-ONLY, never modified here.
all: combat_sim test_combat2
combat_sim: combat_sim.cpp combat2_profile.h combat2_weapon.h combat2_tactics.h
	$(CXX) $(CXXFLAGS) combat_sim.cpp -o combat_sim
test_combat2: test_combat2.cpp combat2_profile.h combat2_weapon.h combat2_tactics.h
	$(CXX) $(CXXFLAGS) test_combat2.cpp -o test_combat2
test: all
	./test_combat2
	python3 run_combat_qa.py --seeds 16
bench: combat_sim
	./combat_sim --bench
curve: combat_sim
	./combat_sim --weapon-curve
clean:
	rm -f combat_sim test_combat2
.PHONY: all test bench curve clean
