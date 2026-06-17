# C++ / ROS 2 Robotics Simulation Foundation

This repository contains a C++ and ROS 2 robotics simulation project focused on mobile robot state updates, ROS 2 messaging, odometry, TF frames, runtime safety, performance timing, debugging, and regression testing.

The project started as a C++ robotics simulation foundation and was extended into a ROS 2 C++ simulator.

---

## Current Features

* C++ mobile robot simulation core
* ROS 2 `rclcpp` node
* `/cmd_vel` subscriber using `geometry_msgs/msg/Twist`
* `/robot_pose` publisher using `geometry_msgs/msg/Pose2D`
* `/odom` publisher using `nav_msgs/msg/Odometry`
* `/tf` broadcaster for `odom -> base_link`
* Runtime parameters for timestep, initial pose, timeout, and velocity limits
* Velocity clamping using `std::clamp`
* Command timeout safety
* Parameter validation guards
* Performance timing using `std::chrono::steady_clock`
* Debug workflow documentation
* Regression test checklist

---

## ROS 2 Topics

| Topic         | Type                       | Purpose                 |
| ------------- | -------------------------- | ----------------------- |
| `/cmd_vel`    | `geometry_msgs/msg/Twist`  | Velocity command input  |
| `/robot_pose` | `geometry_msgs/msg/Pose2D` | Simple 2D robot pose    |
| `/odom`       | `nav_msgs/msg/Odometry`    | Standard robot odometry |
| `/tf`         | `tf2_msgs/msg/TFMessage`   | Transform tree data     |

---

## Frame Relationship

```txt
odom
  └── base_link
```

The simulator publishes the pose of `base_link` relative to `odom`.

---

## Build

```bash
cd ros2_ws
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

---

## Run

```bash
ros2 run cpp_robotics_sim_ros sim_node
```

Run with parameters:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.1 -p cmd_timeout:=0.5 -p max_linear_velocity:=0.5 -p max_angular_velocity:=0.8
```

---

## Send Commands

One-shot command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Continuous command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Clamp test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 5.0}, angular: {z: 3.0}}"
```

Expected clamped output:

```txt
linear.x=0.50, angular.z=0.80
```

---

## Check Odometry

```bash
ros2 topic type /odom
ros2 topic echo --once /odom --field pose.pose.position
ros2 topic echo --once /odom --field twist.twist
```

---

## Check TF

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

---

## Performance Timing

The simulator prints callback timing:

```txt
Performance: callback avg=... ms, max=... ms, budget=... ms
```

The budget is:

```txt
dt * 1000 ms
```

Examples:

```txt
dt = 0.1   -> 100 ms budget
dt = 0.01  -> 10 ms budget
dt = 0.001 -> 1 ms budget
```

---

## Documentation

Additional documentation:

* `docs/system_architecture.md`
* `docs/debug_workflow.md`
* `docs/regression_tests.md`

---

## Engineering Focus

This project demonstrates:

* robotics simulation architecture
* ROS 2 C++ node development
* topic-based robot control
* odometry publishing
* TF frame broadcasting
* parameterized runtime behavior
* safety guards
* debugging discipline
* performance timing
* regression testing
