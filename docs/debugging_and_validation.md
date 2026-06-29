# Debugging and Validation — C++ / ROS 2 Robotics Simulation Foundation

This document defines the debugging workflow, validation checks, regression tests, and failure-diagnosis commands for the C++ / ROS 2 robotics simulation project.

The goal is to avoid random debugging. Every failure should be classified, isolated, tested, and documented.

---

## 1. Debugging Principle

Main rule:

```txt
Do not randomly edit code.
First classify the failure, then test systematically.
```

Every issue should be placed into one of these categories:

```txt
build failure
launch failure
parameter/config failure
topic communication failure
motion/kinematics failure
odometry failure
TF failure
QoS mismatch
rosbag2 recording/replay failure
RViz2 visualization failure
diagnostics failure
launch regression failure
URDF failure
Xacro failure
robot_state_publisher failure
joint_state_publisher failure
RobotModel visualization failure
Gazebo launch failure
Gazebo spawn failure
ros2_control failure
controller_manager failure
joint_state_broadcaster failure
diff_drive_controller failure
Gazebo motion failure
Gazebo sensor failure
ros_gz_bridge failure
LaserScan /scan failure
simulation time /clock failure
performance/timing issue
Git/repository hygiene issue
```

---

## 2. Standard Build Check

Use this after source, launch, config, robot description, world, or documentation changes.

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Pass criteria:

```txt
colcon build completes successfully
no missing package errors
no missing header errors
no CMake install errors
install/setup.bash exists
```

Common failures:

| Symptom                         | Likely Cause                     | Fix                                                           |
| ------------------------------- | -------------------------------- | ------------------------------------------------------------- |
| `package not found`             | workspace not sourced            | `source install/setup.bash`                                   |
| `launch file not found`         | launch folder not installed      | check `install(DIRECTORY launch ...)` in `CMakeLists.txt`     |
| config file not found           | config folder not installed      | check `install(DIRECTORY config ...)` in `CMakeLists.txt`     |
| RViz config missing             | rviz folder not installed        | check `install(DIRECTORY rviz ...)` in `CMakeLists.txt`       |
| URDF file missing               | urdf folder not installed        | check `install(DIRECTORY urdf ...)` in `CMakeLists.txt`       |
| Xacro file missing              | xacro folder not installed       | check `install(DIRECTORY xacro ...)` in `CMakeLists.txt`      |
| world file missing              | worlds folder not installed      | check `install(DIRECTORY worlds ...)` in `CMakeLists.txt`     |
| old behavior after edits        | stale build/install folders      | `rm -rf build install log`, rebuild, re-source                |
| diagnostics headers missing     | missing dependency               | check `diagnostic_msgs` in `package.xml` and `CMakeLists.txt` |
| `joint_state_publisher` missing | system package not installed     | install `ros-jazzy-joint-state-publisher`                     |
| `ros_gz_sim` missing            | Gazebo ROS package not installed | install `ros-jazzy-ros-gz-sim`                                |
| `gz_ros2_control` missing       | Gazebo ros2_control package missing | install `ros-jazzy-gz-ros2-control`                         |
| controller packages missing     | ros2_control stack missing        | install `ros-jazzy-ros2-control ros-jazzy-ros2-controllers`    |
| `/scan` bridge missing          | ros_gz_bridge missing or not launched | install/check `ros-jazzy-ros-gz-bridge`                    |

---

## 3. ROS 2 Usage Validation Flow

This is the standard user-facing validation flow after building the simulator.

### i. Launch Simulator

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Expected:

```txt
/sim_node starts
/cmd_vel exists
/robot_pose publishes
/odom publishes
/tf publishes
/diagnostics publishes
```

### ii. Publish Command

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected:

```txt
robot moves while command stream is active
robot stops after command stream ends and timeout expires
```

### iii. Inspect Runtime Outputs

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

Expected:

```txt
/robot_pose contains x, y, theta
/odom contains odom frame and base_link child frame
/tf contains odom -> base_link
/diagnostics contains sim_node status and key-value fields
```

### iv. Run Regression Script

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

### Usage Validation Pass Criteria

```txt
simulator launches
topics exist
commands are accepted
pose publishes
odom publishes
TF publishes
diagnostics publishes
RViz2 config loads
launch regression passes
```

---

## 4. Launch Validation

Launch simulator:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Pass criteria:

```txt
/sim_node starts
no parameter validation error
no launch import error
/robot_pose publishes
/odom publishes
/tf publishes
/diagnostics publishes
```

Common launch failures:

| Symptom                                  | Likely Cause                          | Fix                                       |
| ---------------------------------------- | ------------------------------------- | ----------------------------------------- |
| `ModuleNotFoundError: launch_ros.action` | wrong import name                     | use `from launch_ros.actions import Node` |
| launch file cannot find YAML             | config not installed                  | install `config/` in `CMakeLists.txt`     |
| parameters do not change                 | edited source YAML but not rebuilt    | rebuild and check installed YAML          |
| node exits immediately                   | invalid parameter                     | check `dt`, timeout, velocity limits      |
| `/diagnostics` missing after launch      | node not rebuilt or publisher missing | rebuild and check `sim_node.cpp`          |
| `robot_state_publisher` package missing  | dependency not installed              | install `ros-jazzy-robot-state-publisher` |
| `joint_state_publisher` package missing  | dependency not installed              | install `ros-jazzy-joint-state-publisher` |
| `ros_gz_sim` package missing             | Gazebo ROS package not installed      | install `ros-jazzy-ros-gz-sim`            |

