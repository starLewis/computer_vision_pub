cmake_minimum_required(VERSION 3.12)
project(14CCallPython)
set(CMAKE_CXX_STANDARD 14)

find_package(OpenCV REQUIRED)

include_directories(
        /usr/include/python2.7
)

link_directories(/usr/lib/python2.7/config-x86_64-linux-gnu)

add_executable(14CCallPython
        main.cpp)

target_link_libraries(14CCallPython
        libpython2.7.so
        ${OpenCV_LIBS})

#add_library()