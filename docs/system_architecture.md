# System Architecture — C++ / ROS 2 Robotics Simulation Foundation

This document explains how the standalone C++ simulator, differential-drive module, manipulator module, ROS 2 simulator, diagnostics layer, visualization workflow, launch regression workflow, robot description stack, RViz RobotModel workflow, and Gazebo spawn workflow are organized and connected.

---

## 1. Project Purpose

This repository demonstrates a robotics simulation foundation built in stages:

1. Standalone C++ robotics simulation fundamentals
2. Differential-drive mobile robot simulation
3. Manipulator joint-state simulation
4. ROS 2 C++ integration using standard robot topics, odometry, TF, launch files, YAML parameters, launch arguments, QoS profiles, rosbag2, RViz2, diagnostics, and launch regression testing
5. Robot description modeling using URDF and Xacro
6. Robot state publishing using `robot_state_publisher`
7. Joint state publishing using `joint_state_publisher`
8. RViz RobotModel visualization
9. Gazebo Sim spawning using `ros_gz_sim`

The goal is to show both low-level C++ simulation logic and ROS 2 robotics system integration.

The project is intentionally built as an engineering artifact, not just a code exercise. It includes modular structure, runtime configuration, validation checks, debugging workflow, regression testing, performance timing, visualization, diagnostics, robot modeling, Gazebo spawning, and documentation.

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

The repository has four main layers:

```txt
standalone_cpp/  = pure C++ simulation modules
ros2_ws/         = ROS 2 C++ simulator, robot model, visualization, and Gazebo integration
scripts/         = repeatable validation and regression scripts
docs/            = architecture, debugging, validation, interface, and daily documentation
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

The simulator models a planar mobile robot controlled through `/cmd_vel`.

It accepts velocity commands, applies command timeout and velocity clamping, updates robot pose using planar kinematics, publishes robot state, publishes odometry, broadcasts the transform between `odom` and `base_link`, and reports runtime diagnostics.

---

## 4. Extended Robot Architecture After Days 71–76

The project now has a robot description and Gazebo spawn layer in addition to the original ROS 2 kinematic simulator.

```txt
                         /cmd_vel
                            |
                            v
                        sim_node
                            |
        ------------------------------------------------
        |                    |                         |
        v                    v                         v
   /robot_pose             /odom                      /tf
                                                odom -> base_link


       xacro/diffbot.xacro
                |
                v
        /robot_description
                |
                v
       robot_state_publisher  <---  /joint_states
                |
                v
        /tf and /tf_static
        base_link -> robot links


       empty_diffbot_world.sdf
                |
                v
            Gazebo Sim
                ^
                |
        ros_gz_sim create
                ^
                |
        /robot_description
```

The key transform ownership rule is:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
```

This prevents duplicate TF publishers for the same transform.

---

## 5. Standalone C++ Layer

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

## 6. Differential-Drive Module

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

## 7. Manipulator Module

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

## 8. Main Demo Runner

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

## 9. ROS 2 Integration Layer

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

## 10. ROS 2 Node

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

## 11. Topic Architecture

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

| Topic          | Type                                  | Direction | Purpose                                  |
| -------------- | ------------------------------------- | --------- | ---------------------------------------- |
| `/cmd_vel`     | `geometry_msgs/msg/Twist`             | Input     | Velocity command input                   |
| `/robot_pose`  | `geometry_msgs/msg/Pose2D`            | Output    | Simple 2D robot pose for quick debugging |
| `/odom`        | `nav_msgs/msg/Odometry`               | Output    | Standard robot odometry                  |
| `/tf`          | `tf2_msgs/msg/TFMessage`              | Output    | Transform tree data                      |
| `/diagnostics` | `diagnostic_msgs/msg/DiagnosticArray` | Output    | Runtime health and simulator diagnostics |

---

## 12. Topic Interface Documentation Layer

Day 70 added a dedicated topic interface reference:

```txt
docs/topic_interface_reference.md
```

This document defines the runtime communication contract for the ROS 2 simulator.

It documents:

```txt
/cmd_vel input contract
/robot_pose output contract
/odom output contract
/tf frame contract
/diagnostics health/status contract
/robot_description model contract
/joint_states robot model contract
/tf_static fixed transform contract
QoS behavior
validation commands
common interface failures
```

