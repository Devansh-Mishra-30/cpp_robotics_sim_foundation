# C++ / ROS 2 Robotics Simulation Foundation

This repository contains a C++ and ROS 2 robotics simulation project focused on mobile robot state updates, differential-drive kinematics, ROS 2 messaging, odometry, TF frames, runtime configuration, launch workflows, QoS profiles, safety validation, diagnostics, performance timing, debugging, visualization, regression testing, URDF/Xacro robot modeling, RViz RobotModel visualization, and Gazebo spawning.

The project started as a standalone C++ robotics simulation foundation and was extended into a ROS 2 C++ simulator with robot description and Gazebo integration.

---

## Project Structure

This repository is organized into four main layers:

```txt
standalone_cpp/  -> Pure C++ robotics simulation modules
ros2_ws/         -> ROS 2 C++ simulator, robot model, RViz, and Gazebo integration
scripts/         -> Regression and validation scripts
docs/            -> Architecture, debugging, regression, integration, topic interface, and daily documentation
```

Current structure:

```txt
cpp_robotics_sim_foundation/
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
│       │   └── sim_params.yaml
│       ├── launch/
│       │   ├── sim.launch.py
│       │   ├── description.launch.py
│       │   ├── robot_model_viz.launch.py
│       │   └── gazebo_spawn.launch.py
│       ├── rviz/
│       │   ├── sim_debug.rviz
│       │   └── diffbot_robot_model.rviz
│       ├── src/
│       │   └── sim_node.cpp
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
└── docs/
    ├── daily_documentation.md
    ├── system_architecture.md
    ├── debugging_and_validation.md
    └── topic_interface_reference.md
```

---

## ROS 2 Usage Quickstart

This section shows the shortest path to build, launch, command, inspect, visualize, and validate the ROS 2 simulator.

---

### 1. Build the ROS 2 Workspace

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Expected:

```txt
Summary: 1 package finished
```

---

### 2. Launch the Simulator

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Expected runtime interfaces:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

Expected node:

```txt
/sim_node
```

---

### 3. Send a Motion Command

In a second terminal:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected behavior:

```txt
robot pose updates
odom publishes updated state
TF updates odom -> base_link
diagnostics reports OK while commands are fresh
```

Stop the command publisher with:

```txt
Ctrl+C
```

After command timeout expires, the robot should stop.

---

### 4. Inspect Robot State

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
/robot_pose contains x, y, theta
/odom contains header.frame_id = odom
/odom contains child_frame_id = base_link
tf2_echo shows odom -> base_link
```

---

### 5. Check Diagnostics

```bash
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Expected message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected status behavior:

```txt
level: 0  -> Simulator running
level: 1  -> cmd_vel timeout active
```

---

### 6. Check Parameters

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Default values:

```txt
dt = 0.1
initial_x = 0.0
initial_y = 0.0
initial_theta = 0.0
cmd_timeout = 0.5
max_linear_velocity = 0.5
max_angular_velocity = 0.8
```

---

### 7. Launch with Runtime Overrides

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

Verify overrides:

```bash
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node dt
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Expected:

```txt
initial_x = 2.0
initial_y = 1.0
initial_theta = 0.5
dt = 0.05
cmd_timeout = 1.0
max_linear_velocity = 0.2
max_angular_velocity = 0.4
```

---

### 8. Open RViz2 Odometry / TF Visualization

```bash
rviz2 -d "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/rviz/sim_debug.rviz"
```

Expected RViz setup:

```txt
Fixed Frame: odom
Displays: Grid, TF, Odometry
Odometry Topic: /odom
```

Expected frame tree:

```txt
odom
  └── base_link
```

---

### 9. Record a rosbag2 Run

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

### 10. Run Launch Regression

From the repository root:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected result:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## Robot Model, RViz RobotModel, and Gazebo Usage

The project includes a differential-drive robot description and Gazebo spawn workflow.

Robot description files:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

The URDF/Xacro model defines:

```txt
base_link
├── left_wheel_link
├── right_wheel_link
└── caster_link
```

Joints:

```txt
left_wheel_joint   continuous
right_wheel_joint  continuous
caster_joint       fixed
```

---

### 1. Launch Robot Description Stack

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

Check robot description:

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/robot_description.txt
```

Check joint states:

```bash
ros2 topic echo /joint_states --once
```

Expected joint names:

```txt
left_wheel_joint
right_wheel_joint
```

