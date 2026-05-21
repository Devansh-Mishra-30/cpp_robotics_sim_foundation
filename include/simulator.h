#pragma once

#include <vector>

#include "pose2d.h"
#include "robot_command.h"

class Simulator {
public:
	explicit Simulator(double dt, const Pose2D& initialPose = Pose2D{0.0, 0.0, 0.0});
	void step(const RobotCommand& command);

	const Pose2D& getPose() const;
	const std::vector<Pose2D>& getTrajectory() const;

private:
	Pose2D pose_;
	double dt_;
	std::vector<Pose2D> trajectory_;
};