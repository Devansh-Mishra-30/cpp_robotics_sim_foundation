# System Architecture — C++ / ROS 2 Robotics Simulation Foundation

## Document Purpose

This document is the consolidated system architecture reference for `cpp_robotics_sim_foundation`.

It describes how the project is organized as a robotics simulation engineering stack:

- standalone C++ simulation foundation
- ROS 2 kinematic simulator
- URDF/Xacro robot description
- RViz visualization
- Gazebo Sim world and robot spawn
- `ros2_control` + `diff_drive_controller`
- simulated lidar and ROS-Gazebo bridges
- noisy odometry and trajectory validation tools
- GoogleTest, CI, and performance benchmarking
- Nav2 odom-frame navigation stack
- lifecycle, costmap, planner, controller, recovery, waypoint, and rosbag validation

The current release is a consolidation checkpoint focused on making the project understandable, reproducible, and easy to review.

---

## 1. Project Identity

`cpp_robotics_sim_foundation` is a progressive robotics simulation project that starts from low-level C++ simulation and grows into a ROS 2 / Gazebo / Nav2 mobile robot simulation stack.

The project demonstrates:

```txt
C++ simulation fundamentals
ROS 2 node architecture
topics, parameters, launch files, QoS, diagnostics
odometry and TF
URDF/Xacro robot modeling
RViz visualization
Gazebo Sim physics simulation
ros2_control and diff_drive_controller
simulated LaserScan sensing
ROS-Gazebo bridging
noisy odometry generation
trajectory validation and plotting
GoogleTest unit testing
GitHub Actions CI
performance benchmarking
Nav2 lifecycle/costmap/planner/controller validation
goal navigation, recovery behavior, waypoint navigation, and rosbag evidence
```

The project is intentionally built as an engineering artifact, not only a tutorial. Every major subsystem has runtime commands, validation checks, and documentation.

---

## 2. Documentation Architecture

The documentation is consolidated into four main files:

```txt
docs/
  system_architecture.md          # what the system is and how the layers connect
  topic_interface_reference.md    # topics, actions, services, frames, params, files
  debugging_and_validation.md     # build/debug/test/validation workflow and failure modes
  daily_documentation.md          # chronological day-by-day progress record
```

Supporting utilities live outside `docs/`:

```txt
scripts/
  hard_reset.sh                   # kills stale ROS/Gazebo/RViz/controller processes
  launch_regression.sh      # original kinematic simulator launch regression
```

Documentation policy:

```txt
Architecture content        -> system_architecture.md
Topic/action/interface data -> topic_interface_reference.md
Debug/test/validation data  -> debugging_and_validation.md
Chronological day notes     -> daily_documentation.md
Executable scripts          -> scripts/
Obsolete duplicate docs     -> delete after useful content is merged
```

---

## 3. Corrected Repository Structure

Target public-facing structure:

```txt
cpp_robotics_sim_foundation/
├── .github/
│   └── workflows/
│       └── ros2_jazzy_ci.yml
│
├── data/
│   └── .gitkeep
│
├── docs/
│   ├── daily_documentation.md
│   ├── debugging_and_validation.md
│   ├── system_architecture.md
│   └── topic_interface_reference.md
│
├── plots/
│   ├── .gitkeep
│   └── trajectory_validation.png
│
├── scripts/
│   ├── launch_regression.sh
│   └── hard_reset.sh
│
├── ros2_ws/
│   └── src/cpp_robotics_sim_ros/
│       ├── config/
│       │   ├── nav2_params.yaml
│       │   ├── ros2_control.yaml
│       │   └── sim_params.yaml
│       ├── include/
│       │   └── cpp_robotics_sim_ros/
│       │       └── core_math.hpp
│       ├── launch/
│       │   ├── description.launch.py
│       │   ├── gazebo_spawn.launch.py
│       │   ├── nav2_navigation.launch.py
│       │   ├── robot_model_viz.launch.py
│       │   ├── ros2_control.launch.py
│       │   └── sim.launch.py
│       ├── rviz/
│       │   ├── diffbot_robot_model.rviz
│       │   └── sim_debug.rviz
│       ├── scripts/
│       │   ├── cmd_vel_twist_bridge.py
│       │   ├── nav2_costmap_check.sh
│       │   ├── nav2_lifecycle_check.sh
│       │   ├── nav2_planner_controller_check.sh
│       │   ├── noisy_odom_node.py
│       │   ├── plot_trajectory_validation.py
│       │   └── trajectory_validation_recorder.py
│       ├── src/
│       │   ├── performance_benchmark.cpp
│       │   └── sim_node.cpp
│       ├── test/
│       │   └── test_core_math.cpp
│       ├── urdf/
│       │   └── diffbot.urdf
│       ├── worlds/
│       │   └── empty_diffbot_world.sdf
│       ├── xacro/
│       │   └── diffbot.xacro
│       ├── CMakeLists.txt
│       └── package.xml
│
├── standalone_cpp/
│   ├── include/
│   ├── src/
│   └── CMakeLists.txt
│
├── README.md
└── .gitignore
```

