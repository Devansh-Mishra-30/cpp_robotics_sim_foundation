# System Architecture — C++ / ROS 2 Robotics Simulation Foundation

This document explains how the standalone C++ simulator, differential-drive module, manipulator module, ROS 2 simulator, diagnostics layer, visualization workflow, and launch regression workflow are organized and connected.

---

## 1. Project Purpose

This repository demonstrates a robotics simulation foundation built in stages:

1. Standalone C++ robotics simulation fundamentals
2. Differential-drive mobile robot simulation
3. Manipulator joint-state simulation
4. ROS 2 C++ integration using standard robot topics, odometry, TF, launch files, YAML parameters, launch arguments, QoS profiles, rosbag2, RViz2, diagnostics, and launch regression testing

The goal is to show both low-level C++ simulation logic and ROS 2 robotics system integration.

The project is intentionally built as an engineering artifact, not just a code exercise. It includes modular structure, runtime configuration, validation checks, debugging workflow, regression testing, performance timing, visualization, diagnostics, and documentation.

---

## 2. Repository Layers

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
│       │   └── sim.launch.py
│       ├── rviz/
│       │   └── sim_debug.rviz
│       ├── src/
│       │   └── sim_node.cpp
│       ├── CMakeLists.txt
│       └── package.xml
│
├── scripts/
│   └── day68_launch_regression.sh
│
└── docs/
    ├── daily_documentation.md
    ├── system_architecture.md
    └── debugging_and_validation.md
```

The repository has four main layers:

```txt
standalone_cpp/  = pure C++ simulation modules
ros2_ws/         = ROS 2 C++ simulator integration
scripts/         = repeatable validation and regression scripts
docs/            = architecture, debugging, validation, and daily documentation
```

---

## 3. High-Level System Architecture

```txt
                   geometry_msgs/msg/Twist
                         /cmd_vel
                            |
                            v
                 +-------------------------+
                 |        sim_node         |
                 |-------------------------|
                 | cmdVelCallback()        |
                 | timerCallback()         |
                 | validateParameters()    |
                 | publishOdometry()       |
                 | publishTransform()      |
                 | publishDiagnostics()    |
                 +-------------------------+
                    |        |        |        |
                    |        |        |        |
                    v        v        v        v
          /robot_pose     /odom     /tf   /diagnostics
        Pose2D msg     Odometry   TF     DiagnosticArray
```

Frame tree:

```txt
odom
  └── base_link
