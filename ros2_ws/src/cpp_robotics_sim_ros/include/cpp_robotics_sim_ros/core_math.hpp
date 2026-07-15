// Copyright 2026 Devansh Mishra
//
// Use of this source code is governed by an MIT-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/MIT.

#pragma once

/*
  Testable Core Math and Pose Utilities

  Why this file exists:
  ---------------------
  A ROS 2 / Gazebo robot stack has many moving parts:
    - nodes
    - topics
    - launch files
    - parameters
    - controllers
    - Gazebo physics
    - TF frames
    - RViz visualization

  But the safest first layer to test is the deterministic math layer.

  These functions do NOT depend on ROS.
  They do NOT depend on Gazebo.
  They do NOT publish topics.
  They do NOT require simulation time.

  That makes them ideal for GoogleTest.

  Core math tests:
    1. clamp()
    2. wrapToPi()
    3. integratePose()

  This creates the foundation for automated testing and future CI.
*/

#include <cmath>
#include <stdexcept>

namespace cpp_robotics_sim_ros
{

    // Simple 2D robot pose used for testing planar mobile robot kinematics.
struct Pose2D
{
  double x{0.0};
  double y{0.0};
  double theta{0.0};
};

    /*
      clamp(value, min_value, max_value)

      Purpose:
      --------
      Limit a value to a safe range.

      Robotics use cases:
        - velocity limits
        - angular velocity limits
        - motor command limits
        - sensor value guards
        - controller output saturation

      Example:
        clamp(2.0, -1.0, 1.0) = 1.0
        clamp(-2.0, -1.0, 1.0) = -1.0
        clamp(0.5, -1.0, 1.0) = 0.5

      Design choice:
      --------------
      If min_value > max_value, this function throws an exception.
      That catches configuration mistakes early.
    */
inline double clamp(double value, double min_value, double max_value)
{
  if (min_value > max_value) {
    throw std::invalid_argument("clamp() received min_value greater than max_value");
  }

  if (value < min_value) {
    return min_value;
  }

  if (value > max_value) {
    return max_value;
  }

  return value;
}

    /*
      wrapToPi(angle)

      Purpose:
      --------
      Normalize an angle into the range [-pi, pi).

      Robotics use cases:
        - heading error
        - yaw normalization
        - odometry orientation
        - controller angular error
        - avoiding angle discontinuity

      Convention used here:
      ---------------------
      Range is [-pi, pi)

      That means:
        wrapToPi(pi)      = -pi
        wrapToPi(2*pi)    = 0
        wrapToPi(-2*pi)   = 0
        wrapToPi(3*pi)    = -pi

      Why this matters:
      -----------------
      Without wrapping, a robot heading can grow forever:
        0, pi, 2pi, 3pi, 4pi, ...

      But physically, 0 and 2pi represent the same orientation.
    */
inline double wrapToPi(double angle)
{
  constexpr double PI = 3.14159265358979323846;
  constexpr double TWO_PI = 2.0 * PI;

  angle = std::fmod(angle + PI, TWO_PI);

  if (angle < 0.0) {
    angle += TWO_PI;
  }

  return angle - PI;
}

    /*
      integratePose(pose, linear_velocity, angular_velocity, dt)

      Purpose:
      --------
      Advance a planar robot pose by one timestep using a simple unicycle model.

      Model:
      ------
        x_next     = x + v * cos(theta) * dt
        y_next     = y + v * sin(theta) * dt
        theta_next = theta + omega * dt

      where:
        v     = linear velocity in robot forward direction
        omega = yaw rate / angular velocity
        dt    = timestep

      Robotics use cases:
        - differential-drive odometry
        - simulator pose update
        - dead reckoning
        - simple kinematic prediction

      Important:
      ----------
      This is a kinematic update, not a full physics simulation.
      Gazebo handles physics separately.
    */
inline Pose2D integratePose(
  const Pose2D & pose,
  double linear_velocity,
  double angular_velocity,
  double dt)
{
  if (dt < 0.0) {
    throw std::invalid_argument("integratePose() received negative dt");
  }

  Pose2D next_pose;

  next_pose.x = pose.x + linear_velocity * std::cos(pose.theta) * dt;
  next_pose.y = pose.y + linear_velocity * std::sin(pose.theta) * dt;
  next_pose.theta = wrapToPi(pose.theta + angular_velocity * dt);

  return next_pose;
}

}  // namespace cpp_robotics_sim_ros