Generated and local-only artifacts should not be committed unless intentionally selected:

```txt
build/
install/
log/
bags/
*.mcap
*.db3
large CSV outputs
```

---

## 4. System Layer Overview

The project has five major layers.

```txt
Layer 1: Standalone C++ simulation foundation
Layer 2: ROS 2 kinematic simulator
Layer 3: Robot model + Gazebo + ros2_control
Layer 4: Validation, testing, CI, benchmark, and evidence tooling
Layer 5: Nav2 navigation stack
```

High-level view:

```txt
standalone_cpp/
  -> deterministic C++ simulation concepts

ros2_ws/src/cpp_robotics_sim_ros/
  -> ROS 2 nodes, robot model, Gazebo launch, controllers, sensors, Nav2, tests

scripts/
  -> repo-level reset and regression utilities

docs/
  -> architecture, interfaces, debugging/validation, daily timeline
```

---

## 5. Layer 1 — Standalone C++ Simulation Foundation

The standalone C++ layer exists to isolate robotics math and simulation logic from ROS 2 middleware.

Folder:

```txt
standalone_cpp/
```

It includes:

```txt
differential-drive mobile robot simulation
manipulator joint-state simulation
simulation loops
pose integration
trajectory logging
trajectory metrics
validation checks
modular headers and sources
CMake build
```

This layer teaches and validates:

```txt
C++ syntax precision
header/source separation
state containers
pass-by-reference updates
deterministic simulation loops
kinematic modeling
trajectory analysis
small-scale validation
```

The standalone executable is conceptually:

```txt
robotics_sim
```

This layer does not publish ROS topics and does not interact with Gazebo.

---

## 6. Layer 2 — ROS 2 Kinematic Simulator

The original ROS 2 simulator is a C++ `rclcpp` node.

Node:

```txt
/sim_node
```

Executable:

```txt
sim_node
```

Launch:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Runtime flow:

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

Responsibilities:

```txt
subscribe to /cmd_vel
store latest velocity command
clamp unsafe commands
apply command timeout
integrate planar pose
publish geometry_msgs/Pose2D on /robot_pose
publish nav_msgs/Odometry on /odom
broadcast odom -> base_link
publish diagnostics
measure timer callback performance
```

This stack is useful for learning ROS 2 concepts without Gazebo physics.

---

## 7. Kinematic Simulator Math

The kinematic simulator uses planar unicycle-style motion.

State:

```txt
x, y, theta
```

Command:

```txt
v = linear.x
w = angular.z
```

Update:

```txt
theta = theta + w * dt
x     = x + v * cos(theta) * dt
y     = y + v * sin(theta) * dt
```

Heading normalization:

```cpp
theta = atan2(sin(theta), cos(theta));
```

Yaw quaternion for odometry and TF:

```cpp
q.x = 0.0;
q.y = 0.0;
q.z = sin(theta / 2.0);
q.w = cos(theta / 2.0);
```

