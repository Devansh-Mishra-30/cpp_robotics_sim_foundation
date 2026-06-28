# Daily Documentation — C++ Robotics Simulation Foundation

This document tracks the daily progress of the `cpp_robotics_sim_foundation` project.

The project is a modular robotics simulation foundation built in C++ and ROS 2. It started from basic C++ simulation patterns and is now moving toward a professional ROS 2 robotics simulation stack with launch files, YAML configuration, runtime launch arguments, QoS profiles, rosbag2, RViz, URDF/Xacro, robot state publishing, joint state publishing, Gazebo, validation, and portfolio-ready documentation.

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
* RViz2 visualization workflow
* runtime diagnostics on `/diagnostics`
* launch regression script
* debugging workflow
* performance timing
* URDF robot model
* Xacro robot description
* `robot_state_publisher` workflow
* `joint_state_publisher` workflow
* RViz RobotModel visualization
* Gazebo Sim spawn workflow
* `ros2_control` hardware interface configuration
* `controller_manager` workflow
* `joint_state_broadcaster` integration
* `diff_drive_controller` integration
* Gazebo-driven differential-drive motion
* simulated lidar sensor
* `/scan` LaserScan bridge through `ros_gz_bridge`
* RViz visualization of robot model, odometry, TF, and lidar
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
│       ├── urdf/
│       │   └── diffbot.urdf
│       ├── xacro/
│       │   └── diffbot.xacro
│       ├── worlds/
│       │   └── empty_diffbot_world.sdf
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
    ├── debugging_and_validation.md
    ├── system_architecture.md
    └── topic_interface_reference.md
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

| Launch Argument        | Default | Purpose                                    |
| ---------------------- | ------: | ------------------------------------------ |
| `dt`                   |     0.1 | Simulation timestep                        |
| `initial_x`            |     0.0 | Initial robot x position                   |
| `initial_y`            |     0.0 | Initial robot y position                   |
| `initial_theta`        |     0.0 | Initial robot heading in radians           |
| `cmd_timeout`          |     0.5 | Stops robot if command input becomes stale |
| `max_linear_velocity`  |     0.5 | Linear velocity safety clamp               |
| `max_angular_velocity` |     0.8 | Angular velocity safety clamp              |

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

| Topic          | Endpoint                                      | QoS Choice                        | Reason                                                                                                |
| -------------- | --------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/cmd_vel`     | Subscriber                                    | reliable, volatile, keep_last(10) | Commands should be delivered reliably, but stale commands should not be replayed to late subscribers. |
| `/robot_pose`  | Publisher                                     | reliable, volatile, keep_last(10) | Low-rate simulator pose output should be reliable for debugging and validation.                       |
| `/odom`        | Publisher                                     | reliable, volatile, keep_last(10) | Odometry is important state output for RViz, rosbag2, and validation.                                 |
| `/diagnostics` | Publisher                                     | reliable, volatile, keep_last(10) | Diagnostics should be reliable for runtime health checks.                                             |
| `/tf`          | Publisher via `tf2_ros::TransformBroadcaster` | handled by tf2 broadcaster        | Standard TF broadcaster manages transform publication.                                                |

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

diagnostics_publisher_ = this->create_publisher<diagnostic_msgs::msg::DiagnosticArray>(
    "/diagnostics",
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
ros2 topic info /diagnostics --verbose
```

Expected for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics`:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

The code explicitly configures `KeepLast(10)`. The ROS 2 CLI may display history/depth as `UNKNOWN` depending on middleware introspection, so the code-level QoS definition is the source of truth for history/depth.

## Functional Verification

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 topic echo --once /diagnostics
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
ros2 topic echo --once /robot_pose
```

## Interview Explanation

Day 64 made the simulator’s ROS 2 communication behavior explicit using QoS profiles. Instead of passing only queue-depth integers, the node now defines reliability, durability, history, and depth for command, state, odometry, and diagnostics topics. I used reliable, volatile, keep_last(10) for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics` because these topics should communicate current command/state data reliably without replaying stale old messages to late subscribers. For future high-rate sensor topics like lidar or camera streams, I would consider best-effort QoS because dropping old sensor frames can be better than processing delayed stale data.

---

# Day 65 — rosbag2 Recording and Replay

## Goal

Record and replay simulator topic data using rosbag2.

## Deliverable

Created a repeatable rosbag2 workflow for recording:

| Topic         | Purpose                                |
| ------------- | -------------------------------------- |
| `/cmd_vel`    | Command input sent to the simulator    |
| `/robot_pose` | Simple 2D pose output                  |
| `/odom`       | Standard odometry output               |
| `/tf`         | Transform data for `odom -> base_link` |

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

# Day 66 — RViz2 Visualization

## Goal

Visualize the ROS 2 simulator state using RViz2.

## Deliverable

Created a saved RViz2 configuration:

```txt
ros2_ws/src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

The RViz2 configuration visualizes:

| Display  | Purpose                                          |
| -------- | ------------------------------------------------ |
| Grid     | Ground/reference plane                           |
| TF       | Shows the `odom -> base_link` frame relationship |
| Odometry | Visualizes robot motion from `/odom`             |

## RViz Fixed Frame

```txt
odom
```

## RViz Displays

```txt
Grid
TF
Odometry
```

Odometry topic:

```txt
/odom
```

## Run Simulator

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## Open RViz from Source Config

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

rviz2 -d src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

## Open RViz from Installed Config

```bash
rviz2 -d "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/rviz/sim_debug.rviz"
```

## Motion Test

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected RViz behavior:

```txt
base_link moves relative to odom
TF axes update
/odom visualization updates
```

## Why This Matters

RViz2 provides visual debugging for robot state, odometry, and TF. Instead of only checking terminal output, the simulator can now be visually inspected to confirm that the robot frame, odometry message, and transform tree behave correctly during motion.

## Interview Explanation

Day 66 added RViz2 visualization to the simulator workflow. I created a saved RViz2 config that uses `odom` as the fixed frame and displays Grid, TF, and Odometry. This lets me visually inspect the `odom -> base_link` transform and verify that `/odom` updates correctly when `/cmd_vel` commands move the robot.

---

# Day 67 — Diagnostics

## Goal

Add runtime diagnostics to the ROS 2 simulator.

## Deliverable

Added a `/diagnostics` publisher using:

```txt
diagnostic_msgs/msg/DiagnosticArray
diagnostic_msgs/msg/DiagnosticStatus
diagnostic_msgs/msg/KeyValue
```

The simulator now publishes structured runtime health/status information for the node.

## Diagnostic Topic

```txt
/diagnostics
```

## Diagnostic Fields

The diagnostic message reports:

| Field                      | Meaning                            |
| -------------------------- | ---------------------------------- |
| `dt`                       | Simulation timestep                |
| `cmd_timeout`              | Command timeout threshold          |
| `time_since_cmd`           | Time since last `/cmd_vel`         |
| `timeout_active`           | Whether command timeout is active  |
| `linear_velocity`          | Current linear velocity            |
| `angular_velocity`         | Current angular velocity           |
| `max_linear_velocity`      | Linear velocity clamp limit        |
| `max_angular_velocity`     | Angular velocity clamp limit       |
| `pose_x`                   | Current x position                 |
| `pose_y`                   | Current y position                 |
| `pose_theta`               | Current heading                    |
| `callback_time_ms`         | Current callback runtime           |
| `average_callback_time_ms` | Average callback runtime           |
| `max_callback_time_ms`     | Worst callback runtime             |
| `timing_budget_ms`         | Allowed callback budget from `dt`  |
| `callback_count`           | Number of timer callbacks executed |

## Status Levels

```txt
OK   = simulator running with fresh command input
WARN = cmd_vel timeout active
```

## Verification Commands

```bash
ros2 topic list | grep diagnostics
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

## OK-State Test

Run a continuous command:

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

Stop the `/cmd_vel` publisher and wait longer than `cmd_timeout`.

Then check diagnostics:

```bash
ros2 topic echo --once /diagnostics
```

Expected:

```txt
level: 1
message: cmd_vel timeout active
timeout_active: true
```

## Why This Matters

Diagnostics make the simulator easier to debug and validate. Instead of relying only on terminal logs, the node now publishes structured runtime health information that can be inspected, recorded, monitored, and extended later for system-level debugging.

## Interview Explanation

Day 67 added a `/diagnostics` publisher to the ROS 2 simulator using `diagnostic_msgs/msg/DiagnosticArray`. The diagnostics report node health, command timeout status, velocity limits, current pose, and callback timing. The diagnostic status changes from OK to WARN when `/cmd_vel` becomes stale, which makes runtime health visible through a standard ROS 2 topic.

---

## Diagnostics Checks

```bash
ros2 topic list | grep diagnostics
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Expected topic:

```txt
/diagnostics
```

Expected message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected health states:

```txt
OK   when fresh /cmd_vel commands are being received
WARN when cmd_vel timeout is active
```

---

# Day 68 — Launch Regression

## Goal

Create a repeatable launch regression workflow for the ROS 2 simulator.

## Deliverable

Added a launch regression script:

```txt
scripts/day68_launch_regression.sh
```

The script validates that the simulator launches correctly and that the core ROS 2 runtime interfaces are alive.

## What the Script Checks

| Check                  | Purpose                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------ |
| Default launch         | Confirms `ros2 launch cpp_robotics_sim_ros sim.launch.py` starts successfully        |
| Topic existence        | Verifies `/cmd_vel`, `/robot_pose`, `/odom`, `/tf`, and `/diagnostics`               |
| Default parameters     | Confirms expected parameters are loaded                                              |
| State outputs          | Confirms `/robot_pose`, `/odom`, `/tf`, and `/diagnostics` publish                   |
| Command response       | Confirms `/cmd_vel` input does not break runtime behavior                            |
| Diagnostics type/QoS   | Confirms `/diagnostics` uses `diagnostic_msgs/msg/DiagnosticArray` with expected QoS |
| Launch overrides       | Confirms launch arguments override runtime parameters                                |
| Override runtime check | Confirms the node still publishes state after override launch                        |

