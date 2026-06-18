#include "differential_drive/mobile_robot.h"
#include <cmath>

#include "differential_drive/robot_utils.h"

MobileRobot::MobileRobot(const Pose2D& initialPose)
	: pose_(initialPose) {
	trajectory_.push_back(pose_);
}

void MobileRobot::update(const RobotCommand& command, double dt) {
	pose_.x += command.v * std::cos(pose_.theta) * dt;
	pose_.y += command.v * std::sin(pose_.theta) * dt;
	pose_.theta = wrapToPi(pose_.theta + command.omega * dt);

	trajectory_.push_back(pose_);
}

void MobileRobot::reset(const Pose2D& initialPose) {
	pose_ = initialPose;
	trajectory_.clear();
	trajectory_.push_back(pose_);
}

const Pose2D& MobileRobot::getPose() const {
	return pose_;
}

const std::vector<Pose2D>& MobileRobot::getTrajectory() const {
	return trajectory_;
}
