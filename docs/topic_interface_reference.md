# Topic and Interface Reference — C++ / ROS 2 Robotics Simulation Foundation

This document defines the public runtime interface contract for the `cpp_robotics_sim_ros` package through the Day 100 Nav2 integration checkpoint.

It covers the ROS 2 topics, actions, services, frames, parameters, scripts, generated artifacts, and validation commands used by the standalone C++ simulator, ROS 2 kinematic simulator, Gazebo/`ros2_control` robot stack, sensor stack, validation tooling, and Nav2 odom-frame navigation stack.

The goal is simple: another engineer should be able to understand what each component publishes, subscribes to, commands, validates, and records without reading the whole codebase first.

---

## 1. Current Day 100 Interface Scope

The project currently exposes four major interface groups.

```txt
1. Original ROS 2 kinematic simulator interfaces
2. Gazebo + ros2_control differential-drive robot interfaces
3. Validation, testing, benchmarking, and rosbag evidence interfaces
4. Nav2 navigation interfaces through Day 100
```

The current public documentation set is intended to be:

```txt
README.md

docs/
  system_architecture.md
  topic_interface_reference.md
  debugging_and_validation.md

scripts/
  hard_reset.sh
```

The older day-specific documentation can be deleted after its useful content is consolidated into these reference documents.

---

## 2. High-Level Runtime Interface Map

### 2.1 Original Kinematic Simulator Stack

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

This stack is useful for validating basic ROS 2 node behavior, planar kinematics, command timeout logic, velocity clamping, odometry, TF, diagnostics, launch files, YAML parameters, QoS, and rosbag workflows.

### 2.2 Gazebo ros2_control Stack

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
/diff_drive_controller/cmd_vel_out
/tf
/joint_states
```

This is the physics-based control stack. It moves the robot in Gazebo.

### 2.3 Sensor Stack

```txt
Gazebo gpu_lidar
    ↓
Gazebo Transport /scan
    ↓
ros_gz_bridge
    ↓
ROS 2 /scan
```

This stack exposes the simulated lidar as `sensor_msgs/msg/LaserScan` for RViz, Nav2 costmaps, and future SLAM/localization work.

### 2.4 Nav2 Odom-Frame Navigation Stack

```txt
NavigateToPose / NavigateThroughPoses action goal
    ↓
Nav2 bt_navigator
    ↓
planner_server + global_costmap
    ↓
controller_server + local_costmap
    ↓
/cmd_vel
    ↓
cmd_vel_twist_bridge.py
    ↓
/diff_drive_controller/cmd_vel
    ↓
diff_drive_controller
    ↓
Gazebo robot motion
```

Important Day 100 rule:

```txt
Nav2 currently runs in odom-frame mode.
There is no map -> odom localization chain yet.
SLAM, AMCL, and EKF localization are planned after the Day 100 Nav2 checkpoint.
```

---

## 3. Core Frame Contract

### 3.1 Current Frame Tree

The expected frame tree for the Gazebo/Nav2 stack is:

```txt
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

A temporary/static compatibility transform may also exist for the Gazebo scan frame:

```txt
lidar_link -> diffbot/base_link/diffbot_lidar
```

This was added because the bridged `/scan` header used the Gazebo-style frame:

```txt
frame_id: diffbot/base_link/diffbot_lidar
```

RViz and Nav2 costmaps require the scan frame to be connected to the TF tree.

### 3.2 Transform Ownership

| Transform / Interface | Owner in Kinematic Simulator Stack | Owner in Gazebo/Nav2 Stack |
|---|---|---|
| `odom -> base_link` | `sim_node` | `diff_drive_controller` |
| `base_link -> wheel links` | `robot_state_publisher` using `/joint_states` | `robot_state_publisher` using `/joint_states` |
| `/joint_states` | `joint_state_publisher` | `joint_state_broadcaster` |
| fixed robot links | `robot_state_publisher` | `robot_state_publisher` |
| scan compatibility frame | not used | static transform publisher |

Critical rule:

```txt
Do not run sim_node and diff_drive_controller as simultaneous publishers of odom -> base_link.
```

---

## 4. Topic Summary

### 4.1 Core Simulator and Robot Description Topics