## Run Command

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

## Pass Criteria

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

## Why This Matters

Launch regression testing gives the project a repeatable validation gate. Instead of manually checking topics, parameters, diagnostics, odometry, TF, and launch overrides after every change, the script verifies the critical ROS 2 runtime behavior in one command.

## Interview Explanation

Day 68 added a launch regression script for the ROS 2 simulator. The script launches the node, verifies expected topics, checks parameters, validates odometry, TF, diagnostics, command response, QoS, and launch argument overrides. This makes the simulator easier to maintain because future changes can be tested against a repeatable regression workflow before committing.

---

# Day 69 — ROS 2 Usage Documentation

## Goal

Add clear user-facing ROS 2 usage documentation for the simulator.

## Deliverable

Updated the project README with a ROS 2 usage quickstart covering:

```txt
workspace build
simulator launch
/cmd_vel command publishing
/robot_pose inspection
/odom inspection
/tf inspection
/diagnostics inspection
parameter checks
launch argument overrides
RViz2 visualization
rosbag2 recording/replay
launch regression script
```

## Why This Matters

A robotics project should not only work on the developer's machine. It should be easy for another engineer, recruiter, interviewer, or future teammate to build, run, inspect, and validate.

Day 69 turns the README into a practical usage guide instead of only a project description.

## Usage Flow Documented

```txt
build workspace
source ROS 2 environment
launch simulator
publish velocity command
inspect pose, odometry, TF, and diagnostics
open RViz2
record or replay rosbag2 data
run launch regression before commit
```

## Key Commands Added

Build:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Launch:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Inspect:

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

Run regression:

```bash
./scripts/day68_launch_regression.sh
```

## Interview Explanation

Day 69 improved the project’s user-facing documentation. I added a ROS 2 usage quickstart that explains how to build the workspace, launch the simulator, publish commands, inspect pose, odometry, TF, diagnostics, use RViz2, record rosbag2 data, and run the launch regression script. This makes the project easier for another engineer to reproduce and validate.

---

# Day 70 — Topic Interface Documentation

## Goal

Create a clear ROS 2 topic interface reference for the simulator.

## Deliverable

Added:

```txt
docs/topic_interface_reference.md
```

The document explains each ROS 2 topic used by the simulator:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

## What Was Documented

For each topic, the documentation defines:

```txt
topic direction
message type
purpose
important fields
QoS behavior
validation commands
expected output
common failure modes
```

## Why This Matters

Robotics systems are interface-driven. A node is only useful if another engineer can understand what it subscribes to, what it publishes, what message types it uses, and how to validate those interfaces.

Day 70 turns the simulator topics into a documented interface contract.

## Interface Contract

```txt
/cmd_vel provides command input
/robot_pose provides simple 2D debug state
/odom provides ROS-standard odometry
/tf provides odom -> base_link transform
/diagnostics provides runtime health and timeout status
```

## Validation Command Summary

```bash
ros2 topic list
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
ros2 topic type /diagnostics
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 topic echo --once /diagnostics
ros2 run tf2_ros tf2_echo odom base_link
```

## Interview Explanation

Day 70 added a ROS 2 topic interface reference. It documents each topic’s direction, message type, fields, QoS behavior, validation commands, and common failure modes. This makes the simulator easier to integrate, debug, and explain because the runtime communication contract is clearly defined.

---

# Day 71 — URDF Robot Model

## Goal

Create a standard ROS robot description for the differential-drive robot.

## Deliverable

Added:

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

## What Was Implemented

The static URDF model includes:

```txt
visual geometry
collision geometry
basic inertial properties
continuous wheel joints
fixed caster joint
```

The important architecture rule established on Day 71:

```txt
sim_node owns odom -> base_link
URDF owns robot structure below base_link
```

## Validation Commands

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf")
print("PASS: URDF XML parsed successfully")
PY

grep -n '<link name' ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
grep -n '<joint name' ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
```

Installed file check:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ls "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/urdf/diffbot.urdf"
```

## Interview Explanation

Day 71 added a standard URDF model for the differential-drive robot. The model defines the base, wheels, caster, visual geometry, collision geometry, inertial properties, and joint structure. The simulator still owns the moving `odom -> base_link` transform, while the robot description owns the structure below `base_link`.

---

# Day 72 — Xacro Macros

## Goal

Convert the static URDF model into a reusable parameterized Xacro model.

## Deliverable

