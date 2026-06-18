# Day 60 Robotics Simulation Assessment

This document summarizes the Day 1–60 robotics simulation engineering milestone.

---

## 1. Project Summary

This project is a modular robotics simulation foundation built in C++ and ROS 2.

It contains:

- standalone C++ simulation modules
- differential-drive mobile robot simulation
- manipulator joint-state simulation
- ROS 2 C++ simulator integration
- odometry publishing
- TF broadcasting
- regression testing
- debugging workflow
- performance timing
- project documentation

---

## 2. Repository Structure

```txt
cpp_robotics_sim_foundation/
├── standalone_cpp/
│   ├── include/
│   │   ├── differential_drive/
│   │   └── manipulator/
│   ├── src/
│   │   ├── differential_drive/
│   │   ├── manipulator/
│   │   └── main.cpp
│   └── CMakeLists.txt
│
├── ros2_ws/
│   └── src/cpp_robotics_sim_ros/
│
└── docs/
```

---

# Day 61 — ROS 2 Launch System

## Goal

Create a one-command ROS 2 launch workflow for the simulator stack.

## Deliverable

The simulator can now be started with:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## What Changed

Added:

```txt
ros2_ws/src/cpp_robotics_sim_ros/launch/sim.launch.py
```

Updated CMake to install the launch directory:

```cmake
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)
```

## Why This Matters

A launch file makes the ROS 2 stack repeatable. Instead of manually running the node and passing parameters through terminal commands, the launch file defines the node startup in one version-controlled place.

---

# Day 62 — YAML Parameters

## Goal

Move simulator runtime parameters out of the launch file and into a YAML configuration file.

## Deliverable

The simulator now loads parameters from:

```txt
ros2_ws/src/cpp_robotics_sim_ros/config/sim_params.yaml
```

The simulator still launches with:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

## YAML File

```yaml
sim_node:
  ros__parameters:
    dt: 0.1
    initial_x: 0.0
    initial_y: 0.0
    initial_theta: 0.0
    cmd_timeout: 0.5
    max_linear_velocity: 0.5
    max_angular_velocity: 0.8
```

## Launch File Change

Before Day 62, parameters were written directly inside `sim.launch.py`.

After Day 62, the launch file loads:

```python
params_file = os.path.join(package_share_dir, "config", "sim_params.yaml")
```

and passes it into the node:

```python
parameters=[params_file]
```

## Why This Matters

YAML configuration separates runtime parameters from code and launch logic. This makes the simulator easier to tune, reproduce, and extend. Robotics projects commonly use YAML files for controller gains, robot limits, sensor settings, navigation parameters, and simulation settings.

## Verification Commands

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

In another terminal:

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 param get /sim_node dt
ros2 param get /sim_node initial_x
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

## Expected Result

```txt
dt: 0.1
initial_x: 0.0
cmd_timeout: 0.5
max_linear_velocity: 0.5
max_angular_velocity: 0.8
```

## Interview Explanation

Day 62 moved simulator parameters from the launch file into a YAML configuration file. The launch file now locates the installed package share directory, finds `config/sim_params.yaml`, and passes that file to `sim_node`. This separates code, launch behavior, and runtime configuration. It matters because professional robotics systems use YAML for controller parameters, robot limits, sensor settings, and navigation configuration.

---

# Day 63 — Launch Arguments

## Goal

Add runtime launch arguments for selected simulator parameters.

## Deliverable

The simulator can still be launched with the default YAML configuration:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py
```

It can also override selected parameters from the terminal:

```bash
ros2 launch cpp_robotics_sim_ros sim.launch.py dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

## Parameters Exposed as Launch Arguments

| Launch Argument | Default | Purpose |
|---|---:|---|
| dt | 0.1 | Simulation timestep |
| cmd_timeout | 0.5 | Stops robot if command input becomes stale |
| max_linear_velocity | 0.5 | Linear velocity safety clamp |
| max_angular_velocity | 0.8 | Angular velocity safety clamp |

## Launch File Design

The YAML file provides the default configuration:

```python
parameters=[
    params_file,
    {
        "dt": ParameterValue(LaunchConfiguration("dt"), value_type=float),
        "cmd_timeout": ParameterValue(LaunchConfiguration("cmd_timeout"), value_type=float),
        "max_linear_velocity": ParameterValue(LaunchConfiguration("max_linear_velocity"), value_type=float),
        "max_angular_velocity": ParameterValue(LaunchConfiguration("max_angular_velocity"), value_type=float),
    },
]
```

The dictionary after `params_file` overrides selected YAML parameters at runtime.

## Verification Commands

```bash
cd "/mnt/c/Self study/PRACTICE C++/Cdev/01_joint_basics/ros2_ws"
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
ros2 launch cpp_robotics_sim_ros sim.launch.py dt:=0.05 cmd_timeout:=1.0 max_linear_velocity:=0.2 max_angular_velocity:=0.4
```

In another terminal:

```bash
ros2 param get /sim_node dt
ros2 param get /sim_node cmd_timeout
ros2 param get /sim_node max_linear_velocity
ros2 param get /sim_node max_angular_velocity
```

Expected:

```txt
Double value is: 0.05
Double value is: 1.0
Double value is: 0.2
Double value is: 0.4
```

## Interview Explanation

Day 63 added launch arguments on top of the YAML configuration. YAML stores stable defaults, while launch arguments allow runtime overrides without editing files. This is useful in robotics simulation because engineers often need to test different timesteps, timeout values, and velocity limits quickly while keeping the base configuration version-controlled.