Check fixed transform:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected fixed transform:

```txt
base_link -> caster_link
```

Check wheel transforms:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
```

---

### 2. Launch RViz RobotModel Visualization

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

This launch file starts:

```txt
sim_node
robot_state_publisher
joint_state_publisher
rviz2
```

Expected RViz displays:

```txt
Grid
TF
RobotModel
Odometry
```

Expected RViz fixed frame:

```txt
odom
```

Expected RobotModel source:

```txt
/robot_description
```

Expected extended frame tree:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

Motion test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.4}}"
```

Expected behavior:

```txt
RViz displays the robot body, wheels, caster, TF frames, and odometry
robot moves relative to odom when /cmd_vel is published
```

---

### 3. Launch Gazebo Spawn Workflow

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected Gazebo result:

```txt
Gazebo Sim opens
ground plane appears
diffbot appears in the world
spawn_diffbot exits cleanly
```

Gazebo world file:

```txt
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
```

Check ROS-side topics:

```bash
ros2 topic list | grep -E "robot_description|joint_states|tf|clock"
```

Expected ROS-side topics:

```txt
/robot_description
/joint_states
/tf
/tf_static
```

Check Gazebo topics:

```bash
gz topic -l | grep world
```

Expected:

```txt
/world/empty_diffbot_world/...
```

Current Gazebo scope:

```txt
Robot can spawn in Gazebo
Ground plane appears
Robot model appears
Robot is not yet driven by ros2_control
Robot is not yet driven by a Gazebo diff-drive plugin
Gazebo odometry is not yet bridged back to ROS
Sensors are not yet simulated
```

---

## Transform Ownership

The project follows a strict TF ownership rule:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
```

This prevents duplicate TF publishers for the same transform.

Original simulator frame tree:

```txt
odom
  └── base_link
```

Extended robot-description frame tree:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

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

## ROS 2 Integration

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
/diagnostics
```

The ROS 2 node subscribes to velocity commands, updates pose, publishes odometry, broadcasts the `odom -> base_link` transform, and publishes runtime diagnostics.

The robot description layer adds:

```txt
/robot_description
/joint_states
/tf_static
```

These interfaces allow RViz and Gazebo tools to understand the robot structure.

---

## Regression Scripts

The scripts layer contains repeatable validation workflows:

```txt
scripts/day68_launch_regression.sh
```

The Day 68 launch regression script validates that the ROS 2 runtime stack still launches correctly and publishes the expected topics, parameters, TF, odometry, and diagnostics.

Run:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## Documentation

See:

```txt
docs/daily_documentation.md
docs/system_architecture.md
docs/debugging_and_validation.md
docs/topic_interface_reference.md
```

The daily engineering log tracks the roadmap from C++ fundamentals through ROS 2 launch, YAML parameters, launch arguments, QoS profiles, rosbag2 recording/replay, RViz2 visualization, diagnostics, launch regression, URDF/Xacro robot modeling, robot state publishing, joint state publishing, RViz RobotModel visualization, and Gazebo spawning.

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
* `/diagnostics` publisher using `diagnostic_msgs/msg/DiagnosticArray`
* Runtime diagnostic reporting for timeout state, velocity limits, pose, and callback timing
* ROS 2 launch workflow using `sim.launch.py`
* YAML runtime configuration using `config/sim_params.yaml`
* Launch argument overrides for initial pose, timestep, timeout, and velocity limits
* Explicit ROS 2 QoS profiles for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics`
* rosbag2 recording and replay workflow for `/cmd_vel`, `/robot_pose`, `/odom`, and `/tf`
* RViz2 visualization workflow with saved `sim_debug.rviz` config
* Launch regression script for repeatable ROS 2 runtime validation
* ROS 2 topic interface reference for `/cmd_vel`, `/robot_pose`, `/odom`, `/tf`, `/diagnostics`, `/robot_description`, `/joint_states`, and `/tf_static`
* Runtime parameters for timestep, initial pose, timeout, and velocity limits
* Velocity clamping using `std::clamp`
* Command timeout safety
* Parameter validation guards
* Performance timing using `std::chrono::steady_clock`
* Debug workflow documentation
* Daily engineering documentation
* Static URDF model for the differential-drive robot
* Parameterized Xacro model for reusable robot description
* `robot_state_publisher` launch workflow
* `joint_state_publisher` integration for wheel joints
* RViz RobotModel visualization with `diffbot_robot_model.rviz`
* Gazebo Sim world and robot spawn workflow

---

## Topic Interface Reference

A detailed topic interface reference is available at:

```txt
docs/topic_interface_reference.md
```

It documents:

```txt
topic direction
message type
important fields
QoS behavior
frame relationships
validation commands
common interface failures
interview explanation
```

---

## ROS 2 Topics

| Topic                | Type                                  | Producer                            | Purpose                                  |
| -------------------- | ------------------------------------- | ----------------------------------- | ---------------------------------------- |
| `/cmd_vel`           | `geometry_msgs/msg/Twist`             | external command source             | Velocity command input                   |
| `/robot_pose`        | `geometry_msgs/msg/Pose2D`            | `sim_node`                          | Simple 2D robot pose                     |
| `/odom`              | `nav_msgs/msg/Odometry`               | `sim_node`                          | Standard robot odometry                  |
| `/tf`                | `tf2_msgs/msg/TFMessage`              | `sim_node`, `robot_state_publisher` | Transform tree data                      |
| `/tf_static`         | `tf2_msgs/msg/TFMessage`              | `robot_state_publisher`             | Fixed transform tree data                |
| `/diagnostics`       | `diagnostic_msgs/msg/DiagnosticArray` | `sim_node`                          | Runtime health and simulator diagnostics |
| `/robot_description` | `std_msgs/msg/String`                 | `robot_state_publisher`             | Robot model XML                          |
| `/joint_states`      | `sensor_msgs/msg/JointState`          | `joint_state_publisher`             | Joint positions for robot links          |

---

## Frame Relationship

Original simulator relationship:

```txt
odom
  └── base_link