---

## 5. Topic Interface Reference Check

The full topic interface contract is documented in:

```txt
docs/topic_interface_reference.md
```

Use it when validating:

```txt
topic names
message types
important fields
QoS behavior
frame IDs
diagnostics behavior
common interface failures
robot description interfaces
joint state interfaces
TF ownership
ros2_control interfaces
controller_manager state
Gazebo control topics
LaserScan sensor interfaces
simulation time and /clock
```

Quick interface check:

```bash
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
ros2 topic type /diagnostics
```

List active simulator topics:

```bash
ros2 topic list
```

Expected simulator topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

Expected robot-description topics when `description.launch.py` is running:

```txt
/robot_description
/joint_states
/tf
/tf_static
```

Expected Gazebo control and sensor topics when `ros2_control.launch.py` is running:

```txt
/clock
/robot_description
/joint_states
/tf
/tf_static
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/diff_drive_controller/cmd_vel_out
/scan
```

Check pose:

```bash
ros2 topic echo --once /robot_pose
```

Check odometry:

```bash
ros2 topic echo --once /odom
```

Check diagnostics:

```bash
ros2 topic echo --once /diagnostics
```

Check command subscriber:

```bash
ros2 topic info /cmd_vel
```

Expected:

```txt
Type: geometry_msgs/msg/Twist
Subscription count: 1
```

Pass criteria:

```txt
/cmd_vel has one subscriber
/robot_pose publishes geometry_msgs/msg/Pose2D
/odom publishes nav_msgs/msg/Odometry
/tf publishes tf2_msgs/msg/TFMessage
/diagnostics publishes diagnostic_msgs/msg/DiagnosticArray
```

---

## 6. Command and Motion Validation

Send one command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Then check pose:

```bash
ros2 topic echo --once /robot_pose
```

Pass criteria:

```txt
pose changes after command
x changes for forward motion
theta changes for angular motion
robot stops after cmd_timeout if no new command arrives
```

Continuous command test:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Pass criteria:

```txt
robot continues moving while commands arrive
robot stops after commands stop and timeout expires
diagnostics show OK while fresh commands are arriving
diagnostics show WARN after command timeout becomes active
```

---

## 7. Parameter Validation

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

Expected default values:

```txt
dt = 0.1
initial_x = 0.0
initial_y = 0.0
initial_theta = 0.0
cmd_timeout = 0.5
max_linear_velocity = 0.5
max_angular_velocity = 0.8
```

Check installed YAML:

```bash
cat "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/config/sim_params.yaml"
```

Launch override test:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

Then verify:

```bash
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node dt
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Pass criteria:

```txt
terminal launch overrides appear in ros2 param get
robot starts near overridden initial pose
velocity limits match overridden clamp values
```

---

## 8. Velocity Clamp Validation

Send unsafe command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 5.0}, angular: {z: 3.0}}"
```

Expected clamp behavior:

```txt
linear.x is clamped to max_linear_velocity
angular.z is clamped to max_angular_velocity
```

With default parameters:

```txt
linear.x = 5.0  ->  0.5
angular.z = 3.0 ->  0.8
```

Negative clamp test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: -5.0}, angular: {z: -3.0}}"
```

Expected:

```txt
linear.x = -5.0  ->  -0.5
angular.z = -3.0 ->  -0.8
```

---

## 9. Odometry Validation

Check odometry type:

```bash
ros2 topic type /odom
```

Expected:

```txt
nav_msgs/msg/Odometry
```

Check position:

```bash
ros2 topic echo --once /odom --field pose.pose.position
```

Check twist:

```bash
ros2 topic echo --once /odom --field twist.twist
```

Pass criteria:

```txt
odom header frame_id is odom
odom child_frame_id is base_link
position x/y matches planar robot pose
twist linear.x matches current command after clamping
twist angular.z matches current command after clamping
```

---

## 10. TF Validation

Check simulator transform:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

Pass criteria:

```txt
transform exists
parent frame is odom
child frame is base_link
translation matches robot pose x/y
yaw quaternion changes with theta
```

Expected frame tree after Days 71-80:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

Transform ownership rule:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link

Gazebo ros2_control stack owns:
  diff_drive_controller owns odom -> base_link
  joint_state_broadcaster owns /joint_states
```

Important rule:

```txt
Do not run sim_node and diff_drive_controller as simultaneous publishers of odom -> base_link.
```

Common TF failures:

| Symptom                     | Likely Cause                                  | Fix                                               |
| --------------------------- | --------------------------------------------- | ------------------------------------------------- |
| `Invalid frame ID`          | TF not broadcasting                           | check `publishTransform()`                        |
| `odom` missing              | wrong parent frame                            | verify transform header                           |
| `base_link` missing         | wrong child frame                             | verify child frame ID                             |
| TF exists but odom differs  | pose/odom/TF inconsistency                    | compare pose, odom, and transform values          |
| wheel frames missing        | `/joint_states` missing                       | launch `joint_state_publisher`                    |
| caster frame missing        | fixed joint missing or `/tf_static` QoS issue | echo `/tf_static` with transient local durability |
| duplicate transform warning | two nodes publishing same transform           | keep `odom -> base_link` only in `sim_node`       |

---

## 11. QoS Validation