The simulator publishes:

```txt
/odom
header.frame_id = odom
child_frame_id  = base_link
```

---

## 8. Kinematic Simulator Safety and Diagnostics

Safety features:

```txt
velocity command clamping
command timeout
parameter validation
diagnostic status publishing
callback timing measurement
```

Important parameters:

```txt
dt
initial_x
initial_y
initial_theta
cmd_timeout
max_linear_velocity
max_angular_velocity
```

Configuration path:

```txt
config/sim_params.yaml
```

Launch override example:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py   initial_x:=2.0   initial_y:=1.0   initial_theta:=0.5   dt:=0.05   cmd_timeout:=1.0   max_linear_velocity:=0.2   max_angular_velocity:=0.4
```

Parameter precedence for exposed parameters:

```txt
terminal override > launch argument default > YAML > C++ default
```

Diagnostics topic:

```txt
/diagnostics
diagnostic_msgs/msg/DiagnosticArray
```

Diagnostics report:

```txt
dt
cmd_timeout
time_since_cmd
timeout_active
current command
velocity limits
current pose
callback time
average callback time
max callback time
timing budget
callback count
```

---

## 9. Robot Description Layer

The robot is modeled as a differential-drive robot.

Reference URDF:

```txt
urdf/diffbot.urdf
```

Maintainable robot model:

```txt
xacro/diffbot.xacro
```

Primary links:

```txt
base_link
left_wheel_link
right_wheel_link
caster_link
lidar_link
```

Primary joints:

```txt
left_wheel_joint   continuous
right_wheel_joint  continuous
caster_joint       fixed
lidar_joint        fixed
```

Xacro is used because it supports reusable properties and macros for:

```txt
chassis dimensions
wheel radius
wheel width
wheel separation
caster dimensions
lidar dimensions
masses
inertia blocks
wheel link generation
ros2_control interface declaration
Gazebo sensor declaration
```

Robot description flow:

```txt
diffbot.xacro
  ↓
xacro command in launch
  ↓
robot_description parameter
  ↓
robot_state_publisher
  ↓
/robot_description
/tf
/tf_static
```

---

## 10. Robot State and Joint State Publishing

Two joint-state mechanisms exist in the project.

### Visualization-only stack

```txt
joint_state_publisher
  ↓
/joint_states
  ↓
robot_state_publisher
  ↓
base_link -> wheel link transforms
```

This is used for RViz robot model visualization without Gazebo control.

### Gazebo ros2_control stack

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
  ↓
robot_state_publisher
```

This is the correct joint state owner when Gazebo and `ros2_control` are active.

---

## 11. Gazebo Simulation Layer

World file:

```txt
worlds/empty_diffbot_world.sdf
```

Gazebo launch files:

```txt
gazebo_spawn.launch.py
ros2_control.launch.py
nav2_navigation.launch.py
```

The world contains:

```txt
physics system
user commands system
scene broadcaster system
sensors system
sun light
ground plane
static lidar obstacle boxes
```

Static obstacle boxes:

```txt
scan_box_front:
  center = (2.0, 0.0, 0.5)
  size   = (0.4, 1.0, 1.0)
  footprint approx:
    x = 1.8 to 2.2
    y = -0.5 to 0.5

scan_box_left:
  center = (0.0, 2.0, 0.5)
  size   = (1.0, 0.4, 1.0)
  footprint approx:
    x = -0.5 to 0.5
    y = 1.8 to 2.2
```

Gazebo spawn flow:

```txt
empty_diffbot_world.sdf
  ↓
Gazebo Sim starts
  ↓
robot_description is published from Xacro
  ↓
ros_gz_sim create spawns diffbot
  ↓
diffbot appears in Gazebo
```

Important distinction:

```txt
Gazebo simulates physics, joints, contact, obstacles, and sensors.
RViz visualizes ROS topics and TF.
RViz does not simulate physics and does not add real obstacles.
```

---

## 12. ros2_control and Gazebo Hardware Interface

