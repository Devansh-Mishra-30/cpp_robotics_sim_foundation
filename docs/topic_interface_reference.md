
# ROS 2 Topic Interface Reference



This document defines the ROS 2 topic interfaces used by the `cpp_robotics_sim_ros` simulator.



The purpose of this document is to make the runtime interface clear enough that another engineer can understand what the simulator subscribes to, what it publishes, what message types are used, what fields matter, and how to validate each topic.



---



## 1. Interface Overview



The simulator exposes a planar mobile robot through standard ROS 2 communication interfaces.



```txt

/cmd_vel

   ↓

sim_node

   ↓

/robot_pose

/odom

/tf

/diagnostics

```



The node accepts velocity commands, updates the robot pose, publishes simple 2D pose, publishes standard odometry, broadcasts TF, and reports diagnostics.



---



## 2. Topic Summary



| Topic | Direction | Message Type | Purpose |

|---|---|---|---|

| `/cmd_vel` | Input | `geometry_msgs/msg/Twist` | Velocity command input |

| `/robot_pose` | Output | `geometry_msgs/msg/Pose2D` | Simple 2D pose debugging output |

| `/odom` | Output | `nav_msgs/msg/Odometry` | Standard odometry output |

| `/tf` | Output | `tf2_msgs/msg/TFMessage` | Transform tree output |

| `/diagnostics` | Output | `diagnostic_msgs/msg/DiagnosticArray` | Runtime health and simulator status |



---



## 3. QoS Summary



| Topic | Endpoint | QoS |

|---|---|---|

| `/cmd_vel` | Subscriber | reliable, volatile, keep_last(10) |

| `/robot_pose` | Publisher | reliable, volatile, keep_last(10) |

| `/odom` | Publisher | reliable, volatile, keep_last(10) |

| `/diagnostics` | Publisher | reliable, volatile, keep_last(10) |

| `/tf` | Publisher | handled by `tf2_ros::TransformBroadcaster` |



The state topics use reliable communication because they are low-rate simulator outputs used for debugging and validation.



The durability is volatile because these are live runtime values. Old commands or stale state should not be replayed automatically to late subscribers.



---



# 4. `/cmd_vel`



## Purpose



`/cmd_vel` is the velocity command input topic.



The simulator subscribes to this topic and uses it to update robot motion.



## Message Type



```txt

geometry_msgs/msg/Twist

```



## Direction



```txt

Input to sim_node

```



## Used Fields



```txt

linear.x   = forward linear velocity

angular.z  = yaw angular velocity

```



Other fields are ignored by the current planar simulator:



```txt

linear.y

linear.z

angular.x

angular.y

```



## Example Command



One-shot command:



```bash

ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"

```



Continuous command:



```bash

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"

```



## Safety Behavior



Incoming commands are clamped using configured limits:



```txt

max_linear_velocity

max_angular_velocity

```



With default values:



```txt

linear.x = 5.0  ->  0.5

angular.z = 3.0 ->  0.8

```



If no fresh `/cmd_vel` arrives before `cmd_timeout`, the robot stops.



## Validation Commands



```bash

ros2 topic info /cmd_vel

ros2 topic info /cmd_vel --verbose

```



Expected:



```txt

Type: geometry_msgs/msg/Twist

Subscription count: 1

Reliability: RELIABLE

Durability: VOLATILE

```



---



# 5. `/robot_pose`



## Purpose



`/robot_pose` is a simple 2D pose output used for quick debugging.



It is easier to inspect than the full `/odom` message.



## Message Type



```txt

geometry_msgs/msg/Pose2D

```



## Direction



```txt

Output from sim_node

```



## Fields



```txt

x      = robot x position

y      = robot y position

theta  = robot heading angle in radians

```



## Example Check



```bash

ros2 topic echo --once /robot_pose

```



Expected structure:



```txt

x: ...

y: ...

theta: ...

```



## Validation Criteria



```txt

x changes during forward motion

theta changes during rotational motion

pose stops changing after command timeout

pose starts near launch-configured initial pose

```