Inspect QoS:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /tf --verbose
ros2 topic info /diagnostics --verbose
```

Expected for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics`:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

The code explicitly configures:

```cpp
rclcpp::QoS(rclcpp::KeepLast(10))
```

The ROS 2 CLI may show history/depth as `UNKNOWN` depending on middleware introspection. The code-level QoS definition is the source of truth for `KeepLast(10)`.

Pass criteria:

```txt
/cmd_vel subscription exists
/robot_pose publisher exists
/odom publisher exists
/diagnostics publisher exists
reliability shows RELIABLE
durability shows VOLATILE
robot still moves from /cmd_vel
```

For `/tf_static`, use transient local durability when echoing:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

---

## 12. rosbag2 Validation Workflow

rosbag2 is used to record and replay simulator behavior for debugging and validation.

Create local bag folder:

```bash
mkdir -p bags
```

Record:

```bash
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
```

During recording, send commands:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
sleep 1
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.4}, angular: {z: -0.2}}"
sleep 1
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Stop recording:

```txt
Ctrl+C
```

Inspect:

```bash
ros2 bag info bags/day65_baseline
```

Expected recorded topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

Replay:

```bash
ros2 bag play bags/day65_baseline
```

While replay is running, verify:

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
```

Pass criteria:

```txt
/cmd_vel is recorded
/robot_pose is recorded
/odom is recorded
/tf is recorded
bag replay republishes robot state topics
TF can be inspected during replay
```

Optional diagnostics recording:

```bash
ros2 bag record -o bags/day67_diagnostics /cmd_vel /robot_pose /odom /tf /diagnostics
```

Important Git rule:

```txt
Do not commit actual rosbag2 data.
Commit only bags/README.md.
```

---

## 13. RViz2 Validation Workflow

RViz2 is used to visually validate odometry and TF behavior.

### Launch Simulator

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros sim.launch.py
```

### Open RViz from Source Config

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

rviz2 -d src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

### Open RViz from Installed Config

```bash
rviz2 -d "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/rviz/sim_debug.rviz"
```

### Expected RViz Settings

```txt
Fixed Frame: odom
Displays: Grid, TF, Odometry
Odometry Topic: /odom
```

### Motion Test

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

### Pass Criteria

```txt
RViz opens without errors
Fixed Frame is odom
TF display shows odom and base_link
Odometry display uses /odom
base_link moves when /cmd_vel is published
Odometry visualization updates during motion
robot stops after command timeout
saved RViz config reloads from source path
saved RViz config reloads from installed package path
```

### Common RViz Failures

| Failure                            | Likely Cause                                   | First Check                                                           |
| ---------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------- |
| Fixed frame error                  | wrong fixed frame                              | set Fixed Frame to `odom`                                             |
| No TF frames                       | simulator not running or TF not publishing     | `ros2 run tf2_ros tf2_echo odom base_link`                            |
| No odometry display                | wrong topic selected                           | set Odometry topic to `/odom`                                         |
| `/odom` not in dropdown            | simulator not running or workspace not sourced | `ros2 topic list`                                                     |
| saved config missing after rebuild | `rviz/` folder not installed                   | check `install(DIRECTORY launch config rviz ...)` in `CMakeLists.txt` |
| RViz opens but robot does not move | no active `/cmd_vel` command                   | publish `/cmd_vel` at a continuous rate                               |

---

## 14. Diagnostics Validation Workflow

The simulator publishes runtime health information on `/diagnostics`.

### Topic Check

```bash
ros2 topic list | grep diagnostics
```

Expected:

```txt
/diagnostics
```

### Echo Diagnostics

```bash
ros2 topic echo --once /diagnostics
```

Expected message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected diagnostic status fields:

```txt
name: sim_node
hardware_id: cpp_robotics_sim_ros
level: 0 or 1
message: Simulator running or cmd_vel timeout active
```

Expected key-value fields:

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

### OK-State Test

Publish continuous command input:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Then check diagnostics:

```bash
ros2 topic echo --once /diagnostics
```

Pass criteria:

```txt
level: 0
message: Simulator running
timeout_active: false
```

### WARN-State Test

Stop the command publisher and wait longer than `cmd_timeout`.

Then check diagnostics:

```bash
ros2 topic echo --once /diagnostics
```

Pass criteria:

```txt
level: 1
message: cmd_vel timeout active
timeout_active: true
```

### QoS Check

```bash
ros2 topic info /diagnostics --verbose
```

Expected:

```txt
Type: diagnostic_msgs/msg/DiagnosticArray
Reliability: RELIABLE
Durability: VOLATILE
```

### Common Diagnostics Failures

| Failure                                | Likely Cause                               | First Check                              |
| -------------------------------------- | ------------------------------------------ | ---------------------------------------- |
| `/diagnostics` missing                 | publisher not created or node not running  | `ros2 topic list`                        |
| build cannot find diagnostic messages  | missing dependency                         | check `package.xml` and `CMakeLists.txt` |
| diagnostics topic exists but no values | `publishDiagnostics()` not called          | check `timerCallback()`                  |
| always WARN                            | no fresh `/cmd_vel` command                | publish continuous `/cmd_vel`            |
| always OK                              | timeout logic not connected to diagnostics | check `timeout_active`                   |
| timing budget wrong                    | wrong variable used                        | use `dt_ * 1000.0`                       |
| missing key-value fields               | fields not pushed into `status.values`     | check `makeKeyValue(...)` calls          |

