cmake_minimum_required(VERSION 3.9)
project(03ReadPointCloudFromCE30D)

include_directories(
        /usr/local/include/ce30_driver
)

set(CMAKE_CXX_STANDARD 11)

find_package(OpenCV REQUIRED)
find_package(ce30_driver 1.0.4 REQUIRED)

add_executable(03ReadPointCloudFromCE30D
        main.cpp
        CE30Driver.cpp
        )

target_link_libraries(
        03ReadPointCloudFromCE30D
        ${CE30_DRIVER_LIBRARIES}
        ce30_pcviz
        -lboost_system
        -lboost_thread
        ${OpenCV_LIBS}
)