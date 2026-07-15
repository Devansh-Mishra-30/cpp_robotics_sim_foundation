# C++ / ROS 2 Robotics Simulation Foundation

![ROS 2 Jazzy CI](https://github.com/Devansh-Mishra-30/cpp_robotics_sim_foundation/actions/workflows/ros2_jazzy_ci.yml/badge.svg)

A robotics simulation engineering project built around C++, ROS 2 Jazzy, Gazebo Sim, `ros2_control`, differential-drive control, simulated sensing, validation tooling, and Nav2 navigation.

The project started as a standalone C++ robotics simulator and has grown into a ROS 2 / Gazebo mobile robot simulation stack with robot modeling, controller integration, lidar simulation, odometry, TF, RViz visualization, trajectory validation, GoogleTest, GitHub Actions CI, performance benchmarking, and Nav2 navigation evidence.

Current release status: **Nav2 integration, validation tooling, documentation, and browser-based control workflow are operational.**

---

## What This Project Demonstrates

This repository is designed as an engineering artifact, not only a demo.

It demonstrates:

- C++ robotics simulation fundamentals
- differential-drive kinematics
- manipulator joint-state simulation
- ROS 2 C++ node development
- launch files, YAML parameters, runtime overrides, and QoS
- odometry and TF publishing
- runtime diagnostics
- URDF/Xacro robot modeling
- RViz robot visualization
- Gazebo Sim spawning and world setup
- `ros2_control`, `controller_manager`, `joint_state_broadcaster`, and `diff_drive_controller`
- simulated 2D lidar through `ros_gz_bridge`
- noisy odometry generation and covariance modeling
- trajectory validation with CSV logging and plotting
- deterministic C++ unit testing with GoogleTest
- GitHub Actions CI for ROS 2 Jazzy build/test validation
- deterministic C++ performance benchmarking
- Nav2 lifecycle, costmap, planner, controller, goal-navigation, recovery, waypoint, and rosbag evidence workflows

---

## Current System Capability

The current stack can:

- build the ROS 2 workspace from source
- run deterministic C++ unit tests
- launch a custom C++ ROS 2 kinematic simulator
- launch a Gazebo Sim differential-drive robot with `ros2_control`
- publish odometry, TF, joint states, clock, and simulated lidar
- visualize robot state, odometry, TF, costmaps, plans, and scans in RViz
- bridge Nav2 `/cmd_vel` commands into the stamped command format required by `diff_drive_controller`
- activate the Nav2 lifecycle stack
- publish local and global costmaps in the `odom` frame
- compute global paths through the Nav2 planner
- execute single-goal navigation
- execute waypoint navigation through `/navigate_through_poses`
- test recovery behavior for blocked, difficult, and invalid goals
- record replayable rosbag2/MCAP navigation evidence
- run validation scripts for lifecycle, costmaps, planner/controller setup, and core tests

Current navigation mode:

```txt
odom-frame Nav2 navigation
```

Current limitation:

```txt
No SLAM, AMCL, map frame, or EKF localization is active yet.
Those are planned for the next phase.
```

---

## Repository Structure

```txt
cpp_robotics_sim_foundation/
├── .github/
│   └── workflows/
│       └── ros2_jazzy_ci.yml
│
├── standalone_cpp/
│   ├── include/
│   │   ├── differential_drive/
│   │   └── manipulator/
│   ├── src/
│   │   ├── differential_drive/
│   │   ├── manipulator/
│   │   └── main.cpp
│   └── CMakeLists.txt
│
├── ros2_ws/
│   └── src/cpp_robotics_sim_ros/
│       ├── config/
│       │   ├── sim_params.yaml
│       │   └── ros2_control.yaml
│       ├── include/
│       │   └── cpp_robotics_sim_ros/
│       │       └── core_math.hpp
│       ├── launch/
│       │   ├── sim.launch.py
│       │   ├── description.launch.py
│       │   ├── robot_model_viz.launch.py
│       │   ├── gazebo_spawn.launch.py
│       │   ├── ros2_control.launch.py
│       │   └── nav2_navigation.launch.py
│       ├── nav2/
│       │   └── diffbot_nav2_params.yaml
│       ├── rviz/
│       │   ├── sim_debug.rviz
│       │   └── diffbot_robot_model.rviz
│       ├── scripts/
│       │   ├── cmd_vel_twist_bridge.py
│       │   ├── noisy_odom_node.py
│       │   ├── trajectory_validation_recorder.py
│       │   ├── plot_trajectory_validation.py
│       │   ├── nav2_lifecycle_check.sh
│       │   ├── nav2_costmap_check.sh
│       │   └── nav2_planner_controller_check.sh
│       ├── src/
│       │   ├── sim_node.cpp
│       │   └── performance_benchmark.cpp
│       ├── test/
│       │   └── test_core_math.cpp
│       ├── urdf/
│       │   └── diffbot.urdf
│       ├── worlds/
│       │   └── empty_diffbot_world.sdf
│       ├── xacro/
│       │   └── diffbot.xacro
│       ├── CMakeLists.txt
│       └── package.xml
│
├── scripts/
│   ├── launch_regression.sh
│   └── hard_reset.sh
│
├── data/
│   └── .gitkeep
│
├── plots/
│   ├── .gitkeep
│   └── trajectory_validation.png
│
├── docs/
│   ├── system_architecture.md
│   ├── topic_interface_reference.md
│   └── debugging_and_validation.md
│
├── README.md
└── .gitignore
```

Generated artifacts such as build folders, rosbag data, and generated CSV outputs should stay local unless intentionally committed:

```txt
build/
install/
log/
bags/
*.db3
*.mcap
```

---

## Main Documentation

The public documentation is organized into three core files:

| Document | Purpose |
|---|---|
| [`docs/system_architecture.md`](docs/system_architecture.md) | Explains the full system architecture, runtime layers, command flow, TF ownership, Nav2 integration, validation layers, and current limitations. |
| [`docs/topic_interface_reference.md`](docs/topic_interface_reference.md) | Defines ROS 2 topics, actions, services, frames, parameters, files, scripts, message types, producers, consumers, and validation commands. |
| [`docs/debugging_and_validation.md`](docs/debugging_and_validation.md) | Documents build checks, reset workflow, lifecycle checks, costmap checks, planner/controller checks, recovery tests, waypoint tests, rosbag evidence, CI, and common failure modes. |

---

## Requirements

Recommended environment:

```txt
Ubuntu 24.04 / WSL2 Ubuntu 24.04
ROS 2 Jazzy
Gazebo Sim 8
Python 3
colcon
Git
```

Common ROS packages used by the project include:

```txt
ros-jazzy-navigation2
ros-jazzy-nav2-bringup
ros-jazzy-ros-gz-sim
ros-jazzy-ros-gz-bridge
ros-jazzy-gz-ros2-control
ros-jazzy-ros2-control
ros-jazzy-ros2-controllers
ros-jazzy-xacro
ros-jazzy-robot-state-publisher
ros-jazzy-joint-state-publisher
ros-jazzy-rviz2
ros-jazzy-tf2-tools
python3-matplotlib
```

Install missing dependencies as needed:

```bash
sudo apt update

sudo apt install -y \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-rviz2 \
  ros-jazzy-tf2-tools \
  python3-matplotlib
```

---

## Build

From the repository root:

```bash
cd cpp_robotics_sim_foundation

rm -rf build install log

source /opt/ros/jazzy/setup.bash

rosdep install --from-paths ros2_ws/src --ignore-src -r -y

colcon build --cmake-args -DBUILD_TESTING=ON

source install/setup.bash
```

Expected:

```txt
Summary: 1 package finished
```

Verify installed package executables:

```bash
ros2 pkg executables cpp_robotics_sim_ros
```

Important executables and scripts include:

```txt
cpp_robotics_sim_ros sim_node
cpp_robotics_sim_ros noisy_odom_node.py
cpp_robotics_sim_ros trajectory_validation_recorder.py
cpp_robotics_sim_ros plot_trajectory_validation.py
cpp_robotics_sim_ros performance_benchmark
cpp_robotics_sim_ros cmd_vel_twist_bridge.py
cpp_robotics_sim_ros nav2_lifecycle_check.sh
cpp_robotics_sim_ros nav2_costmap_check.sh
cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

---

## Run Tests

Run the deterministic C++ GoogleTest suite:

```bash
cd cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+

colcon test-result --verbose
```

Expected:

```txt
Summary: 17 tests, 0 errors, 0 failures, 0 skipped
```

The test suite validates deterministic C++ functions such as:

```txt
clamp()
wrapToPi()
integratePose()
```

These tests intentionally do not launch Gazebo, RViz, Nav2, or ROS graph runtime nodes.

---

## Hard Reset

Use the reset script when stale ROS/Gazebo/RViz/controller processes interfere with a clean run:

```bash
cd cpp_robotics_sim_foundation

./scripts/hard_reset.sh
```

The reset script is a development utility. It should not be confused with documentation.

---

## Quickstart: Custom ROS 2 Kinematic Simulator

Launch the custom C++ simulator:

```bash
cd cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Expected interfaces:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

Send a velocity command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Inspect outputs:

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

Expected behavior:

```txt
/robot_pose updates
/odom publishes state
/tf publishes odom -> base_link
/diagnostics reports OK while commands are fresh
robot stops after cmd_timeout when commands stop
```

---

## Quickstart: Gazebo + ros2_control Stack

Launch Gazebo, the robot model, `ros2_control`, `diff_drive_controller`, lidar bridge, and RViz-compatible simulation-time data:

```bash
cd cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Validate controllers:

```bash
ros2 control list_controllers
```

Expected:

```txt
joint_state_broadcaster active
diff_drive_controller active
```

Drive the Gazebo robot:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Check odometry, TF, clock, and lidar:

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo /clock --once
ros2 topic type /scan
ros2 topic echo /scan --once
```

Expected:

```txt
robot moves in Gazebo
/diff_drive_controller/odom updates
odom -> base_link TF updates
/clock publishes simulation time
/scan publishes sensor_msgs/msg/LaserScan
```

---

## Quickstart: Nav2 Navigation Stack

Launch the current Nav2-enabled simulation stack:

```bash
cd cpp_robotics_sim_foundation

./scripts/hard_reset.sh

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros nav2_navigation.launch.py
```

This launch stack starts the Gazebo robot, robot description, `ros2_control`, lidar, Nav2 navigation stack, `/cmd_vel` bridge, lifecycle activation fallback, and RViz-ready topics.

Run the three main Nav2 checks in another terminal:

```bash
cd cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

Expected:

```txt
LIFECYCLE CHECK: PASS
COSTMAP CHECK: PASS
PLANNER/CONTROLLER CHECK: PASS
```

Send a single navigation goal:

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: odom},
    pose: {
      position: {x: 0.8, y: -0.4, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: -0.3826834, w: 0.9238795}
    }
  },
  behavior_tree: ''
}"
```

Expected:

```txt
Goal accepted
/cmd_vel publishes geometry_msgs/msg/Twist
/diff_drive_controller/cmd_vel publishes geometry_msgs/msg/TwistStamped
/diff_drive_controller/odom changes
robot moves in Gazebo/RViz
Goal finishes with SUCCEEDED
```

---

## Nav2 Command Flow

Nav2 publishes an unstamped `Twist` command:

```txt
/cmd_vel
geometry_msgs/msg/Twist
```

The Gazebo `diff_drive_controller` expects a stamped command:

```txt
/diff_drive_controller/cmd_vel
geometry_msgs/msg/TwistStamped
```

The bridge node connects these interfaces:

```txt
Nav2 controller_server
        ↓
/cmd_vel
        ↓
cmd_vel_twist_bridge.py
        ↓
/diff_drive_controller/cmd_vel
        ↓
diff_drive_controller
        ↓
ros2_control
        ↓
gz_ros2_control
        ↓
Gazebo wheel joints
```

This keeps Nav2 interface behavior standard while satisfying the controller's stamped command requirement.

---

## RViz

For Gazebo and Nav2 visualization, RViz should use simulation time and `odom` as the fixed frame.

Open RViz with the saved config:

```bash
cd cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

rviz2 -d ros2_ws/src/cpp_robotics_sim_ros/rviz/sim_debug.rviz --ros-args -p use_sim_time:=true
```

Recommended displays:

```txt
Grid
TF
RobotModel
Odometry
LaserScan
Global Costmap
Local Costmap
Plan / Path
```

Recommended fixed frame:

```txt
odom
```

If RViz shows stale TF or missing data, run a hard reset, relaunch, and verify `/clock` publishes.

---

## rosbag2 / MCAP Navigation Evidence

Record a replayable Nav2 run:

```bash
cd cpp_robotics_sim_foundation

mkdir -p bags/day98_nav2_goal_evidence

ros2 bag record -o bags/day98_nav2_goal_evidence/goal_run_01 \
  /cmd_vel \
  /cmd_vel_nav \
  /cmd_vel_smoothed \
  /diff_drive_controller/cmd_vel \
  /diff_drive_controller/cmd_vel_out \
  /diff_drive_controller/odom \
  /odom \
  /tf \
  /tf_static \
  /scan \
  /plan \
  /plan_smoothed \
  /local_plan \
  /received_global_plan \
  /transformed_global_plan \
  /local_costmap/costmap \
  /local_costmap/costmap_updates \
  /local_costmap/published_footprint \
  /global_costmap/costmap \
  /global_costmap/costmap_updates \
  /global_costmap/published_footprint \
  /behavior_tree_log
```

Inspect the bag folder:

```bash
ros2 bag info bags/day98_nav2_goal_evidence/goal_run_01
```

Replay:

```bash
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock
```

MCAP storage is valid. Run `ros2 bag info` and `ros2 bag play` on the bag folder, not directly on the `.mcap` file.

Do not commit rosbag files to Git.

---

## Validation Workflow

Use this after meaningful changes.

### Build and test

```bash
cd cpp_robotics_sim_foundation

rm -rf build install log

source /opt/ros/jazzy/setup.bash

colcon build --cmake-args -DBUILD_TESTING=ON

source install/setup.bash

colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+

colcon test-result --verbose
```

### Original simulator regression

```bash
./scripts/launch_regression.sh
```

### Nav2 regression

```bash
ros2 launch cpp_robotics_sim_ros nav2_navigation.launch.py
```

In another terminal:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

### Runtime sanity checks

```bash
ros2 action list -t | sort | grep -E "compute_path|follow_path|navigate"
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /bt_navigator
ros2 topic echo --once /scan --field header
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic info /cmd_vel
ros2 topic info /diff_drive_controller/cmd_vel
```

---

## Performance Benchmark

Run the deterministic C++ pose-update benchmark:

```bash
cd cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run cpp_robotics_sim_ros performance_benchmark \
  --output data/day88_performance_results.csv \
  --report docs/performance_report.md
```

Benchmark scope:

```txt
Included:
  deterministic C++ pose integration
  multiple timestep values
  multiple virtual robot states
  wall-clock timing
  estimated real-time factor

Not included:
  Gazebo physics
  ROS middleware
  Nav2
  TF broadcasting
  lidar simulation
  rosbag logging
  RViz rendering
```

---

## Key ROS 2 Interfaces

| Interface | Type | Purpose |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Nav2/custom simulator velocity command |
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/msg/TwistStamped` | Gazebo diff-drive controller input |
| `/diff_drive_controller/odom` | `nav_msgs/msg/Odometry` | Gazebo controller odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | Simulated lidar output |
| `/tf` | `tf2_msgs/msg/TFMessage` | Dynamic transforms |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | Static robot transforms |
| `/local_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | Nav2 local costmap |
| `/global_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | Nav2 global costmap |
| `/plan` | `nav_msgs/msg/Path` | Nav2 global path |
| `/local_plan` | `nav_msgs/msg/Path` | Nav2 local controller path |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Single-goal navigation action |
| `/navigate_through_poses` | `nav2_msgs/action/NavigateThroughPoses` | Waypoint navigation action |
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | Planner path computation action |
| `/follow_path` | `nav2_msgs/action/FollowPath` | Controller path-following action |

Full details are documented in [`docs/topic_interface_reference.md`](docs/topic_interface_reference.md).

---

## Transform Ownership

The project has two runtime modes with different transform ownership.

Custom kinematic simulator stack:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

Gazebo / ros2_control / Nav2 stack:

```txt
diff_drive_controller owns:
  odom -> base_link

joint_state_broadcaster owns:
  /joint_states

robot_state_publisher owns:
  base_link -> robot link transforms
```

Important rule:

```txt
Do not run sim_node and diff_drive_controller together as simultaneous publishers of odom -> base_link.
```

Current navigation frame chain:

```txt
odom -> base_link -> lidar_link
```

Future localization frame chain:

```txt
map -> odom -> base_link
```

---

## Known Limitations

Current limitations:

- Nav2 currently runs in `odom` frame only.
- No persistent map is active yet.
- SLAM Toolbox is not integrated yet.
- AMCL is not integrated yet.
- EKF fusion is not active yet.
- Dynamic obstacle benchmarking is not implemented yet.
- Simulation-level CI does not yet launch Gazebo/Nav2 in GitHub Actions.
- Docker/devcontainer setup is planned but not complete.
- Bag data is generated locally and intentionally ignored by Git.

---

## Planned Enhancements

Next planned phase:

```txt
Days 101-120:
  SLAM and mapping
  map saving/loading
  AMCL localization
  EKF localization readiness
  stronger scenario validation
  public v1.0 cleanup
```

Later planned improvements:

```txt
Docker/devcontainer support
playable teleop release
PS4/controller support
scenario runner
dynamic obstacle tests
sensor noise and physics parameter sweeps
rosbag replay-based regression
performance profiling for Gazebo/Nav2 runtime
public portfolio demo videos
```

---

## GitHub Actions CI

The repository includes a ROS 2 Jazzy GitHub Actions workflow:

```txt
.github/workflows/ros2_jazzy_ci.yml
```

Current CI validates:

```txt
checkout
ROS 2 Jazzy dependency installation
colcon build
GoogleTest execution
test log upload
```

Current CI does not yet validate:

```txt
Gazebo launch
controller activation
Nav2 lifecycle
/scan runtime behavior
costmap runtime behavior
full navigation scenarios
```

Those are planned for later simulation-release engineering.

---

## Engineering Summary

This project demonstrates a robotics simulation stack that is:

```txt
buildable
testable
launchable
visualizable
controllable
measurable
debuggable
replayable
documented
```

The current system demonstrates robot modeling, Gazebo control, lidar sensing, odometry and TF validation, GoogleTest coverage, continuous integration, C++ performance benchmarking, and Nav2 integration with lifecycle, costmap, planner, controller, goal-navigation, recovery, waypoint, and rosbag evidence.

The next phase will move from odom-frame navigation toward map-based SLAM/localization and stronger autonomy validation.