Added:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
```

## What Was Implemented

The Xacro file adds reusable parameters and macros for:

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

The static Day 71 URDF remains as a reference artifact, while the Xacro file becomes the maintainable robot description used by later launch workflows.

## Validation Commands

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"

source /opt/ros/jazzy/setup.bash

xacro "ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro" > /tmp/diffbot_from_xacro.urdf

python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("/tmp/diffbot_from_xacro.urdf")
print("PASS: Xacro generated valid URDF XML")
PY

grep -n '<link name' /tmp/diffbot_from_xacro.urdf
grep -n '<joint name' /tmp/diffbot_from_xacro.urdf
```

Installed Xacro check:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

xacro "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/xacro/diffbot.xacro" > /tmp/installed_diffbot_from_xacro.urdf
```

## Interview Explanation

Day 72 converted the robot description from a fixed URDF into a parameterized Xacro file. This makes the robot description easier to maintain because repeated structures such as wheel links and inertial blocks can be generated from macros and shared parameters instead of being manually duplicated.

---

# Day 73 — robot_state_publisher

## Goal

Launch `robot_state_publisher` with the generated robot description.

## Deliverable

Added:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/description.launch.py
```

The launch file loads:

```txt
xacro/diffbot.xacro
```

and publishes:

```txt
/robot_description
/tf
/tf_static
```

## Important Fixes Learned

Because the local repository path contains spaces, the Xacro command needed quoting inside the launch file.

Because the generated XML is passed as a ROS parameter, the launch file must force the value to be treated as a string:

```python
ParameterValue(robot_description_content, value_type=str)
```

Without this, ROS 2 tries to parse the XML as YAML.

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Second terminal:

```bash
ros2 node list
ros2 node info /robot_state_publisher
ros2 topic list | grep -E "robot_description|tf"

ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint" /tmp/robot_description.txt

ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected fixed transform:

```txt
frame_id: base_link
child_frame_id: caster_link
```

## Interview Explanation

Day 73 added `robot_state_publisher` integration. The launch file evaluates the Xacro model, passes the generated XML to the `robot_description` parameter, and starts `robot_state_publisher`. This publishes the robot description and fixed transforms such as `base_link -> caster_link`. The simulator still owns `odom -> base_link`, so transform ownership remains clean.

---

# Day 74 — joint_state_publisher

## Goal

Add `/joint_states` so the continuous wheel joints can be published and consumed by `robot_state_publisher`.

## Deliverable

Updated:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/description.launch.py
```

The launch file now starts:

```txt
robot_state_publisher
joint_state_publisher
```

## Runtime Topics

Day 74 adds:

```txt
/joint_states
```

Expected joint names:

```txt
left_wheel_joint
right_wheel_joint
```

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Second terminal:

```bash
ros2 node list
ros2 topic list | grep -E "joint_states|robot_description|tf"
ros2 topic echo /joint_states --once

ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link caster_link
```

Expected wheel transforms:

```txt
base_link -> left_wheel_link
base_link -> right_wheel_link
```

Expected caster transform:

```txt
base_link -> caster_link
```

## Interview Explanation

Day 74 added `joint_state_publisher` so the robot model has joint state input for the continuous wheel joints. `robot_state_publisher` uses `/joint_states` plus the robot description to publish dynamic wheel link transforms. This completes the basic robot description TF tree below `base_link`.

---

# Day 75 — RViz Robot Model Visualization

## Goal

Display the full robot model in RViz using the robot description and TF tree.

## Deliverable

Added:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/robot_model_viz.launch.py
ros2_ws/src/cpp_robotics_sim_ros/rviz/diffbot_robot_model.rviz
```

The launch file starts:

```txt
sim_node
robot_state_publisher
joint_state_publisher
rviz2
```

## RViz Displays

The Day 75 RViz config includes:

```txt
Grid
TF
RobotModel
Odometry
```

Fixed frame:

```txt
odom
```

Robot description source:

```txt
/robot_description
```

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

Second terminal:

```bash
ros2 node list

ros2 topic list | grep -E "/cmd_vel|/robot_pose|/odom|/tf|/tf_static|/joint_states|/robot_description"

ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
ros2 run tf2_ros tf2_echo base_link caster_link
```

Motion test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.4}}"
```

Expected behavior:

```txt
RViz displays the robot body, wheels, caster, TF frames, and odometry.
The robot moves relative to odom when /cmd_vel is published.
```

## Interview Explanation

Day 75 integrated the robot model into RViz. The launch file brings up the simulator, robot description publishers, joint state publisher, and RViz together. RViz uses `odom` as the fixed frame, displays the RobotModel from `/robot_description`, and shows the TF tree and odometry output. This visually verifies that `sim_node` owns `odom -> base_link` while `robot_state_publisher` owns the robot structure below `base_link`.

---

# Day 76 — Gazebo / Ignition Spawn

## Goal

Spawn the differential-drive robot model into Gazebo Sim.

## Deliverable

Added:

```txt
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
ros2_ws/src/cpp_robotics_sim_ros/launch/gazebo_spawn.launch.py
```

The launch file starts:

```txt
Gazebo Sim
description.launch.py
spawn_diffbot from /robot_description
```

