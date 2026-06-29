# Debugging and Validation — C++ / ROS 2 Robotics Simulation Foundation

This document defines the debugging workflow, validation commands, regression checks, and common failure modes for the `cpp_robotics_sim_foundation` project through **Day 85**.

The project now includes:

```txt
standalone C++ simulation modules
ROS 2 C++ kinematic simulator
URDF/Xacro robot model
robot_state_publisher and joint state workflows
RViz visualization
Gazebo Sim spawning
ros2_control + controller_manager
joint_state_broadcaster
diff_drive_controller
simulated lidar and /scan bridge
/clock simulation time bridge
Nav2 and state-estimation notes
noisy odometry node
trajectory validation recorder
trajectory validation plotting and report generation
Day 68 launch regression
```

The goal of this document is to avoid random debugging. Every failure should be classified, isolated, tested, and documented.

---

## 1. Debugging Principle

Main rule:

```txt
Do not randomly edit code.
First classify the failure, then test systematically.
```

Use this mental sequence:

```txt
1. What did I run?
2. What did I expect?
3. What actually happened?
4. Which layer failed?
5. Which command proves it?
6. What is the smallest fix?
7. Rebuild, re-source, and re-test.
```

Typical failure categories:

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
RViz visualization failure
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
noisy odometry failure
Python ROS node execution failure
trajectory CSV recording failure
plot/report generation failure
CRLF/shebang failure
matplotlib/Python dependency failure
performance/timing issue
Git/repository hygiene issue
```

---

## 2. Standard Build Check

Use this after source, launch, config, robot description, world, controller, Python script, or documentation changes.

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
ROS 2 package executables are discoverable
```

Check installed executables:

```bash
ros2 pkg executables cpp_robotics_sim_ros
```

For Days 83-85, expected Python scripts:

```txt
cpp_robotics_sim_ros noisy_odom_node.py
cpp_robotics_sim_ros trajectory_validation_recorder.py
cpp_robotics_sim_ros plot_trajectory_validation.py
```

Common build failures:

| Symptom | Likely Cause | Fix |
|---|---|---|
| `package not found` | workspace not sourced | `source install/setup.bash` |
| `launch file not found` | launch folder not installed | check `install(DIRECTORY launch ...)` in `CMakeLists.txt` |
| config file not found | config folder not installed | check `install(DIRECTORY config ...)` in `CMakeLists.txt` |
| RViz config missing | rviz folder not installed | check `install(DIRECTORY rviz ...)` in `CMakeLists.txt` |
| URDF file missing | urdf folder not installed | check `install(DIRECTORY urdf ...)` in `CMakeLists.txt` |
| Xacro file missing | xacro folder not installed | check `install(DIRECTORY xacro ...)` in `CMakeLists.txt` |
| world file missing | worlds folder not installed | check `install(DIRECTORY worlds ...)` in `CMakeLists.txt` |
| Python script not found by `ros2 run` | script not installed | check `install(PROGRAMS scripts/... DESTINATION lib/${PROJECT_NAME})` |
| old behavior after edits | stale build/install folders | `rm -rf build install log`, rebuild, re-source |
| diagnostics headers missing | missing dependency | check `diagnostic_msgs` in `package.xml` and `CMakeLists.txt` |
| `joint_state_publisher` missing | system package not installed | install `ros-jazzy-joint-state-publisher` |
| `ros_gz_sim` missing | Gazebo ROS package not installed | install `ros-jazzy-ros-gz-sim` |
| `gz_ros2_control` missing | Gazebo ros2_control package missing | install `ros-jazzy-gz-ros2-control` |
| controller packages missing | ros2_control stack missing | install `ros-jazzy-ros2-control ros-jazzy-ros2-controllers` |
| `/scan` bridge missing | ros_gz_bridge missing or not launched | install/check `ros-jazzy-ros-gz-bridge` |

---

## 3. Python ROS Script Checks

Days 83-85 add Python ROS/tooling scripts inside:

```txt
ros2_ws/src/cpp_robotics_sim_ros/scripts/
```

Current scripts:

```txt
noisy_odom_node.py
trajectory_validation_recorder.py
plot_trajectory_validation.py
```

These scripts must have:

```txt
Linux LF line endings
correct shebang as first line
executable permission
valid Python syntax
CMake install(PROGRAMS ...) entry
```

### 3.1 Shebang Check

Run from `ros2_ws`:

```bash
head -n 3 src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py | cat -A
head -n 3 src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py | cat -A
head -n 3 src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py | cat -A
```

Expected first line:

```txt
#!/usr/bin/env python3$
```

There should be no `^M`.

### 3.2 Fix CRLF Line Endings

If a script shows `^M` or fails with `python3\r`, run:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

sed -i 's/\r$//' src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
sed -i 's/\r$//' src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
sed -i 's/\r$//' src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
```

In VS Code, set line endings to:

```txt
LF
```

not:

```txt
CRLF
```

### 3.3 Make Scripts Executable

```bash
chmod +x src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
chmod +x src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
chmod +x src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
```

Verify:

```bash
ls -l src/cpp_robotics_sim_ros/scripts/*.py
```

Expected permissions start with:

```txt
-rwx
```

### 3.4 Syntax Check

```bash
python3 -m py_compile src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
python3 -m py_compile src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
python3 -m py_compile src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
```

Expected:

```txt
no output
```

Common Python script failures:

| Symptom | Likely Cause | Fix |
|---|---|---|
| `/usr/bin/env: ‘python3\r’: No such file or directory` | Windows CRLF endings | `sed -i 's/\r$//' <script>` and rebuild |
| `Exec format error` | missing shebang or shebang not first line | ensure first line is `#!/usr/bin/env python3` |
| `Permission denied` | script not executable | `chmod +x <script>` |
| `ros2 run` cannot find script | not installed in CMake | add script to `install(PROGRAMS ...)` and rebuild |
| `SyntaxError` | Python syntax/paste issue | run `python3 -m py_compile <script>` and fix line shown |
| `ModuleNotFoundError: matplotlib` | plotting dependency missing | `sudo apt install -y python3-matplotlib` |

---

## 4. ROS 2 Usage Validation Flow

This is the standard user-facing validation flow after building the simulator.

### 4.1 Launch Original Kinematic Simulator

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

### 4.2 Publish Command

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected:

```txt
robot moves while command stream is active
robot stops after command stream ends and timeout expires
```

### 4.3 Inspect Runtime Outputs

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

### 4.4 Run Regression Script

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## 5. Launch Validation

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
| `robot_state_publisher` package missing | dependency not installed | install `ros-jazzy-robot-state-publisher` |
| `joint_state_publisher` package missing | dependency not installed | install `ros-jazzy-joint-state-publisher` |
| `ros_gz_sim` package missing | Gazebo ROS package not installed | install `ros-jazzy-ros-gz-sim` |

---

## 6. Topic Interface Reference Check

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
robot description interfaces
joint state interfaces
TF ownership
ros2_control interfaces
controller_manager state
Gazebo control topics
LaserScan sensor interfaces
simulation time and /clock
noisy odometry interfaces
trajectory validation interfaces
plot/report file outputs
```

Quick original simulator interface check:

```bash
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
ros2 topic type /diagnostics
```

Expected original simulator topics:

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

Expected Gazebo control, sensor, and validation topics when `ros2_control.launch.py`, `noisy_odom_node.py`, and the recorder are running:

```txt
/clock
/robot_description
/joint_states
/tf
/tf_static
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/diff_drive_controller/cmd_vel_out
/odom_noisy
/scan
```

---

## 7. Command and Motion Validation

Original kinematic simulator command:

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

Gazebo control stack command:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

Important distinction:

```txt
/cmd_vel moves the custom sim_node stack.
/diff_drive_controller/cmd_vel moves the Gazebo ros2_control stack.
sim_node does not move Gazebo.
```

---

## 8. Parameter Validation

Check loaded parameters for the original simulator:

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

Pass criteria:

```txt
terminal launch overrides appear in ros2 param get
robot starts near overridden initial pose
velocity limits match overridden clamp values
```

---

## 9. Odometry Validation

Original simulator odometry:

```bash
ros2 topic type /odom
ros2 topic echo --once /odom --field pose.pose.position
ros2 topic echo --once /odom --field twist.twist
```

Expected:

```txt
nav_msgs/msg/Odometry
odom header frame_id is odom
odom child_frame_id is base_link
position x/y matches planar robot pose
twist linear.x matches current command after clamping
twist angular.z matches current command after clamping
```

Gazebo controller odometry:

```bash
ros2 topic type /diff_drive_controller/odom
ros2 topic echo /diff_drive_controller/odom --once
```

Expected:

```txt
nav_msgs/msg/Odometry
header.frame_id is odom
child_frame_id is base_link
pose changes when Gazebo robot moves
```

Noisy odometry:

```bash
ros2 topic type /odom_noisy
ros2 topic echo /odom_noisy --once
```

Expected:

```txt
nav_msgs/msg/Odometry
pose is close to /diff_drive_controller/odom but includes small noise
pose.covariance and twist.covariance are populated
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

Frame tree through Day 85:

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
Kinematic simulator stack:
  sim_node owns odom -> base_link
  robot_state_publisher owns base_link -> robot links

Gazebo ros2_control stack:
  diff_drive_controller owns odom -> base_link
  joint_state_broadcaster owns /joint_states
  robot_state_publisher owns base_link -> robot links
```

Important:

```txt
Do not run sim_node and diff_drive_controller as simultaneous publishers of odom -> base_link.
```

Common TF failures:

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Invalid frame ID` | TF not broadcasting | check `publishTransform()` or active controller |
| `odom` missing | wrong parent frame | verify transform header |
| `base_link` missing | wrong child frame | verify child frame ID |
| TF exists but odom differs | pose/odom/TF inconsistency | compare pose, odom, and transform values |
| wheel frames missing | `/joint_states` missing | launch `joint_state_publisher` or controller stack |
| caster/lidar frame missing | fixed joint missing or `/tf_static` QoS issue | echo `/tf_static` with transient local durability |
| duplicate transform warning | two nodes publishing same transform | keep one owner for `odom -> base_link` |
| `TF_OLD_DATA` warnings | stale nodes or sim-time mismatch | kill old nodes, verify `/clock`, use `use_sim_time:=true` |

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

For `/tf_static`, use transient local durability when echoing:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

For `/scan` in RViz, use Best Effort if needed:

```txt
LaserScan Reliability Policy: Best Effort
```

---

## 12. rosbag2 Validation Workflow

Create local bag folder:

```bash
mkdir -p bags
```

Record original simulator topics:

```bash
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

Pass criteria:

```txt
/cmd_vel is recorded
/robot_pose is recorded
/odom is recorded
/tf is recorded
bag replay republishes robot state topics
TF can be inspected during replay
```

Important Git rule:

```txt
Do not commit actual rosbag2 data.
Commit only bags/README.md if needed.
```

---

## 13. RViz2 Validation Workflow

Original simulator RViz:

```bash
rviz2 -d src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

Gazebo control stack RViz:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Recommended Gazebo RViz settings:

```txt
Fixed Frame: odom
RobotModel Description Topic: /robot_description
Odometry Topic: /diff_drive_controller/odom
LaserScan Topic: /scan
LaserScan Reliability Policy: Best Effort if needed
```

Pass criteria:

```txt
RViz opens without errors
Fixed Frame is odom
TF display shows odom and base_link
RobotModel displays the robot
Odometry display tracks the correct odom topic
LaserScan displays /scan
robot moves in RViz when Gazebo moves and use_sim_time is true
```

---

## 14. Diagnostics Validation Workflow

Check diagnostics:

```bash
ros2 topic list | grep diagnostics
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Expected message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected status:

```txt
OK   when simulator is running with fresh command input
WARN when cmd_vel timeout is active
```

Expected diagnostic fields:

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

---

## 15. Launch Regression Workflow

The launch regression script validates the original ROS 2 kinematic simulator stack.

Script:

```txt
scripts/day68_launch_regression.sh
```

Run:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

What it validates:

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

Common launch regression failures:

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

## 16. Robot Description Validation

### 16.1 URDF Validation

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

Link and joint checks:

```bash
grep -n '<link name' ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
grep -n '<joint name' ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

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

### 16.2 Xacro Validation

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

### 16.3 robot_state_publisher Validation

Launch:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Checks:

```bash
ros2 node list
ros2 node info /robot_state_publisher
ros2 topic list | grep -E "robot_description|tf|joint_states"
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt
```

Static transform check:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

---

## 17. joint_state_publisher and RViz RobotModel Validation

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

---

## 18. Gazebo Spawn Validation

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

Gazebo-side checks:

```bash
gz topic -l | grep world
```

Installed world check:

```bash
ls "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf"
```

Common Gazebo spawn failures:

| Failure | Likely Cause | First Check |
|---|---|---|
| `ros_gz_sim` not found | missing ROS-Gazebo package | install `ros-jazzy-ros-gz-sim` |
| Gazebo opens but no robot | spawn failed or robot_description missing | inspect launch terminal output |
| world file missing | `worlds/` not installed | check CMake install block |
| robot falls through ground | collision/inertial/world issue | inspect collision geometry |

---

## 19. ros2_control Validation

Launch Gazebo control stack:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
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

Common ros2_control failures:

| Failure | Likely Cause | First Check |
|---|---|---|
| `/controller_manager` missing | `gz_ros2_control` plugin did not load | inspect Gazebo launch log |
| `gz_ros2_control` package missing | package not installed | `ros2 pkg prefix gz_ros2_control` |
| hardware interfaces missing | Xacro `ros2_control` block wrong | inspect generated URDF from Xacro |
| `joint_state_broadcaster` inactive | spawner ran before controller_manager was ready | increase launch delay or manually spawn |
| FastDDS/FastCDR symbol error | ROS package version mismatch | reinstall Jazzy control/middleware packages |
| `No clock received` | sim time enabled but `/clock` not bridged | check `/clock` bridge |

---

## 20. Gazebo Differential-Drive Control Validation

Launch:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
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
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
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

## 21. Simulated Lidar and /scan Validation

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

Lidar TF check:

```bash
ros2 run tf2_ros tf2_echo base_link lidar_link
```

RViz setup:

```txt
Fixed Frame: odom
RobotModel: /robot_description
Odometry topic: /diff_drive_controller/odom
LaserScan topic: /scan
LaserScan Reliability Policy: Best Effort if needed
```

---

## 22. Simulation Time and RViz/Gazebo Synchronization

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

Stop old nodes:

```bash
pkill -f gz || true
pkill -f rviz2 || true
pkill -f robot_state_publisher || true
pkill -f joint_state_publisher || true
pkill -f controller_manager || true
pkill -f parameter_bridge || true
pkill -f sim_node || true
```

Relaunch Gazebo control stack, then start RViz with sim time:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Pass criteria:

```txt
RViz RobotModel moves with Gazebo robot
LaserScan moves consistently with robot motion
TF_OLD_DATA warnings disappear after clean restart
```

---

## 23. Noisy Odometry Validation — Day 83

Day 83 adds:

```txt
ros2_ws/src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
```

Runtime flow:

```txt
/diff_drive_controller/odom
        ↓
noisy_odom_node.py
        ↓
/odom_noisy
```

Input:

```txt
/diff_drive_controller/odom
nav_msgs/msg/Odometry
```

Output:

```txt
/odom_noisy
nav_msgs/msg/Odometry
```

### 23.1 Build and Script Checks

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

python3 -m py_compile src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
head -n 3 src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py | cat -A
ls -l src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
```

Expected:

```txt
no syntax errors
first line is #!/usr/bin/env python3
script has executable permission
```

### 23.2 Runtime Check

Terminal 1:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Terminal 2:

```bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

Expected:

```txt
Day 83 noisy odometry node started
Subscribing: /diff_drive_controller/odom
Publishing:  /odom_noisy
```

Terminal 3:

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
/odom_noisy is nav_msgs/msg/Odometry
covariance includes nonzero values such as 0.0004 and 1.0
```

### 23.3 Common Noisy Odom Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| `/odom_noisy` missing | noisy node not running or not installed | `ros2 run cpp_robotics_sim_ros noisy_odom_node.py` |
| node starts but no messages | `/diff_drive_controller/odom` not publishing | launch Gazebo control stack |
| covariance all zero | `set_covariance()` not called or wrong field assignment | echo covariance |
| yaw looks discontinuous | normal angle wrapping around +/- pi | inspect yaw wrapping logic |
| robot does not move | expected; noisy odom is feedback only | publish to `/diff_drive_controller/cmd_vel` |

Important rule:

```txt
/odom_noisy does not move Gazebo.
It is a noisy feedback stream for validation and future localization work.
```

---

## 24. Trajectory Validation Recorder — Day 84

Day 84 adds:

```txt
ros2_ws/src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
data/.gitkeep
```

Runtime flow:

```txt
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/odom_noisy
        ↓
trajectory_validation_recorder.py
        ↓
data/day84_trajectory_validation.csv
```

### 24.1 Script Checks

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

python3 -m py_compile src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
head -n 3 src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py | cat -A
ls -l src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
```

Expected:

```txt
no syntax errors
first line is #!/usr/bin/env python3
script has executable permission
```

### 24.2 Runtime Recording Flow

Terminal 1:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Terminal 2:

```bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

Terminal 3, from repository root:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
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
Writing CSV:       /mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/data/day84_trajectory_validation.csv
Sample rate:       20.0 Hz
```

Terminal 4:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

Let it run for 10-15 seconds, then stop the command publisher, recorder, and noisy odom node.

### 24.3 CSV Verification

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"

ls data/day84_trajectory_validation.csv
head data/day84_trajectory_validation.csv
wc -l data/day84_trajectory_validation.csv
```

Expected header:

```txt
time_sec,cmd_linear_x,cmd_angular_z,actual_x,actual_y,actual_yaw,actual_linear_x,actual_angular_z,noisy_x,noisy_y,noisy_yaw
```

Sanity checks:

```bash
awk -F, 'NR>1 {print $2, $3; exit}' data/day84_trajectory_validation.csv
awk -F, 'NR>1 {print $4, $5, $6; exit}' data/day84_trajectory_validation.csv
awk -F, 'NR>1 {print $9, $10, $11; exit}' data/day84_trajectory_validation.csv
```

Expected:

```txt
command values are not blank
actual odom values are not blank
noisy odom values are not blank
```

### 24.4 Common Recorder Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| CSV only has header | `/diff_drive_controller/odom` not arriving | echo `/diff_drive_controller/odom` |
| noisy columns blank | `/odom_noisy` not publishing | run noisy odom node and echo `/odom_noisy` |
| command columns zero | command publisher not running or wrong topic | publish `TwistStamped` to `/diff_drive_controller/cmd_vel` |
| CSV writes to wrong folder | recorder launched from wrong directory or path resolution issue | check printed `Writing CSV:` path |
| `python3\r` shebang error | CRLF line endings | convert to LF and rebuild |

---

## 25. Plotting and Validation Report — Day 85

Day 85 adds:

```txt
ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
plots/.gitkeep
```

Generated outputs:

```txt
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

Input:

```txt
data/day84_trajectory_validation.csv
```

Flow:

```txt
data/day84_trajectory_validation.csv
        ↓
plot_trajectory_validation.py
        ↓
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

### 25.1 Script Checks

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

python3 -m py_compile src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
head -n 3 src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py | cat -A
ls -l src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
```

Expected:

```txt
no syntax errors
first line is #!/usr/bin/env python3
script has executable permission
```

Check matplotlib:

```bash
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

If missing:

```bash
sudo apt update
sudo apt install -y python3-matplotlib
```

### 25.2 Generate Plot and Report

Run from repository root:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"

python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

Expected:

```txt
Input CSV:        /mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/data/day84_trajectory_validation.csv
Generated plot:   /mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/plots/trajectory_validation.png
Generated report: /mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/docs/trajectory_validation_report.md
Samples:          <number of CSV data rows>
```

Important bash note:

```txt
If a command ends with backslash \, bash waits for the next line and shows >.
Do not add blank lines between continued command lines.
The final line must not end with backslash.
```

Safe one-line command:

```bash
python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

### 25.3 Verify Outputs

```bash
ls plots/trajectory_validation.png
ls docs/trajectory_validation_report.md
ls -lh plots/trajectory_validation.png
head -80 docs/trajectory_validation_report.md
```

Metric checks:

```bash
grep -n "actual path length" docs/trajectory_validation_report.md
grep -n "final actual x" docs/trajectory_validation_report.md
grep -n "mean position noise error" docs/trajectory_validation_report.md
grep -n "max yaw noise error" docs/trajectory_validation_report.md
grep -n "max actual linear velocity" docs/trajectory_validation_report.md
grep -n "max actual yaw rate" docs/trajectory_validation_report.md
```

Expected:

```txt
plot exists and is not 0 bytes
report exists
all metric grep commands return lines
```

### 25.4 Plot Interpretation

For the command:

```txt
linear velocity = 0.25 m/s
yaw rate        = 0.2 rad/s
```

Expected turning radius:

```txt
R = v / omega = 0.25 / 0.2 = 1.25 m
```

Expected plot behavior:

```txt
actual trajectory is circular
noisy trajectory overlaps actual trajectory with small jitter
yaw wraps from +pi to -pi, which is normal angle wrapping
actual linear velocity tracks commanded linear velocity
actual yaw rate tracks commanded yaw rate
```

### 25.5 Common Plot/Report Failures

| Failure | Likely Cause | First Check |
|---|---|---|
| CSV file not found | Day 84 recorder not run or wrong path | `ls data/day84_trajectory_validation.csv` |
| missing required column | recorder script old or CSV manually edited | `head data/day84_trajectory_validation.csv` |
| plot file 0 bytes | matplotlib failure or interrupted script | rerun plotting command |
| report missing metrics | script old or report generation failed | grep metric names |
| `SyntaxError: unterminated triple-quoted f-string` | incomplete paste of plotting script | replace file and run `py_compile` |
| `ModuleNotFoundError: matplotlib` | dependency missing | install `python3-matplotlib` |
| bash shows `>` prompt | command ended with backslash | finish command correctly or use one-line version |

---

## 26. Days 81-85 Validation Flow

Use this full validation flow after Days 81-85 changes.

### 26.1 Clean Build

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

### 26.2 Verify Executables

```bash
ros2 pkg executables cpp_robotics_sim_ros | grep -E "noisy|trajectory"
```

Expected:

```txt
cpp_robotics_sim_ros noisy_odom_node.py
cpp_robotics_sim_ros trajectory_validation_recorder.py
cpp_robotics_sim_ros plot_trajectory_validation.py
```

### 26.3 Launch Gazebo and Record Validation Data

Terminal 1:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Terminal 2:

```bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

Terminal 3:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run cpp_robotics_sim_ros trajectory_validation_recorder.py
```

Terminal 4:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

### 26.4 Generate Plot and Report

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"

python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

### 26.5 Verify Day 85 Artifacts

```bash
ls data/day84_trajectory_validation.csv
ls plots/trajectory_validation.png
ls docs/trajectory_validation_report.md

head data/day84_trajectory_validation.csv
ls -lh plots/trajectory_validation.png

grep -n "actual path length" docs/trajectory_validation_report.md
grep -n "mean position noise error" docs/trajectory_validation_report.md
grep -n "max actual linear velocity" docs/trajectory_validation_report.md
grep -n "max actual yaw rate" docs/trajectory_validation_report.md
```

### 26.6 Run Regression

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## 27. Regression Test Checklist

Run this checklist after meaningful simulator changes.

| Test | Command / Method | Expected Result |
|---|---|---|
| Build | `colcon build --cmake-args -DBUILD_TESTING=OFF` | Build passes |
| Python syntax | `python3 -m py_compile <script>` | No output |
| Script install | `ros2 pkg executables cpp_robotics_sim_ros` | scripts listed |
| Launch | `ros2 launch cpp_robotics_sim_ros sim.launch.py` | Node starts |
| Topic list | `ros2 topic list` | `/cmd_vel`, `/robot_pose`, `/odom`, `/tf`, `/diagnostics` exist |
| Pose output | `ros2 topic echo --once /robot_pose` | Pose message appears |
| Odom output | `ros2 topic echo --once /odom` | Odometry message appears |
| TF output | `tf2_echo odom base_link` | Transform appears |
| Diagnostics output | `ros2 topic echo --once /diagnostics` | DiagnosticArray message appears |
| Command motion | publish `/cmd_vel` | Pose changes |
| Timeout | stop `/cmd_vel` | Robot stops after timeout |
| Params | `ros2 param get` | Expected values appear |
| Launch args | override launch arguments | Overridden values appear |
| QoS | `ros2 topic info --verbose` | Reliable/volatile appears |
| RViz2 | open saved RViz config | Grid, TF, and Odometry display correctly |
| URDF parse | Python XML parse | URDF XML parses |
| Xacro generation | `xacro diffbot.xacro` | generated URDF parses |
| robot_state_publisher | `description.launch.py` | `/robot_description`, `/tf`, `/tf_static` exist |
| joint_state_publisher | `description.launch.py` | `/joint_states` exists |
| RViz RobotModel | `robot_model_viz.launch.py` | RobotModel appears |
| Gazebo spawn | `gazebo_spawn.launch.py` | diffbot appears in Gazebo |
| ros2_control | `ros2_control.launch.py` | controller_manager and hardware interfaces appear |
| joint broadcaster | `ros2 control list_controllers` | joint_state_broadcaster active |
| diff-drive controller | `ros2 control list_controllers` | diff_drive_controller active |
| Gazebo drive command | publish `TwistStamped` to controller | robot moves in Gazebo |
| Controller odom | echo `/diff_drive_controller/odom` | odom publishes with `odom` and `base_link` frames |
| Lidar scan | echo `/scan` | LaserScan ranges publish |
| Lidar TF | `tf2_echo base_link lidar_link` | fixed lidar transform appears |
| RViz sim time | `rviz2 --ros-args -p use_sim_time:=true` | RViz tracks Gazebo motion without TF_OLD_DATA |
| Noisy odom | echo `/odom_noisy` | noisy Odometry publishes with covariance |
| CSV recorder | run recorder while robot moves | CSV file generated with data rows |
| Plot/report | run plotting script | PNG and Markdown report generated |
| Launch regression | `./scripts/day68_launch_regression.sh` | Regression script passes |

---

## 28. Common Failure Modes

| Failure | Likely Cause | First Check |
|---|---|---|
| No `/robot_pose` | node not running or publisher failed | `ros2 node list`, `ros2 topic list` |
| No `/cmd_vel` subscriber | node not launched | `ros2 topic info /cmd_vel` |
| No `/diagnostics` | diagnostics publisher missing or not rebuilt | `ros2 topic list` |
| Robot does not move | no command or command timeout | publish command continuously |
| Robot moves forever | timeout logic broken | stop commands and wait |
| Parameters not changing | YAML/install mismatch | check installed YAML |
| Launch override ignored | parameter dictionary order wrong | dictionary must come after `params_file` |
| TF missing | transform broadcaster issue | `tf2_echo odom base_link` |
| Bag missing topics | topics not active during recording | start simulator before recording |
| RViz config missing after build | rviz directory not installed | check CMake install block |
| Diagnostics always WARN | no fresh command input | publish `/cmd_vel` at 10 Hz |
| Launch regression script fails with `bash\r` | CRLF line endings | convert shell script to LF |
| Xacro command fails with spaces in path | launch command not quoted | quote model path in `Command(...)` |
| XML parsed as YAML | robot description not forced to string | use `ParameterValue(..., value_type=str)` |
| no `/joint_states` | publisher/broadcaster not installed or launched | `ros2 node list` |
| Gazebo opens but no robot | spawn failed or `/robot_description` missing | inspect launch terminal |
| controller_manager missing | gz_ros2_control plugin not loaded | inspect Gazebo log |
| diff_drive_controller missing | spawner missing or YAML issue | `ros2 control list_controllers` |
| wheel names empty | YAML indentation wrong | installed `ros2_control.yaml` |
| Gazebo moves but RViz does not | sim time or odom topic mismatch | `/clock`, RViz use_sim_time, odom topic |
| `/scan` missing | sensor or bridge not running | `gz topic -l`, `ros2 topic list` |
| TF_OLD_DATA warnings | stale nodes or clock mismatch | restart stack and use sim time |
| `/odom_noisy` missing | noisy odom node not running | `ros2 run cpp_robotics_sim_ros noisy_odom_node.py` |
| CSV missing | recorder not run or wrong path | check recorder terminal and `data/` |
| plot missing | plotting script not run or matplotlib missing | run script and check dependency |
| Python `python3\r` error | Windows CRLF line endings | `sed -i 's/\r$//' <script>` |
| Python `Exec format error` | bad shebang or not first line | inspect with `head -n 3 <script> | cat -A` |
| `.sdf` not tracked | `.gitignore` excludes SDF files | `git check-ignore -v` |

---

## 29. Standalone C++ Validation

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

## 30. Git Validation

Before every commit:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
git status --short
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

Day 84 raw CSV is optional and should usually not be committed unless intentionally preserving a validation run:

```bash
git restore --staged data/day84_trajectory_validation.csv 2>/dev/null || true
```

Recommended Days 81-85 staged files:

```bash
git add README.md
git add docs/daily_documentation.md
git add docs/debugging_and_validation.md
git add docs/system_architecture.md
git add docs/topic_interface_reference.md
git add docs/nav2_architecture.md
git add docs/state_estimation_notes.md
git add docs/trajectory_validation_report.md
git add ros2_ws/src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
git add ros2_ws/src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
git add ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
git add ros2_ws/src/cpp_robotics_sim_ros/CMakeLists.txt
git add ros2_ws/src/cpp_robotics_sim_ros/package.xml
git add data/.gitkeep
git add plots/.gitkeep
git add plots/trajectory_validation.png
```

Final pre-commit validation:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash

cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

Commit:

```bash
git commit -m "Days 81-85 add autonomy validation readiness"
git push
git status
```

---

## 31. Day 85 Completion Checklist

Days 81-85 are complete when all of this is true:

```txt
docs/nav2_architecture.md exists
docs/state_estimation_notes.md exists
noisy_odom_node.py exists and runs
/odom_noisy publishes nav_msgs/msg/Odometry with covariance
trajectory_validation_recorder.py exists and runs
data/day84_trajectory_validation.csv is generated locally
plot_trajectory_validation.py exists and runs
plots/trajectory_validation.png exists and is not empty
docs/trajectory_validation_report.md exists and contains metrics
README.md is updated
docs/daily_documentation.md is updated
docs/system_architecture.md is updated
docs/topic_interface_reference.md is updated
docs/debugging_and_validation.md is updated
clean build passes
Day 68 launch regression passes
Git status is reviewed before commit
```

Final engineering statement:

```txt
The project now demonstrates not only Gazebo robot motion, but also controlled uncertainty injection, command-vs-actual-vs-noisy data recording, quantitative metrics, plotting, and validation reporting.
```
