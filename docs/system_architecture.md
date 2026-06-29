# System Architecture — C++ / ROS 2 Robotics Simulation Foundation

This document explains how the standalone C++ simulator, ROS 2 simulator, robot description stack, RViz workflow, Gazebo simulation workflow, `ros2_control` stack, differential-drive controller, simulated lidar sensor, ROS-Gazebo bridge, noisy odometry stream, and trajectory validation workflow are organized and connected.

The project is intentionally built as an engineering artifact, not only a code exercise. It includes modular structure, runtime configuration, validation checks, debugging workflow, regression testing, visualization, diagnostics, robot modeling, Gazebo control, simulated sensing, noisy measurement generation, CSV-based validation, plotting, and documentation.

---

## 1. Project Purpose

This repository demonstrates a robotics simulation foundation built in stages:

```txt
1. Standalone C++ robotics simulation fundamentals
2. Differential-drive mobile robot simulation
3. Manipulator joint-state simulation
4. ROS 2 C++ integration using topics, parameters, odometry, TF, launch files, YAML config, QoS, rosbag2, RViz, diagnostics, and regression testing
5. Robot description modeling using URDF and Xacro
6. Robot state publishing using robot_state_publisher
7. Joint state publishing using joint_state_publisher and joint_state_broadcaster
8. RViz RobotModel visualization
9. Gazebo Sim spawning using ros_gz_sim
10. Gazebo control using ros2_control, controller_manager, gz_ros2_control, and diff_drive_controller
11. Simulated lidar sensor modeling and /scan bridging using ros_gz_bridge
12. Navigation architecture readiness using Nav2 concept notes
13. State estimation readiness using EKF, covariance, odometry drift, and uncertainty notes
14. Noisy odometry generation using a Python ROS 2 validation node
15. Trajectory validation recording using CSV output
16. Plot/report generation for portfolio-ready simulation validation evidence
```

The goal is to show both low-level C++ simulation logic and ROS 2 robotics system integration.

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
│       │   ├── sim_params.yaml
│       │   └── ros2_control.yaml
│       ├── launch/
│       │   ├── sim.launch.py
│       │   ├── description.launch.py
│       │   ├── robot_model_viz.launch.py
│       │   ├── gazebo_spawn.launch.py
│       │   └── ros2_control.launch.py
│       ├── rviz/
│       │   ├── sim_debug.rviz
│       │   └── diffbot_robot_model.rviz
│       ├── scripts/
│       │   ├── noisy_odom_node.py
│       │   ├── trajectory_validation_recorder.py
│       │   └── plot_trajectory_validation.py
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
├── data/
│   └── .gitkeep
│
├── plots/
│   ├── .gitkeep
│   └── trajectory_validation.png
│
└── docs/
    ├── daily_documentation.md
    ├── debugging_and_validation.md
    ├── system_architecture.md
    ├── topic_interface_reference.md
    ├── nav2_architecture.md
    ├── state_estimation_notes.md
    └── trajectory_validation_report.md
```

Main layers:

```txt
standalone_cpp/  = pure C++ simulation modules
ros2_ws/         = ROS 2 simulator, robot model, visualization, Gazebo, control, sensor, and validation nodes
scripts/         = repeatable validation and regression scripts
data/            = local validation CSV output directory
plots/           = portfolio-ready validation plots
docs/            = architecture, debugging, validation, topic interface, navigation, estimation, and report documentation
```

---

## 3. High-Level Architecture Summary

The project has two main robot runtime stacks and one validation layer.

### 3.1 Custom Kinematic Simulator Stack

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

This stack is useful for learning and validating:

```txt
C++ ROS 2 node development
custom planar kinematics
custom odometry publishing
custom TF broadcasting
diagnostics
runtime parameters
launch workflows
validation discipline
```

### 3.2 Gazebo ros2_control Stack

```txt
/diff_drive_controller/cmd_vel
    ↓
diff_drive_controller
    ↓
ros2_control
    ↓
gz_ros2_control
    ↓
Gazebo wheel joints
    ↓
/diff_drive_controller/odom
/tf
/joint_states
```

This stack is the physics-based Gazebo control workflow.

Important rule:

```txt
sim_node does not move Gazebo.
Gazebo movement uses diff_drive_controller, ros2_control, and gz_ros2_control.
```

### 3.3 Autonomy Validation Layer

```txt
/diff_drive_controller/odom
    ↓