---



# 6. `/odom`



## Purpose



`/odom` is the standard ROS 2 odometry output.



It is used by RViz2, validation tools, and future navigation/simulation layers.



## Message Type



```txt

nav_msgs/msg/Odometry

```



## Direction



```txt

Output from sim_node

```



## Frame IDs



```txt

header.frame_id: odom

child_frame_id: base_link

```



## Important Fields



```txt

pose.pose.position.x

pose.pose.position.y

pose.pose.position.z



pose.pose.orientation.x

pose.pose.orientation.y

pose.pose.orientation.z

pose.pose.orientation.w



twist.twist.linear.x

twist.twist.angular.z

```



For planar motion:



```txt

position.z = 0

orientation represents yaw only

twist.linear.x = current linear velocity

twist.angular.z = current angular velocity

```



## Quaternion Convention



The simulator converts planar heading `theta` into yaw quaternion form:



```txt

q.x = 0

q.y = 0

q.z = sin(theta / 2)

q.w = cos(theta / 2)

```



## Example Checks



```bash

ros2 topic type /odom

ros2 topic echo --once /odom

ros2 topic echo --once /odom --field pose.pose.position

ros2 topic echo --once /odom --field twist.twist

```



Expected type:



```txt

nav_msgs/msg/Odometry

```



## Validation Criteria



```txt

header.frame_id is odom

child_frame_id is base_link

position x/y matches /robot_pose

orientation matches theta as yaw quaternion

twist values match clamped command

```



---



# 7. `/tf`



## Purpose



`/tf` publishes the transform tree relationship between the world/odometry frame and the robot body frame.



## Message Type



```txt

tf2_msgs/msg/TFMessage

```



## Direction



```txt

Output from tf2_ros::TransformBroadcaster

```



## Frame Relationship



```txt

odom

  └── base_link

```



This means `base_link` is the robot body frame, expressed relative to the `odom` frame.



## Example Check



```bash

ros2 run tf2_ros tf2_echo odom base_link

```



Expected structure:



```txt

Translation: [x, y, 0.000]

Rotation: Quaternion [0.000, 0.000, z, w]

```



## Validation Criteria



```txt

transform exists

parent frame is odom

child frame is base_link

translation matches robot x/y

rotation matches robot theta

RViz2 can use odom as Fixed Frame

```



---



# 8. `/diagnostics`



## Purpose



`/diagnostics` publishes structured runtime health information for the simulator.



It is used to inspect node status, timeout state, current command/state values, and callback timing.



## Message Type



```txt

diagnostic_msgs/msg/DiagnosticArray

```



## Direction



```txt

Output from sim_node

```



## Status Levels



```txt

level: 0  -> OK

level: 1  -> WARN

```



Current behavior:



```txt

OK   = simulator running with fresh command input

WARN = cmd_vel timeout active

```



## Diagnostic Identity



Expected fields:



```txt

name: sim_node

hardware_id: cpp_robotics_sim_ros

```



## Key-Value Fields



The diagnostic report includes:



```txt

dt

cmd_timeout

time_since_cmd

timeout_active

linear_velocity

angular_velocity

max_linear_velocity

max_angular_velocity

pose_x

pose_y

pose_theta

callback_time_ms

average_callback_time_ms

max_callback_time_ms

timing_budget_ms

callback_count

```



## Example Checks



```bash

ros2 topic echo --once /diagnostics

ros2 topic info /diagnostics --verbose

```



Expected type:



```txt

diagnostic_msgs/msg/DiagnosticArray

```



Expected QoS:



```txt

Reliability: RELIABLE

Durability: VOLATILE

```



## OK-State Test



Run continuous command input:



```bash

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"

```



Then check diagnostics:



```bash

ros2 topic echo --once /diagnostics

```



Expected:



```txt

level: 0

message: Simulator running

timeout_active: false

```



## WARN-State Test



Stop `/cmd_vel`, wait longer than `cmd_timeout`, then run:



```bash

ros2 topic echo --once /diagnostics

```



Expected:



```txt

level: 1

message: cmd_vel timeout active

timeout_active: true

```



---



# 9. Interface Flow



## Command-to-State Flow



```txt

/cmd_vel

   ↓

cmdVelCallback()

   ↓

store latest command and timestamp

   ↓

timerCallback()

   ↓

check timeout

   ↓

clamp velocity

   ↓

integrate pose

   ↓

publish /robot_pose

   ↓

publish /odom

   ↓

broadcast /tf

   ↓

publish /diagnostics

```



## Runtime Inspection Flow



```txt

ros2 topic list

   ↓

ros2 topic echo /robot_pose

   ↓

ros2 topic echo /odom

   ↓

tf2_echo odom base_link

   ↓

ros2 topic echo /diagnostics

```



---



# 10. Interface Contract



The simulator should satisfy this contract:



```txt

If /cmd_vel publishes valid commands:

  robot pose should update



If /cmd_vel stops:

  robot should stop after cmd_timeout



If robot pose updates:

  /robot_pose, /odom, and /tf should remain consistent



If diagnostics is active:

  /diagnostics should report OK or WARN based on timeout state



If launch arguments override parameters:

  topic behavior should reflect the overridden values

```



---



# 11. Full Interface Validation Commands



Start simulator:



```bash

ros2 launch cpp_robotics_sim_ros sim.launch.py

```



List topics:



```bash

ros2 topic list

```



Check types:



```bash

ros2 topic type /cmd_vel

ros2 topic type /robot_pose

ros2 topic type /odom

ros2 topic type /tf

ros2 topic type /diagnostics

```



Check messages:



```bash

ros2 topic echo --once /robot_pose

ros2 topic echo --once /odom

ros2 topic echo --once /diagnostics

ros2 run tf2_ros tf2_echo odom base_link

```



Check QoS:



```bash

ros2 topic info /cmd_vel --verbose

ros2 topic info /robot_pose --verbose

ros2 topic info /odom --verbose

ros2 topic info /diagnostics --verbose

```



Send command:



```bash

ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}"

```



Run launch regression:



```bash

./scripts/day68_launch_regression.sh

```



---



# 12. Common Interface Failures



| Failure | Likely Cause | First Check |

|---|---|---|

| `/cmd_vel` has no subscriber | node not running | `ros2 topic info /cmd_vel` |

| `/robot_pose` missing | publisher not created or node crashed | `ros2 topic list` |

| `/odom` missing | odom publisher missing or node not rebuilt | `ros2 topic list` |

| `/tf` missing | transform broadcaster issue | `ros2 run tf2_ros tf2_echo odom base_link` |

| `/diagnostics` missing | diagnostics publisher missing | `ros2 topic list` |

| wrong message type | topic name reused incorrectly | `ros2 topic type <topic>` |

| no motion after command | command not received, timeout active, or velocity clamped to zero | `/diagnostics` and `/robot_pose` |

| motion never stops | timeout logic broken | stop `/cmd_vel` and watch diagnostics |

| RViz frame error | TF missing or wrong fixed frame | set Fixed Frame to `odom` |

| diagnostics always WARN | no active `/cmd_vel` stream | publish `/cmd_vel` at 10 Hz |

| diagnostics always OK | timeout state not wired to diagnostics | check timeout logic |



---



# 13. Interview Explanation



The simulator exposes a clear ROS 2 topic interface. It subscribes to `/cmd_vel` using `geometry_msgs/msg/Twist`, publishes a simple `/robot_pose` using `geometry_msgs/msg/Pose2D`, publishes standard `/odom` using `nav_msgs/msg/Odometry`, broadcasts `odom -> base_link` on TF, and publishes runtime health on `/diagnostics` using `diagnostic_msgs/msg/DiagnosticArray`. I documented each topic’s type, direction, important fields, QoS behavior, validation commands, and common failure modes so the interface is easy to test and explain.

