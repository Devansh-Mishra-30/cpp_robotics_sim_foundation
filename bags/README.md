# Bags

This folder is used for local rosbag2 recordings.

Actual bag recordings are ignored by Git because they can become large.

## Day 65 Baseline Recording

Record:

```bash
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