| Topic | Type | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | CLI, teleop, Nav2 controller output | `sim_node` or bridge | Command input for original sim and Nav2 command stream |
| `/robot_pose` | `geometry_msgs/msg/Pose2D` | `sim_node` | CLI/debug tools | Simple 2D pose output for the kinematic simulator |
| `/odom` | `nav_msgs/msg/Odometry` | `sim_node` or odom relay/source depending launch | RViz, rosbag, debug tools | Standard odometry topic in simple stack; Nav2 may also expose/consume odom-frame data |
| `/tf` | `tf2_msgs/msg/TFMessage` | TF broadcasters | RViz, Nav2, TF tools | Dynamic transform tree |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | `robot_state_publisher`, static TF publishers | RViz, Nav2, TF tools | Fixed transforms |
| `/diagnostics` | `diagnostic_msgs/msg/DiagnosticArray` | `sim_node` | CLI/debug tools | Runtime health for original simulator |
| `/robot_description` | `std_msgs/msg/String` / parameter-backed | `robot_state_publisher` | RViz, Gazebo spawn, controller stack | Generated robot model XML |
| `/joint_states` | `sensor_msgs/msg/JointState` | `joint_state_publisher` or `joint_state_broadcaster` | `robot_state_publisher` | Joint state input for robot link transforms |
| `/dynamic_joint_states` | `control_msgs/msg/DynamicJointState` | `joint_state_broadcaster` | CLI/debug tools | Detailed `ros2_control` joint interface states |

### 4.2 Gazebo and Controller Topics

| Topic | Type | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/msg/TwistStamped` | CLI, bridge | `diff_drive_controller` | Stamped velocity command that moves Gazebo robot |
| `/diff_drive_controller/cmd_vel_out` | `geometry_msgs/msg/TwistStamped` | `diff_drive_controller` | CLI, rosbag, validation | Limited/smoothed command output from controller |
| `/diff_drive_controller/odom` | `nav_msgs/msg/Odometry` | `diff_drive_controller` | RViz, validation tools, Nav2/localization | Gazebo controller odometry |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo via bridge | ROS nodes using sim time, RViz | Simulation time source |
| `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo lidar via bridge | RViz, Nav2 costmaps, future SLAM | Simulated 2D lidar |

### 4.3 Noisy Odometry and Validation Topics

