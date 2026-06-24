# Daily Documentation — C++ Robotics Simulation Foundation

This document tracks the daily progress of the `cpp_robotics_sim_foundation` project.

The project is a modular robotics simulation foundation built in C++ and ROS 2. It started from basic C++ simulation patterns and is now moving toward a professional ROS 2 robotics simulation stack with launch files, YAML configuration, runtime launch arguments, QoS profiles, rosbag2, RViz, URDF/Xacro, Gazebo, validation, and portfolio-ready documentation.

---

## 1. Project Summary

This project contains:

* standalone C++ simulation modules
* differential-drive mobile robot simulation
* manipulator joint-state simulation
* ROS 2 C++ simulator integration
* `/cmd_vel` subscriber
* `/robot_pose` publisher
* `/odom` publisher
* TF broadcaster for `odom -> base_link`
* ROS 2 launch workflow
* YAML runtime configuration
* launch argument overrides
* explicit QoS profiles
* rosbag2 recording and replay workflow
* regression testing
* debugging workflow
* performance timing
* project documentation

---

## 2. Repository Structure

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
│       ├── src/
│       │   └── sim_node.cpp
│       ├── CMakeLists.txt
│       └── package.xml
│
└── docs/
    ├── daily_documentation.md
    ├── debugging_and_validation.md
    └── system_architecture.md

```

---

# Days 1–60 — Foundation Summary

## Phase 1: Days 1–10 — Core C++ Simulation Basics

Built the first C++ robotics simulation patterns from scratch:

* vectors and indexing for robot data
* pass-by-reference update functions
* utility math such as clamp and angle wrapping
* statistics over robot state vectors
* fixed-timestep simulation loops
* `JointState` and `Pose2D` state containers
* multi-joint state storage using `std::vector<JointState>`
* single-joint update logic
* multi-joint update loops

Key lesson:

```txt
C++ simulation code must be exact. Correct indexing, references, validation, and update logic matter immediately.
```

---

## Phase 2: Days 11–20 — Mobile Robot and Safety Foundation

Built the first mobile robot simulation layer:

* planar robot state using `x`, `y`, and `theta`
* pose integration from linear and angular velocity
* trajectory storage using `std::vector<Pose2D>`
* final pose and trajectory reporting
* heading-aware motion using `cos(theta)` and `sin(theta)`
* command structs separating robot input from robot state
* differential-drive wheel-speed to body-velocity conversion
* basic target-tracking controller
* safety guards for invalid timestep, vector size, and invalid parameters

Key lesson:

```txt
A mobile robot simulator needs state, command input, kinematics, trajectory logging, and safety validation.
```

---

## Phase 3: Days 21–30 — Modular C++ Project Structure

Converted early scripts into a more professional C++ project:

* header/source separation
* cleaner simulation architecture
* reusable utilities
* trajectory analysis
* scenario testing
* manipulator joint-state mini-simulation
* differential-drive mobile robot mini-simulation
* code cleanup with naming, const-correctness, and references
* final project integration
* Day 30 assessment

Key lesson:

```txt
A portfolio project should be modular, explainable, buildable, and testable instead of being one large script.
```

---

## Phase 4: Days 31–44 — C++ Robotics Software Foundation

Strengthened the standalone C++ simulator:

* CMake-based multi-file build
* clean `include/` and `src/` project layout
* class-based mobile robot simulator
* const/reference correctness
* STL usage for trajectory data and metrics
* CSV trajectory logging
* build/debug discipline
* differential-drive kinematics
* scenario runner
* validation tests
* target tracking
* final cleanup for GitHub

Key lesson:

```txt
The standalone simulator became a deterministic robotics software artifact with kinematics, validation, metrics, and repeatable scenarios.
```

---

## Phase 5: Days 45–60 — ROS 2 C++ Integration and Validation

Integrated the simulator into ROS 2:

* created an `ament_cmake` ROS 2 package
* built a C++ `rclcpp` simulation node
* added `/cmd_vel` subscriber
* added `/robot_pose` publisher
* added `/odom` publisher
* added TF broadcaster for `odom -> base_link`
* added ROS 2 parameters
* added command timeout behavior
* added velocity clamping
* added parameter validation
* added performance timing using `std::chrono::steady_clock`
* documented debugging workflow
* documented regression checklist
* added manipulator joint-state mini-sim
* completed Day 60 assessment

Key lesson:

```txt
The project moved from standalone C++ simulation into a ROS 2 robotics stack with topics, parameters, odometry, TF, validation, timing, and documentation.
```

---

## Day 60 Assessment Result

| Area                                   | Status               |
| -------------------------------------- | -------------------- |
| Conceptual understanding               | Passed               |
| Project architecture understanding     | Passed               |
| ROS 2 topic/parameter/TF understanding | Passed               |
| C++ syntax precision                   | Needs daily practice |
| Git/build discipline                   | Improving            |
| Interview explanation                  | Improving            |

Main Day 60 weakness:

```txt
Concepts are strong, but exact syntax still needs daily drilling.
```

Daily rule going forward:

```txt
Write 20–30 lines of C++ or ROS 2 launch/config code from memory before checking old code.
```

---

# Day 61 — ROS 2 Launch System

## Goal

Create a one-command ROS 2 launch workflow for the simulator stack.

## Deliverable

The simulator can now be started with:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## What Changed

Added:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/sim.launch.py
```