```

Extended robot model relationship:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

The simulator publishes the pose of `base_link` relative to `odom`.

`robot_state_publisher` publishes the robot link structure below `base_link`.

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
linear.x = 0.50
angular.z = 0.80
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

Expected type:

```txt
nav_msgs/msg/Odometry
```

Expected frames:

```txt
header.frame_id: odom
child_frame_id: base_link
```

---

## Check TF

Simulator transform:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

Robot link transforms:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link caster_link
```

---

## Check QoS

The simulator uses explicit QoS profiles for command, state, and diagnostics topics.

| Topic          | Endpoint   | QoS                                                                    |
| -------------- | ---------- | ---------------------------------------------------------------------- |
| `/cmd_vel`     | Subscriber | reliable, volatile, keep_last(10)                                      |
| `/robot_pose`  | Publisher  | reliable, volatile, keep_last(10)                                      |
| `/odom`        | Publisher  | reliable, volatile, keep_last(10)                                      |
| `/diagnostics` | Publisher  | reliable, volatile, keep_last(10)                                      |
| `/tf`          | Publisher  | handled by `tf2_ros::TransformBroadcaster` and `robot_state_publisher` |
| `/tf_static`   | Publisher  | transient local behavior expected                                      |

Inspect QoS:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /diagnostics --verbose
ros2 topic info /tf --verbose
```

Expected for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics`:

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

Actual bag data is stored locally under `bags/` and ignored by Git. Only `bags/README.md` should be tracked.

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

## RViz RobotModel Visualization

The project includes a saved RobotModel RViz configuration:

```txt
ros2_ws/src/cpp_robotics_sim_ros/rviz/diffbot_robot_model.rviz
```

Launch the full robot visualization stack:

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

This starts:

```txt
sim_node
robot_state_publisher
joint_state_publisher
rviz2
```

Expected RViz displays:

```txt
Grid
TF
RobotModel
Odometry
```

Expected fixed frame:

```txt
odom
```

Expected RobotModel source:

```txt
/robot_description
```

Expected full frame tree:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

---

## Robot Description Validation

Validate static URDF:

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf")
print("PASS: URDF XML parsed successfully")
PY
```

Generate URDF from Xacro:

```bash
source /opt/ros/jazzy/setup.bash
xacro "ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro" > /tmp/diffbot_from_xacro.urdf
```

Validate generated URDF:

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("/tmp/diffbot_from_xacro.urdf")
print("PASS: Xacro generated valid URDF XML")
PY
```

Inspect links and joints:

```bash
grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/diffbot_from_xacro.urdf
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/diffbot_from_xacro.urdf
```

---

## Gazebo Simulation

The project includes a Gazebo Sim world:

```txt
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
```