| Topic | Type | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `/odom_noisy` | `nav_msgs/msg/Odometry` | `noisy_odom_node.py` | validation recorder, future localization | Noisy odometry stream with covariance |
| `/diff_drive_controller/odom` | `nav_msgs/msg/Odometry` | `diff_drive_controller` | `noisy_odom_node.py`, recorder | Ground-truth-like controller odometry source |
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/msg/TwistStamped` | CLI/bridge | recorder, controller | Command evidence for trajectory validation |

### 4.4 Nav2 Topics

| Topic | Type | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Nav2 controller / velocity smoother | bridge, debug tools | Main Nav2 velocity output |
| `/cmd_vel_nav` | `geometry_msgs/msg/Twist` | Nav2 command path | velocity smoother / debug tools | Nav2 intermediate command stream |
| `/cmd_vel_smoothed` | `geometry_msgs/msg/Twist` | `velocity_smoother` | bridge or downstream command path | Smoothed velocity command stream |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz 2D/Nav2 Goal tool | Nav2 goal handling tools | RViz-published goal pose when using RViz goal tool |
| `/plan` | `nav_msgs/msg/Path` | `planner_server` | RViz, controller, rosbag | Global planned path |
| `/plan_smoothed` | `nav_msgs/msg/Path` | smoother server if used | RViz/controller/debug tools | Smoothed path output when active |
| `/local_plan` | `nav_msgs/msg/Path` | controller server | RViz/debug tools | Local controller trajectory/path |
| `/received_global_plan` | `nav_msgs/msg/Path` | controller server | RViz/debug tools | Global plan received by controller |
| `/transformed_global_plan` | `nav_msgs/msg/Path` | controller server | RViz/debug tools | Global plan transformed into local/controller frame |
| `/behavior_tree_log` | `nav2_msgs/msg/BehaviorTreeLog` | Nav2 behavior tree navigator | debug tools, rosbag | Behavior tree transition evidence |
| `/planner_selector` | selector-specific Nav2 message | Nav2 selector | Nav2 tools | Planner selection interface when enabled |

### 4.5 Nav2 Costmap Topics

| Topic | Type | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `/local_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | local costmap node | RViz, rosbag, debug tools | Local obstacle/costmap view |
| `/local_costmap/costmap_updates` | `map_msgs/msg/OccupancyGridUpdate` | local costmap node | RViz/debug tools | Incremental local costmap updates |
| `/local_costmap/published_footprint` | `geometry_msgs/msg/PolygonStamped` | local costmap node | RViz/debug tools | Robot footprint in local costmap context |
| `/local_costmap/footprint` | `geometry_msgs/msg/Polygon` or related costmap interface | costmap stack | costmap tools | Local footprint input/output interface |
| `/local_costmap/obstacle_layer` | `nav_msgs/msg/OccupancyGrid` | local costmap obstacle layer | RViz/debug tools | Local obstacle layer visualization |
| `/global_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | global costmap node | RViz, planner, rosbag | Global odom-frame costmap |
| `/global_costmap/costmap_updates` | `map_msgs/msg/OccupancyGridUpdate` | global costmap node | RViz/debug tools | Incremental global costmap updates |
| `/global_costmap/published_footprint` | `geometry_msgs/msg/PolygonStamped` | global costmap node | RViz/debug tools | Robot footprint in global costmap context |
| `/global_costmap/obstacle_layer` | `nav_msgs/msg/OccupancyGrid` | global costmap obstacle layer | RViz/debug tools | Global obstacle layer visualization |

Observed Day 98 rosbag evidence included nonzero costmap data for:

```txt
/global_costmap/costmap
/global_costmap/published_footprint
/local_costmap/costmap
/local_costmap/published_footprint
```

`costmap_updates` can have zero messages if full costmap publications are sufficient during the short run.

---

## 5. Action Interface Summary

Nav2 exposes action servers for planning, path following, single-goal navigation, and waypoint navigation.

| Action | Type | Owner | Purpose |
|---|---|---|---|
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | `planner_server` | Compute a global path to one goal pose |
| `/compute_path_through_poses` | `nav2_msgs/action/ComputePathThroughPoses` | `planner_server` | Compute a path through multiple poses |
| `/follow_path` | `nav2_msgs/action/FollowPath` | `controller_server` | Follow a provided path |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | `bt_navigator` | Full single-goal Nav2 task |
| `/navigate_through_poses` | `nav2_msgs/action/NavigateThroughPoses` | `bt_navigator` / waypoint behavior | Navigate through multiple goal poses |

Useful check:

```bash
ros2 action list -t | sort | grep -E "compute_path|follow_path|navigate"
```

Expected Day 100 core actions:

```txt
/compute_path_to_pose [nav2_msgs/action/ComputePathToPose]
/compute_path_through_poses [nav2_msgs/action/ComputePathThroughPoses]
/follow_path [nav2_msgs/action/FollowPath]
/navigate_to_pose [nav2_msgs/action/NavigateToPose]
/navigate_through_poses [nav2_msgs/action/NavigateThroughPoses]
```

---

## 6. Service Interface Summary

### 6.1 Nav2 Lifecycle Manager

| Service | Type | Purpose |
|---|---|---|
| `/lifecycle_manager_navigation/manage_nodes` | `nav2_msgs/srv/ManageLifecycleNodes` | Startup, activate, deactivate, reset, or shutdown Nav2 lifecycle nodes |

Manual activation command:

```bash
ros2 service call /lifecycle_manager_navigation/manage_nodes nav2_msgs/srv/ManageLifecycleNodes "{command: 2}"
```

This project includes a delayed lifecycle activation fallback in the Nav2 launch workflow because autostart did not always activate every Nav2 node reliably.

### 6.2 ros2_control Services

`controller_manager` exposes controller lifecycle and hardware service interfaces used by the `ros2 control` CLI.

Primary CLI checks:

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

Expected controllers in the Gazebo control stack:

```txt
joint_state_broadcaster active
diff_drive_controller active
```

### 6.3 ROS Parameter Services

Most ROS 2 nodes expose standard parameter services. This project uses them heavily for validation:

```bash
ros2 param get /controller_server controller_frequency
ros2 param get /controller_server FollowPath.max_vel_x
ros2 param get /local_costmap/local_costmap global_frame
ros2 param get /global_costmap/global_costmap robot_base_frame
```

---

## 7. Node Summary

| Node | Layer | Main Interfaces |
|---|---|---|
| `/sim_node` | original C++ kinematic simulator | subscribes `/cmd_vel`; publishes `/robot_pose`, `/odom`, `/tf`, `/diagnostics` |
| `/robot_state_publisher` | robot description | reads `robot_description` + `/joint_states`; publishes `/tf`, `/tf_static`, `/robot_description` |
| `/joint_state_publisher` | visualization-only robot model | publishes `/joint_states` |
| `/controller_manager` | `ros2_control` | owns controller lifecycle and hardware interfaces |
| `/diff_drive_controller` | controller | subscribes `/diff_drive_controller/cmd_vel`; publishes `/diff_drive_controller/odom`, `/diff_drive_controller/cmd_vel_out`, `/tf` |
| `/joint_state_broadcaster` | controller | publishes `/joint_states`, `/dynamic_joint_states` |
| `/parameter_bridge` | Gazebo-ROS bridge | bridges `/clock` and `/scan` |
| `/noisy_odom_node` | validation/localization readiness | subscribes `/diff_drive_controller/odom`; publishes `/odom_noisy` |
| `/trajectory_validation_recorder` | validation tooling | subscribes command/odom/noisy odom; writes CSV |
| `/cmd_vel_twist_bridge` | Nav2-to-controller bridge | subscribes `/cmd_vel`; publishes `/diff_drive_controller/cmd_vel` |
| `/planner_server` | Nav2 | owns path planning actions and `/plan` |
| `/controller_server` | Nav2 | owns `/follow_path`, local plan, command generation |
| `/bt_navigator` | Nav2 | owns `/navigate_to_pose`, `/navigate_through_poses` |
| `/behavior_server` | Nav2 | recovery behavior actions |
| `/velocity_smoother` | Nav2 | smooths Nav2 command velocities |
| `/local_costmap/local_costmap` | Nav2 | publishes local costmap topics |
| `/global_costmap/global_costmap` | Nav2 | publishes global costmap topics |
| `/waypoint_follower` | Nav2 | supports multi-pose/waypoint navigation |

---

## 8. Important Topic Details

## 8.1 `/cmd_vel`

Purpose:

```txt
Command input for the original simulator and the main Nav2 velocity command output.
```

Type:

```txt
geometry_msgs/msg/Twist
```

Used fields:

```txt
linear.x
angular.z
```

In the original simulator:

```txt
/cmd_vel -> sim_node -> /robot_pose, /odom, /tf, /diagnostics
```

In the Nav2/Gazebo stack:

```txt
Nav2 /cmd_vel -> cmd_vel_twist_bridge.py -> /diff_drive_controller/cmd_vel
```

Example check:

```bash
ros2 topic info /cmd_vel
ros2 topic echo /cmd_vel
```

---

## 8.2 `/diff_drive_controller/cmd_vel`

Purpose:

```txt
Stamped velocity command input that moves the Gazebo robot through diff_drive_controller.
```

Type:

```txt
geometry_msgs/msg/TwistStamped
```

Used fields:

```txt
header.stamp
header.frame_id
twist.linear.x
twist.angular.z
```

The bridge uses:

```txt
header.frame_id: base_link
```

Example direct command:

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

Validation:

```bash
ros2 topic info /diff_drive_controller/cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
```

Expected type:

```txt
geometry_msgs/msg/TwistStamped
```

---

## 8.3 `/diff_drive_controller/odom`

Purpose:

```txt
Odometry output from the Gazebo differential-drive controller.
```

Type:

```txt
nav_msgs/msg/Odometry
```

Expected frames:

```txt
header.frame_id: odom
child_frame_id: base_link
```

Used by:

```txt
RViz
noisy_odom_node.py
trajectory_validation_recorder.py
Nav2 odom-frame navigation
rosbag evidence
```

Validation:

```bash
ros2 topic echo --once /diff_drive_controller/odom
ros2 topic echo /diff_drive_controller/odom --field pose.pose.position
```

---

## 8.4 `/scan`

Purpose:

```txt
Simulated 2D lidar scan from Gazebo, bridged into ROS 2.
```

Type:

```txt
sensor_msgs/msg/LaserScan
```

Important fields:

```txt
header.frame_id
angle_min
angle_max
angle_increment
range_min
range_max
ranges
```

Validation:

```bash
ros2 topic list | grep scan
ros2 topic type /scan
ros2 topic echo --once /scan --field header
ros2 topic echo --once /scan
```

Important Day 93 lesson:

```txt
A LaserScan topic can publish valid ranges but still fail in RViz/costmaps if the scan frame is not connected to TF.
```

---

## 8.5 `/tf` and `/tf_static`

Purpose:

```txt
Provide transform relationships for robot state, visualization, sensor interpretation, and navigation.
```

Type:

```txt
tf2_msgs/msg/TFMessage
```

Checks:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable --once
```

