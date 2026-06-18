#pragma once

#include<vector>

#include "differential_drive/differential_drive.h"
#include "differential_drive/pose2d.h"

class DifferentialDriveRobot {
public:
	DifferentialDriveRobot(const Pose2D& initialPose,
		double wheelRadius,
		double wheelBase
	);
	void update(const WheelCommand& wheelCommand, double dt);
	void reset(const Pose2D& initialPose);
	const Pose2D& getPose() const;
	const std::vector<Pose2D>& getTrajectory() const;
	double getWheelRadius() const;
	double getWheelBase() const;

private:
	Pose2D pose_{};
	std::vector<Pose2D> trajectory_;
	double wheelRadius_{};
	double wheelBase_{};
};