---

## 15. Launch Regression Workflow

The launch regression script validates the core ROS 2 runtime behavior in one command.

### Script

```txt
scripts/day68_launch_regression.sh
```

### Run

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

### What It Validates

```txt
default launch starts successfully
/cmd_vel exists
/robot_pose exists
/odom exists
/tf exists
/diagnostics exists
default parameters load correctly
/robot_pose publishes
/odom publishes
/tf publishes
/diagnostics publishes
/cmd_vel command is accepted
/diagnostics type is DiagnosticArray
/diagnostics QoS is reliable and volatile
launch argument overrides work
overridden launch still publishes pose
```

### Pass Criteria

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

### Common Launch Regression Failures

| Failure                                     | Likely Cause                                             | First Check                                           |
| ------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| launch exits early                          | node crash or invalid parameters                         | check launch log printed by script                    |
| missing `/diagnostics`                      | diagnostics publisher missing or package not rebuilt     | `ros2 topic list`                                     |
| parameter check fails                       | YAML or launch override mismatch                         | `ros2 param get /sim_node <param>`                    |
| topic echo times out                        | publisher not active or node not running                 | `ros2 topic list`                                     |
| diagnostics QoS fails                       | wrong QoS used for diagnostics publisher                 | check `state_qos` in `sim_node.cpp`                   |
| override test fails                         | launch argument not wired correctly                      | check `sim.launch.py`                                 |
| script cannot source workspace              | build/install missing                                    | rebuild and source `install/setup.bash`               |
| `/usr/bin/env: bash\r` error                | Windows CRLF line endings                                | convert script to LF line endings                     |
| `AMENT_TRACE_SETUP_FILES: unbound variable` | Bash strict unset-variable mode conflicts with ROS setup | use `set -eo pipefail` instead of `set -euo pipefail` |

---

## 16. Regression Test Checklist

Run this checklist after meaningful simulator changes.

| Test                   | Command / Method                                 | Expected Result                                                 |
| ---------------------- | ------------------------------------------------ | --------------------------------------------------------------- |
| Build                  | `colcon build --cmake-args -DBUILD_TESTING=OFF`  | Build passes                                                    |
| Launch                 | `ros2 launch cpp_robotics_sim_ros sim.launch.py` | Node starts                                                     |
| Topic list             | `ros2 topic list`                                | `/cmd_vel`, `/robot_pose`, `/odom`, `/tf`, `/diagnostics` exist |
| Pose output            | `ros2 topic echo --once /robot_pose`             | Pose message appears                                            |
| Odom output            | `ros2 topic echo --once /odom`                   | Odometry message appears                                        |
| TF output              | `tf2_echo odom base_link`                        | Transform appears                                               |
| Diagnostics output     | `ros2 topic echo --once /diagnostics`            | DiagnosticArray message appears                                 |
| Command motion         | publish `/cmd_vel`                               | Pose changes                                                    |
| Timeout                | stop `/cmd_vel`                                  | Robot stops after timeout                                       |
| Diagnostics OK state   | publish continuous `/cmd_vel`                    | diagnostics level is OK                                         |
| Diagnostics WARN state | stop `/cmd_vel` and wait                         | diagnostics level is WARN                                       |
| Clamp positive         | send large positive command                      | Velocity clamps to max                                          |
| Clamp negative         | send large negative command                      | Velocity clamps to negative max                                 |
| Params                 | `ros2 param get`                                 | Expected values appear                                          |
| Launch args            | override launch arguments                        | Overridden values appear                                        |
| QoS                    | `ros2 topic info --verbose`                      | Reliable/volatile appears                                       |
| rosbag2 record         | `ros2 bag record`                                | Bag is created                                                  |
| rosbag2 info           | `ros2 bag info`                                  | Expected topics recorded                                        |
| rosbag2 replay         | `ros2 bag play`                                  | Pose/odom/TF replay                                             |
| RViz2                  | open saved RViz config                           | Grid, TF, and Odometry display correctly                        |
| URDF parse             | Python XML parse                                 | URDF XML parses                                                 |
| Xacro generation       | `xacro diffbot.xacro`                            | generated URDF parses                                           |
| robot_state_publisher  | `description.launch.py`                          | `/robot_description`, `/tf`, `/tf_static` exist                 |
| joint_state_publisher  | `description.launch.py`                          | `/joint_states` exists                                          |
| RViz RobotModel        | `robot_model_viz.launch.py`                      | RobotModel appears                                              |
| Gazebo spawn           | `gazebo_spawn.launch.py`                         | diffbot appears in Gazebo                                       |
| ros2_control           | `ros2_control.launch.py`                         | controller_manager and hardware interfaces appear               |
| joint broadcaster      | `ros2 control list_controllers`                  | joint_state_broadcaster active                                  |
| diff-drive controller  | `ros2 control list_controllers`                  | diff_drive_controller active                                    |
| Gazebo drive command   | publish `TwistStamped` to controller             | robot moves in Gazebo                                           |
| Controller odom        | echo `/diff_drive_controller/odom`               | odom publishes with `odom` and `base_link` frames               |
| Lidar scan             | echo `/scan`                                     | LaserScan ranges publish                                        |
| Lidar TF               | `tf2_echo base_link lidar_link`                  | fixed lidar transform appears                                   |
| RViz sim time          | `rviz2 --ros-args -p use_sim_time:=true`         | RViz tracks Gazebo motion without TF_OLD_DATA                   |
| Launch regression      | `./scripts/day68_launch_regression.sh`           | Regression script passes                                        |

