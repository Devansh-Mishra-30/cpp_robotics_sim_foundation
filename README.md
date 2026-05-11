# 01_joint_basics
# C++ Robotics Simulation Foundation

This project is a modular C++ robotics simulation foundation built as part of my robotics software development roadmap.

The goal of this project is to build clean C++ fundamentals for robotics simulation, including robot state representation, command handling, fixed timestep simulation, trajectory storage, utility math, and basic simulation architecture.

## Current Status

This repository currently represents the foundation stage of the simulator.

It includes:

- `Pose2D` state representation
- Robot command structure
- Fixed timestep simulation loop
- Heading-aware 2D motion update
- Utility functions
- Basic reporting structure
- Header and source file separation
- Clean project organization for future expansion

## Why This Project Exists

I am building this project to strengthen my C++ robotics programming foundation from the perspective of modeling, simulation, control, and ROS 2 integration.

The long-term goal is to evolve this foundation into a complete robotics simulation project with:

- Differential-drive robot simulation
- Trajectory analysis
- Scenario testing
- CSV logging
- Validation checks
- Controller logic
- ROS 2 integration
- TF frame publishing
- rosbag2 recording
- Portfolio-ready documentation

## Mathematical Model

The current simulator is based on planar robot motion.

The robot pose is represented as:

```text
x      = robot position in the world x-direction
y      = robot position in the world y-direction
theta  = robot heading angle
