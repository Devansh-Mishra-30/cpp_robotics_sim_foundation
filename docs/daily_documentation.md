# Daily Documentation — C++ / ROS 2 Robotics Simulation Foundation

This document is the chronological engineering log for the `cpp_robotics_sim_foundation` project through **Day 100**.

The project started as a standalone C++ robotics simulation foundation and grew into a ROS 2 / Gazebo mobile robot simulation stack with robot modeling, `ros2_control`, lidar simulation, validation tooling, GoogleTest, CI, performance benchmarking, Nav2 planning/control, recovery testing, waypoint navigation, and replayable rosbag2 evidence.

Day 100 consolidates the project documentation into four primary documents:

```text
README.md

docs/system_architecture.md
docs/topic_interface_reference.md
docs/debugging_and_validation.md
docs/daily_documentation.md
```

Utility scripts live outside documentation:

```text
scripts/hard_reset.sh
```

The rule from Day 100 onward is:

```text
Useful technical content goes into the four main docs.
Temporary or duplicated notes are deleted after consolidation.
Executable utilities go in scripts/.
```

---

## 1. Project Summary Through Day 100

The project currently includes:

- standalone C++ simulation modules
- differential-drive mobile robot simulation
- manipulator joint-state simulation
- ROS 2 C++ simulator integration
- `/cmd_vel`, `/robot_pose`, `/odom`, `/tf`, and `/diagnostics`
- launch files, YAML configuration, and launch arguments
- explicit QoS choices for command/state topics
- rosbag2 recording and replay workflows
- RViz visualization
- URDF and Xacro robot modeling
- `robot_state_publisher` and joint-state workflows
- Gazebo Sim spawning
- `ros2_control`, `controller_manager`, `joint_state_broadcaster`, and `diff_drive_controller`
- Gazebo-driven wheel motion
- simulated lidar with `/scan` bridge through `ros_gz_bridge`
- simulation time through `/clock`
- noisy odometry generation
- trajectory validation recording, plotting, and reporting
- GoogleTest unit tests for deterministic C++ math
- GitHub Actions CI for ROS 2 Jazzy build/test validation
- deterministic performance benchmark
- Nav2 lifecycle bringup
- Nav2 local/global costmaps
- Nav2 planner/controller validation
- Nav2 goal navigation
- Nav2 recovery/failure behavior tests
- Nav2 waypoint navigation
- Nav2 rosbag2 evidence recording
- Nav2 debugging documentation
- Day 100 documentation consolidation

---

## 2. Current Repository Documentation Policy

Only four detailed documentation files should remain in `docs/`:

```text
docs/system_architecture.md
docs/topic_interface_reference.md
docs/debugging_and_validation.md
docs/daily_documentation.md
```

### 2.1 system_architecture.md

Purpose:

```text
Explain the complete system architecture, major layers, data flow, control flow, transform ownership, validation layers, and Day 100 capabilities.
```

This file answers:

```text
What was built?
How are the components connected?
What owns motion, odometry, TF, sensing, planning, control, and validation?
What is currently supported?
What is not supported yet?
```

### 2.2 topic_interface_reference.md

Purpose:

```text
Define the runtime interface contract: topics, actions, services, frames, message types, parameters, and validation commands.
```

This file answers:

```text
What topics/actions exist?
What message types are used?
Who publishes and subscribes?
Which frames are expected?
Which CLI commands validate each interface?
```

### 2.3 debugging_and_validation.md

Purpose:

```text
Provide repeatable debugging, validation, CI, rosbag, recovery, waypoint, and failure-mode procedures.
```

This file answers:

```text
How do I debug this system?
How do I validate lifecycle, costmaps, TF, scan, controller, planner, goal navigation, waypoints, and rosbag evidence?
What common failures have already been seen?
How do I recover from them?
```

### 2.4 daily_documentation.md

Purpose:

```text
Track chronological project progress and summarize what each day added or validated.
```

This file answers:

```text
What happened each day?
What changed?
What was learned?
What was validated?
What is the current milestone status?
```

---

## 3. Phase Summary

