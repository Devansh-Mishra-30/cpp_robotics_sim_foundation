# ROS 2 Topic Interface Reference

This document defines the ROS 2 topic, file, test, CI, benchmark, and validation interfaces used by the `cpp_robotics_sim_ros` simulator, robot description stack, Gazebo `ros2_control` stack, differential-drive controller, simulated lidar workflow, noisy odometry workflow, trajectory validation workflow, GoogleTest suite, GitHub Actions CI workflow, and deterministic performance benchmark.

The purpose of this document is to make the runtime and validation interfaces clear enough that another engineer can understand what each stack subscribes to, what it publishes, what message types are used, what fields matter, what node owns each transform, what files are generated, what tests run, and how to validate each interface through Day 90.

---

## 1. Interface Overview

The project has several related runtime interfaces.

### 1.1 Original Kinematic Simulator Stack

```txt
/cmd_vel
   ↓
sim_node
   ↓
/robot_pose
/odom
/tf
/diagnostics
```

The node accepts velocity commands, updates the robot pose, publishes simple 2D pose, publishes standard odometry, broadcasts TF, and reports diagnostics.

### 1.2 Robot Description Stack

```txt
diffbot.xacro
   ↓
/robot_description
   ↓
robot_state_publisher  ←  /joint_states
   ↓
/tf
/tf_static
```

The robot description stack exposes the robot structure below `base_link`.

### 1.3 Gazebo Control Stack

```txt
/diff_drive_controller/cmd_vel
   ↓
diff_drive_controller
   ↓
ros2_control hardware interfaces
   ↓
gz_ros2_control
   ↓
Gazebo wheel joints
   ↓
/diff_drive_controller/odom
/tf
```

The Gazebo control stack moves the robot in the physics simulator.

### 1.4 Simulated Lidar Stack

```txt
Gazebo gpu_lidar
   ↓
Gazebo /scan
   ↓
ros_gz_bridge
   ↓
ROS /scan
```

The simulated lidar stack exposes Gazebo sensor data as a ROS 2 `LaserScan` topic.

### 1.5 Noisy Odometry Stack

```txt
/diff_drive_controller/odom
   ↓
noisy_odom_node.py
   ↓
/odom_noisy
```

The noisy odometry stack creates a controlled noisy measurement stream from actual Gazebo controller odometry.

Important:

```txt
/odom_noisy does not move Gazebo.
It is a feedback/measurement topic, not an actuation topic.
```

### 1.6 Trajectory Validation Stack

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

The trajectory validation stack records command, actual odometry, and noisy odometry data, then converts it into plots and report metrics.


### 1.7 Automated Testing and CI Stack

```txt
day86_testable_core.hpp
   ↓
test_day86_core.cpp
   ↓
GoogleTest
   ↓
colcon test
   ↓
GitHub Actions CI
```

The automated testing stack validates deterministic C++ math utilities and pose integration independent of ROS 2 runtime, Gazebo, RViz, and controller execution.

### 1.8 Performance Benchmark Stack

```txt
day88_performance_benchmark
   ↓
data/day88_performance_results.csv
docs/performance_report.md
```

The performance benchmark stack measures deterministic C++ pose-update timing for multiple timestep values.

### 1.9 Documentation and Assessment Stack

```txt
local validation commands
   ↓
docs/day89_validation_checkpoint.md
   ↓
Day 90 final assessment notes
```

The Day 89-90 documentation layer records the current validation state before continuing into the next implementation phase.

---

## 2. Frame Tree and Transform Ownership

The extended frame tree through Day 90 is:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

### 2.1 Kinematic Simulator Stack Ownership

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

### 2.2 Gazebo Control Stack Ownership

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

---

## 3. Topic Summary

| Topic | Direction | Message Type | Producer | Consumer | Purpose |
|---|---|---|---|---|---|
| `/cmd_vel` | Input | `geometry_msgs/msg/Twist` | external command source | `sim_node` | Velocity command input for the kinematic simulator stack |
| `/robot_pose` | Output | `geometry_msgs/msg/Pose2D` | `sim_node` | CLI/debug tools | Simple 2D pose debugging output |
| `/odom` | Output | `nav_msgs/msg/Odometry` | `sim_node` | RViz, validation tools, rosbag2 | Standard odometry output for the kinematic simulator stack |
| `/tf` | Output | `tf2_msgs/msg/TFMessage` | `sim_node`, `robot_state_publisher`, `diff_drive_controller` | RViz, TF tools | Dynamic transform tree output |
| `/tf_static` | Output | `tf2_msgs/msg/TFMessage` | `robot_state_publisher` | RViz, TF tools | Fixed transform tree output |
| `/diagnostics` | Output | `diagnostic_msgs/msg/DiagnosticArray` | `sim_node` | CLI/debug/monitoring tools | Runtime health and simulator status |
| `/robot_description` | Output / parameter-backed topic | `std_msgs/msg/String` | `robot_state_publisher` | RViz RobotModel, Gazebo spawn workflow, `controller_manager` | Robot model XML |
| `/joint_states` | Output | `sensor_msgs/msg/JointState` | `joint_state_publisher` or `joint_state_broadcaster` | `robot_state_publisher` | Joint positions/velocities for robot links |
| `/dynamic_joint_states` | Output | `control_msgs/msg/DynamicJointState` | `joint_state_broadcaster` | debugging/control tools | Detailed `ros2_control` joint interface states |
| `/diff_drive_controller/cmd_vel` | Input | `geometry_msgs/msg/TwistStamped` | CLI/teleop/future navigation | `diff_drive_controller` | Velocity command input for Gazebo-driven robot |
| `/diff_drive_controller/odom` | Output | `nav_msgs/msg/Odometry` | `diff_drive_controller` | RViz, validation tools, future navigation/localization | Odometry output from Gazebo diff-drive controller |
| `/diff_drive_controller/cmd_vel_out` | Output | `geometry_msgs/msg/TwistStamped` | `diff_drive_controller` | CLI/debug tools | Limited velocity command after controller limits |
| `/odom_noisy` | Output | `nav_msgs/msg/Odometry` | `noisy_odom_node.py` | validation recorder, future localization/EKF tools | Noisy odometry stream generated from `/diff_drive_controller/odom` |
| `/scan` | Output | `sensor_msgs/msg/LaserScan` | `ros_gz_bridge` from Gazebo lidar | RViz, future Nav2/SLAM/costmaps | Simulated 2D lidar scan |
| `/clock` | Output | `rosgraph_msgs/msg/Clock` | `ros_gz_bridge` from Gazebo | ROS nodes and RViz using sim time | Simulation time source |

`controller_manager` also exposes ROS services used by the `ros2 control` CLI and controller spawners, but the main user-facing runtime interfaces in this document are topics.


Additional non-topic interfaces added through Day 90:

| Interface | Type | Producer / Owner | Consumer | Purpose |
|---|---|---|---|---|
| `test_day86_core` | GoogleTest executable | `ament_add_gtest` / CMake | `colcon test`, GitHub Actions | Unit-test deterministic C++ math and pose integration |
| `.github/workflows/ros2_jazzy_ci.yml` | CI workflow | GitHub Actions | GitHub repository checks | Build and test the ROS 2 workspace on push/pull request |
| `day88_performance_benchmark` | C++ executable | `cpp_robotics_sim_ros` package | CLI, docs, future CI | Benchmark deterministic pose-update timing |
| `data/day88_performance_results.csv` | CSV artifact | performance benchmark executable | performance report, manual inspection | Store benchmark timing results |
| `docs/performance_report.md` | Markdown artifact | performance benchmark executable | documentation/review | Report timing metrics and interpretation |
| `docs/day89_validation_checkpoint.md` | Markdown artifact | manual validation checkpoint | documentation/review | Record build, test, CI, benchmark, and validation status |