---

## 17. Common Failure Modes

| Failure                                            | Likely Cause                                          | First Check                               |
| -------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------- |
| No `/robot_pose`                                   | node not running or publisher failed                  | `ros2 node list`, `ros2 topic list`       |
| No `/cmd_vel` subscriber                           | node not launched                                     | `ros2 topic info /cmd_vel`                |
| No `/diagnostics`                                  | diagnostics publisher missing or not rebuilt          | `ros2 topic list`                         |
| Robot does not move                                | no command or command timeout                         | publish `/cmd_vel` continuously           |
| Robot moves forever                                | timeout logic broken                                  | stop commands and wait                    |
| Parameters not changing                            | YAML/install mismatch                                 | check installed YAML                      |
| Launch override ignored                            | parameter dictionary order wrong                      | dictionary must come after `params_file`  |
| TF missing                                         | transform broadcaster issue                           | `tf2_echo odom base_link`                 |
| Odom exists but TF missing                         | odom publisher works, TF broadcaster failed           | inspect `publishTransform()`              |
| Bag missing topics                                 | topics not active during recording                    | start simulator before recording          |
| Bag replay empty                                   | wrong bag path or no messages recorded                | `ros2 bag info`                           |
| RViz config missing after build                    | rviz directory not installed                          | check CMake install block                 |
| Diagnostics always WARN                            | no fresh command input                                | publish `/cmd_vel` at 10 Hz               |
| Diagnostics always OK                              | timeout logic not connected                           | inspect timeout condition                 |
| Launch regression script fails with `bash\r`       | CRLF line endings                                     | convert shell script to LF                |
| Launch regression script fails with unset variable | `set -u` conflicts with ROS setup                     | use `set -eo pipefail`                    |
| Build uses wrong cache                             | stale build folder                                    | `rm -rf build install log`                |
| Generated files in Git                             | `.gitignore` missing rule                             | check `git status`                        |
| Xacro command fails with spaces in path            | launch command not quoted                             | quote model path in `Command(...)`        |
| XML parsed as YAML                                 | robot description not forced to string                | use `ParameterValue(..., value_type=str)` |
| no `/joint_states`                                 | `joint_state_publisher` not installed or not launched | `ros2 node list`                          |
| no wheel transforms                                | missing joint states                                  | `ros2 topic echo /joint_states --once`    |
| Gazebo opens but no robot                          | spawn failed or `/robot_description` missing          | inspect launch terminal                   |
| Gazebo world missing                               | `worlds/` not installed                               | check CMake install block                 |
| controller_manager missing                         | gz_ros2_control plugin not loaded                     | inspect Gazebo log                        |
| diff_drive_controller missing                      | spawner missing or YAML issue                         | `ros2 control list_controllers`           |
| wheel names empty                                  | YAML indentation wrong                                | installed `ros2_control.yaml`             |
| Gazebo moves but RViz does not                     | sim time or odom topic mismatch                       | `/clock`, RViz use_sim_time, odom topic   |
| `/scan` missing                                    | sensor or bridge not running                          | `gz topic -l`, `ros2 topic list`          |
| TF_OLD_DATA warnings                               | stale nodes or clock mismatch                         | restart stack and use sim time            |
| `.sdf` not tracked                                 | `.gitignore` excludes SDF files                       | `git check-ignore -v`                     |

---

## 18. Robot Description and Gazebo Validation — Days 71–80

This section validates the URDF, Xacro, `robot_state_publisher`, `joint_state_publisher`, RViz RobotModel, and Gazebo spawn workflow.

---

## 18.1 URDF Validation

Static URDF path:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

XML parse check:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"

python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf")
print("PASS: URDF XML parsed successfully")
PY
```

Link check:

```bash
grep -n '<link name' ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

Expected links:

```txt
base_link
left_wheel_link
right_wheel_link
caster_link
```

Joint check:

```bash
grep -n '<joint name' ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

Expected joints:

```txt
left_wheel_joint
right_wheel_joint
caster_joint
```

Installed URDF check:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ls "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/urdf/diffbot.urdf"
```

Common URDF failures:

| Failure                | Likely Cause                   | First Check                             |
| ---------------------- | ------------------------------ | --------------------------------------- |
| XML parse error        | unclosed tag or typo           | Python XML parse command                |
| missing link           | link name typo                 | `grep -n '<link name'`                  |
| missing joint          | joint name typo                | `grep -n '<joint name'`                 |
| installed URDF missing | `urdf/` not installed in CMake | check `install(DIRECTORY ... urdf ...)` |

---

## 18.2 Xacro Validation

Xacro path:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

Generate URDF from Xacro:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"

source /opt/ros/jazzy/setup.bash

xacro "ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro" > /tmp/diffbot_from_xacro.urdf
```

Parse generated URDF:

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("/tmp/diffbot_from_xacro.urdf")
print("PASS: Xacro generated valid URDF XML")
PY
```

Installed Xacro check:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

