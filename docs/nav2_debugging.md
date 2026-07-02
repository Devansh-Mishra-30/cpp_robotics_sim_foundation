# Day 99 - Nav2 Debugging Guide

## Goal

Document the main Nav2 debugging workflows used in the ROS 2/Gazebo differential-drive simulation stack.

This guide covers lifecycle failures, costmap visibility, TF issues, LaserScan frame issues, controller command flow, planner/controller validation, recovery behavior, rosbag evidence, and known non-blocking warnings.

## Stack

- ROS 2 Jazzy
- Gazebo Sim 8
- ros2_control differential-drive robot
- Nav2 planner/controller/behavior stack
- RViz2
- `/cmd_vel` Twist to `/diff_drive_controller/cmd_vel` TwistStamped bridge
- Odom-frame navigation only at this stage

---

## 1. Clean Reset Workflow

Use this when stale nodes, stuck Gazebo processes, or old Nav2 nodes interfere with a new run.

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation

./docs/hard_reset_command.sh

If the script has Windows CRLF issues:

sed -i 's/\r$//' docs/hard_reset_command.sh
chmod +x docs/hard_reset_command.sh

Then rebuild and launch:

rm -rf build install log

source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash

ros2 launch cpp_robotics_sim_ros nav2_navigation.launch.py
2. Standard Validation Checks

Run these after launch:

ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh

Expected:

DAY 92 LIFECYCLE CHECK: PASS
DAY 93 COSTMAP CHECK: PASS
DAY 94 PLANNER/CONTROLLER CHECK: PASS

These checks validate lifecycle nodes, costmap topics, scan data, TF, planner action availability, path generation, and controller tuning parameters.

3. Lifecycle Debugging

Check lifecycle states:

ros2 lifecycle get /controller_server
ros2 lifecycle get /smoother_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /velocity_smoother
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /waypoint_follower

Expected active state:

active [3]

If nodes are stuck in inactive state:

inactive [2]

try activating through the lifecycle manager:

ros2 service call /lifecycle_manager_navigation/manage_nodes nav2_msgs/srv/ManageLifecycleNodes "{command: 2}"

The launch file includes a delayed lifecycle activation fallback because autostart did not always activate all Nav2 nodes reliably.

4. Nav2 Action Server Debugging

List action servers:

ros2 action list -t | sort | grep -E "compute_path|follow_path|navigate|waypoint|spin|wait|backup|drive"

Expected core actions:

/compute_path_to_pose [nav2_msgs/action/ComputePathToPose]
/follow_path [nav2_msgs/action/FollowPath]
/navigate_to_pose [nav2_msgs/action/NavigateToPose]
/navigate_through_poses [nav2_msgs/action/NavigateThroughPoses]

If /navigate_to_pose is missing, check:

ros2 lifecycle get /bt_navigator
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server

If /compute_path_to_pose is missing, check:

ros2 lifecycle get /planner_server

If /follow_path is missing, check:

ros2 lifecycle get /controller_server
5. Costmap Debugging

Check costmap nodes:

ros2 node list | grep costmap

Expected:

/local_costmap/local_costmap
/global_costmap/global_costmap

Check costmap topics:

ros2 topic list | sort | grep -E "costmap|footprint|scan"

Expected important topics:

/scan
/local_costmap/costmap
/global_costmap/costmap
/local_costmap/published_footprint
/global_costmap/published_footprint

Check message flow:

ros2 topic echo --once /scan
ros2 topic echo --once /local_costmap/costmap
ros2 topic echo --once /global_costmap/costmap

Check costmap frames:

ros2 param get /local_costmap/local_costmap global_frame
ros2 param get /local_costmap/local_costmap robot_base_frame
ros2 param get /global_costmap/global_costmap global_frame
ros2 param get /global_costmap/global_costmap robot_base_frame

Expected:

global_frame: odom
robot_base_frame: base_link
6. RViz Costmap Debugging

RViz should use:

Fixed Frame: odom

Recommended displays:

RobotModel
TF
LaserScan
Local Costmap
Global Costmap
Plan / Path
Odometry

If costmaps do not appear:

Confirm /scan publishes.
Confirm /local_costmap/costmap publishes.
Confirm /global_costmap/costmap publishes.
Confirm odom -> base_link TF exists.
Confirm the LaserScan frame has a valid TF path to base_link or odom.
7. TF Debugging

Check odom to base link:

ros2 run tf2_ros tf2_echo odom base_link

Expected:

Transform data should stream continuously.

Check TF tree:

ros2 run tf2_tools view_frames

This creates a PDF showing the TF tree.

Common expected structure:

odom -> base_link
base_link -> robot body/wheel/lidar links
8. LaserScan Frame Debugging

Check scan header:

ros2 topic echo --once /scan --field header

A previous issue showed /scan publishing with:

frame_id: diffbot/base_link/diffbot_lidar

RViz could not visualize the scan until a static transform was added from:

lidar_link -> diffbot/base_link/diffbot_lidar

If scan data exists but RViz cannot display it, check whether the scan frame exists in the TF tree.

9. cmd_vel Bridge Debugging

Nav2 publishes:

/cmd_vel
geometry_msgs/msg/Twist

The Gazebo diff-drive controller expects:

/diff_drive_controller/cmd_vel
geometry_msgs/msg/TwistStamped

The bridge converts:

/cmd_vel Twist
  -> cmd_vel_twist_bridge.py
  -> /diff_drive_controller/cmd_vel TwistStamped

