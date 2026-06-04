#include "target_controller.h"

#include <algorithm>
#include <cmath>

#include "robot_utils.h"

RobotCommand computeTargetTrackingControl(
	const Pose2D& currentPose,
	const Pose2D& targetPose,
	const TargetControllerGains& gains
) {
	const double dx = targetPose.x - currentPose.x;
	const double dy = targetPose.y - currentPose.y;

	const double distanceError = std::sqrt(dx * dx + dy * dy);

	if (distanceError <= gains.positionTolerance) {
		return { 0.0,0.0 };
	}

	const double targetHeading = std::atan2(dy, dx);
	const double headingError = wrapToPi(targetHeading - currentPose.theta);

	double linearSpeed = gains.linearGain * distanceError;
	double angularSpeed = gains.angularGain * headingError;

	linearSpeed = std::clamp(
		linearSpeed,
		-gains.maxLinearSpeed,
		gains.maxLinearSpeed
	);
	angularSpeed = std::clamp(
		angularSpeed,
		-gains.maxAngularSpeed,
		gains.maxAngularSpeed
	);

	return { linearSpeed, angularSpeed };
}