---

## 4. QoS Summary

| Topic | Endpoint | QoS |
|---|---|---|
| `/cmd_vel` | `sim_node` subscriber | reliable, volatile, keep_last(10) |
| `/robot_pose` | `sim_node` publisher | reliable, volatile, keep_last(10) |
| `/odom` | `sim_node` publisher | reliable, volatile, keep_last(10) |
| `/diagnostics` | `sim_node` publisher | reliable, volatile, keep_last(10) |
| `/tf` | publisher | handled by TF broadcaster, `robot_state_publisher`, or `diff_drive_controller` |
| `/tf_static` | publisher | transient local behavior expected for fixed transforms |
| `/robot_description` | publisher/parameter | transient local behavior expected |
| `/joint_states` | publisher | standard joint state publisher/broadcaster behavior |
| `/diff_drive_controller/cmd_vel` | `diff_drive_controller` subscriber | controller default QoS; expects `TwistStamped` |
| `/diff_drive_controller/odom` | `diff_drive_controller` publisher | controller default QoS |
| `/diff_drive_controller/cmd_vel_out` | `diff_drive_controller` publisher | controller default QoS |
| `/odom_noisy` | `noisy_odom_node.py` publisher | reliable, volatile, queue depth 10 through `rclpy` default construction |
| `/scan` | bridge publisher | sensor-style QoS; RViz may need Best Effort |
| `/clock` | bridge publisher | simulation-time clock QoS |

The kinematic simulator state topics use reliable communication because they are low-rate outputs used for debugging and validation.

The durability for live simulator values is volatile because old commands or stale state should not be replayed automatically to late subscribers.

`/tf_static` and `/robot_description` behave differently from live command/state topics because fixed transforms and robot model descriptions should be available to late subscribers.

High-rate sensor topics such as `/scan` are commonly visualized with Best Effort reliability in RViz if a reliability mismatch appears.

---

## 5. `/cmd_vel`

### Purpose

`/cmd_vel` is the velocity command input topic for the custom kinematic simulator stack.

### Message Type

```txt
geometry_msgs/msg/Twist
```

### Direction

```txt
Input to sim_node
```

### Producer

```txt
external command source
ros2 topic pub command
future teleop node
future navigation/control layer for the custom kinematic stack
```

### Consumer

```txt
sim_node
```

### Used Fields

```txt
linear.x   = forward linear velocity
angular.z  = yaw angular velocity
```

Other fields are ignored by the current planar simulator:

```txt
linear.y
linear.z
angular.x
angular.y
```

### Example Command

One-shot command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Continuous command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

### Safety Behavior

Incoming commands are clamped using configured limits:

```txt
max_linear_velocity
max_angular_velocity
```

With default values:

```txt
linear.x = 5.0  ->  0.5
angular.z = 3.0 ->  0.8
```

If no fresh `/cmd_vel` arrives before `cmd_timeout`, the robot stops.

### Validation Commands

```bash
ros2 topic info /cmd_vel
ros2 topic info /cmd_vel --verbose
```

Expected:

```txt
Type: geometry_msgs/msg/Twist
Subscription count: 1
Reliability: RELIABLE
Durability: VOLATILE
```

### Validation Criteria

```txt
/cmd_vel exists when sim_node is running
/cmd_vel has one subscriber
linear.x affects forward motion
angular.z affects heading motion
large commands are clamped
stale commands time out
```

---

## 6. `/robot_pose`

### Purpose

`/robot_pose` is a simple 2D pose output used for quick debugging.

It is easier to inspect than the full `/odom` message.

### Message Type

```txt
geometry_msgs/msg/Pose2D
```

### Direction

```txt
Output from sim_node
```

### Producer

```txt
sim_node
```

### Consumers

```txt
CLI debugging
validation checks
future lightweight plotting/debug tools
```

### Fields

```txt
x      = robot x position
y      = robot y position
theta  = robot heading angle in radians
```

### Example Check

```bash
ros2 topic echo --once /robot_pose
```

Expected structure:

```txt
x: ...
y: ...
theta: ...
```

### Validation Criteria

```txt
x changes during forward motion
theta changes during rotational motion
pose stops changing after command timeout
pose starts near launch-configured initial pose
pose remains consistent with /odom position and odom -> base_link TF
```

---

## 7. `/odom`

### Purpose

`/odom` is the standard ROS 2 odometry output from the custom kinematic simulator stack.

It is used by RViz2, validation tools, rosbag2 workflows, and future simulation layers.

### Message Type

```txt
nav_msgs/msg/Odometry
```

### Direction

```txt
Output from sim_node
```

### Producer

```txt
sim_node
```

### Consumers

```txt
RViz Odometry display
rosbag2 recording
validation tools
future navigation/control layers for the custom kinematic stack
```

### Frame IDs

```txt
header.frame_id: odom
child_frame_id: base_link
```

### Important Fields

```txt
pose.pose.position.x
pose.pose.position.y
pose.pose.position.z
pose.pose.orientation.x
pose.pose.orientation.y
pose.pose.orientation.z
pose.pose.orientation.w
twist.twist.linear.x
twist.twist.angular.z
```

For planar motion:

```txt
position.z = 0
orientation represents yaw only
twist.linear.x = current linear velocity
twist.angular.z = current angular velocity
```

### Quaternion Convention

The simulator converts planar heading `theta` into yaw quaternion form:

```txt
q.x = 0
q.y = 0
q.z = sin(theta / 2)
q.w = cos(theta / 2)
```

### Example Checks

```bash
ros2 topic type /odom
ros2 topic echo --once /odom
ros2 topic echo --once /odom --field pose.pose.position
ros2 topic echo --once /odom --field twist.twist
```

Expected type:

```txt
nav_msgs/msg/Odometry
```

### Validation Criteria

```txt
header.frame_id is odom
child_frame_id is base_link
position x/y matches /robot_pose
orientation matches theta as yaw quaternion
twist values match clamped command
odom remains consistent with odom -> base_link TF
```

---

## 8. `/tf`

### Purpose

`/tf` publishes dynamic transform tree relationships.

In this project, `/tf` can have different sources depending on the launch stack:

```txt
sim_node
robot_state_publisher
diff_drive_controller
```

### Message Type

```txt
tf2_msgs/msg/TFMessage
```

### Direction

```txt
Output from tf2_ros::TransformBroadcaster, robot_state_publisher, and diff_drive_controller
```

### Transform Ownership

In the kinematic simulator stack, `sim_node` owns:

```txt
odom -> base_link
```

In the Gazebo control stack, `diff_drive_controller` owns:

```txt
odom -> base_link
```

`robot_state_publisher` owns robot structure below `base_link`:

```txt
base_link -> left_wheel_link
base_link -> right_wheel_link
base_link -> caster_link
base_link -> lidar_link
```

Fixed transforms appear through `/tf_static`.

### Frame Relationship

Full expected tree through Day 90:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

### Example Checks

Simulator/Gazebo moving transform:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Wheel and lidar transforms:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Expected moving transform structure:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

Expected wheel transform positions:

```txt
base_link -> left_wheel_link:  [0.000, 0.180, 0.080]
base_link -> right_wheel_link: [0.000, -0.180, 0.080]
```

### Validation Criteria

```txt
odom -> base_link transform exists
parent frame is odom
child frame is base_link
translation matches robot x/y
rotation matches robot yaw
base_link -> wheel transforms exist when /joint_states is active
base_link -> lidar_link transform exists
RViz2 can use odom as Fixed Frame
```