noisy_odom_node.py
    ↓
/odom_noisy
```

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

This layer proves that the simulated behavior is measurable, recordable, plotable, and reportable.

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

The standalone layer isolates the math and simulation logic from ROS 2 communication. This makes it easier to test state updates, command handling, and validation logic before integrating with ROS 2.

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

Main behavior:

```txt
wheel speeds -> v and omega -> pose update -> trajectory -> metrics
```

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

Main behavior:

```txt
q_next = q_current + q_dot * dt
q_next = clamp(q_next, min_position, max_position)
```

---

## 7. ROS 2 Kinematic Simulator Layer

Folder:

```txt
ros2_ws/src/cpp_robotics_sim_ros/
```

Node:

```txt
/sim_node
```

Executable:

```txt
sim_node
```

The ROS 2 simulator uses:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

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

Runtime flow:

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

---

## 8. Kinematic Model

The custom simulator uses planar unicycle-style kinematics.

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

## 9. Odometry and Quaternion Conversion

ROS odometry and TF use quaternions for orientation.

For planar yaw:

```cpp
q.x = 0.0;
q.y = 0.0;
q.z = sin(theta / 2.0);
q.w = cos(theta / 2.0);
```

Roll and pitch are zero, so only `z` and `w` are needed to represent yaw.

Custom simulator odometry:

```txt
/odom
header.frame_id = odom
child_frame_id  = base_link
```

Gazebo controller odometry:

```txt
/diff_drive_controller/odom
header.frame_id = odom
child_frame_id  = base_link
```

---

## 10. Safety Logic

### 10.1 Velocity Clamping

Incoming velocity commands are limited using configured maximum values.

Example:

```txt
linear.x = 5.0  ->  0.5
angular.z = 3.0 ->  0.8
```

This prevents unrealistic or unsafe commands from driving the simulator.

### 10.2 Command Timeout

The simulator stores the time of the last received `/cmd_vel`.

If no fresh command arrives within `cmd_timeout`, the robot stops:

```txt
linear_velocity = 0
angular_velocity = 0
```

This prevents stale commands from moving the robot forever.

### 10.3 Parameter Validation

The simulator rejects invalid runtime parameters:

```txt
dt <= 0
cmd_timeout <= 0
max_linear_velocity < 0
max_angular_velocity < 0
```

This follows the fail-fast principle: bad configuration should stop the node before it produces misleading simulation results.

---

## 11. Launch and Configuration Flow

The simulator is launched with:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

The launch file loads:

```txt
config/sim_params.yaml
```

Current simulator YAML parameters:

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

For exposed parameters, precedence is:

```txt
terminal override > DeclareLaunchArgument default > YAML > C++ hardcoded default
```

---

## 12. QoS Design

The simulator uses explicit QoS profiles for command, state, and diagnostics topics.

| Topic | Endpoint | QoS Choice | Reason |
|---|---|---|---|
| `/cmd_vel` | subscriber | reliable, volatile, keep_last(10) | Commands should be reliable, but stale commands should not replay to late subscribers. |
| `/robot_pose` | publisher | reliable, volatile, keep_last(10) | Low-rate simulator pose output should be reliable for debugging. |
| `/odom` | publisher | reliable, volatile, keep_last(10) | Odometry is important state output for RViz, rosbag2, and validation. |
| `/diagnostics` | publisher | reliable, volatile, keep_last(10) | Diagnostics should be reliable for health checks. |
| `/tf` | TF broadcaster | handled by TF broadcaster | Standard TF broadcaster manages transform publication. |

The code explicitly configures `KeepLast(10)`. ROS 2 CLI may display history/depth as `UNKNOWN` depending on middleware introspection, so the code-level QoS definition is the source of truth.

---

## 13. Robot Description Layer

The robot description layer defines the physical robot structure.

Static reference URDF:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

Main maintainable Xacro model:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

The robot model defines:

```txt
base_link
├── left_wheel_link
├── right_wheel_link
├── caster_link
└── lidar_link
```

Joints:

```txt
left_wheel_joint   continuous
right_wheel_joint  continuous
caster_joint       fixed
lidar_joint        fixed
```

Xacro is used because it allows reusable properties and macros for:

```txt
chassis dimensions
wheel radius
wheel width
wheel separation
caster radius
lidar dimensions
masses
inertia blocks
wheel link generation
ros2_control interface definition
Gazebo sensor definition
```

---

## 14. robot_state_publisher Layer

Launch file:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/description.launch.py
```