## World File

The Gazebo world includes:

```txt
empty_diffbot_world
physics system
user commands system
scene broadcaster system
sun light
ground plane
```

## Spawn Flow

```txt
gazebo_spawn.launch.py
    ↓
start Gazebo Sim with empty_diffbot_world.sdf
    ↓
start robot_state_publisher + joint_state_publisher through description.launch.py
    ↓
publish /robot_description from Xacro
    ↓
ros_gz_sim create spawns diffbot from /robot_description
```

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected:

```txt
Gazebo opens
ground plane appears
diffbot appears in the world
spawn_diffbot exits cleanly
```

Second terminal:

```bash
ros2 node list
ros2 topic list | grep -E "robot_description|joint_states|tf|clock"
gz topic -l | grep world
```

Expected ROS-side topics:

```txt
/robot_description
/joint_states
/tf
/tf_static
```

## Current Scope

Day 76 only proves that the robot can be spawned into Gazebo.

It does not yet implement:

```txt
ros2_control
differential drive plugin
/cmd_vel driving inside Gazebo
sensor simulation
Gazebo-to-ROS odometry bridge
```

Those are later days.

## Interview Explanation

Day 76 moved the project from RViz-only robot visualization into Gazebo-based simulation. I added a Gazebo world and a launch file that starts Gazebo Sim, publishes the Xacro-generated robot description, and spawns the differential-drive robot model into the physics simulator from `/robot_description`. This is the foundation for later `ros2_control`, differential-drive plugin integration, and sensor simulation.

---


# Day 77 — ros2_control Basics

## Goal

Add the foundation for controlling the Gazebo robot through the standard `ros2_control` framework.

## Deliverable

Added a `ros2_control` block to the Xacro model and a controller configuration file:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
ros2_ws/src/cpp_robotics_sim_ros/launch/ros2_control.launch.py
```

Day 77 did not focus on driving the robot yet. It focused on exposing the simulated wheel joints as control interfaces and proving that Gazebo can load the `controller_manager` stack.

## What Was Implemented

The Xacro model now contains a `ros2_control` system block:

```xml
<ros2_control name="DiffBotSystem" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>

  <joint name="left_wheel_joint">
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>

  <joint name="right_wheel_joint">
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
</ros2_control>
```

This means each wheel joint can receive a velocity command and report position and velocity state.

## Gazebo ros2_control Plugin

The Xacro model also loads the Gazebo ROS 2 Control plugin:

```xml
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <parameters>$(find cpp_robotics_sim_ros)/config/ros2_control.yaml</parameters>
  </plugin>
</gazebo>
```

This plugin connects Gazebo's simulated joints to ROS 2 control interfaces.

## Controller Configuration

Day 77 initially added `joint_state_broadcaster`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
```

## Launch Flow

The Day 77 launch stack starts:

```txt
Gazebo Sim
robot_state_publisher
spawn_diffbot
controller_manager from gz_ros2_control
joint_state_broadcaster spawner
```

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Second terminal:

```bash
ros2 node list
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic echo /joint_states --once
```

Expected controller:

```txt
joint_state_broadcaster active
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

## Debugging Notes

A library mismatch initially caused this error:

```txt
libcontroller_manager_msgs__rosidl_typesupport_fastrtps_cpp.so: undefined symbol
```

This was fixed by reinstalling the relevant ROS 2 Jazzy control and middleware packages.

A separate `No clock received` warning was caused by nodes using simulation time before `/clock` was bridged into ROS. This was fixed by adding a `/clock` bridge.

## Interview Explanation

Day 77 added the `ros2_control` foundation. The Xacro model now declares velocity command interfaces and position/velocity state interfaces for both wheel joints. Gazebo provides the simulated hardware through `gz_ros2_control/GazeboSimSystem`, and the `controller_manager` loads `joint_state_broadcaster` to publish joint states from the simulated hardware interfaces. This is the standard path used to connect ROS 2 controllers to simulated or real robot hardware.

---

# Day 78 — Gazebo Differential-Drive Control

## Goal

Connect body velocity commands to wheel motion in Gazebo using `diff_drive_controller`.

## Deliverable

The Gazebo robot now drives from a ROS 2 velocity command topic.

Updated:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
ros2_ws/src/cpp_robotics_sim_ros/launch/ros2_control.launch.py
ros2_ws/src/cpp_robotics_sim_ros/package.xml
```

## Controller Configuration

The controller YAML now defines both controllers:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

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
    publish_limited_velocity: true

    cmd_vel_timeout: 0.5
    use_stamped_vel: true

    linear.x.has_velocity_limits: true
    linear.x.max_velocity: 0.5
    linear.x.min_velocity: -0.5

    angular.z.has_velocity_limits: true
    angular.z.max_velocity: 1.0
    angular.z.min_velocity: -1.0
