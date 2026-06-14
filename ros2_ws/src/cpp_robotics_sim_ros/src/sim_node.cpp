#include <chrono>
#include <memory>
#include <functional>
#include <cmath>

#include "geometry_msgs/msg/pose2_d.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class SimNode : public rclcpp::Node {
public:
    SimNode()
    : Node("sim_node") {
        pose_publisher_ = create_publisher<geometry_msgs::msg::Pose2D>("robot_pose", 10
        );

        cmd_subscriber_ = create_subscription<geometry_msgs::msg::Twist>("cmd_vel", 10, 
            std::bind(&SimNode::cmdVelCallback, 
                this, std::placeholders::_1));

        timer_ = create_wall_timer(100ms,
            std::bind(&SimNode::timerCallback, this)

        );

        RCLCPP_INFO(get_logger(), "Day 47 ROS 2 cmd_vel subscriber node started");
    }
private:

    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        linear_velocity_ = msg->linear.x;
        angular_velocity_ = msg->angular.z;

        RCLCPP_INFO(get_logger(), "Received cmd_vel: linear.x=%.2f, angular.z=%.2f", linear_velocity_, angular_velocity_);
    }

    void timerCallback() {
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
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SimNode>();

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}