xacro "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/xacro/diffbot.xacro" > /tmp/installed_diffbot_from_xacro.urdf
```

Common Xacro failures:

| Failure                    | Likely Cause           | First Check                          |
| -------------------------- | ---------------------- | ------------------------------------ |
| `xacro: command not found` | missing package        | install `ros-jazzy-xacro`            |
| bad macro expansion        | property or macro typo | run `xacro <file>` manually          |
| generated XML invalid      | invalid Xacro output   | parse `/tmp/diffbot_from_xacro.urdf` |
| installed Xacro missing    | `xacro/` not installed | check CMake install block            |

---

## 18.3 robot_state_publisher Validation

Launch:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Node check:

```bash
ros2 node list
ros2 node info /robot_state_publisher
```

Expected node:

```txt
/robot_state_publisher
```

Expected published topics:

```txt
/robot_description
/tf
/tf_static
```

Robot description check:

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/robot_description.txt
```

Static transform check:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected fixed transform:

```txt
frame_id: base_link
child_frame_id: caster_link
```

Common `robot_state_publisher` failures:

| Failure                       | Likely Cause                                  | First Check                              |
| ----------------------------- | --------------------------------------------- | ---------------------------------------- |
| XML parsed as YAML            | missing `ParameterValue(..., value_type=str)` | inspect launch file                      |
| Xacro path with spaces fails  | command argument not quoted                   | check `Command(['xacro "', model, '"'])` |
| no `/robot_description`       | node failed to start                          | `ros2 node list`                         |
| no `/tf_static`               | fixed joint missing or echo QoS wrong         | use transient local durability           |
| duplicate `odom -> base_link` | wrong transform ownership                     | sim_node owns `odom -> base_link` only   |

---

## 18.4 joint_state_publisher Validation

Launch:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Expected nodes:

```txt
/robot_state_publisher
/joint_state_publisher
```

Topic check:

```bash
ros2 topic list | grep -E "joint_states|robot_description|tf"
```

Expected topics:

```txt
/joint_states
/robot_description
/tf
/tf_static
```

Joint state check:

```bash
ros2 topic echo /joint_states --once
```

Expected joint names:

```txt
left_wheel_joint
right_wheel_joint
```

Wheel transform checks:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link caster_link
```

Expected translations:

```txt
base_link -> left_wheel_link:  [0.000, 0.180, 0.080]
base_link -> right_wheel_link: [0.000, -0.180, 0.080]
base_link -> caster_link:      [-0.170, 0.000, 0.035]
```

Common `joint_state_publisher` failures:

| Failure             | Likely Cause              | First Check                               |
| ------------------- | ------------------------- | ----------------------------------------- |
| package not found   | missing install           | install `ros-jazzy-joint-state-publisher` |
| no `/joint_states`  | node not launched         | `ros2 node list`                          |
| no wheel TF         | joint states missing      | `ros2 topic echo /joint_states --once`    |
| wheel links missing | Xacro joint/link mismatch | inspect `/tmp/robot_description.txt`      |

---

## 18.5 RViz RobotModel Validation

Launch:

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

Expected nodes:

```txt
/sim_node
/robot_state_publisher
/joint_state_publisher
/rviz2
```

Expected topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/tf_static
/joint_states
/robot_description
/diagnostics
```

TF checks:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link caster_link
```

RViz expected displays:

```txt
Grid
TF
RobotModel
Odometry
```

RViz fixed frame:

```txt
odom
```

RobotModel source:

```txt
/robot_description
```

Common RViz RobotModel failures:

| Failure                       | Likely Cause                           | First Check                            |
| ----------------------------- | -------------------------------------- | -------------------------------------- |
| RobotModel red                | missing TF or robot_description        | `ros2 topic list`                      |
| fixed frame error             | `odom` not available                   | `tf2_echo odom base_link`              |
| robot links missing           | joint states missing                   | `ros2 topic echo /joint_states --once` |
| installed RViz config missing | `rviz/` not installed                  | check CMake install block              |
| robot not moving              | no `/cmd_vel` or sim_node not launched | `ros2 node list`                       |

---

## 18.6 Gazebo Spawn Validation

Launch:

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected:

```txt
Gazebo Sim opens
ground plane appears
diffbot appears in the world
spawn_diffbot exits cleanly
```

ROS-side checks:

```bash
ros2 node list
ros2 topic list | grep -E "robot_description|joint_states|tf|clock"
```

Expected topics:

```txt
/robot_description
/joint_states
/tf
/tf_static
```

Gazebo-side checks:

```bash
gz topic -l | grep world
```

Expected:

```txt
/world/empty_diffbot_world/...
```

Installed world check:

```bash
ls "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf"
```

Installed launch check:

```bash
ls "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/launch/gazebo_spawn.launch.py"
```

Common Gazebo failures:

| Failure                    | Likely Cause                              | First Check                        |
| -------------------------- | ----------------------------------------- | ---------------------------------- |
| `ros_gz_sim` not found     | missing ROS-Gazebo package                | install `ros-jazzy-ros-gz-sim`     |
| Gazebo opens but no robot  | spawn failed or robot_description missing | launch terminal output             |
| world file missing         | `worlds/` not installed                   | check CMake install block          |
| robot falls through ground | collision/inertial/world issue            | inspect collision geometry         |
| robot does not drive       | expected at Day 76                        | Day 77/78 adds control/plugin work |


---

## 18.7 ros2_control Validation — Day 77

Launch the Gazebo control stack:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Expected launch sequence:

```txt
Gazebo opens
robot_state_publisher starts
spawn_diffbot succeeds
gz_ros2_control loads controller_manager
DiffBotSystem hardware initializes
DiffBotSystem hardware activates
joint_state_broadcaster spawns and becomes active
```

Controller check:

```bash
ros2 control list_controllers
```

Expected:

```txt
joint_state_broadcaster active
```

Hardware interface check:

```bash
ros2 control list_hardware_interfaces
```

Expected interfaces:

```txt
left_wheel_joint/velocity command interface
right_wheel_joint/velocity command interface
left_wheel_joint/position state interface
left_wheel_joint/velocity state interface
right_wheel_joint/position state interface
right_wheel_joint/velocity state interface
```

Joint state check:

```bash
ros2 topic echo /joint_states --once
```

Expected joint names:

```txt
left_wheel_joint
right_wheel_joint
```

Common ros2_control failures:

| Failure | Likely Cause | First Check |
|---|---|---|
| `/controller_manager` missing | `gz_ros2_control` plugin did not load | inspect Gazebo launch log |
| `gz_ros2_control` package missing | package not installed | `ros2 pkg prefix gz_ros2_control` |
| hardware interfaces missing | Xacro `ros2_control` block wrong | inspect generated URDF from Xacro |
| `joint_state_broadcaster` inactive | spawner ran before controller_manager was ready | increase launch delay or manually spawn |
| FastDDS/FastCDR symbol error | ROS package version mismatch | reinstall Jazzy control/middleware packages |
| `No clock received` | sim time enabled but `/clock` not bridged | check `/clock` bridge |

Pass criteria:

```txt
/controller_manager exists
joint_state_broadcaster is active
wheel command/state interfaces are visible
/joint_states publishes wheel joint names
```

---

## 18.8 Gazebo Differential-Drive Control Validation — Day 78

Day 78 validates that the robot can move in Gazebo using `diff_drive_controller`.

Controller YAML must contain a top-level `diff_drive_controller` parameter block:

```yaml
controller_manager:
  ros__parameters:
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
    use_stamped_vel: true