| Phase | Days | Focus | Result |
|---|---:|---|---|
| Foundation C++ | 1–30 | simulation basics, state updates, mobile robot, manipulator, modular C++ | deterministic C++ robotics simulation base |
| ROS 2 Core | 31–60 | ROS 2 node, topics, odometry, TF, parameters, diagnostics | custom ROS 2 kinematic simulator |
| ROS 2 Tooling | 61–70 | launch, YAML, arguments, QoS, rosbag, RViz, regression, docs | repeatable ROS 2 workflow |
| Robot Modeling + Gazebo | 71–80 | URDF, Xacro, robot_state_publisher, Gazebo, ros2_control, lidar | Gazebo-controlled diff-drive robot with scan data |
| Validation + Quality | 81–90 | Nav2 concepts, state-estimation notes, noisy odom, CSV validation, GTest, CI, benchmark | measurable, testable simulation foundation |
| Nav2 Integration | 91–100 | Nav2 lifecycle, costmaps, planner/controller, goals, recovery, waypoints, rosbag, docs | working odom-frame Nav2 navigation stack |

---

# Days 1–60 — C++ and ROS 2 Foundation

## Phase 1: Days 1–10 — Core C++ Simulation Basics

Built the first C++ robotics simulation patterns from scratch:

- vectors and indexing for robot data
- pass-by-reference update functions
- clamp and angle wrapping utilities
- fixed-timestep simulation loops
- `JointState` and `Pose2D` containers
- multi-joint state storage
- single-joint and multi-joint update logic

Key lesson:

```text
C++ simulation code must be exact. Correct indexing, references, validation, and update logic matter immediately.
```

## Phase 2: Days 11–20 — Mobile Robot and Safety Foundation

Built the first mobile robot simulation layer:

- planar robot state using `x`, `y`, and `theta`
- pose integration from linear and angular velocity
- trajectory storage and reporting
- differential-drive wheel-speed to body-velocity conversion
- basic target-tracking controller
- safety guards for invalid timestep, vector size, and parameters

Key lesson:

```text
A mobile robot simulator needs state, command input, kinematics, trajectory logging, and safety validation.
```

## Phase 3: Days 21–30 — Modular C++ Project Structure

Converted early scripts into a more professional C++ project:

- header/source separation
- reusable utilities
- trajectory analysis
- scenario testing
- manipulator joint-state mini-simulation
- differential-drive mobile robot mini-simulation
- code cleanup with naming, const correctness, and references

Key lesson:

```text
A portfolio project should be modular, explainable, buildable, and testable instead of being one large script.
```

## Phase 4: Days 31–44 — C++ Robotics Software Foundation

Strengthened the standalone simulator:

- CMake-based multi-file build
- clean `include/` and `src/` layout
- class-based mobile robot simulator
- STL usage for trajectory data and metrics
- CSV trajectory logging
- differential-drive kinematics
- scenario runner
- validation tests
- target tracking

Key lesson:

```text
The standalone simulator became a deterministic robotics software artifact with kinematics, validation, metrics, and repeatable scenarios.
```

## Phase 5: Days 45–60 — ROS 2 C++ Integration and Validation

Integrated the simulator into ROS 2:

- created an `ament_cmake` ROS 2 package
- built a C++ `rclcpp` simulation node
- added `/cmd_vel` subscriber
- added `/robot_pose` publisher
- added `/odom` publisher
- added TF broadcaster for `odom -> base_link`
- added ROS 2 parameters
- added command timeout behavior
- added velocity clamping
- added parameter validation
- added performance timing using `std::chrono::steady_clock`
- documented debugging workflow
- documented regression checklist

Day 60 assessment result:

| Area | Status |
|---|---|
| Conceptual understanding | Passed |
| Project architecture understanding | Passed |
| ROS 2 topic/parameter/TF understanding | Passed |
| C++ syntax precision | Needs daily practice |
| Git/build discipline | Improving |
| Interview explanation | Improving |

Main lesson:

```text
The project moved from standalone C++ simulation into a ROS 2 robotics stack with topics, parameters, odometry, TF, validation, timing, and documentation.
```

---

# Days 61–70 — ROS 2 Tooling and Interfaces

## Day 61 — ROS 2 Launch System

Goal:

```text
Create a one-command ROS 2 launch workflow for the simulator stack.
```

Deliverable:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/launch/sim.launch.py
```

Result:

```text
The simulator can be started repeatably through ros2 launch instead of manual node execution.
```

## Day 62 — YAML Parameters

Goal:

```text
Move simulator runtime parameters into YAML configuration.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

Result:

```text
Runtime settings such as timestep, initial pose, timeout, and velocity limits are now stored in a ROS 2 YAML config file.
```

## Day 63 — Launch Arguments

Goal:

```text
Expose key simulator parameters as runtime launch arguments.
```