This launch file evaluates the Xacro model and starts:

```txt
robot_state_publisher
joint_state_publisher
```

`robot_state_publisher` publishes:

```txt
/robot_description
/tf
/tf_static
```

Important launch behavior:

```txt
Xacro output must be wrapped as a string parameter using ParameterValue(..., value_type=str).
The Xacro command must quote model paths because the local repository path contains spaces.
```

The robot description stack flow:

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

---

## 15. Joint State Layers

There are two joint state mechanisms in the project.

### 15.1 joint_state_publisher

Used in the visualization-only robot description stack.

```txt
joint_state_publisher
    ↓
/joint_states
    ↓
robot_state_publisher
    ↓
base_link -> wheel link transforms
```

This is useful for simple model visualization without real hardware or a control stack.

### 15.2 joint_state_broadcaster

Used in the Gazebo `ros2_control` stack.

```txt
Gazebo simulated wheel joints
    ↓
gz_ros2_control
    ↓
ros2_control state interfaces
    ↓
joint_state_broadcaster
    ↓
/joint_states
```

This is the correct owner of `/joint_states` in the Gazebo control stack.

---

## 16. RViz Visualization Layer

The simulator includes saved RViz configurations:

```txt
ros2_ws/src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
ros2_ws/src/cpp_robotics_sim_ros/rviz/diffbot_robot_model.rviz
```

RViz can visualize:

```txt
Grid
TF
RobotModel
Odometry
LaserScan
```

For the original custom simulator stack:

```txt
Fixed Frame: odom
Odometry Topic: /odom
```

For the Gazebo control stack:

```txt
Fixed Frame: odom
Odometry Topic: /diff_drive_controller/odom
LaserScan Topic: /scan
use_sim_time: true
```

RViz is a visualization and debugging tool. It does not simulate physics and does not move the robot.

---

## 17. Gazebo Spawn Layer

World file:

```txt
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
```

Gazebo spawn launch file:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/gazebo_spawn.launch.py
```

The Gazebo world includes:

```txt
physics system
user commands system
scene broadcaster system
sensors system
sun light
ground plane
scan obstacle boxes
```

Gazebo spawn flow:

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

## 18. ros2_control Hardware Interface Layer

The Xacro model declares a `ros2_control` system block.

Each wheel joint exposes:

```txt
command interface: velocity
state interfaces: position, velocity
```

Architecture role:

```txt
diffbot.xacro ros2_control block
        ↓
generated robot_description
        ↓
gz_ros2_control plugin
        ↓
controller_manager
        ↓
controllers operate on hardware interfaces
```

`ros2_control` separates controller logic from hardware or simulator backend. In this project, Gazebo is the simulated hardware backend.

---

## 19. controller_manager Layer

`controller_manager` is created by the `gz_ros2_control` Gazebo plugin.

Its role is to:

```txt
load controllers
configure controllers
activate controllers
connect controllers to hardware interfaces
report controller state through ros2 control CLI
```

Expected controllers:

```txt
joint_state_broadcaster active
diff_drive_controller active
```

Validation command:

```bash
ros2 control list_controllers
```

---

## 20. diff_drive_controller Layer

The diff-drive controller receives body velocity commands and converts them into wheel velocity commands.

Input topic:

```txt
/diff_drive_controller/cmd_vel
```

Message type:

```txt
geometry_msgs/msg/TwistStamped
```

Output topics:

```txt
/diff_drive_controller/odom
/diff_drive_controller/cmd_vel_out
/tf when enable_odom_tf is true
```

Control flow:

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
/diff_drive_controller/odom + /tf
```

---

## 21. Differential-Drive Control Math

For wheel radius `r`, wheel separation `L`, right wheel angular velocity `wr`, and left wheel angular velocity `wl`:

```txt
v = r / 2 * (wr + wl)
omega = r / L * (wr - wl)
```