Launch Gazebo and spawn the robot:

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected:

```txt
Gazebo opens
ground plane appears
diffbot appears in the world
spawn_diffbot exits cleanly
```

Day 76 Gazebo scope:

```txt
Gazebo world loads
robot description is published
robot is spawned from /robot_description
robot appears in Gazebo
```

Not implemented yet:

```txt
ros2_control
Gazebo differential-drive plugin
/cmd_vel driving the Gazebo robot
sensor simulation
Gazebo-to-ROS odometry bridge
```

---

## Diagnostics

The simulator publishes structured runtime diagnostics on:

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
```

Inspect diagnostics QoS:

```bash
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

The diagnostic status is:

```txt
OK   when simulator is running with fresh command input
WARN when cmd_vel timeout is active
```

OK-state test:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
ros2 topic echo --once /diagnostics
```

Expected OK-state behavior:

```txt
level: 0
message: Simulator running
timeout_active: false
```

WARN-state test:

```bash
ros2 topic echo --once /diagnostics
```

Run the WARN-state test after stopping `/cmd_vel` and waiting longer than `cmd_timeout`.

Expected WARN-state behavior:

```txt
level: 1
message: cmd_vel timeout active
timeout_active: true
```

---

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

## Launch Regression

The project includes a repeatable launch regression script:

```txt
scripts/day68_launch_regression.sh
```

Run it from the repository root:

```bash
./scripts/day68_launch_regression.sh
```

The script validates:

```txt
default launch
required ROS 2 topics
default parameters
robot pose output
odometry output
TF output
diagnostics output
command response
diagnostics QoS/type
launch argument overrides
```

Expected result:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## Verification Workflow

Use this sequence after meaningful source, launch, config, robot description, world, or documentation changes.

### Build

```bash
cd ros2_ws
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

### Launch Simulator

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
ros2 topic info /diagnostics --verbose
ros2 topic info /tf --verbose
```

### Diagnostics Checks

```bash
ros2 topic list | grep diagnostics
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Expected topic:

```txt
/diagnostics
```

Expected message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected status behavior:

```txt
level: 0  -> Simulator running
level: 1  -> cmd_vel timeout active
```

### Robot Description Checks

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Second terminal:

```bash
ros2 node list
ros2 topic list | grep -E "robot_description|joint_states|tf|tf_static"

ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/robot_description.txt

ros2 topic echo /joint_states --once
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

### RViz RobotModel Checks

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

Expected:

```txt
RViz opens
Grid display appears
TF display appears
RobotModel display appears
Odometry display appears
```

### Gazebo Spawn Checks

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected:

```txt
Gazebo opens
ground plane appears
diffbot appears in the world
```

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

### Launch Regression Check

From the repository root:

```bash
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## Documentation

Additional documentation:

* `docs/daily_documentation.md`
* `docs/system_architecture.md`
* `docs/debugging_and_validation.md`
* `docs/topic_interface_reference.md`

The daily engineering log tracks the roadmap from C++ fundamentals through ROS 2 launch, YAML parameters, launch arguments, QoS profiles, rosbag2 recording/replay, RViz2 visualization, diagnostics, launch regression, URDF/Xacro robot modeling, RViz RobotModel visualization, and Gazebo spawning.

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
* parameterized runtime behavior
* safety guards
* debugging discipline
* performance timing
* regression testing
* portfolio-ready engineering documentation

---

## Current Status

| Area                              | Status              |
| --------------------------------- | ------------------- |
| Standalone C++ simulator          | Complete foundation |
| ROS 2 node integration            | Complete foundation |
| Launch workflow                   | Added               |
| YAML configuration                | Added               |
| Launch argument overrides         | Added               |
| QoS profiles                      | Added               |
| rosbag2 workflow                  | Added               |
| RViz2 odometry/TF visualization   | Added               |
| Diagnostics                       | Added               |
| Launch regression                 | Added               |
| Topic interface reference         | Added               |
| URDF robot model                  | Added               |
| Xacro robot description           | Added               |
| `robot_state_publisher` workflow  | Added               |
| `joint_state_publisher` workflow  | Added               |
| RViz RobotModel visualization     | Added               |
| Gazebo world and robot spawn      | Added               |
| `ros2_control` integration        | Planned             |
| Gazebo differential-drive control | Planned             |
| Sensor simulation                 | Planned             |

Next planned milestone:

```txt
Day 77 — ros2_control basics
```