Example:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05
```

Result:

```text
The same launch file can run different scenarios without editing YAML or code.
```

## Day 64 — ROS 2 QoS Profiles

Goal:

```text
Make ROS 2 communication behavior explicit.
```

Implemented explicit QoS for:

```text
/cmd_vel
/robot_pose
/odom
/diagnostics
```

Design choice:

```text
Reliable + volatile + keep_last(10) for command/state/debug topics.
```

## Day 65 — rosbag2 Recording and Replay

Goal:

```text
Record and replay simulator topic data using rosbag2.
```

Recorded baseline topics:

```text
/cmd_vel
/robot_pose
/odom
/tf
```

Result:

```text
The simulator gained reproducible recorded evidence for command, pose, odometry, and TF behavior.
```

## Day 66 — RViz2 Visualization

Goal:

```text
Visualize simulator state using RViz2.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

Displays:

```text
Grid
TF
Odometry
```

Fixed frame:

```text
odom
```

## Day 67 — Diagnostics

Goal:

```text
Publish runtime health information.
```

Added:

```text
/diagnostics
```

Message type:

```text
diagnostic_msgs/msg/DiagnosticArray
```

Diagnostics report:

```text
timestep, timeout status, current command, velocity limits, current pose, callback timing, and callback count.
```

## Day 68 — Launch Regression

Goal:

```text
Create a repeatable launch regression workflow.
```

Added:

```text
scripts/day68_launch_regression.sh
```

Result:

```text
The original ROS 2 simulator stack gained an automated validation script for launch, topics, params, state outputs, TF, diagnostics, and command response.
```

## Day 69 — ROS 2 Usage Documentation

Goal:

```text
Make the simulator easier for another engineer to build, run, inspect, and validate.
```

Result:

```text
The README gained practical usage commands for build, launch, topic inspection, RViz, rosbag, and regression testing.
```

## Day 70 — Topic Interface Documentation

Goal:

```text
Create a ROS 2 topic interface reference.
```

Added:

```text
docs/topic_interface_reference.md
```

Result:

```text
The simulator gained a documented topic contract covering names, message types, direction, important fields, QoS, validation commands, and failure modes.
```

---

# Days 71–80 — Robot Modeling, Gazebo, ros2_control, and Lidar

## Day 71 — URDF Robot Model

Goal:

```text
Create a standard ROS robot description for the differential-drive robot.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

Model includes:

```text
base_link
left_wheel_link
right_wheel_link
caster_link
```

Joints:

```text
left_wheel_joint
right_wheel_joint
caster_joint
```

## Day 72 — Xacro Macros

Goal:

```text
Convert static URDF into maintainable parameterized Xacro.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

Result:

```text
Robot geometry, inertial properties, wheels, and repeated structures became parameterized and easier to maintain.
```

## Day 73 — robot_state_publisher

Goal:

```text
Launch robot_state_publisher with the generated robot description.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/launch/description.launch.py
```

Result:

```text
The Xacro-generated robot_description is published and used to produce TF below base_link.
```

Important fix:

```text
Xacro XML must be passed as a string parameter using ParameterValue(..., value_type=str).
```

## Day 74 — joint_state_publisher

Goal:

```text
Publish joint states for continuous wheel joints in the visualization-only stack.
```

Result:

```text
robot_state_publisher can publish wheel link transforms from /joint_states.
```

## Day 75 — RViz Robot Model Visualization

Goal:

```text
Display the full robot model in RViz.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/launch/robot_model_viz.launch.py
ros2_ws/src/cpp_robotics_sim_ros/rviz/diffbot_robot_model.rviz
```

Result:

```text
RViz can show RobotModel, TF, odometry, and the robot structure below base_link.
```

## Day 76 — Gazebo Spawn

Goal:

```text
Spawn the differential-drive robot model into Gazebo Sim.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
ros2_ws/src/cpp_robotics_sim_ros/launch/gazebo_spawn.launch.py
```

Result:

```text
Gazebo starts with a world and the robot spawns from /robot_description.
```

## Day 77 — ros2_control Basics

Goal:

```text
Expose wheel joints as ros2_control hardware interfaces through Gazebo.
```

Added:

```text
ros2_control block in diffbot.xacro
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
ros2_ws/src/cpp_robotics_sim_ros/launch/ros2_control.launch.py
```

Result:

```text
controller_manager and joint_state_broadcaster can connect to simulated wheel joint interfaces.
```

