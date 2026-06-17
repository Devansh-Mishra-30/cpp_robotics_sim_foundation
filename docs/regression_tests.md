# ROS 2 Simulator Regression Tests

This document defines repeatable regression tests for the ROS 2 C++ simulator.

Regression testing means running the same known scenarios after code changes to confirm old behavior still works.

---

## Standard Build

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

---

## Standard Run

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.1 -p cmd_timeout:=0.5 -p max_linear_velocity:=0.5 -p max_angular_velocity:=0.8
```

Expected:

```txt
Node starts successfully
Parameters are loaded
/robot_pose publishes
/odom publishes
/tf publishes
```

---

## Test 1: Zero Command

Command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Check:

```bash
ros2 topic echo --once /robot_pose
```

Expected:

```txt
x stays approximately unchanged
y stays approximately unchanged
theta stays approximately unchanged
```

Pass condition:

```txt
Robot does not move under zero command.
```

---

## Test 2: Straight Motion

Restart node first.

Command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}"
```

Let it run for about 2 seconds, then stop with `Ctrl + C`.

Check:

```bash
ros2 topic echo --once /robot_pose
```

Expected:

```txt
x increases
y stays close to 0
theta stays close to 0
```

Pass condition:

```txt
Straight-line motion works.
```

---

## Test 3: Pure Rotation

Restart node first.

Command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

Let it run for about 2 seconds, then stop.

Check:

```bash
ros2 topic echo --once /robot_pose
```

Expected:

```txt
x stays close to 0
y stays close to 0
theta changes
```

Pass condition:

```txt
Pure rotation works without translation drift.
```

---

## Test 4: Curved Motion

Restart node first.

Command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Expected:

```txt
x changes
y changes
theta changes
robot follows curved motion
```

Pass condition:

```txt
Combined linear and angular velocity creates curved motion.
```

---

## Test 5: Positive Velocity Clamp

Command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 5.0}, angular: {z: 3.0}}"
```

Expected node log:

```txt
Received cmd_vel: linear.x=0.50, angular.z=0.80
```

Pass condition:

```txt
Positive commands above limits are clamped.
```

---

## Test 6: Negative Velocity Clamp

Command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: -5.0}, angular: {z: -3.0}}"
```

Expected node log:

```txt
Received cmd_vel: linear.x=-0.50, angular.z=-0.80
```

Pass condition:

```txt
Negative commands below limits are clamped.
```

---

## Test 7: Timeout

Command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Expected:

```txt
Robot moves briefly
After 0.5 sec, timeout warning appears
Velocity becomes zero
Pose stops changing
```

Expected log:

```txt
cmd_vel timeout: stopping robot
```

Pass condition:

```txt
Stale command does not keep robot moving forever.
```

---

## Test 8: Continuous Command No Timeout

Command:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
```

Expected:

```txt
Robot keeps moving
No timeout warning while command is publishing
```

Pass condition:

```txt
Timeout does not trigger while fresh commands arrive faster than cmd_timeout.
```

---

## Test 9: Invalid dt Rejection

Command:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.0
```

Expected:

```txt
Node refuses to start
Invalid parameter error is printed
```

Pass condition:

```txt
dt <= 0 is rejected.
```

---

## Test 10: Invalid Timeout Rejection

Command:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p cmd_timeout:=0.0
```

Expected:

```txt
Node refuses to start
Invalid parameter error is printed
```

Pass condition:

```txt
cmd_timeout <= 0 is rejected.
```

---

## Test 11: Invalid Velocity Limit Rejection

Commands:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p max_linear_velocity:=-1.0
```

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p max_angular_velocity:=-1.0
```

Expected:

```txt
Node refuses to start
Invalid parameter error is printed
```

Pass condition:

```txt
Negative velocity limits are rejected.
```

---

## Test 12: Odometry Topic

Check:

```bash
ros2 topic type /odom
```

Expected:

```txt
nav_msgs/msg/Odometry
```

Check position:

```bash
ros2 topic echo --once /odom --field pose.pose.position
```

Expected:

```txt
Position matches robot motion.
```

Pass condition:

```txt
/odom exists and publishes robot pose.
```

---

## Test 13: TF Topic

Check:

```bash
ros2 topic type /tf
```

Expected:

```txt
tf2_msgs/msg/TFMessage
```

Check transform:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
Translation and rotation are visible.
Values update when robot moves.
```

Pass condition:

```txt
TF transform odom -> base_link is published.
```

---

## Test 14: Odom and TF Consistency

Check odometry position:

```bash
ros2 topic echo --once /odom --field pose.pose.position
```

Check TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Expected:

```txt
/odom pose.pose.position.x approximately equals TF translation x
/odom pose.pose.position.y approximately equals TF translation y
```

Pass condition:

```txt
/odom and /tf describe the same robot pose.
```

---

## Test 15: Performance Timing

Run:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.1
```

Expected log:

```txt
Performance: callback avg=... ms, max=... ms, budget=100.00 ms
```

Run:

```bash
ros2 run cpp_robotics_sim_ros sim_node --ros-args -p dt:=0.01
```

Expected log:

```txt
Performance: callback avg=... ms, max=... ms, budget=10.00 ms
```

Pass condition:

```txt
Callback average time is below timing budget.
```

---

## Regression Summary Checklist

- [Y] Zero command: pose remains unchanged
- [Y] Straight motion: x increases, y and theta stay stable
- [Y] Pure rotation: theta changes, x and y stay stable
- [Y] Curved motion: x, y, and theta change
- [Y] Positive clamp: large positive command clamps to max limits
- [Y] Negative clamp: large negative command clamps to negative max limits
- [Y] Timeout: robot stops after stale command
- [Y] Continuous command: no timeout while publishing faster than cmd_timeout
- [Y] Invalid dt: node rejects dt <= 0
- [Y] Invalid timeout: node rejects cmd_timeout <= 0
- [Y] Invalid velocity limits: node rejects negative limits
- [Y] /odom: nav_msgs/Odometry publishes correctly
- [Y] /tf: odom → base_link transform is available
- [Y] Odom/TF consistency: /odom pose matches TF translation
- [Y] Performance: average callback time stays below timing budget

---

## Regression Principle

After every major code change, run at least:

```txt
Build test
Zero command test
Straight motion test
Clamp test
Timeout test
/odom test
/tf test
Performance timing check
```

The simulator passes regression if existing behavior still works after new changes.