The robot Xacro declares a `ros2_control` system using the Gazebo simulated hardware backend.

Each wheel joint exposes:

```txt
command interface: velocity
state interface: position
state interface: velocity
```

Architecture:

```txt
diffbot.xacro ros2_control block
  ↓
generated robot_description
  ↓
gz_ros2_control plugin
  ↓
controller_manager
  ↓
controllers operate on simulated wheel hardware interfaces
```

`ros2_control` separates controller logic from the hardware/simulator backend. In this project, Gazebo is the simulated hardware.

---

## 13. controller_manager and Controllers

`controller_manager` is created by the `gz_ros2_control` Gazebo plugin.

It is responsible for:

```txt
loading controllers
configuring controllers
activating controllers
connecting controllers to hardware interfaces
exposing controller state through ros2 control CLI
```

Expected active controllers:

```txt
joint_state_broadcaster
diff_drive_controller
```

Validation:

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

---

## 14. Differential-Drive Controller Layer

The Gazebo-driven robot is moved by `diff_drive_controller`.

Input topic:

```txt
/diff_drive_controller/cmd_vel
geometry_msgs/msg/TwistStamped
```

Output topics:

```txt
/diff_drive_controller/odom
/diff_drive_controller/cmd_vel_out
/tf
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
Gazebo wheel joints
  ↓
robot moves in Gazebo
  ↓
/diff_drive_controller/odom
/tf odom -> base_link
```

Differential-drive math used internally by the controller:

```txt
v     = r / 2 * (wr + wl)
omega = r / L * (wr - wl)

wr = (v + omega * L / 2) / r
wl = (v - omega * L / 2) / r
```

Where:

```txt
v      = body forward velocity
omega  = yaw velocity
r      = wheel radius
L      = wheel separation
wr     = right wheel angular velocity
wl     = left wheel angular velocity
```

---

## 15. Simulated Lidar and ROS-Gazebo Bridge

The robot has a simulated 2D lidar attached to:

```txt
lidar_link
```

Sensor type:

```txt
Gazebo gpu_lidar
```

Gazebo-to-ROS bridge flow:

```txt
Gazebo gpu_lidar sensor
  ↓
Gazebo /scan
  ↓
ros_gz_bridge parameter_bridge
  ↓
ROS 2 /scan
  ↓
sensor_msgs/msg/LaserScan
```

The bridge also exposes simulation time:

```txt
Gazebo /clock
  ↓
ros_gz_bridge
  ↓
ROS 2 /clock
```

RViz and ROS nodes that visualize Gazebo-driven data must use simulation time:

```txt
use_sim_time: true
```

If wall time and sim time are mixed, RViz may show stale TF warnings.

---

## 16. Transform Ownership

Transform ownership depends on which stack is running.

### Kinematic simulator stack

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

### Gazebo / ros2_control / Nav2 stack

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
Do not run sim_node and diff_drive_controller as simultaneous publishers of odom -> base_link.
```

Expected frame tree:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

A Gazebo scan frame issue was observed where `/scan` used a Gazebo-generated frame name. The fix was to add the required static transform so the scan frame connects into the TF tree.

---

## 17. RViz Visualization Layer

Saved RViz configs:

```txt
rviz/sim_debug.rviz
rviz/diffbot_robot_model.rviz
```

For Gazebo/Nav2 workflows, RViz should use:

```txt
Fixed Frame: odom
use_sim_time: true
```

Important displays:

```txt
Grid
TF
RobotModel
Odometry
LaserScan
Global Costmap
Local Costmap
Global Plan
Local Plan
```

RViz can send goals through the goal tool, but it does not create real obstacles. Real obstacles must be in Gazebo/SDF.

---

## 18. Validation and Measurement Layer

The project includes a measurement layer for simulation evidence.

### Noisy odometry

```txt
/diff_drive_controller/odom
  ↓
noisy_odom_node.py
  ↓