## Day 78 — Gazebo Differential-Drive Control

Goal:

```text
Drive the Gazebo robot using diff_drive_controller.
```

Controller input:

```text
/diff_drive_controller/cmd_vel
geometry_msgs/msg/TwistStamped
```

Controller outputs:

```text
/diff_drive_controller/odom
/diff_drive_controller/cmd_vel_out
/tf
```

Result:

```text
The robot physically moves in Gazebo using ros2_control and diff_drive_controller.
```

## Day 79 — Sensor Modeling

Goal:

```text
Add a simulated lidar and bridge it into ROS 2.
```

Added:

```text
lidar_link
gpu_lidar sensor
/scan bridge through ros_gz_bridge
```

Result:

```text
Gazebo lidar data is available in ROS as /scan and visible in RViz.
```

Important fix:

```text
RViz and Gazebo must use the same simulation time source through /clock and use_sim_time.
```

## Day 80 — Robot Modeling Review and Interview Preparation

Goal:

```text
Consolidate the full robot modeling and simulation architecture from Days 71–79.
```

System through Day 80:

```text
Xacro -> robot_description -> robot_state_publisher -> TF below base_link
Gazebo world + spawned robot -> gz_ros2_control -> controller_manager -> diff_drive_controller -> wheel motion
Gazebo lidar -> ros_gz_bridge -> /scan -> RViz
```

Key explanation:

```text
RViz visualizes ROS data. Gazebo simulates physics. ros2_control connects ROS controllers to Gazebo-simulated joints.
```

---

# Days 81–90 — Validation, Testing, CI, and Performance

## Day 81 — Nav2 Concept Architecture

Goal:

```text
Document Nav2 architecture before implementation.
```

Concepts documented:

```text
map -> odom -> base_link
planner vs controller
global costmap vs local costmap
recovery behavior
Nav2 command path to diff_drive_controller
```

Result:

```text
The project gained a conceptual bridge from robot simulation to autonomous navigation.
```

## Day 82 — State Estimation Concept Architecture

Goal:

```text
Document state estimation, covariance, odometry drift, and EKF readiness.
```

Concepts documented:

```text
state vector
motion model
prediction/correction
covariance
wheel odometry drift
sensor fusion readiness
```

## Day 83 — Noisy Odometry Node

Goal:

```text
Create a noisy odometry stream from Gazebo controller odometry.
```

Added:

```text
ros2_ws/src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
```

Flow:

```text
/diff_drive_controller/odom -> noisy_odom_node.py -> /odom_noisy
```

Result:

```text
The project can simulate imperfect odometry measurements with covariance for future localization/EKF work.
```

## Day 84 — Trajectory Validation Recorder

Goal:

```text
Record command, actual odometry, and noisy odometry into CSV.
```

Added:

```text
trajectory_validation_recorder.py
data/day84_trajectory_validation.csv
```

Recorded fields include:

```text
time, commanded velocities, actual pose/yaw/velocity, noisy pose/yaw
```

Result:

```text
The project can measure command vs actual vs noisy behavior over time.
```

## Day 85 — Plotting and Validation Report

Goal:

```text
Convert trajectory CSV into plots and a markdown report.
```

Added:

```text
plot_trajectory_validation.py
plots/trajectory_validation.png
docs/trajectory_validation_report.md
```

Result:

```text
The project can generate quantitative validation evidence from simulation data.
```

## Day 86 — GoogleTest Unit Testing

Goal:

```text
Add automated C++ unit tests for deterministic logic.
```

Added:

```text
day86_testable_core.hpp
test_day86_core.cpp
```

Validated:

```text
clamp()
wrapToPi()
integratePose()
```

Result:

```text
17 tests, 0 failures.
```

## Day 87 — GitHub Actions CI

Goal:

```text
Validate build and tests remotely through GitHub Actions.
```

Added:

```text
.github/workflows/ros2_jazzy_ci.yml
```

CI validates:

```text
checkout
ROS 2 Jazzy dependency install
rosdep install
colcon build
colcon test
colcon test-result
artifact upload
```

Result:

```text
The repository gained remote build/test validation.
```

## Day 88 — Deterministic C++ Performance Benchmark

Goal:

```text
Create a deterministic C++ pose-update timing benchmark.
```

Added:

```text
day88_performance_benchmark.cpp
data/day88_performance_results.csv
docs/performance_report.md
```

Observed baseline:

```text
dt=0.1    RTF ≈ 5684.98
dt=0.01   RTF ≈ 574.99
dt=0.001  RTF ≈ 57.23
```

Scope:

```text
This benchmark measures deterministic C++ pose-update timing, not Gazebo, ROS middleware, sensors, RViz, or Nav2.
```

## Day 89 — Validation Checkpoint

Goal:

```text
Validate the current stack after adding tests, CI, and benchmark layers.
```

Checked:

```text
clean WSL workspace
ROS 2 workspace build
GoogleTest execution
GitHub Actions CI status
performance benchmark execution
documentation status
```

Result:

```text
The project had build, unit-test, CI, performance, trajectory, and documentation validation layers before Nav2 implementation.
```

## Day 90 — Final Assessment and Interview Simulation

Goal:

```text
Assess whether the system could be explained and defended as a complete robotics simulation foundation.
```

Assessment areas:

```text
C++ simulator
ROS 2 topics
parameters
QoS
odometry
TF
RViz
URDF/Xacro
Gazebo
ros2_control
diff_drive_controller
lidar bridge
noisy odometry
trajectory validation
GoogleTest
CI
performance benchmark
known limitations
next phase direction
```

Result:

```text
Day 90 marked the transition from simulation foundation and validation tooling into the Nav2 working integration phase.
```

---

# Days 91–100 — Nav2 Working Integration Phase

## Day 91 — Nav2 Bringup Scaffold

Goal:

```text
Create the initial Nav2 launch/config scaffold on top of the Gazebo diff-drive robot stack.
```

Main outcome:

```text
The project gained a Nav2 navigation launch workflow that starts Gazebo, robot description, ros2_control, lidar bridge, RViz-ready data, Nav2 nodes, velocity smoother, and the command bridge.
```

Important architecture rule:

```text
Nav2 publishes Twist commands on /cmd_vel.
diff_drive_controller expects TwistStamped commands on /diff_drive_controller/cmd_vel.
The project therefore uses a Twist -> TwistStamped bridge.
```

Command path:

```text
Nav2 controller_server
  -> /cmd_vel
  -> cmd_vel_twist_bridge.py
  -> /diff_drive_controller/cmd_vel
  -> diff_drive_controller
  -> ros2_control
  -> Gazebo wheel joints
```

Result:

```text
Nav2 launch structure existed, but lifecycle activation and costmap behavior still needed validation.
```

## Day 92 — Nav2 Lifecycle Activation

Goal:

```text
Make Nav2 lifecycle nodes active and create a validation script.
```

Validated active lifecycle nodes:

```text
/controller_server
/smoother_server
/planner_server
/behavior_server
/velocity_smoother
/bt_navigator
/waypoint_follower
```

Added validation script:

```text
nav2_lifecycle_check.sh
```

Pass result:

```text
DAY 92 LIFECYCLE CHECK: PASS
```

Meaning:

```text
The Nav2 stack is not merely launched. Its managed lifecycle nodes reach active state.
```

## Day 93 — Nav2 Costmap Visibility

Goal:

```text
Validate local/global costmaps, scan input, robot footprint, and odom-frame costmap configuration.
```

Validated nodes:

```text
/local_costmap/local_costmap
/global_costmap/global_costmap
```

Validated topics:

```text
/scan
/local_costmap/costmap
/global_costmap/costmap
/local_costmap/published_footprint
/global_costmap/published_footprint
```

Validated frames:

```text
local_costmap.global_frame = odom
local_costmap.robot_base_frame = base_link
global_costmap.global_frame = odom
global_costmap.robot_base_frame = base_link
```

Validated TF:

```text
odom -> base_link
```

Added validation script:

```text
nav2_costmap_check.sh
```

Pass result:

```text
DAY 93 COSTMAP CHECK: PASS
```

Meaning:

```text
Nav2 can receive lidar data, publish local/global costmaps, and transform robot state in odom frame.
```

## Day 94 — Nav2 Planner and Controller Validation

Goal:

```text
Validate Nav2 planner/controller action servers, planner path generation, FollowPath controller parameters, and basic path-following motion.
```

Validated actions:

```text
/compute_path_to_pose
/follow_path
/navigate_to_pose
/navigate_through_poses
/compute_path_through_poses
```

Planner test:

```text
/compute_path_to_pose accepted an odom-frame goal and returned a non-empty path.
```

Controller parameter validation:

```text
controller_frequency = 10.0
FollowPath.max_vel_x = 0.25
FollowPath.max_vel_theta = 0.6
FollowPath.acc_lim_x = 0.5
FollowPath.acc_lim_theta = 1.0
FollowPath.sim_time = 1.5
FollowPath.vx_samples = 20
FollowPath.vtheta_samples = 20
```

Added validation script:

```text
nav2_planner_controller_check.sh
```

Script result:

```text
DAY 94 PLANNER/CONTROLLER CHECK: PASS
```

Additional runtime validation:

```text
A small /navigate_to_pose goal caused the robot to move in Gazebo, proving planner -> controller -> /cmd_vel -> bridge -> diff_drive_controller -> Gazebo motion.
```

Meaning:

```text
The Nav2 planner/controller layer was functional enough to compute paths and send executable velocity commands into the Gazebo control stack.
```

## Day 95 — Nav2 Goal Navigation

Goal:

```text
Send real Nav2 goals and verify closed-loop robot movement in Gazebo/RViz.
```

Validated flow:

```text
/navigate_to_pose goal accepted
/plan generated
/cmd_vel published
/diff_drive_controller/cmd_vel received TwistStamped commands
/diff_drive_controller/odom changed
Gazebo robot moved
RViz showed path/costmap/robot evidence
```

Result:

```text
DAY 95: PASS
```

Meaning:

```text
The robot completed the first true closed-loop Nav2 goal navigation milestone.
```

Important observation:

```text
The first movement was not perfectly tuned, but it proved the full Nav2-to-Gazebo command path worked.
```

## Day 96 — Nav2 Recovery Behavior Tests

Goal:

```text
Test normal, blocked, obstacle-constrained, and outside-costmap navigation behavior.
```

Fixed SDF obstacles:

```text
scan_box_front:
  center = (2.0, 0.0)
  footprint x = 1.8 to 2.2
  footprint y = -0.5 to 0.5

scan_box_left:
  center = (0.0, 2.0)
  footprint x = -0.5 to 0.5
  footprint y = 1.8 to 2.2
```

### Test 1 — Goal Inside Obstacle

Goal:

```text
(2.0, 0.0)
```

Observed:

```text
Goal accepted.
Robot attempted navigation for a long time.
Robot showed oscillation / left-right shaking.
number_of_recoveries reached 18.
distance_remaining stayed nonzero.
Final status: ABORTED.
error_code: 105.
Stack did not crash.
```

Result:

```text
PASS for blocked-goal recovery/failure behavior observation.
```

### Test 2 — Goal Behind Front Obstacle

Goal:

```text
(2.8, 0.0)
```

Observed:

```text
Robot was offset to the side after the previous test.
Nav2 found a feasible side route.
number_of_recoveries reached 8.
Final distance_remaining was approximately 0.195 m.
Final status: SUCCEEDED.
error_code: 0.
```

Result:

```text
PASS. Nav2 reached the goal when a feasible side route existed.
```

### Test 3 — Goal Outside Practical Costmap

Goal:

```text
(20.0, 20.0)
```

Observed:

```text
Goal accepted.
Nav2 immediately aborted.
Robot did not attempt to drive toward the far target.
number_of_recoveries = 0.
distance_remaining = 0.0.
Final status: ABORTED.
error_code: 204.
Stack did not crash.
```

Result:

```text
PASS. Nav2 cleanly rejected the outside-costmap goal.
```

Meaning:

```text
The system handles different failure modes without crashing: blocked obstacle goals trigger repeated recovery attempts, feasible obstacle-side goals can succeed, and far outside-costmap goals abort immediately.
```

## Day 97 — Nav2 Waypoint Navigation

Goal:

```text
Validate multi-goal navigation using /navigate_through_poses.
```

Action used:

```text
/navigate_through_poses [nav2_msgs/action/NavigateThroughPoses]
```

### Mission 1 — Easy Positive-X Waypoint Mission

Waypoints:

```text
(0.5, 0.0)
(0.8, -0.4)
(1.2, -0.6)
```

Observed:

```text
Goal accepted.
Robot moved through the waypoint sequence.
/cmd_vel published.
/diff_drive_controller/cmd_vel received TwistStamped commands.
/diff_drive_controller/odom changed.
Mission completed comfortably.
Final status: SUCCEEDED.
```

Result:

```text
PASS
```

### Mission 2 — Mirrored Negative-X Waypoint Mission

Waypoints:

```text
(-0.5, 0.0)
(-0.8, -0.4)
(-1.2, -0.6)
```

