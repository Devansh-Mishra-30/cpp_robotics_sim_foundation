# C++ / ROS 2 Robotics Simulation Foundation

This repository contains a C++ and ROS 2 robotics simulation project focused on mobile robot state updates, differential-drive kinematics, ROS 2 messaging, odometry, TF frames, runtime configuration, launch workflows, QoS profiles, safety validation, performance timing, debugging, and regression testing.

The project started as a standalone C++ robotics simulation foundation and was extended into a ROS 2 C++ simulator.

---

## Project Structure

This repository is organized into three main layers:

```txt
standalone_cpp/  -> Pure C++ robotics simulation modules
ros2_ws/         -> ROS 2 C++ simulator integration
docs/            -> Architecture, debugging, regression, integration, and daily documentation
```

### Standalone C++ Modules

The standalone C++ project is split into two main simulation modules:

```txt
standalone_cpp/include/differential_drive/
standalone_cpp/src/differential_drive/
```

This module contains the differential-drive mobile robot simulation, including wheel-speed conversion, pose updates, trajectory metrics, validation scenarios, and target tracking.

```txt
standalone_cpp/include/manipulator/
standalone_cpp/src/manipulator/
```

This module contains the manipulator joint-state simulation, including joint position updates, joint velocity integration, and joint limit clamping.

`standalone_cpp/src/main.cpp` is the combined demo runner that executes both the differential-drive and manipulator demos.

### ROS 2 Integration

The ROS 2 layer is located at:

```txt
ros2_ws/src/cpp_robotics_sim_ros/
```

It exposes the mobile robot simulation through standard ROS 2 interfaces:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

The ROS 2 node subscribes to velocity commands, updates pose, publishes odometry, and broadcasts the `odom -> base_link` transform.

---

### Documentation

See:

```txt
docs/daily_documentation.md
docs/system_architecture.md
docs/debugging_and_validation.md
```

The daily engineering log tracks the roadmap from C++ fundamentals through ROS 2 launch, YAML parameters, launch arguments, QoS profiles, rosbag2 recording/replay, and RViz2 visualization.
---

## Current Features

* C++ mobile robot simulation core
* C++ manipulator joint-state mini-simulation
* Differential-drive wheel-speed to body-velocity conversion
* Pose integration using `x`, `y`, and `theta`
* Trajectory logging and metrics
* Validation scenarios and regression checklist
* ROS 2 `rclcpp` node
* `/cmd_vel` subscriber using `geometry_msgs/msg/Twist`
* `/robot_pose` publisher using `geometry_msgs/msg/Pose2D`
* `/odom` publisher using `nav_msgs/msg/Odometry`
* `/tf` broadcaster for `odom -> base_link`
* ROS 2 launch workflow using `sim.launch.py`
* YAML runtime configuration using `config/sim_params.yaml`
* Launch argument overrides for initial pose, timestep, timeout, and velocity limits
* Explicit ROS 2 QoS profiles for `/cmd_vel`, `/robot_pose`, and `/odom`
* rosbag2 recording and replay workflow for `/cmd_vel`, `/robot_pose`, `/odom`, and `/tf`
* RViz2 visualization workflow with saved `sim_debug.rviz` config
* `/diagnostics` publisher using `diagnostic_msgs/msg/DiagnosticArray`
* Runtime diagnostic reporting for timeout state, velocity limits, pose, and callback timing
* Runtime parameters for timestep, initial pose, timeout, and velocity limits
* Velocity clamping using `std::clamp`
* Command timeout safety
* Parameter validation guards
* Performance timing using `std::chrono::steady_clock`
* Debug workflow documentation
* Daily engineering documentation

---

## ROS 2 Topics

| Topic         | Type                                  | Purpose                                  |
| ------------- | ------------------------------------- | ---------------------------------------- |
| `/cmd_vel`    | `geometry_msgs/msg/Twist`             | Velocity command input                   |
| `/robot_pose` | `geometry_msgs/msg/Pose2D`            | Simple 2D robot pose                     |
| `/odom`       | `nav_msgs/msg/Odometry`               | Standard robot odometry                  |
| `/tf`         | `tf2_msgs/msg/TFMessage`              | Transform tree data                      |
| `/diagnostics`| `diagnostic_msgs/msg/DiagnosticArray` | Runtime health and simulator diagnostics |

---

## Frame Relationship

```txt
odom
  └── base_link
```

The simulator publishes the pose of `base_link` relative to `odom`.

---

## Build

From the ROS 2 workspace:

```bash
cd ros2_ws
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

---

## Run

Launch the simulator with the default YAML configuration:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

The launch file loads parameters from:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

Run with launch argument overrides:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

For exposed parameters, the precedence is:

```txt
terminal override > DeclareLaunchArgument default > YAML > C++ hardcoded default
```

---

## Runtime Configuration

Default simulator parameters are stored in:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

Current parameters:

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

Check loaded parameters:

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Check the installed YAML file that ROS 2 is actually using:

```bash
cat "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/config/sim_params.yaml"
```

---

## Send Commands

One-shot command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Continuous command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Clamp test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 5.0}, angular: {z: 3.0}}"
```

Expected clamped output:

```txt
linear.x=0.50, angular.z=0.80
```

---

## Check Pose

```bash
ros2 topic echo --once /robot_pose
```

Expected fields:

```txt
x: ...
y: ...
theta: ...
```

---

## Check Odometry

