cmake_minimum_required(VERSION 3.8)
project(cpp_robotics_sim_ros)

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

ament_target_dependencies(sim_node
rclcpp
std_msgs
geometry_msgs
nav_msgs
tf2_ros
diagnostic_msgs)

install(TARGETS
sim_node
DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
launch
config
rviz
urdf
xacro
worlds
DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(PROGRAMS
  scripts/noisy_odom_node.py
  scripts/trajectory_validation_recorder.py
  scripts/plot_trajectory_validation.py
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


