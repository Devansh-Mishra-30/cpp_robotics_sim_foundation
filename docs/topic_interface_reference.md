# ROS 2 Topic Interface Reference

This document defines the ROS 2 topic interfaces used by the `cpp_robotics_sim_ros` simulator and robot description stack.

The purpose of this document is to make the runtime interface clear enough that another engineer can understand what the simulator subscribes to, what it publishes, what message types are used, what fields matter, what node owns each transform, and how to validate each interface.

---

## 1. Interface Overview

The simulator exposes a planar mobile robot through standard ROS 2 communication interfaces.

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

Days 71–76 extend the interface with robot description and visualization topics:

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

The extended frame tree is:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

Transform ownership rule:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
```

---

## 2. Topic Summary

| Topic                | Direction                       | Message Type                          | Producer                            | Consumer                                         | Purpose                             |
| -------------------- | ------------------------------- | ------------------------------------- | ----------------------------------- | ------------------------------------------------ | ----------------------------------- |
| `/cmd_vel`           | Input                           | `geometry_msgs/msg/Twist`             | external command source             | `sim_node`                                       | Velocity command input              |
| `/robot_pose`        | Output                          | `geometry_msgs/msg/Pose2D`            | `sim_node`                          | CLI/debug tools                                  | Simple 2D pose debugging output     |
| `/odom`              | Output                          | `nav_msgs/msg/Odometry`               | `sim_node`                          | RViz, validation tools, future navigation layers | Standard odometry output            |
| `/tf`                | Output                          | `tf2_msgs/msg/TFMessage`              | `sim_node`, `robot_state_publisher` | RViz, TF tools                                   | Dynamic transform tree output       |
| `/tf_static`         | Output                          | `tf2_msgs/msg/TFMessage`              | `robot_state_publisher`             | RViz, TF tools                                   | Fixed transform tree output         |
| `/diagnostics`       | Output                          | `diagnostic_msgs/msg/DiagnosticArray` | `sim_node`                          | CLI/debug/monitoring tools                       | Runtime health and simulator status |
| `/robot_description` | Output / parameter-backed topic | `std_msgs/msg/String`                 | `robot_state_publisher`             | RViz RobotModel, Gazebo spawn workflow           | Robot model XML                     |
| `/joint_states`      | Output                          | `sensor_msgs/msg/JointState`          | `joint_state_publisher`             | `robot_state_publisher`                          | Joint positions for robot links     |

---

## 3. QoS Summary

| Topic                | Endpoint   | QoS                                                                    |
| -------------------- | ---------- | ---------------------------------------------------------------------- |
| `/cmd_vel`           | Subscriber | reliable, volatile, keep_last(10)                                      |
| `/robot_pose`        | Publisher  | reliable, volatile, keep_last(10)                                      |
| `/odom`              | Publisher  | reliable, volatile, keep_last(10)                                      |
| `/diagnostics`       | Publisher  | reliable, volatile, keep_last(10)                                      |
| `/tf`                | Publisher  | handled by `tf2_ros::TransformBroadcaster` and `robot_state_publisher` |
| `/tf_static`         | Publisher  | transient local behavior expected for fixed transforms                 |
| `/robot_description` | Publisher  | transient local behavior expected                                      |
| `/joint_states`      | Publisher  | standard `joint_state_publisher` behavior                              |

The state topics use reliable communication because they are low-rate simulator outputs used for debugging and validation.

The durability for live simulator values is volatile because old commands or stale state should not be replayed automatically to late subscribers.

`/tf_static` and `/robot_description` behave differently from live command/state topics because fixed transforms and robot model descriptions should be available to late subscribers.

---

# 4. `/cmd_vel`

## Purpose

`/cmd_vel` is the velocity command input topic.

The simulator subscribes to this topic and uses it to update robot motion.

## Message Type

```txt
geometry_msgs/msg/Twist
```

## Direction

```txt
Input to sim_node
```

## Producer

```txt
external command source
ros2 topic pub command
future teleop node
future navigation/control layer
```

## Consumer

```txt
sim_node
```

## Used Fields

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

## Example Command

One-shot command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Continuous command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

## Safety Behavior

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

## Validation Commands

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

## Validation Criteria

```txt
/cmd_vel exists when sim_node is running
/cmd_vel has one subscriber
linear.x affects forward motion
angular.z affects heading motion
large commands are clamped
stale commands time out
```

---

# 5. `/robot_pose`

## Purpose

`/robot_pose` is a simple 2D pose output used for quick debugging.

It is easier to inspect than the full `/odom` message.

## Message Type

```txt
geometry_msgs/msg/Pose2D
```

## Direction

```txt
Output from sim_node
```

## Producer

```txt
sim_node
```

## Consumers

```txt
CLI debugging
validation checks
future lightweight plotting/debug tools
```

## Fields

```txt
x      = robot x position
y      = robot y position
theta  = robot heading angle in radians
```

## Example Check

```bash
ros2 topic echo --once /robot_pose
```

Expected structure:

```txt
x: ...
y: ...
theta: ...
```

## Validation Criteria

```txt
x changes during forward motion
theta changes during rotational motion
pose stops changing after command timeout
pose starts near launch-configured initial pose
pose remains consistent with /odom position and odom -> base_link TF
```

---

# 6. `/odom`

## Purpose

`/odom` is the standard ROS 2 odometry output.

It is used by RViz2, validation tools, rosbag2 workflows, and future navigation/simulation layers.

## Message Type

```txt
nav_msgs/msg/Odometry
```

## Direction

```txt
Output from sim_node
```

## Producer

```txt
sim_node
```

## Consumers

```txt
RViz Odometry display
rosbag2 recording
validation tools
future navigation/control layers
```

## Frame IDs

```txt
header.frame_id: odom
child_frame_id: base_link
```

## Important Fields

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

## Quaternion Convention

The simulator converts planar heading `theta` into yaw quaternion form:

```txt
q.x = 0
q.y = 0
q.z = sin(theta / 2)
q.w = cos(theta / 2)
```

## Example Checks

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

## Validation Criteria

```txt
header.frame_id is odom
child_frame_id is base_link
position x/y matches /robot_pose
orientation matches theta as yaw quaternion
twist values match clamped command
odom remains consistent with odom -> base_link TF
```

---

# 7. `/tf`

## Purpose

`/tf` publishes dynamic transform tree relationships.

In this project, `/tf` has two sources:

```txt
sim_node
robot_state_publisher
```

## Message Type

```txt
tf2_msgs/msg/TFMessage
```

## Direction

```txt
Output from tf2_ros::TransformBroadcaster and robot_state_publisher
```

## Transform Ownership

`sim_node` owns:

```txt
odom -> base_link
```

`robot_state_publisher` owns robot structure below `base_link`:

```txt
base_link -> left_wheel_link
base_link -> right_wheel_link
```

The fixed caster transform may appear through `/tf_static`:

```txt
base_link -> caster_link
```

## Frame Relationship

Full expected tree after Days 71–76:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

## Example Checks

Simulator transform:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Wheel transforms:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
```

