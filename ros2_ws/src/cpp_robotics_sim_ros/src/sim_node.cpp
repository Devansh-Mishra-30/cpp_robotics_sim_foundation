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
        this->declare_parameter<double>("dt", 0.1);
        this->declare_parameter<double>("initial_x", 0.0);
        this->declare_parameter<double>("initial_y", 0.0);
        this->declare_parameter<double>("initial_theta", 0.0);

        dt_ = this->get_parameter("dt").as_double();
        pose_.x = this->get_parameter("initial_x").as_double();
        pose_.y = this->get_parameter("initial_y").as_double();
        pose_.theta = this->get_parameter("initial_theta").as_double();

        pose_publisher_ = create_publisher<geometry_msgs::msg::Pose2D>("/robot_pose", 10
        );

        auto time_period = std::chrono::duration<double>(dt_);

        cmd_subscriber_ = create_subscription<geometry_msgs::msg::Twist>("/cmd_vel", 10, 
            std::bind(&SimNode::cmdVelCallback, 
                this, std::placeholders::_1));

        timer_ = this->create_wall_timer(std::chrono::duration_cast<std::chrono::milliseconds>(time_period),
            std::bind(&SimNode::timerCallback, this)

        );

        RCLCPP_INFO(get_logger(), "Day 48 ROS 2 parameterized simulator node started");
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