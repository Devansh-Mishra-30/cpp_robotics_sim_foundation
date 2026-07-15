cmake_minimum_required(VERSION 3.8)

project(cpp_robotics_sim_ros)

# -----------------------------------------------------------------------------
# Compiler configuration
# -----------------------------------------------------------------------------

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
  )
endif()

# -----------------------------------------------------------------------------
# Package dependencies
# -----------------------------------------------------------------------------

find_package(ament_cmake REQUIRED)

find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(diagnostic_msgs REQUIRED)

# -----------------------------------------------------------------------------
# C++ executables
# -----------------------------------------------------------------------------

add_executable(
  sim_node
  src/sim_node.cpp
)

target_include_directories(
  sim_node
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

ament_target_dependencies(
  sim_node
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  tf2_ros
  diagnostic_msgs
)

add_executable(
  performance_benchmark
  src/performance_benchmark.cpp
)

target_include_directories(
  performance_benchmark
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# -----------------------------------------------------------------------------
# Install C++ executables
# -----------------------------------------------------------------------------

install(
  TARGETS
    sim_node
    performance_benchmark
  DESTINATION lib/${PROJECT_NAME}
)

# -----------------------------------------------------------------------------
# Install public headers
# -----------------------------------------------------------------------------

install(
  DIRECTORY include/
  DESTINATION include
)

# -----------------------------------------------------------------------------
# Install ROS package resources
# -----------------------------------------------------------------------------

install(
  DIRECTORY
    launch
    config
    rviz
    urdf
    xacro
    worlds
    nav2
    maps
    web
  DESTINATION share/${PROJECT_NAME}
)

# -----------------------------------------------------------------------------
# Install Python and shell executables
# -----------------------------------------------------------------------------

install(
  PROGRAMS
    scripts/noisy_odom_node.py
    scripts/trajectory_validation_recorder.py
    scripts/plot_trajectory_validation.py
    scripts/cmd_vel_twist_bridge.py
    scripts/nav2_lifecycle_check.sh
    scripts/nav2_costmap_check.sh
    scripts/nav2_planner_controller_check.sh
    scripts/localization_comparison_recorder.py
    scripts/plot_localization_comparison.py
    scripts/covariance_analysis.py
    scripts/localization_fusion_recorder.py
    scripts/plot_localization_fusion.py
    scripts/command_mux_node.py
    scripts/keyboard_teleop_node.py
    scripts/simulation_manager_node.py
    scripts/mode_manager_node.py
    scripts/localization_manager_node.py
    scripts/mapping_manager_node.py
    scripts/navigation_goal_manager_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# -----------------------------------------------------------------------------
# Tests and quality checks
# -----------------------------------------------------------------------------

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)

  ament_lint_auto_find_test_dependencies()

  # ---------------------------------------------------------------------------
  # Python unit tests
  # ---------------------------------------------------------------------------

  ament_add_pytest_test(
    test_navigation_goal_validation
    test/test_navigation_goal_validation.py
    TIMEOUT 30
  )

  ament_add_pytest_test(
    test_map_name_validation
    test/test_map_name_validation.py
    TIMEOUT 30
  )

  ament_add_pytest_test(
    test_environment_validation
    test/test_environment_validation.py
    TIMEOUT 30
  )

  ament_add_pytest_test(
    test_localization_environment_switch
    test/test_localization_environment_switch.py
    TIMEOUT 30
  )

  ament_add_pytest_test(
    test_mode_transition_rules
    test/test_mode_transition_rules.py
    TIMEOUT 30
  )

  ament_add_pytest_test(
    test_safe_map_path_resolution
    test/test_safe_map_path_resolution.py
    TIMEOUT 30
  )

  # ---------------------------------------------------------------------------
  # C++ unit tests
  # ---------------------------------------------------------------------------

  ament_add_gtest(
    test_core_math
    test/test_core_math.cpp
  )

  if(TARGET test_core_math)
    target_include_directories(
      test_core_math
      PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    )
  endif()
endif()

ament_package()