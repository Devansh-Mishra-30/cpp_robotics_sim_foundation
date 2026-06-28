# C++ / ROS 2 Robotics Simulation Foundation

This repository contains a C++ and ROS 2 robotics simulation project focused on mobile robot state updates, differential-drive kinematics, ROS 2 messaging, odometry, TF frames, runtime configuration, launch workflows, QoS profiles, rosbag2, diagnostics, RViz visualization, URDF/Xacro robot modeling, Gazebo simulation, `ros2_control`, differential-drive control, simulated lidar, validation, and engineering documentation.

The project started as a standalone C++ robotics simulation foundation and has been extended into a ROS 2 + Gazebo robot simulation stack with robot description, physics-based motion, controller integration, and sensor output.

---

## Project Structure

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

Main layers:

```txt
standalone_cpp/  -> Pure C++ robotics simulation modules
ros2_ws/         -> ROS 2 simulator, robot model, Gazebo, ros2_control, RViz, and sensor integration
scripts/         -> Regression and validation scripts
docs/            -> Architecture, debugging, validation, topic interface, and daily documentation
```

---

## Quickstart: Build

From the ROS 2 workspace:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Expected:

```txt
Summary: 1 package finished
```

---

## Quickstart: Original ROS 2 Kinematic Simulator

Launch the custom C++ simulator:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Expected node:

```txt
/sim_node
```

Expected runtime interfaces:

```txt
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

Send a command from a second terminal:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

Inspect state:

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

Expected behavior:

```txt
robot pose updates
/odom publishes updated state
/tf updates odom -> base_link
/diagnostics reports OK while commands are fresh
robot stops after cmd_timeout when commands stop
```

---

## Quickstart: Gazebo Control and Lidar Stack

Launch the Gazebo physics simulation, `ros2_control`, diff-drive controller, and lidar bridge:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Expected:

```txt
Gazebo opens
diffbot spawns
controller_manager starts
joint_state_broadcaster becomes active
diff_drive_controller becomes active
/scan publishes LaserScan data
```

Validate controllers:

```bash
ros2 control list_controllers
```

Expected:

```txt
joint_state_broadcaster active
diff_drive_controller active
```

Validate hardware interfaces:

```bash
ros2 control list_hardware_interfaces
```

Expected wheel interfaces include:

```txt
left_wheel_joint/velocity command interface
right_wheel_joint/velocity command interface
left_wheel_joint/position state interface
left_wheel_joint/velocity state interface
right_wheel_joint/position state interface
right_wheel_joint/velocity state interface
```

Drive the Gazebo robot:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Check controller odometry:

```bash
ros2 topic echo /diff_drive_controller/odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

Check lidar:

```bash
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Expected:

```txt
/scan is sensor_msgs/msg/LaserScan
lidar_link exists in TF
robot moves in Gazebo
/diff_drive_controller/odom updates
```

---

## RViz for Gazebo Control Stack

When visualizing Gazebo-driven data, RViz must use simulation time.

Start RViz with:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

Recommended RViz displays:

```txt
Grid
TF
RobotModel
Odometry
LaserScan
```

Recommended settings:

```txt
Fixed Frame: odom
RobotModel Description Topic: /robot_description
Odometry Topic: /diff_drive_controller/odom
LaserScan Topic: /scan
LaserScan Reliability Policy: Best Effort if needed
```

If RViz shows stale TF errors such as:

```txt
TF_OLD_DATA ignoring data from the past for frame base_link
```

cleanly stop old Gazebo/RViz/ROS processes, relaunch the Gazebo control stack, verify `/clock`, and reopen RViz with `use_sim_time:=true`.

---

## Robot Model, RViz RobotModel, and Gazebo Usage

Robot description files:

```txt
ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf
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

Launch robot description stack:

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Expected nodes:

```txt
/robot_state_publisher
/joint_state_publisher
```

Expected topics:

```txt
/robot_description
/joint_states
/tf
/tf_static
```

Launch RViz RobotModel stack:

```bash
ros2 launch cpp_robotics_sim_ros robot_model_viz.launch.py
```

This starts the original kinematic simulator, robot description publishers, joint state publisher, and RViz.

Launch Gazebo spawn-only workflow:

```bash
ros2 launch cpp_robotics_sim_ros gazebo_spawn.launch.py
```

This proves that the robot model can be spawned into Gazebo from `/robot_description`.

Launch Gazebo control workflow:

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

This starts Gazebo, spawns the robot, loads `controller_manager`, activates `joint_state_broadcaster` and `diff_drive_controller`, bridges `/clock`, and bridges lidar data into `/scan`.

---

## Transform Ownership

The project has two related runtime stacks. The transform owner changes depending on which stack is running.

Kinematic simulator stack:

```txt
sim_node owns:
  odom -> base_link

robot_state_publisher owns:
  base_link -> left_wheel_link
  base_link -> right_wheel_link
  base_link -> caster_link
  base_link -> lidar_link
```

Gazebo control stack:

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

Full frame tree through Day 80:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

---

## Gazebo, ros2_control, and Lidar Architecture

Gazebo control flow:

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

Lidar sensor flow:

```txt
Gazebo gpu_lidar sensor on lidar_link
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

Clock flow:

```txt
Gazebo simulation clock
        ↓
ros_gz_bridge
        ↓
ROS /clock
        ↓
RViz and ROS nodes using use_sim_time
```

---

## Differential-Drive Math

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

The custom C++ simulator uses planar kinematic pose integration. The Gazebo control stack uses `diff_drive_controller` to convert body velocity commands into wheel joint velocity commands.

---

## Runtime Configuration

Original simulator parameters are stored in:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

Current simulator parameters:

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

Gazebo controller parameters are stored in:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
```

Core controller configuration:

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
```

---

## ROS 2 Topics Through Day 80

| Topic | Type | Producer | Purpose |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | external command source | Velocity command input for `sim_node` |
| `/robot_pose` | `geometry_msgs/msg/Pose2D` | `sim_node` | Simple 2D robot pose |
| `/odom` | `nav_msgs/msg/Odometry` | `sim_node` | Kinematic simulator odometry |
| `/tf` | `tf2_msgs/msg/TFMessage` | `sim_node`, `robot_state_publisher`, `diff_drive_controller` | Transform tree data |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | `robot_state_publisher` | Fixed transform tree data |
| `/diagnostics` | `diagnostic_msgs/msg/DiagnosticArray` | `sim_node` | Runtime health and simulator diagnostics |
| `/robot_description` | `std_msgs/msg/String` | `robot_state_publisher` | Robot model XML |
| `/joint_states` | `sensor_msgs/msg/JointState` | `joint_state_publisher` or `joint_state_broadcaster` | Joint positions/velocities for robot links |
| `/dynamic_joint_states` | `control_msgs/msg/DynamicJointState` | `joint_state_broadcaster` | Detailed ros2_control joint interface states |
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/msg/TwistStamped` | command source | Gazebo diff-drive command input |
| `/diff_drive_controller/odom` | `nav_msgs/msg/Odometry` | `diff_drive_controller` | Gazebo diff-drive odometry |
| `/diff_drive_controller/cmd_vel_out` | `geometry_msgs/msg/TwistStamped` | `diff_drive_controller` | Limited command output |
| `/scan` | `sensor_msgs/msg/LaserScan` | `ros_gz_bridge` from Gazebo lidar | Simulated lidar scan |
| `/clock` | `rosgraph_msgs/msg/Clock` | `ros_gz_bridge` from Gazebo | Simulation time |

---

## Standalone C++ Modules

The standalone C++ project is split into two main simulation modules.

Differential-drive module:

```txt
standalone_cpp/include/differential_drive/
standalone_cpp/src/differential_drive/
```

This module contains the differential-drive mobile robot simulation, including wheel-speed conversion, pose updates, trajectory metrics, validation scenarios, and target tracking.

Manipulator module:

```txt
standalone_cpp/include/manipulator/
standalone_cpp/src/manipulator/
```

This module contains the manipulator joint-state simulation, including joint position updates, joint velocity integration, and joint limit clamping.

`standalone_cpp/src/main.cpp` is the combined demo runner that executes both the differential-drive and manipulator demos.

---

## Diagnostics

The original simulator publishes structured runtime diagnostics on:

```txt
/diagnostics
```

Message type:

```txt
diagnostic_msgs/msg/DiagnosticArray
```

Check diagnostics:

```bash
ros2 topic echo --once /diagnostics
ros2 topic info /diagnostics --verbose
```

The diagnostic report includes:

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

Diagnostic status:

```txt
OK   when simulator is running with fresh command input
WARN when cmd_vel timeout is active
```

---

## rosbag2 Recording and Replay

Record simulator topics:

```bash
mkdir -p bags
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

Expected recorded topics:

```txt
/cmd_vel
/robot_pose
/odom
/tf
```

Actual bag data is stored locally under `bags/` and should not be committed to Git.

---

## Launch Regression

The project includes a repeatable launch regression script:

```txt
scripts/day68_launch_regression.sh
```

Run it from the repository root:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

Expected:

```txt
========== PASS: Day 68 launch regression succeeded ==========
```

The regression validates the original ROS 2 kinematic simulator stack and should still pass after Gazebo, control, and sensor changes.

---

## Verification Workflow

Use this after meaningful source, launch, config, robot description, world, controller, sensor, or documentation changes.

### Build

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

### Original Simulator Checks

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
ros2 topic list
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

### Robot Description Checks

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py

ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt
grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt

ros2 topic echo /joint_states --once
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

### Gazebo Control and Sensor Checks

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py

ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 topic echo /diff_drive_controller/odom --once
ros2 topic type /scan
ros2 topic echo /scan --once
ros2 topic echo /clock --once
ros2 run tf2_ros tf2_echo base_link lidar_link
```