### Common Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `odom` missing | simulator/controller not running or TF broadcaster broken | `ros2 node list`, `tf2_echo odom base_link` |
| `base_link` missing | wrong child frame ID | inspect transform publisher or controller frame config |
| wheel frames missing | `/joint_states` missing | `ros2 topic echo /joint_states --once` |
| duplicate TF warning | two nodes publish same transform | do not run `sim_node` and `diff_drive_controller` as `odom -> base_link` owners together |
| `TF_OLD_DATA` warnings | RViz/Gazebo sim-time mismatch or stale nodes | restart stack, verify `/clock`, launch RViz with `use_sim_time:=true` |
| RViz fixed frame error | TF tree incomplete | set Fixed Frame to `odom` and check TF |

---

## 9. `/tf_static`

### Purpose

`/tf_static` publishes fixed transforms from the robot description.

Fixed transforms are used for links that do not move relative to their parent.

### Message Type

```txt
tf2_msgs/msg/TFMessage
```

### Direction

```txt
Output from robot_state_publisher
```

### Producer

```txt
robot_state_publisher
```

### Consumers

```txt
RViz TF display
RViz RobotModel display
TF tools
```

### Expected Fixed Transforms

Current fixed transforms include:

```txt
base_link -> caster_link
base_link -> lidar_link
```

Expected caster translation:

```txt
translation.x = -0.17
translation.y = 0.0
translation.z = 0.035
rotation.w = 1.0
```

Expected lidar translation:

```txt
translation.x = 0.15
translation.y = 0.0
translation.z = 0.18
```

### Validation Command

Use transient local durability when echoing `/tf_static`:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected structure:

```txt
transforms:
- header:
    frame_id: base_link
  child_frame_id: caster_link
```

### Validation Criteria

```txt
/tf_static exists
base_link -> caster_link is published
base_link -> lidar_link is published
caster_link and lidar_link appear in RViz TF tree
late subscribers can receive the fixed transform
```

---

## 10. `/diagnostics`

### Purpose

`/diagnostics` publishes structured runtime health information for the custom kinematic simulator.

It is used to inspect node status, timeout state, current command/state values, and callback timing.

### Message Type

```txt
diagnostic_msgs/msg/DiagnosticArray
```

### Direction

```txt
Output from sim_node
```

### Producer

```txt
sim_node
```

### Consumers

```txt
CLI debugging
rosbag2 diagnostics recording
future monitoring tools
```

### Status Levels

```txt
level: 0  -> OK
level: 1  -> WARN
```

Current behavior:

```txt
OK   = simulator running with fresh command input
WARN = cmd_vel timeout active
```

### Diagnostic Identity

Expected fields:

```txt
name: sim_node
hardware_id: cpp_robotics_sim_ros
```

### Key-Value Fields

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

### Example Checks

```bash
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Expected type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected QoS:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

### OK-State Test

Run continuous command input:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Then check diagnostics:

```bash
ros2 topic echo --once /diagnostics
```

Expected:

```txt
level: 0
message: Simulator running
timeout_active: false
```

### WARN-State Test

Stop `/cmd_vel`, wait longer than `cmd_timeout`, then run:

```bash
ros2 topic echo --once /diagnostics
```

Expected:

```txt
level: 1
message: cmd_vel timeout active
timeout_active: true
```

---

## 11. `/robot_description`

### Purpose

`/robot_description` provides the generated robot model XML.

The XML is produced from:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

The robot model describes the structure below `base_link`.

### Message Type

```txt
std_msgs/msg/String
```

The same content is also available through the `robot_description` parameter on `/robot_state_publisher`.

### Direction

```txt
Output from robot_state_publisher / parameter-backed robot model interface
```

### Producer

```txt
description.launch.py
robot_state_publisher
```

### Consumers

```txt
robot_state_publisher
RViz RobotModel display
ros_gz_sim create spawn command
controller_manager / gz_ros2_control workflow
debugging tools
```

### Model Content

Expected links:

```txt
base_link
left_wheel_link
right_wheel_link
caster_link
lidar_link
```

Expected joints:

```txt
left_wheel_joint
right_wheel_joint
caster_joint
lidar_joint
```

Expected joint types:

```txt
left_wheel_joint   continuous
right_wheel_joint  continuous
caster_joint       fixed
lidar_joint        fixed
```

### Validation Commands

Launch robot description stack:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Check parameter content:

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt
```

Check topic existence:

```bash
ros2 topic list | grep robot_description
```

Expected:

```txt
/robot_description
```

### Validation Criteria

```txt
/robot_description exists
robot_description parameter exists on /robot_state_publisher
generated XML contains all expected links
generated XML contains all expected joints
generated XML contains ros2_control wheel interfaces
generated XML contains lidar sensor configuration
RViz RobotModel can load the robot model
Gazebo spawn can use the robot model
```

### Common Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `/robot_description` missing | `robot_state_publisher` not running | `ros2 node list` |
| XML parsed as YAML | launch parameter not forced to string | use `ParameterValue(..., value_type=str)` |
| Xacro command fails | path quoting issue or Xacro typo | run `xacro diffbot.xacro` manually |
| robot model missing links | Xacro macro/link typo | inspect `/tmp/robot_description.txt` |
| RViz RobotModel red | missing robot description or TF | check `/robot_description` and TF tree |

---

## 12. `/joint_states`

### Purpose

`/joint_states` publishes joint positions and velocities for the robot model joints.

For this project, it provides wheel joint states to `robot_state_publisher`.

In the visualization-only stack, `/joint_states` comes from `joint_state_publisher`.

In the Gazebo `ros2_control` stack, `/joint_states` comes from `joint_state_broadcaster`.

### Message Type

```txt
sensor_msgs/msg/JointState
```

### Direction

```txt
Output from joint_state_publisher or joint_state_broadcaster, depending on launch stack
```

### Producers

```txt
joint_state_publisher
joint_state_broadcaster
```

### Consumer

```txt
robot_state_publisher
```

### Expected Joint Names

```txt
left_wheel_joint
right_wheel_joint
```

The caster and lidar joints are fixed, so they do not need moving joint states.

### Example Check

```bash
ros2 topic echo /joint_states --once
```

Expected structure:

```txt
name:
- left_wheel_joint
- right_wheel_joint
position:
- ...
- ...
```

The exact numeric values may vary. In the Gazebo control stack, values come from simulated hardware state interfaces through `joint_state_broadcaster`.

### Validation Criteria

```txt
/joint_states exists
left_wheel_joint appears
right_wheel_joint appears
robot_state_publisher receives joint states
base_link -> left_wheel_link transform exists
base_link -> right_wheel_link transform exists
```

### Common Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `/joint_states` missing | `joint_state_publisher` not installed/launched or broadcaster inactive | `ros2 node list`, `ros2 control list_controllers` |
| wheel joint names missing | Xacro joint names do not match | inspect robot description |
| wheel transforms missing | robot_state_publisher not receiving joint states | echo `/joint_states` |
| package not found | missing system package | install `ros-jazzy-joint-state-publisher` |

---

## 13. `/dynamic_joint_states`

### Purpose

`/dynamic_joint_states` exposes detailed `ros2_control` interface state information.

It is useful for debugging hardware interface state in the Gazebo control stack.

### Message Type

```txt
control_msgs/msg/DynamicJointState
```

### Direction

```txt
Output from joint_state_broadcaster
```

### Producer

```txt
joint_state_broadcaster
```

### Consumers

```txt
CLI debugging
control interface inspection tools
```

### Example Check

```bash
ros2 topic echo /dynamic_joint_states --once
```

### Validation Criteria