Inverse mapping from commanded body velocity to wheel velocity:

```txt
wr = (v + omega * L / 2) / r
wl = (v - omega * L / 2) / r
```

Where:

```txt
v      = robot forward velocity
omega  = robot yaw velocity
r      = wheel radius
L      = wheel separation
wr     = right wheel angular velocity
wl     = left wheel angular velocity
```

`diff_drive_controller` performs this conversion internally.

For the Day 85 validation command:

```txt
linear velocity = 0.25 m/s
yaw rate        = 0.2 rad/s
```

Expected turning radius:

```txt
R = v / omega = 0.25 / 0.2 = 1.25 m
```

This produces a circular trajectory in the validation plot.

---

## 22. Simulated Lidar Sensor Layer

Day 79 adds a simulated lidar mounted on:

```txt
lidar_link
```

The lidar is attached by a fixed joint:

```txt
base_link -> lidar_link
```

Gazebo sensor type:

```txt
gpu_lidar
```

Sensor output:

```txt
Gazebo /scan
```

ROS bridged output:

```txt
ROS /scan
sensor_msgs/msg/LaserScan
```

Sensor architecture:

```txt
lidar_link in Xacro
        ↓
Gazebo gpu_lidar sensor
        ↓
Gazebo Transport /scan
        ↓
ros_gz_bridge parameter_bridge
        ↓
ROS 2 /scan
        ↓
RViz LaserScan display
```

---

## 23. ROS-Gazebo Bridge Layer

`ros_gz_bridge` converts data between Gazebo Transport and ROS 2 topics.

Current bridges:

```txt
/clock:
  gz.msgs.Clock -> rosgraph_msgs/msg/Clock

/scan:
  gz.msgs.LaserScan -> sensor_msgs/msg/LaserScan
```

The bridge is needed because Gazebo and ROS 2 use different communication systems.

Gazebo Transport is not the same as ROS 2 DDS topics. The bridge maps message types and forwards data between them.

---

## 24. Simulation Time Layer

Gazebo publishes simulation time on `/clock`.

ROS nodes and RViz must use simulation time when visualizing Gazebo-driven data.

Required behavior:

```txt
Gazebo publishes /clock
ros_gz_bridge bridges /clock into ROS
RViz runs with use_sim_time:=true
TF timestamps and RViz time agree
```

If RViz uses wall time while Gazebo uses simulation time, RViz may show:

```txt
TF_OLD_DATA ignoring data from the past for frame base_link
```

Correct RViz launch command:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

---

## 25. Transform Ownership

The transform owner changes depending on which stack is running.

### 25.1 Kinematic Simulator Stack

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

### 25.2 Gazebo Control Stack

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

Full frame tree through Day 85:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

---

## 26. RViz vs Gazebo Architecture

RViz is a ROS visualization and debugging tool.

Gazebo is a physics simulator.

```txt
RViz:
  visualizes ROS topics and TF
  does not simulate physics
  does not move the robot

Gazebo:
  simulates worlds, rigid bodies, joints, contacts, plugins, and sensors
  moves the robot through physics and controller commands
```

In this project:

```txt
Gazebo:
  simulates robot body, wheel joints, ground plane, obstacles, and lidar sensor

ros2_control:
  connects ROS controllers to Gazebo simulated joints

RViz:
  visualizes robot_description, TF, odometry, and LaserScan
```

---

## 27. Day 80 System Summary

Through Day 80, the robot modeling and simulation system is:

```txt
Xacro robot model
        ↓
robot_description
        ↓
robot_state_publisher
        ↓
TF tree below base_link

Gazebo world + robot spawn
        ↓
Gazebo physics simulation
        ↓
gz_ros2_control
        ↓
controller_manager
        ↓
joint_state_broadcaster + diff_drive_controller
        ↓
Gazebo wheel joint motion
        ↓
/diff_drive_controller/odom + /tf

Gazebo lidar sensor
        ↓
ros_gz_bridge
        ↓
/scan
        ↓
RViz LaserScan visualization
```

Expected Gazebo control validation command:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Expected result:

```txt
robot moves in Gazebo
robot moves in RViz when sim time is enabled
/diff_drive_controller/odom updates
/scan remains active
```

---

## 28. Nav2 Concept Architecture — Day 81