```

The simulator models a planar mobile robot controlled through `/cmd_vel`. It accepts velocity commands, applies command timeout and velocity clamping, updates robot pose using planar kinematics, publishes robot state, publishes odometry, broadcasts the transform between `odom` and `base_link`, and reports runtime diagnostics.

---

## 4. Standalone C++ Layer

The standalone C++ layer contains the core robotics simulation logic without ROS 2 dependencies.

It demonstrates:

* C++ project structure
* simulation loops
* kinematic updates
* trajectory logging
* trajectory metrics
* validation checks
* manipulator joint-state updates
* differential-drive mobile robot simulation
* modular file organization

This layer builds into the executable:

```txt
robotics_sim
```

The standalone layer is useful because it isolates the simulation logic from ROS 2 communication. This makes it easier to test math, state updates, command handling, and validation logic before integrating with ROS 2.

---

## 5. Differential-Drive Module

Folder:

```txt
standalone_cpp/include/differential_drive/
standalone_cpp/src/differential_drive/
```

Purpose:

The differential-drive module models a mobile robot that converts wheel speeds into robot motion.

Main concepts:

```txt
left wheel speed
right wheel speed
linear velocity
angular velocity
2D pose
trajectory
target tracking
validation metrics
```

Main data types:

```txt
Pose2D
RobotCommand
WheelCommand
TrajectoryMetrics
SimulationScenario
ValidationResult
```

Main behavior:

```txt
wheel speeds -> v and omega -> pose update -> trajectory -> metrics
```

This module demonstrates mobile robot kinematics, trajectory validation, and target-tracking simulation.

---

## 6. Manipulator Module

Folder:

```txt
standalone_cpp/include/manipulator/
standalone_cpp/src/manipulator/
```

Purpose:

The manipulator module models basic joint-space motion for a robot arm.

Main concepts:

```txt
joint name
joint position
joint velocity
joint minimum limit
joint maximum limit
joint update
joint clamping
```

Main data type:

```txt
JointState
```

Main behavior:

```txt
q_next = q_current + q_dot * dt
q_next = clamp(q_next, min_position, max_position)
```

This module demonstrates manipulator joint-state simulation, timestep integration, and joint safety limits.

---

## 7. Main Demo Runner

File:

```txt
standalone_cpp/src/main.cpp
```

`main.cpp` acts as the combined standalone demo runner.

It runs:

```txt
differential-drive demo
manipulator joint-state demo
scenario runner demo
validation tests
target-tracking demo
```

The logic is separated into modules, while `main.cpp` coordinates the demos.

---

## 8. ROS 2 Integration Layer

Folder:

```txt
ros2_ws/src/cpp_robotics_sim_ros/
```

Purpose:

The ROS 2 layer integrates the mobile robot simulation concepts into a ROS 2 C++ node.

The ROS 2 simulator uses:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

The node receives velocity commands, updates robot pose, publishes odometry, broadcasts the `odom -> base_link` transform, and publishes structured runtime diagnostics.

This demonstrates how standalone simulation logic can be exposed through standard ROS 2 robotics interfaces.

---

## 9. ROS 2 Node

Node name:

```txt
/sim_node
```

Executable:

```txt
sim_node
```

Package:

```txt
cpp_robotics_sim_ros
```

The node is written in C++ using `rclcpp`.

Main responsibilities:

```txt
subscribe to /cmd_vel
store latest command
check command timeout
clamp unsafe velocity commands
integrate robot pose
publish /robot_pose
publish /odom
broadcast odom -> base_link transform
publish /diagnostics
report runtime timing
```

---

## 10. Topic Architecture

```txt
/cmd_vel
   │
   ▼
+---------------------+
|      sim_node       |
|                     |
|  cmd callback       |
|  timer update       |
|  pose update        |
|  odom publish       |
|  TF broadcast       |
|  diagnostics publish|
+---------------------+
   │        │        │          │
   ▼        ▼        ▼          ▼
/robot_pose /odom    /tf   /diagnostics
```

| Topic | Type | Direction | Purpose |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Input | Velocity command input |
| `/robot_pose` | `geometry_msgs/msg/Pose2D` | Output | Simple 2D robot pose for quick debugging |
| `/odom` | `nav_msgs/msg/Odometry` | Output | Standard robot odometry |
| `/tf` | `tf2_msgs/msg/TFMessage` | Output | Transform tree data |
| `/diagnostics` | `diagnostic_msgs/msg/DiagnosticArray` | Output | Runtime health and simulator diagnostics |

---

## 11. Inputs

### `/cmd_vel`

Type:

```txt
geometry_msgs/msg/Twist
```

Used fields:

```txt
linear.x   = forward velocity command
angular.z  = yaw rate command
```

The simulator clamps incoming commands using configured velocity limits.

Example command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

---

## 12. Outputs

### `/robot_pose`

Type:

```txt
geometry_msgs/msg/Pose2D
```

Fields:

```txt
x
y
theta
```

This is a simple 2D pose output for quick debugging.

---

### `/odom`

Type:

```txt
nav_msgs/msg/Odometry
```

The odometry message includes:

```txt
timestamp
parent frame: odom
child frame: base_link
position
orientation quaternion
linear velocity
angular velocity
covariance fields
```

The simulator uses `/odom` to publish the robot state in a ROS-standard format.

---

### `/tf`

Type:

```txt
tf2_msgs/msg/TFMessage
```

The TF relationship is:

```txt
odom -> base_link
```

This means the robot body frame `base_link` is located and oriented relative to the `odom` frame.

---

### `/diagnostics`

Type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

The diagnostics message reports:

```txt
command timeout state
current command age
current linear and angular velocity
velocity limits
current pose
callback timing
average callback time
max callback time
timing budget
callback count
```

Diagnostic status behavior:

```txt
OK   when command input is fresh
WARN when cmd_vel timeout is active
```

---

## 13. Frame Tree

```txt
odom
  └── base_link
