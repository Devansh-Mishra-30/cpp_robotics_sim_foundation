# ROS 2 Topic Interface Reference

This document defines the ROS 2 topic interfaces used by the `cpp_robotics_sim_ros` simulator, robot description stack, Gazebo `ros2_control` stack, differential-drive controller, and simulated lidar sensor workflow.

The purpose of this document is to make the runtime interface clear enough that another engineer can understand what each stack subscribes to, what it publishes, what message types are used, what fields matter, what node owns each transform, and how to validate each interface through Day 80.

---

## 1. Interface Overview

The project has two related runtime interfaces.

The original kinematic simulator stack exposes a planar mobile robot through `sim_node`:

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

The robot description stack exposes the robot structure:

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

The Gazebo control and sensor stack exposes a physics-simulated robot:

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

The simulated lidar stack exposes sensor data:

```txt
Gazebo gpu_lidar
   ↓
Gazebo /scan
   ↓
ros_gz_bridge
   ↓
ROS /scan
```

The extended frame tree through Day 80 is:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

Transform ownership rule for the kinematic simulator stack:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

Transform ownership rule for the Gazebo control stack:

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

## 2. Topic Summary

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
| `/dynamic_joint_states` | Output | `control_msgs/msg/DynamicJointState` | `joint_state_broadcaster` | debugging/control tools | Detailed ros2_control joint interface states |
| `/diff_drive_controller/cmd_vel` | Input | `geometry_msgs/msg/TwistStamped` | CLI/teleop/future navigation | `diff_drive_controller` | Velocity command input for Gazebo-driven robot |
| `/diff_drive_controller/odom` | Output | `nav_msgs/msg/Odometry` | `diff_drive_controller` | RViz, validation tools, future navigation | Odometry output from Gazebo diff-drive controller |
| `/diff_drive_controller/cmd_vel_out` | Output | `geometry_msgs/msg/TwistStamped` | `diff_drive_controller` | CLI/debug tools | Limited velocity command after controller limits |
| `/scan` | Output | `sensor_msgs/msg/LaserScan` | `ros_gz_bridge` from Gazebo lidar | RViz, future Nav2/SLAM/costmaps | Simulated 2D lidar scan |
| `/clock` | Output | `rosgraph_msgs/msg/Clock` | `ros_gz_bridge` from Gazebo | ROS nodes and RViz using sim time | Simulation time source |

`controller_manager` also exposes ROS services used by the `ros2 control` CLI and controller spawners, but the main user-facing runtime interfaces in this document are topics.

---

## 3. QoS Summary

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
| `/scan` | bridge publisher | sensor-style QoS; RViz may need Best Effort |
| `/clock` | bridge publisher | simulation-time clock QoS |

The kinematic simulator state topics use reliable communication because they are low-rate outputs used for debugging and validation.

The durability for live simulator values is volatile because old commands or stale state should not be replayed automatically to late subscribers.

`/tf_static` and `/robot_description` behave differently from live command/state topics because fixed transforms and robot model descriptions should be available to late subscribers.

High-rate sensor topics such as `/scan` are commonly visualized with Best Effort reliability in RViz if a reliability mismatch appears.

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

In this project, `/tf` can have different sources depending on the launch stack:

```txt
sim_node
robot_state_publisher
diff_drive_controller
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

## Frame Relationship

Full expected tree after Days 71-80:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
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
base_link -> lidar_link transform exists after Day 79
RViz2 can use odom as Fixed Frame
```

## Common Failures

| Failure                | Likely Cause                                   | First Check                                       |
| ---------------------- | ---------------------------------------------- | ------------------------------------------------- |
| `odom` missing         | simulator not running or TF broadcaster broken | `ros2 node list`, `tf2_echo odom base_link`       |
| `base_link` missing    | wrong child frame ID                           | inspect `publishTransform()`                      |
| wheel frames missing   | `/joint_states` missing                        | `ros2 topic echo /joint_states --once`            |
| duplicate TF warning   | two nodes publish same transform               | do not run `sim_node` and `diff_drive_controller` as `odom -> base_link` owners together |
| `TF_OLD_DATA` warnings | RViz/Gazebo sim-time mismatch or stale nodes | restart stack, verify `/clock`, launch RViz with `use_sim_time:=true` |
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

