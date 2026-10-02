CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

all: test_botcore

test_botcore: test_botcore.cpp botcore.h
	$(CXX) $(CXXFLAGS) -o $@ test_botcore.cpp

test: test_botcore
	./test_botcore | tee test_output.txt

clean:
	rm -f test_botcore test_output.txt

.PHONY: all test clean