Day 81 adds conceptual documentation for Nav2:

```txt
docs/nav2_architecture.md
```

Nav2 is the ROS 2 navigation framework used to move a robot from its current pose to a goal pose while avoiding obstacles.

Core navigation model:

```txt
localization tells the robot where it is
costmaps tell the robot where it is safe to move
planner decides the path
controller sends velocity commands
recovery handles failure cases
```

Important frame chain:

```txt
map -> odom -> base_link
```

Frame meanings:

```txt
base_link = robot body frame
odom      = smooth local frame that can drift
map       = globally corrected frame that can correct odometry drift
```

Planner/controller separation:

```txt
planner    = computes the path
controller = computes the velocity command needed right now
```

Costmap separation:

```txt
global_costmap = long-range route planning
local_costmap  = short-range obstacle avoidance and path execution
```

Future Nav2 connection to this project:

```txt
Nav2 controller_server
        ↓
/diff_drive_controller/cmd_vel
        ↓
diff_drive_controller
        ↓
ros2_control
        ↓
gz_ros2_control
        ↓
Gazebo wheel joints
```

Important:

```txt
Nav2 would eventually command the Gazebo control stack through /diff_drive_controller/cmd_vel.
sim_node does not move Gazebo.
```

---

## 29. State Estimation Concept Architecture — Day 82

Day 82 adds conceptual documentation for state estimation and EKF readiness:

```txt
docs/state_estimation_notes.md
```

State estimation means estimating robot state from imperfect measurements.

A simple 2D robot state can include:

```txt
x position
y position
yaw angle
linear velocity
yaw rate
```

A simple state vector:

```txt
state = [x, y, yaw, linear_velocity, yaw_rate]
```

Odometry is useful because it is smooth and local, but it drifts because small errors accumulate over time.

Common odometry error sources:

```txt
wheel slip
encoder noise
incorrect wheel radius
incorrect wheel separation
timing error
model mismatch
uneven ground
```

EKF architecture:

```txt
previous state + motion model
        ↓
prediction step
        ↓
sensor measurements
        ↓
correction step
        ↓
estimated state
```

For a differential-drive robot, the nonlinear motion model is:

```txt
x_next   = x + v * cos(yaw) * dt
y_next   = y + v * sin(yaw) * dt
yaw_next = yaw + yaw_rate * dt
```

Covariance architecture:

```txt
low covariance  = more trust
high covariance = less trust
```

ROS odometry covariance fields:

```txt
pose.covariance
twist.covariance
```

Important:

```txt
Covariance stores variance, not standard deviation.
variance = standard_deviation²
```

---

## 30. Noisy Odometry Node — Day 83

Day 83 adds a Python ROS 2 node:

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

The node adds controlled Gaussian noise to:

```txt
x
y
yaw
linear velocity
angular velocity
```

It also fills covariance values based on configured standard deviations.

Default parameters:

```txt
input_topic                    = /diff_drive_controller/odom
output_topic                   = /odom_noisy
position_noise_std             = 0.02 m
yaw_noise_std                  = 0.02 rad
linear_velocity_noise_std      = 0.02 m/s
angular_velocity_noise_std     = 0.02 rad/s
random_seed                    = 42
```

Noisy odometry architecture:

```txt
actual Gazebo controller odometry
        ↓
deep copy odometry message
        ↓
extract yaw from quaternion
        ↓
add x, y, yaw, velocity noise
        ↓
convert noisy yaw back to quaternion
        ↓
set pose and twist covariance
        ↓
publish /odom_noisy
```

Important rule:

```txt
/odom_noisy does not move Gazebo.
It is a noisy feedback stream for validation and future localization work.
```

Odometry is feedback. Velocity command topics are actuation.

Gazebo motion still comes from:

```txt
/diff_drive_controller/cmd_vel
        ↓
diff_drive_controller
        ↓
ros2_control
        ↓
gz_ros2_control
        ↓
Gazebo wheel joints
```

---

## 31. Trajectory Validation Recorder — Day 84

Day 84 adds a Python ROS 2 recorder node:

```txt
ros2_ws/src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
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

The recorder subscribes to:

```txt
/diff_drive_controller/cmd_vel
/diff_drive_controller/odom
/odom_noisy
```

It writes:

```txt
data/day84_trajectory_validation.csv
```

CSV columns:

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

Recorder architecture:

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

This design intentionally uses latest-value storage because the three topics do not necessarily arrive at exactly the same timestamp.

The recorder is validation tooling, not a controller.

Python is used because this layer focuses on:

```txt
CSV logging
quick validation scripts
data analysis
plotting workflow
report generation
engineering tooling
```

The core simulation and control stack remains C++ and `ros2_control`.

---

## 32. Plotting and Validation Report — Day 85

Day 85 adds a Python plotting and report generation script:

```txt
ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
```

Input:

```txt
data/day84_trajectory_validation.csv
```

Outputs:

```txt
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

Plot/report flow:

```txt
data/day84_trajectory_validation.csv
        ↓
plot_trajectory_validation.py
        ↓
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

The plot includes:

```txt
actual vs noisy trajectory
yaw over time
commanded vs actual linear velocity
commanded vs actual yaw rate
```

The report includes:

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

Validation plot interpretation:

```txt
The robot was commanded with linear velocity 0.25 m/s and yaw rate 0.2 rad/s.
The expected turning radius is R = v / omega = 0.25 / 0.2 = 1.25 m.
The actual trajectory is circular, which matches the differential-drive command.
The noisy trajectory closely follows the actual trajectory with small jitter.
The yaw plot wraps from +pi to -pi, which is normal angle wrapping.
The actual velocity tracks the commanded velocity closely.
```

---

## 33. Days 81-85 Complete Validation Architecture

The complete Day 85 validation architecture is:

```txt
Gazebo robot motion:
    /diff_drive_controller/cmd_vel
        ↓
    diff_drive_controller
        ↓
    ros2_control
        ↓
    gz_ros2_control
        ↓
    Gazebo wheel joints
        ↓
    /diff_drive_controller/odom

Noisy measurement stream:
    /diff_drive_controller/odom
        ↓
    noisy_odom_node.py
        ↓
    /odom_noisy

Validation recording:
    /diff_drive_controller/cmd_vel
    /diff_drive_controller/odom
    /odom_noisy
        ↓
    trajectory_validation_recorder.py
        ↓
    data/day84_trajectory_validation.csv

Plot and report generation:
    data/day84_trajectory_validation.csv
        ↓
    plot_trajectory_validation.py
        ↓
    plots/trajectory_validation.png
    docs/trajectory_validation_report.md
```

This proves that the simulation behavior is:

```txt
commandable
measurable
recordable
plotable
reportable
explainable
repeatable
```

Before Days 81-85, the project proved:

```txt
the robot model can be described
the robot can spawn in Gazebo
the robot can be controlled through ros2_control
the robot can publish odometry, TF, joint states, scan, and clock
RViz can visualize the result
```

After Days 81-85, the project also proves:

```txt
the system is ready to discuss Nav2 architecture
the system is ready to discuss state estimation and EKF concepts
the system can simulate noisy odometry measurements
the system can record command vs actual vs noisy feedback
the system can generate quantitative validation metrics
the system can produce portfolio-ready plots and reports
```

This is a simulation engineering step because it moves the project from “the robot moves” to “the robot behavior can be measured and validated.”

---

## 34. Diagnostics Layer

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

This turns simulator health into a ROS 2 topic instead of only terminal logs.

---

## 35. Performance Timing

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

## 36. Data Recording and Replay

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

For Days 84-85, validation data is stored as CSV and plotted using Python:

```txt
data/day84_trajectory_validation.csv
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

Raw rosbag2 data and large raw CSV files should generally not be committed unless intentionally needed.

---

## 37. Launch Regression Layer

Day 68 adds a launch regression layer around the ROS 2 simulator architecture.

Regression script:

```txt
scripts/day68_launch_regression.sh
```

This script validates that the original ROS 2 kinematic simulator stack still works after changes.

What the regression layer checks:

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

Run command:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

The regression script acts as a repeatable system-level validation gate before committing.

---

## 38. Build Commands