Current fixed transforms include:

```txt
base_link -> caster_link
base_link -> lidar_link
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
base_link -> lidar_link is published after Day 79
caster_link and lidar_link appear in RViz TF tree
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

## Validation Commands

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

## Validation Criteria

```txt
/robot_description exists
robot_description parameter exists on /robot_state_publisher
generated XML contains all expected links
generated XML contains all expected joints
generated XML contains ros2_control wheel interfaces
generated XML contains lidar sensor configuration after Day 79
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

For this project, it provides wheel joint states to `robot_state_publisher`.

In the visualization-only stack, `/joint_states` comes from `joint_state_publisher`.

In the Gazebo `ros2_control` stack, `/joint_states` comes from `joint_state_broadcaster`.

## Message Type

```txt
sensor_msgs/msg/JointState
```

## Direction

```txt
Output from `joint_state_publisher` or `joint_state_broadcaster`, depending on launch stack
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

The exact numeric values may vary. In the Gazebo control stack, values come from simulated hardware state interfaces through `joint_state_broadcaster`.

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

# 12. `/diff_drive_controller/cmd_vel`

## Purpose

`/diff_drive_controller/cmd_vel` is the velocity command input for the Gazebo-driven robot.

Unlike the original `/cmd_vel` used by `sim_node`, this controller topic expects a stamped command.

## Message Type

```txt
geometry_msgs/msg/TwistStamped
```

## Direction

```txt
Input to diff_drive_controller
```

## Producer

```txt
ros2 topic pub command
future teleop node
future Nav2 controller output after remapping/relay
```

## Consumer

```txt
diff_drive_controller
```

## Used Fields

```txt
twist.linear.x   = forward velocity command
twist.angular.z  = yaw velocity command
```

## Example Command

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

## Validation Criteria

```txt
/diff_drive_controller/cmd_vel exists when diff_drive_controller is active
message type is geometry_msgs/msg/TwistStamped
linear.x drives forward/backward motion in Gazebo
angular.z drives rotation in Gazebo
robot stops after controller timeout when commands stop
```

---

# 13. `/diff_drive_controller/odom`

## Purpose

`/diff_drive_controller/odom` is the odometry output from the Gazebo differential-drive controller.

It represents the Gazebo-controlled robot state, not the custom `sim_node` kinematic state.

## Message Type

```txt
nav_msgs/msg/Odometry
```

## Direction

```txt
Output from diff_drive_controller
```

## Producer

```txt
diff_drive_controller
```

## Consumers

```txt
RViz Odometry display
validation tools
future Nav2/localization stack
```

## Frame IDs

```txt
header.frame_id: odom
child_frame_id: base_link
```

## Example Checks

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

## Validation Criteria

```txt
/diff_drive_controller/odom exists
type is nav_msgs/msg/Odometry
pose changes when Gazebo robot moves
child_frame_id is base_link
header.frame_id is odom
RViz Odometry display uses /diff_drive_controller/odom in Gazebo control stack
```

---

# 14. `/diff_drive_controller/cmd_vel_out`

## Purpose

`/diff_drive_controller/cmd_vel_out` reports the velocity command after controller-side limiting.

It is useful for debugging whether velocity limits are being applied.

## Message Type

```txt
geometry_msgs/msg/TwistStamped
```

## Direction

```txt
Output from diff_drive_controller
```

## Producer

```txt
diff_drive_controller
```

## Consumers

```txt
CLI/debug tools
future validation tools
```

## Example Check

```bash
ros2 topic echo /diff_drive_controller/cmd_vel_out --once
```

## Validation Criteria

```txt
cmd_vel_out appears when publish_limited_velocity is true
message type is geometry_msgs/msg/TwistStamped
values reflect controller velocity limits
```

---

# 15. `/scan`

## Purpose

`/scan` is the simulated 2D lidar output.

The lidar is simulated in Gazebo as a `gpu_lidar` sensor attached to `lidar_link`, then bridged into ROS through `ros_gz_bridge`.

## Message Type

```txt
sensor_msgs/msg/LaserScan
```

## Direction

```txt
Output from ros_gz_bridge into ROS
```

## Producer

```txt
Gazebo gpu_lidar sensor
ros_gz_bridge parameter_bridge
```

## Consumers

```txt
RViz LaserScan display
future Nav2 costmaps
future SLAM Toolbox
future AMCL/localization workflows
```

## Important Fields

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

## Example Checks

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

## RViz Settings

```txt
Fixed Frame: odom
LaserScan Topic: /scan
Reliability Policy: Best Effort if needed
```

## Validation Criteria

```txt
/scan exists
type is sensor_msgs/msg/LaserScan
ranges are populated
lidar_link exists in TF
LaserScan appears in RViz
scan changes relative to obstacles as the robot moves
```

---

# 16. `/clock`

## Purpose

`/clock` provides Gazebo simulation time to ROS nodes and RViz.

It is required when nodes use `use_sim_time:=true`.

## Message Type

```txt
rosgraph_msgs/msg/Clock
```

## Direction

```txt
Output from ros_gz_bridge into ROS
```

## Producer

```txt
Gazebo Sim
ros_gz_bridge parameter_bridge
```

## Consumers

```txt
RViz when use_sim_time is true
robot_state_publisher when use_sim_time is true
controller-related nodes using simulation time
other ROS nodes using simulation time
```

## Example Check

```bash
ros2 topic list | grep clock
ros2 topic echo /clock --once
```

## Validation Criteria

```txt
/clock exists during Gazebo launch
/clock publishes rosgraph_msgs/msg/Clock
RViz launched with use_sim_time tracks Gazebo motion
TF_OLD_DATA warnings are absent after a clean restart
```

## Common Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `No clock received` | clock bridge missing or Gazebo paused | `ros2 topic echo /clock --once` |
| `TF_OLD_DATA` | stale nodes or wall-time/sim-time mismatch | restart stack and use `rviz2 --ros-args -p use_sim_time:=true` |
| RViz robot stationary while Gazebo moves | RViz using wall time or wrong odom topic | set sim time and `/diff_drive_controller/odom` |

---

# 17. Interface Flow

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

## Gazebo Control Flow

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

## Sensor Bridge Flow

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

## Clock Bridge Flow

```txt
Gazebo simulation clock
   ↓
