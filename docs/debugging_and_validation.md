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
performance/timing issue
Git/repository hygiene issue
```

---

## 2. Standard Build Check

Use this after source, launch, config, or documentation changes.

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

| Symptom | Likely Cause | Fix |
|---|---|---|
| `package not found` | workspace not sourced | `source install/setup.bash` |
| `launch file not found` | launch folder not installed | check `install(DIRECTORY launch ...)` in `CMakeLists.txt` |
| config file not found | config folder not installed | check `install(DIRECTORY config ...)` in `CMakeLists.txt` |
| RViz config missing | rviz folder not installed | check `install(DIRECTORY launch config rviz ...)` in `CMakeLists.txt` |
| old behavior after edits | stale build/install folders | `rm -rf build install log`, rebuild, re-source |
| diagnostics headers missing | missing dependency | check `diagnostic_msgs` in `package.xml` and `CMakeLists.txt` |

---

---

## ROS 2 Usage Validation Flow

This is the standard user-facing validation flow after building the simulator.

## i. Launch Simulator

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

## ii. Publish Command

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected:

```txt
robot moves while command stream is active
robot stops after command stream ends and timeout expires
```

## iii. Inspect Runtime Outputs

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

## iv. Run Regression Script

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

## check. Usage Validation Pass Criteria

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


## 3. Launch Validation

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

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: launch_ros.action` | wrong import name | use `from launch_ros.actions import Node` |
| launch file cannot find YAML | config not installed | install `config/` in `CMakeLists.txt` |
| parameters do not change | edited source YAML but not rebuilt | rebuild and check installed YAML |
| node exits immediately | invalid parameter | check `dt`, timeout, velocity limits |
| `/diagnostics` missing after launch | node not rebuilt or publisher missing | rebuild and check `sim_node.cpp` |

---

## 4. Topic Validation

---

## Topic Interface Reference Check

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
```

Quick interface check:

```bash
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
ros2 topic type /diagnostics
```

List active topics:

```bash
ros2 topic list
```

Expected topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
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

## 5. Command and Motion Validation

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

## 6. Parameter Validation

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

## 7. Velocity Clamp Validation

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

## 8. Odometry Validation

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

## 9. TF Validation

Check transform:

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

Common TF failures:

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Invalid frame ID` | TF not broadcasting | check `publishTransform()` |
| `odom` missing | wrong parent frame | verify transform header |
| `base_link` missing | wrong child frame | verify child frame ID |
| TF exists but odom differs | pose/odom/TF inconsistency | compare pose, odom, and transform values |

---

## 10. QoS Validation

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

---

## 11. rosbag2 Validation Workflow

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

Optional Day 67+ diagnostics recording:

```bash
ros2 bag record -o bags/day67_diagnostics /cmd_vel /robot_pose /odom /tf /diagnostics
```

Important Git rule:

```txt
Do not commit actual rosbag2 data.
Commit only bags/README.md.
```

---

## 12. RViz2 Validation Workflow

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

| Failure | Likely Cause | First Check |
|---|---|---|
| Fixed frame error | wrong fixed frame | set Fixed Frame to `odom` |
| No TF frames | simulator not running or TF not publishing | `ros2 run tf2_ros tf2_echo odom base_link` |
| No odometry display | wrong topic selected | set Odometry topic to `/odom` |
| `/odom` not in dropdown | simulator not running or workspace not sourced | `ros2 topic list` |
| saved config missing after rebuild | `rviz/` folder not installed | check `install(DIRECTORY launch config rviz ...)` in `CMakeLists.txt` |
| RViz opens but robot does not move | no active `/cmd_vel` command | publish `/cmd_vel` at a continuous rate |

---

## 13. Diagnostics Validation Workflow

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

| Failure | Likely Cause | First Check |
|---|---|---|
| `/diagnostics` missing | publisher not created or node not running | `ros2 topic list` |
| build cannot find diagnostic messages | missing dependency | check `package.xml` and `CMakeLists.txt` |
| diagnostics topic exists but no values | `publishDiagnostics()` not called | check `timerCallback()` |
| always WARN | no fresh `/cmd_vel` command | publish continuous `/cmd_vel` |
| always OK | timeout logic not connected to diagnostics | check `timeout_active` |
| timing budget wrong | wrong variable used | use `dt_ * 1000.0` |
| missing key-value fields | fields not pushed into `status.values` | check `makeKeyValue(...)` calls |

---

## 14. Launch Regression Workflow

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

