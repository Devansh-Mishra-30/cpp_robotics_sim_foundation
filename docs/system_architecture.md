# ROS 2 Simulator System Architecture

This document explains the architecture of the ROS 2 C++ robot simulator.

---

## 1. System Goal

The simulator models a simple planar mobile robot controlled through `/cmd_vel`.

It accepts velocity commands, updates robot pose using planar kinematics, and publishes robot state through:

* `/robot_pose`
* `/odom`
* `/tf`

The system includes safety checks, velocity clamping, command timeout behavior, parameter validation, performance timing, debug workflows, and regression tests.

---

## 2. ROS 2 Node

Node name:

```txt
/sim_node
```

Executable:

```txt
sim_node
```

Package:

```txt
cpp_robotics_sim_ros
```

The node is written in C++ using `rclcpp`.

---

## 3. Topic Architecture

```txt
/cmd_vel
   │
   ▼
+----------------+
|    sim_node    |
|                |
|  cmd callback  |
|  timer update  |
|  pose update   |
|  odom publish  |
|  TF broadcast  |
+----------------+
   │       │       │
   ▼       ▼       ▼
/robot_pose   /odom   /tf
```

---

## 4. Inputs

### `/cmd_vel`

Type:

```txt
geometry_msgs/msg/Twist
```

Used fields:

```txt
linear.x   = forward velocity command
angular.z  = yaw rate command
```

The simulator clamps incoming commands using configured velocity limits.

---

## 5. Outputs

### `/robot_pose`

Type:

```txt
geometry_msgs/msg/Pose2D
```

Fields:

```txt
x
y
theta
```

This is a simple 2D pose output for quick debugging.

---

### `/odom`

Type:

```txt
nav_msgs/msg/Odometry
```

The odometry message includes:

```txt
timestamp
parent frame: odom
child frame: base_link
position
orientation quaternion
linear velocity
angular velocity
covariance fields
```

The simulator uses `/odom` to publish the robot state in a ROS-standard format.

---

### `/tf`

Type:

```txt
tf2_msgs/msg/TFMessage
```

The TF relationship is:

```txt
odom -> base_link
```

This means the robot body frame `base_link` is located and oriented relative to the `odom` frame.

---

## 6. Frame Tree

```txt
odom
  └── base_link
```

`odom` is the parent frame.

`base_link` is the moving robot body frame.

---

## 7. Kinematic Model

The simulator uses planar unicycle-style kinematics.

State:

```txt
x, y, theta
```

Command:

```txt
v = linear velocity
w = angular velocity
```

Update equations:

```txt
theta = theta + w * dt
x     = x + v * cos(theta) * dt
y     = y + v * sin(theta) * dt
```

The heading angle is wrapped using:

```cpp
theta = atan2(sin(theta), cos(theta));
```

This keeps `theta` in a stable angular range.

---

## 8. Quaternion Conversion

ROS odometry and TF use quaternions for orientation.

For planar yaw:

```cpp
q.x = 0.0;
q.y = 0.0;
q.z = sin(theta / 2.0);
q.w = cos(theta / 2.0);
```

Roll and pitch are zero, so only `z` and `w` are needed to represent yaw.

---

## 9. Safety Logic

### Velocity Clamping

Incoming velocity commands are limited using:

```cpp
std::clamp(...)
```

Example:

```txt
linear.x = 5.0  ->  0.5
angular.z = 3.0 ->  0.8
```

This prevents unrealistic or unsafe commands from driving the simulator.

---

### Command Timeout

The simulator stores the time of the last received `/cmd_vel`.

If no fresh command arrives within `cmd_timeout`, the robot stops:

```txt
linear_velocity = 0
angular_velocity = 0
```

This prevents stale commands from moving the robot forever.

---

## 10. Parameter Validation

The simulator rejects invalid runtime parameters:

```txt
dt <= 0
cmd_timeout <= 0
max_linear_velocity < 0
max_angular_velocity < 0
```

This follows the fail-fast principle: bad configuration should stop the node before it produces misleading simulation results.

---

## 11. Performance Timing

The timer callback is measured using:

```cpp
std::chrono::steady_clock
```

The simulator reports:

```txt
average callback time
max callback time
timing budget = dt * 1000 ms
```

This helps verify whether the simulator can keep up with the intended update rate.

---

## 12. Validation and Regression

The simulator is validated using repeatable regression tests:

```txt
zero command
straight motion
pure rotation
curved motion
positive clamp
negative clamp
timeout
continuous command
invalid parameter rejection
/odom publishing
/tf publishing
odom/TF consistency
performance timing
```

These tests are documented in:

```txt
docs/regression_tests.md
```

---

## 13. Debug Workflow

Debugging commands and common failure modes are documented in:

```txt
docs/debug_workflow.md
```

The main debugging principle is:

```txt
Do not randomly edit code.
First classify the failure, then test systematically.
```

---

## 14. Current Limitations

The current simulator is intentionally simple.

Limitations:

```txt
No full physics engine
No wheel slip model
No sensor noise yet
No IMU or lidar topic yet
No Gazebo physics integration yet
No Nav2 stack yet
No hardware interface yet
```

These are planned future extensions.

---

## 15. Future Work

Planned improvements:

```txt
YAML configuration
launch files
rosbag2 recording
RViz visualization
URDF/Xacro robot model
Gazebo integration
sensor topic simulation
noise model
Monte Carlo validation
unit tests
CI pipeline
```
