#pragma once

#include <vector>

#include "differential_drive/robot_command.h"
#include "differential_drive/pose2d.h"

class Simulator {
public:
	explicit Simulator(double dt, const Pose2D& initialPose);
	void step(const RobotCommand& command);

	const Pose2D& getPose() const;
	const std::vector<Pose2D>& getTrajectory() const;

private:
	Pose2D pose_{};
	double dt_{};
	std::vector<Pose2D> trajectory_;
};