Nav2 depends on a valid transform chain between:

```txt
odom
base_link
scan frame
```

---

## 8.6 `/plan`, `/local_plan`, and Controller Path Topics

Purpose:

```txt
Expose global and local planning evidence from Nav2.
```

Types:

```txt
nav_msgs/msg/Path
```

Important topics:

```txt
/plan
/local_plan
/received_global_plan
/transformed_global_plan
/plan_smoothed
```

Validation:

```bash
ros2 topic echo --once /plan
ros2 topic echo --once /local_plan
```

During Day 98 rosbag evidence, `/plan`, `/local_plan`, `/received_global_plan`, and `/transformed_global_plan` had nonzero message counts.

---

## 8.7 `/behavior_tree_log`

Purpose:

```txt
Records Nav2 behavior-tree transitions during navigation.
```

Type:

```txt
nav2_msgs/msg/BehaviorTreeLog
```

Useful for:

```txt
confirming goal execution
confirming recovery behavior
recording navigation evidence in rosbag2
```

Validation:

```bash
ros2 topic echo /behavior_tree_log
```

---

## 9. Parameter Interface Summary

### 9.1 Original Simulator Parameters

Node:

```txt
/sim_node
```

Parameters:

```txt
dt
initial_x
initial_y
initial_theta
cmd_timeout
max_linear_velocity
max_angular_velocity
```

