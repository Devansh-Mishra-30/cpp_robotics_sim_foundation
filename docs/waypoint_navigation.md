# Day 97 - Nav2 Waypoint Navigation

## Goal

Validate multi-goal navigation using Nav2 `NavigateThroughPoses` in the odom-frame Gazebo/RViz robot simulation stack.

## Stack Under Test

- ROS 2 Jazzy
- Gazebo Sim 8
- ros2_control differential-drive robot
- Nav2 planner/controller/behavior stack
- `/cmd_vel` Twist to `/diff_drive_controller/cmd_vel` TwistStamped bridge
- Odom-frame navigation only
- Fixed SDF obstacle world with `scan_box_front` and `scan_box_left`

## Pre-checks

The following checks passed before waypoint testing:

```bash
ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
Action Used
/navigate_through_poses [nav2_msgs/action/NavigateThroughPoses]
Monitored Topics
ros2 topic echo /cmd_vel
ros2 topic echo /diff_drive_controller/cmd_vel
ros2 topic echo /diff_drive_controller/odom --field pose.pose.position
Mission 1 - Easy Multi-Waypoint Mission

Command pattern:

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

Observed result:

Goal was accepted.
Robot moved through the waypoint sequence.
/cmd_vel published non-zero velocity commands.
/diff_drive_controller/cmd_vel received TwistStamped commands.
/diff_drive_controller/odom changed during the mission.
Mission completed comfortably.

Status:

SUCCEEDED

Result:

PASS
Mission 2 - Mirrored Negative-X Multi-Waypoint Mission

Command pattern:

ros2 action send_goal --feedback /navigate_through_poses nav2_msgs/action/NavigateThroughPoses "{
  poses: [
    {
      header: {frame_id: odom},
      pose: {
        position: {x: -0.5, y: 0.0, z: 0.0},
        orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
      }
    },
    {
      header: {frame_id: odom},
      pose: {
        position: {x: -0.8, y: -0.4, z: 0.0},
        orientation: {x: 0.0, y: 0.0, z: -0.3826834, w: 0.9238795}
      }
    },
    {
      header: {frame_id: odom},
      pose: {
        position: {x: -1.2, y: -0.6, z: 0.0},
        orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
      }
    }
  ],
  behavior_tree: ''
}"

Observed result:

Goal was accepted.
Robot moved through the mirrored waypoint sequence.
Odom changed consistently.
Mission succeeded.

Status:

SUCCEEDED

Result:

PASS
Mission 3 - Obstacle-Side / Harder Waypoint Mission

Observed result:

Goal was accepted.
Robot initially struggled near the obstacle-side route.
Robot appeared stuck for some time before recovering.
Feedback showed repeated recovery behavior.
number_of_recoveries reached 16 in the captured feedback.
number_of_poses_remaining reached 1 near the end of the mission.
Final result was successful.
Final error_code was 0.
Robot reached the mission endpoint after recovery behavior.

Status:

SUCCEEDED

Result:

PASS with recoveries
Summary
Mission	Scenario	Result	Notes
1	Easy positive-x waypoint sequence	PASS	Completed comfortably
2	Mirrored negative-x waypoint sequence	PASS	Completed successfully
3	Obstacle-side / harder route	PASS	Succeeded after recoveries
Interpretation

Day 97 confirmed that the robot can execute multi-goal navigation using Nav2 NavigateThroughPoses.

The easy and mirrored waypoint missions completed successfully. The harder obstacle-side mission showed recovery behavior and temporary difficulty, but ultimately succeeded. This is useful evidence that the Nav2 stack can handle sequential goals and recover from some local navigation difficulty.

Known Notes
Exact recovery counts were not captured for the first two missions.
The harder mission captured number_of_recoveries: 16.
Some commands were run sequentially without manually stopping between every mission. Since missions reached successful status, this was acceptable for Day 97 validation.
Current navigation is still odom-frame only. Map-based SLAM/AMCL localization starts later.
Future work should record a rosbag for waypoint navigation and add a reusable waypoint mission script.