```txt
/dynamic_joint_states exists when joint_state_broadcaster is active
wheel joint interfaces appear
position and velocity state interfaces are visible
```

---

## 14. `/diff_drive_controller/cmd_vel`

### Purpose

`/diff_drive_controller/cmd_vel` is the velocity command input for the Gazebo-driven robot.

Unlike the original `/cmd_vel` used by `sim_node`, this controller topic expects a stamped command.

### Message Type

```txt
geometry_msgs/msg/TwistStamped
```

### Direction

```txt
Input to diff_drive_controller
```

### Producer

```txt
ros2 topic pub command
future teleop node
future Nav2 controller output after remapping/relay
```

### Consumer

```txt
diff_drive_controller
```

### Used Fields

```txt
twist.linear.x   = forward velocity command
twist.angular.z  = yaw velocity command
```

### Example Command

Straight motion:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Circular motion used for Day 84/85 validation:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

### Validation Criteria

```txt
/diff_drive_controller/cmd_vel exists when diff_drive_controller is active
message type is geometry_msgs/msg/TwistStamped
linear.x drives forward/backward motion in Gazebo
angular.z drives rotation in Gazebo
robot stops after controller timeout when commands stop
```

### Important Architecture Rule

```txt
/diff_drive_controller/cmd_vel moves Gazebo.
/odom_noisy does not move Gazebo.
```

---

## 15. `/diff_drive_controller/odom`

### Purpose

`/diff_drive_controller/odom` is the odometry output from the Gazebo differential-drive controller.

It represents the Gazebo-controlled robot state, not the custom `sim_node` kinematic state.

### Message Type

```txt
nav_msgs/msg/Odometry
```

### Direction

```txt
Output from diff_drive_controller
```

### Producer

```txt
diff_drive_controller
```

### Consumers

```txt
RViz Odometry display
noisy_odom_node.py
trajectory_validation_recorder.py
future Nav2/localization stack
future EKF/sensor fusion workflow
```

### Frame IDs

```txt
header.frame_id: odom
child_frame_id: base_link
```

### Important Fields

```txt
pose.pose.position.x
pose.pose.position.y
pose.pose.orientation
twist.twist.linear.x
twist.twist.angular.z
pose.covariance
twist.covariance
```

### Example Checks

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

### Validation Criteria

```txt
/diff_drive_controller/odom exists
type is nav_msgs/msg/Odometry
pose changes when Gazebo robot moves
child_frame_id is base_link
header.frame_id is odom
RViz Odometry display uses /diff_drive_controller/odom in Gazebo control stack
noisy_odom_node.py can subscribe to it
trajectory_validation_recorder.py can record it
```

---

## 16. `/diff_drive_controller/cmd_vel_out`

### Purpose

`/diff_drive_controller/cmd_vel_out` reports the velocity command after controller-side limiting.

It is useful for debugging whether velocity limits are being applied.

### Message Type

```txt
geometry_msgs/msg/TwistStamped
```

### Direction

```txt
Output from diff_drive_controller
```

### Producer

```txt
diff_drive_controller
```

### Consumers

```txt
CLI/debug tools
future validation tools
```

### Example Check

```bash
ros2 topic echo /diff_drive_controller/cmd_vel_out --once
```

### Validation Criteria

```txt
cmd_vel_out appears when publish_limited_velocity is true
message type is geometry_msgs/msg/TwistStamped
values reflect controller velocity limits
```

---

## 17. `/odom_noisy`

### Purpose

`/odom_noisy` is a noisy odometry stream generated from the Gazebo controller odometry topic.

It is used for validation, uncertainty modeling, EKF readiness, localization readiness, and Sim2Real-style testing.

### Message Type

```txt
nav_msgs/msg/Odometry
```

### Direction

```txt
Output from noisy_odom_node.py
```

### Producer

```txt
noisy_odom_node.py
```

### Consumers

```txt
trajectory_validation_recorder.py
future EKF/localization tools
future validation tools
```

### Input Source

`/odom_noisy` is created from:

```txt
/diff_drive_controller/odom
```

Flow:

```txt
/diff_drive_controller/odom
   ↓
noisy_odom_node.py
   ↓
/odom_noisy
```

### Noise Fields

The node adds Gaussian noise to:

```txt
x position
y position
yaw
linear velocity
angular velocity
```

### Covariance Fields

The node fills:

```txt
pose.covariance
twist.covariance
```

Important covariance indices:

```txt
pose.covariance[0]   = x variance
pose.covariance[7]   = y variance
pose.covariance[35]  = yaw variance

twist.covariance[0]  = linear velocity x variance
twist.covariance[35] = angular velocity z variance
```

Covariance stores variance:

```txt
variance = standard_deviation²
```

With default `0.02` standard deviation:

```txt
0.02² = 0.0004
```

### Default Parameters

```txt
input_topic                    = /diff_drive_controller/odom
output_topic                   = /odom_noisy
position_noise_std             = 0.02 m
yaw_noise_std                  = 0.02 rad
linear_velocity_noise_std      = 0.02 m/s
angular_velocity_noise_std     = 0.02 rad/s
random_seed                    = 42
```

### Example Run

```bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

Expected:

```txt
Day 83 noisy odometry node started
Subscribing: /diff_drive_controller/odom
Publishing:  /odom_noisy
```

### Validation Commands

With Gazebo control stack running:

```bash
ros2 topic list | grep odom
ros2 topic type /odom_noisy
ros2 topic echo /odom_noisy --once
ros2 topic echo /odom_noisy --once | grep -A 40 "covariance"
```

Expected:

```txt
/diff_drive_controller/odom
/odom_noisy
```

Expected type:

```txt
nav_msgs/msg/Odometry
```

Expected covariance values:

```txt
0.0004
1.0
```

### Validation Criteria

```txt
/odom_noisy exists when noisy_odom_node.py is running
/odom_noisy publishes nav_msgs/msg/Odometry
x and y are close to actual odometry but not identical
yaw is close to actual yaw but not identical
pose covariance is populated
twist covariance is populated
```

### Important Architecture Rule

```txt
/odom_noisy does not move Gazebo.
It is a noisy feedback stream only.
```

---

## 18. `/scan`

### Purpose

`/scan` is the simulated 2D lidar output.

The lidar is simulated in Gazebo as a `gpu_lidar` sensor attached to `lidar_link`, then bridged into ROS through `ros_gz_bridge`.

### Message Type

```txt
sensor_msgs/msg/LaserScan
```

### Direction

```txt
Output from ros_gz_bridge into ROS
```

### Producer

```txt
Gazebo gpu_lidar sensor
ros_gz_bridge parameter_bridge
```

### Consumers

```txt
RViz LaserScan display
future Nav2 costmaps
future SLAM Toolbox
future AMCL/localization workflows
```

### Important Fields

```txt
header.frame_id
angle_min
angle_max
angle_increment
range_min
range_max
ranges
intensities
```

Expected frame:

```txt
header.frame_id: lidar_link
```

### Example Checks

```bash
ros2 topic list | grep scan
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

If ROS `/scan` is missing, check Gazebo side:

```bash
gz topic -l | grep scan
gz topic -e -t /scan
```

Manual bridge test:

```bash
ros2 run ros_gz_bridge parameter_bridge "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
```

### RViz Settings

```txt
Fixed Frame: odom
LaserScan Topic: /scan
Reliability Policy: Best Effort if needed
```

### Validation Criteria

```txt
/scan exists
type is sensor_msgs/msg/LaserScan
ranges are populated
lidar_link exists in TF
LaserScan appears in RViz
scan changes relative to obstacles as the robot moves
```

---

## 19. `/clock`

### Purpose