```

`odom` is the parent frame.

`base_link` is the moving robot body frame.

The simulator publishes the pose of `base_link` relative to `odom`.

---

## 14. Runtime Flow

The ROS 2 simulator follows this runtime flow:

```txt
/cmd_vel
   ↓
cmdVelCallback()
   ↓
store latest command + timestamp
   ↓
timerCallback()
   ↓
command timeout check
   ↓
velocity clamp
   ↓
pose integration
   ↓
publish /robot_pose
   ↓
publish /odom
   ↓
broadcast odom -> base_link TF
   ↓
publish /diagnostics
```

This separates asynchronous command input from fixed-rate simulation updates.

---

## 15. Kinematic Model

The simulator uses planar unicycle-style kinematics.

State:

```txt
x, y, theta
```

Command:

```txt
v = linear velocity
w = angular velocity
```

Update equations:

```txt
theta = theta + w * dt
x     = x + v * cos(theta) * dt
y     = y + v * sin(theta) * dt
```

The heading angle is wrapped using:

```cpp
theta = atan2(sin(theta), cos(theta));
```

This keeps `theta` in a stable angular range.

---

## 16. Quaternion Conversion

ROS odometry and TF use quaternions for orientation.

For planar yaw:

```cpp
q.x = 0.0;
q.y = 0.0;
q.z = sin(theta / 2.0);
q.w = cos(theta / 2.0);
```

Roll and pitch are zero, so only `z` and `w` are needed to represent yaw.

---

## 17. Safety Logic

### Velocity Clamping

Incoming velocity commands are limited using:

```cpp
std::clamp(...)
```

Example:

```txt
linear.x = 5.0  ->  0.5
angular.z = 3.0 ->  0.8
```

This prevents unrealistic or unsafe commands from driving the simulator.

---

### Command Timeout

The simulator stores the time of the last received `/cmd_vel`.

If no fresh command arrives within `cmd_timeout`, the robot stops:

```txt
linear_velocity = 0
angular_velocity = 0
```

This prevents stale commands from moving the robot forever.

---

## 18. Parameter Validation

The simulator rejects invalid runtime parameters:

```txt
dt <= 0
cmd_timeout <= 0
max_linear_velocity < 0
max_angular_velocity < 0
```

This follows the fail-fast principle: bad configuration should stop the node before it produces misleading simulation results.

---

## 19. Launch and Configuration Flow

The simulator is launched with:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

The launch file loads the YAML config:

```txt
config/sim_params.yaml
```

Current YAML parameters:

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

The launch file also exposes runtime overrides:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

For exposed parameters, the precedence is:

```txt
terminal override > DeclareLaunchArgument default > YAML > C++ hardcoded default
```

This allows stable default configuration through YAML while still supporting fast runtime experiments from the terminal.

---

## 20. QoS Design

The simulator uses explicit QoS profiles for command, state, and diagnostics topics.

| Topic | Endpoint | QoS Choice | Reason |
|---|---|---|---|
| `/cmd_vel` | Subscriber | reliable, volatile, keep_last(10) | Commands should be delivered reliably, but stale commands should not be replayed to late subscribers. |
| `/robot_pose` | Publisher | reliable, volatile, keep_last(10) | Low-rate simulator pose output should be reliable for debugging and validation. |
| `/odom` | Publisher | reliable, volatile, keep_last(10) | Odometry is important state output for RViz, rosbag2, and validation. |
| `/diagnostics` | Publisher | reliable, volatile, keep_last(10) | Diagnostics should be available reliably for runtime health checks. |
| `/tf` | Publisher via `tf2_ros::TransformBroadcaster` | handled by tf2 broadcaster | Standard TF broadcaster manages transform publication. |

Code pattern:

```cpp
const auto command_qos = rclcpp::QoS(rclcpp::KeepLast(10))
    .reliable()
    .durability_volatile();