ros_gz_bridge
   ↓
ROS /clock
   ↓
RViz and ROS nodes using use_sim_time
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
   ↓
ros2 control list_controllers
   ↓
ros2 topic echo /diff_drive_controller/odom
   ↓
ros2 topic echo /scan
   ↓
ros2 topic echo /clock
```

---

# 18. Interface Contract

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

If ros2_control.launch.py is running:
  controller_manager should load joint_state_broadcaster and diff_drive_controller

If diff_drive_controller receives TwistStamped commands:
  Gazebo robot should move and /diff_drive_controller/odom should update

If the lidar sensor and bridge are active:
  /scan should publish sensor_msgs/msg/LaserScan

If RViz is visualizing Gazebo data:
  RViz should use simulation time from /clock
```

---

# 19. Full Interface Validation Commands

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

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt
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

## Check Dynamic Wheel and Lidar Transforms

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link lidar_link
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

## Launch Gazebo Control and Sensor Stack

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

## Run Launch Regression

```bash
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

# 20. Common Interface Failures

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
| Gazebo robot does not drive             | controller inactive, wrong command topic, or wrong message type   | `ros2 control list_controllers`, publish `TwistStamped` to controller |
| `diff_drive_controller` missing          | spawner missing or YAML issue                                     | `ros2 control list_controllers`                    |
| wheel names empty                        | `ros2_control.yaml` indentation wrong                             | inspect installed controller YAML                  |
| `/controller_manager` missing            | `gz_ros2_control` plugin failed                                   | inspect Gazebo launch output                       |
| Gazebo moves but RViz stays still        | RViz sim-time mismatch or wrong odom topic                        | use `/clock`, `use_sim_time:=true`, `/diff_drive_controller/odom` |
| `/scan` missing                          | lidar sensor or bridge not running                                | `gz topic -l`, `ros2 topic list`                   |
| LaserScan display empty                  | RViz topic not selected or QoS mismatch                           | set topic `/scan`, Reliability Best Effort         |
| `TF_OLD_DATA` warnings                   | stale nodes or wall-time/sim-time mismatch                        | restart stack and use simulation time              |
| `.sdf` world missing on GitHub           | `.gitignore` ignored SDF files                                    | `git check-ignore -v`, `git add -f`                |

---

# 21. Interface Ownership Summary

## `sim_node` Owns in the Kinematic Simulator Stack

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

## `joint_state_publisher` Owns in the Visualization-Only Description Stack

```txt
/joint_states
```

## `joint_state_broadcaster` Owns in the Gazebo ros2_control Stack

```txt
/joint_states
/dynamic_joint_states
```

## `diff_drive_controller` Owns in the Gazebo Control Stack

```txt
/diff_drive_controller/cmd_vel subscriber
/diff_drive_controller/odom publisher
/diff_drive_controller/cmd_vel_out publisher
/tf broadcaster for odom -> base_link when enable_odom_tf is true
wheel velocity command interfaces through ros2_control
```

## `ros_gz_bridge` Owns

```txt
/clock bridge from Gazebo to ROS
/scan bridge from Gazebo to ROS
```

## Gazebo Spawn Workflow Uses

```txt
/robot_description
ros_gz_sim create
empty_diffbot_world.sdf
```

## Gazebo Sensor Workflow Uses

```txt
lidar_link
gpu_lidar sensor
Gazebo /scan
ROS /scan
```

---

# 22. Interview Explanation

The project now exposes two related ROS 2 interfaces.

The original kinematic simulator subscribes to `/cmd_vel` using `geometry_msgs/msg/Twist`, publishes a simple `/robot_pose` using `geometry_msgs/msg/Pose2D`, publishes standard `/odom` using `nav_msgs/msg/Odometry`, broadcasts `odom -> base_link` on TF, and publishes runtime health on `/diagnostics` using `diagnostic_msgs/msg/DiagnosticArray`.

The robot description stack converts `diffbot.xacro` into `/robot_description`. `robot_state_publisher` uses that model plus `/joint_states` to publish the robot link transforms below `base_link`. In the visualization-only stack, `/joint_states` comes from `joint_state_publisher`. In the Gazebo control stack, `/joint_states` comes from `joint_state_broadcaster`.

The Gazebo control stack uses `ros2_control`. The Xacro model defines velocity command interfaces and position/velocity state interfaces for both wheel joints. `gz_ros2_control` exposes those Gazebo joints to `controller_manager`. `controller_manager` loads `joint_state_broadcaster` and `diff_drive_controller`. The diff-drive controller subscribes to `/diff_drive_controller/cmd_vel` as `geometry_msgs/msg/TwistStamped`, converts body velocity into wheel velocity commands, moves the robot in Gazebo, publishes `/diff_drive_controller/odom`, and publishes `odom -> base_link` TF when enabled.

Day 79 adds a simulated lidar. Gazebo simulates the `gpu_lidar` sensor on `lidar_link`, publishes a Gazebo `/scan` topic, and `ros_gz_bridge` converts it into ROS `/scan` as `sensor_msgs/msg/LaserScan`. The `/clock` bridge provides simulation time so RViz and ROS nodes can visualize Gazebo data without timestamp errors.

The key ownership rule is that `sim_node` owns `odom -> base_link` only in the original kinematic simulator stack, while `diff_drive_controller` owns `odom -> base_link` in the Gazebo control stack. RViz visualizes the robot model, TF, odometry, and lidar, but Gazebo and the controllers are what simulate and move the robot.