Expected simulator transform structure:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

Expected wheel transform positions:

```txt
base_link -> left_wheel_link:  [0.000, 0.180, 0.080]
base_link -> right_wheel_link: [0.000, -0.180, 0.080]
```

## Validation Criteria

```txt
odom -> base_link transform exists
parent frame is odom
child frame is base_link
translation matches robot x/y
rotation matches robot theta
base_link -> wheel transforms exist when /joint_states is active
RViz2 can use odom as Fixed Frame
```

## Common Failures

| Failure                | Likely Cause                                   | First Check                                       |
| ---------------------- | ---------------------------------------------- | ------------------------------------------------- |
| `odom` missing         | simulator not running or TF broadcaster broken | `ros2 node list`, `tf2_echo odom base_link`       |
| `base_link` missing    | wrong child frame ID                           | inspect `publishTransform()`                      |
| wheel frames missing   | `/joint_states` missing                        | `ros2 topic echo /joint_states --once`            |
| duplicate TF warning   | two nodes publish same transform               | keep `odom -> base_link` owned only by `sim_node` |
| RViz fixed frame error | TF tree incomplete                             | set Fixed Frame to `odom` and check TF            |

---

# 8. `/tf_static`

## Purpose

`/tf_static` publishes fixed transforms from the robot description.