Updated CMake to install the launch directory:

```cmake
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)
```

## Why This Matters

A launch file makes the ROS 2 stack repeatable. Instead of manually running the node and passing parameters through terminal commands, the launch file defines the node startup in one version-controlled place.

## Verification Commands

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

In another terminal:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic list
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
```

Command test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

## Interview Explanation

Day 61 added a ROS 2 launch file for the simulator stack. This allows the C++ `sim_node` to be started with one repeatable command instead of relying on manual terminal commands. The launch directory must be installed into `share/${PROJECT_NAME}` so `ros2 launch` can discover it from the installed package. This prepares the project for YAML parameters, RViz, rosbag2, URDF, and Gazebo workflows.

---

# Day 62 — YAML Parameters

## Goal

Move simulator runtime parameters out of the launch file and into a YAML configuration file.

## Deliverable

The simulator now loads parameters from:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

The simulator still launches with:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## YAML File

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

## Launch File Change

Before Day 62, parameters were written directly inside `sim.launch.py`.

After Day 62, the launch file locates the installed package share directory:

```python
package_share_dir = get_package_share_directory("cpp_robotics_sim_ros")
```

Then it builds the path to the YAML config file:

```python
params_file = os.path.join(package_share_dir, "config", "sim_params.yaml")
```

Then it passes the YAML file into the node:

```python
parameters=[params_file]
```

## CMake Install Change

Updated CMake to install both the `launch/` and `config/` directories:

```cmake
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)
```

## Why This Matters

YAML configuration separates runtime parameters from code and launch logic. This makes the simulator easier to tune, reproduce, and extend. Robotics projects commonly use YAML files for controller gains, robot limits, sensor settings, navigation parameters, and simulation settings.

## Verification Commands

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

In another terminal:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 param get /sim_node dt
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Expected:

```txt
Double value is: 0.1
Double value is: 0.0
Double value is: 0.0
Double value is: 0.0
Double value is: 0.5
Double value is: 0.5
Double value is: 0.8
```

## Installed YAML Check

To verify what ROS 2 is actually using from the installed package:

```bash
cat "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/config/sim_params.yaml"
```

## Interview Explanation

Day 62 moved simulator parameters from the launch file into a YAML configuration file. The launch file now locates the installed package share directory, finds `config/sim_params.yaml`, and passes that file to `sim_node`. This separates code, launch behavior, and runtime configuration. It matters because professional robotics systems use YAML for controller parameters, robot limits, sensor settings, and navigation configuration.

---

# Day 63 — Launch Arguments

## Goal

Add runtime launch arguments for simulator parameters.

## Deliverable

The simulator can still be launched with the default YAML configuration:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

It can also override selected parameters from the terminal:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

## Parameters Exposed as Launch Arguments

| Launch Argument      | Default | Purpose                                    |
| -------------------- | ------: | ------------------------------------------ |
| dt                   |     0.1 | Simulation timestep                        |
| initial_x            |     0.0 | Initial robot x position                   |
| initial_y            |     0.0 | Initial robot y position                   |
| initial_theta        |     0.0 | Initial robot heading in radians           |
| cmd_timeout          |     0.5 | Stops robot if command input becomes stale |
| max_linear_velocity  |     0.5 | Linear velocity safety clamp               |
| max_angular_velocity |     0.8 | Angular velocity safety clamp              |

## Launch File Design

The YAML file provides the baseline configuration. The launch file then exposes selected values as terminal-overridable launch arguments.

Core imports:

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
```

Example launch argument:

```python
dt_arg = DeclareLaunchArgument(
    "dt",
    default_value="0.1",
    description="Simulation timestep in seconds",
)
```

Example parameter override:

```python
"dt": ParameterValue(
    LaunchConfiguration("dt"),
    value_type=float,
),
```

The node receives parameters in this order:

```python
parameters=[
    params_file,
    {
        "dt": ParameterValue(LaunchConfiguration("dt"), value_type=float),
        "initial_x": ParameterValue(LaunchConfiguration("initial_x"), value_type=float),
        "initial_y": ParameterValue(LaunchConfiguration("initial_y"), value_type=float),
        "initial_theta": ParameterValue(LaunchConfiguration("initial_theta"), value_type=float),
        "cmd_timeout": ParameterValue(LaunchConfiguration("cmd_timeout"), value_type=float),
        "max_linear_velocity": ParameterValue(LaunchConfiguration("max_linear_velocity"), value_type=float),
        "max_angular_velocity": ParameterValue(LaunchConfiguration("max_angular_velocity"), value_type=float),
    },
]
```

The dictionary after `params_file` overrides matching YAML values.

## Parameter Precedence

For parameters exposed through the Day 63 launch dictionary:

```txt
terminal override > DeclareLaunchArgument default > YAML > C++ hardcoded default
```

Example:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py dt:=0.05
```

This gives the node:

```txt
dt = 0.05
```

If no terminal override is given, the `DeclareLaunchArgument` default is used for exposed parameters.

## Verification Commands

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
ros2 launch cpp_robotics_sim_ros sim.launch.py initial_x:=2.0 initial_y:=1.0 initial_theta:=0.5 dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

In another terminal:

```bash
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node dt
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Expected:

```txt
Double value is: 2.0
Double value is: 1.0
Double value is: 0.5
Double value is: 0.05
Double value is: 1.0
Double value is: 0.2
Double value is: 0.4
```

Pose check:

```bash
ros2 topic echo --once /robot_pose
```

Expected pose should start near:

```txt
x: 2.0
y: 1.0
theta: 0.5
```

## Interview Explanation

Day 63 added launch arguments on top of the YAML configuration. YAML stores stable baseline parameters, while launch arguments allow runtime overrides from the terminal without editing files. The launch file uses `DeclareLaunchArgument`, `LaunchConfiguration`, and `ParameterValue` to pass typed parameter overrides into `sim_node`. For exposed parameters, the launch-argument dictionary is passed after the YAML file, so terminal/default launch values override YAML values. This is useful for quickly testing different starting poses, timesteps, timeout values, and velocity limits.

---

# Day 64 — ROS 2 QoS Profiles

## Goal

Make ROS 2 communication behavior explicit by defining QoS profiles for command and state topics.

## Deliverable

The simulator now uses explicit QoS profiles instead of raw queue-depth integers.

| Topic         | Endpoint                                      | QoS Choice                        | Reason                                                                                                |
| ------------- | --------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/cmd_vel`    | Subscriber                                    | reliable, volatile, keep_last(10) | Commands should be delivered reliably, but stale commands should not be replayed to late subscribers. |
| `/robot_pose` | Publisher                                     | reliable, volatile, keep_last(10) | Low-rate simulator pose output should be reliable for debugging and validation.                       |
| `/odom`       | Publisher                                     | reliable, volatile, keep_last(10) | Odometry is important state output for RViz, rosbag2, and validation.                                 |
| `/tf`         | Publisher via `tf2_ros::TransformBroadcaster` | handled by tf2 broadcaster        | Standard TF broadcaster manages transform publication.                                                |

## Code Pattern

```cpp
const auto command_qos = rclcpp::QoS(rclcpp::KeepLast(10))
    .reliable()
    .durability_volatile();

const auto state_qos = rclcpp::QoS(rclcpp::KeepLast(10))
    .reliable()
    .durability_volatile();
```

Publisher/subscriber usage:

```cpp
pose_publisher_ = this->create_publisher<geometry_msgs::msg::Pose2D>(
    "/robot_pose",
    state_qos
);

odom_publisher_ = this->create_publisher<nav_msgs::msg::Odometry>(
    "/odom",
    state_qos
);

