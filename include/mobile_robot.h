#pragma once

#include <vector>

#include "pose2d.h"
#include "robot_command.h"

class MobileRobot {
public: 
	explicit MobileRobot(const Pose2D& initialPose);

	void update(const RobotCommand& command, double dt);

	void reset(const Pose2D& initialPose);

	const Pose2D& getPose() const;

	const std::vector<Pose2D>& getTrajectory() const;

private:
	Pose2D pose_{};
	std::vector<Pose2D> trajectory_;
};
