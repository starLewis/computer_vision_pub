cmake_minimum_required(VERSION 3.9)
project(07TestContours)

find_package(OpenCV REQUIRED)
set(CMAKE_CXX_STANDARD 11)

include_directories(
        ../../AutoFlightCodes/catkin_ws/src/WindAppCore/DroneCVSDK/CvTask/Common/inc/
        ../../AutoFlightCodes/catkin_ws/src/WindAppCore/CppFun/inc_pub/
)

FILE(GLOB source_file
        main.cpp
        ../../AutoFlightCodes/catkin_ws/src/WindAppCore/DroneCVSDK/CvTask/Common/src/*.cpp
        )

add_executable(07TestContours
        ${source_file}
        )

target_link_libraries(
        07TestContours
        ${OpenCV_LIBS}
)