cmd_subscriber_ = this->create_subscription<geometry_msgs::msg::Twist>(
    "/cmd_vel",
    command_qos,
    std::bind(&SimNode::cmdVelCallback, this, std::placeholders::_1)
);
```

## QoS Concepts

| QoS Policy  | Meaning                                       | Typical Choice                                                     |
| ----------- | --------------------------------------------- | ------------------------------------------------------------------ |
| History     | How many messages are queued                  | `KeepLast(N)` for most robotics topics                             |
| Reliability | Whether delivery is guaranteed                | `Reliable` for command/state, `BestEffort` for high-rate sensors   |
| Durability  | Whether late subscribers receive old messages | `Volatile` for live data, `TransientLocal` for latched/static data |
| Deadline    | Expected maximum time between messages        | Useful for real-time monitoring                                    |
| Lifespan    | How long a message remains valid              | Useful when stale data should expire                               |
| Liveliness  | Whether publisher is still alive              | Useful for detecting dead publishers                               |

## Verification Commands

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /tf --verbose
```

Expected for `/cmd_vel`, `/robot_pose`, and `/odom`:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

The code explicitly configures `KeepLast(10)`. The ROS 2 CLI may display history/depth as `UNKNOWN` depending on middleware introspection, so the code-level QoS definition is the source of truth for history/depth.

## Functional Verification

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
ros2 topic echo --once /robot_pose
```

## Interview Explanation

Day 64 made the simulator’s ROS 2 communication behavior explicit using QoS profiles. Instead of passing only queue-depth integers, the node now defines reliability, durability, history, and depth for command and state topics. I used reliable, volatile, keep_last(10) for `/cmd_vel`, `/robot_pose`, and `/odom` because these topics should communicate current command/state data reliably without replaying stale old messages to late subscribers. For future high-rate sensor topics like lidar or camera streams, I would consider best-effort QoS because dropping old sensor frames can be better than processing delayed stale data.

---

# Day 65 — rosbag2 Recording and Replay

## Goal

Record and replay simulator topic data using rosbag2.

## Deliverable

Created a repeatable rosbag2 workflow for recording:

| Topic | Purpose |
|---|---|
| `/cmd_vel` | Command input sent to the simulator |
| `/robot_pose` | Simple 2D pose output |
| `/odom` | Standard odometry output |
| `/tf` | Transform data for `odom -> base_link` |

## Recording Command

```bash
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
```

## Motion Commands Used During Recording

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
sleep 1
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.4}, angular: {z: -0.2}}"
sleep 1
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

## Bag Inspection

```bash
ros2 bag info bags/day65_baseline
```

Expected topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

## Replay Command

```bash
ros2 bag play bags/day65_baseline
```

## Verification During Replay

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
```

## Why This Matters

rosbag2 makes simulation behavior reproducible. Instead of only watching terminal output live, I can record command input, pose output, odometry, and TF data, then replay the same run later for debugging, validation, and portfolio evidence.

## Interview Explanation

Day 65 added rosbag2 recording and replay to the simulator workflow. I recorded `/cmd_vel`, `/robot_pose`, `/odom`, and `/tf` so the simulator’s command input and state outputs can be inspected after a run. This is useful for robotics debugging because it preserves evidence of what commands were sent, what state was published, and whether odometry and TF behaved consistently.

---

# Current Verification Workflow

Use this after meaningful source, launch, config, or documentation changes.

## Build

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

## Launch

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## Runtime Checks

```bash
ros2 topic list
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
```

## Command Test

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
ros2 topic echo --once /robot_pose
```

## Parameter Checks

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node initial_x
ros2 param get /sim_node initial_y
ros2 param get /sim_node initial_theta
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

## QoS Checks

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /robot_pose --verbose
ros2 topic info /odom --verbose
ros2 topic info /tf --verbose
```

## rosbag2 Checks

```bash
ros2 bag record -o bags/day65_baseline /cmd_vel /robot_pose /odom /tf
ros2 bag info bags/day65_baseline
ros2 bag play bags/day65_baseline
```

Expected recorded topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

---

# Git Discipline

Before every commit:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
git status
git diff
```

Stage only intended files:

```bash
git add <specific-file>
```

Check staged files:

```bash
git diff --cached --name-only
```

Do not commit:

```txt
build/
install/
log/
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
```

Expected `.gitignore` entries:

```gitignore
build/
install/
log/
ros2_ws/build/
ros2_ws/install/
ros2_ws/log/
```

---

# Current Status

|  Day | Status                | Main Deliverable                            |
| ---: | --------------------- | ------------------------------------------- |
| 1–60 | Complete              | Standalone C++ + ROS 2 simulator foundation |
|   61 | Complete              | ROS 2 launch file                           |
|   62 | Complete              | YAML parameter config                       |
|   63 | Complete              | Launch argument overrides                   |
|   64 | Complete              | Explicit QoS profiles                       |
|   65 | Complete              | rosbag2 recording and replay workflow       |

Next planned day:

```txt
Day 66 — RViz2 visualization
```