/odom_noisy
```

Purpose:

```txt
controlled measurement noise
covariance fields
state-estimation readiness
Sim2Real-style robustness preparation
```

### Trajectory validation

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
```

Validation proves the system is:

```txt
commandable
measurable
recordable
plotable
explainable
repeatable
```

---

## 19. GoogleTest Unit Testing Layer

Deterministic C++ unit tests validate the core math layer.

Files:

```txt
include/cpp_robotics_sim_ros/core_math.hpp
test/test_core_math.cpp
```

Tested functions:

```txt
clamp()
wrapToPi()
integratePose()
```

Current unit test baseline:

```txt
17 tests
0 errors
0 failures
0 skipped
```

Purpose:

```txt
GoogleTest verifies deterministic C++ math.
It does not replace Gazebo, launch, sensor, controller, or Nav2 runtime tests.
```

---

## 20. GitHub Actions CI Layer

CI workflow:

```txt
.github/workflows/ros2_jazzy_ci.yml
```

CI validates:

```txt
repository checkout
ROS 2 Jazzy dependency installation
rosdep dependency installation
colcon build
GoogleTest execution
test log artifact upload
```

CI currently does not run full Gazebo/Nav2 scenarios because those are runtime simulation checks, not simple unit tests.

CI role:

```txt
remote build/test gate for code correctness
```

---

## 21. Performance Benchmarking Layer

A deterministic C++ benchmark measures the core update layer.

Executable:

```txt
performance_benchmark
```

Benchmark measures:

```txt
deterministic pose integration timing
multiple dt values
virtual robot updates
wall-clock time
estimated real-time factor
```

Reported baseline:

```txt
dt=0.1    RTF ≈ 5684.98
dt=0.01   RTF ≈ 574.99
dt=0.001  RTF ≈ 57.23
```

Scope limitation:

```txt
This benchmark does not include Gazebo physics, rendering, ROS middleware, TF, sensors, rosbag, RViz, or Nav2.
```

---

## 22. Nav2 Integration Layer — Days 91-100

Days 91-100 added the first working Nav2 navigation phase.

Primary launch:

```txt
launch/nav2_navigation.launch.py
```

Primary parameters:

```txt
config/nav2_params.yaml
```

Primary validation scripts:

```txt
scripts/nav2_lifecycle_check.sh
scripts/nav2_costmap_check.sh
scripts/nav2_planner_controller_check.sh
```

Primary bridge:

```txt
scripts/cmd_vel_twist_bridge.py
```

Nav2 phase scope:

```txt
odom-frame navigation only
no SLAM yet
no saved map yet
no AMCL yet
no EKF active in Nav2 loop yet
```

The goal of this phase is to prove:

```txt
Nav2 launches
lifecycle nodes activate
local and global costmaps publish
planner can compute paths
controller can follow paths
Nav2 commands reach the Gazebo diff-drive controller
robot reaches goals in Gazebo/RViz
recovery/failure behavior is observable
waypoint navigation works
rosbag evidence is recorded and replayable
```

---

## 23. Nav2 Runtime Architecture

Nav2 command flow:

```txt
NavigateToPose / NavigateThroughPoses action
  ↓
bt_navigator
  ↓
planner_server
  ↓
/plan
  ↓
controller_server
  ↓
/cmd_vel_nav
  ↓
velocity_smoother
  ↓
/cmd_vel
  ↓
cmd_vel_twist_bridge.py
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
  ↓
robot moves
  ↓
/diff_drive_controller/odom
/tf
```

Sensor/costmap flow:

```txt
Gazebo obstacles
  ↓
Gazebo lidar
  ↓
ros_gz_bridge
  ↓
/scan
  ↓
Nav2 obstacle layers
  ↓
/local_costmap/costmap
/global_costmap/costmap
```

Planning and feedback flow:

```txt
/diff_drive_controller/odom
/tf
/scan
/costmaps
  ↓
Nav2 planner/controller/behavior tree
  ↓
path, local plan, recoveries, velocity commands
```

---

## 24. Why `cmd_vel_twist_bridge.py` Exists

