// Copyright 2026 Devansh Mishra
//
// Use of this source code is governed by an MIT-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/MIT.

#pragma once

#include <cmath>
#include <stdexcept>

namespace cpp_robotics_sim_ros
{

struct Pose2D
{
  double x{0.0};
  double y{0.0};
  double theta{0.0};
};

inline bool isFinitePose(const Pose2D & pose)
{
  return
    std::isfinite(pose.x) &&
    std::isfinite(pose.y) &&
    std::isfinite(pose.theta);
}

inline double clamp(
  double value,
  double min_value,
  double max_value)
{
  if (
    !std::isfinite(value) ||
    !std::isfinite(min_value) ||
    !std::isfinite(max_value))
  {
    throw std::invalid_argument(
            "clamp() requires finite inputs");
  }

  if (min_value > max_value) {
    throw std::invalid_argument(
            "clamp() received min_value greater than max_value");
  }

  if (value < min_value) {
    return min_value;
  }

  if (value > max_value) {
    return max_value;
  }

  return value;
}

inline double wrapToPi(double angle)
{
  if (!std::isfinite(angle)) {
    throw std::invalid_argument(
            "wrapToPi() requires a finite angle");
  }

  constexpr double kPi = 3.14159265358979323846;
  constexpr double kTwoPi = 2.0 * kPi;

  angle = std::fmod(angle + kPi, kTwoPi);

  if (angle < 0.0) {
    angle += kTwoPi;
  }

  return angle - kPi;
}

inline Pose2D integratePose(
  const Pose2D & pose,
  double linear_velocity,
  double angular_velocity,
  double dt)
{
  if (!isFinitePose(pose)) {
    throw std::invalid_argument(
            "integratePose() requires a finite pose");
  }

  if (
    !std::isfinite(linear_velocity) ||
    !std::isfinite(angular_velocity) ||
    !std::isfinite(dt))
  {
    throw std::invalid_argument(
            "integratePose() requires finite motion inputs");
  }

  if (dt < 0.0) {
    throw std::invalid_argument(
            "integratePose() received negative dt");
  }

  Pose2D next_pose;

  next_pose.x =
    pose.x +
    linear_velocity * std::cos(pose.theta) * dt;

  next_pose.y =
    pose.y +
    linear_velocity * std::sin(pose.theta) * dt;

  next_pose.theta = wrapToPi(
    pose.theta + angular_velocity * dt);

  return next_pose;
}

}  // namespace cpp_robotics_sim_ros