```

Controller check:

```bash
ros2 control list_controllers
```

Expected:

```txt
joint_state_broadcaster active
diff_drive_controller active
```

Topic check:

```bash
ros2 topic list | grep diff_drive
```

Expected topics:

```txt
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/diff_drive_controller/cmd_vel_out
```

Drive command:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.2}, angular: {z: 0.3}}}"
```

Odometry check:

```bash
ros2 topic echo /diff_drive_controller/odom --once
```

TF check:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Pass criteria:

```txt
diff_drive_controller is active
Gazebo robot moves from TwistStamped command
/diff_drive_controller/odom publishes
odom -> base_link TF updates when enable_odom_tf is true
```

Common diff-drive failures:

| Failure | Likely Cause | First Check |
|---|---|---|
| controller does not appear | spawner not added to launch | inspect `ros2_control.launch.py` |
| wheel names empty | YAML indentation wrong | installed `ros2_control.yaml` |
| controller inactive | hardware interfaces unavailable | `ros2 control list_hardware_interfaces` |
| robot does not move | wrong command topic or wrong message type | publish `TwistStamped` to `/diff_drive_controller/cmd_vel` |
| odom publishes but RViz does not move | RViz time or TF issue | `tf2_echo odom base_link` |

---

## 18.9 Simulated Lidar and /scan Validation — Day 79

Day 79 validates the simulated lidar sensor and ROS bridge.

Expected robot model addition:

```txt
lidar_link
lidar_joint fixed from base_link to lidar_link
```

Expected sensor stack:

```txt
Gazebo gpu_lidar sensor
  -> Gazebo /scan topic
  -> ros_gz_bridge
  -> ROS /scan topic
  -> sensor_msgs/msg/LaserScan
  -> RViz LaserScan display
```

Launch:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

ROS scan checks:

```bash
ros2 topic list | grep scan
ros2 topic type /scan
ros2 topic echo /scan --once
```

Expected:

```txt
/scan
sensor_msgs/msg/LaserScan
ranges: [...]
```

Gazebo scan check if ROS `/scan` is missing:

```bash
gz topic -l | grep scan
gz topic -e -t /scan
```

Manual bridge test:

```bash
ros2 run ros_gz_bridge parameter_bridge "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
```

Lidar TF check:

```bash
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Expected translation:

```txt
Translation near [0.150, 0.000, 0.180]
```

RViz setup:

```txt
Fixed Frame: odom
RobotModel: /robot_description
Odometry topic: /diff_drive_controller/odom
LaserScan topic: /scan
LaserScan Reliability Policy: Best Effort if needed
```

Pass criteria:

```txt
/scan exists
/scan type is sensor_msgs/msg/LaserScan
/scan publishes ranges
lidar_link exists in TF
LaserScan appears in RViz
robot still drives in Gazebo
```

Common lidar failures:

| Failure | Likely Cause | First Check |
|---|---|---|
| no `/scan` in ROS | bridge not running | check `scan_bridge` in launch |
| no `/scan` in Gazebo | sensor not attached or sensors plugin missing | check world SDF and Xacro sensor block |
| scan echo hangs | Gazebo paused or sensor not publishing | press play in Gazebo |
| RViz LaserScan empty topic | topic not selected | set LaserScan topic to `/scan` |
| RViz LaserScan red | QoS mismatch or frame missing | set Best Effort and check `lidar_link` TF |
| `.sdf` world not on GitHub | `.gitignore` ignored SDF files | `git check-ignore -v <world.sdf>` and `git add -f` |

---

## 18.10 Simulation Time and RViz/Gazebo Synchronization — Day 79/80

Gazebo publishes simulation time. ROS nodes and RViz must use `/clock` when `use_sim_time` is enabled.

Clock bridge check:

```bash
ros2 topic list | grep clock
ros2 topic echo /clock --once
```

Expected:

```txt
/clock publishes rosgraph_msgs/msg/Clock
```

If RViz shows old TF warnings:

```txt
TF_OLD_DATA ignoring data from the past for frame base_link
```

Stop all old nodes:

```bash
pkill -f gz || true
pkill -f rviz2 || true
pkill -f robot_state_publisher || true
pkill -f joint_state_publisher || true
pkill -f controller_manager || true
pkill -f parameter_bridge || true
pkill -f sim_node || true
```

Relaunch the Gazebo control stack, then start RViz with sim time:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Pass criteria:

```txt
RViz RobotModel moves with Gazebo robot
LaserScan moves consistently with robot motion
TF_OLD_DATA warnings disappear after clean restart
```

Common sim-time failures:

| Failure | Likely Cause | First Check |
|---|---|---|
| RViz robot stationary but Gazebo moves | RViz using wall time or wrong odom topic | launch RViz with `use_sim_time:=true` |
| TF_OLD_DATA warnings | stale nodes or time mismatch | kill old nodes and verify `/clock` |
| no clock received | `/clock` bridge missing | check `clock_bridge` in launch |
| odometry display static | RViz using `/odom` instead of `/diff_drive_controller/odom` | update Odometry topic |

---

## 18.11 Day 80 Review Gate

Day 80 is a documentation and interview-readiness checkpoint. No new feature is required.

A Day 80 review passes when the engineer can explain:

```txt
URDF vs Xacro
robot_description
robot_state_publisher
joint_state_publisher vs joint_state_broadcaster
TF ownership
RViz vs Gazebo
ros2_control hardware interfaces
controller_manager
gz_ros2_control
diff_drive_controller
ros_gz_sim create
ros_gz_bridge
/clock and use_sim_time
/scan LaserScan flow
```

System explanation check:

```txt
The robot model is defined in Xacro.
robot_state_publisher uses robot_description and /joint_states to publish link TF.
Gazebo simulates the robot and sensor physics.
gz_ros2_control exposes Gazebo joints as ros2_control hardware interfaces.
controller_manager loads joint_state_broadcaster and diff_drive_controller.
diff_drive_controller converts body velocity commands into wheel velocity commands.
ros_gz_bridge converts Gazebo /scan and /clock into ROS topics.
RViz visualizes robot model, TF, odometry, and LaserScan.
```

Day 80 documentation commit should include updated documentation files only, unless a small doc-support config file was intentionally changed.


---

## 19. Standalone C++ Validation

Build standalone simulator on Linux / WSL:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/standalone_cpp"
rm -rf build
mkdir build
cd build
cmake ..
cmake --build .
./robotics_sim
```

Build standalone simulator on Windows PowerShell:

```powershell
cd "C:\Self study\PRACTICE C++\Cdev\01_joint_basics\standalone_cpp"
.\build.ps1
```

Pass criteria:

```txt
standalone executable builds
differential-drive demo runs
manipulator joint-state demo runs
validation scenarios run
target-tracking demo runs
```

Common standalone build issue:

```txt
Do not reuse the same CMake build folder between WSL and Windows PowerShell.
Delete build/ before switching environments.
```

---

## 20. Git Validation

Before every commit:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
git status
git diff
```

Check staged files:

```bash
git diff --cached --name-only
```

Generated folders should not be committed:

```txt
build/
install/
log/
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
standalone_cpp/build/
bags/day65_baseline/
bags/day67_diagnostics/
```

Check if generated files are tracked:

```bash
git ls-files | grep -E "(^build/|^install/|^log/|^ros2_ws/build/|^ros2_ws/install/|^ros2_ws/log/|^standalone_cpp/build/|^bags/day65_baseline/|^bags/day67_diagnostics/)"
```

Expected:

```txt
# no output
```

---

## 21. Commit Gate

A commit is allowed only if:

```txt
build passes
launch works
required topics publish
parameters are correct
TF works
diagnostics work
launch regression passes when applicable
changed workflow is documented
generated files are ignored
git diff --cached --name-only shows only intended files
```

For documentation updates through Day 80, expected staged files may include:

```txt
README.md
docs/daily_documentation.md
docs/debugging_and_validation.md
docs/system_architecture.md
docs/topic_interface_reference.md
```

For Day 71-80 robot modeling, Gazebo, control, and sensor commits, expected staged files may include:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
ros2_ws/src/cpp_robotics_sim_ros/launch/description.launch.py
ros2_ws/src/cpp_robotics_sim_ros/launch/robot_model_viz.launch.py
ros2_ws/src/cpp_robotics_sim_ros/launch/gazebo_spawn.launch.py
ros2_ws/src/cpp_robotics_sim_ros/launch/ros2_control.launch.py
ros2_ws/src/cpp_robotics_sim_ros/rviz/diffbot_robot_model.rviz
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
ros2_ws/src/cpp_robotics_sim_ros/CMakeLists.txt
ros2_ws/src/cpp_robotics_sim_ros/package.xml
```

Do not stage:

```txt
bags/day65_baseline/
bags/day67_diagnostics/
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
standalone_cpp/build/
```
