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
	src/mobile_robot.cpp
	src/differential_drive_robot.cpp
 "include/differential_drive_robot.h" "src/differential_drive_robot.cpp" "include/trajectory_metrics.h" "include/simulation_scenario.h" "include/validation_result.h")

target_include_directories(robotics_sim
	PRIVATE
		${CMAKE_CURRENT_SOURCE_DIR}/include
)

if (MSVC)
	target_compile_options(robotics_sim PRIVATE /W4)
else()
	target_compile_options(robotics_sim PRIVATE -Wall -Wextra -Wpedantic)
endif()