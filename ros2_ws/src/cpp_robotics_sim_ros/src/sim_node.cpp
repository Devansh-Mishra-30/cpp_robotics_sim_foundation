// Copyright 2026 Devansh Mishra
//
// Use of this source code is governed by an MIT-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/MIT.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <exception>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>

#include "cpp_robotics_sim_ros/core_math.hpp"
#include "diagnostic_msgs/msg/diagnostic_array.hpp"
#include "diagnostic_msgs/msg/diagnostic_status.hpp"
#include "diagnostic_msgs/msg/key_value.hpp"
#include "geometry_msgs/msg/pose2_d.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_broadcaster.hpp"

namespace cpp_robotics_sim_ros
{

class SimNode : public rclcpp::Node
{
public:
  SimNode()
  : Node("sim_node")
  {
    declareParameters();
    loadParameters();
    validateParameters();

    pose_.theta = wrapToPi(pose_.theta);
    last_cmd_time_ = now();

    const auto command_qos = rclcpp::QoS(
      rclcpp::KeepLast(10))
      .reliable()
      .durability_volatile();

    const auto state_qos = rclcpp::QoS(
      rclcpp::KeepLast(10))
      .reliable()
      .durability_volatile();

    pose_publisher_ =
      create_publisher<geometry_msgs::msg::Pose2D>(
      "/robot_pose",
      state_qos);

    odom_publisher_ =
      create_publisher<nav_msgs::msg::Odometry>(
      "/odom",
      state_qos);

    diagnostics_publisher_ =
      create_publisher<diagnostic_msgs::msg::DiagnosticArray>(
      "/diagnostics",
      state_qos);

    tf_broadcaster_ =
      std::make_unique<tf2_ros::TransformBroadcaster>(*this);

    cmd_subscriber_ =
      create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel",
      command_qos,
      std::bind(
        &SimNode::cmdVelCallback,
        this,
        std::placeholders::_1));

    const auto timer_period =
      std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::duration<double>(dt_));

    if (timer_period.count() <= 0) {
      throw std::invalid_argument(
              "dt is too small to create a timer");
    }

    timer_ = create_wall_timer(
      timer_period,
      std::bind(&SimNode::timerCallback, this));

    RCLCPP_INFO(
      get_logger(),
      "Simulator initialized: dt=%.6f s, "
      "command timeout=%.3f s, "
      "linear limit=%.3f m/s, "
      "angular limit=%.3f rad/s",
      dt_,
      cmd_timeout_,
      max_linear_velocity_,
      max_angular_velocity_);
  }