Fixed transforms are used for links that do not move relative to their parent.

## Message Type

```txt
tf2_msgs/msg/TFMessage
```

## Direction

```txt
Output from robot_state_publisher
```

## Producer

```txt
robot_state_publisher
```

## Consumers

```txt
RViz TF display
RViz RobotModel display
TF tools
```

## Expected Fixed Transform

The current fixed transform is:

```txt
base_link -> caster_link
```

Expected values:

```txt
translation.x = -0.17
translation.y = 0.0
translation.z = 0.035
rotation.w = 1.0
```

## Validation Command

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

## Validation Criteria

```txt
/tf_static exists
base_link -> caster_link is published
caster_link appears in RViz TF tree
late subscribers can receive the fixed transform
```

---

# 9. `/diagnostics`

## Purpose

`/diagnostics` publishes structured runtime health information for the simulator.

It is used to inspect node status, timeout state, current command/state values, and callback timing.

## Message Type

```txt
diagnostic_msgs/msg/DiagnosticArray
```

## Direction

```txt
Output from sim_node
```

## Producer

```txt
sim_node
```

## Consumers

```txt
CLI debugging
rosbag2 diagnostics recording
future monitoring tools
```

## Status Levels

```txt
level: 0  -> OK
level: 1  -> WARN
```

Current behavior:

```txt
OK   = simulator running with fresh command input
WARN = cmd_vel timeout active
```

## Diagnostic Identity

Expected fields:

```txt
name: sim_node
hardware_id: cpp_robotics_sim_ros
```

## Key-Value Fields

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

## Example Checks

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

## OK-State Test

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

## WARN-State Test

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

# 10. `/robot_description`

## Purpose

`/robot_description` provides the generated robot model XML.

The XML is produced from:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

The robot model describes the structure below `base_link`.

## Message Type

```txt
std_msgs/msg/String
```

The same content is also available through the `robot_description` parameter on `/robot_state_publisher`.

## Direction

```txt
Output from robot_state_publisher / parameter-backed robot model interface
```

## Producer

```txt
description.launch.py
robot_state_publisher
```

## Consumers

```txt
robot_state_publisher
RViz RobotModel display
ros_gz_sim create spawn command
debugging tools
```

## Model Content

Expected links:

```txt
base_link
left_wheel_link
right_wheel_link
caster_link
```

Expected joints:

```txt
left_wheel_joint
right_wheel_joint
caster_joint
```

Expected joint types:

```txt
left_wheel_joint   continuous
right_wheel_joint  continuous
caster_joint       fixed
```

## Validation Commands