| Failure | Likely Cause | First Check |
|---|---|---|
| launch exits early | node crash or invalid parameters | check launch log printed by script |
| missing `/diagnostics` | diagnostics publisher missing or package not rebuilt | `ros2 topic list` |
| parameter check fails | YAML or launch override mismatch | `ros2 param get /sim_node <param>` |
| topic echo times out | publisher not active or node not running | `ros2 topic list` |
| diagnostics QoS fails | wrong QoS used for diagnostics publisher | check `state_qos` in `sim_node.cpp` |
| override test fails | launch argument not wired correctly | check `sim.launch.py` |
| script cannot source workspace | build/install missing | rebuild and source `install/setup.bash` |
| `/usr/bin/env: bash\r` error | Windows CRLF line endings | convert script to LF line endings |
| `AMENT_TRACE_SETUP_FILES: unbound variable` | Bash strict unset-variable mode conflicts with ROS setup | use `set -eo pipefail` instead of `set -euo pipefail` |

---

## 15. Regression Test Checklist

Run this checklist after meaningful simulator changes.

| Test | Command / Method | Expected Result |
|---|---|---|
| Build | `colcon build --cmake-args -DBUILD_TESTING=OFF` | Build passes |
| Launch | `ros2 launch cpp_robotics_sim_ros sim.launch.py` | Node starts |
| Topic list | `ros2 topic list` | `/cmd_vel`, `/robot_pose`, `/odom`, `/tf`, `/diagnostics` exist |
| Pose output | `ros2 topic echo --once /robot_pose` | Pose message appears |
| Odom output | `ros2 topic echo --once /odom` | Odometry message appears |
| TF output | `tf2_echo odom base_link` | Transform appears |
| Diagnostics output | `ros2 topic echo --once /diagnostics` | DiagnosticArray message appears |
| Command motion | publish `/cmd_vel` | Pose changes |
| Timeout | stop `/cmd_vel` | Robot stops after timeout |
| Diagnostics OK state | publish continuous `/cmd_vel` | diagnostics level is OK |
| Diagnostics WARN state | stop `/cmd_vel` and wait | diagnostics level is WARN |
| Clamp positive | send large positive command | Velocity clamps to max |
| Clamp negative | send large negative command | Velocity clamps to negative max |
| Params | `ros2 param get` | Expected values appear |
| Launch args | override launch arguments | Overridden values appear |
| QoS | `ros2 topic info --verbose` | Reliable/volatile appears |
| rosbag2 record | `ros2 bag record` | Bag is created |
| rosbag2 info | `ros2 bag info` | Expected topics recorded |
| rosbag2 replay | `ros2 bag play` | Pose/odom/TF replay |
| RViz2 | open saved RViz config | Grid, TF, and Odometry display correctly |
| Launch regression | `./scripts/day68_launch_regression.sh` | Regression script passes |

---

## 16. Common Failure Modes

| Failure | Likely Cause | First Check |
|---|---|---|
| No `/robot_pose` | node not running or publisher failed | `ros2 node list`, `ros2 topic list` |
| No `/cmd_vel` subscriber | node not launched | `ros2 topic info /cmd_vel` |
| No `/diagnostics` | diagnostics publisher missing or not rebuilt | `ros2 topic list` |
| Robot does not move | no command or command timeout | publish `/cmd_vel` continuously |
| Robot moves forever | timeout logic broken | stop commands and wait |
| Parameters not changing | YAML/install mismatch | check installed YAML |
| Launch override ignored | parameter dictionary order wrong | dictionary must come after `params_file` |
| TF missing | transform broadcaster issue | `tf2_echo odom base_link` |
| Odom exists but TF missing | odom publisher works, TF broadcaster failed | inspect `publishTransform()` |
| Bag missing topics | topics not active during recording | start simulator before recording |
| Bag replay empty | wrong bag path or no messages recorded | `ros2 bag info` |
| RViz config missing after build | rviz directory not installed | check CMake install block |
| Diagnostics always WARN | no fresh command input | publish `/cmd_vel` at 10 Hz |
| Diagnostics always OK | timeout logic not connected | inspect timeout condition |
| Launch regression script fails with `bash\r` | CRLF line endings | convert shell script to LF |
| Launch regression script fails with unset variable | `set -u` conflicts with ROS setup | use `set -eo pipefail` |
| Build uses wrong cache | stale build folder | `rm -rf build install log` |
| Generated files in Git | `.gitignore` missing rule | check `git status` |

---

## 17. Standalone C++ Validation

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

## 18. Git Validation

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

## 19. Commit Gate

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

For Day 68, expected staged files:

```txt
README.md
docs/daily_documentation.md
docs/debugging_and_validation.md
scripts/day68_launch_regression.sh
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
