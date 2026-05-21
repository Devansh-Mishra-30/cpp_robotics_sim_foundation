cmake_minimum_required(VERSION 3.16)

project(cpp_robotics_sim_foundation LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(robotics_sim
	src/main.cpp
	src/simulator.cpp
	src/robot_utils.cpp
	src/reporter.cpp
	src/differential_drive.cpp
	src/manipulator_utils.cpp
)

target_include_directories(robotics_sim
	PRIVATE
		${CMAKE_CURRENT_SOURCE_DIR}/include
)