Nav2 publishes:

```txt
/cmd_vel
geometry_msgs/msg/Twist
```

The Gazebo diff-drive controller expects:

```txt
/diff_drive_controller/cmd_vel
geometry_msgs/msg/TwistStamped
```

The bridge converts between them:

```txt
/cmd_vel Twist
  ↓
cmd_vel_twist_bridge.py
  ↓
/diff_drive_controller/cmd_vel TwistStamped
```

This allows Nav2 to control the Gazebo robot without changing the controller interface.

---

## 25. Nav2 Lifecycle Architecture

Nav2 uses lifecycle-managed nodes. Important nodes:

```txt
/lifecycle_manager_navigation
/controller_server
/smoother_server
/planner_server
/behavior_server
/velocity_smoother
/bt_navigator
/waypoint_follower
/local_costmap/local_costmap
/global_costmap/global_costmap
```

Lifecycle pass state:

```txt
active [3]
```

Lifecycle validation confirmed that the main Nav2 nodes become active and expose navigation actions.

The project includes a lifecycle validation script:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
```

---

## 26. Nav2 Costmap Architecture

The Nav2 phase currently uses odom-frame costmaps.

Expected costmap frames:

```txt
local_costmap.global_frame  = odom
local_costmap.robot_base_frame = base_link

global_costmap.global_frame = odom
global_costmap.robot_base_frame = base_link
```

Core topics:

```txt
/scan
/local_costmap/costmap
/global_costmap/costmap
/local_costmap/published_footprint
/global_costmap/published_footprint
```

Costmap validation confirmed:

```txt
/scan publishes
local costmap publishes
global costmap publishes
odom -> base_link TF exists
costmap frames are odom/base_link
RViz shows local/global costmaps
```

Validation script:

```bash
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
```

---

## 27. Nav2 Planner and Controller Architecture

Core actions:

```txt
/compute_path_to_pose
/follow_path
/navigate_to_pose
/navigate_through_poses
```

Planner and controller validation confirmed:

```txt
planner_server active
controller_server active
/compute_path_to_pose exists
/follow_path exists
/navigate_to_pose exists
planner computes odom-frame path
controller parameters are readable and conservative
robot can move from a Nav2 action command
```

Planner validation command:

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{...}"
```

Controller parameter baseline:

```txt
controller_frequency = 10.0
FollowPath.max_vel_x = 0.25
FollowPath.max_vel_theta = 0.6
FollowPath.acc_lim_x = 0.5
FollowPath.acc_lim_theta = 1.0
FollowPath.sim_time = 1.5
FollowPath.vx_samples = 20
FollowPath.vtheta_samples = 20
```

Validation script:

```bash
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

---

## 28. Goal Navigation Architecture

Closed-loop goal navigation was validated.

Goal command path:

```txt
/navigate_to_pose action
  ↓
bt_navigator
  ↓
planner_server
  ↓
controller_server
  ↓
velocity_smoother
  ↓
/cmd_vel
  ↓
cmd_vel_twist_bridge.py
  ↓
/diff_drive_controller/cmd_vel
  ↓