`/clock` provides Gazebo simulation time to ROS nodes and RViz.

It is required when nodes use `use_sim_time:=true`.

### Message Type

```txt
rosgraph_msgs/msg/Clock
```

### Direction

```txt
Output from ros_gz_bridge into ROS
```

### Producer

```txt
Gazebo Sim
ros_gz_bridge parameter_bridge
```

### Consumers

```txt
RViz when use_sim_time is true
robot_state_publisher when use_sim_time is true
controller-related nodes using simulation time
other ROS nodes using simulation time
```

### Example Check

```bash
ros2 topic list | grep clock
ros2 topic echo /clock --once
```

### Validation Criteria

```txt
/clock exists during Gazebo launch
/clock publishes rosgraph_msgs/msg/Clock
RViz launched with use_sim_time tracks Gazebo motion
TF_OLD_DATA warnings are absent after a clean restart
```

### Common Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `No clock received` | clock bridge missing or Gazebo paused | `ros2 topic echo /clock --once` |
| `TF_OLD_DATA` | stale nodes or wall-time/sim-time mismatch | restart stack and use `rviz2 --ros-args -p use_sim_time:=true` |
| RViz robot stationary while Gazebo moves | RViz using wall time or wrong odom topic | set sim time and `/diff_drive_controller/odom` |

---

## 20. Trajectory Validation CSV Interface

The Day 84 recorder is not only a ROS topic consumer. It also creates a CSV data interface.

### Producer

```txt
trajectory_validation_recorder.py
```

### Output File

```txt
data/day84_trajectory_validation.csv
```

### Input Topics

```txt
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/odom_noisy
```

### CSV Columns

```txt
time_sec
cmd_linear_x
cmd_angular_z
actual_x
actual_y
actual_yaw
actual_linear_x
actual_angular_z
noisy_x
noisy_y
noisy_yaw
```

### Recorder Flow

```txt
cmd_vel callback
   ↓
store latest commanded linear velocity and yaw rate

actual odom callback
   ↓
store latest actual x, y, yaw, linear velocity, yaw rate

noisy odom callback
   ↓
store latest noisy x, y, yaw

timer at 20 Hz
   ↓
write latest values to CSV
```

### Validation Commands

```bash
cd "~/robotics_projects/cpp_robotics_sim_foundation"

ls data/day84_trajectory_validation.csv
head data/day84_trajectory_validation.csv
wc -l data/day84_trajectory_validation.csv
```

Expected header:

```txt
time_sec,cmd_linear_x,cmd_angular_z,actual_x,actual_y,actual_yaw,actual_linear_x,actual_angular_z,noisy_x,noisy_y,noisy_yaw
```

### Validation Criteria

```txt
CSV file exists
CSV has the expected header
CSV contains command values
CSV contains actual odometry values
CSV contains noisy odometry values
noisy fields are not blank after /odom_noisy is active
```

---

## 21. Plot and Report File Interface

Day 85 converts the CSV interface into plot and report artifacts.

### Producer

```txt
plot_trajectory_validation.py
```

### Input File

```txt
data/day84_trajectory_validation.csv
```

### Output Files

```txt
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

### Plot Contents

```txt
actual vs noisy trajectory
yaw over time
commanded vs actual linear velocity
commanded vs actual yaw rate
```

### Report Metrics

```txt
sample count
duration
actual path length
final actual x
final actual y
final actual yaw
mean position noise error
max position noise error
mean yaw noise error
max yaw noise error
max commanded linear velocity
max actual linear velocity
max commanded yaw rate
max actual yaw rate
```

### Generation Command

Run from the repository root:

```bash
python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

### Validation Commands

```bash
ls plots/trajectory_validation.png
ls docs/trajectory_validation_report.md
ls -lh plots/trajectory_validation.png

grep -n "actual path length" docs/trajectory_validation_report.md
grep -n "mean position noise error" docs/trajectory_validation_report.md
grep -n "max actual linear velocity" docs/trajectory_validation_report.md
grep -n "max actual yaw rate" docs/trajectory_validation_report.md
```

### Validation Criteria

```txt
plot exists
plot file is not empty
report exists
report contains path length
report contains final pose
report contains mean/max position noise error
report contains mean/max yaw noise error
report contains max velocity and yaw rate metrics
```

---


## 22. GoogleTest Unit-Test Interface — Day 86

Day 86 adds a C++ unit-test interface using GoogleTest.

This is not a ROS topic interface. It is a software validation interface.

### 22.1 Testable Core Header

```txt
ros2_ws/src/cpp_robotics_sim_ros/include/cpp_robotics_sim_ros/day86_testable_core.hpp
```

The header contains deterministic functions and data structures that can be tested without starting ROS 2 or Gazebo:

```txt
Pose2D
clamp()
wrapToPi()
integratePose()
```

### 22.2 GoogleTest Source File

```txt
ros2_ws/src/cpp_robotics_sim_ros/test/test_day86_core.cpp
```

The test file validates:

```txt
command/value clamping
angle normalization
forward pose integration
side-direction pose integration
pure rotation
theta wrapping after integration
repeated deterministic integration
invalid negative timestep handling
```

### 22.3 CMake Test Target

The CMake interface is:

```cmake
ament_add_gtest(test_day86_core
  test/test_day86_core.cpp
)
```

The test executable is registered with `colcon test`.

### 22.4 Test Command

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+

colcon test-result --verbose
```

Expected result:

```txt
Summary: 17 tests, 0 errors, 0 failures, 0 skipped
```

### 22.5 Interface Meaning

GoogleTest validates small deterministic C++ functions.

It answers:

```txt
Is this function correct?
```

It does not answer:

```txt
Did Gazebo launch?
Did RViz visualize?
Did /scan publish?
Did the robot navigate?
```

Those are launch, regression, or simulation validation questions.

---

## 23. GitHub Actions CI Interface — Day 87

Day 87 adds a remote build/test interface through GitHub Actions.

This is not a ROS topic interface. It is a repository automation interface.

### 23.1 Workflow File

```txt
.github/workflows/ros2_jazzy_ci.yml
```

### 23.2 CI Trigger

The workflow runs on:

```txt
push to main
pull request to main
manual workflow_dispatch
```

### 23.3 CI Environment

```txt
ubuntu-24.04
ROS 2 Jazzy
colcon
ament_cmake
ament_cmake_gtest
```

### 23.4 CI Flow

```txt
GitHub push / pull request
   ↓
checkout repository
   ↓
install ROS 2 Jazzy dependencies
   ↓
rosdep install package dependencies
   ↓
colcon build
   ↓
colcon test
   ↓
upload colcon test logs
   ↓
pass/fail status badge
```

### 23.5 CI Output

The workflow produces:

```txt
GitHub Actions pass/fail status
colcon test logs artifact
README CI badge status
```

### 23.6 Current CI Scope

Current CI validates:

```txt
the ROS 2 workspace builds
the GoogleTest target builds
the GoogleTest suite passes
test logs upload as an artifact
```

Current CI does not yet validate:

```txt
Gazebo launch runtime
controller activation
/scan runtime behavior
/clock runtime behavior
Nav2 behavior
full simulation scenario scoring
```

### 23.7 Interface Meaning

CI answers:

```txt
Can the project build and run its test suite automatically in a clean remote environment?
```

---

## 24. Performance Benchmark Interface — Day 88

Day 88 adds a deterministic C++ benchmark executable.

This is not a ROS topic interface. It is a CLI executable and file-output interface.

### 24.1 Executable

```txt
day88_performance_benchmark
```

Package executable path after build/install:

```txt
cpp_robotics_sim_ros day88_performance_benchmark
```

### 24.2 Source File

```txt
ros2_ws/src/cpp_robotics_sim_ros/src/day88_performance_benchmark.cpp
```

### 24.3 Input Arguments

```txt
--output <csv_path>
--report <markdown_path>
--sim-duration <seconds>
--virtual-robots <count>
--trials <count>
```

Default benchmark configuration:

```txt
dt values: 0.1, 0.01, 0.001
simulated duration: 10 seconds
virtual robot states: 1000
trials per dt: 5
```

### 24.4 Output Files

```txt
data/day88_performance_results.csv
docs/performance_report.md
```

### 24.5 Benchmark Command

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

ros2 run cpp_robotics_sim_ros day88_performance_benchmark --output data/day88_performance_results.csv --report docs/performance_report.md
```