Launch robot description stack:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Check parameter content:

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/robot_description.txt
```

Check topic existence:

```bash
ros2 topic list | grep robot_description
```

Expected:

```txt
/robot_description
```

## Validation Criteria

```txt
/robot_description exists
robot_description parameter exists on /robot_state_publisher
generated XML contains all expected links
generated XML contains all expected joints
RViz RobotModel can load the robot model
Gazebo spawn can use the robot model
```

## Common Failures

| Failure                      | Likely Cause                          | First Check                               |
| ---------------------------- | ------------------------------------- | ----------------------------------------- |
| `/robot_description` missing | `robot_state_publisher` not running   | `ros2 node list`                          |
| XML parsed as YAML           | launch parameter not forced to string | use `ParameterValue(..., value_type=str)` |
| Xacro command fails          | path quoting issue or Xacro typo      | run `xacro diffbot.xacro` manually        |
| robot model missing links    | Xacro macro/link typo                 | inspect `/tmp/robot_description.txt`      |
| RViz RobotModel red          | missing robot description or TF       | check `/robot_description` and TF tree    |

---

# 11. `/joint_states`

## Purpose

`/joint_states` publishes joint positions for the robot model joints.

For this project, it is currently used to provide wheel joint states to `robot_state_publisher`.

## Message Type

```txt
sensor_msgs/msg/JointState
```

## Direction

```txt
Output from joint_state_publisher
```

## Producer

```txt
joint_state_publisher
```

## Consumer

```txt
robot_state_publisher
```

## Expected Joint Names

```txt
left_wheel_joint
right_wheel_joint
```

The caster joint is fixed, so it does not need a moving joint state.

## Example Check

```bash
ros2 topic echo /joint_states --once
```

Expected structure:

```txt
name:
- left_wheel_joint
- right_wheel_joint
position:
- 0.0
- 0.0
```

The exact numeric values may vary if the joint state publisher is configured differently later.

## Validation Criteria

```txt
/joint_states exists
left_wheel_joint appears
right_wheel_joint appears
robot_state_publisher receives joint states
base_link -> left_wheel_link transform exists
base_link -> right_wheel_link transform exists
```

## Common Failures

| Failure                   | Likely Cause                                          | First Check                               |
| ------------------------- | ----------------------------------------------------- | ----------------------------------------- |
| `/joint_states` missing   | `joint_state_publisher` not installed or not launched | `ros2 node list`                          |
| wheel joint names missing | Xacro joint names do not match                        | inspect robot description                 |
| wheel transforms missing  | robot_state_publisher not receiving joint states      | echo `/joint_states`                      |
| package not found         | missing system package                                | install `ros-jazzy-joint-state-publisher` |

---

# 12. Interface Flow

## Command-to-State Flow

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

## Robot-Description-to-TF Flow

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

## Joint-State-to-Link-TF Flow

```txt
joint_state_publisher
   ↓
/joint_states
   ↓
robot_state_publisher
   ↓
base_link -> left_wheel_link
base_link -> right_wheel_link
```

## Gazebo Spawn Flow

```txt
/robot_description
   ↓
ros_gz_sim create
   ↓
diffbot model appears in Gazebo
```

## Runtime Inspection Flow

```txt
ros2 topic list
   ↓
ros2 topic echo /robot_pose
   ↓
ros2 topic echo /odom
   ↓
tf2_echo odom base_link
   ↓
ros2 topic echo /diagnostics
   ↓
ros2 param get /robot_state_publisher robot_description
   ↓
ros2 topic echo /joint_states
   ↓
tf2_echo base_link left_wheel_link
   ↓
ros2 topic echo /tf_static --qos-durability transient_local --once
```

---

# 13. Interface Contract

The simulator should satisfy this contract:

```txt
If /cmd_vel publishes valid commands:
  robot pose should update

If /cmd_vel stops:
  robot should stop after cmd_timeout

If robot pose updates:
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
```

---

# 14. Full Interface Validation Commands

## Start Simulator

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## List Topics

```bash
ros2 topic list
```

## Check Simulator Topic Types

```bash
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
ros2 topic type /diagnostics
```

## Check Simulator Messages

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 topic echo --once /diagnostics
ros2 run tf2_ros tf2_echo odom base_link
```

## Check QoS

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /diagnostics --verbose
```

## Send Command

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

## Launch Robot Description Stack

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

## Check Robot Description

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/robot_description.txt
```

## Check Joint States

```bash
ros2 topic echo /joint_states --once
```

## Check Static Transform

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected:

```txt
base_link -> caster_link
```

## Check Dynamic Wheel Transforms

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
```

## Launch RViz RobotModel Stack

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

## Launch Gazebo Spawn Stack

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected:

```txt
Gazebo opens
ground plane appears
diffbot appears in the world
```

## Run Launch Regression

```bash
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