This layer does not change the runtime architecture. It makes the architecture easier to integrate, test, debug, and explain.

---

## 13. Interface Contract Summary

```txt
/cmd_vel
  external command source -> sim_node

/robot_pose
  sim_node -> simple 2D pose debugging

/odom
  sim_node -> ROS-standard odometry

/tf
  sim_node -> odom to base_link transform
  robot_state_publisher -> robot link transforms below base_link

/tf_static
  robot_state_publisher -> fixed robot link transforms

/diagnostics
  sim_node -> runtime health and timeout status

/robot_description
  Xacro-generated robot model XML

/joint_states
  joint_state_publisher -> wheel joint positions
```

---

## 14. Inputs

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

## 15. Outputs

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

The simulator publishes:

```txt
odom -> base_link
```

`robot_state_publisher` publishes robot link transforms below `base_link`.

---

### `/tf_static`

Type:

```txt
tf2_msgs/msg/TFMessage
```

Fixed robot description transforms are published here.

Current fixed transform:

```txt
base_link -> caster_link
```

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

## 16. Frame Tree

Original simulator frame tree:

```txt
odom
  └── base_link
```

Extended frame tree after URDF/Xacro and robot state publishing:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

`odom` is the parent world/odometry frame.

`base_link` is the moving robot body frame.

`left_wheel_link`, `right_wheel_link`, and `caster_link` are robot structure frames below `base_link`.

Transform ownership:

```txt
sim_node:
  odom -> base_link

robot_state_publisher:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
```

---

## 17. Runtime Flow

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

Robot description runtime flow:

```txt
diffbot.xacro
   ↓
xacro command in launch
   ↓
robot_description parameter
   ↓
robot_state_publisher
   ↓
/tf_static and /tf for robot links
```

Joint state runtime flow:

```txt
diffbot.xacro joint definitions
   ↓
joint_state_publisher
   ↓
/joint_states
   ↓
robot_state_publisher
   ↓
wheel link transforms
```

Gazebo spawn runtime flow:

```txt
empty_diffbot_world.sdf
   ↓
Gazebo Sim starts
   ↓
/robot_description is published
   ↓
ros_gz_sim create
   ↓
diffbot model appears in Gazebo world
```

---

## 18. Kinematic Model

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

## 19. Quaternion Conversion

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

## 20. Safety Logic

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

## 21. Parameter Validation

The simulator rejects invalid runtime parameters:

```txt
dt <= 0
cmd_timeout <= 0
max_linear_velocity < 0
max_angular_velocity < 0
```

This follows the fail-fast principle: bad configuration should stop the node before it produces misleading simulation results.

---

## 22. Launch and Configuration Flow

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

## 23. QoS Design

The simulator uses explicit QoS profiles for command, state, and diagnostics topics.

| Topic          | Endpoint                                      | QoS Choice                        | Reason                                                                                                |
| -------------- | --------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/cmd_vel`     | Subscriber                                    | reliable, volatile, keep_last(10) | Commands should be delivered reliably, but stale commands should not be replayed to late subscribers. |
| `/robot_pose`  | Publisher                                     | reliable, volatile, keep_last(10) | Low-rate simulator pose output should be reliable for debugging and validation.                       |
| `/odom`        | Publisher                                     | reliable, volatile, keep_last(10) | Odometry is important state output for RViz, rosbag2, and validation.                                 |
| `/diagnostics` | Publisher                                     | reliable, volatile, keep_last(10) | Diagnostics should be available reliably for runtime health checks.                                   |
| `/tf`          | Publisher via `tf2_ros::TransformBroadcaster` | handled by tf2 broadcaster        | Standard TF broadcaster manages transform publication.                                                |
| `/tf_static`   | Publisher via `robot_state_publisher`         | transient local behavior expected | Fixed transforms should be available to late subscribers.                                             |

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

## 24. Data Recording and Replay

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

## 25. RViz2 Visualization Layer

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

## 26. RViz RobotModel Visualization Layer

Day 75 adds a full robot model visualization configuration:

```txt
ros2_ws/src/cpp_robotics_sim_ros/rviz/diffbot_robot_model.rviz
```

The launch file is:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/robot_model_viz.launch.py
```

