cmake_minimum_required(VERSION 3.10)
project(dna_ai LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(CURL REQUIRED)
find_package(ZLIB REQUIRED)

add_executable(dna_ai src/main.cpp)

target_link_libraries(dna_ai PRIVATE CURL::libcurl ZLIB::ZLIB)

target_compile_options(dna_ai PRIVATE -O3 -march=native -Wall -Wextra)

include(CTest)
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

add_executable(gc_content_test tests/gc_content_test.cpp src/main.cpp)
target_compile_definitions(gc_content_test PRIVATE UNIT_TESTING)
target_link_libraries(gc_content_test PRIVATE GTest::gtest_main CURL::libcurl ZLIB::ZLIB)
add_test(NAME gc_content_test COMMAND gc_content_test)