Observed:

```text
Goal accepted.
Robot moved through the mirrored waypoint sequence.
Odom changed consistently.
Mission succeeded.
Final status: SUCCEEDED.
```

Result:

```text
PASS
```

### Mission 3 — Obstacle-Side / Harder Waypoint Mission

Observed:

```text
Goal accepted.
Robot initially struggled near the obstacle-side route.
Robot appeared stuck for some time before recovering.
number_of_recoveries reached 16 in captured feedback.
number_of_poses_remaining reached 1 near the end.
Final result: SUCCEEDED.
error_code: 0.
```

Result:

```text
PASS with recoveries
```

Meaning:

```text
The robot can execute multi-goal missions. Easy missions succeed smoothly, and harder obstacle-side missions can still succeed after recovery behavior.
```

## Day 98 — Nav2 rosbag2 Evidence

Goal:

```text
Record a replayable rosbag2 dataset for a successful Nav2 goal navigation run.
```

Storage:

```text
MCAP
```

Bag folder:

```text
bags/day98_nav2_goal_evidence/goal_run_01
```

Bag info:

```text
Files:      goal_run_01_0.mcap
Bag size:   3.4 MiB
Storage id: mcap
ROS Distro: Jazzy
Duration:   31.118688884 s
Messages:   6809
```

Key recorded topics and counts:

| Topic | Count |
|---|---:|
| `/behavior_tree_log` | 8 |
| `/cmd_vel` | 81 |
| `/cmd_vel_nav` | 35 |
| `/cmd_vel_smoothed` | 86 |
| `/diff_drive_controller/cmd_vel` | 81 |
| `/diff_drive_controller/cmd_vel_out` | 2672 |
| `/diff_drive_controller/odom` | 1336 |
| `/global_costmap/costmap` | 20 |
| `/global_costmap/published_footprint` | 58 |
| `/local_costmap/costmap` | 48 |
| `/local_costmap/published_footprint` | 142 |
| `/local_plan` | 34 |
| `/plan` | 4 |
| `/received_global_plan` | 38 |
| `/scan` | 267 |
| `/tf` | 1863 |
| `/tf_static` | 2 |
| `/transformed_global_plan` | 34 |

Replay command:

```bash
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock
```

Replay result:

```text
rosbag2 player started successfully.
```

Important note:

```text
/goal_pose was included in the recording command, but the goal was sent through /navigate_to_pose action rather than RViz's /goal_pose topic, so /goal_pose did not appear in the final bag topic list.
```

Meaning:

```text
Day 98 created replayable evidence for commands, odometry, TF, scan, costmaps, plans, and behavior-tree logs during a successful Nav2 run.
```

## Day 99 — Nav2 Debugging Guide

Goal:

```text
Document the debugging and validation procedures learned from Days 91–98.
```

Covered:

```text
hard reset workflow
build workflow
lifecycle debugging
costmap debugging
RViz debugging
TF debugging
LaserScan frame debugging
cmd_vel bridge debugging
planner debugging
controller debugging
goal navigation debugging
recovery behavior debugging
waypoint navigation debugging
rosbag2 evidence debugging
ROS log search
known RTPS shared-memory warning
decision tree for common failures
```

Important non-blocking warning:

```text
RTPS_TRANSPORT_SHM Error Failed init_port fastrtps_port7005: open_and_lock_file failed -> Function open_port_internal
```

Current interpretation:

```text
Non-blocking. It has not prevented lifecycle checks, costmaps, TF, scan data, actions, planner path generation, controller checks, goal navigation, waypoint navigation, or rosbag recording.
```

Meaning:

```text
The project now has a practical debugging guide for Nav2 bringup and runtime failure analysis.
```

## Day 100 — Nav2 Phase Review and Documentation Consolidation

Goal:

```text
Consolidate the documentation into a clean public Day 100 structure.
```

Final documentation structure:

```text
README.md

docs/system_architecture.md
docs/topic_interface_reference.md
docs/debugging_and_validation.md
docs/daily_documentation.md
```

Utility script location:

```text
scripts/hard_reset.sh
```

Day 100 consolidation policy:

```text
No archive folder.
Useful content is merged into the four main docs.
Duplicated or obsolete files are deleted.
Executable scripts live in scripts/.
```

Day 100 Nav2 phase result:

```text
Lifecycle validation: PASS
Costmap validation: PASS
Planner/controller validation: PASS
Goal navigation: PASS
Recovery behavior tests: PASS
Waypoint navigation: PASS
rosbag2 evidence: PASS
Debugging guide: PASS
Documentation consolidation: PASS
```

Meaning:

```text
Day 100 closes the Nav2 odom-frame integration phase. The project now has a working, validated, documented ROS 2/Gazebo/Nav2 robot simulation stack ready for the next phase.
```

---

# Day 100 Final Technical Status

## Working Capabilities

The robot stack can currently:

- launch Gazebo with the diffbot world and fixed obstacle boxes
- spawn the differential-drive robot
- activate `ros2_control` and `diff_drive_controller`
- publish odometry and TF
- publish simulated lidar scans on `/scan`
- run Nav2 lifecycle nodes in active state
- publish local and global costmaps
- compute odom-frame paths
- publish Nav2 velocity commands
- bridge `/cmd_vel` Twist to `/diff_drive_controller/cmd_vel` TwistStamped
- move the robot in Gazebo from Nav2 goals
- execute single-goal navigation
- handle blocked and outside-costmap goals without crashing
- execute multi-waypoint navigation through `/navigate_through_poses`
- record replayable Nav2 rosbag2 evidence
- run validation scripts for lifecycle, costmaps, and planner/controller checks

## Main Validation Scripts

```text
nav2_lifecycle_check.sh
nav2_costmap_check.sh
nav2_planner_controller_check.sh
```

## Current Main Launch

```bash
ros2 launch cpp_robotics_sim_ros nav2_navigation.launch.py
```

## Current Hard Reset

```bash
./scripts/hard_reset.sh
```

## Current Navigation Frame Strategy

```text
Current navigation is odom-frame only.
Map-based SLAM, AMCL, and EKF localization are later phases.
```

## Current Limitations

- no SLAM yet
- no saved map navigation yet
- no AMCL localization yet
- no EKF fused localization in the Nav2 loop yet
- no Docker packaging yet
- no joystick/PS4 teleop yet
- no collision-aware teleop safety filter yet
- no automated scenario runner yet
- no full navigation metrics dashboard yet
- no multi-robot simulation yet
- no CI-based Gazebo/Nav2 runtime test yet

These limitations are intentional. The Day 100 milestone focused on getting the core ROS 2/Gazebo/Nav2 odom-frame stack working and documented.

---

# Day 100 Interview Explanation

```text
This project started as a standalone C++ robotics simulation foundation and evolved into a ROS 2/Gazebo mobile robot simulation stack. The early work built deterministic C++ simulation logic, differential-drive kinematics, trajectory logging, and validation. The ROS 2 phase added topics, odometry, TF, launch files, YAML parameters, QoS, diagnostics, RViz, rosbag2, URDF/Xacro, robot_state_publisher, Gazebo, ros2_control, diff_drive_controller, simulated lidar, noisy odometry, GoogleTest, CI, and performance benchmarking.

The Nav2 phase integrated the robot with lifecycle-managed Nav2 nodes, local/global costmaps, planner/controller validation, goal navigation, recovery behavior testing, waypoint navigation, and replayable rosbag2 evidence. The current stack can compute paths, publish velocity commands, bridge Nav2 Twist commands into the TwistStamped diff-drive controller interface, move the robot in Gazebo, and validate the behavior through scripts and recorded evidence.

Day 100 consolidates the project into four main engineering documents: system architecture, topic/interface reference, debugging and validation, and daily documentation. The project is now a documented, validated odom-frame ROS 2/Gazebo/Nav2 simulation stack ready for the next phase: SLAM, saved maps, localization, Dockerization, scenario validation, metrics, and advanced play-mode features.
```

---

# Next Phase Direction After Day 100

Recommended direction for Days 101–120:

```text
Day 101–105: SLAM Toolbox bringup and manual map building
Day 106–110: map save/load and AMCL localization
Day 111–115: map-based Nav2 goal navigation
Day 116–120: validation cleanup, README polish, screenshots, demo video, and public baseline release
```

Recommended post-Day-120 feature direction:

```text
Dockerized public baseline
keyboard/PS4 teleoperation
manual SLAM exploration
saved-map autonomous navigation
manual/autonomous mode switching
collision-aware velocity filtering
scenario-based navigation validation
navigation metrics dashboard
sensor noise and physics sensitivity testing
performance profiling
```

The Day 100 conclusion:

```text
The project is no longer only a robot demo. It is becoming a reproducible robotics simulation and validation platform.
```