Check:

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

### 9.2 diff_drive_controller Parameters

Configured in:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml
```

Important parameters:

```txt
left_wheel_names
right_wheel_names
wheel_separation
wheel_radius
odom_frame_id
base_frame_id
enable_odom_tf
publish_limited_velocity
cmd_vel_timeout
use_stamped_vel
linear.x.max_velocity
angular.z.max_velocity
```

Key interface rule:

```txt
use_stamped_vel: true
```

This is why `/diff_drive_controller/cmd_vel` expects `geometry_msgs/msg/TwistStamped`.

### 9.3 Nav2 Costmap Parameters

Nodes:

```txt
/local_costmap/local_costmap
/global_costmap/global_costmap
```

Expected Day 100 frame parameters:

```txt
global_frame: odom
robot_base_frame: base_link
```

Check:

```bash
ros2 param get /local_costmap/local_costmap global_frame
ros2 param get /local_costmap/local_costmap robot_base_frame
ros2 param get /global_costmap/global_costmap global_frame
ros2 param get /global_costmap/global_costmap robot_base_frame
```

### 9.4 Nav2 Controller Parameters

Node:

```txt
/controller_server
```

Important Day 94 parameters:

```txt
controller_frequency: 10.0
FollowPath.max_vel_x: 0.25
FollowPath.max_vel_theta: 0.6
FollowPath.acc_lim_x: 0.5
FollowPath.acc_lim_theta: 1.0
FollowPath.sim_time: 1.5
FollowPath.vx_samples: 20
FollowPath.vtheta_samples: 20
```

Check:

```bash
ros2 param get /controller_server controller_frequency
ros2 param get /controller_server FollowPath.max_vel_x
ros2 param get /controller_server FollowPath.max_vel_theta
ros2 param get /controller_server FollowPath.acc_lim_x
ros2 param get /controller_server FollowPath.acc_lim_theta
ros2 param get /controller_server FollowPath.sim_time
ros2 param get /controller_server FollowPath.vx_samples
ros2 param get /controller_server FollowPath.vtheta_samples
```

---

## 10. File and Artifact Interfaces

### 10.1 Core Source and Configuration Files

| File / Folder | Purpose |
|---|---|
| `standalone_cpp/` | Pure C++ simulation modules |
| `ros2_ws/src/cpp_robotics_sim_ros/src/sim_node.cpp` | Original ROS 2 kinematic simulator node |
| `ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro` | Maintainable robot model |
| `ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf` | Static reference robot model |
| `ros2_ws/src/cpp_robotics_sim_ros/worlds/empty_diffbot_world.sdf` | Gazebo world with obstacles |
| `ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml` | Original simulator parameters |
| `ros2_ws/src/cpp_robotics_sim_ros/config/ros2_control.yaml` | Controller manager and diff-drive controller parameters |
| `ros2_ws/src/cpp_robotics_sim_ros/nav2/diffbot_nav2_params.yaml` | Nav2 planner/controller/costmap parameters |

### 10.2 Launch Files

| Launch File | Purpose |
|---|---|
| `sim.launch.py` | Original kinematic simulator launch |
| `description.launch.py` | Robot description and state publisher launch |
| `robot_model_viz.launch.py` | RViz robot model visualization launch |
| `gazebo_spawn.launch.py` | Spawn robot in Gazebo |
| `ros2_control.launch.py` | Gazebo + ros2_control + controllers + sensors |
| `nav2_navigation.launch.py` | Full Gazebo + ros2_control + bridge + Nav2 navigation stack |

### 10.3 Runtime Scripts

| Script | Purpose |
|---|---|
| `scripts/hard_reset.sh` | Kill stale ROS/Gazebo/RViz processes before clean launch |
| `scripts/launch_regression.sh` | Original simulator launch regression |
| `cmd_vel_twist_bridge.py` | Convert Nav2 `/cmd_vel` Twist to controller TwistStamped |
| `noisy_odom_node.py` | Generate noisy odometry stream |
| `trajectory_validation_recorder.py` | Record command/actual/noisy data into CSV |
| `plot_trajectory_validation.py` | Generate validation plot and report |
| `nav2_lifecycle_check.sh` | Validate Nav2 lifecycle/action readiness |
| `nav2_costmap_check.sh` | Validate scan, costmaps, and frames |
| `nav2_planner_controller_check.sh` | Validate planner action and controller parameters |

### 10.4 Generated Artifacts

| Artifact | Purpose | Git Policy |
|---|---|---|
| `data/day84_trajectory_validation.csv` | Trajectory validation data | usually local/generated |
| `plots/trajectory_validation.png` | Validation plot | optional if useful for portfolio |
| `data/day88_performance_results.csv` | C++ benchmark results | generated/local unless intentionally committed |
| `bags/day98_nav2_goal_evidence/goal_run_01/` | rosbag2 Nav2 evidence | do not commit |
| `*.mcap` | rosbag2 MCAP storage file | do not commit |
| `*.db3` | rosbag2 SQLite storage file | do not commit |

Recommended `.gitignore` entries:

```gitignore
bags/
*.mcap
*.db3
```

---

## 11. Validation Script Interfaces

### 11.1 Lifecycle Check

Command:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
```

