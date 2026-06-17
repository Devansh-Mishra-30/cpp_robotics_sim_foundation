# ROS 2 Simulator Debug Workflow

This document is the debugging checklist for the `cpp_robotics_sim_ros` simulator.

Core rule:

Do not randomly edit code. First identify whether the problem is a build issue, dependency issue, workspace/source issue, node startup issue, topic issue, parameter issue, callback issue, TF issue, or runtime behavior issue.

---

## 1. Build Check

From the ROS 2 workspace:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

Pass condition:

```txt
Summary: 1 package finished
```

If the build fails, check:

* Wrong include path
* Missing semicolon
* Wrong variable name
* Missing dependency in `package.xml`
* Missing `find_package(...)` in `CMakeLists.txt`
* Missing dependency inside `ament_target_dependencies(...)`

---

## 2. Run Node

```bash
ros2 run cpp_robotics_sim_ros sim_node
```

Pass condition:

```txt
sim_node starts without crashing
```

Expected startup logs should include loaded parameters and simulator start message.

---

## 3. Check Node Exists

```bash
ros2 node list
```

Expected:

```txt
/sim_node
```

If `/sim_node` does not appear:

* Node may not be running
* Wrong workspace may not be sourced
* Build may have failed
* Executable name may be wrong
* Node may have crashed at startup

---

## 4. Check Topics

```bash
ros2 topic list
```

Expected:

```txt
/cmd_vel
/odom
/robot_pose
/tf
```

If a topic is missing, check whether the publisher/subscriber was created and whether it is stored as a class member.

---

## 5. Check Topic Types

```bash
ros2 topic type /cmd_vel
ros2 topic type /robot_pose
ros2 topic type /odom
ros2 topic type /tf
```

Expected:

```txt
/cmd_vel     -> geometry_msgs/msg/Twist
/robot_pose -> geometry_msgs/msg/Pose2D
/odom       -> nav_msgs/msg/Odometry
/tf         -> tf2_msgs/msg/TFMessage
```

If a topic type is wrong, check the publisher/subscriber message type in code.

---

## 6. Check Publish Rates

```bash
ros2 topic hz /robot_pose
ros2 topic hz /odom
ros2 topic hz /tf
```

Expected for `dt = 0.1`:

```txt
approximately 10 Hz
```

Because:

```txt
rate = 1 / dt = 1 / 0.1 = 10 Hz
```

If the rate is wrong:

* Check `dt`
* Check timer creation
* Check if the timer callback is running
* Check if the node is spinning
* Check whether the topic is actually being published inside the timer callback

---

## 7. Check Parameters

```bash
ros2 param list /sim_node
```

Expected parameters:

```txt
dt
initial_x
initial_y
initial_theta
cmd_timeout
max_linear_velocity
max_angular_velocity
```

Check specific values:

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

If parameter values are not what you expect:

* Make sure you passed them using `--ros-args -p`
* Make sure there are no spaces around `:=`
* Make sure the node was restarted after changing launch/runtime values
* Make sure the correct workspace was sourced

Correct parameter override format:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.1 -p cmd_timeout:=0.5 -p max_linear_velocity:=0.5 -p max_angular_velocity:=0.8
```

---

## 8. Check Command Input

Send one command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Expected:

```txt
Node receives cmd_vel
Pose changes briefly
Timeout stops robot after cmd_timeout
```

If `/cmd_vel` does not affect motion, check:

* Subscriber topic name is `/cmd_vel`
* Subscriber type is `geometry_msgs/msg/Twist`
* Callback is being called
* `linear_velocity_` and `angular_velocity_` are being updated
* Timeout is not immediately resetting velocities
* The timer callback is using the updated velocities

---

## 9. Check Continuous Command Behavior

Publish continuously at 10 Hz:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Expected:

```txt
Pose keeps changing
No timeout while command is publishing
```

If timeout happens while publishing:

* Check command publish rate
* Check `cmd_timeout`
* Check whether `last_cmd_time_` is updated inside `cmdVelCallback()`

Important:

```txt
1 Hz command = one command every 1.0 sec
cmd_timeout = 0.5 sec
robot will stop between commands