Check topic types:

ros2 topic info /cmd_vel
ros2 topic info /diff_drive_controller/cmd_vel

Watch command flow:

ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel

If the bridge fails with exit code 127, check CRLF line endings:

sed -i 's/\r$//' ros2_ws/src/cpp_robotics_sim_ros/scripts/cmd_vel_twist_bridge.py
chmod +x ros2_ws/src/cpp_robotics_sim_ros/scripts/cmd_vel_twist_bridge.py

Rebuild:

colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
10. Planner Debugging

Test planner action directly:

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

Expected:

Goal accepted
path.header.frame_id: odom
poses: non-empty
Goal finished with status: SUCCEEDED

If the planner fails:

Check /planner_server lifecycle state.
Check global costmap publishes.
Check global_frame is odom.
Check goal is not inside an obstacle or outside the costmap.
11. Controller Debugging

Check controller server:

ros2 lifecycle get /controller_server

Check controller frequency and FollowPath parameters:

ros2 param get /controller_server controller_frequency
ros2 param get /controller_server FollowPath.max_vel_x
ros2 param get /controller_server FollowPath.max_vel_theta
ros2 param get /controller_server FollowPath.acc_lim_x
ros2 param get /controller_server FollowPath.acc_lim_theta
ros2 param get /controller_server FollowPath.sim_time
ros2 param get /controller_server FollowPath.vx_samples
ros2 param get /controller_server FollowPath.vtheta_samples

Expected conservative values:

controller_frequency: 10.0
max_vel_x: 0.25
max_vel_theta: 0.6
acc_lim_x: 0.5
acc_lim_theta: 1.0
sim_time: 1.5
vx_samples: 20
vtheta_samples: 20

If the robot shakes left-right:

Use action feedback with --feedback.
Watch distance_remaining.
Watch number_of_recoveries.
Watch /cmd_vel.
Check whether angular.z keeps flipping sign.
Check whether odom position actually changes.
12. Goal Navigation Debugging

Send a small test goal:

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

Good signs:

Goal accepted
/cmd_vel publishes
/diff_drive_controller/cmd_vel publishes
/diff_drive_controller/odom changes
Robot moves in Gazebo
Goal finishes with SUCCEEDED

If the goal aborts:

ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator

Then inspect feedback:

distance_remaining
number_of_recoveries
error_code
Goal status
13. Recovery Behavior Debugging

Use feedback:

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

Interpretation:

number_of_recoveries increases = recovery behavior is happening
distance_remaining decreases = robot is making progress
distance_remaining stays high = robot is stuck
Goal ABORTED = clean failure if lifecycle nodes remain active

Day 96 observations:

Goal inside obstacle: ABORTED after repeated recoveries.
Goal behind obstacle: SUCCEEDED when a side route existed.
Goal far outside costmap: ABORTED immediately.
14. Waypoint Navigation Debugging

Check action:

ros2 action list -t | grep navigate_through

Send a simple waypoint mission:

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

Good signs:

Goal accepted
number_of_poses_remaining decreases
/cmd_vel publishes
odom changes
Goal finishes with SUCCEEDED
15. rosbag2 Evidence Debugging

Record evidence:

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

Inspect:

ros2 bag info bags/day98_nav2_goal_evidence/goal_run_01

Replay:

ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock

Notes:

MCAP storage is valid.
Run ros2 bag info on the bag folder, not the .mcap file directly.
Do not commit bag files to git.
16. ROS Log Search

ROS logs are stored under:

~/.ros/log

Search latest logs:

grep -RniE "fail|abort|recover|replan|oscillat|stuck|patience|valid|goal|controller|planner|behavior" ~/.ros/log/latest 2>/dev/null

If latest is unavailable:

grep -RniE "fail|abort|recover|replan|oscillat|stuck|patience|valid|goal|controller|planner|behavior" ~/.ros/log 2>/dev/null | tail -n 80
17. Known Non-Blocking Warning

The following warning appears often:

RTPS_TRANSPORT_SHM Error Failed init_port fastrtps_port7005: open_and_lock_file failed -> Function open_port_internal

Current status:

Non-blocking.

It has not blocked:

Lifecycle checks
Costmap checks
TF
Scan data
Action servers
Planner path generation
Controller parameter checks
Goal navigation
Waypoint navigation
rosbag recording

Do not derail debugging because of this warning unless communication actually fails.

18. Debugging Decision Tree
Robot does not move

Check:

ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
ros2 topic echo /diff_drive_controller/odom --field pose.pose.position

If /cmd_vel publishes but /diff_drive_controller/cmd_vel does not, debug the bridge.

If /diff_drive_controller/cmd_vel publishes but odom does not change, debug ros2_control/Gazebo.

Costmaps not visible

Check:

ros2 topic echo --once /scan
ros2 topic echo --once /local_costmap/costmap
ros2 run tf2_ros tf2_echo odom base_link

Then verify RViz Fixed Frame is odom.

Goal aborts immediately

Check:

ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose ...

If compute path fails, it is likely planner/global costmap/goal validity.

Robot shakes left-right

Check feedback:

number_of_recoveries
distance_remaining

Check command signs:

ros2 topic echo /cmd_vel

If angular.z flips signs and distance does not decrease, it is likely local controller oscillation or recovery behavior.

Bag replay does not show data

Check:

ros2 bag info <bag_folder>

Make sure RViz Fixed Frame is odom.

Result
DAY 99 NAV2 DEBUGGING GUIDE: PASS