Expected:

```txt
DAY 92 LIFECYCLE CHECK: PASS
```

Validates:

```txt
/controller_server active
/smoother_server active
/planner_server active
/behavior_server active
/velocity_smoother active
/bt_navigator active
/waypoint_follower active
/navigate_to_pose action exists
/navigate_through_poses action exists
/lifecycle_manager_navigation/manage_nodes exists
```

### 11.2 Costmap Check

Command:

```bash
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
```

Expected:

```txt
DAY 93 COSTMAP CHECK: PASS
```

Validates:

```txt
local costmap node exists
global costmap node exists
/scan exists and publishes
/local_costmap/costmap publishes
/global_costmap/costmap publishes
footprint topics exist
local/global costmap frames are odom/base_link
odom -> base_link TF exists
```

### 11.3 Planner/Controller Check

Command:

```bash
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

Expected:

```txt
DAY 94 PLANNER/CONTROLLER CHECK: PASS
```

Validates:

```txt
planner actions exist
controller actions exist
ComputePathToPose succeeds
controller FollowPath parameters match expected tuning
```

---

## 12. Nav2 Command Interfaces

### 12.1 Compute a Path to a Pose

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{
  goal: {
    header: {frame_id: odom},
    pose: {
      position: {x: 0.8, y: 0.4, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  },
  planner_id: GridBased,
  use_start: false
}"
```

Expected:

```txt
Goal accepted
path.header.frame_id: odom
poses: non-empty
Goal finished with status: SUCCEEDED
error_code: 0
```

### 12.2 Navigate to One Goal

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: odom},
    pose: {
      position: {x: 0.8, y: -0.4, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: -0.3826834, w: 0.9238795}
    }
  },
  behavior_tree: ''
}"
```

Expected good signs:

```txt
Goal accepted
/cmd_vel publishes
/diff_drive_controller/cmd_vel publishes
/diff_drive_controller/odom changes
Robot moves in Gazebo
Goal finishes with SUCCEEDED
error_code: 0
```

### 12.3 Navigate Through Multiple Poses

```bash
ros2 action send_goal --feedback /navigate_through_poses nav2_msgs/action/NavigateThroughPoses "{
  poses: [
    {
      header: {frame_id: odom},
      pose: {
        position: {x: 0.5, y: 0.0, z: 0.0},
        orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
      }
    },
    {
      header: {frame_id: odom},
      pose: {
        position: {x: 0.8, y: -0.4, z: 0.0},
        orientation: {x: 0.0, y: 0.0, z: -0.3826834, w: 0.9238795}
      }
    },
    {
      header: {frame_id: odom},
      pose: {
        position: {x: 1.2, y: -0.6, z: 0.0},
        orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
      }
    }
  ],
  behavior_tree: ''
}"
```

Expected:

```txt
Goal accepted
number_of_poses_remaining decreases
/cmd_vel publishes
odom changes
Goal finishes with SUCCEEDED
```

---

## 13. rosbag2 Evidence Interface

### 13.1 Day 98 Bag

Folder:

```txt
bags/day98_nav2_goal_evidence/goal_run_01
```

Storage:

```txt
MCAP
```

Observed Day 98 evidence:

```txt
Files:      goal_run_01_0.mcap
Bag size:   3.4 MiB
Duration:   31.118688884s
Messages:   6809
Storage id: mcap
```

### 13.2 Record Command

```bash
ros2 bag record -o bags/day98_nav2_goal_evidence/goal_run_01 \
  /cmd_vel \
  /cmd_vel_nav \
  /cmd_vel_smoothed \
  /diff_drive_controller/cmd_vel \
  /diff_drive_controller/cmd_vel_out \
  /diff_drive_controller/odom \
  /odom \
  /tf \
  /tf_static \
  /scan \
  /goal_pose \
  /plan \
  /plan_smoothed \
  /local_plan \
  /received_global_plan \
  /transformed_global_plan \
  /local_costmap/costmap \
  /local_costmap/costmap_updates \
  /local_costmap/published_footprint \
  /global_costmap/costmap \
  /global_costmap/costmap_updates \
  /global_costmap/published_footprint \
  /behavior_tree_log
```

### 13.3 Inspect and Replay

Inspect the bag folder, not the `.mcap` file directly:

```bash
ros2 bag info bags/day98_nav2_goal_evidence/goal_run_01
```

Replay:

```bash
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock
```

Replay at slower speed if needed:

```bash
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock --rate 0.5
```

### 13.4 Day 98 Nonzero Evidence Counts

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

Note:

```txt
/goal_pose may not appear if the goal was sent through the /navigate_to_pose action instead of the RViz goal topic.
That is acceptable when the bag still records commands, odometry, TF, scan, costmaps, path topics, and behavior-tree logs.
```

---

## 14. Testing and CI Interfaces

### 14.1 GoogleTest Interface

Source files:

```txt
ros2_ws/src/cpp_robotics_sim_ros/include/cpp_robotics_sim_ros/core_math.hpp
ros2_ws/src/cpp_robotics_sim_ros/test/test_core_math.cpp
```

Validated functions:

```txt
clamp()
wrapToPi()
integratePose()
Pose2D
```

Command:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+
colcon test-result --verbose
```

Expected:

```txt
Summary: 17 tests, 0 errors, 0 failures, 0 skipped
```

### 14.2 GitHub Actions CI Interface

Workflow:

```txt
.github/workflows/ros2_jazzy_ci.yml
```

Current CI validates:

```txt
repository checkout
ROS 2 Jazzy dependency install
rosdep install
colcon build
GoogleTest execution
colcon test logs upload
```

Current CI does not yet validate:

```txt
Gazebo runtime launch
controller activation
/scan runtime checks
Nav2 runtime navigation
SLAM/localization behavior
full scenario scoring
```

### 14.3 Performance Benchmark Interface

Executable:

```txt
cpp_robotics_sim_ros performance_benchmark
```

Command:

```bash
ros2 run cpp_robotics_sim_ros performance_benchmark \
  --output data/day88_performance_results.csv \
  --report docs/performance_report.md
```

Outputs:

```txt
data/day88_performance_results.csv
docs/performance_report.md
```

Scope:

```txt
Deterministic C++ pose-update timing only.
Does not include Gazebo, Nav2, sensors, RViz, rosbag, or ROS middleware overhead.
```

---

## 15. Standard Interface Validation Checklist

After launching the Nav2 stack, run:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

Expected:

```txt
DAY 92 LIFECYCLE CHECK: PASS
DAY 93 COSTMAP CHECK: PASS
DAY 94 PLANNER/CONTROLLER CHECK: PASS
```

Manual quick interface checks:

```bash
ros2 topic list | sort | grep -E "cmd_vel|odom|scan|tf|costmap|goal|plan|behavior|waypoint|navigate|global|local"
ros2 action list -t | sort | grep -E "compute_path|follow_path|navigate"
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /scan --field header
ros2 topic echo --once /local_costmap/costmap
ros2 topic echo --once /global_costmap/costmap
```

---

## 16. Interface Ownership Rules

These rules prevent most integration bugs.

```txt
1. /cmd_vel is geometry_msgs/msg/Twist.
2. /diff_drive_controller/cmd_vel is geometry_msgs/msg/TwistStamped.
3. Nav2 publishes Twist, so the bridge is required for the current controller config.
4. Gazebo moves only through diff_drive_controller and ros2_control.
5. /odom_noisy does not move the robot.
6. RViz visualizes data; it does not simulate physics.
7. Gazebo simulates physics and sensors.
8. robot_state_publisher publishes robot link transforms from robot_description and joint_states.
9. joint_state_publisher is for visualization-only stacks.
10. joint_state_broadcaster is for ros2_control stacks.
11. Only one node should own odom -> base_link at a time.
12. Nav2 Day 100 uses odom as the global frame because map localization is not added yet.
13. /scan must have a connected TF frame before RViz/Nav2 costmaps can use it correctly.
14. rosbag2 evidence should be stored locally and ignored by git.
```

---

## 17. Current Day 100 Capability Contract

As of Day 100, the system supports:

```txt
C++ kinematic simulation
ROS 2 topics, odometry, TF, parameters, QoS, diagnostics
URDF/Xacro robot description
RViz robot visualization
Gazebo robot spawning
ros2_control integration
diff_drive_controller velocity control
simulated lidar and /scan bridge
simulation time through /clock
noisy odometry generation
trajectory validation CSV and plot workflow
GoogleTest unit testing
GitHub Actions CI
C++ performance benchmarking
Nav2 lifecycle activation
Nav2 local/global costmaps in odom frame
Nav2 ComputePathToPose validation
Nav2 NavigateToPose single-goal execution
Nav2 recovery behavior tests
Nav2 NavigateThroughPoses waypoint execution
rosbag2 MCAP evidence recording and replay
```

Current known limitations:

```txt
No map frame yet
No SLAM yet
No AMCL yet
No EKF localization integration yet
No dynamic obstacle benchmark yet
No automated Gazebo/Nav2 CI scenario test yet
No Dockerized public demo yet
No controller/gamepad teleop release yet
```

---

## 18. Day 100 Interview Summary

```txt
The project exposes a clear ROS 2 interface contract across a custom C++ simulator, a Gazebo ros2_control robot stack, validation tooling, and a working Nav2 odom-frame navigation stack. The most important command path is Nav2 /cmd_vel as Twist, converted by a bridge into /diff_drive_controller/cmd_vel as TwistStamped, which drives diff_drive_controller, ros2_control, and Gazebo wheel joints. The main feedback path is diff_drive_controller odometry, TF, LaserScan, costmaps, planner paths, local plans, and behavior-tree logs. The system is validated through lifecycle checks, costmap checks, planner/controller checks, goal navigation tests, recovery tests, waypoint tests, unit tests, CI, performance benchmarks, and rosbag2 MCAP evidence.
```
