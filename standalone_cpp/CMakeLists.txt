cmake_minimum_required(VERSION 3.16)

project(cpp_robotics_sim_foundation LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(robotics_sim
	src/main.cpp

	src/differential_drive/simulator.cpp
	src/differential_drive/robot_utils.cpp
	src/differential_drive/differential_drive_reporter.cpp
	src/differential_drive/differential_drive.cpp
	src/differential_drive/mobile_robot.cpp
	src/differential_drive/differential_drive_robot.cpp
	src/differential_drive/target_controller.cpp

	src/manipulator/manipulator_reporter.cpp
	src/manipulator/manipulator_utils.cpp
)

target_include_directories(robotics_sim
	PRIVATE
		${CMAKE_CURRENT_SOURCE_DIR}/include
)

if (MSVC)
	target_compile_options(robotics_sim PRIVATE /W4)
else()
	target_compile_options(robotics_sim PRIVATE -Wall -Wextra -Wpedantic)
endif()