#include "simulator.h"
#include "pose2d.h"
#include "robot_command.h"
#include "robot_utils.h"
#include <cmath>


Simulator::Simulator(double dt) : robotPose_{0.0,0.0,0.0},
dt_{dt} {
	trajectory_.push_back(robotPose_);
} 

void Simulator::step(const RobotCommand& command) {
	robotPose_.x += command.v * std::cos(robotPose_.theta) * dt_;
	robotPose_.y += command.v * std::sin(robotPose_.theta) * dt_;
	robotPose_.theta = wrapToPi(robotPose_.theta + command.omega * dt_);
	trajectory_.push_back(robotPose_);
}

const Pose2D& Simulator::getPose() const {
	return robotPose_;
}

const std::vector<Pose2D>& Simulator::getTrajectory() const {
	return trajectory_;
}