This launch file starts:

```txt
sim_node
robot_state_publisher
joint_state_publisher
rviz2
```

RViz displays:

```txt
Grid
TF
RobotModel
Odometry
```

The fixed frame is:

```txt
odom
```

The RobotModel source is:

```txt
/robot_description
```

This validates the complete visual stack:

```txt
odom -> base_link -> left_wheel_link
                  -> right_wheel_link
                  -> caster_link
```

---

## 27. Diagnostics Layer

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

## 28. Launch Regression Layer

Day 68 adds a launch regression layer around the ROS 2 simulator architecture.

The regression script is:

```txt
scripts/day68_launch_regression.sh
```

This script does not change the robot simulation model. Instead, it validates that the runtime architecture still works after changes.

### What the Regression Layer Checks

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

### Architecture Role

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

### Why This Layer Matters

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

## 29. URDF Robot Description Layer

Day 71 adds a static URDF robot description:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

The URDF defines:

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

The URDF includes:

```txt
visual geometry
collision geometry
basic inertial properties
continuous wheel joints
fixed caster joint
```

The URDF does not publish transforms by itself. It is a robot structure description. It becomes active when used by `robot_state_publisher`.

---

## 30. Xacro Robot Description Layer

Day 72 converts the static URDF into a parameterized Xacro model:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

The Xacro model defines reusable properties and macros for:

```txt
chassis dimensions
wheel radius
wheel width
wheel separation
caster radius
masses
box inertia
wheel inertia
sphere inertia
wheel link generation
```

The Xacro model is the maintainable robot description source used by later launch files.

Robot description generation flow:

```txt
diffbot.xacro
   ↓
xacro command
   ↓
generated URDF XML
   ↓
robot_description parameter
```

---

## 31. robot_state_publisher Layer

Day 73 adds:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/description.launch.py
```

This launch file evaluates the Xacro model and starts:

```txt
robot_state_publisher
```

It publishes:

```txt
/robot_description
/tf
/tf_static
```

Important launch behavior:

```txt
Xacro output must be wrapped as a string parameter using ParameterValue(..., value_type=str)
The Xacro command must quote model paths because the local repository path contains spaces
```

The fixed caster transform appears on `/tf_static`:

```txt
base_link -> caster_link
```

---

## 32. joint_state_publisher Layer

Day 74 updates `description.launch.py` to also start:

```txt
joint_state_publisher
```

It publishes:

```txt
/joint_states
```

Expected joint names:

```txt
left_wheel_joint
right_wheel_joint
```

`robot_state_publisher` uses `/joint_states` plus `/robot_description` to publish transforms for continuous joints:

```txt
base_link -> left_wheel_link
base_link -> right_wheel_link
```

This completes the basic robot description TF tree below `base_link`.

---

## 33. Gazebo Spawn Layer

Day 76 adds a Gazebo world:

```txt
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
```

and a Gazebo launch file:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/gazebo_spawn.launch.py
```

The world includes:

```txt
empty_diffbot_world
physics system
user commands system
scene broadcaster system
sun light
ground plane
```

Gazebo spawn flow:

```txt
gazebo_spawn.launch.py
        ├── ros_gz_sim gz_sim.launch.py
        ├── empty_diffbot_world.sdf
        ├── description.launch.py
        └── ros_gz_sim create from /robot_description
```

Day 76 proves that the robot model can be inserted into a Gazebo physics world.

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

## 34. Performance Timing

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

## 35. Relationship Between Modules

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

Robot description layer:
URDF/Xacro structural robot model

Visualization layer:
RViz TF/Odometry/RobotModel inspection

Gazebo layer:
physics-simulation world and robot spawn entry point
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
frame ownership
robot model structure
simulation environment setup
```

---

## 36. Build Standalone C++ Project

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

## 37. Build ROS 2 Project

```bash
cd ros2_ws
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Launch simulator:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Launch robot description stack:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Launch RViz RobotModel stack:

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

Launch Gazebo spawn stack:

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

---

## 38. Verification Commands

Check simulator topics:

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

Check simulator TF:

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

Check robot link transforms:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link caster_link
```

Check Gazebo topics:

```bash
gz topic -l | grep world
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

