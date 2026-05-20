#pragma once

#include <vector>

#include "pose2d.h"
#include "robot_command.h"

class Simulator {
public:
	Simulator(double dt, const Pose2D& initialPose);

	void step(const RobotCommand& command);

	const Pose2D& getPose() const;
	const std::vector<Pose2D>& getTrajectory() const;

private:
	double dt_{};
	Pose2D pose_{};
	std::vector<Pose2D> trajectory_;
};