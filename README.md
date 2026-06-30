# C++ / ROS 2 Robotics Simulation Foundation

![ROS 2 Jazzy CI](https://github.com/Devansh-Mishra-30/cpp_robotics_sim_foundation/actions/workflows/ros2_jazzy_ci.yml/badge.svg)

This repository contains a C++ and ROS 2 robotics simulation project focused on mobile robot state updates, differential-drive kinematics, ROS 2 messaging, odometry, TF frames, runtime configuration, launch workflows, QoS profiles, rosbag2, diagnostics, RViz visualization, URDF/Xacro robot modeling, Gazebo simulation, `ros2_control`, differential-drive control, simulated lidar, validation, uncertainty modeling, trajectory analysis, automated testing, CI, performance benchmarking, and engineering documentation.

The project started as a standalone C++ robotics simulation foundation and has been extended into a ROS 2 + Gazebo robot simulation stack with robot description, physics-based motion, controller integration, sensor output, noisy odometry generation, trajectory validation, plotting, GoogleTest, GitHub Actions CI, performance benchmarking, and validation-focused documentation.

---

## Current Checkpoint

Current project state: **complete through Day 90**.

The current stack includes:

```txt
standalone C++ robotics simulation modules
ROS 2 C++ kinematic simulator
launch files and YAML runtime configuration
QoS profiles
rosbag2 workflow
RViz visualization
runtime diagnostics
launch regression script
URDF/Xacro robot model
robot_state_publisher and joint-state workflows
Gazebo Sim spawn workflow
ros2_control + controller_manager
joint_state_broadcaster
diff_drive_controller
Gazebo-driven differential-drive motion
simulated lidar sensor
/scan LaserScan bridge
/clock simulation-time bridge
Nav2 architecture notes
state-estimation and EKF notes
noisy odometry node
trajectory validation recorder
trajectory validation plot/report generation
GoogleTest unit tests
GitHub Actions CI
deterministic C++ performance benchmark
Day 90 final assessment documentation
```

The final public v1.0 release rewrite will happen later. For now, this README preserves the roadmap/checkpoint structure while keeping the project reproducible and technically clear.

---

## Active Development Environment

The active working copy is inside the WSL/Linux filesystem:

```txt
/home/devansh/robotics_projects/cpp_robotics_sim_foundation
```

Short path:

```txt
~/robotics_projects/cpp_robotics_sim_foundation
```

Recommended editor workflow:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation
code .
```

Do not use the old Windows-mounted path as the active development repo.

---

## Project Structure

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
│       │       └── day86_testable_core.hpp
│       ├── launch/
│       │   ├── sim.launch.py
│       │   ├── description.launch.py
│       │   ├── robot_model_viz.launch.py
│       │   ├── gazebo_spawn.launch.py
│       │   └── ros2_control.launch.py
│       ├── rviz/
│       │   ├── sim_debug.rviz
│       │   └── diffbot_robot_model.rviz
│       ├── scripts/
│       │   ├── noisy_odom_node.py
│       │   ├── trajectory_validation_recorder.py
│       │   └── plot_trajectory_validation.py
│       ├── src/
│       │   ├── sim_node.cpp
│       │   └── day88_performance_benchmark.cpp
│       ├── test/
│       │   └── test_day86_core.cpp
│       ├── urdf/
│       │   └── diffbot.urdf
│       ├── xacro/
│       │   └── diffbot.xacro
│       ├── worlds/
│       │   └── empty_diffbot_world.sdf
│       ├── CMakeLists.txt
│       └── package.xml
│
├── scripts/
│   └── day68_launch_regression.sh
│
├── data/
│   └── .gitkeep
│
├── plots/
│   ├── .gitkeep
│   └── trajectory_validation.png
│
└── docs/
    ├── daily_documentation.md
    ├── system_architecture.md
    ├── debugging_and_validation.md
    ├── topic_interface_reference.md
    ├── nav2_architecture.md
    ├── state_estimation_notes.md
    ├── trajectory_validation_report.md
    ├── day86_gtest_report.md
    ├── day87_ci_report.md
    └── performance_report.md
```

Main layers:

```txt
standalone_cpp/  -> pure C++ robotics simulation modules
ros2_ws/         -> ROS 2 simulator, robot model, Gazebo, ros2_control, RViz, sensor integration, validation nodes, tests, and benchmark executable
scripts/         -> regression and validation scripts
data/            -> local validation CSV output directory
plots/           -> validation plots
docs/            -> architecture, debugging, validation, topic interface, navigation, estimation, testing, CI, performance, and daily documentation
.github/         -> GitHub Actions CI workflow
```

---

## Quickstart: Build ROS 2 Workspace

From the ROS 2 workspace:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

rm -rf build install log

source /opt/ros/jazzy/setup.bash

colcon build --cmake-args -DBUILD_TESTING=ON

source install/setup.bash
```

Expected:

```txt
Summary: 1 package finished
```

Verify installed executables:

```bash
ros2 pkg executables cpp_robotics_sim_ros
```

Expected important executables include:

```txt
cpp_robotics_sim_ros sim_node
cpp_robotics_sim_ros noisy_odom_node.py
cpp_robotics_sim_ros trajectory_validation_recorder.py
cpp_robotics_sim_ros plot_trajectory_validation.py
cpp_robotics_sim_ros day88_performance_benchmark
```

---

## Quickstart: Run GoogleTest

The project includes GoogleTest unit tests for deterministic C++ math and pose integration.

Run:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+

colcon test-result --verbose
```

Expected:

```txt
Summary: 17 tests, 0 errors, 0 failures, 0 skipped
```

The current GoogleTest suite validates:

```txt
clamp()
wrapToPi()
integratePose()
```

These tests are intentionally independent of ROS 2 runtime nodes and Gazebo so they can run quickly and deterministically.

---

## Quickstart: Original ROS 2 Kinematic Simulator

Launch the custom C++ simulator:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Expected node:

```txt
/sim_node
```

Expected runtime interfaces:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

Send a command from a second terminal:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Inspect state:

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

Expected behavior:

```txt
robot pose updates
/odom publishes updated state
/tf updates odom -> base_link
/diagnostics reports OK while commands are fresh
robot stops after cmd_timeout when commands stop
```

---

## Quickstart: Gazebo Control and Lidar Stack

Launch the Gazebo physics simulation, `ros2_control`, diff-drive controller, and lidar bridge:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Expected:

```txt
Gazebo opens
diffbot spawns
controller_manager starts
joint_state_broadcaster becomes active
diff_drive_controller becomes active
/scan publishes LaserScan data
/clock publishes simulation time
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

Validate hardware interfaces:

```bash
ros2 control list_hardware_interfaces
```

Expected wheel interfaces include:

```txt
left_wheel_joint/velocity command interface
right_wheel_joint/velocity command interface
left_wheel_joint/position state interface
left_wheel_joint/velocity state interface
right_wheel_joint/position state interface
right_wheel_joint/velocity state interface
```

Drive the Gazebo robot:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Check controller odometry:

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

Check lidar:

```bash
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Expected:

```txt
/scan is sensor_msgs/msg/LaserScan
lidar_link exists in TF
robot moves in Gazebo
/diff_drive_controller/odom updates
```

---

## Quickstart: Noisy Odometry and Trajectory Validation

The validation stack compares commanded motion, actual Gazebo odometry, and intentionally noisy odometry.

### Terminal 1: Launch Gazebo control stack

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

### Terminal 2: Run noisy odometry node

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

Expected:

```txt
Day 83 noisy odometry node started
Subscribing: /diff_drive_controller/odom
Publishing:  /odom_noisy
```

### Terminal 3: Run trajectory validation recorder

Run from the repository root so the CSV writes to root `data/`:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash

ros2 run cpp_robotics_sim_ros trajectory_validation_recorder.py
```

Expected:

```txt
Day 84 trajectory validation recorder started
Command topic:     /diff_drive_controller/cmd_vel
Actual odom topic: /diff_drive_controller/odom
Noisy odom topic:  /odom_noisy
Writing CSV:       data/day84_trajectory_validation.csv
Sample rate:       20.0 Hz
```

### Terminal 4: Command robot motion

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

Let it run for 10 to 15 seconds, then stop the publisher, recorder, and noisy odometry node.

### Verify CSV

From repository root:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

ls data/day84_trajectory_validation.csv
head data/day84_trajectory_validation.csv
wc -l data/day84_trajectory_validation.csv
```

Expected CSV header:

```txt
time_sec,cmd_linear_x,cmd_angular_z,actual_x,actual_y,actual_yaw,actual_linear_x,actual_angular_z,noisy_x,noisy_y,noisy_yaw
```

### Generate plot and report

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

Expected outputs:

```txt
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

Validate:

```bash
ls plots/trajectory_validation.png
ls docs/trajectory_validation_report.md
ls -lh plots/trajectory_validation.png

grep -n "actual path length" docs/trajectory_validation_report.md
grep -n "mean position noise error" docs/trajectory_validation_report.md
grep -n "max actual linear velocity" docs/trajectory_validation_report.md
grep -n "max actual yaw rate" docs/trajectory_validation_report.md
```

---

## Quickstart: Performance Benchmark

The project includes a deterministic C++ benchmark for the pose-update layer.

Run:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash

ros2 run cpp_robotics_sim_ros day88_performance_benchmark --output data/day88_performance_results.csv --report docs/performance_report.md
```

Expected generated outputs:

```txt
data/day88_performance_results.csv
docs/performance_report.md
```

Observed Day 88 benchmark result:

```txt
dt=0.1    steps=100     mean wall time ≈ 1.83 ms     RTF ≈ 5684.98
dt=0.01   steps=1000    mean wall time ≈ 17.40 ms    RTF ≈ 574.99
dt=0.001  steps=10000   mean wall time ≈ 174.74 ms   RTF ≈ 57.23
```

This benchmark does not include Gazebo physics, ROS middleware overhead, TF broadcasting, sensor simulation, RViz, rosbag logging, or Nav2. It is the first deterministic C++ timing baseline.

---

## GitHub Actions CI

The repository includes GitHub Actions CI:

```txt
.github/workflows/ros2_jazzy_ci.yml
```

The CI workflow runs on:

```txt
ubuntu-24.04
ROS 2 Jazzy
```

Current CI verifies:

```txt
ROS 2 workspace builds
GoogleTest target builds
GoogleTest unit tests pass
test logs are uploaded as artifacts
```

The current CI does not yet run full Gazebo launch regression, controller activation checks, `/scan` runtime checks, Nav2 tests, or full simulation scenario scoring.

---

## RViz for Gazebo Control Stack

When visualizing Gazebo-driven data, RViz must use simulation time.

Start RViz with:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Recommended RViz displays:

```txt
Grid
TF
RobotModel
Odometry
LaserScan
```

Recommended settings:

```txt
Fixed Frame: odom
RobotModel Description Topic: /robot_description
Odometry Topic: /diff_drive_controller/odom
LaserScan Topic: /scan
LaserScan Reliability Policy: Best Effort if needed
```

If RViz shows stale TF errors such as:

```txt
TF_OLD_DATA ignoring data from the past for frame base_link
```

cleanly stop old Gazebo/RViz/ROS processes, relaunch the Gazebo control stack, verify `/clock`, and reopen RViz with `use_sim_time:=true`.

---

## Robot Model, RViz RobotModel, and Gazebo Usage

Robot description files:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

The robot model defines:

```txt
base_link
├── left_wheel_link
├── right_wheel_link
├── caster_link
└── lidar_link
```

Joints:

```txt
left_wheel_joint   continuous
right_wheel_joint  continuous
caster_joint       fixed
lidar_joint        fixed
```

Launch robot description stack:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Expected nodes:

```txt
/robot_state_publisher
/joint_state_publisher
```

Expected topics:

```txt
/robot_description
/joint_states
/tf
/tf_static
```

Launch RViz RobotModel stack:

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

This starts the original kinematic simulator, robot description publishers, joint state publisher, and RViz.

Launch Gazebo spawn-only workflow:

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

This proves that the robot model can be spawned into Gazebo from `/robot_description`.

Launch Gazebo control workflow:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

This starts Gazebo, spawns the robot, loads `controller_manager`, activates `joint_state_broadcaster` and `diff_drive_controller`, bridges `/clock`, and bridges lidar data into `/scan`.

---

## Two Runtime Stacks

The project has two related but separate runtime stacks.

### Custom Kinematic Simulator Stack

```txt
/cmd_vel
    -> sim_node
    -> /robot_pose
    -> /odom
    -> /tf
    -> /diagnostics
```

This stack is useful for learning:

```txt
C++ simulation logic
planar kinematics
custom odometry publishing
custom TF broadcasting
diagnostics
runtime parameters
launch workflows
validation discipline
```

### Gazebo ros2_control Stack

```txt
/diff_drive_controller/cmd_vel
    -> diff_drive_controller
    -> ros2_control
    -> gz_ros2_control
    -> Gazebo wheel joints
    -> /diff_drive_controller/odom
    -> /tf
    -> /joint_states
```

This stack is the physics-based Gazebo control workflow.

Important:

```txt
sim_node does not move Gazebo.
Gazebo movement uses diff_drive_controller, ros2_control, and gz_ros2_control.
```

---

## Transform Ownership

The transform owner changes depending on which stack is running.

Kinematic simulator stack:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

Gazebo control stack:

```txt
diff_drive_controller owns:
  odom -> base_link

joint_state_broadcaster owns:
  /joint_states

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

Important rule:

```txt
Do not run sim_node and diff_drive_controller together as simultaneous publishers of odom -> base_link.
```

Full frame tree:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

---

## Gazebo, ros2_control, and Lidar Architecture

Gazebo control flow:

```txt
/diff_drive_controller/cmd_vel
        ↓
diff_drive_controller
        ↓
left_wheel_joint and right_wheel_joint velocity commands
        ↓
gz_ros2_control
        ↓
Gazebo simulated wheel joints
        ↓
robot moves in Gazebo
        ↓
/diff_drive_controller/odom + /tf
```

Lidar sensor flow:

```txt
Gazebo gpu_lidar sensor on lidar_link
        ↓
Gazebo /scan topic
        ↓
ros_gz_bridge parameter_bridge
        ↓
ROS /scan topic
        ↓
sensor_msgs/msg/LaserScan
        ↓
RViz LaserScan display
```

Clock flow:

```txt
Gazebo simulation clock
        ↓
ros_gz_bridge
        ↓
ROS /clock
        ↓
RViz and ROS nodes using use_sim_time
```

Noisy odometry flow:

```txt
/diff_drive_controller/odom
        ↓
noisy_odom_node.py
        ↓
/odom_noisy
```

Trajectory validation flow:

```txt
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/odom_noisy
        ↓
trajectory_validation_recorder.py
        ↓
data/day84_trajectory_validation.csv
        ↓
plot_trajectory_validation.py
        ↓
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

Important:

```txt
/odom_noisy does not move Gazebo.
It is a noisy feedback stream for validation and future localization work.
```

---

## Navigation and State Estimation Readiness

Navigation notes:

```txt
docs/nav2_architecture.md
```

State estimation notes:

```txt
docs/state_estimation_notes.md
```

Main Nav2 mental model:

```txt
localization tells the robot where it is
costmaps tell the robot where it is safe to move
planner decides the path
controller sends velocity commands
recovery handles failure cases
```

Important navigation frame chain:

```txt
map -> odom -> base_link
```

State-estimation mental model:

```txt
state estimation = estimating robot pose and velocity from imperfect measurements
odometry         = smooth short-term motion estimate that drifts
IMU              = angular velocity and acceleration sensing
sensor fusion    = combining multiple noisy measurements
EKF              = prediction + correction using covariance
covariance       = uncertainty of pose or velocity measurement
```

---

## Differential-Drive Math

For wheel radius `r`, wheel separation `L`, right wheel angular velocity `wr`, and left wheel angular velocity `wl`:

```txt
v = r / 2 * (wr + wl)
omega = r / L * (wr - wl)
```

Inverse mapping from commanded body velocity to wheel velocity:

```txt
wr = (v + omega * L / 2) / r
wl = (v - omega * L / 2) / r
```

For a constant velocity command:

```txt
linear velocity = 0.25 m/s
yaw rate        = 0.2 rad/s
```

Expected turning radius:

```txt
R = v / omega = 0.25 / 0.2 = 1.25 m
```

This produces a circular trajectory in the validation plot.

---

## Runtime Configuration

Original simulator parameters are stored in:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

Current simulator parameters:

```yaml
sim_node:
  ros__parameters:
    dt: 0.1
    initial_x: 0.0
    initial_y: 0.0
    initial_theta: 0.0
    cmd_timeout: 0.5
    max_linear_velocity: 0.5
    max_angular_velocity: 0.8
```

Gazebo controller parameters are stored in:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
```

Core controller configuration:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

diff_drive_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
    wheel_separation: 0.34
    wheel_radius: 0.07
    odom_frame_id: odom
    base_frame_id: base_link
    enable_odom_tf: true
    publish_limited_velocity: true
    cmd_vel_timeout: 0.5
    use_stamped_vel: true
```

Noisy odometry defaults:

```txt
input_topic                    = /diff_drive_controller/odom
output_topic                   = /odom_noisy
position_noise_std             = 0.02 m
yaw_noise_std                  = 0.02 rad
linear_velocity_noise_std      = 0.02 m/s
angular_velocity_noise_std     = 0.02 rad/s
random_seed                    = 42
```

Trajectory recorder defaults:

```txt
cmd_topic          = /diff_drive_controller/cmd_vel
actual_odom_topic  = /diff_drive_controller/odom
noisy_odom_topic   = /odom_noisy
output_csv         = data/day84_trajectory_validation.csv
sample_rate_hz     = 20.0
```

---

## ROS 2 Topics

| Topic                                | Type                                  | Producer                                                     | Purpose                                                         |
| ------------------------------------ | ------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------- |
| `/cmd_vel`                           | `geometry_msgs/msg/Twist`             | external command source                                      | Velocity command input for `sim_node`                           |
| `/robot_pose`                        | `geometry_msgs/msg/Pose2D`            | `sim_node`                                                   | Simple 2D robot pose                                            |
| `/odom`                              | `nav_msgs/msg/Odometry`               | `sim_node`                                                   | Kinematic simulator odometry                                    |
| `/tf`                                | `tf2_msgs/msg/TFMessage`              | `sim_node`, `robot_state_publisher`, `diff_drive_controller` | Transform tree data                                             |
| `/tf_static`                         | `tf2_msgs/msg/TFMessage`              | `robot_state_publisher`                                      | Fixed transform tree data                                       |
| `/diagnostics`                       | `diagnostic_msgs/msg/DiagnosticArray` | `sim_node`                                                   | Runtime health and simulator diagnostics                        |
| `/robot_description`                 | `std_msgs/msg/String`                 | `robot_state_publisher`                                      | Robot model XML                                                 |
| `/joint_states`                      | `sensor_msgs/msg/JointState`          | `joint_state_publisher` or `joint_state_broadcaster`         | Joint positions/velocities for robot links                      |
| `/dynamic_joint_states`              | `control_msgs/msg/DynamicJointState`  | `joint_state_broadcaster`                                    | Detailed ros2_control joint interface states                    |
| `/diff_drive_controller/cmd_vel`     | `geometry_msgs/msg/TwistStamped`      | command source                                               | Gazebo diff-drive command input                                 |
| `/diff_drive_controller/odom`        | `nav_msgs/msg/Odometry`               | `diff_drive_controller`                                      | Gazebo diff-drive odometry                                      |
| `/diff_drive_controller/cmd_vel_out` | `geometry_msgs/msg/TwistStamped`      | `diff_drive_controller`                                      | Limited command output                                          |
| `/odom_noisy`                        | `nav_msgs/msg/Odometry`               | `noisy_odom_node.py`                                         | Noisy odometry stream generated from Gazebo controller odometry |
| `/scan`                              | `sensor_msgs/msg/LaserScan`           | `ros_gz_bridge` from Gazebo lidar                            | Simulated lidar scan                                            |
| `/clock`                             | `rosgraph_msgs/msg/Clock`             | `ros_gz_bridge` from Gazebo                                  | Simulation time                                                 |

---

## Standalone C++ Modules

The standalone C++ project is split into two main simulation modules.

Differential-drive module:

```txt
standalone_cpp/include/differential_drive/
standalone_cpp/src/differential_drive/
```

This module contains the differential-drive mobile robot simulation, including wheel-speed conversion, pose updates, trajectory metrics, validation scenarios, and target tracking.

Manipulator module:

```txt
standalone_cpp/include/manipulator/
standalone_cpp/src/manipulator/
```

This module contains the manipulator joint-state simulation, including joint position updates, joint velocity integration, and joint limit clamping.

`standalone_cpp/src/main.cpp` is the combined demo runner that executes both the differential-drive and manipulator demos.

---

## Diagnostics

The original simulator publishes structured runtime diagnostics on:

```txt
/diagnostics
```

Message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Check diagnostics:

```bash
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

The diagnostic report includes:

```txt
dt
cmd_timeout
time_since_cmd
timeout_active
linear_velocity
angular_velocity
max_linear_velocity
max_angular_velocity
pose_x
pose_y
pose_theta
callback_time_ms
average_callback_time_ms
max_callback_time_ms
timing_budget_ms
callback_count
```

Diagnostic status:

```txt
OK   when simulator is running with fresh command input
WARN when cmd_vel timeout is active
```

---

## rosbag2 Recording and Replay

Record simulator topics:

```bash
mkdir -p bags
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
```

Inspect:

```bash
ros2 bag info bags/day65_baseline
```

Replay:

```bash
ros2 bag play bags/day65_baseline
```

Expected recorded topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

Actual bag data is stored locally under `bags/` and should not be committed to Git.

---

## Launch Regression

The project includes a repeatable launch regression script:

```txt
scripts/day68_launch_regression.sh
```

Run it from the repository root:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

The regression validates the original ROS 2 kinematic simulator stack and should still pass after Gazebo, control, sensor, uncertainty, validation, testing, CI, and benchmarking changes.

---

## Verification Workflow

Use this after meaningful source, launch, config, robot description, world, controller, sensor, validation, test, CI, benchmark, or documentation changes.

### Build

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

rm -rf build install log

source /opt/ros/jazzy/setup.bash

colcon build --cmake-args -DBUILD_TESTING=ON

source install/setup.bash
```

### Test

```bash
colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+

colcon test-result --verbose
```

Expected:

```txt
Summary: 17 tests, 0 errors, 0 failures, 0 skipped
```

### Benchmark

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

ros2 run cpp_robotics_sim_ros day88_performance_benchmark --output data/day88_performance_results.csv --report docs/performance_report.md
```

### Original Simulator Checks

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
ros2 topic list
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

### Robot Description Checks

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py

ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt
grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt

ros2 topic echo /joint_states --once
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

### Gazebo Control and Sensor Checks

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py

ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic echo /diff_drive_controller/odom --once
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 topic echo /clock --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Drive test:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Expected:

```txt
robot moves in Gazebo
/diff_drive_controller/odom updates
/scan remains active
RViz tracks Gazebo motion when use_sim_time is true
```

### Noisy Odometry Checks

```bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

In another terminal:

```bash
ros2 topic list | grep odom
ros2 topic echo /odom_noisy --once
ros2 topic echo /odom_noisy --once | grep -A 40 "covariance"
```

Expected:

```txt
/odom_noisy exists
/odom_noisy publishes nav_msgs/msg/Odometry
pose and twist covariance values are populated
```

### Trajectory Validation Checks

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash

ros2 run cpp_robotics_sim_ros trajectory_validation_recorder.py
```

After commanding robot motion, verify:

```bash
ls data/day84_trajectory_validation.csv
head data/day84_trajectory_validation.csv
wc -l data/day84_trajectory_validation.csv
```

Generate plot and report:

```bash
python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

Verify:

```bash
ls plots/trajectory_validation.png
ls docs/trajectory_validation_report.md

grep -n "actual path length" docs/trajectory_validation_report.md
grep -n "mean position noise error" docs/trajectory_validation_report.md
grep -n "max actual linear velocity" docs/trajectory_validation_report.md
grep -n "max actual yaw rate" docs/trajectory_validation_report.md
```

### Regression Check

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation
./scripts/day68_launch_regression.sh
```

---

## Documentation

Primary documentation:

```txt
docs/daily_documentation.md
docs/system_architecture.md
docs/debugging_and_validation.md
docs/topic_interface_reference.md
```

Supporting documentation:

```txt
docs/nav2_architecture.md
docs/state_estimation_notes.md
docs/trajectory_validation_report.md
docs/day86_gtest_report.md
docs/day87_ci_report.md
docs/performance_report.md
```

Current consolidation plan:

```txt
Day 100: consolidate documentation into cleaner industry-standard structure
Day 120: final public v1.0 release rewrite
```

At Day 120, the project will be rewritten from roadmap-style documentation into public implementation-style documentation.

---

## Engineering Focus

This project demonstrates:

* robotics simulation architecture
* C++ simulation design
* differential-drive kinematics
* manipulator joint-state simulation
* ROS 2 C++ node development
* topic-based robot control
* odometry publishing
* TF frame broadcasting
* diagnostics publishing
* launch-based runtime workflows
* YAML runtime configuration
* launch argument overrides
* QoS profile design
* rosbag2 recording and replay
* RViz2 visual debugging
* RViz RobotModel visualization
* launch regression testing
* URDF robot modeling
* Xacro robot modeling
* robot state publishing
* joint state publishing
* Gazebo world setup
* Gazebo robot spawning
* `ros2_control` hardware interface design
* `controller_manager` workflow
* `joint_state_broadcaster` integration
* `diff_drive_controller` integration
* Gazebo differential-drive motion
* simulated lidar sensor modeling
* `/scan` bridging with `ros_gz_bridge`
* `/clock` and simulation-time synchronization
* Nav2 architecture understanding
* state estimation and EKF concepts
* odometry noise modeling
* covariance interpretation
* noisy odometry publishing
* trajectory validation recording
* CSV-based validation workflow
* commanded vs actual trajectory comparison
* actual vs noisy odometry comparison
* validation plotting
* GoogleTest unit testing
* GitHub Actions CI
* performance benchmarking
* validation reports
* parameterized runtime behavior
* safety guards
* debugging discipline
* regression testing
* engineering documentation

---

## Current Status

| Area                                  | Status              |
| ------------------------------------- | ------------------- |
| Standalone C++ simulator              | Complete foundation |
| ROS 2 node integration                | Complete foundation |
| Launch workflow                       | Added               |
| YAML configuration                    | Added               |
| Launch argument overrides             | Added               |
| QoS profiles                          | Added               |
| rosbag2 workflow                      | Added               |
| RViz2 odometry/TF visualization       | Added               |
| Diagnostics                           | Added               |
| Launch regression                     | Added               |
| Topic interface reference             | Added               |
| URDF robot model                      | Added               |
| Xacro robot description               | Added               |
| `robot_state_publisher` workflow      | Added               |
| `joint_state_publisher` workflow      | Added               |
| RViz RobotModel visualization         | Added               |
| Gazebo world and robot spawn          | Added               |
| `ros2_control` integration            | Added               |
| `joint_state_broadcaster` integration | Added               |
| Gazebo differential-drive control     | Added               |
| `diff_drive_controller` odometry      | Added               |
| Simulated lidar sensor                | Added               |
| `/scan` LaserScan bridge              | Added               |
| `/clock` simulation-time bridge       | Added               |
| Nav2 architecture notes               | Added               |
| State estimation and EKF notes        | Added               |
| Noisy odometry node                   | Added               |
| `/odom_noisy` topic                   | Added               |
| Trajectory validation recorder        | Added               |
| Validation CSV workflow               | Added               |
| Trajectory validation plot            | Added               |
| Trajectory validation report          | Added               |
| GoogleTest unit tests                 | Added               |
| GitHub Actions CI                     | Added               |
| Performance benchmark                 | Added               |
| Day 89 validation checkpoint          | Added               |
| Day 90 final assessment               | Added               |
| Nav2 integration                      | Planned             |
| SLAM/localization                     | Planned             |
| Full launch/simulation CI regression  | Planned             |
| Docker/devcontainer                   | Planned             |
| Public v1.0 release rewrite           | Planned             |

Current milestone:

```txt
Days 1-90 complete:
C++ foundation, ROS 2 integration, robot modeling, Gazebo control, lidar, noisy odometry, validation plotting, GoogleTest, GitHub Actions CI, performance benchmarking, and Day 90 assessment.
```

Next planned phase:

```txt
Days 91-100:
Nav2 working integration and documentation consolidation.
```

---

## Day 90 Interview Summary

I built a modular C++ robotics simulation foundation with standalone differential-drive and manipulator modules, then integrated the mobile robot simulator into ROS 2 using `/cmd_vel`, `/robot_pose`, `/odom`, TF, and `/diagnostics`.

I extended the project into a robot modeling and simulation stack with URDF, Xacro, `robot_state_publisher`, joint state publishing, RViz RobotModel visualization, Gazebo spawning, `ros2_control` hardware interfaces, `controller_manager`, `joint_state_broadcaster`, `diff_drive_controller`, Gazebo-driven wheel motion, simulated lidar, `/scan` bridging through `ros_gz_bridge`, and simulation-time synchronization through `/clock`.

The project has two clearly separated runtime stacks. In the custom kinematic simulator stack, `sim_node` owns `odom -> base_link` and publishes custom odometry, TF, pose, and diagnostics. In the Gazebo control stack, `diff_drive_controller` owns `odom -> base_link`, `joint_state_broadcaster` owns `/joint_states`, `robot_state_publisher` owns the robot link transforms below `base_link`, and Gazebo motion is driven through `ros2_control` and `gz_ros2_control`.

For autonomy readiness, I added Nav2 architecture notes covering `map -> odom -> base_link`, global and local costmaps, planner/controller separation, recovery behaviors, and lifecycle nodes. I also added state-estimation notes covering odometry drift, sensor fusion, EKF prediction/correction, covariance, and simulation noise.

For validation readiness, I added a noisy odometry node that subscribes to `/diff_drive_controller/odom`, adds controlled Gaussian noise to position, yaw, linear velocity, and angular velocity, fills covariance, and republishes the result on `/odom_noisy`. I then added a trajectory validation recorder that records `/diff_drive_controller/cmd_vel`, `/diff_drive_controller/odom`, and `/odom_noisy` to CSV. The plotting/report script generates a trajectory validation plot and Markdown report with path length, final pose, noise error, velocity, and yaw-rate metrics.

For software-quality readiness, I added GoogleTest unit tests for deterministic C++ math functions such as command clamping, angle wrapping, and pose integration. I then added GitHub Actions CI so the ROS 2 Jazzy workspace builds and the GoogleTest suite runs automatically on GitHub. Finally, I added a deterministic C++ performance benchmark to compare different timestep settings and generate a timing report.

This project now demonstrates not just that a robot moves in simulation, but that the simulated behavior can be modeled, controlled, measured, tested, benchmarked, documented, and explained as an engineering system.