10 Hz command = one command every 0.1 sec
cmd_timeout = 0.5 sec
robot should keep moving
```

---

## 10. Check Velocity Clamping

Run node with limits:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p max_linear_velocity:=0.5 -p max_angular_velocity:=0.8
```

Send excessive positive command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 5.0}, angular: {z: 3.0}}"
```

Expected:

```txt
Received cmd_vel: linear.x=0.50, angular.z=0.80
```

Send excessive negative command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: -5.0}, angular: {z: -3.0}}"
```

Expected:

```txt
Received cmd_vel: linear.x=-0.50, angular.z=-0.80
```

Send inside-limit command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.4}}"
```

Expected:

```txt
Received cmd_vel: linear.x=0.30, angular.z=0.40
```

If clamp does not work, check:

* `std::clamp(...)` usage
* Max velocity parameter values
* Whether the callback logs clamped values or raw values
* Whether `max_linear_velocity_` and `max_angular_velocity_` were loaded correctly

---

## 11. Check Odometry

Check position only:

```bash
ros2 topic echo --once /odom --field pose.pose.position
```

Check orientation only:

```bash
ros2 topic echo --once /odom --field pose.pose.orientation
```

Check velocity only:

```bash
ros2 topic echo --once /odom --field twist.twist
```

Expected:

```txt
pose.pose.position.x and y match robot motion
orientation uses quaternion z and w for yaw
twist.twist.linear.x shows forward velocity
twist.twist.angular.z shows yaw rate
```

If full `/odom` output is too large, avoid printing covariance by using `--field`.

---

## 12. Check TF

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
Translation: [x, y, 0.000]
Rotation: Quaternion [0.000, 0.000, z, w]
```

When the robot moves, translation and rotation should update.

If `tf2_echo odom base_link` fails, check:

* `/tf` appears in `ros2 topic list`
* `tf_broadcaster_` exists as a class member
* `publishTransform()` is called inside the timer callback
* `sendTransform(transform_msg)` is called
* `header.frame_id = "odom"`
* `child_frame_id = "base_link"`
* Correct command order: `tf2_echo odom base_link`

---

## 13. Check `/odom` and `/tf` Consistency

Check `/odom` position:

```bash
ros2 topic echo --once /odom --field pose.pose.position
```

Check TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
/odom pose.pose.position.x ≈ TF translation x
/odom pose.pose.position.y ≈ TF translation y
```

If they do not match:

* Check whether `/odom` and `/tf` both use `pose_.x`
* Check whether `/odom` and `/tf` both use `pose_.y`
* Check whether both use the same quaternion formula
* Check if timestamps are being updated

---

## 14. Parameter Validation Debugging

Invalid `dt` test:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.0
```

Expected:

```txt
Invalid parameter: dt must be > 0
Invalid simulator parameters
```

Invalid timeout test:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p cmd_timeout:=0.0
```

Expected:

```txt
Invalid parameter: cmd_timeout must be > 0
Invalid simulator parameters
```

Invalid linear velocity limit:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p max_linear_velocity:=-1.0
```

Expected:

```txt
Invalid parameter: max_linear_velocity must be >= 0
Invalid simulator parameters
```