### 24.6 CSV Columns

```txt
dt
simulated_duration_sec
steps
virtual_robot_count
trials
total_updates
mean_total_wall_ms
mean_avg_step_us
max_step_us
mean_realtime_factor
checksum
```

### 24.7 Observed Results

```txt
dt=0.1    steps=100     mean wall time ≈ 1.83 ms     RTF ≈ 5684.98
dt=0.01   steps=1000    mean wall time ≈ 17.40 ms    RTF ≈ 574.99
dt=0.001  steps=10000   mean wall time ≈ 174.74 ms   RTF ≈ 57.23
```

### 24.8 Interface Meaning

The performance benchmark answers:

```txt
How expensive is the deterministic C++ pose-update layer for different timestep values?
```

It does not include:

```txt
Gazebo physics
ROS middleware overhead
TF publishing
sensor simulation
RViz rendering
rosbag logging
Nav2 behavior
```

---

## 25. Validation Checkpoint and Assessment Interfaces — Days 89-90

Days 89-90 add documentation and assessment interfaces around the current project state.

### 25.1 Day 89 Validation Checkpoint

```txt
docs/day89_validation_checkpoint.md
```

This document records:

```txt
local build status
GoogleTest status
GitHub Actions CI status
performance benchmark status
current validation artifacts
what is validated
what is not yet automated
```

### 25.2 Day 90 Final Assessment

Day 90 is an assessment and interview-simulation checkpoint.

It does not add a new ROS topic.

It checks whether the project can be explained through:

```txt
architecture
interfaces
TF ownership
Gazebo vs RViz
ros2_control ownership
validation layers
GoogleTest and CI
performance benchmark results
current limitations
next implementation phase
```

### 25.3 Day 90 Interface Meaning

Day 90 answers:

```txt
Can the full system be explained, validated, defended, and extended?
```

It is a readiness checkpoint before the next implementation phase.

---

## 26. Interface Flow Summary

### 26.1 Kinematic Simulator Command-to-State Flow

```txt
/cmd_vel
   ↓
cmdVelCallback()
   ↓
store latest command and timestamp
   ↓
timerCallback()
   ↓
check timeout
   ↓
clamp velocity
   ↓
integrate pose
   ↓
publish /robot_pose
   ↓
publish /odom
   ↓
broadcast odom -> base_link
   ↓
publish /diagnostics
```

### 26.2 Robot-Description-to-TF Flow

```txt
diffbot.xacro
   ↓
xacro command in description.launch.py
   ↓
robot_description parameter
   ↓
robot_state_publisher
   ↓
/tf_static for fixed joints
/tf for moving joints
```

### 26.3 Joint-State-to-Link-TF Flow

```txt
joint_state_publisher or joint_state_broadcaster
   ↓
/joint_states
   ↓
robot_state_publisher
   ↓
base_link -> left_wheel_link
base_link -> right_wheel_link
```

### 26.4 Gazebo Spawn Flow

```txt
/robot_description
   ↓
ros_gz_sim create
   ↓
diffbot model appears in Gazebo
```

### 26.5 Gazebo Control Flow

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
/diff_drive_controller/odom
/tf odom -> base_link
```

### 26.6 Noisy Odometry Flow

```txt
/diff_drive_controller/odom
   ↓
noisy_odom_node.py
   ↓
/odom_noisy
```

### 26.7 Validation Recording Flow

```txt
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/odom_noisy
   ↓
trajectory_validation_recorder.py
   ↓
data/day84_trajectory_validation.csv
```

### 26.8 Plot/Report Flow

```txt
data/day84_trajectory_validation.csv
   ↓
plot_trajectory_validation.py
   ↓
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

### 26.9 Sensor Bridge Flow

```txt
Gazebo gpu_lidar on lidar_link
   ↓
Gazebo /scan
   ↓
ros_gz_bridge
   ↓
ROS /scan
   ↓
RViz LaserScan / future Nav2 / future SLAM
```

### 26.10 Clock Bridge Flow

```txt
Gazebo simulation clock
   ↓
ros_gz_bridge
   ↓
ROS /clock
   ↓
RViz and ROS nodes using use_sim_time
```


### 26.11 GoogleTest Flow

```txt
day86_testable_core.hpp
   ↓
test_day86_core.cpp
   ↓
test_day86_core executable
   ↓
colcon test
   ↓
test result XML and console output
```

### 26.12 GitHub Actions CI Flow

```txt
push / pull_request / workflow_dispatch
   ↓
GitHub Actions runner on ubuntu-24.04
   ↓
install ROS 2 Jazzy dependencies
   ↓
colcon build
   ↓
colcon test
   ↓
CI badge and log artifact
```

### 26.13 Performance Benchmark Flow

```txt
day88_performance_benchmark
   ↓
integratePose() timing loop
   ↓
data/day88_performance_results.csv
   ↓
docs/performance_report.md
```


---

## 27. Full Interface Contract

The simulator should satisfy this contract:

```txt
If /cmd_vel publishes valid commands:
  custom kinematic robot pose should update

If /cmd_vel stops:
  custom kinematic robot should stop after cmd_timeout

If custom robot pose updates:
  /robot_pose, /odom, and odom -> base_link TF should remain consistent

If diagnostics is active:
  /diagnostics should report OK or WARN based on timeout state

If launch arguments override parameters:
  topic behavior should reflect the overridden values

If description.launch.py is running:
  /robot_description, /joint_states, /tf, and /tf_static should exist

If /joint_states is active:
  wheel link transforms should exist

If robot_model_viz.launch.py is running:
  RViz should show Grid, TF, RobotModel, and Odometry

If gazebo_spawn.launch.py is running:
  Gazebo should open and spawn diffbot from /robot_description

If ros2_control.launch.py is running:
  controller_manager should load joint_state_broadcaster and diff_drive_controller

If diff_drive_controller receives TwistStamped commands:
  Gazebo robot should move and /diff_drive_controller/odom should update

If noisy_odom_node.py is running with Gazebo odometry active:
  /odom_noisy should publish noisy nav_msgs/msg/Odometry messages

If trajectory_validation_recorder.py is running:
  command, actual odom, and noisy odom should be recorded to CSV

If plot_trajectory_validation.py is executed:
  a plot and validation report should be generated from the CSV

If the lidar sensor and bridge are active:
  /scan should publish sensor_msgs/msg/LaserScan

If RViz is visualizing Gazebo data:
  RViz should use simulation time from /clock

If colcon test is executed:
  GoogleTest should run test_day86_core and report zero failures

If GitHub Actions CI runs:
  the workspace should build and GoogleTest should pass on Ubuntu 24.04

If day88_performance_benchmark is executed:
  data/day88_performance_results.csv and docs/performance_report.md should be generated

If Day 89-90 documentation is current:
  validation state, limitations, and next-phase readiness should be clear
```

---

## 28. Full Interface Validation Commands

### 28.1 Start Custom Simulator

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