robot motion in Gazebo
```

Observed result:

```txt
Nav2 goal accepted
path appeared in RViz
/cmd_vel published
/diff_drive_controller/cmd_vel received TwistStamped commands
/diff_drive_controller/odom changed
robot moved in Gazebo
robot reached goal in Gazebo/RViz
```

RViz goal behavior:

```txt
RViz 2D Goal Pose / Nav2 Goal publishes goal intent.
CLI NavigateToPose action also works and is useful for repeatable tests.
```

---

## 29. Recovery and Failure Behavior Architecture

Three failure and recovery conditions were tested using fixed SDF obstacles.

Test 1 — goal inside front obstacle:

```txt
goal = (2.0, 0.0)
result = ABORTED
error_code = 105
number_of_recoveries = 18
behavior = repeated recovery/oscillation, stack survived
```

Test 2 — goal behind obstacle:

```txt
goal = (2.8, 0.0)
result = SUCCEEDED
error_code = 0
number_of_recoveries = 8
behavior = side route around obstacle, reached goal
```

Test 3 — goal outside practical costmap region:

```txt
goal = (20.0, 20.0)
result = ABORTED
error_code = 204
number_of_recoveries = 0
behavior = immediate clean abort, no robot drive attempt
```

Interpretation:

```txt
Nav2 does not silently crash on bad goals.
It either attempts recovery or aborts cleanly depending on the failure mode.
```

---

## 30. Waypoint Navigation Architecture

Multi-goal missions were tested using:

```txt
/navigate_through_poses
nav2_msgs/action/NavigateThroughPoses
```

Mission results:

```txt
easy positive-x mission             -> SUCCEEDED
mirrored negative-x mission         -> SUCCEEDED
obstacle-side harder waypoint route -> SUCCEEDED after recoveries
```

Important feedback fields:

```txt
number_of_poses_remaining
number_of_recoveries
distance_remaining
```

The robot was validated against sequential goals rather than only a single goal.

---

## 31. rosbag2 Evidence Architecture

A replayable Nav2 evidence dataset was recorded.

Bag path:

```txt
bags/day98_nav2_goal_evidence/goal_run_01
```

Storage:

```txt
MCAP
```

Bag summary:

```txt
Size: 3.4 MiB
Duration: 31.118688884 s
Messages: 6809
```

Important recorded topics:

```txt
/behavior_tree_log
/cmd_vel
/cmd_vel_nav
/cmd_vel_smoothed
/diff_drive_controller/cmd_vel
/diff_drive_controller/cmd_vel_out
/diff_drive_controller/odom
/global_costmap/costmap
/global_costmap/published_footprint
/local_costmap/costmap
/local_costmap/published_footprint
/local_plan
/plan
/received_global_plan
/scan
/tf
/tf_static
/transformed_global_plan
```

Replay:

```bash
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock
```

Important note:

```txt
The goal was sent through the /navigate_to_pose action, so /goal_pose did not appear in the final bag.
That is acceptable because the bag contains command, odometry, TF, scan, costmap, plan, and behavior-tree evidence.
```

Bag data should remain local and ignored by git.

---

## 32. Nav2 Debugging Architecture

A repeatable Nav2 debugging workflow was consolidated.

Main debug categories:

```txt
lifecycle state
action server availability
costmap topics and frames
scan topic and scan frame
TF tree
cmd_vel bridge
planner action
controller parameters
goal feedback
recovery behavior
waypoint feedback
rosbag evidence
ROS log search
```

Most important diagnostic commands:

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator

ros2 action list -t | sort

ros2 topic echo --once /scan --field header
ros2 run tf2_ros tf2_echo odom base_link

ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
ros2 topic echo /diff_drive_controller/odom --field pose.pose.position
```

Known non-blocking warning:

```txt
RTPS_TRANSPORT_SHM Error Failed init_port fastrtps_port7005: open_and_lock_file failed -> Function open_port_internal
```

Current status:

```txt
Non-blocking. It has not prevented lifecycle checks, costmaps, actions, planning, navigation, waypoints, or rosbag recording.
```

---

## 33. Hard Reset Utility

The project uses a hard reset script to kill stale simulator processes before clean launches.

Corrected location:

```txt
scripts/hard_reset.sh
```

Usage:

```bash
./scripts/hard_reset.sh
```

The script belongs in `scripts/`, not `docs/`, because it is an executable utility.

This script is used before major runtime tests to prevent stale Gazebo, RViz, controller, bridge, or Nav2 nodes from interfering with fresh validation.

---

## 34. Standard Launch and Validation Flow

Clean reset:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

./scripts/hard_reset.sh
```

Build:

```bash
source /opt/ros/jazzy/setup.bash
rm -rf build install log
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Launch Nav2 stack:

```bash
ros2 launch cpp_robotics_sim_ros nav2_navigation.launch.py
```

Run validation:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