private:
  void declareParameters()
  {
    declare_parameter<double>("dt", 0.1);
    declare_parameter<double>("initial_x", 0.0);
    declare_parameter<double>("initial_y", 0.0);
    declare_parameter<double>("initial_theta", 0.0);
    declare_parameter<double>("cmd_timeout", 0.5);
    declare_parameter<double>("max_linear_velocity", 1.0);
    declare_parameter<double>("max_angular_velocity", 1.0);
  }

  void loadParameters()
  {
    dt_ = get_parameter("dt").as_double();
    pose_.x = get_parameter("initial_x").as_double();
    pose_.y = get_parameter("initial_y").as_double();
    pose_.theta = get_parameter("initial_theta").as_double();
    cmd_timeout_ =
      get_parameter("cmd_timeout").as_double();
    max_linear_velocity_ =
      get_parameter("max_linear_velocity").as_double();
    max_angular_velocity_ =
      get_parameter("max_angular_velocity").as_double();
  }

  void validateParameters() const
  {
    if (!std::isfinite(dt_) || dt_ <= 0.0) {
      throw std::invalid_argument(
              "dt must be finite and greater than zero");
    }

    if (!isFinitePose(pose_)) {
      throw std::invalid_argument(
              "initial pose values must be finite");
    }

    if (
      !std::isfinite(cmd_timeout_) ||
      cmd_timeout_ <= 0.0)
    {
      throw std::invalid_argument(
              "cmd_timeout must be finite and greater than zero");
    }

    if (
      !std::isfinite(max_linear_velocity_) ||
      max_linear_velocity_ < 0.0)
    {
      throw std::invalid_argument(
              "max_linear_velocity must be finite "
              "and non-negative");
    }

    if (
      !std::isfinite(max_angular_velocity_) ||
      max_angular_velocity_ < 0.0)
    {
      throw std::invalid_argument(
              "max_angular_velocity must be finite "
              "and non-negative");
    }
  }

  void cmdVelCallback(
    const geometry_msgs::msg::Twist::SharedPtr msg)
  {
    if (
      !std::isfinite(msg->linear.x) ||
      !std::isfinite(msg->angular.z))
    {
      linear_velocity_ = 0.0;
      angular_velocity_ = 0.0;
      last_cmd_time_ = now();

      RCLCPP_WARN(
        get_logger(),
        "Rejected non-finite velocity command");
      return;
    }

    linear_velocity_ = clamp(
      msg->linear.x,
      -max_linear_velocity_,
      max_linear_velocity_);

    angular_velocity_ = clamp(
      msg->angular.z,
      -max_angular_velocity_,
      max_angular_velocity_);

    last_cmd_time_ = now();

    RCLCPP_DEBUG(
      get_logger(),
      "Accepted velocity command: linear=%.3f, angular=%.3f",
      linear_velocity_,
      angular_velocity_);
  }

  void timerCallback()
  {
    const auto callback_start =
      std::chrono::steady_clock::now();

    const double raw_time_since_cmd =
      (now() - last_cmd_time_).seconds();

    const double time_since_cmd =
      std::max(0.0, raw_time_since_cmd);

    const bool timeout_active =
      time_since_cmd > cmd_timeout_;

    if (timeout_active) {
      linear_velocity_ = 0.0;
      angular_velocity_ = 0.0;

      RCLCPP_WARN_THROTTLE(
        get_logger(),
        *get_clock(),
        1000,
        "Command timeout active; commanded velocity is zero");
    }

    pose_ = integratePose(
      pose_,
      linear_velocity_,
      angular_velocity_,
      dt_);

    geometry_msgs::msg::Pose2D pose_message;
    pose_message.x = pose_.x;
    pose_message.y = pose_.y;
    pose_message.theta = pose_.theta;

    pose_publisher_->publish(pose_message);
    publishOdometry();
    publishTransform();

    const auto callback_end =
      std::chrono::steady_clock::now();

    const double callback_time_ms =
      std::chrono::duration<double, std::milli>(
      callback_end - callback_start).count();

    total_callback_time_ms_ += callback_time_ms;
    ++callback_count_;

    max_callback_time_ms_ = std::max(
      max_callback_time_ms_,
      callback_time_ms);

    const double average_callback_time_ms =
      total_callback_time_ms_ /
      static_cast<double>(callback_count_);

    RCLCPP_INFO_THROTTLE(
      get_logger(),
      *get_clock(),
      1000,
      "Pose: x=%.3f, y=%.3f, theta=%.3f, "
      "linear=%.3f, angular=%.3f",
      pose_.x,
      pose_.y,
      pose_.theta,
      linear_velocity_,
      angular_velocity_);

    publishDiagnostics(
      time_since_cmd,
      timeout_active,
      callback_time_ms,
      average_callback_time_ms);
  }

  void publishOdometry()
  {
    nav_msgs::msg::Odometry message;

    message.header.stamp = now();
    message.header.frame_id = "odom";
    message.child_frame_id = "base_link";

    message.pose.pose.position.x = pose_.x;
    message.pose.pose.position.y = pose_.y;

    message.pose.pose.orientation.z =
      std::sin(pose_.theta / 2.0);
    message.pose.pose.orientation.w =
      std::cos(pose_.theta / 2.0);

    message.twist.twist.linear.x = linear_velocity_;
    message.twist.twist.angular.z = angular_velocity_;

    odom_publisher_->publish(message);
  }

  void publishTransform()
  {
    geometry_msgs::msg::TransformStamped message;

    message.header.stamp = now();
    message.header.frame_id = "odom";
    message.child_frame_id = "base_link";

    message.transform.translation.x = pose_.x;
    message.transform.translation.y = pose_.y;

    message.transform.rotation.z =
      std::sin(pose_.theta / 2.0);
    message.transform.rotation.w =
      std::cos(pose_.theta / 2.0);

    tf_broadcaster_->sendTransform(message);
  }

  diagnostic_msgs::msg::KeyValue makeKeyValue(
    const std::string & key,
    const std::string & value) const
  {
    diagnostic_msgs::msg::KeyValue entry;
    entry.key = key;
    entry.value = value;
    return entry;
  }

  void publishDiagnostics(
    double time_since_cmd,
    bool timeout_active,
    double callback_time_ms,
    double average_callback_time_ms)
  {
    diagnostic_msgs::msg::DiagnosticArray message;
    message.header.stamp = now();

    diagnostic_msgs::msg::DiagnosticStatus status;
    status.name = "sim_node";
    status.hardware_id = "cpp_robotics_sim_ros";

    if (timeout_active) {
      status.level =
        diagnostic_msgs::msg::DiagnosticStatus::WARN;
      status.message = "Command timeout active";
    } else {
      status.level =
        diagnostic_msgs::msg::DiagnosticStatus::OK;
      status.message = "Simulator running";
    }

    status.values = {
      makeKeyValue("dt", std::to_string(dt_)),
      makeKeyValue(
        "cmd_timeout",
        std::to_string(cmd_timeout_)),
      makeKeyValue(
        "time_since_cmd",
        std::to_string(time_since_cmd)),
      makeKeyValue(
        "timeout_active",
        timeout_active ? "true" : "false"),
      makeKeyValue(
        "linear_velocity",
        std::to_string(linear_velocity_)),
      makeKeyValue(
        "angular_velocity",
        std::to_string(angular_velocity_)),
      makeKeyValue(
        "max_linear_velocity",
        std::to_string(max_linear_velocity_)),
      makeKeyValue(
        "max_angular_velocity",
        std::to_string(max_angular_velocity_)),
      makeKeyValue("pose_x", std::to_string(pose_.x)),
      makeKeyValue("pose_y", std::to_string(pose_.y)),
      makeKeyValue(
        "pose_theta",
        std::to_string(pose_.theta)),
      makeKeyValue(
        "callback_time_ms",
        std::to_string(callback_time_ms)),
      makeKeyValue(
        "average_callback_time_ms",
        std::to_string(average_callback_time_ms)),
      makeKeyValue(
        "max_callback_time_ms",
        std::to_string(max_callback_time_ms_)),
      makeKeyValue(
        "timing_budget_ms",
        std::to_string(dt_ * 1000.0)),
      makeKeyValue(
        "callback_count",
        std::to_string(callback_count_)),
    };

    message.status.push_back(status);
    diagnostics_publisher_->publish(message);
  }

  rclcpp::Publisher<geometry_msgs::msg::Pose2D>::SharedPtr
    pose_publisher_;

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr
    odom_publisher_;

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr
    cmd_subscriber_;

  rclcpp::Publisher<
    diagnostic_msgs::msg::DiagnosticArray>::SharedPtr
    diagnostics_publisher_;

  rclcpp::TimerBase::SharedPtr timer_;

  std::unique_ptr<tf2_ros::TransformBroadcaster>
  tf_broadcaster_;

  Pose2D pose_{};

  double dt_{0.1};
  double linear_velocity_{0.0};
  double angular_velocity_{0.0};
  double cmd_timeout_{0.5};
  double max_linear_velocity_{1.0};
  double max_angular_velocity_{1.0};

  rclcpp::Time last_cmd_time_;

  double total_callback_time_ms_{0.0};
  double max_callback_time_ms_{0.0};
  std::uint64_t callback_count_{0};
};

}  // namespace cpp_robotics_sim_ros

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);

  try {
    auto node =
      std::make_shared<cpp_robotics_sim_ros::SimNode>();

    rclcpp::spin(node);
  } catch (const std::exception & error) {
    RCLCPP_FATAL(
      rclcpp::get_logger("sim_node"),
      "Simulator failed: %s",
      error.what());

    rclcpp::shutdown();
    return 1;
  }

  rclcpp::shutdown();
  return 0;
}