Invalid angular velocity limit:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p max_angular_velocity:=-1.0
```

Expected:

```txt
Invalid parameter: max_angular_velocity must be >= 0
Invalid simulator parameters
```

If validation does not trigger:

* Check `validateParameters()`
* Check whether validation is called after loading parameters
* Check whether `throw std::runtime_error(...)` is present
* Check whether `<stdexcept>` is included

---

## 15. Common Build Error Patterns

### Wrong include path

Error:

```txt
fatal error: tf2_ros/transform_broadcaster.hpp: No such file or directory
```

Diagnosis:

```txt
Wrong include path or missing package.
```

Fix:

```cpp
#include "tf2_ros/transform_broadcaster.h"
```

---

### Wrong variable name

Error:

```txt
‘transform’ was not declared in this scope
```

Diagnosis:

```txt
Declared one variable name but used another.
```

Example wrong code:

```cpp
geometry_msgs::msg::TransformStamped transform_msg;
transform.header.frame_id = "odom";
```

Fix:

```cpp
transform_msg.header.frame_id = "odom";
```

---

### Wrong broadcaster name

Error:

```txt
‘transform_broadcaster_’ was not declared in this scope
```

Diagnosis:

```txt
Member variable is named differently.
```

Fix:

```cpp
tf_broadcaster_->sendTransform(transform_msg);
```

---

### Missing dependency

Symptoms:

```txt
Package compiles fail after adding nav_msgs or tf2_ros
```

Check `package.xml`:

```xml
<depend>nav_msgs</depend>
<depend>tf2_ros</depend>
```

Check `CMakeLists.txt`:

```cmake
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

ament_target_dependencies(sim_node
  rclcpp
  geometry_msgs
  nav_msgs
  tf2_ros
)
```

---

## 16. Common Runtime Bug Patterns

### Topic missing

If `/odom` or `/tf` is missing:

Check:

* Publisher or broadcaster was created
* Publisher/broadcaster is stored as a member variable
* Timer callback is running
* Publish/sendTransform call exists
* Correct workspace was sourced
* Node was restarted after rebuilding

---

### Topic exists but no data

Check:

* Timer callback is publishing
* Node is spinning
* Message publish call exists
* Callback is not blocked
* You are echoing the correct topic

---

### `/cmd_vel` does not move robot

Check:

* Subscriber topic name is `/cmd_vel`
* Subscriber message type is `geometry_msgs/msg/Twist`
* `cmdVelCallback()` is running
* `linear_velocity_` and `angular_velocity_` are updated
* Timeout is not immediately setting velocities to zero
* Timer callback is using velocity values for integration

---

### Robot moves and stops repeatedly

Likely cause:

```txt
Command publish frequency is slower than cmd_timeout.
```

Example:

```txt
Command frequency = 1 Hz
Command period = 1.0 sec
cmd_timeout = 0.5 sec
Robot stops between commands
```

Fix:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

or:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p cmd_timeout:=2.0
```

---

### TF not working

Check:

* `tf2_ros` dependency exists
* `TransformBroadcaster` exists as a member variable
* `sendTransform()` is called every timer update
* `header.frame_id` and `child_frame_id` are correct
* `tf2_echo` order is correct: `odom base_link`

---

## 17. Controlled Test Commands

Zero motion:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Straight motion:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}"
```

Pure rotation:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

Curved motion:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Clamp test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 5.0}, angular: {z: 3.0}}"
```

Timeout test:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

---

## 18. Debugging Principle

Do not randomly edit code.

First classify the failure:

* Build error
* Missing dependency
* Wrong workspace/source issue
* Node startup issue
* Missing topic
* Wrong message type
* Parameter issue
* Subscriber/callback issue
* Timer/publisher issue
* TF frame issue
* Runtime behavior issue

Then debug in this order:

1. Build
2. Source workspace
3. Run node
4. Check node list
5. Check topic list
6. Check topic types
7. Check topic rates
8. Echo topics
9. Check parameters
10. Check TF
11. Send controlled commands
12. Compare expected behavior to actual behavior

---

## 19. Fail Fast Principle

The simulator should stop early when configuration is invalid.

Examples:

```txt
dt <= 0
cmd_timeout <= 0
max_linear_velocity < 0
max_angular_velocity < 0
```

Failing fast prevents meaningless simulation results and makes the cause of the problem obvious.