```bash
ros2 topic type /odom
ros2 topic echo --once /odom --field pose.pose.position
ros2 topic echo --once /odom --field twist.twist
```

---

## Check TF

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

---

## Check QoS

The simulator uses explicit QoS profiles for command and state topics.

| Topic         | Endpoint   | QoS                                        |
| ------------- | ---------- | ------------------------------------------ |
| `/cmd_vel`    | Subscriber | reliable, volatile, keep_last(10)          |
| `/robot_pose` | Publisher  | reliable, volatile, keep_last(10)          |
| `/odom`       | Publisher  | reliable, volatile, keep_last(10)          |
| `/tf`         | Publisher  | handled by `tf2_ros::TransformBroadcaster` |

Inspect QoS:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /tf --verbose
```

Expected for `/cmd_vel`, `/robot_pose`, and `/odom`:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

The code explicitly configures `KeepLast(10)`. Some ROS 2 CLI outputs may show history/depth as `UNKNOWN` depending on middleware introspection.

---

## rosbag2 Recording and Replay

The simulator includes a rosbag2 workflow for recording and replaying command, pose, odometry, and TF data.

Record simulator topics:

```bash
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
```

Inspect the bag:

```bash
ros2 bag info bags/day65_baseline
```

Replay the bag:

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

Actual bag data is stored locally under `bags/` and ignored by Git. Only `bags/README.md` is tracked.

---

## RViz2 Visualization

The simulator includes a saved RViz2 debugging configuration:

```txt
ros2_ws/src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

Launch the simulator:

```bash
cd ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Open RViz using the source config:

```bash
rviz2 -d src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

Open RViz using the installed package config:

```bash
rviz2 -d "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/rviz/sim_debug.rviz"
```

The RViz config displays:

```txt
Grid
TF
Odometry on /odom
```

Expected frame tree:

```txt
odom
  └── base_link
```

Motion test:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected behavior:

```txt
base_link moves relative to odom
TF display updates
Odometry display updates from /odom
```

---

## Diagnostics

The simulator publishes structured runtime diagnostics on:

```txt
/diagnostics

Message type:

diagnostic_msgs/msg/DiagnosticArray

Check diagnostics:

ros2 topic echo --once /diagnostics

Inspect diagnostics QoS:

ros2 topic info /diagnostics --verbose

The diagnostic report includes:

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

The diagnostic status is:

OK   when simulator is running with fresh command input
WARN when cmd_vel timeout is active

OK-state test:

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
ros2 topic echo --once /diagnostics

WARN-state test:

ros2 topic echo --once /diagnostics

Run the WARN-state test after stopping /cmd_vel and waiting longer than cmd_timeout.


### Add to Verification Workflow

Paste this after RViz2 checks or QoS checks:

```
### Diagnostics Checks

```bash
ros2 topic list | grep diagnostics
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose

Expected topic:

/diagnostics

Expected message type:

diagnostic_msgs/msg/DiagnosticArray

Expected status behavior:

level: 0  -> Simulator running
level: 1  -> cmd_vel timeout active

## Performance Timing

The simulator prints callback timing:

```txt
Performance: callback avg=... ms, max=... ms, budget=... ms
```

The budget is:

```txt
dt * 1000 ms
```

Examples:

```txt
dt = 0.1   -> 100 ms budget
dt = 0.01  -> 10 ms budget
dt = 0.001 -> 1 ms budget
```

---

## Verification Workflow

Use this sequence after meaningful source, launch, config, or documentation changes.

### Build

```bash
cd ros2_ws
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

### Launch

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

### Topic Checks

```bash
ros2 topic list
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
```

### Command Test

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
ros2 topic echo --once /robot_pose
```

### Parameter Checks

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

### QoS Checks

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /tf --verbose
```

---

### rosbag2 Checks

```bash
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
ros2 bag info bags/day65_baseline
ros2 bag play bags/day65_baseline
```

Expected recorded topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

### RViz2 Checks

Open RViz from source config:

```bash
rviz2 -d src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

Open RViz from installed config:

```bash
rviz2 -d "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/rviz/sim_debug.rviz"
```

Expected RViz setup:

```txt
Fixed Frame: odom
Displays: Grid, TF, Odometry
Odometry Topic: /odom
```

---

## Documentation

Additional documentation:

* `docs/daily_documentation.md`
* `docs/system_architecture.md`
* `docs/debugging_and_validation.md`

The daily engineering log tracks the roadmap from C++ fundamentals through ROS 2 launch, YAML parameters, launch arguments, QoS profiles, rosbag2 recording/replay, and RViz2 visualization.
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
* launch-based runtime workflows
* YAML runtime configuration
* launch argument overrides
* QoS profile design
* rosbag2 recording and replay
* RViz2 visual debugging
* parameterized runtime behavior
* safety guards
* debugging discipline
* performance timing
* regression testing
* portfolio-ready engineering documentation

---

## Current Status

| Area                      | Status              |
| ------------------------- | ------------------- |
| Standalone C++ simulator  | Complete foundation |
| ROS 2 node integration    | Complete foundation |
| Launch workflow           | Added               |
| YAML configuration        | Added               |
| Launch argument overrides | Added               |
| QoS profiles              | Added               |
| rosbag2 workflow          | Added               |
| RViz visualization        | Added               |
| Diagnostics               | Added               |
| URDF/Xacro robot model    | Planned             |
| Gazebo integration        | Planned             |

Next planned milestone:

```txt
Day 68 — Launch Regression
```