Drive test:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.0}}}"
```

Expected:

```txt
robot moves in Gazebo
/diff_drive_controller/odom updates
/scan remains active
RViz tracks Gazebo motion when use_sim_time is true
```

### Regression Check

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics"
./scripts/day68_launch_regression.sh
```

---

## Documentation

Additional documentation:

```txt
docs/daily_documentation.md
docs/system_architecture.md
docs/debugging_and_validation.md
docs/topic_interface_reference.md
```

The documentation tracks the roadmap from C++ fundamentals through ROS 2 launch, YAML parameters, launch arguments, QoS profiles, rosbag2, RViz2, diagnostics, regression, URDF/Xacro robot modeling, robot state publishing, Gazebo spawning, `ros2_control`, differential-drive controller integration, simulated lidar, `/scan` bridging, and Day 80 interview review.

---

## Engineering Focus

This project demonstrates:

* robotics simulation architecture
* C++ simulation design
* differential-drive kinematics
* manipulator joint-state simulation
* ROS 2 C++ node development
* topic-based robot control
* odometry publishing
* TF frame broadcasting
* diagnostics publishing
* launch-based runtime workflows
* YAML runtime configuration
* launch argument overrides
* QoS profile design
* rosbag2 recording and replay
* RViz2 visual debugging
* RViz RobotModel visualization
* launch regression testing
* URDF robot modeling
* Xacro robot modeling
* robot state publishing
* joint state publishing
* Gazebo world setup
* Gazebo robot spawning
* `ros2_control` hardware interface design
* `controller_manager` workflow
* `joint_state_broadcaster` integration
* `diff_drive_controller` integration
* Gazebo differential-drive motion
* simulated lidar sensor modeling
* `/scan` bridging with `ros_gz_bridge`
* `/clock` and simulation-time synchronization
* parameterized runtime behavior
* safety guards
* debugging discipline
* performance timing
* regression testing
* portfolio-ready engineering documentation

---

## Current Status

| Area | Status |
|---|---|
| Standalone C++ simulator | Complete foundation |
| ROS 2 node integration | Complete foundation |
| Launch workflow | Added |
| YAML configuration | Added |
| Launch argument overrides | Added |
| QoS profiles | Added |
| rosbag2 workflow | Added |
| RViz2 odometry/TF visualization | Added |
| Diagnostics | Added |
| Launch regression | Added |
| Topic interface reference | Added |
| URDF robot model | Added |
| Xacro robot description | Added |
| `robot_state_publisher` workflow | Added |
| `joint_state_publisher` workflow | Added |
| RViz RobotModel visualization | Added |
| Gazebo world and robot spawn | Added |
| `ros2_control` integration | Added |
| `joint_state_broadcaster` integration | Added |
| Gazebo differential-drive control | Added |
| `diff_drive_controller` odometry | Added |
| Simulated lidar sensor | Added |
| `/scan` LaserScan bridge | Added |
| `/clock` simulation-time bridge | Added |
| Day 80 robot modeling review | Added |
| Nav2 integration | Planned |
| SLAM/localization | Planned |
| Automated tests and CI | Planned |

Next planned milestone:

```txt
Day 81 - Nav2 concepts and architecture
```

---

## Day 80 Interview Summary

I built a modular C++ robotics simulation foundation with standalone differential-drive and manipulator modules, then integrated the mobile robot simulator into ROS 2 using `/cmd_vel`, `/robot_pose`, `/odom`, TF, and `/diagnostics`. I extended the project into a robot modeling and simulation stack with URDF, Xacro, `robot_state_publisher`, joint state publishing, RViz RobotModel visualization, Gazebo spawning, `ros2_control` hardware interfaces, `controller_manager`, `joint_state_broadcaster`, `diff_drive_controller`, Gazebo-driven wheel motion, simulated lidar, `/scan` bridging through `ros_gz_bridge`, and simulation-time synchronization through `/clock`.

In the custom kinematic simulator stack, `sim_node` owns `odom -> base_link`. In the Gazebo control stack, `diff_drive_controller` owns `odom -> base_link`, `joint_state_broadcaster` owns `/joint_states`, `robot_state_publisher` owns the robot link transforms below `base_link`, and RViz visualizes the resulting robot model, odometry, TF, and lidar data.
