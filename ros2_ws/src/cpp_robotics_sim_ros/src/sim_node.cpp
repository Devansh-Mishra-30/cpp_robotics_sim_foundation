#include <chrono>
#include <memory>
#include <functional>

#include "geometry_msgs/msg/pose2_d.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class SimNode : public rclcpp::Node {
public:
    SimNode()
    : Node("sim_node") {
        pose_publisher_ = create_publisher<geometry_msgs::msg::Pose2D>("robot_pose", 10
        );

        timer_ = create_wall_timer(100ms,
            std::bind(&SimNode::timerCallback, this)

        );

        RCLCPP_INFO(get_logger(), "Day 46 ROS 2 simulation node started");
    }
private:
    void timerCallback() {
        pose_.x += linear_velocity_ * dt_;
        pose_.theta = 0.0;

        pose_publisher_->publish(pose_);
        RCLCPP_INFO(get_logger(), "Published pose: x=%.2f, y=%.2f, theta=%.2f",
            pose_.x,
            pose_.y,
            pose_.theta);
    }
    rclcpp::Publisher<geometry_msgs::msg::Pose2D>::SharedPtr pose_publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    geometry_msgs::msg::Pose2D pose_{};
    double dt_{0.1};
    double linear_velocity_{ 0.5 };
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SimNode>();

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}