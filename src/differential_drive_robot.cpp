#include "differential_drive_robot.h"

#include <cmath>

#include "robot_utils.h"

DifferentialDriveRobot::DifferentialDriveRobot(
	const Pose2D& initialPose,
	double wheelRadius,
	double wheelBase
)

	: pose_(initialPose),
	wheelRadius_(wheelRadius),
	wheelBase_(wheelBase) {
	trajectory_.push_back(pose_);
}

void DifferentialDriveRobot::update(const WheelCommand& wheelCommand, double dt) {
	const RobotCommand command = convertWheelCommandToRobotCommand(
		wheelCommand,
		wheelRadius_,
		wheelBase_
	);
	pose_.x += command.v * std::cos(pose_.theta) * dt;
	pose_.y += command.v * std::sin(pose_.theta) * dt;
	pose_.theta = wrapToPi(pose_.theta + command.omega * dt);
}

void DifferentialDriveRobot::reset(const Pose2D& initialPose) {
	pose_ = initialPose;
	trajectory_.clear();
	trajectory_.push_back(pose_);
}

const Pose2D& DifferentialDriveRobot::getPose() const {
	return pose_;
}

const std::vector<Pose2D>& DifferentialDriveRobot::getTrajectory() const {
	return trajectory_;
}

double DifferentialDriveRobot::getWheelRadius() const {
	return wheelRadius_;
}

double DifferentialDriveRobot::getWheelBase() const {
	return wheelBase_;
}

