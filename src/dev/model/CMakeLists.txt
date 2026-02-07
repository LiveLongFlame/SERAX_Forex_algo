cmake_minimum_required(VERSION 3.15)
project(ml_module)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON) # Required for Python modules

# Find Python interpreter + development headers
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Use pybind11 via CMake
# This will look inside your Python site-packages (venv) automatically
find_package(pybind11 REQUIRED)

# Find Armadillo
find_package(Armadillo REQUIRED)

# Source files
set(SRC_FILES
    ml.cpp
    objects/PRICE.cpp
)

# Create Python module
pybind11_add_module(ml ${SRC_FILES})

# Link Armadillo
target_link_libraries(ml PRIVATE ${ARMADILLO_LIBRARIES})

