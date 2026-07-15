# Debugging and Validation — C++ / ROS 2 Robotics Simulation Foundation

**Status:** Consolidated validation documentation
**Scope:** Standalone C++ simulator, ROS 2 kinematic simulator, Gazebo Sim, `ros2_control`, differential-drive controller, lidar, Nav2 odom-frame navigation, recovery tests, waypoint navigation, rosbag evidence, GoogleTest, GitHub Actions CI, and performance benchmarking.

This document is the project's main engineering validation guide. It replaces scattered day-specific notes by consolidating the repeatable checks, failure modes, debugging workflows, and proof-of-work evidence into one public-facing reference.

---

## 1. Debugging Philosophy

Do not randomly edit code when something fails. First isolate the layer, then test the smallest interface that proves or disproves the failure.

Use this sequence:

```text
1. What did I run?
2. What did I expect?
3. What actually happened?
4. Which layer failed?
5. Which command proves that layer failed?
6. What is the smallest fix?
7. Rebuild, re-source, relaunch, and retest.
```

Common failure categories:

```text
Build / dependency failure
Install / package discovery failure
Launch failure
Parameter / YAML failure
Topic type mismatch
TF failure
Simulation-time failure
Gazebo spawn failure
ros2_control / controller failure
LaserScan / bridge failure
Nav2 lifecycle failure
Costmap failure
Planner failure
Controller / path-following failure
Goal navigation failure
Recovery / oscillation behavior
Waypoint mission failure
rosbag record / replay failure
CI failure
Git hygiene failure
```

---

## 2. Standard Workspace Commands

### 2.1 Repository Root

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation
```

### 2.2 Hard Reset

Use this whenever stale Gazebo, RViz, bridge, controller, or Nav2 processes interfere with a clean run.

```bash
./scripts/hard_reset.sh
```

If the script fails because of Windows line endings:

```bash
sed -i 's/\r$//' scripts/hard_reset.sh
chmod +x scripts/hard_reset.sh
```

### 2.3 Clean Build

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
```

For fast runtime-only checks:

```bash
colcon build --cmake-args -DBUILD_TESTING=OFF
```

### 2.4 Package Executable Check

```bash
ros2 pkg executables cpp_robotics_sim_ros
```

Expected important executables and scripts include:

```text
sim_node
performance_benchmark
cmd_vel_twist_bridge.py
noisy_odom_node.py
trajectory_validation_recorder.py
plot_trajectory_validation.py
nav2_lifecycle_check.sh
nav2_costmap_check.sh
nav2_planner_controller_check.sh
```

---

## 3. Validation Gate

Before calling the Nav2 phase healthy, run:

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

Expected final lines:

```text
LIFECYCLE CHECK: PASS
COSTMAP CHECK: PASS
PLANNER/CONTROLLER CHECK: PASS
```

These three scripts form the Nav2 regression baseline.

---

## 4. Build and Install Debugging

### 4.1 Build Command

```bash
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
```

### 4.2 Common Build Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| `package not found` | Workspace not sourced | `source install/setup.bash` |
| Launch file not found | Launch directory not installed | Check `install(DIRECTORY launch ...)` in `CMakeLists.txt` |
| Config file not found | Config directory not installed | Check `install(DIRECTORY config ...)` |
| RViz config missing | RViz directory not installed | Check `install(DIRECTORY rviz ...)` |
| World file missing | Worlds directory not installed | Check `install(DIRECTORY worlds ...)` |
| Script not found by `ros2 run` | Script not installed | Check `install(PROGRAMS scripts/... DESTINATION lib/${PROJECT_NAME})` |
| Old behavior after edits | Stale build/install | `rm -rf build install log`, rebuild, re-source |
| Python script fails with `python3\r` | CRLF line endings | `sed -i 's/\r$//' <script>` |
| Permission denied | Script is not executable | `chmod +x <script>` |
| Controller packages missing | ROS control packages missing | Install `ros-jazzy-ros2-control ros-jazzy-ros2-controllers` |
| Gazebo bridge missing | ROS-Gazebo bridge not installed/launched | Check `ros-jazzy-ros-gz-bridge` |

