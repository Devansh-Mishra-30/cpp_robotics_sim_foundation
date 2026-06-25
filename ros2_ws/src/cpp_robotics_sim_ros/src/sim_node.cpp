#include <chrono>
#include <memory>
#include <functional>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <string>

#include "geometry_msgs/msg/pose2_d.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/transform_broadcaster.hpp"
#include "diagnostic_msgs/msg/diagnostic_array.hpp"
#include "diagnostic_msgs/msg/diagnostic_status.hpp"
#include "diagnostic_msgs/msg/key_value.hpp"

class SimNode : public rclcpp::Node {
public:
    SimNode()
    : Node("sim_node") {
        this->declare_parameter<double>("dt", 0.1);
        this->declare_parameter<double>("initial_x", 0.0);
        this->declare_parameter<double>("initial_y", 0.0);
        this->declare_parameter<double>("initial_theta", 0.0);
        this->declare_parameter<double>("cmd_timeout", 0.5);
        this->declare_parameter<double>("max_linear_velocity", 1.0);
        this->declare_parameter<double>("max_angular_velocity", 1.0);

        dt_ = this->get_parameter("dt").as_double();
        pose_.x = this->get_parameter("initial_x").as_double();
        pose_.y = this->get_parameter("initial_y").as_double();
        pose_.theta = this->get_parameter("initial_theta").as_double();
        cmd_timeout_ = this->get_parameter("cmd_timeout").as_double();
        max_linear_velocity_ = this->get_parameter("max_linear_velocity").as_double();
        max_angular_velocity_ = this->get_parameter("max_angular_velocity").as_double();
        last_cmd_time_ = this->now();

        if (!validateParameters()) {
            throw std::runtime_error("Invalid simulator parameters");
        }

        RCLCPP_INFO(
            get_logger(),
            "Parameters loaded: dt = %.3f, cmd_timeout=%.3f, max_v=%.3f, max_w=%.3f",
            dt_,
            cmd_timeout_,
            max_linear_velocity_,
            max_angular_velocity_
        );

        const auto command_qos = rclcpp::QoS(rclcpp::KeepLast(10))
            .reliable()
            .durability_volatile();

        const auto state_qos = rclcpp::QoS(rclcpp::KeepLast(10))
            .reliable()
            .durability_volatile();

        pose_publisher_ = create_publisher<geometry_msgs::msg::Pose2D>("/robot_pose", state_qos
        );

        odom_publisher_ = this->create_publisher<nav_msgs::msg::Odometry>("/odom", state_qos);

        diagnostics_publisher_ = this->create_publisher<diagnostic_msgs::msg::DiagnosticArray>("/diagnostics", state_qos);

        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

        auto time_period = std::chrono::duration<double>(dt_);

        cmd_subscriber_ = create_subscription<geometry_msgs::msg::Twist>("/cmd_vel", command_qos, 
            std::bind(&SimNode::cmdVelCallback, 
                this, std::placeholders::_1));

        RCLCPP_INFO(get_logger(), "QoS configured: /cmd_vel reliable volatile depth=10, /robot_pose reliable volatile depth=10, /odom reliable volatile depth=10");

        timer_ = this->create_wall_timer(std::chrono::duration_cast<std::chrono::milliseconds>(time_period),
            std::bind(&SimNode::timerCallback, this)

        );

        RCLCPP_INFO(get_logger(), "Day 67 ROS 2 simulator with diagnostics enabled");
    }
private:

    bool validateParameters() {
        bool valid = true;

        if (dt_ <= 0.0) {
            RCLCPP_ERROR(
                get_logger(),
                "Invalid parameter: dt must be > 0. Current dt=%.3f",
                dt_
            );
            valid = false;
        }

        if (cmd_timeout_ <= 0.0) {
            RCLCPP_ERROR(
                get_logger(),
                "Invalid parameter: cmd_timeout must be > 0. Current cmd_timeout=%.3f",
                cmd_timeout_
            );
            valid = false;
        }
        if (max_linear_velocity_ < 0.0) {
            RCLCPP_ERROR(
                get_logger(),
                "Invalid parameter: max_linear_velocity must be >= 0. Current max_linear_velocity =%.3f",
                max_linear_velocity_
            );
            valid = false;
        }
        if (max_angular_velocity_ < 0.0) {
            RCLCPP_ERROR(
                get_logger(),
                "Invalid parameter: max_angular_velocity must be >= 0. Current max_angular_velocity =%.3f",
                max_angular_velocity_
                );
            valid = false;
        }
        return valid;
    }

    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        linear_velocity_ = std::clamp(msg->linear.x, -max_linear_velocity_, max_linear_velocity_);
        angular_velocity_ = std::clamp(msg->angular.z, -max_angular_velocity_, max_angular_velocity_);
        last_cmd_time_ = this->now();
        RCLCPP_INFO(get_logger(), "Received cmd_vel: linear.x=%.2f, angular.z=%.2f", linear_velocity_, angular_velocity_);
    }

    void timerCallback() {
        auto start_time = std::chrono::steady_clock::now();

        double time_since_cmd = (this->now() - last_cmd_time_).seconds();

        bool timeout_active = time_since_cmd > cmd_timeout_;

        if (timeout_active) {
            linear_velocity_ = 0.0;
            angular_velocity_ = 0.0;

            RCLCPP_WARN_THROTTLE(get_logger(),
                *get_clock(),
                1000,
                "cmd_vel timeout: stopping robot");
        }

        pose_.theta += angular_velocity_ * dt_;
        pose_.theta = std::atan2(std::sin(pose_.theta), std::cos(pose_.theta));
        pose_.x += linear_velocity_ * std::cos(pose_.theta) * dt_;
        pose_.y += linear_velocity_ * std::sin(pose_.theta) * dt_;

        pose_publisher_->publish(pose_);
        publishOdometry();
        publishTransform();

        RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 1000, "Pose: x=%.2f, y=%.2f, theta=%.2f | v=%.2f, w=%.2f",
            pose_.x,
            pose_.y,
            pose_.theta,
            linear_velocity_,
            angular_velocity_);
        
        auto end_time = std::chrono::steady_clock::now();

        double callback_time_ms =
            std::chrono::duration<double, std::milli>(end_time - start_time).count();

        total_callback_time_ms_ += callback_time_ms;
        callback_count_++;

        if (callback_time_ms > max_callback_time_ms_) {
            max_callback_time_ms_ = callback_time_ms;
        }

        double average_callback_time_ms = total_callback_time_ms_ / callback_count_;

        RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 2000,
            "Performance callback avg=%.4f ms, max=%.4f ms, budget=%.2f ms",
            average_callback_time_ms,
            max_callback_time_ms_,
            dt_ * 1000.0);

        publishDiagnostics(time_since_cmd, timeout_active, callback_time_ms, average_callback_time_ms);
    }

    void publishOdometry() {
        nav_msgs::msg::Odometry odom_msg;
        odom_msg.header.stamp = this->now();
        odom_msg.header.frame_id = "odom";
        odom_msg.child_frame_id = "base_link";

        odom_msg.pose.pose.position.x = pose_.x;
        odom_msg.pose.pose.position.y = pose_.y;
        odom_msg.pose.pose.position.z = 0.0;

        odom_msg.pose.pose.orientation.x = 0.0;
        odom_msg.pose.pose.orientation.y = 0.0;
        odom_msg.pose.pose.orientation.z = std::sin(pose_.theta / 2.0);
        odom_msg.pose.pose.orientation.w = std::cos(pose_.theta / 2.0);

        odom_msg.twist.twist.linear.x = linear_velocity_;
        odom_msg.twist.twist.linear.y = 0.0;
        odom_msg.twist.twist.linear.z = 0.0;

        odom_msg.twist.twist.angular.x = 0.0;
        odom_msg.twist.twist.angular.y = 0.0;
        odom_msg.twist.twist.angular.z = angular_velocity_;
        odom_publisher_->publish(odom_msg);
    }

    void publishTransform() {
        geometry_msgs::msg::TransformStamped transform_msg;

        transform_msg.header.stamp = this->now();
        transform_msg.header.frame_id = "odom";
        transform_msg.child_frame_id = "base_link";

        transform_msg.transform.translation.x = pose_.x;
        transform_msg.transform.translation.y = pose_.y;
        transform_msg.transform.translation.z = 0.0;

        transform_msg.transform.rotation.x = 0.0;
        transform_msg.transform.rotation.y = 0.0;
        transform_msg.transform.rotation.z = std::sin(pose_.theta / 2.0);
        transform_msg.transform.rotation.w = std::cos(pose_.theta / 2.0);

        tf_broadcaster_->sendTransform(transform_msg);
    }

    diagnostic_msgs::msg::KeyValue makeKeyValue(
        const std::string& key,
        const std::string& value
    ) const {
        diagnostic_msgs::msg::KeyValue key_value;
        key_value.key = key;
        key_value.value = value;
        return key_value;
    }

    void publishDiagnostics(
        double time_since_cmd,
        bool timeout_active,
        double callback_time_ms,
        double average_callback_time_ms
    ) {
        diagnostic_msgs::msg::DiagnosticArray diagnostics_msg;
        diagnostics_msg.header.stamp = this->now();

        diagnostic_msgs::msg::DiagnosticStatus status;
        status.name = "sim_node";
        status.hardware_id = "cpp_robotics_sim_ros";

        if (timeout_active) {
            status.level = diagnostic_msgs::msg::DiagnosticStatus::WARN;
            status.message = "cmd_vel timeout active";
        }
        else {
            status.level = diagnostic_msgs::msg::DiagnosticStatus::OK;
            status.message = "Simulator running";
        }

        status.values.push_back(makeKeyValue("dt", std::to_string(dt_)));
        status.values.push_back(makeKeyValue("cmd_timeout", std::to_string(cmd_timeout_)));
        status.values.push_back(makeKeyValue("time_since_cmd", std::to_string(time_since_cmd)));
        status.values.push_back(makeKeyValue("timeout_active", timeout_active ? "true" : "false"));
        status.values.push_back(makeKeyValue("linear_velocity", std::to_string(linear_velocity_)));
        status.values.push_back(makeKeyValue("angular_velocity", std::to_string(angular_velocity_)));
        status.values.push_back(makeKeyValue("max_linear_velocity", std::to_string(max_linear_velocity_)));
        status.values.push_back(makeKeyValue("max_angular_velocity", std::to_string(max_angular_velocity_)));
        status.values.push_back(makeKeyValue("pose_x", std::to_string(pose_.x)));
        status.values.push_back(makeKeyValue("pose_y", std::to_string(pose_.y)));
        status.values.push_back(makeKeyValue("pose_theta", std::to_string(pose_.theta)));
        status.values.push_back(makeKeyValue("callback_time_ms", std::to_string(callback_time_ms)));
        status.values.push_back(makeKeyValue("average_callback_time_ms", std::to_string(average_callback_time_ms)));
        status.values.push_back(makeKeyValue("max_callback_time_ms", std::to_string(max_callback_time_ms_)));
        status.values.push_back(makeKeyValue("timing_budget_ms", std::to_string(dt_ * 1000.0)));
        status.values.push_back(makeKeyValue("callback_count", std::to_string(callback_count_)));

        diagnostics_msg.status.push_back(status);

        diagnostics_publisher_->publish(diagnostics_msg);
    }

    rclcpp::Publisher<geometry_msgs::msg::Pose2D>::SharedPtr pose_publisher_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_publisher_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_subscriber_;
    rclcpp::Publisher<diagnostic_msgs::msg::DiagnosticArray>::SharedPtr diagnostics_publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    geometry_msgs::msg::Pose2D pose_{};
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;


    double dt_{0.1};
    double linear_velocity_{ 0.0 };
    double angular_velocity_{ 0.0 };
    double cmd_timeout_{ 0.5 };
    double max_linear_velocity_{ 1.0 };
    double max_angular_velocity_{ 1.0 };
    rclcpp::Time last_cmd_time_;
    double total_callback_time_ms_{ 0.0 };
    double max_callback_time_ms_{ 0.0 };
    int callback_count_{ 0 };
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SimNode>();

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}