### 28.2 List Topics

```bash
ros2 topic list
```

### 28.3 Check Custom Simulator Topic Types

```bash
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
ros2 topic type /diagnostics
```

### 28.4 Check Custom Simulator Messages

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 topic echo --once /diagnostics
ros2 run tf2_ros tf2_echo odom base_link
```

### 28.5 Check Custom Simulator QoS

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /diagnostics --verbose
```

### 28.6 Send Custom Simulator Command

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

### 28.7 Launch Robot Description Stack

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

### 28.8 Check Robot Description

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt
```

### 28.9 Check Joint States

```bash
ros2 topic echo /joint_states --once
```

### 28.10 Check Static Transform

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected:

```txt
base_link -> caster_link
base_link -> lidar_link
```

### 28.11 Check Dynamic Wheel and Lidar Transforms

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link lidar_link
```

### 28.12 Launch RViz RobotModel Stack

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

Expected RViz displays:

```txt
Grid
TF
RobotModel
Odometry
```

### 28.13 Launch Gazebo Spawn Stack

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected:

```txt
Gazebo opens
ground plane appears
diffbot appears in the world
```

### 28.14 Launch Gazebo Control and Sensor Stack

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Expected controllers:

```bash
ros2 control list_controllers
```

```txt
joint_state_broadcaster active
diff_drive_controller active
```

Expected Gazebo control topics:

```bash
ros2 topic type /diff_drive_controller/cmd_vel
ros2 topic type /diff_drive_controller/odom
ros2 topic echo /diff_drive_controller/odom --once
```

Expected lidar and clock topics:

```bash
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 topic echo /clock --once
```

Drive Gazebo robot:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

### 28.15 Run Noisy Odometry Node

```bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

Validation:

```bash
ros2 topic list | grep odom
ros2 topic type /odom_noisy
ros2 topic echo /odom_noisy --once
ros2 topic echo /odom_noisy --once | grep -A 40 "covariance"
```

Expected:

```txt
/odom_noisy exists
/odom_noisy type is nav_msgs/msg/Odometry
covariance values are populated
```

### 28.16 Run Trajectory Validation Recorder

From repository root:

```bash
cd "~/robotics_projects/cpp_robotics_sim_foundation"
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run cpp_robotics_sim_ros trajectory_validation_recorder.py
```

Command robot motion:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

Verify CSV:

```bash
ls data/day84_trajectory_validation.csv
head data/day84_trajectory_validation.csv
wc -l data/day84_trajectory_validation.csv
```

### 28.17 Generate Plot and Report

From repository root:

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

### 28.18 Run Launch Regression

```bash
cd "~/robotics_projects/cpp_robotics_sim_foundation"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```


### 28.19 Run GoogleTest

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

### 28.20 Check GitHub Actions CI

```txt
GitHub repository -> Actions -> ROS 2 Jazzy CI
```

Expected:

```txt
ROS 2 Jazzy CI: Passing
```

### 28.21 Run Performance Benchmark

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

ros2 run cpp_robotics_sim_ros day88_performance_benchmark --output data/day88_performance_results.csv --report docs/performance_report.md
```

Expected outputs:

```txt
data/day88_performance_results.csv
docs/performance_report.md
```


---

## 29. Common Interface Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `/cmd_vel` has no subscriber | `sim_node` not running | `ros2 topic info /cmd_vel` |
| `/robot_pose` missing | publisher not created or node crashed | `ros2 topic list` |
| `/odom` missing | odom publisher missing or node not rebuilt | `ros2 topic list` |
| `/tf` missing | transform broadcaster issue | `ros2 run tf2_ros tf2_echo odom base_link` |
| `/diagnostics` missing | diagnostics publisher missing | `ros2 topic list` |
| wrong message type | topic name reused incorrectly | `ros2 topic type <topic>` |
| no motion after command | command not received, timeout active, or velocity clamped to zero | `/diagnostics` and `/robot_pose` |
| motion never stops | timeout logic broken | stop `/cmd_vel` and watch diagnostics |
| RViz frame error | TF missing or wrong fixed frame | set Fixed Frame to `odom` |
| diagnostics always WARN | no active `/cmd_vel` stream | publish `/cmd_vel` at 10 Hz |
| diagnostics always OK | timeout state not wired to diagnostics | check timeout logic |
| `/robot_description` missing | `robot_state_publisher` not running | `ros2 node list` |
| robot description XML parsed as YAML | missing `ParameterValue(..., value_type=str)` | inspect `description.launch.py` |
| Xacro command fails with spaces in path | model path not quoted | inspect `Command(['xacro "', model, '"'])` |
| `/joint_states` missing | `joint_state_publisher` not installed/launched or broadcaster inactive | `ros2 node list`, `ros2 control list_controllers` |
| wheel links missing in TF | no joint states or joint name mismatch | `ros2 topic echo /joint_states --once` |
| `/tf_static` echo shows no output | wrong QoS for static transform echo | use transient local durability |
| RobotModel display is red | missing robot description or TF | check `/robot_description`, `/joint_states`, `/tf` |
| Gazebo opens but no robot appears | spawn failed or `/robot_description` missing | inspect launch terminal output |
| Gazebo robot does not drive | controller inactive, wrong command topic, or wrong message type | `ros2 control list_controllers`, publish `TwistStamped` to controller |
| `diff_drive_controller` missing | spawner missing or YAML issue | `ros2 control list_controllers` |
| wheel names empty | `ros2_control.yaml` indentation wrong | inspect installed controller YAML |
| `/controller_manager` missing | `gz_ros2_control` plugin failed | inspect Gazebo launch output |
| Gazebo moves but RViz stays still | RViz sim-time mismatch or wrong odom topic | use `/clock`, `use_sim_time:=true`, `/diff_drive_controller/odom` |
| `/scan` missing | lidar sensor or bridge not running | `gz topic -l`, `ros2 topic list` |
| LaserScan display empty | RViz topic not selected or QoS mismatch | set topic `/scan`, Reliability Best Effort |
| `TF_OLD_DATA` warnings | stale nodes or wall-time/sim-time mismatch | restart stack and use simulation time |
| `/odom_noisy` missing | noisy odometry node not running or not installed | `ros2 pkg executables cpp_robotics_sim_ros | grep noisy` |
| `/odom_noisy` exists but no messages | `/diff_drive_controller/odom` not publishing | launch Gazebo control stack and echo controller odom |
| noisy covariance is all zero | covariance assignment bug | inspect `set_covariance()` in `noisy_odom_node.py` |
| `python3\r` shebang error | Windows CRLF line endings | `sed -i 's/\r$//' <script.py>` and use LF in VS Code |
| recorder CSV missing | recorder launched from wrong workspace or not running | check recorder terminal and `ls data/` |
| recorder CSV has blank noisy fields | `/odom_noisy` was not running before recording | start noisy node before recorder |
| plot script cannot find CSV | wrong working directory or wrong `--csv` path | run from repo root or pass absolute path |
| matplotlib import error | Python plotting dependency missing | `sudo apt install -y python3-matplotlib` |
| `.sdf` world missing on GitHub | `.gitignore` ignored SDF files | `git check-ignore -v`, `git add -f` |
| GoogleTest target missing | CMake test target not registered | check `ament_add_gtest(test_day86_core ...)` |
| `colcon test-result` shows old lint failures | stale test results from earlier run | `colcon test-result --delete`, rerun tests |
| GitHub Actions fails before build | dependency install or rosdep issue | inspect Actions log step that failed |
| CI badge not updating | wrong workflow filename or badge URL | verify `.github/workflows/ros2_jazzy_ci.yml` |
| performance benchmark not found | workspace not rebuilt or not sourced | rebuild and `source install/setup.bash` |
| benchmark report missing | wrong working directory or output path | run benchmark from repo root |
| CSV ignored by Git | `.gitignore` contains `*.csv` | expected for raw data, use `git add -f` only if intentional |