## 39. Validation and Regression

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
URDF XML validation
Xacro generation validation
robot_state_publisher validation
joint_state_publisher validation
RViz RobotModel validation
Gazebo world validation
Gazebo spawn validation
```

These tests are documented in:

```txt
docs/debugging_and_validation.md
```

---

## 40. Debug Workflow

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

## 41. What This Project Demonstrates

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
* RViz RobotModel visualization
* performance timing
* engineering documentation
* rosbag2 recording and replay
* launch regression validation
* URDF robot modeling
* Xacro robot modeling
* `robot_state_publisher` workflow
* `joint_state_publisher` workflow
* Gazebo Sim world setup
* Gazebo robot spawning through `ros_gz_sim`

---

## 42. Current Limitations

Current limitations:

```txt
The manipulator module does not yet publish ROS 2 /joint_states.
The manipulator module does not yet include forward kinematics.
The differential-drive Gazebo model is spawned but not yet driven by ros2_control or a Gazebo diff-drive plugin.
The ROS 2 kinematic sim_node and Gazebo physics model are not yet dynamically coupled.
Sensor simulation is not yet added.
ros2_control integration is not yet added.
Gazebo-to-ROS odometry bridging is not yet added.
Automated tests and CI are not yet added.
```

---

## 43. Future Work

Planned future work:

```txt
Add ros2_control/controller-manager integration
Add Gazebo differential-drive plugin or ros2_control hardware interface
Drive the Gazebo robot from /cmd_vel
Add simulated lidar or camera topics
Add noise and uncertainty models
Add Gazebo-to-ROS odometry/sensor bridging
Add unit tests and CI
Add final portfolio screenshots, plots, and demo video/GIF
```

---

## 44. User-Facing Usage Layer

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

Days 71–76 extend usage documentation to include:

```txt
validate URDF
generate URDF from Xacro
launch robot_state_publisher
launch joint_state_publisher
inspect /robot_description
inspect /joint_states
inspect /tf_static
open RViz RobotModel visualization
spawn the robot in Gazebo
```

This does not change the runtime architecture. It makes the architecture easier to operate, validate, and explain.

---

## 45. Usage Architecture Flow

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

Robot model usage flow:

```txt
developer or reviewer
        ↓
build + source workspace
        ↓
ros2 launch cpp_robotics_sim_ros description.launch.py
        ↓
inspect /robot_description, /joint_states, /tf_static
        ↓
tf2_echo base_link left_wheel_link/right_wheel_link/caster_link
```

RViz RobotModel usage flow:

```txt
developer or reviewer
        ↓
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
        ↓
RViz opens with Grid, TF, RobotModel, Odometry
        ↓
robot model is visually checked against odom/base_link TF
```

Gazebo usage flow:

```txt
developer or reviewer
        ↓
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
        ↓
Gazebo opens empty_diffbot_world.sdf
        ↓
/robot_description is published
        ↓
ros_gz_sim create spawns diffbot
        ↓
robot appears in Gazebo
```

---

## 46. Why This Layer Matters

Robotics simulation projects must be reproducible.

Usage documentation turns the system from personal code into an engineering artifact that another person can build, run, inspect, validate, and debug.

The project now covers three levels of reproducibility:

```txt
1. Runtime reproducibility:
   Launch files, YAML parameters, and CLI validation commands.

2. Interface reproducibility:
   Topic interface reference, TF ownership rules, QoS definitions, and diagnostics.

3. Simulation environment reproducibility:
   URDF/Xacro model, RViz RobotModel config, Gazebo world file, and Gazebo spawn launch.
```

---

## 47. Interview Summary

In interview language:

```txt
I built a modular C++ robotics simulation foundation with separate differential-drive and manipulator modules, then integrated the mobile robot simulation into ROS 2 using /cmd_vel, /robot_pose, /odom, TF, and /diagnostics. The project includes launch files, YAML parameters, launch argument overrides, explicit QoS profiles, rosbag2 recording/replay, RViz visualization, runtime diagnostics, performance timing, launch regression testing, URDF/Xacro robot modeling, robot_state_publisher, joint_state_publisher, RViz RobotModel visualization, and a Gazebo Sim spawn workflow. The simulator owns odom -> base_link, while the robot description stack owns the robot structure below base_link.
```
