#include <chrono>
#include <memory>
#include <functional>

#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class SimNode : public rclcpp::Node {
public:
    SimNode()
    : Node("sim_node") {
        timer_ = create_wall_timer(1000ms, std::bind(&SimNode::timerCallback, this)
    );
    RCLCPP_INFO(get_logger(), "Day 45 ROS 2 simulation node started");
    }
private:
    void timerCallback() {
        RCLCPP_INFO(get_logger(), "C++ robotics simulator ROS 2 bridge is running");
    }

    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<SimNode>();

    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}