```

Important YAML lesson:

```txt
The second diff_drive_controller block must be top-level, aligned with controller_manager.
```

If it is nested under `controller_manager`, the controller loads without its parameters and fails because wheel names are empty.

## Control Chain

```txt
/diff_drive_controller/cmd_vel
        ↓
diff_drive_controller
        ↓
left_wheel_joint velocity command
right_wheel_joint velocity command
        ↓
gz_ros2_control
        ↓
Gazebo simulated wheel joints
        ↓
robot moves in Gazebo
        ↓
/diff_drive_controller/odom and /tf publish robot motion
```

## Differential-Drive Math

For wheel radius `r` and wheel separation `L`:

```txt
v = r / 2 * (wr + wl)
omega = r / L * (wr - wl)
```

Inverse mapping:

```txt
wr = (v + omega * L / 2) / r
wl = (v - omega * L / 2) / r
```

Where:

```txt
v      = robot forward velocity
omega  = robot yaw velocity
wr     = right wheel angular velocity
wl     = left wheel angular velocity
r      = wheel radius
L      = distance between left and right wheels
```

`diff_drive_controller` performs this conversion internally.

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Second terminal:

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic list | grep diff_drive
```

Expected controllers:

```txt
joint_state_broadcaster active
diff_drive_controller active
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

Expected behavior:

```txt
robot moves in Gazebo
wheel joints rotate
/diff_drive_controller/odom updates
```

## Interview Explanation

Day 78 added the differential-drive controller. The controller receives a `TwistStamped` body velocity command, converts the requested linear and angular velocity into left and right wheel velocity commands, sends those commands through `ros2_control`, and Gazebo applies them to the simulated wheel joints. The controller also publishes odometry and, with `enable_odom_tf: true`, publishes the moving `odom -> base_link` transform.

---

# Day 79 — Sensor Modeling

## Goal

Add a simulated sensor and validate that its ROS topic output is visible and usable.

## Deliverable

Added a simulated 2D lidar to the Gazebo robot and bridged it into ROS as:

```txt
/scan
```

Message type:

```txt
sensor_msgs/msg/LaserScan
```

Updated:

```txt
ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro
ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
ros2_ws/src/cpp_robotics_sim_ros/launch/ros2_control.launch.py
```

## Lidar Robot Model

The Xacro model now includes:

```txt
lidar_link
lidar_joint fixed from base_link to lidar_link
```

The lidar is mounted on the robot body, above and slightly forward of `base_link`.

Expected transform:

```txt
base_link -> lidar_link
```

## Gazebo Sensor

A Gazebo `gpu_lidar` sensor is attached to `lidar_link`.

The sensor publishes a Gazebo LaserScan topic:

```txt
/scan
```

The lidar uses:

```txt
360 horizontal samples
full 360 degree scan
minimum range around 0.08 m
maximum range around 8.0 m
10 Hz update rate
```

## World File

The world file now contains:

```txt
physics system
user commands system
scene broadcaster system
sensors system
sun light
ground plane
scan obstacle boxes
```

The obstacle boxes provide visible objects for the lidar to detect.

## Bridge Flow

```txt
Gazebo gpu_lidar sensor
        ↓
Gazebo /scan topic
        ↓
ros_gz_bridge parameter_bridge
        ↓
ROS /scan topic
        ↓
sensor_msgs/msg/LaserScan
        ↓
