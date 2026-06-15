#include <chrono>
#include <memory>
#include <functional>
#include <cmath>
#include <algorithm>

#include "geometry_msgs/msg/pose2_d.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

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

        pose_publisher_ = create_publisher<geometry_msgs::msg::Pose2D>("/robot_pose", 10
        );

        auto time_period = std::chrono::duration<double>(dt_);

        cmd_subscriber_ = create_subscription<geometry_msgs::msg::Twist>("/cmd_vel", 10, 
            std::bind(&SimNode::cmdVelCallback, 
                this, std::placeholders::_1));

        timer_ = this->create_wall_timer(std::chrono::duration_cast<std::chrono::milliseconds>(time_period),
            std::bind(&SimNode::timerCallback, this)

        );

        RCLCPP_INFO(get_logger(), "Day 49 ROS 2 safety enabled simulator node started");
    }
private:

    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        linear_velocity_ = std::clamp(msg->linear.x, -max_linear_velocity_, max_linear_velocity_);
        angular_velocity_ = std::clamp(msg->angular.z, -max_angular_velocity_, max_angular_velocity_);
        last_cmd_time_ = this->now();
        RCLCPP_INFO(get_logger(), "Received cmd_vel: linear.x=%.2f, angular.z=%.2f", linear_velocity_, angular_velocity_);
    }

    void timerCallback() {
        double time_since_cmd = (this->now() - last_cmd_time_).seconds();

        if (time_since_cmd > cmd_timeout_) {
            linear_velocity_ = 0.0;
            angular_velocity_ = 0.0;
        }

        pose_.theta += angular_velocity_ * dt_;
        pose_.theta = std::atan2(std::sin(pose_.theta), std::cos(pose_.theta));
        pose_.x += linear_velocity_ * std::cos(pose_.theta) * dt_;
        pose_.y += linear_velocity_ * std::sin(pose_.theta) * dt_;

        pose_publisher_->publish(pose_);
        RCLCPP_INFO(get_logger(), "Published pose: x=%.2f, y=%.2f, theta=%.2f",
            pose_.x,
            pose_.y,
            pose_.theta);
    }
    rclcpp::Publisher<geometry_msgs::msg::Pose2D>::SharedPtr pose_publisher_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_subscriber_;
    rclcpp::TimerBase::SharedPtr timer_;
    geometry_msgs::msg::Pose2D pose_{};
    double dt_{0.1};
    double linear_velocity_{ 0.0 };
    double angular_velocity_{ 0.0 };
    double cmd_timeout_{ 0.5 };
    double max_linear_velocity_{ 1.0 };
    double max_angular_velocity_{ 1.0 };
    rclcpp::Time last_cmd_time_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SimNode>();

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}