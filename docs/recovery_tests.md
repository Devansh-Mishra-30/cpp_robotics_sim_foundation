# Day 96 - Nav2 Recovery Behavior Tests

## Goal

Test Nav2 behavior under normal, blocked, obstacle-constrained, and outside-costmap navigation goals in the odom-frame Gazebo/RViz navigation stack.

## Stack Under Test

- ROS 2 Jazzy
- Gazebo Sim 8
- ros2_control differential-drive robot
- Nav2 planner/controller/behavior stack
- `/cmd_vel` Twist to `/diff_drive_controller/cmd_vel` TwistStamped bridge
- Odom-frame navigation only
- Fixed SDF obstacle world

## Fixed Obstacles

The Gazebo world contains two static obstacle boxes:

### scan_box_front

```xml
<model name="scan_box_front">
  <pose>2.0 0 0.5 0 0 0</pose>
  <size>0.4 1.0 1.0</size>
</model>

Approximate footprint:

x: 1.8 to 2.2
y: -0.5 to 0.5
scan_box_left
<model name="scan_box_left">
  <pose>0 2.0 0.5 0 0 0</pose>
  <size>1.0 0.4 1.0</size>
</model>

Approximate footprint:

x: -0.5 to 0.5
y: 1.8 to 2.2

These obstacles are detected through the simulated lidar and represented in the Nav2 local/global costmaps.

Pre-checks

The following validation checks passed before recovery testing:

ros2 run cpp_robotics_sim_ros nav2_lifecycle_check.sh
ros2 run cpp_robotics_sim_ros nav2_costmap_check.sh
ros2 run cpp_robotics_sim_ros nav2_planner_controller_check.sh
Test 1 - Goal Inside Front Obstacle

Command:

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

Expected behavior:

The target is inside scan_box_front, so the robot should not be able to reach the goal safely.

Observed behavior:

Goal was accepted.
Robot attempted navigation for a long time.
Robot showed oscillation / left-right shaking behavior.
Nav2 recovery count increased repeatedly.
number_of_recoveries reached 18.
distance_remaining stayed nonzero.
Final result was ABORTED.
Final error_code was 105.
Nav2 stack did not crash.

Result:

PASS for blocked-goal recovery/failure behavior observation.
Test 2 - Goal Behind Front Obstacle

Command:

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

Expected behavior:

The target is behind scan_box_front, so Nav2 should try to find a feasible route around the obstacle.

Observed behavior:

Goal was accepted.
Robot was already offset to the side after the previous test.
Nav2 found a feasible side route around the obstacle.
Robot reached the goal.
number_of_recoveries reached 8.
Final distance_remaining was approximately 0.195 m.
Final result was SUCCEEDED.
Final error_code was 0.

Result:

PASS. Nav2 reached the goal when a feasible route around the obstacle existed.
Test 3 - Goal Outside Practical Costmap / Map Region

Command:

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

Expected behavior:

The target is far outside the practical odom-frame global costmap/navigation region, so Nav2 should reject or abort cleanly.

Observed behavior:

Goal was accepted.
Nav2 immediately aborted.
Robot did not try to drive toward the far target.
number_of_recoveries stayed 0.
distance_remaining reported 0.0 because no useful path was generated.
Final result was ABORTED.
Final error_code was 204.
Stack did not crash.

Result:

PASS. Nav2 cleanly rejected the outside-costmap goal.
Summary

Day 96 confirmed that the Nav2 stack can be tested under both successful and failed navigation conditions:

Test	Scenario	Result	Recovery Count	Final Status
1	Goal inside obstacle	Failed cleanly	18	ABORTED
2	Goal behind obstacle	Reached goal	8	SUCCEEDED
3	Goal outside costmap/map region	Failed immediately	0	ABORTED
Interpretation

The robot does not simply crash or silently fail when given bad goals. Nav2 either attempts recovery behavior or aborts cleanly depending on the failure type.

The inside-obstacle case produced repeated recovery behavior and visible oscillation. The behind-obstacle case succeeded when a side route was available. The outside-costmap case was rejected immediately with an abort.

Known Notes
RTPS_TRANSPORT_SHM Error Failed init_port... still appears but did not block lifecycle checks, costmap checks, planner/controller checks, or navigation goals.
Current navigation is odom-frame only.
Map-based SLAM/AMCL localization is planned later.
Future tuning should improve oscillation behavior, recovery timing, and obstacle-adjacent path quality.