### 38.1 Build Standalone C++ Project

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/standalone_cpp"
rm -rf build
mkdir build
cd build
cmake ..
cmake --build .
./robotics_sim
```

### 38.2 Build ROS 2 Project

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Verify Python validation scripts are installed:

```bash
ros2 pkg executables cpp_robotics_sim_ros | grep -E "noisy|trajectory"
```

Expected:

```txt
cpp_robotics_sim_ros noisy_odom_node.py
cpp_robotics_sim_ros trajectory_validation_recorder.py
cpp_robotics_sim_ros plot_trajectory_validation.py
```

---

## 39. Launch Commands

Launch original simulator:

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

Launch Gazebo control, diff-drive, and lidar stack:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

---

## 40. Core Verification Commands

Check simulator topics:

```bash
ros2 topic list
```

Check custom simulator pose:

```bash
ros2 topic echo --once /robot_pose
```

Check custom simulator odometry:

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

Send custom simulator command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Check robot description:

```bash
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt
grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt
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
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Check Gazebo control:

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

Check Gazebo controller odometry:

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

Check lidar sensor:

```bash
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Check simulation time:

```bash
ros2 topic echo /clock --once
```

Check noisy odometry:

```bash
ros2 topic echo /odom_noisy --once
ros2 topic echo /odom_noisy --once | grep -A 40 "covariance"
```

Run launch regression:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

---

## 41. Trajectory Validation Workflow

### 41.1 Launch Gazebo Control Stack

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

### 41.2 Run Noisy Odometry Node

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run cpp_robotics_sim_ros noisy_odom_node.py
```

### 41.3 Run Trajectory Recorder

Run from repository root:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run cpp_robotics_sim_ros trajectory_validation_recorder.py
```

### 41.4 Command Robot Motion

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

### 41.5 Verify CSV

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

### 41.6 Generate Plot and Report

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
python3 ros2_ws/src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py --csv data/day84_trajectory_validation.csv --plot plots/trajectory_validation.png --report docs/trajectory_validation_report.md
```

Verify outputs:

```bash
ls plots/trajectory_validation.png
ls docs/trajectory_validation_report.md
ls -lh plots/trajectory_validation.png

grep -n "actual path length" docs/trajectory_validation_report.md
grep -n "mean position noise error" docs/trajectory_validation_report.md
grep -n "max actual linear velocity" docs/trajectory_validation_report.md
grep -n "max actual yaw rate" docs/trajectory_validation_report.md
```

---

## 42. Validation and Regression Coverage

The project is validated using repeatable checks:

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
ros2_control validation
controller_manager validation
joint_state_broadcaster validation
diff_drive_controller validation
Gazebo driving validation
LaserScan /scan validation
simulation time validation
RViz/Gazebo synchronization validation
noisy odometry publishing
covariance validation
trajectory CSV validation
trajectory plot/report validation
```

These tests are documented in:

```txt
docs/debugging_and_validation.md
```

---

## 43. Relationship Between Modules

The project is intentionally separated:

```txt
Manipulator module:
  joint-space state update

Differential-drive module:
  mobile robot pose and trajectory update

ROS 2 simulator layer:
  standard robotics communication through topics, odometry, TF, parameters, and diagnostics

Robot description layer:
  URDF/Xacro structural robot model

Visualization layer:
  RViz TF, odometry, RobotModel, and LaserScan inspection

Gazebo layer:
  physics simulation world, robot spawn, joint motion, and sensor simulation

ros2_control layer:
  controller_manager, hardware interfaces, joint_state_broadcaster, and diff_drive_controller

Bridge layer:
  /clock and /scan conversion between Gazebo Transport and ROS 2

Autonomy concept layer:
  Nav2, localization, costmaps, planner/controller separation, EKF, covariance, uncertainty