### 4.3 Python Script Sanity Checks

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws

python3 -m py_compile src/cpp_robotics_sim_ros/scripts/noisy_odom_node.py
python3 -m py_compile src/cpp_robotics_sim_ros/scripts/trajectory_validation_recorder.py
python3 -m py_compile src/cpp_robotics_sim_ros/scripts/plot_trajectory_validation.py
python3 -m py_compile src/cpp_robotics_sim_ros/scripts/cmd_vel_twist_bridge.py

head -n 1 src/cpp_robotics_sim_ros/scripts/cmd_vel_twist_bridge.py | cat -A
ls -l src/cpp_robotics_sim_ros/scripts/*.py
```

Expected first line:

```text
#!/usr/bin/env python3$
```

There should be no `^M`.

---

## 5. Launch Debugging

### 5.1 Kinematic Simulator Launch

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

Expected topics:

```text
/cmd_vel
/robot_pose
/odom
/tf
/diagnostics
```

### 5.2 Gazebo / ros2_control Launch

```bash
ros2 launch cpp_robotics_sim_ros ros2_control.launch.py
```

Expected:

```text
Gazebo opens
robot appears in world
controller_manager exists
joint_state_broadcaster active
diff_drive_controller active
/scan publishes
/clock publishes
```

### 5.3 Nav2 Launch

```bash
ros2 launch cpp_robotics_sim_ros nav2_navigation.launch.py
```

Expected:

```text
Gazebo opens
robot spawns
controllers activate
/cmd_vel bridge starts
Nav2 lifecycle nodes become active
costmaps publish
planner/controller actions exist
```

---

## 6. ROS 2 Kinematic Simulator Validation

### 6.1 Command Test

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"
```

### 6.2 State Checks

```bash
ros2 topic echo --once /robot_pose
ros2 topic echo --once /odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /diagnostics
```

Pass criteria:

```text
/robot_pose changes after command
/odom publishes nav_msgs/msg/Odometry
odom -> base_link TF exists
/diagnostics reports node health
robot stops after cmd_timeout when commands stop
```

---

## 7. URDF / Xacro / Robot Description Validation

### 7.1 Static URDF Parse

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("ros2_ws/src/cpp_robotics_sim_ros/urdf/diffbot.urdf")
print("PASS: URDF XML parsed successfully")
PY
```

### 7.2 Xacro Generation

```bash
source /opt/ros/jazzy/setup.bash
xacro ros2_ws/src/cpp_robotics_sim_ros/xacro/diffbot.xacro > /tmp/diffbot_from_xacro.urdf

python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("/tmp/diffbot_from_xacro.urdf")
print("PASS: Xacro generated valid URDF XML")
PY
```

### 7.3 Description Launch

```bash
ros2 launch cpp_robotics_sim_ros description.launch.py
```

Checks:

```bash
ros2 topic list | grep -E "robot_description|joint_states|tf"
ros2 param get /robot_state_publisher robot_description > /tmp/robot_description.txt

grep -E "base_link|left_wheel_link|right_wheel_link|caster_link|lidar_link" /tmp/robot_description.txt
grep -E "left_wheel_joint|right_wheel_joint|caster_joint|lidar_joint" /tmp/robot_description.txt
```

Common robot description failures:

| Symptom | Likely Cause | Fix |
|---|---|---|
| XML parsed as YAML | Launch parameter not forced to string | Use `ParameterValue(..., value_type=str)` |
| Xacro command fails | Path quoting or Xacro typo | Run `xacro` manually |
| RobotModel missing in RViz | Missing `/robot_description` or TF | Check `robot_state_publisher` and `/tf_static` |
| Wheel links missing | `/joint_states` missing | Check `joint_state_publisher` or `joint_state_broadcaster` |

---

## 8. Gazebo, ros2_control, and Controller Validation

### 8.1 Controller State

```bash
ros2 control list_controllers
```

Expected:

```text
joint_state_broadcaster active
diff_drive_controller active
```

### 8.2 Hardware Interfaces

```bash
ros2 control list_hardware_interfaces
```

Expected interfaces:

```text
left_wheel_joint/velocity command interface
right_wheel_joint/velocity command interface
left_wheel_joint/position state interface
left_wheel_joint/velocity state interface
right_wheel_joint/position state interface
right_wheel_joint/velocity state interface
```

### 8.3 Direct Gazebo Drive Command

```bash
ros2 topic pub -r 10 /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.25}, angular: {z: 0.2}}}"
```

Expected:

```text
robot moves in Gazebo
/diff_drive_controller/odom changes
odom -> base_link TF updates
/diff_drive_controller/cmd_vel_out publishes if enabled
```

### 8.4 Common ros2_control Failures

| Symptom | Likely Cause | First Check |
|---|---|---|
| `/controller_manager` missing | `gz_ros2_control` plugin did not load | Inspect Gazebo launch terminal |
| Controller inactive | Hardware interfaces unavailable | `ros2 control list_hardware_interfaces` |
| Wheel names empty | YAML indentation wrong | Check installed `ros2_control.yaml` |
| Robot does not move | Wrong command topic/type | Publish `TwistStamped` to `/diff_drive_controller/cmd_vel` |
| Odom publishes but RViz does not move | Sim-time or TF issue | Check `/clock`, `use_sim_time`, `tf2_echo` |

---

## 9. Sensor, Scan, and Simulation-Time Validation

### 9.1 `/scan` Validation

```bash
ros2 topic list | grep scan
ros2 topic type /scan
ros2 topic echo /scan --once
```

Expected:

```text
/scan
sensor_msgs/msg/LaserScan
ranges: [...]
```

### 9.2 Lidar TF

```bash
ros2 run tf2_ros tf2_echo base_link lidar_link
```

If `/scan` uses a Gazebo-expanded frame such as `diffbot/base_link/diffbot_lidar`, verify a valid TF path exists from that frame into the robot tree.

### 9.3 Gazebo-Side Sensor Check

If ROS `/scan` is missing:

```bash
gz topic -l | grep scan
gz topic -e -t /scan
```

### 9.4 `/clock` Validation

```bash
ros2 topic list | grep clock
ros2 topic echo /clock --once
```

Expected:

```text
/clock publishes rosgraph_msgs/msg/Clock
```

### 9.5 RViz Sim-Time Rule

When visualizing Gazebo-driven data, launch RViz with simulation time or ensure the config uses sim time:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

RViz recommended settings:

```text
Fixed Frame: odom
RobotModel: /robot_description
Odometry: /diff_drive_controller/odom
LaserScan: /scan
LaserScan Reliability: Best Effort if needed
```

---

## 10. TF Validation and Ownership

### 10.1 Check Main Transform

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```text
Transform streams continuously
translation x/y changes when robot moves
rotation represents yaw
```

### 10.2 Frame Tree

```bash
ros2 run tf2_tools view_frames
```

Expected frame concept:

```text
odom
  └── base_link
      ├── left_wheel_link
      ├── right_wheel_link
      ├── caster_link
      └── lidar_link
```

### 10.3 Transform Ownership Rule

```text
Kinematic simulator stack:
  sim_node owns odom -> base_link

Gazebo / Nav2 stack:
  diff_drive_controller owns odom -> base_link
  robot_state_publisher owns base_link -> robot links
  joint_state_broadcaster owns /joint_states
```

Do not run `sim_node` and `diff_drive_controller` as simultaneous publishers of `odom -> base_link`.

### 10.4 Common TF Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| RViz fixed frame error | TF tree incomplete | Set Fixed Frame to `odom`, check `tf2_echo` |
| `base_link` missing | Odometry/controller not publishing | Check `/diff_drive_controller/odom` and controller state |
| Wheel frames missing | `/joint_states` missing | Check joint broadcaster / robot state publisher |
| Duplicate TF warning | Two nodes publish same transform | Do not run `sim_node` with Gazebo controller stack |
| `TF_OLD_DATA` | Stale nodes or sim-time mismatch | Hard reset and relaunch with sim time |

---

## 11. Nav2 Lifecycle Validation

### 11.1 Automated Check

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
```

Pass criteria:

```text
/lifecycle_manager_navigation exists
/controller_server active [3]
/smoother_server active [3]
/planner_server active [3]
/behavior_server active [3]
/velocity_smoother active [3]
/bt_navigator active [3]
/waypoint_follower active [3]
/navigate_to_pose exists
/navigate_through_poses exists
/lifecycle_manager_navigation/manage_nodes exists
LIFECYCLE CHECK: PASS
```

### 11.2 Manual Lifecycle Checks

```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /smoother_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /velocity_smoother
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /waypoint_follower
```

Expected:

```text
active [3]
```

### 11.3 Lifecycle Failure Handling

If nodes are inactive:

```bash
ros2 service call /lifecycle_manager_navigation/manage_nodes nav2_msgs/srv/ManageLifecycleNodes "{command: 2}"
```

If lifecycle activation still fails, inspect the launch terminal for missing parameters, missing costmap layers, TF failure, or controller server configuration errors.

---

## 12. Nav2 Costmap Validation

### 12.1 Automated Check

```bash
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
```

Pass criteria:

```text
/local_costmap/local_costmap exists
/global_costmap/global_costmap exists
/scan publishes
/local_costmap/costmap publishes
/global_costmap/costmap publishes
/local_costmap/published_footprint publishes
/global_costmap/published_footprint publishes
local_costmap global_frame = odom
local_costmap robot_base_frame = base_link
global_costmap global_frame = odom
global_costmap robot_base_frame = base_link
odom -> base_link TF exists
COSTMAP CHECK: PASS
```

### 12.2 Manual Costmap Checks

```bash
ros2 node list | grep costmap
ros2 topic list | sort | grep -E "costmap|footprint|scan"
ros2 topic echo --once /scan
ros2 topic echo --once /local_costmap/costmap
ros2 topic echo --once /global_costmap/costmap
```

### 12.3 Costmap Frame Parameters

```bash
ros2 param get /local_costmap/local_costmap global_frame
ros2 param get /local_costmap/local_costmap robot_base_frame
ros2 param get /global_costmap/global_costmap global_frame
ros2 param get /global_costmap/global_costmap robot_base_frame
```

Expected:

```text
String value is: odom
String value is: base_link
```

### 12.4 RViz Costmap Debugging

RViz Fixed Frame:

```text
odom
```

Displays:

```text
RobotModel
TF
LaserScan
Local Costmap
Global Costmap
Plan / Path
Odometry
```

RViz does not create real obstacles. Gazebo/SDF creates physical obstacles; RViz visualizes scan/costmap evidence.

---

## 13. Nav2 Planner and Controller Validation

### 13.1 Automated Check

```bash
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

Pass criteria:

```text
/compute_path_to_pose exists
/follow_path exists
/navigate_to_pose exists
/planner_server active [3]
/controller_server active [3]
ComputePathToPose returns odom-frame path
Controller frequency and FollowPath params are readable
PLANNER/CONTROLLER CHECK: PASS
```

### 13.2 Action Server Check

```bash
ros2 action list -t | sort | grep -E "compute_path|follow_path|navigate"
```

Expected:

```text
/compute_path_through_poses [nav2_msgs/action/ComputePathThroughPoses]
/compute_path_to_pose [nav2_msgs/action/ComputePathToPose]
/follow_path [nav2_msgs/action/FollowPath]
/navigate_through_poses [nav2_msgs/action/NavigateThroughPoses]
/navigate_to_pose [nav2_msgs/action/NavigateToPose]
```

### 13.3 Direct Planner Test

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

```text
Goal accepted
path.header.frame_id: odom
poses: non-empty
Goal finished with status: SUCCEEDED
error_code: 0
```

### 13.4 Controller Parameters

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

Expected conservative values:

```text
controller_frequency = 10.0
max_vel_x = 0.25
max_vel_theta = 0.6
acc_lim_x = 0.5
acc_lim_theta = 1.0
sim_time = 1.5
vx_samples = 20
vtheta_samples = 20
```

---

## 14. Nav2 Goal Navigation Validation

### 14.1 CLI Goal

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: odom},
    pose: {
      position: {x: 0.5, y: 0.0, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  },
  behavior_tree: ''
}"
```

Expected:

```text
Goal accepted
/cmd_vel publishes nonzero commands
/diff_drive_controller/cmd_vel receives TwistStamped commands
/diff_drive_controller/odom changes
robot moves in Gazebo
path/costmap evidence appears in RViz
Goal finishes with SUCCEEDED or reaches the accepted validation tolerance
```

### 14.2 RViz Goal

In RViz:

```text
Fixed Frame = odom
Tool = 2D Goal Pose / Nav2 Goal
Goal topic = /goal_pose if prompted
```

Click a nearby open area, hold, drag to set final orientation, and release.

### 14.3 Command Flow Monitors

```bash
ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
ros2 topic echo /diff_drive_controller/odom --field pose.pose.position
```

---

## 15. Nav2 Recovery Behavior Tests

Recovery behavior was tested using valid and invalid navigation goals with fixed SDF obstacles.

### 15.1 Fixed Obstacles

`scan_box_front`:

```text
center = (2.0, 0.0)
size   = 0.4 x 1.0 x 1.0
approx footprint: x = 1.8 to 2.2, y = -0.5 to 0.5
```

`scan_box_left`:

```text
center = (0.0, 2.0)
size   = 1.0 x 0.4 x 1.0
approx footprint: x = -0.5 to 0.5, y = 1.8 to 2.2
```

### 15.2 Test 1 — Goal Inside Obstacle

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: odom},
    pose: {
      position: {x: 2.0, y: 0.0, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  },
  behavior_tree: ''
}"
```

Observed result:

```text
Goal accepted
Robot tried for a long time
Robot oscillated / shook left-right
number_of_recoveries reached 18
distance_remaining stayed nonzero
Final status: ABORTED
error_code: 105
Stack did not crash
```

Result:

```text
PASS for blocked-goal recovery/failure observation
```

### 15.3 Test 2 — Goal Behind Front Obstacle

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: odom},
    pose: {
      position: {x: 2.8, y: 0.0, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  },
  behavior_tree: ''
}"
```

Observed result:

```text
Goal accepted
Robot found a feasible side route
number_of_recoveries reached 8
Final distance_remaining approximately 0.195 m
Final status: SUCCEEDED
error_code: 0
```

Result:

```text
PASS — Nav2 reached the goal when a feasible route existed
```

### 15.4 Test 3 — Outside Practical Costmap Region

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: odom},
    pose: {
      position: {x: 20.0, y: 20.0, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  },
  behavior_tree: ''
}"
```

Observed result:

```text
Goal accepted
Nav2 immediately aborted
Robot did not drive toward the far target
number_of_recoveries = 0
distance_remaining = 0.0
Final status: ABORTED
error_code: 204
Stack did not crash
```

Result:

```text
PASS — outside-costmap goal was rejected cleanly
```

### 15.5 Post-Failure Lifecycle Check

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator
```

Expected:

```text
active [3]
active [3]
active [3]
active [3]
```

---

## 16. Waypoint Navigation Validation

### 16.1 Action Check

```bash
ros2 action list -t | sort | grep -E "navigate_through|waypoint|navigate_to_pose"
```

Expected:

```text
/navigate_through_poses [nav2_msgs/action/NavigateThroughPoses]
/navigate_to_pose [nav2_msgs/action/NavigateToPose]
```

### 16.2 Easy Multi-Waypoint Mission

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

Observed result:

```text
Mission accepted
Robot moved through waypoint sequence
/cmd_vel published
/diff_drive_controller/odom changed
Final status: SUCCEEDED
```

### 16.3 Mirrored Negative-X Mission

The same mission was mirrored with negative `x` values:

```text
(-0.5, 0.0)
(-0.8, -0.4)
(-1.2, -0.6)
```

Observed result:

```text
Final status: SUCCEEDED
```

### 16.4 Obstacle-Side / Harder Mission

Observed result:

```text
Robot initially struggled near the route
Robot appeared stuck for some time
Recovery behavior occurred
number_of_recoveries reached 16 in captured feedback
Final status: SUCCEEDED
error_code: 0
```

Result:

```text
PASS — NavigateThroughPoses works for multi-goal missions, including a harder route with recoveries
```

---

## 17. rosbag2 Evidence Workflow

### 17.1 Recording Command

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

### 17.2 Goal Used During Recording

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

### 17.3 Bag Info Result

```text
Files:             goal_run_01_0.mcap
Bag size:          3.4 MiB
Storage id:        mcap
ROS Distro:        jazzy
Duration:          31.118688884s
Messages:          6809
```

Important nonzero topics:

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

### 17.4 Bag Inspection

```bash
ros2 bag info bags/day98_nav2_goal_evidence/goal_run_01
```

### 17.5 Bag Replay

```bash
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock
```

Replay started successfully with `rosbag2_player`.

### 17.6 Notes

```text
MCAP is valid rosbag2 storage.
Run ros2 bag info on the bag folder, not directly on the .mcap file.
/goal_pose may not appear if the goal was sent through the /navigate_to_pose action instead of RViz.
Do not commit bag data.
```

`.gitignore` should include:

```gitignore
bags/
*.mcap
*.db3
```

Result:

```text
PASS — replayable Nav2 dataset recorded with command, odometry, TF, scan, costmap, plan, and behavior-tree evidence
```

---

## 18. Nav2 Debugging Guide

### 18.1 Lifecycle Debug

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /velocity_smoother
```

### 18.2 Actions Debug

```bash
ros2 action list -t | sort | grep -E "compute_path|follow_path|navigate|spin|wait|backup|drive"
```

### 18.3 Costmap Debug

```bash
ros2 topic list | sort | grep -E "costmap|footprint|scan"
ros2 topic echo --once /scan
ros2 topic echo --once /local_costmap/costmap
ros2 topic echo --once /global_costmap/costmap
```

### 18.4 TF Debug

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo --once /scan --field header
```

### 18.5 Command Flow Debug

```bash
ros2 topic info /cmd_vel
ros2 topic info /diff_drive_controller/cmd_vel
ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
```

Expected command path:

```text
Nav2 /cmd_vel                       geometry_msgs/msg/Twist
  -> cmd_vel_twist_bridge.py
  -> /diff_drive_controller/cmd_vel geometry_msgs/msg/TwistStamped
  -> diff_drive_controller
  -> Gazebo robot motion
```

---

## 19. Unit Testing

### 19.1 Test Command

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash

colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+
colcon test-result --verbose
```

Expected:

```text
Summary: 17 tests, 0 errors, 0 failures, 0 skipped
```

### 19.2 What GoogleTest Validates

```text
clamp()
wrapToPi()
integratePose()
Pose2D deterministic behavior
invalid dt handling
angle wrapping
forward motion
side-direction motion
pure rotation
repeated deterministic integration
```

GoogleTest validates deterministic C++ logic. It does not validate Gazebo, RViz, sensors, controllers, or Nav2 runtime behavior.

---

## 20. GitHub Actions CI

### 20.1 Current CI Scope

The current GitHub Actions workflow validates:

```text
repository checkout
ROS 2 Jazzy dependency installation
rosdep dependency installation
colcon build
GoogleTest execution
colcon test logs artifact upload
```

### 20.2 Local CI Mirror

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash

colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+
colcon test-result --verbose
```

### 20.3 GitHub CLI Checks

```bash
gh run list --limit 5
gh run watch
```

### 20.4 Current CI Limitations

Current CI does not yet run:

```text
Gazebo runtime launch
controller activation checks
/scan runtime checks
/clock runtime checks
TF runtime checks
Nav2 goals
rosbag replay
SLAM/localization tests
```

Those belong to later release and validation automation.

---

## 21. Performance Benchmarking

### 21.1 Benchmark Command

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

ros2 run cpp_robotics_sim_ros performance_benchmark \
  --output data/day88_performance_results.csv \
  --report docs/performance_report.md
```

### 21.2 Observed Baseline

```text
dt=0.1    steps=100     mean wall time ≈ 1.83 ms     RTF ≈ 5684.98
dt=0.01   steps=1000    mean wall time ≈ 17.40 ms    RTF ≈ 574.99
dt=0.001  steps=10000   mean wall time ≈ 174.74 ms   RTF ≈ 57.23
```

### 21.3 Benchmark Scope

Includes:

```text
deterministic C++ pose integration
multiple virtual robot states
multiple dt values
multiple trials
wall-clock timing
estimated real-time factor
```

Does not include:

```text
Gazebo physics
rendering
ROS middleware
controller_manager overhead
TF broadcasting
sensor simulation
rosbag logging
RViz
Nav2
```

---

## 22. Debugging Decision Trees

### 22.1 Robot Does Not Move

Check:

```bash
ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
ros2 topic echo /diff_drive_controller/odom --field pose.pose.position
```

Interpretation:

```text
/cmd_vel publishes but /diff_drive_controller/cmd_vel does not:
  bridge problem

/diff_drive_controller/cmd_vel publishes but odom does not change:
  controller/Gazebo/ros2_control problem

odom changes but RViz does not move:
  RViz fixed frame, sim time, or TF problem
```

### 22.2 Costmaps Not Visible

Check:

```bash
ros2 topic echo --once /scan
ros2 topic echo --once /local_costmap/costmap
ros2 topic echo --once /global_costmap/costmap
ros2 run tf2_ros tf2_echo odom base_link
```

Then verify RViz:

```text
Fixed Frame = odom
LaserScan reliability = Best Effort if needed
Costmap displays enabled
```

### 22.3 Goal Aborts Immediately

Check:

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{...}"
```

If compute path fails:

```text
planner / global costmap / invalid goal issue
```

If compute path succeeds but navigation aborts:

```text
controller / local costmap / recovery behavior issue
```

### 22.4 Robot Shakes Left-Right

Use action feedback:

```bash
ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{...}"
```

Interpretation:

```text
number_of_recoveries increases:
  Nav2 recovery behavior is active

distance_remaining decreases:
  robot is making progress

distance_remaining stays high and angular.z flips signs:
  local controller oscillation or recovery loop

Goal ABORTED and lifecycle nodes remain active:
  clean failure, useful recovery-behavior evidence
```

### 22.5 Bag Replay Does Not Show Data

Check:

```bash
ros2 bag info <bag_folder>
ros2 bag play <bag_folder> --clock
```

RViz:

```text
Fixed Frame = odom
Use sim time if needed
Displays point to recorded topics
```

---

## 23. ROS Log Search

ROS logs are stored under:

```bash
~/.ros/log
```

Search latest logs:

```bash
grep -RniE "fail|abort|recover|replan|oscillat|stuck|patience|valid|goal|controller|planner|behavior" ~/.ros/log/latest 2>/dev/null
```

If `latest` does not exist:

```bash
grep -RniE "fail|abort|recover|replan|oscillat|stuck|patience|valid|goal|controller|planner|behavior" ~/.ros/log 2>/dev/null | tail -n 80
```

Main launch terminal logs are also important. Look for messages from:

```text
planner_server
controller_server
bt_navigator
behavior_server
velocity_smoother
local_costmap
global_costmap
cmd_vel_twist_bridge
controller_manager
diff_drive_controller
```

---

## 24. Known Non-Blocking Warning

This warning appears frequently:

```text
RTPS_TRANSPORT_SHM Error Failed init_port fastrtps_port7005: open_and_lock_file failed -> Function open_port_internal
```

Current status:

```text
Non-blocking.
```

It has not blocked:

```text
lifecycle checks
costmap checks
TF
scan data
action servers
planner path generation
controller parameter checks
goal navigation
recovery tests
waypoint navigation
rosbag recording
rosbag replay
```

Do not derail debugging because of this warning unless communication actually fails.

---

## 25. Git Hygiene and Evidence Policy

### 25.1 Do Commit

```text
source code
launch files
YAML config
URDF/Xacro/world files
RViz config
validation scripts
documentation
small generated plots if intentionally part of portfolio
```

### 25.2 Do Not Commit

```text
build/
install/
log/
bags/
*.mcap
*.db3
large raw temporary outputs
```

Recommended `.gitignore` entries:

```gitignore
build/
install/
log/
bags/
*.mcap
*.db3
```

### 25.3 Commit After Validation

Before committing meaningful runtime changes:

```bash
git status --short

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
colcon test --packages-select cpp_robotics_sim_ros --event-handlers console_direct+
colcon test-result --verbose
```

For Nav2 phase changes, also run:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
```

---

## 26. Final Validation Summary

The project has validated:

```text
standalone C++ simulation logic
ROS 2 kinematic simulator topics and TF
launch/YAML parameter workflow
QoS documentation
rosbag2 baseline workflow
RViz visualization
URDF/Xacro robot model
robot_state_publisher and joint state workflows
Gazebo spawn
ros2_control interfaces
joint_state_broadcaster
diff_drive_controller motion
simulated lidar and /scan bridge
simulation time /clock behavior
noisy odometry stream
trajectory validation recorder
plot/report generation
GoogleTest unit tests
GitHub Actions CI
performance benchmark
Nav2 lifecycle activation
local/global costmaps
planner/controller action availability
ComputePathToPose path generation
controller tuning parameters
Nav2 goal navigation
recovery/failure behavior
NavigateThroughPoses waypoint missions
rosbag2 Nav2 evidence dataset
```

Result:

```text
The project is no longer only a robot demo. It is a validated ROS 2/Gazebo/Nav2 simulation stack with repeatable checks, debugging workflows, and evidence artifacts.
```

---

## 27. Current Limitations

Current limitations:

```text
Navigation is odom-frame only.
No SLAM map is used yet.
No AMCL localization is used yet.
No EKF fusion is active in the Nav2 stack yet.
CI does not run Gazebo/Nav2 runtime tests yet.
Nav2 behavior near obstacles can still oscillate.
Recovery tuning is not final.
Waypoint missions are manually launched, not scripted yet.
rosbag evidence is local and ignored by git.
Docker/devcontainer packaging is planned later.
```

These are planned enhancements and are not blockers for the current Nav2 integration.

---

## 28. Validation Pass Statement

```text
NAV2 INTEGRATION REVIEW: PASS
```

The system can now be explained, launched, validated, debugged, and demonstrated as an odom-frame ROS 2/Gazebo/Nav2 mobile robot simulation stack.
