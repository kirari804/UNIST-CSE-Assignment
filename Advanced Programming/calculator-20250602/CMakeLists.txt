cmake_minimum_required(VERSION 3.0)
project(Calculator)

add_executable(calc calculator.cc parse.cc expr.cc)
target_compile_options(calc PRIVATE -std=c++23 -Wall -g -fsanitize=address)
target_link_libraries(calc PRIVATE -fsanitize=address)