Validation layer:
  noisy odometry, CSV recording, plotting, metrics, and Markdown report generation
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
hardware interface abstraction
controller ownership
sensor topic bridging
simulation time synchronization
measurement uncertainty
quantitative validation metrics
```

---

## 44. What This Project Demonstrates

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
* `ros2_control` hardware interface design
* `controller_manager` workflow
* `joint_state_broadcaster` integration
* `diff_drive_controller` integration
* Gazebo-driven differential-drive motion
* simulated lidar sensor modeling
* `/scan` LaserScan bridge using `ros_gz_bridge`
* simulation time and `/clock` synchronization
* RViz/Gazebo debugging
* Nav2 architecture understanding
* state estimation and EKF concepts
* odometry drift and covariance interpretation
* controlled Gaussian odometry noise
* noisy odometry publishing on `/odom_noisy`
* command vs actual vs noisy trajectory recording
* CSV-based validation workflow
* trajectory validation plotting
* Markdown validation report generation
* path length, final pose, velocity, yaw rate, and noise-error metrics
* portfolio-ready simulation validation evidence

---

## 45. Current Limitations

Current limitations after Day 85:

```txt
The manipulator module does not yet publish ROS 2 /joint_states.
The manipulator module does not yet include forward kinematics.
The original ROS 2 kinematic sim_node and the Gazebo physics robot are separate runtime stacks.
The project does not yet include full Nav2 bringup.
The project does not yet include SLAM Toolbox mapping.
The project does not yet include AMCL map-based localization.
The project does not yet include a full robot_localization EKF configuration.
The lidar exists, but Nav2 costmaps and SLAM are not yet consuming /scan.
The project has controlled odometry noise, but no full sensor fusion pipeline yet.
Automated unit tests and CI are not yet added.
```

Resolved through Day 85:

```txt
Gazebo robot spawning is complete.
ros2_control integration is complete at the foundation level.
diff_drive_controller drives the Gazebo robot.
Gazebo lidar sensor simulation is added.
/scan is bridged into ROS.
RViz can visualize robot model, odometry, TF, and LaserScan with sim time.
Nav2 architecture notes are added.
State estimation and EKF notes are added.
Controlled noisy odometry is added on /odom_noisy.
Trajectory validation recording is added.
Validation plotting is added.
A trajectory validation report is generated.
```

---

## 46. Future Work

Planned future work:

```txt
Add Nav2 bringup/configuration
Use /scan for Nav2 costmaps
Add mapping with SLAM Toolbox
Save and load maps
Add AMCL localization
Add robot_localization EKF configuration
Fuse odometry and IMU-style data
Add more realistic sensor noise models
Add rosbag-based validation workflows
Add automated unit tests
Add CI
Add final portfolio screenshots, plots, and demo video/GIF
```

---

## 47. Day 85 Interview Summary

I built a modular C++ robotics simulation foundation with standalone differential-drive and manipulator modules, then integrated the mobile robot simulator into ROS 2 using `/cmd_vel`, `/robot_pose`, `/odom`, TF, and `/diagnostics`.

I extended the project into a robot modeling and simulation stack with URDF, Xacro, `robot_state_publisher`, joint state publishing, RViz RobotModel visualization, Gazebo spawning, `ros2_control` hardware interfaces, `controller_manager`, `joint_state_broadcaster`, `diff_drive_controller`, Gazebo-driven wheel motion, simulated lidar, `/scan` bridging through `ros_gz_bridge`, and simulation-time synchronization through `/clock`.

The project now has two clearly separated stacks. In the custom kinematic simulator stack, `sim_node` owns `odom -> base_link` and publishes custom odometry, TF, pose, and diagnostics. In the Gazebo control stack, `diff_drive_controller` owns `odom -> base_link`, `joint_state_broadcaster` owns `/joint_states`, `robot_state_publisher` owns the robot link transforms below `base_link`, and Gazebo motion is driven through `ros2_control` and `gz_ros2_control`.

For autonomy readiness, I added Nav2 architecture notes covering `map -> odom -> base_link`, global and local costmaps, planner/controller separation, recovery behaviors, and lifecycle nodes. I also added state estimation notes covering odometry drift, IMU contribution, sensor fusion, EKF prediction/correction, covariance, and simulation noise.

For validation readiness, I added a noisy odometry node that subscribes to `/diff_drive_controller/odom`, adds controlled Gaussian noise to position, yaw, linear velocity, and angular velocity, fills covariance, and republishes the result on `/odom_noisy`. I then added a trajectory validation recorder that records `/diff_drive_controller/cmd_vel`, `/diff_drive_controller/odom`, and `/odom_noisy` to CSV. Finally, I added a plotting/report script that generates a portfolio-ready trajectory validation plot and report with path length, final pose, mean/max position noise error, mean/max yaw noise error, max velocity, and max yaw rate.

This demonstrates not just that the robot moves in simulation, but that the simulated behavior can be measured, validated, visualized, and explained in an interview-ready engineering workflow.
