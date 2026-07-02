# Day 98 - Nav2 rosbag2 Evidence

## Goal

Record a replayable rosbag2 dataset for a successful Nav2 goal navigation run in the odom-frame Gazebo/RViz robot simulation stack.

## Stack Under Test

- ROS 2 Jazzy
- Gazebo Sim 8
- ros2_control differential-drive robot
- Nav2 planner/controller/behavior stack
- `/cmd_vel` Twist to `/diff_drive_controller/cmd_vel` TwistStamped bridge
- Odom-frame navigation only
- Fixed SDF obstacle world

## Pre-checks

The following validation scripts passed before recording:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
Bag Folder
bags/day98_nav2_goal_evidence/goal_run_01

The bag folder is ignored by git to avoid committing binary rosbag data.

Storage Format

The bag was recorded using MCAP storage.

Files:      goal_run_01_0.mcap
Bag size:   3.4 MiB
Storage id: mcap
Duration:   31.118688884s
Messages:   6809
ROS Distro: jazzy
Topics Recorded
/behavior_tree_log
/cmd_vel
/cmd_vel_nav
/cmd_vel_smoothed
/diff_drive_controller/cmd_vel
/diff_drive_controller/cmd_vel_out
/diff_drive_controller/odom
/global_costmap/costmap
/global_costmap/costmap_updates
/global_costmap/published_footprint
/local_costmap/costmap
/local_costmap/costmap_updates
/local_costmap/published_footprint
/local_plan
/odom
/plan
/plan_smoothed
/received_global_plan
/scan
/tf
/tf_static
/transformed_global_plan
Nonzero Evidence Topics

The bag contains nonzero data for the main navigation evidence topics:

Topic	Message Count
/behavior_tree_log	8
/cmd_vel	81
/cmd_vel_nav	35
/cmd_vel_smoothed	86
/diff_drive_controller/cmd_vel	81
/diff_drive_controller/cmd_vel_out	2672
/diff_drive_controller/odom	1336
/global_costmap/costmap	20
/global_costmap/published_footprint	58
/local_costmap/costmap	48
/local_costmap/published_footprint	142
/local_plan	34
/plan	4
/received_global_plan	38
/scan	267
/tf	1863
/tf_static	2
/transformed_global_plan	34
Recording Command
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
Goal Command Used During Recording
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
Observed Result
Goal was accepted.
/cmd_vel published nonzero Twist commands.
/cmd_vel_nav and /cmd_vel_smoothed captured the Nav2 velocity command path.
/diff_drive_controller/cmd_vel received TwistStamped commands from the bridge.
/diff_drive_controller/cmd_vel_out captured controller command output.
/diff_drive_controller/odom changed during the run.
/scan captured simulated lidar data.
/tf and /tf_static captured frame data.
/plan, /local_plan, /received_global_plan, and /transformed_global_plan captured path evidence.
Local/global costmaps were recorded.
Behavior tree logs were recorded.
Goal navigation completed successfully.
Bag Inspection Command
ros2 bag info bags/day98_nav2_goal_evidence/goal_run_01
Replay Command
ros2 bag play bags/day98_nav2_goal_evidence/goal_run_01 --clock

Replay started successfully with rosbag2 player.

Notes
/goal_pose was included in the recording command, but the goal was sent through the /navigate_to_pose action, not through RViz's /goal_pose topic. Therefore /goal_pose did not appear in the final bag topic list.
This is acceptable for Day 98 because the action-based goal still produced replayable command, odometry, TF, scan, costmap, plan, and behavior-tree evidence.
Future RViz-specific evidence can record /goal_pose by sending the goal with the RViz 2D Goal Pose / Nav2 Goal tool.
Bag data is stored locally under bags/ and ignored by git.
Result
DAY 98 ROSBAG2 EVIDENCE: PASS