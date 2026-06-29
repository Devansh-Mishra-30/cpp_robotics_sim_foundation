# Day 81 — Nav2 Architecture Notes

## Goal

Understand the basic architecture of Nav2 for robotics simulation and interview readiness.

Main concepts:

* `map`
* `odom`
* `base_link`
* costmaps
* planner
* controller
* recovery behavior
* lifecycle nodes

This is a concept day. The project does not run Nav2 yet.

---

## 1. Big Picture

Nav2 is the ROS 2 navigation stack.

It helps a mobile robot move from its current position to a goal position while avoiding obstacles.

A simple mental model is:

```txt
localization tells the robot where it is
costmaps tell the robot where it is safe to move
planner decides the path
controller sends velocity commands
recovery handles failure cases
```

---

## 2. Important Frames

Navigation depends heavily on TF frames.

The most important frame chain is:

```txt
map -> odom -> base_link
```

---

## 3. `base_link`

`base_link` is the robot body frame.

It is attached to the robot chassis.

Sensors, wheels, lidar, camera, and robot geometry are usually defined relative to `base_link`.

Interview answer:

```txt
base_link is the moving coordinate frame attached to the robot body.
```

---

## 4. `odom`

`odom` is the local odometry frame.

It is smooth and continuous, but it can drift over time.

Wheel odometry usually contributes to the `odom -> base_link` transform.

Interview answer:

```txt
odom is good for smooth short-term motion, but it accumulates drift.
```

---

## 5. `map`

`map` is the globally corrected world frame.

It is usually produced by localization systems such as:

* AMCL
* SLAM
* GPS-based localization
* external localization systems

The `map` frame can correct drift.

Interview answer:

```txt
map is globally stable, but it can jump when localization corrects the robot pose.
```

---

## 6. Why `map`, `odom`, and `base_link` Are Separate

The robot needs both:

1. Smooth local motion.
2. Globally corrected position.

That is why ROS navigation commonly uses:

```txt
map -> odom -> base_link
```

`odom -> base_link` is smooth but drifts.

`map -> odom` corrects global drift.

Interview answer:

```txt
The map frame gives global correction, odom gives smooth local motion, and base_link represents the robot body.
```

---

## 7. Costmaps

A costmap is a grid representation of the world.

Each cell has a cost.

Example:

```txt
free space       -> low cost
obstacle         -> high/lethal cost
near obstacle    -> inflated cost
unknown space    -> unknown cost
```

Nav2 usually uses two costmaps:

```txt
global_costmap
local_costmap
```

---

## 8. Global Costmap

The global costmap represents the larger environment.

It is used by the planner.

It usually includes:

* static map
* known obstacles
* inflated obstacle regions

Interview answer:

```txt
The global costmap is used to plan a path from the robot's current pose to the goal.
```

---

## 9. Local Costmap

The local costmap represents the area near the robot.

It updates frequently using live sensor data such as lidar.

It is used by the controller to avoid nearby obstacles.

Interview answer:

```txt
The local costmap helps the controller react to nearby obstacles while following the path.
```

---

## 10. Planner

The planner computes a path from the robot's current pose to the goal pose.

Input:

```txt
current robot pose
goal pose
global costmap
```

Output:

```txt
planned path
```

Interview answer:

```txt
The planner decides where the robot should go.
```

---

## 11. Controller

The controller converts the planned path into velocity commands.

Input:

```txt
planned path
current robot pose
local costmap
robot velocity limits
```

Output:

```txt
/cmd_vel
```

For a differential-drive robot, the command usually contains:

```txt
linear x velocity
angular z velocity
```

Interview answer:

```txt
The controller decides what velocity the robot should execute right now.
```

---

## 12. Recovery Behaviors

Recovery behaviors are used when navigation fails.

Examples:

* spin
* backup
* wait
* clear costmap
* retry planning

Interview answer:

```txt
Recovery behaviors help the robot handle stuck or failed navigation situations.
```

---

## 13. Lifecycle Nodes

Nav2 uses lifecycle nodes.

Lifecycle nodes have managed states:

```txt
unconfigured
inactive
active
finalized
```

This allows Nav2 to start and stop systems in a controlled order.

Interview answer:

```txt
Nav2 is a group of lifecycle-managed nodes, not one single node.
```

---

## 14. Nav2 Data Flow

A simplified Nav2 flow is:

```txt
map_server
    |
    v
global_costmap
    |
    v
planner_server
    |
    v
global path
    |
    v
controller_server
    |
    v
/cmd_vel
    |
    v
robot base controller
```

With localization:

```txt
wheel odom / sensors
        |
        v
localization
        |
        v
map -> odom -> base_link
```

---

## 15. Relationship to This Project

This project currently has two stacks.

### Custom Kinematic Simulator Stack

```txt
/cmd_vel
    -> sim_node
    -> /robot_pose
    -> /odom
    -> /tf
    -> /diagnostics
```

This stack is useful for learning:

* C++ simulation logic
* odometry
* TF
* diagnostics
* validation

But this stack does not move Gazebo.

---

### Gazebo ros2_control Stack

```txt
/diff_drive_controller/cmd_vel
    -> diff_drive_controller
    -> ros2_control
    -> gz_ros2_control
    -> Gazebo wheel joints
    -> /diff_drive_controller/odom
    -> /tf
    -> /joint_states
```

This is the stack that moves the robot in Gazebo.

Important rule:

```txt
sim_node does not move Gazebo.
Gazebo movement uses diff_drive_controller, ros2_control, and gz_ros2_control.
```

---

## 16. How Nav2 Would Connect Later

In the future, Nav2 would send velocity commands to the robot controller.

For the Gazebo stack, that means Nav2 would eventually command:

```txt
/diff_drive_controller/cmd_vel
```

Then the flow would become:

```txt
Nav2 controller_server
    -> /diff_drive_controller/cmd_vel
    -> diff_drive_controller
    -> ros2_control
    -> gz_ros2_control
    -> Gazebo wheel joints
```

---

## 17. Interview Answer: What is Nav2?

Nav2 is the ROS 2 navigation framework used to move a robot from its current pose to a goal pose while avoiding obstacles.

It combines localization, TF, costmaps, planning, control, recovery behaviors, and lifecycle management.

A strong answer is:

```txt
Nav2 takes a goal pose, uses localization to know where the robot is, uses costmaps to understand obstacles, uses a planner to generate a path, and uses a controller to generate velocity commands for the robot.
```

---

## 18. Interview Answer: Planner vs Controller

The planner computes the path.

The controller follows the path.

```txt
planner = where should the robot go?
controller = what velocity should the robot execute now?
```

---

## 19. Interview Answer: Global Costmap vs Local Costmap

The global costmap is used for long-range planning.

The local costmap is used for short-range obstacle avoidance and control.

```txt
global costmap = plan the route
local costmap = safely execute the route
```

---

## 20. Day 81 Completion Criteria

Day 81 is complete when I can explain:

* what Nav2 does
* `map -> odom -> base_link`
* why `odom` drifts
* why `map` corrects drift
* global costmap vs local costmap
* planner vs controller
* recovery behavior
* lifecycle nodes
* how Nav2 would connect to my Gazebo `ros2_control` stack
* why `sim_node` does not move Gazebo