RViz LaserScan display
```

The launch file adds:

```txt
/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan
```

## Sim Time Lesson

RViz initially showed `TF_OLD_DATA` warnings and the robot appeared stationary even while Gazebo moved.

Cause:

```txt
RViz and Gazebo/controller stack were not using the same time source.
```

Fix:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Also ensure `/clock` is bridged:

```txt
/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock
```

## Validation Commands

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Second terminal:

```bash
ros2 topic list | grep scan
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 topic echo /diff_drive_controller/odom --once
```

Expected:

```txt
/scan
sensor_msgs/msg/LaserScan
lidar_link TF exists
/diff_drive_controller/odom publishes
```

RViz setup:

```txt
Fixed Frame: odom
RobotModel: /robot_description
Odometry: /diff_drive_controller/odom
LaserScan: /scan
LaserScan Reliability Policy: Best Effort if needed
```

Drive command:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Expected behavior:

```txt
robot moves in Gazebo
robot moves in RViz
LaserScan appears in RViz
LaserScan changes relative to obstacles as the robot moves
```

## Git Lesson

The Gazebo world file was accidentally ignored by `.gitignore` because of an SDF ignore rule.

Fix:

```bash
git check-ignore -v ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
git add -f ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf
```

Long-term fix:

```gitignore
!ros2_ws/src/cpp_robotics_sim_ros/worlds/
!ros2_ws/src/cpp_robotics_sim_ros/worlds/*.sdf
```

## Interview Explanation

Day 79 added sensor modeling to the Gazebo robot. I added a `lidar_link` and fixed transform from `base_link`, attached a Gazebo `gpu_lidar` sensor to that link, enabled the Gazebo sensors system in the world file, added obstacles for scan returns, and bridged Gazebo's LaserScan output into ROS as `/scan`. RViz visualizes the `/scan` topic together with the robot model, odometry, and TF. I also fixed a sim-time mismatch so RViz and Gazebo use the same `/clock` source.

---

# Day 80 — Robot Modeling Review and Interview Preparation

## Goal

Review and document the full robot modeling and simulation stack from Days 71-79.

## Deliverable

Day 80 is not a new feature day. It is a consolidation day.

The goal is to be able to explain:

```txt
URDF
Xacro
robot_description
robot_state_publisher
joint_state_publisher
joint_state_broadcaster
TF and TF ownership
RViz
Gazebo
ros2_control
controller_manager
gz_ros2_control
diff_drive_controller
ros_gz_sim
ros_gz_bridge
LaserScan sensor flow
sim time and /clock
```

## System Architecture Through Day 80

```txt
Xacro robot model
        ↓
robot_description
        ↓
robot_state_publisher
        ↓
TF tree below base_link

Gazebo world + spawned robot
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

Gazebo gpu_lidar
        ↓
ros_gz_bridge
        ↓
/scan
        ↓
RViz LaserScan display
```

## RViz vs Gazebo

RViz is a ROS visualization and debugging tool. It visualizes data that already exists on ROS topics and TF.

Gazebo is a physics simulator. It simulates worlds, rigid bodies, joints, contacts, sensors, and plugins.

In this project:

```txt
Gazebo simulates the robot and lidar.
ros2_control sends controller commands to Gazebo joints.
RViz visualizes robot state, TF, odometry, and scan data.
```

RViz does not cause the robot to move. Gazebo physics and controllers cause the robot to move.

## Who Talks to What

| Component | Talks To | Purpose |
|---|---|---|
| `diffbot.xacro` | `robot_state_publisher`, Gazebo spawn, `gz_ros2_control` | Defines robot links, joints, sensors, and control interfaces |
| `robot_state_publisher` | `/robot_description`, `/joint_states`, `/tf`, `/tf_static` | Publishes link transforms from the robot model |
| `ros_gz_sim create` | `/robot_description`, Gazebo world | Spawns robot entity into Gazebo |
| `gz_ros2_control` | Gazebo joints, `controller_manager` | Exposes simulated joints as ROS 2 control hardware |
| `controller_manager` | controllers, hardware interfaces | Loads and manages controllers |
| `joint_state_broadcaster` | hardware state interfaces, `/joint_states` | Publishes wheel joint states |
| `diff_drive_controller` | `/diff_drive_controller/cmd_vel`, wheel interfaces, `/odom`, `/tf` | Converts body velocity into wheel commands and publishes odometry |
| `ros_gz_bridge` | Gazebo Transport, ROS topics | Bridges `/clock` and `/scan` into ROS |
| RViz | `/robot_description`, `/tf`, `/odom`, `/scan` | Visualizes robot model, transforms, odometry, and lidar |
| Gazebo | world SDF, robot model, plugins | Simulates physics, joints, and sensors |

## Control Ownership

Standalone ROS simulator stack:

```txt
sim_node owns odom -> base_link
```

Gazebo control stack:

```txt
diff_drive_controller owns odom -> base_link
robot_state_publisher owns base_link -> robot links
joint_state_broadcaster owns /joint_states
```

Do not run `sim_node` inside the Gazebo control stack, or TF ownership becomes confusing.

## Hard Concepts Learned

### URDF vs Xacro

URDF is the robot description format.

Xacro is a macro/preprocessor system that generates URDF.

Use URDF for static reference models. Use Xacro for maintainable, parameterized robot descriptions.

### joint_state_publisher vs joint_state_broadcaster

`joint_state_publisher` is useful for simple visualization without real hardware or a control stack.

`joint_state_broadcaster` belongs to `ros2_control`. It reads actual state interfaces from hardware or simulated hardware and publishes `/joint_states`.

### Gazebo plugin vs ros2_control controller

A Gazebo plugin runs inside the Gazebo simulation environment.

A ros2_control controller runs through `controller_manager` and commands hardware interfaces.

`gz_ros2_control` connects these two worlds.

### Bridge vs Publisher

A normal ROS publisher publishes directly to a ROS topic.

A bridge converts messages between Gazebo Transport and ROS 2.

`/scan` exists in Gazebo first, then `ros_gz_bridge` converts it into ROS `sensor_msgs/msg/LaserScan`.

### Clock and Sim Time

Gazebo uses simulation time. ROS nodes and RViz must use `/clock` when `use_sim_time` is true.

If RViz uses wall time while Gazebo uses sim time, TF errors such as `TF_OLD_DATA` can appear.

## Final Day 80 Interview Explanation

I built a differential-drive robot simulation stack in ROS 2 and Gazebo. The robot is described in Xacro with links, joints, inertial properties, collision geometry, visual geometry, ros2_control interfaces, and a lidar sensor. The Xacro is converted into `robot_description`, which is consumed by `robot_state_publisher` and by the Gazebo spawn process. Gazebo simulates the robot in a physics world. The `gz_ros2_control` plugin exposes the simulated wheel joints as ros2_control hardware interfaces. `controller_manager` loads `joint_state_broadcaster` and `diff_drive_controller`. The broadcaster publishes `/joint_states`; the diff-drive controller receives velocity commands, converts body velocity into wheel velocity commands, moves the simulated wheel joints, and publishes odometry and TF. A Gazebo lidar sensor publishes scan data, which is bridged into ROS as `/scan` using `ros_gz_bridge`. RViz visualizes the robot model, TF tree, odometry, and lidar scan using simulation time from `/clock`.

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
ros2 topic info /diagnostics --verbose
```

Expected for `/cmd_vel`, `/robot_pose`, `/odom`, and `/diagnostics`:

```txt
Reliability: RELIABLE
Durability: VOLATILE
```

## Diagnostics Checks

```bash
ros2 topic list | grep diagnostics
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

Expected topic:

```txt
/diagnostics
```

Expected message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Expected health states:

```txt
OK   when fresh /cmd_vel commands are being received
WARN when cmd_vel timeout is active
```

## Robot Description Checks

Launch robot description stack:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
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

Check static transform:

```bash
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Expected static transform:

```txt
base_link -> caster_link
```

Check wheel transforms:

```bash
ros2 run tf2_ros tf2_echo base_link left_wheel_link
ros2 run tf2_ros tf2_echo base_link right_wheel_link
```

## RViz RobotModel Checks

Launch the full robot visualization stack:

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

Expected RViz setup:

```txt
Fixed Frame: odom
Displays: Grid, TF, RobotModel, Odometry
RobotModel Source: /robot_description
Odometry Topic: /odom
```

Expected frame tree:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      └── caster_link
```

## Gazebo Spawn Checks

Launch Gazebo spawn workflow:

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

Expected behavior:

```txt
Gazebo Sim opens
ground plane appears
diffbot appears in the world
spawn_diffbot exits cleanly
```

Check Gazebo topics:

```bash
gz topic -l | grep world
```

## Gazebo Control and Lidar Checks

Launch the Gazebo control stack:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Check controllers:

```bash
ros2 control list_controllers
```

Expected:

```txt
joint_state_broadcaster active
diff_drive_controller active
```

Check sensor output:

```bash
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Expected:

```txt
/scan is sensor_msgs/msg/LaserScan
lidar_link exists in TF
```

Drive robot in Gazebo:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Expected:

```txt
robot moves in Gazebo
robot moves in RViz when RViz uses sim time
/diff_drive_controller/odom updates
/scan remains active
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

## RViz2 Checks

Open RViz from source config:

```bash
rviz2 -d src/cpp_robotics_sim_ros/rviz/sim_debug.rviz
```

Open RViz from installed config:

```bash
rviz2 -d "$(ros2 pkg prefix cpp_robotics_sim_ros)/share/cpp_robotics_sim_ros/rviz/sim_debug.rviz"
```

Expected RViz setup:

```txt
Fixed Frame: odom
Displays: Grid, TF, Odometry
Odometry Topic: /odom
```

Motion test:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Expected behavior:

```txt
base_link moves relative to odom
TF display updates
Odometry display updates
```

## Launch Regression Check

Run the automated regression script from the repository root:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
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

|  Day | Status   | Main Deliverable                            |
| ---: | -------- | ------------------------------------------- |
| 1-60 | Complete | Standalone C++ + ROS 2 simulator foundation |
|   61 | Complete | ROS 2 launch file                           |
|   62 | Complete | YAML parameter config                       |
|   63 | Complete | Launch argument overrides                   |
|   64 | Complete | Explicit QoS profiles                       |
|   65 | Complete | rosbag2 recording and replay workflow       |
|   66 | Complete | RViz2 visualization config                  |
|   67 | Complete | Runtime diagnostics on `/diagnostics`       |
|   68 | Complete | Launch regression script                    |
|   69 | Complete | ROS 2 usage quickstart documentation        |
|   70 | Complete | ROS 2 topic interface reference             |
|   71 | Complete | Static differential-drive URDF model        |
|   72 | Complete | Parameterized Xacro robot description       |
|   73 | Complete | `robot_state_publisher` launch workflow     |
|   74 | Complete | `joint_state_publisher` integration         |
|   75 | Complete | RViz RobotModel visualization               |
|   76 | Complete | Gazebo Sim world and robot spawn workflow   |
|   77 | Complete | `ros2_control` hardware interface foundation |
|   78 | Complete | Gazebo differential-drive controller motion |
|   79 | Complete | Simulated lidar sensor and `/scan` bridge   |
|   80 | Complete | Robot modeling review and interview prep    |

Next planned day:

```txt
Day 81 - Nav2 concepts and architecture
```
