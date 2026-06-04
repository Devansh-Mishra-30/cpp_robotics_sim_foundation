#pragma once

#include "pose2d.h"
#include "robot_command.h"

struct TargetControllerGains {
	double linearGain{};
	double angularGain{};
	double maxLinearSpeed{};
	double maxAngularSpeed{};
	double positionTolerance{};
};

RobotCommand computeTargetTrackingControl(
	const Pose2D& currentPose,
	const Pose2D& targetPose,
	const TargetControllerGains& gains
);