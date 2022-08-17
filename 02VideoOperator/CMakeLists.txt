cmake_minimum_required(VERSION 3.12)
project(02VideoOperator)

find_package(OpenCV REQUIRED)

set(CMAKE_CXX_STANDARD 14)

add_executable(02VideoOperator
        main.cpp)

target_link_libraries(
        02VideoOperator
        ${OpenCV_LIBS}
)