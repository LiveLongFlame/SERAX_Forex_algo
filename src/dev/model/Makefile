CXX      := g++
CXXFLAGS := -std=c++17 -Wall -O2
LIBS     :=  -larmadillo

# Rule: make main.cpp -> main
ml: ml.cpp
	$(CXX) $(CXXFLAGS) ml.cpp  objects/PRICE.cpp -o ml $(LIBS)
