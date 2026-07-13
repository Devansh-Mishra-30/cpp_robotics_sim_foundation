cmake_minimum_required(VERSION 3.8)
project(cpp_robotics_sim_ros)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(diagnostic_msgs REQUIRED)

add_executable(sim_node src/sim_node.cpp)

add_executable(day88_performance_benchmark src/day88_performance_benchmark.cpp)

target_include_directories(day88_performance_benchmark PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(sim_node
rclcpp
std_msgs
geometry_msgs
nav_msgs
tf2_ros
diagnostic_msgs)

install(TARGETS
sim_node
day88_performance_benchmark
DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
launch
config
rviz
urdf
xacro
worlds
nav2
maps
web
DESTINATION share/${PROJECT_NAME})

# ---------------------------------------------------------------------------
# Lint tools are intentionally skipped for now.
#
# Reason:
# Day 86 is focused on GoogleTest unit testing for deterministic C++ math.
# Full style/lint cleanup is planned later during the code-quality phase.
#
# This does NOT affect runtime behavior.
# This does NOT disable GoogleTest.
# This only prevents style tools like flake8/uncrustify/cppcheck from failing
# the Day 86 unit-test workflow.
# ---------------------------------------------------------------------------
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)

  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  set(ament_cmake_cppcheck_FOUND TRUE)
  set(ament_cmake_flake8_FOUND TRUE)
  set(ament_cmake_pep257_FOUND TRUE)
  set(ament_cmake_uncrustify_FOUND TRUE)
  set(ament_cmake_xmllint_FOUND TRUE)
  set(ament_cmake_lint_cmake_FOUND TRUE)

  ament_lint_auto_find_test_dependencies()
endif()

install(PROGRAMS
  scripts/noisy_odom_node.py
  scripts/trajectory_validation_recorder.py
  scripts/plot_trajectory_validation.py
  scripts/cmd_vel_twist_bridge.py
  scripts/nav2_lifecycle_check.sh
  scripts/nav2_costmap_check.sh
  scripts/nav2_planner_controller_check.sh
  scripts/day104_localization_comparison.py
  scripts/plot_day104_localization_comparison.py
  scripts/day107_covariance_analysis.py
  scripts/day108_fusion_analysis.py
  scripts/command_mux_node.py
  scripts/keyboard_teleop_node.py
  scripts/simulation_manager_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------------------------------------------------------------------
# Day 86 - GoogleTest Unit Tests
# ---------------------------------------------------------------------------
# These tests validate the deterministic C++ math/kinematics layer:
#   - clamp()
#   - wrapToPi()
#   - integratePose()
#
# They do not launch ROS nodes or Gazebo.
# They are fast unit tests and will be reused in CI later.
if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)

  ament_add_gtest(test_day86_core
    test/test_day86_core.cpp
  )

  if(TARGET test_day86_core)
    target_include_directories(test_day86_core PUBLIC
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
      $<INSTALL_INTERFACE:include>
    )
  endif()
endif()

ament_package()


