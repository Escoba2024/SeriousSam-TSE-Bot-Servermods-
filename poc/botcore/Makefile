CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

all: test_botcore test_botcore_ai

test_botcore: test_botcore.cpp botcore.h
	$(CXX) $(CXXFLAGS) -o $@ test_botcore.cpp

test_botcore_ai: test_botcore_ai.cpp botcore_ai.h
	$(CXX) $(CXXFLAGS) -o $@ test_botcore_ai.cpp

test: test_botcore test_botcore_ai
	./test_botcore | tee test_output.txt
	./test_botcore_ai | tee test_ai_output.txt

clean:
	rm -f test_botcore test_botcore_ai test_output.txt test_ai_output.txt

.PHONY: all test clean