const auto state_qos = rclcpp::QoS(rclcpp::KeepLast(10))
    .reliable()
    .durability_volatile();
```

Expected QoS inspection for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics`:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

The code explicitly configures `KeepLast(10)`. The ROS 2 CLI may display history/depth as `UNKNOWN` depending on middleware introspection, so the code-level QoS definition is the source of truth for history/depth.

---

## 21. Data Recording and Replay

The simulator supports rosbag2 recording and replay for reproducible debugging and validation.

Recorded topics for the Day 65 baseline:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

Recording command:

```bash
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
```

Inspection command:

```bash
ros2 bag info bags/day65_baseline
```

Replay command:

```bash
ros2 bag play bags/day65_baseline
```

This allows the same command, state, odometry, and TF sequence to be inspected after the run and replayed for validation.

---

## 22. RViz2 Visualization Layer

The simulator includes a saved RViz2 configuration:

```txt
ros2_ws/src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

RViz2 visualizes:

```txt
Grid
TF
Odometry on /odom
```

The fixed frame is:

```txt
odom
```

The visualization layer helps confirm that the `odom -> base_link` TF relationship and `/odom` output are behaving correctly during motion.

---

## 23. Diagnostics Layer

The diagnostics layer publishes structured runtime health data on:

```txt
/diagnostics
```

Message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

The diagnostics layer reports:

```txt
simulation timestep
command timeout threshold
time since last command
timeout active state
current command velocities
velocity limits
current pose
latest callback time
average callback time
max callback time
timing budget
callback count
```

This layer turns simulator health into a ROS 2 topic instead of only terminal logs.

---

## 24. Launch Regression Layer

Day 68 adds a launch regression layer around the ROS 2 simulator architecture.

The regression script is:

```txt
scripts/day68_launch_regression.sh
```

This script does not change the robot simulation model. Instead, it validates that the runtime architecture still works after changes.

## What the Regression Layer Checks

```txt
ROS 2 package launch
node startup
topic availability
parameter loading
pose publishing
odometry publishing
TF broadcasting
diagnostics publishing
QoS/type inspection
command input path
launch argument override path
```

## Architecture Role

```txt
source code / launch / config changes
        ↓
clean build
        ↓
ros2 launch cpp_robotics_sim_ros sim.launch.py
        ↓
runtime ROS 2 graph
        ↓
topics, parameters, TF, odom, diagnostics
        ↓
day68_launch_regression.sh validates expected behavior
```

## Why This Layer Matters

The launch regression script acts as a repeatable system-level validation gate. It confirms that the ROS 2 runtime interfaces are still alive and correctly connected before a change is committed.

This helps prevent silent breakages in:

```txt
launch files
YAML parameters
topic names
publisher/subscriber setup
TF output
odometry output
diagnostics output
QoS configuration
launch argument overrides
```

---

## 25. Performance Timing

The timer callback is measured using:

```cpp
std::chrono::steady_clock
```

The simulator reports:

```txt
average callback time
max callback time
timing budget = dt * 1000 ms
```

This helps verify whether the simulator can keep up with the intended update rate.

Examples:

```txt
dt = 0.1   -> 100 ms budget
dt = 0.01  -> 10 ms budget
dt = 0.001 -> 1 ms budget
```

---

## 26. Relationship Between Modules

The project is intentionally separated:

```txt
Manipulator module:
joint-space state update

Differential-drive module:
mobile robot pose and trajectory update

ROS 2 module:
standard robotics communication layer

Diagnostics/regression layer:
runtime health monitoring and repeatable validation
```

They are connected conceptually because all layers use the same simulation engineering principles:

```txt
state representation
timestep integration
input commands
safety limits
validation
debugging
documentation
regression testing
```

---

## 27. Build Standalone C++ Project

```bash
cd standalone_cpp
rm -rf build
mkdir build
cd build
cmake ..
cmake --build .
./robotics_sim
```

---

## 28. Build ROS 2 Project

```bash
cd ros2_ws
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Launch:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

---

## 29. Verification Commands

Check topics:

```bash
ros2 topic list
```

Check pose:

```bash
ros2 topic echo --once /robot_pose
```

Check odometry:

```bash
ros2 topic echo --once /odom
```

Check TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Check diagnostics:

```bash
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Send command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Check QoS:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /diagnostics --verbose
ros2 topic info /tf --verbose
```

Run launch regression:

```bash
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## 30. Validation and Regression

The simulator is validated using repeatable checks:

```txt
zero command
straight motion
pure rotation
curved motion
positive clamp
negative clamp
timeout
continuous command
invalid parameter rejection
/odom publishing
/tf publishing
/diagnostics publishing
odom/TF consistency
performance timing
QoS inspection
launch workflow
YAML parameter loading
launch argument overrides
rosbag2 recording
rosbag2 inspection
rosbag2 replay
RViz2 visualization
launch regression script
```

These tests are documented in:

```txt
docs/debugging_and_validation.md
```

---

## 31. Debug Workflow

Debugging commands and common failure modes are documented in:

```txt
docs/debugging_and_validation.md
```

The main debugging principle is:

```txt
Do not randomly edit code.
First classify the failure, then test systematically.
```

---

## 32. What This Project Demonstrates

This project demonstrates:

* C++ robotics simulation fundamentals
* clean module separation
* differential-drive kinematics
* manipulator joint-state simulation
* trajectory metrics
* validation tests
* debug workflow
* regression testing
* ROS 2 C++ node development
* launch-based runtime workflow
* YAML runtime configuration
* launch argument overrides
* explicit QoS profiles
* odometry publishing
* TF broadcasting
* diagnostics publishing
* RViz2 visualization
* performance timing
* engineering documentation
* rosbag2 recording and replay
* launch regression validation

---

## 33. Current Limitations

Current limitations:

```txt
The manipulator module does not yet publish ROS 2 /joint_states.
The manipulator module does not yet include forward kinematics.
The differential-drive physics model is kinematic, not full rigid-body dynamics.
The ROS 2 module currently focuses on mobile robot state, not manipulator state.
URDF/Xacro robot description is planned.
Gazebo integration is planned.
Sensor simulation is planned.
ros2_control integration is planned.
```

---

## 34. Future Work

Planned future work:

```txt
Add URDF/Xacro robot model
Add robot_state_publisher workflow
Add ROS 2 /joint_states publisher
Add Gazebo simulation
Add sensor topics
Add noise and uncertainty models
Add ros2_control/controller-manager integration
Add unit tests and CI
Add final portfolio screenshots, plots, and demo video/GIF
```

---

## User-Facing Usage Layer

Day 69 adds a user-facing usage documentation layer to the project.

This layer explains how another engineer should interact with the ROS 2 simulator:

```txt
build the workspace
launch the simulator
publish /cmd_vel commands
inspect /robot_pose
inspect /odom
inspect /tf
inspect /diagnostics
open RViz2
record/replay rosbag2 data
run launch regression
```

This does not change the runtime architecture. It makes the architecture easier to operate, validate, and explain.

## Usage Architecture Flow

```txt
developer or reviewer
        ↓
README usage quickstart
        ↓
build + source workspace
        ↓
ros2 launch cpp_robotics_sim_ros sim.launch.py
        ↓
publish /cmd_vel
        ↓
inspect /robot_pose, /odom, /tf, /diagnostics
        ↓
RViz2 / rosbag2 / launch regression
```

## Why This Layer Matters

Robotics simulation projects must be reproducible. Usage documentation turns the system from personal code into an engineering artifact that another person can build, run, inspect, and validate.

## 35. Interview Summary

In interview language:

```txt
I built a modular C++ robotics simulation foundation with separate differential-drive and manipulator modules, then integrated the mobile robot simulation into ROS 2 using /cmd_vel, /robot_pose, /odom, TF, and /diagnostics. The project includes launch files, YAML parameters, launch argument overrides, explicit QoS profiles, rosbag2 recording/replay, RViz2 visualization, validation tests, joint limits, safety checks, performance timing, launch regression testing, and documentation.
```