Expected:

```txt
LIFECYCLE CHECK: PASS
COSTMAP CHECK: PASS
PLANNER/CONTROLLER CHECK: PASS
```

---

## 35. Current Capability

The project can:

```txt
build standalone C++ simulation components
build ROS 2 Jazzy workspace
run deterministic C++ GoogleTests
run GitHub Actions CI
spawn a differential-drive robot in Gazebo
drive the robot through ros2_control
publish odom, TF, joint states, scan, and clock
visualize robot, odom, TF, scan, and costmaps in RViz
bridge Nav2 /cmd_vel into diff_drive_controller TwistStamped commands
activate Nav2 lifecycle nodes
publish local and global costmaps
compute odom-frame paths
execute NavigateToPose goals
execute NavigateThroughPoses waypoint missions
observe and document recovery/failure behavior
record and replay rosbag2 MCAP evidence
```

Current scope limitations:

```txt
navigation is odom-frame only
no SLAM yet
no saved map yet
no AMCL localization yet
EKF is conceptually prepared but not active in the Nav2 loop
no Docker packaging yet
no public one-command play mode yet
```

---

## 36. System Architecture Summary

The current core system is:

```txt
Gazebo world + obstacles
  ↓
Gazebo diffbot model from Xacro
  ↓
gz_ros2_control
  ↓
controller_manager
  ↓
joint_state_broadcaster + diff_drive_controller
  ↓
/diff_drive_controller/odom + /tf + /joint_states

Gazebo lidar
  ↓
ros_gz_bridge
  ↓
/scan
  ↓
Nav2 costmaps

Nav2 lifecycle nodes
  ↓
planner_server + controller_server + behavior_server + bt_navigator
  ↓
/cmd_vel
  ↓
cmd_vel_twist_bridge.py
  ↓
/diff_drive_controller/cmd_vel
  ↓
Gazebo robot motion

Validation layer
  ↓
lifecycle/costmap/planner-controller scripts
  ↓
goal, recovery, waypoint tests
  ↓
rosbag2 evidence
  ↓
documentation
```

---

## 37. Interview-Level Explanation

This project began as a standalone C++ robotics simulation foundation and evolved into a ROS 2 / Gazebo / Nav2 mobile robot simulation stack.

The standalone C++ layer validates core simulation logic such as pose integration, command clamping, and trajectory metrics. The ROS 2 kinematic simulator adds topics, parameters, odometry, TF, diagnostics, launch files, QoS, RViz, and rosbag workflows. The robot modeling phase adds URDF/Xacro, `robot_state_publisher`, joint state workflows, Gazebo spawning, `ros2_control`, `controller_manager`, `diff_drive_controller`, simulated lidar, `/scan` bridging, and simulation time.

The validation layer adds noisy odometry, trajectory CSV recording, plotting, GoogleTest unit tests, GitHub Actions CI, and deterministic performance benchmarking.

The Nav2 phase connects the Gazebo robot to a working navigation stack. Nav2 publishes `/cmd_vel`, a bridge converts it to `TwistStamped`, and the diff-drive controller moves the robot in Gazebo. The stack validates lifecycle activation, costmaps, planner path generation, controller parameters, single-goal navigation, recovery behavior, waypoint navigation, and rosbag evidence.

The project is a reproducible ROS 2, Gazebo, and Nav2 mobile robot simulation foundation with SLAM, saved-map workflows, localization, Docker packaging, validation tooling, and browser-based controls.

---

## 38. Planned Architecture Direction

Recommended next phase direction:

```txt
SLAM, map persistence, and localization foundation
Release cleanup, validation, documentation, and public baseline
Dockerized runnable baseline
Public runnable simulator
Teleoperation and controller-based play mode
Scenario validation and quantitative metrics
Research-grade simulation validation testbed
```

The architecture should continue to prioritize:

```txt
reproducibility
measurable behavior
clear topic/action interfaces
clean launch commands
validation scripts
debugging documentation
runtime evidence
performance awareness
```
