#include "simulator.h"
#include "robot_utils.h"
#include <cmath>


Simulator::Simulator(double dt, const Pose2D& initialPose)
	: dt_(dt), pose_(initialPose) {
	trajectory_.push_back(pose_);
}

void Simulator::step(const RobotCommand& command) {
	pose_.x += command.v * std::cos(pose_.theta) * dt_;
	pose_.y += command.v * std::sin(pose_.theta) * dt_;
	pose_.theta = wrapToPi(pose_.theta + command.omega * dt_);
	trajectory_.push_back(pose_);
}

const Pose2D& Simulator::getPose() const {
	return pose_;
}

const std::vector<Pose2D>& Simulator::getTrajectory() const {
	return trajectory_;
}