# 15. Common Interface Failures

| Failure                                 | Likely Cause                                                      | First Check                                        |
| --------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------- |
| `/cmd_vel` has no subscriber            | `sim_node` not running                                            | `ros2 topic info /cmd_vel`                         |
| `/robot_pose` missing                   | publisher not created or node crashed                             | `ros2 topic list`                                  |
| `/odom` missing                         | odom publisher missing or node not rebuilt                        | `ros2 topic list`                                  |
| `/tf` missing                           | transform broadcaster issue                                       | `ros2 run tf2_ros tf2_echo odom base_link`         |
| `/diagnostics` missing                  | diagnostics publisher missing                                     | `ros2 topic list`                                  |
| wrong message type                      | topic name reused incorrectly                                     | `ros2 topic type <topic>`                          |
| no motion after command                 | command not received, timeout active, or velocity clamped to zero | `/diagnostics` and `/robot_pose`                   |
| motion never stops                      | timeout logic broken                                              | stop `/cmd_vel` and watch diagnostics              |
| RViz frame error                        | TF missing or wrong fixed frame                                   | set Fixed Frame to `odom`                          |
| diagnostics always WARN                 | no active `/cmd_vel` stream                                       | publish `/cmd_vel` at 10 Hz                        |
| diagnostics always OK                   | timeout state not wired to diagnostics                            | check timeout logic                                |
| `/robot_description` missing            | `robot_state_publisher` not running                               | `ros2 node list`                                   |
| robot description XML parsed as YAML    | missing `ParameterValue(..., value_type=str)`                     | inspect `description.launch.py`                    |
| Xacro command fails with spaces in path | model path not quoted                                             | inspect `Command(['xacro "', model, '"'])`         |
| `/joint_states` missing                 | `joint_state_publisher` not installed or not launched             | `ros2 node list`                                   |
| wheel links missing in TF               | no joint states or joint name mismatch                            | `ros2 topic echo /joint_states --once`             |
| `/tf_static` echo shows no output       | wrong QoS for static transform echo                               | use transient local durability                     |
| RobotModel display is red               | missing robot description or TF                                   | check `/robot_description`, `/joint_states`, `/tf` |
| Gazebo opens but no robot appears       | spawn failed or `/robot_description` missing                      | inspect launch terminal output                     |
| Gazebo robot does not drive             | expected at Day 76                                                | Day 77/78 adds control/plugin work                 |

---

# 16. Interface Ownership Summary

## `sim_node` Owns

```txt
/cmd_vel subscriber
/robot_pose publisher
/odom publisher
/tf broadcaster for odom -> base_link
/diagnostics publisher
```

## `robot_state_publisher` Owns

```txt
/robot_description
/tf for robot link transforms
/tf_static for fixed robot link transforms
```

## `joint_state_publisher` Owns

```txt
/joint_states
```

## Gazebo Spawn Workflow Uses

```txt
/robot_description
ros_gz_sim create
empty_diffbot_world.sdf
```

---

# 17. Interview Explanation

The simulator exposes a clear ROS 2 topic interface. It subscribes to `/cmd_vel` using `geometry_msgs/msg/Twist`, publishes a simple `/robot_pose` using `geometry_msgs/msg/Pose2D`, publishes standard `/odom` using `nav_msgs/msg/Odometry`, broadcasts `odom -> base_link` on TF, and publishes runtime health on `/diagnostics` using `diagnostic_msgs/msg/DiagnosticArray`.

Days 71–76 extend the interface with robot description topics. The Xacro model is converted into `/robot_description`, `joint_state_publisher` provides `/joint_states`, and `robot_state_publisher` publishes the robot link transforms below `base_link`. The simulator still owns `odom -> base_link`, which keeps transform ownership clean. RViz uses `/robot_description`, `/joint_states`, `/tf`, `/tf_static`, and `/odom` to visualize the full robot model, while Gazebo uses `/robot_description` to spawn the robot into the simulation world.