---

## 30. Interface Ownership Summary

### 30.1 `sim_node` Owns in the Kinematic Simulator Stack

```txt
/cmd_vel subscriber
/robot_pose publisher
/odom publisher
/tf broadcaster for odom -> base_link
/diagnostics publisher
```

### 30.2 `robot_state_publisher` Owns

```txt
/robot_description
/tf for robot link transforms
/tf_static for fixed robot link transforms
```

### 30.3 `joint_state_publisher` Owns in the Visualization-Only Description Stack

```txt
/joint_states
```

### 30.4 `joint_state_broadcaster` Owns in the Gazebo ros2_control Stack

```txt
/joint_states
/dynamic_joint_states
```

### 30.5 `diff_drive_controller` Owns in the Gazebo Control Stack

```txt
/diff_drive_controller/cmd_vel subscriber
/diff_drive_controller/odom publisher
/diff_drive_controller/cmd_vel_out publisher
/tf broadcaster for odom -> base_link when enable_odom_tf is true
wheel velocity command interfaces through ros2_control
```

### 30.6 `noisy_odom_node.py` Owns

```txt
/diff_drive_controller/odom subscriber
/odom_noisy publisher
pose and twist covariance assignment for noisy odometry
```

### 30.7 `trajectory_validation_recorder.py` Owns

```txt
/diff_drive_controller/cmd_vel subscriber
/diff_drive_controller/odom subscriber
/odom_noisy subscriber
data/day84_trajectory_validation.csv writer
```

### 30.8 `plot_trajectory_validation.py` Owns

```txt
data/day84_trajectory_validation.csv reader
plots/trajectory_validation.png writer
docs/trajectory_validation_report.md writer
```

### 30.9 `ros_gz_bridge` Owns

```txt
/clock bridge from Gazebo to ROS
/scan bridge from Gazebo to ROS
```

### 30.10 Gazebo Spawn Workflow Uses

```txt
/robot_description
ros_gz_sim create
empty_diffbot_world.sdf
```

### 30.11 Gazebo Sensor Workflow Uses

```txt
lidar_link
gpu_lidar sensor
Gazebo /scan
ROS /scan
```

### 30.12 GoogleTest Owns

```txt
test_day86_core executable
test result XML under build/cpp_robotics_sim_ros/test_results/
unit-test validation for clamp, wrapToPi, and integratePose
```

### 30.13 GitHub Actions Owns

```txt
remote build/test workflow
CI pass/fail status
colcon test log artifact
README badge status
```

### 30.14 Day 88 Benchmark Owns

```txt
day88_performance_benchmark executable
data/day88_performance_results.csv
docs/performance_report.md
```

### 30.15 Day 89-90 Documentation Owns

```txt
validation checkpoint
assessment summary
current limitations
next-phase readiness notes
```


---

## 31. Interview Explanation

The project exposes two main robot-motion interfaces, one sensor interface, one validation interface, and one software-quality interface.

The original kinematic simulator subscribes to `/cmd_vel` using `geometry_msgs/msg/Twist`, publishes a simple `/robot_pose` using `geometry_msgs/msg/Pose2D`, publishes standard `/odom` using `nav_msgs/msg/Odometry`, broadcasts `odom -> base_link` on TF, and publishes runtime health on `/diagnostics` using `diagnostic_msgs/msg/DiagnosticArray`.

The robot description stack converts `diffbot.xacro` into `/robot_description`. `robot_state_publisher` uses that model plus `/joint_states` to publish the robot link transforms below `base_link`. In the visualization-only stack, `/joint_states` comes from `joint_state_publisher`. In the Gazebo control stack, `/joint_states` comes from `joint_state_broadcaster`.

The Gazebo control stack uses `/diff_drive_controller/cmd_vel` as the actuation input. `diff_drive_controller` converts `TwistStamped` body velocity commands into wheel velocity commands, sends those commands through `ros2_control` and `gz_ros2_control`, moves the Gazebo wheel joints, and publishes `/diff_drive_controller/odom` plus the moving `odom -> base_link` transform.

The sensor stack simulates a lidar on `lidar_link` in Gazebo. `ros_gz_bridge` converts the Gazebo scan into the ROS `/scan` topic as `sensor_msgs/msg/LaserScan`. It also bridges `/clock` so RViz and ROS nodes can use simulation time.

The validation stack adds noisy odometry and data recording. `noisy_odom_node.py` subscribes to `/diff_drive_controller/odom`, adds controlled Gaussian noise and covariance, and publishes `/odom_noisy`. `trajectory_validation_recorder.py` records `/diff_drive_controller/cmd_vel`, `/diff_drive_controller/odom`, and `/odom_noisy` into a CSV. `plot_trajectory_validation.py` turns that CSV into a plot and Markdown validation report. This proves that the simulation behavior can be commanded, measured, corrupted with controlled uncertainty, recorded, plotted, and explained.

The software-quality stack adds GoogleTest, GitHub Actions CI, and performance benchmarking. GoogleTest validates deterministic C++ math functions such as `clamp`, `wrapToPi`, and `integratePose`. GitHub Actions builds the ROS 2 Jazzy workspace and runs the GoogleTest suite automatically on push or pull request. The Day 88 benchmark measures deterministic pose-update timing and generates a performance report.

Important distinction:

```txt
/diff_drive_controller/cmd_vel is an actuation command.
/odom_noisy is feedback.
/odom_noisy does not move Gazebo.
GoogleTest validates C++ functions.
CI validates build and tests.
The performance benchmark validates deterministic update-loop timing.
```

---

## 32. Day 90 Interface Summary

Through Day 90, the most important runtime and validation interfaces are:

```txt
Custom kinematic simulator:
  /cmd_vel -> sim_node -> /robot_pose, /odom, /tf, /diagnostics

Gazebo control:
  /diff_drive_controller/cmd_vel
      -> diff_drive_controller
      -> ros2_control
      -> gz_ros2_control
      -> Gazebo wheel joints
      -> /diff_drive_controller/odom, /tf, /joint_states

Sensor:
  Gazebo lidar -> ros_gz_bridge -> /scan

Simulation time:
  Gazebo clock -> ros_gz_bridge -> /clock

Noisy odometry:
  /diff_drive_controller/odom -> noisy_odom_node.py -> /odom_noisy

Trajectory validation:
  /diff_drive_controller/cmd_vel
  /diff_drive_controller/odom
  /odom_noisy
      -> trajectory_validation_recorder.py
      -> data/day84_trajectory_validation.csv
      -> plot_trajectory_validation.py
      -> plots/trajectory_validation.png
      -> docs/trajectory_validation_report.md

Unit testing:
  day86_testable_core.hpp
      -> test_day86_core.cpp
      -> GoogleTest
      -> colcon test

Continuous integration:
  .github/workflows/ros2_jazzy_ci.yml
      -> GitHub Actions
      -> colcon build
      -> colcon test
      -> CI badge and test logs

Performance benchmarking:
  day88_performance_benchmark
      -> data/day88_performance_results.csv
      -> docs/performance_report.md

Assessment:
  docs/day89_validation_checkpoint.md
      -> Day 90 final assessment and interview simulation
```

This interface structure makes the project ready for the next roadmap phase: Nav2 working integration, SLAM/localization, EKF configuration, launch-level CI regression, deeper simulator benchmarking, and eventual v1.0 portfolio/release packaging.
