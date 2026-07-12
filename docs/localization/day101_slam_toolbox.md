# Day 101 — SLAM Toolbox Integration

## Goal

Integrate SLAM Toolbox with the existing ROS 2 Jazzy differential-drive Gazebo simulation without breaking the Day 100 Nav2 stack.

## What SLAM Toolbox does

SLAM Toolbox performs simultaneous localization and mapping using:

* lidar scans from `/scan`
* wheel odometry through the TF tree
* scan matching
* pose-graph optimization
* loop-closure support

During mapping, it publishes an occupancy-grid map and the correction transform from `map` to `odom`.

## Frame ownership

The localization TF chain is:

```text
map -> odom -> base_link -> lidar_link -> sensor frame
```

Ownership:

* `slam_toolbox` publishes `map -> odom`
* `diff_drive_controller` publishes `odom -> base_link`
* `robot_state_publisher` publishes robot-link transforms
* `static_transform_publisher` bridges `lidar_link` to the Gazebo lidar frame

This avoids duplicate ownership of `odom -> base_link`.

## Topics

### Inputs

* `/scan`
* `/tf`
* `/tf_static`

### Outputs

* `/map`
* `/map_metadata`
* `map -> odom` TF

### Supporting odometry

* `/diff_drive_controller/odom`

## Files added or updated

* `ros2_ws/src/cpp_robotics_sim_ros/launch/slam_mapping.launch.py`
* `ros2_ws/src/cpp_robotics_sim_ros/config/slam_toolbox.yaml`
* `ros2_ws/src/cpp_robotics_sim_ros/package.xml`

## Lifecycle behavior

SLAM Toolbox is a lifecycle node.

The launch file starts a Nav2 lifecycle manager that automatically:

1. Configures `slam_toolbox`.
2. Activates `slam_toolbox`.

Bond monitoring is disabled with:

```python
"bond_timeout": 0.0
```

This was required because SLAM Toolbox transitioned successfully to `active`, but the lifecycle manager did not receive its bond heartbeat in this setup.

## Launch command

```bash
cd ~/robotics_projects/cpp_robotics_sim_foundation/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch cpp_robotics_sim_ros slam_mapping.launch.py
```

## Validation commands

### Check lifecycle state

```bash
ros2 lifecycle get /slam_toolbox
```

Expected:

```text
active [3]
```

### Check required topics

```bash
ros2 topic list | sort | \
grep -E '^/(map|map_metadata|scan|tf|tf_static|diff_drive_controller/odom)$'
```

### Check map data

```bash
ros2 topic echo --once /map --field info
```

### Check lidar header

```bash
ros2 topic echo --once /scan --field header
```

### Check SLAM correction transform

```bash
ros2 run tf2_ros tf2_echo map odom
```

### Check odometry transform

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

### Check controllers

```bash
ros2 control list_controllers
```

## Motion test

Forward command:

```bash
timeout 4 ros2 topic pub -r 10 \
  /diff_drive_controller/cmd_vel \
  geometry_msgs/msg/TwistStamped \
  "{header: {frame_id: base_link}, twist: {linear: {x: 0.15}, angular: {z: 0.0}}}"
```

Stop command:

```bash
ros2 topic pub --once \
  /diff_drive_controller/cmd_vel \
  geometry_msgs/msg/TwistStamped \
  "{header: {frame_id: base_link}, twist: {linear: {x: 0.0}, angular: {z: 0.0}}}"
```

## Validation evidence

Initial map:

```text
resolution: 0.05 m/cell
width: 45
height: 45
```

Map after movement:

```text
resolution: 0.05 m/cell
width: 76
height: 293
```

This proves that SLAM Toolbox incorporated robot motion and lidar scans into the occupancy grid.

After movement, `map -> odom` was no longer an identity transform:

```text
translation:
  x: 0.283 m
  y: 0.051 m

yaw:
  0.227 rad
  approximately 13 degrees
```

This proves SLAM Toolbox corrected the wheel-odometry frame relative to the map.

## Rosbag evidence

Bag path:

```text
bags/day101_slam_mapping
```

Recorded topics:

* `/tf`
* `/tf_static`
* `/scan`
* `/map`
* `/map_metadata`
* `/diff_drive_controller/odom`
* `/diff_drive_controller/cmd_vel`

Bag summary:

```text
Duration: 47.926 seconds
Messages: 8497
/scan: 468
/map: 25
/map_metadata: 25
/diff_drive_controller/odom: 2333
/diff_drive_controller/cmd_vel: 25
/tf: 5619
/tf_static: 2
```

## Known warnings

### Root-link inertia warning

`robot_state_publisher` reports that KDL does not support inertia on the root link.

This warning existed before Day 101 and does not prevent mapping.

### Static transform argument warning

The old positional syntax for `static_transform_publisher` is deprecated.

The transform still publishes correctly. This can be cleaned up later without changing frame ownership.

### Startup message-filter warning

A lidar message may be dropped during startup while the TF buffer is still filling.

This is acceptable if it occurs only during startup and mapping continues normally.

### Lifecycle bond behavior

SLAM Toolbox configured and activated correctly, but lifecycle bond monitoring did not establish successfully in this setup.

The lifecycle manager therefore uses:

```python
"bond_timeout": 0.0
```

Automatic configuration and activation remain enabled.

## Day 101 result

Day 101 acceptance criteria satisfied:

* SLAM Toolbox launches with simulated lidar.
* `/map` exists.
* `/scan` exists.
* The TF chain is valid.
* Map dimensions grow after robot motion.
* The `map -> odom` correction exists.
* Rosbag evidence is saved.
* Lifecycle activation is automatic.
