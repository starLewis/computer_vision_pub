cmake_minimum_required(VERSION 3.9)
project(CppFun)

find_package(OpenCV REQUIRED)

include_directories(
        inc/
)

set(CMAKE_CXX_STANDARD 11)

add_executable(CppFun
        test/main.cpp
        cvutill/CvLineOperator.cpp
        cvutill/CvVectorImgsShow.cpp
        cvutill/CvKeyLineOperator.cpp
        )

target_link_libraries(
        CppFun
        ${OpenCV_LIBS}
)